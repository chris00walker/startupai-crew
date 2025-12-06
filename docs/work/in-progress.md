---
purpose: "Private technical source of truth for active work"
status: "active"
last_reviewed: "2025-12-05"
---

# In Progress

## Architecture Change Notice (2025-12-05)

**MAJOR**: The Flow-based architecture has been replaced with a 3-Crew architecture.
- **ADR**: See `docs/adr/001-flow-to-crew-migration.md`
- **Reason**: AMP platform has issues with `type = "flow"` projects
- All previous Flow-related work is now archived

---

## Phase 0: 3-Crew AMP Deployment (Active)

Deploy the new 3-Crew architecture to CrewAI AMP.

### Current Status

| Item | Status | Notes |
|------|--------|-------|
| Crew 1 code | ✅ Complete | `src/intake_crew/` at repo root |
| Crew 2 code | ✅ Complete | `startupai-crews/crew-2-validation/` |
| Crew 3 code | ✅ Complete | `startupai-crews/crew-3-decision/` |
| pyproject.toml | ✅ Updated | `type = "crew"` |
| CrewAI login | ⚠️ Pending | Session expired, needs re-auth |
| Crew 1 deployment | ⚠️ Pending | Blocked on login |
| Crews 2 & 3 repos | ⚠️ Pending | Need separate GitHub repos |

### Next Steps

1. Run `crewai login` to authenticate
2. Run `crewai deploy push` for Crew 1
3. Create `startupai-crew-validation` repo for Crew 2
4. Create `startupai-crew-decision` repo for Crew 3
5. Configure `InvokeCrewAIAutomationTool` for crew chaining

### Architecture Summary

```
Crew 1: Intake (4 agents, 6 tasks, 1 HITL)
    ↓ InvokeCrewAIAutomationTool
Crew 2: Validation (12 agents, 21 tasks, 5 HITL)
    ↓ InvokeCrewAIAutomationTool
Crew 3: Decision (3 agents, 5 tasks, 1 HITL)
```

---

## E2E Flow Verification (Archived - Flow Architecture)

**Status**: Superseded by 3-Crew architecture.

The bugs fixed below were for the Flow architecture which is now archived. The new 3-Crew architecture will need its own testing once deployed.

### Bugs Fixed (2025-12-03)

| Bug | Status | File:Line | Notes |
|-----|--------|-----------|-------|
| Assumption schema mismatch | ✅ Fixed | `founder_validation_flow.py:110-168` | `crew_outputs.Assumption` → `state_schemas.Assumption` converter |
| AnalysisCrew missing template vars | ✅ Fixed | `founder_validation_flow.py:264-276` | Added placeholders for `iterate_value_proposition` task |
| GrowthCrew missing template vars | ✅ Fixed | `founder_validation_flow.py:344-372` | Added placeholders for all 4 tasks |
| pivot_value_proposition KeyError | ✅ Fixed | `founder_validation_flow.py:780-832` | Defensive checks + all template vars |
| refine_desirability_tests template vars | ✅ Fixed | `founder_validation_flow.py:839-862` | Added all GrowthCrew template placeholders |
| Netlify token name mismatch | ✅ Fixed | `landing_page_deploy.py:136,545` | Accept `NETLIFY_ACCESS_TOKEN` or `NETLIFY_AUTH_TOKEN` |
| CustomerProfile/ValueMap type mismatch | ✅ Fixed | `founder_validation_flow.py:173-248` | Type converters for crew→state models |

### Listener Errors (✅ Fixed)

**Root Cause**: Type mismatch between crew output models and state models:
- `AnalysisCustomerProfile` (crew) vs `CustomerProfile` (state)
- `AnalysisValueMap` (crew) vs `ValueMap` (state)

**Fix Applied**: Added two conversion functions in `founder_validation_flow.py:173-248`:
- `convert_analysis_profile_to_state()` - Converts crew jobs/pains/gains to state format
- `convert_analysis_value_map_to_state()` - Converts crew pain_relievers/gain_creators lists to dicts

These follow the same pattern as `convert_crew_assumption_to_state()` which fixed the Assumption schema mismatch.

### Environment Status

| Variable | Expected By | Status | Location |
|----------|-------------|--------|----------|
| OPENAI_API_KEY | All crews | ✅ Set | `~/.secrets/startupai` |
| NETLIFY_AUTH_TOKEN | landing_page_deploy.py | ✅ Set | Code now accepts both `ACCESS_TOKEN` and `AUTH_TOKEN` |
| TAVILY_API_KEY | web_search.py | ⚠️ Optional | Only needed for live web research (uses stub if missing) |
| STARTUPAI_WEBHOOK_URL | flow persistence | ⚠️ Optional | Webhook delivery skipped if not set |
| STARTUPAI_WEBHOOK_BEARER_TOKEN | flow persistence | ⚠️ Optional | Webhook auth skipped if not set |

### Test Results

- **Unit tests**: 178/178 passed
- **Live E2E flow**: Progresses through ServiceCrew → AnalysisCrew → GrowthCrew
- **Desirability testing**: Completes successfully
- **Listener callbacks**: Errors after desirability phase (non-blocking)

### Next Steps

