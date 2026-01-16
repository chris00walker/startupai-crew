# ADR-005: State-First Synchronized Loop (DB-First Onboarding State Machine)

**Status**: Proposed
**Date**: 2026-01-16
**Decision Makers**: Chris Walker, Claude AI Assistant
**Context**: Onboarding durability, concurrency, and serverless reliability
**Supersedes**: Extends [ADR-004: Two-Pass Onboarding Architecture](./004-two-pass-onboarding-architecture.md)

## Summary

Adopt a database-first onboarding state machine where **Postgres RPC is the atomic commit point**, with split chat vs. structured state, idempotency and versioning, and frontend hydration with realtime subscriptions.

This moves us from "works in dogfooding" to "impossible to break" under concurrency, refreshes, and serverless execution constraints.

## Context

### The Problem

After implementing Two-Pass Architecture (ADR-004), we fixed the immediate 18% tool call rate issue. However, live dogfooding revealed deeper architectural issues:

| Failure Mode | Root Cause | ADR-004 Status |
|--------------|------------|----------------|
| Data loss on refresh | Volatile frontend state without hydration protocol | Partially addressed (P3) |
| Stage locking | Fuzzy thresholds + LLM-dependent gating | Addressed but fragile |
| 0% progress bugs | Progress derived from LLM assessment, not persisted state | Fixed (P2) but symptoms-only |
| Partial saves | Serverless `onFinish` can be killed after response returns | **Unaddressed** |
| Race conditions | Last-write-wins merge in app layer | **Latent risk** |

**Key Insight**: The Two-Pass Architecture moved assessment from LLM to backend, but kept the state machine in the application layer. This is still vulnerable to:

1. **Serverless "Async Ghost"**: The `onFinish` callback runs after `streamText` returns. In serverless (Netlify Functions), the container can be killed after the response is sent, causing partial saves.

2. **Race Conditions**: Two concurrent requests fetch the same state, both compute merges, last finisher overwrites the first's changes.

3. **Hydration Gap**: Frontend treats conversation as ephemeral UI state, not a view of durable DB state.

### Why Incremental Fixes Won't Work

We've applied 6+ fixes (E1-E4, P2, P3) to ADR-004. Each fixed a symptom but not the root cause:

```
Root Cause: Application-layer state machine with async persistence
     ↓
Symptoms: Invalid Date, progress regression, stage stalls, future: clobbering
     ↓
Fixes: Timestamps, coverage reset, legacy fallback, schema .min(3)
     ↓
Result: Whack-a-mole; new symptoms will emerge
```

The architectural mismatch requires an architectural solution.

## Decision

**Implement State-First Synchronized Loop**: Move the state machine into PostgreSQL with RPC-based atomic commits, split data concerns, and frontend hydration from DB.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         STATE-FIRST SYNCHRONIZED LOOP                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  User Message                                                            │
│       │                                                                  │
│       ▼                                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    Modal Two-Pass Handler                        │    │
│  │  ┌─────────────────┐    ┌─────────────────┐                     │    │
│  │  │ Pass 1: Persona │ →  │ Pass 2: Auditor │                     │    │
│  │  │ (streaming)     │    │ (extraction)    │                     │    │
│  │  └─────────────────┘    └─────────────────┘                     │    │
│  │           │                      │                               │    │
│  │           └──────────┬───────────┘                               │    │
│  │                      ▼                                           │    │
│  │         ┌─────────────────────────┐                              │    │
│  │         │ MANDATORY: Call RPC     │  ← Cannot return until       │    │
│  │         │ (even if extraction     │    RPC commits               │    │
│  │         │  fails)                 │                              │    │
│  │         └─────────────────────────┘                              │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              │                                           │
│                              ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │              PostgreSQL RPC: apply_onboarding_turn               │    │
│  │  ┌──────────────────────────────────────────────────────────┐   │    │
│  │  │ 1. SELECT ... FOR UPDATE (serialize writers)             │   │    │
│  │  │ 2. Check message_id idempotency                          │   │    │
│  │  │ 3. Append chat_turn to chat_history                      │   │    │
│  │  │ 4. Deep-merge patch into phase_state                     │   │    │
│  │  │ 5. Compute progress from field coverage                  │   │    │
│  │  │ 6. Increment version                                     │   │    │
│  │  │ 7. COMMIT (atomic)                                       │   │    │
│  │  └──────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              │                                           │
│                              ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    Frontend (Hydration + Realtime)               │    │
│  │  ┌─────────────────┐    ┌─────────────────┐                     │    │
│  │  │ On Mount:       │    │ Realtime Sub:   │                     │    │
│  │  │ Hydrate from DB │    │ UPDATE events   │                     │    │
│  │  │ (full state)    │    │ → UI refresh    │                     │    │
│  │  └─────────────────┘    └─────────────────┘                     │    │
│  │                              │                                   │    │
│  │                              ▼                                   │    │
│  │                    "Saved ✓ v12"                                 │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Five Pillars

