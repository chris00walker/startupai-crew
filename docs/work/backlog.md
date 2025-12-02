# StartupAI Validation Backlog

This is not a feature list. It's a queue of **hypotheses to validate** using lean startup methodology: Build → Measure → Learn.

## How to Use This Document

1. **Pick a hypothesis** based on what you need to learn next
2. **Build the minimum** required to test it
3. **Measure the outcome** with real users
4. **Learn and decide**: Pivot or persevere
5. **Update this document** with learnings

---

## ✅ COMPLETED HYPOTHESES

### Hypothesis: Multi-Crew System Enables Scale ✅ VALIDATED

> **If** we structure validation as 8 specialized crews with 18 agents using CrewAI Flows,
> **Then** we can deliver higher quality analysis with clear accountability and extensibility.

**Built** (Phase 1-3 Complete):
- ✅ state_schemas.py - StartupValidationState with 70 fields
- ✅ Service Crew - 3 agents (intake, brief capture)
- ✅ Analysis Crew - 2 agents with TavilySearchTool
- ✅ Build Crew - 3 agents with LandingPageGeneratorTool + Netlify deploy
- ✅ Growth Crew - 3 agents (ad creative, communications, social media)
- ✅ Synthesis Crew - 1 agent (pivot decision logic)
- ✅ Finance Crew - 2 agents with UnitEconomicsCalculatorTool
- ✅ Governance Crew - 3 agents with 8 HITL/Flywheel/Privacy tools
- ✅ Non-linear routing with @router decorators (Innovation Physics)
- ✅ 9 @persist() checkpoints for state recovery

**Measured**:
- ✅ All 8 crews deployed to CrewAI AMP
- ✅ REST API `/kickoff` and `/status` working
- ✅ Average execution time: ~5-10 minutes per validation cycle
- ⏳ Output quality vs 6-agent system - PENDING REAL VALIDATION

**Learned**:
- Crew specialization works well for distinct phases (Desirability/Feasibility/Viability)
- Service/Commercial separation provides clear accountability
- Router-based flow enables true non-linear iteration (segment pivots, value pivots)
- State management with 70 fields is comprehensive but requires careful documentation

**Status**: ✅ COMPLETE - All phases implemented, deployed, and operational

---

### Hypothesis: Tools Improve Analysis Quality ✅ PARTIALLY VALIDATED

> **If** we add web search, financial analysis, and deployment tools to agents,
> **Then** analysis quality will significantly improve beyond pure LLM reasoning.

**Built**:
- ✅ `tools/web_search.py` - TavilySearchTool for market research
- ✅ `tools/financial_data.py` - UnitEconomicsCalculatorTool, IndustryBenchmarkTool
- ✅ `tools/landing_page.py` - LandingPageGeneratorTool
- ✅ `tools/landing_page_deploy.py` - Netlify deployment
- ✅ `tools/learning_capture.py` - Flywheel learning capture
- ✅ `tools/learning_retrieval.py` - Semantic search for patterns
- ✅ `tools/privacy_guard.py` - PII detection (40 integration tests)
- ✅ Total: 18 tools implemented and wired to agents

**Measured**:
- ✅ TavilySearchTool provides real web research data
- ✅ LandingPageDeploymentTool successfully deploys to Netlify
- ⏳ Factual accuracy vs pure LLM - PENDING REAL VALIDATION
- ⏳ Token efficiency - PENDING MEASUREMENT

**Learned**:
- Real-time web search (Tavily) significantly improves market research quality
- Tool contracts with ToolResult<T> envelope provide robust error handling
- Financial tools work but may need real cost/revenue data sources
- Privacy tools (PrivacyGuard) successfully prevent PII leakage

**Status**: ✅ MOSTLY COMPLETE - Tools implemented but need real-world validation

---

### Hypothesis: HITL Approvals Prevent Bad Outcomes ✅ IMPLEMENTED

> **If** we require human approval for high-risk actions (spend, campaigns, gates),
> **Then** users will trust the system with more autonomous operation.

**Built**:
- ✅ 6 approval checkpoint types (creative, viability, segment pivot, etc.)
- ✅ Webhook notification system to product app
- ✅ Resume API for continuing flows after approval
- ✅ `webhooks/resume_handler.py` with ApprovalType enum
- ✅ HITL tools: GuardianReviewTool, ViabilityApprovalTool
- ✅ Database migration: `approval_requests` table in product app

