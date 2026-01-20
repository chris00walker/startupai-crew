---
purpose: Reusable VPD methodology patterns for all validation phases
status: active
last_reviewed: 2026-01-07
vpd_compliance: true
---

# StartupAI Validation Methodology

## Overview

This document defines the **reusable methodology patterns** that all StartupAI validation phases follow. It extracts and codifies the Value Proposition Design (VPD) framework by Alex Osterwalder and Yves Pigneur, along with patterns from *Testing Business Ideas* and *The Mom Test*.

**All phase specifications (04-08) reference this document for methodology patterns.**

---

## Guiding Principles

### Agentic Systems Architecture

StartupAI follows the recommended pattern for building agentic systems:

1. **Deterministic Backbone**: Manages structure, branching, state, and guardrails (implemented via Crews with task dependencies)
2. **Scoped Intelligence (Agents)**: Operate within boundaries defined by the orchestration layer
3. **Graduated Complexity**:
   - Simple operations → Plain code
   - Single completions → Ad-hoc LLM calls
   - Tool-use tasks → Single agents
   - Complex reasoning → Multi-agent Crews

> **Implementation Note**: StartupAI uses CrewAI Flows + Crews on Modal serverless. The canonical architecture is 4 flows / 14 crews / 43 agents with Supabase state + HITL checkpoints.

### Anti-Patterns to Avoid

- Over-complicating simple steps with unnecessary agent overhead
- Cramming excessive functionality into single agents (context bloat, hallucination risks)
- Building multi-step workflows without architectural structure
- Using agents as replacements for conditional logic or state management

---

## Value Proposition Design Framework

### The Value Proposition Canvas

The VPC has two sides that must achieve **fit**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       VALUE PROPOSITION CANVAS                               │
│                                                                              │
│   ┌─────────────────────────────┐     ┌─────────────────────────────┐      │
│   │      VALUE MAP (Left)       │     │  CUSTOMER PROFILE (Right)   │      │
│   │                             │     │                             │      │
│   │  ┌───────────────────────┐  │     │  ┌───────────────────────┐  │      │
│   │  │ Products & Services   │  │     │  │    Customer Jobs      │  │      │
│   │  │ What we offer         │  │     │  │ What they're trying   │  │      │
│   │  └───────────────────────┘  │     │  │ to accomplish         │  │      │
│   │                             │     │  └───────────────────────┘  │      │
│   │  ┌───────────────────────┐  │     │                             │      │
│   │  │   Pain Relievers      │◄─┼─FIT─┼──►┌───────────────────────┐  │      │
│   │  │ How we address pains  │  │     │  │      Pains            │  │      │
│   │  └───────────────────────┘  │     │  │ Undesired outcomes    │  │      │
│   │                             │     │  └───────────────────────┘  │      │
│   │  ┌───────────────────────┐  │     │                             │      │
│   │  │   Gain Creators       │◄─┼─FIT─┼──►┌───────────────────────┐  │      │
│   │  │ How we create gains   │  │     │  │      Gains            │  │      │
│   │  └───────────────────────┘  │     │  │ Desired outcomes      │  │      │
│   │                             │     │  └───────────────────────┘  │      │
│   └─────────────────────────────┘     └─────────────────────────────┘      │
│                                                                              │
│   PROBLEM-SOLUTION FIT: Value Map addresses Customer Profile                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Customer Profile Components

#### Jobs-to-be-Done

| Type | Description | Example |
|------|-------------|---------|
| **Functional** | Tasks to complete | "Validate my startup idea" |
| **Emotional** | How they want to feel | "Feel confident I'm not wasting time" |
| **Social** | How they want to be perceived | "Be seen as a smart entrepreneur" |
| **Supporting - Buyer** | Comparing, purchasing, delivery | "Compare validation services easily" |
| **Supporting - Co-creator** | Feedback, customization | "Customize the validation process" |
| **Supporting - Transferrer** | Canceling, disposing, reselling | "Export my data if I leave" |

#### Pains

| Category | Description |
|----------|-------------|
| **Undesired Outcomes** | What they're trying to avoid |
| **Obstacles** | What prevents them from getting job done |
| **Risks** | What could go wrong |

#### Gains

| Category | Description |
|----------|-------------|
| **Required** | Must-have outcomes (table stakes) |
| **Expected** | Standard expectations |
| **Desired** | Would be nice to have |
| **Unexpected** | Delighters beyond expectations |

### Value Map Components

