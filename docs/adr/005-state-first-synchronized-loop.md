# ADR-005: State-First Synchronized Loop (DB-First Onboarding State Machine)

**Status**: Accepted (Amended)
**Date**: 2026-01-16
**Amended**: 2026-01-16 (Architecture Reality Check)
**Decision Makers**: Chris Walker, Claude AI Assistant
**Context**: Onboarding durability, concurrency, and serverless reliability
**Supersedes**: Extends [ADR-004: Two-Pass Onboarding Architecture](./004-two-pass-onboarding-architecture.md)

## Summary

Adopt a database-first onboarding state machine where **Postgres RPC is the atomic commit point**, with split chat vs. structured state, idempotency and versioning, and frontend hydration with realtime subscriptions.

This moves us from "works in dogfooding" to **pragmatic durability** for regular messages and **guaranteed durability** for Stage 7 completion.

## Amendment: Architecture Reality Check (2026-01-16)

### Original vs. Feasible Architecture

The original ADR proposed Modal as the streaming master for Phase 0 chat. Implementation revealed this is **technically infeasible**:

| Constraint | Impact |
|------------|--------|
| Modal 150-second HTTP timeout | Phase 0 conversations can last 10-15 minutes |
| Netlify 30-second function timeout | `onFinish` can be killed after response returns |
| Serverless isolation | No shared state between requests |

**Resolution**: Next.js handles interactive streaming; Modal handles post-completion validation only.

### Revised Durability Model

| Message Type | Durability Level | Mechanism | Acceptable Risk |
|--------------|------------------|-----------|-----------------|
| Regular chat (Stages 1-6) | Client-coordinated | Split /stream + /save, localStorage fallback | Tab close mid-save loses 1 message |
| Stage advancement | Client-coordinated | localStorage fallback | Retry recovers on next mount |
| **Stage 7 completion** | **Server-side** | **Queue + background processor** | **Zero data loss** |

**Rationale**: Losing 1 message mid-conversation is recoverable (user re-types). Losing the Stage 7 summary + CrewAI kickoff is NOT recoverable (hours of work lost). The hybrid approach concentrates guarantees where they matter most.

---

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
┌─────────────────────────────────────────────────────────────────────────────┐
│                   STATE-FIRST SYNCHRONIZED LOOP (AMENDED)                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  LAYER 1: INTERACTIVE STREAMING (Next.js/Netlify)                           │
│  ════════════════════════════════════════════════                           │
│                                                                              │
│  User Message                                                                │
│       │                                                                      │
│       ▼                                                                      │
│  /api/chat/stream (stateless)                                               │
│    - Auth + session validation                                               │
│    - Stream AI response (Groq via OpenRouter)                                │
│    - NO persistence, NO onFinish callback                                    │
│       │                                                                      │
│       ▼ (stream complete)                                                    │
│  Frontend (Optimistic UI)                                                    │
│    - Shows message immediately                                               │
│    - Saves partial progress to localStorage (recovery cache)                 │
│    - Calls /api/chat/save                                                    │
│       │                                                                      │
│       ▼                                                                      │
│  /api/chat/save (atomic)                                                     │
│    - Pass 2: Quality assessment (Stages 1-6 only)                            │
│    - Call RPC: apply_onboarding_turn                                         │
│    - Returns { version, stageAdvanced, progress }                            │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │              PostgreSQL RPC: apply_onboarding_turn                   │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │ 1. SELECT ... FOR UPDATE (serialize writers)                 │   │    │
│  │  │ 2. Check expected_version (reject out-of-order)              │   │    │
│  │  │ 3. Check message_id idempotency                              │   │    │
│  │  │ 4. Append chat_turn to conversation_history                  │   │    │
│  │  │ 5. Deep-merge patch into stage_data                          │   │    │
│  │  │ 6. Compute progress from field coverage                      │   │    │
│  │  │ 7. Increment version                                         │   │    │
│  │  │ 8. COMMIT (atomic)                                           │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│       │                                                                      │
│       ▼                                                                      │
│  Frontend confirms: "Saved ✓ v12"                                           │
│  localStorage cleared (no longer needed)                                     │
│                                                                              │
│  ════════════════════════════════════════════════════════════════════════   │
│                                                                              │
│  LAYER 2: STAGE 7 COMPLETION (Queue + Background Processor)                 │
│  ═══════════════════════════════════════════════════════════                │
│                                                                              │
│  /api/chat/save detects Stage 7 complete                                    │
│       │                                                                      │
│       ▼                                                                      │
│  complete_onboarding_with_kickoff RPC (ATOMIC)                              │
│    - Mark session completed                                                  │
│    - Insert into pending_completions queue                                   │
│    - Single transaction (rollback if either fails)                           │
│       │                                                                      │
│       ▼                                                                      │
│  Background Processor (Edge Function, pg_cron)                              │
│    - Claim work item (FOR UPDATE SKIP LOCKED)                               │
│    - Run quality assessment                                                  │
│    - Create project                                                          │
│    - Call Modal kickoff                                                      │
│    - Update queue with workflow_id                                           │
│    - Retry with backoff (max 10 → dead_letter)                              │
│                                                                              │
│  ════════════════════════════════════════════════════════════════════════   │
│                                                                              │
│  LAYER 3: POST-COMPLETION VALIDATION (Modal)                                │
│  ═══════════════════════════════════════════                                │
│                                                                              │
│  Modal OnboardingCrew                                                        │
│    - Validates Founder's Brief                                               │
│    - Creates HITL checkpoint for approval                                    │
│    - Runs async (not blocking chat)                                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Five Pillars (Amended)