#### Pillar A: Modal Two-Pass Orchestrator (Sequential + Mandatory)

For each user message:

1. **Pass 1 (Persona)**: Generate assistant response (streaming-friendly)
2. **Pass 2 (Auditor)**: Extract structured JSON patch aligned to stage schema
3. **Mandatory Persistence**: Function MUST NOT terminate until RPC commit succeeds

**Critical Rule**: Even if extraction fails, the chat message MUST still be saved. The RPC accepts `patch = null` gracefully.

```python
# Modal handler - MUST await RPC before returning
async def handle_message(run_id: str, user_message: str) -> str:
    message_id = generate_uuid()

    # Pass 1: Generate response
    assistant_response = await generate_persona_response(user_message)

    # Pass 2: Extract structured data (may fail)
    try:
        patch = await extract_structured_patch(user_message, assistant_response)
    except Exception:
        patch = None  # Extraction failed, but chat still saved

    # MANDATORY: Call RPC (blocks until committed)
    chat_turn = {
        "message_id": message_id,
        "user": user_message,
        "assistant": assistant_response,
        "timestamp": datetime.utcnow().isoformat()
    }

    result = await supabase.rpc("apply_onboarding_turn", {
        "p_run_id": run_id,
        "p_message_id": message_id,
        "p_chat_turn": chat_turn,
        "p_patch": patch
    })

    return assistant_response  # Only return AFTER commit
```

#### Pillar B: PostgreSQL RPC as Atomic Commit Point

Move "fetch → merge → compute → save" into a single PostgreSQL function with transactional guarantees.

**Why This Is Decisive**:

| Guarantee | Mechanism |
|-----------|-----------|
| No clobbering | `SELECT ... FOR UPDATE` serializes writers |
| No duplicates | `message_id` idempotency check |
| No partial saves | Single transaction commits atomically |
| Auditability | `version` is monotonic, enables "Saved v12" UX |
| Out-of-order defense | Slower completions can't revert state |

