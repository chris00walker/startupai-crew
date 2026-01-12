---
purpose: "Private technical source of truth for active work"
status: "active"
last_reviewed: "2026-01-10 22:00"
last_audit: "2026-01-10 - Asset generation specs complete, architecture docs updated"
---

# In Progress

## 🎯 Current Priority: Phase 3-4 Live Testing

**Goal**: Complete full validation cycle through Viability phase.

| Phase | Status | Blocker |
|-------|--------|---------|
| Phase 0-2 | ✅ Complete | None (pivot workflow verified) |
| **Phase 3 (Feasibility)** | ⏳ Next | None |
| **Phase 4 (Viability)** | ⏳ Next | Depends on Phase 3 |

**To start Phase 3-4**: Resume the existing run or trigger new `/kickoff`.

---

## Architecture Status (2026-01-10)

| Layer | Status | Notes |
|-------|--------|-------|
| Interaction (Netlify) | ✅ Production | Edge Functions (product app) |
| Orchestration (Supabase) | ✅ Production | PostgreSQL + Realtime + Modal tables + RLS |
| Compute (Modal) | ✅ Redeployed | All fixes deployed 2026-01-10 |
| **Tool Integration** | ✅ Complete | 15 tools, 35+ agents, 681 tests |
| **Landing Pages** | ✅ Complete | Supabase Storage (ADR-003) - E2E tested |
| **Observability** | ⚠️ Backlog | F2/F3 tracing insufficient - see backlog |
| **Asset Generation Specs** | ✅ Complete | Blueprint Pattern + Ad Platform Library |

**ADRs**:
- [ADR-002](../adr/002-modal-serverless-migration.md) - Modal serverless architecture
- [ADR-003](../adr/003-landing-page-storage-migration.md) - Landing page storage migration

---

## ✅ Completed: Asset Generation Architecture (2026-01-10)

**Status**: ✅ COMPLETE - Spec documentation committed
**Reference**: `docs/master-architecture/reference/tool-specifications.md`

### What Was Done

Comprehensive specifications for asset generation tools to support Phase 2 (Desirability) validation:

| Commit | Feature | Purpose |
|--------|---------|---------|
| `ef87146` | Blueprint Pattern | Assembly-based LP generation (9 components, 20 icons) |
| `dcab571` | Progressive Image Resolution (LP) | Unsplash first, AI on demand |
| `3d4d112` | Ad Creative Visuals | Progressive resolution for ad images |
| `68f5178` | Ad Platform Specifications Library | Canonical reference for Meta/Google/LinkedIn/TikTok |

### Key Architecture Decisions

1. **Assembly > Generation**: Use pre-built Tailwind components instead of generating raw HTML
2. **Progressive Image Resolution**: Unsplash for speed ($0), AI generation only on user request
3. **Blueprint Pattern**: JSON stored in DB enables re-generation without full agent chain
4. **Ad Platform Library**: Agents load specs from library, not hardcoded values

### New Reference Documents

| Document | Purpose |
|----------|---------|
| `reference/ad-platform-specifications.md` | Meta, Google, LinkedIn, TikTok specs (NEW) |
| `reference/observability-architecture.md` | Debugging workflow, DB schemas (NEW) |
| `reference/tool-specifications.md` | Updated with asset generation tools |

### Implementation Ready

These specs are ready for implementation:
- `LandingPageGeneratorTool` - Blueprint + Component Registry
- `AdCreativeGeneratorTool` - Copy + Visuals with progressive resolution
- Observability callbacks for debugging

---

## ✅ Completed: Landing Page Storage Migration

**Status**: ✅ COMPLETE - E2E tested 2026-01-10
**ADR**: [ADR-003](../adr/003-landing-page-storage-migration.md)
**Effort**: Completed 2026-01-10

### Problem (RESOLVED)

