# StartupAI Validation Backlog

This is not a feature list. It's a queue of **hypotheses to validate** using lean startup methodology: Build → Measure → Learn.

## How to Use This Document

1. **Pick a hypothesis** based on what you need to learn next
2. **Build the minimum** required to test it
3. **Measure the outcome** with real users
4. **Learn and decide**: Pivot or persevere
5. **Update this document** with learnings

---

## Priority 0: Tool Integration (CRITICAL)

### Hypothesis: Tools Enable Evidence-Based Validation

> **If** we wire tools to all 45 agents using MCP-first architecture,
> **Then** agents will produce evidence-based outputs instead of hallucinations.

**Status**: READY FOR IMPLEMENTATION

**Problem Statement**:
- 36 of 45 agents (80%) lack tools
- Without tools, agents hallucinate: invented market research, fake competitor data, made-up unit economics
- The SAY vs DO evidence hierarchy requires real data collection

**Evidence of Problem**:
```
Current: D2 hallucinates "HR managers struggle with X" (no evidence)
Target:  D2 searches Reddit for real complaints (47 mentions found)
```

**Build Required** (60 hours):

| Phase | Focus | Effort | Status |
|-------|-------|--------|--------|
| A | Core MCP Server | 15h | Not started |
| B | Advanced Tools | 14h | Not started |
| C | External MCP + Analytics | 13h | Not started |
| D | CrewAI Wiring | 18h | Not started |

**Immediate Actions** (7 hours):
1. Migrate tools from `intake_crew/tools/` to `shared/tools/` (1h)
2. Add MCP deps to Modal image (15m)
3. Wire TavilySearchTool to research agents (2h)
4. Apply IntakeCrew pattern to all agents (4h)

**Measure**:
- [ ] All 36 tool-equipped agents have tools wired (0% → 100%)
- [ ] Phase 1 VPC Discovery uses real search data
- [ ] Phase 2 Desirability deploys real landing pages
- [ ] Fit scores based on evidence, not LLM synthesis

**Learn**:
- Does real data change validation outcomes?
- What's the quality difference between hallucinated vs evidence-based outputs?

---

## Priority 1: E2E Validation

### Hypothesis: Full Pipeline Produces Actionable Results

> **If** we complete Phase 3-4 live testing and tool integration,
> **Then** users will receive actionable pivot/proceed recommendations backed by evidence.

**Status**: BLOCKED by Priority 0 (tool integration)

**Build Required**:
- [ ] Complete Phase 3 (Feasibility) live testing
- [ ] Complete Phase 4 (Viability) live testing
- [ ] Test pivot loopback (approve_segment_pivot → Phase 1)
- [ ] E2E validation with tools producing real evidence

**Measure**:
- [ ] Full Phase 0→4 cycle completes successfully
- [ ] Pivot/proceed decision based on real evidence
- [ ] User can trace decision back to evidence sources

---

## Priority 2: Product App Integration

### Hypothesis: Users Complete Analysis

> **If** we provide an end-to-end flow from onboarding to analysis results display,
> **Then** users will complete the full analysis and find value in the output.

**Status**: BLOCKED by Priority 1 (E2E validation)

**Current State**:
- ✅ CrewAI Modal deployment live
- ✅ `/kickoff`, `/status`, `/hitl/approve` endpoints working
- ✅ Webhook to persist results to Supabase
- ❌ Product app doesn't call Modal endpoints yet
- ❌ Product app doesn't display validation results

**Build Required** (Product App repo):
- [ ] Wire onboarding complete → Modal `/kickoff`
- [ ] Poll `/status` for progress updates
- [ ] Display results from `validation_runs` table
- [ ] Display HITL approval UI

**Measure**:
- [ ] Completion rate: onboarding → validation results
- [ ] Time to first result
- [ ] User satisfaction with output quality

---

## ✅ COMPLETED HYPOTHESES

### Hypothesis: Modal Serverless Enables Scale ✅ VALIDATED

> **If** we deploy to Modal serverless with checkpoint-and-resume HITL pattern,
> **Then** we achieve $0 idle costs, platform independence, and simplified deployment.

**Built** (2026-01-08):
- ✅ Modal infrastructure deployed
- ✅ 14 crews, 45 agents implemented
- ✅ 10 HITL checkpoints with checkpoint-and-resume
- ✅ Supabase state persistence + Realtime
- ✅ 185 unit tests passing

**Measured**:
- ✅ $0 idle costs (vs AMP always-on)
- ✅ Single repository (vs 3-repo AMP workaround)
- ✅ Pay-per-second billing
- ✅ Live testing Phase 0-2 passed

**Learned**:
- Modal is ideal for long-running agentic workflows
- Checkpoint-and-resume pattern works well for HITL
- Three-layer architecture (Netlify + Supabase + Modal) provides clean separation

**Status**: ✅ COMPLETE - Modal is production architecture

---

### Hypothesis: Multi-Crew System Enables Scale ✅ VALIDATED

