---
purpose: "Private technical source of truth for current engineering phases"
status: "active"
last_reviewed: "2026-01-10 18:07"
last_audit: "2026-01-10 - Bug #9 verified via StartupAI dogfood run"
---

# Engineering Phases

> **Bug #9 Verified (2026-01-10 18:07)**: StartupAI dogfood run completed Phase 0-2 with pivot. All critical fixes working. Phase 3-4 pending.

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

## 🚀 Tool Architecture (Phases A-D Complete)

**Status**: ✅ CODE COMPLETE (2026-01-10) - Modal redeploy pending
**Implementation**: BaseTool pattern (simpler than planned MCP server)
**Tests**: 681 passing (164 new tool tests)
**Documentation**: `docs/master-architecture/reference/tool-specifications.md`

### Architecture Overview

StartupAI adopts MCP (Model Context Protocol) as the unified tool interface - the equivalent of OpenRouter for LLMs but for tools.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Modal Serverless                             │
├─────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  StartupAI Custom MCP Server (FastMCP + stateless HTTP)    │    │
│  │  Deployed: modal deploy src/mcp_server/app.py              │    │
│  │                                                             │    │
│  │  10 Custom Tools: forum_search, analyze_reviews,           │    │
│  │  social_listen, analyze_trends, transcribe_audio,          │    │
│  │  extract_insights, identify_patterns, run_ab_test,         │    │
│  │  get_analytics, anonymize_data                             │    │
│  └────────────────────────────────────────────────────────────┘    │
│                              │                                       │
│  ┌───────────────────────────┴───────────────────────────────┐     │
│  │              CrewAI Agents (MCP Clients)                   │     │
│  └───────────────────────────────────────────────────────────┘     │
│                              │                                       │
├──────────────────────────────┼───────────────────────────────────────┤
│  External MCP Servers        │                                       │
│  ┌──────────┐ ┌──────────┐ ┌┴─────────┐ ┌──────────┐               │
│  │ Meta Ads │ │Google Ads│ │ Calendar │ │   Fetch  │               │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘               │
└─────────────────────────────────────────────────────────────────────┘
```

### Tool Categories

| Category | Count | Description |
|----------|-------|-------------|
| **EXISTS** | 13 | Implemented and ready to wire |
| **MCP External** | 4 | Use existing MCP servers (Meta Ads, Google Ads, Calendar, Fetch) |
| **MCP Custom** | 10 | Build as FastMCP tools on Modal |
| **LLM-Based** | 6 | Structured LLM output with Pydantic |
| **TOTAL** | 33 | All tools across 45 agents |

### Agent Configuration Pattern

All 45 agents will follow the IntakeCrew pattern with MCP tools:

```python
from mcp_use import MCPClient
from crewai import Agent, LLM

# Connect to StartupAI MCP server
mcp_client = MCPClient(
    url="https://chris00walker--startupai-mcp-tools.modal.run/mcp/",
    transport="streamable-http"
)
mcp_tools = mcp_client.get_tools()

@agent
def observation_agent(self) -> Agent:
    return Agent(
        config=self.agents_config["d2_observation_agent"],
        tools=[
            TavilySearchTool(),   # EXISTS (direct import)
            *mcp_tools,           # MCP Custom (from Modal server)
        ],
        reasoning=True,
        inject_date=True,
        max_iter=25,
        llm=LLM(model="openai/gpt-4o", temperature=0.3),
        verbose=True,
        allow_delegation=False,
    )
