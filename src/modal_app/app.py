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
from typing import Optional
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
    """Request to start a new validation run."""
    project_id: UUID
    user_id: UUID
    entrepreneur_input: str = Field(..., min_length=10)
    session_id: Optional[UUID] = None


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
    decision: str = Field(..., pattern="^(approved|rejected)$")
    feedback: Optional[str] = None


class HITLApproveResponse(BaseModel):
    """Response from HITL approval endpoint."""
    status: str  # resumed, rejected
    next_phase: Optional[int] = None
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
        "project_id": str(request.project_id),
        "user_id": str(request.user_id),
        "status": "pending",
        "current_phase": 0,
        "phase_state": {
            "entrepreneur_input": request.entrepreneur_input,
            "session_id": str(request.session_id) if request.session_id else None,
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


@web_app.post("/hitl/approve", response_model=HITLApproveResponse)
async def hitl_approve(
    request: HITLApproveRequest,
    authorization: str = Header(...),
):
    """
    Process HITL approval/rejection and resume validation.

    On approval: Spawns new container to continue from checkpoint.
    On rejection: Records decision, may trigger pivot flow.
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
    supabase.table("hitl_requests").update({
        "status": request.decision,
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

    if request.decision == "approved":
        # Advance to next phase after HITL approval
        next_phase = current_phase + 1

        # Clear HITL state, advance phase, and resume
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
    else:
        # Record rejection, workflow will handle pivot logic
        supabase.table("validation_runs").update({
            "hitl_state": f"rejected_{request.checkpoint}",
            "status": "paused",
        }).eq("id", str(request.run_id)).execute()

        return HITLApproveResponse(
            status="rejected",
            next_phase=None,
            message=f"Checkpoint '{request.checkpoint}' rejected. Review required.",
        )


@web_app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "startupai-validation"}


# -----------------------------------------------------------------------------
# Modal Functions
# -----------------------------------------------------------------------------

@app.function(
    timeout=3600,  # 1 hour max per orchestration cycle
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

                supabase.table("hitl_requests").insert({
                    "run_id": run_id,
                    "checkpoint_name": checkpoint,
                    "phase": phase_num,
                    "title": phase_result.get("hitl_title", f"Approval Required: {checkpoint}"),
                    "description": phase_result.get("hitl_description", ""),
                    "context": phase_result.get("hitl_context", {}),
                    "options": phase_result.get("hitl_options"),
                    "recommended_option": phase_result.get("hitl_recommended"),
                }).execute()

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
    timeout=3600,
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
# Local Development Entry Point
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # For local testing: modal serve src/modal_app/app.py
    print("Run with: modal serve src/modal_app/app.py")
