---
document_type: feature-audit
status: active
last_verified: 2026-01-13
---

# State Persistence

## Purpose
Document the Supabase persistence layer that enables checkpoint/resume patterns and real-time UI updates.

## Quick Reference

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `validation_runs` | Run state and orchestration | `id`, `phase_state`, `current_phase`, `status` |
| `validation_progress` | Progress events (append-only) | `run_id`, `phase`, `crew`, `status` |
| `hitl_requests` | HITL approval queue | `run_id`, `checkpoint_name`, `status`, `decision` |

---

## Architecture

### Three-Table Pattern

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         validation_runs                                   │
│  Master run state - single row per run                                   │
│  • Orchestration control                                                 │
│  • Full state checkpoint (phase_state JSONB)                            │
│  • HITL coordination                                                     │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
        ┌───────────▼───────────┐       ┌──────────▼──────────┐
        │  validation_progress  │       │   hitl_requests     │
        │  Append-only events   │       │   Approval queue    │
        │  Real-time UI         │       │   Decision tracking │
        └───────────────────────┘       └─────────────────────┘
```

### Checkpoint/Resume Flow

```
[Phase N starts] → update_progress() → [Task executes]
                                           │
                                    [HITL needed?]
                                      │         │
                                     No        Yes
                                      │         │
                              [Continue]    checkpoint_state()
                                           create_hitl_request()
                                           [Container terminates]
                                                  │
                                           [$0 during wait]
                                                  │
                                           [Human approves]
                                                  │
                                           resume_state()
                                           [New container]
                                                  │
                                           [Continue from checkpoint]
```

---

## Tables

### validation_runs

**Purpose**: Master state for each validation run

**Schema**:

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | uuid | No | gen_random_uuid() | Primary key |
| `project_id` | uuid | No | - | FK to projects |
| `user_id` | uuid | No | - | FK to users |
| `status` | text | No | 'pending' | pending, running, paused, completed, failed |
| `current_phase` | int | No | 0 | Current phase (0-4) |
| `phase_state` | jsonb | Yes | {} | Full ValidationRunState serialized |
| `hitl_state` | text | Yes | null | Current HITL checkpoint name |
| `hitl_checkpoint_at` | timestamp | Yes | null | When HITL checkpoint created |
| `started_at` | timestamp | Yes | now() | Run start time |
| `updated_at` | timestamp | Yes | now() | Last update time |
| `completed_at` | timestamp | Yes | null | Run completion time |
| `error_message` | text | Yes | null | Error details if failed |

**Indexes**:
- `idx_validation_runs_project_id` on `project_id`
- `idx_validation_runs_user_id` on `user_id`
- `idx_validation_runs_status` on `status`

**Status Transitions**:
```
pending → running → paused → running → completed
                        ↓
                      failed
