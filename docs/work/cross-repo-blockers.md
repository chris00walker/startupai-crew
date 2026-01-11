---
purpose: "Cross-repository dependency tracking for coordinated delivery"
status: "active"
last_reviewed: "2026-01-10 22:00"
last_synced: "2026-01-10 - Asset generation specs complete, docs updated"
---

# Cross-Repository Blockers

This document tracks dependencies between StartupAI repositories to ensure coordinated delivery.

> **TOOLS WIRED (2026-01-10)**: 15 tools wired to 35+ agents using BaseTool pattern. 681 tests passing. Modal redeploy + Phase 0-4 revalidation pending.

## Ecosystem Status (2026-01-10 20:00)

**Phase 0-2 validated. Phase 3-4 live testing next.**

| Service | Status | Completion | Notes |
|---------|--------|------------|-------|
| CrewAI Backend | **Phase 0-2 VALIDATED** | ~90% | Phase 3-4 live testing pending |
| Product App | Modal integration complete | ~95% | Pointing to Modal endpoints |
| Marketing Site | Live API integration | ~95% | Activity Feed + Metrics connected |

**Production URLs**:
- Modal: `https://chris00walker--startupai-validation-fastapi-app.modal.run`
- Product App: `https://app-startupai-site.netlify.app`
- Marketing: `https://startupai.site`

**Canonical Architecture**: 5 Flows, 14 Crews, 45 Agents, 10 HITL checkpoints
**AMP (ARCHIVED)**: Legacy 3-repo workaround deprecated

**Source of Truth**: `docs/master-architecture/09-status.md`

---

## This Repo Blocks

### Product App (`app.startupai.site`)

| Blocker | Status | Description | Unblocks |
|---------|--------|-------------|----------|
| Modal Infrastructure | ✅ DEPLOYED | Production endpoints live | Product can trigger validation |
| Modal API Endpoints | ✅ WORKING | `/kickoff`, `/status`, `/hitl/approve`, `/health` | Full API operational |
| Supabase Tables | ✅ DEPLOYED | `validation_runs`, `validation_progress`, `hitl_requests` + security fixes | State persistence live |
| Supabase Realtime | ✅ ENABLED | Progress tables publishing | Real-time UI updates |
| 14 Crews Implementation | ✅ COMPLETE | 45 agents, 185 tests passing | All phases ready |
| E2E Integration Test | ✅ COMPLETE | 17 tests, Phase 0→4 flow validated | Production validation ready |

**Modal API Endpoints (Production):**
- `POST /kickoff` - Start validation (returns 202 Accepted + run_id)
- `GET /status/{run_id}` - Check progress from Supabase
- `POST /hitl/approve` - Resume after human approval
- `GET /health` - Health check

### Legacy AMP Deployment (ARCHIVED)

| Item | Status | Notes |
|------|--------|-------|
| 3-Crew Architecture | ⚠️ DEPRECATED | Being archived |
| `startupai-crew-validation` | ⚠️ TO ARCHIVE | Repo will be archived (read-only) |
| `startupai-crew-decision` | ⚠️ TO ARCHIVE | Repo will be archived (read-only) |

> See [ADR-002](../adr/002-modal-serverless-migration.md) for migration details.

### Marketing Site (`startupai.site`)

| Blocker | Status | Description | Unblocks |
|---------|--------|-------------|----------|
| Activity Feed API | ✅ SHIPPED | `GET /api/v1/public/activity` in Product App | Marketing can show live activity |
| Metrics API | ✅ SHIPPED | `GET /api/v1/public/metrics` in Product App | Marketing can show trust metrics |

**All Marketing Site blockers resolved.** APIs are available in Product App.

---

## This Repo Blocked By

| Blocker | Source Repo | Status | Impact |
|---------|-------------|--------|--------|
| Learning tables migration | Product App | ✅ Done | Flywheel learning tools have pgvector tables |

**All upstream blockers resolved.**

---

## Schema Alignment (COMPLETE)

> **Status**: ✅ All migrations deployed (2026-01-10)
> **Documentation**: See [data-flow.md](../master-architecture/reference/data-flow.md) for complete analysis

### Deployed Migrations

| Migration | Purpose | Status |
|-----------|---------|--------|
| `modal_validation_runs` | Checkpoint state | ✅ Deployed |
| `modal_validation_progress` | Realtime progress | ✅ Deployed |
| `modal_hitl_requests` | HITL checkpoint/resume | ✅ Deployed |
| `fix_security_definer_views` | 4 views → SECURITY INVOKER | ✅ Deployed |
| `fix_function_search_paths_v2` | 9 functions with search_path | ✅ Deployed |
| `fix_permissive_rls_policies` | Admin-only UPDATE | ✅ Deployed |
| `fix_rls_auth_initplan_part1-5` | 60+ RLS policies optimized | ✅ Deployed |
| `add_missing_fk_indexes` | 6 FK indexes | ✅ Deployed |

