---
purpose: "Cross-repository dependency tracking for coordinated delivery"
status: "active"
last_reviewed: "2026-01-07"
last_synced: "2026-01-07 - Full ecosystem status sync"
---

# Cross-Repository Blockers

This document tracks dependencies between StartupAI repositories to ensure coordinated delivery.

## Ecosystem Status (2026-01-07)

**All services deployed and functional.** Primary work is E2E verification.

| Service | Status | Completion |
|---------|--------|------------|
| CrewAI Backend | ✅ 3 Crews deployed to AMP | ~85% |
| Product App | ✅ Phase Alpha complete | ~85% |
| Marketing Site | ✅ Production, static export | ~90% |

**Source of Truth**: `docs/master-architecture/09-status.md`

---

## This Repo Blocks

### Product App (`app.startupai.site`)

| Blocker | Status | Description | Unblocks |
|---------|--------|-------------|----------|
| 3-Crew Architecture | ✅ DEPLOYED | 19 agents, 32 tasks, 7 HITL | Full pipeline operational |
| Crew 1 Deployment | ✅ DEPLOYED | UUID: `6b1e5c4d-e708-4921-be55-08fcb0d1e94b` | Product can trigger validation |
| Crews 2 & 3 Repos | ✅ DEPLOYED | Separate GitHub repos created | Full pipeline works |
| Crew Chaining | ✅ CONFIGURED | `InvokeCrewAIAutomationTool` wired | End-to-end validation |
| Crew 1 Best Practices | ✅ COMPLETE | 100% CrewAI alignment (2026-01-06) | Structured outputs |

**All Product App blockers resolved.**

**API Endpoints (LIVE):**
- `POST /kickoff` - Crew 1 entry point (token: `db9f9f4c1a7a`)
- `GET /status/{id}` - Standard AMP endpoint
- HITL webhooks - 7 checkpoints across 3 crews

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

- **CrewAI backend is UNBLOCKED** - All 3 crews deployed to AMP
- **Product App UNBLOCKED** - No remaining blockers from this repo
- **Marketing site UNBLOCKED** - Activity Feed + Metrics APIs shipped
- **Primary work**: E2E verification with live data

---

## Cross-Repo Links

- Product app blockers: `app.startupai.site/docs/work/cross-repo-blockers.md`
- Marketing blockers: `startupai.site/docs/work/cross-repo-blockers.md`
- Master architecture: `docs/master-architecture/09-status.md`

---

**Last Updated**: 2026-01-07

**Changes (2026-01-07 - Full Ecosystem Sync)**:
- Synced with `docs/master-architecture/09-status.md` cross-repo rewrite
- Added Ecosystem Status table
- Updated Marketing Site blockers: Activity Feed + Metrics APIs now SHIPPED
- Added E2E Verification Checklist
- Simplified structure to match other repo blocker files
- Primary blocker is now E2E verification, not deployment
