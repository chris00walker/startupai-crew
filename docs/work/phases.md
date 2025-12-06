---
purpose: "Private technical source of truth for current engineering phases"
status: "active"
last_reviewed: "2025-12-05"
last_audit: "2025-12-05 - Architecture migrated from Flow to 3-Crew"
---

# Engineering Phases

## Architecture Migration Notice (2025-12-05)

**MAJOR CHANGE**: The Flow-based architecture has been replaced with a 3-Crew architecture.

- **ADR**: See `docs/adr/001-flow-to-crew-migration.md`
- **Reason**: AMP platform has issues with `type = "flow"` projects
- **Old code**: Archived to `archive/flow-architecture/`

The phases below are being updated to reflect the new architecture.

---

## Phase 0 - 3-Crew Architecture Deployment (Active)

Deploy the 3-Crew architecture to CrewAI AMP.

### Phase 0 Complete Criteria

**Repository Structure:**
- [x] Crew 1 (Intake) at repo root with `type = "crew"`
- [x] Crew 2 (Validation) code in `startupai-crews/crew-2-validation/`
- [x] Crew 3 (Decision) code in `startupai-crews/crew-3-decision/`
- [ ] Crew 2 in separate GitHub repo
- [ ] Crew 3 in separate GitHub repo

**Deployment:**
- [ ] `crewai login` authenticated
- [ ] Crew 1 deployed to AMP
- [ ] Crew 2 deployed to AMP (separate repo)
- [ ] Crew 3 deployed to AMP (separate repo)
- [ ] Environment variables set in AMP dashboard for all crews

**Crew Chaining:**
- [ ] `InvokeCrewAIAutomationTool` configured for Crew 1 → Crew 2
- [ ] `InvokeCrewAIAutomationTool` configured for Crew 2 → Crew 3
- [ ] End-to-end test: Intake → Validation → Decision

**HITL Verification:**
- [ ] Crew 1 HITL (`approve_intake_to_validation`) works
- [ ] Crew 2 HITL (5 checkpoints) works
- [ ] Crew 3 HITL (`request_human_decision`) works

**Cross-Repo Unblocks:**
- Product App: Can call Crew 1 /kickoff endpoint
- Marketing: Real validation cycles possible

---

## Phase 1 - Service Side + Desirability Validation (Paused - Superseded)

**Note**: This phase used the Flow architecture which has been deprecated. The functionality is now distributed across the 3-Crew architecture.

**Mapping to 3-Crew:**
- Service Crew → Crew 1 (Intake)
- Analysis Crew → Crew 2 (Validation - desirability phase)
- Governance Crew → Distributed across all 3 crews

### Phase 1 Complete Criteria
Phase 1 is **complete** when all of the following are true:

**Code Complete:**
- [x] `state_schemas.py` defines ValidationState with Innovation Physics signals
- [x] All 8 crews implemented with 18 agents
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

## Phase 2 - Commercial Side + Build/Test (Queued)
- Build Crew, Growth Crew, Synthesis Crew
- Add pivot/proceed router logic
- Implement evidence synthesis
- Dependencies: Phase 1 completion

### Phase 2 Complete Criteria
Phase 2 is **complete** when all of the following are true:

**Code Complete:**
- [x] Build Crew functional with 3 agents (UX/UI Designer, Frontend Developer, Backend Developer)
- [x] Growth Crew functional with 3 agents (Ad Creative, Communications, Social Media Analyst)
- [x] Synthesis Crew functional with 1 agent (Project Manager)
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

## Phase 3 - Governance + Viability (Planned)
- Finance Crew
- Enhanced Governance Crew (Audit Agent, Security Agent)
- Flywheel learning capture
- Dependencies: Phase 2 completion

### Phase 3 Complete Criteria
Phase 3 is **complete** when all of the following are true:

**Code Complete:**
- [x] Finance Crew functional with 2 agents (Financial Controller, Legal & Compliance)
- [x] Enhanced Governance Crew with 3 agents (QA Auditor, Compliance Monitor, Accountability Tracker)
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

## Transition Plan

The current working 6-agent system will remain deployed during the Flows rebuild. The transition will occur when:

1. Phase 1 is complete and tested
2. Output quality matches or exceeds current system
3. Product app integration verified

At that point, the new Phase 1 Flow will replace the current deployment.
