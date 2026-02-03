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
6. Phase 1 Stage A completes → HITL: approve_brief (editable)
7. Phase 1 Stage B completes → HITL: approve_discovery_output (Brief + VPC)
8. Continue to Phase 2
```

**Entry Point:** `/onboarding/founder`

**UI Specification:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                    What's your business idea? *                             │
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
│   Help us understand your market (optional but recommended)                  │
│                                                                              │
│   Industry:     [ Select...          ▼]                                     │
│   Target user:  [ Select...          ▼]                                     │
│   Geography:    [ Select...          ▼]                                     │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ Have notes to share? (optional)                                     │   │
│   │                                                                      │   │
│   │ [ Paste text ]                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│                       [ Start Validation → ]                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

> **V1 Scope**: Text-only input. File upload (PDF, DOCX) deferred to V2.

**Validation Rules:**
- Business idea: Required, min 10 characters
- Hints: Optional (industry, target_user, geography dropdowns)
- Notes: Optional, max 10,000 characters

### Consultant (Client Management)

> **Architectural Update (2026-02-03)**: The Consultant persona is part of the Portfolio Holder umbrella. See [02-organization.md](./02-organization.md#portfolio-holder-marketplace-umbrella) for the complete marketplace architecture.

#### Three Connection Flows

Consultants (Portfolio Holders) can establish relationships with Founders through three flows:

**Flow 1: Invite-New** (Traditional)
```
1. Sign up → redirect to /consultant-dashboard
2. Dashboard shows "Invite Client"
3. Enter client email + select relationship_type (advisory, capital, program, service, ecosystem)
4. System sends invite email with token
5. Founder receives email → signs up → accepts/declines connection
6. If accepted: Relationship active, consultant linked
7. Phase 1 runs for client's project
8. Consultant reviews HITL checkpoints with client
```

**Flow 2: Link-Existing** (Marketplace)
```
1. Verified consultant browses Founder Directory
2. Directory shows founders with:
   - founder_directory_opt_in = TRUE
   - problem_fit IN ('partial_fit', 'strong_fit')
3. Consultant views founder's evidence package (badges only until connected)
4. Consultant sends connection request with:
   - relationship_type selection
   - Optional message
5. Founder reviews request on dashboard
6. Founder accepts/declines (30-day cooldown on decline)
7. If accepted: Full evidence access granted
```

**Flow 3: Founder RFQ** (Marketplace)
```
1. Founder creates Request for Quote (RFQ) specifying:
   - What they need (capital, advisory, program, service, ecosystem)
   - Industries, stage, timeline, budget range
2. RFQ posted to RFQ Board (verified consultants only)
3. Verified consultant browses RFQ Board
4. Consultant responds with message
5. Founder reviews responses
6. Founder accepts/declines each response
7. If accepted: Connection created with specified relationship_type
```

**Entry Point (Invite):** `/consultant-dashboard` → Invite Client
**Entry Point (Browse):** `/consultant/founders` → Founder Directory (verified only)
**Entry Point (RFQ):** `/consultant/rfq` → RFQ Board (verified only)

#### Verification Requirement

Only **verified** consultants can access:
- Founder Directory (`/consultant/founders`)
- RFQ Board (`/consultant/rfq`)

Verification status is tied to paid subscription (Advisor $199/mo or Capital $499/mo). See [02-organization.md](./02-organization.md#verification-system) for details.

#### Relationship Types

| Type | Description | Typical Entities |
|------|-------------|------------------|
| `advisory` | Strategic guidance | Mentors, coaches, fractional executives |
| `capital` | Funding support | Angels, VCs, family offices |
| `program` | Cohort-based support | Accelerators, incubators |
| `service` | Professional support | Lawyers, accountants, agencies |
| `ecosystem` | Community and networking | Coworking, startup communities |

**Entry Point (Traditional):** `/consultant-dashboard` → Add Client

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
  "hints": {
    "industry": "consumer_tech",
    "target_user": "parents",
    "geography": "north_america"
  },
  "additional_context": "Optional notes (max 10,000 chars)",
  "client_id": "uuid (optional - for consultant flow)",
  "idempotency_key": "client-generated-uuid (optional)"
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `raw_idea` | Yes | Business idea (min 10 chars) |
| `hints` | No | Structured hints to constrain research |
| `additional_context` | No | Supplementary notes |
| `client_id` | No | For consultant flow |
| `idempotency_key` | No | Prevents duplicate runs |

**Response:**
```json
{
  "project_id": "uuid",
  "run_id": "uuid",
  "status": "phase_1_started",
  "redirect_url": "/projects/{project_id}"
}
```

> **Note**: Response uses `run_id` (not `validation_run_id`) to match Modal API conventions.

**Backend Steps:**
1. Check idempotency (return existing run if duplicate)
2. Check rate limits (return 429 if exceeded)
3. Validate input
4. Create `project` record with `raw_idea` and `hints`
5. Create `validation_run` record
6. Call Modal `/kickoff` with `raw_idea` and `hints`
7. Return project ID and run ID

### Database Changes

**New fields on `projects` table:**
```sql
ALTER TABLE projects ADD COLUMN raw_idea TEXT NOT NULL;
ALTER TABLE projects ADD COLUMN hints JSONB;
ALTER TABLE projects ADD COLUMN additional_context TEXT;
```

**Hints schema:**
```typescript
// projects.hints JSONB structure
interface ProjectHints {
  industry?: string;        // e.g., "SaaS", "E-commerce", "Healthcare"
  target_user?: string;     // e.g., "Small business owners", "Enterprise IT"
  geography?: string;       // e.g., "North America", "Global", "UK"
}
```

> **Design Note**: Hints are stored at the project level (not run level) because they describe the business context which doesn't change between validation runs. The hints guide BriefGenerationCrew's research but don't override AI-discovered insights.

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
  "hints": {
    "industry": "Consumer Apps",
    "target_user": "Parents with children",
    "geography": "North America"
  },
  "additional_context": "Optional notes..."
}
```

### New Phase 1 Outputs
1. **Founder's Brief** - Generated from research (not user input)
2. **Customer Profile** - VPC left side
3. **Value Map** - VPC right side

### Phase 1 HITL Checkpoints

**Old:** Two separate checkpoints in different phases
- `approve_founders_brief` (Phase 0) - after 7-stage conversation
- `approve_vpc_completion` (Phase 1) - after VPC generation

**New:** Two checkpoints within Phase 1
- `approve_brief` (Phase 1, Stage A) - after BriefGenerationCrew, brief is editable
- `approve_discovery_output` (Phase 1, Stage B) - after VPC generation, final review

**Sequencing:**
```
Phase 1 Stage A: BriefGenerationCrew
    ↓
HITL: approve_brief (user can edit brief)
    ↓
Phase 1 Stage B: VPC crews run with edited brief
    ↓
HITL: approve_discovery_output (review Brief + VPC together)
    ↓
Phase 2
```

User edits the brief at `approve_brief`, then reviews the complete output at `approve_discovery_output` before proceeding to Phase 2.

---

## What Was Removed

> **Historical Context (2026-01-19)**: This section documents the migration from the previous 7-stage conversational architecture to Quick Start. These components no longer exist in the current system.

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

**Net effect (historical):** OnboardingCrew was dissolved. GV1 and S1 moved to Phase 1's BriefGenerationCrew.

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

**No HITL checkpoint in Phase 0.** The first HITL is now in Phase 1: `approve_brief` (after BriefGenerationCrew), followed by `approve_discovery_output` (after VPC crews).

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
