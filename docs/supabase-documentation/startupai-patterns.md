# StartupAI Supabase Patterns

Supabase patterns specific to the StartupAI ecosystem, including state persistence, HITL workflows, and Realtime integration.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  StartupAI Three-Layer Architecture                             │
├─────────────────────────────────────────────────────────────────┤
│  INTERACTION LAYER (Netlify/Product App)                        │
│  • User triggers validation                                     │
│  • Receives real-time progress updates (Supabase Realtime)      │
│  • Handles HITL approvals                                       │
├─────────────────────────────────────────────────────────────────┤
│  ORCHESTRATION LAYER (Supabase)                                │
│  • State persistence (PostgreSQL)                               │
│  • Real-time updates (WebSocket)                                │
│  • Approval queue management                                    │
│  • User authentication                                          │
├─────────────────────────────────────────────────────────────────┤
│  COMPUTE LAYER (Modal)                                          │
│  • 5 Flow functions (one per phase)                             │
│  • Ephemeral containers (pay-per-second)                        │
│  • Checkpoint-and-resume at HITL points                         │
└─────────────────────────────────────────────────────────────────┘
```

## Core Tables

### validation_runs

Primary table tracking validation workflow state.

```sql
CREATE TABLE validation_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

  -- Status tracking
  status TEXT NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending', 'running', 'awaiting_approval', 'completed', 'failed', 'cancelled')),

  -- Phase tracking
  current_phase INTEGER DEFAULT 0,
  phase_state JSONB DEFAULT '{}',
  progress_percent INTEGER DEFAULT 0,

  -- Results
  final_decision TEXT,
  final_report JSONB,
  error_message TEXT,

  -- Timestamps
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE validation_runs ENABLE ROW LEVEL SECURITY;

-- Indexes
CREATE INDEX idx_validation_runs_project ON validation_runs(project_id);
CREATE INDEX idx_validation_runs_status ON validation_runs(status);
CREATE INDEX idx_validation_runs_created ON validation_runs(created_at DESC);

-- Enable Realtime
ALTER PUBLICATION supabase_realtime ADD TABLE validation_runs;
```

### hitl_requests

Human-in-the-loop approval queue.

```sql
CREATE TABLE hitl_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id UUID NOT NULL REFERENCES validation_runs(id) ON DELETE CASCADE,

  -- Checkpoint info
  checkpoint_name TEXT NOT NULL,
  phase INTEGER NOT NULL,

  -- Context for human review
  context JSONB NOT NULL DEFAULT '{}',
  summary TEXT,

  -- Decision tracking
  status TEXT NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending', 'approved', 'rejected', 'timeout')),
  decision TEXT,
  decision_notes TEXT,
  decided_by UUID REFERENCES auth.users(id),
  decided_at TIMESTAMPTZ,

  -- Expiration
  expires_at TIMESTAMPTZ,

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE hitl_requests ENABLE ROW LEVEL SECURITY;

-- Indexes
CREATE INDEX idx_hitl_run_id ON hitl_requests(run_id);
CREATE INDEX idx_hitl_status ON hitl_requests(status);
CREATE INDEX idx_hitl_pending ON hitl_requests(created_at) WHERE status = 'pending';

-- Enable Realtime
ALTER PUBLICATION supabase_realtime ADD TABLE hitl_requests;
```

### projects

User projects that validation runs belong to.

```sql
CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  name TEXT NOT NULL,
  description TEXT,
  entrepreneur_input TEXT,  -- Original input for validation

  -- Metadata
  status TEXT DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

-- Owner access only
CREATE POLICY "Users manage own projects"
ON projects FOR ALL
TO authenticated
USING (owner_id = auth.uid())
WITH CHECK (owner_id = auth.uid());
```

## RLS Policies

### validation_runs Policies

```sql
-- Users can view their own validation runs
CREATE POLICY "View own validation runs"
ON validation_runs FOR SELECT
TO authenticated
USING (
  project_id IN (
    SELECT id FROM projects WHERE owner_id = auth.uid()
  )
);

-- Only system can insert/update (via service role)
-- Users trigger via API, not direct insert
```

### hitl_requests Policies

```sql
-- Users can view HITL requests for their projects
CREATE POLICY "View own HITL requests"
ON hitl_requests FOR SELECT
TO authenticated
USING (
  run_id IN (
    SELECT vr.id FROM validation_runs vr
    JOIN projects p ON vr.project_id = p.id
    WHERE p.owner_id = auth.uid()
  )
);

-- Users can approve/reject their own HITL requests
CREATE POLICY "Decide own HITL requests"
ON hitl_requests FOR UPDATE
TO authenticated
USING (
  run_id IN (
    SELECT vr.id FROM validation_runs vr
    JOIN projects p ON vr.project_id = p.id
    WHERE p.owner_id = auth.uid()
  )
)
WITH CHECK (
  -- Can only update decision-related columns
  status IN ('approved', 'rejected')
);
```

## State Persistence Pattern

Modal functions checkpoint state to Supabase before HITL pauses.

### Save State (Modal → Supabase)

```python
# src/state/persistence.py

