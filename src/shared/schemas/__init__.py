"""
Pydantic schemas for crew outputs.

These schemas define the expected output structure from each crew.
Used for validation and type safety.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class CrewOutput(BaseModel):
    """Base class for all crew outputs."""

    crew_name: str
    phase: int
    execution_time_ms: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BriefGenerationCrewOutput(CrewOutput):
    """Output from BriefGenerationCrew (Phase 1 Stage A)."""

    crew_name: str = "BriefGenerationCrew"
    phase: int = 1

    founders_brief: dict[str, Any]
    legitimacy_report: dict[str, Any]


class DiscoveryCrewOutput(CrewOutput):
    """Output from DiscoveryCrew (Phase 1)."""

    crew_name: str = "DiscoveryCrew"
    phase: int = 1

    segments_discovered: list[dict[str, Any]]
    primary_segment: str
    segment_rationale: str


class CustomerProfileCrewOutput(CrewOutput):
    """Output from CustomerProfileCrew (Phase 1)."""

    crew_name: str = "CustomerProfileCrew"
    phase: int = 1

    jobs: list[dict[str, Any]]
    pains: list[dict[str, Any]]
    gains: list[dict[str, Any]]


class ValueDesignCrewOutput(CrewOutput):
    """Output from ValueDesignCrew (Phase 1)."""

    crew_name: str = "ValueDesignCrew"
    phase: int = 1

    products_services: list[dict[str, Any]]
    pain_relievers: list[dict[str, Any]]
    gain_creators: list[dict[str, Any]]


class FitAssessmentCrewOutput(CrewOutput):
    """Output from FitAssessmentCrew (Phase 1)."""

    crew_name: str = "FitAssessmentCrew"
    phase: int = 1

    fit_score: int
    fit_status: str
    gate_ready: bool
    blockers: list[str] = Field(default_factory=list)


class BuildCrewOutput(CrewOutput):
    """Output from BuildCrew (Phase 2/3)."""

    crew_name: str = "BuildCrew"

    # Phase 2: Campaign assets
    landing_page_url: Optional[str] = None
    ad_creatives: list[dict[str, Any]] = Field(default_factory=list)

    # Phase 3: Technical assessment
    feasibility_assessment: Optional[dict[str, Any]] = None


class GrowthCrewOutput(CrewOutput):
    """Output from GrowthCrew (Phase 2)."""

    crew_name: str = "GrowthCrew"
    phase: int = 2

    campaign_metrics: dict[str, Any]
    conversion_funnel: dict[str, Any]
    experiments: list[dict[str, Any]]


class GovernanceCrewOutput(CrewOutput):
    """Output from GovernanceCrew (Phase 2/3/4)."""

    crew_name: str = "GovernanceCrew"

    gate_passed: bool
    gate_decision: str
    issues: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class FinanceCrewOutput(CrewOutput):
    """Output from FinanceCrew (Phase 4)."""

    crew_name: str = "FinanceCrew"
    phase: int = 4

    unit_economics: dict[str, Any]
    market_sizing: dict[str, Any]
    pricing_analysis: dict[str, Any]


class SynthesisCrewOutput(CrewOutput):
    """Output from SynthesisCrew (Phase 4)."""

    crew_name: str = "SynthesisCrew"
    phase: int = 4

    evidence_summary: dict[str, Any]
    decision_recommendation: str
    decision_rationale: str
    confidence_score: float
    pivot_recommendation: Optional[str] = None