```

### Implementation Phases

See `docs/master-architecture/reference/tool-mapping.md` for detailed roadmap.

#### Phase A: Core MCP Server (Week 1) - 15 hours

| Task | MCP Tool Name | Target Agents | Effort |
|------|---------------|---------------|--------|
| Create FastMCP server on Modal | - | All | 4h |
| Implement `forum_search` | ForumScraperTool | D2, J1, PAIN_RES, GAIN_RES | 3h |
| Implement `analyze_reviews` | ReviewAnalysisTool | D2, J1, PAIN_RES, GAIN_RES | 3h |
| Implement `social_listen` | SocialListeningTool | D2 | 2h |
| Implement `analyze_trends` | TrendAnalysisTool | D2 | 2h |
| Deploy to Modal | - | - | 1h |

**Deliverable**: Research agents can gather real customer insights from Reddit, app stores, and web.

#### Phase B: Advanced Tools (Week 2) - 14 hours

| Task | MCP Tool Name | Target Agents | Effort |
|------|---------------|---------------|--------|
| Implement `transcribe_audio` | TranscriptionTool | D1 | 3h |
| Implement `extract_insights` | InsightExtractorTool | D1, D4 | 4h |
| Implement `identify_patterns` | BehaviorPatternTool | D2, D3 | 4h |
| Implement `run_ab_test` | ABTestTool | P1, P2, W1 | 3h |

**Deliverable**: Interview transcription and pattern recognition operational.

#### Phase C: External MCP + Analytics (Week 3) - 13 hours

| Task | Implementation | Target Agents | Effort |
|------|----------------|---------------|--------|
| Implement `get_analytics` | MCP Custom | P3, D3, L1, W1, W2 | 3h |
| Implement `anonymize_data` | MCP Custom (Presidio) | Learning pipeline | 2h |
| Connect Meta Ads MCP | External server | P1, P2, P3, D3 | 2h |
| Connect Google Ads MCP | External server | P1, P2, P3 | 2h |
| Connect Calendar MCP | External server | D1 | 2h |
| Integration testing | - | All | 4h |

**Deliverable**: Ad platforms and analytics connected via MCP.

#### Phase D: CrewAI Integration (Week 4) - 18 hours

| Task | Implementation | Target Agents | Effort |
|------|----------------|---------------|--------|
| Wire EXISTS tools to agents | Direct import | All phases | 4h |
| Add MCP client to agents | mcp_use library | All phases | 4h |
| Build LLM-Based tools | Structured output | O1, E1, V1-V3, C2 | 4h |
| End-to-end testing | Full pipeline | All | 4h |
| Documentation | Agent configs | - | 2h |

**Deliverable**: All 45 agents fully equipped with evidence-based tools.

### Cost Summary

| Category | Monthly Cost |
|----------|--------------|
| Modal MCP server compute | ~$5-10 |
| External MCP servers | $0 |
| HuggingFace (on Modal) | $0 |
| Free-tier APIs | $0 |
| **TOTAL ADDITIONAL** | **~$5-10** |

**Reference Documents**:
- Tool specifications: `docs/master-architecture/reference/tool-specifications.md`
- Agent-to-tool mapping: `docs/master-architecture/reference/tool-mapping.md`
- Tool lifecycle: `docs/master-architecture/reference/agentic-tool-framework.md`

See `docs/work/cross-repo-blockers.md` for ecosystem impact.

---

## Architecture Implementation Status

### Modal Serverless (DEPLOYED - 2026-01-08)

**STATUS**: Infrastructure deployed, crews implemented, tools wired. **MODAL REDEPLOY + LIVE TESTING PENDING.**

- **ADR**: See [ADR-002](../adr/002-modal-serverless-migration.md) (current)
- **Infrastructure**: Modal + Supabase + Netlify deployed to production
- **Crews**: All 14 crews implemented with 45 agents
- **Tools**: 15 tools wired to 35+ agents (Phases A-D complete 2026-01-10)
- **Tests**: 681 tests passing (164 new tool tests)
- **Benefits**: $0 idle costs, platform-agnostic, single repo
- **Gap**: Deployed Modal code predates tool integration; needs redeploy

### Implementation Summary

| Component | Status | Details |
|-----------|--------|---------|
| Modal infrastructure | ✅ Complete | Production deployment live |
| Phase 0 (Onboarding) | ✅ Complete | 1 crew, 4 agents, 24 tests |
| Phase 1 (VPC Discovery) | ✅ Complete | 5 crews, 18 agents, 25 tests |
| Phase 2 (Desirability) | ✅ Complete | 3 crews, 9 agents, 42 tests |
| Phase 3 (Feasibility) | ✅ Complete | 2 crews, 5 agents, 36 tests |
| Phase 4 (Viability) | ✅ Complete | 3 crews, 9 agents, 58 tests |
| E2E Integration | ⏳ Pending | Ready to test |

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

### Live Testing Progress (2026-01-10) - WITH TOOLS

> **Session 2**: Modal redeployed with tool-wired code. Enum bugs found and fixed.
> **Run ID**: `52fe3efa-59b6-4c28-9f82-abd1d0d55b4b`

> **Details**: See [modal-live-testing.md](./modal-live-testing.md) for full learnings.

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 0 (Onboarding) | ✅ PASSED | Founder's Brief generated |
| Phase 1 (VPC Discovery) | ✅ PASSED | Fixed enum bugs (#7, #8), fit score 78/100 |
| Phase 2 (Desirability) | ✅ PASSED | NO_INTEREST signal → Segment pivot |
| Phase 1 (Pivot) | ✅ PASSED | New segment: Healthcare Online Platforms |
| Phase 2 (Retry) | 🔄 Running | Fixed #10-12, BuildCrew executing |
| Phase 3 (Feasibility) | ⏳ Pending | - |
| Phase 4 (Viability) | ⏳ Pending | - |

**Session 2 Progress**:
1. ~~Modal redeploy~~ - ✅ Completed (2026-01-10)
2. ~~Phase 0 revalidation~~ - ✅ Passed (no issues)
3. ~~Phase 1 revalidation~~ - ✅ Passed (enum bugs fixed)
4. ~~Phase 2 revalidation~~ - ✅ Passed (pivot tested)
5. ~~Bug fixes deployed~~ - ✅ Completed (2026-01-10 15:08)
6. **Phase 2 retry** - 🔄 In progress (BuildCrew executing)
7. Phase 3-4 revalidation - ⏳ Pending
8. Production cutover verification - ⏳ Pending

**Bugs Found & Fixed**:
- #7: `JobType` enum missing `supporting` (VPD has 4 job types) - `359abd2`
- #8: `GainRelevance` enum missing `expected` (VPD Kano model has 4 levels) - `359abd2`
- #9: HITL duplicate key on pivot - Expire pending HITLs before insert - ✅ Fixed
- #10: AnalyticsTool expected string, LLM passed dict - Added args_schema - `623322a`
- #11: Segment alternatives returned `[]` on error - Added fallback + logging - `623322a`
- #12: DesirabilityEvidence JSON parsing crashed - Added try/catch - `623322a`

**Additional Fixes (2026-01-10)**:
- Phase 2 tool integration gap: F1, F2, F3, G3 now have tools wired (100% coverage)
- Container timeout: Increased from 3600s to 7200s (2 hours)
- RLS security: Verified enabled on all Modal tables

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
