"""
State schemas for the Innovation Physics Flow Logic.

This module defines the Pydantic models that carry signals through the validation flow,
implementing the specific decision trees from Strategyzer methodologies.
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, validator


# =======================================================================================
# INNOVATION PHYSICS ENUMS - Core signals for routing decisions
# =======================================================================================

class EvidenceStrength(str, Enum):
    """Signal strength from experiments"""
    STRONG = "strong"        # >60% positive signal with behavioral commitment
    WEAK = "weak"            # 30-60% positive signal or verbal only
    NONE = "none"            # <30% positive signal or negative

class CommitmentType(str, Enum):
    """Depth of customer commitment (Zombie Check)"""
    SKIN_IN_GAME = "skin_in_game"  # Money, time, or reputation committed
    VERBAL = "verbal"                # Only verbal interest, no real commitment
    NONE = "none"                    # No commitment or interest

class FeasibilityStatus(str, Enum):
    """Can we actually build what we're promising?"""
    POSSIBLE = "possible"            # We can build it with current resources
    CONSTRAINED = "constrained"      # We can build a degraded version
    IMPOSSIBLE = "impossible"        # Cannot build with any available resources

class UnitEconomicsStatus(str, Enum):
    """The survival equation"""
    PROFITABLE = "profitable"        # LTV > 3x CAC, positive margins
    MARGINAL = "marginal"           # LTV = 1-3x CAC, thin margins
    UNDERWATER = "underwater"        # LTV < CAC, bleeding money

class PivotRecommendation(str, Enum):
    """Strategic pivot options based on evidence"""
    SEGMENT_PIVOT = "segment_pivot"      # Wrong audience, change Customer Segment
    VALUE_PIVOT = "value_pivot"          # Wrong promise, change Value Proposition
    CHANNEL_PIVOT = "channel_pivot"      # Wrong distribution, change Channels
    MODEL_PIVOT = "model_pivot"          # Wrong economics, change Revenue Model
    FEATURE_PIVOT = "feature_pivot"      # Core feature impossible, downgrade offer
    NO_PIVOT = "no_pivot"                # Continue with current approach
    KILL = "kill"                        # Stop project, no viable path


# =======================================================================================
# ASSUMPTION TRACKING
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

    @validator('priority')
    def validate_priority(cls, v):
        """Priority 1-3 are critical, 4-7 are important, 8-10 are nice-to-have"""
        return v


# =======================================================================================
# CUSTOMER & MARKET MODELS
# =======================================================================================

class CustomerJob(BaseModel):
    """Jobs to be Done framework"""
    functional: str      # What task are they trying to accomplish?
    emotional: str       # How do they want to feel?
    social: str         # How do they want to be perceived?
    importance: int = Field(ge=1, le=10)

class CustomerProfile(BaseModel):
    """Value Proposition Canvas - Customer Profile side"""
    segment_name: str
    jobs: List[CustomerJob]
    pains: List[str]           # Frustrations, risks, obstacles
    gains: List[str]           # Benefits, desires, requirements
    pain_intensity: Dict[str, int] = {}  # Pain -> intensity (1-10)
    gain_importance: Dict[str, int] = {} # Gain -> importance (1-10)
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
# TESTING & EVIDENCE
# =======================================================================================

class ExperimentType(str, Enum):
    """From Testing Business Ideas library"""
    PROBLEM_INTERVIEW = "problem_interview"
    SOLUTION_INTERVIEW = "solution_interview"
    LANDING_PAGE = "landing_page"
    FAKE_DOOR = "fake_door"
    CONCIERGE_MVP = "concierge_mvp"
    WIZARD_OF_OZ = "wizard_of_oz"
    CROWDFUNDING = "crowdfunding"
    LETTER_OF_INTENT = "letter_of_intent"

class ExperimentResult(BaseModel):
    """Evidence from a single experiment"""
    experiment_type: ExperimentType
    assumption_id: str
    sample_size: int
    success_rate: float = Field(ge=0, le=1)
    commitment_type: CommitmentType
    evidence_strength: EvidenceStrength
    key_learnings: List[str]
    pivot_signals: List[str] = []
    timestamp: datetime

class DesirabilityEvidence(BaseModel):
    """Aggregated desirability signals"""
    problem_resonance: float = Field(ge=0, le=1)  # % who say it's top 3 problem
    solution_preference: float = Field(ge=0, le=1) # % who prefer our solution
    willingness_to_pay: float = Field(ge=0, le=1)  # % who would pay
    commitment_depth: CommitmentType
    traffic_quality: str  # High/Medium/Low
    conversion_rate: float = Field(ge=0, le=1)
    zombie_ratio: float = Field(ge=0, le=1)  # Action/Verbal interest ratio
    experiments: List[ExperimentResult] = []

class FeasibilityEvidence(BaseModel):
    """Technical and operational reality check"""
    core_features_feasible: Dict[str, FeasibilityStatus]
    technical_debt_estimate: Optional[str] = None
    required_resources: List[str]
    missing_capabilities: List[str]
    partner_dependencies: Dict[str, str]
    downgrade_required: bool = False
    downgrade_impact: Optional[str] = None