```sql
CREATE OR REPLACE FUNCTION apply_onboarding_turn(
    p_run_id UUID,
    p_message_id UUID,
    p_chat_turn JSONB,
    p_patch JSONB DEFAULT NULL
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_run RECORD;
    v_new_history JSONB;
    v_new_state JSONB;
    v_new_version INT;
    v_progress INT;
    v_new_stage INT;
BEGIN
    -- 1. Lock row for update (serializes concurrent writers)
    SELECT * INTO v_run
    FROM validation_runs
    WHERE id = p_run_id
      AND user_id = auth.uid()  -- RLS-safe
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Run not found or unauthorized';
    END IF;

    -- 2. Idempotency: check if message_id already exists
    IF v_run.chat_history @> jsonb_build_array(jsonb_build_object('message_id', p_message_id)) THEN
        -- Already processed, return current state (no-op)
        RETURN jsonb_build_object(
            'status', 'duplicate',
            'version', v_run.version,
            'current_stage', v_run.current_stage
        );
    END IF;

    -- 3. Append chat turn to history
    v_new_history := v_run.chat_history || jsonb_build_array(p_chat_turn);

    -- 4. Deep-merge patch into phase_state (if provided)
    IF p_patch IS NOT NULL THEN
        v_new_state := jsonb_deep_merge(v_run.phase_state, p_patch);
    ELSE
        v_new_state := v_run.phase_state;
    END IF;

    -- 5. Compute progress from field coverage (deterministic)
    v_progress := compute_stage_progress(v_run.current_stage, v_new_state);

    -- 6. Check stage advancement (binary gate: all required fields present)
    v_new_stage := v_run.current_stage;
    IF stage_requirements_met(v_run.current_stage, v_new_state) THEN
        v_new_stage := LEAST(v_run.current_stage + 1, 7);
    END IF;

    -- 7. Increment version and update
    v_new_version := v_run.version + 1;

    UPDATE validation_runs
    SET chat_history = v_new_history,
        phase_state = v_new_state,
        current_stage = v_new_stage,
        version = v_new_version,
        overall_progress = v_progress,
        updated_at = NOW()
    WHERE id = p_run_id;

    -- 8. Return result for frontend
    RETURN jsonb_build_object(
        'status', 'committed',
        'version', v_new_version,
        'current_stage', v_new_stage,
        'progress', v_progress
    );
END;
$$;
```

#### Pillar C: Split Chat History from Structured State

Separate concerns to prevent cross-contamination:

| Column | Purpose | Properties |
|--------|---------|------------|
| `chat_history` | Durable record of conversation turns | Append-only, includes `message_id` |
| `phase_state` | Structured business data per stage | Deep-merged from extraction patches |

**Benefits**:
- Extraction failures don't corrupt conversation integrity
- Prompts can reference `chat_history` without parsing business state
- Queries against `phase_state` are clean and typed

```typescript
// phase_state structure (typed per stage)
interface PhaseState {
  stage1?: {
    business_concept?: string;
    inspiration?: string;
  };
  stage2?: {
    target_segment?: string;
    customer_pain_points?: string[];
  };
  // ... stages 3-7
}
```

#### Pillar D: Deterministic Progress + Binary Gate

Replace fuzzy LLM-assessed thresholds with **field-coverage requirements**.

**Stage Advancement Rule**: Stage N advances to N+1 if and only if ALL required fields for stage N are non-null/non-empty in `phase_state`.

```sql
-- Deterministic stage requirements (no LLM opinion)
CREATE OR REPLACE FUNCTION stage_requirements_met(
    p_stage INT,
    p_state JSONB
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    CASE p_stage
        WHEN 1 THEN
            RETURN p_state->'stage1'->>'business_concept' IS NOT NULL
               AND p_state->'stage1'->>'inspiration' IS NOT NULL;
        WHEN 2 THEN
            RETURN p_state->'stage2'->>'target_segment' IS NOT NULL
               AND jsonb_array_length(COALESCE(p_state->'stage2'->'customer_pain_points', '[]')) >= 2;
        -- ... stages 3-7
        WHEN 7 THEN
            RETURN jsonb_array_length(COALESCE(p_state->'stage7'->'key_insights', '[]')) >= 3
               AND jsonb_array_length(COALESCE(p_state->'stage7'->'next_steps', '[]')) >= 3;
        ELSE
            RETURN FALSE;
    END CASE;
END;
$$;
```

**Progress Calculation**: Derived from field coverage, not stored (to avoid drift).

```sql
-- Progress = (filled required fields / total required fields) per stage
CREATE OR REPLACE FUNCTION compute_stage_progress(
    p_stage INT,
    p_state JSONB
)
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    v_base INT;
    v_stage_progress FLOAT;
BEGIN
    -- Base progress from completed stages (0-85%)
    v_base := ((p_stage - 1) * 100) / 7;

    -- Stage progress from field coverage (0-14% within stage)
    v_stage_progress := calculate_field_coverage(p_stage, p_state) * (100.0 / 7);

    RETURN LEAST(95, v_base + v_stage_progress::INT);
END;
$$;
```

