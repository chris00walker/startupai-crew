"""
Phase 0: Onboarding Flow

Two-layer architecture:
- Layer 1: "Alex" chat (Vercel AI SDK in product app) conducts conversational interview
- Layer 2: This flow validates and compiles the Founder's Brief

Crew: OnboardingCrew (4 agents)
Agents:
    - O1 (Interview Gap Analyzer): Analyzes Alex conversation for completeness
    - GV1 (Concept Validator): Legitimacy screening
    - GV2 (Intent Verification): Ensures accurate capture
    - S1 (Brief Compiler): Synthesizes into Founder's Brief

HITL Checkpoint: approve_founders_brief
"""

# @story US-F01, US-FT01, US-AB01

import json
import logging
from typing import Any

from src.state import update_progress
from src.state.models import FoundersBrief

logger = logging.getLogger(__name__)


def execute(run_id: str, state: dict[str, Any]) -> dict[str, Any]:
    """
    Execute Phase 0: Onboarding.

    Args:
        run_id: Validation run ID
        state: Current state dict

    Returns:
        Updated state with Phase 0 outputs and HITL checkpoint
    """
    logger.info(json.dumps({
        "event": "phase_0_start",
        "run_id": run_id,
    }))

    # Update progress: Phase started
    update_progress(
        run_id=run_id,
        phase=0,
        crew="OnboardingCrew",
        status="started",
        progress_pct=0,
    )

    entrepreneur_input = state.get("entrepreneur_input", "")
    conversation_transcript = state.get("conversation_transcript", "")
    user_type = state.get("user_type", "founder")

    # ==========================================================================
    # Execute OnboardingCrew
    # ==========================================================================

    # Import here to avoid circular imports during Modal image build
    from src.crews.onboarding import run_onboarding_crew

    # Task 1: Interview Gap Analysis (O1) - analyzes Alex conversation
    update_progress(
        run_id=run_id,
        phase=0,
        crew="OnboardingCrew",
        agent="O1",
        task="analyze_interview_gaps",
        status="in_progress",
        progress_pct=10,
    )

    # Task 2: Concept Validation (GV1)
    update_progress(
        run_id=run_id,
        phase=0,
        crew="OnboardingCrew",
        agent="GV1",
        task="validate_concept_legitimacy",
        status="queued",
        progress_pct=10,
    )

    # Task 3: Intent Verification (GV2)
    update_progress(
        run_id=run_id,
        phase=0,
        crew="OnboardingCrew",
        agent="GV2",
        task="verify_intent_capture",
        status="queued",
        progress_pct=10,
    )

    # Task 4: Brief Compilation (S1)
    update_progress(
        run_id=run_id,
        phase=0,
        crew="OnboardingCrew",
        agent="S1",
        task="compile_founders_brief",
        status="queued",
        progress_pct=10,
    )

    try:
        # Execute the crew - this runs all 4 agents in sequence
        # Pass both the transcript (from Alex) and extracted data
        founders_brief = run_onboarding_crew(
            entrepreneur_input=entrepreneur_input,
            conversation_transcript=conversation_transcript,
            user_type=user_type,
        )

        # Update progress after successful completion
        update_progress(
            run_id=run_id,
            phase=0,
            crew="OnboardingCrew",
            status="completed",
            progress_pct=100,
        )

    except Exception as e:
        logger.error(json.dumps({
            "event": "phase_0_crew_error",
            "run_id": run_id,
            "error": str(e),
        }))

        update_progress(
            run_id=run_id,
            phase=0,
            crew="OnboardingCrew",
            status="failed",
            progress_pct=0,
            error_message=str(e),
        )

        raise

    # ==========================================================================
    # Prepare HITL Checkpoint: approve_founders_brief
    # ==========================================================================

    logger.info(json.dumps({
        "event": "phase_0_hitl_checkpoint",
        "run_id": run_id,
        "checkpoint": "approve_founders_brief",
    }))

    # Update state with Founder's Brief
    updated_state = {
        **state,
        "founders_brief": founders_brief.model_dump(mode="json"),
    }

    # Return HITL checkpoint for human approval
    return {
        "state": updated_state,
        "hitl_checkpoint": "approve_founders_brief",
        "hitl_title": "Approve Founder's Brief",
        "hitl_description": (
            "Review the Founder's Brief to ensure it accurately captures "
            "the business idea before proceeding to VPC Discovery."
        ),
        "hitl_context": {
            "founders_brief": founders_brief.model_dump(mode="json"),
            "qa_status": {
                "legitimacy_check": founders_brief.qa_status.legitimacy_check,
                "legitimacy_notes": founders_brief.qa_status.legitimacy_notes,
                "intent_verification": founders_brief.qa_status.intent_verification,
                "intent_notes": founders_brief.qa_status.intent_notes,
                "overall_status": founders_brief.qa_status.overall_status,
            },
        },
        "hitl_options": [
            {
                "id": "approve",
                "label": "Approve",
                "description": "Proceed to VPC Discovery (Phase 1)",
            },
            {
                "id": "revise",
                "label": "Request Revisions",
                "description": "Return for clarification with specific feedback",
            },
            {
                "id": "reject",
                "label": "Reject",
                "description": "Concept fails legitimacy check - cannot proceed",
            },
        ],
        "hitl_recommended": "approve",
    }
