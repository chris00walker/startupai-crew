# StartupAI Architectural Review

**Date**: 2025-11-25
**Reviewer**: Senior Systems Architect / Principal Engineer Analysis
**Scope**: All StartupAI artifacts including flows, crews, tools, state models, ETL design, and configuration

---

## Executive Summary

StartupAI's architecture demonstrates strong conceptual foundations with the Innovation Physics validation framework and well-structured CrewAI Flow orchestration. However, several critical gaps exist between design documentation and implementation that must be addressed before this becomes a "production-grade, self-improving system."

**Overall Assessment**: The design is comprehensive and methodologically sound, but the implementation is at ~30% completion with significant gaps in contracts, persistence, observability, and developer experience.

---

## 1. CONTRACTS BETWEEN FLOW ⇄ CREWS ⇄ TOOLS

### What's Good

1. **Pydantic models are well-defined** in `state_schemas.py`:
   - Strong typing for core enums (`EvidenceStrength`, `CommitmentType`, `FeasibilityStatus`, etc.)
   - Nested models for complex artifacts (`CustomerProfile`, `ValueMap`, `ExperimentResult`)
   - Validation with `Field(ge=0, le=1)` constraints on scores

2. **Clear state contract**: `ValidationState` carries all signals needed for routing decisions

3. **Separation of concerns**: Each crew has dedicated config files (`agents.yaml`, `tasks.yaml`)

### What's Missing or Risky

1. **No tool output contracts**: Tool definitions in `03-validation-spec.md` use `dict` returns instead of strict Pydantic models:
   ```python
   # Current (loose)
   def generate_ads(...) -> List[dict]:

   # Needed (strict)
   def generate_ads(...) -> ToolResult[List[AdVariant]]:
   ```

2. **No error handling envelope**: Tools assume success. No standard pattern for:
   - Partial failures (3 of 5 ads generated)
   - Retryable errors vs. fatal errors
   - Fallback behavior

3. **Model duplication risk**: Two parallel state schemas exist:
   - `ValidationState` in `state_schemas.py` (current implementation)
   - `StartupValidationState` in `03-validation-spec.md` and `master-spec.md` (design docs)

   These have different field names and structures, creating confusion.

4. **Crew output contracts undefined**: Crews return `result.pydantic` but the expected Pydantic models aren't specified:
   ```python
   # internal_validation_flow.py:68-70
   self.state.business_idea = result.pydantic.business_idea  # What model?
   self.state.target_segments = result.pydantic.target_segments
   self.state.assumptions = result.pydantic.assumptions
   ```

5. **Flow assumes tools always succeed**:
   ```python
   # No error handling in flow methods
   result = ServiceCrew().crew().kickoff(inputs={...})
   self.state.business_idea = result.pydantic.business_idea  # What if None?
   ```

### Concrete Recommendations

**File**: `src/startupai/models/tool_contracts.py` (NEW)
```python
from typing import TypeVar, Generic, Optional, List
from pydantic import BaseModel

T = TypeVar('T')

class ToolResult(BaseModel, Generic[T]):
    """Standard envelope for all tool outputs."""
    ok: bool
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    payload: Optional[T] = None
    retryable: bool = False

class AdGenerationResult(BaseModel):
    variants: List[AdVariant]
    generation_metadata: dict

class PageDeploymentResult(BaseModel):
    deployed_urls: List[str]
    deployment_ids: List[str]
    provider: str
```

**File**: `src/startupai/models/crew_outputs.py` (NEW)
```python
class ServiceCrewOutput(BaseModel):
    """Output contract for Service Crew intake task."""
    business_idea: str
    target_segments: List[str]
    assumptions: List[Assumption]
    problem_statement: str
    revenue_model: str

class AnalysisCrewOutput(BaseModel):
    """Output contract for Analysis Crew."""
    customer_profile: CustomerProfile
    value_map: ValueMap
```

**Migration Required**:
- Unify `ValidationState` and `StartupValidationState` into a single canonical model
- Update all flow methods to handle `ToolResult` errors with retry/fallback logic

---

## 2. STATE & PERSISTENCE MANAGEMENT

### What's Good

