"""
State schemas for the Innovation Physics Flow Logic.

This module defines the Pydantic models that carry signals through the validation flow,
implementing the specific decision trees from Strategyzer methodologies.

Architecture: StartupValidationState (31 fields, signal-based)
"""

from typing import List, Optional, Dict, Any, Literal
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator, HttpUrl


# =======================================================================================
# PHASE & RISK TRACKING
# =======================================================================================

class Phase(str, Enum):
    """Current phase in the gated validation process"""
    IDEATION = "ideation"
    DESIRABILITY = "desirability"
    FEASIBILITY = "feasibility"
    VIABILITY = "viability"
    VALIDATED = "validated"
    KILLED = "killed"


class RiskAxis(str, Enum):
    """Which risk dimension is currently being tested"""
    DESIRABILITY = "desirability"
    FEASIBILITY = "feasibility"
    VIABILITY = "viability"


# =======================================================================================
# INNOVATION PHYSICS SIGNALS - Core routing signals
# =======================================================================================

class ProblemFit(str, Enum):
    """Problem-Solution fit assessment from Sage"""
    UNKNOWN = "unknown"
    NO_FIT = "no_fit"           # Customer doesn't care about the problem
    PARTIAL_FIT = "partial_fit"  # Some resonance but not strong
    STRONG_FIT = "strong_fit"    # Strong problem resonance validated


class DesirabilitySignal(str, Enum):
    """Signal strength from desirability testing (Pulse)"""
    NO_SIGNAL = "no_signal"            # Not yet tested
    NO_INTEREST = "no_interest"        # Low traffic / low signup - wrong segment
    WEAK_INTEREST = "weak_interest"    # High CTR, low conversion - zombies detected
    STRONG_COMMITMENT = "strong_commitment"  # Strong signup/preorder evidence


class FeasibilitySignal(str, Enum):
    """Technical feasibility assessment (Forge)"""
    UNKNOWN = "unknown"
    GREEN = "green"                      # Feasible with current resources
    ORANGE_CONSTRAINED = "orange_constrained"  # Feasible only with scope reduction
    RED_IMPOSSIBLE = "red_impossible"     # Cannot build with any available resources


class ViabilitySignal(str, Enum):
    """Unit economics and market viability (Ledger)"""
    UNKNOWN = "unknown"
    PROFITABLE = "profitable"        # LTV > CAC with healthy margins
    UNDERWATER = "underwater"        # CAC > LTV, bleeding money
    ZOMBIE_MARKET = "zombie_market"  # CAC < LTV but TAM too small


class PivotType(str, Enum):
    """Strategic pivot options based on evidence"""
    NONE = "none"                    # No pivot needed
    SEGMENT_PIVOT = "segment_pivot"  # Wrong audience, change Customer Segment
    VALUE_PIVOT = "value_pivot"      # Wrong promise, change Value Proposition
    CHANNEL_PIVOT = "channel_pivot"  # Wrong distribution, change Channels
    PRICE_PIVOT = "price_pivot"      # Increase price (viability issue)
    COST_PIVOT = "cost_pivot"        # Reduce CAC (viability issue)
    KILL = "kill"                    # Stop project, no viable path


# =======================================================================================
# HUMAN-IN-THE-LOOP STATUS
# =======================================================================================

class HumanApprovalStatus(str, Enum):
    """HITL workflow status for pivot decisions"""
    NOT_REQUIRED = "not_required"
    PENDING = "pending"          # Waiting for human decision
    APPROVED = "approved"        # Human approved recommendation
    REJECTED = "rejected"        # Human rejected recommendation
    OVERRIDDEN = "overridden"    # Human chose different path


