"""
Pydantic models for validation state management.

These models are serialized to JSON and stored in Supabase for checkpoint/resume.
Based on the VPD (Value Proposition Design) framework by Osterwalder/Pigneur.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field


# -----------------------------------------------------------------------------
# Enums
# -----------------------------------------------------------------------------

class ValidationSignal(str, Enum):
    """Validation signal strengths for Innovation Physics routing."""

    # Desirability signals
    NO_INTEREST = "no_interest"
    MILD_INTEREST = "mild_interest"
    STRONG_COMMITMENT = "strong_commitment"

    # Feasibility signals
    GREEN = "green"
    ORANGE_CONSTRAINED = "orange_constrained"
    RED_IMPOSSIBLE = "red_impossible"

    # Viability signals
    PROFITABLE = "profitable"
    MARGINAL = "marginal"
    UNDERWATER = "underwater"


class PivotRecommendation(str, Enum):
    """Pivot recommendations from Innovation Physics routing."""

    NO_PIVOT = "no_pivot"
    SEGMENT_PIVOT = "segment_pivot"  # Wrong customer segment
    VALUE_PIVOT = "value_pivot"  # Wrong value proposition
    FEATURE_PIVOT = "feature_pivot"  # Feature downgrade needed
    STRATEGIC_PIVOT = "strategic_pivot"  # Unit economics failure
    KILL = "kill"  # Fundamental issues, recommend stopping


class JobType(str, Enum):
    """Types of customer jobs (VPD framework).

    Four job types per Osterwalder/Pigneur VPD:
    - Functional: Tasks to complete
    - Emotional: How they want to feel
    - Social: How they want to be perceived
    - Supporting: Buyer, co-creator, transferrer roles
    """

    FUNCTIONAL = "functional"
    SOCIAL = "social"
    EMOTIONAL = "emotional"
    SUPPORTING = "supporting"  # Buyer, co-creator, transferrer jobs


class PainSeverity(str, Enum):
    """Severity levels for customer pains."""

    EXTREME = "extreme"
    SEVERE = "severe"
    MODERATE = "moderate"
    MILD = "mild"


class GainRelevance(str, Enum):
    """Relevance levels for customer gains (VPD Kano model).

    Four levels per Osterwalder/Pigneur VPD:
    - Essential: Required gains (must-haves)
    - Expected: Baseline gains (standard expectations)
    - Nice-to-have: Desired gains (differentiation)
    - Unexpected: Delighter gains (wow factor)
    """

    ESSENTIAL = "essential"  # Required, must-have gains
    EXPECTED = "expected"  # Baseline expectations
    NICE_TO_HAVE = "nice_to_have"  # Desired, would be nice
    UNEXPECTED = "unexpected"  # Delighters, wow factor


class ValidationStatus(str, Enum):
    """Validation status for VPC elements."""

    VALIDATED = "validated"
    INVALIDATED = "invalidated"
    UNTESTED = "untested"


class EvidenceType(str, Enum):
    """Evidence types in SAY vs DO hierarchy."""

    # DO evidence (stronger)
    SKIN_IN_GAME = "skin_in_game"  # Money, time, reputation committed
    BEHAVIOR = "behavior"  # Observed actions
    CTA_CLICKS = "cta_clicks"  # Click-through actions

    # SAY evidence (weaker)
    VERBAL_COMMITMENT = "verbal_commitment"
    SURVEY_RESPONSE = "survey_response"
    INTERVIEW_STATEMENT = "interview_statement"


# -----------------------------------------------------------------------------
# Founder's Brief (Phase 0 Output)
# -----------------------------------------------------------------------------

class AssumptionCategory(str, Enum):
    """Categories for business assumptions."""

    CUSTOMER = "customer"
    PROBLEM = "problem"
    SOLUTION = "solution"
    BUSINESS_MODEL = "business_model"


class Assumption(BaseModel):
    """A testable assumption about the business."""

    assumption: str
    category: AssumptionCategory = AssumptionCategory.PROBLEM
    risk_level: str = Field(..., pattern="^(high|medium|low)$")
    how_to_test: str = ""
    testable: bool = True
    tested: bool = False
    validated: Optional[bool] = None


class TheIdea(BaseModel):
    """The founder's core business idea."""

    one_liner: str
    description: str
    inspiration: str = ""
    unique_insight: str = ""


class ProblemHypothesis(BaseModel):
    """Hypothesis about the problem being solved (NOT VALIDATED)."""

    problem_statement: str
    who_has_this_problem: str
    frequency: str = ""
    current_alternatives: str = ""
    why_alternatives_fail: str = ""
    evidence_of_problem: Optional[str] = None
    validation_status: str = "HYPOTHESIS - NOT VALIDATED"


