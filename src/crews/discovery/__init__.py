"""
Phase 1: VPC Discovery Crews

6 crews / 20 agents for discovering customer reality and designing value.

Includes BriefGenerationCrew for Quick Start flow (Phase 1 Stage A).
"""

import json
import logging
from typing import Any, Optional

from src.crews.discovery.brief_generation_crew import BriefGenerationCrew
from src.crews.discovery.discovery_crew import DiscoveryCrew
from src.crews.discovery.customer_profile_crew import CustomerProfileCrew
from src.crews.discovery.value_design_crew import ValueDesignCrew
from src.crews.discovery.wtp_crew import WTPCrew
from src.crews.discovery.fit_assessment_crew import FitAssessmentCrew
from src.state.models import CustomerProfile, ValueMap, FitAssessment, FoundersBrief


def run_brief_generation_crew(
    raw_idea: str,
    hints: Optional[str] = None,
) -> FoundersBrief:
    """
    Execute BriefGenerationCrew to generate a Founder's Brief from raw idea.

    This is the Quick Start entry point for Phase 1 Stage A.

    Args:
        raw_idea: The founder's raw business idea
        hints: Optional context/hints provided by the founder

    Returns:
        FoundersBrief ready for HITL approval at approve_brief checkpoint
    """
    if not raw_idea or len(raw_idea.strip()) < 3:
        raise ValueError(f"raw_idea is empty or too short: '{raw_idea}'. Cannot generate brief.")

    crew = BriefGenerationCrew()
    result = crew.crew().kickoff(
        inputs={
            "raw_idea": raw_idea,
            "hints": hints or "",
        }
    )

    # Validate the generated brief references the original input
    brief_obj = result.pydantic if hasattr(result, "pydantic") and result.pydantic else result
    if hasattr(brief_obj, "model_dump"):
        brief_text = json.dumps(brief_obj.model_dump(), default=str).lower()
    else:
        brief_text = str(brief_obj).lower()
    idea_words = [w for w in raw_idea.lower().split() if len(w) > 3]
    match_count = sum(1 for w in idea_words if w in brief_text)
    if idea_words and match_count / len(idea_words) < 0.1:
        logger = logging.getLogger(__name__)
        logger.warning(
            "HALLUCINATION DETECTED: Brief has <10%% keyword overlap with input. "
            "Input: '%s', Match: %d/%d", raw_idea, match_count, len(idea_words)
        )

    return result.pydantic if hasattr(result, "pydantic") else result


def run_discovery_crew(founders_brief: dict[str, Any]) -> dict[str, Any]:
    """
    Execute DiscoveryCrew to validate segment and collect evidence.

    Args:
        founders_brief: The Founder's Brief from Phase 0

    Returns:
        Discovery results with assumptions map and evidence
    """
    crew = DiscoveryCrew()
    result = crew.crew().kickoff(inputs={"founders_brief": founders_brief})
    return result.raw if hasattr(result, "raw") else str(result)


def run_customer_profile_crew(
    founders_brief: dict[str, Any],
    discovery_results: dict[str, Any],
) -> CustomerProfile:
    """
    Execute CustomerProfileCrew to extract Jobs, Pains, Gains.

    Args:
        founders_brief: The Founder's Brief
        discovery_results: Results from DiscoveryCrew

    Returns:
        CustomerProfile with jobs, pains, gains
    """
    crew = CustomerProfileCrew()
    result = crew.crew().kickoff(
        inputs={
            "founders_brief": founders_brief,
            "discovery_results": discovery_results,
        }
    )
    return result.pydantic if hasattr(result, "pydantic") else result


def run_value_design_crew(
    founders_brief: dict[str, Any],
    customer_profile: dict[str, Any],
) -> ValueMap:
    """
    Execute ValueDesignCrew to design Pain Relievers and Gain Creators.

    Args:
        founders_brief: The Founder's Brief
        customer_profile: The Customer Profile

    Returns:
        ValueMap with pain relievers and gain creators
    """
    crew = ValueDesignCrew()
    result = crew.crew().kickoff(
        inputs={
            "founders_brief": founders_brief,
            "customer_profile": customer_profile,
        }
    )
    return result.pydantic if hasattr(result, "pydantic") else result


def run_wtp_crew(
    customer_profile: dict[str, Any],
    value_map: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute WTPCrew for willingness-to-pay analysis.

    Args:
        customer_profile: The Customer Profile
        value_map: The Value Map

    Returns:
        WTP analysis results
    """
    crew = WTPCrew()
    result = crew.crew().kickoff(
        inputs={
            "customer_profile": customer_profile,
            "value_map": value_map,
        }
    )
    return result.pydantic if hasattr(result, "pydantic") else result


def run_fit_assessment_crew(
    customer_profile: dict[str, Any],
    value_map: dict[str, Any],
    wtp_results: dict[str, Any],
) -> FitAssessment:
    """
    Execute FitAssessmentCrew to score VPC fit.

    Args:
        customer_profile: The Customer Profile
        value_map: The Value Map
        wtp_results: WTP analysis results

    Returns:
        FitAssessment with fit score
    """
    crew = FitAssessmentCrew()
    result = crew.crew().kickoff(
        inputs={
            "customer_profile": customer_profile,
            "value_map": value_map,
            "wtp_results": wtp_results,
        }
    )
    return result.pydantic if hasattr(result, "pydantic") else result


__all__ = [
    "BriefGenerationCrew",
    "DiscoveryCrew",
    "CustomerProfileCrew",
    "ValueDesignCrew",
    "WTPCrew",
    "FitAssessmentCrew",
    "run_brief_generation_crew",
    "run_discovery_crew",
    "run_customer_profile_crew",
    "run_value_design_crew",
    "run_wtp_crew",
    "run_fit_assessment_crew",
]
