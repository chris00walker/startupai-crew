# ADR-006: Quick Start Architecture (Phase 0 Simplification)

**Status**: Accepted
**Date**: 2026-01-19
**Decision Makers**: Chris Walker, Claude AI Assistant
**Context**: Phase 0 onboarding failures due to AI in critical path
**Supersedes**: [ADR-004](./004-two-pass-onboarding-architecture.md) (Two-Pass Onboarding) - partially superseded for Phase 0

## Summary

Replace the 7-stage AI conversation in Phase 0 with a **Quick Start** form that captures only the business idea (1-3 sentences). The Founder's Brief becomes an **output of Phase 1** (generated from AI research) rather than an **input collected during onboarding**.

This eliminates AI from the Phase 0 critical path, achieving:
- **30 seconds** onboarding (was 30+ minutes)
- **$0 AI cost** for Phase 0 (was $17+)
- **100% deterministic** behavior (was 57-92% variance)
- **~2000 lines of code deleted** from frontend

## Context

### The Problem

Phase 0 (Onboarding) used a 7-stage AI conversation to collect the Founder's Brief:

```
Stage 1: Problem Statement
Stage 2: Target Customer
Stage 3: Solution Approach
Stage 4: Market Context
Stage 5: Competition
Stage 6: Validation Approach
Stage 7: Summary & Confirmation
```

Each stage used AI to:
1. Generate contextual questions
2. Assess response quality
3. Extract structured data
4. Decide when to advance

This architecture had fundamental problems:

| Problem | Evidence | Impact |
|---------|----------|--------|
| **Non-determinism** | Same transcript → 57-92% progress variance | Tests unreliable |
| **High cost** | $17+ per test run ($1.47 even with "free" models) | Unsustainable testing |
| **Test flakiness** | E2E tests passed/failed randomly | CI/CD blocked |
| **Slow onboarding** | 30+ minutes per user | High abandonment risk |
| **Redundant data** | User guesses market size → Phase 1 researches it anyway | Wasted effort |

### Root Cause Analysis

The root cause was identified through systematic debugging:

> **We put AI in the critical path for something that doesn't require AI.**

The 7-stage conversation collected information that Phase 1 would research anyway:
- Market size and trends → Phase 1 researches this
- Competitor landscape → Phase 1 researches this
- Customer segments → Phase 1 researches this

Users were guessing answers that AI could find more accurately through research.

### Failed Mitigation Attempts

Before this architectural pivot, we attempted several fixes:

1. **Two-Pass Architecture (ADR-004)**: Separated LLM conversation from backend assessment. Improved determinism but didn't address the fundamental issue of AI in critical path.

2. **Scoring Rubrics**: Added explicit 0-5 scales for quality assessment. Helped slightly but LLMs still exhibited variance.

3. **Model Switching**: Tried GPT-4.1-nano, GPT-4-turbo, Claude. All showed similar variance patterns.

4. **Prompt Engineering**: Extensive prompt iteration. Marginal improvements, never reached acceptable determinism.

The conclusion: **The architecture itself was flawed, not the implementation.**

## Decision

### 1. Replace Phase 0 with Quick Start

**Before (7-Stage Conversation):**
```
User signs up
    ↓
Alex AI conducts 7-stage interview (30+ min)
    ↓
AI extracts Founder's Brief from transcript
    ↓
HITL: approve_founders_brief
    ↓
Phase 1 begins
```

**After (Quick Start):**
```
User signs up
    ↓
User enters business idea (30 seconds)
    ↓
Phase 1 Stage A: BriefGenerationCrew runs
    ↓
HITL: approve_brief (user can edit)
    ↓
Phase 1 Stage B: VPC crews run with edited brief
    ↓
HITL: approve_discovery_output (Brief + VPC review)
    ↓
Phase 2 begins
```

