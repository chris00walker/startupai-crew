---
purpose: Product app smart artifact and canvas architecture
status: planning
last_reviewed: 2026-01-05
vpd_compliance: true
---

# Product App Smart Artifact Architecture

> **VPD Framework**: This architecture implements Value Proposition Design (Osterwalder/Pigneur) with Testing Business Ideas methodology. See [05-phase-0-1-specification.md](../05-phase-0-1-specification.md) for Phase 0-1 specification.

## Vision: Reimagining Strategyzer Frameworks

Traditional Strategyzer tools (VPC, BMC, Testing Business Ideas) rely on static formats: PDFs, posters, whiteboards, sticky notes. While helpful for ideation, these are a "horror show to maintain" - disconnected, unversioned, and divorced from actual validation evidence.

**The StartupAI reimagining**:
- Transform canvases from static documents into **living digital artifacts**
- Wire frameworks together so insights flow between VPC, BMC, and TBI
- Connect canvases to real testing assets and evidence
- Enable both human DIY entry and AI agent population
- Keep humans in the loop with configurable approval checkpoints

## Human/AI Mode Configuration

All four interaction modes are configurable in dashboard settings:

| Mode | Scope | Behavior |
|------|-------|----------|
| **Global toggle** | Project-level | Set DIY or AI-assisted mode for entire project |
| **Per-canvas toggle** | Canvas-level | VPC, BMC, TBI can each be independently DIY or AI |
| **Per-section hybrid** | Section-level | Within a canvas, some sections DIY, others AI-populated |
| **Suggestion-based** | Entry-level | AI always suggests, human confirms/edits before save |

**Default behavior**: AI does initial heavy lifting (populating canvases from onboarding brief and analysis), but all modes are selectable. Users choose their level of control.

## Approval Checkpoints

Six categories of actions require explicit human approval before AI proceeds:

### 1. Spend Increases
- Any experiment or test that costs money beyond current budget
- Ad spend, user testing incentives, tool subscriptions
- Shows projected cost, ROI estimate, and alternatives

### 2. Campaign Launch
- All advertising and marketing campaigns before they go live
- **Critical control point**: Content leaves StartupAI's ecosystem and enters the broader internet/social media
- Includes: ad creative, copy, targeting parameters, landing pages, email sequences
- Client reviews and signs off on everything that will represent their brand publicly

### 3. Stage Gate Progression
- Moving between validation stages: Desirability → Feasibility → Viability
- Guardian QA must pass before gate unlock is offered
- Human reviews evidence synthesis and confirms readiness

### 4. Pivot Recommendations
- When evidence suggests significant VPC/BMC changes
- Compass synthesizes invalidated assumptions
- Human approves pivot direction before AI updates canvases

### 5. Direct Customer Contact
- Before AI initiates contact with real people (interview requests, survey outreach, user testing recruitment)
- Different from broadcast campaigns - this is 1:1 or 1:few contact representing the client
- Includes: email outreach, LinkedIn messages, phone call scripts
- Client reviews messaging and target list before contact begins

### 6. Third-Party Data Sharing
- When system needs to share client project data with external tools or services
- Connecting to new APIs, uploading data to testing platforms, analytics integrations
- Shows: what data will be shared, with whom, for what purpose, retention policy
- Client retains control over where their business data goes

**Approval UI**: Modal with clear context, evidence summary, and approve/reject/modify options.

## Framework Wiring Logic

### Stage-Based BMC Population

```
┌─────────────────────────────────────────────────────────────────┐
│                    BUSINESS MODEL CANVAS                        │
├─────────────┬─────────────┬───────────────┬─────────────────────┤
│ Key         │ Key         │ Value         │ Customer      │ Customer   │
│ Partners    │ Activities  │ Propositions  │ Relationships │ Segments   │
│ [FEAS]      │ [FEAS]      │ [DESIR]       │ [DESIR/FEAS]  │ [DESIR]    │
├─────────────┴─────────────┼───────────────┼───────────────┴─────┤
│ Key Resources             │               │ Channels            │
│ [FEAS]                    │               │ [DESIR/FEAS]        │
├───────────────────────────┴───────────────┴─────────────────────┤
│ Cost Structure [VIAB]           │ Revenue Streams [DESIR/VIAB]  │
└─────────────────────────────────┴───────────────────────────────┘
```

