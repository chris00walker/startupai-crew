---
purpose: "Private technical source of truth for recently delivered work"
status: "active"
last_reviewed: "2026-01-10"
---

# Recently Delivered

## Timeline Clarification (2026-01-10)

| Date | Event | Notes |
|------|-------|-------|
| 2026-01-09 AM | Phase 0-2 live testing | 6 bugs found/fixed, BEFORE tools |
| 2026-01-09-10 | Tool integration Phases A-D | 15 tools, 35+ agents, 681 tests |
| 2026-01-10 | Schema alignment | Modal migrations deployed to Supabase |
| 2026-01-10 15:08 | Bug fixes deployed | #10-12 fixed, Phase 2 retry running |
| 2026-01-10 | **4 Critical Issues Fixed** | Bug #9, tool gap, timeout, RLS |
| **Next** | Complete Phase 2-4 live test | All blockers resolved |

---

## 4 Critical Issues Resolved (2026-01-10)

Fixed all blocking issues from system assessment for production readiness.

### Issues Fixed

| Issue | Problem | Fix | Files |
|-------|---------|-----|-------|
| **Bug #9** | HITL duplicate key constraint on pivot | Expire pending HITLs before insert | `persistence.py` |
| **Tool Gap** | 4 of 9 Phase 2 agents had no tools (44%) | Wire F1, F2, F3, G3 | `build_crew.py`, `governance_crew.py` |
| **Timeout** | Container timeout 1h insufficient | Increase to 2h | `app.py` |
| **RLS** | Security not enabled | Verified already deployed | N/A |

### Files Changed

| File | Changes |
|------|---------|
| `src/state/persistence.py` | Added cancel logic in `create_hitl_request()` - expire pending before insert |
| `src/crews/desirability/build_crew.py` | F1: CanvasBuilderTool, TestCardTool; F2: same; F3: CalendarTool, MethodologyCheckTool |
| `src/crews/desirability/governance_crew.py` | G3: LearningCardTool |
| `src/modal_app/app.py` | timeout: 3600 → 7200 for both functions |
| `db/migrations/008_enable_validation_runs_rls.sql` | RLS migration created (already applied) |
| `tests/test_pivot_workflow.py` | Updated test expectation for Bug #11 fallback |

### Validation

- 678 tests passing (all pass)
- Modal deployed successfully
- RLS policies verified: 16 policies active on 3 tables

---

## Bug Fixes Deployed (2026-01-10 15:08)

Fixed 3 bugs discovered during Phase 2 live testing with tools.

### Issues Fixed

| # | Issue | Root Cause | Fix | Commit |
|---|-------|------------|-----|--------|
| 10 | AnalyticsTool expected string, LLM passed dict | Tool used JSON string parsing, not Pydantic | Added `args_schema` for typed input | `623322a` |
| 11 | Segment alternatives returned `[]` on error | No error handling in `generate_alternative_segments()` | Added input validation + fallback alternatives | `623322a` |
| 12 | DesirabilityEvidence JSON parsing crashed | Malformed LLM output caused parse error | Added try/catch with default evidence | `623322a` |

### Files Modified

| File | Changes |
|------|---------|
| `src/shared/tools/analytics_privacy.py` | Added `AnalyticsInput`, `AdPlatformInput`, `CalendarInput` schemas; updated `_run()` signatures |
| `src/modal_app/helpers/segment_alternatives.py` | Added input validation, logging, and fallback alternatives |
| `src/crews/desirability/__init__.py` | Added try/catch with default evidence in `run_growth_crew()` |
| `tests/tools/test_analytics_privacy.py` | Updated tests to use new typed parameter API |

### Pattern Learned

CrewAI tools should use Pydantic `args_schema` for typed input validation rather than parsing JSON strings. The LLM naturally passes structured data, so let CrewAI validate it.

```python
class AnalyticsInput(BaseModel):
    site_id: str = Field(..., description="Netlify site ID")
    days: int = Field(default=7, description="Number of days to fetch")

class AnalyticsTool(BaseTool):
    args_schema: type[BaseModel] = AnalyticsInput

    def _run(self, site_id: str, days: int = 7) -> str:
        # Typed parameters - no JSON parsing needed
        ...
```