The `LandingPageDeploymentTool` using Netlify API had authentication issues:
- Token could CREATE sites but could not DEPLOY to them (401 Unauthorized)
- Token could not LIST sites or GET user info
- Architecture mismatch: Netlify is permanent hosting, we need temporary artifacts

### Solution (IMPLEMENTED)

Migrated to Supabase Storage for landing page deployment:
- Public bucket serves HTML files via CDN
- Client-side JavaScript captures pageviews and form submissions
- RLS policies allow anonymous INSERT for tracking
- Natural cleanup when validation run expires
- Already in our stack (no new infrastructure)

### Implementation Phases

| Phase | Task | Status |
|-------|------|--------|
| 1 | Create Supabase tables (migration 009) | ✅ Complete |
| 2 | Rewrite `LandingPageDeploymentTool` for Supabase Storage | ✅ Complete |
| 3 | Update tests (34 tests passing) | ✅ Complete |
| 4 | Archive Netlify implementation | ✅ Complete |

### Verification (2026-01-10)

✅ **Storage bucket created and verified**:
- Bucket: `landing-pages` (public)
- Test upload: SUCCESS
- Test URL: https://eqxropalhxjeyvfcoyxg.supabase.co/storage/v1/object/public/landing-pages/test/simple-test.html
- HTTP Status: 200 OK

✅ **E2E test completed** (run_id: `8bf58864-d220-4d5b-9dfe-e27e75b9a8f2`):
- Phase 0 → Phase 1 → Phase 2 progression
- Landing pages deployed to storage (variant-a, variant-b)
- Database records created in `landing_page_variants`
- Public URLs accessible (HTTP 200)

⚠️ **Note**: Landing page content was placeholder HTML - this is an agent content generation issue, not infrastructure.

⚠️ **Optional**: Add `SUPABASE_ANON_KEY` to Modal secrets for client-side tracking:
```bash
modal secret update startupai-secrets SUPABASE_ANON_KEY=<anon-key>
```

### Files Changed

- `src/shared/tools/landing_page_deploy.py` - Rewrote for Supabase Storage (~150 lines vs 522)
- `db/migrations/009_landing_page_tables.sql` - Tables: landing_page_variants, lp_submissions, lp_pageviews
- `tests/tools/test_landing_page_deploy.py` - Updated tests to mock Supabase
- `archive/netlify-landing-page-deploy.py` - Old Netlify implementation archived

---

## Backlog: F2/F3 Placeholder HTML & Tracing Gaps

**Status**: 🔴 NEEDS ATTENTION - Identified during E2E test
**Priority**: P0/P1
**Estimated Effort**: ~10 hours

### Problem

During E2E testing, F2/F3 agents generated placeholder HTML (`<!DOCTYPE html><html>...Variant A HTML...</html>`) instead of real landing pages.

### Root Cause Analysis (Modal Developer Investigation)

1. **Missing structured output schemas** - Tasks lack `output_pydantic` to enforce HTML structure
2. **Insufficient logging** - BuildCrew results not logged, intermediate task outputs not captured
3. **Ambiguous task descriptions** - Tasks say "build landing page" but don't specify "output full HTML"
4. **Tool gap** - F2 has no HTML generation tool; relies on free-form LLM output

### Tracing Checklist

| Feature | Status |
|---------|--------|
| Modal logging configured | ✅ JSON at app level |
| Phase logging enabled | ✅ All transitions logged |
| Agent verbose mode | ✅ `verbose=True` |
| **Crew output logging** | ❌ BuildCrew results NOT logged |
| **Task output logging** | ❌ Individual task results NOT captured |
| **Structured outputs** | ❌ No `output_pydantic` schemas |
| **Step callbacks** | ❌ Agent reasoning NOT traced |
| **Debug mode** | ❌ `MODAL_LOGLEVEL` not set |

### Recommended Fixes

