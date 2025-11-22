---
purpose: "Private technical source of truth for current engineering phases"
status: "active"
last_reviewed: "2025-11-21"
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
- [ ] `state_schemas.py` defines ValidationState, ClientBrief, CustomerProfile, CompetitorReport
- [ ] Service Crew functional with 3 agents (Customer Service, Founder Onboarding, Consultant Onboarding)
- [ ] Analysis Crew functional with 2 agents (Customer Researcher, Competitor Analyst)
- [ ] Governance Crew (Phase 1) functional with QA Agent
- [ ] Phase 1 Flow orchestrates crews with `@listen` and `@router` decorators
- [ ] `@persist()` decorators placed for state recovery

**Flywheel Learning (Phase 1):**
- [ ] Supabase learning tables created (pgvector)
- [ ] Anonymizer tool implemented
- [ ] PrivacyGuard tool implemented
- [ ] LearningCaptureTool implemented
- [ ] LearningRetrievalTool implemented
- [ ] Learning capture integrated into Phase 1 Flow

**Integration Complete:**
- [ ] Deployed to CrewAI AMP and accessible via `/kickoff`
- [ ] Results persist to Supabase (entrepreneur_briefs, analysis_results tables)
- [ ] Learnings persist to Supabase (learnings, patterns, outcomes tables)
- [ ] Product app can poll status and retrieve results

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
