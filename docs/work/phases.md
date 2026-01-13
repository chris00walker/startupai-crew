---
purpose: "Private technical source of truth for engineering phase status"
status: "active"
last_reviewed: "2026-01-13"
---

# Engineering Phases

## Architecture Summary

### Canonical Architecture (Modal Serverless)

| Metric | Count |
|--------|-------|
| Phases | 5 (0-4) |
| Flows | 5 (Onboarding, VPCDiscovery, Desirability, Feasibility, Viability) |
| Crews | 14 |
| Agents | 45 |
| HITL Checkpoints | 10 |

**Production URL**: `https://chris00walker--startupai-validation-fastapi-app.modal.run`

### Three-Layer Architecture

| Layer | Technology | Status |
|-------|------------|--------|
| Interaction | Netlify Edge Functions | ✅ Production |
| Orchestration | Supabase (PostgreSQL + Realtime) | ✅ Production |
| Compute | Modal (ephemeral, pay-per-second) | ✅ Production |

**ADR**: [ADR-002](../adr/002-modal-serverless-migration.md)

---

## Current Implementation Status

| Component | Code | Evidence Quality |
|-----------|------|------------------|
| Modal infrastructure | ✅ Complete | N/A |
| Phase 0 (Onboarding) | ✅ Complete | ⚠️ LLM-only |
| Phase 1 (VPC Discovery) | ✅ Complete | ⚠️ Partial (only Tavily works) |
| Phase 2 (Desirability) | ✅ Complete | 🔴 Blocked (no ad APIs, placeholder HTML) |
| Phase 3 (Feasibility) | ✅ Complete | ⏳ Not tested |
| Phase 4 (Viability) | ✅ Complete | ⏳ Not tested |

**Details**: See [in-progress.md](./in-progress.md) for per-phase breakdown.

---

## Decision Log

### Remove D1 Interview Agent (2026-01-12)

**Decision**: Remove D1 from DiscoveryCrew

**Rationale**:
- TranscriptionTool is a stub (no Whisper API)
- CalendarTool generates fake time slots
- Agent produces hallucinated interviews, not real customer data
- Surveys are more appropriate for automated SAY evidence

**Impact**: DiscoveryCrew reduces from 5 to 4 agents.

### SurveyTool Integration - Tally (2026-01-12)

**Decision**: Integrate Tally for survey-based SAY evidence

**Rationale**:
- Free unlimited submissions (unlike Typeform's 10/month)
- Native API and webhooks
- Good respondent UX

**Status**: Not yet implemented.

### Supabase Storage for Landing Pages (2026-01-10)

**Decision**: Use Supabase Storage instead of Netlify for landing pages

**Rationale**:
- Netlify token had permission issues
- Landing pages are temporary artifacts, not permanent sites
- Supabase already in stack

**ADR**: [ADR-003](../adr/003-landing-page-storage-migration.md)
**Status**: ✅ Implemented

---

## Schema Alignment

### P0: Modal Tables (✅ DEPLOYED)

| Table | Status |
|-------|--------|
| `validation_runs` | ✅ Deployed |
| `validation_progress` | ✅ Deployed |
| `hitl_requests` | ✅ Deployed |

### P1-P3: VPD Tables (Planned)

| Table | Purpose | Status |
|-------|---------|--------|
| `founders_briefs` | VPD-aligned Phase 0 output | ⏳ Planned |
| `customer_profile_elements` | Jobs/Pains/Gains | ⏳ Planned |
| `value_map_elements` | Products/Relievers/Creators | ⏳ Planned |
| `test_cards` / `learning_cards` | TBI framework | ⏳ Planned |

---

## Legacy Architecture (ARCHIVED)

The 3-crew deployment (Intake, Validation, Decision) has been archived. See `archive/amp-deployment/` for historical reference.

---

## Related Documents

- [in-progress.md](./in-progress.md) - Current work and per-phase status
- [backlog.md](./backlog.md) - Hypothesis queue
- [modal-live-testing.md](./modal-live-testing.md) - Detailed test session logs
- [ADR-002](../adr/002-modal-serverless-migration.md) - Modal migration decision

---
**Last Updated**: 2026-01-13
