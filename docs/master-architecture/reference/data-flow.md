---
purpose: Complete data flow documentation from tool output to Supabase storage
status: active
last_reviewed: 2026-01-10
vpd_compliance: true
---

# Data Flow: Tool Output → State → Supabase

This document describes the complete data flow through the StartupAI validation engine, from tool output to Supabase persistence.

> **Cross-Repo Coordination**: This document captures schema alignment analysis between `startupai-crew` (Pydantic models) and `app.startupai.site` (Supabase tables). See [database-schemas.md](./database-schemas.md) for table definitions.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        TOOL LAYER                                        │
│  TavilySearchTool, ForumSearchTool, ReviewAnalysisTool, etc.            │
│  Output: Formatted strings with structured data                          │
│  Location: src/shared/tools/                                             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        TASK LAYER                                        │
│  Agent processes tool outputs via context chaining                       │
│  Output: Raw string or output_pydantic model                             │
│  Location: src/crews/*/config/tasks.yaml                                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        PYDANTIC LAYER                                    │
│  FoundersBrief, CustomerProfile, ValueMap, DesirabilityEvidence, etc.   │
│  result.pydantic → typed Pydantic instance                               │
│  Location: src/state/models.py                                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        STATE LAYER                                       │
│  ValidationRunState (src/state/models.py:559)                            │
│  state.model_dump(mode="json") → dict                                    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        PERSISTENCE LAYER                                 │
│  checkpoint_state() in src/state/persistence.py                          │
│  supabase.table("validation_runs").update(phase_state=JSONB)            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        SUPABASE LAYER                                    │
│  validation_runs (Modal checkpoint state)                                │
│  validation_progress (Realtime UI updates)                               │
│  hitl_requests (HITL checkpoint/resume)                                  │
│  crewai_validation_states (Product App consumption)                      │
│  learnings, patterns, outcomes (Flywheel learning)                       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Data Flow

### 1. Tool Layer

**Location**: `src/shared/tools/`

Tools output formatted strings that agents consume as context:

```python
# Example: TavilySearchTool output
## Web Search Results for: startup validation challenges
Found 5 results in 234ms
### Summary
Early-stage startups face challenges with...
### Sources
1. TechCrunch Article
   URL: https://techcrunch.com/...
   Relevance: 0.92
```

**Key Tools**:
| Tool | Output Type | Used By |
|------|-------------|---------|
| `TavilySearchTool` | `WebSearchOutput` → string | D2, J1, Research agents |
| `ForumSearchTool` | `ForumSearchOutput` → string | D2, PAIN_RES, GAIN_RES |
| `ReviewAnalysisTool` | `ReviewAnalysisOutput` → string | D2 |
| `TestCardTool` | `TestCardOutput` → structured | E1 |
| `LearningCardTool` | `LearningCardOutput` → structured | E1, D4 |

### 2. Task Layer

**Location**: `src/crews/*/config/tasks.yaml`

Tasks chain together via `context:` field:

```yaml
conduct_founder_interview:
  agent: o1_founder_interview
  expected_output: "Structured interview summary..."

validate_concept_legitimacy:
  agent: gv1_concept_validator
  context:
    - conduct_founder_interview  # Receives previous task output
  expected_output: "JSON validation report..."

compile_founders_brief:
  agent: s1_brief_compiler
  context:
    - conduct_founder_interview
    - validate_concept_legitimacy
    - verify_intent_capture
  expected_output: "Complete Founder's Brief..."
```

### 3. Pydantic Layer

**Location**: `src/state/models.py`

Tasks with `output_pydantic=ModelName` produce typed instances:

```python
# Phase 0 Output
class FoundersBrief(BaseModel):
    the_idea: TheIdea
    problem_hypothesis: ProblemHypothesis
    customer_hypothesis: CustomerHypothesis
    solution_hypothesis: SolutionHypothesis
    key_assumptions: list[Assumption]
    success_criteria: SuccessCriteria
    qa_status: QAStatus

# Phase 1 Output
class CustomerProfile(BaseModel):
    segment_name: str
    jobs: list[CustomerJob]
    pains: list[CustomerPain]
    gains: list[CustomerGain]

class ValueMap(BaseModel):
    products_services: list[ProductService]
    pain_relievers: list[PainReliever]
    gain_creators: list[GainCreator]

class FitAssessment(BaseModel):
    fit_score: int  # 0-100
    fit_status: str  # strong|moderate|weak|none
    gate_ready: bool
```

### 4. State Layer

**Location**: `src/state/models.py:559`

All phase outputs aggregate into `ValidationRunState`:

```python
class ValidationRunState(BaseModel):
    # Identity
    run_id: UUID
    project_id: UUID
    user_id: UUID

    # Execution state
    current_phase: int  # 0-4
    status: str  # pending|running|paused|completed|failed
    hitl_state: Optional[str]

    # Phase outputs
    entrepreneur_input: str
    founders_brief: Optional[FoundersBrief]
    customer_profile: Optional[CustomerProfile]
    value_map: Optional[ValueMap]
    fit_assessment: Optional[FitAssessment]
    desirability_evidence: Optional[DesirabilityEvidence]
    feasibility_evidence: Optional[FeasibilityEvidence]
    viability_evidence: Optional[ViabilityEvidence]

    # Signals
    desirability_signal: Optional[ValidationSignal]
    feasibility_signal: Optional[ValidationSignal]
    viability_signal: Optional[ValidationSignal]

    # Final decision
    pivot_recommendation: Optional[PivotRecommendation]
    final_decision: Optional[str]