1. **Rich state model**: `ValidationState` carries comprehensive signals:
   - Phase tracking (`current_phase`, `retry_count`, `max_retries`)
   - Evidence collection (`desirability_evidence`, `feasibility_evidence`, `viability_evidence`)
   - Pivot history with timestamps

2. **Helper methods**: `should_pivot()`, `calculate_zombie_ratio()`, `add_pivot_to_history()`

3. **Design docs specify persistence**: `@persist` decorator mentioned in `03-validation-spec.md`

### What's Missing or Risky

1. **No StateRepository abstraction**: Load/save operations aren't abstracted:
   ```python
   # Current: No persistence code exists
   # Needed:
   class StateRepository:
       def get_state(self, project_id: str) -> ValidationState: ...
       def save_state(self, state: ValidationState, event: ValidationEvent) -> None: ...
       def get_history(self, project_id: str) -> List[ValidationEvent]: ...
   ```

2. **No event logging**: Phase transitions and routing decisions aren't captured:
   - When did the project move from DESIRABILITY to FEASIBILITY?
   - Why did the router choose `segment_pivot_required`?
   - What was the evidence at each decision point?

3. **Missing audit trail fields**: `audit_log_ids` exists but isn't populated anywhere

4. **No versioning**: State snapshots for replay/debugging aren't implemented

5. **`pivot_history` uses `Dict[str, Any]`** - loses type safety:
   ```python
   # Current
   pivot_history: List[Dict[str, Any]] = []

   # Needed
   pivot_history: List[PivotEvent] = []
   ```

### Concrete Recommendations

**File**: `src/startupai/persistence/state_repository.py` (NEW)
```python
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

class ValidationEvent(BaseModel):
    """Immutable event for audit trail."""
    event_id: str
    project_id: str
    timestamp: datetime
    event_type: str  # "phase_change", "pivot", "gate_pass", "gate_fail"
    from_state: dict
    to_state: dict
    reason: str
    triggered_by: str  # "desirability_gate", "feasibility_gate", etc.

class StateRepository(ABC):
    @abstractmethod
    def get_state(self, project_id: str) -> Optional[ValidationState]: ...

    @abstractmethod
    def save_state(self, state: ValidationState, event: ValidationEvent) -> None: ...

    @abstractmethod
    def get_events(self, project_id: str) -> List[ValidationEvent]: ...

class SupabaseStateRepository(StateRepository):
    """Concrete implementation using Supabase."""
    def __init__(self, supabase_client): ...
```

**File**: Database migration for `validation_events` table:
```sql
CREATE TABLE validation_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    event_type TEXT NOT NULL,
    from_state JSONB,
    to_state JSONB,
    reason TEXT,
    triggered_by TEXT,
    evidence_snapshot JSONB
);
```

**Update routers to emit events**:
```python
@router(test_desirability)
def desirability_gate(self) -> str:
    decision = self._calculate_routing_decision()

    # Emit event
    self.emit_event(ValidationEvent(
        event_type="gate_decision",
        from_state={"phase": "desirability", "evidence": self.state.desirability_evidence.dict()},
        to_state={"next_step": decision},
        reason=self._get_routing_reason(),
        triggered_by="desirability_gate"
    ))

    return decision
```

---

## 3. LEARNING LOOP QUALITY

### What's Good

1. **Comprehensive Flywheel design** in `reference/flywheel-learning.md`:
   - Three learning types: Pattern, Outcome, Domain
   - Anonymization pipeline specified
   - pgvector integration for semantic search

2. **Rich example learning captures** showing Innovation Physics signal correlation:
   - Zombie ratio patterns
   - Segment pivot outcomes
   - CAC/LTV domain expertise

3. **Database schema defined** with proper indexes

### What's Missing or Risky

1. **No policy versioning**: Can't A/B test experiment configurations:
   ```python
   # Current: Static YAML config
   # Needed: Versioned policy tracking
   class ProjectExperimentConfig(BaseModel):
       policy_version: str = "yaml_baseline_v1"
       # ...
   ```

2. **No outcome tracking mechanism**: Learning captures are designed but not implemented:
   - How do we know if a "proceed" recommendation was correct?
   - What happens when a validated project fails post-launch?

