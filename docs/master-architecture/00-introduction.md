---
purpose: Repository introduction, architecture overview, and quick start
status: active
last_reviewed: 2026-01-20
vpd_compliance: true
architectural_pivot: 2026-01-19
---

# StartupAI Crew - Introduction & Architecture

## Overview

**VPD-compliant validation engine for delivering Fortune 500-quality strategic analysis**

This repository contains the brain of the StartupAI ecosystem - a multi-phase crew orchestration system that powers the AI Founders team. It implements the **Value Proposition Design (VPD)** framework by Osterwalder & Pigneur using CrewAI Flows to deliver Problem-Solution Fit, Desirability, Feasibility, and Viability validation.

> **VPD Framework Compliance**: This system implements patterns from *Value Proposition Design*, *Testing Business Ideas*, and *Business Model Generation*. See [03-methodology.md](./03-methodology.md) for VPD framework reference and phase documents (04-08) for detailed implementation.

## Design Principles

### 1. Service/Commercial Model
Organized around the customer, not a linear pipeline:
- **Service Side**: Customer intake and brief capture
- **Commercial Side**: Value delivery through analysis and validation
- **Compass**: Balances competing interests, synthesizes evidence
- **Guardian**: Governance oversight across all functions

### 2. Gated Validation
Validation follows the Strategyzer methodology with four gates:
```
VALUE PROPOSITION DESIGN → [Test Cycles] → VPC GATE → [Test Cycles] → DESIRABILITY GATE → [Test Cycles] → FEASIBILITY GATE → [Test Cycles] → VIABILITY GATE
```

**Key principles:**
- **VPD comes first**: You must design and validate the Value Proposition Canvas (Customer Profile + Value Map) before testing desirability. There's no point asking "do they want it?" until you've validated you're targeting the correct customer segment.
- **Test cycles at every stage**: Each phase requires iterative testing. VPD itself requires cycles to achieve Problem-Solution Fit (fit score ≥ 70).
- **Non-linear with pivots**: This is NOT a straight linear process. At any point, a critical failure in Testing Business Ideas can force a pivot (SEGMENT_PIVOT, VALUE_PIVOT, FEATURE_PIVOT, PRICE_PIVOT, COST_PIVOT, MODEL_PIVOT) that loops back to an earlier phase.
- **Gates are checkpoints**: Each gate (`approve_vpc_completion`, `approve_desirability_gate`, `approve_feasibility_gate`, `approve_viability_gate`) requires evidence-based validation before proceeding.

### 3. CrewAI Pattern Hierarchy

This architecture uses CrewAI's documented patterns. Understanding the hierarchy is essential:

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

**Pattern Definitions** (per CrewAI documentation):

| Pattern | Definition | Key Characteristic |
|---------|------------|-------------------|
| **Phase** | Business/methodology concept | NOT a CrewAI construct - decomposed into Flows |
| **Flow** | Event-driven orchestration with `@start`, `@listen`, `@router` | Controls WHEN and IF crews execute |
| **Crew** | Collaborative GROUP of agents (2+) | Controls HOW agents collaborate |
| **Agent** | Individual executor with role/goal/backstory | Performs tasks |
| **Task** | Specific work item assigned to an agent | Produces output |

**Critical Rule**: A crew must have 2+ agents. One agent is NOT a crew - it's just an agent called within a Flow method.

**Routing & State**:
- **Routers** (`@router`): Implement governance gates with conditional routing
- **Structured State**: Pydantic models carry data through the Flow
- **Listeners**: `@listen("gate_label")` handles route-specific logic

## Ecosystem Position

```
┌─────────────────────┐
│   AI Founders Core  │
│   (startupai-crew)  │  ← THIS REPOSITORY
│  CrewAI Flows Engine│
└──────────┬──────────┘
           │
┌──────────┼──────────────┐
│          │              │
▼          │              ▼
┌──────────────┐   │    ┌──────────────┐
│startupai.site│   │    │app.startupai │
│  Marketing   │   │    │   .site      │
│  (Netlify)   │   │    │  (Netlify)   │
└──────────────┘   │    └──────────────┘
                   │
                   ▼
           ┌─────────────┐
           │  Supabase   │
           │   Shared DB │
           └─────────────┘
```

## The 6 AI Founders

> **Single Source**: See [02-organization.md](./02-organization.md) for complete founder details, responsibilities, and organizational structure.

