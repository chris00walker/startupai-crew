# StartupAI Architecture Evolution Plan

**Document Type**: Architecture Decision Record + Evolution Roadmap
**Date**: 2026-01-06
**Principle**: EVOLVE, not refactor. Phase 0-1 (05-spec) is a PREQUEL that feeds INTO Phase 2+ (03-spec).

---

## Executive Summary

This document synthesizes findings from a comprehensive 4-agent audit across all 3 StartupAI repositories to establish ground truth and plan an evolutionary path from the current architecture to the enhanced Phase 0-1 specification.

**Key Finding**: The 05-spec describes a system that doesn't exist. The actual implementation uses Agentuity agent-driven onboarding, not interview-based APIs. Evolution must be additive, not replacement.

---

## 1. Ground Truth Summary

### 1.1 Database Reality

| Table | Supabase | Drizzle | Status |
|-------|----------|---------|--------|
| `user_profiles` | DEPLOYED | EXISTS | Working |
| `projects` | DEPLOYED | EXISTS | Working |
| `hypotheses` | DEPLOYED | EXISTS | Working |
| `evidence` | DEPLOYED | EXISTS | Working |
| `experiments` | DEPLOYED | EXISTS | Working |
| `reports` | DEPLOYED | EXISTS | Working |
| `entrepreneur_briefs` | DEPLOYED (29 cols) | **MISSING** | Needs schema |
| `onboarding_sessions` | DEPLOYED (20 cols) | **MISSING** | Needs schema |
| `approval_requests` | DEPLOYED | **MISSING** | Needs schema |
| `approval_history` | DEPLOYED | **MISSING** | Needs schema |
| `approval_preferences` | DEPLOYED | **MISSING** | Needs schema |
| `learnings` | DEPLOYED | **MISSING** | Flywheel table |
| `patterns` | DEPLOYED | **MISSING** | Flywheel table |
| `outcomes` | DEPLOYED | **MISSING** | Flywheel table |
| `domain_expertise` | DEPLOYED | **MISSING** | Flywheel table |
| `value_proposition_canvas` | **NOT EXISTS** | EXISTS | PHANTOM |
| `business_model_canvas` | **NOT EXISTS** | EXISTS | PHANTOM |
| `crewai_validation_states` | **NOT EXISTS** | EXISTS (67 cols) | PHANTOM |
| `learning_cards` | **NOT EXISTS** | EXISTS | PHANTOM |
| `founders_briefs` | **NOT EXISTS** | **NOT EXISTS** | 05-spec planned |
| `customer_profile_elements` | **NOT EXISTS** | **NOT EXISTS** | 05-spec planned |
| `value_map_elements` | **NOT EXISTS** | **NOT EXISTS** | 05-spec planned |
| `vpc_fit_scores` | **NOT EXISTS** | **NOT EXISTS** | 05-spec planned |
| `test_cards` | **NOT EXISTS** | **NOT EXISTS** | 05-spec planned |

**Legend**:
- **PHANTOM**: Drizzle schema exists but no migration/table in database
- **MISSING**: Table exists but no Drizzle schema for type-safe queries

### 1.2 API Reality

| Documented Endpoint | Actual Status | Notes |
|---------------------|---------------|-------|
| `/api/onboarding/start` | EXISTS | Agentuity agent, NOT interview-based |
| `/api/onboarding/message` | EXISTS | Streaming AI conversation |
| `/api/onboarding/complete` | EXISTS | Creates project, fires CrewAI |
| `/api/crewai/webhook` | EXISTS | Unified webhook (works) |
| `/api/crewai/status` | EXISTS | Poll kickoff status |
| `/api/approvals` | EXISTS | GET list, PATCH decision |
| `/api/vpc/[projectId]` | EXISTS | GET segments, POST upsert |
| `/api/interview/start` | **NOT EXISTS** | 05-spec describes |
| `/api/interview/continue` | **NOT EXISTS** | 05-spec describes |
| `/api/brief/{id}` | **NOT EXISTS** | 05-spec describes |
| `/api/brief/approve` | **NOT EXISTS** | 05-spec describes |

**34 total endpoints exist** - see full audit for details.

### 1.3 CrewAI Reality

| Component | Documented | Actual |
|-----------|------------|--------|
| Architecture | Flows (03-spec) | Crews (type="crew") |
| Crew 1: Intake | 4 agents, 6 tasks, 1 HITL | DEPLOYED, `tools=[]` |
| Crew 2: Validation | 12 agents, 21 tasks, 5 HITL | DEPLOYED, `tools=[]` |
| Crew 3: Decision | 3 agents, 5 tasks, 1 HITL | DEPLOYED, `tools=[]` |
| Phase 0 OnboardingFlow | Specified in 05-spec | NOT IMPLEMENTED |
| Phase 1 VPCDiscoveryFlow | Specified in 05-spec | NOT IMPLEMENTED |
| Archived Tools | 24+ tools in archive | NOT CONNECTED |
| State Persistence | Between crews | NOT IMPLEMENTED |