### Future Migrations (P1-P3)

| Priority | Table | Purpose |
|----------|-------|---------|
| P1 | `founders_briefs` | VPD-aligned Phase 0 output |
| P2 | `customer_profile_elements` | VPC Jobs/Pains/Gains |
| P2 | `value_map_elements` | VPC Products/Relievers/Creators |
| P3 | `test_cards`, `learning_cards` | TBI framework |

---

## Tool Architecture Implementation

**Status**: ✅ PHASES A-D COMPLETE (2026-01-10) - Modal redeploy pending
**Implementation**: BaseTool pattern (simpler than planned MCP server)
**Owner**: CrewAI Backend (this repo)

### Architecture Decision

Implemented tools using **BaseTool pattern** (direct Python):
- Simpler than MCP server architecture
- 15 tools implemented, wired to 35+ agents
- 681 tests passing (164 new tool tests)
- MCP server pattern documented but not needed for current scope

### Implementation Summary (Complete)

| Phase | Focus | Status | Tools |
|-------|-------|--------|-------|
| A | Customer Research | ✅ Complete | ForumSearchTool, ReviewAnalysisTool, SocialListeningTool, TrendAnalysisTool |
| B | Advanced Analysis | ✅ Complete | TranscriptionTool, InsightExtractorTool, BehaviorPatternTool, ABTestTool |
| C | Analytics & Privacy | ✅ Complete | AnalyticsTool, AnonymizerTool, AdPlatformTool, CalendarTool |
| D | LLM-Based Tools | ✅ Complete | CanvasBuilderTool, TestCardTool, LearningCardTool |
| **TOTAL** | | **✅ Complete** | **15 tools, 35+ agents** |

### Reference Documents

| Document | Purpose |
|----------|---------|
| `reference/tool-specifications.md` | Full MCP architecture + tool specs |
| `reference/tool-mapping.md` | Agent-to-tool matrix with MCP categories |
| `reference/agent-specifications.md` | All 45 agent configurations |
| `reference/agentic-tool-framework.md` | Tool lifecycle framework |
| `reference/ad-platform-specifications.md` | Meta, Google, LinkedIn, TikTok ad specs (NEW) |
| `reference/observability-architecture.md` | Database schemas, callbacks, debugging (NEW) |

---

## Remaining Work (Not Blockers - Internal)

| Item | Status | Owner | Notes |
|------|--------|-------|-------|
| **Tool Integration (Phases A-D)** | ✅ Complete | Crew | 15 tools, 35+ agents, 681 tests |
| **Landing Page Migration (ADR-003)** | ✅ Complete | Crew | Supabase Storage E2E verified |
| **Asset Generation Specs** | ✅ Complete | Crew | Blueprint Pattern + Ad Platform Library |
| **Phase 0-2 Live Testing** | ✅ Complete | Crew | Pivot workflow verified |
| **Phase 3-4 Live Testing** | ⏳ Next | Crew | Feasibility + Viability |
| **F2/F3 Content Quality** | 🔴 Backlog | Crew | `output_pydantic` schemas needed |
| **Asset Generation Implementation** | ⏳ Planned | Crew | Implement from specs when F2/F3 fixed |

---

## Marketing Promise Gap

| Promise | Technical Status |
|---------|------------------|
| "Build your MVP" | ⚠️ LandingPageGeneratorTool SPEC COMPLETE; implementation pending |
| "Real ad spend ($450-525)" | ⚠️ AdCreativeGeneratorTool SPEC COMPLETE; API integration pending |
| "Real user testing" | ⚠️ Progressive Image Resolution spec ready; implementation pending |
| "Unit economics (CAC/LTV)" | ✅ 10 UnitEconomicsModels with industry benchmarks |
| "2-week validation cycles" | ⚠️ Tools exist; quality depends on data |
| "Evidence-based validation" | ✅ TavilySearchTool provides real web research |
| "6 AI Founders team" | ✅ 45 agents across 14 crews |

**Primary gaps**:
- Ad platform integration (Meta/Google APIs) - explicitly deferred
- Asset generation implementation - specs complete, waiting on F2/F3 content quality fix

---

## E2E Verification Checklist

### Infrastructure Verification (2026-01-08) ✅

