# StartupAI Validation Backlog

> **Architectural Pivot (2026-01-19)**: Phase 0 was simplified to Quick Start. Agent count: 45 → 43. See [ADR-006](../adr/006-quick-start-architecture.md).

This is not a feature list. It's a queue of **hypotheses to validate** using lean startup methodology: Build → Measure → Learn.

## How to Use This Document

1. **Pick a hypothesis** based on what you need to learn next
2. **Build the minimum** required to test it
3. **Measure the outcome** with real users
4. **Learn and decide**: Pivot or persevere
5. **Update this document** with learnings

---

## Priority 0: Tool Quality - IN PROGRESS

### Hypothesis: Tools Enable Evidence-Based Validation

> **If** we wire tools to all 43 agents with working external connections,
> **Then** agents will produce evidence-based outputs instead of hallucinations.

**Status**: ⚠️ **PARTIALLY COMPLETE** - Structure done, quality issues remain

**What's Done**:
- ✅ 15 tools created with BaseTool pattern
- ✅ 35+ agents have tools wired
- ✅ 678 tests passing

**What's Broken** (discovered 2026-01-12):

| Tool | Status | Issue |
|------|--------|-------|
| ForumSearchTool | ❌ Stub | Not implemented |
| ReviewAnalysisTool | ❌ Stub | Not implemented |
| SocialListeningTool | ❌ Stub | Not implemented |
| TrendAnalysisTool | ❌ Stub | Not implemented |
| TranscriptionTool | ❌ Stub | No Whisper API |
| CalendarTool | ❌ Stub | Generates fake slots |
| AdPlatformTool | ❌ Blocked | No Meta/Google API integration |
| LandingPageGeneratorTool | ⚠️ Quality | Generates placeholder HTML |

**Working Tools** (4 of 15):
- TavilySearchTool ✅
- LandingPageDeploymentTool ✅
- AnalyticsTool ✅
- AnonymizerTool ✅

**Measure** (PARTIALLY VALIDATED):
- [x] All 4 phases complete: 15 tools implemented
- [x] 35+ agents now have tools wired
- [x] 678 tests passing
- [ ] Phase 1 VPC Discovery uses real search data → Only Tavily works
- [ ] Phase 2 Desirability deploys real landing pages → Placeholder HTML
- [ ] Fit scores based on evidence, not LLM synthesis → Mostly hallucinated

**Learn**:
- Tests pass but don't verify external API connections
- Tool "completion" ≠ tool "quality"
- Many agents still hallucinate due to stub tools

**Next Actions**:
1. Fix F2 placeholder HTML (add output_pydantic)
2. Decide on AdPlatform strategy (implement APIs or remove)
3. Implement or remove stub tools

**Two-Layer Onboarding** (implemented 2026-01-13):
- ✅ O1 renamed to "Interview Gap Analyzer"
- ✅ Full conversation_transcript passed to Modal
- ✅ Consultant path now triggers Modal validation
- ⏳ Pending: Deploy to Modal and test

**Agent Wiring Gaps** (updated 2026-01-19 for Quick Start):

| Phase | Agents with `tools=[]` | Impact |
|-------|------------------------|--------|
| 0 | None (Quick Start has no agents) | No AI in Phase 0 |
| 1 | GV1, S1 (BriefGenerationCrew), CP2, CP4, CP6, FA2 (rankers) | Brief generation uses pure LLM (by design) |
| 3 | FB1, FB2, FB3 (all 3) | **Feasibility assessed without research** |
| 4 | F2, F3, SY1, SY2, SY3, VGV3 (6) | Synthesis without learning capture |

**Priority Wiring**:
1. **P1**: Phase 3 FeasibilityBuildCrew - needs research capability
2. **P2**: Phase 4 SynthesisCrew - needs LearningCardTool
3. **P3**: Ranker agents - could use AnalyticsTool for evidence-based ranking

---

## Priority 1: E2E Validation

### Hypothesis: Full Pipeline Produces Actionable Results

> **If** we complete Phase 0-4 live testing with working tools,
> **Then** users will receive actionable pivot/proceed recommendations backed by evidence.

**Status**: ⚠️ BLOCKED by tool quality issues

**Current State**:
- Phase 0-2 tested, but results are disappointing
- Every run shows NO_INTEREST signal
- Validation metrics: Zombie Ratio 80-90%, Problem Resonance 5-18%
- Cannot determine if metrics are real or hallucinated

**Build Required**:
- [x] Modal deployed with tools
- [x] Phase 0-2 tested
- [ ] **Fix tool quality issues** (Priority 0)
- [ ] Investigate validation metrics (real vs hallucinated?)
- [ ] Complete Phase 3 (Feasibility) live testing
- [ ] Complete Phase 4 (Viability) live testing

