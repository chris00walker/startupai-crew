---
purpose: "Cross-repository dependency tracking for coordinated delivery"
status: "active"
last_reviewed: "2026-01-08"
last_synced: "2026-01-08 - Modal serverless migration proposed"
---

# Cross-Repository Blockers

This document tracks dependencies between StartupAI repositories to ensure coordinated delivery.

> **Architecture Migration**: Migrating from CrewAI AMP (3 repos) to Modal serverless (single repo). See [ADR-002](../adr/002-modal-serverless-migration.md).

## Ecosystem Status (2026-01-08)

**Architecture migration in progress.** AMP deployment deprecated; migrating to Modal.

| Service | Status | Completion | Notes |
|---------|--------|------------|-------|
| CrewAI Backend | Modal migration PROPOSED | ~60% | See ADR-002 |
| Product App | Phase Alpha complete | ~85% | Pending Modal integration |
| Marketing Site | Production, static export | ~90% | No changes needed |

**Key Change**: Returning to **single repository** (was 3 repos for AMP workaround).

**Source of Truth**: `docs/master-architecture/09-status.md`

---

## This Repo Blocks

### Product App (`app.startupai.site`)

| Blocker | Status | Description | Unblocks |
|---------|--------|-------------|----------|
| Modal Deployment | ⏳ PENDING | Modal serverless migration | Product can trigger validation |
| Modal API Endpoints | ⏳ PENDING | `/kickoff`, `/status`, `/hitl/approve` | Full pipeline operational |
| Supabase Realtime | ⏳ PENDING | Progress updates via Realtime | Real-time UI updates |

**Current blockers**: Modal migration (ADR-002)

**Target API Endpoints (Modal):**
- `POST /kickoff` - Start validation (returns 202 Accepted)
- `GET /status/{run_id}` - Check progress from Supabase
- `POST /hitl/approve` - Resume after human approval

### Legacy AMP Deployment (DEPRECATED)

| Blocker | Status | Description |
|---------|--------|-------------|
| 3-Crew Architecture | ⚠️ DEPRECATED | Being replaced by Modal |
| Crew 1-3 Deployments | ⚠️ DEPRECATED | UUIDs preserved for reference only |
| Crew Chaining | ⚠️ DEPRECATED | Will be replaced by native Python calls |

> See [ADR-002](../adr/002-modal-serverless-migration.md) for migration details.

### Marketing Site (`startupai.site`)

| Blocker | Status | Description | Unblocks |
|---------|--------|-------------|----------|
| Activity Feed API | ✅ SHIPPED | `GET /api/v1/public/activity` in Product App | Marketing can show live activity |
| Metrics API | ✅ SHIPPED | `GET /api/v1/public/metrics` in Product App | Marketing can show trust metrics |

**All Marketing Site blockers resolved.** APIs are available in Product App.

---

## This Repo Blocked By

| Blocker | Source Repo | Status | Impact |
|---------|-------------|--------|--------|
| Learning tables migration | Product App | ✅ Done | Flywheel learning tools have pgvector tables |

**All upstream blockers resolved.**

---

## Remaining Work (Not Blockers - Internal)

| Item | Status | Owner | Notes |
|------|--------|-------|-------|
| E2E flow verification | ⚠️ Ready to test | All repos | All components exist |
| Ad platform integration | ❌ Not connected | Crew | Meta/Google Ads APIs - deferred |
| Real analytics tracking | ⚠️ Partial | Crew | PostHog exists; ad analytics pending |

---

## Marketing Promise Gap

| Promise | Technical Status |
|---------|------------------|
| "Build your MVP" | ⚠️ LandingPageGeneratorTool exists; full scaffold pending |
| "Real ad spend ($450-525)" | ❌ No Meta/Google Ads API integrated |
| "Real user testing" | ❌ No analytics/experiment framework |
| "Unit economics (CAC/LTV)" | ✅ 10 UnitEconomicsModels with industry benchmarks |
| "2-week validation cycles" | ⚠️ Tools exist; quality depends on data |
| "Evidence-based validation" | ✅ TavilySearchTool provides real web research |
| "6 AI Founders team" | ✅ 19 agents across 3 crews |

**Primary gap**: Ad platform integration (Meta/Google APIs) - explicitly deferred.

---

## E2E Verification Checklist

The following flow needs live verification:

```
User lands on startupai.site
    ↓
Signs up (Supabase Auth)
    ↓
Redirects to app.startupai.site with plan
    ↓
Completes onboarding chat (7 stages)
    ↓
Triggers CrewAI analysis (POST /kickoff)
    ↓
CrewAI processes through 3 crews
    ↓
Webhook persists results to Supabase
    ↓
Dashboard displays validation results
    ↓
Marketing activity feed shows real activity
```

**Status**: All components exist. Needs live end-to-end test.

---

## Coordination Notes

- **CrewAI backend**: Modal migration in progress (ADR-002)
- **Product App**: Waiting for Modal endpoints to integrate
- **Marketing site**: UNBLOCKED - Activity Feed + Metrics APIs shipped
- **Primary work**: Complete Modal migration, then E2E verification

**Single Repo Benefit**: Modal migration returns us to single repository (`startupai-crew`). No more cross-repo coordination for Crews 2 & 3.

---

## Cross-Repo Links

- Product app blockers: `app.startupai.site/docs/work/cross-repo-blockers.md`
- Marketing blockers: `startupai.site/docs/work/cross-repo-blockers.md`
- Master architecture: `docs/master-architecture/09-status.md`
- Architecture Decision Records: `docs/adr/`

---

**Last Updated**: 2026-01-08

**Changes (2026-01-08 - Modal Migration)**:
- Added Modal serverless migration notice (ADR-002)
- Updated Ecosystem Status to show migration in progress
- Noted return to single repository (was 3 repos for AMP)
- Updated Product App blockers for Modal endpoints
- Marked legacy AMP deployment as DEPRECATED
- Updated Coordination Notes

**Previous (2026-01-07 - Full Ecosystem Sync)**:
- Synced with `docs/master-architecture/09-status.md` cross-repo rewrite
- Added Ecosystem Status table
