---
purpose: "Cross-repository dependency tracking for coordinated delivery"
status: "active"
last_reviewed: "2025-11-26"
---

# Cross-Repository Blockers

This document tracks dependencies between StartupAI repositories to ensure coordinated delivery.

## Marketing Promise Gap (Critical)

The marketing site makes promises that require technical capabilities not yet built. This represents the **work to be done** to deliver on marketing promises.

| Gap | Description | Impact |
|-----|-------------|--------|
| MVP Building | Marketing promises "working software in days" | No code generation capability exists |
| Real Ad Spend | Marketing promises $450-525 ad budget execution | No Meta/Google Ads API integration |
| Real User Testing | Marketing promises "test with real customers" | No analytics or experiment framework |
| Unit Economics | Marketing promises CAC/LTV analysis | Finance Crew outputs are LLM-generated fiction |
| Evidence-Based | Marketing promises data-driven validation | All crew outputs are synthetic, not real data |

### Capabilities Required to Close Gap

1. **MVP Generation**: Code scaffolding, template deployment, GitHub integration
2. **Ad Platform Integration**: Meta Business API, Google Ads API for real campaigns
3. **Analytics Integration**: Real user tracking, conversion measurement
4. **Financial Modeling**: Connect to real cost/revenue data, not LLM generation
5. **Web Research Tools**: Competitor research APIs, market data sources

---

## This Repo Blocks

### Product App (`app.startupai.site`)

| Blocker | Status | Description | Unblocks |
|---------|--------|-------------|----------|
| Phase 1 Completion | ⚠️ Partial | Flow works, outputs are synthetic | Product can display results (quality is fiction) |
| Results → Supabase | Not Started | Persist to `entrepreneur_briefs`, `analysis_results` tables | Product app can display analysis results |
| Real Analysis Tools | Not Started | Tools for web research, data retrieval | Outputs transition from synthetic to real |
| Flywheel Learning Schema | Not Started | SQL for `learnings`, `patterns`, `outcomes`, `domain_expertise` tables | Learning tools can persist/query |
| Resume/Webhook API | Not Started | `POST /resume` with `human_feedback` for HITL | Product approval UI |

**Specific API Endpoints Needed:**
- `POST /kickoff` - Already working
- `GET /status/{id}` - Already working
- `POST /resume` - For approval workflows (per `reference/approval-workflows.md`)
- Webhook to `https://app.startupai.site/api/approvals/webhook` - Push notifications

**Flywheel Learning Tables Needed:**
- Schema: See `docs/master-architecture/reference/flywheel-learning.md`
- Requires pgvector extension enabled in Supabase
- Tables: `learnings`, `patterns`, `outcomes`, `domain_expertise`

### Marketing Site (`startupai.site`)

| Blocker | Status | Description | Unblocks |
|---------|--------|-------------|----------|
| Activity Feed API | Not Started | `GET /api/v1/public/activity` - agent status | Marketing transparency page |
| Metrics API | Not Started | `GET /api/v1/public/metrics` - validation counts | Marketing trust metrics |

**Note:** Marketing site can implement Netlify functions that query Supabase directly (per `reference/marketing-integration.md`) rather than waiting for CrewAI APIs. This provides an alternative unblock path.

## This Repo Blocked By

| Blocker | Source Repo | Status | Impact |
|---------|-------------|--------|--------|
| Learning tables migration | Product App | Not Started | Flywheel learning tools need pgvector tables in Supabase |

**Note**: Product app manages Supabase migrations. Learning tables schema is defined in `docs/master-architecture/reference/flywheel-learning.md`.

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
**Last Updated**: 2025-11-26

**Changes**: Added Marketing Promise Gap section documenting capabilities required to deliver on marketing claims. Updated Phase 1 status to reflect partial completion (flow works, outputs synthetic).
