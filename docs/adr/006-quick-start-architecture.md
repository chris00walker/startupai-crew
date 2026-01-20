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
Phase 1 begins immediately
    ↓
AI researches and generates Founder's Brief
    ↓
HITL: approve_discovery_output (Brief + VPC)
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
- Pitch deck: Optional, max 10MB PDF
- Notes: Optional, max 10,000 characters

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

### 4. Combine HITL Checkpoints

**Before:** Two separate checkpoints
- `approve_founders_brief` (Phase 0)
- `approve_vpc_completion` (Phase 1)

**After:** One combined checkpoint
- `approve_discovery_output` (Phase 1)

User reviews all discovery outputs together:
1. AI-generated Founder's Brief (editable)
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
  "additional_context": "Optional notes or pitch deck text",
  "client_id": "uuid (optional - for consultant flow)"
}
```

**Response:**
```json
{
  "project_id": "uuid",
  "validation_run_id": "uuid",
  "status": "phase_1_started",
  "redirect_url": "/projects/{project_id}"
}
```

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
