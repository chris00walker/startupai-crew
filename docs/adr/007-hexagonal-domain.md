# ADR-007: Hexagonal Domain Preparation

**Status**: Accepted
**Date**: 2026-01-23
**Decision Makers**: Chris Walker, Claude AI Assistant
**Context**: Need to improve testability and reduce framework coupling in CrewAI crews
**Related**: [Hexagonal Extraction Plan](../master-architecture/reference/hexagonal-extraction-plan.md)

## Summary

Prepare for future hexagonal architecture extraction by **marking domain candidates in traceability metadata** without performing any refactoring now. This establishes a clear migration path while allowing current development to continue uninterrupted.

The preparation adds two fields to the traceability override schema:
- `domain_candidate: true` - Marks a story as containing extractable domain logic
- `domain_function: <name>` - Names the future pure function

## Context

### The Problem

CrewAI crews currently contain both:
1. **Domain logic** - Pure business rules (fit scoring, gate evaluation, pivot decisions)
2. **Orchestration code** - Framework-specific wiring (CrewAI tasks, Modal handlers, Supabase writes)

This coupling creates friction:

| Issue | Impact |
|-------|--------|
| Tests require full stack | Slow feedback, flaky CI |
| Domain changes touch multiple layers | High change amplification |
| Business rules scattered across crews | Hard to reason about validation logic |
| Framework lock-in | Difficult to evolve or white-label |

### Why Not Extract Now?

Immediate extraction would be premature:

1. **Stability first** - Current architecture works; extraction is optimization
2. **Risk** - Large refactoring could introduce regressions before Phase Alpha launch
3. **Uncertainty** - Don't yet know which extractions provide most value
4. **Velocity** - Current sprint priorities are feature completion, not architecture

### The Insight

We can **mark** extraction candidates without **performing** extraction. This:
- Documents architectural intent
- Creates a migration backlog
- Enables future planning
- Costs almost nothing to implement

## Decision

### 1. Add Domain Marker Fields to Traceability

Extend the traceability override schema to allow:

```yaml
# docs/traceability/story-code-overrides.yaml
US-AD09:
  db_tables: [validation_runs]
  notes: "FIT_SCORE Agent - Calculate Fit Score"
  domain_candidate: true           # NEW: Mark for extraction
  domain_function: calculate_fit_score  # NEW: Future function name
```

Implementation in `scripts/traceability/config.ts`:

```typescript
export const OVERRIDE_ALLOWED_FIELDS = [
  'db_tables',
  'notes',
  'implementation_status',
  'domain_candidate',    // Mark as future hexagonal domain extraction candidate
  'domain_function',     // Future function name for domain extraction
] as const;
```

### 2. Query Overrides Directly

Domain markers are **planning metadata**, not runtime data. Query them directly from the YAML:

```bash
# Find all extraction candidates
grep -B2 "domain_candidate: true" docs/traceability/story-code-overrides.yaml

# Find a specific candidate
yq '.["US-AD09"]' docs/traceability/story-code-overrides.yaml
```

The generated `story-code-map.json` does not need to include these fields.

### 3. Document the Extraction Plan

Create a reference document with:
- Target directory structure
- Before/after code examples
- Extraction phases prioritized by value
- Port interface definitions
- Testing strategy

See: [Hexagonal Extraction Plan](../master-architecture/reference/hexagonal-extraction-plan.md)

## Consequences

### Positive

- **Zero risk** - No code changes to crews, just metadata
- **Clear intent** - Future developers understand the architectural direction
- **Incremental path** - Can extract one function at a time when ready
- **Traceability integration** - Markers live alongside existing story metadata

### Negative

- **Not enforced** - Markers are advisory; nothing prevents adding more coupled code
- **Maintenance** - Must remember to update markers as understanding evolves
- **Deferred value** - Actual benefits only realized when extraction happens

### Neutral

- **No runtime impact** - Markers are documentation only
- **Schema unchanged** - `story-code-map.json` structure not affected

## Alternatives Considered

### A. Extract Now

Immediately create `src/domain/` and extract all pure functions.

**Rejected**: Too risky before Phase Alpha, unclear prioritization, high effort.

### B. Do Nothing

Continue with current architecture, extract ad-hoc when pain becomes acute.

**Rejected**: Loses the planning benefit, no clear migration path, knowledge lost between sessions.

### C. Create Empty Domain Stubs

Create `src/domain/` directory with empty files as placeholders.

**Rejected**: Empty files create noise, markers in traceability are cleaner.

## Implementation

### Files Changed

| File | Change |
|------|--------|
| `scripts/traceability/config.ts` | Added `domain_candidate`, `domain_function` to allowed fields |
| `docs/traceability/story-code-overrides.yaml` | Updated header, added US-AD09 as proof of concept |
| `docs/traceability/README.md` | Documented new fields |
| `scripts/traceability/__tests__/validate-overrides.test.ts` | Added acceptance test |

### First Candidate Marked

**US-AD09: Calculate Fit Score** (`calculate_fit_score`)

This is the proof-of-concept marker. Future candidates include:
- US-AD10: `evaluate_discovery_gate`
- US-ADB05: `evaluate_desirability_gate`
- US-AFB03: `evaluate_feasibility_gate`
- US-AVB03: `evaluate_viability_gate`

### Verification

```bash
# Tests pass
pnpm traceability:test

# Validation passes
pnpm traceability:validate

# Marker queryable
grep -B1 "domain_candidate: true" docs/traceability/story-code-overrides.yaml
```

## When to Revisit

Trigger extraction when any of:
- Test suite becomes unacceptably slow (>5 min for unit tests)
- Domain change requires touching >3 files
- White-label requirement emerges
- Framework migration considered (CrewAI → LangGraph, Modal → Lambda)

## Related Documents

- [Hexagonal Extraction Plan](../master-architecture/reference/hexagonal-extraction-plan.md) - Full technical vision
- [Traceability README](../../../../app.startupai.site/docs/traceability/README.md) - Override field documentation
- [State Schemas](../master-architecture/reference/state-schemas.md) - Pydantic models (future domain schemas)

---
**Created**: 2026-01-23