| Component | Purpose | Design Principle |
|-----------|---------|------------------|
| **Products & Services** | What we offer | Address top-ranked Jobs |
| **Pain Relievers** | How we address specific pains | Focus on severe pains, do them well |
| **Gain Creators** | How we create specific gains | Prioritize important gains |

---

## Business Model Canvas

The BMC captures the full business model across 9 building blocks:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        BUSINESS MODEL CANVAS                                 │
│                                                                              │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┬────────────┐│
│  │              │              │              │              │            ││
│  │     KEY      │     KEY      │    VALUE     │  CUSTOMER    │  CUSTOMER  ││
│  │   PARTNERS   │  ACTIVITIES  │ PROPOSITIONS │ RELATIONSHIPS│  SEGMENTS  ││
│  │              │              │              │              │            ││
│  │  Who are our │  What key    │  What value  │  What type   │  Who are   ││
│  │  key         │  activities  │  do we       │  of relation │  we        ││
│  │  partners?   │  do our VP   │  deliver?    │  does each   │  creating  ││
│  │              │  require?    │              │  segment     │  value     ││
│  │              │              │              │  expect?     │  for?      ││
│  │              ├──────────────┤              │              │            ││
│  │              │              │              ├──────────────┤            ││
│  │              │     KEY      │              │              │            ││
│  │              │  RESOURCES   │              │   CHANNELS   │            ││
│  │              │              │              │              │            ││
│  │              │  What key    │              │  How do we   │            ││
│  │              │  resources   │              │  reach our   │            ││
│  │              │  do our VP   │              │  customer    │            ││
│  │              │  require?    │              │  segments?   │            ││
│  │              │              │              │              │            ││
│  ├──────────────┴──────────────┴──────────────┴──────────────┴────────────┤│
│  │                                                                         ││
│  │         COST STRUCTURE                    REVENUE STREAMS               ││
│  │                                                                         ││
│  │  What are the most important costs?       For what value are customers  ││
│  │                                           willing to pay?               ││
│  │                                                                         ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### BMC Building Blocks

| Block | Question | Category |
|-------|----------|----------|
| **Customer Segments** | Who are we creating value for? | Demand-Side |
| **Value Propositions** | What value do we deliver? | Core |
| **Channels** | How do we reach customers? | Demand-Side |
| **Customer Relationships** | What relationship does each segment expect? | Demand-Side |
| **Revenue Streams** | For what value are customers willing to pay? | Economics |
| **Key Resources** | What key resources does our VP require? | Supply-Side |
| **Key Activities** | What key activities does our VP require? | Supply-Side |
| **Key Partners** | Who are our key partners and suppliers? | Supply-Side |
| **Cost Structure** | What are the most important costs? | Economics |

---

## Strategyzer Framework Mapping: VPC → BMC

StartupAI's validation phases map directly to the Strategyzer frameworks:

### Phase-to-Framework Mapping

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STRATEGYZER FRAMEWORK MAPPING                             │
│                                                                              │
│  PHASE 0: ONBOARDING                                                        │
│  └── Captures hypotheses about VPC and BMC (not validated)                  │
│                                                                              │
│  PHASE 1: VPC DISCOVERY                                                     │
│  └── VALUE PROPOSITION CANVAS                                               │
│      ├── Customer Profile (Jobs, Pains, Gains)                              │
│      └── Value Map (Products, Pain Relievers, Gain Creators)                │
│                                                                              │
│  PHASES 2-4: BMC VALIDATION                                                 │
│  └── BUSINESS MODEL CANVAS (validated progressively)                        │
│                                                                              │
│      Phase 2: DESIRABILITY (Demand-Side)                                    │
│      ├── Value Propositions (from VPC)                                      │
│      ├── Customer Segments                                                  │
│      ├── Channels                                                           │
│      └── Customer Relationships                                             │
│                                                                              │
│      Phase 3: FEASIBILITY (Supply-Side)                                     │
│      ├── Value Propositions (verified buildable)                            │
│      ├── Key Activities                                                     │
│      ├── Key Resources                                                      │
│      └── Key Partners                                                       │
│                                                                              │
│      Phase 4: VIABILITY (Economics)                                         │
│      ├── Value Propositions (verified profitable)                           │
│      ├── Channels (acquisition costs)                                       │
│      ├── Key Resources (operational costs)                                  │
│      ├── Cost Structure                                                     │
│      └── Revenue Streams                                                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Phase 1 → Value Proposition Canvas