| Priority | Task | Impact | Effort |
|----------|------|--------|--------|
| **P0** | Add `output_pydantic` to build tasks | Prevents placeholders | 2h |
| **P0** | Add BuildCrew logging | Enables debugging | 1h |
| **P1** | Create `HTMLGeneratorTool` for F2 | Ensures real HTML | 3h |
| **P1** | Add `task_callback` logging | Trace execution flow | 1h |
| **P2** | Enable `MODAL_LOGLEVEL=DEBUG` | Deeper visibility | 30m |
| **P2** | Add HTML validation tests | Prevent regressions | 2h |

### Files to Change

- `src/crews/desirability/build_crew.py` - Add task_callback, step_callback
- `src/crews/desirability/__init__.py` - Log BuildCrew outputs
- `src/crews/desirability/config/build_tasks.yaml` - Add output_pydantic schemas
- `src/state/models.py` - Add LandingPageOutput schema
- `src/shared/tools/html_generator.py` - New tool (optional)

---

## Paused: Phase 3-4 Live Testing

**Status**: 🔄 BUG #9 VERIFIED - Pivot Scenario Passed
**Run ID**: `e3368f64-89e9-49c0-8d42-d5cbc16f8eeb` (StartupAI dogfood)
**Current Phase**: Phase 2 - Second pivot checkpoint pending
**Next**: Decide on pivot or proceed to Phase 3

### Critical Fixes Deployed (2026-01-10)

| Issue | Problem | Fix | Status |
|-------|---------|-----|--------|
| **#9** | HITL duplicate key on pivot | Expire pending HITLs before insert | ✅ Fixed |
| **Tool Gap** | 4 of 9 Phase 2 agents had no tools | Wire F1, F2, F3, G3 | ✅ Fixed |
| **Timeout** | Container timeout insufficient (1h) | Increase to 2h | ✅ Fixed |
| **RLS** | Security not enabled on tables | Already deployed | ✅ Verified |
| **#13** | F3 had wrong tools (Calendar/Methodology) | Wire `LandingPageDeploymentTool` | ✅ Fixed |

**Files Changed**:
- `src/state/persistence.py` - Bug #9 HITL cancel logic
- `src/crews/desirability/build_crew.py` - F1, F2, F3 tools wired, F3 now has `LandingPageDeploymentTool`
- `src/crews/desirability/governance_crew.py` - G3 tool wired
- `src/modal_app/app.py` - Timeout 3600s → 7200s
- `db/migrations/008_enable_validation_runs_rls.sql` - RLS migration (already applied)
- `src/shared/tools/landing_page_deploy.py` - Netlify deployment tool (NEW)
- `tests/tools/test_landing_page_deploy.py` - 25 unit tests (NEW)

### Previous Bug Fixes (Still Deployed)

| Issue | Problem | Fix | Commit |
|-------|---------|-----|--------|
| #10 | AnalyticsTool expected string, LLM passed dict | Added Pydantic `args_schema` | `623322a` |
| #11 | Segment alternatives returned `[]` on error | Added fallback + logging | `623322a` |
| #12 | DesirabilityEvidence JSON parsing crashed | Added try/catch with default | `623322a` |

---

## Completed: Tool Integration (Phases A-D)

**Status**: ✅ CODE COMPLETE (not yet deployed/validated)
**Total Effort**: ~50 hours
**Completed**: 2026-01-10

### Why This Matters

Without tools, agents **hallucinate** outputs instead of collecting real evidence:

| Output Type | Without Tools | With Tools |
|-------------|---------------|------------|
| Market Research | Plausible but invented | Real search results with citations |
| Competitor Analysis | Generic observations | Actual competitor URLs and features |
| Landing Pages | Code that might work | Deployed URLs with analytics |
| Unit Economics | Made-up numbers | Calculations based on real CAC/LTV |

### Phase A: Customer Research Tools (Week 1) - COMPLETE

✅ **COMPLETED 2026-01-10** - Implemented as BaseTool pattern (simpler than FastMCP).

