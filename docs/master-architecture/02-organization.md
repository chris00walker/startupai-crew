---
purpose: Single source of truth for 6 AI Founders and agents (Phase 0-4)
status: active
last_reviewed: 2026-01-19
vpd_compliance: true
architectural_update: 2026-01-19
---

# StartupAI Organizational Structure

## Overview

StartupAI is run by a team of AI Founders - six co-equal team members organized around the customer. They collaborate as peers to deliver strategic business analysis and validation using the **Value Proposition Design (VPD)** framework by Alex Osterwalder and Yves Pigneur.

**This document is the SINGLE SOURCE OF TRUTH for founder names, roles, agents, and organizational structure. All other documents reference here - they do not duplicate this content.**

> **VPD Framework Compliance**: This organization implements patterns from *Value Proposition Design*, *Testing Business Ideas*, and *Business Model Generation*. See [03-methodology.md](./03-methodology.md) for VPD framework reference.

## Design Philosophy

### Startup Reality
Startups are temporary organizations in search of sustainable business models. The flat structure is intentional - it's all hands on deck in the search for customers, the development of products, and the formation of a winning team.

### Customer-Centric Model
Inspired by Edwin Korver's RoundMap® Customer Dynamics Lifecycle, StartupAI places the customer at the center rather than using a traditional linear funnel. All founders orient around the customer's journey and needs, engaging adaptively as required.

### Continuous Learning
AI organizations have a structural advantage over human-led companies: they learn from every interaction. This is StartupAI's moat. Learning isn't delegated to a role - it's inherent to the system.

## VPD Framework Reference

> **Single Source**: For complete VPD terminology (Value Proposition Canvas, Test Cards, Learning Cards, Evidence Hierarchy, Problem-Solution Fit criteria), see [03-methodology.md](./03-methodology.md).

This organization implements VPD patterns. Agents use Test Cards to design experiments and Learning Cards to capture results, prioritizing behavioral evidence (DO) over stated preferences (SAY).

## CrewAI Pattern Hierarchy

