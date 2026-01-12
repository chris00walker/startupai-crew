---
purpose: "Private technical source of truth for current engineering phases"
status: "active"
last_reviewed: "2026-01-12"
last_audit: "2026-01-12 - Quality audit complete, evidence gaps identified"
---

# Engineering Phases

> **Quality Audit (2026-01-12)**: Phase 0-2 tool audit revealed significant evidence gaps. Many tools are stubs, ad platform not implemented, interview agent produces hallucinations. Production blocked until quality issues resolved.

## 🚨 Quality Blockers (Must Fix Before Production)

**Current Reality**: Modal infrastructure works, but Phases 0-2 produce **hallucinated evidence**. Tools are wired but many are stubs or missing external connections.

### Critical Blocker #1: AdPlatformTool Not Implemented 🔴
**Impact**: BLOCKS ALL Phase 2 Desirability validation
**Affects**: P1, P2, P3 agents (entire GrowthCrew)

| What's Broken | Reality |
|---------------|---------|
| Meta Ads API | NOT IMPLEMENTED - returns placeholder text |
| Google Ads API | NOT IMPLEMENTED - returns placeholder text |
| Ad campaign creation | Cannot create ANY real ads |
| Ad metrics collection | Returns fake data |

**Options**:
- A) Implement Meta/Google Ads SDK integration (significant work, requires ad accounts)
- B) Accept manual ad data injection for MVP testing
- C) Remove ad experiments, use landing page conversions only as desirability signal

### Critical Blocker #2: D1 Interview Agent Produces Hallucinations 🔴
**Impact**: Phase 1 SAY evidence is fabricated
**Decision**: **REMOVE D1 Interview Agent**

| Problem | Evidence |
|---------|----------|
| TranscriptionTool | STUB - no Whisper API implementation |
| CalendarTool | Generates fake time slots, no real calendar integration |
| Interview outputs | Pure LLM roleplay, not real customer interviews |