1. Add missing env vars to `~/.secrets/startupai`:
   - `NETLIFY_ACCESS_TOKEN` (alias for existing `NETLIFY_AUTH_TOKEN`)
   - `TAVILY_API_KEY` (for web research tools)
   - `STARTUPAI_WEBHOOK_URL` and `STARTUPAI_WEBHOOK_BEARER_TOKEN`
2. Debug listener errors to ensure dictionaries are populated
3. Re-run E2E test with all env vars configured
4. Verify Netlify deployment and webhook delivery

---

## Phase 2D: Privacy & Persistence Infrastructure (✅ Complete)

Privacy protection for Flywheel data and flow state persistence.

| Item | Status | Owner | Notes |
|------|--------|-------|-------|
| Implement PrivacyGuardTool | ✅ Complete | @ai-platform | PII detection, compliance (GDPR/CCPA/HIPAA), cross-validation privacy |
| Create Supabase predictions table | ✅ Complete | @ai-platform | pgvector table for OutcomeTrackerTool |
| Add @persist() decorators to flow | ✅ Complete | @ai-platform | 9 checkpoint methods for state recovery |
| Add PrivacyGuard tests | ✅ Complete | @ai-platform | 40 tests in test_privacy_guard.py |

### Phase 2D Complete Criteria

- [x] PrivacyGuardTool detects PII before Flywheel storage
- [x] Cross-validation privacy boundaries enforced
- [x] Predictions table stores outcomes for model improvement
- [x] Flow can recover from checkpoints via @persist() decorators

---

## Phase 2C: Enhanced Governance + Flywheel Learning (✅ Complete)

Flywheel learning system with industry/stage patterns and outcome tracking.

| Item | Status | Owner | Notes |
|------|--------|-------|-------|
| Enhance LearningCaptureTool patterns | ✅ Complete | @ai-platform | FlywheelInsightsTool with industry/stage patterns |
| Add cross-validation learning retrieval | ✅ Complete | @ai-platform | ValidationContext, similar validation matching |
| Implement outcome tracking | ✅ Complete | @ai-platform | OutcomeTrackerTool with prediction/outcome linking |
| Add Flywheel workflow tests | ✅ Complete | @ai-platform | 38 tests in test_flywheel_workflow.py |

### Phase 2C Complete Criteria

- [x] Pattern learnings captured after each validation phase
- [x] Similar past validations retrieved for context
- [x] Outcome tracking for model improvement
- [x] Governance Crew uses learnings for better predictions

---

## Phase 2B: HITL Workflows - Viability Approval (✅ Complete)

Flow can pause for human viability decisions at the unit economics gate.

| Item | Status | Owner | Notes |
|------|--------|-------|-------|
| Add await_viability_decision flow node | ✅ Complete | @ai-platform | HITL pause at viability gate |
| Wire ViabilityApprovalTool to Finance | ✅ Complete | @ai-platform | Surface LTV/CAC for human review |
| Implement cost pivot decision handler | ✅ Complete | @ai-platform | Price/cost pivot execution |
| Add viability approval tests | ✅ Complete | @ai-platform | 21 tests in test_viability_workflow.py |

### Phase 2B Complete Criteria

- [x] Flow pauses when unit economics need human decision
- [x] /resume payload processes viability decisions (proceed/pivot/kill)
- [x] Finance Crew surfaces unit economics for review
- [x] Cost optimization recommendations presented to user

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

**All Core Phases Complete** - Phase 1A, 1B, 2A, 2B, 2C, and 2D are all implemented.

Next priorities (future phases):
- Real ad platform integration (Meta/Google APIs)
- Real experiment tracking and analytics
- Production webhook integration with product app

---

## What This Unblocks (Downstream)

**Phase 1A + 1B + 2A + 2B Complete unblocks:**
- **Product App**: Can display validation results from webhook
- **All Crews**: Real tools instead of LLM-only outputs
- **Growth Crew**: Can deploy landing pages for experiments
- **Marketing**: Real URLs for demos
- **Quality Assurance**: Human review before ad deployment
- **Compliance**: Review workflow for creative content
- **Strategic Decisions**: Human approval at viability gate
- **Unit Economics**: Real LTV/CAC decisions with human oversight
- **Pivot Execution**: Cost/price optimization with human approval

**Phase 2C Complete unblocks:**
- **Flywheel Learning**: Pattern capture for improved predictions
- **Cross-validation Context**: Learn from similar past validations
- **Model Improvement**: Outcome tracking for continuous improvement

**Phase 2D Complete unblocks:**
- **Privacy Protection**: PII-safe Flywheel data storage
- **Compliance Ready**: GDPR/CCPA/HIPAA checks before storage
- **Flow Recovery**: State persistence at 9 checkpoints for failure recovery
- **Predictions Table**: Outcome tracking storage in Supabase (pgvector)

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
**Last Updated**: 2025-12-05

**Latest Changes (2025-12-05 - Flow to 3-Crew Migration)**:
- **MAJOR**: Architecture migrated from Flow to 3-Crew
- Created 3 crews: Intake (4 agents), Validation (12 agents), Decision (3 agents)
- Crew 1 (Intake) restructured to repo root with `type = "crew"`
- Crews 2 & 3 code ready, need separate GitHub repos
- All Flow-related work archived to `archive/flow-architecture/`
- See ADR-001 for full decision record

**Previous Changes (2025-12-03)**: E2E flow verification (now archived). Fixed 7 runtime bugs discovered during live testing. All 178 unit tests pass.
