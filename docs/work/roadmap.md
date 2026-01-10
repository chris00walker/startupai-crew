---
purpose: "Private technical source of truth for engineering roadmap"
status: "active"
last_reviewed: "2026-01-09"
---

# Roadmap

> **Implementation Blueprint**: `docs/master-architecture/` is the authoritative specification. Tool integration specs in `reference/tool-specifications.md` and `reference/tool-mapping.md`.

## Current Quarter: Q1 2026

**Theme**: Tool Integration & Evidence-Based Validation

| Priority | Deliverable | Status |
|----------|-------------|--------|
| P0 | MCP-First Tool Architecture (60h) | Ready for implementation |
| P0 | Complete Phase 3-4 live testing | In progress |
| P1 | E2E validation with real tools | Blocked by P0 |
| P2 | Product App results display | Blocked by P1 |

## Quarterly Themes

| Quarter | Theme | Key Deliverables |
|---------|-------|------------------|
| **Q1 2026** | Tool Integration | MCP server, 33 tools wired, evidence-based validation |
| Q2 2026 | Production Hardening | Ad platform integration, real experiments, analytics |
| Q3 2026 | Flywheel Optimization | Outcome feedback loop, retrieval tuning, learning metrics |
| Q4 2026 | Scale & Enterprise | Multi-tenant, advanced analytics, compliance |

## Q1 2026 Breakdown

### January: Foundation (Current)

| Week | Focus | Deliverables |
|------|-------|--------------|
| 1 | Core MCP Server | FastMCP on Modal + research tools |
| 2 | Advanced Tools | Transcription, NLP, A/B testing |
| 3 | External MCP | Ad platforms, analytics, calendar |
| 4 | CrewAI Wiring | All 36 agents equipped |

### February: Validation

| Week | Focus | Deliverables |
|------|-------|--------------|
| 1-2 | E2E Testing | Full Phase 0→4 with real tools |
| 3-4 | Product Integration | Results display in Product App |

### March: Hardening

| Week | Focus | Deliverables |
|------|-------|--------------|
| 1-2 | Error Handling | Tool failures, retry logic |
| 3-4 | Observability | Tool call logging, metrics dashboard |

## Competitive Moat: Flywheel Learning

Every validation run makes all 6 AI Founders smarter through shared, anonymized learnings.

**Spec**: See `docs/master-architecture/reference/flywheel-learning.md`

**Current Status**: Tools implemented (LearningCaptureTool, LearningRetrievalTool), database tables deployed, but not yet actively collecting real validation data.

## Architecture Milestones

| Milestone | Date | Status |
|-----------|------|--------|
| Modal infrastructure deployed | 2026-01-08 | ✅ Complete |
| 14 crews / 45 agents implemented | 2026-01-08 | ✅ Complete |
| Live testing Phase 0-2 | 2026-01-09 | ✅ Complete |
| MCP architecture designed | 2026-01-09 | ✅ Complete |
| Tool integration complete | TBD | ⏳ Ready to start |
| E2E with real evidence | TBD | ⏳ Blocked |
| Production cutover | TBD | ⏳ Blocked |

## Previous Milestones (Completed)

| Milestone | Date | Notes |
|-----------|------|-------|
| AMP 3-Crew deployment | 2026-01-04 | Deprecated, replaced by Modal |
| Crew 1 best practices | 2026-01-06 | IntakeCrew pattern established |
| Architecture alignment | 2026-01-07 | 5 Flows, 14 Crews, 45 Agents canonical |
| Modal migration decision | 2026-01-08 | ADR-002 approved |

---

Roadmap is reviewed monthly with product + marketing. Update deliverables once backlog items graduate into committed work.

**Last Updated**: 2026-01-09
