---
purpose: Marketing site AI integration architecture
status: planning
last_reviewed: 2026-01-08
vpd_compliance: true
---

# Marketing Site AI Integration

> **VPD Framework**: The marketing site showcases StartupAI's Value Proposition Design methodology. See [03-methodology.md](../03-methodology.md) for framework details.

The marketing site (startupai.site) requires AI integration to embody our transparency values and demonstrate the AI Founders' capabilities before conversion.

## Customer Service Agent

**Dual Placement Strategy**:

### 1. Floating Chat Widget
- Persistent bottom-right bubble available on all pages
- General support agent answering questions about StartupAI, pricing, features
- Implemented in site `layout.tsx` for global availability
- Uses Vercel AI SDK for streaming responses

### 2. Founder-Specific Chat in Modals
- Extend `FounderProfileCard.tsx` with tabbed interface: "Profile" | "Chat"
- Each founder responds in character based on their role:
  - **Sage**: Strategy questions, VPC design, customer insights
  - **Forge**: Technical feasibility, build considerations
  - **Pulse**: Growth tactics, market signals
  - **Compass**: Synthesis, tradeoffs, decision support
  - **Guardian**: Governance, risk, accountability
  - **Ledger**: Financial viability, unit economics
- System prompts derived from founder personality/role in `aiFounders` data

### Backend Architecture
- Netlify function: `/.netlify/functions/chat`
- Input: `{ message: string, founderId?: string, context?: string }`
- Routes to AI model with founder-specific system prompts
- Stores conversation history in Supabase for continuity

## Live Data Integration

Replace all hardcoded mock data with live platform metrics to demonstrate transparency.

### Supabase Schema (New Tables)

```sql
-- Aggregated platform statistics
CREATE TABLE platform_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  metric_name TEXT NOT NULL,          -- 'validations_completed', 'mvps_built', etc.
  metric_value INTEGER NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Anonymized recent agent activities
CREATE TABLE public_activity_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  founder_id TEXT NOT NULL,           -- 'sage', 'forge', etc.
  activity_type TEXT NOT NULL,        -- 'analysis', 'build', 'validation'
  description TEXT NOT NULL,          -- Anonymized activity description
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Per-founder performance metrics
CREATE TABLE founder_stats (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  founder_id TEXT NOT NULL UNIQUE,
  analyses_completed INTEGER DEFAULT 0,
  accuracy_rate DECIMAL(5,2),
  avg_response_time INTERVAL,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Netlify Functions (Data Layer)

**`/.netlify/functions/metrics`**
- Returns: platform stats + founder stats
- Caches responses (5-10 min TTL)
- Reduces Supabase load

**`/.netlify/functions/activities`**
- Returns: recent anonymized activities
- Filterable by founder
- Paginated results

### Frontend Data Flow

**Current State** (to replace):
```typescript
// src/data/agentActivity.ts - hardcoded
export const aiFounders = [
  { name: "Guardian", stats: { analyses: 142, accuracy: "94%" } },
  // ...
];
```

**Target State**:
```typescript
// src/data/agentActivity.ts - fetches live data
export async function getFounderStats(): Promise<FounderStats[]> {
  const response = await fetch('/.netlify/functions/metrics');
  return response.json();
}