class ViabilityEvidence(BaseModel):
    """Financial survival metrics"""
    cac: Optional[float] = None  # Customer Acquisition Cost
    ltv: Optional[float] = None  # Lifetime Value
    ltv_cac_ratio: Optional[float] = None
    gross_margin: Optional[float] = None
    payback_period_months: Optional[int] = None
    unit_economics_status: UnitEconomicsStatus
    pricing_validated: bool = False
    market_size_validated: bool = False


# =======================================================================================
# QUALITY & GOVERNANCE
# =======================================================================================

class QAStatus(str, Enum):
    """Guardian's quality assessment"""
    PASSED = "passed"
    FAILED = "failed"
    CONDITIONAL = "conditional"  # Passed with required changes
    ESCALATED = "escalated"    # Needs human review

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
# MAIN VALIDATION STATE - Carries all signals through the flow
# =======================================================================================

class ValidationPhase(str, Enum):
    """Current phase in the gated validation process"""
    INTAKE = "intake"
    DESIRABILITY = "desirability"
    FEASIBILITY = "feasibility"
    VIABILITY = "viability"
    SYNTHESIS = "synthesis"
    COMPLETE = "complete"

class ValidationState(BaseModel):
    """
    Master state for Innovation Physics flow.
    This carries all signals needed for the routing logic.
    """

    # Identity & Context
    id: str
    timestamp_created: datetime
    timestamp_updated: datetime
    current_phase: ValidationPhase = ValidationPhase.INTAKE

    # Business Context (from intake)
    business_idea: str
    entrepreneur_input: str  # Raw input from entrepreneur
    target_segments: List[str] = []

    # Core Assumptions
    assumptions: List[Assumption] = []

    # Customer Understanding
    customer_profiles: Dict[str, CustomerProfile] = {}  # segment -> profile
    value_maps: Dict[str, ValueMap] = {}  # segment -> value map
    competitor_report: Optional[CompetitorReport] = None

    # Evidence Collection (Phase-specific)
    desirability_evidence: Optional[DesirabilityEvidence] = None
    feasibility_evidence: Optional[FeasibilityEvidence] = None
    viability_evidence: Optional[ViabilityEvidence] = None

    # Innovation Physics Signals (for routing)
    evidence_strength: EvidenceStrength = EvidenceStrength.NONE
    commitment_type: CommitmentType = CommitmentType.NONE
    feasibility_status: FeasibilityStatus = FeasibilityStatus.POSSIBLE
    unit_economics_status: UnitEconomicsStatus = UnitEconomicsStatus.UNDERWATER
    pivot_recommendation: PivotRecommendation = PivotRecommendation.NO_PIVOT

    # Quality & Governance
    qa_reports: List[QAReport] = []
    current_qa_status: Optional[QAStatus] = None

    # Routing Control
    retry_count: int = 0
    max_retries: int = 3
    human_input_required: bool = False
    human_input_reason: Optional[str] = None

    # Pivot History (learning trail)
    pivot_history: List[Dict[str, Any]] = []

    # Final Outputs
    final_recommendation: Optional[str] = None
    evidence_summary: Optional[Dict[str, Any]] = None
    next_steps: List[str] = []

    def get_critical_assumptions(self) -> List[Assumption]:
        """Get assumptions with priority 1-3"""
        return [a for a in self.assumptions if a.priority <= 3]

    def get_current_segment_profile(self) -> Optional[CustomerProfile]:
        """Get the primary customer profile being tested"""
        if self.target_segments and self.customer_profiles:
            return self.customer_profiles.get(self.target_segments[0])
        return None

    def calculate_zombie_ratio(self) -> float:
        """Calculate ratio of actual commitment to verbal interest"""
        if not self.desirability_evidence:
            return 0.0

        if self.desirability_evidence.problem_resonance == 0:
            return 0.0

        # Zombie ratio = actual action / verbal interest
        return self.desirability_evidence.conversion_rate / max(
            self.desirability_evidence.problem_resonance, 0.01
        )

    def should_pivot(self) -> bool:
        """Determine if evidence suggests a pivot is needed"""
        # Phase 1: Desirability failures
        if self.current_phase == ValidationPhase.DESIRABILITY:
            if self.evidence_strength == EvidenceStrength.NONE:
                return True
            if self.commitment_type == CommitmentType.NONE:
                return True
            if self.calculate_zombie_ratio() < 0.1:  # Zombie detected
                return True

        # Phase 2: Feasibility failures
        elif self.current_phase == ValidationPhase.FEASIBILITY:
            if self.feasibility_status == FeasibilityStatus.IMPOSSIBLE:
                return True

        # Phase 3: Viability failures
        elif self.current_phase == ValidationPhase.VIABILITY:
            if self.unit_economics_status == UnitEconomicsStatus.UNDERWATER:
                if self.retry_count >= 2:  # Tried to fix economics twice
                    return True

        return False

    def add_pivot_to_history(self, pivot_type: PivotRecommendation, reason: str):
        """Track pivot decisions for learning"""
        self.pivot_history.append({
            "timestamp": datetime.now(),
            "phase": self.current_phase,
            "pivot_type": pivot_type,
            "reason": reason,
            "evidence_strength": self.evidence_strength,
            "retry_count": self.retry_count
        })

    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


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
    pivot_type: PivotRecommendation
    specific_changes: List[str]
    evidence_basis: List[str]
    success_criteria: List[str]
    estimated_impact: str