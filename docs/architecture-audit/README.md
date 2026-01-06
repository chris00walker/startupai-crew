# StartupAI Architecture Audit

**Date**: 2026-01-06
**Scope**: All 3 StartupAI repositories
**QA Status**: CORRECTED - See QA-CORRECTIONS.md

---

## Documents

| File | Description |
|------|-------------|
| [QA-CORRECTIONS.md](./QA-CORRECTIONS.md) | **READ FIRST** - Corrections to original audit findings |
| [EVOLUTION-PLAN.md](./EVOLUTION-PLAN.md) | Master plan - Synthesized findings + 4-stage evolution roadmap |
| [01-DATABASE-AUDIT.md](./01-DATABASE-AUDIT.md) | Database schema audit (23 tables, 4 phantom, 10+ missing Drizzle) |
| [02-API-AUDIT.md](./02-API-AUDIT.md) | API routes audit (33 active endpoints, 1 dead) |
| [03-CREWAI-AUDIT.md](./03-CREWAI-AUDIT.md) | CrewAI implementation audit (19 agents, no tools wired) |
| [04-FRONTEND-AUDIT.md](./04-FRONTEND-AUDIT.md) | Frontend component audit (75% ready, missing hooks) |

---

## Quick Summary

### Ground Truth vs Documentation

| Spec | Status |
|------|--------|
| 03-validation-spec (Phase 2+) | **PARTIALLY IMPLEMENTED** - 3 crews deployed, no tools |
| 05-phase-0-1-specification | **NOT IMPLEMENTED** - specification only |

### Critical Gaps

1. **Database**: 4 phantom tables (Drizzle exists, no migration)
2. **API**: 05-spec describes endpoints that don't exist
3. **CrewAI**: ALL agents have `tools=[]` - archived tools not connected
4. **Frontend**: Missing data hooks (`useVPC`, `useCrewAIReport`, etc.)

### QA Corrections (Important!)

The original audit had errors. Key corrections:

1. **Onboarding uses Vercel AI SDK**, NOT Agentuity
   - Conversations go through `/api/chat` (Vercel AI SDK streamText)
   - NOT `/api/onboarding/message` (dead code)

2. **Dead code found**:
   - `/api/onboarding/message/route.ts` - 500+ lines never called
   - V1 `OnboardingWizard.tsx` - not used by any page
   - Agentuity references are dead code

3. **Effective endpoint count**: 33 (not 34, one is dead)

### Evolution Strategy

| Stage | Scope | Risk |
|-------|-------|------|
| 1. Database | ADD 6 tables | LOW |
| 2. API | ADD endpoints | LOW |
| 3. CrewAI | Wire tools + state | MEDIUM |
| 4. Frontend | Hooks + transforms | LOW |

### MVP First Step

Create 2 migrations:
1. `founders_briefs` - Phase 0 output
2. `customer_profile_elements` - VPC storage

---

## How to Use This Audit

1. **Read EVOLUTION-PLAN.md** first for the complete picture
2. **Reference individual audits** for detailed findings
3. **Follow the 4-stage evolution** to avoid breaking existing functionality
4. **Start with MVP** (Stage 1, 2 tables) for quick wins

---

## Methodology

This audit was conducted by 4 specialized sub-agents:

1. **Database Auditor** - Examined all migrations and Drizzle schemas
2. **API Auditor** - Examined all 34+ API routes
3. **CrewAI Auditor** - Examined all 3 crew repositories
4. **Frontend Auditor** - Examined components and data hooks

A **Coordinator** synthesized all findings into the evolution plan.
