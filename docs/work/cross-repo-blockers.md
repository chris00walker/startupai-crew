---
purpose: "Cross-repository dependency tracking for coordinated delivery"
status: "active"
last_reviewed: "2026-01-08"
last_synced: "2026-01-08 - E2E integration tests complete (202 tests passing)"
---

# Cross-Repository Blockers

This document tracks dependencies between StartupAI repositories to ensure coordinated delivery.

> **E2E Integration Tests Complete**: All 14 crews with 45 agents implemented. 202 tests passing (185 crew + 17 E2E). Ready for live production validation. See [ADR-002](../adr/002-modal-serverless-migration.md).

## Ecosystem Status (2026-01-08)

**E2E integration tests complete.** All 14 crews implemented, 202 tests passing, ready for live production validation.

| Service | Status | Completion | Notes |
|---------|--------|------------|-------|
| CrewAI Backend | E2E tested | ~90% | 14 crews, 45 agents, 202 tests |
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
| 14 Crews Implementation | ✅ COMPLETE | 45 agents, 185 tests passing | All phases ready |
| E2E Integration Test | ✅ COMPLETE | 17 tests, Phase 0→4 flow validated | Production validation ready |

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
| Live production validation | ⏳ Ready | All repos | E2E tests passing, needs real run |
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

### Full Flow (Ready for E2E Test)

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
Modal processes through 5 phases (14 crews, 45 agents)
    ↓
Results persist to Supabase
    ↓
Dashboard displays validation results
    ↓
Marketing activity feed shows real activity
```

**Status**: E2E integration tests complete (17 tests). Ready for live production validation.

---

## Coordination Notes

- **E2E integration tests COMPLETE** - 17 tests validating Phase 0→4 flow (2026-01-08)
- **202 tests passing** - 185 crew tests + 17 E2E integration tests
- **Crew implementation COMPLETE** - All 14 crews with 45 agents
- **Modal infrastructure DEPLOYED** - Production endpoints verified
- **Product App UPDATED** - Pointing to Modal endpoints (not AMP)
- **Marketing site CONNECTED** - Live Activity Feed + Metrics components
- **AMP DEPRECATED** - Legacy repos archived
- **Primary work**: First live production validation run

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

**Changes (2026-01-08 - E2E Integration Tests Complete)**:
- Added 17 E2E integration tests (Phase 0→4 flow)
- 202 tests passing (185 crew + 17 E2E)
- Updated completion status: ~90% (was ~85%)
- Ready for live production validation run

**Previous (2026-01-08 - Crew Implementation Complete)**:
- All 14 crews implemented with 45 agents
- 185 tests passing (Phases 0-4 covered)
- Updated completion status: ~85% (was ~70%)
- Ready for E2E integration testing
- Primary work is now E2E test + production validation

**Previous (2026-01-08 - Modal Production Deployment)**:
- Modal serverless deployed to production
- Infrastructure verification passed (health, auth, endpoints)
- Product app updated to point to Modal (not AMP)
- Marketing site live components created (Activity Feed, Metrics)
- AMP marked as deprecated, repos to be archived

**Previous (2026-01-08 - Modal Migration Proposed)**:
- Added Modal serverless migration notice (ADR-002)
- Updated Ecosystem Status to show migration in progress
- Noted return to single repository (was 3 repos for AMP)