class CustomerHypothesis(BaseModel):
    """Hypothesis about the target customer (NOT VALIDATED)."""

    primary_segment: str
    segment_description: str = ""
    characteristics: list[str] = Field(default_factory=list)
    where_to_find_them: str = ""
    estimated_size: Optional[str] = None
    validation_status: str = "HYPOTHESIS - NOT VALIDATED"


class SolutionHypothesis(BaseModel):
    """Hypothesis about the proposed solution (NOT VALIDATED)."""

    proposed_solution: str
    key_features: list[str] = Field(default_factory=list)
    differentiation: str = ""
    unfair_advantage: Optional[str] = None
    validation_status: str = "HYPOTHESIS - NOT VALIDATED"


class SuccessCriteria(BaseModel):
    """Criteria for validation success."""

    minimum_viable_signal: str = ""
    deal_breakers: list[str] = Field(default_factory=list)
    target_metrics: dict[str, str] = Field(default_factory=dict)
    problem_resonance_target: float = 0.50
    zombie_ratio_max: float = 0.30
    fit_score_target: int = 70


class FounderContext(BaseModel):
    """Context about the founder and their situation."""

    founder_background: str = ""
    motivation: str = ""
    time_commitment: str = "exploring"  # full_time, part_time, exploring
    resources_available: str = ""


class QAStatus(BaseModel):
    """Quality assurance status from validation agents."""

    legitimacy_check: str = "pending"  # pass, fail, needs_review
    legitimacy_notes: str = ""
    intent_verification: str = "pending"  # pass, fail, needs_followup
    intent_notes: str = ""
    overall_status: str = "pending"  # approved, rejected, pending


class InterviewMetadata(BaseModel):
    """Metadata about the interview process."""

    interview_duration_minutes: int = 0
    interview_turns: int = 0
    followup_questions_asked: int = 0
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)


class FoundersBrief(BaseModel):
    """
    Founder's Brief captured during Phase 0 onboarding.

    This is the PRIME ARTIFACT from Phase 0 that informs all downstream phases.
    All hypotheses are marked as NOT VALIDATED until tested in subsequent phases.
    """

    # Identity (optional - populated at runtime)
    brief_id: Optional[str] = None
    founder_id: Optional[str] = None
    session_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    version: int = 1

    # The Idea
    the_idea: TheIdea

    # Hypotheses (NOT validated - captured for testing)
    problem_hypothesis: ProblemHypothesis
    customer_hypothesis: CustomerHypothesis
    solution_hypothesis: SolutionHypothesis

    # Assumptions & Success
    key_assumptions: list[Assumption] = Field(default_factory=list)
    success_criteria: SuccessCriteria = Field(default_factory=SuccessCriteria)

    # Founder Context
    founder_context: FounderContext = Field(default_factory=FounderContext)

    # QA Status
    qa_status: QAStatus = Field(default_factory=QAStatus)

    # Metadata
    metadata: InterviewMetadata = Field(default_factory=InterviewMetadata)

    # Legacy fields (for backward compatibility)
    @property
    def concept(self) -> str:
        """Legacy accessor for concept."""
        return self.the_idea.description

    @property
    def one_liner(self) -> str:
        """Legacy accessor for one_liner."""
        return self.the_idea.one_liner

    @property
    def concept_legitimacy(self) -> str:
        """Legacy accessor for concept_legitimacy."""
        return self.qa_status.legitimacy_check

    @property
    def intent_verification(self) -> str:
        """Legacy accessor for intent_verification."""
        return self.qa_status.intent_verification


# -----------------------------------------------------------------------------
# Customer Profile (VPD - Right Side of Canvas)
# -----------------------------------------------------------------------------

class CustomerJob(BaseModel):
    """A customer job from the VPD Customer Profile."""

    id: str
    job_statement: str  # "When [situation], I want to [motivation] so I can [outcome]"
    job_type: JobType
    priority: int = Field(ge=1, le=10)
    importance_score: Optional[float] = None
    validation_status: ValidationStatus = ValidationStatus.UNTESTED
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    evidence_ids: list[str] = Field(default_factory=list)


class CustomerPain(BaseModel):
    """A customer pain from the VPD Customer Profile."""

    id: str
    pain_statement: str
    severity: PainSeverity
    priority: int = Field(ge=1, le=10)
    validation_status: ValidationStatus = ValidationStatus.UNTESTED
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    evidence_ids: list[str] = Field(default_factory=list)