**Measure**:
- [ ] Full Phase 0→4 cycle completes successfully
- [ ] At least one run shows STRONG_COMMITMENT signal
- [ ] Pivot/proceed decision based on real evidence

---

## Priority 2: Product App Integration

### Hypothesis: Users Complete Analysis

> **If** we provide an end-to-end flow from onboarding to analysis results display,
> **Then** users will complete the full analysis and find value in the output.

**Status**: ✅ MOSTLY COMPLETE - Core UI wired, results view uses existing components

**Current State** (verified 2026-01-13):

| Layer | Status | Details |
|-------|--------|---------|
| `/api/analyze` → Modal `/kickoff` | ✅ Wired | `createModalClient().kickoff()` works |
| `/api/crewai/status` → Modal `/status` | ✅ Wired | Polling works |
| `PATCH /api/approvals/[id]` → Modal `/hitl/approve` | ✅ Wired | HITL decisions work |
| Webhook receives progress | ✅ Wired | Inserts into `validation_progress` |
| Approvals UI + Realtime | ✅ Wired | `/approvals` shows HITL requests |
| Progress UI + Realtime | ✅ Wired | `useValidationProgress` hook with Realtime |
| Progress timeline component | ✅ Wired | `ValidationProgressTimeline` component |
| Validation results display | ✅ Wired | Uses existing `VPCReportViewer` + `InnovationPhysicsPanel` |

**Build Required** (Product App repo):
- [x] Wire onboarding complete → Modal `/kickoff`
- [x] Display HITL approval UI
- [x] Add Realtime subscription to `validation_progress`
- [x] Create progress timeline component showing crew/agent/task progress
- [x] Create validation results view showing final outputs (VPC, evidence, signals)
- [ ] **Wire evidence explorer** to display validation evidence (uses existing component)

---

## ✅ COMPLETED HYPOTHESES

### Hypothesis: Modal Serverless Enables Scale ✅ VALIDATED

> **If** we deploy to Modal serverless with checkpoint-and-resume HITL pattern,
> **Then** we achieve $0 idle costs, platform independence, and simplified deployment.

**Status**: ✅ COMPLETE - Modal is production architecture

---

### Hypothesis: Multi-Crew System Enables Scale ✅ VALIDATED

> **If** we structure validation as 4 Flows with 14 Crews and 43 Agents,
> **Then** we can deliver higher quality analysis with clear accountability.

**Status**: ✅ COMPLETE - Architecture implemented (updated for Quick Start pivot)

---

### Hypothesis: HITL Approvals Prevent Bad Outcomes ✅ IMPLEMENTED

> **If** we require human approval for high-risk actions,
> **Then** users will trust the system with more autonomous operation.

**Status**: ✅ BACKEND COMPLETE - Frontend UI pending

---

## Deprioritized (Revisit Later)

- **Real-time Streaming** - Unclear if wanted
- **Advanced Market Data APIs** - Start with Tavily first
- **Public Activity/Metrics APIs** - Need production traffic first

---

## Learnings Log

| Date | Hypothesis | Outcome | Learning | Decision |
|------|------------|---------|----------|----------|
| 2026-01-13 | Tool Quality | ⚠️ Partial | 4/15 tools actually work, rest are stubs | Fix quality issues |
| 2026-01-10 | Tool Integration | Structure done | 15 tools wired, but quality not validated | Test with real APIs |
| 2026-01-08 | Modal serverless | ✅ Validated | $0 idle, single repo | Production architecture |
| 2026-01-07 | Architecture | ✅ Validated | 5 Flows, 14 Crews canonical | Proceed |

---

## Implementation Status Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Modal Infrastructure | ✅ Complete | Production deployment live |
| 14 Crews / 43 Agents | ✅ Complete | Structure complete (Quick Start pivot) |
| 10 HITL Checkpoints | ✅ Complete | All operational (Phase 0 has no HITL) |
| Tool Wiring | ✅ Complete | 15 tools attached to agents |
| **Tool Quality** | ⚠️ **Issues** | 4/15 tools work, 7 stubs, 4 quality issues |
| Live Testing Phase 0-2 | ⚠️ Complete | Results disappointing |
| Live Testing Phase 3-4 | ⏳ Blocked | Blocked by tool quality |
| Product App Integration | ⏳ Blocked | Blocked by E2E validation |

---

**Last Updated**: 2026-01-19

**Latest Changes**:
- Updated for Quick Start architectural pivot (ADR-006)
- Agent count: 45 → 43 (O1, GV2 deleted)
- Flow count: 5 → 4 (OnboardingFlow deleted)
- Phase 0 now has no AI, no agents, no HITL
- Downgraded "Tool Integration" from COMPLETE to PARTIALLY COMPLETE
- Added honest assessment of tool quality issues
- Updated status to reflect 4/15 tools actually working
- Added learning about tests not verifying external connections
