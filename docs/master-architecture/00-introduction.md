---
purpose: Repository introduction, architecture overview, and quick start
status: active
last_reviewed: 2026-01-07
vpd_compliance: true
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

### 3. Flows + Crews Architecture
- **Crews**: Autonomous agent teams that collaborate on tasks
- **Flows**: Event-driven orchestration that coordinates crews
- **Routers**: Implement governance gates with conditional routing
- **Structured State**: Pydantic models carry data through the system

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

### Phase 0: Onboarding (Founder's Brief)

**Purpose**: Capture business hypothesis and create Founder's Brief

| Crew | Focus | Output |
|------|-------|--------|
| Interview Crew (Sage) | 7-area discovery interview | Structured interview responses |
| QA Crew (Guardian) | Legitimacy screening, intent verification | Validation report |
| Brief Compilation (Sage) | Synthesize hypothesis | **Founder's Brief** |

**HITL**: `approve_founders_brief` - Founder approves brief before Phase 1

### Phase 1: VPC Discovery (Customer Profile + Value Map)

**Purpose**: Discover customer reality and design value using VPD framework

| Crew | Focus | Output |
|------|-------|--------|
| Discovery Crew (Sage) | Customer interviews, observation, CTA tests | Validated Customer Profile |
| Value Design Crew (Forge) | Products, Pain Relievers, Gain Creators | Value Map |
| Pricing Crew (Ledger) | Willingness-to-pay experiments | WTP validation |
| Fit Assessment (Compass) | Problem-Solution Fit scoring | **Validated VPC** (fit ≥ 70) |

**HITL**: `approve_experiment_plan`, `approve_pricing_test`, `approve_vpc_completion`

### Phase 2: Desirability Validation

**Purpose**: Test whether customers actually want the value proposition

| Crew | Focus | Output |
|------|-------|--------|
| Build Crew (Forge) | Landing pages, testable artifacts | Deployed experiments |
| Growth Crew (Pulse) | Ad campaigns, analytics tracking | Desirability evidence |
| Governance (Guardian) | Experiment validation, brand safety | QA approval |

**HITL**: `approve_campaign_launch`, `approve_spend_increase`, `approve_desirability_gate`

**Exit**: `STRONG_COMMITMENT` (problem_resonance ≥ 0.3, zombie_ratio < 0.7)

### Phase 3: Feasibility Validation

**Purpose**: Assess whether the validated value proposition can be built

| Crew | Focus | Output |
|------|-------|--------|
| Build Crew (Forge) | Architecture, cost estimation, constraints | Technical assessment |
| Governance (Guardian) | Security review, feasibility gate | Approval or downgrade |

**HITL**: `approve_feasibility_gate`

**Exit**: `GREEN` signal (or successful downgrade with desirability retest)

### Phase 4: Viability Validation + Final Decision

**Purpose**: Validate business model economics and make final recommendation

| Crew | Focus | Output |
|------|-------|--------|
| Finance Crew (Ledger) | CAC, LTV, unit economics, compliance | Viability assessment |
| Synthesis Crew (Compass) | Evidence synthesis, pivot/proceed options | Final recommendation |
| Governance (Guardian) | Audit trail, flywheel learning capture | Validated learnings |

**HITL**: `approve_viability_gate`, `request_human_decision`

**Exit**: `PROFITABLE` → VALIDATED | Strategic pivot or KILL

## Inputs & Outputs

**Input**: Founder's business idea description → triggers Phase 0 structured interview.

**Outputs** (structured deliverables per phase):

### Phase 0 (Onboarding)
- **Founder's Brief** (structured hypothesis capture):
  - The Idea (concept, one-liner)
  - Problem Hypothesis (who, what, alternatives)
  - Customer Hypothesis (segment, characteristics)
  - Solution Hypothesis (approach, features)
  - Key Assumptions (ranked by risk)
  - Success Criteria (founder-defined validation goals)
- QA Report (concept legitimacy + intent verification)

### Phase 1 (VPC Discovery)
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

**Status**: Multi-phase architecture with VPD framework compliance
**Last Updated**: 2026-01-07
