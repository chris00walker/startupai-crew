"""
StartupAI Modal Serverless Application

Main entry point for the 5-Flow / 14-Crew / 45-Agent validation engine.
Implements the Serverless Agentic Loop architecture per ADR-002.

Endpoints:
    POST /kickoff        - Start validation run (returns 202 + run_id)
    GET  /status/{run_id} - Check progress (reads from Supabase)
    POST /hitl/approve   - Resume after human approval

Usage:
    modal deploy src/modal_app/app.py      # Deploy to Modal
    modal serve src/modal_app/app.py       # Local development
"""

import os
import sys
import json
import hmac
import logging
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID, uuid4

# Add src directory to Python path for Modal container
if "/root/src" not in sys.path:
    sys.path.insert(0, "/root/src")
if "/root" not in sys.path:
    sys.path.insert(0, "/root")

import modal
from fastapi import FastAPI, HTTPException, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Modal App Definition
# -----------------------------------------------------------------------------

# Define the container image with all dependencies
# Use add_local_dir to include the src directory for imports
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "crewai>=0.80.0",
        "crewai-tools>=0.14.0",
        "fastapi>=0.115.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "supabase>=2.0.0",
        "openai>=1.0.0",
        "tavily-python>=0.3.0",
        "httpx>=0.27.0",
        # MCP integration for tool framework
        "mcp>=1.0.0",
        "fastmcp>=0.1.0",
        "mcp-use>=0.1.0",
    )
    .add_local_dir("src", remote_path="/root/src")
)

# Create the Modal App
app = modal.App(
    name="startupai-validation",
    image=image,
    secrets=[modal.Secret.from_name("startupai-secrets")],
)

# -----------------------------------------------------------------------------
# FastAPI Application
# -----------------------------------------------------------------------------

web_app = FastAPI(
    title="StartupAI Validation API",
    description="5-Flow / 14-Crew / 45-Agent validation engine",
    version="0.1.0",
)

# CORS configuration
web_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.startupai.site",
        "https://startupai.site",
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# Request/Response Models
# -----------------------------------------------------------------------------

class KickoffRequest(BaseModel):
    """Request to start a new validation run.

    Quick Start flow:
    - Phase 0: Pass-through (stores raw_idea + hints)
    - Phase 1 Stage A: BriefGenerationCrew generates Founder's Brief
    - Phase 1 Stage B: VPC Discovery crews run
    """
    project_id: UUID
    user_id: UUID
    entrepreneur_input: str = Field(..., min_length=10)
    session_id: Optional[UUID] = None
    conversation_transcript: Optional[str] = None  # Full conversation from Alex chat
    user_type: Optional[str] = "founder"  # "founder" or "consultant"
    hints: Optional[dict[str, Any]] = None
    additional_context: Optional[str] = None


class KickoffResponse(BaseModel):
    """Response from kickoff endpoint."""
    run_id: UUID
    status: str = "started"
    message: str = "Validation run initiated"


class StatusResponse(BaseModel):
    """Response from status endpoint."""
    run_id: UUID
    status: str  # pending, running, paused, completed, failed
    current_phase: int
    phase_name: str
    progress: list[dict]
    hitl_pending: Optional[dict] = None
    started_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    error_message: Optional[str] = None


class HITLApproveRequest(BaseModel):
    """Request to approve/reject HITL checkpoint."""
    run_id: UUID
    checkpoint: str
    # Decision options:
    # - approved: Proceed to next phase
    # - rejected: Stop and pause workflow
    # - override_proceed: Override pivot recommendation and proceed anyway
    # - iterate: Re-run current phase with same hypothesis
    # - segment_1, segment_2, segment_3: Select alternative segment for pivot
    # - custom_segment: Custom segment hypothesis (requires feedback with details)
    decision: str = Field(
        ...,
        pattern="^(approved|rejected|override_proceed|iterate|segment_[1-9]|custom_segment)$"
    )
    feedback: Optional[str] = None
    # For segment pivot: custom segment details if decision is custom_segment
    custom_segment_data: Optional[dict] = None


class HITLApproveResponse(BaseModel):
    """Response from HITL approval endpoint."""
    status: str  # resumed, rejected, pivot, iterate
    next_phase: Optional[int] = None
    pivot_type: Optional[str] = None  # segment_pivot, value_pivot
    message: str