### Validation

- 154 tool tests passing (updated for new API)
- Modal redeployed with fixes
- Phase 2 BuildCrew executing

---

## Tool Integration COMPLETE (2026-01-10)

All 4 phases of tool integration completed. 15 tools wired to 35+ agents.

### Summary

| Phase | Focus | Tools | Tests |
|-------|-------|-------|-------|
| A | Customer Research | 4 | 31 |
| B | Advanced Analysis | 4 | 35 |
| C | Analytics & Privacy | 4 | 42 |
| D | LLM-Based Tools | 3 | 46 |
| **TOTAL** | | **15** | **164** |

### Final State

- **678 tests passing** (164 new tool tests)
- **35+ agents** with tools wired
- **15 tools** implemented
- **4 weeks** / 60 hours of work

---

## Phase D: LLM-Based Tools (2026-01-10)

Completed Phase D with 3 LLM-based tools for structured validation outputs.

### Tools Implemented

| Tool | Purpose | Agents |
|------|---------|--------|
| `CanvasBuilderTool` | VPC element generation (Pydantic) | V1, V2, V3 |
| `TestCardTool` | Strategyzer Test Card design | E1 |
| `LearningCardTool` | Strategyzer Learning Card capture | E1, D4 |

### Additional Wiring

| Agent | Tool | Purpose |
|-------|------|---------|
| G2 (Desirability) | AnonymizerTool | PII scrubbing |
| G2 (Feasibility) | AnonymizerTool | Architecture security |
| G2 (Viability) | AnonymizerTool | Final PII verification |

### Files Created

- `src/shared/tools/llm_tools.py` - 3 tools (~700 lines)
- `tests/tools/test_llm_tools.py` - 46 tests (~400 lines)

### Crews Modified

- `src/crews/discovery/value_design_crew.py` - V1, V2, V3 wired
- `src/crews/discovery/discovery_crew.py` - E1, D4 wired
- `src/crews/desirability/governance_crew.py` - G2 wired
- `src/crews/feasibility/governance_crew.py` - G2 wired
- `src/crews/viability/governance_crew.py` - G2 wired

### Validation

- 678 tests pass (46 new)
- Commit `7faa12e`

---

## Phase C: Analytics & Privacy Tools (2026-01-10)

Completed Phase C tool integration with 4 new tools wired to 8 agents.

### Tools Implemented

| Tool | Purpose | Agents |
|------|---------|--------|
| `AnalyticsTool` | Netlify Analytics API for LP metrics | P3, D3, L1, W1, W2 |
| `AnonymizerTool` | PII removal (regex + optional Presidio) | Learning pipeline |
| `AdPlatformTool` | MCP wrapper for Meta/Google Ads | P1, P2, P3, D3 |
| `CalendarTool` | Interview scheduling via Calendar MCP | D1 |

### Files Created

- `src/shared/tools/analytics_privacy.py` - 4 tools (~700 lines)
- `tests/tools/test_analytics_privacy.py` - 42 tests (~430 lines)

### Crews Modified

- `src/crews/discovery/discovery_crew.py` - D1, D3 tools wired
- `src/crews/discovery/wtp_crew.py` - W1, W2 tools wired
- `src/crews/desirability/growth_crew.py` - P1, P2, P3 tools wired
- `src/crews/viability/finance_crew.py` - L1 tools wired

### Validation

- 632 tests pass (42 new)
- Commit `c6f8043`

---

## Phase B: Advanced Analysis Tools (2026-01-10)

Completed Phase B tool integration with 4 advanced tools.

### Tools Implemented

| Tool | Purpose | Agents |
|------|---------|--------|
| `TranscriptionTool` | Whisper API integration for audio | D1 |
| `InsightExtractorTool` | LLM-based interview pattern extraction | D1, D4 |
| `BehaviorPatternTool` | Statistical behavior analysis | D2, D3, D4 |
| `ABTestTool` | Experiment design with stats | P1, P2, W1, D3 |

### Validation

- 590 tests pass (35 new)
- Commit `5577720`

---

## Phase A: Customer Research Tools (2026-01-10)

Completed Phase A tool integration with 4 customer research tools.

