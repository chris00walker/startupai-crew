---
purpose: "Cross-repository dependency tracking for coordinated delivery"
status: "active"
last_reviewed: "2026-01-08"
last_synced: "2026-01-08 - Modal serverless production deployment verified"
---

# Cross-Repository Blockers

This document tracks dependencies between StartupAI repositories to ensure coordinated delivery.

> **Modal Migration Complete**: Modal serverless infrastructure deployed to production. Crew implementation in progress. See [ADR-002](../adr/002-modal-serverless-migration.md).

## Ecosystem Status (2026-01-08)

**Modal serverless deployed to production.** Infrastructure verified, crew implementation in progress.

| Service | Status | Completion | Notes |
|---------|--------|------------|-------|
| CrewAI Backend | Modal deployed | ~70% | Infrastructure live, crews being implemented |
| Product App | Modal integration complete | ~95% | Pointing to Modal endpoints |
| Marketing Site | Live API integration | ~95% | Activity Feed + Metrics connected |

**Production URLs**:
- Modal: `https://chris00walker--startupai-validation-fastapi-app.modal.run`
- Product App: `https://app-startupai-site.netlify.app`
- Marketing: `https://startupai.site`

**Canonical Architecture**: 5 Flows, 14 Crews, 45 Agents, 10 HITL checkpoints
**AMP (ARCHIVED)**: Legacy 3-repo workaround deprecated

**Source of Truth**: `docs/master-architecture/09-status.md`

---

## This Repo Blocks

### Product App (`app.startupai.site`)

| Blocker | Status | Description | Unblocks |
|---------|--------|-------------|----------|
| Modal Infrastructure | ✅ DEPLOYED | Production endpoints live | Product can trigger validation |
| Modal API Endpoints | ✅ WORKING | `/kickoff`, `/status`, `/hitl/approve`, `/health` | Full API operational |
| Supabase Tables | ✅ READY | `validation_runs`, `validation_progress`, `hitl_requests` | State persistence works |
| Supabase Realtime | ✅ ENABLED | Progress tables publishing | Real-time UI updates |
| 14 Crews Implementation | ⏳ IN PROGRESS | Building from master-architecture specs | Fresh build approach |

**Modal API Endpoints (Production):**
- `POST /kickoff` - Start validation (returns 202 Accepted + run_id)
- `GET /status/{run_id}` - Check progress from Supabase
- `POST /hitl/approve` - Resume after human approval
- `GET /health` - Health check

### Legacy AMP Deployment (ARCHIVED)

| Item | Status | Notes |
|------|--------|-------|
| 3-Crew Architecture | ⚠️ DEPRECATED | Being archived |
| `startupai-crew-validation` | ⚠️ TO ARCHIVE | Repo will be archived (read-only) |
| `startupai-crew-decision` | ⚠️ TO ARCHIVE | Repo will be archived (read-only) |

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

### Infrastructure Verification (2026-01-08) ✅

| Endpoint | Status | Result |
|----------|--------|--------|
| Modal `/health` | ✅ Verified | `{"status":"healthy","service":"startupai-validation"}` |
| Modal auth | ✅ Verified | Returns 401 for invalid tokens |
| Product App login | ✅ Verified | Returns 200 |
| Marketing site | ✅ Verified | Returns 200 |
| Marketing APIs | ✅ Verified | `/public-activity`, `/public-metrics` returning JSON |

### Full Flow (Pending crew completion)

```
User lands on startupai.site
    ↓
Signs up (Supabase Auth)
    ↓
Redirects to app.startupai.site with plan
    ↓
Completes onboarding chat (7 stages)
    ↓
Triggers Modal validation (POST /kickoff)
    ↓
Modal processes through 5 phases (14 crews)
    ↓
Results persist to Supabase
    ↓
Dashboard displays validation results
    ↓
Marketing activity feed shows real activity
```

**Status**: Infrastructure verified. Awaiting crew implementation completion.

---

## Coordination Notes

- **Modal infrastructure DEPLOYED** - Production endpoints verified (2026-01-08)
- **Product App UPDATED** - Pointing to Modal endpoints (not AMP)
- **Marketing site CONNECTED** - Live Activity Feed + Metrics components created
- **AMP DEPRECATED** - Legacy repos being archived
- **Primary work**: Complete 14 crews implementation, then run first production validation

**Single Repo Benefit**: Modal migration returns us to single repository (`startupai-crew`). No more cross-repo coordination for Crews 2 & 3.

---

## Cross-Repo Links

- Product app blockers: `app.startupai.site/docs/work/cross-repo-blockers.md`
- Marketing blockers: `startupai.site/docs/work/cross-repo-blockers.md`
- Master architecture: `docs/master-architecture/09-status.md`
- Architecture Decision Records: `docs/adr/`
- Migration plan: `~/.claude/plans/federated-prancing-lollipop.md`

---

**Last Updated**: 2026-01-08

**Changes (2026-01-08 - Modal Production Deployment)**:
- Modal serverless deployed to production
- Infrastructure verification passed (health, auth, endpoints)
- Product app updated to point to Modal (not AMP)
- Marketing site live components created (Activity Feed, Metrics)
- AMP marked as deprecated, repos to be archived
- Updated blockers to reflect Modal infrastructure status
- Primary work is now crew implementation (14 crews)

**Previous (2026-01-08 - Modal Migration Proposed)**:
- Added Modal serverless migration notice (ADR-002)
- Updated Ecosystem Status to show migration in progress
- Noted return to single repository (was 3 repos for AMP)