| Founder | Title | Primary Domain |
|---------|-------|----------------|
| **Sage** | CSO | Strategy, VPC design, owns Service Side |
| **Forge** | CTO | Build, technical feasibility |
| **Pulse** | CMO | Marketing, market signals, desirability evidence |
| **Compass** | CPO | Balance, synthesis, pivot/proceed |
| **Guardian** | CGO | Governance, accountability, oversight |
| **Ledger** | CFO | Finance, viability, compliance |

## Phase-Based Architecture

> **Single Source**: See [02-organization.md](./02-organization.md) for complete agent details. Phase specifications: [04-phase-0](./04-phase-0-onboarding.md), [05-phase-1](./05-phase-1-vpc-discovery.md), [06-phase-2](./06-phase-2-desirability.md), [07-phase-3](./07-phase-3-feasibility.md), [08-phase-4](./08-phase-4-viability.md).

### Phase 0: Quick Start (No AI)

> **Architectural Pivot (2026-01-19)**: Phase 0 was simplified to Quick Start. See [ADR-006](../adr/006-quick-start-architecture.md).

**Purpose**: Fast capture of business idea (30 seconds)

**Architecture**: Simple form submission with no AI:

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Quick Start Form** | Product App (Next.js) | User enters business idea + optional context |
| **Phase 1 Trigger** | API call | Immediately starts Phase 1 after submission |

**Flow**: None - form submission only, no CrewAI in Phase 0

| Metric | Value |
|--------|-------|
| Duration | ~30 seconds |
| AI Cost | $0 |
| Crews | None |
| Agents | None |
| HITL | None |

**Output**: `raw_idea` and optional `additional_context` passed to Phase 1

**Brief Generation**: The Founder's Brief is now AI-generated in Phase 1 by BriefGenerationCrew (GV1 + S1)

**HITL**: Combined with Phase 1 as `approve_discovery_output` (Brief + VPC approval)

### Phase 1: VPC Discovery (Brief Generation + Customer Profile + Value Map)

**Purpose**: Generate Founder's Brief from research, discover customer reality, design value using VPD framework

**Flow**: `VPCDiscoveryFlow` - Orchestrates brief generation and discovery crews with fit routing

| Crew | Agents | Focus | Output |
|------|--------|-------|--------|
| BriefGenerationCrew | GV1, S1 | Generate Founder's Brief from research | **Founder's Brief** |
| DiscoveryCrew | E1, D1, D2, D3, D4 | Experiment design, evidence collection | SAY + DO evidence |
| CustomerProfileCrew | J1, J2, P1, P2, G1, G2 | Jobs, Pains, Gains research + ranking | Customer Profile |
| ValueDesignCrew | V1, V2, V3 | Products, Pain Relievers, Gain Creators | Value Map |
| WTPCrew | W1, W2 | Willingness-to-pay experiments | WTP validation |
| FitAssessmentCrew | F1, F2 | Fit scoring, iteration routing | **Validated VPC** (fit ≥ 70) |

**HITL**: `approve_discovery_output` (combined Brief + VPC), `approve_experiment_plan`, `approve_pricing_test`

### Phase 2: Desirability Validation

**Purpose**: Test whether customers actually want the value proposition

**Flow**: `DesirabilityFlow` - Orchestrates build/growth with desirability routing

| Crew | Agents | Focus | Output |
|------|--------|-------|--------|
| BuildCrew | F1, F2, F3 | Landing pages, testable artifacts | Deployed experiments |
| GrowthCrew | P1, P2, P3 | Ad campaigns, analytics tracking | Desirability evidence |
| GovernanceCrew | G1, G2, G3 | Experiment validation, brand safety | QA approval |

**HITL**: `approve_campaign_launch`, `approve_spend_increase`, `approve_desirability_gate`

**Exit**: `STRONG_COMMITMENT` (problem_resonance ≥ 0.3, zombie_ratio < 0.7)

### Phase 3: Feasibility Validation

**Purpose**: Assess whether the validated value proposition can be built

**Flow**: `FeasibilityFlow` - Orchestrates technical assessment with downgrade routing

| Crew | Agents | Focus | Output |
|------|--------|-------|--------|
| BuildCrew | F1, F2, F3 | Architecture, cost estimation, constraints | Technical assessment |
| GovernanceCrew | G1, G2, G3 | Security review, feasibility gate | Approval or downgrade |

**HITL**: `approve_feasibility_gate`

**Exit**: `GREEN` signal (or successful downgrade with desirability retest)

### Phase 4: Viability Validation + Final Decision