#### Pillar A: Split Stream/Save Endpoints (Amended from Modal)

**Original**: Modal Two-Pass Orchestrator
**Amended**: Next.js Split Endpoints (Modal 150s limit makes streaming infeasible)

For each user message:

1. **`/api/chat/stream`**: Generate assistant response (streaming, stateless)
2. **`/api/chat/save`**: Extract structured JSON patch + persist to RPC
3. **Mandatory Persistence**: Save MUST complete before showing "Saved ✓"

**Critical Rule**: Even if extraction fails, the chat message MUST still be saved. The RPC accepts `patch = null` gracefully.

```typescript
// Next.js /api/chat/save handler
export async function POST(request: NextRequest) {
  const { sessionId, messageId, userMessage, assistantMessage, expectedVersion } = await request.json();

  // Pass 2: Extract structured data (may fail)
  let patch = null;
  try {
    const assessment = await assessConversationQuality(stage, history, existingBrief);
    patch = assessment?.extractedData || null;
  } catch (error) {
    console.warn('[save] Extraction failed, saving chat only');
  }

  // MANDATORY: Call RPC (blocks until committed)
  const chatTurn = {
    message_id: messageId,
    role: 'user',
    content: userMessage,
    timestamp: new Date().toISOString(),
  };
  const assistantTurn = {
    message_id: `${messageId}-assistant`,
    role: 'assistant',
    content: assistantMessage,
    timestamp: new Date().toISOString(),
  };

  const { data: result } = await supabase.rpc('apply_onboarding_turn', {
    p_session_id: sessionId,
    p_message_id: messageId,
    p_chat_turns: [chatTurn, assistantTurn],
    p_patch: patch,
    p_expected_version: expectedVersion,  // Out-of-order defense
  });

  return NextResponse.json(result);
}
```

#### Pillar B: PostgreSQL RPC as Atomic Commit Point (With expected_version)

Move "fetch → merge → compute → save" into a single PostgreSQL function with transactional guarantees.

**Why This Is Decisive**:

| Guarantee | Mechanism |
|-----------|-----------|
| No clobbering | `SELECT ... FOR UPDATE` serializes writers |
| No duplicates | `message_id` idempotency check |
| No partial saves | Single transaction commits atomically |
| Auditability | `version` is monotonic, enables "Saved v12" UX |
| **Out-of-order defense** | **`expected_version` rejects stale writes** |