### Tools Implemented

| Tool | Purpose | Agents |
|------|---------|--------|
| `ForumSearchTool` | Reddit/StackOverflow search | D2, J1, PAIN_RES, GAIN_RES |
| `ReviewAnalysisTool` | Product review aggregation | D2, J1, PAIN_RES, GAIN_RES |
| `SocialListeningTool` | Social platform monitoring | D2 |
| `TrendAnalysisTool` | Trend search integration | D2 |

### Validation

- 555 tests pass (31 new)
- Commit `7a4ab1f`

---

## Tool Integration Immediate Actions (2026-01-09)

Completed all unblocking actions for tool integration.

### Actions Completed

| Action | Impact |
|--------|--------|
| Migrated tools to `shared/tools/` | All crews can now import TavilySearchTool, MethodologyCheckTool |
| Added MCP deps to Modal image | mcp, fastmcp, mcp_use packages available |
| Wired TavilySearchTool | 4 research agents (D2, J1, PAIN_RES, GAIN_RES) |
| Applied IntakeCrew pattern | All 45 agents now have `tools=[]`, `reasoning`, `inject_date`, `max_iter`, `llm` config |

### Files Modified

- `src/shared/tools/web_search.py` - TavilySearchTool, CustomerResearchTool
- `src/shared/tools/methodology_check.py` - MethodologyCheckTool
- `src/shared/tools/__init__.py` - Exports for all tools
- `src/modal_app/app.py` - Added MCP packages to Modal image
- All 14 crew files updated with IntakeCrew pattern

### Validation

- 524 tests pass
- All tool imports validated
- All crew imports validated

---

## MCP-First Tool Architecture Design (2026-01-09)

Comprehensive tool integration architecture designed and documented.

### Architecture Documents Created

| Date | Item | Notes |
|------|------|-------|
| 2026-01-09 | `reference/agentic-tool-framework.md` | Tool lifecycle, agent configuration patterns, implementation tiers |
| 2026-01-09 | `reference/tool-mapping.md` | Agent-to-tool assignments across all 45 agents |
| 2026-01-09 | `reference/tool-specifications.md` | All 33 tools detailed with APIs and examples |

### Tool Categories Defined

| Category | Count | Description |
|----------|-------|-------------|
| EXISTS | 13 | Implemented, ready to wire |
| MCP Custom | 10 | Build as FastMCP tools on Modal |
| MCP External | 4 | Use existing MCP servers (Meta Ads, Google Ads, Calendar, Fetch) |
| LLM-Based | 6 | Structured output with Pydantic |
| **TOTAL** | 33 | All tools mapped to agents |

### Implementation Roadmap

60-hour, 4-week roadmap defined:
- Phase A: Core MCP Server (15h)
- Phase B: Advanced Tools (14h)
- Phase C: External MCP + Analytics (13h)
- Phase D: CrewAI Integration (18h)

---

## Modal Live Testing Phase 0-2 (2026-01-09)

Live testing with real LLM calls validated core functionality.

### Testing Results

| Phase | Status | Issues Found | Issues Fixed |
|-------|--------|--------------|--------------|
| Phase 0 (Onboarding) | ✅ PASSED | 1 | 1 |
| Phase 1 (VPC Discovery) | ✅ PASSED | 2 | 2 |
| Phase 2 (Desirability) | ✅ PASSED | 2 | 2 |

### Bugs Fixed During Testing

| Date | Bug | Fix | Commit |
|------|-----|-----|--------|
| 2026-01-09 | HITL phase advancement bug | Fixed state machine | `46c7da6` |
| 2026-01-09 | Template variable interpolation timing | Fixed in crew configs | `b96e7a7`, `346e02e` |
| 2026-01-09 | Signal-based HITL routing | VPD compliance fix | `e6ce56b` |

---

## Modal Serverless Migration (2026-01-08)

Complete migration from CrewAI AMP to Modal serverless.

### Architecture Decision

| Date | Item | Notes |
|------|------|-------|
| 2026-01-08 | ADR-002 | Modal serverless migration decision documented |
| 2026-01-08 | Three-layer architecture | Netlify + Supabase + Modal |
| 2026-01-08 | $0 idle costs | Pay-per-second billing |
| 2026-01-08 | Single repository | No more 3-repo workaround |

