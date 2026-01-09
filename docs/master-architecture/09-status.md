---
purpose: Authoritative ecosystem status across all three services
status: active
last_reviewed: 2026-01-09
last_updated: 2026-01-09
vpd_compliance: true
---

# StartupAI Ecosystem Status

This document provides an **authoritative, cross-repository view** of implementation status across the three-service ecosystem. Updated by cross-referencing all repos.

> **Methodology Reference**: See [03-methodology.md](./03-methodology.md) for VPD framework patterns.

---

## Executive Summary

| Service | Status | Completion | Primary Blocker |
|---------|--------|------------|-----------------|
| **AI Founders Core** (startupai-crew) | Live testing Phase 0-2 complete | ~95% | Phase 3-4 live validation |
| **Marketing Site** (startupai.site) | Production, static export | ~95% | None (live API connected) |
| **Product App** (app.startupai.site) | Modal integration complete | ~95% | Live E2E verification |

> **Live Testing In Progress (2026-01-09)**: Phase 0-2 validated with real LLM calls. 5 issues discovered and fixed. Signal-based HITL routing implemented. See [modal-live-testing.md](../work/modal-live-testing.md).

**Ecosystem State**: Modal serverless deployed and live testing in progress. Phase 0 (Onboarding), Phase 1 (VPC Discovery), and Phase 2 (Desirability) validated with real LLM calls. Key fixes: template variable timing, HITL phase advancement, signal-based routing.

---

## Architecture Status

### CrewAI Pattern Hierarchy

