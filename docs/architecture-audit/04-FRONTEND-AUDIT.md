# Frontend Component Audit Report

**Repository**: `/home/chris/projects/app.startupai.site`
**Date**: 2026-01-06
**Auditor**: Sub-Agent 4 (Frontend Developer)

---

## Executive Summary

- **UI Framework**: Next.js (hybrid App Router + Pages Router)
- **Component Library**: shadcn/ui (New York theme) + Tailwind CSS
- **Overall Status**: 75% ready - UI excellent, data integration incomplete

### Critical Findings

1. **Canvas UIs exist** but expect simplified data (strings vs complex objects)
2. **Missing hooks**: `useCrewAIReport`, `useVPC`, `useBMC`, `useApprovals`
3. **Data transformation gap**: DB stores complex objects, UI expects strings
4. **HITL approval UI** is 100% complete but needs backend integration

---

## Pages & Routes Structure

### App Router (`/src/app/`)

| Route | Purpose | Status |
|-------|---------|--------|
| `/signup`, `/login` | Authentication | Active |
| `/onboarding/*` | AI-powered onboarding | Active |
| `/project/[id]/*` | Project views | Active |
| `/approvals` | HITL approval dashboard | Built |
| `/api/*` | API routes (34+) | Active |

### Pages Router (`/src/pages/`)

| Page | Purpose | Status |
|------|---------|--------|
| `/founder-dashboard` | Main founder view | Working |
| `/consultant-dashboard` | Consultant portfolio | Working |
| `/canvas/vpc` | VPC editor | Built (localStorage) |
| `/canvas/bmc` | BMC editor | Built (localStorage) |
| `/canvas/tbi` | TBI editor | Built |
| `/ai-analysis` | CrewAI results | Built (no data hook) |
| `/analytics` | Project analytics | Built |
| `/validation` | Validation workflow | Built |

---

## Dashboard Components

### FounderDashboard

**Location**: `/src/pages/founder-dashboard.tsx`

**Tabs**:
1. Overview - Gate status, evidence quality
2. Canvases - VPC, BMC, TBI gallery
3. Assumption Map - Strategyzer mapping
4. Experiment Cards - Test planning
5. Evidence & Learnings - Evidence ledger

**Data Dependencies**:

| Component | Data Source | Status |
|-----------|-------------|--------|
| QuickStats | `useGateEvaluation` | Working |
| GateDashboard | `useProjects` + Netlify Function | Working |
| ValidationResultsSummary | Reports table | **MISSING HOOK** |
| InnovationPhysicsPanel | CrewAI state | **MISSING HOOK** |
| VPCSummaryCard | VPC table | **MISSING HOOK** |

---

## Canvas Components

### ValuePropositionCanvas

**Location**: `/src/components/canvas/ValuePropositionCanvas.tsx`

**Expected Data Shape (UI)**:
```typescript
{
  customerProfile: {
    jobs: string[],
    pains: string[],
    gains: string[]
  },
  valueMap: {
    productsAndServices: string[],
    gainCreators: string[],
    painRelievers: string[]
  }
}
```

**Actual Database Shape**:
```typescript
{
  jobs: VPCJobItem[],  // {id, functional, emotional, social, importance, source}
  pains: VPCPainItem[], // {id, description, intensity, source}
  gains: VPCGainItem[], // {id, description, importance, source}
  // ...
}
```

**Storage**: localStorage with key `vpc-canvas-${canvasId}`
**Gap**: Expects simple arrays, DB stores complex objects with metadata.

### BusinessModelCanvas

**Location**: `/src/components/canvas/BusinessModelCanvas.tsx`

**Expected Data Shape (UI)**:
```typescript
{
  keyPartners: string[],
  keyActivities: string[],
  keyResources: string[],
  valuePropositions: string[],
  customerRelationships: string[],
  channels: string[],
  customerSegments: string[],
  costStructure: string[],
  revenueStreams: string[]
}
```