class ArtifactApprovalStatus(str, Enum):
    """Approval status for creative artifacts (ads, landing pages)"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"


# =======================================================================================
# EXPERIMENT PLATFORM & BUDGET
# =======================================================================================

class Platform(str, Enum):
    """Advertising/testing platforms"""
    META = "meta"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"
    GOOGLE_SEARCH = "google_search"
    GOOGLE_DISPLAY = "google_display"


# =======================================================================================
# ASSUMPTION TRACKING (preserved from original)
# =======================================================================================

class AssumptionCategory(str, Enum):
    """Three risks from Testing Business Ideas"""
    DESIRABILITY = "desirability"
    FEASIBILITY = "feasibility"
    VIABILITY = "viability"


class AssumptionStatus(str, Enum):
    """Validation status of assumptions"""
    UNTESTED = "untested"
    TESTING = "testing"
    VALIDATED = "validated"
    INVALIDATED = "invalidated"
    REVISED = "revised"


class EvidenceStrength(str, Enum):
    """Signal strength from experiments (used in experiments)"""
    STRONG = "strong"        # >60% positive signal with behavioral commitment
    WEAK = "weak"            # 30-60% positive signal or verbal only
    NONE = "none"            # <30% positive signal or negative


class CommitmentType(str, Enum):
    """Depth of customer commitment (Zombie Check)"""
    SKIN_IN_GAME = "skin_in_game"  # Money, time, or reputation committed
    VERBAL = "verbal"               # Only verbal interest, no real commitment
    NONE = "none"                   # No commitment or interest


class Assumption(BaseModel):
    """Core assumption being tested"""
    id: str
    statement: str
    category: AssumptionCategory
    priority: int = Field(ge=1, le=10)
    evidence_needed: str
    status: AssumptionStatus = AssumptionStatus.UNTESTED
    evidence_strength: Optional[EvidenceStrength] = None
    test_results: List[Dict[str, Any]] = []

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        """Priority 1-3 are critical, 4-7 are important, 8-10 are nice-to-have"""
        return v


# =======================================================================================
# CUSTOMER & MARKET MODELS (preserved from original)
# =======================================================================================

class CustomerJob(BaseModel):
    """Jobs to be Done framework"""
    functional: str      # What task are they trying to accomplish?
    emotional: str       # How do they want to feel?
    social: str          # How do they want to be perceived?
    importance: int = Field(ge=1, le=10)


class CustomerProfile(BaseModel):
    """Value Proposition Canvas - Customer Profile side"""
    segment_name: str
    jobs: List[CustomerJob]
    pains: List[str]           # Frustrations, risks, obstacles
    gains: List[str]           # Benefits, desires, requirements
    pain_intensity: Dict[str, int] = {}  # Pain -> intensity (1-10)
    gain_importance: Dict[str, int] = {}  # Gain -> importance (1-10)
    resonance_score: Optional[float] = None  # 0-1, from testing


class ValueMap(BaseModel):
    """Value Proposition Canvas - Value Map side"""
    products_services: List[str]
    pain_relievers: Dict[str, str]  # Pain -> How we relieve it
    gain_creators: Dict[str, str]   # Gain -> How we create it
    differentiators: List[str]       # What makes us unique


class CompetitorAnalysis(BaseModel):
    """Competitive positioning"""
    competitor_name: str
    strengths: List[str]
    weaknesses: List[str]
    positioning: str
    price_point: Optional[str] = None
    market_share: Optional[float] = None


class CompetitorReport(BaseModel):
    """Full competitive landscape"""
    competitors: List[CompetitorAnalysis]
    positioning_map: Dict[str, Any]  # X/Y axis positioning
    our_positioning: str
    differentiation_strategy: str


# =======================================================================================
# EXPERIMENT ARTIFACTS - Phase 1 (Desirability)
# =======================================================================================

class DesirabilityMetrics(BaseModel):
    """Metrics from a desirability experiment"""
    experiment_id: str
    platform: Platform
    ad_ids: List[str] = []
    landing_page_url: Optional[str] = None
    impressions: int = 0
    clicks: int = 0
    signups: int = 0
    spend_usd: float = 0.0
    ctr: float = 0.0               # computed: clicks / impressions
    conversion_rate: float = 0.0    # signups / clicks


class AdVariant(BaseModel):
    """Advertisement creative variant"""
    id: str
    platform: Platform
    headline: str
    body: str
    cta: str
    asset_url: Optional[str] = None

    # Creative structure fields (for learning)
    hook_type: Optional[Literal["problem-agitate-solve", "social-proof", "urgency", "testimonial", "curiosity"]] = None
    tone: Optional[Literal["direct", "playful", "premium", "technical", "empathetic"]] = None
    format: Optional[Literal["short-form", "long-form", "listicle", "question-lead"]] = None

    # Approval fields
    approval_status: ArtifactApprovalStatus = ArtifactApprovalStatus.DRAFT
    human_approval_status: HumanApprovalStatus = HumanApprovalStatus.NOT_REQUIRED
    human_comment: Optional[str] = None


class LandingPageVariant(BaseModel):
    """Landing page variant for experiments"""
    id: str
    variant_tag: str  # baseline, lite_scope, price_test_A, etc.
    preview_url: Optional[str] = None
    deployed_url: Optional[str] = None
    hosting_provider: Optional[str] = None  # vercel, netlify, etc.
    route_path: Optional[str] = None        # "/v1", "/v1-lite", etc.
    approval_status: ArtifactApprovalStatus = ArtifactApprovalStatus.DRAFT
    human_approval_status: HumanApprovalStatus = HumanApprovalStatus.NOT_REQUIRED
    human_comment: Optional[str] = None


class PlatformBudgetConfig(BaseModel):
    """Budget configuration for a single platform"""
    platform: Platform
    duration_days: int
    total_budget_usd: float
    min_impressions: int
    target_cpc_usd: Optional[float] = None
    audience_spec: Dict[str, Any] = Field(default_factory=dict)


class ExperimentRoutingConfig(BaseModel):
    """Routing configuration for experiment deployment"""
    experiment_id: Optional[str] = None
    platform_campaign_ids: Dict[str, List[str]] = Field(default_factory=dict)
    platform_budgets: List[PlatformBudgetConfig] = Field(default_factory=list)


class DesirabilityExperimentRun(BaseModel):
    """Complete desirability experiment run"""
    id: str
    downgrade_active: bool = False
    ad_variants: List[AdVariant] = Field(default_factory=list)
    landing_page_variants: List[LandingPageVariant] = Field(default_factory=list)
    routing: ExperimentRoutingConfig = Field(default_factory=ExperimentRoutingConfig)
    per_platform_metrics: List[DesirabilityMetrics] = Field(default_factory=list)
    aggregate_metrics: Optional[DesirabilityMetrics] = None
    approval_status: ArtifactApprovalStatus = ArtifactApprovalStatus.DRAFT
    guardian_issues: List[str] = Field(default_factory=list)


# =======================================================================================
# FEASIBILITY ARTIFACT - Phase 2
# =======================================================================================

class FeatureToggle(BaseModel):
    """Feature-level feasibility tracking"""
    feature_id: str
    feature_name: str
    enabled: bool = True
    complexity: int = Field(ge=1, le=10, default=5)  # 1-10
    monthly_cost_usd: float = 0.0
    dependencies: List[str] = []
    can_downgrade: bool = True


class FeasibilityArtifact(BaseModel):
    """Technical feasibility assessment output"""
    build_id: str
    mvp_url: Optional[str] = None

    # Feature-level tracking
    features: List[FeatureToggle] = []
    removed_features: List[str] = []
    retained_features: List[str] = []

    # Component-level costs
    api_costs: Dict[str, float] = {}      # {"openai": 50, "stripe": 10}
    infra_costs: Dict[str, float] = {}    # {"vercel": 20, "supabase": 25}
    total_monthly_cost_usd: float = 0.0

    technical_complexity_score: int = Field(ge=1, le=10, default=5)
    notes: Optional[str] = None


# =======================================================================================
# VIABILITY METRICS - Phase 3
# =======================================================================================

class ViabilityMetrics(BaseModel):
    """Unit economics and financial viability"""
    cac_usd: float = 0.0
    ltv_usd: float = 0.0
    ltv_cac_ratio: float = 0.0
    gross_margin_pct: float = 0.0
    tam_annual_revenue_potential_usd: float = 0.0
    monthly_churn_pct: float = 0.0
    payback_months: float = 0.0


# =======================================================================================
# EVIDENCE MODELS - Used by Flow for Phase Outputs
# =======================================================================================

class DesirabilityEvidence(BaseModel):
    """Evidence collected from desirability testing phase"""
    problem_resonance: float = 0.0  # 0-1 scale, how much the problem resonates
    conversion_rate: float = 0.0    # Signup/click rate
    commitment_depth: CommitmentType = CommitmentType.NONE
    zombie_ratio: float = 0.0       # High interest but no commitment
    experiments: List[Dict[str, Any]] = Field(default_factory=list)
    key_learnings: List[str] = Field(default_factory=list)
    tested_segments: List[str] = Field(default_factory=list)

    # Metrics from ad campaigns
    impressions: int = 0
    clicks: int = 0
    signups: int = 0
    spend_usd: float = 0.0


class FeasibilityEvidence(BaseModel):
    """Evidence collected from feasibility testing phase"""
    core_features_feasible: Dict[str, str] = Field(default_factory=dict)  # feature -> POSSIBLE/CONSTRAINED/IMPOSSIBLE
    technical_risks: List[str] = Field(default_factory=list)
    skill_requirements: List[str] = Field(default_factory=list)
    estimated_effort: Optional[str] = None
    downgrade_required: bool = False
    downgrade_impact: Optional[str] = None
    removed_features: List[str] = Field(default_factory=list)
    alternative_approaches: List[str] = Field(default_factory=list)
    monthly_cost_estimate_usd: float = 0.0


class ViabilityEvidence(BaseModel):
    """Evidence collected from viability testing phase"""
    cac: float = 0.0                # Customer Acquisition Cost
    ltv: float = 0.0                # Lifetime Value
    ltv_cac_ratio: float = 0.0      # Must be > 3 for healthy business
    gross_margin: float = 0.0       # Gross margin percentage
    payback_months: float = 0.0     # Months to recover CAC
    break_even_customers: int = 0   # Customers needed to break even
    tam_usd: float = 0.0            # Total Addressable Market
    market_share_target: float = 0.0
    viability_assessment: Optional[str] = None  # Summary assessment


# =======================================================================================
# QUALITY & GOVERNANCE
# =======================================================================================

class QAStatus(str, Enum):
    """Guardian's quality assessment"""
    PASSED = "passed"
    FAILED = "failed"
    CONDITIONAL = "conditional"  # Passed with required changes
    ESCALATED = "escalated"      # Needs human review