3. **Success scoring is simplistic**:
   ```python
   # Current: Binary success (problem_resonance > 0.6)
   # Needed: Nuanced scoring with confidence intervals
   ```

4. **No retrieval-aware config resolver implemented**: `ExperimentConfigResolver` is in docs but not in code

5. **Missing learning capture points** in flow:
   - `_capture_flywheel_learnings()` is called but stores to nowhere
   - No `LearningCaptureTool` implementation exists

### Concrete Recommendations

**File**: `src/startupai/tools/learning_capture.py` (NEW)
```python
class LearningCaptureTool(BaseTool):
    name: str = "capture_learning"
    description: str = "Store anonymized learning for future validations"

    def __init__(self, supabase_client, embedding_client):
        self.supabase = supabase_client
        self.embeddings = embedding_client

    def _run(
        self,
        learning_type: Literal["pattern", "outcome", "domain"],
        title: str,
        description: str,
        context: dict,
        founder: Literal["sage", "forge", "pulse", "compass", "guardian", "ledger"],
        phase: Literal["desirability", "feasibility", "viability"],
        tags: List[str] = None,
        confidence_score: float = None
    ) -> str:
        # 1. Anonymize context
        anonymized = Anonymizer().abstract_context(context)

        # 2. Generate embedding
        embedding = self.embeddings.embed(f"{title} {description}")

        # 3. Store in Supabase
        self.supabase.table("learnings").insert({
            "learning_type": learning_type,
            "founder": founder,
            "phase": phase,
            "title": title,
            "description": description,
            "context_abstract": anonymized,
            "tags": tags or [],
            "embedding": embedding,
            "confidence_score": confidence_score
        }).execute()

        return f"Learning captured: {title}"
```

**Policy versioning strategy**:
```python
# In experiment_outcomes table
policy_version: str  # "yaml_baseline", "retrieval_v1", "retrieval_v2"

# Simple bandit for policy selection
def select_policy(project_context: dict) -> str:
    if random.random() < 0.8:
        return "retrieval_v1"  # Exploitation
    return "yaml_baseline"  # Exploration

# Track which policy served each experiment
experiment_run.policy_version = select_policy(context)
```

---

## 4. OBSERVABILITY & MONITORING

### What's Good

1. **Flow methods have print statements** for debugging:
   ```python
   print(f"✅ Intake complete. Target segments: {self.state.target_segments}")
   ```

2. **Design docs mention dashboards** for phase distribution and metrics

### What's Missing or Risky

1. **No structured logging schema**: Print statements don't capture structured data

2. **No centralized metrics**:
   - Token costs per crew/task
   - Latency per phase
   - Error rates by tool/crew
   - Experiment volume over time

3. **No portfolio view implementation**: Can't see all projects and their phase distribution

4. **No alerting**: No way to know if a project is stuck or a tool is failing repeatedly

5. **CrewAI AMP observability not configured**: Dashboard exists but integration unclear

### Concrete Recommendations

**File**: `src/startupai/observability/structured_logger.py` (NEW)
```python
import json
from datetime import datetime
from typing import Optional

class StructuredLogger:
    def __init__(self, sink: str = "supabase"):
        self.sink = sink

    def log(
        self,
        project_id: str,
        crew: str,
        task: str,
        status: str,
        latency_ms: int,
        policy_version: Optional[str] = None,
        error: Optional[str] = None,
        tokens_used: Optional[int] = None,
        extra: Optional[dict] = None
    ):
        entry = {
            "ts": datetime.utcnow().isoformat(),
            "project_id": project_id,
            "crew": crew,
            "task": task,
            "status": status,
            "latency_ms": latency_ms,
            "policy_version": policy_version,
            "error": error,
            "tokens_used": tokens_used,
            **(extra or {})
        }

        if self.sink == "supabase":
            # Insert to execution_logs table
            pass
        else:
            print(json.dumps(entry))
```

