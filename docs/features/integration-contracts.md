---
document_type: feature-audit
status: active
last_verified: 2026-01-13
---

# Integration Contracts

## Purpose
Bridge document that defines the contracts between the CrewAI backend (this repo) and the product app (`app.startupai.site`). Answers open questions from the product app's feature documentation.

## Quick Reference

| Contract | Direction | Mechanism | Status |
|----------|-----------|-----------|--------|
| Kickoff | Product → CrewAI | `POST /kickoff` | `active` |
| Status Poll | Product → CrewAI | `GET /status/{run_id}` | `active` |
| HITL Approval | Product → CrewAI | `POST /hitl/approve` | `active` |
| Progress Events | CrewAI → Product | Supabase Realtime | `active` |
| HITL Webhook | CrewAI → Product | `POST /api/crewai/webhook` | `active` |
| Completion Webhook | CrewAI → Product | `POST /api/crewai/webhook` | `active` |

---

## Product App Open Questions (Resolved)

The product app's `wiring-matrix.md` (lines 53-58) raised these integration questions:

### Q1: Do Modal endpoints match product app expectations?

**Answer**: YES ✅

| Expected Endpoint | Implementation | Status |
|-------------------|----------------|--------|
| `POST /kickoff` | `src/modal_app/app.py:202-247` | ✅ Implemented |
| `GET /status/{run_id}` | `src/modal_app/app.py:250-308` | ✅ Implemented |
| `POST /hitl/approve` | `src/modal_app/app.py:311-569` | ✅ Implemented |

**Base URL**: `https://chris00walker--startupai-validation-fastapi-app.modal.run`

### Q2: Webhook vs Supabase Realtime - which pattern?

**Answer**: BOTH ✅

| Pattern | Use Case | Implementation |
|---------|----------|----------------|
| Supabase Realtime | Real-time progress updates | `validation_progress` table inserts |
| Webhook | HITL checkpoint notification | `POST /api/crewai/webhook` with `flow_type: "hitl_checkpoint"` |
| Webhook | Completion notification | `POST /api/crewai/webhook` with `flow_type: "founder_validation"` |

**Rationale**:
- Supabase Realtime for low-latency progress streaming (WebSocket)
- Webhooks for important events that need guaranteed delivery and product app side effects

### Q3: Phase 0 endpoint mapping - spec vs product app?

**Answer**: SEPARATED BY DESIGN ✅

| Layer | Responsibility | Endpoints |
|-------|----------------|-----------|
| Product App | Onboarding interview UI | `/api/onboarding/*`, `/api/chat` |
| CrewAI (Modal) | Phase 0 OnboardingCrew execution | `/kickoff` triggers all phases |

**Flow**:
```
[Product App Onboarding] → Captures entrepreneur_input via AI chat
                       → POST /api/onboarding/complete
                       → POST /kickoff to Modal with entrepreneur_input
                       → Phase 0 OnboardingCrew processes
                       → FoundersBrief generated
                       → HITL checkpoint created
```

The spec's `/interview/start` endpoint is not needed - the product app's `/api/onboarding/*` handles the interview UI, and Phase 0 receives the final `entrepreneur_input`.

### Q4: HITL flow - approval_requests table alignment?

**Answer**: CORRECT ✅

**CrewAI Side**:
```
[Phase N] → create_hitl_request() → INSERT into hitl_requests
                                 → _send_hitl_webhook() → POST /api/crewai/webhook
```

**Product App Side**:
```
[Webhook received] → INSERT into approval_requests (product app table)
                  → User sees in /approvals UI
                  → User makes decision
                  → PATCH /api/approvals/[id]
                  → POST /hitl/approve to Modal
                  → Modal resumes execution
```

**Tables**:
- `hitl_requests` (Supabase, owned by CrewAI) - Source of truth for HITL state
- `approval_requests` (Supabase, owned by Product App) - UI-friendly representation

---

## API Contracts

### POST /kickoff

**Request** (TypeScript):
```typescript
interface KickoffRequest {
  project_id: string;         // UUID
  user_id: string;            // UUID
  entrepreneur_input: string; // Min 10 chars, from onboarding
  session_id?: string;        // UUID, optional onboarding session
}
```

**Response**:
```typescript
interface KickoffResponse {
  run_id: string;   // UUID - Use for status polling
  status: "started";
  message: string;
}
```

**Product App Usage** (`/api/analyze/route.ts`):
```typescript
const response = await fetch(
  `${process.env.MODAL_API_URL}/kickoff`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.MODAL_BEARER_TOKEN}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      project_id: projectId,
      user_id: userId,
      entrepreneur_input: entrepreneurInput,
      session_id: sessionId,
    }),
  }
);
const { run_id } = await response.json();
```