class QAReport(BaseModel):
    """Guardian's governance assessment"""
    status: QAStatus
    framework_compliance: bool
    logical_consistency: bool
    completeness: bool
    specific_issues: List[str] = []
    required_changes: List[str] = []
    confidence_score: float = Field(ge=0, le=1)


# =======================================================================================
# MAIN STATE: StartupValidationState (70 fields)
# =======================================================================================

class StartupValidationState(BaseModel):
    """
    Master state for Innovation Physics flow.
    70 fields organized by owner/purpose.

    This replaces the legacy ValidationState with signal-based architecture.

    Field Categories:
    - Identity & Bookkeeping (4 fields)
    - Problem/Solution Fit - Sage (5 fields)
    - Innovation Physics Signals (3 fields)
    - Desirability Artifacts - Pulse (2 fields)
    - Feasibility Artifact - Forge (1 field)
    - Viability Metrics - Ledger (1 field)
    - Pivot & Routing State (2 fields)
    - Global Human Approvals (2 fields)
    - HITL Bookkeeping (2 fields)
    - Guardian/Governance Metadata (2 fields)
    - Evidence Containers (3 fields)
    - Signal Tracking (4 fields)
    - Output Tracking (3 fields)
    - QA and Governance (2 fields)
    - HITL Workflow (3 fields)
    - Retry Logic (3 fields)
    - Legacy Compatibility (7 fields)
    - Service Crew Outputs (3 fields)
    - Analysis Crew Outputs (2 fields)
    - Growth Crew Outputs - Ad Metrics (4 fields)
    - Build Crew Outputs - Cost Estimates (3 fields)
    - Finance Crew Outputs - Unit Economics (5 fields)
    - Synthesis Crew Outputs (1 field)
    - Governance Crew Outputs (3 fields)
    """

    # =================== IDENTITY & BOOKKEEPING (8 fields) ===================
    # Note: CrewAI Flow requires 'id' field directly - cannot use property
    id: str = Field(default_factory=lambda: f"val_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    project_id: str = ""  # Will be synced with id in validator
    user_id: str = ""  # User ID from product app (for persistence)
    session_id: str = ""  # Onboarding session ID (for entrepreneur_briefs linking)
    kickoff_id: str = ""  # CrewAI kickoff ID (for status tracking)
    iteration: int = 0
    phase: Phase = Phase.IDEATION
    current_risk_axis: RiskAxis = RiskAxis.DESIRABILITY

    # =================== PROBLEM/SOLUTION FIT - Sage (5 fields) ===================
    problem_fit: ProblemFit = ProblemFit.UNKNOWN
    current_segment: Optional[str] = None
    current_value_prop: Optional[str] = None
    vpc_document_url: Optional[str] = None  # External VPC doc reference
    bmc_document_url: Optional[str] = None  # External BMC doc reference

    # =================== INNOVATION PHYSICS SIGNALS (3 fields) ===================
    desirability_signal: DesirabilitySignal = DesirabilitySignal.NO_SIGNAL
    feasibility_signal: FeasibilitySignal = FeasibilitySignal.UNKNOWN
    viability_signal: ViabilitySignal = ViabilitySignal.UNKNOWN

    # =================== DESIRABILITY ARTIFACTS - Pulse (2 fields) ===================
    desirability_experiments: List[DesirabilityExperimentRun] = Field(default_factory=list)
    downgrade_active: bool = False  # True if testing lite/downgraded value prop

    # =================== FEASIBILITY ARTIFACT - Forge (1 field) ===================
    last_feasibility_artifact: Optional[FeasibilityArtifact] = None

    # =================== VIABILITY METRICS - Ledger (1 field) ===================
    last_viability_metrics: Optional[ViabilityMetrics] = None

    # =================== PIVOT & ROUTING STATE (2 fields) ===================
    last_pivot_type: PivotType = PivotType.NONE
    pending_pivot_type: PivotType = PivotType.NONE

    # =================== GLOBAL HUMAN APPROVALS (2 fields) ===================
    human_approval_status: HumanApprovalStatus = HumanApprovalStatus.NOT_REQUIRED
    human_comment: Optional[str] = None

    # =================== HITL BOOKKEEPING (2 fields) ===================
    last_human_decision_task_id: Optional[str] = None
    last_human_decision_run_id: Optional[str] = None

    # =================== GUARDIAN/GOVERNANCE METADATA (2 fields) ===================
    guardian_last_issues: List[str] = Field(default_factory=list)
    audit_log_ids: List[str] = Field(default_factory=list)

    # =================== EVIDENCE CONTAINERS (3 fields) ===================
    desirability_evidence: Optional[DesirabilityEvidence] = None
    feasibility_evidence: Optional[FeasibilityEvidence] = None
    viability_evidence: Optional[ViabilityEvidence] = None

    # =================== SIGNAL TRACKING (4 fields) ===================
    commitment_type: Optional[CommitmentType] = None
    evidence_strength: Optional[EvidenceStrength] = None
    feasibility_status: Optional[FeasibilitySignal] = None
    unit_economics_status: Optional[ViabilitySignal] = None

    # =================== OUTPUT TRACKING (3 fields) ===================
    evidence_summary: Optional[str] = None
    final_recommendation: Optional[str] = None
    next_steps: List[str] = Field(default_factory=list)

    # =================== QA AND GOVERNANCE (2 fields) ===================
    qa_reports: List[QAReport] = Field(default_factory=list)
    current_qa_status: Optional[QAStatus] = None

    # =================== HITL WORKFLOW (3 fields) ===================
    human_input_required: bool = False
    human_input_reason: Optional[str] = None
    pivot_recommendation: Optional[PivotType] = None

    # =================== RETRY LOGIC (3 fields) ===================
    pivot_history: List[Dict[str, Any]] = Field(default_factory=list)
    max_retries: int = 3
    retry_count: int = 0

    # =================== LEGACY COMPATIBILITY FIELDS (7 fields) ===================
    # These maintain compatibility with existing flow logic during migration
    business_idea: Optional[str] = None
    entrepreneur_input: Optional[str] = None
    target_segments: List[str] = Field(default_factory=list)
    assumptions: List[Assumption] = Field(default_factory=list)
    customer_profiles: Dict[str, CustomerProfile] = Field(default_factory=dict)
    value_maps: Dict[str, ValueMap] = Field(default_factory=dict)
    competitor_report: Optional[CompetitorReport] = None

    # =================== SERVICE CREW OUTPUTS (3 fields) ===================
    problem_statement: Optional[str] = None
    solution_description: Optional[str] = None
    revenue_model: Optional[str] = None

    # =================== ANALYSIS CREW OUTPUTS (2 fields) ===================
    segment_fit_scores: Dict[str, float] = Field(default_factory=dict)
    analysis_insights: List[str] = Field(default_factory=list)

    # =================== GROWTH CREW OUTPUTS - Ad Metrics (4 fields) ===================
    ad_impressions: int = 0
    ad_clicks: int = 0
    ad_signups: int = 0
    ad_spend: float = 0.0

    # =================== CREATIVE ARTIFACTS - Landing Pages (4 fields) ===================
    landing_pages: List[Dict[str, Any]] = Field(default_factory=list)  # Generated LP variants
    creative_review_results: List[Any] = Field(default_factory=list)  # GuardianReviewResult objects
    creatives_needing_human_review: List[Dict[str, Any]] = Field(default_factory=list)  # Artifacts flagged for HITL
    auto_approved_creatives: List[str] = Field(default_factory=list)  # Artifact IDs that passed auto-QA

    # =================== BUILD CREW OUTPUTS - Cost Estimates (3 fields) ===================
    api_costs: Dict[str, float] = Field(default_factory=dict)
    infra_costs: Dict[str, float] = Field(default_factory=dict)
    total_monthly_cost: float = 0.0

    # =================== FINANCE CREW OUTPUTS - Unit Economics (5 fields) ===================
    cac: float = 0.0
    ltv: float = 0.0
    ltv_cac_ratio: float = 0.0
    gross_margin: float = 0.0
    tam: float = 0.0

    # =================== SYNTHESIS CREW OUTPUTS (1 field) ===================
    synthesis_confidence: float = 0.0

    # =================== GOVERNANCE CREW OUTPUTS (3 fields) ===================
    framework_compliance: bool = False
    logical_consistency: bool = False
    completeness: bool = False

    # =================== VALIDATORS ===================

    @model_validator(mode='after')
    def sync_project_id(self) -> 'StartupValidationState':
        """Ensure project_id is synced with id for backward compatibility"""
        if not self.project_id:
            object.__setattr__(self, 'project_id', self.id)
        return self

    # =================== HELPER METHODS ===================

    def get_critical_assumptions(self) -> List[Assumption]:
        """Get assumptions with priority 1-3"""
        return [a for a in self.assumptions if a.priority <= 3]

    def get_current_segment_profile(self) -> Optional[CustomerProfile]:
        """Get the primary customer profile being tested"""
        if self.current_segment and self.customer_profiles:
            return self.customer_profiles.get(self.current_segment)
        if self.target_segments and self.customer_profiles:
            return self.customer_profiles.get(self.target_segments[0])
        return None

    def calculate_zombie_ratio(self) -> float:
        """
        Calculate ratio of actual commitment to verbal interest.
        High zombie ratio (>0.7) means people say they're interested but don't commit.
        """
        if not self.desirability_experiments:
            return 0.0

        latest = self.desirability_experiments[-1]
        if not latest.aggregate_metrics:
            return 0.0

        metrics = latest.aggregate_metrics
        if metrics.clicks == 0:
            return 0.0

        # Zombie ratio = (clicks - signups) / clicks = 1 - conversion_rate
        return 1.0 - metrics.conversion_rate

    def calculate_problem_resonance(self) -> float:
        """Calculate problem resonance from experiment metrics"""
        if not self.desirability_experiments:
            return 0.0

        latest = self.desirability_experiments[-1]
        if not latest.aggregate_metrics:
            return 0.0

        metrics = latest.aggregate_metrics
        if metrics.impressions == 0:
            return 0.0

        # Problem resonance approximated by CTR
        return metrics.ctr

    def should_pivot(self) -> bool:
        """Determine if evidence suggests a pivot is needed"""
        # Phase 1: Desirability failures
        if self.phase == Phase.DESIRABILITY:
            if self.desirability_signal == DesirabilitySignal.NO_INTEREST:
                return True  # Segment pivot needed
            if self.desirability_signal == DesirabilitySignal.WEAK_INTEREST:
                return True  # Value pivot needed (zombies detected)

        # Phase 2: Feasibility failures
        elif self.phase == Phase.FEASIBILITY:
            if self.feasibility_signal == FeasibilitySignal.RED_IMPOSSIBLE:
                return True  # Kill or major pivot
            if self.feasibility_signal == FeasibilitySignal.ORANGE_CONSTRAINED:
                return True  # Downgrade needed

        # Phase 3: Viability failures
        elif self.phase == Phase.VIABILITY:
            if self.viability_signal == ViabilitySignal.UNDERWATER:
                return True  # Price or cost pivot needed
            if self.viability_signal == ViabilitySignal.ZOMBIE_MARKET:
                return True  # Market too small

        return False

    def add_pivot_to_history(self, pivot_type: PivotType, reason: str):
        """Track pivot decisions for learning (stored in audit_log_ids)"""
        # This would integrate with the persistence layer
        self.last_pivot_type = pivot_type
        self.audit_log_ids.append(
            f"{datetime.now().isoformat()}|{self.phase.value}|{pivot_type.value}|{reason}"
        )

    class Config:
        """Pydantic configuration"""
        use_enum_values = True


# =======================================================================================
# FLOW CONTROL MODELS
# =======================================================================================

class RouterDecision(BaseModel):
    """Output from router methods"""
    next_step: str
    reason: str
    human_input_required: bool = False
    human_prompt: Optional[str] = None


class PivotDecision(BaseModel):
    """Strategic pivot decision from Compass"""
    pivot_type: PivotType
    specific_changes: List[str]
    evidence_basis: List[str]
    success_criteria: List[str]
    estimated_impact: str


# =======================================================================================
# TYPE ALIASES for backward compatibility
# =======================================================================================

# Allow existing code to use ValidationState as alias
ValidationState = StartupValidationState
ValidationPhase = Phase
PivotRecommendation = PivotType
FeasibilityStatus = FeasibilitySignal
UnitEconomicsStatus = ViabilitySignal
