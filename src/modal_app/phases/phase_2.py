"""
Phase 2: Desirability Flow

Validates customer demand through experiments.

Crews (3):
    - BuildCrew: Landing page, ad creative generation
    - GrowthCrew: Campaign execution, analytics
    - GovernanceCrew: Spend approval, quality gates

Agents: 9 total

HITL Checkpoints:
    - approve_campaign_launch
    - approve_spend_increase
    - approve_desirability_gate (or approve_segment_pivot / approve_value_pivot)
"""

import json
import logging
from typing import Any

from src.state import update_progress
from src.modal_app.helpers.segment_alternatives import (
    generate_alternative_segments,
    format_segment_options,
)

logger = logging.getLogger(__name__)


def execute(run_id: str, state: dict[str, Any]) -> dict[str, Any]:
    """
    Execute Phase 2: Desirability.

    Args:
        run_id: Validation run ID
        state: Current state dict (must contain VPC from Phase 1)

    Returns:
        Updated state with Phase 2 outputs and HITL checkpoint
    """
    logger.info(json.dumps({
        "event": "phase_2_start",
        "run_id": run_id,
    }))

    # Extract Phase 1 outputs
    customer_profile = state.get("customer_profile", {})
    value_map = state.get("value_map", {})
    founders_brief = state.get("founders_brief", {})

    # ==========================================================================
    # Crew 1: BuildCrew - Landing pages and testable artifacts
    # ==========================================================================

    update_progress(
        run_id=run_id,
        phase=2,
        crew="BuildCrew",
        status="started",
        progress_pct=0,
    )

    # Import here to avoid circular imports during Modal image build
    from src.crews.desirability import (
        run_build_crew,
        run_growth_crew,
        run_governance_crew,
    )

    try:
        # Extract value proposition from value map
        value_proposition = {
            "products_services": value_map.get("products_services", []),
            "pain_relievers": value_map.get("pain_relievers", []),
            "gain_creators": value_map.get("gain_creators", []),
            "one_liner": founders_brief.get("the_idea", {}).get("one_liner", ""),
        }

        update_progress(
            run_id=run_id,
            phase=2,
            crew="BuildCrew",
            agent="F1",
            task="design_landing_page",
            status="in_progress",
            progress_pct=5,
        )

        build_results = run_build_crew(
            value_proposition=value_proposition,
            customer_profile=customer_profile,
        )

        # Convert to dict if needed
        build_results_dict = (
            build_results if isinstance(build_results, dict) else {"raw": str(build_results)}
        )

        update_progress(
            run_id=run_id,
            phase=2,
            crew="BuildCrew",
            status="completed",
            progress_pct=30,
        )

    except Exception as e:
        logger.error(json.dumps({
            "event": "phase_2_build_error",
            "run_id": run_id,
            "error": str(e),
        }))
        update_progress(
            run_id=run_id,
            phase=2,
            crew="BuildCrew",
            status="failed",
            error_message=str(e),
        )
        raise

    # ==========================================================================
    # Crew 2: GrowthCrew - Ad campaigns and evidence collection
    # ==========================================================================

    update_progress(
        run_id=run_id,
        phase=2,
        crew="GrowthCrew",
        status="started",
        progress_pct=30,
    )

    try:
        # Extract customer pains for ad copy
        customer_pains = [
            pain.get("pain_statement", "")
            for pain in customer_profile.get("pains", [])
        ]

        update_progress(
            run_id=run_id,
            phase=2,
            crew="GrowthCrew",
            agent="P1",
            task="create_ad_variants",
            status="in_progress",
            progress_pct=35,
        )

        desirability_evidence = run_growth_crew(
            ad_concepts=build_results_dict,
            landing_pages=build_results_dict.get("landing_pages", {}),
            customer_pains=customer_pains,
            value_proposition=value_proposition,
        )

        # Convert to dict if it's a Pydantic model
        desirability_dict = (
            desirability_evidence.model_dump(mode="json")
            if hasattr(desirability_evidence, "model_dump")
            else desirability_evidence
        )

        update_progress(
            run_id=run_id,
            phase=2,
            crew="GrowthCrew",
            status="completed",
            progress_pct=70,
        )

    except Exception as e:
        logger.error(json.dumps({
            "event": "phase_2_growth_error",
            "run_id": run_id,
            "error": str(e),
        }))
        update_progress(
            run_id=run_id,
            phase=2,
            crew="GrowthCrew",
            status="failed",
            error_message=str(e),
        )
        raise

    # ==========================================================================
    # Crew 3: GovernanceCrew - QA, security, and audit
    # ==========================================================================

    update_progress(
        run_id=run_id,
        phase=2,
        crew="GovernanceCrew",
        status="started",
        progress_pct=70,
    )

    try:
        governance_results = run_governance_crew(
            activities={"phase": 2, "crews_completed": ["BuildCrew", "GrowthCrew"]},
            creative_assets=build_results_dict,
            experiment_data=desirability_dict,
        )

        update_progress(
            run_id=run_id,
            phase=2,
            crew="GovernanceCrew",
            status="completed",
            progress_pct=100,
        )

    except Exception as e:
        logger.error(json.dumps({
            "event": "phase_2_governance_error",
            "run_id": run_id,
            "error": str(e),
        }))
        update_progress(
            run_id=run_id,
            phase=2,
            crew="GovernanceCrew",
            status="failed",
            error_message=str(e),
        )
        raise

    # ==========================================================================
    # Determine Desirability Signal
    # ==========================================================================

    problem_resonance = desirability_dict.get("problem_resonance", 0.0)
    zombie_ratio = desirability_dict.get("zombie_ratio", 1.0)

    # Signal determination per Innovation Physics
    if problem_resonance < 0.3:
        signal = "no_interest"
        recommendation = "segment_pivot"
    elif zombie_ratio >= 0.7:
        signal = "mild_interest"
        recommendation = "value_pivot"
    else:
        signal = "strong_commitment"
        recommendation = "proceed"

    # ==========================================================================
    # Signal-Based HITL Checkpoint Routing
    # ==========================================================================
    #
    # Per VPD methodology, the HITL checkpoint depends on the desirability signal:
    # - STRONG_COMMITMENT: approve_desirability_gate → proceed to Phase 3
    # - NO_INTEREST: approve_segment_pivot → loop back to Phase 1
    # - MILD_INTEREST: approve_value_pivot → loop back to Phase 1

    # Update state with Phase 2 outputs
    updated_state = {
        **state,
        "build_results": build_results_dict,
        "desirability_evidence": desirability_dict,
        "desirability_signal": signal,
        "desirability_recommendation": recommendation,
    }

    # Determine checkpoint based on signal
    if signal == "strong_commitment":
        checkpoint = "approve_desirability_gate"
        title = "Desirability Validated - Ready for Feasibility"
        description = (
            f"STRONG COMMITMENT achieved. "
            f"Problem resonance: {problem_resonance:.1%} (≥30% threshold met). "
            f"Zombie ratio: {zombie_ratio:.1%} (<70% threshold met). "
            "Customers want this. Ready to assess if we can build it."
        )
        options = [
            {
                "id": "approved",
                "label": "Proceed to Feasibility",
                "description": "Continue to Phase 3 to assess technical feasibility",
            },
            {
                "id": "iterate",
                "label": "Run More Experiments",
                "description": "Gather additional evidence before proceeding",
            },
        ]
        recommended = "approved"

    elif signal == "no_interest":
        checkpoint = "approve_segment_pivot"
        title = "Segment Pivot Recommended - Choose New Target"

        # Generate alternative segments for founder to choose from
        logger.info(json.dumps({
            "event": "generating_segment_alternatives",
            "run_id": run_id,
        }))

        alternative_segments = generate_alternative_segments(
            founders_brief=founders_brief,
            failed_segment=customer_profile,
            desirability_evidence=desirability_dict,
            num_alternatives=3,
        )

        # Format alternatives as HITL options
        options = format_segment_options(
            alternatives=alternative_segments,
            include_custom=True,
            include_override=True,
            include_iterate=True,
        )

        # Build description with alternatives summary
        if alternative_segments:
            top_segment = alternative_segments[0]
            description = (
                f"NO INTEREST signal detected. "
                f"Problem resonance: {problem_resonance:.1%} (below 30% threshold). "
                f"The target segment '{customer_profile.get('segment_name', 'Unknown')}' "
                "does not resonate with the problem.\n\n"
                f"**Recommended pivot**: {top_segment['segment_name']} "
                f"(confidence: {top_segment.get('confidence', 0):.0%})\n\n"
                "Select which customer segment to test next, or specify your own."
            )
            recommended = "segment_1"  # Recommend highest-confidence alternative
        else:
            description = (
                f"NO INTEREST signal detected. "
                f"Problem resonance: {problem_resonance:.1%} (below 30% threshold). "
                "The target customer segment does not resonate with the problem. "
                "Recommend pivoting to a different customer segment."
            )
            recommended = "custom_segment"

        # Store alternatives in state for use during pivot
        updated_state["segment_alternatives"] = alternative_segments

    else:  # mild_interest
        checkpoint = "approve_value_pivot"
        title = "Value Pivot Recommended"
        description = (
            f"MILD INTEREST signal detected. "
            f"Problem resonance: {problem_resonance:.1%} (≥30% - customers notice the problem). "
            f"Zombie ratio: {zombie_ratio:.1%} (≥70% - but they don't commit). "
            "Customers acknowledge the problem but don't take action. "
            "Recommend refining the value proposition."
        )
        options = [
            {
                "id": "approved",
                "label": "Approve Value Pivot",
                "description": "Return to Phase 1 to refine value proposition",
            },
            {
                "id": "override_proceed",
                "label": "Override - Proceed Anyway",
                "description": "Ignore signal and continue to Phase 3 (requires justification)",
            },
            {
                "id": "iterate",
                "label": "Run More Experiments",
                "description": "Gather additional evidence with current value prop",
            },
        ]
        recommended = "approved"

    logger.info(json.dumps({
        "event": "phase_2_hitl_checkpoint",
        "run_id": run_id,
        "checkpoint": checkpoint,
        "signal": signal,
        "problem_resonance": problem_resonance,
        "zombie_ratio": zombie_ratio,
        "recommendation": recommendation,
    }))

    # Build HITL context
    hitl_context = {
        "signal": signal,
        "problem_resonance": problem_resonance,
        "zombie_ratio": zombie_ratio,
        "conversion_rate": desirability_dict.get("conversion_rate", 0.0),
        "ad_metrics": {
            "impressions": desirability_dict.get("ad_impressions", 0),
            "clicks": desirability_dict.get("ad_clicks", 0),
            "signups": desirability_dict.get("ad_signups", 0),
            "spend": desirability_dict.get("ad_spend", 0.0),
        },
        "recommendation": recommendation,
        "failed_segment": customer_profile.get("segment_name", "Unknown"),
    }

    # Add segment alternatives for pivot scenarios
    if signal == "no_interest" and "segment_alternatives" in updated_state:
        hitl_context["segment_alternatives"] = updated_state["segment_alternatives"]

    # Return HITL checkpoint for human approval
    return {
        "state": updated_state,
        "hitl_checkpoint": checkpoint,
        "hitl_title": title,
        "hitl_description": description,
        "hitl_context": hitl_context,
        "hitl_options": options,
        "hitl_recommended": recommended,
    }