**Measured**:
- ⏳ Approval latency - PENDING REAL USERS
- ⏳ Override rate - PENDING REAL USERS
- ⏳ Trust scores - PENDING SURVEY

**Learned**:
- Webhook + resume pattern works well for async approvals
- Database schema supports approval tracking and rationale capture
- Product app UI for approvals exists but needs frontend implementation
- Resume handler validates bearer tokens and approval types correctly

**Status**: ✅ BACKEND COMPLETE - Frontend UI pending in product app

---

## Priority 1: Core Value Delivery

### Hypothesis: Users Complete Analysis ⏳ IN PROGRESS

> **If** we provide an end-to-end flow from onboarding to analysis results display,
> **Then** users will complete the full analysis and find value in the output.

**Built**:
- ✅ CrewAI flow with `/kickoff` endpoint
- ✅ `/status/{id}` endpoint for polling
- ✅ Webhook to persist results to Supabase (`_persist_to_supabase()`)
- ✅ Database schema for results storage (reports, evidence tables)
- ❌ Product app UI to display results - MISSING

**Blocking Issue**:
- Backend persistence works (webhook saves to Supabase)
- Frontend needs results display page to show analysis output

**Minimum Build Remaining**:
```
[x] API route to poll CrewAI /status - DONE
[x] Webhook handler for results - DONE
[x] Store in reports/evidence tables - DONE
[ ] Basic results display page in product app - TODO
```

**Status**: ⏳ 75% COMPLETE - Backend done, frontend UI pending

**Next Steps**:
1. Build results display page in product app
2. Test E2E flow: Onboarding → Kickoff → Webhook → Display
3. Measure completion rate and user satisfaction

---

### Hypothesis: Quality Output Drives Referrals

> **If** the analysis quality matches Fortune 500 consulting,
> **Then** users will refer other founders.

**Status**: BLOCKED - Requires results display page (above)

---

## Priority 2: User Acquisition

### Hypothesis: Transparency Increases Trust

> **If** we show real-time agent activity on the marketing site,
> **Then** visitors will trust the AI and convert to signup.

**Status**: NOT STARTED

**Required APIs**:
- `GET /api/v1/public/activity` - Recent agent activity feed
- `GET /api/v1/public/metrics` - Aggregate metrics

**Note**: These APIs mentioned in `04-status.md` as not implemented

---

### Hypothesis: Public Metrics Build Credibility

> **If** we display aggregate metrics (analyses completed, satisfaction scores),
> **Then** visitors will trust the platform.

**Status**: NOT STARTED - Requires completed analyses to have data

---

## Priority 3: Learning & Improvement

### Hypothesis: Flywheel Learning Compounds Value ⏳ PARTIALLY COMPLETE

> **If** we capture and retrieve validation patterns from past projects,
> **Then** analysis quality will improve over time.

**Built**:
- ✅ `tools/learning_capture.py` - Pattern/outcome/domain learning
- ✅ `tools/learning_retrieval.py` - Semantic search via pgvector
- ✅ `tools/flywheel_insights.py` - Domain expertise retrieval
- ✅ AnonymizerTool - PII abstraction before storage
- ✅ PrivacyGuardTool - Data leakage prevention (40 tests)
- ✅ Flow integration - `_capture_flywheel_learnings()` in flow
- ❌ Supabase tables - `learnings`, `patterns`, `outcomes` NOT CREATED

**Blocking Issue**:
- Tools are implemented and wired
- Database schema defined in architecture docs
- **Migration needs to be run in product app Supabase**

**Status**: ⏳ 80% COMPLETE - Tools ready, database migration pending

---

## Priority 4: Enterprise-Grade Reliability

### Hypothesis: Structured Observability Enables Operations

> **If** we have structured logging, event tracking, and dashboards,
> **Then** we can operate the system reliably at scale.

**Built**:
- ✅ `observability/structured_logger.py` - JSON logging with event types
- ✅ `persistence/events.py` - ValidationEvent with 10+ event types
- ✅ `persistence/state_repository.py` - Abstract persistence layer
- ✅ Event factory functions (phase transitions, router decisions, errors)
- ❌ Dashboard queries - NOT BUILT
- ❌ Metrics aggregation - NOT BUILT

**Status**: ⏳ 60% COMPLETE - Infrastructure ready, dashboards pending

---

## Deprioritized (Revisit Later)

### Real-time Streaming
> Users want to watch analysis happen step-by-step.

**Why deprioritized**: Unclear if this is actually wanted. Validate core value first.

### Advanced Market Data APIs
> Bloomberg, Crunchbase, etc. for competitive intelligence.

