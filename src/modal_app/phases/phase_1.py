"""
Phase 1: VPC Discovery Flow

Customer Profile + Value Map discovery with fit assessment.

Crews (5):
    - DiscoveryCrew: Segment discovery and research
    - CustomerProfileCrew: Jobs, Pains, Gains extraction
    - ValueDesignCrew: Pain Relievers, Gain Creators design
    - WTPCrew: Willingness-to-pay analysis
    - FitAssessmentCrew: VPC fit scoring

Agents: 18 total

HITL Checkpoints:
    - approve_experiment_plan
    - approve_pricing_test
    - approve_vpc_completion
"""

# @story US-F06, US-H01, US-H02, US-AJ02, US-AJ03

import json
import logging
from typing import Any

from src.state import update_progress

logger = logging.getLogger(__name__)


def execute(run_id: str, state: dict[str, Any]) -> dict[str, Any]:
    """
    Execute Phase 1: VPC Discovery.

    Args:
        run_id: Validation run ID
        state: Current state dict (must contain founders_brief)

    Returns:
        Updated state with Phase 1 outputs and HITL checkpoint
    """
    # Check for pivot context (segment pivot from Phase 2)
    pivot_type = state.get("pivot_type")
    target_segment = state.get("target_segment_hypothesis")
    failed_segment = state.get("failed_segment")

    logger.info(json.dumps({
        "event": "phase_1_start",
        "run_id": run_id,
        "is_pivot": pivot_type is not None,
        "pivot_type": pivot_type,
        "target_segment": target_segment.get("segment_name") if target_segment else None,
    }))

    founders_brief = state.get("founders_brief", {})

    # If this is a segment pivot, augment founder's brief with pivot context
    if pivot_type == "segment_pivot" and target_segment:
        pivot_context = {
            "is_pivot": True,
            "target_segment_hypothesis": target_segment,
            "failed_segment": failed_segment,
            "pivot_instructions": (
                f"IMPORTANT: This is a SEGMENT PIVOT. The previous customer segment "
                f"'{failed_segment}' did not show interest (low problem resonance). "
                f"\n\nYou MUST target a DIFFERENT segment: '{target_segment.get('segment_name')}'."
                f"\nDescription: {target_segment.get('segment_description', '')}"
                f"\nRationale: {target_segment.get('why_better_fit', '')}"
                f"\n\nDo NOT rediscover the same segment. Focus on the new target segment."
            ),
        }
        # Merge pivot context into founders_brief for crews to use
        founders_brief = {
            **founders_brief,
            "pivot_context": pivot_context,
        }
        logger.info(json.dumps({
            "event": "phase_1_pivot_context_applied",
            "run_id": run_id,
            "target_segment": target_segment.get("segment_name"),
        }))

    # ==========================================================================
    # Crew 1: DiscoveryCrew - Segment validation and evidence collection
    # ==========================================================================

    update_progress(
        run_id=run_id,
        phase=1,
        crew="DiscoveryCrew",
        status="started",
        progress_pct=0,
    )

    # Import here to avoid circular imports during Modal image build
    from src.crews.discovery import (
        run_discovery_crew,
        run_customer_profile_crew,
        run_value_design_crew,
        run_wtp_crew,
        run_fit_assessment_crew,
    )

    try:
        # Task: Map assumptions and collect evidence
        update_progress(
            run_id=run_id,
            phase=1,
            crew="DiscoveryCrew",
            agent="E1",
            task="map_assumptions",
            status="in_progress",
            progress_pct=5,
        )

        discovery_results = run_discovery_crew(founders_brief)

        update_progress(
            run_id=run_id,
            phase=1,
            crew="DiscoveryCrew",
            status="completed",
            progress_pct=20,
        )

    except Exception as e:
        logger.error(json.dumps({
            "event": "phase_1_discovery_error",
            "run_id": run_id,
            "error": str(e),
        }))
        update_progress(
            run_id=run_id,
            phase=1,
            crew="DiscoveryCrew",
            status="failed",
            error_message=str(e),
        )
        raise

    # ==========================================================================
    # Crew 2: CustomerProfileCrew - Jobs, Pains, Gains extraction
    # ==========================================================================

    update_progress(
        run_id=run_id,
        phase=1,
        crew="CustomerProfileCrew",
        status="started",
        progress_pct=20,
    )

    try:
        customer_profile = run_customer_profile_crew(
            founders_brief=founders_brief,
            discovery_results=discovery_results,
        )

        # Convert to dict if it's a Pydantic model
        customer_profile_dict = (
            customer_profile.model_dump(mode="json")
            if hasattr(customer_profile, "model_dump")
            else customer_profile
        )

        update_progress(
            run_id=run_id,
            phase=1,
            crew="CustomerProfileCrew",
            status="completed",
            progress_pct=40,
        )

    except Exception as e:
        logger.error(json.dumps({
            "event": "phase_1_customer_profile_error",
            "run_id": run_id,
            "error": str(e),
        }))
        update_progress(
            run_id=run_id,
            phase=1,
            crew="CustomerProfileCrew",
            status="failed",
            error_message=str(e),
        )
        raise

    # ==========================================================================
    # Crew 3: ValueDesignCrew - Pain Relievers, Gain Creators
    # ==========================================================================

    update_progress(
        run_id=run_id,
        phase=1,
        crew="ValueDesignCrew",
        status="started",
        progress_pct=40,
    )

    try:
        value_map = run_value_design_crew(
            founders_brief=founders_brief,
            customer_profile=customer_profile_dict,
        )

        # Convert to dict if it's a Pydantic model
        value_map_dict = (
            value_map.model_dump(mode="json")
            if hasattr(value_map, "model_dump")
            else value_map
        )

        update_progress(
            run_id=run_id,
            phase=1,
            crew="ValueDesignCrew",
            status="completed",
            progress_pct=60,
        )

    except Exception as e:
        logger.error(json.dumps({
            "event": "phase_1_value_design_error",
            "run_id": run_id,
            "error": str(e),
        }))
        update_progress(
            run_id=run_id,
            phase=1,
            crew="ValueDesignCrew",
            status="failed",
            error_message=str(e),
        )
        raise

    # ==========================================================================
    # Crew 4: WTPCrew - Willingness-to-pay analysis
    # ==========================================================================

    update_progress(
        run_id=run_id,
        phase=1,
        crew="WTPCrew",
        status="started",
        progress_pct=60,
    )

    try:
        wtp_results = run_wtp_crew(
            customer_profile=customer_profile_dict,
            value_map=value_map_dict,
        )

        # Convert to dict if needed
        wtp_results_dict = (
            wtp_results.model_dump(mode="json")
            if hasattr(wtp_results, "model_dump")
            else wtp_results
        )

        update_progress(
            run_id=run_id,
            phase=1,
            crew="WTPCrew",
            status="completed",
            progress_pct=80,
        )

    except Exception as e:
        logger.error(json.dumps({
            "event": "phase_1_wtp_error",
            "run_id": run_id,
            "error": str(e),
        }))
        update_progress(
            run_id=run_id,
            phase=1,
            crew="WTPCrew",
            status="failed",
            error_message=str(e),
        )
        raise

    # ==========================================================================
    # Crew 5: FitAssessmentCrew - VPC fit scoring
    # ==========================================================================

    update_progress(
        run_id=run_id,
        phase=1,
        crew="FitAssessmentCrew",
        status="started",
        progress_pct=80,
    )

    try:
        fit_assessment = run_fit_assessment_crew(
            customer_profile=customer_profile_dict,
            value_map=value_map_dict,
            wtp_results=wtp_results_dict,
        )

        # Convert to dict if needed
        fit_assessment_dict = (
            fit_assessment.model_dump(mode="json")
            if hasattr(fit_assessment, "model_dump")
            else fit_assessment
        )

        update_progress(
            run_id=run_id,
            phase=1,
            crew="FitAssessmentCrew",
            status="completed",
            progress_pct=100,
        )

    except Exception as e:
        logger.error(json.dumps({
            "event": "phase_1_fit_assessment_error",
            "run_id": run_id,
            "error": str(e),
        }))
        update_progress(
            run_id=run_id,
            phase=1,
            crew="FitAssessmentCrew",
            status="failed",
            error_message=str(e),
        )
        raise

    # ==========================================================================
    # Prepare HITL Checkpoint: approve_vpc_completion
    # ==========================================================================

    logger.info(json.dumps({
        "event": "phase_1_hitl_checkpoint",
        "run_id": run_id,
        "checkpoint": "approve_vpc_completion",
        "fit_score": fit_assessment_dict.get("fit_score", 0),
    }))

    # Update state with Phase 1 outputs
    updated_state = {
        **state,
        "customer_profile": customer_profile_dict,
        "value_map": value_map_dict,
        "wtp_results": wtp_results_dict,
        "fit_assessment": fit_assessment_dict,
    }

    # Clear pivot context after successful completion (don't carry forward)
    if "target_segment_hypothesis" in updated_state:
        # Keep record of pivot but clear the hypothesis since it's been applied
        updated_state["last_pivot"] = {
            "target_segment": updated_state.pop("target_segment_hypothesis"),
            "failed_segment": updated_state.pop("failed_segment", None),
            "pivot_type": updated_state.pop("pivot_type", None),
            "pivot_from_phase": updated_state.pop("pivot_from_phase", None),
            "pivot_reason": updated_state.pop("pivot_reason", None),
        }

    # Check if fit score meets threshold (70)
    fit_score = fit_assessment_dict.get("fit_score", 0)
    gate_ready = fit_score >= 70

    # Return HITL checkpoint for human approval
    return {
        "state": updated_state,
        "hitl_checkpoint": "approve_vpc_completion",
        "hitl_title": "VPC Discovery Complete",
        "hitl_description": (
            f"VPC fit score: {fit_score}/100. "
            f"{'Ready to proceed to Desirability validation.' if gate_ready else 'Fit score below 70 - consider iterating.'}"
        ),
        "hitl_context": {
            "fit_score": fit_score,
            "gate_ready": gate_ready,
            "was_pivot": "last_pivot" in updated_state,
            "pivot_details": updated_state.get("last_pivot"),
            "customer_profile_summary": {
                "segment": customer_profile_dict.get("segment_name", "Unknown"),
                "jobs_count": len(customer_profile_dict.get("jobs", [])),
                "pains_count": len(customer_profile_dict.get("pains", [])),
                "gains_count": len(customer_profile_dict.get("gains", [])),
            },
            "value_map_summary": {
                "products_count": len(value_map_dict.get("products_services", [])),
                "pain_relievers_count": len(value_map_dict.get("pain_relievers", [])),
                "gain_creators_count": len(value_map_dict.get("gain_creators", [])),
            },
        },
        "hitl_options": [
            {
                "id": "approve",
                "label": "Approve",
                "description": "Proceed to Phase 2 Desirability validation",
            },
            {
                "id": "iterate",
                "label": "Iterate",
                "description": "Re-run discovery with refined hypotheses",
            },
            {
                "id": "segment_pivot",
                "label": "Segment Pivot",
                "description": "Target a different customer segment",
            },
        ],
        "hitl_recommended": "approve" if gate_ready else "iterate",
    }
