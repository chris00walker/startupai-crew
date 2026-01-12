---
purpose: "Private technical source of truth for engineering roadmap"
status: "active"
last_reviewed: "2026-01-10"
last_audit: "2026-01-10 - Plan audit complete, roadmap aligned with reality"
---

# Roadmap

> **Implementation Blueprint**: `docs/master-architecture/` is the authoritative specification. Tool integration specs in `reference/tool-specifications.md` and `reference/tool-mapping.md`.

## Current Quarter: Q1 2026

**Theme**: Production Validation & Evidence Quality

| Priority | Deliverable | Status |
|----------|-------------|--------|
| P0 | Complete Phase 3-4 live testing | ⏳ In progress (Phase 0-2 complete) |
| P0 | Fix F2/F3 placeholder HTML issue | 🔴 Backlog (agent content quality) |
| P1 | Schema Alignment P1-P3 | ⏳ Planned (VPD tables) |
| P2 | Architecture Documentation Refactoring | ⏸️ Deferred (24-32h strategic) |

### What's COMPLETE (2026-01-10)

| Deliverable | Status | Notes |
|-------------|--------|-------|
| Tool Integration (Phases A-D) | ✅ Complete | 15 tools, 35+ agents, 681 tests |
| Landing Page Migration (ADR-003) | ✅ Complete | Supabase Storage, E2E verified |
| Schema Alignment P0 | ✅ Complete | Modal tables deployed |
| Bug Fixes #7-12 | ✅ Complete | All resolved |
| Live Testing Phase 0-2 | ✅ Complete | Pivot workflow verified |

## Quarterly Themes

| Quarter | Theme | Key Deliverables |
|---------|-------|------------------|
| **Q1 2026** | Production Validation | Complete Phase 3-4, fix agent quality, production users |
| Q2 2026 | Production Hardening | Ad platform integration, real experiments, analytics |
| Q3 2026 | Flywheel Optimization | Outcome feedback loop, retrieval tuning, learning metrics |
| Q4 2026 | Scale & Enterprise | Multi-tenant, advanced analytics, compliance |

## Q1 2026 Breakdown

### January Week 2 (Current - 2026-01-10)

| Focus | Deliverables | Status |
|-------|--------------|--------|
| Tool Integration | 15 tools wired to 35+ agents (BaseTool pattern) | ✅ Complete |
| Landing Pages | Supabase Storage migration (ADR-003) | ✅ Complete |
| Bug Fixes | #7-12 (enum bugs, HITL duplicate key, tool input types) | ✅ Complete |
| Live Testing | Phase 0-2 with pivot scenario | ✅ Complete |
| **Phase 3-4** | Feasibility + Viability live testing | ⏳ Next |

### January Week 3 (Next)

| Focus | Deliverables | Status |
|-------|--------------|--------|
| Phase 3-4 Live Testing | Complete validation through Viability | ⏳ Planned |
| F2/F3 Quality Fix | Add `output_pydantic` schemas for real HTML | ⏳ Planned |
| Production Cutover | First real user validation | ⏳ Planned |

### February: Production Users

| Week | Focus | Deliverables |
|------|-------|--------------|
| 1-2 | First Production Users | Real validation runs with paying customers |
| 3-4 | Quality Iteration | Fix issues discovered in production |

### March: Hardening

| Week | Focus | Deliverables |
|------|-------|--------------|
| 1-2 | Error Handling | Tool failures, retry logic, observability |
| 3-4 | Architecture Docs | Master architecture refactoring (deferred from Jan) |

## Competitive Moat: Flywheel Learning

Every validation run makes all 6 AI Founders smarter through shared, anonymized learnings.

**Spec**: See `docs/master-architecture/reference/flywheel-learning.md`

**Current Status**: Tools implemented (LearningCaptureTool, LearningRetrievalTool), database tables deployed. First real learning capture pending Phase 3-4 completion.

## Architecture Milestones

| Milestone | Date | Status |
|-----------|------|--------|
| Modal infrastructure deployed | 2026-01-08 | ✅ Complete |
| 14 crews / 45 agents implemented | 2026-01-08 | ✅ Complete |
| Live testing Phase 0-2 | 2026-01-09 | ✅ Complete |
| Tool integration (15 tools) | 2026-01-10 | ✅ Complete |
| Landing page migration (ADR-003) | 2026-01-10 | ✅ Complete |
| Schema alignment P0 | 2026-01-10 | ✅ Complete |
| Bug fixes #7-12 | 2026-01-10 | ✅ Complete |
| **Live testing Phase 3-4** | TBD | ⏳ In progress |
| **Production cutover** | TBD | ⏳ Blocked by Phase 3-4 |

## Previous Milestones (Completed)

| Milestone | Date | Notes |
|-----------|------|-------|
| AMP 3-Crew deployment | 2026-01-04 | Deprecated, replaced by Modal |
| Crew 1 best practices | 2026-01-06 | IntakeCrew pattern established |
| Architecture alignment | 2026-01-07 | 5 Flows, 14 Crews, 45 Agents canonical |
| Modal migration decision | 2026-01-08 | ADR-002 approved |
| MCP architecture designed | 2026-01-09 | Implemented as BaseTool pattern instead |

## Deferred Work (Strategic Backlog)

| Item | Est. Effort | Reason Deferred | Original Plan |
|------|-------------|-----------------|---------------|
| Architecture Documentation Refactoring | 24-32h | Production validation takes priority | `merry-prancing-spark.md` |
| Schema Alignment P1-P3 | 8-12h | P0 (Modal tables) sufficient for MVP | `effervescent-swimming-hollerith.md` |

---

Roadmap is reviewed monthly with product + marketing. Update deliverables once backlog items graduate into committed work.

**Last Updated**: 2026-01-10

**Changes (2026-01-10 - Plan Audit)**:
- Updated milestone table with actual completion dates
- Marked tool integration as COMPLETE (was "Ready to start")
- Added landing page migration and schema alignment milestones
- Added "Deferred Work" section to track strategic backlog
- Changed theme from "Tool Integration" to "Production Validation" (tools done)
- Updated Q1 breakdown to reflect current week's progress
