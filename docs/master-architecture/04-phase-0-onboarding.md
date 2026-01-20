---
purpose: Phase 0 specification - Quick Start (simplified onboarding)
status: active
last_reviewed: 2026-01-19
vpd_compliance: true
architectural_pivot: 2026-01-19
---

# Phase 0: Quick Start

> **Architectural Pivot (2026-01-19)**: This document reflects a fundamental simplification of the onboarding process. The previous 7-stage conversational interview has been replaced with a Quick Start flow. See [Architectural Decision](#architectural-decision) for rationale.

## Purpose

Get users into validation as fast as possible. Phase 0 captures the minimal information needed to begin Phase 1 research.

**The Founder's Brief is now an OUTPUT of Phase 1, not an INPUT collected during onboarding.**

## Quick Start Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           QUICK START                                        │
│                                                                              │
│  Entry: User signs up and lands on onboarding page                          │
│  Exit: Project created, Phase 1 triggered                                   │
│  Duration: ~30 seconds                                                       │
│  AI Calls: 0                                                                 │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  User provides:                                                              │
│  • Business idea (1-3 sentences, free text)                                 │
│  • Optional: Upload pitch deck or paste notes                               │
│                                                                              │
│  System creates:                                                             │
│  • Project record with raw_idea                                             │
│  • Validation run record                                                     │
│                                                                              │
│  System triggers:                                                            │
│  • Phase 1 via Modal /kickoff                                               │
│                                                                              │
│  User redirected to:                                                         │
│  • Dashboard showing "Phase 1: Researching your idea..."                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Why This Works

| Aspect | Old (7-Stage Conversation) | New (Quick Start) |
|--------|---------------------------|-------------------|
| Time to start | 30+ minutes | 30 seconds |
| AI cost | $17+ per user | $0 |
| Determinism | 57-92% variance | 100% deterministic |
| User effort | Answer 28 fields | Write 1-3 sentences |
| Data quality | User guesses | AI researches |

**Key Insight**: Phase 1 (VPC Discovery) already researches market, customers, and competitors. Having users provide this information upfront was redundant—and often wrong.

---

## User Flows

### Founder (Direct)

```
1. Sign up → redirect to /onboarding/founder
2. Enter business idea (30 seconds)
3. Click "Start Validation"
4. System creates project + triggers Phase 1
5. Redirect to dashboard (shows Phase 1 progress)
6. Phase 1 completes → HITL: approve_discovery_output
7. Continue to Phase 2
```

**Entry Point:** `/onboarding/founder`

**UI Specification:**
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
│   │                                                                      │   │
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

### Consultant (Client Management)

**Constraint:** Consultants can only add Founders who have already signed up.

```
1. Sign up → redirect to /consultant-dashboard
2. Dashboard shows "Add your first client"
3. Search for client by email (must be existing Founder)
4. Enter business idea on client's behalf
5. System creates project under client's account
6. Consultant linked as advisor
7. Phase 1 runs for client's project
8. Consultant reviews HITL checkpoints with client
```

**Entry Point:** `/consultant-dashboard` → Add Client

**UI Specification:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Add Client                                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Find your client:                                                          │
│  (Client must have an existing StartupAI Founder account)                   │
│                                                                              │
│  ┌───────────────────────────────────────────────────────┐ [ Search ]       │
│  │ client@example.com                                     │                  │
│  └───────────────────────────────────────────────────────┘                  │
│                                                                              │
│  ✓ Found: Sarah Johnson (sarah@example.com)                                 │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  What's their business idea?                                                │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                      │   │
│   │ [Same input as Founder Quick Start]                                 │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│                       [ Start Validation → ]                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Relationship Model:**
- Project belongs to Client (Founder)
- Consultant is linked as `advisor_id` on project
- Both can view project progress
- Consultant can approve HITL checkpoints (configurable)

---

## Backend Flow

### API: Quick Start Submission

**Endpoint:** `POST /api/projects/quick-start`

**Request:**
```json
{
  "raw_idea": "A meal planning app that helps busy parents...",
  "additional_context": "Optional notes or extracted pitch deck text",
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

**Backend Steps:**
1. Validate input
2. Create `project` record
3. Create `validation_run` record
4. Call Modal `/kickoff` with `raw_idea`
5. Return project ID

### Database Changes

**New field on `projects` table:**
```sql
ALTER TABLE projects ADD COLUMN raw_idea TEXT NOT NULL;
ALTER TABLE projects ADD COLUMN additional_context TEXT;
```

**Removed dependencies:**
- `onboarding_sessions` table → deprecated (can be dropped after migration)
- `entrepreneur_briefs` table → now populated by Phase 1, not Phase 0

---

## Phase 1 Integration

Phase 1 (VPC Discovery) now has expanded responsibilities:

### Input
```json
{
  "project_id": "uuid",
  "raw_idea": "A meal planning app that helps busy parents...",
  "additional_context": "Optional notes..."
}
```

### New Phase 1 Outputs
1. **Founder's Brief** - Generated from research (not user input)
2. **Customer Profile** - VPC left side
3. **Value Map** - VPC right side

### Combined HITL Checkpoint

**Old:** Two separate checkpoints
- `approve_founders_brief` (Phase 0)
- `approve_vpc` (Phase 1)

**New:** Single combined checkpoint
- `approve_discovery_output` (Phase 1)

User reviews all three outputs together before proceeding to Phase 2.

---

## What Was Removed

### Removed Components

| Component | Reason |
|-----------|--------|
| 7-stage conversation (Alex/Maya) | Replaced by single text input |
| Per-message AI assessment | No conversation to assess |
| Stage progression logic | No stages |
| OnboardingCrew (4 agents) | No transcript to process |
| Two-Pass Architecture | No passes needed |

### Removed Agents

| Agent ID | Name | Disposition |
|----------|------|-------------|
| O1 | Interview Gap Analyzer | DELETED - no interview |
| GV1 | Concept Validator | MOVED to Phase 1 |
| GV2 | Intent Verification | DELETED - no transcript |
| S1 | Brief Compiler | MOVED to Phase 1 |

**Net effect:** OnboardingCrew dissolved. Validation and compilation responsibilities moved to Phase 1 VPCDiscoveryCrew.

### Removed Code (Frontend)

| File | Lines | Reason |
|------|-------|--------|
| `founder-quality-assessment.ts` | ~400 | No assessment needed |
| `founder-stages-config.ts` | ~200 | No stages |
| `consultant-quality-assessment.ts` | ~300 | No assessment needed |
| `consultant-stages-config.ts` | ~150 | No stages |
| `founder-onboarding-prompt.ts` | ~300 | No AI conversation |
| `consultant-onboarding-prompt.ts` | ~120 | No AI conversation |
| Streaming chat components | ~500 | No streaming |

**Total:** ~2000 lines of complex code removed.

---

## Architectural Decision

### Problem Statement

The original Phase 0 had AI in the critical path:
1. AI generates questions
2. User responds freely
3. AI extracts data from response
4. AI assesses completeness
5. Loop until "done"

This caused:
- **Non-determinism:** Same conversation → different progress (57-92% variance)
- **High cost:** $17+ per test run, $1.47 per "free" model attempt
- **Test flakiness:** E2E tests unreliable
- **Slow onboarding:** 30+ minutes per user

### Root Cause

> We put AI in the critical path for something that doesn't require AI.

The 7-stage conversation collected information that Phase 1 would research anyway:
- Market size → Phase 1 researches this
- Competitors → Phase 1 researches this
- Customer segments → Phase 1 researches this

Users were guessing answers that AI could find more accurately.

### Solution

1. **Remove AI from Phase 0** - Quick Start is a simple form
2. **Move brief generation to Phase 1** - AI researches, then compiles brief
3. **Combine HITL checkpoints** - User reviews brief + VPC together

### Benefits

| Metric | Before | After |
|--------|--------|-------|
| Time to start validation | 30+ min | 30 sec |
| Onboarding AI cost | $17+ | $0 |
| Test determinism | ~75% | 100% |
| Code complexity | 2000+ lines | ~100 lines |
| User friction | High | Minimal |

---

## Migration Notes

### Existing Projects

Projects created before this change have `entrepreneur_brief` populated from the old conversation flow. These will continue to work—Phase 1 can use the existing brief instead of generating one.

### Feature Flag

During transition:
```env
FEATURE_QUICK_START=true  # Use new flow
FEATURE_QUICK_START=false # Use legacy conversation
```

### Data Migration

No immediate migration required. The `onboarding_sessions` table can be retained for historical data and dropped after 90 days if no issues arise.

---

## Entry/Exit Criteria

### Entry Criteria
- User has signed up and is authenticated
- User lands on onboarding page

### Exit Criteria
- Project created with `raw_idea`
- Phase 1 triggered via Modal
- User redirected to dashboard

**No HITL checkpoint in Phase 0.** The first HITL is now in Phase 1: `approve_discovery_output`.

---

## Summary

### What Phase 0 Does Now
1. Capture business idea (1-3 sentences)
2. Create project record
3. Trigger Phase 1
4. Redirect to dashboard

### What Phase 0 Does NOT Do
- Collect 28 fields of data
- Run AI conversations
- Assess quality or completeness
- Generate Founder's Brief

### Pattern Summary

| Pattern | This Phase |
|---------|------------|
| **Phase** | Phase 0: Quick Start |
| **Flow** | N/A (no CrewAI involvement) |
| **Crew** | N/A |
| **Agents** | 0 |
| **HITL** | None (moved to Phase 1) |

---

## Related Documents

### Architecture
- [00-introduction.md](./00-introduction.md) - Quick start and orientation
- [01-ecosystem.md](./01-ecosystem.md) - Three-service architecture
- [02-organization.md](./02-organization.md) - Agent organization
- [03-methodology.md](./03-methodology.md) - VPD framework

### Phase Specifications
- **Phase 0: Quick Start** - (this document)
- [05-phase-1-vpc-discovery.md](./05-phase-1-vpc-discovery.md) - VPC Discovery + Brief Generation
- [06-phase-2-desirability.md](./06-phase-2-desirability.md) - Desirability validation
- [07-phase-3-feasibility.md](./07-phase-3-feasibility.md) - Feasibility validation
- [08-phase-4-viability.md](./08-phase-4-viability.md) - Viability + Decision

### Historical
- [adr/004-two-pass-onboarding-architecture.md](../adr/004-two-pass-onboarding-architecture.md) - SUPERSEDED
- [adr/005-state-first-synchronized-loop.md](../adr/005-state-first-synchronized-loop.md) - SUPERSEDED

---

## Appendix: Founder's Brief Schema

The Founder's Brief schema remains unchanged. It is now an OUTPUT of Phase 1 rather than Phase 0.

```python
class FoundersBrief(BaseModel):
    """Generated by Phase 1 from research + raw_idea."""

    # Identity
    brief_id: str
    project_id: str
    created_at: datetime
    version: int = 1

    # The Idea (from user input)
    the_idea: TheIdea

    # Hypotheses (generated from research - NOT validated)
    problem_hypothesis: ProblemHypothesis
    customer_hypothesis: CustomerHypothesis
    solution_hypothesis: SolutionHypothesis

    # Assumptions & Success (AI-generated priorities)
    key_assumptions: List[Assumption]
    success_criteria: SuccessCriteria

    # Research Context (new - from Phase 1 research)
    market_research: MarketResearch
    competitor_analysis: CompetitorAnalysis

    # QA Status
    qa_status: QAStatus


class TheIdea(BaseModel):
    """Extracted from user's raw_idea input."""
    raw_input: str  # Original user text
    one_liner: str  # AI-refined summary
    description: str  # AI-expanded description
    category: str  # AI-classified industry/category


class MarketResearch(BaseModel):
    """New - generated by Phase 1 research."""
    market_size: str
    growth_rate: str
    key_trends: List[str]
    regulatory_considerations: List[str]


class CompetitorAnalysis(BaseModel):
    """New - generated by Phase 1 research."""
    direct_competitors: List[Competitor]
    indirect_alternatives: List[str]
    market_gaps: List[str]
```

See [05-phase-1-vpc-discovery.md](./05-phase-1-vpc-discovery.md) for full brief generation specification.