class CustomerGain(BaseModel):
    """A customer gain from the VPD Customer Profile."""

    id: str
    gain_statement: str
    relevance: GainRelevance
    priority: int = Field(ge=1, le=10)
    validation_status: ValidationStatus = ValidationStatus.UNTESTED
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    evidence_ids: list[str] = Field(default_factory=list)


class CustomerProfile(BaseModel):
    """
    VPD Customer Profile (right side of Value Proposition Canvas).

    Contains Jobs, Pains, and Gains for a customer segment.
    """

    segment_name: str
    segment_description: str

    jobs: list[CustomerJob] = Field(default_factory=list)
    pains: list[CustomerPain] = Field(default_factory=list)
    gains: list[CustomerGain] = Field(default_factory=list)

    # Aggregate metrics
    jobs_validated: int = 0
    pains_validated: int = 0
    gains_validated: int = 0


# -----------------------------------------------------------------------------
# Value Map (VPD - Left Side of Canvas)
# -----------------------------------------------------------------------------

class ProductService(BaseModel):
    """A product/service from the VPD Value Map."""

    id: str
    name: str
    description: str
    addresses_jobs: list[str] = Field(default_factory=list)  # Job IDs


class PainReliever(BaseModel):
    """A pain reliever from the VPD Value Map."""

    id: str
    description: str
    addresses_pain_id: str
    effectiveness: str = Field(..., pattern="^(eliminates|reduces|none)$")
    validation_status: ValidationStatus = ValidationStatus.UNTESTED
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)


class GainCreator(BaseModel):
    """A gain creator from the VPD Value Map."""

    id: str
    description: str
    addresses_gain_id: str
    effectiveness: str = Field(..., pattern="^(exceeds|meets|misses)$")
    validation_status: ValidationStatus = ValidationStatus.UNTESTED
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)


class ValueMap(BaseModel):
    """
    VPD Value Map (left side of Value Proposition Canvas).

    Contains Products/Services, Pain Relievers, and Gain Creators.
    """

    products_services: list[ProductService] = Field(default_factory=list)
    pain_relievers: list[PainReliever] = Field(default_factory=list)
    gain_creators: list[GainCreator] = Field(default_factory=list)


# -----------------------------------------------------------------------------
# Fit Assessment (VPD - Canvas Alignment)
# -----------------------------------------------------------------------------

class FitAssessment(BaseModel):
    """
    Assessment of fit between Customer Profile and Value Map.

    Fit score must be >= 70 to proceed from Phase 1 to Phase 2.
    """

    fit_score: int = Field(ge=0, le=100)
    fit_status: str = Field(..., pattern="^(strong|moderate|weak|none)$")

    # Coverage metrics
    profile_completeness: float = Field(ge=0.0, le=1.0)
    value_map_coverage: float = Field(ge=0.0, le=1.0)

    # Evidence strength
    evidence_strength: str = Field(..., pattern="^(strong|weak|none)$")
    experiments_run: int = 0
    experiments_passed: int = 0

    # Gate readiness
    gate_ready: bool = False
    blockers: list[str] = Field(default_factory=list)


# -----------------------------------------------------------------------------
# Evidence Models
# -----------------------------------------------------------------------------

class Experiment(BaseModel):
    """A validation experiment (Test Card + Learning Card)."""

    id: str
    experiment_type: str  # landing_page, ad_test, interview, prototype_test
    tbi_experiment_id: Optional[str] = None  # e.g., "T1.1"

    # Test Card
    hypothesis: str
    test_description: str
    metric: str
    success_criteria: str

    # Learning Card (after execution)
    observation: Optional[str] = None
    learning: Optional[str] = None
    decisions_actions: Optional[str] = None

    # Results
    passed: Optional[bool] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    sample_size: Optional[int] = None
    evidence_type: Optional[EvidenceType] = None  # SAY vs DO

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class DesirabilityEvidence(BaseModel):
    """Evidence collected during Phase 2 Desirability validation."""

    # Ad campaign metrics
    ad_impressions: int = 0
    ad_clicks: int = 0
    ad_signups: int = 0
    ad_spend: float = 0.0

    # Conversion funnel
    landing_page_visitors: int = 0
    cta_clicks: int = 0
    signups: int = 0

    # Key metrics
    problem_resonance: float = Field(0.0, ge=0.0, le=1.0)
    zombie_ratio: float = Field(0.0, ge=0.0, le=1.0)
    conversion_rate: float = Field(0.0, ge=0.0, le=1.0)

    # Signal derivation
    commitment_type: Optional[EvidenceType] = None
    signal: Optional[ValidationSignal] = None

    # Experiments
    experiments: list[Experiment] = Field(default_factory=list)


