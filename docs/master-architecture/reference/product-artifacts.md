---
purpose: Product app smart artifact and canvas architecture
status: planning
last_reviewed: 2025-11-21
---

# Product App Smart Artifact Architecture

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

- [approval-workflows.md](./approval-workflows.md) - HITL implementation patterns
- [database-schemas.md](./database-schemas.md) - SQL schema definitions
- [02-organization.md](../02-organization.md) - Founder approval ownership

---
**Last Updated**: 2025-11-21