Phase 1 focuses **exclusively** on achieving Problem-Solution Fit through the VPC:

| VPC Component | Phase 1 Activity | Evidence Source |
|---------------|------------------|-----------------|
| **Customer Profile** | Discover Jobs, Pains, Gains | Interviews, observation, CTA tests |
| **Value Map** | Design Products, Pain Relievers, Gain Creators | VPC alignment with Customer Profile |
| **Fit** | Score Problem-Solution Fit ≥ 70 | Evidence triangulation |

**Output**: Validated VPC ready to inform BMC validation

### Phase 2 → BMC Demand-Side Blocks

Phase 2 validates that customers **actually want** the value proposition:

| BMC Block | What's Validated | Evidence Source |
|-----------|------------------|-----------------|
| **Value Propositions** | Does the value resonate? | Landing page conversions, ad engagement |
| **Customer Segments** | Is this the right audience? | `problem_resonance` metric |
| **Channels** | Can we reach them effectively? | Channel experiment results (Meta, Google, etc.) |
| **Customer Relationships** | What relationship type works? | User behavior, engagement patterns |

**Innovation Physics Signals**:
- `problem_resonance < 0.3` → SEGMENT_PIVOT (wrong Customer Segments)
- `zombie_ratio >= 0.7` → VALUE_PIVOT (wrong Value Proposition)

### Phase 3 → BMC Supply-Side Blocks

Phase 3 validates that we **can build** the value proposition:

| BMC Block | What's Validated | Evidence Source |
|-----------|------------------|-----------------|
| **Value Propositions** | Can we actually deliver this? | Technical assessment |
| **Key Activities** | What operations are required? | Build complexity analysis |
| **Key Resources** | What assets do we need? | Resource audit, cost estimation |
| **Key Partners** | Who provides critical inputs? | Supplier/API evaluation |

**Innovation Physics Signals**:
- `feasibility_signal == ORANGE_CONSTRAINED` → FEATURE_PIVOT (downgrade Key Activities/Resources)
- `feasibility_signal == RED_IMPOSSIBLE` → KILL

### Phase 4 → BMC Economics Blocks

Phase 4 validates that the business model **makes money**:

| BMC Block | What's Validated | Evidence Source |
|-----------|------------------|-----------------|
| **Value Propositions** | Is it profitable to deliver? | Unit economics analysis |
| **Channels** | What's the acquisition cost? | CAC from channel experiments |
| **Key Resources** | What are operational costs? | Infrastructure + API costs |
| **Cost Structure** | Total cost model | Sum of all costs |
| **Revenue Streams** | What will customers pay? | WTP experiments, pricing tests |

**Innovation Physics Signals**:
- `viability_signal == UNDERWATER` → PRICE_PIVOT or COST_PIVOT
- `viability_signal == ZOMBIE_MARKET` → MODEL_PIVOT or KILL

### BMC Block Validation Summary

| BMC Block | Phase Validated | Pivot if Invalid |
|-----------|-----------------|------------------|
| Customer Segments | Phase 2 | SEGMENT_PIVOT |
| Value Propositions | Phases 1-4 | VALUE_PIVOT, FEATURE_PIVOT |
| Channels | Phases 2, 4 | CHANNEL_PIVOT |
| Customer Relationships | Phase 2 | VALUE_PIVOT |
| Revenue Streams | Phases 1 (WTP), 4 | PRICE_PIVOT |
| Key Resources | Phases 3, 4 | FEATURE_PIVOT, COST_PIVOT |
| Key Activities | Phase 3 | FEATURE_PIVOT |
| Key Partners | Phase 3 | FEATURE_PIVOT |
| Cost Structure | Phase 4 | COST_PIVOT |

### Value Proposition as the Core

Notice that **Value Propositions** is validated in every phase:

1. **Phase 1**: Designed through VPC (Problem-Solution Fit)
2. **Phase 2**: Tested for desirability (do customers want it?)
3. **Phase 3**: Tested for feasibility (can we build it?)
4. **Phase 4**: Tested for viability (can we profit from it?)

This reflects the Strategyzer insight that the Value Proposition is the **heart of the business model** - everything else flows from it.

---

## Evidence Hierarchy (SAY vs DO)

**Core Principle**: What customers SAY and what they DO are two different things. Behavioral evidence is stronger than stated preferences.

### Evidence Weighting