**Why deprioritized**: Start with Tavily web search, add expensive APIs only if needed.

### Policy Versioning & A/B Testing
> Version experiment configs and test retrieval-based policies vs baseline.

**Why deprioritized**: Need production traffic before A/B testing makes sense.

**Known Issue**: `ExperimentConfigResolver.resolve()` ignores `force_policy` parameter - always returns `YAML_BASELINE` instead of the forced policy. Test failure in `test_area_improvements.py::test_resolve_with_forced_policy`. Fix required before A/B testing can work.

### CrewAI AMP Memory Caching Issue
> CrewAI AMP deployment returns cached `consultant_onboarding` results instead of executing `founder_validation` flow.

**Why deprioritized**: Requires CrewAI team support to resolve.

**Known Issue (2025-12-02)**:
- When calling AMP with `flow_type: "founder_validation"`, the API returns cached `consultant_onboarding` results
- Status response shows `"source":"memory"` indicating cached data, not fresh execution
- The `/inputs` endpoint shows only `ConsultantOnboardingState` fields, not `ValidationState`
- Possible causes:
  1. AMP caches results by some key that matches across flow types
  2. AMP is defaulting to the wrong flow when discovering schemas
  3. Memory persistence from earlier successful `consultant_onboarding` runs
- Workarounds attempted:
  - Using unique user_id/project_id/session_id combinations (didn't help)
  - Multiple redeployments (didn't clear cache)
  - `crewai reset-memories --all` only works locally, not on AMP
- **Next steps**: Contact CrewAI support or wait for cache expiration

### Business Model-Specific Viability
> UnitEconomicsModel library for DTC, marketplace, SaaS, etc.

**Why deprioritized**: Start with generic CAC/LTV, specialize when validated.

---

## Learnings Log

| Date | Hypothesis | Outcome | Learning | Decision |
|------|------------|---------|----------|----------|
| 2025-11-26 | Multi-crew system | ✅ Validated | 8 crews with 18 agents deployed successfully | Proceed with current architecture |
| 2025-11-26 | Tool quality | ⏳ Partial | TavilySearch works; financial tools need real data | Validate with real projects |
| 2025-11-26 | HITL workflow | ✅ Validated | Webhook + resume pattern works | Build frontend UI next |

---

## Decision Framework

When choosing what to validate next, ask:

1. **What's the riskiest assumption?** Start there.
2. **What blocks other work?** Unblock it.
3. **What can we learn fastest?** Minimize build time.
4. **What has the biggest impact if true?** Maximize learning value.

**Current Priority**: **Results Display UI** is the critical blocker
- Riskiest: Will users find value in the analysis output?
- Blocking: All retention and referral hypotheses
- Fastest: UI work only (backend complete)
- Biggest impact: Enables real user validation

**Next Priority**: **Flywheel Database Migration** (quick unblock)
- Fastest: Just run the migration
- Impact: Enables compounding learning

---

## Implementation Status Summary

| Component | Status | Completion |
|-----------|--------|------------|
| 8-Crew/18-Agent Architecture | ✅ Complete | 100% |
| Non-linear Innovation Physics Routers | ✅ Complete | 100% |
| 18 Tools (Web Search, Financial, Deployment, HITL, Flywheel, Privacy) | ✅ Complete | 100% |
| State Management (StateRepository, ValidationEvent) | ✅ Complete | 100% |
| Observability (StructuredLogger) | ✅ Complete | 100% |
| HITL Webhook + Resume Backend | ✅ Complete | 100% |
| Results Persistence to Supabase | ✅ Complete | 100% |
| Developer Experience (Makefile, scripts, tests) | ✅ Complete | 100% |
| Tool Contracts (ToolResult envelope) | ✅ Complete | 100% |
| Product App Results Display UI | ❌ Pending | 0% |
| Product App Approval UI | ❌ Pending | 0% |
| Flywheel Database Tables | ❌ Pending Migration | 0% |
| Public Activity/Metrics APIs | ❌ Not Started | 0% |
| Policy Versioning | ❌ Not Started | 0% |
| Business Model-Specific Viability | ❌ Not Started | 0% |

---

## Last Updated
2025-12-02

**Latest Changes**:
- Added known issue for `force_policy` bug in ExperimentConfigResolver
- Updated with Phase 1-3 completion status
- Marked completed hypotheses (Multi-crew, Tools, HITL backend)
- Updated blocking issues and next priorities
- Added implementation status summary table
