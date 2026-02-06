"""
Phase 1: VPC Discovery Flow

Two-stage architecture (Quick Start flow):

Stage A - Brief Generation:
    - BriefGenerationCrew: Generate Founder's Brief from raw_idea + hints
    - HITL: approve_brief (editable)

Stage B - VPC Discovery:
    - DiscoveryCrew: Segment discovery and research
    - CustomerProfileCrew: Jobs, Pains, Gains extraction
    - ValueDesignCrew: Pain Relievers, Gain Creators design
    - WTPCrew: Willingness-to-pay analysis
    - FitAssessmentCrew: VPC fit scoring
    - HITL: approve_discovery_output

Crews: 6 total (1 Stage A + 5 Stage B)
Agents: 20 total (2 Stage A + 18 Stage B)

Flow:
    raw_idea + hints → BriefGenerationCrew → approve_brief
        → DiscoveryCrew → CustomerProfileCrew → ValueDesignCrew
        → WTPCrew → FitAssessmentCrew → approve_discovery_output
"""

# @story US-F06, US-H01, US-H02, US-AD01, US-AH02, US-AB01, US-AD10

import json
import logging
from typing import Any

from src.state import update_progress
from src.shared.gate_policies import evaluate_gate_for_user, DEFAULT_POLICIES

logger = logging.getLogger(__name__)


def execute(run_id: str, state: dict[str, Any]) -> dict[str, Any]:
    """
    Execute Phase 1: VPC Discovery (two-stage).

    Stage A: Generate Founder's Brief from raw_idea + hints
    Stage B: Run VPC Discovery crews

    Args:
        run_id: Validation run ID
        state: Current state dict

    Returns:
        Updated state with Phase 1 outputs and HITL checkpoint
    """
    # Check for pivot context (segment pivot from Phase 2)
    pivot_type = state.get("pivot_type")
    target_segment = state.get("target_segment_hypothesis")
    failed_segment = state.get("failed_segment")

    # Check if we have a founders_brief yet
    founders_brief = state.get("founders_brief")

    logger.info(json.dumps({
        "event": "phase_1_start",
        "run_id": run_id,
        "has_founders_brief": founders_brief is not None,
        "is_pivot": pivot_type is not None,
        "pivot_type": pivot_type,
        "target_segment": target_segment.get("segment_name") if target_segment else None,
    }))

    # ==========================================================================
    # Stage A: Brief Generation (if no founders_brief yet)
    # ==========================================================================
    if not founders_brief:
        return _execute_stage_a(run_id, state)

    # ==========================================================================
    # Stage B: VPC Discovery (founders_brief exists)
    # ==========================================================================
    return _execute_stage_b(run_id, state, founders_brief)


def _execute_stage_a(run_id: str, state: dict[str, Any]) -> dict[str, Any]:
    """
    Execute Stage A: Generate Founder's Brief from raw_idea + hints.

    Args:
        run_id: Validation run ID
        state: Current state dict (must contain raw_idea)

    Returns:
        HITL checkpoint: approve_brief
    """
    logger.info(json.dumps({
        "event": "phase_1_stage_a_start",
        "run_id": run_id,
    }))

    raw_idea = state.get("entrepreneur_input", state.get("raw_idea", ""))
    hints_dict = state.get("hints", {})  # Raw dict from state (for UI via hitl_context)

    # Convert dict to human-readable string for crew template interpolation
    if isinstance(hints_dict, dict) and hints_dict:
        hints_str = "\n".join(f"- {k.replace('_', ' ').title()}: {v}" for k, v in hints_dict.items())
    else:
        hints_str = str(hints_dict) if hints_dict else ""

    update_progress(
        run_id=run_id,
        phase=1,
        crew="BriefGenerationCrew",
        status="started",
        progress_pct=0,
    )

    # Import here to avoid circular imports during Modal image build
    from src.crews.discovery import run_brief_generation_crew

    try:
        update_progress(
            run_id=run_id,
            phase=1,
            crew="BriefGenerationCrew",
            agent="GV1",
            task="validate_concept_legitimacy",
            status="in_progress",
            progress_pct=5,
        )

        founders_brief = run_brief_generation_crew(
            raw_idea=raw_idea,
            hints=hints_str,
        )

        # Convert to dict if it's a Pydantic model
        founders_brief_dict = (
            founders_brief.model_dump(mode="json")
            if hasattr(founders_brief, "model_dump")
            else founders_brief
        )

        update_progress(
            run_id=run_id,
            phase=1,
            crew="BriefGenerationCrew",
            status="completed",
            progress_pct=15,
        )

    except Exception as e:
        logger.error(json.dumps({
            "event": "phase_1_stage_a_error",
            "run_id": run_id,
            "error": str(e),
        }))
        update_progress(
            run_id=run_id,
            phase=1,
            crew="BriefGenerationCrew",
            status="failed",
            error_message=str(e),
        )
        raise

    # ==========================================================================
    # Prepare HITL Checkpoint: approve_brief
    # ==========================================================================

    logger.info(json.dumps({
        "event": "phase_1_stage_a_hitl_checkpoint",
        "run_id": run_id,
        "checkpoint": "approve_brief",
    }))

    # Update state with Founder's Brief
    updated_state = {
        **state,
        "founders_brief": founders_brief_dict,
    }

    # Return HITL checkpoint for human approval (editable brief)
    return {
        "state": updated_state,
        "hitl_checkpoint": "approve_brief",
        "hitl_title": "Review Founder's Brief",
        "hitl_description": (
            "Review and edit the AI-generated Founder's Brief before proceeding "
            "to VPC Discovery. Make any corrections needed."
        ),
        "hitl_context": {
            "founders_brief": founders_brief_dict,
            "qa_status": founders_brief_dict.get("qa_status", {}),
            "editable": True,  # Signal to UI that this brief can be edited
            "entrepreneur_input": raw_idea,  # Original input for UI comparison
            "hints": hints_dict or None,  # Structured dict for UI rendering
        },
        "hitl_options": [
            {
                "id": "approve",
                "label": "Approve Brief",
                "description": "Proceed to VPC Discovery with this brief",
            },
            {
                "id": "iterate",
                "label": "Regenerate",
                "description": "Regenerate the brief with additional context",
            },
            {
                "id": "reject",
                "label": "Reject",
                "description": "Concept fails legitimacy check - cannot proceed",
            },
        ],
        "hitl_recommended": "approve",
    }