> **Single Source**: See [00-introduction.md](./00-introduction.md#3-crewai-pattern-hierarchy) for complete pattern definitions.

The architecture follows CrewAI's documented patterns:

```
PHASE (Business Concept) → FLOW (Orchestration) → CREW (Agent Group) → AGENT → TASK
```

| Metric | Count | Notes |
|--------|-------|-------|
| **Phases** | 5 | Business concepts (0: Onboarding → 4: Viability) |
| **Flows** | 5 | Event-driven orchestrators with `@start`, `@listen`, `@router` |
| **Crews** | 14 | Collaborative agent groups (2+ agents each) |
| **Agents** | 45 | Individual executors with role/goal/backstory |
| **HITL Checkpoints** | 10 | Human approval gates |

### Phase Structure (VPD Framework)

StartupAI implements a 5-phase validation architecture based on Value Proposition Design:

| Phase | Name | Flow | Crews | Agents | Specification |
|-------|------|------|-------|--------|---------------|
| **0** | Onboarding | `OnboardingFlow` | 1 | 4 | [04-phase-0-onboarding.md](./04-phase-0-onboarding.md) |
| **1** | VPC Discovery | `VPCDiscoveryFlow` | 5 | 18 | [05-phase-1-vpc-discovery.md](./05-phase-1-vpc-discovery.md) |
| **2** | Desirability | `DesirabilityFlow` | 3 | 9 | [06-phase-2-desirability.md](./06-phase-2-desirability.md) |
| **3** | Feasibility | `FeasibilityFlow` | 2 | 5 | [07-phase-3-feasibility.md](./07-phase-3-feasibility.md) |
| **4** | Viability | `ViabilityFlow` | 3 | 9 | [08-phase-4-viability.md](./08-phase-4-viability.md) |

### Crew Summary (14 Crews)

| Phase | Crew | Agents | Purpose |
|-------|------|--------|---------|
| 0 | `OnboardingCrew` | O1, GV1, GV2, S1 | Interview, validate, compile brief |
| 1 | `DiscoveryCrew` | E1, D1-D4 | Experiment design, evidence collection |
| 1 | `CustomerProfileCrew` | J1, J2, PAIN_RES, PAIN_RANK, GAIN_RES, GAIN_RANK | Jobs, Pains, Gains discovery |
| 1 | `ValueDesignCrew` | V1-V3 | Products, Pain Relievers, Gain Creators |
| 1 | `WTPCrew` | W1-W2 | Willingness-to-pay validation |
| 1 | `FitAssessmentCrew` | FIT_SCORE, FIT_ROUTE | Fit scoring, iteration routing |
| 2 | `BuildCrew` | F1-F3 | Landing pages, test artifacts |
| 2 | `GrowthCrew` | P1-P3 | Ad campaigns, desirability signals |
| 2 | `GovernanceCrew` | G1-G3 | QA, security, audit |
| 3 | `BuildCrew` | F1-F3 | Technical feasibility (reused) |
| 3 | `GovernanceCrew` | G1, G2 | Gate validation |
| 4 | `FinanceCrew` | L1-L3 | Unit economics, compliance |
| 4 | `SynthesisCrew` | C1-C3 | Evidence synthesis, decision |
| 4 | `GovernanceCrew` | G1-G3 | Final validation, flywheel |

### Modal Serverless Deployment (Production)

> **Status**: DEPLOYED - See [ADR-002](../adr/002-modal-serverless-migration.md) for full architecture.

**Three-Layer Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│  INTERACTION LAYER (Netlify) - Edge Functions trigger Modal │
└─────────────────────────────────┬───────────────────────────┘
                                  │
┌─────────────────────────────────┼───────────────────────────┐
│  ORCHESTRATION LAYER (Supabase) - State + Realtime + RLS   │
└─────────────────────────────────┬───────────────────────────┘
                                  │
┌─────────────────────────────────┼───────────────────────────┐
│  COMPUTE LAYER (Modal) - Ephemeral Python, pay-per-second  │
└─────────────────────────────────────────────────────────────┘
```

**Production URL:** `https://chris00walker--startupai-validation-fastapi-app.modal.run`

**Implementation Status:**

| Task | Status | Notes |
|------|--------|-------|
| ADR written | ✅ Complete | [ADR-002](../adr/002-modal-serverless-migration.md) |
| Modal account setup | ✅ Complete | Production deployment live |
| Supabase tables | ✅ Complete | validation_runs, validation_progress, hitl_requests |
| modal_app/ scaffold | ✅ Complete | 5 phase modules, FastAPI app |
| 14 crews implemented | ✅ Complete | 45 agents, 185 tests passing |
| Phase flows | ✅ Complete | phase_0 through phase_4 |
| E2E testing | ✅ Complete | 17 tests, Phase 0→4 flow validated |
| Production cutover | ⏳ Pending | Awaiting live validation run |

### 3-Crew Deployment (AMP Platform) - DEPRECATED

> **Status**: DEPRECATED due to platform reliability issues. Being replaced by Modal serverless. See [ADR-001](../adr/001-flow-to-crew-migration.md) (superseded) and [ADR-002](../adr/002-modal-serverless-migration.md).

Legacy deployment (reference only):

| Crew | Repository | UUID | Status |
|------|------------|------|--------|
| **Crew 1: Intake** | `chris00walker/startupai-crew` | `6b1e5c4d-e708-4921-be55-08fcb0d1e94b` | ⚠️ Deprecated |
| **Crew 2: Validation** | `chris00walker/startupai-crew-validation` | `3135e285-c0e6-4451-b7b6-d4a061ac4437` | ⚠️ Deprecated |
| **Crew 3: Decision** | `chris00walker/startupai-crew-decision` | `7da95dc8-7bb5-4c90-925b-2861fa9cba20` | ⚠️ Deprecated |

> **Note**: The 3-Crew AMP deployment was a platform-constrained workaround that exhibited reliability issues. See [Architecture Migration History](#architecture-migration-history) for context.

### Architecture Migration History

| Date | Change | Reason |
|------|--------|--------|
| 2026-01-08 | **Modal serverless migration proposed** | AMP reliability issues, platform-agnostic deployment, $0 idle costs |
| 2026-01-08 | ADR-002 written, ADR-001 superseded | Document Modal architecture decision |
| 2026-01-07 | CrewAI pattern standardization across all docs | Align with CrewAI documentation: Phase → Flow → Crew → Agent |
| 2026-01-07 | Fixed one-agent "crews" → consolidated into proper crews | CrewAI definition: crew = collaborative group (2+ agents) |
| 2026-01-07 | Renamed "Flow 1-7" to proper Crew names in Phase 1 | Terminology correction: those were Crews, not Flows |
| 2026-01-06 | Crew 1 aligned to CrewAI best practices (100%) | Pydantic schemas, reasoning mode, enriched backstories |
| 2026-01-05 | Added VPD Phase 0-4 specifications | Framework compliance |
| 2025-12-05 | Migrated from Flow to Crew architecture | AMP compatibility issues with `type = "flow"` |

---

## AI Founders Core (`startupai-crew`)

### What Works

| Capability | Status | Notes |
|------------|--------|-------|
| 5-Flow/14-Crew architecture | ✅ Implemented | 45 agents, 10 HITL checkpoints |
| Modal serverless deployment | ✅ Production | Single repo, $0 idle costs |
| 14 crews implemented | ✅ Complete | All crews with YAML configs |
| 45 agents defined | ✅ Complete | Role, goal, backstory for each |
| Phase flows (0-4) | ✅ Complete | phase_0.py through phase_4.py |
| Test suite | ✅ 555 tests | Crew tests + E2E + live testing suite |
| Pydantic output schemas | ✅ Complete | ValidationRunState, ViabilityEvidence, etc. |
| HITL integration | ✅ Complete | 10 checkpoints with checkpoint-and-resume |
| Supabase state persistence | ✅ Complete | validation_runs, validation_progress tables |
| Tools | ✅ 18+ tools | TavilySearch, CustomerResearch, MethodologyCheck, etc. |

### What's Pending

| Item | Status | Blocker |
|------|--------|---------|
| Live production validation | ⏳ Ready | E2E tests passing, needs real run |
| Tool wiring to agents | ⏳ Partial | Some tools need agent assignment |
| Ad platform integration | ❌ Not connected | Meta/Google Ads APIs (business decision) |
| Real analytics tracking | ⚠️ Partial | PostHog exists; ad platform analytics missing |

### HITL Checkpoints (10 canonical)

> **Canonical Count**: 10 HITL checkpoints across all 5 phases. The AMP 3-crew deployment had an additional crew-chaining checkpoint (`approve_intake_to_validation`) which is not part of the canonical architecture.

#### Phase 0: Onboarding

| Checkpoint | Owner | Purpose |
|------------|-------|---------|
| `approve_founders_brief` | Founder + Guardian | Founder's Brief approval |

#### Phase 1: VPC Discovery

| Checkpoint | Owner | Purpose |
|------------|-------|---------|
| `approve_experiment_plan` | Sage (E1) | Experiment design approval |
| `approve_pricing_test` | Ledger (W1, W2) | Pricing test approval |
| `approve_vpc_completion` | Compass (F1) | VPC gate (fit ≥ 70) |

#### Phase 2: Desirability

| Checkpoint | Owner | Purpose |
|------------|-------|---------|
| `approve_campaign_launch` | Forge + Pulse | Ad creative approval |
| `approve_spend_increase` | Guardian | Budget approval |
| `approve_desirability_gate` | Guardian | Gate: Desirability → Feasibility |

#### Phase 3: Feasibility

| Checkpoint | Owner | Purpose |
|------------|-------|---------|
| `approve_feasibility_gate` | Guardian | Gate: Feasibility → Viability |

#### Phase 4: Viability

| Checkpoint | Owner | Purpose |
|------------|-------|---------|
| `approve_viability_gate` | Guardian | Gate: Viability → Decision |
| `request_human_decision` | Founder | Final pivot/proceed decision |

#### AMP-Only Checkpoint (DEPRECATED)

> **⚠️ NOT CANONICAL**: This checkpoint existed only in the AMP 3-crew workaround architecture.

| Checkpoint | Purpose | Status |
|------------|---------|--------|
| `approve_intake_to_validation` | Gate: Crew 1 → Crew 2 | DEPRECATED (AMP workaround) |

### Crew 1 Architecture (Latest)

**Best Practices Alignment**: 100%

| Component | Status |
|-----------|--------|
| Pydantic schemas | ✅ 6 output models in `src/intake_crew/schemas.py` |
| `output_pydantic` | ✅ All 6 tasks enforce structured outputs |
| `reasoning=True` | ✅ Enabled for S2 (research) and G1 (QA) |
| Enriched backstories | ✅ Years of experience, methodology expertise |
| Tools wired | ✅ TavilySearchTool, CustomerResearchTool, MethodologyCheckTool |

---

## Marketing Site (`startupai.site`)

### What Works

| Feature | Status | Notes |
|---------|--------|-------|
| Static export | ✅ Production | Next.js 15, deployed on Netlify |
| 6 AI Founders showcase | ✅ Complete | Guardian + 5 operational founders with avatars |
| Two-layer governance diagram | ✅ Complete | Guardian meta-governance visualization |
| Lead capture (Waitlist) | ✅ Production | Formspree → Zapier → Supabase |
| Sign-up flow | ✅ Working | Supabase Auth + GitHub OAuth |
| Plan parameter passing | ✅ Working | Tier selection captured on signup |
| PostHog analytics | ✅ Bootstrapped | Client-side instrumentation |
| All content pages | ✅ Complete | Home, Product, Pricing, About, AI Strategy, etc. |

### What's Using Mock Data

| Feature | Current State | Required Integration |
|---------|---------------|---------------------|
| Activity Feed | ✅ Components built, mock data | Connect to Product App API |
| Metrics Dashboard | ✅ Components built, mock data | Connect to Product App API |
| Founder Stats | Hardcoded values | Connect to real CrewAI metrics |
| Journey Updates | Static content | Wire to real learning captures |

### What Doesn't Exist

| Feature | Notes |
|---------|-------|
| Real-time updates | Static site; no websocket/polling |
| AI Chat | Not applicable (static); redirects to product app |
| Contact form backend | Frontend validation only; no persistence |

### Marketing vs Reality Gap

| Promise | Reality | Status |
|---------|---------|--------|
| "Build your MVP" | LandingPageGeneratorTool exists | ⚠️ Full scaffold pending |
| "Real ad spend ($450-525)" | No Meta/Google Ads API | ❌ Not connected |
| "Unit economics analysis" | 10 UnitEconomicsModels + benchmarks | ✅ Complete |
| "2-week validation cycles" | Flow runs in minutes | ⚠️ Quality depends on data |
| "Evidence-based validation" | TavilySearchTool provides research | ✅ Works |
| "6 AI Founders team" | 19 agents across 3 crews | ✅ Complete |

---

## Product App (`app.startupai.site`)

### What Works

| Feature | Status | Notes |
|---------|--------|-------|
| Supabase Auth | ✅ Production | GitHub OAuth, JWT sessions |
| Onboarding chat | ✅ Complete | Vercel AI SDK, 7 stages, streaming, session resume |
| Alex persona | ✅ Complete | Team awareness of 6 AI Founders |
| Founder dashboard | ✅ Complete | 595 lines, 5 tabs |
| Consultant dashboard | ✅ Complete | 376 lines, real portfolio data |
| CrewAI webhook | ✅ Production-ready | Multi-table persistence, idempotent |
| Public APIs | ✅ Shipped | Activity Feed + Metrics for marketing |
| HITL approval system | ✅ Complete | 9 approval types, decision workflows |
| VPC visualization | ✅ Complete | Strategyzer-style SVG with animated fit |
| Evidence Explorer | ✅ Complete | D-F-V categorization and metrics |
| Component library | ✅ 50+ components | Shadcn UI |
| Test suite | ✅ 463+ passing | Jest + Playwright |
| Accessibility | ✅ 70% WCAG 2.1 AA | Foundation complete |

### Database Status

| Table | Schema | Data | UI |
|-------|--------|------|-----|
| users | ✅ | ✅ | ✅ |
| projects | ✅ | ✅ | ✅ |
| reports | ✅ | Via webhook | ✅ |
| evidence | ✅ | Via webhook | ✅ |
| entrepreneur_briefs | ✅ | Via webhook | ✅ |
| crewai_validation_states | ✅ | Via webhook | Internal |
| public_activity_log | ✅ | Via webhook | ✅ |
| onboarding_sessions | ✅ | ✅ | ✅ |
| approvals | ✅ | ✅ | ✅ |

### What's Pending

| Item | Status | Notes |
|------|--------|-------|
| E2E flow verification | ⚠️ Needs live test | All components exist |
| PostHog coverage gaps | ⚠️ 13+ events defined | Need implementation |
| Dashboard mock replacement | ⚠️ Some remaining | Wire to CrewAI data |
| Screen reader polish | ⚠️ In progress | Accessibility refinements |

---

## Cross-Service Integration

### Working Integrations

| From | To | Method | Status |
|------|-----|--------|--------|
| Marketing → Supabase | Auth | Browser client | ✅ Working |
| Marketing → Product | Redirect | Plan parameter | ✅ Working |
| Product → CrewAI | Kickoff | REST API | ✅ Implemented |
| CrewAI → Product | Results | Webhook | ✅ Production-ready |
| CrewAI → Supabase | Persist | Via webhook | ✅ Working |
| Product → Marketing | Public APIs | REST | ✅ Shipped |

### Pending Integrations

| From | To | Status | Blocker |
|------|-----|--------|---------|
| Marketing ← Product | Activity Feed | ⚠️ API exists | Marketing needs to connect |
| Marketing ← Product | Metrics | ⚠️ API exists | Marketing needs to connect |
| CrewAI ← Ad Platforms | Campaign data | ❌ Not connected | Meta/Google API integration |

### Environment Variable Sync

| Variable | Marketing | Product | Crew |
|----------|-----------|---------|------|
| Supabase URL | ✅ Set | ✅ Set | N/A |
| Supabase Anon Key | ✅ Set | ✅ Set | N/A |
| Supabase Service Key | N/A | ✅ Set | N/A |
| OpenAI Key | N/A | ✅ Set | ✅ Set (AMP) |
| CrewAI Bearer | N/A | ✅ Set | N/A |
| PostHog Key | ✅ Set | ✅ Set | N/A |

---

## Critical Path to Launch

### Completed

- [x] Modal serverless infrastructure deployed
- [x] 14 crews implemented (45 agents)
- [x] 5 phase flows implemented (phase_0 through phase_4)
- [x] 555 tests (crew + E2E + live testing suite)
- [x] E2E integration tests (Phase 0→4 flow validated)
- [x] Product app Modal integration complete
- [x] Marketing site live API integration
- [x] HITL approval system (10 checkpoints)
- [x] Onboarding flow with AI coach
- [x] Guardian showcase on marketing site
- [x] Public APIs for marketing (Activity Feed + Metrics)

### Remaining Work

| Priority | Task | Owner | Blocker |
|----------|------|-------|---------|
| **P0** | First live validation run | Crew | None - E2E tests passing |
| **P1** | Tool wiring to agents | Crew | None |
| **P2** | PostHog coverage gaps | Product | None |
| **P3** | Ad platform integration | Crew | Business decision |

### E2E Verification Checklist

The following flow needs live verification:

```
User lands on startupai.site
    ↓
Signs up (Supabase Auth)
    ↓
Redirects to app.startupai.site with plan
    ↓
Completes onboarding chat (7 stages)
    ↓
Triggers Modal validation (POST /kickoff)
    ↓
Modal processes through 5 phases (14 crews, 45 agents)
    ↓
Results persist to Supabase (validation_runs table)
    ↓
Dashboard displays validation results
    ↓
Marketing activity feed shows real activity
```

**Status**: E2E integration tests passing (17 tests). Ready for live production validation run.

---

## Known Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| No ad platform APIs | Cannot run real ad campaigns | Manual campaign management |
| Static marketing site | No real-time updates | Periodic refresh or embed from product app |
| Token usage (~100K/run) | $2-5 per analysis | Acceptable for current pricing |
| No streaming progress | Users wait without updates | Future: SSE for progress |

---

## Change Log

| Date | Changes |
|------|---------|
| **2026-01-09** | Live Testing & Test Suite Expansion |
| | Phase 0-2 validated with real LLM calls |
| | 6 issues discovered and fixed during live testing |
| | Test suite expanded: 555 total tests |
| | Updated completion status: ~95% (was ~92%) |
| **2026-01-08** | E2E Integration Tests Complete |
| | Added 17 E2E integration tests (Phase 0→4 flow) |
| | Total: 202 tests passing (185 crew + 17 E2E) |
| | Updated completion status: ~90% (was ~85%) |
| | Ready for live production validation run |
| **2026-01-08** | Crew Implementation Complete |
| | All 14 crews implemented with 45 agents |
| | 185 crew tests passing (Phases 0-4) |
| | Modal infrastructure deployed to production |
| | Updated completion status: ~85% (was ~60%) |
| | Ready for E2E integration testing |
| **2026-01-08** | Modal Serverless Migration |
| | Proposed migration from CrewAI AMP to Modal serverless ([ADR-002](../adr/002-modal-serverless-migration.md)) |
| | Marked 3-Crew AMP deployment as DEPRECATED |
| | Added Modal Serverless Deployment section with migration status |
| | Updated Architecture Migration History |
| | ADR-001 superseded by ADR-002 |
| **2026-01-07** | CrewAI Pattern Standardization |
| | Added CrewAI Pattern Hierarchy section (Phase → Flow → Crew → Agent) |
| | Updated counts: 5 Flows, 14 Crews, 45 Agents, 10 HITL |
| | Added complete Crew Summary table |
| | Clarified 3-Crew AMP deployment as platform workaround |
| | Added Architecture Migration History entries |
| **2026-01-07** | Full rewrite with cross-repo verification |
| | Updated phase structure to 0-4 (was 0-3) |
| | Corrected deployment status: all 3 crews deployed |
| | Added marketing Guardian showcase |
| | Added product Public APIs (Activity Feed + Metrics) |
| | Updated test count: 463+ passing |
| | Corrected blockers: E2E verification, not deployment |
| 2026-01-06 | Crew 1 aligned to 100% CrewAI best practices |
| 2026-01-05 | Added VPD Phase 0-4 specifications |
| 2025-12-05 | Migrated from Flow to 3-Crew architecture |

---

## Related Documents

### Architecture
- [00-introduction.md](./00-introduction.md) - Quick start and orientation
- [01-ecosystem.md](./01-ecosystem.md) - Three-service architecture overview
- [02-organization.md](./02-organization.md) - 6 AI Founders and agents
- [03-methodology.md](./03-methodology.md) - VPD framework reference

### Phase Specifications
- [04-phase-0-onboarding.md](./04-phase-0-onboarding.md) - Founder's Brief capture
- [05-phase-1-vpc-discovery.md](./05-phase-1-vpc-discovery.md) - VPC Discovery
- [06-phase-2-desirability.md](./06-phase-2-desirability.md) - Desirability validation
- [07-phase-3-feasibility.md](./07-phase-3-feasibility.md) - Feasibility validation
- [08-phase-4-viability.md](./08-phase-4-viability.md) - Viability + Decision

### Reference
- [reference/api-contracts.md](./reference/api-contracts.md) - API specifications
- [reference/approval-workflows.md](./reference/approval-workflows.md) - HITL patterns

### Architecture Decision Records
- [ADR-001](../adr/001-flow-to-crew-migration.md) - Flow to 3-Crew Migration (Superseded)
- [ADR-002](../adr/002-modal-serverless-migration.md) - Modal Serverless Migration (Current)

### Cross-Repo Status
- `startupai.site/docs/work/cross-repo-blockers.md`
- `app.startupai.site/docs/work/cross-repo-blockers.md`
