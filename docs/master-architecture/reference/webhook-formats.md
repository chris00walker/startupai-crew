---
purpose: Webhook payload schemas for Modal and product app integration
status: planning
last_reviewed: 2026-01-08
vpd_compliance: true
---

# Webhook Formats

> **Modal Migration**: This document supports the Modal serverless architecture. See [ADR-002](../../adr/002-modal-serverless-migration.md) for migration context.

This document defines webhook payload schemas for all event types in the Modal serverless architecture.

---

## Overview

While Supabase Realtime handles most real-time updates, webhooks may be used for:
- Direct Modal-to-Product-App notifications (if Realtime unavailable)
- External integrations (Slack, email notifications)
- Audit logging

### Unified Webhook Endpoint

All webhooks go to a single endpoint with `event_type` discriminator:

```
POST /api/crewai/webhook
Content-Type: application/json
Authorization: Bearer <WEBHOOK_SECRET>
```

---

## Event Types

| Event Type | Trigger | Purpose |
|------------|---------|---------|
| `progress` | Task completion | Real-time progress update |
| `hitl_required` | Checkpoint reached | Approval needed |
| `phase_complete` | Phase finished | Phase transition |
| `run_complete` | Validation done | Final results ready |
| `error` | Failure occurred | Error notification |

---

## Progress Event

Sent when a task completes within a phase.

```typescript
// TODO: Finalize schema during implementation
interface ProgressEvent {
  event_type: 'progress';
  run_id: string;
  phase: number;
  task_name: string;
  status: 'completed';
  message: string;
  timestamp: string;
}
```

---

## HITL Required Event

Sent when a human approval checkpoint is reached.

```typescript
// TODO: Finalize schema during implementation
interface HITLRequiredEvent {
  event_type: 'hitl_required';
  run_id: string;
  checkpoint_id: string;  // e.g., 'approve_founders_brief'
  phase: number;
  context: {
    summary: string;
    artifact_url?: string;
    decision_options: string[];  // e.g., ['approve', 'reject', 'revise']
  };
  timestamp: string;
}
```

---

## Phase Complete Event

Sent when a phase finishes (after HITL approval).

```typescript
// TODO: Finalize schema during implementation
interface PhaseCompleteEvent {
  event_type: 'phase_complete';
  run_id: string;
  phase: number;
  next_phase: number | null;  // null if final phase
  summary: string;
  timestamp: string;
}
```

---

## Run Complete Event

Sent when the entire validation run finishes.

```typescript
// TODO: Finalize schema during implementation
interface RunCompleteEvent {
  event_type: 'run_complete';
  run_id: string;
  final_decision: 'proceed' | 'pivot' | 'kill';
  pivot_type?: string;  // If pivot: 'SEGMENT_PIVOT', 'VALUE_PIVOT', etc.
  report_url: string;
  timestamp: string;
}
```

---

## Error Event

Sent when an error occurs.

```typescript
// TODO: Finalize schema during implementation
interface ErrorEvent {
  event_type: 'error';
  run_id: string;
  phase: number;
  error_code: string;
  error_message: string;
  recoverable: boolean;
  retry_after?: number;  // Seconds until retry is allowed
  timestamp: string;
}
```

---

## TypeScript Union Type

```typescript
// TODO: Add to shared types package
type WebhookEvent =
  | ProgressEvent
  | HITLRequiredEvent
  | PhaseCompleteEvent
  | RunCompleteEvent
  | ErrorEvent;

// Discriminated union handler
function handleWebhook(event: WebhookEvent) {
  switch (event.event_type) {
    case 'progress':
      // Handle progress
      break;
    case 'hitl_required':
      // Show approval modal
      break;
    // ...
  }
}
```

---

## Authentication

### Bearer Token Validation

```typescript
// TODO: Add validation example
// Verify Authorization header matches WEBHOOK_SECRET
```

### Signature Validation (Optional)

```typescript
// TODO: Consider HMAC signature for additional security
```

---

## Retry Policy

| Scenario | Retry Behavior |
|----------|----------------|
| 2xx response | No retry |
| 4xx response | No retry (client error) |
| 5xx response | Retry with exponential backoff |
| Timeout | Retry up to 3 times |

---

## Related Documents

- [api-contracts.md](./api-contracts.md) - Modal API endpoint specs
- [approval-workflows.md](./approval-workflows.md) - HITL checkpoint patterns
- [product-app-integration.md](./product-app-integration.md) - Product app integration guide
- [ADR-002](../../adr/002-modal-serverless-migration.md) - Modal migration decision

---
**Last Updated**: 2026-01-08
**Status**: Planning stub - full content TBD during Modal implementation