> **If** we structure validation as 5 Flows with 14 Crews and 45 Agents,
> **Then** we can deliver higher quality analysis with clear accountability.

**Built** (Phase 1-3 Complete):
- ✅ 5 Flows orchestrating 14 Crews
- ✅ 45 agents with specialized roles
- ✅ Non-linear routing with Innovation Physics
- ✅ 10 HITL checkpoints

**Measured**:
- ✅ All phases deployed to Modal
- ✅ REST API working
- ✅ 185+ tests passing

**Learned**:
- Crew specialization works well for distinct phases
- Pattern hierarchy (Phase → Flow → Crew → Agent → Task) is clear
- Router-based flow enables true non-linear iteration

**Status**: ✅ COMPLETE - All phases implemented

---

### Hypothesis: Tools Improve Analysis Quality ✅ PARTIALLY VALIDATED

> **If** we add web search, financial analysis, and deployment tools to agents,
> **Then** analysis quality will significantly improve beyond pure LLM reasoning.

**Built** (IntakeCrew only):
- ✅ TavilySearchTool wired to S2
- ✅ CustomerResearchTool wired to S2
- ✅ MethodologyCheckTool wired to G1
- ❌ Other 40+ agents still lack tools

**Measured**:
- ✅ IntakeCrew produces evidence-based research
- ❌ Modal crews produce hallucinated outputs (no tools)

**Learned**:
- Tools dramatically improve output quality
- IntakeCrew pattern is the model for all agents
- 60-hour roadmap to complete tool integration

**Status**: ⏳ 11% COMPLETE - Tool integration is Priority 0

---

### Hypothesis: HITL Approvals Prevent Bad Outcomes ✅ IMPLEMENTED

> **If** we require human approval for high-risk actions,
> **Then** users will trust the system with more autonomous operation.

**Built**:
- ✅ 10 HITL checkpoints across 5 phases
- ✅ Checkpoint-and-resume pattern on Modal
- ✅ `/hitl/approve` endpoint
- ✅ Supabase `hitl_requests` table

**Measured**:
- ✅ HITL pauses work correctly
- ✅ Resume continues from checkpoint
- ⏳ User trust - PENDING REAL USERS

**Status**: ✅ BACKEND COMPLETE - Frontend UI in Product App pending

---

## Deprioritized (Revisit Later)

### Real-time Streaming
> Users want to watch analysis happen step-by-step.

**Why deprioritized**: Unclear if wanted. Validate core value first.

### Advanced Market Data APIs
> Bloomberg, Crunchbase for competitive intelligence.

**Why deprioritized**: Start with Tavily, add expensive APIs only if needed.

### Public Activity/Metrics APIs
> Show real-time agent activity on marketing site.

**Why deprioritized**: Need production traffic first.

---

## Learnings Log

| Date | Hypothesis | Outcome | Learning | Decision |
|------|------------|---------|----------|----------|
| 2026-01-09 | MCP-first tools | Ready | Architecture designed, 60h to implement | Proceed |
| 2026-01-08 | Modal serverless | ✅ Validated | $0 idle, single repo, pay-per-second | Proceed |
| 2026-01-07 | Architecture alignment | ✅ Validated | 5 Flows, 14 Crews, 45 Agents canonical | Proceed |
| 2025-11-27 | Multi-crew system | ✅ Validated | Specialization works | Proceed |
| 2025-11-26 | HITL workflow | ✅ Validated | Checkpoint-resume works | Build frontend |

---

## Decision Framework

When choosing what to validate next, ask:

1. **What's the riskiest assumption?** Start there.
2. **What blocks other work?** Unblock it.
3. **What can we learn fastest?** Minimize build time.
4. **What has the biggest impact if true?** Maximize learning value.

**Current Priority**: **Tool Integration** is the critical blocker
- Riskiest: Will tools change validation quality?
- Blocking: All evidence-based validation
- Fastest: 7h immediate actions unblock everything
- Biggest impact: Enables real validation vs hallucination

---

## Implementation Status Summary

| Component | Status | Completion |
|-----------|--------|------------|
| Modal Infrastructure | ✅ Complete | 100% |
| 14 Crews / 45 Agents | ✅ Complete | 100% |
| 10 HITL Checkpoints | ✅ Complete | 100% |
| State Management | ✅ Complete | 100% |
| 185+ Unit Tests | ✅ Complete | 100% |
| Live Testing Phase 0-2 | ✅ Complete | 100% |
| MCP Architecture Design | ✅ Complete | 100% |
| **Tool Integration** | ❌ CRITICAL | **0%** |
| Live Testing Phase 3-4 | ⏳ Pending | 0% |
| Product App Integration | ⏳ Blocked | 0% |

---

**Last Updated**: 2026-01-09

**Latest Changes**:
- Complete rewrite for Modal serverless architecture
- Added Priority 0: Tool Integration (60h roadmap)
- Updated completed hypotheses with Modal validation
- Removed deprecated AMP references
- Updated implementation status to reflect current state