**Database schema for logs**:
```sql
CREATE TABLE execution_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ts TIMESTAMPTZ DEFAULT NOW(),
    project_id UUID,
    crew TEXT NOT NULL,
    task TEXT NOT NULL,
    status TEXT NOT NULL,
    latency_ms INT,
    policy_version TEXT,
    error TEXT,
    tokens_used INT,
    extra JSONB
);

CREATE INDEX idx_logs_project ON execution_logs(project_id);
CREATE INDEX idx_logs_crew ON execution_logs(crew);
CREATE INDEX idx_logs_ts ON execution_logs(ts DESC);
```

**Minimal dashboard queries**:
```sql
-- Projects by phase
SELECT current_phase, COUNT(*) FROM flow_executions GROUP BY current_phase;

-- Average latency by crew
SELECT crew, AVG(latency_ms) FROM execution_logs WHERE ts > NOW() - INTERVAL '7 days' GROUP BY crew;

-- Error rate by tool
SELECT task, COUNT(*) FILTER (WHERE status = 'error') * 100.0 / COUNT(*) as error_rate
FROM execution_logs WHERE ts > NOW() - INTERVAL '7 days' GROUP BY task;
```

---

## 5. CREATIVE LEARNING (HOOKS, STRUCTURES, PATTERNS)

### What's Good

1. **AdVariant and LandingPageVariant models defined** with approval status tracking

2. **Design mentions creative pattern learning** in flywheel docs

### What's Missing or Risky

1. **No structured creative attributes**: Ads have `headline`, `body`, `cta` but no:
   - `hook_type` (problem-agitate-solve, social-proof, urgency)
   - `tone` (direct, playful, premium, technical)
   - `format` (short-form, long-form, listicle)

2. **No creative outcomes schema**: Can't learn which hook/tone combos work

3. **CopywritingTool not implemented**: Stub in docs, no actual code

4. **No pattern-based generation**: LLM generates "from scratch" each time

### Concrete Recommendations

**Extend AdVariant model**:
```python
class AdVariant(BaseModel):
    id: str
    platform: Platform
    headline: str
    body: str
    cta: str
    asset_url: Optional[HttpUrl] = None

    # NEW: Creative structure fields
    hook_type: Literal["problem-agitate-solve", "social-proof", "urgency", "testimonial", "curiosity"]
    tone: Literal["direct", "playful", "premium", "technical", "empathetic"]
    format: Literal["short-form", "long-form", "listicle", "question-lead"]

    # Approval fields
    approval_status: ArtifactApprovalStatus = ArtifactApprovalStatus.DRAFT
    human_approval_status: HumanApprovalStatus = HumanApprovalStatus.NOT_REQUIRED
    human_comment: Optional[str] = None
```

**Creative outcomes ETL**:
```sql
CREATE TABLE creative_outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ad_variant_id UUID,
    hook_type TEXT,
    tone TEXT,
    format TEXT,
    platform TEXT,
    segment_type TEXT,  -- "b2b", "b2c", "b2b2c"

    -- Performance metrics
    impressions INT,
    clicks INT,
    conversions INT,
    ctr DECIMAL(5,4),
    cvr DECIMAL(5,4),

    -- Learning signals
    relative_performance DECIMAL(5,2),  -- vs baseline
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Pattern-based generation in CopywritingTool**:
```python
class CopywritingTool(BaseTool):
    def generate_ads(self, vpc: dict, platform: Platform, segment_type: str) -> List[AdVariant]:
        # 1. Retrieve winning patterns for this segment/platform
        patterns = self.learning_retrieval.query(
            f"High-performing ad patterns for {segment_type} on {platform}",
            learning_type="pattern"
        )

        # 2. Select hook/tone based on patterns
        hook_type = self._select_hook(patterns, segment_type)
        tone = self._select_tone(patterns, platform)

        # 3. Generate with explicit structure
        prompt = f"""
        Generate an ad using:
        - Hook type: {hook_type}
        - Tone: {tone}
        - VPC: {vpc}

        Successful patterns for reference:
        {patterns}
        """

        return self.llm.generate(prompt)
