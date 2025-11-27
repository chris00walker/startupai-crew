---
purpose: "Cross-repository dependency tracking for coordinated delivery"
status: "active"
last_reviewed: "2025-11-26"
---

# Cross-Repository Blockers

This document tracks dependencies between StartupAI repositories to ensure coordinated delivery.

## Marketing Promise Gap (Updated 2025-11-26)

The marketing site makes promises that require technical capabilities. Status after code audit:

| Gap | Description | Status |
|-----|-------------|--------|
| MVP Building | Marketing promises "working software in days" | ⚠️ LandingPageGeneratorTool + Netlify deploy exist; full app scaffold pending |
| Real Ad Spend | Marketing promises $450-525 ad budget execution | ❌ No Meta/Google Ads API integration |
| Real User Testing | Marketing promises "test with real customers" | ❌ No analytics or experiment framework |
| Unit Economics | Marketing promises CAC/LTV analysis | ⚠️ UnitEconomicsCalculatorTool exists; may need real data sources |
| Evidence-Based | Marketing promises data-driven validation | ⚠️ TavilySearchTool provides real web research |

### Capabilities Required to Close Gap

1. **MVP Generation**: ✅ LandingPageGeneratorTool exists; full app scaffolding pending
2. **Ad Platform Integration**: ❌ Meta Business API, Google Ads API not connected
3. **Analytics Integration**: ❌ Real user tracking, conversion measurement pending
4. **Financial Modeling**: ⚠️ Tools exist; may need real cost/revenue data sources
5. **Web Research Tools**: ✅ TavilySearchTool + 4 research tools implemented

---

## This Repo Blocks

### Product App (`app.startupai.site`)

| Blocker | Status | Description | Unblocks |
|---------|--------|-------------|----------|
| Phase 2D Completion | ✅ Complete | Flow works with 18 tools, @persist(), HITL | Product can display results |
| Results → Supabase | ✅ Implemented | `_persist_to_supabase()` webhook in flow | Product app can display analysis results |
| Real Analysis Tools | ✅ Implemented | TavilySearchTool, CompetitorResearchTool, etc. | Real web research available |
| Flywheel Learning Schema | ❌ Not Started | SQL for `learnings`, `patterns`, `outcomes`, `domain_expertise` tables | Learning tools can persist/query |
| Resume/Webhook API | ✅ Implemented | `webhooks/resume_handler.py` with 5 approval types | Product approval UI |

**Specific API Endpoints Status:**
- `POST /kickoff` - ✅ Working
- `GET /status/{id}` - ✅ Working
- `POST /resume` - ✅ Implemented (`webhooks/resume_handler.py`)
- Webhook notifications - ✅ Implemented (creative approval, viability decision)

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

- **Phase 2D Complete** - All code criteria met (see `phases.md`)
- Results persistence mechanism: ✅ Webhook implemented (`_persist_to_supabase()`)
- Activity Feed API added to `backlog.md` per marketing dependency
- Flywheel tables still need migration in product app

## Cross-Repo Links

- Product app blockers: `app.startupai.site/docs/work/cross-repo-blockers.md`
- Marketing blockers: `startupai.site/docs/work/cross-repo-blockers.md`
- Master architecture: `docs/master-architecture/01-ecosystem.md`
- API contracts: `docs/master-architecture/reference/api-contracts.md`
- Approval workflows: `docs/master-architecture/reference/approval-workflows.md`

---
**Last Updated**: 2025-11-26

**Changes (2025-11-26 - Post-Audit)**:
- **MAJOR CORRECTION**: Updated multiple blockers from "Not Started" to "Implemented"
- Results → Supabase: ✅ `_persist_to_supabase()` webhook exists
- Resume/Webhook API: ✅ `webhooks/resume_handler.py` with 5 approval types
- Real Analysis Tools: ✅ TavilySearchTool + 4 research tools implemented
- Phase status updated from "Phase 1 Partial" to "Phase 2D Complete"
- Only remaining blocker for Product App: Flywheel learning tables migration
