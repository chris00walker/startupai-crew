---
purpose: Pydantic state schemas for Modal checkpoint/resume pattern
status: planning
last_reviewed: 2026-01-08
vpd_compliance: true
---

# State Schemas

> **Modal Migration**: This document supports the Modal serverless architecture. See [ADR-002](../../adr/002-modal-serverless-migration.md) for migration context.

This document defines the Pydantic state models used for checkpoint/resume pattern in Modal serverless functions.

---

## Overview

Modal functions persist state to Supabase at HITL checkpoints. When a human approves, the function resumes from the saved state. These schemas define the structure of persisted state.

**Key Pattern**: Checkpoint → Persist to Supabase → Terminate Container → Resume on Approval

---

## ValidationRunState (Top-Level)

The root state model persisted to `validation_runs.phase_state`:

```python
# TODO: Define during Modal implementation
class ValidationRunState(BaseModel):
    run_id: str
    project_id: str
    current_phase: int  # 0-4
    phase_outputs: Dict[str, Any]  # Per-phase output data
    hitl_state: Optional[str]  # Current checkpoint name
    pivot_history: List[str]  # SEGMENT_PIVOT, VALUE_PIVOT, etc.
    created_at: datetime
    updated_at: datetime
```

---

## Phase-Specific State Models

### Phase 0: OnboardingState

```python
# TODO: Define during implementation
# See 04-phase-0-onboarding.md for schema requirements
```

### Phase 1: VPCDiscoveryState

```python
# TODO: Define during implementation
# See 05-phase-1-vpc-discovery.md for schema requirements
```

### Phase 2: DesirabilityState

```python
# TODO: Define during implementation
# See 06-phase-2-desirability.md for schema requirements
```

### Phase 3: FeasibilityState

```python
# TODO: Define during implementation
# See 07-phase-3-feasibility.md for schema requirements
```

### Phase 4: ViabilityState

```python
# TODO: Define during implementation
# See 08-phase-4-viability.md for schema requirements
```

---

## Serialization Patterns

### Supabase JSONB Storage

```python
# TODO: Document serialization approach
# - model_dump(exclude_none=True) for writing
# - model_validate(data) for reading
```

### State Recovery

```python
# TODO: Document how to recover state on resume
```

---

## State Transitions

| From State | To State | Trigger |
|------------|----------|---------|
| Phase 0 | Phase 1 | `approve_founders_brief` |
| Phase 1 | Phase 2 | `approve_vpc_completion` |
| Phase 2 | Phase 3 | `approve_desirability_gate` |
| Phase 3 | Phase 4 | `approve_feasibility_gate` |
| Phase 4 | Complete | `request_human_decision` |

---

## Related Documents

- [modal-configuration.md](./modal-configuration.md) - Modal platform setup
- [database-schemas.md](./database-schemas.md) - Supabase table definitions
- [approval-workflows.md](./approval-workflows.md) - HITL checkpoint patterns
- [04-phase-0-onboarding.md](../04-phase-0-onboarding.md) - Phase 0 specification
- [05-phase-1-vpc-discovery.md](../05-phase-1-vpc-discovery.md) - Phase 1 specification
- [06-phase-2-desirability.md](../06-phase-2-desirability.md) - Phase 2 specification
- [07-phase-3-feasibility.md](../07-phase-3-feasibility.md) - Phase 3 specification
- [08-phase-4-viability.md](../08-phase-4-viability.md) - Phase 4 specification
- [ADR-002](../../adr/002-modal-serverless-migration.md) - Modal migration decision

---
**Last Updated**: 2026-01-08
**Status**: Planning stub - full content TBD during Modal implementation
