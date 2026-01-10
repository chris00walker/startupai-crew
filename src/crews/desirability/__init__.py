# Desirability crews (Phase 2)
import json
import logging
from typing import Any

from src.crews.desirability.build_crew import BuildCrew
from src.crews.desirability.growth_crew import GrowthCrew
from src.crews.desirability.governance_crew import GovernanceCrew
from src.state.models import DesirabilityEvidence

logger = logging.getLogger(__name__)


def run_build_crew(
    value_proposition: dict[str, Any],
    customer_profile: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute BuildCrew to create landing pages and testable artifacts.

    Args:
        value_proposition: The value proposition from Phase 1
        customer_profile: The customer profile from Phase 1

    Returns:
        Build results with landing page URLs and designs
    """
    crew = BuildCrew()
    result = crew.crew().kickoff(
        inputs={
            "value_proposition": value_proposition,
            "customer_profile": customer_profile,
        }
    )
    return result.raw if hasattr(result, "raw") else str(result)


def run_growth_crew(
    ad_concepts: dict[str, Any],
    landing_pages: dict[str, Any],
    customer_pains: list[str],
    value_proposition: dict[str, Any],
) -> DesirabilityEvidence:
    """
    Execute GrowthCrew to run ad campaigns and compute desirability signals.

    Args:
        ad_concepts: Ad creative concepts from BuildCrew
        landing_pages: Landing page URLs
        customer_pains: Customer pain points
        value_proposition: Value proposition

    Returns:
        DesirabilityEvidence with problem_resonance and zombie_ratio
    """
    try:
        crew = GrowthCrew()
        result = crew.crew().kickoff(
            inputs={
                "ad_concepts": ad_concepts,
                "landing_pages": landing_pages,
                "customer_pains": customer_pains,
                "value_proposition": value_proposition,
            }
        )

        # Try to get Pydantic model first
        if hasattr(result, "pydantic") and result.pydantic is not None:
            logger.info(json.dumps({
                "event": "growth_crew_success",
                "has_pydantic": True,
            }))
            return result.pydantic

        # Fall back to raw output and try to parse
        raw = result.raw if hasattr(result, "raw") else str(result)
        logger.warning(json.dumps({
            "event": "growth_crew_no_pydantic",
            "raw_type": type(raw).__name__,
            "raw_preview": str(raw)[:200] if raw else "empty",
        }))

        # Try to parse raw as JSON and construct DesirabilityEvidence
        if isinstance(raw, str) and raw.strip().startswith("{"):
            try:
                data = json.loads(raw)
                return DesirabilityEvidence(**data)
            except (json.JSONDecodeError, TypeError) as parse_error:
                logger.error(json.dumps({
                    "event": "growth_crew_parse_error",
                    "error": str(parse_error),
                }))

        # Return default evidence with low signal (triggers NO_INTEREST)
        # Low problem_resonance triggers segment pivot HITL
        logger.warning(json.dumps({
            "event": "growth_crew_fallback_evidence",
            "reason": f"Failed to parse crew output: {str(raw)[:100]}",
        }))
        return DesirabilityEvidence(
            problem_resonance=0.1,  # Below 30% threshold - will trigger segment pivot
            zombie_ratio=0.9,
        )

    except Exception as e:
        logger.error(json.dumps({
            "event": "growth_crew_error",
            "error": str(e),
        }))
        # Return default evidence on error (triggers NO_INTEREST signal)
        # This ensures the flow continues rather than crashing
        return DesirabilityEvidence(
            problem_resonance=0.1,
            zombie_ratio=0.9,
        )


def run_governance_crew(
    activities: dict[str, Any],
    creative_assets: dict[str, Any],
    experiment_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute GovernanceCrew for QA, security review, and audit.

    Args:
        activities: Validation activities to review
        creative_assets: Creative assets for QA
        experiment_data: Experiment data for security review

    Returns:
        Governance results with compliance reports
    """
    crew = GovernanceCrew()
    result = crew.crew().kickoff(
        inputs={
            "activities": activities,
            "creative_assets": creative_assets,
            "experiment_data": experiment_data,
        }
    )
    return result.raw if hasattr(result, "raw") else str(result)


__all__ = [
    "BuildCrew",
    "GrowthCrew",
    "GovernanceCrew",
    "run_build_crew",
    "run_growth_crew",
    "run_governance_crew",
]