# -----------------------------------------------------------------------------
# Authentication
# -----------------------------------------------------------------------------

def verify_bearer_token(authorization: str = Header(...)) -> bool:
    """Verify bearer token authentication."""
    expected = os.environ.get("WEBHOOK_BEARER_TOKEN", "startupai-modal-secret-2026")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization[7:]
    if not hmac.compare_digest(token, expected):
        raise HTTPException(status_code=401, detail="Invalid bearer token")

    return True


# -----------------------------------------------------------------------------
# Supabase Client (lazy initialization)
# -----------------------------------------------------------------------------

_supabase_client = None


def get_supabase():
    """Get or create Supabase client."""
    global _supabase_client
    if _supabase_client is None:
        from supabase import create_client
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_KEY"]
        _supabase_client = create_client(url, key)
    return _supabase_client


# -----------------------------------------------------------------------------
# API Endpoints
# -----------------------------------------------------------------------------

# @story US-F01, US-FT01, US-C07, US-AB01
@web_app.post("/kickoff", response_model=KickoffResponse, status_code=202)
async def kickoff(
    request: KickoffRequest,
    background_tasks: BackgroundTasks,
    authorization: str = Header(...),
):
    """
    Start a new validation run.

    Returns 202 Accepted immediately, spawns validation in background.
    Poll /status/{run_id} for progress updates.
    """
    verify_bearer_token(authorization)

    run_id = uuid4()

    logger.info(json.dumps({
        "event": "kickoff_received",
        "run_id": str(run_id),
        "project_id": str(request.project_id),
        "user_id": str(request.user_id),
    }))

    # Create validation run record in Supabase
    supabase = get_supabase()
    supabase.table("validation_runs").insert({
        "id": str(run_id),
        "run_id": str(run_id),
        "project_id": str(request.project_id),
        "user_id": str(request.user_id),
        "status": "pending",
        "current_phase": 0,
        "phase_state": {
            "entrepreneur_input": request.entrepreneur_input,
            "session_id": str(request.session_id) if request.session_id else None,
            "conversation_transcript": request.conversation_transcript,
            "user_type": request.user_type or "founder",
            "hints": request.hints,
            "additional_context": request.additional_context,
        },
        "started_at": datetime.now(timezone.utc).isoformat(),
    }).execute()

    # Spawn the validation orchestrator asynchronously
    run_validation.spawn(str(run_id))

    return KickoffResponse(
        run_id=run_id,
        status="started",
        message="Validation run initiated. Poll /status/{run_id} for progress.",
    )


# @story US-F08, US-F09, US-F10
@web_app.get("/status/{run_id}", response_model=StatusResponse)
async def get_status(
    run_id: UUID,
    authorization: str = Header(...),
):
    """
    Get current status of a validation run.

    Reads from Supabase for instant response (no Modal container needed).
    """
    verify_bearer_token(authorization)

    supabase = get_supabase()

    # Get run record
    result = supabase.table("validation_runs").select("*").eq(
        "id", str(run_id)
    ).single().execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Validation run not found")

    run = result.data

    # Get progress records
    progress_result = supabase.table("validation_progress").select("*").eq(
        "run_id", str(run_id)
    ).order("created_at", desc=False).execute()

    progress = progress_result.data or []

    # Check for pending HITL request
    hitl_result = supabase.table("hitl_requests").select("*").eq(
        "run_id", str(run_id)
    ).eq("status", "pending").execute()

    hitl_pending = hitl_result.data[0] if hitl_result.data else None

    # Get phase name from config
    phase_names = {
        0: "Onboarding",
        1: "VPC Discovery",
        2: "Desirability",
        3: "Feasibility",
        4: "Viability",
    }
    phase_name = phase_names.get(run["current_phase"], f"Phase {run['current_phase']}")

    return StatusResponse(
        run_id=run_id,
        status=run["status"],
        current_phase=run["current_phase"],
        phase_name=phase_name,
        progress=progress,
        hitl_pending=hitl_pending,
        started_at=run.get("started_at"),
        updated_at=run.get("updated_at"),
        error_message=run.get("error_message"),
    )