```

### 5. Persistence Layer

**Location**: `src/state/persistence.py`

Checkpoint/resume pattern for Modal serverless:

```python
def checkpoint_state(run_id: str, state: ValidationRunState, hitl_checkpoint: Optional[str] = None):
    state_json = state.model_dump(mode="json")  # Serialize Pydantic → dict

    update_data = {
        "phase_state": state_json,      # Full state as JSONB
        "current_phase": state.current_phase,
        "updated_at": datetime.now().isoformat(),
    }

    if hitl_checkpoint:
        update_data["hitl_state"] = hitl_checkpoint
        update_data["status"] = "paused"
        # Container terminates here - $0 cost during human review

    supabase.table("validation_runs").update(update_data).eq("id", run_id).execute()
```

### 6. Supabase Layer

**Location**: `app.startupai.site/supabase/migrations/`

Three Modal-specific tables:

| Table | Purpose | Realtime |
|-------|---------|----------|
| `validation_runs` | Checkpoint state (JSONB `phase_state`) | No |
| `validation_progress` | Append-only progress log | Yes |
| `hitl_requests` | HITL checkpoint/resume queue | Yes |

---

## Schema Alignment Matrix

| Pydantic Model | Supabase Table | Status | Notes |
|----------------|----------------|--------|-------|
| `ValidationRunState` | `validation_runs` | ✅ Migration created | Modal checkpoint state |
| `ValidationRunState` | `crewai_validation_states` | ✅ Deployed | Product App fallback |
| `FoundersBrief` | `entrepreneur_briefs` | ⚠️ Mismatch | Flat vs nested structure |
| `FoundersBrief` | `founders_briefs` | ⏳ Planned | VPD-aligned version |
| `CustomerProfile` | `customer_profile_elements` | ⏳ Planned | Normalized VPC |
| `ValueMap` | `value_map_elements` | ⏳ Planned | Normalized VPC |
| `FitAssessment` | `vpc_fit_scores` | ⏳ Planned | Fit tracking |
| `Experiment` | `test_cards` + `learning_cards` | ⏳ Planned | TBI framework |
| `DesirabilityEvidence` | JSONB in `crewai_validation_states` | ✅ Works | Flexible storage |
| `FeasibilityEvidence` | JSONB in `crewai_validation_states` | ✅ Works | Flexible storage |
| `ViabilityEvidence` | JSONB in `crewai_validation_states` | ✅ Works | Flexible storage |
| Flywheel models | `learnings`, `patterns`, `outcomes` | ✅ Deployed | pgvector search |

### Migration Status

| Priority | Table | Status | Migration File |
|----------|-------|--------|----------------|
| P0 | `validation_runs` | ✅ Migration created | `20260110000001_modal_validation_runs.sql` |
| P0 | `validation_progress` | ✅ Migration created | `20260110000002_modal_validation_progress.sql` |
| P0 | `hitl_requests` | ✅ Migration created | `20260110000003_modal_hitl_requests.sql` |
| P1 | `founders_briefs` | ⏳ Planned | Not yet created |
| P2 | `customer_profile_elements` | ⏳ Planned | Not yet created |
| P2 | `value_map_elements` | ⏳ Planned | Not yet created |
| P2 | `vpc_fit_scores` | ⏳ Planned | Not yet created |
| P3 | `test_cards` | ⏳ Planned | Not yet created |
| P3 | `learning_cards` | ⏳ Planned | Not yet created |

---

## Serialization Patterns

### Pydantic → Supabase

```python
# In persistence.py
state_json = state.model_dump(mode="json")
# mode="json" ensures:
# - UUIDs → strings
# - datetime → ISO strings
# - Enums → string values
# - Nested models → dicts
```

### Supabase → Pydantic

```python
# In persistence.py
result = supabase.table("validation_runs").select("*").eq("id", run_id).single().execute()
phase_state = result.data.get("phase_state", {})
state = ValidationRunState(**phase_state)  # Pydantic validates on instantiation
```

---

## Signal Flow for Phase Routing

Validation signals gate phase transitions:

```
Phase 2 (Desirability)
  │
  ├─ STRONG_COMMITMENT → Phase 3 (Feasibility)
  ├─ MILD_INTEREST → Segment pivot suggested
  └─ NO_INTEREST → Recommend kill

Phase 3 (Feasibility)
  │
  ├─ GREEN → Phase 4 (Viability)
  ├─ ORANGE_CONSTRAINED → Feature downgrade suggested
  └─ RED_IMPOSSIBLE → Recommend kill

Phase 4 (Viability)
  │
  ├─ PROFITABLE → PROCEED
  ├─ MARGINAL → Value pivot suggested
  └─ UNDERWATER → Recommend kill
```

---

## Related Documents

- [database-schemas.md](./database-schemas.md) - SQL table definitions
- [state-schemas.md](./state-schemas.md) - Pydantic model documentation
- [tool-specifications.md](./tool-specifications.md) - Tool implementation specs
- [ADR-002](../../adr/002-modal-serverless-migration.md) - Modal architecture decision

---

**Last Updated**: 2026-01-10
**Status**: Active - Schema alignment analysis complete, P0 migrations created