**Storage**: localStorage
**Gap**: Same as VPC - needs transformation layer.

---

## Report Display

### CrewAIReportViewer

**Location**: `/src/components/reports/CrewAIReportViewer.tsx`

**Expected Data Shape**:
```typescript
{
  metadata: {
    phase: Phase,
    iteration: number,
    businessIdea: string,
    problemStatement: string
  },
  desirability: {
    customerProfiles: Record<string, CustomerProfile>,
    analysisInsights: string[],
    adMetrics: { impressions, clicks, signups, spend }
  },
  feasibility: {
    feasibilitySignal: FeasibilitySignal,
    coreFeaturesFeasible: Record<string, string>,
    removedFeatures: string[],
    monthlyRunCost: number
  },
  viability: {
    viabilitySignal: ViabilitySignal,
    cac: number,
    ltv: number,
    ltv_cac_ratio: number,
    grossMargin: number
  },
  governance: {
    status: QAStatus,
    issues: string[],
    confidence_score: number
  }
}
```

**Views**: D-F-V Risk Axis OR Strategyzer Phase
**Status**: Built, **NO HOOK TO FETCH DATA**

---

## Approval System

### Components

| Component | Purpose | Status |
|-----------|---------|--------|
| `ApprovalList` | List with filters | Built |
| `ApprovalCard` | Individual card | Built |
| `ApprovalDetailModal` | Full details | Built |
| `ApprovalTypeIndicator` | Type badge | Built |
| `FounderAvatar` | AI founder avatar | Built |
| `EvidenceSummary` | Evidence context | Built |

**Expected Data Shape** (`ApprovalRequest`):
```typescript
{
  id: string;
  approval_type: ApprovalType;
  owner_role: OwnerRole;
  title: string;
  description: string;
  task_output: Record<string, unknown>;
  evidence_summary: Record<string, unknown>;
  options: ApprovalOption[];
  status: 'pending' | 'approved' | 'rejected';
}
```

**Founder Metadata**:
```typescript
{
  sage: { name: 'Sage', title: 'CSO', specialty: 'Strategic coordination' },
  forge: { name: 'Forge', title: 'CTO', specialty: 'Technical feasibility' },
  pulse: { name: 'Pulse', title: 'CGO', specialty: 'Growth strategy' },
  compass: { name: 'Compass', title: 'CPO', specialty: 'Product vision' },
  guardian: { name: 'Guardian', title: 'CGO', specialty: 'QA/Compliance' },
  ledger: { name: 'Ledger', title: 'CFO', specialty: 'Financial analysis' }
}
```

**Status**: UI 100% complete, needs backend webhook integration.

---

## Data Hooks

### Existing (Working)

| Hook | Purpose | Status |
|------|---------|--------|
| `useProjects` | Fetch user projects | Working |
| `useActiveProjects` | Active projects only | Working |
| `useGateEvaluation` | Gate status (Netlify Function) | Working |
| `useGateAlerts` | Gate readiness alerts | Working |
| `useRecentActivity` | Recent activity | Working |
| `useRecommendedActions` | Next steps | Working |

### Missing (Need to Create)

| Hook | Purpose | Tables/APIs |
|------|---------|-------------|
| `useCrewAIReport` | Fetch CrewAI reports | `reports` table |
| `useVPC` | Fetch/update VPC | `value_proposition_canvas` |
| `useBMC` | Fetch/update BMC | `business_model_canvas` |
| `useApprovals` | Fetch pending approvals | `approval_requests` |
| `useFoundersBrief` | Fetch founder's brief | `founders_briefs` |

---

## TypeScript Interfaces

**Location**: `/src/types/crewai.ts` (894 lines)