**Total: 19 agents, 32 tasks, 7 HITL checkpoints deployed**

### 1.4 Frontend Reality

| Component | Status | Issue |
|-----------|--------|-------|
| ValuePropositionCanvas | EXISTS | Expects `string[]`, DB has complex objects |
| BusinessModelCanvas | EXISTS | Expects `string[]`, DB has complex objects |
| CrewAIReportViewer | EXISTS | No `useCrewAIReport` hook |
| ApprovalList/Card | EXISTS | No `useApprovals` hook |
| FounderDashboard | WORKING | Gate evaluation via Netlify Function |
| OnboardingWizard | WORKING | Agentuity agent-driven |
| `useVPC` | **NOT EXISTS** | Components use localStorage |
| `useBMC` | **NOT EXISTS** | Components use localStorage |
| `useCrewAIReport` | **NOT EXISTS** | No implementation |
| `useApprovals` | **NOT EXISTS** | No implementation |

**Frontend is 75% ready** - UI excellent, data integration incomplete.

---

## 2. Integration Point Analysis

### 2.1 Current Data Flow (Working)

```
[User starts onboarding]
        │
        ▼
/api/onboarding/start ──► Creates onboarding_session
        │
        ▼
/api/onboarding/message ──► Agentuity AI conversation (streaming)
        │
        ▼
/api/onboarding/complete ──► Creates:
    1. entrepreneur_briefs (29 columns)
    2. projects (links to user)
    3. POST to CrewAI /kickoff
        │
        ▼
[CrewAI Crew 1: Intake runs]
    - Parses entrepreneur_input
    - Creates VPC (in-memory, not persisted)
    - HITL: approve_intake_to_validation
    - Triggers Crew 2 via InvokeCrewAIAutomationTool
        │
        ▼
[CrewAI Crew 2: Validation runs]
    - D/F/V experiments (no real tools)
    - 5 HITL checkpoints
    - Triggers Crew 3
        │
        ▼
[CrewAI Crew 3: Decision runs]
    - Synthesizes evidence
    - HITL: request_human_decision
    - Sends webhook to /api/crewai/webhook
        │
        ▼
/api/crewai/webhook ──► Persists to:
    - reports
    - evidence
    - crewai_validation_states
    - public_activity_log
```

### 2.2 Target Data Flow (With Phase 0-1)

```
[Phase 0: Enhanced Onboarding]
        │
        ▼
founders_briefs ──► Structured brief with:
    - concept, one_liner
    - target_who, target_what
    - customer_segment, characteristics
    - solution_approach, key_features
    - key_assumptions (ranked)
    - success_criteria
    - QA status
        │
        ▼
[Phase 1: VPC Discovery]
        │
        ▼
customer_profile_elements ──► Jobs/Pains/Gains
value_map_elements ──► Products/Pain Relievers/Gain Creators
vpc_fit_scores ──► Fit tracking
test_cards / learning_cards ──► TBI experiments
        │
        ▼
[Phase 2+: Deployed Crews]
    - Intake Crew receives founders_briefs + VPC state
    - Validation Crew runs experiments
    - Decision Crew synthesizes
```

### 2.3 Key Integration Points

1. **entrepreneur_briefs → founders_briefs**: Can coexist - `founders_briefs` is a superset
2. **VPC Storage**: Need `customer_profile_elements` + `value_map_elements` tables
3. **Crew 1 Input**: Should receive structured `founders_briefs` + initial VPC state
4. **State Handoff**: Need Supabase-backed state or webhook-based state passing

---

## 3. Evolution Sequence

### Stage 1: Database Additions (ADD only)

**Objective**: Create missing tables without touching existing ones.

**New Tables Required**:

```sql
-- Phase 0 Output
CREATE TABLE founders_briefs ( ... );

-- Phase 1 VPC Storage
CREATE TABLE customer_profile_elements ( ... );
CREATE TABLE value_map_elements ( ... );
CREATE TABLE vpc_fit_scores ( ... );

-- TBI Experiment Framework
CREATE TABLE test_cards ( ... );
CREATE TABLE learning_cards ( ... );
```

**Drizzle Schemas to Create** (in product app):
- `founders-briefs.ts`
- `customer-profile-elements.ts`
- `value-map-elements.ts`
- `vpc-fit-scores.ts`
- `test-cards.ts`
- `learning-cards.ts`

**Risk**: LOW - pure additions

---

### Stage 2: API Additions

**Objective**: Add new endpoints while keeping existing ones working.

**New Endpoints**:

