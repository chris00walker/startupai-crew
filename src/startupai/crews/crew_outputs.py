"""
Pydantic Output Models for CrewAI Crews.

These models define structured outputs for each crew, enabling type-safe
data flow from crews to the validation flow.

Usage:
    result = ServiceCrew().crew().kickoff(
        inputs={...},
        output_pydantic=ServiceCrewOutput
    )
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

from startupai.flows.state_schemas import (
    AssumptionCategory,
    CustomerProfile,
    ValueMap,
    CompetitorReport,
    CommitmentType,
    QAStatus,
    PivotType,
)


# =======================================================================================
# SERVICE CREW OUTPUTS (Sage)
# =======================================================================================

class Assumption(BaseModel):
    """Individual assumption to be tested"""
    assumption: str
    category: Literal["desirability", "feasibility", "viability"]
    criticality: Literal["high", "medium", "low"] = "medium"


class ServiceCrewOutput(BaseModel):
    """Output from Service Crew - Entrepreneur Brief capture"""
    business_idea: str = Field(description="Core value proposition in one sentence")
    target_segments: List[str] = Field(default_factory=list, description="Target customer segments")
    problem_statement: str = Field(default="", description="Pain points being addressed")
    solution_description: str = Field(default="", description="How the product solves the problem")
    assumptions: List[Assumption] = Field(default_factory=list, description="Critical beliefs")
    revenue_model: str = Field(default="", description="How the business will make money")


class SegmentPivotOutput(BaseModel):
    """Output from segment pivot analysis"""
    current_segment_analysis: str = Field(description="Why the current segment failed")
    new_segment: str = Field(description="Recommended alternative segment")
    segment_rationale: str = Field(description="Why this segment is better suited")
    testing_approach: str = Field(description="How to validate with new segment")


# =======================================================================================
# ANALYSIS CREW OUTPUTS (Sage)
# =======================================================================================

class CustomerJob(BaseModel):
    """Job-to-be-done for a customer"""
    job: str
    job_type: Literal["functional", "social", "emotional"] = "functional"
    importance: int = Field(ge=1, le=10, default=5)


class CustomerPain(BaseModel):
    """Customer pain point"""
    pain: str
    severity: int = Field(ge=1, le=10, default=5)


class CustomerGain(BaseModel):
    """Customer desired gain"""
    gain: str
    importance: int = Field(ge=1, le=10, default=5)


class AnalysisCustomerProfile(BaseModel):
    """Customer profile from analysis"""
    jobs: List[CustomerJob] = Field(default_factory=list)
    pains: List[CustomerPain] = Field(default_factory=list)
    gains: List[CustomerGain] = Field(default_factory=list)


class AnalysisValueMap(BaseModel):
    """Value map from analysis"""
    pain_relievers: List[str] = Field(default_factory=list)
    gain_creators: List[str] = Field(default_factory=list)
    products_services: List[str] = Field(default_factory=list)


class AnalysisCrewOutput(BaseModel):
    """Output from Analysis Crew - Customer segment analysis"""
    customer_profile: AnalysisCustomerProfile = Field(default_factory=AnalysisCustomerProfile)
    value_map: AnalysisValueMap = Field(default_factory=AnalysisValueMap)
    fit_score: float = Field(ge=0, le=1, default=0.5, description="Problem-solution fit")
    key_insights: List[str] = Field(default_factory=list)


class CompetitorAnalysisOutput(BaseModel):
    """Output from competitor analysis task"""
    direct_competitors: List[Dict[str, Any]] = Field(default_factory=list)
    indirect_competitors: List[Dict[str, Any]] = Field(default_factory=list)
    substitutes: List[str] = Field(default_factory=list)
    positioning_map: Dict[str, Any] = Field(default_factory=dict)
    market_gaps: List[str] = Field(default_factory=list)
    competitive_threats: List[str] = Field(default_factory=list)


class ValuePropIterationOutput(BaseModel):
    """Output from value proposition iteration"""
    new_value_map: AnalysisValueMap = Field(default_factory=AnalysisValueMap)
    changes_made: List[str] = Field(default_factory=list)
    expected_impact: str = ""
    testing_approach: str = ""


# =======================================================================================
# BUILD CREW OUTPUTS (Forge)
# =======================================================================================

class FeatureFeasibility(BaseModel):
    """Feasibility assessment for a single feature"""
    feature: str
    status: Literal["POSSIBLE", "CONSTRAINED", "IMPOSSIBLE"]
    constraints: List[str] = Field(default_factory=list)
    alternatives: List[str] = Field(default_factory=list)


class BuildCrewOutput(BaseModel):
    """Output from Build Crew - Feasibility assessment"""
    core_features_feasible: Dict[str, str] = Field(
        default_factory=dict,
        description="Feature -> POSSIBLE/CONSTRAINED/IMPOSSIBLE"
    )
    technical_risks: List[str] = Field(default_factory=list)
    skill_requirements: List[str] = Field(default_factory=list)
    estimated_effort: str = Field(default="", description="Effort estimate")
    downgrade_required: bool = Field(default=False)
    downgrade_impact: Optional[str] = None
    api_costs: Dict[str, float] = Field(default_factory=dict)
    infra_costs: Dict[str, float] = Field(default_factory=dict)
    total_monthly_cost: float = 0.0


class DowngradeOutput(BaseModel):
    """Output from downgrade design task"""
    downgraded_value_maps: Dict[str, AnalysisValueMap] = Field(default_factory=dict)
    removed_features: List[str] = Field(default_factory=list)
    alternative_approaches: List[str] = Field(default_factory=list)
    impact_assessment: str = ""


# =======================================================================================
# GROWTH CREW OUTPUTS (Pulse)
# =======================================================================================

class ExperimentResult(BaseModel):
    """Result of a single experiment"""
    name: str
    hypothesis: str = ""
    method: str = ""
    success_criteria: str = ""
    results: Optional[Dict[str, Any]] = None
    passed: Optional[bool] = None


class GrowthCrewOutput(BaseModel):
    """Output from Growth Crew - Desirability testing"""
    experiments: List[ExperimentResult] = Field(default_factory=list)
    problem_resonance: float = Field(ge=0, le=1, default=0.0)
    conversion_rate: float = Field(ge=0, le=1, default=0.0)
    traffic_quality: Literal["High", "Medium", "Low"] = "Low"
    commitment_depth: Literal["SKIN_IN_GAME", "VERBAL", "NONE"] = "NONE"
    key_learnings: List[str] = Field(default_factory=list)

    # Ad campaign metrics
    impressions: int = 0
    clicks: int = 0
    signups: int = 0
    spend_usd: float = 0.0


class PricingTestOutput(BaseModel):
    """Output from pricing test task"""
    acceptance_rate: float = Field(ge=0, le=1, default=0.0)
    segment_breakdown: Dict[str, float] = Field(default_factory=dict)
    objections: List[str] = Field(default_factory=list)
    value_gaps: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class DegradationTestOutput(BaseModel):
    """Output from degradation acceptance test"""
    acceptance_rate: float = Field(ge=0, le=1, default=0.0)
    essential_features: List[str] = Field(default_factory=list)
    acceptable_tradeoffs: List[str] = Field(default_factory=list)
    price_impact: str = ""
    competitive_position: str = ""


# =======================================================================================
# SYNTHESIS CREW OUTPUTS (Compass)
# =======================================================================================

class SynthesisCrewOutput(BaseModel):
    """Output from Synthesis Crew - Evidence synthesis and pivot recommendation"""
    recommendation: str = Field(description="Final recommendation")
    pivot_recommendation: PivotType = PivotType.NONE
    evidence_summary: str = Field(default="", description="Summary of all evidence")
    specific_changes: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0, le=1, default=0.5)
    next_steps: List[str] = Field(default_factory=list)


class PivotDecisionOutput(BaseModel):
    """Output from pivot decision analysis"""
    pivot_type: PivotType
    evidence_basis: List[str] = Field(default_factory=list)
    specific_changes: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)
    estimated_impact: str = ""


# =======================================================================================
# FINANCE CREW OUTPUTS (Ledger)
# =======================================================================================

class FinanceCrewOutput(BaseModel):
    """Output from Finance Crew - Viability analysis"""
    cac: float = Field(ge=0, default=0.0, description="Customer Acquisition Cost")
    ltv: float = Field(ge=0, default=0.0, description="Customer Lifetime Value")
    ltv_cac_ratio: float = Field(ge=0, default=0.0, description="LTV/CAC ratio")
    gross_margin: float = Field(ge=0, le=1, default=0.0, description="Gross margin %")
    payback_months: float = Field(ge=0, default=0.0)
    break_even_customers: int = Field(ge=0, default=0)
    tam_usd: float = Field(ge=0, default=0.0, description="Total Addressable Market")
    viability_assessment: str = Field(default="", description="Assessment summary")


class OptimizedMetricsOutput(BaseModel):
    """Output from unit economics optimization"""
    optimized_metrics: FinanceCrewOutput = Field(default_factory=FinanceCrewOutput)
    optimization_strategies: List[str] = Field(default_factory=list)
    expected_improvement: str = ""


# =======================================================================================
# GOVERNANCE CREW OUTPUTS (Guardian)
# =======================================================================================

class GovernanceCrewOutput(BaseModel):
    """Output from Governance Crew - QA and audit"""
    status: QAStatus = QAStatus.CONDITIONAL
    framework_compliance: bool = False
    logical_consistency: bool = False
    completeness: bool = False
    specific_issues: List[str] = Field(default_factory=list)
    required_changes: List[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0, le=1, default=0.5)
    improvement_areas: List[str] = Field(default_factory=list)


# =======================================================================================
# EXPORTS - Map crew names to their output models
# =======================================================================================

CREW_OUTPUT_MODELS = {
    "service": ServiceCrewOutput,
    "analysis": AnalysisCrewOutput,
    "build": BuildCrewOutput,
    "growth": GrowthCrewOutput,
    "synthesis": SynthesisCrewOutput,
    "finance": FinanceCrewOutput,
    "governance": GovernanceCrewOutput,
}