**Key Interfaces**:
```typescript
// Validation State
export interface StartupValidationState { /* 100+ fields */ }

// Customer & Market
export interface CustomerProfile { segment_name, jobs, pains, gains }
export interface ValueMap { products_services, pain_relievers, gain_creators }
export interface CompetitorReport { competitors, positioning_map }

// Signals
export type DesirabilitySignal = 'no_signal' | 'weak_interest' | 'strong_commitment'
export type FeasibilitySignal = 'unknown' | 'green' | 'orange_constrained' | 'red_impossible'
export type ViabilitySignal = 'unknown' | 'profitable' | 'marginal' | 'underwater'

// Approvals
export interface ApprovalRequest { id, approval_type, owner_role, options }
export interface ApprovalOption { id, label, description, recommended, risk_level }
```

---

## Component → Data Dependency Map

### High-Priority Gaps

| Component | Expected Data | Issue |
|-----------|---------------|-------|
| `CrewAIReportViewer` | Structured report | No hook |
| `ValidationResultsSummary` | Validation results | No hook |
| `VPCCanvas` | VPC from DB | localStorage only |
| `BMCCanvas` | BMC from DB | localStorage only |
| `ApprovalList` | Pending approvals | No hook |

---

## Data Transformation Requirements

### VPC: Database → UI

**Database**:
```json
{
  "jobs": [
    {
      "id": "uuid-1",
      "functional": "Reduce customer acquisition costs",
      "emotional": "Feel confident",
      "importance": 9,
      "source": "crewai"
    }
  ]
}
```

**UI Expected**:
```json
{
  "customerProfile": {
    "jobs": ["Reduce customer acquisition costs"]
  }
}
```

**Transform Function**:
```typescript
function dbToUI(dbData: VPCDBShape): VPCUIShape {
  return {
    customerProfile: {
      jobs: dbData.jobs.map(j => j.functional),
      pains: dbData.pains.map(p => p.description),
      gains: dbData.gains.map(g => g.description)
    },
    valueMap: {
      productsAndServices: dbData.productsAndServices.map(p => p.text),
      gainCreators: dbData.gainCreators.map(gc => gc.creator),
      painRelievers: dbData.painRelievers.map(pr => pr.relief)
    }
  }
}
```

### UI → Database (Reverse)

```typescript
function uiToDb(uiData: VPCUIShape, projectId: string): VPCDBShape {
  return {
    jobs: uiData.customerProfile.jobs.map((text, i) => ({
      id: crypto.randomUUID(),
      functional: text,
      importance: 5, // default
      source: 'manual'
    })),
    // ... similar for pains, gains, etc.
  }
}
```

---

## Recommendations

### Priority 1: Implement Missing Hooks

```typescript
// /hooks/useCrewAIReport.ts
export function useCrewAIReport(projectId: string) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['crewai-report', projectId],
    queryFn: () => fetchReport(projectId)
  });
  return { reports: data, isLoading, error };
}

// /hooks/useVPC.ts
export function useVPC(projectId: string) {
  // Fetch from DB, transform to UI shape
  // Mutation to save back (transform to DB shape)
}
```

### Priority 2: Build Transformation Layer

Create `/lib/transforms/`:
- `vpc-transforms.ts` - VPC DB ↔ UI
- `bmc-transforms.ts` - BMC DB ↔ UI
- `report-transforms.ts` - Report JSONB → Component

### Priority 3: Wire Canvas Components

1. Replace localStorage with `useVPC` hook
2. Add "Load from CrewAI" button
3. Add save-to-DB on change
4. Keep localStorage as fallback/cache

### Priority 4: Connect Approval System

1. Implement `useApprovals` hook
2. Wire to `/api/approvals` GET
3. Add decision submission to `/api/approvals/[id]` PATCH
4. Test webhook flow end-to-end

---

## Overall Assessment

| Area | Status | Notes |
|------|--------|-------|
| UI Components | 95% | Excellent, well-built |
| Data Hooks | 50% | Missing critical hooks |
| Type Safety | 90% | Comprehensive types exist |
| Data Transformation | 0% | Not implemented |
| Backend Integration | 70% | APIs exist, hooks missing |

**Frontend is 75% ready**. UI excellent, data integration incomplete.