```
POST /api/brief/create          # Create founders_brief
GET  /api/brief/{id}            # Get founders_brief
PUT  /api/brief/{id}            # Update founders_brief
POST /api/brief/{id}/approve    # HITL approval

GET  /api/vpc/{projectId}/profile    # Get customer profile elements
POST /api/vpc/{projectId}/profile    # Upsert profile element

GET  /api/vpc/{projectId}/valuemap   # Get value map elements
POST /api/vpc/{projectId}/valuemap   # Upsert value map element

GET  /api/vpc/{projectId}/fit        # Get current fit score
POST /api/vpc/{projectId}/fit        # Calculate fit score

POST /api/experiments/test-card      # Create TBI test card
POST /api/experiments/learning-card  # Record learning
```

**Extend Existing** (backwards compatible):
- `/api/onboarding/complete` - Also create `founders_briefs` if available
- `/api/crewai/webhook` - Update `vpc_fit_scores`, create `learning_cards`

**Risk**: LOW - additive logic

---

### Stage 3: CrewAI Additions

**Objective**: Wire tools to deployed crews, add state persistence.

**Tools to Wire** (from archive):

| Tool | Target | Purpose |
|------|--------|---------|
| `TavilySearchTool` | Crew 1 (S2) | Customer research |
| `LandingPageGeneratorTool` | Crew 2 (F2) | LP generation |
| `LandingPageDeploymentTool` | Crew 2 (F2) | Deploy to Netlify |
| `GuardianReviewTool` | Crew 2 (G1) | Creative QA |
| `MethodologyCheckTool` | Crew 1 (G1) | VPC validation |
| `LearningCaptureTool` | Crew 3 (C3) | Flywheel capture |
| `UnitEconomicsModels` | Crew 2 (L1) | Viability calcs |
| `PrivacyGuardTool` | Crew 2 (G2) | PII stripping |

**State Persistence** (Recommended: Supabase table):
- Create `crew_execution_state` table
- Each crew reads/writes via Supabase client

**Risk**: MEDIUM - requires redeploy of all 3 crews

---

### Stage 4: Frontend Additions

**Objective**: Create hooks that connect UI to DB.

**Hooks to Create**:

```typescript
useVPC(projectId): {
  customerProfile: { jobs, pains, gains },
  valueMap: { products, painRelievers, gainCreators },
  fitScore,
  upsertProfileElement,
  upsertValueMapElement,
}

useFoundersBrief(projectId): {
  brief, isLoading, approve, update
}

useCrewAIReport(projectId): {
  reports, latestReport, isLoading
}

useApprovals(projectId?): {
  pending, history, approve
}
```

**Transformation Layer** (DB ↔ UI):
- `customer_profile_elements[]` → `{ jobs: string[], pains: string[], gains: string[] }`
- Bidirectional for edits

**Risk**: LOW - additive changes

---

## 4. Minimal Viable First Step

### MVP: Create 2 Tables

**Why These**:
1. `founders_briefs` - Required for Phase 0 output
2. `customer_profile_elements` - Required for VPC storage

**Migration 1: founders_briefs**

```sql
CREATE TABLE founders_briefs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id) UNIQUE,
  concept TEXT NOT NULL,
  one_liner TEXT,
  target_who TEXT NOT NULL,
  target_what TEXT NOT NULL,
  current_alternatives JSONB,
  customer_segment TEXT NOT NULL,
  customer_characteristics JSONB,
  solution_approach TEXT NOT NULL,
  key_features JSONB,
  key_assumptions JSONB NOT NULL,
  problem_resonance_target DECIMAL(3,2) DEFAULT 0.50,
  zombie_ratio_max DECIMAL(3,2) DEFAULT 0.30,
  fit_score_target INTEGER DEFAULT 70,
  concept_legitimacy TEXT CHECK (concept_legitimacy IN ('pass', 'fail', 'pending')),
  intent_verification TEXT CHECK (intent_verification IN ('pass', 'fail', 'pending')),
  qa_issues JSONB,
  status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'pending_approval', 'approved', 'rejected')),
  approved_at TIMESTAMPTZ,
  approved_by UUID,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_founders_briefs_project ON founders_briefs(project_id);
CREATE INDEX idx_founders_briefs_status ON founders_briefs(status);
```

**Migration 2: customer_profile_elements**

```sql
CREATE TABLE customer_profile_elements (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id),
  element_type TEXT NOT NULL CHECK (element_type IN ('job', 'pain', 'gain')),
  element_text TEXT NOT NULL,
  job_type TEXT CHECK (job_type IN ('functional', 'social', 'emotional')),
  job_statement TEXT,
  pain_severity TEXT CHECK (pain_severity IN ('extreme', 'severe', 'moderate', 'mild')),
  gain_relevance TEXT CHECK (gain_relevance IN ('essential', 'nice_to_have', 'unexpected')),
  priority INTEGER DEFAULT 0,
  importance_score DECIMAL(3,2),
  validation_status TEXT DEFAULT 'untested' CHECK (validation_status IN ('validated', 'invalidated', 'untested')),
  confidence_score DECIMAL(3,2),
  evidence_count INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_profile_elements_project ON customer_profile_elements(project_id);
CREATE INDEX idx_profile_elements_type ON customer_profile_elements(element_type);
```