#### Pillar E: Frontend Hydration + Realtime

The frontend is a **view** of database state, not the source of truth.

**On Mount**:
```typescript
// Hydrate from DB (not localStorage, not URL params)
const { data: run } = await supabase
  .from('validation_runs')
  .select('*')
  .eq('id', runId)
  .single();

setMessages(run.chat_history);
setPhaseState(run.phase_state);
setCurrentStage(run.current_stage);
setVersion(run.version);
```

**Realtime Subscription**:
```typescript
// Subscribe to updates for this run
const subscription = supabase
  .channel(`run:${runId}`)
  .on('postgres_changes', {
    event: 'UPDATE',
    schema: 'public',
    table: 'validation_runs',
    filter: `id=eq.${runId}`
  }, (payload) => {
    // Backend committed - update UI
    setMessages(payload.new.chat_history);
    setPhaseState(payload.new.phase_state);
    setCurrentStage(payload.new.current_stage);
    setVersion(payload.new.version);
    showSaveConfirmation(`Saved v${payload.new.version}`);
  })
  .subscribe();
```

**Save Confirmation UX**:
```
┌─────────────────────────────────────────┐
│ Stage 2: Customer Discovery             │
│                                         │
│ [conversation...]                       │
│                                         │
│ ─────────────────────────────────────── │
│                          Saved ✓ v12    │
└─────────────────────────────────────────┘
```

## Data Model

### Primary Table: `validation_runs`

```sql
CREATE TABLE validation_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    project_id UUID REFERENCES projects(id),

    -- Split state (Pillar C)
    chat_history JSONB NOT NULL DEFAULT '[]'::jsonb,
    phase_state JSONB NOT NULL DEFAULT '{}'::jsonb,

    -- Progression
    current_stage INT NOT NULL DEFAULT 1,
    overall_progress INT NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'active',

    -- Versioning (Pillar B)
    version INT NOT NULL DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_validation_runs_user ON validation_runs(user_id);
CREATE INDEX idx_validation_runs_status ON validation_runs(status);

-- RLS
ALTER TABLE validation_runs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own runs"
    ON validation_runs FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update own runs"
    ON validation_runs FOR UPDATE
    USING (auth.uid() = user_id);
```

### Migration from `onboarding_sessions`

```sql
-- Migrate existing data
INSERT INTO validation_runs (
    id, user_id, project_id,
    chat_history, phase_state,
    current_stage, overall_progress, status,
    version, created_at, updated_at
)
SELECT
    session_id,
    user_id,
    project_id,
    COALESCE(conversation_history, '[]'::jsonb),
    COALESCE(stage_data->'brief', '{}'::jsonb),
    current_stage,
    overall_progress,
    status,
    1,  -- Start versioning
    created_at,
    last_activity
FROM onboarding_sessions;
```

## Operational Guarantees

With RPC + split state + idempotency + versioning:

| Failure Mode | Prevention Mechanism |
|--------------|---------------------|
| Partial saves | Modal blocks until RPC COMMIT |
| Data loss on refresh | Frontend hydrates from DB |
| Stage lock | Binary gate on field coverage |
| 0% progress | Progress derived from persisted fields |
| Concurrent clobbering | `FOR UPDATE` serializes writers |
| Duplicate messages | `message_id` idempotency check |
| Out-of-order updates | `version` is monotonic |

## Answers to Open Questions

### Q1: Should progress be stored or derived?

**Recommendation: Derive, with optional cache.**

- Primary: Always derive progress from `phase_state` field coverage
- Cache: Store `overall_progress` in table for query convenience, but ONLY update it inside the RPC
- This prevents drift between stored and computed values

### Q2: Do we need `validation_progress` event log immediately?

**Recommendation: Start with `validation_runs` subscription, add event log later.**