```

### validation_progress

**Purpose**: Append-only progress events for real-time UI

**Schema**:

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | uuid | No | gen_random_uuid() | Primary key |
| `run_id` | uuid | No | - | FK to validation_runs |
| `phase` | int | No | - | Phase number (0-4) |
| `crew` | text | No | - | Crew name |
| `task` | text | Yes | null | Task name |
| `agent` | text | Yes | null | Agent name |
| `status` | text | No | 'started' | started, in_progress, completed, failed, skipped |
| `progress_pct` | int | Yes | null | Progress percentage (0-100) |
| `output` | jsonb | Yes | null | Task output |
| `error_message` | text | Yes | null | Error details |
| `duration_ms` | int | Yes | null | Execution time in ms |
| `created_at` | timestamp | No | now() | Event timestamp |

**Indexes**:
- `idx_validation_progress_run_id` on `run_id`
- `idx_validation_progress_created_at` on `created_at`

**Usage Pattern**: Insert-only, ordered by `created_at` for timeline display.

### hitl_requests

**Purpose**: HITL approval queue and decision tracking

**Schema**:

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | uuid | No | gen_random_uuid() | Primary key |
| `run_id` | uuid | No | - | FK to validation_runs |
| `checkpoint_name` | text | No | - | Checkpoint identifier |
| `phase` | int | No | - | Phase number (0-4) |
| `title` | text | No | - | Human-readable title |
| `description` | text | No | - | Decision context |
| `context` | jsonb | Yes | {} | Phase-specific data |
| `options` | jsonb | Yes | [] | Array of decision options |
| `recommended_option` | text | Yes | null | Default recommendation |
| `status` | text | No | 'pending' | pending, approved, rejected, expired |
| `decision` | text | Yes | null | Selected decision value |
| `feedback` | text | Yes | null | Human feedback |
| `decision_at` | timestamp | Yes | null | Decision timestamp |
| `decision_by` | uuid | Yes | null | User who decided |
| `created_at` | timestamp | No | now() | Request created |
| `updated_at` | timestamp | Yes | now() | Last updated |

**Indexes**:
- `idx_hitl_requests_run_id` on `run_id`
- `idx_hitl_requests_status` on `status`
- `idx_hitl_requests_checkpoint` on `checkpoint_name`

**Status Values**:
- `pending`: Awaiting human decision
- `approved`: Decision made (includes segment_*, override_proceed)
- `rejected`: Decision was reject/rejected
- `expired`: Request expired after 7 days or superseded

---

## Persistence Functions

### checkpoint_state()

**File**: `src/state/persistence.py:41-98`

**Purpose**: Save full state to Supabase before container termination

```python
def checkpoint_state(
    run_id: str,
    state: ValidationRunState,
    hitl_checkpoint: Optional[str] = None,
) -> bool:
```

**Behavior**:
- Serializes `ValidationRunState` to JSONB
- Updates `phase_state`, `current_phase`, `updated_at`
- If `hitl_checkpoint` provided: sets `hitl_state`, `status = 'paused'`
- Otherwise: sets `status = 'running'`

### resume_state()

**File**: `src/state/persistence.py:101-156`

**Purpose**: Restore state when container resumes after HITL

```python
def resume_state(run_id: str) -> Optional[ValidationRunState]:
```

**Behavior**:
- Fetches `validation_runs` row by `run_id`
- Deserializes `phase_state` JSONB back to `ValidationRunState`
- Returns `None` if not found

### update_progress()

**File**: `src/state/persistence.py:163-219`

**Purpose**: Append progress event for real-time UI

```python
def update_progress(
    run_id: str,
    phase: int,
    crew: str,
    task: Optional[str] = None,
    agent: Optional[str] = None,
    status: str = "started",
    progress_pct: Optional[int] = None,
    output: Optional[dict] = None,
    error_message: Optional[str] = None,
    duration_ms: Optional[int] = None,
) -> bool:
```

**Behavior**:
- Inserts new row into `validation_progress`
- Triggers Supabase Realtime for subscribers
- Never updates existing rows (append-only)

### create_hitl_request()

**File**: `src/state/persistence.py:226-290`

**Purpose**: Create HITL approval request in queue

```python
def create_hitl_request(
    run_id: str,
    checkpoint: HITLCheckpoint,
) -> Optional[str]:
```

**Behavior**:
1. Expires any existing pending HITL for same checkpoint (Bug #9 fix)
2. Inserts new `hitl_requests` row with checkpoint details
3. Returns HITL request ID

### get_hitl_decision()

**File**: `src/state/persistence.py:293-319`

**Purpose**: Check HITL decision status

```python
def get_hitl_decision(run_id: str, checkpoint_name: str) -> Optional[dict]:
```

**Behavior**:
- Queries `hitl_requests` for matching run_id + checkpoint_name
- Returns decision details if found

---

## State Models

### ValidationRunState

**File**: `src/state/models.py:575-629`

**Purpose**: Complete state for checkpoint/resume

```python
class ValidationRunState(BaseModel):
    # Identity
    run_id: UUID
    project_id: UUID
    user_id: UUID
    session_id: Optional[UUID] = None

    # Execution state
    current_phase: int = 0
    status: str = "pending"
    hitl_state: Optional[str] = None

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
    final_decision: Optional[str] = None
    decision_rationale: Optional[str] = None

    # Timestamps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Error tracking
    error_message: Optional[str] = None
    retry_count: int = 0