```sql
CREATE OR REPLACE FUNCTION apply_onboarding_turn(
    p_session_id VARCHAR(255),
    p_message_id UUID,
    p_chat_turns JSONB,
    p_patch JSONB DEFAULT NULL,
    p_expected_version INT DEFAULT NULL  -- Out-of-order defense
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_session RECORD;
    v_new_history JSONB;
    v_new_state JSONB;
    v_new_version INT;
    v_progress INT;
    v_new_stage INT;
BEGIN
    -- 1. Lock row for update (serializes concurrent writers)
    SELECT * INTO v_session
    FROM onboarding_sessions
    WHERE session_id = p_session_id
      AND user_id = auth.uid()  -- RLS-safe
    FOR UPDATE;

    IF NOT FOUND THEN
        RETURN jsonb_build_object('status', 'not_found');
    END IF;

    -- 2. Out-of-order defense: reject stale writes
    IF p_expected_version IS NOT NULL AND v_session.version != p_expected_version THEN
        RETURN jsonb_build_object(
            'status', 'version_conflict',
            'current_version', v_session.version,
            'expected_version', p_expected_version
        );
    END IF;

    -- 3. Idempotency: check if message_id already exists
    IF v_session.conversation_history @> jsonb_build_array(
        jsonb_build_object('message_id', p_message_id)
    ) THEN
        -- Already processed, return current state (no-op)
        RETURN jsonb_build_object(
            'status', 'duplicate',
            'version', v_session.version,
            'current_stage', v_session.current_stage
        );
    END IF;

    -- 4. Append chat turns to history
    v_new_history := v_session.conversation_history || p_chat_turns;

    -- 5. Deep-merge patch into stage_data (if provided)
    IF p_patch IS NOT NULL THEN
        v_new_state := jsonb_deep_merge(
            COALESCE(v_session.stage_data, '{}'::jsonb),
            jsonb_build_object('brief', p_patch)
        );
    ELSE
        v_new_state := v_session.stage_data;
    END IF;

    -- 6. Compute progress from field coverage (deterministic)
    v_progress := compute_stage_progress(v_session.current_stage, v_new_state);

    -- 7. Check stage advancement (binary gate: required fields present)
    v_new_stage := v_session.current_stage;
    IF stage_requirements_met(v_session.current_stage, v_new_state) THEN
        v_new_stage := LEAST(v_session.current_stage + 1, 7);
    END IF;

    -- 8. Increment version and update
    v_new_version := COALESCE(v_session.version, 0) + 1;

    UPDATE onboarding_sessions
    SET conversation_history = v_new_history,
        stage_data = v_new_state,
        current_stage = v_new_stage,
        version = v_new_version,
        overall_progress = v_progress,
        message_count = COALESCE(message_count, 0) + jsonb_array_length(p_chat_turns),
        last_activity = NOW()
    WHERE session_id = p_session_id;

    -- 9. Return result for frontend
    RETURN jsonb_build_object(
        'status', 'committed',
        'version', v_new_version,
        'current_stage', v_new_stage,
        'stage_advanced', v_new_stage > v_session.current_stage,
        'progress', v_progress
    );
END;
$$;
```

#### Pillar C: Split Chat History from Structured State

Separate concerns to prevent cross-contamination:

| Column | Purpose | Properties |
|--------|---------|------------|
| `conversation_history` | Durable record of conversation turns | Append-only, includes `message_id` |
| `stage_data.brief` | Structured business data per stage | Deep-merged from extraction patches |

**Benefits**:
- Extraction failures don't corrupt conversation integrity
- Prompts can reference `conversation_history` without parsing business state
- Queries against `stage_data` are clean and typed

#### Pillar D: Deterministic Progress + Binary Gate

Replace fuzzy LLM-assessed thresholds with **field-coverage requirements**.

**Stage Advancement Rule**: Stage N advances to N+1 if and only if ALL required fields for stage N are non-null/non-empty in `stage_data.brief`.