### Infrastructure Deployed

| Component | Status | Notes |
|-----------|--------|-------|
| Modal functions | ✅ Deployed | 5 phase functions |
| Supabase tables | ✅ Deployed | State persistence |
| FastAPI endpoints | ✅ Deployed | /kickoff, /status, /hitl/approve |
| Secrets configuration | ✅ Deployed | startupai-secrets |

**Production URL**: `https://chris00walker--startupai-validation-fastapi-app.modal.run`

### Crews Implemented

| Phase | Crews | Agents | Tests |
|-------|-------|--------|-------|
| Phase 0 | OnboardingCrew | 4 | 24 |
| Phase 1 | DiscoveryCrew, CustomerProfileCrew, ValueDesignCrew, WTPCrew, FitAssessmentCrew | 18 | 25 |
| Phase 2 | BuildCrew, GrowthCrew, GovernanceCrew | 9 | 42 |
| Phase 3 | BuildCrew, GovernanceCrew | 5 | 36 |
| Phase 4 | FinanceCrew, SynthesisCrew, GovernanceCrew | 9 | 58 |
| **TOTAL** | 14 | 45 | 185 |

---

## Architecture Documentation Standardization (2026-01-07)

Master architecture documents aligned with CrewAI patterns.

### Documents Updated

| Date | Document | Changes |
|------|----------|---------|
| 2026-01-07 | All 10 docs | Consistent YAML frontmatter with `vpd_compliance: true` |
| 2026-01-07 | All docs | Related Documents navigation section |
| 2026-01-07 | `02-organization.md` | Complete crew structure |
| 2026-01-07 | `09-status.md` | Full rewrite with cross-repo verification |

### Pattern Hierarchy Established

```
PHASE (Business Concept) → FLOW (Orchestration) → CREW (Agent Group) → AGENT → TASK
```

**Critical Rule**: A crew must have 2+ agents (per CrewAI docs)

### Architecture Metrics

| Metric | Canonical | AMP (Deprecated) |
|--------|-----------|------------------|
| Phases | 5 | 5 |
| Flows | 5 | N/A |
| Crews | 14 | 3 |
| Agents | 45 | 19 |
| HITL | 10 | 7 |

---

## Crew 1 Best Practices Alignment (2026-01-06)

IntakeCrew (Crew 1) achieved 100% CrewAI best practices alignment.

### Improvements Implemented

| Date | Item | Notes |
|------|------|-------|
| 2026-01-06 | `src/intake_crew/schemas.py` | 397 lines, 6 task output models |
| 2026-01-06 | `output_pydantic` wired | All 6 tasks |
| 2026-01-06 | TavilySearchTool | Wired to S2 |
| 2026-01-06 | CustomerResearchTool | Wired to S2 |
| 2026-01-06 | MethodologyCheckTool | Wired to G1 |
| 2026-01-06 | Agent backstories | All 4 enriched |
| 2026-01-06 | `reasoning=True` | S2 and G1 agents |

### Testing

| Date | Item | Notes |
|------|------|-------|
| 2026-01-06 | `tests/test_intake_schemas.py` | 517 lines, 28 tests |

---

## AMP 3-Crew Deployment (2026-01-04) - DEPRECATED

> **DEPRECATED**: Replaced by Modal serverless. See ADR-002.

### Deployment Summary

| Crew | UUID | Status |
|------|------|--------|
| Crew 1 (Intake) | `6b1e5c4d-e708-4921-be55-08fcb0d1e94b` | Archived |
| Crew 2 (Validation) | `3135e285-c0e6-4451-b7b6-d4a061ac4437` | Archived |
| Crew 3 (Decision) | `7da95dc8-7bb5-4c90-925b-2861fa9cba20` | Archived |

### Why Deprecated

- Platform reliability issues (caching, memory)
- Multi-repo complexity (3 separate repos required)
- Always-on costs vs Modal's pay-per-second

---

## Areas 3, 6, 7: Architectural Improvements (2025-11-27)

Final implementation of architectural improvements bringing the system to 100% complete.

