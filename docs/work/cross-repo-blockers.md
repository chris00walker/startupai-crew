---
purpose: "Cross-repository dependency tracking for coordinated delivery"
status: "active"
last_reviewed: "2025-12-05"
---

# Cross-Repository Blockers

This document tracks dependencies between StartupAI repositories to ensure coordinated delivery.

## Architecture Change Notice (2025-12-05)

**MAJOR**: Migrated from Flow to 3-Crew architecture. See ADR-001.

**Impact on Cross-Repo:**
- This repo now hosts **Crew 1 (Intake)** only
- Crews 2 & 3 require **new GitHub repositories**
- Product App will call Crew 1's `/kickoff` endpoint (same API, different internal structure)

## Marketing Promise Gap (Updated 2025-11-26)

The marketing site makes promises that require technical capabilities. Status after code audit:

| Gap | Description | Status |
|-----|-------------|--------|
| MVP Building | Marketing promises "working software in days" | ⚠️ LandingPageGeneratorTool + Netlify deploy exist; full app scaffold pending |
| Real Ad Spend | Marketing promises $450-525 ad budget execution | ❌ No Meta/Google Ads API integration |
| Real User Testing | Marketing promises "test with real customers" | ❌ No analytics or experiment framework |
| Unit Economics | Marketing promises CAC/LTV analysis | ✅ 10 business model-specific UnitEconomicsModels with industry benchmarks |
| Evidence-Based | Marketing promises data-driven validation | ⚠️ TavilySearchTool provides real web research |

### Capabilities Required to Close Gap

1. **MVP Generation**: ✅ LandingPageGeneratorTool exists; full app scaffolding pending
2. **Ad Platform Integration**: ❌ Meta Business API, Google Ads API not connected
3. **Analytics Integration**: ⚠️ PolicyBandit + offline evaluation exist; ad platform analytics pending
4. **Financial Modeling**: ✅ 10 business model-specific UnitEconomicsModels with industry benchmarks
5. **Web Research Tools**: ✅ TavilySearchTool + 4 research tools implemented
6. **Budget Guardrails**: ✅ BudgetGuardrails with hard/soft enforcement (Area 6)
7. **Policy Versioning**: ✅ PolicyBandit with UCB algorithm for A/B testing (Area 3)

---

## This Repo Blocks

### Product App (`app.startupai.site`)

| Blocker | Status | Description | Unblocks |
|---------|--------|-------------|----------|
| 3-Crew Architecture | ⚠️ Pending | Code complete, needs AMP deployment | Product can call Crew 1 |
| Crew 1 Deployment | ⚠️ Pending | Requires `crewai login` and deploy | Product can trigger validation |
| Crews 2 & 3 Repos | ⚠️ Pending | Need separate GitHub repos | Full pipeline works |
| Crew Chaining | ⚠️ Pending | `InvokeCrewAIAutomationTool` config | End-to-end validation |

**New API Endpoints (after 3-Crew deployment):**
- `POST /kickoff` - Will be Crew 1 entry point
- `GET /status/{id}` - Standard AMP endpoint
- HITL webhooks - 7 checkpoints across 3 crews

**⚠️ CRITICAL: Deployment Required**
- 3-Crew code: ✅ Complete (19 agents, 32 tasks, 7 HITL)
- Crew 1 at repo root: ✅ Done
- Crews 2 & 3 repos: ❌ Not created
- AMP deployment: ❌ Pending `crewai login`
- Blocker owner: This repo - must complete Phase 0 deployment

**Previous Flow Integration (DEPRECATED):**
The previous Flow-based integration is archived. Product App should wait for 3-Crew deployment before updating integration.

**Flywheel Learning Tables:**
- Schema: See `docs/master-architecture/reference/flywheel-learning.md`
- Requires pgvector extension enabled in Supabase
- Tables: `learnings`, `patterns`, `outcomes`, `domain_expertise`
- Status: ✅ Tables exist, will be used by Crew 2 (Validation) once deployed