| Task | Target Agents | Effort | Status |
|------|---------------|--------|--------|
| Create `customer_research.py` with 4 tools | All research | 4h | ✅ Done |
| Implement `ForumSearchTool` | D2, J1, PAIN_RES, GAIN_RES | - | ✅ Done |
| Implement `ReviewAnalysisTool` | D2, J1, PAIN_RES, GAIN_RES | - | ✅ Done |
| Implement `SocialListeningTool` | D2 | - | ✅ Done |
| Implement `TrendAnalysisTool` | D2 | - | ✅ Done |
| Wire tools to agents | D2, J1, PAIN_RES, GAIN_RES | 1h | ✅ Done |
| Add unit tests | - | 1h | ✅ Done |

**Tools wired to agents**:
- D2: TavilySearchTool + ForumSearchTool + ReviewAnalysisTool + SocialListeningTool + TrendAnalysisTool
- J1, PAIN_RES, GAIN_RES: TavilySearchTool + ForumSearchTool + ReviewAnalysisTool

**Tests**: 555 passing (31 new tool tests)

### Phase B: Advanced Tools (Week 2) - COMPLETE

✅ **COMPLETED 2026-01-10** - Implemented as BaseTool pattern with LLM/scipy backends.

| Task | Target Agents | Effort | Status |
|------|---------------|--------|--------|
| Implement `TranscriptionTool` | D1 | 3h | ✅ Done |
| Implement `InsightExtractorTool` | D1, D4 | 4h | ✅ Done |
| Implement `BehaviorPatternTool` | D2, D3 | 4h | ✅ Done |
| Implement `ABTestTool` | P1, P2, W1 | 3h | ✅ Done |
| Wire tools to agents | D1, D2, D3, D4, P1, P2, W1 | 1h | ✅ Done |
| Add unit tests | - | 1h | ✅ Done |

**Tools wired to agents**:
- D1: TranscriptionTool + InsightExtractorTool
- D2: BehaviorPatternTool (added to Phase A tools)
- D3: BehaviorPatternTool + ABTestTool
- D4: InsightExtractorTool + BehaviorPatternTool
- P1, P2: ABTestTool
- W1: ABTestTool

**Tests**: 590 passing (35 new Phase B tool tests)

### Phase C: External MCP + Analytics (Week 3) - COMPLETE

✅ **COMPLETED 2026-01-10** - Implemented as BaseTool pattern with MCP placeholders.

| Task | Target Agents | Effort | Status |
|------|---------------|--------|--------|
| Implement `AnalyticsTool` (get_analytics) | P3, D3, L1, W1, W2 | 3h | ✅ Done |
| Implement `AnonymizerTool` (anonymize_data) | Learning pipeline | 2h | ✅ Done |
| Implement `AdPlatformTool` (Meta/Google MCP wrapper) | P1, P2, P3, D3 | 2h | ✅ Done |
| Implement `CalendarTool` (Calendar MCP wrapper) | D1 | 2h | ✅ Done |
| Wire tools to agents | 4 crews | 1h | ✅ Done |
| Add unit tests | - | 1h | ✅ Done |

**Tools wired to agents**:
- D1: CalendarTool
- D3: AnalyticsTool + AdPlatformTool
- W1, W2: AnalyticsTool
- P1, P2: AdPlatformTool
- P3: AnalyticsTool + AdPlatformTool
- L1: AnalyticsTool

**Tests**: 632 passing (42 new Phase C tool tests)

### Phase D: LLM-Based Tools + Final Integration (Week 4) - COMPLETE

✅ **COMPLETED 2026-01-10** - LLM-based tools for structured output + governance wiring.

| Task | Target Agents | Effort | Status |
|------|---------------|--------|--------|
| Implement `CanvasBuilderTool` | V1, V2, V3 | 2h | ✅ Done |
| Implement `TestCardTool` | E1 | 2h | ✅ Done |
| Implement `LearningCardTool` | E1, D4 | 2h | ✅ Done |
| Wire AnonymizerTool to G2 | G2 x3 governance crews | 1h | ✅ Done |
| Add unit tests | - | 2h | ✅ Done |

