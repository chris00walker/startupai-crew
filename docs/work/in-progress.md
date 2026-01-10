---
purpose: "Private technical source of truth for active work"
status: "active"
last_reviewed: "2026-01-10"
---

# In Progress

## Architecture Status (2026-01-10)

**CURRENT**: Production-ready fixes deployed. 4 critical issues resolved. Ready for Phase 2-4 validation.

| Layer | Status | Notes |
|-------|--------|-------|
| Interaction (Netlify) | ✅ Production | Edge Functions |
| Orchestration (Supabase) | ✅ Production | PostgreSQL + Realtime + Modal tables + RLS |
| Compute (Modal) | ✅ Redeployed | All fixes deployed 2026-01-10 |
| **Tool Integration** | ✅ Complete | 100% agents wired (was 56%), args_schema pattern |

**ADR**: See [ADR-002](../adr/002-modal-serverless-migration.md) for architecture.

---

## Active Work: Phase 3-4 Live Testing

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

**Files Changed**:
- `src/state/persistence.py` - Bug #9 HITL cancel logic
- `src/crews/desirability/build_crew.py` - F1, F2, F3 tools wired
- `src/crews/desirability/governance_crew.py` - G3 tool wired
- `src/modal_app/app.py` - Timeout 3600s → 7200s
- `db/migrations/008_enable_validation_runs_rls.sql` - RLS migration (already applied)

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

### AMP 3-Crew Architecture (DEPRECATED - 2025-12-05)

The 3-Crew AMP architecture was replaced by Modal serverless. See [ADR-002](../adr/002-modal-serverless-migration.md).

- Crew 1 (Intake): Archived to `archive/amp-deployment/`
- Crew 2 (Validation): Separate repo archived
- Crew 3 (Decision): Separate repo archived

### Flow Architecture (DEPRECATED - 2025-12-03)

The original Flow-based architecture had runtime bugs that were fixed before the AMP migration. All fixes are preserved in the current Modal implementation.

---

## How to Use This Document

1. **Pick a task** from Phase A above (start with immediate actions)
2. **Update status** when you start work
3. **Move to done.md** when complete
4. **Update phases.md** checkboxes to match

---
**Last Updated**: 2026-01-10

**Latest Changes**:
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