- Phase 1: Subscribe to `validation_runs` UPDATE events (sufficient for MVP)
- Phase 2: Add `validation_events` append-only log for richer analytics/debugging
- The event log adds complexity; validate core architecture first

### Q3: Should auto-advance be server-driven or UI-driven?

**Recommendation: Server-driven in RPC.**

- Stage advancement happens atomically with state update (inside RPC)
- UI receives new stage via realtime subscription
- Prevents race where UI thinks it advanced but DB disagrees
- Binary gate logic lives in one place (PostgreSQL), not duplicated in UI

## Consequences

### Positive

1. **Impossible to partially save** - RPC is atomic, Modal blocks until commit
2. **Impossible to lose data on refresh** - Frontend always hydrates from DB
3. **Impossible to clobber under concurrency** - Row-level locking serializes
4. **Impossible to duplicate messages** - `message_id` idempotency
5. **Deterministic progress** - No LLM opinion, just field coverage
6. **Auditable state** - `version` enables "Saved v12" UX and debugging
7. **Clean separation** - Chat history vs. business state don't contaminate each other

### Negative

1. **Migration complexity** - Must migrate `onboarding_sessions` → `validation_runs`
2. **PostgreSQL function maintenance** - RPC logic lives in SQL, not TypeScript
3. **Realtime dependency** - Requires Supabase Realtime to be reliable
4. **Testing complexity** - Must test RPC functions separately

### Mitigations

| Risk | Mitigation |
|------|------------|
| Migration | Backfill script with validation; keep old table as backup |
| SQL maintenance | Keep RPC simple; complex logic in helper functions |
| Realtime failure | Fallback polling on subscription error |
| Testing | Supabase local for RPC tests; Jest for frontend hydration |

## Implementation Sequence

### PR 1: Schema + Migration
- Add `validation_runs` table with `chat_history`, `phase_state`, `version`
- Create `jsonb_deep_merge` helper function
- Migration script from `onboarding_sessions`

### PR 2: Core RPC
- Implement `apply_onboarding_turn` with row lock + idempotency
- Implement `stage_requirements_met` and `compute_stage_progress`
- Unit tests for RPC functions

### PR 3: Modal Handler Update
- Update Modal to call RPC instead of direct Supabase updates
- Ensure handler blocks until RPC commit
- Handle extraction failures gracefully (chat still saved)

### PR 4: Frontend Hydration + Realtime
- Hydrate from `validation_runs` on mount
- Subscribe to realtime updates filtered by `id=eq.runId`
- Show "Saved v{version}" confirmation
- Remove localStorage/URL state dependencies

### PR 5: Cleanup + Deprecation
- Deprecate `onboarding_sessions` table
- Remove Two-Pass `onFinish` callback logic
- Update documentation

## Verification

### Automated
```bash
# RPC function tests
supabase test db

# Frontend hydration tests
pnpm test -- --testPathPattern="validation-runs"

# E2E: concurrent submission test
pnpm test:e2e -- concurrent-onboarding
```

### Manual
1. Start onboarding, refresh mid-conversation → chat history preserved
2. Open two tabs, submit simultaneously → no clobbering, both messages saved
3. Kill browser mid-message → next visit shows last saved state
4. Complete stage requirements → stage advances automatically
5. Check "Saved v{X}" updates in realtime

## Rollback Plan

If critical issues arise:

1. Revert Modal handler to direct Supabase updates
2. Frontend reads from `onboarding_sessions` (still populated)
3. Two-Pass Architecture (ADR-004) resumes with known limitations

## References

- [ADR-004: Two-Pass Onboarding Architecture](./004-two-pass-onboarding-architecture.md)
- [Supabase Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)
- [PostgreSQL FOR UPDATE](https://www.postgresql.org/docs/current/sql-select.html#SQL-FOR-UPDATE-SHARE)
- [Supabase Realtime](https://supabase.com/docs/guides/realtime)

## Changelog

| Date | Change |
|------|--------|
| 2026-01-16 | Initial ADR proposed |
