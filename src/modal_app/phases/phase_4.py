"""
Phase 4: Viability Flow

Validates unit economics and makes final decision.

Crews (3):
    - FinanceCrew: CAC/LTV, pricing, market sizing
    - SynthesisCrew: Evidence synthesis, decision recommendation
    - ViabilityGovernanceCrew: Final gate, decision approval

Agents: 9 total

HITL Checkpoints:
    - approve_viability_gate
    - approve_pivot
    - approve_proceed
    - request_human_decision
"""

# @story US-H08, US-H09, US-P04, US-AJ06, US-AJ07

import json
import logging
from typing import Any

from src.state import update_progress

logger = logging.getLogger(__name__)


def execute(run_id: str, state: dict[str, Any]) -> dict[str, Any]:
    """
    Execute Phase 4: Viability.

    Args:
        run_id: Validation run ID
        state: Current state dict (must contain all prior phase outputs)

    Returns:
        Updated state with Phase 4 outputs and final decision
    """
    logger.info(json.dumps({
        "event": "phase_4_start",
        "run_id": run_id,
    }))

    # Extract required inputs from prior phases
    founders_brief = state.get("founders_brief", {})
    customer_profile = state.get("customer_profile", {})
    value_map = state.get("value_map", {})
    wtp_results = state.get("wtp_results", {})
    desirability_evidence = state.get("desirability_evidence", {})
    feasibility_evidence = state.get("feasibility_evidence", {})

    # ==========================================================================
    # Crew 1: FinanceCrew - Unit economics calculation
    # ==========================================================================

    update_progress(
        run_id=run_id,
        phase=4,
        crew="FinanceCrew",
        status="started",
        progress_pct=0,
    )

    # Import here to avoid circular imports during Modal image build
    from src.crews.viability import (
        run_finance_crew,
        run_synthesis_crew,
        run_viability_governance_crew,
    )

    try:
        # Prepare pricing data from WTP results
        pricing_data = {
            "target_price": wtp_results.get("target_price", 0),
            "willingness_to_pay": wtp_results.get("willingness_to_pay", 0),
            "price_sensitivity": wtp_results.get("price_sensitivity", 0),
        }

        # Derive business model from founders brief
        solution = founders_brief.get("solution_hypothesis", {})
        business_model = solution.get("business_model", "saas_b2b_smb")

        update_progress(
            run_id=run_id,
            phase=4,
            crew="FinanceCrew",
            agent="L1",
            task="calculate_cac",
            status="in_progress",
            progress_pct=10,
        )

        viability_evidence = run_finance_crew(
            experiment_data=desirability_evidence,
            desirability_evidence=desirability_evidence,
            pricing_data=pricing_data,
            business_model=business_model,
        )

        # Convert to dict if it's a Pydantic model
        viability_dict = (
            viability_evidence.model_dump(mode="json")
            if hasattr(viability_evidence, "model_dump")
            else viability_evidence
        )

        update_progress(
            run_id=run_id,
            phase=4,
            crew="FinanceCrew",
            status="completed",
            progress_pct=40,
        )

    except Exception as e:
        logger.error(json.dumps({
            "event": "phase_4_finance_error",
            "run_id": run_id,
            "error": str(e),
        }))
        update_progress(
            run_id=run_id,
            phase=4,
            crew="FinanceCrew",
            status="failed",
            error_message=str(e),
        )
        raise

    # ==========================================================================
    # Crew 2: SynthesisCrew - Evidence synthesis and decision options
    # ==========================================================================

    update_progress(
        run_id=run_id,
        phase=4,
        crew="SynthesisCrew",
        status="started",
        progress_pct=40,
    )

    try:
        # Prepare VPC evidence summary
        vpc_evidence = {
            "customer_profile": customer_profile,
            "value_map": value_map,
            "fit_score": state.get("fit_assessment", {}).get("fit_score", 0),
        }

        synthesis_results = run_synthesis_crew(
            founders_brief=founders_brief,
            vpc_evidence=vpc_evidence,
            desirability_evidence=desirability_evidence,
            feasibility_evidence=feasibility_evidence,
            viability_evidence=viability_dict,
        )

        # Convert to dict if needed
        synthesis_dict = (
            synthesis_results if isinstance(synthesis_results, dict)
            else {"raw": str(synthesis_results)}
        )

        update_progress(
            run_id=run_id,
            phase=4,
            crew="SynthesisCrew",
            status="completed",
            progress_pct=70,
        )

    except Exception as e:
        logger.error(json.dumps({
            "event": "phase_4_synthesis_error",
            "run_id": run_id,
            "error": str(e),
        }))
        update_progress(
            run_id=run_id,
            phase=4,
            crew="SynthesisCrew",
            status="failed",
            error_message=str(e),
        )
        raise

    # ==========================================================================
    # Crew 3: ViabilityGovernanceCrew - Final audit and flywheel
    # ==========================================================================

    update_progress(
        run_id=run_id,
        phase=4,
        crew="ViabilityGovernanceCrew",
        status="started",
        progress_pct=70,
    )

    try:
        # Compile complete validation record
        validation_record = {
            "run_id": run_id,
            "phases_completed": [0, 1, 2, 3, 4],
            "founders_brief": founders_brief,
            "vpc_evidence": vpc_evidence,
            "desirability_evidence": desirability_evidence,
            "feasibility_evidence": feasibility_evidence,
            "viability_evidence": viability_dict,
        }

        all_outputs = {
            "phase_0": founders_brief,
            "phase_1": {"customer_profile": customer_profile, "value_map": value_map},
            "phase_2": desirability_evidence,
            "phase_3": feasibility_evidence,
            "phase_4": viability_dict,
        }

        learnings = synthesis_dict.get("learnings", {})

        governance_results = run_viability_governance_crew(
            validation_record=validation_record,
            all_outputs=all_outputs,
            learnings=learnings,
        )

        update_progress(
            run_id=run_id,
            phase=4,
            crew="ViabilityGovernanceCrew",
            status="completed",
            progress_pct=100,
        )

    except Exception as e:
        logger.error(json.dumps({
            "event": "phase_4_governance_error",
            "run_id": run_id,
            "error": str(e),
        }))
        update_progress(
            run_id=run_id,
            phase=4,
            crew="ViabilityGovernanceCrew",
            status="failed",
            error_message=str(e),
        )
        raise

    # ==========================================================================
    # Determine Viability Signal and Final Decision
    # ==========================================================================

    # Get viability metrics
    cac = viability_dict.get("cac", 0)
    ltv = viability_dict.get("ltv", 0)
    ltv_cac_ratio = viability_dict.get("ltv_cac_ratio", 0)
    tam = viability_dict.get("tam_usd", 0)

    # Get signal from evidence
    signal_raw = viability_dict.get("signal")
    if signal_raw:
        signal = signal_raw.value if hasattr(signal_raw, "value") else str(signal_raw)
    else:
        # Derive signal from metrics
        if ltv_cac_ratio >= 3.0:
            signal = "profitable"
        elif ltv_cac_ratio >= 1.0 and tam < 1_000_000:
            signal = "marginal"  # Zombie market
        else:
            signal = "underwater"

    # Determine pivot recommendation
    if signal == "profitable":
        pivot_recommendation = "no_pivot"
        final_decision = "proceed"
    elif signal == "marginal":
        pivot_recommendation = "strategic_pivot"
        final_decision = "pivot"
    else:  # underwater
        pivot_recommendation = "strategic_pivot"
        final_decision = "pivot"

    # ==========================================================================
    # Prepare HITL Checkpoint: request_human_decision
    # ==========================================================================

    logger.info(json.dumps({
        "event": "phase_4_hitl_checkpoint",
        "run_id": run_id,
        "checkpoint": "request_human_decision",
        "signal": signal,
        "ltv_cac_ratio": ltv_cac_ratio,
        "recommendation": final_decision,
    }))

    # Build decision rationale
    decision_rationale = _build_decision_rationale(
        desirability_evidence=desirability_evidence,
        feasibility_evidence=feasibility_evidence,
        viability_dict=viability_dict,
        signal=signal,
    )

    # Update state with Phase 4 outputs
    updated_state = {
        **state,
        "viability_evidence": viability_dict,
        "viability_signal": signal,
        "synthesis_results": synthesis_dict,
        "pivot_recommendation": pivot_recommendation,
        "final_decision": final_decision,
        "decision_rationale": decision_rationale,
    }

    gate_ready = signal == "profitable"

    # Return HITL checkpoint for human decision
    return {
        "state": updated_state,
        "hitl_checkpoint": "request_human_decision",
        "hitl_title": "Validation Complete - Final Decision Required",
        "hitl_description": (
            f"Viability signal: {signal.upper()}. "
            f"LTV:CAC ratio: {ltv_cac_ratio:.1f}x (target: ≥3.0x). "
            f"{'Business model validated - ready to proceed!' if gate_ready else 'Strategic decision required.'}"
        ),
        "hitl_context": {
            "signal": signal,
            "unit_economics": {
                "cac": cac,
                "ltv": ltv,
                "ltv_cac_ratio": ltv_cac_ratio,
                "gross_margin": viability_dict.get("gross_margin", 0),
                "payback_months": viability_dict.get("payback_months"),
            },
            "market": {
                "tam": tam,
                "sam": viability_dict.get("sam_usd", 0),
                "som": viability_dict.get("som_usd", 0),
            },
            "phase_signals": {
                "desirability": state.get("desirability_signal", "unknown"),
                "feasibility": state.get("feasibility_signal", "unknown"),
                "viability": signal,
            },
            "recommendation": final_decision,
            "rationale": decision_rationale,
        },
        "hitl_options": [
            {
                "id": "proceed",
                "label": "Proceed",
                "description": "Validation complete - move to execution",
            },
            {
                "id": "price_pivot",
                "label": "Price Pivot",
                "description": "Increase prices and re-test desirability",
            },
            {
                "id": "cost_pivot",
                "label": "Cost Pivot",
                "description": "Reduce costs and re-assess feasibility",
            },
            {
                "id": "model_pivot",
                "label": "Model Pivot",
                "description": "Change business model - return to Phase 1",
            },
            {
                "id": "kill",
                "label": "Kill Project",
                "description": "No viable path forward - capture learnings",
            },
        ],
        "hitl_recommended": "proceed" if gate_ready else "price_pivot",
    }