### 2. Quick Start UI Specification

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                    What's your business idea?                               │
│                                                                              │
│   Describe your startup idea in a few sentences. Tell us what you're        │
│   building and who it's for.                                                │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                      │   │
│   │ Example: "A meal planning app that helps busy parents reduce food   │   │
│   │ waste and save time on weekly meal decisions."                      │   │
│   │                                                                      │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ Have a pitch deck or notes? (optional)                              │   │
│   │                                                                      │   │
│   │ [ Upload PDF ]  [ Paste text ]                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│                       [ Start Validation → ]                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Validation Rules:**
- Business idea: Required, min 10 characters
- Structured hints: Optional (industry, target_user, geography) - see Risk 1 mitigation
- Notes: Optional, max 10,000 characters (V1: text only, file upload deferred to V2)

> **Note**: The UI wireframe above shows the minimal version. The recommended version with structured hints is documented in [Risk 1 Mitigation](#risk-1-thin-input-produces-low-fidelity-briefs).

### 3. Move Brief Generation to Phase 1

Phase 1 gains a new crew: `BriefGenerationCrew`

```
Phase 1: VPC Discovery
│
├── BriefGenerationCrew (NEW)
│   ├── GV1: Concept Validator (moved from Phase 0)
│   └── S1: Brief Compiler (moved from Phase 0)
│
├── DiscoveryCrew
├── CustomerProfileCrew
├── ValueDesignCrew
├── WTPCrew
└── FitAssessmentCrew
```

The Brief is now generated from:
1. User's `raw_idea` (Quick Start input)
2. Market research (AI-conducted)
3. Competitor analysis (AI-conducted)
4. Customer discovery (AI-conducted)

### 4. Restructure HITL Checkpoints

**Before:** Two separate checkpoints in different phases
- `approve_founders_brief` (Phase 0) - after 7-stage conversation
- `approve_vpc_completion` (Phase 1) - after VPC generation

**After:** Two checkpoints within Phase 1
- `approve_brief` (Phase 1, Stage A) - after BriefGenerationCrew, brief is editable
- `approve_discovery_output` (Phase 1, Stage B) - after VPC generation, final review

**Sequencing:**
```
Phase 1 Stage A: BriefGenerationCrew
    ↓
HITL: approve_brief (edit brief here)
    ↓
Phase 1 Stage B: DiscoveryCrew, CustomerProfileCrew, ValueDesignCrew, etc.
    ↓
HITL: approve_discovery_output (review Brief + VPC)
    ↓
Phase 2
```

**What user reviews at `approve_brief`:**
1. AI-generated Founder's Brief (editable fields)
2. Research citations and provenance

**What user reviews at `approve_discovery_output`:**
1. Final Founder's Brief (with any edits)
2. Customer Profile (VPC left side)
3. Value Map (VPC right side)
4. Key hypotheses to test

### 5. Agent Changes

| Agent | Previous Location | New Location | Rationale |
|-------|-------------------|--------------|-----------|
| O1: Interview Gap Analyzer | Phase 0 OnboardingCrew | **DELETED** | No interview to analyze |
| GV1: Concept Validator | Phase 0 OnboardingCrew | Phase 1 BriefGenerationCrew | Validates researched concept |
| GV2: Intent Verification | Phase 0 OnboardingCrew | **DELETED** | No transcript to verify |
| S1: Brief Compiler | Phase 0 OnboardingCrew | Phase 1 BriefGenerationCrew | Compiles brief from research |

**Net effect:**
- Agents: 45 → 43 (-2)
- Flows: 5 → 4 (-1, OnboardingFlow deleted)
- Crews: 14 (OnboardingCrew dissolved, BriefGenerationCrew added to Phase 1)

### 6. API Changes

**New Endpoint:**
```bash
POST /api/projects/quick-start
Content-Type: application/json

{
  "raw_idea": "A meal planning app that helps busy parents...",
  "hints": {
    "industry": "consumer_tech",
    "target_user": "parents",
    "geography": "north_america"
  },
  "additional_context": "Optional notes (max 10,000 chars)",
  "client_id": "uuid (optional - for consultant flow)",
  "idempotency_key": "hash (optional - prevents duplicate runs)"
}
```

**Response:**
```json
{
  "project_id": "uuid",
  "run_id": "uuid",
  "status": "phase_1_started",
  "redirect_url": "/projects/{project_id}"
}
```

**Response (duplicate detected):**
```json
{
  "project_id": "uuid",
  "run_id": "uuid",
  "status": "already_started",
  "message": "A validation run for this idea was started recently"
}
```

> **Note**: Response uses `run_id` consistently (not `validation_run_id`) to match Modal API conventions.

**Deprecated Endpoints:**
- `POST /interview/start`
- `POST /interview/continue`
- `POST /brief/create`
- `POST /brief/{id}/approve`

## Consequences

### Positive

1. **100% Deterministic**: No AI variance in onboarding path
2. **$0 Phase 0 Cost**: No AI calls until Phase 1
3. **30-Second Onboarding**: Minimal user friction
4. **Better Data Quality**: AI research > user guesses
5. **Simpler Testing**: E2E tests are reliable
6. **Code Deletion**: ~2000 lines of complex frontend code removed
7. **Single Review Point**: User reviews Brief + VPC together

### Negative

1. **Less Upfront Context**: AI starts with minimal user input
2. **ADR-004 Partially Obsolete**: Two-Pass Architecture no longer needed for Phase 0
3. **Migration Work**: Existing onboarding code must be removed/refactored

### Neutral

1. **Brief Quality**: May differ from user-provided (could be better or worse)
2. **User Perception**: Some users may prefer guided conversation (can add back as optional)

## Risks and Mitigations

### Risk 1: Thin Input Produces Low-Fidelity Briefs

**Problem**: If `raw_idea` is vague (e.g., "AI startup"), Phase 1 may generate confident but off-target output. The BriefGenerationCrew has no context to disambiguate.

**Mitigation**: Add optional structured hints without breaking the 30-second flow.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  What's your business idea? *                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ A meal planning app that helps busy parents...                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  Help us understand your market (optional but recommended)                  │
│                                                                              │
│  Industry:        [ Consumer Tech      ▼]                                   │
│  Target user:     [ Parents            ▼]                                   │
│  Geography:       [ North America      ▼]                                   │
│                                                                              │
│                       [ Start Validation → ]                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

**API Extension**:
```json
{
  "raw_idea": "A meal planning app...",
  "hints": {
    "industry": "consumer_tech",
    "target_user": "parents",
    "geography": "north_america"
  }
}
```

These hints are passed to BriefGenerationCrew to constrain research scope. If omitted, the crew infers from `raw_idea`.

### Risk 2: Duplicate Phase 1 Runs (No Idempotency)

**Problem**: Immediate Phase 1 kickoff wastes compute on:
- Double-clicks or flaky network retries
- Low-quality submissions that should be filtered
- Spam/abuse without rate limiting

**Mitigation**: Add idempotency and rate limiting to `/api/projects/quick-start`.

These are **two separate mechanisms** with different purposes:

| Mechanism | Purpose | Window | Key |
|-----------|---------|--------|-----|
| **Idempotency** | Prevent accidental duplicates (double-click, retry) | 5 minutes | Client-provided or auto-generated |
| **Rate Limiting** | Prevent abuse (spam, compute waste) | 1 hour | User ID |

**Idempotency** (client-provided key preferred):
```typescript
// Client can provide explicit idempotency key
const idempotencyKey = req.body.idempotency_key
  ?? hash(`${userId}:${normalizeText(rawIdea)}:${Date.now()}`);

// Check for existing run with same key (any time - keys are unique)
const existingRun = await db.query.validationRuns.findFirst({
  where: eq(validationRuns.idempotencyKey, idempotencyKey)
});

if (existingRun) {
  return { project_id: existingRun.projectId, run_id: existingRun.id, status: 'already_started' };
}
```

> **Design choice**: Client-provided keys are permanent (no time window). Auto-generated keys include timestamp, so retries after page refresh create new runs. This matches Stripe's idempotency semantics.

**Rate Limiting** (separate check):
```typescript
// Count runs in last hour for this user
const recentRunCount = await db.query.validationRuns.count({
  where: and(
    eq(validationRuns.userId, userId),
    gt(validationRuns.createdAt, oneHourAgo)
  )
});

const limit = getUserRateLimit(user.plan); // trial: 3, paid: 10, consultant: 20
if (recentRunCount >= limit) {
  return res.status(429).json({ error: 'RATE_LIMITED', retry_after: secondsUntilWindowResets });
}
```

**Rate Limits by Plan**:
| User Type | Limit | Window |
|-----------|-------|--------|
| Trial | 3 runs | 1 hour |
| Paid | 10 runs | 1 hour |
| Consultant | 20 runs | 1 hour |

### Risk 3: Combined HITL Review Feels Heavy

**Problem**: `approve_discovery_output` combines Brief + VPC review. If the brief is wrong, user must reject everything and wait for full Phase 1 re-run. Users may want to correct the brief before reviewing VPC outputs.

**Mitigation**: Split Phase 1 into two stages with brief editing between them.

**Phase 1 Internal Sequencing**:
```
Quick Start Form submitted
    ↓
Phase 1 Stage A: BriefGenerationCrew runs
    ↓
HITL Checkpoint: approve_brief (user can edit)
    ↓
Phase 1 Stage B: VPC crews run with edited brief
    ↓
HITL Checkpoint: approve_discovery_output (Brief + VPC review)
    ↓
Phase 2 begins
```

> **Key insight**: The original flow said "Phase 1 begins immediately" but didn't specify that Phase 1 has **internal stages**. BriefGenerationCrew runs first. The user edits the brief. Then VPC crews run using the edited brief as input. This is NOT a re-run; it's the natural sequencing.

**HITL Checkpoints in Phase 1**:
| Checkpoint | When | User Action |
|------------|------|-------------|
| `approve_brief` | After BriefGenerationCrew | Edit brief fields, then approve |
| `approve_discovery_output` | After VPC crews | Review Brief + VPC together, approve |

**Brief Provenance** (shown at `approve_brief`):
```json
{
  "founders_brief": {
    "the_idea": {
      "value": "A meal planning app for busy parents...",
      "source": "user_input",
      "editable": true
    },
    "problem_hypothesis": {
      "value": "Parents waste 3+ hours/week on meal decisions...",
      "source": "ai_research",
      "editable": true,
      "research_citations": ["source1", "source2"]
    },
    "customer_hypothesis": {
      "value": "Dual-income parents with children under 12...",
      "source": "ai_research",
      "editable": true
    }
  }
}
```

**UI Behavior at `approve_brief`**:
1. User sees Brief with provenance indicators (📝 user input, 🔬 AI research)
2. User can edit any field before approval
3. Edits are tracked: `edited_by: "user"`, `original_value: "..."`
4. On approval, edited brief becomes input to VPC crews
5. VPC crews run with the user-corrected brief

**UI Behavior at `approve_discovery_output`**:
1. User sees final Brief (with any edits applied) + VPC outputs
2. This is a confirmation checkpoint, not an editing checkpoint
3. User approves to proceed to Phase 2, or rejects to pause

This gives users control over the brief before it affects VPC generation, without requiring a re-run.

### Risk 4: Optional Uploads Imply Undocumented Policies

**Problem**: The UI shows "Upload PDF" and "Paste text" but doesn't address:
- Supported file types
- Storage location and encryption
- PII handling (what if they upload customer data?)
- Parsing strategy (OCR? Text extraction?)
- Retention policy (how long is data kept?)

**Mitigation**: V1 scope is **text-only** with clear documentation.

**V1 Scope**:
| Feature | V1 Status | Notes |
|---------|-----------|-------|
| Text paste | ✅ Supported | Max 10,000 characters |
| PDF upload | ❌ Deferred to V2 | Requires parsing pipeline |
| DOCX upload | ❌ Deferred to V2 | Requires parsing pipeline |
| Image upload | ❌ Deferred to V2 | Requires OCR |

**Text Handling (V1)**:
- Stored in `projects.additional_context` (text column)
- No file storage (Supabase Storage not used in V1)
- Passed directly to BriefGenerationCrew as context
- Retained for duration of project lifecycle
- Deleted when project is deleted (cascade)

**V2 File Upload Requirements** (documented for future):
- Storage: Supabase Storage with RLS (`evidence-files` bucket)
- Encryption: At-rest encryption via Supabase
- Parsing: PDF → text extraction, DOCX → text extraction
- PII: Warning banner "Don't include customer PII"
- Retention: 90 days after project completion, then auto-delete
- Compliance: GDPR deletion requests honored within 72 hours

### Risk 5: Migration Needs Clean Sunset Path

**Problem**: Existing `onboarding_sessions` contain 7-stage conversation data. Deprecated `/interview/*` endpoints may still have active callers. Need clean sunset to avoid broken flows.

**Mitigation**: Explicit deprecation timeline with backward compatibility.

**Deprecation Timeline**:
| Date | Action |
|------|--------|
| 2026-01-19 | ADR-006 accepted, Quick Start development begins |
| 2026-01-26 | Quick Start deployed, old endpoints marked `@deprecated` |
| 2026-02-02 | Old endpoints return `410 Gone` with migration message |
| 2026-02-16 | Old endpoints removed from codebase |
| 2026-03-01 | `onboarding_sessions` table archived and dropped |

**Backward Compatibility** (2026-01-26 to 2026-02-02):
```typescript
// Old endpoint returns deprecation notice (422, not 301)
// Note: 301 is for GET redirects; POST endpoints should use 4xx with migration info
app.post('/interview/start', (req, res) => {
  return res.status(422).json({
    error: 'ENDPOINT_DEPRECATED',
    message: 'This endpoint is deprecated. Use POST /api/projects/quick-start instead.',
    migration_guide: 'https://docs.startupai.site/migration/quick-start',
    sunset_date: '2026-02-02',
    new_endpoint: '/api/projects/quick-start'
  });
});
```

> **HTTP semantics**: 301/302 are for GET redirects and many clients won't auto-follow for POST. Use 422 (Unprocessable Entity) during deprecation period with clear migration instructions, then 410 (Gone) after sunset.

**Existing Session Handling**:
- Sessions with `status: 'in_progress'` → Mark as `status: 'legacy_abandoned'`
- Sessions with `status: 'completed'` → Retain for audit (Brief already extracted)
- No automatic migration (users restart with Quick Start)

## Alternatives Considered

### 1. Scoring Rubrics with Explicit Scales

**Approach**: Add 0-5 scoring rubrics for each quality dimension
**Why Rejected**: Helps but doesn't eliminate variance; still AI in critical path

### 2. Simplified Assessment (Binary Pass/Fail)

**Approach**: Reduce quality checks to simple yes/no decisions
**Why Rejected**: Loses nuance; still AI-dependent

### 3. Staged Assessment with Checkpoints

**Approach**: Hard stage boundaries with deterministic transitions
**Why Rejected**: Complexity remains; AI still in critical path

### 4. Hybrid Form + AI

**Approach**: Structured form with optional AI elaboration
**Why Rejected**: More complex than pure Quick Start; AI still optional dependency

### 5. Template-Based Extraction

**Approach**: Predefined templates instead of free-form extraction
**Why Rejected**: Doesn't address the fundamental issue of redundant data collection

### 6. Multi-Model Consensus

**Approach**: Use multiple LLMs and take consensus
**Why Rejected**: Increases cost 3x; doesn't guarantee determinism

### 7. Human Review Gateway

**Approach**: Human reviews AI extraction before proceeding
**Why Rejected**: Adds latency; doesn't reduce AI cost

### 8. Deferred Assessment

**Approach**: Collect all input first, assess once at end
**Why Rejected**: Still requires AI assessment; same variance issues

### 9. Confidence-Weighted Progression

**Approach**: Only advance when AI confidence exceeds threshold
**Why Rejected**: May never reach threshold; user stuck in loop

### 10. Semantic Similarity Matching

**Approach**: Match responses against ideal patterns
**Why Rejected**: Requires maintaining ideal patterns; still fuzzy

### 11. Remove Phase 0 Entirely (CHOSEN)

**Approach**: Single text input, Brief generated by Phase 1
**Why Chosen**: Eliminates root cause; simplest solution; best user experience

## Migration Path

### Phase 1: Documentation Updates ✅ COMPLETE
- [x] Update `04-phase-0-onboarding.md` (rewrite to Quick Start)
- [x] Update `05-phase-1-vpc-discovery.md` (add BriefGenerationCrew)
- [x] Update `02-organization.md` (agent changes)
- [x] Update `reference/approval-workflows.md` (HITL changes)
- [x] Update `reference/api-contracts.md` (API changes)
- [x] Update `09-status.md` (status changes)
- [x] Create ADR-006 (this document)

### Phase 2: Backend Implementation
- [ ] Add `raw_idea` column to `projects` table
- [ ] Create `POST /api/projects/quick-start` endpoint
- [ ] Update Modal kickoff to accept `raw_idea` instead of `brief_id`
- [ ] Implement `BriefGenerationCrew` in Phase 1
- [ ] Update HITL checkpoint to `approve_discovery_output`

### Phase 3: Frontend Implementation
- [ ] Create Quick Start page (`/onboarding/founder`)
- [ ] Delete 7-stage conversation components
- [ ] Delete assessment logic (~400 lines)
- [ ] Delete stage configuration (~200 lines)
- [ ] Delete AI prompts (~420 lines)
- [ ] Update consultant flow to use Quick Start

### Phase 4: Testing & Cleanup
- [ ] E2E test: Quick Start → Phase 1 → HITL → Phase 2
- [ ] Delete deprecated code
- [ ] Archive ADR-004 as partially superseded
- [ ] Verify dogfooding flow works

## Consultant Flow

**Constraint:** Consultants can only add Founders who have already signed up.

```
1. Consultant signs up → redirect to /consultant-dashboard
2. Dashboard shows "Add your first client"
3. Search for client by email (must be existing Founder)
4. Enter business idea on client's behalf
5. System creates project under client's account
6. Consultant linked as advisor_id on project
7. Phase 1 runs for client's project
8. Consultant reviews HITL checkpoints with client
```

This constraint is enforced by the existing `users` table foreign key relationship.

## Success Metrics

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| Onboarding time | 30+ min | 30 sec | <1 min |
| Phase 0 AI cost | $17+ | $0 | $0 |
| Progress variance | 57-92% | 0% | 0% |
| E2E test reliability | ~75% | 100% | 100% |
| Code complexity | 2000+ lines | ~100 lines | <200 lines |

## Related Documents

- [ADR-002: Modal Serverless Migration](./002-modal-serverless-migration.md) - Compute infrastructure
- [ADR-004: Two-Pass Onboarding Architecture](./004-two-pass-onboarding-architecture.md) - Partially superseded
- [04-phase-0-onboarding.md](../docs/master-architecture/04-phase-0-onboarding.md) - Quick Start specification
- [05-phase-1-vpc-discovery.md](../docs/master-architecture/05-phase-1-vpc-discovery.md) - Brief Generation specification

## Changelog

| Date | Change |
|------|--------|
| 2026-01-19 | Initial proposal and acceptance |
| 2026-01-19 | Documentation updates complete |
| 2026-01-20 | Added Risks and Mitigations section (thin input, idempotency, HITL UX, uploads, migration) |
| 2026-01-20 | Fixed: consistent `run_id` key, Phase 1 two-stage sequencing, idempotency vs rate limit separation, HTTP 422 for deprecated POSTs |
