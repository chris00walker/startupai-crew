---
purpose: Pydantic state schemas for Modal checkpoint/resume pattern
status: active
last_reviewed: 2026-01-10
vpd_compliance: true
---

# State Schemas

> **Modal Migration**: This document supports the Modal serverless architecture. See [ADR-002](../../adr/002-modal-serverless-migration.md) for migration context.
> **Implementation**: Schemas are implemented in `src/state/models.py` (613 lines).
> **Data Flow**: See [data-flow.md](./data-flow.md) for complete tool output → Supabase pipeline.

This document defines the Pydantic state models used for checkpoint/resume pattern in Modal serverless functions.

---

## Overview

Modal functions persist state to Supabase at HITL checkpoints. When a human approves, the function resumes from the saved state.

**Key Pattern**: Checkpoint → Persist to Supabase → Terminate Container ($0 cost) → Resume on Approval

**Implementation**: `src/state/persistence.py` (370 lines)

---

## ValidationRunState (Top-Level)

The root state model persisted to `validation_runs.phase_state`:

```python
class ValidationRunState(BaseModel):
    """Complete state for a validation run."""

    # Identity
    run_id: UUID
    project_id: UUID
    user_id: UUID
    session_id: Optional[UUID] = None

    # Execution state
    current_phase: int = 0  # 0-4
    status: str = "pending"  # pending, running, paused, completed, failed
    hitl_state: Optional[str] = None  # Current checkpoint name when paused

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
```

---

## Phase 0: Founder's Brief

```python
class FoundersBrief(BaseModel):
    """Founder's Brief captured during Phase 0 onboarding."""

    # Identity
    brief_id: Optional[str] = None
    founder_id: Optional[str] = None
    session_id: Optional[str] = None
    version: int = 1

    # The Idea
    the_idea: TheIdea  # one_liner, description, inspiration, unique_insight

    # Hypotheses (NOT validated - captured for testing)
    problem_hypothesis: ProblemHypothesis  # problem_statement, who_has_this_problem
    customer_hypothesis: CustomerHypothesis  # primary_segment, characteristics
    solution_hypothesis: SolutionHypothesis  # proposed_solution, key_features

    # Assumptions & Success
    key_assumptions: list[Assumption] = Field(default_factory=list)
    success_criteria: SuccessCriteria = Field(default_factory=SuccessCriteria)

    # Founder Context
    founder_context: FounderContext = Field(default_factory=FounderContext)

    # QA Status
    qa_status: QAStatus = Field(default_factory=QAStatus)

    # Metadata
    metadata: InterviewMetadata = Field(default_factory=InterviewMetadata)
```

---

## Phase 1: VPC Discovery

### CustomerProfile (Right Side of VPC)

```python
class CustomerProfile(BaseModel):
    """VPD Customer Profile (right side of Value Proposition Canvas)."""

    segment_name: str
    segment_description: str

    jobs: list[CustomerJob] = Field(default_factory=list)
    pains: list[CustomerPain] = Field(default_factory=list)
    gains: list[CustomerGain] = Field(default_factory=list)

    # Aggregate metrics
    jobs_validated: int = 0
    pains_validated: int = 0
    gains_validated: int = 0

class CustomerJob(BaseModel):
    """A customer job from the VPD Customer Profile."""
    id: str
    job_statement: str  # "When [situation], I want to [motivation] so I can [outcome]"
    job_type: JobType  # functional, social, emotional, supporting
    priority: int = Field(ge=1, le=10)
    validation_status: ValidationStatus = ValidationStatus.UNTESTED
    evidence_ids: list[str] = Field(default_factory=list)

class CustomerPain(BaseModel):
    """A customer pain from the VPD Customer Profile."""
    id: str
    pain_statement: str
    severity: PainSeverity  # extreme, severe, moderate, mild
    priority: int = Field(ge=1, le=10)
    validation_status: ValidationStatus = ValidationStatus.UNTESTED

class CustomerGain(BaseModel):
    """A customer gain from the VPD Customer Profile."""
    id: str
    gain_statement: str
    relevance: GainRelevance  # essential, expected, nice_to_have, unexpected
    priority: int = Field(ge=1, le=10)
    validation_status: ValidationStatus = ValidationStatus.UNTESTED
```

### ValueMap (Left Side of VPC)

```python
class ValueMap(BaseModel):
    """VPD Value Map (left side of Value Proposition Canvas)."""

    products_services: list[ProductService] = Field(default_factory=list)
    pain_relievers: list[PainReliever] = Field(default_factory=list)
    gain_creators: list[GainCreator] = Field(default_factory=list)

class PainReliever(BaseModel):
    """A pain reliever from the VPD Value Map."""
    id: str
    description: str
    addresses_pain_id: str
    effectiveness: str  # eliminates, reduces, none
    validation_status: ValidationStatus = ValidationStatus.UNTESTED

class GainCreator(BaseModel):
    """A gain creator from the VPD Value Map."""
    id: str
    description: str
    addresses_gain_id: str
    effectiveness: str  # exceeds, meets, misses
    validation_status: ValidationStatus = ValidationStatus.UNTESTED
```

### FitAssessment