class FeasibilityEvidence(BaseModel):
    """Evidence collected during Phase 3 Feasibility validation."""

    # Technical assessment
    core_features_feasible: bool = True
    downgrade_required: bool = False
    downgrade_features: list[str] = Field(default_factory=list)

    # Cost estimates
    api_costs_monthly: float = 0.0
    infra_costs_monthly: float = 0.0
    total_monthly_cost: float = 0.0

    # Timeline
    mvp_weeks: Optional[int] = None
    full_product_weeks: Optional[int] = None

    # Signal
    signal: Optional[ValidationSignal] = None
    constraints: list[str] = Field(default_factory=list)


class ViabilityEvidence(BaseModel):
    """Evidence collected during Phase 4 Viability validation."""

    # Unit economics
    cac: float = 0.0  # Customer Acquisition Cost
    ltv: float = 0.0  # Lifetime Value
    ltv_cac_ratio: float = 0.0
    payback_months: Optional[int] = None

    # Pricing
    target_price: float = 0.0
    willingness_to_pay: float = 0.0
    price_sensitivity: Optional[float] = None

    # Market sizing
    tam_usd: float = 0.0  # Total Addressable Market
    sam_usd: float = 0.0  # Serviceable Addressable Market
    som_usd: float = 0.0  # Serviceable Obtainable Market

    # Margins
    gross_margin: float = 0.0

    # Signal
    signal: Optional[ValidationSignal] = None
    unit_economics_status: str = "unknown"  # profitable, marginal, underwater


# -----------------------------------------------------------------------------
# HITL Checkpoint
# -----------------------------------------------------------------------------

class HITLCheckpoint(BaseModel):
    """A Human-in-the-Loop checkpoint."""

    checkpoint_name: str
    phase: int
    title: str
    description: str

    # Context for decision
    context: dict[str, Any] = Field(default_factory=dict)

    # Decision options
    options: Optional[list[dict[str, str]]] = None
    recommended_option: Optional[str] = None

    # Decision (filled after human input)
    decision: Optional[str] = None
    feedback: Optional[str] = None
    decided_by: Optional[UUID] = None
    decided_at: Optional[datetime] = None


# -----------------------------------------------------------------------------
# Phase State
# -----------------------------------------------------------------------------

class PhaseState(BaseModel):
    """State for a single phase."""

    phase_number: int
    phase_name: str
    status: str = "pending"  # pending, running, completed, failed

    # Timestamps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Outputs (phase-specific)
    outputs: dict[str, Any] = Field(default_factory=dict)

    # HITL checkpoints encountered
    hitl_checkpoints: list[HITLCheckpoint] = Field(default_factory=list)


# -----------------------------------------------------------------------------
# Full Validation Run State
# -----------------------------------------------------------------------------

class ValidationRunState(BaseModel):
    """
    Complete state for a validation run.

    Serialized to JSON and stored in Supabase for checkpoint/resume.
    """

    # Identity
    run_id: UUID
    project_id: UUID
    user_id: UUID
    session_id: Optional[UUID] = None

    # Execution state
    current_phase: int = 0
    status: str = "pending"  # pending, running, paused, completed, failed
    hitl_state: Optional[str] = None

    # Input
    entrepreneur_input: str
    founders_brief: Optional[FoundersBrief] = None

    # Phase 1: VPC Discovery
    customer_profile: Optional[CustomerProfile] = None
    value_map: Optional[ValueMap] = None
    fit_assessment: Optional[FitAssessment] = None

    # Phase 2: Desirability
    desirability_evidence: Optional[DesirabilityEvidence] = None
    desirability_signal: Optional[ValidationSignal] = None

    # Phase 3: Feasibility
    feasibility_evidence: Optional[FeasibilityEvidence] = None
    feasibility_signal: Optional[ValidationSignal] = None

    # Phase 4: Viability
    viability_evidence: Optional[ViabilityEvidence] = None
    viability_signal: Optional[ValidationSignal] = None

    # Final decision
    pivot_recommendation: Optional[PivotRecommendation] = None
    final_decision: Optional[str] = None  # proceed, pivot, kill
    decision_rationale: Optional[str] = None

    # Phase states (for detailed tracking)
    phase_states: list[PhaseState] = Field(default_factory=list)

    # Timestamps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Error tracking
    error_message: Optional[str] = None
    retry_count: int = 0
