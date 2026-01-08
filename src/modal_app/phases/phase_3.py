"""
Phase 3: Feasibility Flow

Validates technical feasibility.

Crews (2):
    - FeasibilityBuildCrew: Technical assessment
    - FeasibilityGovernanceCrew: Feasibility gate

Agents: 5 total

HITL Checkpoints:
    - approve_feasibility_gate
"""

import json
import logging
from typing import Any

from src.state import update_progress

logger = logging.getLogger(__name__)


def execute(run_id: str, state: dict[str, Any]) -> dict[str, Any]:
    """
    Execute Phase 3: Feasibility.

    Args:
        run_id: Validation run ID
        state: Current state dict (must contain VPC from Phase 1)

    Returns:
        Updated state with Phase 3 outputs and HITL checkpoint
    """
    logger.info(json.dumps({
        "event": "phase_3_start",
        "run_id": run_id,
    }))

    # Extract required inputs
    customer_profile = state.get("customer_profile", {})
    value_map = state.get("value_map", {})

    # ==========================================================================
    # Crew 1: FeasibilityBuildCrew - Technical assessment
    # ==========================================================================

    update_progress(
        run_id=run_id,
        phase=3,
        crew="FeasibilityBuildCrew",
        status="started",
        progress_pct=0,
    )

    # Import here to avoid circular imports during Modal image build
    from src.crews.feasibility import (
        run_feasibility_build_crew,
        run_feasibility_governance_crew,
    )

    try:
        update_progress(
            run_id=run_id,
            phase=3,
            crew="FeasibilityBuildCrew",
            agent="F1",
            task="extract_feature_requirements",
            status="in_progress",
            progress_pct=10,
        )

        feasibility_evidence = run_feasibility_build_crew(
            value_map=value_map,
            customer_profile=customer_profile,
        )

        # Convert to dict if it's a Pydantic model
        feasibility_dict = (
            feasibility_evidence.model_dump(mode="json")
            if hasattr(feasibility_evidence, "model_dump")
            else feasibility_evidence
        )

        update_progress(
            run_id=run_id,
            phase=3,
            crew="FeasibilityBuildCrew",
            status="completed",
            progress_pct=60,
        )

    except Exception as e:
        logger.error(json.dumps({
            "event": "phase_3_build_error",
            "run_id": run_id,
            "error": str(e),
        }))
        update_progress(
            run_id=run_id,
            phase=3,
            crew="FeasibilityBuildCrew",
            status="failed",
            error=str(e),
        )
        raise

    # ==========================================================================
    # Crew 2: FeasibilityGovernanceCrew - Gate validation
    # ==========================================================================

    update_progress(
        run_id=run_id,
        phase=3,
        crew="FeasibilityGovernanceCrew",
        status="started",
        progress_pct=60,
    )

    try:
        # Prepare technical architecture from assessment
        technical_architecture = {
            "constraints": feasibility_dict.get("constraints", []),
            "api_costs": feasibility_dict.get("api_costs_monthly", 0),
            "infra_costs": feasibility_dict.get("infra_costs_monthly", 0),
        }

        governance_results = run_feasibility_governance_crew(
            feasibility_assessment=feasibility_dict,
            technical_architecture=technical_architecture,
        )

        update_progress(
            run_id=run_id,
            phase=3,
            crew="FeasibilityGovernanceCrew",
            status="completed",
            progress_pct=100,
        )

    except Exception as e:
        logger.error(json.dumps({
            "event": "phase_3_governance_error",
            "run_id": run_id,
            "error": str(e),
        }))
        update_progress(
            run_id=run_id,
            phase=3,
            crew="FeasibilityGovernanceCrew",
            status="failed",
            error=str(e),
        )
        raise

    # ==========================================================================
    # Determine Feasibility Signal
    # ==========================================================================

    # Get signal from evidence (default to checking core_features_feasible)
    signal_raw = feasibility_dict.get("signal")
    if signal_raw:
        signal = signal_raw.value if hasattr(signal_raw, "value") else str(signal_raw)
    else:
        # Derive signal from evidence
        core_feasible = feasibility_dict.get("core_features_feasible", True)
        downgrade_required = feasibility_dict.get("downgrade_required", False)

        if not core_feasible:
            signal = "red_impossible"
        elif downgrade_required:
            signal = "orange_constrained"
        else:
            signal = "green"

    # ==========================================================================
    # Prepare HITL Checkpoint: approve_feasibility_gate
    # ==========================================================================

    logger.info(json.dumps({
        "event": "phase_3_hitl_checkpoint",
        "run_id": run_id,
        "checkpoint": "approve_feasibility_gate",
        "signal": signal,
    }))

    # Update state with Phase 3 outputs
    updated_state = {
        **state,
        "feasibility_evidence": feasibility_dict,
        "feasibility_signal": signal,
    }

    # Determine gate readiness and recommendation
    if signal == "green":
        gate_ready = True
        recommendation = "proceed"
    elif signal == "orange_constrained":
        gate_ready = False
        recommendation = "feature_pivot"
    else:  # red_impossible
        gate_ready = False
        recommendation = "kill"

    total_monthly_cost = (
        feasibility_dict.get("api_costs_monthly", 0) +
        feasibility_dict.get("infra_costs_monthly", 0)
    )

    # Build description
    signal_display = signal.upper().replace("_", " ")
    rec_display = recommendation.upper().replace("_", " ")
    if gate_ready:
        description = (
            f"Signal: {signal_display}. "
            f"Monthly costs: ${total_monthly_cost:,.2f}. "
            "Ready for viability analysis."
        )
    else:
        description = (
            f"Signal: {signal_display}. "
            f"Monthly costs: ${total_monthly_cost:,.2f}. "
            f"Recommendation: {rec_display}"
        )

    # Return HITL checkpoint for human approval
    return {
        "state": updated_state,
        "hitl_checkpoint": "approve_feasibility_gate",
        "hitl_title": "Feasibility Assessment Complete",
        "hitl_description": description,
        "hitl_context": {
            "signal": signal,
            "core_features_feasible": feasibility_dict.get("core_features_feasible", True),
            "downgrade_required": feasibility_dict.get("downgrade_required", False),
            "downgrade_features": feasibility_dict.get("downgrade_features", []),
            "costs": {
                "api_monthly": feasibility_dict.get("api_costs_monthly", 0),
                "infra_monthly": feasibility_dict.get("infra_costs_monthly", 0),
                "total_monthly": total_monthly_cost,
            },
            "constraints": feasibility_dict.get("constraints", []),
            "recommendation": recommendation,
        },
        "hitl_options": [
            {
                "id": "approve",
                "label": "Approve",
                "description": "Proceed to Phase 4 Viability analysis",
            },
            {
                "id": "feature_pivot",
                "label": "Feature Pivot",
                "description": "Downgrade features and re-test desirability",
            },
            {
                "id": "kill",
                "label": "Kill Project",
                "description": "Technical impossibility - terminate validation",
            },
        ],
        "hitl_recommended": "approve" if gate_ready else recommendation,
    }