| Endpoint | Status | Result |
|----------|--------|--------|
| Modal `/health` | ✅ Verified | `{"status":"healthy","service":"startupai-validation"}` |
| Modal auth | ✅ Verified | Returns 401 for invalid tokens |
| Product App login | ✅ Verified | Returns 200 |
| Marketing site | ✅ Verified | Returns 200 |
| Marketing APIs | ✅ Verified | `/public-activity`, `/public-metrics` returning JSON |

### Full Flow (Ready for E2E Test)

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
Results persist to Supabase
    ↓
Dashboard displays validation results
    ↓
Marketing activity feed shows real activity
```

**Status**: E2E integration tests complete (17 tests). Ready for live production validation.

---

## Coordination Notes

- **E2E integration tests COMPLETE** - 17 tests validating Phase 0→4 flow (2026-01-08)
- **202 tests passing** - 185 crew tests + 17 E2E integration tests
- **Crew implementation COMPLETE** - All 14 crews with 45 agents
- **Modal infrastructure DEPLOYED** - Production endpoints verified
- **Product App UPDATED** - Pointing to Modal endpoints (not AMP)
- **Marketing site CONNECTED** - Live Activity Feed + Metrics components
- **AMP DEPRECATED** - Legacy repos archived
- **Primary work**: First live production validation run

**Single Repo Benefit**: Modal migration returns us to single repository (`startupai-crew`). No more cross-repo coordination for Crews 2 & 3.

---

## Cross-Repo Links

- Product app blockers: `app.startupai.site/docs/work/cross-repo-blockers.md`
- Marketing blockers: `startupai.site/docs/work/cross-repo-blockers.md`
- Master architecture: `docs/master-architecture/09-status.md`
- Architecture Decision Records: `docs/adr/`
- Migration plan: `~/.claude/plans/federated-prancing-lollipop.md`

---

**Last Updated**: 2026-01-10 22:00

**Changes (2026-01-10 - Asset Generation Specs)**:
- ✅ **ASSET GENERATION**: Blueprint Pattern, Progressive Image Resolution, Ad Platform Library
- ✅ **NEW DOCS**: `ad-platform-specifications.md`, `observability-architecture.md`
- ✅ **MARKETING GAP UPDATED**: LandingPageGeneratorTool and AdCreativeGeneratorTool specs complete
- ⏳ **NEXT**: Phase 3-4 live testing, then asset generation implementation

**Changes (2026-01-10 - Plan Audit)**:
- ✅ **PLAN AUDIT**: All 4 today's plans audited against codebase
- ✅ **ROADMAP ALIGNED**: phases.md, roadmap.md, in-progress.md updated
- ✅ **PHASE 0-2 VALIDATED**: Live testing with pivot workflow verified
- ⏳ **NEXT**: Phase 3-4 live testing

**Changes (2026-01-10 - Schema Alignment Complete)**:
- ✅ **DEPLOYED**: Modal tables in Product App (`validation_runs`, `validation_progress`, `hitl_requests`)
- ✅ **SECURITY**: 4 views, 9 functions, RLS policies fixed
- ✅ **PERFORMANCE**: 60+ RLS policies optimized, 6 FK indexes added
- Schema alignment section updated to COMPLETE

**Previous (2026-01-09 - MCP Architecture Designed)**:
- 🚀 **MCP-FIRST**: Adopted Model Context Protocol as unified tool interface
- Architecture: 13 EXISTS + 10 MCP Custom + 4 MCP External + 6 LLM-Based = 33 tools
- Implementation roadmap: 60 hours over 4 weeks (~$5-10/month cost)
- Updated `reference/tool-specifications.md` with MCP server pattern
- Updated `reference/tool-mapping.md` with MCP categories
- Updated `docs/work/phases.md` with implementation phases
- Ready for Phase A: Core MCP Server setup

**Previous (2026-01-09 - Architecture Specs Complete)**:
- Architecture documentation refactored to be "bullet proof"
- Created `reference/agent-specifications.md` - All 45 agents documented
- Created `reference/tool-specifications.md` - All 33 tools with schemas
- Refactored `reference/tool-mapping.md` - Complete mapping matrix

**Previous (2026-01-08 - E2E Integration Tests Complete)**:
- Added 17 E2E integration tests (Phase 0→4 flow)
- 202 tests passing (185 crew + 17 E2E)

**Previous (2026-01-08 - Modal Production Deployment)**:
- Modal serverless deployed to production
- Infrastructure verification passed (health, auth, endpoints)
- Product app updated to point to Modal (not AMP)
- Marketing site live components created (Activity Feed, Metrics)
- AMP marked as deprecated, repos to be archived
