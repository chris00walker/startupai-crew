---
purpose: "Private technical source of truth for active work"
status: "active"
last_reviewed: "2026-01-10"
---

# In Progress

## Architecture Status (2026-01-10)

**CURRENT**: Tool integration Phases A-D complete (15 tools, 35+ agents). Modal redeploy + Phase 0-4 revalidation pending.

| Layer | Status | Notes |
|-------|--------|-------|
| Interaction (Netlify) | ✅ Production | Edge Functions |
| Orchestration (Supabase) | ✅ Production | PostgreSQL + Realtime + Modal tables |
| Compute (Modal) | ⚠️ Stale | Deployed code predates tool integration |
| **Tool Integration** | ✅ Code Complete | 15 tools wired to 35+ agents. Modal redeploy pending. |

**ADR**: See [ADR-002](../adr/002-modal-serverless-migration.md) for architecture.

---

## Active Work: Modal Redeploy + Phase 0-4 Revalidation

**Status**: ⏳ IN PROGRESS
**Blocker**: Modal deployment has stale code (predates tool integration)
**Next**: Deploy tool-wired code to Modal, run Phase 0 live test

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

## Live Testing Progress

> **Important**: Live testing Phase 0-2 (2026-01-09) predates tool integration (2026-01-10).
> Tools are wired in code but not yet deployed to Modal or validated in live testing.
> **Next step**: Modal redeploy + Phase 0-4 revalidation with integrated tools.

See [modal-live-testing.md](./modal-live-testing.md) for full details.

| Phase | Status | Issues Found | Issues Fixed |
|-------|--------|--------------|--------------|
| Phase 0 (Onboarding) | ⚠️ Revalidate | 1 | 1 |
| Phase 1 (VPC Discovery) | ⚠️ Revalidate | 2 | 2 |
| Phase 2 (Desirability) | ⚠️ Revalidate | 2 | 2 |
| Phase 3 (Feasibility) | ⏳ Pending | - | - |
| Phase 4 (Viability) | ⏳ Pending | - | - |

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
- **TOOL INTEGRATION COMPLETE** (2026-01-10)
  - All 4 phases (A-D) implemented
  - 15 tools created, 35+ agents wired
  - 678 tests passing (164 new tool tests)
- Phase D LLM-Based Tools COMPLETE (2026-01-10)
  - CanvasBuilderTool, TestCardTool, LearningCardTool
  - AnonymizerTool wired to G2 governance agents
  - 46 new tests
- Phase C Analytics & Privacy Tools COMPLETE (2026-01-10)
  - AnalyticsTool, AnonymizerTool, AdPlatformTool, CalendarTool
  - 42 new tests
- Phase B Advanced Tools COMPLETE (2026-01-10)
  - TranscriptionTool, InsightExtractorTool, BehaviorPatternTool, ABTestTool
  - 35 new tests
- Phase A Customer Research Tools COMPLETE (2026-01-10)
  - ForumSearchTool, ReviewAnalysisTool, SocialListeningTool, TrendAnalysisTool
  - 41 new tests