| Evidence Type | Weight | Description | Example |
|---------------|--------|-------------|---------|
| **Paid** | 5 | Actually paid money | Pre-order, crowdfunding pledge |
| **High-Commitment CTA** | 4 | Significant action required | Demo request, application form |
| **Medium-Commitment CTA** | 3 | Moderate action | Email signup, form fill |
| **Low-Commitment CTA** | 2 | Minimal action | Click, view, like |
| **Stated** | 1 | Verbal commitment | "I would buy this" |
| **Implied** | 0.5 | Absence of rejection | Didn't say no |

### Evidence Triangulation

When synthesizing evidence from multiple sources:

1. **Collect** evidence from interviews (SAY), observations (DO-indirect), and CTAs (DO-direct)
2. **Weight** by evidence type using hierarchy above
3. **Compare** SAY vs DO for discrepancies (important signal!)
4. **Score** confidence based on:
   - Evidence volume (sample size)
   - Evidence diversity (multiple methods)
   - Evidence consistency (do sources agree?)

---

## Testing Business Ideas Framework

### Assumptions Mapping

Before testing, prioritize assumptions using a 2×2 matrix:

```
                         EVIDENCE STRENGTH
                    Weak ◄────────────► Strong

           High    ┌─────────────┬─────────────┐
                   │             │             │
        I          │   TEST      │   MONITOR   │
        M          │   FIRST     │             │
        P          │  (Risky)    │  (Validated)│
        O          │             │             │
        R          ├─────────────┼─────────────┤
        T          │             │             │
        A          │   TEST      │   IGNORE    │
        N          │   LATER     │             │
        C          │  (Nice to   │  (Low risk) │
        E          │   know)     │             │
                   │             │             │
           Low     └─────────────┴─────────────┘
```

**Focus on top-left quadrant**: High importance + Weak evidence = Riskiest assumptions

### Test Card Framework

Every experiment must have a Test Card **before** running:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  TEST CARD                                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  STEP 1: HYPOTHESIS                                                          │
│  "We believe that [customer segment] will [expected behavior]               │
│   because [reason/assumption]"                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  STEP 2: TEST                                                                │
│  To verify, we will: [specific experiment description]                       │
│  Cost: [budget]  Duration: [timeline]  Reliability: [low/medium/high]       │
├─────────────────────────────────────────────────────────────────────────────┤
│  STEP 3: METRIC                                                              │
│  We will measure: [specific metric]                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  STEP 4: CRITERIA (SET IN ADVANCE!)                                          │
│  We are right if: [specific threshold]                                       │
│  Example: "8 out of 100 landing page visitors sign up for waitlist"         │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Critical**: Success criteria MUST be set BEFORE the experiment runs.

### Learning Card Framework

After every experiment, capture results:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  LEARNING CARD                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  HYPOTHESIS                                                                  │
│  "We believed that..."                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  OBSERVATION                                                                 │
│  "We observed..."  [include actual data/metrics]                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  LEARNINGS                                                                   │
│  "From that we learned that..."                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  DECISIONS & ACTIONS                                                         │
│  "Therefore we will..."                                                      │
│  Owner: [who]  Deadline: [when]                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Strategyzer Experiment Library (44 Experiments)

### Discovery Experiments (Weak-Moderate Evidence, Fast, Cheap)

| Experiment | Evidence Type | Description |
|------------|---------------|-------------|
| Customer Interviews | SAY | Talk to potential customers about problems |
| Discovery Surveys | SAY | Open-ended exploration questions |
| Discussion Forums | DO-indirect | Monitor existing community discussions |
| Search Trend Analysis | DO-indirect | Analyze Google Trends, keyword volumes |
| Follow-Me-Home | DO-indirect | Observe customers in natural context |
| Sales Force Feedback | SAY | Gather insights from sales team |
| Data Analysis | DO-indirect | Analyze existing customer data |

### Validation Experiments (Stronger Evidence, More Investment)

| Experiment | Evidence Type | Description |
|------------|---------------|-------------|
| Landing Page (Smoke Test) | DO-CTA | Simple page with signup CTA |
| Fake Door Test | DO-CTA | UI elements for features that don't exist |
| Explainer Video | DO-CTA | Video describing concept + CTA |
| A/B Split Test | DO-CTA | Compare two variants |
| Email Campaign | DO-CTA | Test message resonance |
| Social Media Campaign | DO-CTA | Test audience targeting |
| Online Ad Campaign | DO-CTA | Test messaging and audience |
| Crowdfunding | DO-$$$ | Validate with financial commitment |
| Pre-sale | DO-$$$ | Collect payment before building |
| Wizard of Oz | DO | Manual service behind automated facade |
| Concierge MVP | DO | Manual, transparent personal service |
| Single Feature MVP | DO | Build one core feature only |

