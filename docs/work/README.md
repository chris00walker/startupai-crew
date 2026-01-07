---
purpose: "Private technical source of truth for CrewAI engineering work tracking"
status: "active"
last_reviewed: "2026-01-07"
---

# Work Tracking

**Current Status:** 3-Crew architecture DEPLOYED to AMP (~85% overall). See [phases.md](./phases.md) for details.

- Planning cadence: bi-weekly sprint planning + monthly roadmap review.
- Tracking tools: GitHub Projects (`startupai-crew` board) and linear issue labels.
- Every crew/flow change should be documented in `work/features/` with scope, test plan, checklist, and delivery notes.

## Quick Links

- [Backlog](./backlog.md) - Hypothesis queue
- [In Progress](./in-progress.md) - Active work items
- [Done](./done.md) - Recently delivered
- [Phases](./phases.md) - Engineering phases
- [Cross-Repo Blockers](./cross-repo-blockers.md) - Dependencies and downstream impacts

## Architecture Status

| Component | Status | Notes |
|-----------|--------|-------|
| 3-Crew Architecture | ✅ DEPLOYED | 19 agents, 32 tasks, 7 HITL |
| Crew 1 (Intake) | ✅ DEPLOYED | This repo, 100% CrewAI best practices |
| Crew 2 (Validation) | ✅ DEPLOYED | Separate repo |
| Crew 3 (Decision) | ✅ DEPLOYED | Separate repo |
| Crew Chaining | ✅ CONFIGURED | `InvokeCrewAIAutomationTool` |
| E2E Verification | ⚠️ PENDING | All components exist |

## Cross-Repo Coordination

This repository is **upstream** of both downstream repos. Updates here unblock:
- **Product App**: `app.startupai.site/docs/work/cross-repo-blockers.md`
- **Marketing Site**: `startupai.site/docs/work/cross-repo-blockers.md`

When completing phase milestones, update downstream blockers files to notify those repos.

## Related Documents

- [Master Architecture Status](../master-architecture/09-status.md) - Ecosystem source of truth
- [Cross-Repo Blockers](./cross-repo-blockers.md) - Dependency tracking