```

### HITLCheckpoint

**File**: `src/state/models.py:527-547`

**Purpose**: HITL checkpoint details

```python
class HITLCheckpoint(BaseModel):
    checkpoint_name: str
    phase: int
    title: str
    description: str
    context: dict[str, Any] = Field(default_factory=dict)
    options: Optional[list[dict[str, str]]] = None
    recommended_option: Optional[str] = None
    decision: Optional[str] = None
    feedback: Optional[str] = None
    decided_by: Optional[UUID] = None
    decided_at: Optional[datetime] = None
```

---

## Supabase Realtime

### Progress Subscription

Product app subscribes to progress events:

```typescript
const channel = supabase
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
      // Update UI with new progress event
      addProgressEvent(payload.new);
    }
  )
  .subscribe();
```

### HITL Subscription

Product app subscribes to HITL requests:

```typescript
const channel = supabase
  .channel('hitl_requests')
  .on(
    'postgres_changes',
    {
      event: 'INSERT',
      schema: 'public',
      table: 'hitl_requests',
      filter: `user_id=eq.${userId}`,
    },
    (payload) => {
      // Show approval notification
      showApprovalNotification(payload.new);
    }
  )
  .subscribe();
```

---

## RLS Policies

### validation_runs

```sql
-- Users can read their own runs
CREATE POLICY "Users can read own runs" ON validation_runs
  FOR SELECT USING (auth.uid() = user_id);

-- Service role can manage all runs
CREATE POLICY "Service can manage runs" ON validation_runs
  FOR ALL USING (auth.role() = 'service_role');
```

### validation_progress

```sql
-- Users can read progress for their runs
CREATE POLICY "Users can read own progress" ON validation_progress
  FOR SELECT USING (
    run_id IN (SELECT id FROM validation_runs WHERE user_id = auth.uid())
  );

-- Service role can insert progress
CREATE POLICY "Service can insert progress" ON validation_progress
  FOR INSERT WITH CHECK (auth.role() = 'service_role');
```

### hitl_requests

```sql
-- Users can read/update their own HITL requests
CREATE POLICY "Users can read own HITL" ON hitl_requests
  FOR SELECT USING (
    run_id IN (SELECT id FROM validation_runs WHERE user_id = auth.uid())
  );

CREATE POLICY "Users can update own HITL" ON hitl_requests
  FOR UPDATE USING (
    run_id IN (SELECT id FROM validation_runs WHERE user_id = auth.uid())
  );

-- Service role can manage all HITL
CREATE POLICY "Service can manage HITL" ON hitl_requests
  FOR ALL USING (auth.role() = 'service_role');
```

---

## Migration Files

**Location**: `db/migrations/`

| Migration | Purpose |
|-----------|---------|
| `001_validation_runs.sql` | Create validation_runs table |
| `002_validation_progress.sql` | Create validation_progress table |
| `003_hitl_requests.sql` | Create hitl_requests table |
| `004_indexes.sql` | Add performance indexes |
| `005_rls_policies.sql` | Row Level Security |

---

## Cost Optimization

### $0 During HITL

The checkpoint/resume pattern ensures containers terminate during human review:

```
[Container running: $0.001/s]
         │
    checkpoint_state()
    create_hitl_request()
         │
    [Container terminates]
         │
    [Human reviews: $0.00]  ← Could be hours/days
         │
    [POST /hitl/approve]
         │
    resume_state()
    [New container: $0.001/s]
```

### Progress Append-Only

Insert-only pattern for `validation_progress`:
- No update contention
- Simple query pattern
- Efficient Realtime broadcasting

---

## Gaps / TODOs

- [ ] Add data retention policy (archive old runs after 90 days)
- [ ] Add soft delete support for GDPR compliance
- [ ] Consider partitioning `validation_progress` by date
- [ ] Add read replica for status queries

---

## Related Documents

- [api-entrypoints.md](./api-entrypoints.md) - API that uses persistence
- [hitl-checkpoint-map.md](./hitl-checkpoint-map.md) - HITL checkpoint details
- [integration-contracts.md](./integration-contracts.md) - Product app integration
- [../adr/002-modal-serverless-migration.md](../adr/002-modal-serverless-migration.md) - Architecture decision