**Resolution**: Remove D1 agent. Replace with SurveyTool for SAY evidence collection (see Blocker #3).

### Critical Blocker #3: No SurveyTool Exists 🔴
**Impact**: Cannot collect SAY evidence at scale
**Methodology requires**: Surveys for quantitative SAY evidence

**Recommendation**: Integrate **Tally** (free survey tool)
- ✅ Free unlimited forms, questions, and submissions
- ✅ Has API access and webhooks for integration
- ✅ Good UX for respondents
- ✅ No per-response pricing (unlike Typeform's 10/month limit)

**Alternative**: Google Forms (completely free, but needs Zapier middleware for API)

| Tool | Free Tier | API | Best For |
|------|-----------|-----|----------|
| **Tally** | Unlimited | Yes + Webhooks | Our use case |
| Typeform | 10 responses/mo | Yes | Too limited |
| Google Forms | Unlimited | Via middleware | Backup option |

### Critical Blocker #4: DO-Indirect Evidence Tools Are Stubs 🟡
**Impact**: Phase 1 D2 agent claims evidence it cannot collect

| Tool | Claimed Function | Reality |
|------|------------------|---------|
| ForumSearchTool | Mine Reddit, forums | **STUB** - not implemented |
| ReviewAnalysisTool | Analyze app store reviews | **STUB** - not implemented |
| SocialListeningTool | Monitor social mentions | **STUB** - not implemented |
| TrendAnalysisTool | Analyze Google Trends | **STUB** - not implemented |

**Working**: Only TavilySearchTool provides real external data.

### Critical Blocker #5: Product App Integration Not Wired 🔴
**Impact**: Users cannot see ANY validation results
**Location**: `~/projects/app.startupai.site`

| What's Broken | Reality |
|---------------|---------|
| Kickoff trigger | Product app doesn't call Modal `/kickoff` with correct params |
| Progress display | No UI shows real-time validation progress |
| Results retrieval | No UI retrieves/displays completed validation results |
| HITL approvals | No UI for human approval checkpoints |

**Current State**:
- Product app calls generic `$CREWAI_API_URL` without `flow_type: 'founder_validation'`
- Falls back to `generateStrategicAnalysis()` mock data
- Users see **mock recommendations**, not real AI validation
- Supabase tables exist (`validation_runs`, `validation_progress`, `hitl_requests`) but no frontend reads them

**Required for Each Phase**:

| Phase | Backend (this repo) | Frontend (app.startupai.site) |
|-------|---------------------|-------------------------------|
| Phase 0 | ✅ OnboardingFlow works | ❌ No Founder's Brief display |
| Phase 1 | ⚠️ VPCDiscoveryFlow partial | ❌ No VPC/Customer Profile UI |
| Phase 2 | 🔴 DesirabilityFlow blocked | ❌ No experiment results UI |
| Phase 3 | ⏳ Not tested | ❌ No feasibility report UI |
| Phase 4 | ⏳ Not tested | ❌ No final decision UI |
| HITL | ✅ Checkpoints work | ❌ No approval UI |

**Integration Tasks (Product App)**:
1. [ ] Update `/api/crewai/analyze` to call Modal `/kickoff` with correct params
2. [ ] Create validation progress component (subscribe to Supabase Realtime)
3. [ ] Create results display pages for each phase output
4. [ ] Create HITL approval UI (read `hitl_requests`, POST to `/hitl/approve`)
5. [ ] Add navigation from onboarding → validation → results

**Cross-Repo Coordination Required**: This work spans both repos:
- `startupai-crew`: Backend API contracts (this repo) ✅ Defined
- `app.startupai.site`: Frontend UI + API routes ❌ Not implemented

---

## Tool Reality Matrix (2026-01-12 Audit)

### Phase 0: Onboarding
| Agent | Tools | Status | Notes |
|-------|-------|--------|-------|
| O1 (Founder Interview) | None | ⚠️ LLM-only | No external validation |
| GV1 (Concept Validator) | None | ⚠️ LLM-only | No external validation |
| GV2 (Intent Verification) | None | ⚠️ LLM-only | No external validation |
| S1 (Brief Compiler) | None | ⚠️ LLM-only | Compiles from LLM outputs |

**Phase 0 Verdict**: Works as screening tool, but all outputs are unvalidated LLM reasoning.

### Phase 1: VPC Discovery
| Agent | Tools | Status | Notes |
|-------|-------|--------|-------|
| E1 (Experiment Designer) | TestCardTool, LearningCardTool | ✅ Working | LLM-based card generation |
| **D1 (Interview)** | TranscriptionTool, CalendarTool | 🔴 **REMOVE** | All stubs, produces hallucinations |
| D2 (Observation) | Tavily ✅, Forum ❌, Reviews ❌, Social ❌, Trends ❌ | ⚠️ Partial | Only Tavily works |
| D3 (CTA Tests) | ABTestTool ✅, AdPlatformTool ❌ | 🔴 Blocked | No ad platform APIs |
| D4 (Evidence Triangulation) | InsightExtractorTool, BehaviorPatternTool | ✅ Working | LLM synthesis |
| J1, J2 (Jobs) | Tavily ✅ | ⚠️ Partial | Forum/review tools are stubs |
| PAIN_RES, PAIN_RANK | Tavily ✅ | ⚠️ Partial | Forum/review tools are stubs |
| GAIN_RES, GAIN_RANK | Tavily ✅ | ⚠️ Partial | Forum/review tools are stubs |
| V1, V2, V3 (Value Design) | CanvasBuilderTool | ✅ Working | LLM-based VPC design |
| W1, W2 (WTP) | - | ⚠️ Manual | Needs real pricing experiment data |
| FIT_SCORE, FIT_ASSESS | MethodologyCheckTool | ✅ Working | VPC fit scoring |

### Phase 2: Desirability
| Agent | Tools | Status | Notes |
|-------|-------|--------|-------|
| F1 (Designer) | CanvasBuilderTool, TestCardTool | ✅ Working | Design artifacts |
| F2 (Developer) | LandingPageGeneratorTool | ⚠️ Quality issue | Generates placeholder HTML |
| F3 (Backend) | LandingPageDeploymentTool | ✅ Working | Deploys to Supabase Storage |
| P1 (Ad Creative) | AdPlatformTool | 🔴 **BLOCKED** | No Meta/Google API |
| P2 (Copywriting) | AdPlatformTool | 🔴 **BLOCKED** | No Meta/Google API |
| P3 (Analytics) | AnalyticsTool ✅, AdPlatformTool ❌ | 🔴 **BLOCKED** | Landing analytics work, ad metrics don't |
| G1 (QA) | MethodologyCheckTool | ✅ Working | QA validation |
| G2 (Security) | AnonymizerTool | ✅ Working | PII removal |
| G3 (Audit) | LearningCardTool | ✅ Working | Audit trail |

---

## What Actually Works Today

```
✅ WORKING (Real External Data):
├── TavilySearchTool (web search)
├── LandingPageDeploymentTool (Supabase Storage)
├── AnalyticsTool (landing page metrics only)
└── AnonymizerTool (PII removal)

✅ WORKING (LLM-Based, No External Validation):
├── VPC design and fit scoring
├── Test Card / Learning Card generation
├── Governance tools (QA checks)
└── Phase 0 onboarding flow

🔴 BLOCKED (Missing Implementation):
├── AdPlatformTool (Meta/Google APIs)
├── ForumSearchTool
├── ReviewAnalysisTool
├── SocialListeningTool
├── TrendAnalysisTool
└── TranscriptionTool

❌ HALLUCINATED (Remove):
└── D1 Interview Agent (simulated interviews)

❌ MISSING (Never Built):
└── SurveyTool (required for SAY evidence)
```

---

## Recommended Fix Order

### Phase 0: Make It Visible First
Before fixing evidence quality, users need to SEE results.

| # | Issue | Repo | Effort | Impact |
|---|-------|------|--------|--------|
| 0a | Wire Product App → Modal kickoff | app.startupai.site | 2-4h | Users can trigger validation |
| 0b | Add validation progress UI | app.startupai.site | 4-6h | Users see real-time status |
| 0c | Add Phase 0 results display | app.startupai.site | 4-6h | Users see Founder's Brief |
| 0d | Add HITL approval UI | app.startupai.site | 4-6h | Users can approve checkpoints |

### Phase 1: Fix Evidence Quality
After visibility, fix the quality of what users see.

| # | Issue | Repo | Effort | Impact |
|---|-------|------|--------|--------|
| 1 | Remove D1 Interview agent | startupai-crew | 2h | Stops hallucinated interviews |
| 2 | Add SurveyTool (Tally integration) | startupai-crew | 4-6h | Enables real SAY evidence |
| 3 | Decide Ad Platform strategy (A/B/C) | Decision | - | Unblocks Phase 2 |
| 4 | Fix F2 placeholder HTML | startupai-crew | 4h | Quality landing pages |
| 5 | Implement DO-indirect tools (or remove) | startupai-crew | 8-16h | Honest evidence sources |

### Phase 2: Complete the Loop
Wire remaining phases to product app.

| # | Issue | Repo | Effort | Impact |
|---|-------|------|--------|--------|
| 6 | Add Phase 1 VPC results display | app.startupai.site | 6-8h | Users see customer profile |
| 7 | Add Phase 2 experiment results UI | app.startupai.site | 6-8h | Users see desirability evidence |
| 8 | Add Phase 3-4 results display | app.startupai.site | 8-12h | Users see final decision |

---

## What's Done (Infrastructure Only)

| Item | Date | Notes |
|------|------|-------|
| Modal Infrastructure | 2026-01-08 | Production deployment live |
| Landing Page Deployment | 2026-01-10 | Supabase Storage E2E verified |
| Schema Alignment P0 | 2026-01-10 | Modal tables deployed |
| Bug Fixes #7-12 | 2026-01-10 | Enum bugs, HITL, tool input validation |
| Tool Wiring (structure) | 2026-01-10 | Tools attached to agents, but many are stubs |

## What's Deferred (Not Blocking Quality Fixes)

| Item | Effort | Why Deferred | Plan File |
|------|--------|--------------|-----------|
| Phase 3-4 Live Testing | 4-6h | Phase 0-2 quality must be fixed first | - |
| Architecture Documentation | 24-32h | Production quality takes priority | `merry-prancing-spark.md` |
| Schema Alignment P1-P3 | 8-12h | P0 sufficient for MVP | `effervescent-swimming-hollerith.md` |

---

## Architecture Summary

### Canonical Architecture (Per CrewAI Documentation)
| Metric | Count |
|--------|-------|
| **Phases** | 5 (0-4) |
| **Flows** | 5 (OnboardingFlow, VPCDiscoveryFlow, DesirabilityFlow, FeasibilityFlow, ViabilityFlow) |
| **Crews** | 14 |
| **Agents** | 45 |
| **HITL Checkpoints** | 10 |

### Target Deployment: Modal Serverless (DEPLOYED)
| Component | Description | Status |
|-----------|-------------|--------|
| **Interaction Layer** | Netlify Edge Functions | ✅ Production |
| **Orchestration Layer** | Supabase (PostgreSQL + Realtime) | ✅ Production |
| **Compute Layer** | Modal (ephemeral Python, pay-per-second) | ✅ Production |

**Production URL**: `https://chris00walker--startupai-validation-fastapi-app.modal.run`

See [ADR-002](../adr/002-modal-serverless-migration.md) for full architecture.

### AMP Deployment (DEPRECATED)
| Metric | Count |
|--------|-------|
| **Crews** | 3 (Intake, Validation, Decision) |
| **Agents** | 19 |
| **HITL Checkpoints** | 7 |

> **DEPRECATED**: Being replaced by Modal serverless. See [ADR-001](../adr/001-flow-to-crew-migration.md) (superseded) and [ADR-002](../adr/002-modal-serverless-migration.md).

**Pattern Hierarchy**: `PHASE → FLOW → CREW → AGENT → TASK`
**Critical Rule**: A crew must have 2+ agents (per CrewAI docs)

---

## 🔧 Tool Architecture (Audit: 2026-01-12)

**Status**: ⚠️ PARTIAL - Many tools are stubs or missing external connections
**Implementation**: BaseTool pattern (MCP server was planned but not built)
**Tests**: 681 passing (but tests don't verify external API connections)
**Documentation**: `docs/master-architecture/reference/tool-specifications.md`

### Architecture Reality (vs. Plan)

The MCP server architecture was **planned but not implemented**. Current state:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Modal Serverless                             │
├─────────────────────────────────────────────────────────────────────┤
│  CrewAI Agents with BaseTool pattern                                │
│                                                                      │
│  WORKING:                          STUBS/BLOCKED:                   │
│  ├── TavilySearchTool ✅            ├── ForumSearchTool ❌           │
│  ├── LandingPageDeploymentTool ✅   ├── ReviewAnalysisTool ❌        │
│  ├── AnalyticsTool ✅               ├── SocialListeningTool ❌       │
│  ├── AnonymizerTool ✅              ├── TrendAnalysisTool ❌         │
│  ├── MethodologyCheckTool ✅        ├── TranscriptionTool ❌         │
│  ├── TestCardTool ✅                ├── AdPlatformTool ❌ (no APIs)  │
│  ├── LearningCardTool ✅            └── CalendarTool ❌ (fake slots) │
│  └── CanvasBuilderTool ✅                                            │
│                                                                      │
│  NOT BUILT:                                                          │
│  └── SurveyTool (methodology requires, never implemented)           │
└─────────────────────────────────────────────────────────────────────┘
```

### Tool Status Summary

| Category | Planned | Working | Stubs | Blocked | Missing |
|----------|---------|---------|-------|---------|---------|
| Research | 6 | 1 (Tavily) | 4 | 0 | 0 |
| Evidence Collection | 3 | 0 | 1 (Transcription) | 1 (Calendar) | 1 (Survey) |
| Ad Platform | 1 | 0 | 0 | 1 (no APIs) | 0 |
| Landing Pages | 2 | 2 | 0 | 0 | 0 |
| Analytics | 1 | 1 | 0 | 0 | 0 |
| Governance | 3 | 3 | 0 | 0 | 0 |
| VPC/Cards | 3 | 3 | 0 | 0 | 0 |
| **TOTAL** | **19** | **10** | **5** | **2** | **1** |

### Agent Configuration Pattern

Current agents use BaseTool pattern (MCP was planned but not implemented):

```python
from crewai import Agent, LLM
from src.shared.tools import TavilySearchTool, CanvasBuilderTool

@agent
def observation_agent(self) -> Agent:
    return Agent(
        config=self.agents_config["d2_observation_agent"],
        tools=[
            TavilySearchTool(),      # ✅ WORKING
            # ForumSearchTool(),     # ❌ STUB - not implemented
            # ReviewAnalysisTool(),  # ❌ STUB - not implemented
        ],
        reasoning=True,
        inject_date=True,
        max_iter=25,
        llm=LLM(model="openai/gpt-4o", temperature=0.3),
        verbose=True,
        allow_delegation=False,
    )
```

---

## 📋 Decision Log

### Decision: Remove D1 Interview Agent (2026-01-12)

**Context**: D1 (Interview Agent) in DiscoveryCrew produces hallucinated interview transcripts.

**Problem**:
- TranscriptionTool is a stub (no Whisper API implementation)
- CalendarTool generates fake time slots (no real calendar integration)
- Agent output is pure LLM roleplay, not real customer interviews
- Creates false confidence in "customer evidence" that doesn't exist

**Decision**: **REMOVE D1 Interview Agent from Phase 1**

**Rationale**:
1. Interviews require scheduling real humans - not feasible for automated validation
2. Surveys are more appropriate for automated SAY evidence collection
3. Simulated interviews provide negative value (false confidence)
4. VPD methodology supports surveys as valid SAY evidence source

**Migration**:
1. Remove D1 agent from DiscoveryCrew
2. Add SurveyTool (Tally integration) for SAY evidence
3. Update Phase 1 flow to use survey distribution instead of interview scheduling
4. Adjust agent count: Phase 1 goes from 18 to 17 agents

**Impact**: DiscoveryCrew reduces from 5 agents to 4 agents.

### Decision: SurveyTool Integration - Tally (2026-01-12)

**Context**: VPD methodology requires surveys for quantitative SAY evidence. No survey tool exists.

**Options Evaluated**:

| Tool | Free Tier | API | Verdict |
|------|-----------|-----|---------|
| **Tally** | Unlimited forms, submissions | Yes + Webhooks | ✅ SELECTED |
| Typeform | 10 responses/month | Yes | Too limited |
| Google Forms | Unlimited | Via Zapier only | Backup option |

**Decision**: Integrate **Tally** via their API/webhooks

**Rationale**:
1. Free unlimited submissions (critical for validation experiments)
2. Native API and webhook support (no middleware needed)
3. Good respondent UX (modern, mobile-friendly)
4. No per-response pricing model

**Implementation**:
1. Create TallySurveyTool in `src/shared/tools/`
2. Wire to new survey agent (replaces D1)
3. Store survey responses in Supabase `survey_responses` table
4. Connect to CustomerProfileCrew for Jobs/Pains/Gains evidence

---

## Tool Implementation Backlog

### Must Fix (Blocking Production Quality)

| # | Tool | Effort | Priority | Notes |
|---|------|--------|----------|-------|
| 1 | SurveyTool (Tally) | 4-6h | P0 | New tool, replaces D1 interviews |
| 2 | AdPlatformTool | 8-16h | P0 | Requires ad account setup |
| 3 | F2 LandingPageGeneratorTool | 4h | P1 | Fix placeholder HTML output |

### Should Fix (Evidence Quality)

| # | Tool | Effort | Priority | Notes |
|---|------|--------|----------|-------|
| 4 | ForumSearchTool | 4h | P2 | Reddit API or scraping |
| 5 | ReviewAnalysisTool | 4h | P2 | App Store/Play Store APIs |
| 6 | SocialListeningTool | 4h | P2 | Twitter/X API or alternative |
| 7 | TrendAnalysisTool | 3h | P2 | Google Trends scraping |

### Can Remove (Not Essential)

| # | Tool | Decision | Notes |
|---|------|----------|-------|
| 8 | TranscriptionTool | REMOVE | D1 agent being removed |
| 9 | CalendarTool | REMOVE | D1 agent being removed |

**Reference Documents**:
- Tool specifications: `docs/master-architecture/reference/tool-specifications.md`
- Agent-to-tool mapping: `docs/master-architecture/reference/tool-mapping.md`

See `docs/work/cross-repo-blockers.md` for ecosystem impact.

---

## Architecture Implementation Status

### Modal Serverless (DEPLOYED - 2026-01-08)

**STATUS**: Infrastructure deployed, but **evidence quality is poor**. Many tools are stubs.

- **ADR**: See [ADR-002](../adr/002-modal-serverless-migration.md) (current)
- **Infrastructure**: Modal + Supabase + Netlify deployed to production ✅
- **Crews**: All 14 crews implemented with 45 agents ✅
- **Tools**: 10 of 19 tools actually work; 5 are stubs, 2 blocked, 1 missing
- **Tests**: 681 tests passing (but don't verify external API connections)
- **Benefits**: $0 idle costs, platform-agnostic, single repo
- **Gap**: Tool quality issues cause hallucinated evidence

### Implementation Summary (Honest Assessment)

| Component | Code | Evidence Quality | Notes |
|-----------|------|------------------|-------|
| Modal infrastructure | ✅ Complete | N/A | Production deployment live |
| Phase 0 (Onboarding) | ✅ Complete | ⚠️ LLM-only | No external validation |
| Phase 1 (VPC Discovery) | ✅ Complete | ⚠️ Partial | Only Tavily works; D1 hallucinated |
| Phase 2 (Desirability) | ✅ Complete | 🔴 Blocked | GrowthCrew blocked on AdPlatformTool |
| Phase 3 (Feasibility) | ✅ Complete | ⏳ Not tested | Blocked by Phase 2 |
| Phase 4 (Viability) | ✅ Complete | ⏳ Not tested | Blocked by Phase 2 |
| E2E Integration | 🔴 Blocked | - | Cannot complete until Phase 2 fixed |

### Previous: AMP Deployment (ARCHIVED)

- **ADR**: See [ADR-001](../adr/001-flow-to-crew-migration.md) (superseded by ADR-002)
- **Status**: Deprecated and archived
- **Code**: Archived to `archive/amp-deployment/`

The phases below reflect the canonical architecture (5 Flows, 14 Crews, 45 Agents).

---

## Phase 0 - AMP Deployment (COMPLETE)

Deploy the 3-Crew AMP workaround architecture to CrewAI AMP.

**Status**: DEPLOYED (2026-01-04)
**Crew 1 Enhanced**: 100% CrewAI Best Practices Alignment (2026-01-06)
**Architecture Aligned**: Canonical architecture documented (2026-01-07)

### Phase 0 Complete Criteria

**Repository Structure:**
- [x] Crew 1 (Intake) at repo root with `type = "crew"`
- [x] Crew 2 (Validation) code in `startupai-crews/crew-2-validation/`
- [x] Crew 3 (Decision) code in `startupai-crews/crew-3-decision/`
- [x] Crew 2 in separate GitHub repo (`chris00walker/startupai-crew-validation`)
- [x] Crew 3 in separate GitHub repo (`chris00walker/startupai-crew-decision`)

**Deployment:**
- [x] `crewai login` authenticated
- [x] Crew 1 deployed to AMP (UUID: `6b1e5c4d-e708-4921-be55-08fcb0d1e94b`)
- [x] Crew 2 deployed to AMP (UUID: `3135e285-c0e6-4451-b7b6-d4a061ac4437`)
- [x] Crew 3 deployed to AMP (UUID: `7da95dc8-7bb5-4c90-925b-2861fa9cba20`)
- [ ] Environment variables set in AMP dashboard for all crews (CREW_2_URL, CREW_3_URL, tokens)

**Crew Chaining:**
- [x] `InvokeCrewAIAutomationTool` configured for Crew 1 → Crew 2
- [x] `InvokeCrewAIAutomationTool` configured for Crew 2 → Crew 3
- [ ] End-to-end test: Intake → Validation → Decision (pending env var config)

**HITL Verification:**
- [ ] Crew 1 HITL (`approve_intake_to_validation`) works
- [ ] Crew 2 HITL (5 checkpoints) works
- [ ] Crew 3 HITL (`request_human_decision`) works

**Cross-Repo Unblocks:**
- Product App: Can call Crew 1 /kickoff endpoint
- Marketing: Real validation cycles possible

---

## Phase 0.6 - Architecture Alignment (IN PROGRESS)

Complete remaining items from architecture audit (2026-01-06).

**Status**: IN PROGRESS

### Documentation (COMPLETE)
- [x] `reference/api-contracts.md` - Phase 0-1 endpoints documented
- [x] `reference/database-schemas.md` - All schemas documented (including crew_execution_state)
- [x] `reference/tool-mapping.md` - Tool-to-agent assignments documented
- [x] `04-status.md` - Vercel AI SDK architecture correction reflected

### Database Migrations (PENDING)
Create and deploy migrations for Phase 0-1 tables:
- [ ] `founders_briefs` - Phase 0 Founder's Brief output
- [ ] `customer_profile_elements` - Jobs/Pains/Gains storage
- [ ] `value_map_elements` - Products/Pain Relievers/Gain Creators
- [ ] `vpc_fit_scores` - Fit score tracking
- [ ] `test_cards` - TBI experiment design
- [ ] `learning_cards` - TBI experiment results
- [ ] `crew_execution_state` - Cross-crew state persistence

### Tool Wiring (PENDING)
Wire archived tools to deployed crews (see `reference/tool-mapping.md` for details):

**Crew 2 (Validation):**
- [ ] `LandingPageGeneratorTool` → F2 (Frontend Developer)
- [ ] `LandingPageDeploymentTool` → F2 (Frontend Developer)
- [ ] `GuardianReviewTool` → G1 (QA Reviewer)
- [ ] `PrivacyGuardTool` → G2 (Security Analyst)
- [ ] `UnitEconomicsModelsTool` → L1 (Financial Controller)
- [ ] `BusinessModelClassifierTool` → L1 (Financial Controller)
- [ ] `BudgetGuardrailsTool` → L1 (Financial Controller)
- [ ] `CodeValidatorTool` → F3 (Backend Developer)

**Crew 3 (Decision):**
- [ ] `LearningCaptureTool` → C3 (Roadmap Writer)
- [ ] `LearningRetrievalTool` → C1 (Product PM)
- [ ] `AnonymizerTool` → C3 (Roadmap Writer)

### Cross-Repo Work (Product App - NOT THIS REPO)
Items identified in architecture audit that belong in `app.startupai.site`:
- Dead code removal (`/api/onboarding/message/route.ts`)
- V1 component archival (`OnboardingWizard.tsx`, `ConversationInterface.tsx`)
- Missing Drizzle schemas (12 tables)
- Frontend hooks (`useVPC`, `useCrewAIReport`, `useApprovals`, etc.)

---

## Phase 0.5 - Crew 1 CrewAI Best Practices Alignment (COMPLETE)

Achieve 100% alignment with CrewAI best practices for Crew 1 (Intake).

**Status**: COMPLETE (2026-01-06)
**Commit**: `327ce50`

### Improvements Implemented

**Pydantic Output Schemas:**
- [x] `src/intake_crew/schemas.py` created (397 lines)
- [x] 6 task output models: FounderBrief, CustomerResearchOutput, ValuePropositionCanvas, QAGateOutput, HumanApprovalInput, CrewInvocationResult
- [x] 6 enums: RiskLevel, PainSeverity, GainImportance, JobType, QAStatus, ApprovalDecision
- [x] `output_pydantic` wired to all 6 tasks in `crew.py`

**Tool Integration:**
- [x] `TavilySearchTool` wired to S2 (CustomerResearch)
- [x] `CustomerResearchTool` wired to S2 (CustomerResearch)
- [x] `MethodologyCheckTool` migrated and wired to G1 (QA)
- [x] Tools exported in `src/intake_crew/tools/__init__.py`

**Agent Enhancements:**
- [x] Reasoning enabled for S2 and G1 agents (`reasoning=True`)
- [x] All 4 agent backstories enriched with expertise depth
- [x] Task expected_outputs aligned with Pydantic schema fields

**Testing:**
- [x] `tests/test_intake_schemas.py` created (517 lines, 28 tests)
- [x] All tests passing

**Documentation:**
- [x] `docs/master-architecture/04-status.md` updated
- [x] `docs/master-architecture/reference/crew1-output-schemas.md` created
- [x] `docs/3-crew-deployment.md` tools section added

---

## Phase 1 - VPC Discovery + Desirability (Canonical: VPCDiscoveryFlow + DesirabilityFlow)

**Canonical Architecture** (per `docs/master-architecture/`):
- **VPCDiscoveryFlow**: 5 Crews (DiscoveryCrew, CustomerProfileCrew, ValueDesignCrew, WTPCrew, FitAssessmentCrew) - 18 agents
- **DesirabilityFlow**: 3 Crews (BuildCrew, GrowthCrew, GovernanceCrew) - 9 agents

**AMP Deployment Mapping**:
- VPCDiscoveryFlow → Crew 1 (Intake) + partial Crew 2
- DesirabilityFlow → Crew 2 (Validation - desirability phase)
- GovernanceCrew → Distributed across all 3 AMP crews

### Phase 1 Complete Criteria
Phase 1 is **complete** when all of the following are true:

**Code Complete:**
- [x] `state_schemas.py` defines ValidationState with Innovation Physics signals
- [x] Canonical: 8 crews with 27 agents (Phase 1 VPC + Desirability)
- [x] Synthesis Crew complete with pivot decision logic
- [x] Phase 1 Flow orchestrates crews with `@listen` and `@router` decorators
- [x] `@persist()` decorators placed for state recovery (9 checkpoints)
- [x] `main.py` entry point created

**Innovation Physics Logic:**
- [x] State signals implemented (EvidenceStrength, CommitmentType, FeasibilityStatus, UnitEconomicsStatus, PivotRecommendation)
- [x] Desirability Gate router (Problem-Solution + Product-Market filters)
- [x] Feasibility Gate router (Downgrade Protocol)
- [x] Viability Gate router (Unit Economics Trigger)
- [x] Human-in-the-loop integration points
- [x] Pivot history tracking for Flywheel

**Flywheel Learning (Phase 1):**
- [x] Supabase learning tables created (pgvector) - ✅ All tables deployed (learnings, patterns, outcomes, domain_expertise)
- [x] Anonymizer tool implemented
- [x] PrivacyGuard tool implemented (40 integration tests)
- [x] LearningCaptureTool implemented
- [x] LearningRetrievalTool implemented
- [x] Learning capture integrated into Phase 1 Flow

**Database Migrations (All Deployed 2025-11-27):**
- [x] flow_executions table (001)
- [x] validation_events table (002)
- [x] experiment_outcomes table (004) - Area 3 policy versioning
- [x] policy_version column on learnings (005)
- [x] decision_log table (006) - Area 6 budget guardrails

**Integration Complete:**
- [x] Deployed to CrewAI AMP and accessible via `/kickoff`
- [x] Results persist to Supabase via webhook
- [x] Learnings persist to Supabase (learnings, patterns, outcomes tables) - ✅ Tables deployed
- [x] Product app can poll status via `/status/{id}`
- [x] Product app has webhook receiver at `/api/crewai/webhook`
- [ ] Product app can retrieve and display results
- [ ] **PRODUCT APP CALLS founder_validation FLOW** ❌ NOT WIRED

### ⚠️ CRITICAL INTEGRATION GAP

**Status:** Backend founder_validation flow is fully implemented and deployed, but the product app does NOT call it.

**Current Behavior:**
- Product app (`/frontend/src/app/api/onboarding/complete/route.ts:619-672`) calls a generic `$CREWAI_API_URL` endpoint
- No `flow_type: 'founder_validation'` parameter passed
- Falls back to `generateStrategicAnalysis()` mock data if CrewAI call fails
- Users see mock recommendations, not actual AI validation

**What Needs to Happen:**
1. Product app must extract `entrepreneur_input` from onboarding brief
2. Product app must call `POST /kickoff` with:
   - `flow_type: "founder_validation"` ← **MISSING**
   - `entrepreneur_input: "..."`
   - `project_id: UUID`
   - `user_id: UUID`
   - `session_id: UUID`
3. Product app must store `kickoff_id` from response
4. Product app must poll `GET /status/{kickoff_id}` until completion
5. Product app must display results from `crewai_validation_states` table

**Blocked By:** Product App team - needs to implement flow_type routing in `/onboarding/complete` route

**Unblocks:** Real founder validation results for users (currently returns mock data)

**Validation Complete:**
- [ ] Tested with StartupAI's own business context
- [ ] Output quality reviewed by team
- [ ] QA Agent passes all checks
- [ ] Anonymization verified (no PII in learnings)

**Handoff Ready:**
- [ ] Product app updates `/onboarding/complete` to call founder_validation flow (see CRITICAL INTEGRATION GAP above)
- [ ] Product app receives and stores results from webhook
- [ ] Product app displays validation results from `crewai_validation_states` table
- [ ] Documentation updated in master-architecture/ with actual integration status

**Cross-Repo Unblocks:**
- Product App: Phase Alpha results display
- Marketing: First validation cycles (Phase 4)

### Phase 1 Honest Assessment (2025-11-26)

**What Phase 1 Actually Delivers:**
- ✅ Flow orchestration with non-linear routing (3 gated phases)
- ✅ State management with 70 fields and typed outputs
- ✅ All 8 crews callable via API with Pydantic output models
- ✅ CrewAI AMP deployment live and responding
- ⚠️ All crew outputs are LLM-generated (synthetic data, not real analysis)

**What Phase 1 Does NOT Deliver:**
- ⚠️ Real market research - TavilySearchTool exists but outputs may still be synthetic
- ⚠️ Real competitor analysis - CompetitorResearchTool exists with Tavily integration
- ⚠️ Real financial modeling - UnitEconomicsCalculatorTool + IndustryBenchmarkTool exist
- ❌ Real experiments (no ad platform integration - Meta/Google APIs not connected)
- ⚠️ MVP code generation - LandingPageGeneratorTool + CodeValidatorTool exist, full MVP scaffold not yet
- ✅ Results persistence to Supabase - webhook implemented in `_persist_to_supabase()`

**Marketing vs Reality Gap:**

| Marketing Promise | Phase 1 Reality |
|-------------------|-----------------|
| "Build your MVP" | LandingPageGeneratorTool + Netlify deployment exist; full app scaffold pending |
| "Real ad spend ($450-525)" | No ad platform APIs integrated (Meta/Google) |
| "Test with real users" | No analytics or experiment framework |
| "Unit economics analysis" | ✅ 10 business model-specific UnitEconomicsModels with industry benchmarks |
| "2-week validation cycles" | Flow runs in minutes; tools exist but validation quality TBD |

**Capabilities Required for Marketing Parity:**
1. MVP Generation - ✅ Landing pages exist; full app scaffolding pending
2. Ad Platform Integration - ❌ Meta Business API, Google Ads API not connected
3. Analytics Integration - ⚠️ PolicyBandit + offline evaluation exist; ad platform analytics pending
4. Financial Modeling - ✅ 10 business model-specific UnitEconomicsModels with industry benchmarks
5. Web Research Tools - ✅ TavilySearchTool + 4 research tools implemented
6. Results Persistence - ✅ Webhook to Supabase implemented
7. Budget Guardrails - ✅ BudgetGuardrails with hard/soft enforcement (Area 6)
8. Policy Versioning - ✅ PolicyBandit with UCB algorithm for A/B testing (Area 3)

---

## Architectural Improvements Complete (2025-11-27)

All 8 architectural improvements from `docs/drafts/eight-areas-of-improvement.md` are now **100% complete**:

| Area | Status | Key Deliverables |
|------|--------|------------------|
| 1. Tight Contracts | ✅ 100% | ToolResult envelope, typed crew outputs |
| 2. State Management | ✅ 100% | StateRepository, ValidationEvent, @persist() |
| 3. Policy Versioning | ✅ 100% | PolicyBandit (UCB), ExperimentConfigResolver, offline eval |
| 4. Observability | ✅ 90% | StructuredLogger, EventType enum (dashboards pending) |
| 5. Creative Learning | ✅ 80% | hook_type, tone fields on AdVariant |
| 6. HITL & Guardrails | ✅ 100% | BudgetGuardrails, DecisionLogger, resume_handler |
| 7. Business Model Viability | ✅ 100% | BusinessModelClassifier, 10 UnitEconomicsModels |
| 8. Developer Experience | ✅ 95% | Makefile, scripts/, 150+ tests |

See `docs/IMPLEMENTATION_ANALYSIS.md` for detailed evidence.

---

## Phase 2 - Feasibility (Canonical: FeasibilityFlow)

**Canonical Architecture** (per `docs/master-architecture/07-phase-3-feasibility.md`):
- **FeasibilityFlow**: 2 Crews (BuildCrew, GovernanceCrew) - 4 agents
- BuildCrew reused from Phase 1 (Desirability)

**AMP Deployment Mapping**:
- FeasibilityFlow → Crew 2 (Validation - feasibility phase)

### Phase 2 Complete Criteria
Phase 2 is **complete** when all of the following are true:

**Code Complete:**
- [x] BuildCrew functional with 3 agents (Tech Architect F1, Prototype Designer F2, Launch Planner F3)
- [x] GovernanceCrew functional with 3 agents (QA Specialist G1, Risk Assessor G2, Ethics Guardian G3)
- [x] Canonical: 2 crews, 4 agents for feasibility gate
- [x] Pivot/proceed router logic implemented (Innovation Physics routers)
- [x] Evidence synthesis aggregates across experiments

**Flywheel Learning (Phase 2):**
- [x] LearningRetrievalTool integrated into Governance Crew
- [x] Experiment pattern capture via LearningCaptureTool
- [x] Outcome tracking via OutcomeTrackerTool
- [x] Guardian data leakage checks via PrivacyGuardTool (40 tests)

**Integration Complete:**
- [x] Build artifacts deployable (LandingPageDeploymentTool → Netlify)
- [ ] Growth experiments trackable with metrics (no ad platform APIs)
- [x] Evidence persists to Supabase via webhook
- [x] Experiment learnings captured via _capture_flywheel_learnings()

**Validation Complete:**
- [ ] End-to-end test cycle with real experiment
- [ ] Pivot/proceed recommendation generated
- [ ] Evidence synthesis reviewed by team
- [ ] Retrieval quality metrics meet targets (>70% useful)

**Cross-Repo Unblocks:**
- Product App: Evidence UI, experiment tracking
- Marketing: Demo of full desirability validation cycle

---

## Phase 3 - Viability + Decision (Canonical: ViabilityFlow)

**Canonical Architecture** (per `docs/master-architecture/08-phase-4-viability.md`):
- **ViabilityFlow**: 3 Crews (FinanceCrew, SynthesisCrew, GovernanceCrew) - 9 agents
- Final decision: Pivot/Proceed/Pause

**AMP Deployment Mapping**:
- ViabilityFlow → Crew 2 (Validation - viability phase) + Crew 3 (Decision)

### Phase 3 Complete Criteria
Phase 3 is **complete** when all of the following are true:

**Code Complete:**
- [x] FinanceCrew functional with 3 agents (Financial Modeler L1, Viability Analyst L2, Compliance Monitor L3)
- [x] SynthesisCrew functional with 3 agents (Evidence Synthesizer C1, Insight Connector C2, Pivot Advisor C3)
- [x] GovernanceCrew functional with 3 agents (reused)
- [x] Full 3-gate validation flow (Desirability → Feasibility → Viability)

**Flywheel Learning (Phase 3):**
- [x] Outcome feedback loop implemented (OutcomeTrackerTool)
- [x] Domain expertise capture via FlywheelInsightsTool
- [x] Privacy audit by Guardian via PrivacyGuardTool
- [ ] Retrieval optimization (founder-specific patterns tuned)
- [ ] Learning quality metrics dashboard

**Integration Complete:**
- [x] Viability metrics calculated via ViabilityApprovalTool
- [x] Audit trail via ValidationEvent persistence
- [x] Flywheel system tools operational (capture, retrieval, insights)
- [ ] Cross-validation learning queries performant (needs Supabase tables)

**Validation Complete:**
- [ ] Full validation cycle with all 3 gates
- [ ] Unit economics calculated for StartupAI
- [ ] Outcome tracking shows prediction accuracy >60%
- [ ] Learning database growing with each validation

**Cross-Repo Unblocks:**
- Product App: Full dashboard with all 3 gates
- Marketing: Case study with complete validation cycle

---

## Implementation Status: Modal Serverless

The Modal serverless architecture is **DEPLOYED** and live testing is **IN PROGRESS**.

### Current State (Modal - PRODUCTION)
- Single modular monolith repo
- 5 Flows implemented as Modal functions
- 14 Crews with 45 agents total
- 10 HITL checkpoints with checkpoint-and-resume pattern
- Supabase for state persistence + Realtime for UI updates
- **185 unit tests passing**
- **Live testing: Phase 0-2 validated** (2026-01-09)

### Migration Tasks

See [ADR-002](../adr/002-modal-serverless-migration.md) for architecture details.

| Phase | Task | Status |
|-------|------|--------|
| 1 | Infrastructure (Modal account, Supabase tables) | ✅ Complete |
| 2 | Code migration (modal_app/, crews/) | ✅ Complete |
| 3 | Unit testing (185 tests) | ✅ Complete |
| 4 | E2E integration testing (mocked) | ✅ Complete (17 tests) |
| 5 | **Live testing with real LLM calls** | 🔄 In Progress |
| 6 | Production cutover | ⏳ Pending |

### Live Testing Progress (Updated 2026-01-12)

> **Quality Audit**: While flows execute, evidence quality is poor. Many outputs are hallucinated.
> **Run ID**: `52fe3efa-59b6-4c28-9f82-abd1d0d55b4b`

> **Details**: See [modal-live-testing.md](./modal-live-testing.md) for execution logs.

| Phase | Execution | Evidence Quality | Blockers |
|-------|-----------|------------------|----------|
| Phase 0 (Onboarding) | ✅ Runs | ⚠️ LLM-only | No external validation |
| Phase 1 (VPC Discovery) | ✅ Runs | ⚠️ Partial | D1 hallucinated, 4 tools are stubs |
| Phase 2 (Desirability) | ✅ Runs | 🔴 Blocked | GrowthCrew cannot run (no ad APIs) |
| Phase 3 (Feasibility) | ⏳ Not tested | - | Blocked by Phase 2 quality |
| Phase 4 (Viability) | ⏳ Not tested | - | Blocked by Phase 2 quality |

**Key Finding (2026-01-12)**: Flows execute successfully but produce hallucinated evidence:
- D1 "interviews" are LLM roleplay (no real customers)
- D2 "forum/review evidence" is fabricated (tools are stubs)
- P1/P2/P3 "ad campaigns" never created (no ad platform APIs)
- Phase 2 desirability signal is meaningless without real ad experiments

**Previous Bug Fixes (2026-01-10)**:
- #7: `JobType` enum missing `supporting` - `359abd2`
- #8: `GainRelevance` enum missing `expected` - `359abd2`
- #9: HITL duplicate key on pivot - Fixed
- #10: AnalyticsTool expected string, LLM passed dict - `623322a`
- #11: Segment alternatives returned `[]` on error - `623322a`
- #12: DesirabilityEvidence JSON parsing crashed - `623322a`

**Infrastructure (Working)**:
- Modal deployment: ✅ Production live
- Container timeout: 7200s (2 hours)
- RLS security: Enabled on all tables
- Supabase Realtime: Working

### Legacy (AMP - ARCHIVED)
- 3 Crews: Intake (4 agents), Validation (12 agents), Decision (3 agents)
- **Status**: Deprecated and archived
- **Issues**: Platform reliability problems, multi-repo complexity

**Reference**: See `docs/master-architecture/` for canonical architecture specifications.

---

## Phase E: Schema Alignment

> **Discovered**: 2026-01-10 - Cross-repo analysis revealed Modal tables not deployed
> **Status**: ✅ P0 COMPLETE - Modal migrations deployed to Supabase
> **Documentation**: See [data-flow.md](../master-architecture/reference/data-flow.md) for complete analysis

### Problem Statement (RESOLVED)

The `persistence.py` layer writes to Supabase tables that now exist:
- `validation_runs` - Checkpoint state (✅ DEPLOYED)
- `validation_progress` - Realtime progress (✅ DEPLOYED)
- `hitl_requests` - HITL queue (✅ DEPLOYED)

### Migration Status

#### P0: Modal Serverless (✅ DEPLOYED - 2026-01-10)

| Table | Migration | Status |
|-------|-----------|--------|
| `validation_runs` | `20260110130048_modal_validation_runs` | ✅ Deployed |
| `validation_progress` | `20260110130106_modal_validation_progress` | ✅ Deployed |
| `hitl_requests` | `20260110130129_modal_hitl_requests` | ✅ Deployed |

Deployed to Supabase via MCP on 2026-01-10.

#### P1: VPD-Aligned Founder's Brief

| Table | Purpose | Status |
|-------|---------|--------|
| `founders_briefs` | VPD-aligned Phase 0 output | ⏳ Planned |

The existing `entrepreneur_briefs` table has flat structure that doesn't match the nested `FoundersBrief` Pydantic model.

#### P2: VPC Tables

| Table | Purpose | Status |
|-------|---------|--------|
| `customer_profile_elements` | VPC Jobs/Pains/Gains | ⏳ Planned |
| `value_map_elements` | VPC Products/Relievers/Creators | ⏳ Planned |
| `vpc_fit_scores` | Fit score tracking | ⏳ Planned |

#### P3: TBI Framework

| Table | Purpose | Status |
|-------|---------|--------|
| `test_cards` | Experiment design | ⏳ Planned |
| `learning_cards` | Experiment results | ⏳ Planned |

### Completion Criteria

- [x] P0 migrations created (3 Modal tables)
- [x] Data flow documentation created
- [x] `database-schemas.md` updated with status matrix
- [x] `cross-repo-blockers.md` corrected
- [x] P0 migrations deployed to Supabase (2026-01-10)
- [ ] P1-P3 migrations created and deployed