### GET /status/{run_id}

**Response** (TypeScript):
```typescript
interface StatusResponse {
  run_id: string;
  status: 'pending' | 'running' | 'paused' | 'completed' | 'failed';
  current_phase: number;    // 0-4
  phase_name: string;       // Human-readable
  progress: ProgressItem[];
  hitl_pending?: HITLRequest;
  started_at?: string;
  updated_at?: string;
  error_message?: string;
}

interface ProgressItem {
  id: string;
  run_id: string;
  phase: number;
  crew: string;
  agent?: string;
  task?: string;
  status: 'started' | 'in_progress' | 'completed' | 'failed' | 'skipped';
  progress_pct?: number;
  output?: any;
  created_at: string;
}

interface HITLRequest {
  id: string;
  checkpoint_name: string;
  phase: number;
  title: string;
  description: string;
  options: DecisionOption[];
  recommended_option?: string;
  context: any;
}

interface DecisionOption {
  value: string;
  label: string;
  description: string;
}
```

### POST /hitl/approve

**Request** (TypeScript):
```typescript
interface HITLApproveRequest {
  run_id: string;
  checkpoint: string;
  decision: Decision;
  feedback?: string;
  custom_segment_data?: {
    segment_name: string;
    segment_description?: string;
  };
}

type Decision =
  | 'approved'
  | 'rejected'
  | 'override_proceed'
  | 'iterate'
  | 'segment_1' | 'segment_2' | 'segment_3'
  | 'custom_segment';
```

**Response**:
```typescript
interface HITLApproveResponse {
  status: 'resumed' | 'rejected' | 'pivot' | 'iterate';
  next_phase?: number;
  pivot_type?: 'segment_pivot' | 'value_pivot';
  message: string;
}
```

**Product App Usage** (`PATCH /api/approvals/[id]/route.ts`):
```typescript
const response = await fetch(
  `${process.env.MODAL_API_URL}/hitl/approve`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.MODAL_BEARER_TOKEN}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      run_id: approvalRequest.run_id,
      checkpoint: approvalRequest.checkpoint_name,
      decision: decision,
      feedback: feedback,
    }),
  }
);
```

---

## Webhook Contracts

### HITL Checkpoint Webhook

**Endpoint**: `POST {PRODUCT_APP_URL}/api/crewai/webhook`

**Payload**:
```typescript
interface HITLWebhookPayload {
  flow_type: 'hitl_checkpoint';
  run_id: string;
  project_id: string;
  user_id: string;
  checkpoint: string;
  title: string;
  description: string;
  options: DecisionOption[];
  recommended: string;
  context: any;              // Phase-specific data
  expires_at: string;        // ISO timestamp, 7 days from now
  timestamp: string;         // ISO timestamp
}
```

**Product App Handler** (`/api/crewai/webhook/route.ts`):
```typescript
export async function POST(req: Request) {
  const payload = await req.json();

  if (payload.flow_type === 'hitl_checkpoint') {
    // Insert into approval_requests for UI display
    await supabase.from('approval_requests').insert({
      run_id: payload.run_id,
      project_id: payload.project_id,
      user_id: payload.user_id,
      checkpoint_name: payload.checkpoint,
      title: payload.title,
      description: payload.description,
      options: payload.options,
      recommended_option: payload.recommended,
      context: payload.context,
      expires_at: payload.expires_at,
      status: 'pending',
    });
  }
}
```

### Completion Webhook

**Endpoint**: `POST {PRODUCT_APP_URL}/api/crewai/webhook`

**Payload**:
```typescript
interface CompletionWebhookPayload {
  flow_type: 'founder_validation';
  run_id: string;
  status: 'completed';
  result: ValidationResult;
}

interface ValidationResult {
  founders_brief: FoundersBrief;
  customer_profile: CustomerProfile;
  value_map: ValueMap;
  desirability_evidence: DesirabilityEvidence;
  feasibility_evidence: FeasibilityEvidence;
  viability_evidence: ViabilityEvidence;
  final_decision: 'proceed' | 'pivot' | 'kill';
  decision_rationale: string;
}
```

---

## Supabase Realtime Patterns

### Progress Subscription

**Channel**: `progress:{run_id}`

```typescript
// Product App subscription
const progressChannel = supabase
  .channel(`progress:${runId}`)
  .on(
    'postgres_changes',
    {
      event: 'INSERT',
      schema: 'public',
      table: 'validation_progress',
      filter: `run_id=eq.${runId}`,
    },
    (payload) => {
      const event = payload.new as ProgressItem;
      // Update progress timeline UI
      setProgressEvents(prev => [...prev, event]);
    }
  )
  .subscribe();
```