```

---

## 6. HUMAN-IN-THE-LOOP (HITL) UX & GUARDRAILS

### What's Good

1. **HITL workflow fully designed** in `approval-workflows.md`:
   - Webhook from CrewAI to product app
   - Resume endpoint for decisions
   - Payload schemas defined

2. **Multiple approval types mapped to owners** (Ledger owns spend, Pulse owns campaigns)

3. **Innovation Physics pivot triggers** require human approval:
   - Segment pivot
   - Value pivot
   - Feature downgrade
   - Strategic pivot

### What's Missing or Risky

1. **Product app implementation doesn't exist**:
   - Webhook receiver: NOT IMPLEMENTED
   - Approval UI: NOT IMPLEMENTED
   - Resume client: NOT IMPLEMENTED

2. **Human rationales not captured**: `human_comment` field exists but no structured storage

3. **No budget guardrails**: No `max_budget_per_day` or escalation thresholds

4. **Simulated approvals in flow**:
   ```python
   def _get_human_input_segment_pivot(self) -> Dict[str, Any]:
       # In production, this would trigger a webhook to the product app
       # For now, we simulate approval
       return {"approved": True, "new_segment": "Enterprise Consultants"}
   ```

5. **No approval batching/prioritization**: Approvals arrive ungrouped

6. **No timeout/escalation**: What happens if approval takes 48 hours?

### Concrete Recommendations

**HITL payload schema (explicit)**:
```python
class HITLRequest(BaseModel):
    """What human sees in approval UI."""
    execution_id: str
    task_id: str
    approval_type: str

    # Context for decision
    project_summary: dict
    current_evidence: dict
    signal_values: dict  # problem_resonance, zombie_ratio, etc.

    # Recommendation from AI
    ai_recommendation: str
    ai_reasoning: str

    # Options
    options: List[HITLOption]

class HITLOption(BaseModel):
    action: str
    label: str
    description: str
    rationale: str
    risk_level: Literal["low", "medium", "high"]

class HITLResponse(BaseModel):
    """What human provides."""
    selected_option: str
    rationale: str
    modifications: Optional[dict] = None
    approved_by: str
    timestamp: datetime
```

**Guardrail rules**:
```python
class BudgetGuardrails(BaseModel):
    max_daily_spend_usd: float = 100.0
    max_total_spend_usd: float = 1000.0
    escalation_threshold_usd: float = 500.0
    kill_switch_enabled: bool = True

def check_budget_guardrails(experiment: DesirabilityExperimentRun, guardrails: BudgetGuardrails) -> bool:
    total_budget = sum(b.total_budget_usd for b in experiment.routing.platform_budgets)
    if total_budget > guardrails.max_total_spend_usd:
        raise BudgetExceededError(f"Budget {total_budget} exceeds max {guardrails.max_total_spend_usd}")
    return True
```

**Store human rationales**:
```sql
CREATE TABLE approval_decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    approval_request_id UUID REFERENCES approval_requests(id),
    selected_option TEXT NOT NULL,
    rationale TEXT NOT NULL,
    modifications JSONB,
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMPTZ DEFAULT NOW(),

    -- For learning
    context_snapshot JSONB,
    embedding VECTOR(1536)  -- For similar decision retrieval
);
```

---

## 7. FEASIBILITY & VIABILITY DEPTH

### What's Good

1. **FeasibilityArtifact model** tracks:
   - `removed_features`, `retained_features`
   - `api_cost_estimate_monthly_usd`, `infra_cost_estimate_monthly_usd`
   - `technical_complexity_score`

2. **ViabilityMetrics model** includes:
   - CAC, LTV, LTV/CAC ratio
   - Gross margin, payback period
   - TAM estimate

3. **Downgrade Protocol** properly routes back to desirability testing

### What's Missing or Risky

1. **No feature toggles**: Can't A/B test feature presence:
   ```python
   # Current: Boolean downgrade_active
   # Needed: Feature-level toggles
   class FeatureToggle(BaseModel):
       feature_id: str
       enabled: bool
       downgrade_version: Optional[str] = None
   ```

2. **Single business model assumption**: ViabilityMetrics assumes subscription model. Needs support for:
   - DTC eCommerce (COGS, return rates, shipping)
   - Marketplace (take rate, GMV, liquidity)
   - Freemium (conversion rates, tier distribution)
   - B2B SaaS (contract value, seat expansion)

3. **No component-level cost breakdown**: Infrastructure costs are aggregate

4. **Feasibility assessment is stub**:
   ```python
   # BuildCrew has assess_feasibility task but no actual implementation
   @task
   def assess_feasibility(self) -> Task:
       return Task(config=self.tasks_config['assess_feasibility'])
   ```

### Concrete Recommendations

**Extended FeasibilityArtifact**:
```python
class FeatureToggle(BaseModel):
    feature_id: str
    feature_name: str
    enabled: bool
    complexity: int  # 1-10
    monthly_cost_usd: float
    dependencies: List[str] = []
    can_downgrade: bool = True