**This Enables**:
- Phase 0 to output `founders_briefs` (once API is built)
- VPC components to read/write Jobs/Pains/Gains (once hook is built)
- No changes to existing flow

---

## 5. Risk Assessment

| Stage | Risk | Likelihood | Impact | Mitigation |
|-------|------|------------|--------|------------|
| 1 | Migration conflicts | LOW | HIGH | Test in staging first |
| 1 | Schema drift | MEDIUM | MEDIUM | Generate Drizzle from SQL |
| 2 | Route conflicts | LOW | HIGH | Use distinct paths |
| 2 | Webhook breaks | MEDIUM | HIGH | Feature flag, test thoroughly |
| 3 | Tools fail | MEDIUM | MEDIUM | Test in isolation first |
| 3 | Crew redeploy breaks prod | HIGH | HIGH | Deploy to staging UUIDs first |
| 3 | AMP caching issue | KNOWN | HIGH | Escalate to CrewAI support |
| 4 | Type mismatches | MEDIUM | LOW | Strict TypeScript interfaces |
| 4 | localStorage fallback hides issues | MEDIUM | MEDIUM | Add logging, health checks |

---

## 6. Success Criteria

### Stage 1 Complete When:
- [ ] All 6 new tables exist in Supabase
- [ ] Drizzle schemas exist and type-check
- [ ] Migrations tracked in `supabase/migrations/`
- [ ] SELECT queries return empty results (tables exist)

### Stage 2 Complete When:
- [ ] `/api/brief/*` endpoints respond 200
- [ ] `/api/vpc/{projectId}/profile` works
- [ ] Existing endpoints unchanged
- [ ] Webhook still persists to existing tables

### Stage 3 Complete When:
- [ ] S2 agent has `TavilySearchTool` wired
- [ ] F2 agent has `LandingPageGeneratorTool` wired
- [ ] State persists across crew handoff
- [ ] Full chain completes successfully

### Stage 4 Complete When:
- [ ] `useVPC` returns data from DB
- [ ] `useFoundersBrief` returns data from DB
- [ ] VPC canvas saves to DB (not localStorage)
- [ ] No TypeScript errors

### Full Evolution Complete When:
- [ ] Phase 0 onboarding → `founders_briefs` created
- [ ] User adds Jobs/Pains/Gains → `customer_profile_elements` created
- [ ] CrewAI reads `founders_briefs` as input
- [ ] CrewAI updates `vpc_fit_scores`
- [ ] Learning cards created from experiments
- [ ] E2E: Onboarding → Crews → Dashboard displays VPC with fit score

---

## 7. Documentation Reconciliation

### Critical Issue

The **05-spec describes a different system than what exists**:

| 05-Spec Describes | Reality |
|-------------------|---------|
| `/interview/start` | `/api/onboarding/start` (Agentuity) |
| `/interview/continue` | `/api/onboarding/message` (streaming) |
| `/brief/{id}` | Not implemented |
| `/brief/approve` | `/api/approvals/[id]` (general) |
| Interview-based Q&A | AI conversation flow |

### Options

1. **Update 05-spec** to match actual architecture (recommended)
2. **Build interview system** as alternative flow
3. **Hybrid**: Use conversation for exploration, interview for structured capture

---

## 8. File References

### CrewAI Repository

```
/home/chris/projects/startupai-crew/
├── src/intake_crew/           # Crew 1 (deployed)
├── archive/flow-architecture/
│   └── startupai/tools/       # 24+ tools to migrate
└── docs/master-architecture/
    ├── 03-validation-spec.md  # Phase 2+ spec
    └── 05-phase-0-1-specification.md  # Phase 0-1 spec
```

### Product App

```
/home/chris/projects/app.startupai.site/
├── frontend/src/
│   ├── db/schema/             # Drizzle schemas
│   ├── hooks/                 # React hooks (missing several)
│   └── components/            # UI components
├── app/api/                   # API routes
└── supabase/migrations/       # SQL migrations
```

---

## Next Actions

1. **Approve this plan** or request modifications
2. **Execute Stage 1 MVP**: Create `founders_briefs` + `customer_profile_elements` migrations
3. **Create missing Drizzle schemas** for existing tables
4. **Wire archived tools** to deployed crews

---

**Document Author**: Architecture Synthesis (5-Agent Audit)
**Review Status**: Pending Human Approval
**Last Updated**: 2026-01-06