### Marketing Site (`startupai.site`)

| Blocker | Status | Description | Unblocks |
|---------|--------|-------------|----------|
| Activity Feed API | Not Started | `GET /api/v1/public/activity` - agent status | Marketing transparency page |
| Metrics API | Not Started | `GET /api/v1/public/metrics` - validation counts | Marketing trust metrics |

**Note:** Marketing site can implement Netlify functions that query Supabase directly (per `reference/marketing-integration.md`) rather than waiting for CrewAI APIs. This provides an alternative unblock path.

## This Repo Blocked By

| Blocker | Source Repo | Status | Impact |
|---------|-------------|--------|--------|
| Learning tables migration | Product App | ✅ Done | Flywheel learning tools have pgvector tables in Supabase |

**Note**: Product app manages Supabase migrations. Learning tables schema is defined in `docs/master-architecture/reference/flywheel-learning.md`.

## Coordination Notes

- **Phase 2D Complete** - All code criteria met (see `phases.md`)
- Results persistence mechanism: ✅ Webhook implemented (`_persist_to_supabase()`)
- Activity Feed API added to `backlog.md` per marketing dependency
- Flywheel tables: ✅ Migration complete in product app

## Cross-Repo Links

- Product app blockers: `app.startupai.site/docs/work/cross-repo-blockers.md`
- Marketing blockers: `startupai.site/docs/work/cross-repo-blockers.md`
- Master architecture: `docs/master-architecture/01-ecosystem.md`
- API contracts: `docs/master-architecture/reference/api-contracts.md`
- Approval workflows: `docs/master-architecture/reference/approval-workflows.md`

---
**Last Updated**: 2025-12-05

**Changes (2025-12-05 - Flow to 3-Crew Migration)**:
- **MAJOR**: Architecture migrated from Flow to 3-Crew
- All existing blockers now superseded by 3-Crew deployment blockers
- Product App should wait for 3-Crew deployment before integration changes
- Added Architecture Change Notice section
- Updated blocker table to reflect deployment-pending status
- See ADR-001 for full decision record

**Changes (2025-11-27 - Migrations Deployed)**:
- **Database migrations deployed**: flow_executions (001), validation_events (002), experiment_outcomes (004), policy_version (005), decision_log (006)
- All CrewAI-specific tables now live in Supabase

**Changes (2025-11-27)**:
- **Areas 3, 6, 7 Complete**: All 8 architectural improvements now 100% implemented
- Added Area 3 tools: PolicyBandit, ExperimentConfigResolver
- Added Area 6 tools: BudgetGuardrails, DecisionLogger
- Added Area 7 tools: BusinessModelClassifier, 10 UnitEconomicsModels
- Tool count increased from 18 to 24+
- Flywheel learning tables: ✅ Done (learnings, patterns, outcomes, domain_expertise)
- Product app can now build results display UI (webhook persistence working)
- Marketing site can build transparency features (data available in Supabase)

**Changes (2025-11-26 - Post-Audit)**:
- **MAJOR CORRECTION**: Updated multiple blockers from "Not Started" to "Implemented"
- Results → Supabase: ✅ `_persist_to_supabase()` webhook exists
- Resume/Webhook API: ✅ `webhooks/resume_handler.py` with 5 approval types
- Real Analysis Tools: ✅ TavilySearchTool + 4 research tools implemented
- Flywheel Learning Tables: ✅ Migration complete in product app
- Phase status updated from "Phase 1 Partial" to "Phase 2D Complete"
- No remaining blockers for Product App - ready for E2E testing

**Changes (2025-12-02 - Integration Test Added)**:
- **E2E Integration Test**: `webhook-to-dashboard.integration.test.ts` added to product app
- Tests verify: webhook → 5 tables persistence → dashboard hooks can query data
- Validates complete flow: reports, evidence, crewai_validation_states, projects, public_activity_log
- Dashboard hooks confirmed: useCrewAIState, useInnovationSignals, useVPCData already existed