def _build_decision_rationale(
    desirability_evidence: dict[str, Any],
    feasibility_evidence: dict[str, Any],
    viability_dict: dict[str, Any],
    signal: str,
) -> str:
    """Build a human-readable decision rationale."""
    parts = []

    # Desirability summary
    problem_resonance = desirability_evidence.get("problem_resonance", 0)
    zombie_ratio = desirability_evidence.get("zombie_ratio", 0)
    parts.append(
        f"Desirability: {problem_resonance:.0%} problem resonance, "
        f"{zombie_ratio:.0%} zombie ratio"
    )

    # Feasibility summary
    core_feasible = feasibility_evidence.get("core_features_feasible", True)
    downgrade = feasibility_evidence.get("downgrade_required", False)
    if core_feasible and not downgrade:
        parts.append("Feasibility: GREEN - fully feasible")
    elif core_feasible and downgrade:
        parts.append("Feasibility: ORANGE - required feature downgrade")
    else:
        parts.append("Feasibility: RED - technical impossibility")

    # Viability summary
    ltv_cac = viability_dict.get("ltv_cac_ratio", 0)
    parts.append(f"Viability: {ltv_cac:.1f}x LTV/CAC ratio")

    # Final recommendation
    if signal == "profitable":
        parts.append("Recommendation: PROCEED - business model validated")
    else:
        parts.append(f"Recommendation: Strategic pivot needed ({signal})")

    return ". ".join(parts) + "."
