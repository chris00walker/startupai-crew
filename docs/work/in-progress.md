---
purpose: "Private technical source of truth for active work"
status: "active"
last_reviewed: "2025-11-26"
---

# In Progress

## Phase 2B: HITL Workflows - Viability Approval (Next)

Flow can pause for human viability decisions at the unit economics gate.

| Item | Status | Owner | Notes |
|------|--------|-------|-------|
| Add await_viability_decision flow node | Pending | @ai-platform | HITL pause at viability gate |
| Wire ViabilityApprovalTool to Finance | Pending | @ai-platform | Surface LTV/CAC for human review |
| Implement cost pivot decision handler | Pending | @ai-platform | Increase price vs reduce cost |
| Add viability approval tests | Pending | @ai-platform | test_viability_workflow.py |

### Phase 2B Complete Criteria

- [ ] Flow pauses when unit economics need human decision
- [ ] /resume payload processes viability decisions (proceed/pivot/kill)
- [ ] Finance Crew surfaces unit economics for review
- [ ] Cost optimization recommendations presented to user

---

## Phase 2A: HITL Workflows - Creative Approval (✅ Complete)

Flow can pause for human creative decisions.

| Item | Status | Owner | Notes |
|------|--------|-------|-------|
| Implement /resume webhook handler | ✅ Complete | @ai-platform | Parse creative approval payloads |
| Wire GuardianReviewTool to Governance | ✅ Complete | @ai-platform | Auto-QA creatives |
| Implement MethodologyCheckTool | ✅ Complete | @ai-platform | VPC/BMC structure validation |
| Add await_creative_approval flow node | ✅ Complete | @ai-platform | HITL pause point in flow |
| Add HITL workflow tests | ✅ Complete | @ai-platform | 32 tests passing |

### Phase 2A Complete Criteria

- [x] Flow pauses when Guardian flags issues requiring human review
- [x] /resume payload updates ad/LP approval statuses
- [x] GuardianReviewTool auto-approves safe creatives
- [x] MethodologyCheckTool validates VPC/BMC structure

---

## Phase 1B: Landing Page Deployment + Build Crew (✅ Complete)

Generated landing pages can be deployed for experiments.

| Item | Status | Owner | Notes |
|------|--------|-------|-------|
| Implement LandingPageDeploymentTool (Netlify) | ✅ Complete | @ai-platform | Netlify API integration |
| Wire Build Crew with full tool suite | ✅ Complete | @ai-platform | 3 tools wired to prototype_designer |
| Add deploy_landing_pages task | ✅ Complete | @ai-platform | Build Crew task |
| Add integration tests | ✅ Complete | @ai-platform | 17 tests passing |

### Phase 1B Complete Criteria

- [x] LandingPageDeploymentTool deploys HTML to Netlify subdomain
- [x] Build Crew generates + deploys landing pages end-to-end
- [x] CodeValidatorTool runs before deployment
- [x] Integration tests pass

---

## Phase 1A: Results Persistence + Tool Wiring (✅ Complete)

Closing the critical blocker - users can see validation results.

| Item | Status | Owner | Notes |
|------|--------|-------|-------|
| Wire TavilySearchTool to Analysis Crew | ✅ Complete | @ai-platform | Already implemented |
| Wire IndustryBenchmarkTool to Finance Crew | ✅ Complete | @ai-platform | Already implemented |
| Wire LearningCaptureTool to Governance Crew | ✅ Complete | @ai-platform | Added 2025-11-26 |
| Create crewai_config.yaml | ✅ Complete | @ai-platform | Webhooks + memory config |
| Results persistence to Supabase | ✅ Complete | @ai-platform | Already in flow |
| Update work tracking docs | ✅ Complete | @ai-platform | Updated 2025-11-26 |

### Phase 1A Complete Criteria

- [x] Flow completion calls webhook with structured results
- [x] Analysis Crew uses TavilySearchTool for real web research
- [x] Finance Crew uses IndustryBenchmarkTool for real benchmarks
- [x] Governance Crew captures learnings via LearningCaptureTool
- [x] crewai_config.yaml created with webhook URLs and memory config

---

## Phase 1 Core (Previously Completed)

| Item | Status | Notes |
|------|--------|-------|
| State schemas (`state_schemas.py`) | ✅ Complete | Innovation Physics signals + ValidationState + all models |
| Service Crew | ✅ Complete | Web search tools wired |
| Analysis Crew | ✅ Complete | TavilySearchTool + CustomerResearchTool wired |
| Build Crew | ✅ Complete | LandingPageGeneratorTool + CodeValidatorTool wired |
| Growth Crew | ✅ Complete | Stub (needs experiment tools in Phase 2B) |
| Synthesis Crew | ✅ Complete | Full task definitions with pivot logic |
| Finance Crew | ✅ Complete | IndustryBenchmarkTool + UnitEconomicsCalculatorTool wired |
| Governance Crew | ✅ Complete | LearningCaptureTool + AnonymizerTool + HITL tools wired |
| Phase 1 Flow orchestration | ✅ Complete | Non-linear routers with Innovation Physics |
| Results persistence | ✅ Complete | Webhook to product app on flow completion |

---

## Immediate Next Step

**Phase 2B: HITL Workflows - Viability Approval** - Enable human-in-the-loop for viability decisions.

See Phase 2B section above for task breakdown.

---

## What This Unblocks (Downstream)

**Phase 1A + 1B + 2A Complete unblocks:**
- **Product App**: Can display validation results from webhook
- **All Crews**: Real tools instead of LLM-only outputs
- **Growth Crew**: Can deploy landing pages for experiments
- **Marketing**: Real URLs for demos
- **Quality Assurance**: Human review before ad deployment
- **Compliance**: Review workflow for creative content

**Phase 2B Will unblock:**
- **Strategic Decisions**: Human approval at viability gate
- **Unit Economics**: Real LTV/CAC decisions with human oversight
- **Pivot Execution**: Cost/price optimization with human approval

---

## Documentation / Infrastructure

| Item | Status | Notes |
|------|--------|-------|
| Docs reorganization | ✅ Complete | See done.md |
| Work tracking sync | ✅ Complete | Updated 2025-11-26 |
| crewai_config.yaml | ✅ Complete | Webhooks + memory config |

---

## How to Use This Document

1. **Pick an item** from the Phase 2B table above
2. **Update status** when you start work
3. **Move to done.md** when complete
4. **Update phases.md** checkboxes to match

---
**Last Updated**: 2025-11-26

**Latest Changes**: Phase 2A completed - HITL creative approval workflow implemented with GuardianReviewTool, MethodologyCheckTool, /resume webhook handler, and await_creative_approval flow node. 32 integration tests passing. Phase 2B (HITL viability approval) is next.