```sql
-- Deterministic stage requirements (no LLM opinion)
CREATE OR REPLACE FUNCTION stage_requirements_met(
    p_stage INT,
    p_state JSONB
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_brief JSONB;
BEGIN
    v_brief := COALESCE(p_state->'brief', '{}'::jsonb);

    CASE p_stage
        WHEN 1 THEN
            RETURN v_brief->>'business_concept' IS NOT NULL
               AND v_brief->>'inspiration' IS NOT NULL;
        WHEN 2 THEN
            RETURN jsonb_array_length(COALESCE(v_brief->'target_customers', '[]')) >= 1
               AND jsonb_array_length(COALESCE(v_brief->'customer_segments', '[]')) >= 1;
        WHEN 3 THEN
            RETURN v_brief->>'problem_description' IS NOT NULL
               AND v_brief->>'pain_level' IS NOT NULL;
        WHEN 4 THEN
            RETURN v_brief->>'solution_description' IS NOT NULL
               AND v_brief->>'unique_value_prop' IS NOT NULL;
        WHEN 5 THEN
            RETURN jsonb_array_length(COALESCE(v_brief->'competitors', '[]')) >= 1;
        WHEN 6 THEN
            RETURN v_brief->>'budget_range' IS NOT NULL;
        WHEN 7 THEN
            RETURN jsonb_array_length(COALESCE(v_brief->'short_term_goals', '[]')) >= 1
               AND jsonb_array_length(COALESCE(v_brief->'success_metrics', '[]')) >= 1;
        ELSE
            RETURN FALSE;
    END CASE;
END;
$$;
```

**Progress Calculation**: Derived from field coverage, stored for query convenience but only updated inside RPC.

#### Pillar E: Frontend Hydration + Realtime + localStorage Reconciliation (Amended)

The frontend is a **view** of database state, with localStorage as a **recovery cache**.

**Reconciliation Rules**:

| Scenario | Resolution |
|----------|------------|
| Mount with no localStorage | Hydrate from DB |
| Mount with localStorage pending saves | Attempt recovery, then hydrate from DB |
| localStorage version < DB version | Discard localStorage, DB wins |
| localStorage version = DB version | localStorage is stale cache, discard |
| Realtime UPDATE received | Update UI, clear related localStorage |
| Save succeeds | Clear localStorage for that message |
| Save fails | Keep in localStorage for retry |

**On Mount**:
```typescript
// 1. Check for pending saves in localStorage
const pending = getPendingSaves(sessionId);
if (pending.length > 0) {
  await recoverPendingSaves(pending);  // Attempt to save to DB
}

// 2. Hydrate from DB (source of truth)
const { data: session } = await supabase
  .from('onboarding_sessions')
  .select('*')
  .eq('session_id', sessionId)
  .single();

setMessages(session.conversation_history);
setStageData(session.stage_data);
setCurrentStage(session.current_stage);
setVersion(session.version);

// 3. Clear any localStorage that's now stale
clearStalePendingSaves(sessionId, session.version);
```

**Realtime Subscription**:
```typescript
// Subscribe to updates for this session
const subscription = supabase
  .channel(`session:${sessionId}`)
  .on('postgres_changes', {
    event: 'UPDATE',
    schema: 'public',
    table: 'onboarding_sessions',
    filter: `session_id=eq.${sessionId}`
  }, (payload) => {
    // Backend committed - update UI
    setMessages(payload.new.conversation_history);
    setStageData(payload.new.stage_data);
    setCurrentStage(payload.new.current_stage);
    setVersion(payload.new.version);
    showSaveConfirmation(`Saved v${payload.new.version}`);

    // Clear localStorage - DB is now authoritative
    clearPendingSaves(sessionId);
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

---

## Data Model

### Primary Table: `onboarding_sessions` (Existing, with version column)

```sql
-- Add version column to existing table
ALTER TABLE onboarding_sessions
ADD COLUMN IF NOT EXISTS version INT NOT NULL DEFAULT 0;

-- Existing columns used:
-- session_id VARCHAR(255) PRIMARY KEY
-- user_id UUID NOT NULL
-- conversation_history JSONB DEFAULT '[]'
-- stage_data JSONB DEFAULT '{}'
-- current_stage INT DEFAULT 1
-- overall_progress INT DEFAULT 0
-- status VARCHAR(50) DEFAULT 'active'
-- message_count INT DEFAULT 0
-- last_activity TIMESTAMPTZ
-- created_at TIMESTAMPTZ
```

### Queue Table: `pending_completions` (Stage 7 Durability)

```sql
CREATE TABLE pending_completions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) NOT NULL UNIQUE,  -- Prevents duplicate kickoffs
    user_id UUID NOT NULL,
    conversation_history JSONB NOT NULL,
    stage_data JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',  -- pending, processing, completed, dead_letter
    attempts INT DEFAULT 0,
    last_attempt TIMESTAMPTZ,
    workflow_id VARCHAR(255),  -- Populated on successful kickoff
    project_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error_message TEXT,

    CONSTRAINT fk_session FOREIGN KEY (session_id)
        REFERENCES onboarding_sessions(session_id) ON DELETE CASCADE
);