### Experiment Selection by Learning Goal

```
LEARNING GOAL → EXPERIMENT TYPES

"Does this segment exist?"
├── Discussion Forums (Indirect/DO) - Are they asking about this?
├── Search Trend Analysis (Indirect/DO) - Are they searching for this?
├── Data Analysis (Indirect/DO) - Do we have existing evidence?
└── Customer Interviews (Direct/SAY) - Can we find and talk to them?

"Is this segment reachable?"
├── Online Ad Campaign (Indirect/DO) - Can we target them?
├── Social Media Campaign (Indirect/DO) - Where do they respond?
└── Email Campaign (Direct/DO) - Can we reach them directly?

"Is this segment interested?"
├── Landing Page/Smoke Test (Indirect/DO+CTA) - Do they sign up?
├── Fake Door Test (Indirect/DO+CTA) - Do they click on features?
├── Explainer Video (Indirect/DO+CTA) - Do they watch and act?
└── A/B Split Test (Indirect/DO) - Which message resonates?

"Is this segment willing to pay?"
├── Pre-sale (Indirect/DO+$$) - Will they pay before it exists?
├── Crowdfunding (Indirect/DO+$$) - Will they pledge money?
├── Mock Sale (Indirect/DO) - Will they go through checkout?
└── Wizard of Oz (Direct/DO) - Will they pay for manual service?
```

---

## The Mom Test Interview Methodology

### Core Rules

```
RULE 1: Talk about their life, not your idea
RULE 2: Ask about specifics in the PAST, not generics or opinions about the FUTURE
RULE 3: Talk less, listen more (they talk 80%, you talk 20%)
```

### Never Ask (Hypothetical Questions)

- "Would you buy a product that did X?"
- "Do you think this is a good idea?"
- "Would you use this?"
- "How much would you pay for this?"

### Always Ask (Fact-Based Questions)

- "Talk me through what happened the last time X came up"
- "Show me how you currently do this"
- "When is the last time you struggled with this?"
- "What have you already tried? What happened?"
- "Are you actively searching for a solution? What's the sticking point?"

### Strategyzer's 8 Ground Rules

1. Listen more, talk less
2. Use open-ended follow-up questions ("Can you expand on that...")
3. Focus on FACTS, not opinions (ask "When is the last time..." not "Would you...")
4. Ask "why" frequently ("Why is that important to you?")
5. Don't ask about buying decisions directly
6. NEVER offer solutions during discovery interviews
7. Keep your value proposition in the background
8. Ask for referrals at the end

---

## Problem-Solution Fit Criteria

Phase 1 exit requires achieving Problem-Solution Fit:

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| **Fit Score** | ≥ 70/100 | Weighted coverage of Jobs, Pains, Gains |
| **Jobs Addressed** | ≥ 75% | Top-ranked jobs have Products/Services |
| **Pains Addressed** | ≥ 75% | Top-ranked pains have Pain Relievers |
| **Gains Addressed** | ≥ 70% | Top-ranked gains have Gain Creators |
| **WTP Validated** | Yes | Behavioral evidence (not just stated) |

### Fit Score Calculation

```python
fit_score = (
    (jobs_addressed_pct * 0.30) +
    (pains_addressed_pct * 0.35) +
    (gains_addressed_pct * 0.25) +
    (wtp_validated * 0.10 * 100)
)
```

---

## Innovation Physics Signals

The validation flow uses computed metrics for routing decisions:

### Core Signals

| Signal | Type | Values |
|--------|------|--------|
| `desirability_signal` | Enum | NO_SIGNAL, NO_INTEREST, WEAK_INTEREST, STRONG_COMMITMENT |
| `feasibility_signal` | Enum | UNKNOWN, GREEN, ORANGE_CONSTRAINED, RED_IMPOSSIBLE |
| `viability_signal` | Enum | UNKNOWN, PROFITABLE, UNDERWATER, ZOMBIE_MARKET |

### Evidence Metrics

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| `problem_resonance` | (clicks + signups) / impressions | Fraction resonating with problem |
| `zombie_ratio` | (clicks - signups) / clicks | "Interested but not committed" |

