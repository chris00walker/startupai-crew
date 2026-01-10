"""
Supabase persistence layer for validation state.

Implements checkpoint/resume pattern for Modal serverless functions.
$0 cost during HITL waits - containers terminate after checkpointing.
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Optional, Any
from uuid import UUID

from .models import ValidationRunState, HITLCheckpoint

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Supabase Client
# -----------------------------------------------------------------------------

_supabase_client = None


def get_supabase():
    """Get or create Supabase client (lazy initialization)."""
    global _supabase_client
    if _supabase_client is None:
        from supabase import create_client
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_KEY"]
        _supabase_client = create_client(url, key)
    return _supabase_client


# -----------------------------------------------------------------------------
# State Checkpoint/Resume
# -----------------------------------------------------------------------------

def checkpoint_state(
    run_id: str,
    state: ValidationRunState,
    hitl_checkpoint: Optional[str] = None,
) -> bool:
    """
    Checkpoint validation state to Supabase.

    Called before HITL wait or at phase boundaries.
    Enables container termination with $0 cost during human review.

    Args:
        run_id: Validation run ID
        state: Current validation state
        hitl_checkpoint: Optional HITL checkpoint name (pauses execution)

    Returns:
        True if checkpoint successful
    """
    supabase = get_supabase()

    try:
        # Serialize state to JSON
        state_json = state.model_dump(mode="json")

        update_data = {
            "phase_state": state_json,
            "current_phase": state.current_phase,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        if hitl_checkpoint:
            update_data["hitl_state"] = hitl_checkpoint
            update_data["hitl_checkpoint_at"] = datetime.now(timezone.utc).isoformat()
            update_data["status"] = "paused"
        else:
            update_data["status"] = "running"

        supabase.table("validation_runs").update(update_data).eq(
            "id", run_id
        ).execute()

        logger.info(json.dumps({
            "event": "state_checkpointed",
            "run_id": run_id,
            "phase": state.current_phase,
            "hitl_checkpoint": hitl_checkpoint,
        }))

        return True

    except Exception as e:
        logger.error(json.dumps({
            "event": "checkpoint_failed",
            "run_id": run_id,
            "error": str(e),
        }))
        return False


def resume_state(run_id: str) -> Optional[ValidationRunState]:
    """
    Resume validation state from Supabase.

    Called when container restarts after HITL approval.

    Args:
        run_id: Validation run ID

    Returns:
        ValidationRunState if found, None otherwise
    """
    supabase = get_supabase()

    try:
        result = supabase.table("validation_runs").select("*").eq(
            "id", run_id
        ).single().execute()

        if not result.data:
            logger.warning(f"No state found for run_id: {run_id}")
            return None

        run_data = result.data
        phase_state = run_data.get("phase_state", {})

        # Handle case where phase_state is the full ValidationRunState
        if "run_id" in phase_state:
            state = ValidationRunState(**phase_state)
        else:
            # Legacy format or partial state
            state = ValidationRunState(
                run_id=UUID(run_id),
                project_id=UUID(run_data["project_id"]),
                user_id=UUID(run_data["user_id"]),
                current_phase=run_data["current_phase"],
                status=run_data["status"],
                entrepreneur_input=phase_state.get("entrepreneur_input", ""),
                **{k: v for k, v in phase_state.items() if k != "entrepreneur_input"}
            )

        logger.info(json.dumps({
            "event": "state_resumed",
            "run_id": run_id,
            "phase": state.current_phase,
        }))

        return state

    except Exception as e:
        logger.error(json.dumps({
            "event": "resume_failed",
            "run_id": run_id,
            "error": str(e),
        }))
        return None


# -----------------------------------------------------------------------------
# Progress Updates
# -----------------------------------------------------------------------------

def update_progress(
    run_id: str,
    phase: int,
    crew: str,
    task: Optional[str] = None,
    agent: Optional[str] = None,
    status: str = "started",
    progress_pct: Optional[int] = None,
    output: Optional[dict] = None,
    error_message: Optional[str] = None,
    duration_ms: Optional[int] = None,
) -> bool:
    """
    Update progress for real-time UI updates via Supabase Realtime.

    Progress records are append-only for instant UI subscription.

    Args:
        run_id: Validation run ID
        phase: Phase number (0-4)
        crew: Crew name
        task: Task name (optional)
        agent: Agent name (optional)
        status: Status (started, in_progress, completed, failed, skipped)
        progress_pct: Progress percentage (0-100)
        output: Task output (optional)
        error_message: Error message if failed
        duration_ms: Execution duration in milliseconds

    Returns:
        True if update successful
    """
    supabase = get_supabase()

    try:
        supabase.table("validation_progress").insert({
            "run_id": run_id,
            "phase": phase,
            "crew": crew,
            "task": task,
            "agent": agent,
            "status": status,
            "progress_pct": progress_pct,
            "output": output,
            "error_message": error_message,
            "duration_ms": duration_ms,
        }).execute()

        return True

    except Exception as e:
        logger.error(json.dumps({
            "event": "progress_update_failed",
            "run_id": run_id,
            "error": str(e),
        }))
        return False


# -----------------------------------------------------------------------------
# HITL Requests
# -----------------------------------------------------------------------------

def create_hitl_request(
    run_id: str,
    checkpoint: HITLCheckpoint,
) -> Optional[str]:
    """
    Create a HITL approval request in Supabase.

    Container terminates after this - $0 cost during human review.

    Args:
        run_id: Validation run ID
        checkpoint: HITL checkpoint details

    Returns:
        HITL request ID if created, None on error
    """
    supabase = get_supabase()

    try:
        # Bug #9 fix: Cancel any existing pending HITL for this checkpoint
        # Uses 'expired' status (not 'cancelled' - not in CHECK constraint)
        cancel_result = supabase.table("hitl_requests").update({
            "status": "expired",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("run_id", run_id).eq(
            "checkpoint_name", checkpoint.checkpoint_name
        ).eq("status", "pending").execute()

        if cancel_result.data:
            logger.info(json.dumps({
                "event": "hitl_expired_for_new",
                "run_id": run_id,
                "checkpoint": checkpoint.checkpoint_name,
                "expired_count": len(cancel_result.data),
            }))

        result = supabase.table("hitl_requests").insert({
            "run_id": run_id,
            "checkpoint_name": checkpoint.checkpoint_name,
            "phase": checkpoint.phase,
            "title": checkpoint.title,
            "description": checkpoint.description,
            "context": checkpoint.context,
            "options": checkpoint.options,
            "recommended_option": checkpoint.recommended_option,
        }).execute()

        hitl_id = result.data[0]["id"] if result.data else None

        logger.info(json.dumps({
            "event": "hitl_request_created",
            "run_id": run_id,
            "hitl_id": hitl_id,
            "checkpoint": checkpoint.checkpoint_name,
        }))

        return hitl_id

    except Exception as e:
        logger.error(json.dumps({
            "event": "hitl_request_failed",
            "run_id": run_id,
            "error": str(e),
        }))
        return None


def get_hitl_decision(run_id: str, checkpoint_name: str) -> Optional[dict]:
    """
    Get HITL decision for a checkpoint.

    Called after container resumes to check approval status.

    Args:
        run_id: Validation run ID
        checkpoint_name: Checkpoint name

    Returns:
        Decision dict with status, decision, feedback, or None if not found
    """
    supabase = get_supabase()

    try:
        result = supabase.table("hitl_requests").select(
            "status", "decision", "feedback", "decision_at", "decision_by"
        ).eq("run_id", run_id).eq("checkpoint_name", checkpoint_name).execute()

        if not result.data:
            return None

        return result.data[0]

    except Exception as e:
        logger.error(json.dumps({
            "event": "get_hitl_decision_failed",
            "run_id": run_id,
            "checkpoint": checkpoint_name,
            "error": str(e),
        }))
        return None


# -----------------------------------------------------------------------------
# Webhook Helpers
# -----------------------------------------------------------------------------

def send_webhook(
    run_id: str,
    event_type: str,
    payload: dict[str, Any],
) -> bool:
    """
    Send webhook to product app.

    Args:
        run_id: Validation run ID
        event_type: Event type (e.g., "phase_complete", "hitl_required", "validation_complete")
        payload: Event payload

    Returns:
        True if webhook sent successfully
    """
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
                "event_type": event_type,
                **payload,
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
            "event_type": event_type,
            "status_code": response.status_code,
        }))

        return True

    except Exception as e:
        logger.error(json.dumps({
            "event": "webhook_failed",
            "run_id": run_id,
            "event_type": event_type,
            "error": str(e),
        }))
        return False