class FeasibilityArtifact(BaseModel):
    build_id: str
    mvp_url: Optional[HttpUrl] = None

    # Feature-level tracking
    features: List[FeatureToggle] = []
    removed_features: List[str] = []
    retained_features: List[str] = []

    # Component-level costs
    api_costs: Dict[str, float] = {}  # {"openai": 50, "stripe": 10}
    infra_costs: Dict[str, float] = {}  # {"vercel": 20, "supabase": 25}
    total_monthly_cost_usd: float = 0.0

    technical_complexity_score: int = 0
    notes: Optional[str] = None
```

**Business model-specific viability**:
```python
class BusinessModelType(str, Enum):
    SUBSCRIPTION_SAAS = "subscription_saas"
    DTC_ECOMMERCE = "dtc_ecommerce"
    MARKETPLACE = "marketplace"
    FREEMIUM = "freemium"
    B2B_ENTERPRISE = "b2b_enterprise"

class SubscriptionViability(BaseModel):
    mrr: float
    arr: float
    monthly_churn_pct: float
    expansion_revenue_pct: float
    payback_months: float

class EcommerceViability(BaseModel):
    aov: float  # Average order value
    cogs_pct: float
    return_rate_pct: float
    shipping_cost_per_order: float
    contribution_margin: float

class ViabilityMetrics(BaseModel):
    business_model: BusinessModelType
    cac_usd: float
    ltv_usd: float
    ltv_cac_ratio: float

    # Model-specific metrics
    subscription: Optional[SubscriptionViability] = None
    ecommerce: Optional[EcommerceViability] = None
    marketplace: Optional[MarketplaceViability] = None
```

---

## 8. DEVELOPER EXPERIENCE (DX) & WORKFLOW

### What's Good

1. **CLAUDE.md** provides good project context with:
   - Directory structure
   - Core commands
   - Deployment configuration

2. **pyproject.toml** with uv for dependency management

3. **Local testing command**: `crewai run`

### What's Missing or Risky

1. **No seed data scripts**: Can't quickly populate test projects

2. **No test suite**: Zero automated tests for:
   - Routing logic correctness
   - State transitions
   - Tool contracts
   - ETL pipelines

3. **No local simulation mode**: Must hit real APIs for any testing

4. **No ETL scripts**: Learning pipeline is designed but not executable

5. **Missing Makefile/scripts**:
   - `make seed-demo-project`
   - `make run-etl`
   - `make simulate-flow`
   - `make test`

6. **No .env.example**: New developers don't know required variables

### Concrete Recommendations

**File**: `scripts/seed_demo_project.py` (NEW)
```python
#!/usr/bin/env python
"""Seed a demo project for local testing."""

from startupai.flows.state_schemas import (
    ValidationState,
    CustomerProfile,
    ValueMap,
    Assumption,
    AssumptionCategory,
)
from datetime import datetime
import uuid

def seed_demo_project():
    state = ValidationState(
        id=f"demo_{uuid.uuid4().hex[:8]}",
        timestamp_created=datetime.now(),
        timestamp_updated=datetime.now(),
        entrepreneur_input="Demo: AI-powered validation platform...",
        business_idea="AI-powered startup validation",
        target_segments=["Founders", "Consultants"],
        assumptions=[
            Assumption(
                id="a1",
                statement="Founders want faster validation",
                category=AssumptionCategory.DESIRABILITY,
                priority=1,
                evidence_needed="50+ signups in 7 days"
            )
        ]
    )

    # Save to Supabase or local JSON
    print(f"Created demo project: {state.id}")
    return state

if __name__ == "__main__":
    seed_demo_project()