```python
class FitAssessment(BaseModel):
    """Assessment of fit between Customer Profile and Value Map."""

    fit_score: int = Field(ge=0, le=100)  # Must be >= 70 to proceed
    fit_status: str  # strong, moderate, weak, none

    # Coverage metrics
    profile_completeness: float = Field(ge=0.0, le=1.0)
    value_map_coverage: float = Field(ge=0.0, le=1.0)

    # Evidence strength
    evidence_strength: str  # strong, weak, none
    experiments_run: int = 0
    experiments_passed: int = 0

    # Gate readiness
    gate_ready: bool = False
    blockers: list[str] = Field(default_factory=list)
```

---

## Phase 2-4: Evidence Models

### DesirabilityEvidence

```python
class DesirabilityEvidence(BaseModel):
    """Evidence collected during Phase 2 Desirability validation."""

    # Ad campaign metrics
    ad_impressions: int = 0
    ad_clicks: int = 0
    ad_signups: int = 0
    ad_spend: float = 0.0

    # Key metrics
    problem_resonance: float = Field(0.0, ge=0.0, le=1.0)
    zombie_ratio: float = Field(0.0, ge=0.0, le=1.0)
    conversion_rate: float = Field(0.0, ge=0.0, le=1.0)

    # Signal derivation
    signal: Optional[ValidationSignal] = None  # no_interest, mild_interest, strong_commitment

    # Experiments
    experiments: list[Experiment] = Field(default_factory=list)
```

### FeasibilityEvidence

```python
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
    signal: Optional[ValidationSignal] = None  # green, orange_constrained, red_impossible
    constraints: list[str] = Field(default_factory=list)
```

### ViabilityEvidence

```python
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

    # Market sizing
    tam_usd: float = 0.0  # Total Addressable Market
    sam_usd: float = 0.0  # Serviceable Addressable Market
    som_usd: float = 0.0  # Serviceable Obtainable Market

    # Signal
    signal: Optional[ValidationSignal] = None  # profitable, marginal, underwater
    unit_economics_status: str = "unknown"
```

---

## Enums

```python
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
    SEGMENT_PIVOT = "segment_pivot"
    VALUE_PIVOT = "value_pivot"
    FEATURE_PIVOT = "feature_pivot"
    STRATEGIC_PIVOT = "strategic_pivot"
    KILL = "kill"

class JobType(str, Enum):
    """Four job types per Osterwalder/Pigneur VPD."""
    FUNCTIONAL = "functional"   # Tasks to complete
    SOCIAL = "social"           # How they want to be perceived
    EMOTIONAL = "emotional"     # How they want to feel
    SUPPORTING = "supporting"   # Buyer, co-creator, transferrer roles

class PainSeverity(str, Enum):
    EXTREME = "extreme"
    SEVERE = "severe"
    MODERATE = "moderate"
    MILD = "mild"

class GainRelevance(str, Enum):
    """Four levels per Osterwalder/Pigneur VPD Kano model."""
    ESSENTIAL = "essential"         # Required, must-have gains
    EXPECTED = "expected"           # Baseline expectations
    NICE_TO_HAVE = "nice_to_have"   # Desired, differentiation
    UNEXPECTED = "unexpected"       # Delighters, wow factor

class ValidationStatus(str, Enum):
    VALIDATED = "validated"
    INVALIDATED = "invalidated"
    UNTESTED = "untested"
```

---

## Serialization Patterns

### Writing to Supabase

```python
# In persistence.py
def checkpoint_state(run_id: str, state: ValidationRunState):
    state_json = state.model_dump(mode="json")
    # mode="json" ensures:
    # - UUIDs → strings
    # - datetime → ISO strings
    # - Enums → string values
    # - Nested models → dicts
    # - None values included (for explicit null)

    supabase.table("validation_runs").update({
        "phase_state": state_json,
        "current_phase": state.current_phase,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", run_id).execute()
```

### Reading from Supabase

```python
# In persistence.py
def resume_state(run_id: str) -> ValidationRunState:
    result = supabase.table("validation_runs").select("*").eq(
        "id", run_id
    ).single().execute()

    phase_state = result.data.get("phase_state", {})
    # Pydantic validates on instantiation
    state = ValidationRunState(**phase_state)
    return state
```

---

## State Transitions

| From State | To State | Trigger | Signal Condition |
|------------|----------|---------|------------------|
| Phase 0 | Phase 1 | `approve_founders_brief` | QA pass |
| Phase 1 | Phase 2 | `approve_vpc_completion` | fit_score >= 70 |
| Phase 2 | Phase 3 | `approve_desirability_gate` | STRONG_COMMITMENT |
| Phase 2 | Phase 1 (pivot) | `approve_segment_pivot` | MILD_INTEREST |
| Phase 3 | Phase 4 | `approve_feasibility_gate` | GREEN |
| Phase 3 | Phase 2 (downgrade) | `approve_feature_pivot` | ORANGE_CONSTRAINED |
| Phase 4 | Complete | `request_human_decision` | Any signal |

---

## Related Documents

- [data-flow.md](./data-flow.md) - Complete tool output → Supabase pipeline
- [database-schemas.md](./database-schemas.md) - Supabase table definitions
- [approval-workflows.md](./approval-workflows.md) - HITL checkpoint patterns
- [ADR-002](../../adr/002-modal-serverless-migration.md) - Modal migration decision

---

**Last Updated**: 2026-01-10
**Status**: Active - Reflects actual implementation in `src/state/models.py`