**Tools wired to agents**:
- V1, V2, V3: CanvasBuilderTool
- E1: TestCardTool + LearningCardTool
- D4: LearningCardTool (added)
- G2 (Desirability, Feasibility, Viability): AnonymizerTool

**Tests**: 678 passing (46 new Phase D tool tests)

---

## Immediate Actions (Unblocks Everything)

✅ **COMPLETED 2026-01-09** - All immediate actions done.

| Action | Effort | Status |
|--------|--------|--------|
| Migrate tools from `intake_crew/tools/` to `shared/tools/` | 1h | ✅ Done |
| Add MCP deps to Modal image (`mcp`, `fastmcp`, `mcp_use`) | 15m | ✅ Done |
| Wire TavilySearchTool to D2, J1, PAIN_RES, GAIN_RES | 2h | ✅ Done |
| Apply IntakeCrew pattern to all 45 agents | 4h | ✅ Done |

**Tools wired**:
- TavilySearchTool: D2, J1, PAIN_RES, GAIN_RES (4 research agents)
- MethodologyCheckTool: FIT_SCORE, G1 across 4 governance crews (5 QA agents)

**Next**: Phase A - Core MCP Server (15 hours)

---

## Live Testing Progress (With Tools)

> **Session 3 (2026-01-10)**: StartupAI dogfood run - Bug #9 pivot fix verified!
> **Run ID**: `e3368f64-89e9-49c0-8d42-d5cbc16f8eeb`

See [modal-live-testing.md](./modal-live-testing.md) for full details.

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 0 (Onboarding) | ✅ PASSED | StartupAI Founder's Brief, 85% confidence |
| Phase 1 (VPC Discovery) | ✅ PASSED | Fit score 70/100, Non-Technical Founders |
| Phase 2 (Desirability) | ✅ PASSED | NO_INTEREST → Segment pivot triggered |
| Phase 1 (Pivot) | ✅ PASSED | Fit score 78/100 (improved!) |
| Phase 2 (Retry) | ✅ PASSED | Bug #9 verified - 2nd pivot checkpoint OK |
| Phase 3 (Feasibility) | ⏳ Pending | Awaiting pivot decision |
| Phase 4 (Viability) | ⏳ Pending | - |

**Bug #9 Verification**: Two `approve_segment_pivot` checkpoints created successfully without duplicate key error.

### Issues Found and Fixed

| # | Issue | Status | Commit |
|---|-------|--------|--------|
| 7 | JobType enum missing 'supporting' | ✅ Fixed | `359abd2` |
| 8 | GainRelevance enum missing 'expected' | ✅ Fixed | `359abd2` |
| 9 | HITL duplicate key constraint | ✅ Fixed | See current commit |
| 10 | AnalyticsTool input type mismatch | ✅ Fixed | `623322a` |
| 11 | Segment alternatives silent failure | ✅ Fixed | `623322a` |
| 12 | DesirabilityEvidence JSON parsing | ✅ Fixed | `623322a` |

---

## Blockers

✅ **ALL BLOCKERS RESOLVED** (2026-01-10)

| Blocker | Resolution | Date |
|---------|------------|------|
| Tool Migration | Tools migrated to `shared/tools/` | 2026-01-09 |
| MCP Dependencies | Packages added to Modal image | 2026-01-09 |
| Agent Configuration | IntakeCrew pattern applied to all 45 agents | 2026-01-09 |
| Tool Wiring | All 15 tools wired to 35+ agents | 2026-01-10 |

---

## Previous Work (ARCHIVED)

### Legacy 3-Crew Workaround (ARCHIVED - 2025-12-05)

The 3-crew workaround was replaced by Modal serverless. See [ADR-002](../adr/002-modal-serverless-migration.md).

- Crew 1 (Intake): Archived to `archive/amp-deployment/`
- Crew 2 (Validation): Separate repo archived
- Crew 3 (Decision): Separate repo archived