### HITL Notification Subscription

**Channel**: `hitl:{user_id}`

```typescript
// Product App subscription
const hitlChannel = supabase
  .channel(`hitl:${userId}`)
  .on(
    'postgres_changes',
    {
      event: 'INSERT',
      schema: 'public',
      table: 'hitl_requests',
      filter: `run_id=in.(${userRunIds.join(',')})`,
    },
    (payload) => {
      const request = payload.new as HITLRequest;
      // Show approval notification
      showNotification(`Approval needed: ${request.title}`);
    }
  )
  .subscribe();
```

---

## Environment Variables

### Product App (required for Modal integration)

```env
# Modal API
MODAL_API_URL=https://chris00walker--startupai-validation-fastapi-app.modal.run
MODAL_BEARER_TOKEN=startupai-modal-secret-2026

# Supabase (same instance as CrewAI)
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
```

### CrewAI Modal (required for webhooks)

```env
# Product App webhook
PRODUCT_APP_URL=https://app.startupai.site
WEBHOOK_BEARER_TOKEN=startupai-modal-secret-2026

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...  # Service role key
```

---

## Error Handling

### Product App → CrewAI Errors

| Error | HTTP Code | Handling |
|-------|-----------|----------|
| Invalid request | 400 | Show validation error |
| Unauthorized | 401 | Redirect to login |
| Run not found | 404 | Show "Run not found" message |
| Server error | 500 | Retry with exponential backoff |

### CrewAI → Product App Webhook Errors

| Error | Handling |
|-------|----------|
| Webhook timeout | Log warning, continue (non-blocking) |
| Webhook 4xx | Log error, no retry |
| Webhook 5xx | Retry 3 times with backoff |

---

## Data Model Alignment

### Shared Supabase Tables

Both repos access these tables:

| Table | Writer | Reader | Purpose |
|-------|--------|--------|---------|
| `validation_runs` | CrewAI | Both | Run state |
| `validation_progress` | CrewAI | Product | Progress events |
| `hitl_requests` | CrewAI | Product | HITL requests |
| `approval_requests` | Product | Product | UI-optimized approvals |

### Product App Tables (not shared)

| Table | Purpose |
|-------|---------|
| `projects` | Project metadata |
| `user_profiles` | User settings |
| `onboarding_sessions` | Onboarding chat history |

---

## Testing Integration

### E2E Test Flow

```
1. Product App: Create user + project
2. Product App: POST /api/analyze (triggers Modal)
3. Modal: Runs Phase 0
4. Modal: Creates HITL checkpoint
5. Modal: Sends webhook to Product App
6. Product App: Shows approval in /approvals
7. Product App: PATCH /api/approvals/[id]
8. Modal: Resumes from checkpoint
9. Modal: Completes all phases
10. Modal: Sends completion webhook
11. Product App: Shows results
```

### Test Accounts

| Role | Email | Purpose |
|------|-------|---------|
| Founder | chris00walker@proton.me | E2E validation testing |
| Consultant | chris00walker@gmail.com | Multi-client testing |

---

## Feature Audit Cross-Reference

This document bridges to all other feature audit documents:

| Document | What It Covers |
|----------|----------------|
| [flow-inventory.md](./flow-inventory.md) | 5 Flows, entry/exit criteria |
| [crew-agent-task-matrix.md](./crew-agent-task-matrix.md) | 14 Crews, 45 Agents, 68 Tasks |
| [hitl-checkpoint-map.md](./hitl-checkpoint-map.md) | 10 HITL checkpoints |
| [api-entrypoints.md](./api-entrypoints.md) | 4 API endpoints |
| [tool-wiring-matrix.md](./tool-wiring-matrix.md) | 19 tools, wiring status |
| [phase-mapping.md](./phase-mapping.md) | Spec vs implementation |
| [state-persistence.md](./state-persistence.md) | Supabase tables, functions |

---

## Product App Feature References

The product app's feature docs that reference this repo:

| Product App Doc | Our Resolution |
|-----------------|----------------|
| `wiring-matrix.md:53-58` | Answered in "Open Questions" section |
| `feature-inventory.md:129-132` | All referenced specs current |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-01-13 | Initial document, answered product app questions |

---

## Related Documents

- [../master-architecture/01-ecosystem.md](../master-architecture/01-ecosystem.md) - Three-layer architecture
- [../adr/002-modal-serverless-migration.md](../adr/002-modal-serverless-migration.md) - Architecture decision
- [~/projects/app.startupai.site/docs/features/wiring-matrix.md](~/projects/app.startupai.site/docs/features/wiring-matrix.md) - Product app integration
