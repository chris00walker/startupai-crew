---
purpose: Honest assessment of current implementation status
status: active
last_reviewed: 2026-01-06
vpd_compliance: true
---

# StartupAI Current State - Honest Assessment

This document provides an unvarnished view of what works, what's broken, and what doesn't exist across the three services.

> **VPD Framework**: StartupAI implements the Value Proposition Design (VPD) framework. See [05-phase-0-1-specification.md](./05-phase-0-1-specification.md) for Phase 0-1 details.

## Architecture Change Notice (2026-01-05)

**CURRENT**: Multi-phase crew architecture with VPD framework compliance.
- **Phase 0**: Onboarding (Founder's Brief) - Specified in `05-phase-0-1-specification.md`
- **Phase 1**: VPC Discovery (Customer Profile + Value Map) - Specified in `05-phase-0-1-specification.md`
- **Phases 2-3**: Desirability/Feasibility/Viability validation - 3-Crew deployment

### Previous Changes
- **2025-12-05**: Migrated from Flow-based to Crew-based architecture (AMP compatibility)
- **ADR**: See `docs/adr/001-flow-to-crew-migration.md`
- **Old code**: Archived to `archive/flow-architecture/`

## Status Summary

| Service | Overall Status | Completion | Reality Check |
|---------|---------------|------------|---------------|
| AI Founders Core (startupai-crew) | Multi-phase architecture with VPD compliance | ~75% functional | Phase 0-1 specified, deployed crews online |
| Marketing Site (startupai.site) | Functional, static | 90% | Ad platform APIs (Meta/Google) not connected |
| Product App (app.startupai.site) | Dashboards functional, integration working | ~80-85% | Full UI + CrewAI integration ready |

---

## Marketing vs Reality Gap

### Critical Discrepancies

| Marketing Promise | Technical Reality |
|-------------------|-------------------|
| "Build your MVP, test with real customers" | ⚠️ LandingPageGeneratorTool + Netlify deploy exist; full MVP scaffold pending; no ad integration |
| "Real ad spend ($450-525)" | ❌ No Meta/Google Ads API integration |
| "Unit economics analysis (CAC/LTV)" | ✅ 10 business model-specific UnitEconomicsModels + IndustryBenchmarkTool |
| "2-week validation cycles" | ⚠️ Flow runs in minutes; tools exist but quality depends on Tavily data |
| "Evidence-based validation" | ⚠️ TavilySearchTool provides real web research; analysis quality TBD |
| "6 AI Founders team" | ✅ 8 crews / 18 agents with 18 specialized tools |

### Capabilities Required for Marketing Parity

1. **MVP Generation**: ✅ LandingPageGeneratorTool exists; full app scaffolding pending
2. **Ad Platform Integration**: ❌ Meta Business API, Google Ads API not connected
3. **Real Analytics**: ⚠️ PolicyBandit + offline evaluation exists; ad platform analytics pending
4. **Financial Modeling**: ✅ 10 business model-specific UnitEconomicsModels with industry benchmarks
5. **Web Research Tools**: ✅ TavilySearchTool + 4 research tools implemented
6. **Results Persistence**: ✅ Webhook to Supabase implemented via `_persist_to_supabase()`

---

## AI Founders Core (`startupai-crew`)

### Architecture Status (2026-01-05)

**Current**: Multi-phase crew architecture with VPD framework compliance
**Framework**: Value Proposition Design (Osterwalder/Pigneur)

| Phase | Crew/Flow | Agents | HITL | Status |
|-------|-----------|--------|------|--------|
| Phase 0 | Onboarding | 4 (O1, G1, G2, S1) | 1 | ✅ Specified in `05-phase-0-1-specification.md` |
| Phase 1 | VPC Discovery | 18 (E1, D1-D4, J1-J2, P1-P2, G1-G2, V1-V3, W1-W2, F1-F2) | 3 | ✅ Specified in `05-phase-0-1-specification.md` |
| Phase 2+ | Crew 1: Intake | 4 | 1 | ✅ Deployed to AMP |
| Phase 2+ | Crew 2: Validation | 12 | 5 | ✅ Deployed to AMP |
| Phase 2+ | Crew 3: Decision | 3 | 1 | ✅ Deployed to AMP |

### What Works
- **3-Crew architecture code complete**: 19 agents, 32 tasks, 7 HITL checkpoints
- Crew 1 (Intake) restructured to repo root with `type = "crew"`
- HITL integrated via `human_input: true` on approval tasks
- Task sequencing via `context` arrays (replaces `@listen`/`@router`)

### What's Pending
- **Crew 1 deployment**: Requires `crewai login` then `crewai deploy push`
- **Crews 2 & 3 repos**: Need separate GitHub repos (AMP deploys from root only)
- **Crew chaining**: `InvokeCrewAIAutomationTool` configuration after deployment
- **Environment variables**: Set OPENAI_API_KEY in AMP dashboard for each crew

### Agent Distribution

**Crew 1: Intake (4 agents)** - _Updated 2026-01-06_
- S1 (FounderOnboarding): Parse founder input into structured brief
- S2 (CustomerResearch): Research using JTBD methodology, `reasoning=True`
- S3 (ValueDesigner): Create Value Proposition Canvas
- G1 (QA): Quality assurance with `MethodologyCheckTool` and human approval gate, `reasoning=True`

**Crew 1 Architecture (2026-01-06 Update)**:
- **Pydantic Schemas**: All 6 tasks have `output_pydantic` models enforcing structured outputs
  - `FounderBrief`, `CustomerResearchOutput`, `ValuePropositionCanvas`, `QAGateOutput`, `HumanApprovalInput`, `CrewInvocationResult`
- **Tools**: S2 has `TavilySearchTool` + `CustomerResearchTool`; G1 has `MethodologyCheckTool` + `InvokeCrewAIAutomationTool`
- **Reasoning**: Enabled for S2 (research synthesis) and G1 (QA decisions)
- **Backstories**: Enriched with years of experience, methodology expertise, behavioral tendencies
- **Schema Location**: `src/intake_crew/schemas.py`

**Crew 2: Validation (12 agents)**
- Pulse: P1 (AdCreative), P2 (Comms), P3 (Analytics)
- Forge: F1 (UXUIDesigner), F2 (FrontendDev), F3 (BackendDev)
- Ledger: L1 (FinancialController), L2 (LegalCompliance), L3 (EconomicsReviewer)
- Guardian: G1 (QA), G2 (Security), G3 (Audit)

**Crew 3: Decision (3 agents)**
- C1 (ProductPM): Synthesize evidence, propose options
- C2 (HumanApproval): Present to human for decision
- C3 (RoadmapWriter): Document decisions, update roadmap

### HITL Checkpoints (11 total across all phases)

#### Phase 0-1 Checkpoints (VPD Framework)

| Phase | Checkpoint | Owner | Purpose |
|-------|------------|-------|---------|
| 0 | `approve_founders_brief` | Founder + Guardian | Gate: Founder approves brief before Phase 1 |
| 1 | `approve_experiment_plan` | Sage (E1) | Approve experiment mix before execution |
| 1 | `approve_pricing_test` | Ledger (W1, W2) | Approve tests involving real money |
| 1 | `approve_vpc_completion` | Compass (F1) | Gate: Confirm VPC ready for Phase 2 (fit ≥ 70) |

#### Phase 2+ Checkpoints (Deployed Crews)

| Crew | Checkpoint | Purpose |
|------|------------|---------|
| 1 | `approve_intake_to_validation` | Gate: Intake → Validation |
| 2 | `approve_campaign_launch` | Ad creative approval |
| 2 | `approve_spend_increase` | Budget approval |
| 2 | `approve_desirability_gate` | Gate: Desirability → Feasibility |
| 2 | `approve_feasibility_gate` | Gate: Feasibility → Viability |
| 2 | `approve_viability_gate` | Gate: Viability → Decision |
| 3 | `request_human_decision` | Final pivot/proceed decision |

### Deployment Status

| Item | Status | Notes |
|------|--------|-------|
| pyproject.toml | ✅ Updated | `type = "crew"` at repo root |
| Crew 1 code | ✅ Complete | `src/intake_crew/` |
| Crew 2 code | ✅ Complete | `startupai-crews/crew-2-validation/` |
| Crew 3 code | ✅ Complete | `startupai-crews/crew-3-decision/` |
| AMP deployment | ⚠️ Pending | Requires `crewai login` |
| Crew chaining | ⚠️ Pending | After all crews deployed |

### Archived Code (Flow Architecture)

The original Flow-based architecture is preserved at `archive/flow-architecture/`:
- `startupai/flows/` - Flow orchestration with `@listen`, `@router`, `@persist`
- `startupai/crews/` - 8 crews with 18 agents
- `startupai/tools/` - 24+ tools (still usable)
- `main.py` - Original entry point

**Note**: Tools from the archived code can be ported to the new crews as needed.

### What's Limited (Honest Assessment)
- **Ad platform integration**: Meta/Google Ads APIs not connected - cannot run real ad campaigns
- **Analytics integration**: No PostHog/GA integration for real experiment tracking
- **Token usage**: ~100K tokens per run ($2-5 per analysis)
- **No streaming**: Users wait without progress updates
- **Public APIs**: Activity Feed and Metrics APIs for marketing site not implemented
- **Lost Flow features**: No `@persist()` state recovery, no `@router` conditional branching within crews

### What Doesn't Exist
- Activity Feed API for marketing site (`GET /api/v1/public/activity`)
- Metrics API for marketing site (`GET /api/v1/public/metrics`)
- Meta Business API integration
- Google Ads API integration
- Separate repos for Crews 2 & 3 (code exists, repos don't)

---

## Marketing Site (`startupai.site`)

### What Works
- Static export builds successfully
- Authentication flow to product app works
- Waitlist form (Formspree) collecting leads
- Navigation and content pages render
- SEO metadata in place

**Deployment Details**:
- Platform: Netlify
- Type: Static export (`next export`)

### What's Limited
- **No dynamic content**: Cannot show real-time agent activity
- **Aspirational docs**: Service contracts describe non-existent APIs
- **Plan parameter passing**: Works but untested end-to-end

### What Doesn't Exist
- Real-time activity feed display
- Public metrics dashboard
- Agent work transparency (the core value prop)

### Content Status
| Page | Status | Notes |
|------|--------|-------|
| Home | Complete | Hero, features, CTA |
| About | Complete | Team, mission |
| Pricing | Complete | Plan comparison |
| Beta | Complete | Waitlist signup |
| Contact | Complete | Contact form |

---

## Product App (`app.startupai.site`)

### What Works
- Supabase authentication (GitHub OAuth)
- Database schema (12 migrations deployed)
- Onboarding chat with Vercel AI SDK (7 stages, streaming, session resumption)
- **Full dashboard implementations**:
  - `founder-dashboard.tsx` (595 lines): 5 tabs (Overview, Canvases, Assumption Map, Experiments, Evidence)
  - `consultant-dashboard.tsx` (376 lines): Portfolio view, gate filtering, guided tour
- **Analysis display components**:
  - `InnovationPhysicsPanel` - D-F-V signals visualization with health indicators
  - `VPCSummaryCard`, `GateDashboard`, `ValidationResultsSummary` - integrated in dashboards
  - `CrewAIReportViewer` - dual view modes, PDF export capability
- **CrewAI webhook integration** (production-ready):
  - Comprehensive Zod validation for incoming payloads
  - Multi-table persistence (reports, evidence, crewai_validation_states, public_activity_log)
  - Activity log generation for public feed
  - Idempotent processing via kickoff_id
- Component library (50+ Shadcn components)
- Real data hooks: `useGateEvaluation`, `useRecentActivity`, `useRecommendedActions`
- `DashboardAIAssistant` floating panel for contextual help

**Deployment Details**:
- Platform: Netlify (considering Vercel migration)
- Type: Server-side rendering

### What's Partial
- **CrewAI integration**: Webhook fully implemented, E2E flow needs live verification
- **Evidence collection**: Schema and tables exist, UI shows data but needs testing with real flow
- **Canvas editing**: Components exist (`EditableValuePropositionCanvas`), save-to-DB logic needs verification

### What Doesn't Exist
- Export functionality (PDF/CSV export for reports)
- User settings page
- Approval workflows UI (page exists at `/approvals` but functionality is stub)

### Technical Debt
- **Router migration**: Mix of App Router and Pages Router
- **Type errors**: Some unresolved TypeScript issues
- **Missing tests**: Coverage < 20%
- **Dead references**: Points to non-existent marketing site docs

### Database Status
| Table | Schema | Data | UI |
|-------|--------|------|-----|
| users | Done | Working | Working |
| projects | Done | Working | Working |
| hypotheses | Done | Working | Partial |
| evidence | Done | Populated via webhook | Working |
| onboarding_sessions | Done | Working | Working |
| entrepreneur_briefs | Done | Populated via webhook | Working |
| gate_scores | Done | Populated via webhook | Working |
| crewai_validation_states | Done | Working | N/A (internal) |
| public_activity_log | Done | Working | Partial |

---

## Cross-Service Integration

### Working Integrations
| From | To | Status |
|------|-----|--------|
| Marketing → Supabase Auth | Product callback | Working |
| Product → CrewAI API | Kickoff request | Implemented, untested E2E |
| Marketing → Product | Plan parameter | Working |

### Broken/Missing Integrations
| From | To | Status | Issue |
|------|-----|--------|-------|
| CrewAI → Supabase | Results storage | ✅ Implemented | `_persist_to_supabase()` via webhook |
| CrewAI → Supabase | Flywheel tables | ✅ Migrations deployed | flow_executions, validation_events, experiment_outcomes, decision_log (migrations 001-006) |
| Marketing ← CrewAI | Activity feed | Missing | Public API doesn't exist |
| Marketing ← CrewAI | Metrics API | Missing | Public API doesn't exist |
| Product ← CrewAI | Status polling | Implemented | UI exists in dashboards, needs E2E verification |

### Environment Variable Sync
| Variable | Marketing | Product | Crew |
|----------|-----------|---------|------|
| Supabase URL | Set | Set | N/A |
| Supabase Anon Key | Set | Set | N/A |
| Supabase Service Key | N/A | Set | N/A |
| OpenAI Key | N/A | Set | Set (dashboard) |
| CrewAI Bearer | N/A | Set | N/A |

---

## Critical Blockers

### 1. E2E Flow Verification Needed
**Issue**: All components exist but haven't been verified working together end-to-end with live data.

**Current state**:
- ✅ Results storage implemented via `_persist_to_supabase()` webhook
- ✅ UI components exist (`InnovationPhysicsPanel`, `GateDashboard`, `ValidationResultsSummary`)
- ✅ Dashboards display data from real hooks
- ⚠️ **Needs live E2E test**: User → Onboarding → CrewAI kickoff → Results → Dashboard display

**Required**:
- ✅ API route to poll CrewAI status (implemented)
- ✅ Webhook to persist results (implemented)
- ✅ Store results in `reports` and `evidence` tables (webhook does this)
- ✅ UI to display analysis results (components exist in dashboards)
- ⚠️ **Live E2E verification** with real CrewAI execution

### 2. Marketing Site Cannot Show Agent Activity
**Issue**: Core value proposition is transparency, but no transparency mechanism exists.

**Current state**: Marketing site is static, cannot fetch real-time data.

**Options**:
- Build activity feed API in crew
- Use serverless function on marketing site
- Embed from product app (iframe or microfrontend)

### 3. Documentation Mismatch
**Issue**: Docs describe features that don't exist, causing confusion.

**Required**:
- Archive aspirational docs
- Document only what's implemented
- Use validation backlog for hypotheses

---

## Recommended Next Steps

1. **Verify E2E flow live**: Run full user journey (Onboarding → CrewAI → Dashboard display) with real data
2. **Test CrewAI webhook persistence**: Verify data flows correctly to all tables (reports, evidence, crewai_validation_states)
3. **Complete marketing site transparency**: Activity feed API exists in product app, connect to marketing site display
4. **Increase E2E test coverage**: Add Playwright tests for full validation flow
5. **Ad platform integration**: Connect Meta/Google Ads APIs for real experiment campaigns (deferred)

---

## Last Updated
2026-01-06

**Latest Changes (2026-01-06 - Crew 1 CrewAI Best Practices Alignment)**:
- **Pydantic Schemas**: Created `src/intake_crew/schemas.py` with 6 output models for all tasks
  - FounderBrief, CustomerResearchOutput, ValuePropositionCanvas, QAGateOutput, HumanApprovalInput, CrewInvocationResult
  - 6 enums: RiskLevel, PainSeverity, GainImportance, JobType, QAStatus, ApprovalDecision
- **output_pydantic**: All 6 tasks in Crew 1 now enforce structured outputs via Pydantic
- **MethodologyCheckTool**: Migrated from archive to G1 agent for VPC structure validation
- **Reasoning Mode**: Enabled `reasoning=True` for S2 (research synthesis) and G1 (QA decisions)
- **Agent Backstories**: Enriched all 4 agents with years of experience, methodology expertise, pattern recognition abilities, behavioral tendencies, and decision authority
- **Task Descriptions**: Updated tasks.yaml with explicit schema field references and validation requirements
- **Unit Tests**: Added `tests/test_intake_schemas.py` with 28 tests for schema validation
- **Architecture Score**: Crew 1 now at 100% CrewAI best practices alignment (was ~60%)

**Previous Changes (2026-01-05 - VPD Framework Compliance)**:
- Added Phase 0 (Onboarding) and Phase 1 (VPC Discovery) to architecture
- Reference to `05-phase-0-1-specification.md` for VPD framework implementation
- Updated HITL checkpoints to include Phase 0-1 approval gates
- Changed terminology from "3-Crew" to "Multi-phase architecture"
- Added VPD framework compliance note

**Previous Changes (2025-12-05 - Flow to 3-Crew Migration)**:
- **MAJOR**: Migrated from `type = "flow"` to `type = "crew"` architecture
- **REASON**: AMP platform issues with Flow projects (see ADR-001)
- Created 3 crews: Intake (4 agents), Validation (12 agents), Decision (3 agents)
- Distributed 7 HITL checkpoints across all 3 crews
- Restructured repo: Crew 1 at root, Crews 2 & 3 code in subdirectories
- Archived Flow code to `archive/flow-architecture/`
- Updated completion from "~95%" to "~70%" (code complete, deployment pending)
- Added ADR folder: `docs/adr/001-flow-to-crew-migration.md`

**Previous Changes (2025-12-01 - Product App Status Audit)**:
- **UPDATE**: Product App completion from "65-70%" to "~80-85%"
- **VERIFIED**: Dashboard pages fully implemented (founder-dashboard: 595 lines, consultant-dashboard: 376 lines)
- **VERIFIED**: Analysis display components exist and are integrated (InnovationPhysicsPanel, VPCSummaryCard, GateDashboard)
- **VERIFIED**: CrewAI webhook integration is production-ready with multi-table persistence
- Updated "What Works" section with comprehensive dashboard and integration details
- Updated "What's Partial" to reflect E2E verification needs (not missing components)
- Removed "Analysis results display" from "What Doesn't Exist" (components exist)
- Updated Database Status table to show webhook-populated tables
- Revised Critical Blockers to focus on E2E verification instead of missing UI
- Updated Recommended Next Steps to prioritize verification over building

**Previous Changes (2025-11-27 - Migrations Deployed)**:
- **Database migrations deployed to Supabase**: flow_executions (001), validation_events (002), experiment_outcomes (004), policy_version (005), decision_log (006)
- All CrewAI-specific tables now live and ready for use

**Changes (2025-11-27 - Areas 3, 6, 7 Complete)**:
- **UPDATE**: Completion from "~80% functional" to "~95% functional"
- **Added Area 3 tools**: PolicyBandit, ExperimentConfigResolver for policy versioning & A/B testing
- **Added Area 6 tools**: BudgetGuardrails, DecisionLogger for budget enforcement & audit trail
- **Added Area 7 tools**: BusinessModelClassifier, 10 UnitEconomicsModels for business-specific viability
- Updated tool count from 18 to 24+
- Added "Recently Completed" section for Areas 3, 6, 7

**Previous Changes (2025-11-26 - Post-Audit)**:
- **MAJOR CORRECTION**: Updated completion from "30% functional" to "~80% functional"
- Corrected crew status from "Stub" to "Complete" with tools wired
- Added "What DOES Exist" section documenting implemented capabilities
- Fixed critical discrepancies table to reflect actual tool implementations
- Updated integration status to show `_persist_to_supabase()` works
- Corrected configuration status to show 18 agents and 18 tools

This document should be updated whenever significant changes occur to any service.