```

**File**: `scripts/simulate_flow.py` (NEW)
```python
#!/usr/bin/env python
"""Simulate flow with mock responses for local testing."""

import os
os.environ["MOCK_TOOLS"] = "true"

from startupai.flows import create_validation_flow

def simulate():
    flow = create_validation_flow(
        "Test business idea for simulation..."
    )

    # Mock crew responses
    flow.mock_service_crew_response = {...}
    flow.mock_growth_crew_response = {...}

    result = flow.kickoff()
    print(f"Simulation complete: {result}")

if __name__ == "__main__":
    simulate()
```

**File**: `tests/test_routing_logic.py` (NEW)
```python
import pytest
from startupai.flows.state_schemas import (
    ValidationState,
    EvidenceStrength,
    CommitmentType,
    DesirabilityEvidence,
)
from startupai.flows.internal_validation_flow import InternalValidationFlow

class TestDesirabilityGate:
    def test_low_problem_resonance_triggers_segment_pivot(self):
        state = ValidationState(...)
        state.desirability_evidence = DesirabilityEvidence(
            problem_resonance=0.2,  # < 0.3 threshold
            conversion_rate=0.05,
            commitment_depth=CommitmentType.VERBAL,
        )

        flow = InternalValidationFlow(initial_state=state)
        decision = flow.desirability_gate()

        assert decision == "segment_pivot_required"

    def test_high_zombie_ratio_triggers_value_pivot(self):
        ...

    def test_strong_evidence_proceeds_to_feasibility(self):
        ...
```

**File**: `Makefile` (NEW)
```makefile
.PHONY: dev seed test simulate

dev:
	uv sync
	crewai run

seed:
	python scripts/seed_demo_project.py

test:
	pytest tests/ -v

simulate:
	python scripts/simulate_flow.py

etl:
	python scripts/run_learning_etl.py
```

---

## 9. BEYOND THE 8 AREAS

### Additional Issues Identified

#### 9.1 Hidden Coupling

1. **Flow imports all crews unconditionally**:
   ```python
   # internal_validation_flow.py:30-36
   from startupai.crews.service.service_crew import ServiceCrew
   from startupai.crews.analysis.analysis_crew import AnalysisCrew
   # ... imports all 7 crews
   ```
   This means importing the flow requires all crew dependencies to be valid.

2. **State schema split across multiple files**: `state_schemas.py`, `03-validation-spec.md`, `master-spec.md` all define state differently.

#### 9.2 LLM Magic Without Explicitness

1. **Task descriptions are vague**:
   ```yaml
   # Current
   description: "Analyze the entrepreneur's input and extract structured information"

   # Needed: Explicit output format
   description: |
     Analyze the entrepreneur's input and return JSON matching ServiceCrewOutput:
     {
       "business_idea": "...",
       "target_segments": ["...", "..."],
       "assumptions": [{"statement": "...", "category": "...", "priority": 1}]
     }
   ```

2. **No few-shot examples in task configs**: LLM must infer output format

#### 9.3 Schema Normalization Opportunities

1. **Duplicate platform enums**: `Platform` defined in both `state_schemas.py` and `master-spec.md`

2. **Inconsistent naming**:
   - `ValidationState` vs `StartupValidationState`
   - `CommitmentType` vs `commitment_type` field

#### 9.4 Security/Privacy Gaps

1. **Anonymizer and PrivacyGuard not implemented**: Just stubs in flywheel docs

2. **API keys in environment**: No secrets rotation strategy

3. **No PII detection in logs**: Print statements may leak sensitive data

4. **HITL payloads may contain business-sensitive context**: No access control

### Concrete Recommendations

**Lazy crew imports**:
```python
class InternalValidationFlow(Flow[ValidationState]):
    @cached_property
    def service_crew(self):
        from startupai.crews.service.service_crew import ServiceCrew
        return ServiceCrew()
```

**Explicit task output formats**:
```yaml
capture_entrepreneur_brief:
  description: |
    Analyze the entrepreneur's input and extract structured information.

    REQUIRED OUTPUT FORMAT (JSON):
    {
      "business_idea": "One sentence value proposition",
      "target_segments": ["Segment 1", "Segment 2"],
      "problem_statement": "The problem being solved",
      "assumptions": [
        {
          "statement": "Assumption text",
          "category": "desirability|feasibility|viability",
          "priority": 1-10
        }
      ]
    }
  expected_output: ServiceCrewOutput JSON
