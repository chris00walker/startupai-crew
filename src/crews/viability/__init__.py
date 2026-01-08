# Viability crews (Phase 4)
from typing import Any

from src.crews.viability.finance_crew import FinanceCrew
from src.crews.viability.synthesis_crew import SynthesisCrew
from src.crews.viability.governance_crew import ViabilityGovernanceCrew
from src.state.models import ViabilityEvidence


def run_finance_crew(
    experiment_data: dict[str, Any],
    desirability_evidence: dict[str, Any],
    pricing_data: dict[str, Any],
    business_model: str,
) -> ViabilityEvidence:
    """
    Execute FinanceCrew to calculate unit economics.

    Args:
        experiment_data: Experiment results from Phase 2
        desirability_evidence: Desirability evidence
        pricing_data: Pricing information
        business_model: Business model type

    Returns:
        ViabilityEvidence with CAC, LTV, signals
    """
    crew = FinanceCrew()
    result = crew.crew().kickoff(
        inputs={
            "experiment_data": experiment_data,
            "desirability_evidence": desirability_evidence,
            "pricing_data": pricing_data,
            "business_model": business_model,
        }
    )
    return result.pydantic if hasattr(result, "pydantic") else result


def run_synthesis_crew(
    founders_brief: dict[str, Any],
    vpc_evidence: dict[str, Any],
    desirability_evidence: dict[str, Any],
    feasibility_evidence: dict[str, Any],
    viability_evidence: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute SynthesisCrew to synthesize evidence and propose options.

    Args:
        founders_brief: Phase 0 output
        vpc_evidence: Phase 1 output
        desirability_evidence: Phase 2 output
        feasibility_evidence: Phase 3 output
        viability_evidence: Phase 4 finance output

    Returns:
        Synthesis results with decision options
    """
    crew = SynthesisCrew()
    result = crew.crew().kickoff(
        inputs={
            "founders_brief": founders_brief,
            "vpc_evidence": vpc_evidence,
            "desirability_evidence": desirability_evidence,
            "feasibility_evidence": feasibility_evidence,
            "viability_evidence": viability_evidence,
        }
    )
    return result.raw if hasattr(result, "raw") else str(result)


def run_viability_governance_crew(
    validation_record: dict[str, Any],
    all_outputs: dict[str, Any],
    learnings: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute ViabilityGovernanceCrew for final audit and flywheel persistence.

    Args:
        validation_record: Complete validation record
        all_outputs: All phase outputs
        learnings: Captured learnings

    Returns:
        Governance results with audit trail and flywheel entry
    """
    crew = ViabilityGovernanceCrew()
    result = crew.crew().kickoff(
        inputs={
            "validation_record": validation_record,
            "all_outputs": all_outputs,
            "learnings": learnings,
        }
    )
    return result.raw if hasattr(result, "raw") else str(result)


__all__ = [
    "FinanceCrew",
    "SynthesisCrew",
    "ViabilityGovernanceCrew",
    "run_finance_crew",
    "run_synthesis_crew",
    "run_viability_governance_crew",
]