### Validation Flow

**1. Desirability Stage (VPC-Driven)**
```
VPC Customer Profile    →   TBI Experiments    →   BMC Population
  - Customer Jobs           - "Do they want it?"    - Customer Segments
  - Pains                   - "Will they pay?"      - Value Propositions
  - Gains                                           - Revenue Streams (pricing)

VPC Value Map
  - Products & Services
  - Pain Relievers
  - Gain Creators
```

**2. Channel & Relationship Testing (Desirability/Feasibility Overlap)**
- *Desirability lens*: Which channels do customers prefer? What relationship type do they want?
- *Feasibility lens*: Can we use those channels cost-effectively? Can we deliver that relationship at scale?
- Evidence populates BMC: Channels, Customer Relationships

**3. Feasibility Stage**
- Key Activities, Key Resources, Key Partners
- Operational capability validation
- Technical feasibility (Forge's domain)

**4. Viability Stage**
- Cost Structure vs Revenue Streams = unit economics
- Sustainable business model validation
- Ledger's financial analysis

### Bidirectional Evidence Flow

Evidence doesn't just validate canvases - it updates them:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│     VPC     │ ←──→│     TBI     │ ←──→│     BMC     │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────┬───────┴───────┬───────────┘
                   │               │
            ┌──────▼───────┐ ┌─────▼──────┐
            │   Evidence   │ │ Hypotheses │
            │   (Vector)   │ │  Tracking  │
            └──────────────┘ └────────────┘
```

- **Evidence validates hypotheses** → Updates hypothesis status across all canvases
- **Contradicting evidence** → Triggers pivot recommendation (requires approval)
- **Strong evidence** → Auto-strengthens related canvas sections
- **Weak evidence** → Suggests additional experiments

## VPC Fit Assessment (Phase 1 Gate)

Before proceeding to Phase 2 validation, the VPC must demonstrate Problem-Solution Fit:

### Fit Score Components

| Metric | Description | Target |
|--------|-------------|--------|
| **fit_score** | Overall Problem-Solution Fit score | ≥ 70/100 |
| **profile_completeness** | % of Jobs/Pains/Gains with validation evidence | ≥ 75% |
| **value_map_coverage** | % of customer pains addressed by pain relievers | ≥ 75% |
| **evidence_strength** | Ratio of DO evidence vs SAY evidence | ≥ 50% DO |

### Fit Status Thresholds

| Status | Fit Score | Action |
|--------|-----------|--------|
| **Strong** | ≥ 80 | Ready for Phase 2 validation |
| **Moderate** | 70-79 | Ready, but monitor closely |
| **Weak** | 50-69 | Iterate on value map design |
| **None** | < 50 | Consider segment pivot |

### Evidence Hierarchy (SAY vs DO)

Evidence quality is weighted by behavioral commitment level:

| Level | Weight | Example | Classification |
|-------|--------|---------|----------------|
| **Paid** | 5 | Pre-order, paid pilot | DO (Direct) |
| **High-CTA** | 4 | Signup, demo request | DO (Direct) |
| **Medium-CTA** | 3 | Email capture, waitlist | DO (Direct) |
| **Low-CTA** | 2 | Social share, referral | DO (Indirect) |
| **Stated** | 1 | Interview response, survey | SAY |
| **Implied** | 0.5 | Review mining, social listening | SAY |

### VPC Completion Approval

The `approve_vpc_completion` HITL checkpoint fires when:
- Fit score ≥ 70
- At least 3 experiments completed
- No untested high-priority assumptions remain

Approval context includes:
- Customer Profile summary (validated Jobs/Pains/Gains)
- Value Map coverage analysis
- Experiment results and learnings
- Recommended Phase 2 focus areas

## BMC Population Sequence by Phase

The Business Model Canvas populates progressively through validation phases:

### Phase 1 (VPC Discovery) → BMC Seeds

| BMC Block | Source | Populated From |
|-----------|--------|----------------|
| **Customer Segments** | VPC Customer Profile | Validated customer segment from discovery |
| **Value Propositions** | VPC Value Map | Products/Services, Pain Relievers, Gain Creators |
| **Revenue Streams** | WTP Experiments | Pricing test results (preliminary) |

### Phase 2 (Desirability) → BMC Demand-Side

| BMC Block | Evidence Source | Populated From |
|-----------|-----------------|----------------|
| **Channels** | Ad platform experiments | Which channels reach customers effectively |
| **Customer Relationships** | User behavior data | Relationship type preferences |
| **Revenue Streams** | Pricing A/B tests | Validated pricing model |

### Phase 2 (Feasibility) → BMC Supply-Side

| BMC Block | Evidence Source | Populated From |
|-----------|-----------------|----------------|
| **Key Activities** | Technical breakdown | What operations are required |
| **Key Resources** | Resource audit | What assets are needed |
| **Key Partners** | Supplier evaluation | Who provides critical inputs |

### Phase 3 (Viability) → BMC Economics

| BMC Block | Evidence Source | Populated From |
|-----------|-----------------|----------------|
| **Cost Structure** | Key Activities + Resources | Operational cost model |
| **Revenue Streams** | Unit economics validation | Final pricing and revenue model |

### Cascade Rules

When VPC updates, BMC updates cascade:
- **Customer Profile change** → Customer Segments + Value Propositions update
- **Value Map change** → Value Propositions + potentially Revenue Streams update
- **Segment pivot** → Full BMC review required

## TBI Experiment Selection Guide

Choosing the right experiment for each hypothesis type:

### Customer Profile Validation

| Hypothesis Type | Recommended Experiments | Cost | Speed | Reliability |
|-----------------|-------------------------|------|-------|-------------|
| **Customer Jobs** | Discovery interviews, contextual inquiry | Low | Medium | High |
| **Customer Pains** | Pain interviews + review mining | Low | Fast | Medium |
| **Customer Gains** | Gain interviews + feature voting | Low | Medium | Medium |

### Value Map Validation

| Hypothesis Type | Recommended Experiments | Cost | Speed | Reliability |
|-----------------|-------------------------|------|-------|-------------|
| **Products/Services** | Paper prototypes, clickable mockups | Medium | Fast | Medium |
| **Pain Relievers** | A/B feature tests, usability studies | Medium | Medium | High |
| **Gain Creators** | Feature flag experiments, NPS surveys | Medium | Fast | Medium |

### Business Model Validation

| Hypothesis Type | Recommended Experiments | Cost | Speed | Reliability |
|-----------------|-------------------------|------|-------|-------------|
| **Pricing (WTP)** | Price sensitivity surveys, A/B pricing | Low-Med | Fast | Medium |
| **Channels** | Multi-channel ad tests | Medium | Fast | High |
| **Unit Economics** | Cohort analysis, CAC/LTV calculation | High | Slow | High |

## Rejection and Invalidation Handling

When experiments invalidate hypotheses:

### Pivot Attempt Limits

| Pivot Type | Max Attempts | After Exhaustion |
|------------|--------------|------------------|
| **Segment Pivot** | 3 | Strategic review with founder |
| **Value Pivot** | 3 | Consider adjacent markets |
| **Feature Pivot** | 2 | Scope reduction or tech pivot |
| **Price Pivot** | 2 | Cost structure review |

### Evidence Contradiction Thresholds

| Scenario | Threshold | Action |
|----------|-----------|--------|
| Single experiment fails | 1 failure | Re-run or iterate design |
| Multiple experiments fail same hypothesis | 2+ failures | Flag for pivot review |
| Conflicting evidence | > 40% contradiction | Segment deeper, find pattern |
| All experiments fail | 100% failure | Kill recommendation |

### Learning Capture on Failure

Every failed experiment produces:
- **Learning Card**: What was learned and implications
- **Flywheel Entry**: Anonymized pattern for future projects
- **VPC Update**: Mark element as invalidated
- **Next Action**: Pivot recommendation or alternative approach

## Innovation Physics Signal Validation Matrix

### Evidence Signals and Routing Logic

| Signal | Gate | Threshold | Router Decision | Canvas Update |
|--------|------|-----------|-----------------|---------------|
| **problem_resonance** | Desirability | < 0.3 | `SEGMENT_PIVOT` → Re-test with new audience | VPC Customer Profile → New segment |
| **zombie_ratio** | Desirability | >= 0.7 | `VALUE_PIVOT` → Adjust value proposition | VPC Value Map → Revise pain relievers/gain creators |
| **commitment_type** | Desirability | `skin_in_game` | `PROCEED` → Pass gate | BMC Revenue Streams → Validated pricing |
| **feasibility_status** | Feasibility | `red_impossible` | `FEATURE_PIVOT` → Downgrade and re-test | VPC Products & Services → Remove impossible features |
| **ltv_cac_ratio** | Viability | < 3.0 | `STRATEGIC_PIVOT` → Price↑ or Cost↓ | BMC Cost Structure / Revenue Streams → Adjust model |
| **unit_economics_status** | Viability | `underwater` | `KILL` or pivot to new model | Terminal decision or full BMC rework |

### Signal Computation and Display

**Desirability Signals** (computed from experiment metrics):
```typescript
interface DesirabilitySignals {
  problem_resonance: number;      // (clicks + signups) / impressions
  zombie_ratio: number;            // (clicks - signups) / clicks
  commitment_type: CommitmentType; // Derived from user actions
  evidence_strength: EvidenceStrength; // Strong (>0.5) | Weak (0.1-0.5) | None (<0.1)
}
```

**Canvas Validation Indicators**:
- 🟢 **Green**: Evidence validates hypothesis (problem_resonance >= 0.5, zombie_ratio < 0.3)
- 🟡 **Yellow**: Weak signal (problem_resonance 0.3-0.5, zombie_ratio 0.3-0.7)
- 🔴 **Red**: Invalidated (problem_resonance < 0.3 or zombie_ratio >= 0.7)
- ⚪ **Gray**: Untested

**Router Decision Display** (in project status):
```typescript
interface RouterStatus {
  current_phase: "desirability" | "feasibility" | "viability" | "validated" | "killed";
  router_decision: string; // Last router decision
  blocking_approval_required: boolean;
  last_pivot_type?: PivotType;
  gate_status: {
    desirability?: { passed: boolean; evidence: DesirabilitySignals };
    feasibility?: { passed: boolean; status: FeasibilityStatus };
    viability?: { passed: boolean; ltv_cac_ratio: number };
  };
}
```

### Pivot Type Mapping to Canvas Sections

| Pivot Type | Primary Canvas | Sections Updated | Evidence Required |
|------------|----------------|------------------|-------------------|
| **SEGMENT_PIVOT** | VPC | Customer Profile (Jobs/Pains/Gains) | problem_resonance < 0.3 |
| **VALUE_PIVOT** | VPC | Value Map (Pain Relievers/Gain Creators) | zombie_ratio >= 0.7 |
| **CHANNEL_PIVOT** | BMC | Channels, Customer Relationships | Channel engagement metrics |
| **PRICE_PIVOT** | BMC | Revenue Streams | Pricing experiment results |
| **COST_PIVOT** | BMC | Cost Structure, Key Partners | Unit economics analysis |
| **MODEL_PIVOT** | BMC | All 9 blocks | Fundamental business model change |
| **FEATURE_PIVOT** | VPC + BMC | Products & Services, Key Activities | feasibility_status = impossible |
| **KILL** | All | Archive project | Terminal failure on any gate |

### Implementation Notes

**For Product App Dashboard**:
1. **Signal Display**: Show real-time Innovation Physics metrics on project status page
2. **Canvas Indicators**: Color-code VPC/BMC sections based on validation state
3. **Router Breadcrumbs**: Visual flow showing which routers were triggered and why
4. **Approval Queue**: HITL decisions for pivots with full evidence context

**For CrewAI Integration**:
- CrewAI computes signals and includes them in `/status` response (see `api-contracts.md`)
- Product app receives signals via webhook or polling
- UI updates validation indicators and triggers approval modals if `blocking_approval_required: true`

## Current Implementation Status

**Infrastructure Complete (~55-60%)**:
- Canvas components (VPC, BMC, TBI) with guided modes
- Data models (projects, hypotheses, experiments, evidence)
- Vector embeddings (pgvector 1536 dims for semantic search)
- AI onboarding (Vercel AI SDK with quality scoring)
- CrewAI integration (strategic analysis)
- Stage-gate validation model

**Missing: Bidirectional Sync Layer**:
- AI insights → canvas auto-population
- Evidence → hypothesis validation visualization
- Canvas sections showing validation status (tested/untested/contradicted)
- Approval workflow UI for spend/gates/pivots
- Mode configuration dashboard

## Implementation Priorities

1. **Mode configuration UI** - Dashboard settings for all 4 interaction modes
2. **Approval workflow** - Modal system for spend/gates/pivots
3. **AI → Canvas bridge** - CrewAI output populates canvas sections
4. **Evidence → Canvas linking** - Visual indicators of validation status
5. **Hypothesis tracking UI** - Connect experiments to hypotheses to evidence
6. **Framework wiring** - VPC changes cascade to BMC, evidence updates all

## Key Files to Modify

**Dashboard Settings**:
- New: `frontend/src/components/settings/AIAssistanceSettings.tsx`
- New: `frontend/src/components/settings/ApprovalPreferences.tsx`

**Canvas Components** (add AI population + validation status):
- `frontend/src/components/canvas/ValuePropositionCanvas.tsx`
- `frontend/src/components/canvas/BusinessModelCanvas.tsx`
- `frontend/src/components/canvas/TestingBusinessIdeasCanvas.tsx`

**Approval Workflow**:
- New: `frontend/src/components/approvals/ApprovalModal.tsx`
- New: `frontend/src/components/approvals/SpendApproval.tsx`
- New: `frontend/src/components/approvals/CampaignApproval.tsx`
- New: `frontend/src/components/approvals/GateApproval.tsx`
- New: `frontend/src/components/approvals/PivotApproval.tsx`

**Evidence Integration**:
- Modify: `frontend/src/db/schema/evidence.ts` (add canvas_section linking)
- New: `frontend/src/components/canvas/ValidationIndicator.tsx`

---

## Related Documents

- [05-phase-0-1-specification.md](../05-phase-0-1-specification.md) - Phase 0-1 VPD specification
- [approval-workflows.md](./approval-workflows.md) - HITL implementation patterns
- [database-schemas.md](./database-schemas.md) - SQL schema definitions
- [02-organization.md](../02-organization.md) - Founder approval ownership
- [flywheel-learning.md](./flywheel-learning.md) - Learning capture patterns

---
**Last Updated**: 2026-01-05

**Latest Changes**:
- Added VPC Fit Assessment section (fit score, evidence hierarchy)
- Added BMC Population Sequence by Phase
- Added TBI Experiment Selection Guide
- Added Rejection and Invalidation Handling (pivot limits, learning capture)
