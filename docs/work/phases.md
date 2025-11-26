---
purpose: "Private technical source of truth for current engineering phases"
status: "active"
last_reviewed: "2025-11-26"
---

# Engineering Phases

## Phase 1 - Service Side + Desirability Validation (Active)
- Create state schemas (`state_schemas.py`)
- Build Service Crew (agents.yaml, tasks.yaml, service_crew.py)
- Build Analysis Crew
- Build Governance Crew (Phase 1 - QA Agent only)
- Create Phase 1 Flow
- Test with StartupAI's own business context
- Owners: AI Platform (lead)

### Phase 1 Complete Criteria
Phase 1 is **complete** when all of the following are true:

**Code Complete:**
- [x] `state_schemas.py` defines ValidationState with Innovation Physics signals
- [x] All 7 crews implemented (stubs ready for LLM tools)
- [x] Synthesis Crew complete with pivot decision logic
- [x] Phase 1 Flow orchestrates crews with `@listen` and `@router` decorators
- [ ] `@persist()` decorators placed for state recovery
- [x] `main.py` entry point created

**Innovation Physics Logic:**
- [x] State signals implemented (EvidenceStrength, CommitmentType, FeasibilityStatus, UnitEconomicsStatus, PivotRecommendation)
- [x] Desirability Gate router (Problem-Solution + Product-Market filters)
- [x] Feasibility Gate router (Downgrade Protocol)
- [x] Viability Gate router (Unit Economics Trigger)
- [x] Human-in-the-loop integration points
- [x] Pivot history tracking for Flywheel

**Flywheel Learning (Phase 1):**
- [ ] Supabase learning tables created (pgvector)
- [x] Anonymizer tool implemented
- [ ] PrivacyGuard tool implemented
- [x] LearningCaptureTool implemented
- [x] LearningRetrievalTool implemented
- [x] Learning capture integrated into Phase 1 Flow

**Integration Complete:**
- [x] Deployed to CrewAI AMP and accessible via `/kickoff`
- [x] Results persist to Supabase via webhook
- [ ] Learnings persist to Supabase (learnings, patterns, outcomes tables)
- [x] Product app can poll status via `/status/{id}`
- [ ] Product app can retrieve and display results

**Validation Complete:**
- [ ] Tested with StartupAI's own business context
- [ ] Output quality reviewed by team
- [ ] QA Agent passes all checks
- [ ] Anonymization verified (no PII in learnings)

**Handoff Ready:**
- [ ] Product app unblocked for Phase Alpha results display
- [ ] Documentation updated in master-architecture/

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
- ❌ Real market research (crews generate plausible-sounding but fictional data)
- ❌ Real competitor analysis (no web search, no data sources)
- ❌ Real financial modeling (CAC/LTV numbers are hallucinated)
- ❌ Real experiments (no ad platform integration)
- ❌ MVP code generation (no build capability)
- ❌ Results persistence to Supabase

**Marketing vs Reality Gap:**

| Marketing Promise | Phase 1 Reality |
|-------------------|-----------------|
| "Build your MVP" | No code generation capability |
| "Real ad spend ($450-525)" | No ad platform APIs integrated |
| "Test with real users" | No analytics or experiment framework |
| "Unit economics analysis" | Finance Crew generates fictional numbers |
| "2-week validation cycles" | Flow runs in minutes, outputs are synthetic |

**Capabilities Required for Marketing Parity:**
1. MVP Generation - Code scaffolding, template deployment, GitHub integration
2. Ad Platform Integration - Meta Business API, Google Ads API
3. Analytics Integration - Real user tracking, conversion measurement
4. Financial Modeling - Connect to real cost/revenue data sources
5. Web Research Tools - Competitor research APIs, market data sources
6. Results Persistence - Store outputs to Supabase for frontend display

---

## Phase 2 - Commercial Side + Build/Test (Queued)
- Build Crew, Growth Crew, Synthesis Crew
- Add pivot/proceed router logic
- Implement evidence synthesis
- Dependencies: Phase 1 completion

### Phase 2 Complete Criteria
Phase 2 is **complete** when all of the following are true:

**Code Complete:**
- [ ] Build Crew functional with 3 agents (UX/UI Designer, Frontend Developer, Backend Developer)
- [ ] Growth Crew functional with 3 agents (Ad Creative, Communications, Social Media Analyst)
- [ ] Synthesis Crew functional with 1 agent (Project Manager)
- [ ] Pivot/proceed router logic implemented
- [ ] Evidence synthesis aggregates across experiments

**Flywheel Learning (Phase 2):**
- [ ] LearningRetrievalTool integrated into all agents
- [ ] Experiment pattern capture on completion
- [ ] Outcome tracking for pivot/proceed decisions
- [ ] Guardian data leakage checks active

**Integration Complete:**
- [ ] Build artifacts deployable (landing pages, prototypes)
- [ ] Growth experiments trackable with metrics
- [ ] Evidence persists to Supabase
- [ ] Experiment learnings captured automatically

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
- [ ] Finance Crew functional with 2 agents (Financial Controller, Legal & Compliance)
- [ ] Enhanced Governance Crew with 3 agents (Audit Agent, Security Agent, QA Agent)
- [ ] Full 3-gate validation flow (Desirability → Feasibility → Viability)

**Flywheel Learning (Phase 3):**
- [ ] Outcome feedback loop implemented (track actual vs predicted)
- [ ] Domain expertise capture for all industries served
- [ ] Periodic learning audit by Guardian
- [ ] Retrieval optimization (founder-specific patterns tuned)
- [ ] Learning quality metrics dashboard

**Integration Complete:**
- [ ] Viability metrics calculated and persisted
- [ ] Audit trail exportable for compliance
- [ ] Full flywheel system operational
- [ ] Cross-validation learning queries performant

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