async def save_checkpoint(
    run_id: str,
    checkpoint_name: str,
    phase: int,
    phase_state: dict,
    context: dict
):
    """Save state before HITL pause."""

    # Update validation run
    supabase.table("validation_runs").update({
        "status": "awaiting_approval",
        "current_phase": phase,
        "phase_state": phase_state,
        "updated_at": datetime.now().isoformat()
    }).eq("id", run_id).execute()

    # Create HITL request
    supabase.table("hitl_requests").insert({
        "run_id": run_id,
        "checkpoint_name": checkpoint_name,
        "phase": phase,
        "context": context,
        "status": "pending",
        "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
    }).execute()
```

### Resume State (Supabase → Modal)

```python
async def load_checkpoint(run_id: str) -> dict:
    """Load state after HITL approval."""

    result = supabase.table("validation_runs").select(
        "id, current_phase, phase_state"
    ).eq("id", run_id).single().execute()

    return result.data
```

## Realtime Integration

### Frontend Subscription

```typescript
// Product app: Subscribe to validation progress

const subscribeToValidation = (runId: string) => {
  return supabase
    .channel(`validation-${runId}`)
    .on(
      'postgres_changes',
      {
        event: 'UPDATE',
        schema: 'public',
        table: 'validation_runs',
        filter: `id=eq.${runId}`
      },
      (payload) => {
        const { status, current_phase, progress_percent } = payload.new

        // Update UI
        setStatus(status)
        setPhase(current_phase)
        setProgress(progress_percent)

        // Handle HITL
        if (status === 'awaiting_approval') {
          showApprovalDialog(runId)
        }

        // Handle completion
        if (status === 'completed') {
          showResults(payload.new.final_report)
        }
      }
    )
    .subscribe()
}
```

### HITL Notifications

```typescript
// Subscribe to HITL requests for current user

const subscribeToHITL = (userId: string) => {
  return supabase
    .channel('hitl-notifications')
    .on(
      'postgres_changes',
      {
        event: 'INSERT',
        schema: 'public',
        table: 'hitl_requests',
        filter: `status=eq.pending`
      },
      async (payload) => {
        // Verify this is for user's project
        const { run_id } = payload.new
        const { data } = await supabase
          .from('validation_runs')
          .select('project:projects(owner_id)')
          .eq('id', run_id)
          .single()

        if (data?.project?.owner_id === userId) {
          showNotification('Approval required', payload.new.summary)
        }
      }
    )
    .subscribe()
}
```

## HITL Approval Flow

### Approve Request (Frontend)

```typescript
async function approveHITL(hitlId: string, decision: 'approved' | 'rejected', notes?: string) {
  // Update HITL request
  const { error } = await supabase
    .from('hitl_requests')
    .update({
      status: decision,
      decision: decision,
      decision_notes: notes,
      decided_by: userId,
      decided_at: new Date().toISOString()
    })
    .eq('id', hitlId)

  if (error) throw error

  // Trigger Modal resume via API
  await fetch('/api/crewai/resume', {
    method: 'POST',
    body: JSON.stringify({ hitl_id: hitlId, decision })
  })
}
```

### Resume Validation (API Route)

```typescript
// Product app: POST /api/crewai/resume

export async function POST(req: Request) {
  const { hitl_id, decision } = await req.json()

  // Get HITL request details
  const { data: hitl } = await supabase
    .from('hitl_requests')
    .select('run_id, checkpoint_name')
    .eq('id', hitl_id)
    .single()

  // Call Modal to resume
  const response = await fetch(
    `${MODAL_URL}/hitl/approve`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        run_id: hitl.run_id,
        checkpoint: hitl.checkpoint_name,
        decision
      })
    }
  )

  return response.json()
}
```

## Progress Tracking

### Update Progress (Modal)

```python
async def update_progress(run_id: str, phase: int, percent: int, message: str = None):
    """Update progress for Realtime subscribers."""

    update_data = {
        "current_phase": phase,
        "progress_percent": percent,
        "updated_at": datetime.now().isoformat()
    }

    if message:
        update_data["phase_state"] = supabase.table("validation_runs").select(
            "phase_state"
        ).eq("id", run_id).single().execute().data["phase_state"]
        update_data["phase_state"]["message"] = message

    supabase.table("validation_runs").update(update_data).eq("id", run_id).execute()
```

## Supabase Project Details

**Project ID**: `eqxropalhxjeyvfcoyxg`
**Region**: us-east-1
**Dashboard**: https://supabase.com/dashboard/project/eqxropalhxjeyvfcoyxg

### Connection Info

```
# Direct connection
Host: db.eqxropalhxjeyvfcoyxg.supabase.co
Port: 5432
Database: postgres
User: postgres

# API URL
https://eqxropalhxjeyvfcoyxg.supabase.co

# Realtime URL
wss://eqxropalhxjeyvfcoyxg.supabase.co/realtime/v1
```

## External Resources

- [StartupAI Modal Patterns](../modal-documentation/startupai-patterns.md)
- [ADR-002: Modal Migration](../adr/002-modal-serverless-migration.md)
- [Master Architecture](../master-architecture/)
