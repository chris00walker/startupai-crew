"""
Phase 0: Onboarding Pass-Through

Quick Start flow: Phase 0 is now a pass-through that stores the raw input
and immediately triggers Phase 1 (which handles brief generation in Stage A).

No crew execution. No HITL checkpoint.

Input:
    - entrepreneur_input (raw_idea): The founder's raw business idea
    - hints: Optional context/hints provided by the founder

Output:
    - State with raw_idea and hints stored
    - Triggers Phase 1 immediately
"""

# @story US-F01, US-FT01, US-AB01

import json
import logging
from typing import Any

from src.state import update_progress

logger = logging.getLogger(__name__)


def execute(run_id: str, state: dict[str, Any]) -> dict[str, Any]:
    """
    Execute Phase 0: Pass-through to Phase 1.

    Quick Start flow - just stores the input and returns.
    No crew execution, no HITL checkpoint.

    Args:
        run_id: Validation run ID
        state: Current state dict (contains entrepreneur_input, hints)

    Returns:
        Updated state ready for Phase 1
    """
    logger.info(json.dumps({
        "event": "phase_0_start",
        "run_id": run_id,
        "flow": "quick_start_passthrough",
    }))

    # Update progress: Phase started and completed immediately
    update_progress(
        run_id=run_id,
        phase=0,
        crew="Passthrough",
        status="started",
        progress_pct=0,
    )

    # Extract input data
    entrepreneur_input = state.get("entrepreneur_input", "")
    hints = state.get("hints", "")
    user_type = state.get("user_type", "founder")

    logger.info(json.dumps({
        "event": "phase_0_input_received",
        "run_id": run_id,
        "input_length": len(entrepreneur_input),
        "has_hints": bool(hints),
        "user_type": user_type,
    }))

    # Update progress: Completed
    update_progress(
        run_id=run_id,
        phase=0,
        crew="Passthrough",
        status="completed",
        progress_pct=100,
    )

    logger.info(json.dumps({
        "event": "phase_0_complete",
        "run_id": run_id,
        "next_phase": 1,
    }))

    # Return state - no HITL checkpoint, proceed directly to Phase 1
    # Phase 1 Stage A (BriefGenerationCrew) will handle brief generation
    return {
        "state": {
            **state,
            "entrepreneur_input": entrepreneur_input,
            "hints": hints,
            "user_type": user_type,
        },
        # No hitl_checkpoint - proceed to Phase 1 immediately
    }