### Flow Architecture (DEPRECATED - 2025-12-03)

The original Flow-based architecture had runtime bugs that were fixed before the Modal migration. All fixes are preserved in the current Modal implementation.

---

## How to Use This Document

1. **Pick a task** from Phase A above (start with immediate actions)
2. **Update status** when you start work
3. **Move to done.md** when complete
4. **Update phases.md** checkboxes to match

---
**Last Updated**: 2026-01-10 22:00

**Latest Changes**:
- **ASSET GENERATION SPECS COMPLETE** (2026-01-10 22:00)
  - Blueprint Pattern for landing pages (9 components, 20 icons)
  - Progressive Image Resolution (Unsplash → AI on demand)
  - Ad Creative Visuals with platform-specific specs
  - Ad Platform Specifications Library (Meta, Google, LinkedIn, TikTok)
  - New reference docs: `ad-platform-specifications.md`, `observability-architecture.md`
- **PLAN AUDIT COMPLETE** (2026-01-10 20:00)
  - Audited all 4 plans from ~/.claude/plans/ created today
  - `swirling-dancing-kay.md` (Landing Page Migration) - ✅ IMPLEMENTED
  - `effervescent-swimming-hollerith.md` (Schema Alignment) - ✅ P0 COMPLETE, P1-P3 deferred
  - `steady-scribbling-kahan.md` (Customer Research Tools) - ✅ IMPLEMENTED (part of larger tool work)
  - `merry-prancing-spark.md` (Architecture Docs) - ⏸️ DEFERRED (24-32h strategic backlog)
  - Updated roadmap.md, phases.md, in-progress.md to align with reality
- **F2/F3 TRACING INVESTIGATION** (2026-01-10)
  - Modal Developer investigated placeholder HTML issue from E2E test
  - Root cause: Missing `output_pydantic` schemas + insufficient crew logging
  - Tracing gaps identified: BuildCrew outputs not logged, no task callbacks
  - P0 fixes documented: Add structured outputs, add BuildCrew logging
  - See "Backlog: F2/F3 Placeholder HTML & Tracing Gaps" section above
- **LANDING PAGE STORAGE MIGRATION COMPLETE** (2026-01-10)
  - ADR-003: Migrated from Netlify API to Supabase Storage
  - `LandingPageDeploymentTool` rewritten for Supabase Storage (~150 lines vs 522)
  - Migration 009 applied: landing_page_variants, lp_submissions, lp_pageviews tables
  - E2E tested: Storage pipeline works, placeholder content is agent issue
  - 34 tests passing, Netlify implementation archived
- **BUG #9 VERIFIED** (2026-01-10 18:07)
  - StartupAI dogfood run completed Phase 0-2 with pivot
  - Two `approve_segment_pivot` checkpoints created without duplicate key error
  - Pivot workflow functioning correctly
  - Run ID: `e3368f64-89e9-49c0-8d42-d5cbc16f8eeb`
- **4 CRITICAL ISSUES RESOLVED** (2026-01-10)
  - Bug #9: HITL duplicate key - expire pending before insert
  - Tool Gap: F1, F2, F3, G3 agents now have tools (was 56% → 100%)
  - Timeout: Container timeout increased to 2 hours
  - RLS: Security verified - policies in place
  - 678 tests passing
  - Modal deployed with all fixes
- **PREVIOUS BUG FIXES** (2026-01-10 15:08)
  - #10: AnalyticsTool args_schema for typed input
  - #11: Segment alternatives error handling
  - #12: DesirabilityEvidence JSON parsing
- **TOOL INTEGRATION COMPLETE** (2026-01-10)
  - All 4 phases (A-D) implemented
  - 15 tools created, 35+ agents wired
  - 678 tests passing (164 new tool tests)
- **ENUM BUGS FIXED** (2026-01-10)
  - #7: JobType.SUPPORTING added (VPD 4-type model)
  - #8: GainRelevance.EXPECTED added (VPD Kano model)
