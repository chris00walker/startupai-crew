---
document_type: feature-audit
status: active
last_verified: 2026-01-13
---

# HITL Checkpoint Map

## Purpose
Comprehensive mapping of all 10 Human-in-the-Loop checkpoints, their trigger conditions, decision options, and product app integration.

## Quick Reference

| Phase | Checkpoint | Trigger | Options | Default |
|-------|------------|---------|---------|---------|
| 0 | `approve_founders_brief` | Brief compiled | approve, revise, reject | approve |
| 1 | `approve_vpc_completion` | Fit assessed | approve, iterate, segment_pivot | approve (if fit ≥ 70) |
| 2 | `approve_desirability_gate` | strong_commitment signal | approved, iterate | approved |
| 2 | `approve_segment_pivot` | no_interest signal | segment_1/2/3, custom, override, iterate | segment_1 |
| 2 | `approve_value_pivot` | mild_interest signal | approved, override, iterate | approved |
| 3 | `approve_feasibility_gate` | Assessment complete | approve, feature_pivot, kill | approve (if green) |
| 4 | `request_human_decision` | Synthesis complete | proceed, price_pivot, cost_pivot, model_pivot, kill | proceed (if profitable) |

**Total**: 10 HITL checkpoints across 5 phases (7 unique, 3 conditional in Phase 2)

---

## HITL Model Schema

**File**: `src/state/models.py:527-547`

```python
class HITLCheckpoint(BaseModel):
    """A Human-in-the-Loop checkpoint."""

    checkpoint_name: str      # Unique identifier
    phase: int                # 0-4
    title: str                # Human-readable title
    description: str          # Decision context

    # Context for decision
    context: dict[str, Any]   # Phase-specific data (metrics, signals, etc.)

    # Decision options
    options: list[dict[str, str]]   # [{value, label, description}]
    recommended_option: str         # Default recommendation

    # Decision (filled after human input)
    decision: str             # Selected option value
    feedback: str             # Optional human feedback
    decided_by: UUID          # User ID
    decided_at: datetime      # Decision timestamp
```

---

## Phase 0: OnboardingFlow

### Checkpoint: `approve_founders_brief`

**Trigger Location**: `src/modal_app/phases/phase_0.py:180-210`

**Trigger Condition**: After OnboardingCrew completes Brief Compiler task

| Option | Value | Description | Next Action |
|--------|-------|-------------|-------------|
| **Approve** | `approve` | Founder's Brief is complete and accurate | → Phase 1 |
| Revise | `revise` | Request clarifications or corrections | → Loop Phase 0 |
| Reject | `reject` | Concept fails legitimacy check | → Fail |

**Default Recommendation**: `approve`

**Context Payload**:
```json
{
  "founders_brief": { /* FoundersBrief model */ },
  "qa_status": { "overall_status": "valid|invalid", "issues": [] },
  "word_count": 500,
  "completeness_score": 0.85
}
```

---

## Phase 1: VPCDiscoveryFlow

### Checkpoint: `approve_vpc_completion`

**Trigger Location**: `src/modal_app/phases/phase_1.py:370-410`

**Trigger Condition**: After FitAssessmentCrew scores VPC fit

| Option | Value | Description | Next Action |
|--------|-------|-------------|-------------|
| **Approve** | `approve` | VPC validated, proceed to Desirability | → Phase 2 |
| Iterate | `iterate` | Re-run discovery with refinements | → Loop Phase 1 |
| Segment Pivot | `segment_pivot` | Target different customer segment | → Loop Phase 1 |

**Default Recommendation**: `approve` if `fit_score >= 70`, else `iterate`

**Gate Condition**: `fit_score >= 70` required to proceed

**Context Payload**:
```json
{
  "customer_profile": { /* Jobs, Pains, Gains */ },
  "value_map": { /* Products, Pain Relievers, Gain Creators */ },
  "fit_assessment": {
    "fit_score": 75,
    "gate_ready": true,
    "gaps": []
  },
  "wtp_results": { /* Willingness-to-pay analysis */ }
}
```

---

## Phase 2: DesirabilityFlow

Phase 2 has **signal-based routing** - the checkpoint triggered depends on market signals.

### Signal Determination (Innovation Physics)

**Calculation Location**: `src/modal_app/phases/phase_2.py:236-248`

