---
purpose: "Cross-repository dependency tracking for coordinated delivery"
status: "active"
last_reviewed: "2025-11-21"
---

# Cross-Repository Blockers

This document tracks dependencies between StartupAI repositories to ensure coordinated delivery.

## This Repo Blocks

### Product App (`app.startupai.site`)

| Blocker | Status | Description | Unblocks |
|---------|--------|-------------|----------|
| Phase 1 Completion | In Progress | Service Crew, Analysis Crew, Governance Crew (QA), Phase 1 Flow | Product Phase Alpha results display |
| Results → Supabase | Not Started | Persist to `entrepreneur_briefs`, `analysis_results` tables | Product app can display analysis results |
| Resume/Webhook API | Not Started | `POST /resume` with `human_feedback` for HITL | Product approval UI |

**Specific API Endpoints Needed:**
- `POST /kickoff` - Already working
- `GET /status/{id}` - Already working
- `POST /resume` - For approval workflows (per `reference/approval-workflows.md`)
- Webhook to `https://app.startupai.site/api/approvals/webhook` - Push notifications

### Marketing Site (`startupai.site`)

| Blocker | Status | Description | Unblocks |
|---------|--------|-------------|----------|
| Activity Feed API | Not Started | `GET /api/v1/public/activity` - agent status | Marketing transparency page |
| Metrics API | Not Started | `GET /api/v1/public/metrics` - validation counts | Marketing trust metrics |

**Note:** Marketing site can implement Netlify functions that query Supabase directly (per `reference/marketing-integration.md`) rather than waiting for CrewAI APIs. This provides an alternative unblock path.

## This Repo Blocked By

| Blocker | Source Repo | Status | Impact |
|---------|-------------|--------|--------|
| None currently | — | — | CrewAI is upstream of all other repos |

## Coordination Notes

- **Phase 1 Complete** criteria defined in `phases.md`
- Results persistence mechanism TBD (webhook vs polling)
- Activity Feed API added to `backlog.md` per marketing dependency

## Cross-Repo Links

- Product app blockers: `app.startupai.site/docs/work/cross-repo-blockers.md`
- Marketing blockers: `startupai.site/docs/work/cross-repo-blockers.md`
- Master architecture: `docs/master-architecture/01-ecosystem.md`
- API contracts: `docs/master-architecture/reference/api-contracts.md`
- Approval workflows: `docs/master-architecture/reference/approval-workflows.md`

---
**Last Updated**: 2025-11-21
