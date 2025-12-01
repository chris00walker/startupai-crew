---
purpose: "Private technical source of truth for CrewAI Flows engineering work tracking"
status: "active"
last_reviewed: "2025-12-01"
---

# Work Tracking

**Current Status:** Phase 2D complete (~85% overall). All 8 crews implemented with 18 tools. See [phases.md](./phases.md) for details.

- Planning cadence: bi-weekly sprint planning + monthly roadmap review.
- Tracking tools: GitHub Projects (`startupai-crew` board) and linear issue labels.
- Every crew/flow change should be documented in `work/features/` with scope, test plan, checklist, and delivery notes.

## Quick Links

- [Backlog](./backlog.md) - Hypothesis queue
- [In Progress](./in-progress.md) - Active work items
- [Done](./done.md) - Recently delivered
- [Phases](./phases.md) - Engineering phases
- [Roadmap](./roadmap.md) - Strategic timeline
- [Cross-Repo Blockers](./cross-repo-blockers.md) - Dependencies and downstream impacts

## Cross-Repo Coordination

This repository is **upstream** of both downstream repos. Updates here unblock:
- **Product App**: `app.startupai.site/docs/work/cross-repo-blockers.md`
- **Marketing Site**: `startupai.site/docs/work/cross-repo-blockers.md`

When completing phase milestones, update downstream blockers files to notify those repos.