```

---

## 10. PRIORITIZED ACTION PLAN

### Must-Do Immediately (Week 1-2)

| Priority | Item | Files Impacted | Effort |
|----------|------|----------------|--------|
| P0 | **Unify state schemas** - Merge ValidationState and StartupValidationState | `state_schemas.py`, docs | 1 day |
| P0 | **Add tool output contracts** - Create `ToolResult` envelope | `models/tool_contracts.py` (new) | 1 day |
| P0 | **Add error handling to flow** - Handle None returns and failures | `internal_validation_flow.py` | 2 days |
| P0 | **Create StateRepository** - Abstract persistence | `persistence/state_repository.py` (new) | 2 days |
| P0 | **Add event logging to routers** - Capture decisions | `internal_validation_flow.py` | 1 day |

### Important But Can Wait (Week 3-4)

| Priority | Item | Files Impacted | Effort |
|----------|------|----------------|--------|
| P1 | **Implement LearningCaptureTool** | `tools/learning_capture.py` (new) | 2 days |
| P1 | **Implement LearningRetrievalTool** | `tools/learning_retrieval.py` (new) | 2 days |
| P1 | **Add structured logging** | `observability/structured_logger.py` (new) | 1 day |
| P1 | **Create test suite** | `tests/` (new) | 3 days |
| P1 | **Add creative structure fields** | `state_schemas.py` | 1 day |
| P1 | **Create seed scripts** | `scripts/` (new) | 1 day |

### Nice-to-Have / Long-Term (Week 5+)

| Priority | Item | Files Impacted | Effort |
|----------|------|----------------|--------|
| P2 | **Policy versioning for A/B tests** | Multiple | 3 days |
| P2 | **Business model-specific viability** | `state_schemas.py`, `finance_crew.py` | 3 days |
| P2 | **HITL UI implementation** | Product app | 5 days |
| P2 | **Dashboard queries** | Supabase | 2 days |
| P2 | **Anonymizer implementation** | `tools/anonymizer.py` (new) | 2 days |
| P2 | **Budget guardrails** | `models/guardrails.py` (new) | 1 day |

---

## Risk Assessment

### If P0 Items Are Not Addressed

1. **State inconsistency**: Dual state schemas will cause confusion and bugs when implementing crew outputs
2. **Silent failures**: Flow will crash on tool errors with no recovery path
3. **No auditability**: Can't explain why a project was killed/validated
4. **Integration fragility**: Real API integrations will expose contract gaps

### If P1 Items Are Not Addressed

1. **No learning accumulation**: Flywheel won't spin - each validation starts from scratch
2. **Blind operations**: No visibility into what's working or failing
3. **Regression risk**: Changes may break routing logic without tests catching it
4. **Slow onboarding**: New developers can't run or test locally

### If P2 Items Are Not Addressed

1. **Suboptimal configs**: Can't learn which experiment strategies work
2. **Generic viability analysis**: Marketplace and SaaS get same treatment
3. **HITL bottleneck**: Approvals remain simulated, can't use in production
4. **Privacy risk**: PII may leak into learning database

---

## Conclusion

StartupAI has a solid conceptual architecture that correctly applies the Innovation Physics framework. The state schemas and flow logic demonstrate deep understanding of the Strategyzer validation methodology.

However, the implementation has critical gaps between design and code:

1. **Contracts are loose** - Dict returns instead of Pydantic models
2. **Persistence is missing** - No StateRepository or event logging
3. **Learning is unimplemented** - Tools are stubs, not working code
4. **Observability is absent** - Print statements instead of structured logs
5. **DX is minimal** - No tests, seeds, or simulation scripts

Addressing the P0 items (state unification, contracts, error handling, persistence) will create a stable foundation. The P1 items (learning tools, logging, tests) will make the system operationally viable. The P2 items will differentiate StartupAI from "a fancy script" into "an industrial-grade, compounding system."

**Recommended next session**: Start with state schema unification and tool contracts (P0), as all other work depends on stable data models.