### Routing Logic (Innovation Physics)

```
IF problem_resonance < 0.3:
    → SEGMENT_PIVOT (wrong audience)

IF problem_resonance >= 0.3 AND zombie_ratio >= 0.7:
    → VALUE_PIVOT (right audience, wrong promise)

IF desirability_signal == STRONG_COMMITMENT:
    → Proceed to Feasibility

IF feasibility_signal == ORANGE_CONSTRAINED:
    → FEATURE_PIVOT (downgrade and re-test desirability)

IF feasibility_signal == RED_IMPOSSIBLE:
    → KILL

IF viability_signal == UNDERWATER or ZOMBIE_MARKET:
    → HITL Decision (PRICE_PIVOT, COST_PIVOT, or KILL)
```

---

## Pivot Types

| Pivot Type | Trigger | Action |
|------------|---------|--------|
| `SEGMENT_PIVOT` | problem_resonance < 0.3 | Change customer segment |
| `VALUE_PIVOT` | High interest, low commitment | Change value proposition |
| `CHANNEL_PIVOT` | Can't reach segment | Change acquisition channel |
| `FEATURE_PIVOT` | Feasibility constrained | Downgrade features, re-test |
| `PRICE_PIVOT` | CAC > LTV | Increase price, re-test desirability |
| `COST_PIVOT` | CAC > LTV | Reduce costs, re-test feasibility |
| `MODEL_PIVOT` | Fundamental unit economics issue | Change business model |
| `KILL` | No viable path | Terminate project |

---

## HITL Checkpoint Pattern

All phases use consistent Human-in-the-Loop patterns:

### Checkpoint Definition

```yaml
checkpoint:
  id: string               # Unique identifier
  phase: number            # Which phase (0-4)
  owner: string            # Primary founder responsible
  purpose: string          # What decision is being made
  presentation: object     # What to show the human
  options: array           # Available decisions
  required_for_exit: bool  # Blocks phase progression
```

### Workflow Pattern

1. Agent prepares decision context
2. Task with `human_input: true` pauses workflow
3. Webhook notifies product app
4. Human reviews and decides in UI
5. Product app calls `/resume` endpoint
6. Flow continues based on decision

---

## Phase Specification Template

All phase documents (04-08) follow this structure:

```markdown
# Phase N: [Name]

## Purpose
- What this phase accomplishes
- What this phase does NOT do
- Entry criteria (what must be true to enter)
- Exit criteria (what must be true to proceed)

## Flow Diagram
ASCII diagram showing orchestration

## Agents
For each agent:
- ID, Name, Founder assignment
- Role, Goal, Backstory
- Tasks with expected outputs
- Tools available

## Output Schemas
Pydantic models for phase artifacts

## HITL Checkpoints
Approval gates within this phase

## Methodology Compliance
How this phase implements VPD patterns (reference this document)
```

---

## Sources

- Osterwalder, A., Pigneur, Y., et al. (2014). *Value Proposition Design*. Wiley.
- Bland, D. J., Osterwalder, A. (2019). *Testing Business Ideas*. Wiley.
- Fitzpatrick, R. (2013). *The Mom Test*. CreateSpace.
- Moesta, B., Spiek, C. *Jobs-to-be-Done Framework*. Re-Wired Group.
- CrewAI Blog. (2025). *Agentic Systems with CrewAI*. blog.crewai.com

---

## Related Documents

### Architecture
- [00-introduction.md](./00-introduction.md) - Quick start and orientation
- [01-ecosystem.md](./01-ecosystem.md) - Three-service architecture overview
- [02-organization.md](./02-organization.md) - 6 AI Founders and agents

### Phase Specifications
- [04-phase-0-onboarding.md](./04-phase-0-onboarding.md) - Quick Start onboarding
- [05-phase-1-vpc-discovery.md](./05-phase-1-vpc-discovery.md) - VPC Discovery (Customer Profile + Value Map)
- [06-phase-2-desirability.md](./06-phase-2-desirability.md) - Desirability validation
- [07-phase-3-feasibility.md](./07-phase-3-feasibility.md) - Feasibility validation
- [08-phase-4-viability.md](./08-phase-4-viability.md) - Viability + Decision

### Reference
- [09-status.md](./09-status.md) - Current implementation status
- [reference/api-contracts.md](./reference/api-contracts.md) - API specifications
- [reference/approval-workflows.md](./reference/approval-workflows.md) - HITL patterns