# @story US-F03, US-H01, US-H02, US-H04, US-H05, US-H06, US-H07, US-H08, US-H09, US-P01, US-P02, US-P03, US-P04
@web_app.post("/hitl/approve", response_model=HITLApproveResponse)
async def hitl_approve(
    request: HITLApproveRequest,
    authorization: str = Header(...),
):
    """
    Process HITL approval/rejection and resume validation.

    Decision handling:
    - approved: Proceed to next phase (or loopback for pivot checkpoints)
    - rejected: Pause workflow for review
    - override_proceed: Override pivot recommendation and force proceed
    - iterate: Re-run current phase with same hypothesis
    """
    verify_bearer_token(authorization)

    supabase = get_supabase()

    logger.info(json.dumps({
        "event": "hitl_decision",
        "run_id": str(request.run_id),
        "checkpoint": request.checkpoint,
        "decision": request.decision,
    }))

    # Update HITL request status
    # Normalize status to valid enum: pending|approved|rejected|expired
    # Store actual decision value in 'decision' column
    if request.decision in ("rejected", "reject"):
        normalized_status = "rejected"
    elif request.decision == "iterate":
        # Iterate keeps it pending for another round
        normalized_status = "pending"
    else:
        # segment_1, segment_2, custom_segment, override_proceed, approved -> approved
        normalized_status = "approved"

    supabase.table("hitl_requests").update({
        "status": normalized_status,
        "decision": request.decision,
        "feedback": request.feedback,
        "decision_at": datetime.now(timezone.utc).isoformat(),
    }).eq("run_id", str(request.run_id)).eq(
        "checkpoint_name", request.checkpoint
    ).eq("status", "pending").execute()

    # Get current run state
    run_result = supabase.table("validation_runs").select("*").eq(
        "id", str(request.run_id)
    ).single().execute()

    if not run_result.data:
        raise HTTPException(status_code=404, detail="Validation run not found")

    run = run_result.data
    current_phase = run["current_phase"]
    phase_state = run.get("phase_state", {})

    # -------------------------------------------------------------------------
    # Handle: SEGMENT SELECTION (segment_1, segment_2, segment_3, custom_segment)
    # -------------------------------------------------------------------------
    if request.decision.startswith("segment_") or request.decision == "custom_segment":
        # This is a segment pivot with a specific segment selected
        if request.checkpoint != "approve_segment_pivot":
            raise HTTPException(
                status_code=400,
                detail="Segment selection is only valid for approve_segment_pivot checkpoint"
            )

        # Get segment alternatives from HITL request context
        hitl_result = supabase.table("hitl_requests").select("context").eq(
            "run_id", str(request.run_id)
        ).eq("checkpoint_name", request.checkpoint).single().execute()

        hitl_context = hitl_result.data.get("context", {}) if hitl_result.data else {}
        segment_alternatives = hitl_context.get("segment_alternatives", [])

        # Determine selected segment
        if request.decision == "custom_segment":
            # Custom segment from founder
            selected_segment = {
                "segment_name": request.custom_segment_data.get("segment_name") if request.custom_segment_data else request.feedback,
                "segment_description": request.custom_segment_data.get("segment_description", "") if request.custom_segment_data else "",
                "confidence": 0.5,  # Unknown confidence for custom
                "is_custom": True,
            }
        else:
            # Selected from alternatives (segment_1, segment_2, etc.)
            segment_index = int(request.decision.split("_")[1]) - 1
            if segment_index < len(segment_alternatives):
                selected_segment = segment_alternatives[segment_index]
                selected_segment["is_custom"] = False
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid segment selection: {request.decision}"
                )

        logger.info(json.dumps({
            "event": "segment_pivot_selected",
            "run_id": str(request.run_id),
            "selected_segment": selected_segment.get("segment_name"),
            "confidence": selected_segment.get("confidence"),
        }))

        # Store pivot context with selected segment for Phase 1 to use
        updated_state = {
            **phase_state,
            "pivot_type": "segment_pivot",
            "pivot_reason": request.feedback or f"Segment pivot to: {selected_segment.get('segment_name')}",
            "pivot_from_phase": current_phase,
            "target_segment_hypothesis": selected_segment,  # NEW: Phase 1 will use this
            "failed_segment": hitl_context.get("failed_segment"),
        }

        supabase.table("validation_runs").update({
            "hitl_state": None,
            "status": "running",
            "current_phase": 1,  # Loop back to Phase 1
            "phase_state": updated_state,
        }).eq("id", str(request.run_id)).execute()

        # Spawn resume function to continue from Phase 1
        resume_from_checkpoint.spawn(str(request.run_id), request.checkpoint)

        return HITLApproveResponse(
            status="pivot",
            next_phase=1,
            pivot_type="segment_pivot",
            message=f"Segment pivot approved. Targeting '{selected_segment.get('segment_name')}' in Phase 1.",
        )

    # -------------------------------------------------------------------------
    # Handle: APPROVED
    # -------------------------------------------------------------------------
    if request.decision == "approved":
        # Check if this is a pivot checkpoint (approved = loop back to Phase 1)
        # Note: segment_pivot now uses segment_* decisions above, but keep fallback
        if request.checkpoint in ("approve_segment_pivot", "approve_value_pivot"):
            # Pivot approved: Loop back to Phase 1
            pivot_type = (
                "segment_pivot" if request.checkpoint == "approve_segment_pivot"
                else "value_pivot"
            )

            # Store pivot context for Phase 1 to use
            updated_state = {
                **phase_state,
                "pivot_type": pivot_type,
                "pivot_reason": request.feedback or f"Pivot approved from Phase 2: {pivot_type}",
                "pivot_from_phase": current_phase,
            }

            supabase.table("validation_runs").update({
                "hitl_state": None,
                "status": "running",
                "current_phase": 1,  # Loop back to Phase 1
                "phase_state": updated_state,
            }).eq("id", str(request.run_id)).execute()

            # Spawn resume function to continue from Phase 1
            resume_from_checkpoint.spawn(str(request.run_id), request.checkpoint)

            return HITLApproveResponse(
                status="pivot",
                next_phase=1,
                pivot_type=pivot_type,
                message=f"Pivot approved. Returning to Phase 1 for {pivot_type.replace('_', ' ')}.",
            )
        elif request.checkpoint == "approve_brief":
            # Brief approved: Stay in Phase 1, continue to Stage B (VPC Discovery)
            # The founders_brief is already in phase_state from Stage A

            supabase.table("validation_runs").update({
                "hitl_state": None,
                "status": "running",
                # Keep current_phase at 1 - Stage B will run next
            }).eq("id", str(request.run_id)).execute()

            # Spawn resume function to continue Phase 1 Stage B
            resume_from_checkpoint.spawn(str(request.run_id), request.checkpoint)

            return HITLApproveResponse(
                status="resumed",
                next_phase=1,
                message="Brief approved. Proceeding to VPC Discovery (Stage B).",
            )
        else:
            # Standard approval: Advance to next phase
            next_phase = current_phase + 1

            supabase.table("validation_runs").update({
                "hitl_state": None,
                "status": "running",
                "current_phase": next_phase,
            }).eq("id", str(request.run_id)).execute()

            # Spawn resume function to continue from next phase
            resume_from_checkpoint.spawn(str(request.run_id), request.checkpoint)

            return HITLApproveResponse(
                status="resumed",
                next_phase=next_phase,
                message=f"Validation resumed from checkpoint '{request.checkpoint}'. Advancing to Phase {next_phase}.",
            )

    # -------------------------------------------------------------------------
    # Handle: OVERRIDE_PROCEED (ignore pivot signal, force proceed)
    # -------------------------------------------------------------------------
    elif request.decision == "override_proceed":
        next_phase = current_phase + 1

        # Store override context
        updated_state = {
            **phase_state,
            "override_applied": True,
            "override_reason": request.feedback or "Human override: proceeding despite pivot signal",
            "override_checkpoint": request.checkpoint,
        }

        supabase.table("validation_runs").update({
            "hitl_state": None,
            "status": "running",
            "current_phase": next_phase,
            "phase_state": updated_state,
        }).eq("id", str(request.run_id)).execute()

        # Spawn resume function to continue from next phase
        resume_from_checkpoint.spawn(str(request.run_id), request.checkpoint)

        return HITLApproveResponse(
            status="resumed",
            next_phase=next_phase,
            message=f"Override applied. Proceeding to Phase {next_phase} despite pivot recommendation.",
        )

    # -------------------------------------------------------------------------
    # Handle: ITERATE (re-run current phase)
    # -------------------------------------------------------------------------
    elif request.decision == "iterate":
        # Mark for iteration and re-run current phase
        updated_state = {
            **phase_state,
            "iteration_count": phase_state.get("iteration_count", 0) + 1,
            "iteration_reason": request.feedback or "Additional experiments requested",
        }

        supabase.table("validation_runs").update({
            "hitl_state": None,
            "status": "running",
            "phase_state": updated_state,
        }).eq("id", str(request.run_id)).execute()

        # Spawn resume function to re-run current phase
        resume_from_checkpoint.spawn(str(request.run_id), request.checkpoint)

        return HITLApproveResponse(
            status="iterate",
            next_phase=current_phase,
            message=f"Iteration requested. Re-running Phase {current_phase} with additional experiments.",
        )

    # -------------------------------------------------------------------------
    # Handle: REJECTED
    # -------------------------------------------------------------------------
    else:
        # Record rejection, workflow pauses
        supabase.table("validation_runs").update({
            "hitl_state": f"rejected_{request.checkpoint}",
            "status": "paused",
        }).eq("id", str(request.run_id)).execute()

        return HITLApproveResponse(
            status="rejected",
            next_phase=None,
            message=f"Checkpoint '{request.checkpoint}' rejected. Review required.",
        )