### Area 3: Policy Versioning & A/B Testing

| Date | Item | Notes |
|------|------|-------|
| 2025-11-27 | PolicyBandit | `tools/policy_bandit.py` - UCB algorithm |
| 2025-11-27 | ExperimentConfigResolver | Policy-based config resolution |
| 2025-11-27 | evaluate_policies.py | Offline evaluation with Z-test, Cohen's d |

### Area 6: Budget Guardrails & Decision Logging

| Date | Item | Notes |
|------|------|-------|
| 2025-11-27 | BudgetGuardrails | Hard/soft enforcement modes |
| 2025-11-27 | DecisionLogger | Audit trail persistence |
| 2025-11-27 | decision_log table | Migration 006 |

### Area 7: Business Model-Specific Viability

| Date | Item | Notes |
|------|------|-------|
| 2025-11-27 | BusinessModelClassifier | Auto-classification from state |
| 2025-11-27 | 10 UnitEconomicsModels | SaaS, Ecommerce, Fintech, Consulting |
| 2025-11-27 | MODEL_REGISTRY | Factory lookup by type |

---

## Phase 2D: Privacy & Persistence (2025-11-26)

| Date | Item | Notes |
|------|------|-------|
| 2025-11-26 | PrivacyGuardTool | PII detection, GDPR/CCPA/HIPAA compliance |
| 2025-11-26 | predictions table | pgvector for OutcomeTrackerTool |
| 2025-11-26 | @persist() decorators | 9 checkpoint methods |
| 2025-11-26 | 40 privacy tests | `test_privacy_guard.py` |

---

## Phase 2C: Flywheel Learning (2025-11-26)

| Date | Item | Notes |
|------|------|-------|
| 2025-11-26 | FlywheelInsightsTool | Industry/stage pattern retrieval |
| 2025-11-26 | OutcomeTrackerTool | Prediction tracking with feedback |
| 2025-11-26 | ValidationContext model | Cross-validation matching |
| 2025-11-26 | 38 flywheel tests | `test_flywheel_workflow.py` |

---

## Phase 2B: HITL Viability Approval (2025-11-26)

| Date | Item | Notes |
|------|------|-------|
| 2025-11-26 | ViabilityApprovalTool | LTV/CAC analysis, pivot recommendations |
| 2025-11-26 | await_viability_decision | Flow pause for human decision |
| 2025-11-26 | Pivot execution | _execute_price_pivot, _execute_cost_pivot |
| 2025-11-26 | 21 viability tests | `test_viability_workflow.py` |

---

## Phase 2A: HITL Creative Approval (2025-11-26)

| Date | Item | Notes |
|------|------|-------|
| 2025-11-26 | GuardianReviewTool | Auto-QA for creatives |
| 2025-11-26 | MethodologyCheckTool | VPC/BMC structure validation |
| 2025-11-26 | ResumeHandler | /resume webhook parsing |
| 2025-11-26 | 32 HITL tests | `test_hitl_workflow.py` |

---

## Phase 1B: Landing Page Deployment (2025-11-26)

| Date | Item | Notes |
|------|------|-------|
| 2025-11-26 | LandingPageDeploymentTool | Netlify API integration |
| 2025-11-26 | Build Crew wiring | 3 tools to prototype_designer |
| 2025-11-26 | 17 build tests | `test_build_crew.py` |

---

## Phase 1A: Results Persistence (2025-11-26)

| Date | Item | Notes |
|------|------|-------|
| 2025-11-26 | LearningCaptureTool | Wired to Governance Crew |
| 2025-11-26 | crewai_config.yaml | Webhooks + pgvector config |
| 2025-11-26 | Results persistence | Already in flow (verified) |

---

## Phase 1: Innovation Physics (2025-11-22)

| Date | Item | Notes |
|------|------|-------|
| 2025-11-22 | state_schemas.py | All Innovation Physics signals |
| 2025-11-22 | Non-linear routers | Desirability, Feasibility, Viability gates |
| 2025-11-22 | 7 crew stubs | All phases covered |
| 2025-11-22 | Synthesis Crew | Complete pivot decision logic |

---

**Last Updated**: 2026-01-10 15:08