// Components use React Query or SWR for caching
const { data: founders, isLoading } = useQuery('founders', getFounderStats);
```

### Mock Data Locations to Replace

| File | Data | Replacement |
|------|------|-------------|
| `src/data/agentActivity.ts:45-192` | `aiFounders` stats | `/.netlify/functions/metrics` |
| `src/data/agentActivity.ts:195-265` | `recentActivities` | `/.netlify/functions/activities` |
| `src/data/agentActivity.ts` | `dashboardMetrics` | `/.netlify/functions/metrics` |
| `src/app/demo/dashboard/page.tsx:29-65` | `activeWorkflows` | Keep demo data (not production) |

**Note**: Static data (names, roles, avatars, personalities) remains hardcoded. Only dynamic metrics and activities fetch from API.

## Implementation Sequence

1. **Supabase schema** - Create tables for metrics and activities
2. **Netlify functions** - Build data fetching endpoints with caching
3. **Update agentActivity.ts** - Export async fetch functions instead of static arrays
4. **Component updates** - Add loading states, error handling, async data fetching
5. **Shared chat component** - Build reusable chat UI
6. **Floating widget** - Implement global chat bubble
7. **Founder modal chat** - Add chat tab to existing modals
8. **Chat backend** - Create Netlify function with founder-specific prompts

## Data Architecture Decision

**Recommended: Netlify Functions → Supabase**

Rationale:
- Keeps marketing site self-contained and deployable
- Enables caching to reduce Supabase load
- Allows rate limiting and security at function layer
- Can be upgraded to call product app API later if needed
- Consistent with existing `/.netlify/functions/contact` pattern

---

## VPD Framework Demonstration

Showcase the VPD methodology to educate and build trust with prospects.

### Educational Content

| Content Type | Purpose | Placement |
|--------------|---------|-----------|
| **VPD Overview** | Explain Osterwalder/Pigneur framework | /methodology page |
| **VPC → TBI → BMC Flow** | Show progression through validation | Interactive diagram |
| **Test Cards/Learning Cards** | Demonstrate experiment rigor | Sample artifacts |
| **Evidence Hierarchy** | SAY vs DO distinction | Trust metrics |

### VPC → TBI → BMC Animation Concept

Interactive visualization showing the validation progression:

```
Stage 1: VPC Discovery
┌─────────────────────────────────────┐
│  Customer Profile  │   Value Map    │
│  [Jobs] [Pains]    │  [Products]    │
│  [Gains]           │  [Relievers]   │
│                    │  [Creators]    │
└─────────────────────────────────────┘
        ↓ (fit score animation)

Stage 2: Testing Business Ideas
┌─────────────────────────────────────┐
│  Test Cards → Experiments → Learning│
│  [Design]    [Execute]    [Capture] │
└─────────────────────────────────────┘
        ↓ (evidence flow animation)

Stage 3: Business Model Canvas
┌─────────────────────────────────────┐
│  Validated sections populate based  │
│  on evidence from experiments       │
└─────────────────────────────────────┘
```

## Example Artifacts (Anonymized)

Showcase real (anonymized) examples to demonstrate quality:

### Customer Profile Example

```markdown
## Validated Customer Profile: B2B HR Tech

### Customer Jobs (Ranked by Importance)
1. **Functional**: "Automate new hire paperwork completion" (validated, 0.82 confidence)
2. **Functional**: "Track compliance training completion" (validated, 0.78 confidence)
3. **Social**: "Appear modern to candidates" (validated, 0.65 confidence)

### Top Pains (Ranked by Severity)
1. "Manual data entry across multiple systems" (extreme, validated)
2. "Compliance audit failures" (severe, validated)
3. "Delayed new hire productivity" (moderate, validated)

### Top Gains (Ranked by Relevance)
1. "Faster time-to-productivity" (essential, validated)
2. "Error-free compliance" (essential, validated)
3. "Better candidate experience" (nice-to-have, validated)
```

### Value Map Example

```markdown
## Value Map: HR Automation Platform

### Products & Services
- Automated onboarding workflow system
- Compliance tracking dashboard
- New hire portal

### Pain Relievers
- "Single source of truth eliminates re-entry" → addresses #1 pain
- "Automated compliance reminders" → addresses #2 pain
- "Day-1 ready setup" → addresses #3 pain

### Gain Creators
- "New hires productive in 3 days vs 2 weeks" → creates #1 gain
- "100% audit pass rate" → creates #2 gain
- "Modern mobile experience" → creates #3 gain