# @story US-A05
@web_app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "startupai-validation"}


# -----------------------------------------------------------------------------
# Modal Functions
# -----------------------------------------------------------------------------

@app.function(
    timeout=7200,  # 2 hours - Phase 2-4 can take 40+ minutes
    cpu=2.0,
    memory=4096,
    retries=modal.Retries(max_retries=2, initial_delay=1.0),
)
def run_validation(run_id: str):
    """
    Main validation orchestrator.

    Executes phases sequentially, checkpointing to Supabase at HITL points.
    Container terminates during HITL waits ($0 cost while waiting).
    """
    logger.info(json.dumps({
        "event": "validation_start",
        "run_id": run_id,
    }))

    supabase = get_supabase()

    # Update status to running
    supabase.table("validation_runs").update({
        "status": "running",
    }).eq("id", run_id).execute()

    try:
        # Get current state
        run_result = supabase.table("validation_runs").select("*").eq(
            "id", run_id
        ).single().execute()
        run = run_result.data

        current_phase = run["current_phase"]
        phase_state = run.get("phase_state", {})

        # Execute phases sequentially
        from src.modal_app.phases import (
            phase_0_onboarding,
            phase_1_vpc_discovery,
            phase_2_desirability,
            phase_3_feasibility,
            phase_4_viability,
        )

        phase_functions = [
            phase_0_onboarding.execute,
            phase_1_vpc_discovery.execute,
            phase_2_desirability.execute,
            phase_3_feasibility.execute,
            phase_4_viability.execute,
        ]

        for phase_num in range(current_phase, 5):
            logger.info(json.dumps({
                "event": "phase_start",
                "run_id": run_id,
                "phase": phase_num,
            }))

            # Update current phase
            supabase.table("validation_runs").update({
                "current_phase": phase_num,
            }).eq("id", run_id).execute()

            # Execute phase
            phase_result = phase_functions[phase_num](run_id, phase_state)

            # Check if HITL checkpoint was triggered
            if phase_result.get("hitl_checkpoint"):
                checkpoint = phase_result["hitl_checkpoint"]
                logger.info(json.dumps({
                    "event": "hitl_checkpoint",
                    "run_id": run_id,
                    "phase": phase_num,
                    "checkpoint": checkpoint,
                }))

                # Save state and create HITL request
                supabase.table("validation_runs").update({
                    "hitl_state": checkpoint,
                    "status": "paused",
                    "phase_state": phase_result.get("state", phase_state),
                }).eq("id", run_id).execute()

                hitl_title = phase_result.get("hitl_title", f"Approval Required: {checkpoint}")
                hitl_description = phase_result.get("hitl_description", "")
                hitl_context = phase_result.get("hitl_context", {})
                hitl_options = phase_result.get("hitl_options", [
                    {"id": "approve", "label": "Approve", "description": "Proceed to next phase"},
                    {"id": "revise", "label": "Request Revisions", "description": "Return for clarification"},
                    {"id": "reject", "label": "Reject", "description": "Stop validation"},
                ])
                hitl_recommended = phase_result.get("hitl_recommended", "approve")

                supabase.table("hitl_requests").insert({
                    "run_id": run_id,
                    "checkpoint_name": checkpoint,
                    "validation_phase": phase_num,
                    "title": hitl_title,
                    "description": hitl_description,
                    "context": hitl_context,
                    "options": hitl_options,
                    "recommended_option": hitl_recommended,
                }).execute()

                # Send webhook to create approval_requests entry in product app
                _send_hitl_webhook(
                    run_id=run_id,
                    project_id=str(run["project_id"]),
                    user_id=str(run["user_id"]),
                    checkpoint=checkpoint,
                    title=hitl_title,
                    description=hitl_description,
                    options=hitl_options,
                    recommended=hitl_recommended,
                    context=hitl_context,
                )

                # Container terminates here - $0 cost while waiting
                return {"status": "paused", "checkpoint": checkpoint}

            # Update state for next phase
            phase_state = phase_result.get("state", phase_state)

            logger.info(json.dumps({
                "event": "phase_complete",
                "run_id": run_id,
                "phase": phase_num,
            }))

        # All phases complete
        supabase.table("validation_runs").update({
            "status": "completed",
            "phase_state": phase_state,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", run_id).execute()

        logger.info(json.dumps({
            "event": "validation_complete",
            "run_id": run_id,
        }))

        # Send webhook to product app
        _send_completion_webhook(run_id, phase_state)

        return {"status": "completed"}

    except Exception as e:
        logger.error(json.dumps({
            "event": "validation_error",
            "run_id": run_id,
            "error": str(e),
        }))

        supabase.table("validation_runs").update({
            "status": "failed",
            "error_message": str(e),
        }).eq("id", run_id).execute()

        raise


@app.function(
    timeout=7200,  # 2 hours - resumed phases can run long
    cpu=2.0,
    memory=4096,
    retries=modal.Retries(max_retries=2, initial_delay=1.0),
)
def resume_from_checkpoint(run_id: str, checkpoint: str):
    """
    Resume validation from a HITL checkpoint after approval.

    Loads state from Supabase and continues execution.
    """
    logger.info(json.dumps({
        "event": "resume_from_checkpoint",
        "run_id": run_id,
        "checkpoint": checkpoint,
    }))

    # Delegate to main orchestrator
    return run_validation.local(run_id)


def _send_hitl_webhook(
    run_id: str,
    project_id: str,
    user_id: str,
    checkpoint: str,
    title: str,
    description: str,
    options: list,
    recommended: str,
    context: dict,
):
    """Send HITL checkpoint webhook to product app to create approval_requests entry."""
    import httpx
    from datetime import timedelta

    product_app_url = os.environ.get("PRODUCT_APP_URL", "https://app.startupai.site")
    webhook_url = f"{product_app_url}/api/crewai/webhook"
    bearer_token = os.environ.get("WEBHOOK_BEARER_TOKEN", "startupai-modal-secret-2026")

    # Calculate expiration (7 days from now)
    expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()

    try:
        response = httpx.post(
            webhook_url,
            json={
                "flow_type": "hitl_checkpoint",
                "run_id": run_id,
                "project_id": project_id,
                "user_id": user_id,
                "checkpoint": checkpoint,
                "title": title,
                "description": description,
                "options": options,
                "recommended": recommended,
                "context": context,
                "expires_at": expires_at,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            headers={
                "Authorization": f"Bearer {bearer_token}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
        response.raise_for_status()
        logger.info(json.dumps({
            "event": "hitl_webhook_sent",
            "run_id": run_id,
            "checkpoint": checkpoint,
            "status_code": response.status_code,
        }))
    except Exception as e:
        logger.error(json.dumps({
            "event": "hitl_webhook_failed",
            "run_id": run_id,
            "checkpoint": checkpoint,
            "error": str(e),
        }))


def _send_completion_webhook(run_id: str, final_state: dict):
    """Send completion webhook to product app."""
    import httpx

    product_app_url = os.environ.get("PRODUCT_APP_URL", "https://app.startupai.site")
    webhook_url = f"{product_app_url}/api/crewai/webhook"
    bearer_token = os.environ.get("WEBHOOK_BEARER_TOKEN", "startupai-modal-secret-2026")

    try:
        response = httpx.post(
            webhook_url,
            json={
                "flow_type": "founder_validation",
                "run_id": run_id,
                "status": "completed",
                "result": final_state,
            },
            headers={
                "Authorization": f"Bearer {bearer_token}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
        response.raise_for_status()
        logger.info(json.dumps({
            "event": "webhook_sent",
            "run_id": run_id,
            "status_code": response.status_code,
        }))
    except Exception as e:
        logger.error(json.dumps({
            "event": "webhook_failed",
            "run_id": run_id,
            "error": str(e),
        }))


# -----------------------------------------------------------------------------
# HITL Expiration Cron
# -----------------------------------------------------------------------------

@app.function(schedule=modal.Cron("0 */6 * * *"))  # Every 6 hours
def expire_stale_hitl_requests():
    """
    Expire HITL requests older than 7 days.

    Runs every 6 hours to clean up abandoned approvals.
    """
    supabase = get_supabase()

    result = supabase.table("hitl_requests").update({
        "status": "expired",
    }).eq("status", "pending").lt(
        "expires_at", datetime.now(timezone.utc).isoformat()
    ).execute()

    expired_count = len(result.data) if result.data else 0

    if expired_count > 0:
        logger.info(json.dumps({
            "event": "hitl_expired",
            "count": expired_count,
        }))

    return {"expired": expired_count}


# -----------------------------------------------------------------------------
# Mount FastAPI to Modal
# -----------------------------------------------------------------------------

@app.function()
@modal.asgi_app()
def fastapi_app():
    """Serve FastAPI app via Modal ASGI."""
    return web_app


# -----------------------------------------------------------------------------
# Test Functions
# -----------------------------------------------------------------------------

@app.function(timeout=300)
def test_netlify_deploy():
    """
    Test LandingPageDeploymentTool with a real Netlify deployment.

    Usage: modal run src/modal_app/app.py::test_netlify_deploy
    """
    import httpx
    from datetime import datetime
    from shared.tools.landing_page_deploy import LandingPageDeploymentTool

    logger.info("Starting LandingPageDeploymentTool test...")

    # Check environment
    netlify_token = os.environ.get("NETLIFY_ACCESS_TOKEN")
    if not netlify_token:
        logger.error("NETLIFY_ACCESS_TOKEN not found!")
        return {"success": False, "error": "NETLIFY_ACCESS_TOKEN not available"}

    logger.info("NETLIFY_ACCESS_TOKEN found in environment")

    # Test HTML
    test_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StartupAI Test - {test_id}</title>
    <style>
        body {{
            font-family: system-ui, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }}
        .card {{
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 32px;
        }}
        h1 {{ margin: 0 0 16px 0; }}
        .meta {{ opacity: 0.8; font-size: 14px; margin-top: 24px; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>Validate Your Startup Idea</h1>
        <p>This is a test deployment from LandingPageDeploymentTool.</p>
        <p>If you can see this page, the deployment was successful!</p>
        <div class="meta">
            Test ID: {test_id}<br>
            Deployed: {datetime.now().isoformat()}
        </div>
    </div>
</body>
</html>"""

    # Deploy
    tool = LandingPageDeploymentTool()
    logger.info(f"Deploying test landing page (test_id={test_id})...")

    result_str = tool._run(
        html=html_content,
        project_id="test-deploy",
        variant_id=f"test-{test_id}",
    )

    logger.info(f"Deployment result:\n{result_str}")

    # Parse result and verify
    if "Landing Page Deployed Successfully" in result_str:
        for line in result_str.split("\n"):
            if "**Live URL:**" in line:
                deployed_url = line.split("**Live URL:**")[1].strip()
                logger.info(f"Deployed URL: {deployed_url}")

                # Verify accessibility
                try:
                    with httpx.Client(timeout=30.0) as client:
                        response = client.get(deployed_url)
                        logger.info(f"HTTP Status: {response.status_code}")

                        if response.status_code == 200:
                            content_ok = "Validate Your Startup Idea" in response.text
                            logger.info(f"Content verified: {content_ok}")
                            return {
                                "success": True,
                                "deployed_url": deployed_url,
                                "test_id": test_id,
                                "http_status": response.status_code,
                                "content_verified": content_ok,
                            }
                        else:
                            return {
                                "success": False,
                                "deployed_url": deployed_url,
                                "error": f"HTTP {response.status_code}",
                            }
                except Exception as e:
                    return {
                        "success": False,
                        "deployed_url": deployed_url,
                        "error": f"Verification failed: {str(e)}",
                    }

    return {"success": False, "error": "Deployment failed", "result": result_str}


@app.function(timeout=60)
def diagnose_netlify_token():
    """
    Diagnose Netlify token permissions and list existing sites.

    Usage: modal run src/modal_app/app.py::diagnose_netlify_token
    """
    import httpx

    netlify_token = os.environ.get("NETLIFY_ACCESS_TOKEN")
    if not netlify_token:
        return {"success": False, "error": "NETLIFY_ACCESS_TOKEN not available"}

    headers = {
        "Authorization": f"Bearer {netlify_token}",
        "Content-Type": "application/json",
    }

    results = {}

    with httpx.Client(timeout=30.0) as client:
        # 1. Get current user info
        user_response = client.get(
            "https://api.netlify.com/api/v1/user",
            headers=headers
        )
        if user_response.status_code == 200:
            user_data = user_response.json()
            results["user"] = {
                "id": user_data.get("id"),
                "email": user_data.get("email"),
                "full_name": user_data.get("full_name"),
            }
        else:
            results["user_error"] = f"HTTP {user_response.status_code}: {user_response.text}"

        # 2. List sites
        sites_response = client.get(
            "https://api.netlify.com/api/v1/sites",
            headers=headers
        )
        if sites_response.status_code == 200:
            sites = sites_response.json()
            results["sites"] = [
                {
                    "id": s.get("id"),
                    "name": s.get("name"),
                    "url": s.get("url"),
                    "created_at": s.get("created_at"),
                }
                for s in sites[:10]  # First 10 sites
            ]
            results["total_sites"] = len(sites)
        else:
            results["sites_error"] = f"HTTP {sites_response.status_code}: {sites_response.text}"

        # 3. Check token scopes by trying to get access tokens list (admin endpoint)
        tokens_response = client.get(
            "https://api.netlify.com/api/v1/oauth/applications",
            headers=headers
        )
        results["oauth_applications_status"] = tokens_response.status_code

    return results


@app.local_entrypoint()
def main():
    """Diagnose Netlify token and test deployment."""
    print("\n" + "=" * 60)
    print("Netlify Token Diagnostic")
    print("=" * 60 + "\n")

    # First run diagnostics
    diag_result = diagnose_netlify_token.remote()

    if "user" in diag_result:
        print(f"User: {diag_result['user'].get('email')}")
        print(f"Name: {diag_result['user'].get('full_name')}")

    if "total_sites" in diag_result:
        print(f"\nTotal Sites: {diag_result['total_sites']}")
        print("\nRecent StartupAI Sites:")
        for site in diag_result.get("sites", []):
            if "startupai" in site.get("name", "").lower():
                print(f"  - {site['name']}: {site['url']}")

    print("\n" + "=" * 60)
    print("LandingPageDeploymentTool Test")
    print("=" * 60 + "\n")

    result = test_netlify_deploy.remote()

    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Deployed URL: {result['deployed_url']}")
        print(f"Test ID: {result['test_id']}")
        print(f"HTTP Status: {result['http_status']}")
        print(f"Content Verified: {result['content_verified']}")
        print(f"\nVisit: {result['deployed_url']}")
    else:
        print(f"Error: {result.get('error', 'Unknown')}")

    print("\n" + "=" * 60 + "\n")
    return result


# -----------------------------------------------------------------------------
# Local Development Entry Point
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # For local testing: modal serve src/modal_app/app.py
    print("Run with: modal serve src/modal_app/app.py")