```python
problem_resonance = (clicks + signups) / impressions
zombie_ratio = (clicks - signups) / clicks
```

| Signal | Condition | Checkpoint |
|--------|-----------|------------|
| `strong_commitment` | resonance >= 30%, zombie < 70% | `approve_desirability_gate` |
| `no_interest` | resonance < 30% | `approve_segment_pivot` |
| `mild_interest` | resonance >= 30%, zombie >= 70% | `approve_value_pivot` |

---

### Checkpoint: `approve_desirability_gate`

**Trigger**: `strong_commitment` signal detected

| Option | Value | Description | Next Action |
|--------|-------|-------------|-------------|
| **Proceed** | `approved` | Strong market signal, proceed to Feasibility | → Phase 3 |
| Iterate | `iterate` | Run more experiments for additional evidence | → Loop Phase 2 |

**Default Recommendation**: `approved`

**Context Payload**:
```json
{
  "desirability_evidence": {
    "impressions": 10000,
    "clicks": 450,
    "signups": 150,
    "problem_resonance": 0.045,
    "zombie_ratio": 0.67,
    "signal": "strong_commitment"
  },
  "build_results": { /* Landing page, ad creative URLs */ }
}
```

---

### Checkpoint: `approve_segment_pivot`

**Trigger**: `no_interest` signal detected

| Option | Value | Description | Next Action |
|--------|-------|-------------|-------------|
| **Segment 1** | `segment_1` | GPT-generated alternative segment | → Phase 1 (pivot) |
| Segment 2 | `segment_2` | GPT-generated alternative segment | → Phase 1 (pivot) |
| Segment 3 | `segment_3` | GPT-generated alternative segment | → Phase 1 (pivot) |
| Custom | `custom_segment` | User-defined segment hypothesis | → Phase 1 (pivot) |
| Override | `override_proceed` | Ignore signal, proceed anyway | → Phase 3 |
| Iterate | `iterate` | Re-run experiments with current segment | → Loop Phase 2 |

**Default Recommendation**: `segment_1` (highest confidence alternative)

**Segment Alternatives Generation**: `src/modal_app/helpers/segment_alternatives.py:20-80`

**Context Payload**:
```json
{
  "desirability_evidence": {
    "problem_resonance": 0.15,
    "zombie_ratio": 0.80,
    "signal": "no_interest"
  },
  "failed_segment": {
    "segment_name": "SMB Owners",
    "failure_reason": "Low problem resonance"
  },
  "segment_alternatives": [
    { "segment_name": "Enterprise IT Directors", "confidence": 0.75, "rationale": "..." },
    { "segment_name": "Startup CTOs", "confidence": 0.68, "rationale": "..." },
    { "segment_name": "Freelance Developers", "confidence": 0.55, "rationale": "..." }
  ]
}
```

---

### Checkpoint: `approve_value_pivot`

**Trigger**: `mild_interest` signal detected (clicks but no conversions)

| Option | Value | Description | Next Action |
|--------|-------|-------------|-------------|
| **Pivot** | `approved` | Return to refine value proposition | → Phase 1 |
| Override | `override_proceed` | Ignore signal, proceed anyway | → Phase 3 |
| Iterate | `iterate` | Run more experiments for clarity | → Loop Phase 2 |

**Default Recommendation**: `approved`

**Context Payload**:
```json
{
  "desirability_evidence": {
    "problem_resonance": 0.35,
    "zombie_ratio": 0.85,
    "signal": "mild_interest"
  },
  "diagnosis": "High click-through but low conversion suggests value proposition mismatch"
}
```

---

## Phase 3: FeasibilityFlow

### Checkpoint: `approve_feasibility_gate`

**Trigger Location**: `src/modal_app/phases/phase_3.py:180-220`

**Trigger Condition**: After FeasibilityGovernanceCrew validates assessment

| Option | Value | Description | Next Action |
|--------|-------|-------------|-------------|
| **Approve** | `approve` | Technically feasible, proceed to Viability | → Phase 4 |
| Feature Pivot | `feature_pivot` | Downgrade features, re-test desirability | → Phase 2 |
| Kill | `kill` | Technical impossibility, no viable path | → Fail |

**Default Recommendation**: Based on signal:
- `green` → `approve`
- `orange_constrained` → `feature_pivot`
- `red_impossible` → `kill`