-- Safe claiming for parallel workers
CREATE INDEX idx_pending_completions_status ON pending_completions(status, created_at);
```

### Atomic Completion RPC (Stage 7)

```sql
CREATE OR REPLACE FUNCTION complete_onboarding_with_kickoff(
    p_session_id VARCHAR(255),
    p_user_id UUID
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    v_session RECORD;
BEGIN
    -- Lock and fetch session
    SELECT * INTO v_session
    FROM onboarding_sessions
    WHERE session_id = p_session_id
    FOR UPDATE;

    IF v_session IS NULL THEN
        RETURN jsonb_build_object('status', 'not_found');
    END IF;

    IF v_session.status = 'completed' THEN
        -- Already completed - but ensure queue row exists (recovery case)
        IF NOT EXISTS (SELECT 1 FROM pending_completions WHERE session_id = p_session_id) THEN
            -- Missing queue row - re-insert for recovery
            INSERT INTO pending_completions (session_id, user_id, conversation_history, stage_data)
            VALUES (p_session_id, p_user_id, v_session.conversation_history, v_session.stage_data);
            RETURN jsonb_build_object('status', 'requeued');
        END IF;
        RETURN jsonb_build_object('status', 'already_completed');
    END IF;

    -- ATOMIC: Mark complete AND insert queue row in same transaction
    UPDATE onboarding_sessions
    SET status = 'completed',
        completed_at = NOW(),
        last_activity = NOW()
    WHERE session_id = p_session_id;

    INSERT INTO pending_completions (session_id, user_id, conversation_history, stage_data)
    VALUES (p_session_id, p_user_id, v_session.conversation_history, v_session.stage_data)
    ON CONFLICT (session_id) DO NOTHING;  -- Idempotent

    RETURN jsonb_build_object('status', 'queued');
END;
$$;
```

---

## Operational Guarantees

With RPC + split state + idempotency + versioning + expected_version:

| Failure Mode | Prevention Mechanism |
|--------------|---------------------|
| Partial saves (Stages 1-6) | Split /stream + /save; localStorage recovery |
| Partial saves (Stage 7) | Queue + background processor with retry |
| Data loss on refresh | Frontend hydrates from DB |
| Stage lock | Binary gate on field coverage |
| 0% progress | Progress derived from persisted fields |
| Concurrent clobbering | `FOR UPDATE` serializes writers |
| Duplicate messages | `message_id` idempotency check |
| **Out-of-order updates** | **`expected_version` rejects stale writes** |
| Tab close mid-stream | localStorage saves partial progress |
| Tab close before save | localStorage recovery on next mount |
| **Worker crashes mid-processing** | **Lease timeout: items stuck > 5 min are reclaimed** |
| **Missing queue row (completed session)** | **Recovery: RPC re-inserts missing queue row** |

### Accepted Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Tab close mid-stream (Stages 1-6) | 1 message lost | User re-types; partial progress in localStorage |
| Tab close before save starts | 1 message lost | localStorage recovery on next mount |
| Network failure | Save delayed | Retry 3x with backoff; localStorage fallback |

---

## Implementation Sequence

### PR 1: Schema + RPC
- Add `version` column to `onboarding_sessions`
- Create `jsonb_deep_merge` helper function
- Create `apply_onboarding_turn` RPC with row lock + idempotency + expected_version
- Create `stage_requirements_met` and `compute_stage_progress` functions

### PR 2: Stream Endpoint
- Create `/api/chat/stream` (stateless, no persistence)
- Extract streaming logic from current `/api/chat/route.ts`
- Remove `onFinish` callback entirely

### PR 3: Save Endpoint
- Create `/api/chat/save` (calls RPC)
- Run quality assessment (Pass 2) for Stages 1-6
- Call `apply_onboarding_turn` RPC
- Handle version conflicts (refetch + retry)

### PR 4: Frontend Integration
- Update `handleSubmit` to call `/stream` then `/save`
- Add "Saved ✓ v{X}" indicator
- Add retry logic with exponential backoff
- Add localStorage fallback for pending saves
- Implement reconciliation rules

### PR 5: Recovery Logic
- Check localStorage for pending saves on mount
- Attempt recovery before DB hydration
- Clear stale localStorage after successful recovery/hydration

### PR 6: Stage 7 Queue
- Create `pending_completions` table
- Create `complete_onboarding_with_kickoff` atomic RPC
- Create background processor (Edge Function or pg_cron)
- Implement safe claiming with `FOR UPDATE SKIP LOCKED`
- Retry with exponential backoff (max 10 → dead_letter)

### PR 7: Cleanup
- Deprecate old `/api/chat/route.ts`
- Update tests
- Add E2E tests for save flow, version conflicts, Stage 7 queue

---

## Verification

### Automated
```bash
# RPC function tests
supabase test db

# Frontend hydration tests
pnpm test -- --testPathPattern="onboarding"

# E2E: concurrent submission test
pnpm test:e2e -- concurrent-onboarding
```

### Manual
1. Start onboarding, refresh mid-conversation → chat history preserved
2. Open two tabs, submit simultaneously → version conflict detected, both messages eventually saved
3. Kill browser mid-message → next visit recovers from localStorage or shows last DB state
4. Complete stage requirements → stage advances automatically
5. Check "Saved v{X}" updates after each message
6. Complete Stage 7 → verify queued and processed by background worker

---

## Rollback Plan

If critical issues arise:

1. Revert to monolithic `/api/chat/route.ts` with `onFinish`
2. Frontend reads from `onboarding_sessions` (still populated)
3. Two-Pass Architecture (ADR-004) resumes with known limitations

---

## References

- [ADR-004: Two-Pass Onboarding Architecture](./004-two-pass-onboarding-architecture.md)
- [Implementation Plan](/home/chris/.claude/plans/shiny-growing-sprout.md)
- [Supabase Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)
- [PostgreSQL FOR UPDATE](https://www.postgresql.org/docs/current/sql-select.html#SQL-FOR-UPDATE-SHARE)
- [Supabase Realtime](https://supabase.com/docs/guides/realtime)

---

## Changelog

| Date | Change |
|------|--------|
| 2026-01-16 | Initial ADR proposed |
| 2026-01-16 | **AMENDED**: Architecture Reality Check - Modal 150s limit makes streaming infeasible; adopted Next.js split /stream + /save; added expected_version for out-of-order defense; kept onboarding_sessions (no migration to validation_runs); added localStorage reconciliation rules; clarified pragmatic vs guaranteed durability |
| 2026-01-18 | **AMENDMENT: Pillar D Implementation Reality** |
|            | - SQL-based `stage_requirements_met()` and `compute_stage_progress()` functions were **not implemented** |
|            | - Actual implementation uses TypeScript `shouldAdvanceStage()` in `quality-assessment.ts` |
|            | - **Topic-based advancement**: Stage advances when 75%+ of topics discussed (not field presence) |
|            | - This approach is more flexible for conversational UX but diverges from the deterministic SQL gate described in Pillar D |
|            | - Related: [precious-kindling-balloon.md](/home/chris/.claude/plans/precious-kindling-balloon.md) TDD implementation |
| 2026-01-18 | **AMENDMENT: SummaryModal Approve/Revise Split Completion Flow** |
|            | - Problem: `complete_onboarding_with_kickoff()` inserted queue row immediately on Stage 7 completion |
|            | - This broke the Revise flow - pg_cron processed queue regardless of user choice |
|            | - Solution: Split completion into two discrete RPCs |
|            | - `queue_onboarding_for_kickoff()` - Called when user clicks "Approve" in SummaryModal |
|            | - `reset_session_for_revision()` - Called when user clicks "Revise", cancels pending queue, resets session |
|            | - `/api/chat/save` no longer auto-queues; returns `queued: false` |
|            | - New endpoints: `/api/onboarding/queue`, `/api/onboarding/revise` |
|            | - Migration: `20260118000001_split_completion_flow.sql` |
|            | See [Plan: prancy-tickling-quokka.md](/home/chris/.claude/plans/prancy-tickling-quokka.md) for implementation details |