**Purpose**: Validate business model economics and make final recommendation

**Flow**: `ViabilityFlow` - Orchestrates economics analysis with strategic routing

| Crew | Agents | Focus | Output |
|------|--------|-------|--------|
| FinanceCrew | L1, L2, L3 | CAC, LTV, unit economics, compliance | Viability assessment |
| SynthesisCrew | C1, C2, C3 | Evidence synthesis, pivot/proceed options | Final recommendation |
| GovernanceCrew | G1, G2, G3 | Audit trail, flywheel learning capture | Validated learnings |

**HITL**: `approve_viability_gate`, `request_human_decision`

**Exit**: `PROFITABLE` → VALIDATED | Strategic pivot or KILL

## Inputs & Outputs

**Input**: Founder's business idea description → triggers Phase 0 structured interview.

**Outputs** (structured deliverables per phase):

### Phase 0 (Quick Start)
- `raw_idea`: User's business idea text (1-3 sentences)
- `additional_context`: Optional supplementary context (pitch deck text, notes)
- `project_id`: Created project UUID
- → Phase 1 starts immediately

### Phase 1 (VPC Discovery + Brief Generation)
- **Founder's Brief** (AI-generated from research):
  - The Idea (concept, one-liner)
  - Problem Hypothesis (who, what, alternatives)
  - Customer Hypothesis (segment, characteristics)
  - Solution Hypothesis (approach, features)
  - Key Assumptions (ranked by risk)
  - Success Criteria (founder-defined validation goals)
- QA Report (concept legitimacy validation)
- **Validated Value Proposition Canvas**:
  - Customer Profile (Jobs, Pains, Gains - ranked and evidence-backed)
  - Value Map (Products, Pain Relievers, Gain Creators)
- Test Cards (experiment designs with pass/fail criteria)
- Learning Cards (experiment results with implications)
- Fit Score (≥ 70 for Phase 1 exit)
- Evidence Summary (SAY vs DO triangulation)

### Phase 2 (Desirability)
- Test Artifacts (landing pages, ads, prototypes)
- Evidence Report (desirability signals: `problem_resonance`, `zombie_ratio`)
- Pivot/Proceed Recommendation

### Phase 3 (Feasibility)
- Technical Assessment (complexity scores, constraints)
- Cost Estimates (development, infrastructure, API)
- Downgrade Protocol (if constrained)

### Phase 4 (Viability)
- Viability Model (unit economics: CAC, LTV, margins)
- Business Model Canvas (all 9 blocks validated)
- Final Recommendation (VALIDATED or KILLED)
- Flywheel Entry (learnings for future validations)

## Quick Start

For deployment, API usage, and development commands, see:
- **Deployment Guide**: [docs/deployment/3-crew-deployment.md](../deployment/3-crew-deployment.md)
- **API Contracts**: [reference/api-contracts.md](./reference/api-contracts.md)
- **Current Status**: [09-status.md](./09-status.md)

---

## Related Documentation

- **Ecosystem Overview**: [01-ecosystem.md](./01-ecosystem.md)
- **Organizational Structure**: [02-organization.md](./02-organization.md) (single source for founders/agents)
- **VPD Methodology**: [03-methodology.md](./03-methodology.md) (framework reference, Strategyzer mapping)
- **Phase 0 (Onboarding)**: [04-phase-0-onboarding.md](./04-phase-0-onboarding.md)
- **Phase 1 (VPC Discovery)**: [05-phase-1-vpc-discovery.md](./05-phase-1-vpc-discovery.md)
- **Phase 2 (Desirability)**: [06-phase-2-desirability.md](./06-phase-2-desirability.md)
- **Phase 3 (Feasibility)**: [07-phase-3-feasibility.md](./07-phase-3-feasibility.md)
- **Phase 4 (Viability)**: [08-phase-4-viability.md](./08-phase-4-viability.md)
- **Current Status**: [09-status.md](./09-status.md)
- **API Contracts**: [reference/api-contracts.md](./reference/api-contracts.md)
- **Approval Workflows**: [reference/approval-workflows.md](./reference/approval-workflows.md)

## Support

- CrewAI Docs: https://docs.crewai.com
- CrewAI Dashboard: https://app.crewai.com
- GitHub Issues: https://github.com/chris00walker/startupai-crew/issues

---

**Status**: Multi-phase architecture with VPD framework compliance (Quick Start pivot 2026-01-19)
**Last Updated**: 2026-01-20
