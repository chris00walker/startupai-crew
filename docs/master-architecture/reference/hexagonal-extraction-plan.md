# Hexagonal Architecture Extraction Plan

**Status**: Planning (Pre-Extraction)
**Related ADR**: [ADR-007: Hexagonal Domain Preparation](../../adr/007-hexagonal-domain.md)
**Traceability**: Stories marked with `domain_candidate: true` in [story-code-overrides.yaml](../../../../app.startupai.site/docs/traceability/story-code-overrides.yaml)

## Vision

Extract pure domain logic from CrewAI crews into a framework-agnostic domain layer. This enables:
- Fast unit tests (milliseconds, no CrewAI/Modal)
- Clean separation of business rules from orchestration
- Vendor portability (swap adapters, domain unchanged)
- White-label deployment flexibility

## Target Structure

```
startupai-crew/
  src/
    domain/                         # Pure Python, zero dependencies
      validation/
        fit_score.py               # calculate_fit_score(profile, value_map) -> FitAssessment
        evidence.py                # weigh_evidence(), triangulate_sources()
        phase_gates.py             # evaluate_gate(phase, signals) -> GateDecision
        pivot_rules.py             # should_pivot(fit, iteration) -> PivotRecommendation
      vpd/
        customer_profile.py        # VPD profile construction rules
        value_map.py               # VPD value map rules
        fit_canvas.py              # Problem-solution fit logic
      hypothesis/
        lifecycle.py               # assumption states, evidence thresholds
        test_card.py               # Test Card validation rules
      schemas/                     # Pydantic models (domain language)
        evidence.py
        fit.py
        gates.py

    ports/                          # Abstract interfaces (protocols)
      persistence.py               # PersistencePort (save_evidence, load_state)
      llm.py                       # LLMPort (generate, classify)
      orchestration.py             # OrchestrationPort (pause_for_hitl, resume)

    adapters/                       # Implementations
      crewai/                      # CrewAI adapter (thin wrapper)
        crews/                     # Current crews, now calling domain logic
      modal/                       # Modal adapter
        handlers.py                # HTTP handlers calling domain
      supabase/                    # Supabase adapter
        persistence.py             # Implements PersistencePort
      openai/                      # LLM adapter
        client.py                  # Implements LLMPort
```

## The Key Insight

**Crews become thin orchestration wrappers, not domain owners.**

### Before: Domain Logic Embedded in Crew

```python
# src/crews/discovery/fit_assessment_crew.py
class FitAssessmentCrew:
    @task
    def calculate_fit(self, state):
        # 50 lines of fit scoring logic HERE
        profile = state.customer_profile
        value_map = state.value_map
        # ... complex VPD calculations ...
        return FitAssessment(score=score, gaps=gaps)
```

### After: Crew is Thin Adapter

```python
# src/domain/validation/fit_score.py
def calculate_fit_score(
    profile: CustomerProfile,
    value_map: ValueMap,
    evidence: list[Evidence]
) -> FitAssessment:
    """Pure VPD fit calculation. No framework dependencies."""
    # The actual algorithm lives HERE, testable in isolation
    ...

# src/adapters/crewai/crews/fit_assessment_crew.py
class FitAssessmentCrew:
    @task
    def calculate_fit(self, state):
        # Thin adapter: just calls domain logic
        return calculate_fit_score(
            state.customer_profile,
            state.value_map,
            state.evidence
        )
```

## Benefits

| Pain Point | How Hexagonal Solves It |
|------------|-------------------------|
| Slow tests (need CrewAI/Modal) | Domain tests are pure Python, run in milliseconds |
| Multi-layer changes for domain tweaks | Change `domain/`, adapters just call it |
| Traceability scattered | `@story US-AD09` on `domain/validation/fit_score.py` |
| Vendor lock-in risk | Swap adapter, domain unchanged |
| White-label complexity | Domain is portable, adapters per deployment |

## Extraction Phases

Don't rewrite everything. Extract incrementally based on value and risk.

### Phase 1: Fit Scoring (Highest Value)

**Story**: [US-AD09](../../../../app.startupai.site/docs/traceability/story-code-overrides.yaml) - Calculate Fit Score
**Target Function**: `calculate_fit_score`
**Why First**: Well-defined inputs/outputs, high test value, critical for HITL decisions

