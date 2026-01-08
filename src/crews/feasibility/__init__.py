# Feasibility crews (Phase 3)
from typing import Any

from src.crews.feasibility.build_crew import FeasibilityBuildCrew
from src.crews.feasibility.governance_crew import FeasibilityGovernanceCrew
from src.state.models import FeasibilityEvidence


def run_feasibility_build_crew(
    value_map: dict[str, Any],
    customer_profile: dict[str, Any],
) -> FeasibilityEvidence:
    """
    Execute FeasibilityBuildCrew to assess technical feasibility.

    Args:
        value_map: The Value Map from Phase 1
        customer_profile: The Customer Profile from Phase 1

    Returns:
        FeasibilityEvidence with signal and cost estimates
    """
    crew = FeasibilityBuildCrew()
    result = crew.crew().kickoff(
        inputs={
            "value_map": value_map,
            "customer_profile": customer_profile,
        }
    )
    return result.pydantic if hasattr(result, "pydantic") else result


def run_feasibility_governance_crew(
    feasibility_assessment: dict[str, Any],
    technical_architecture: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute FeasibilityGovernanceCrew for gate validation.

    Args:
        feasibility_assessment: The feasibility assessment from BuildCrew
        technical_architecture: The proposed technical architecture

    Returns:
        Governance results with gate readiness
    """
    crew = FeasibilityGovernanceCrew()
    result = crew.crew().kickoff(
        inputs={
            "feasibility_assessment": feasibility_assessment,
            "technical_architecture": technical_architecture,
        }
    )
    return result.raw if hasattr(result, "raw") else str(result)


__all__ = [
    "FeasibilityBuildCrew",
    "FeasibilityGovernanceCrew",
    "run_feasibility_build_crew",
    "run_feasibility_governance_crew",
]