**Fit Score: 78/100** (Strong)
```

### Before/After BMC Example

Show how the BMC evolves from hypothesis to validated:

| BMC Block | Before (Hypothesis) | After (Validated) |
|-----------|---------------------|-------------------|
| Customer Segments | "HR teams at growing companies" | "HR teams at 50-500 employee tech companies with compliance burden" |
| Value Propositions | "Streamlined HR automation" | "Compliance-first onboarding that reduces time-to-productivity by 80%" |
| Revenue Streams | "SaaS subscription" | "$49/employee/month with 85% gross margin, validated via pricing experiments" |

## Experiment Visibility

Show the types of experiments run and their outcomes:

### Experiment Types Dashboard

| Experiment Type | Count | Avg Duration | Pass Rate |
|-----------------|-------|--------------|-----------|
| Customer Interviews | 847 | 45 min | 72% |
| Landing Page Tests | 423 | 7 days | 58% |
| Ad Creative Tests | 312 | 5 days | 45% |
| Pricing A/B Tests | 156 | 14 days | 61% |
| Prototype Usability | 89 | 2 hours | 68% |

### Time to Key Learnings

| Learning Type | Typical Time |
|---------------|--------------|
| Problem resonance signal | 3-5 days |
| Zombie ratio assessment | 7-10 days |
| Pricing validation | 14-21 days |
| Fit score ≥70 | 4-6 weeks |
| Full validation | 8-12 weeks |

### Pivot Frequency Stats

| Pivot Type | Frequency | Success After Pivot |
|------------|-----------|---------------------|
| Segment Pivot | 23% of projects | 67% reach fit score ≥70 |
| Value Pivot | 31% of projects | 72% reach fit score ≥70 |
| Price Pivot | 18% of projects | 81% improve unit economics |
| No Pivot | 42% of projects | 85% reach fit score ≥70 |

## Success Definition Transparency

Clear thresholds for what "validated" means at each gate:

### Gate Thresholds

| Gate | Metric | Threshold | What It Means |
|------|--------|-----------|---------------|
| **Phase 1 Exit** | Fit Score | ≥ 70/100 | Problem-Solution Fit demonstrated |
| **Desirability** | problem_resonance | ≥ 50% | Customers care about the problem |
| **Desirability** | zombie_ratio | < 30% | Interest converts to commitment |
| **Feasibility** | feasibility_status | Green | Can be built with available resources |
| **Viability** | ltv_cac_ratio | ≥ 3.0 | Unit economics are sustainable |

### Evidence Quality Standards

| Evidence Type | Weight | Example | Reliability |
|---------------|--------|---------|-------------|
| **DO (Behavioral)** | High | Pre-orders, signups | Very reliable |
| **SAY (Verbal)** | Medium | Interviews, surveys | Moderate reliability |
| **Implied** | Low | Social listening | Directional only |

## Methodology Transparency

### 10 HITL Checkpoints Diagram

Visual showing all human approval points:

```
PHASE 0 (Onboarding)
    └─ [1] approve_founders_brief ← Founder reviews Brief

PHASE 1 (VPC Discovery)
    ├─ [2] approve_experiment_plan ← Founder approves test designs
    ├─ [3] approve_pricing_test ← Founder consents to pricing experiments
    └─ [4] approve_vpc_completion ← Founder confirms fit score ≥70

PHASE 2 (Desirability)
    ├─ [5] approve_campaign_launch ← Creative approval
    ├─ [6] approve_spend_increase ← Budget approval
    └─ [7] approve_desirability_gate ← Evidence review

PHASE 3 (Feasibility)
    └─ [8] approve_feasibility_gate ← Technical review

PHASE 4 (Viability)
    ├─ [9] approve_viability_gate ← Economics review
    └─ [10] request_human_decision ← Final pivot/proceed decision
```

### Typical Timeline Expectations

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| **Phase 0** | 1-2 days | Founder's Brief |
| **Phase 1** | 4-6 weeks | Validated VPC (fit ≥70) |
| **Phase 2** | 4-8 weeks | Desirability + Feasibility gates |
| **Phase 3** | 2-4 weeks | Viability + Final decision |
| **Total** | 10-16 weeks | Validated Business Model |

---

## Related Documents

- [03-methodology.md](../03-methodology.md) - VPD framework and methodology
- [04-phase-0-onboarding.md](../04-phase-0-onboarding.md) - Phase 0 specification
- [05-phase-1-vpc-discovery.md](../05-phase-1-vpc-discovery.md) - Phase 1 specification
- [02-organization.md](../02-organization.md) - Founder roles and personalities
- [api-contracts.md](./api-contracts.md) - API specifications
- [product-artifacts.md](./product-artifacts.md) - Canvas architecture

---
**Last Updated**: 2026-01-08

**Latest Changes**:
- Added VPD Framework Demonstration section
- Added Example Artifacts (anonymized Customer Profile, Value Map, BMC)
- Added Experiment Visibility dashboard metrics
- Added Success Definition transparency
- Added Methodology Transparency (10 HITL checkpoints, timeline)