**Signal Determination**:
| Signal | Condition |
|--------|-----------|
| `green` | Core features feasible, no downgrade needed |
| `orange_constrained` | Feasible with feature constraints |
| `red_impossible` | Core features technically impossible |

**Context Payload**:
```json
{
  "feasibility_evidence": {
    "signal": "green",
    "technical_complexity": "medium",
    "estimated_dev_cost": "$50,000-$100,000",
    "timeline_months": 6,
    "key_risks": [],
    "required_capabilities": []
  },
  "downgrade_options": []
}
```

---

## Phase 4: ViabilityFlow

### Checkpoint: `request_human_decision`

**Trigger Location**: `src/modal_app/phases/phase_4.py:320-380`

**Trigger Condition**: After ViabilityGovernanceCrew synthesizes all evidence

| Option | Value | Description | Next Action |
|--------|-------|-------------|-------------|
| **Proceed** | `proceed` | Validation complete, move to execution | → Complete |
| Price Pivot | `price_pivot` | Increase prices, re-test desirability | → Phase 2 |
| Cost Pivot | `cost_pivot` | Reduce costs, re-assess feasibility | → Phase 3 |
| Model Pivot | `model_pivot` | Change business model fundamentally | → Phase 1 |
| Kill | `kill` | No viable path forward | → Fail |

**Default Recommendation**: Based on signal:
- `profitable` → `proceed`
- `marginal` → `price_pivot`
- `underwater` → `price_pivot` or `kill`

**Signal Determination**:
| Signal | Condition |
|--------|-----------|
| `profitable` | LTV/CAC >= 3.0 |
| `marginal` | 1.0 <= LTV/CAC < 3.0, TAM < $1M |
| `underwater` | LTV/CAC < 1.0 |

**Context Payload**:
```json
{
  "viability_evidence": {
    "signal": "profitable",
    "ltv": 1500,
    "cac": 350,
    "ltv_cac_ratio": 4.3,
    "tam": "$500M",
    "sam": "$50M",
    "som": "$5M"
  },
  "synthesis": {
    "recommendation": "proceed",
    "confidence": 0.85,
    "key_strengths": [],
    "key_risks": []
  },
  "all_evidence": { /* Aggregated from all phases */ }
}
```

---

## API Contract: HITL Approval

### Endpoint

```
POST /hitl/approve
```

**File**: `src/modal_app/app.py:311-569`

### Request Schema

**Model**: `HITLApproveRequest` (`src/modal_app/app.py:134-151`)

```typescript
interface HITLApproveRequest {
  run_id: string;       // UUID of validation run
  checkpoint: string;   // Checkpoint name
  decision: "approved" | "rejected" | "override_proceed" | "iterate"
          | "segment_1" | "segment_2" | "segment_3" | "custom_segment";
  feedback?: string;    // Optional human feedback
  custom_segment_data?: {  // Required if decision is "custom_segment"
    segment_name: string;
    segment_description?: string;
  };
}
```

### Response Schema

**Model**: `HITLApproveResponse` (`src/modal_app/app.py:154-159`)

```typescript
interface HITLApproveResponse {
  status: "resumed" | "rejected" | "pivot" | "iterate";
  next_phase: number | null;
  pivot_type?: "segment_pivot" | "value_pivot";
  message: string;
}
```

### Authentication

```
Authorization: Bearer <WEBHOOK_BEARER_TOKEN>
```

Default token: `startupai-modal-secret-2026` (override via environment variable)

---

## Decision Flow Logic

### Status Normalization

**File**: `src/modal_app/app.py:337-346`

```python
# Database status enum: pending | approved | rejected | expired
if request.decision in ("rejected", "reject"):
    normalized_status = "rejected"
elif request.decision == "iterate":
    normalized_status = "pending"  # Keeps request open
else:
    # segment_*, override_proceed, approved → approved
    normalized_status = "approved"
```

### Decision Handling

| Decision | Handler | State Update | Next Action |
|----------|---------|--------------|-------------|
| `approved` | Standard approval | `current_phase += 1` | Spawn `resume_from_checkpoint` |
| `approved` (pivot checkpoint) | Pivot approval | `current_phase = 1`, `pivot_type` set | Spawn `resume_from_checkpoint` |
| `segment_*` | Segment selection | `current_phase = 1`, `target_segment_hypothesis` set | Spawn `resume_from_checkpoint` |
| `custom_segment` | Custom segment | `current_phase = 1`, custom segment stored | Spawn `resume_from_checkpoint` |
| `override_proceed` | Override | `current_phase += 1`, `override_applied = true` | Spawn `resume_from_checkpoint` |
| `iterate` | Iteration | `iteration_count += 1` | Spawn `resume_from_checkpoint` |
| `rejected` | Rejection | `status = "paused"` | Workflow halted |

