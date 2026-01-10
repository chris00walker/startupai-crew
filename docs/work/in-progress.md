---
purpose: "Private technical source of truth for active work"
status: "active"
last_reviewed: "2026-01-09"
---

# In Progress

## Architecture Status (2026-01-09)

**CURRENT**: Modal serverless deployed to production. Tool integration ready for implementation.

| Layer | Status | Notes |
|-------|--------|-------|
| Interaction (Netlify) | ✅ Production | Edge Functions |
| Orchestration (Supabase) | ✅ Production | PostgreSQL + Realtime |
| Compute (Modal) | ✅ Production | Pay-per-second, $0 idle |
| **Tool Integration** | 🟡 IN PROGRESS | 20/45 agents wired with tools |

**ADR**: See [ADR-002](../adr/002-modal-serverless-migration.md) for architecture.

---

## Active Work: MCP-First Tool Integration

**Status**: READY FOR IMPLEMENTATION
**Total Effort**: 60 hours over 4 weeks
**Designed**: 2026-01-09

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

### Phase C: External MCP + Analytics (Week 3) - 13 hours

| Task | Target Agents | Effort | Status |
|------|---------------|--------|--------|
| Implement `get_analytics` | P3, D3, L1, W1, W2 | 3h | ⏳ Not started |
| Implement `anonymize_data` | Learning pipeline | 2h | ⏳ Not started |
| Connect Meta Ads MCP | P1, P2, P3, D3 | 2h | ⏳ Not started |
| Connect Google Ads MCP | P1, P2, P3 | 2h | ⏳ Not started |
| Connect Calendar MCP | D1 | 2h | ⏳ Not started |
| Integration testing | All | 4h | ⏳ Not started |

**Deliverable**: Ad platforms and analytics connected via MCP

### Phase D: CrewAI Integration (Week 4) - 18 hours

| Task | Target Agents | Effort | Status |
|------|---------------|--------|--------|
| Wire EXISTS tools | All phases | 4h | ⏳ Not started |
| Add MCP client to agents | All phases | 4h | ⏳ Not started |
| Build LLM-Based tools | O1, E1, V1-V3, C2 | 4h | ⏳ Not started |
| End-to-end testing | All | 4h | ⏳ Not started |
| Documentation | - | 2h | ⏳ Not started |

**Deliverable**: All 36 tool-equipped agents wired with evidence collection tools

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

See [modal-live-testing.md](./modal-live-testing.md) for full details.

| Phase | Status | Issues Found | Issues Fixed |
|-------|--------|--------------|--------------|
| Phase 0 (Onboarding) | ✅ PASSED | 1 | 1 |
| Phase 1 (VPC Discovery) | ✅ PASSED | 2 | 2 |
| Phase 2 (Desirability) | ✅ PASSED | 2 | 2 |
| Phase 3 (Feasibility) | ⏳ Pending | - | - |
| Phase 4 (Viability) | ⏳ Pending | - | - |

---

## Blockers

### Blocker 1: Tool Migration (CRITICAL)

**Status**: Tools exist in `src/intake_crew/tools/` but not migrated to `src/shared/tools/`
**Impact**: Cannot wire tools to Modal crews
**Resolution**: 1 hour to copy files + update imports
**Priority**: CRITICAL (unblocks all tool integration)

### Blocker 2: MCP Dependencies

**Status**: Modal image lacks `mcp`, `mcp_use`, `fastmcp` packages
**Impact**: Cannot connect to MCP servers
**Resolution**: 15 minutes to update image definition
**Priority**: HIGH (required for MCP Custom/External tools)

### Blocker 3: Agent Configuration Pattern

**Status**: Agents lack `tools=[]` parameter in 36 of 45 cases
**Impact**: Tools cannot be assigned
**Resolution**: 4 hours to apply "IntakeCrew Pattern" to all agents
**Priority**: HIGH (prerequisite for tool wiring)

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
- Phase B Advanced Tools COMPLETE (2026-01-10)
  - TranscriptionTool, InsightExtractorTool, BehaviorPatternTool, ABTestTool
  - 7 agents wired with new tools (D1, D2, D3, D4, P1, P2, W1)
  - 590 tests passing (35 new)
- Phase A Customer Research Tools COMPLETE (2026-01-10)
- Complete rewrite for Modal serverless architecture
- Added MCP-first tool integration roadmap (60 hours)
- Updated live testing progress (Phase 0-2 complete)