> **Single Source**: For complete CrewAI pattern definitions, see [00-introduction.md](./00-introduction.md#3-crewai-pattern-hierarchy).

This organization uses CrewAI's documented patterns. Understanding the hierarchy is essential:

```
PHASE (Business Concept)
└── FLOW (Orchestration Unit)
    ├── @start() → Entry point
    ├── @listen() → Crew.kickoff()
    │               └── CREW (Collaborative Agent Group)
    │                   ├── Agent 1 (role, goal, backstory)
    │                   ├── Agent 2
    │                   └── Agent N
    │                       └── Tasks
    ├── @router() → Conditional branching (gates)
    └── @listen("label") → Route-specific handlers
```

**Key Definitions**:

| Pattern | Definition | Key Characteristic |
|---------|------------|-------------------|
| **Phase** | Business/methodology concept | NOT a CrewAI construct - decomposed into Flows |
| **Flow** | Event-driven orchestration | Controls WHEN and IF crews execute |
| **Crew** | Collaborative GROUP of agents (2+) | Controls HOW agents collaborate |
| **Agent** | Individual executor | Has role, goal, backstory |
| **Task** | Specific work item | Produces output |

**Critical Rule**: A crew must have 2+ agents. One agent is NOT a crew.

### Complete Crew Summary (All Phases)

| Phase | Flow | Crew | Agents |
|-------|------|------|--------|
| 0: Quick Start | N/A | N/A | (No agents - simple form submission) |
| 1: VPC Discovery | `VPCDiscoveryFlow` | `BriefGenerationCrew` | GV1, S1 (moved from Phase 0) |
| 1: VPC Discovery | `VPCDiscoveryFlow` | `DiscoveryCrew` | E1, D1, D2, D3, D4 |
| 1: VPC Discovery | `VPCDiscoveryFlow` | `CustomerProfileCrew` | J1, J2, PAIN_RES, PAIN_RANK, GAIN_RES, GAIN_RANK |
| 1: VPC Discovery | `VPCDiscoveryFlow` | `ValueDesignCrew` | V1, V2, V3 |
| 1: VPC Discovery | `VPCDiscoveryFlow` | `WTPCrew` | W1, W2 |
| 1: VPC Discovery | `VPCDiscoveryFlow` | `FitAssessmentCrew` | FIT_SCORE, FIT_ROUTE |
| 2: Desirability | `DesirabilityFlow` | `BuildCrew` | F1, F2, F3 |
| 2: Desirability | `DesirabilityFlow` | `GrowthCrew` | P1, P2, P3 |
| 2: Desirability | `DesirabilityFlow` | `GovernanceCrew` | G1, G2, G3 |
| 3: Feasibility | `FeasibilityFlow` | `BuildCrew` | F1, F2, F3 (reused) |
| 3: Feasibility | `FeasibilityFlow` | `GovernanceCrew` | G1, G2 |
| 4: Viability | `ViabilityFlow` | `FinanceCrew` | L1, L2, L3 |
| 4: Viability | `ViabilityFlow` | `SynthesisCrew` | C1, C2, C3 |
| 4: Viability | `ViabilityFlow` | `GovernanceCrew` | G1, G2, G3 |

**Totals**: 5 Phases, 4 Flows (Phase 0 has no flow), 14 Crews, 43 Agents

> **Note (2026-01-19)**: Phase 0 was simplified to Quick Start (no AI). O1 and GV2 were deleted. GV1 and S1 moved to Phase 1 `BriefGenerationCrew`. See [04-phase-0-onboarding.md](./04-phase-0-onboarding.md).

## The AI Founders Team

### Founding Team (Flat Structure)
Six co-equal founders organized around the customer.

| Founder | Title | Responsibility |
|---------|-------|----------------|
| **Sage** | Chief Strategy Officer (CSO) | Business Model Canvas, Value Proposition Design, market analysis, assumption identification |
| **Forge** | Chief Technology Officer (CTO) | MVP code generation, technical architecture, deployment automation |
| **Pulse** | Chief Marketing Officer (CMO) | Ad campaigns, user acquisition, A/B testing, analytics tracking |
| **Compass** | Chief Product Officer (CPO) | Evidence synthesis, pivot vs proceed analysis, recommendations |
| **Guardian** | Chief Governance Officer (CGO) | Governance monitoring, pattern detection, security oversight |
| **Ledger** | Chief Financial Officer (CFO) | Unit economics, revenue model design, pricing strategy, runway projections |

### Founder Dual Responsibilities

Each founder has dual responsibilities: building StartupAI's own validated business model (eating our own dog food) while delivering desirability validation at scale for clients. StartupAI's first product iteration focuses on desirability validation—the first gate all startups must pass.

#### Sage's Dual Responsibilities

**For StartupAI** (building our flywheel):
- Lead VPC design for StartupAI's own value proposition
- Prioritize assumptions to test across customer segments (Founders vs Consultants)
- Define strategic positioning against traditional consulting and DIY tools
- Contribute learnings from client patterns to refine methodology

**For Clients** (desirability validation):
- Guide VPC design linking customer jobs/pains/gains to value map
- Identify and prioritize riskiest assumptions for testing
- Frame strategic context for experiment interpretation

---

#### Forge's Dual Responsibilities

**For StartupAI** (building our flywheel):
- Build and iterate the platform that enables desirability testing at scale
- Technical architecture decisions for the validation engine
- Evaluate build vs buy for expanding capabilities (feasibility, viability tools)

**For Clients** (desirability validation):
- Generate MVPs/prototypes for desirability testing
- Ensure technical pain relievers match customer needs
- Deploy testable artifacts quickly for experiment cycles

---

#### Pulse's Dual Responsibilities

**For StartupAI** (building our flywheel):
- Run desirability experiments for StartupAI itself (user acquisition, messaging tests)
- Collect market signals on StartupAI's value proposition resonance
- Optimize conversion through the 3-cycle funnel (trial → sprint → platform)

**For Clients** (desirability validation):
- Design and execute ad campaigns for desirability evidence
- Collect customer signals (clicks, conversions, engagement)
- Generate quantitative evidence for pivot/proceed decisions

---

#### Compass's Dual Responsibilities

**For StartupAI** (building our flywheel):
- Synthesize evidence from StartupAI's own test cycles
- Recommend pivots or proceed decisions for StartupAI's product roadmap
- Integrate learnings across client engagements into methodology improvements

**For Clients** (desirability validation):
- Synthesize evidence across test cycles within each gate
- Deliver pivot/proceed recommendations based on evidence analysis
- Ensure learnings from each cycle inform the next iteration

---

#### Guardian's Dual Responsibilities

**For StartupAI** (building our flywheel):
- Govern the validation process integrity (no false positives/negatives)
- Monitor data privacy and compliance across client engagements
- Ensure the flywheel doesn't learn bad patterns from edge cases

**For Clients** (desirability validation):
- Monitor governance risks in value proposition delivery
- Flag compliance constraints that affect testability
- Ensure experiment designs meet ethical standards

---

#### Ledger's Dual Responsibilities

**For StartupAI** (building our flywheel):
- Monitor StartupAI's own viability while we build desirability validation for clients
- Resource allocation across founders based on learning ROI
- Pricing strategy for the 3-cycle offering and platform tiers
- Track unit economics as the flywheel matures

**For Clients** (current phase - desirability focus):
- Consulted on pricing/value capture elements in VPC design
- Monitor cost efficiency of test cycles

**For Clients** (future phase - viability validation):
- Unit economics analysis
- Revenue model design
- Pricing strategy recommendations
- Runway/burn rate projections

---

### PSIU Balance (Organizational Physics)
Following Lex Sisney's framework, the team covers all four organizational styles:

| Style | Function | Founders |
|-------|----------|----------|
| **Producer** | Drive results, ship things | Forge, Pulse |
| **Stabilizer** | Systems, consistency, discipline | Guardian, Ledger |
| **Innovator** | Strategy, vision, change | Sage |
| **Unifier** | Integration, synthesis | Compass |

## Customer-Centric Structure

```
                    Sage
                  (Strategy)
                      ↕

   Ledger ←───────────────────────→ Forge
  (Finance)                      (Technology)
      ↕                               ↕

            ┌─────────────┐
            │  CUSTOMER   │
            │  (Center)   │
            └─────────────┘

      ↕                               ↕
  Guardian ←───────────────────────→ Pulse
(Governance)                      (Marketing)

                      ↕
                  Compass
                  (Product)
```

**Key principle**: The customer is the integrating point. All founders maintain awareness of the customer's journey and contribute when relevant - not waiting in sequence for their turn.

## Engagement Model

### Traditional Funnel (What We Don't Do)
```
Marketing → Sales → Product → Support → Renewal
```
Linear handoffs create entropy and lose customer context.

### Customer Orbit (What We Do)
All founders engage based on customer needs:

- **Early journey**: Sage leads (strategy, desirability)
- **Building phase**: Forge leads (feasibility, MVP)
- **Validation phase**: Ledger leads (viability), Pulse leads (growth testing)
- **Decision point**: Compass synthesizes all evidence
- **Throughout**: Guardian monitors governance, Ledger monitors costs

### Derisking Sequence
Following lean startup principles:
1. **Desirability** - Do customers want it? (Sage)
2. **Feasibility** - Can we build it? (Forge)
3. **Viability** - Can we make money? (Ledger)

Note: Ledger monitors cost structure throughout, then does deep viability analysis at the right moment.

## Organizational Structure

### Service/Commercial Model

StartupAI operates as two interconnected sides balanced by Compass, with Guardian providing governance oversight.

```
                    ┌─────────────────┐
                    │    GUARDIAN     │
                    │  (Board Chair)  │
                    │                 │
                    │ • Audit         │
                    │ • Security      │
                    │ • QA            │
                    └────────┬────────┘
                             │ accountable for governance
         ┌───────────────────┼───────────────────┐
         │                   │                   │
    SERVICE SIDE          COMPASS          COMMERCIAL SIDE
    (Customer-Facing)    (Balance)        (Value Delivery)

    ┌─────────────┐    ┌─────────┐    ┌─────────────────┐
    │ Sage owns:  │    │ Project │    │ Sage            │
    │             │    │ Manager │    │ • Customer      │
    │• Customer   │    └────┬────┘    │   Researcher    │
    │  Service    │         │         │ • Competitor    │
    │• Founder    │         │         │   Analyst       │
    │  Onboarding │    [Balances      ├─────────────────┤
    │• Consultant │     competing     │ Forge           │
    │  Onboarding │     interests]    │ • UX/UI Designer│
    └──────┬──────┘                   │ • Frontend Dev  │
           │                          │ • Backend Dev   │
           └──→ [Founder's Brief] ────→├─────────────────┤
                                      │ Pulse           │
                                      │ • Ad Creative   │
                                      │ • Communications│
                                      │ • Social Media  │
                                      │   Analyst       │
                                      ├─────────────────┤
                                      │ Ledger          │
                                      │ • Financial     │
                                      │   Controller    │
                                      │ • Legal &       │
                                      │   Compliance    │
                                      └─────────────────┘
```

### Guardian's Board-Level Role

Guardian is fundamentally different from the other five founders. While Sage, Forge, Pulse, Compass, and Ledger are **Executives** who build and deliver, Guardian is a **Board Member** who oversees and validates.

#### Board vs Executive Distinction

| Dimension | Executives (Sage, Forge, Pulse, Compass, Ledger) | Board (Guardian) |
|-----------|--------------------------------------------------|------------------|
| **Primary Verb** | Builds, executes, delivers | Oversees, validates, challenges |
| **Core Question** | "How do we do this?" | "Should we do this? Is it done right?" |
| **Authority Type** | Responsible for outcomes | Accountable for governance integrity |
| **Involvement** | Hands-on, in the work | Hands-off, above the work |
| **Analogy** | CEO, CFO, CTO, CMO, CPO | Board Chair / Non-Executive Director |
| **Decision Mode** | Makes execution decisions | Reviews, consults, can veto |

#### What Guardian Does NOT Do

Guardian is a **sentinel**, not an executor. Guardian does NOT:
- Build products or features (Forge does)
- Run marketing campaigns (Pulse does)
- Design strategy (Sage does)
- Synthesize evidence for decisions (Compass does)
- Calculate unit economics (Ledger does)
- Own business outcomes

Guardian DOES:
- Ask hard questions others might avoid
- Review decisions for compliance, ethics, and risk
- Validate methodology adherence
- Ensure audit trails exist
- Flag issues and escalate concerns
- Veto decisions that violate governance standards

#### Guardian as Sentinel (Overwatch Model)

```
                    ┌─────────────────────────────┐
                    │         GUARDIAN            │
                    │    (Board-Level Oversight)  │
                    │                             │
                    │  • Veto authority at gates  │
                    │  • Asks hard questions      │
                    │  • Ensures compliance       │
                    │  • Does NOT execute         │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
              ┌─────────┐   ┌─────────┐   ┌─────────┐
              │ G1: QA  │   │G2: Sec  │   │G3: Audit│
              │         │   │         │   │         │
              │ Reviews │   │ Reviews │   │ Records │
              │ quality │   │ privacy │   │decisions│
              └─────────┘   └─────────┘   └─────────┘
```

Guardian's agents **review** and **validate**—they don't **create** or **execute**.

#### Data Governance: Distributed Ownership

Guardian encompasses Chief Governance Officer responsibilities including data governance oversight. However, data-related questions are **owned by domain experts**, with Guardian providing **oversight review**:

| Data Question | Owner | Guardian's Oversight |
|---------------|-------|---------------------|
| Strategic alignment | **Sage** (CSO) | Reviews goal clarity |
| Business objectives | **Sage** + **Compass** | Reviews measurability |
| KPIs & success measures | **Compass** + **Ledger** | Reviews metrics validity |
| Data ownership | **Compass** (CPO) | Reviews accountability |
| Data customers/users | **Sage** (CSO) | Reviews customer focus |
| Required data sources | **Forge** + **Pulse** | Reviews data minimization |
| Data governance & privacy | **Guardian** (direct) | Owns this domain |
| Analytics approach | **Pulse** + **Ledger** | Reviews methodology |
| Technology requirements | **Forge** (CTO) | Reviews security posture |
| Skills & capacity | **Compass** + **Ledger** | Reviews resourcing |
| Change management | **Compass** (CPO) | Reviews risk mitigation |

**Key insight**: Guardian owns **data governance** (privacy, access, security, retention) but NOT data strategy, data collection, or data analysis—those belong to the executive founders.

#### RACI Model for Approvals

Guardian is **always Consulted, never Accountable** for execution decisions. Guardian's accountability is for **governance integrity**, not business outcomes.

| Gate | Accountable (A) | Responsible (R) | Guardian Role |
|------|-----------------|-----------------|---------------|
| `approve_founders_brief` | Sage | S1 | **Consulted** (legitimacy) |
| `approve_experiment_plan` | Sage | E1 | **Consulted** (methodology) |
| `approve_pricing_test` | Ledger | W1, W2 | **Consulted** (compliance) |
| `approve_vpc_completion` | Compass | FIT_SCORE, FIT_ROUTE | **Consulted** (quality) |
| `approve_campaign_launch` | Pulse | P1, P3 | **Consulted** (brand safety) |
| `approve_desirability_gate` | Compass | Evidence synthesis | **Consulted** (methodology) |
| `approve_feasibility_gate` | Forge | F3 | **Consulted** (security) |
| `approve_viability_gate` | Ledger | L1, L3 | **Consulted** (compliance) |
| `request_human_decision` | Compass | C1, C2 | **Consulted** (audit trail) |

**Veto Authority**: While Guardian is "Consulted" not "Accountable," Guardian retains **veto authority** on governance grounds. If a decision violates compliance, ethics, or security standards, Guardian can block progression until issues are resolved.

### Approval Checkpoint Ownership

Human-in-the-loop (HITL) approvals are distributed across founders based on domain expertise and phase. Each approval type has a primary owner who prepares the approval request and a governance reviewer.

#### Phase 0 Approvals (Onboarding)

| Approval Type | Primary Owner | Prepares Request | Governance Review |
|---------------|---------------|------------------|-------------------|
| **Founder's Brief** (`approve_founders_brief`) | Sage + Founder | Brief content, hypothesis capture | Guardian (GV1, GV2) |
| **Concept Legitimacy** | Guardian (GV1) | Legal, ethical, feasibility screening | Sage |
| **Intent Verification** | Guardian (GV2) | Brief accuracy vs founder intent | Sage |

#### Phase 1 Approvals (VPC Discovery)

| Approval Type | Primary Owner | Prepares Request | Governance Review |
|---------------|---------------|------------------|-------------------|
| **Experiment Plan** (`approve_experiment_plan`) | Sage (E1) | Experiment mix, cost, timeline | Guardian |
| **Pricing Tests** (`approve_pricing_test`) | Ledger (W1, W2) | Price points, payment methods | Guardian |
| **VPC Completion** (`approve_vpc_completion`) | Compass (FIT_SCORE) | Fit score, evidence summary | Guardian |

#### Phase 2+ Approvals (Validation)

| Approval Type | Primary Owner | Prepares Request | Governance Review |
|---------------|---------------|------------------|-------------------|
| **Spend Increases** | Ledger (CFO) | Cost analysis, ROI projection, alternatives | Guardian |
| **Campaign Launch** | Pulse (CMO) | Creative, copy, targeting, landing pages | Guardian |
| **Direct Customer Contact** | Pulse (CMO) | Messaging, target list, outreach plan | Guardian |
| **Stage Gate Progression** | Guardian (CGO) | QA report, evidence synthesis, gate criteria | Compass (synthesis) |
| **Pivot Recommendations** | Compass (CPO) | Evidence synthesis, pivot rationale, direction | Guardian |
| **Third-Party Data Sharing** | Guardian (CGO) | Data inventory, recipient, purpose, retention | Ledger (compliance) |

**Workflow Pattern:**
1. Primary owner's crew generates proposal with supporting evidence
2. Task with `human_input: true` pauses workflow
3. Webhook notifies product app → approval modal appears
4. Human reviews, approves/rejects/modifies
5. Product app calls `/resume` endpoint
6. Flow continues based on decision

**Guardian's Approval Orchestration Role:**
Guardian serves as the approval orchestrator, ensuring:
- All approval requests meet quality standards before reaching users
- Approval audit trail is maintained
- Escalations are handled appropriately
- Compliance requirements are satisfied

### The Founder's Brief Handoff

The **Founder's Brief** is the contract between Phase 0 (Onboarding) and Phase 1+ (Validation):

**Phase 0 (Onboarding) captures:**
- The Idea (concept, one-liner hypothesis)
- Problem Hypothesis (who, what, alternatives)
- Customer Hypothesis (segment, characteristics)
- Solution Hypothesis (approach, key features)
- Key Assumptions (ranked by risk)
- Success Criteria (what "validated" means)
- Founder Context (stage, resources, constraints)

**Phase 1+ (Validation) receives:**
- Structured Founder's Brief that informs all downstream analysis
- Everything needed to begin VPC Discovery → Desirability → Feasibility → Viability

> **VPD Note**: The Founder's Brief captures *hypotheses* about customer and value. Phase 1 VPC Discovery validates these against customer reality using experiments from the Testing Business Ideas framework.

### Compass as Balancing Force

Compass (CPO) sits at the center, balancing natural tensions:

| Service Side Wants | Commercial Side Wants |
|--------------------|-----------------------|
| Delight customers | Deliver efficiently |
| Capture full context | Move to execution |
| Accommodate requests | Maintain standards |

**Why Compass:**
- Core competency is synthesizing competing evidence
- Product must balance what's promised (Service) with what's delivered (Commercial)
- Pivot/proceed authority requires seeing both perspectives
- PSIU: Compass is the **Unifier**

## Specialist Agents (Task Executors)

Specialist agents execute specific tasks within each founder's domain. Agents are organized by phase:

- **Phase 0 (Quick Start)**: 0 agents - Simple form submission (no AI)
- **Phase 1+ (Validation)**: 20 agents - VPC Discovery (includes brief generation) through Decision

### Phase 0: Quick Start (No Agents)

> **Architectural Pivot (2026-01-19)**: Phase 0 was simplified from a 7-stage AI conversation to a single form submission. See [04-phase-0-onboarding.md](./04-phase-0-onboarding.md) for details.

Phase 0 is now a **Quick Start** flow with no CrewAI involvement:

- User enters business idea (1-3 sentences)
- System creates project record
- Phase 1 is triggered immediately

**Flow**: N/A (no orchestration needed)
**Crew**: N/A (no agents)
**HITL**: None (first checkpoint is in Phase 1)

#### Agents Removed or Moved

| Former ID | Former Name | Disposition |
|-----------|-------------|-------------|
| ~~O1~~ | ~~Interview Gap Analyzer Agent~~ | **DELETED** - no interview to analyze |
| GV1 | Concept Validator Agent | **MOVED** to Phase 1 `BriefGenerationCrew` |
| ~~GV2~~ | ~~Intent Verification Agent~~ | **DELETED** - no transcript to verify |
| S1 | Brief Compiler Agent | **MOVED** to Phase 1 `BriefGenerationCrew` |

**Reason for change**: AI in the critical path caused non-deterministic behavior (57-92% progress variance), high cost ($17+ per user), and test flakiness. Quick Start eliminates these issues.

### Phase 1: VPC Discovery Agents

Phase 1 agents discover customer reality (Customer Profile) and design value (Value Map) using the VPD framework. **Phase 1 now also generates the Founder's Brief from research.** See [05-phase-1-vpc-discovery.md](./05-phase-1-vpc-discovery.md) for full specification.

**Flow**: `VPCDiscoveryFlow`
**Crews**: 6 crews (20 agents total)

#### BriefGenerationCrew (2 agents) - NEW

> **Added 2026-01-19**: These agents moved from Phase 0 when the architecture was simplified.

| ID | Agent | Founder | Task Focus |
|----|-------|---------|------------|
| **GV1** | Concept Validator Agent | Guardian | Legitimacy screening before research begins |
| **S1** | Brief Compiler Agent | Sage | Synthesizes research into Founder's Brief |

**Input**: `raw_idea` (1-3 sentences from Quick Start)
**Output**: Complete Founder's Brief generated from AI research

#### DiscoveryCrew (5 agents)

| ID | Agent | Founder | Task Focus |
|----|-------|---------|------------|
| **E1** | Experiment Designer | Sage | Design experiment mix using Assumptions Mapping, Test Cards, Learning Cards |
| **D1** | Customer Interview Agent | Sage | Discovery interviews using The Mom Test methodology |
| **D2** | Observation Agent | Pulse | Social listening, forum mining, review mining, search trends |
| **D3** | CTA Test Agent | Pulse | Landing pages, ads, fake doors, explainer videos, pre-sales |
| **D4** | Evidence Triangulation Agent | Guardian | SAY vs DO analysis, confidence scoring, weighted evidence synthesis |

#### CustomerProfileCrew (6 agents)

| ID | Agent | Founder | Task Focus |
|----|-------|---------|------------|
| **J1** | JTBD Researcher | Sage | Discover Jobs-to-be-Done (functional, emotional, social, supporting) |
| **J2** | Job Ranking Agent | Sage | Rank jobs by importance using interviews, surveys, engagement metrics |
| **PAIN_RES** | Pain Researcher | Sage | Discover pains via interviews, review mining, support tickets |
| **PAIN_RANK** | Pain Ranking Agent | Sage | Rank pains by severity |
| **GAIN_RES** | Gain Researcher | Sage | Discover gains via interviews, feature requests, success stories |
| **GAIN_RANK** | Gain Ranking Agent | Sage | Rank gains by importance |

#### ValueDesignCrew (3 agents)

| ID | Agent | Founder | Task Focus |
|----|-------|---------|------------|
| **V1** | Solution Designer | Forge | Design products/services that address top jobs |
| **V2** | Pain Reliever Designer | Forge | Design pain relievers for top pains |
| **V3** | Gain Creator Designer | Forge | Design gain creators for top gains |

#### WTPCrew (2 agents)

| ID | Agent | Founder | Task Focus |
|----|-------|---------|------------|
| **W1** | Pricing Experiment Agent | Ledger | Design WTP experiments (Van Westendorp, pricing A/B, conjoint) |
| **W2** | Payment Test Agent | Ledger | Run payment tests (pre-orders, crowdfunding, LOIs) |

#### FitAssessmentCrew (2 agents)

| ID | Agent | Founder | Task Focus |
|----|-------|---------|------------|
| **FIT_SCORE** | Fit Analyst | Compass | Score Problem-Solution Fit (Customer Profile ↔ Value Map coverage) |
| **FIT_ROUTE** | Iteration Router | Compass | Route back to appropriate crew if fit < 70 |

**Phase 1 HITL Checkpoints**:
- `approve_experiment_plan` - Approve experiment mix before execution
- `approve_pricing_test` - Approve tests involving real money
- `approve_vpc_completion` - Confirm VPC ready for Phase 2 (fit ≥ 70)

### Phase 2: Desirability Agents

Phase 2 tests whether customers actually want the validated value proposition. See [06-phase-2-desirability.md](./06-phase-2-desirability.md) for full specification.

**Flow**: `DesirabilityFlow`
**Crews**: 3 crews (9 agents total)

#### BuildCrew (3 agents)

| ID | Agent | Founder | Task Focus |
|----|-------|---------|------------|
| **F1** | UX/UI Designer | Forge | Design landing pages and test artifacts |
| **F2** | Frontend Developer | Forge | Build landing pages |
| **F3** | Backend Developer | Forge | Deploy testable artifacts |

#### GrowthCrew (3 agents)

| ID | Agent | Founder | Task Focus |
|----|-------|---------|------------|
| **P1** | Ad Creative Agent | Pulse | Generate ad variants |
| **P2** | Communications Agent | Pulse | Write copy |
| **P3** | Analytics Agent | Pulse | Run experiments, compute desirability signals |

#### GovernanceCrew (3 agents)

| ID | Agent | Founder | Task Focus |
|----|-------|---------|------------|
| **G1** | QA Agent | Guardian | Methodology + creative QA |
| **G2** | Security Agent | Guardian | PII protection |
| **G3** | Audit Agent | Guardian | Decision logging |

**Phase 2 HITL Checkpoints**:
- `approve_campaign_launch` - Approve ad campaigns before launch
- `approve_spend_increase` - Approve budget increases
- `approve_desirability_gate` - Confirm desirability signal is STRONG_COMMITMENT

### Phase 3: Feasibility Agents

Phase 3 assesses whether the validated value proposition can be built. See [07-phase-3-feasibility.md](./07-phase-3-feasibility.md) for full specification.

**Flow**: `FeasibilityFlow`
**Crews**: 2 crews (5 agents total, reusing BuildCrew from Phase 2)

#### BuildCrew (3 agents, reused)

| ID | Agent | Founder | Task Focus |
|----|-------|---------|------------|
| **F1** | UX/UI Designer | Forge | Map features to requirements |
| **F2** | Frontend Developer | Forge | Assess frontend feasibility |
| **F3** | Backend Developer | Forge | Assess backend feasibility, set signal |

#### GovernanceCrew (2 agents)

| ID | Agent | Founder | Task Focus |
|----|-------|---------|------------|
| **G1** | QA Agent | Guardian | Gate validation |
| **G2** | Security Agent | Guardian | Architecture security review |

**Phase 3 HITL Checkpoint**: `approve_feasibility_gate` - Confirm feasibility signal is GREEN

### Phase 4: Viability Agents

Phase 4 validates business model economics and makes the final recommendation. See [08-phase-4-viability.md](./08-phase-4-viability.md) for full specification.

**Flow**: `ViabilityFlow`
**Crews**: 3 crews (9 agents total)

#### FinanceCrew (3 agents)

| ID | Agent | Founder | Task Focus |
|----|-------|---------|------------|
| **L1** | Financial Controller | Ledger | Calculate unit economics (CAC, LTV, margins) |
| **L2** | Legal & Compliance | Ledger | Regulatory constraints |
| **L3** | Economics Reviewer | Ledger | Validate assumptions |

#### SynthesisCrew (3 agents)

| ID | Agent | Founder | Task Focus |
|----|-------|---------|------------|
| **C1** | Product PM | Compass | Synthesize evidence across phases |
| **C2** | Human Approval Agent | Compass | HITL decision orchestration |
| **C3** | Roadmap Writer | Compass | Document decision and next steps |

#### GovernanceCrew (3 agents)

| ID | Agent | Founder | Task Focus |
|----|-------|---------|------------|
| **G1** | QA Agent | Guardian | Final validation |
| **G2** | Security Agent | Guardian | PII scrubbing |
| **G3** | Audit Agent | Guardian | Flywheel persistence |

**Phase 4 HITL Checkpoints**:
- `approve_viability_gate` - Confirm viability signal is PROFITABLE
- `request_human_decision` - Final pivot/proceed decision

---

### Service Side Agents (Sage owns)

| Agent | Task Focus |
|-------|------------|
| **Customer Service Agent** | Marketing site conversations, lead qualification, email capture, routing to appropriate onboarding |
| **Founder Onboarding Agent** | Structured interviews for founder segment, business context extraction, brief creation |
| **Consultant Onboarding Agent** | Structured interviews for consultant/agency segment, white-label context, multi-client needs |

### Commercial Side Agents

#### Sage (CSO) - Strategy & Analysis

| Agent | Task Focus |
|-------|------------|
| **Customer Researcher** | Jobs, Pains, Gains analysis using JTBD framework |
| **Competitor Analyst** | Competitive landscape mapping, differentiation opportunities |

#### Forge (CTO) - Build & Deploy

| Agent | Task Focus |
|-------|------------|
| **UX/UI Designer** | Interface design for MVPs and testable artifacts |
| **Frontend Developer** | UI implementation, user-facing code |
| **Backend Developer** | API, data layer, server-side logic |

#### Pulse (CMO) - Marketing & Signals

| Agent | Task Focus |
|-------|------------|
| **Ad Creative Agent** | Ad copy, images, landing pages for desirability testing |
| **Communications Agent** | Messaging, content, press materials |
| **Social Media Analyst** | Social signals, engagement tracking, sentiment analysis |

#### Compass (CPO) - Balance & Synthesis

| Agent | Task Focus |
|-------|------------|
| **Project Manager** | Coordination across Service/Commercial, deliverable tracking, timeline management |

#### Ledger (CFO) - Finance & Compliance

| Agent | Task Focus |
|-------|------------|
| **Financial Controller** | Books, cash flow, runway tracking, budget management |
| **Legal & Compliance Agent** | Contracts, regulatory filings, business compliance |

### Governance Agents (Guardian)

| Agent | Task Focus |
|-------|------------|
| **Audit Agent** | Process audits, compliance verification, accountability tracking |
| **Security Agent** | Data privacy, security monitoring, threat assessment |
| **Quality Assurance Agent** | Framework compliance, logical consistency, output quality |

## CrewAI Implementation

This organizational structure maps directly to CrewAI's documented patterns.

### Pattern Mapping

| Concept | CrewAI Pattern | Implementation |
|---------|----------------|----------------|
| Phases (0-4) | Business concepts | Decompose into Flows |
| Flows | `@start`, `@listen`, `@router` | `OnboardingFlow`, `VPCDiscoveryFlow`, etc. |
| Crews | Collaborative agent groups | `OnboardingCrew`, `DiscoveryCrew`, etc. |
| Agents | Individual executors | Defined in `config/agents.yaml` |
| Tasks | Work items | Defined in `config/tasks.yaml` |

### Implementation Totals

| Metric | Count |
|--------|-------|
| **Phases** | 5 (0: Onboarding, 1: VPC Discovery, 2: Desirability, 3: Feasibility, 4: Viability) |
| **Flows** | 5 (`OnboardingFlow`, `VPCDiscoveryFlow`, `DesirabilityFlow`, `FeasibilityFlow`, `ViabilityFlow`) |
| **Crews** | 14 (see Complete Crew Summary above) |
| **Agents** | 45 (unique agent instances across all phases) |
| **HITL Checkpoints** | 10 (approval gates requiring human decision) |

### Current Status

See [09-status.md](./09-status.md) for current implementation status and deployment details.

---

## Agent Configuration Standard

Every agent in the StartupAI system MUST be configured with the following attributes. This standard ensures consistent behavior, proper tool access, and maintainable code across all 45 agents.

### Required Attributes

| Attribute | Required | Description | Default |
|-----------|----------|-------------|---------|
| `config` | YES | YAML reference for role, goal, backstory | - |
| `tools` | YES | List of tool instances (may be empty list `[]` for pure LLM agents) | - |
| `reasoning` | YES | Enable extended reasoning for complex analysis | `True` |
| `inject_date` | YES | Inject current date context for time-sensitive operations | `True` |
| `max_iter` | YES | Maximum iterations before stopping | 15-25 |
| `llm` | YES | LLM configuration (model, temperature) | See guidelines |
| `verbose` | YES | Logging verbosity for debugging | `True` |
| `allow_delegation` | YES | Inter-agent delegation (disabled for predictable flows) | `False` |

### LLM Temperature Guidelines

Temperature controls creativity vs consistency. Use the following guidelines based on agent type:

| Agent Type | Temperature | Rationale | Example Agents |
|------------|-------------|-----------|----------------|
| Research/Analysis | 0.1-0.3 | Factual accuracy, consistency, reproducible results | D2, J1, PAIN_RES, GAIN_RES, L1 |
| Synthesis/Ranking | 0.3-0.5 | Balanced reasoning, structured evaluation | D4, PAIN_RANK, GAIN_RANK, FIT_SCORE, C1 |
| Design/Creative | 0.6-0.8 | Innovation, variety, creative exploration | F1, V1, V2, V3, P1 |
| Interview/Conversation | 0.7 | Natural dialogue, adaptive responses | O1, D1 |
| Validation/QA | 0.1 | Strict methodology compliance, deterministic checks | G1, G2, GV1, GV2 |

### Standard Agent Constructor Pattern

All agents MUST follow this constructor pattern:

```python
from crewai import Agent
from crewai import LLM

@agent
def agent_name(self) -> Agent:
    """Agent description with ID and purpose."""
    return Agent(
        config=self.agents_config["agent_name"],
        tools=[tool1, tool2],           # List of tool instances (or [] if pure LLM)
        reasoning=True,                  # Extended reasoning enabled
        inject_date=True,                # Current date context
        max_iter=25,                     # Iteration limit
        llm=LLM(
            model="openai/gpt-4o",
            temperature=0.3              # Per agent type guidelines
        ),
        verbose=True,                    # Logging enabled
        allow_delegation=False,          # No inter-agent delegation
    )
```

### Tool Assignment Categories

Agents fall into three categories based on tool requirements:

| Category | Tool Configuration | Example Agents |
|----------|-------------------|----------------|
| **Tool-Equipped** | `tools=[tool1, tool2, ...]` - Specific tools for external data access | D2, J1, F2, P1 |
| **Pure LLM** | `tools=[]` - No external tools, relies on reasoning | GV1, GV2, S1, FIT_SCORE |
| **Hybrid** | Mixed tool + LLM reasoning | D1, D4, C1 |

**Reference**: See [reference/tool-mapping.md](./reference/tool-mapping.md) for complete agent-to-tool mapping.
**Reference**: See [reference/agent-specifications.md](./reference/agent-specifications.md) for full specifications of all 45 agents.

---

## Naming Conventions

### When to Use Founder Names
- Marketing materials (public-facing)
- User interfaces (explaining what's happening)
- Team introductions

**Example**: "Sage is analyzing your strategic positioning..."

### When to Use Specialist Agent Names
- Technical implementation
- API responses
- Logs and debugging
- Configuration files

**Example**: `"agent": "customer_researcher", "task": "jtbd_analysis"`

---

## Related Documents

### Architecture
- [00-introduction.md](./00-introduction.md) - Quick start and orientation
- [01-ecosystem.md](./01-ecosystem.md) - Three-service architecture overview
- [03-methodology.md](./03-methodology.md) - VPD framework reference (Test Cards, Learning Cards, evidence hierarchy)

### Phase Specifications
- [04-phase-0-onboarding.md](./04-phase-0-onboarding.md) - Founder's Brief capture
- [05-phase-1-vpc-discovery.md](./05-phase-1-vpc-discovery.md) - VPC Discovery (Customer Profile + Value Map)
- [06-phase-2-desirability.md](./06-phase-2-desirability.md) - Desirability validation
- [07-phase-3-feasibility.md](./07-phase-3-feasibility.md) - Feasibility validation
- [08-phase-4-viability.md](./08-phase-4-viability.md) - Viability + Decision

### Reference
- [09-status.md](./09-status.md) - Current implementation status
- [reference/api-contracts.md](./reference/api-contracts.md) - API specifications
- [reference/approval-workflows.md](./reference/approval-workflows.md) - HITL patterns

---

## Change Log

| Date | Change | Rationale |
|------|--------|-----------|
| 2026-01-19 | **ARCHITECTURAL PIVOT**: Phase 0 simplified to Quick Start (no AI) | AI in critical path caused non-determinism, $17+ cost, test flakiness |
| 2026-01-19 | Deleted O1 (Interview Gap Analyzer) and GV2 (Intent Verification) | No interview transcript to process |
| 2026-01-19 | Moved GV1 and S1 to Phase 1 `BriefGenerationCrew` | Brief now generated from research, not user input |
| 2026-01-19 | Agent count 45 → 43 | Two agents deleted |
| 2026-01-13 | Documented two-layer Phase 0 architecture (Alex chat + CrewAI validation) | Align documentation with implementation reality (SUPERSEDED 2026-01-19) |
| 2026-01-13 | Renamed O1 from "Founder Interview Agent" to "Interview Gap Analyzer Agent" | Alex conducts interview, O1 analyzes completeness |
| 2026-01-09 | Added Agent Configuration Standard section with required attributes, temperature guidelines, constructor pattern | Bullet-proof specifications before code implementation |
| 2026-01-07 | Added CrewAI Pattern Hierarchy section with complete crew summary | Align with CrewAI documentation patterns |
| 2026-01-07 | Restructured Phase 0-4 agents into crew groupings | Fix one-agent "crews", rename "Flow 1-7" to proper crews |
| 2026-01-07 | Added Phase 2-4 agent sections (Desirability, Feasibility, Viability) | Complete documentation of all phase agents |
| 2026-01-07 | Updated CrewAI Implementation section with pattern mapping and totals | Clear mapping of concepts to CrewAI patterns |
| 2026-01-07 | Replaced VPD terminology section with reference to 03-methodology.md | Single source of truth, reduce duplication |
| 2026-01-07 | Updated document references to new phase documents (04-08) | Archived 05-phase-0-1-specification.md |
| 2026-01-07 | Added Related Documents section | Navigation to phase and reference docs |
| 2026-01-07 | Expanded Guardian's Board-Level Role section with Executive vs Board distinction | Clarify Guardian as sentinel/overwatch, not executor |
| 2026-01-07 | Added RACI model for approvals with Guardian as "Consulted" | Clear accountability chain before HITL |
| 2026-01-07 | Added Data Governance distributed ownership table | Guardian oversees, domain experts own |
| 2026-01-07 | Pulse: Chief Growth Officer → Chief Marketing Officer (CMO) | Standard C-suite title, aligns with marketing-focused activities |
| 2026-01-07 | Added abbreviations (CSO, CTO, CMO, CPO, CGO, CFO) to founder titles | Consistency and clarity |
| 2026-01-05 | Added Phase 0 & Phase 1 agent definitions (O1, G1, G2, S1, E1, D1-D4, J1-J2, P1-P2, G1-G2, V1-V3, W1-W2, F1-F2) | VPD framework compliance |
| 2026-01-05 | Renamed "Client Brief" to "Founder's Brief" throughout | Align with VPD Phase 0 terminology |
| 2026-01-05 | Restructured Approval Checkpoints by phase | Phase 0, Phase 1, Phase 2+ separation |
| 2025-11-21 | Added Approval Checkpoint Ownership section | HITL workflow distribution across founders |
| 2025-11-21 | Complete organizational restructure with Service/Commercial model | Organizational Physics principles, clear separation of concerns |
| 2025-11-21 | Added 18 specialist agents across all founders | Complete task executor coverage |
| 2025-11-21 | Documented Guardian dual role (Founder + Board) | Accountability vs responsibility distinction |
| 2025-11-21 | Added Compass as balancing force between sides | PSIU Unifier role, tension management |
| 2025-11-21 | Defined Founder's Brief as handoff contract | Clear interface between Phase 0 and Phase 1+ |
| 2025-11-20 | Added Ledger as 6th founder (CFO) | Financial viability accountability |
| 2025-11-20 | Restructured to customer-centric model | RoundMap-inspired, customer as integrating point |
| 2025-11-20 | Added PSIU balance documentation | Organizational Physics principles |
| 2025-11-20 | Corrected founder roles to match marketing site | Align with startupai.site team page |
| 2025-11-20 | Reorganized to flat team structure | Reflects startup reality - co-equal founders |
| 2025-11-19 | Added founder personas | Company run by AI Founders |
