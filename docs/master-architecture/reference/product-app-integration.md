---
purpose: Product app integration with Modal serverless and Supabase Realtime
status: planning
last_reviewed: 2026-01-08
vpd_compliance: true
---

# Product App Integration

> **Modal Migration**: This document supports the Modal serverless architecture. See [ADR-002](../../adr/002-modal-serverless-migration.md) for migration context.

This document guides product app developers on consuming the Modal API and Supabase Realtime for validation workflows.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PRODUCT APP (app.startupai.site)                                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │ Kickoff Button  │  │ Progress UI     │  │ Approval Modal  │             │
│  └────────┬────────┘  └────────▲────────┘  └────────┬────────┘             │
│           │                    │                    │                       │
├───────────┼────────────────────┼────────────────────┼───────────────────────┤
│           │                    │                    │                       │
│           ▼                    │                    ▼                       │
│  ┌─────────────────┐  ┌────────┴────────┐  ┌─────────────────┐             │
│  │ Modal /kickoff  │  │ Supabase        │  │ Modal           │             │
│  │ API             │  │ Realtime        │  │ /hitl/approve   │             │
│  └────────┬────────┘  └────────▲────────┘  └────────┬────────┘             │
│           │                    │                    │                       │
├───────────┼────────────────────┼────────────────────┼───────────────────────┤
│           │                    │                    │                       │
│           ▼                    │                    ▼                       │
│  ┌─────────────────────────────┴────────────────────────────────┐          │
│  │                      Modal Functions                          │          │
│  │  (OnboardingFlow → VPCDiscoveryFlow → ... → ViabilityFlow)   │          │
│  └───────────────────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Kickoff Flow

### User Triggers Validation

```typescript
// TODO: Add implementation example
// POST /api/crewai/analyze → calls Modal /kickoff
```

### Modal Response

```json
{
  "run_id": "uuid",
  "status": "started",
  "phase": 0
}
```

---

## Progress Updates

### Supabase Realtime Subscription

```typescript
// TODO: Add React hook example
// useValidationProgress(runId)
```

### Progress Event Schema

```typescript
// TODO: Define TypeScript interface
interface ValidationProgress {
  run_id: string;
  phase: number;
  task_name: string;
  status: 'started' | 'completed' | 'failed';
  message?: string;
  created_at: string;
}
```

### UI Component Pattern

```typescript
// TODO: Add component example
// <ValidationProgress runId={runId} />
```

---

## HITL Handling

### Subscribing to Approval Requests

```typescript
// TODO: Add Realtime subscription for hitl_requests
```

### Approval Modal Component

```typescript
// TODO: Add ApprovalModal component pattern
// - Displays checkpoint context
// - Approve/Reject buttons
// - Sends decision to Modal
```

### Sending Approval

```typescript
// TODO: Add approval API call example
// POST /api/hitl/approve → calls Modal /hitl/approve
```

---

## Results Display

### Reading Final Results

```typescript
// TODO: Add result fetching example
// Read from validation_runs.phase_state
```

### Per-Phase Output Components

| Phase | Component | Displays |
|-------|-----------|----------|
| 0 | `<FoundersBriefCard />` | Founder's Brief summary |
| 1 | `<VPCCanvas />` | Customer Profile + Value Map |
| 2 | `<DesirabilityReport />` | Desirability metrics |
| 3 | `<FeasibilityReport />` | Feasibility assessment |
| 4 | `<FinalReport />` | Complete validation report |

---

## Error Handling

### Failed Runs

```typescript
// TODO: Add error handling pattern
// - Display error message
// - Retry option
// - Support contact
```

### Timeout Handling

```typescript
// TODO: Add timeout handling
// - Poll status if Realtime disconnects
// - Show stale indicator
```

---

## Related Documents

- [api-contracts.md](./api-contracts.md) - Modal API endpoint specs
- [database-schemas.md](./database-schemas.md) - Supabase table schemas
- [supabase-configuration.md](./supabase-configuration.md) - Realtime and RLS setup
- [approval-workflows.md](./approval-workflows.md) - HITL checkpoint patterns
- [state-schemas.md](./state-schemas.md) - Pydantic state models
- [ADR-002](../../adr/002-modal-serverless-migration.md) - Modal migration decision

---
**Last Updated**: 2026-01-08
**Status**: Planning stub - full content TBD during Modal implementation