---

## Persistence Functions

### Create HITL Request

**File**: `src/state/persistence.py:226-290`

```python
def create_hitl_request(
    run_id: str,
    checkpoint: HITLCheckpoint,
) -> Optional[str]:
    """
    Create HITL approval request in Supabase.
    Container terminates after this - $0 cost during human review.
    """
```

**Database Table**: `hitl_requests`

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `run_id` | UUID | FK to validation_runs |
| `checkpoint_name` | string | Checkpoint identifier |
| `phase` | int | Phase number (0-4) |
| `title` | string | Human-readable title |
| `description` | text | Decision context |
| `context` | jsonb | Phase-specific data |
| `options` | jsonb | Array of decision options |
| `recommended_option` | string | Default recommendation |
| `status` | enum | pending, approved, rejected, expired |
| `decision` | string | Selected decision value |
| `feedback` | text | Human feedback |
| `decision_at` | timestamp | When decided |
| `decision_by` | UUID | Who decided |
| `created_at` | timestamp | Request created |
| `updated_at` | timestamp | Last updated |

### Get HITL Decision

**File**: `src/state/persistence.py:293-319`

```python
def get_hitl_decision(run_id: str, checkpoint_name: str) -> Optional[dict]:
    """
    Get HITL decision for a checkpoint.
    Called after container resumes to check approval status.
    """
```

---

## Product App Integration

### Webhook Flow

```
[Modal Phase] → create_hitl_request() → [Supabase hitl_requests]
                                              ↓
                                    [Supabase Realtime]
                                              ↓
                                    [Product App /approvals]
                                              ↓
                                    [Human Decision]
                                              ↓
                                    [POST /hitl/approve]
                                              ↓
                                    [resume_from_checkpoint.spawn()]
                                              ↓
                                    [Next Phase]
```

### Product App Endpoints

| Product App Route | Purpose | CrewAI Integration |
|-------------------|---------|-------------------|
| `GET /api/approvals` | List pending approvals | Queries `hitl_requests` table |
| `PATCH /api/approvals/[id]` | Submit decision | Calls `POST /hitl/approve` |
| `/approvals` UI | Approvals dashboard | Subscribes to Realtime |

### Supabase Realtime Subscription

Product app subscribes to `hitl_requests` table changes:

```typescript
supabase
  .channel('hitl_requests')
  .on('postgres_changes', {
    event: 'INSERT',
    schema: 'public',
    table: 'hitl_requests',
    filter: `status=eq.pending`
  }, (payload) => {
    // Show new approval in UI
  })
  .subscribe()
```

---

## Container Lifecycle at HITL

Per ADR-002 (Modal serverless architecture):

```
[Phase N runs] → [HITL checkpoint reached]
                        ↓
              create_hitl_request()
                        ↓
              [Container terminates] ← $0 cost during wait
                        ↓
              [Human reviews in Product App]
                        ↓
              [POST /hitl/approve]
                        ↓
              resume_from_checkpoint.spawn()
                        ↓
              [New container starts Phase N+1]
```

**Key benefit**: $0 cost during human review (vs always-on containers).

---

## Gaps / TODOs

- [ ] Phase 1 docstring mentions `approve_experiment_plan`, `approve_pricing_test` but only `approve_vpc_completion` is implemented
- [ ] Phase 4 docstring lists `approve_viability_gate`, `approve_pivot`, `approve_proceed` but only `request_human_decision` is implemented
- [ ] No retry/timeout mechanism for expired HITL requests
- [ ] Product app webhook authentication should use HMAC signature (currently bearer token)

---

## Related Documents

- [flow-inventory.md](./flow-inventory.md) - Flow-level HITL triggers
- [crew-agent-task-matrix.md](./crew-agent-task-matrix.md) - Agent task outputs
- [api-entrypoints.md](./api-entrypoints.md) - Full API contract documentation
- [state-persistence.md](./state-persistence.md) - Supabase persistence details
- [integration-contracts.md](./integration-contracts.md) - Product app integration