def _execute_stage_b(
    run_id: str,
    state: dict[str, Any],
    founders_brief: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute Stage B: VPC Discovery with existing crews.

    Args:
        run_id: Validation run ID
        state: Current state dict
        founders_brief: The approved Founder's Brief

    Returns:
        HITL checkpoint: approve_discovery_output
    """
    logger.info(json.dumps({
        "event": "phase_1_stage_b_start",
        "run_id": run_id,
    }))

    # Extract pivot context from state (these live in state, not function params)
    pivot_type = state.get("pivot_type")
    target_segment = state.get("target_segment_hypothesis")
    failed_segment = state.get("failed_segment")

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
            "event": "phase_1_stage_b_pivot_context_applied",
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
    # Prepare HITL Checkpoint: approve_discovery_output
    # ==========================================================================

    logger.info(json.dumps({
        "event": "phase_1_stage_b_hitl_checkpoint",
        "run_id": run_id,
        "checkpoint": "approve_discovery_output",
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

    # Evaluate gate readiness using configurable policy
    fit_score = fit_assessment_dict.get("fit_score", 0)
    user_id = state.get("user_id")

    # Build evidence summary for gate evaluation
    evidence_summary = {
        "experiments_run": fit_assessment_dict.get("experiments_run", 0),
        "experiments_passed": fit_assessment_dict.get("experiments_passed", 0),
        "weak_evidence_count": fit_assessment_dict.get("weak_evidence_count", 0),
        "medium_evidence_count": fit_assessment_dict.get("medium_evidence_count", 0),
        "strong_evidence_count": fit_assessment_dict.get("strong_evidence_count", 0),
        "fit_score": fit_score,
    }

    if user_id:
        # Evaluate against user's custom policy (falls back to defaults if none)
        gate_result = evaluate_gate_for_user(
            user_id=user_id,
            gate="DESIRABILITY",
            evidence_summary=evidence_summary,
        )
        gate_ready = gate_result.gate_ready
        gate_blockers = gate_result.blockers
    else:
        # No user context - use hardcoded defaults for backwards compatibility
        default_policy = DEFAULT_POLICIES["DESIRABILITY"]
        gate_ready = fit_score >= default_policy.thresholds.get("fit_score", 70)
        gate_blockers = [] if gate_ready else [f"fit_score {fit_score} < 70"]

    # Return HITL checkpoint for human approval
    return {
        "state": updated_state,
        "hitl_checkpoint": "approve_discovery_output",
        "hitl_title": "VPC Discovery Complete",
        "hitl_description": (
            f"VPC fit score: {fit_score}/100. "
            f"{'Ready to proceed to Desirability validation.' if gate_ready else 'Fit score below 70 - consider iterating.'}"
        ),
        "hitl_context": {
            "fit_score": fit_score,
            "gate_ready": gate_ready,
            "gate_blockers": gate_blockers if not gate_ready else [],
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