Steps:
1. Create `src/domain/validation/fit_score.py`
2. Extract the algorithm from `FitAssessmentCrew`
3. Add pure unit tests
4. Crew becomes thin adapter

### Phase 2: Phase Gates (Critical for HITL)

**Stories**: US-AD10, US-ADB05, US-AFB03, US-AVB03
**Target Functions**: `evaluate_discovery_gate`, `evaluate_desirability_gate`, `evaluate_feasibility_gate`, `evaluate_viability_gate`
**Why Second**: Gate decisions drive phase transitions, need reliable testing

Steps:
1. Create `src/domain/validation/phase_gates.py`
2. Extract gate evaluation logic from Modal handlers
3. Gate decisions become testable without Modal

### Phase 3: Pivot Rules

**Stories**: US-P01, US-P02, US-P03, US-P04
**Target Function**: `should_pivot`
**Why Third**: Pivot logic is complex, benefits from isolation

Steps:
1. Create `src/domain/validation/pivot_rules.py`
2. Extract pivot decision logic from governance crews

### Phase 4: Evidence & VPD

**Stories**: US-AD02, US-AD03, US-AD04, US-AD05
**Target Functions**: `weigh_evidence`, `triangulate_sources`, VPD canvas construction
**Why Last**: More entangled with LLM calls, needs careful port design

Steps:
1. Create `src/domain/validation/evidence.py`
2. Extract evidence weighting (pure logic)
3. Create `src/domain/vpd/` modules
4. Design `LLMPort` for AI-dependent operations

## Domain Candidate Discovery

Stories are marked as extraction candidates using traceability overrides:

```yaml
# docs/traceability/story-code-overrides.yaml
US-AD09:
  db_tables: [validation_runs]
  notes: "FIT_SCORE Agent - Calculate Fit Score"
  domain_candidate: true
  domain_function: calculate_fit_score
```

Query all candidates:
```bash
grep -B2 "domain_candidate: true" docs/traceability/story-code-overrides.yaml
```

## Port Definitions (Future)

```python
# src/ports/persistence.py
from typing import Protocol

class PersistencePort(Protocol):
    def save_evidence(self, evidence: Evidence) -> str: ...
    def load_validation_state(self, run_id: str) -> ValidationState: ...
    def update_phase(self, run_id: str, phase: Phase) -> None: ...

# src/ports/llm.py
class LLMPort(Protocol):
    def generate(self, prompt: str, schema: type[T]) -> T: ...
    def classify(self, text: str, categories: list[str]) -> str: ...

# src/ports/orchestration.py
class OrchestrationPort(Protocol):
    def pause_for_hitl(self, checkpoint: str, payload: dict) -> None: ...
    def resume(self, run_id: str, decision: Decision) -> None: ...
```

## Testing Strategy

```python
# tests/domain/test_fit_score.py
def test_calculate_fit_score_high_match():
    """Pure domain test - no CrewAI, no Modal, no Supabase."""
    profile = CustomerProfile(
        jobs=["validate business idea quickly"],
        pains=["wasting time on bad ideas"],
        gains=["confidence in direction"]
    )
    value_map = ValueMap(
        products=["AI validation platform"],
        pain_relievers=["automated research"],
        gain_creators=["evidence-based decisions"]
    )
    evidence = [Evidence(type="interview", strength=0.8)]

    result = calculate_fit_score(profile, value_map, evidence)

    assert result.score >= 0.7
    assert "strong problem-solution fit" in result.summary
```

## Migration Checklist

For each extraction:

- [ ] Identify pure logic vs framework-dependent code
- [ ] Create domain module with type hints
- [ ] Write pure unit tests first (TDD)
- [ ] Extract logic, leaving crew as thin wrapper
- [ ] Add `@story` annotation to domain file
- [ ] Update traceability: `pnpm traceability:generate`
- [ ] Remove `domain_candidate` marker (now extracted)

## Related Documents

- [ADR-007: Hexagonal Domain Preparation](../../adr/007-hexagonal-domain.md) - Decision record
- [Agent Specifications](./agent-specifications.md) - Current agent configs
- [State Schemas](./state-schemas.md) - Pydantic models (future domain schemas)
- [Tool Specifications](./tool-specifications.md) - Current tool implementations

---
**Created**: 2026-01-23
**Last Updated**: 2026-01-23
