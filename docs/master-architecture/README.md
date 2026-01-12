# Master Architecture

This directory contains the **ecosystem source of truth** for StartupAI's multi-phase crew architecture.

> **Architecture Migration**: Migrated from the legacy CrewAI managed platform to Modal serverless. See [ADR-002](../adr/002-modal-serverless-migration.md) and [09-status.md](./09-status.md) for current status.

> **VPD Framework**: StartupAI implements the Value Proposition Design (VPD) framework by Osterwalder/Pigneur. The phase specifications provide authoritative VPD implementation patterns.

---

## Reading Order

Start here and progress through the numbered documents:

| Order | Document | Purpose | When to Read |
|-------|----------|---------|--------------|
| 0 | [00-introduction.md](./00-introduction.md) | Repository architecture & quick start | First - get oriented |
| 1 | [01-ecosystem.md](./01-ecosystem.md) | 3-service architecture overview | Second - understand the system |
| 2 | [02-organization.md](./02-organization.md) | 6 founders, agents, VPD terminology | Third - understand the team |
| 3 | [03-methodology.md](./03-methodology.md) | **VPD framework, evidence hierarchy, templates** | Before any implementation |
| 4 | [04-phase-0-onboarding.md](./04-phase-0-onboarding.md) | Phase 0: Founder's Brief capture | When implementing onboarding |
| 5 | [05-phase-1-vpc-discovery.md](./05-phase-1-vpc-discovery.md) | Phase 1: VPC Discovery (Customer Profile + Value Map) | When implementing discovery |
| 6 | [06-phase-2-desirability.md](./06-phase-2-desirability.md) | Phase 2: Desirability validation | When implementing desirability |
| 7 | [07-phase-3-feasibility.md](./07-phase-3-feasibility.md) | Phase 3: Feasibility validation | When implementing feasibility |
| 8 | [08-phase-4-viability.md](./08-phase-4-viability.md) | Phase 4: Viability + Final Decision | When implementing viability |
| 9 | [09-status.md](./09-status.md) | Current state and blockers | Before starting any work |

---

## Phase Overview

```
                         StartupAI Validation Funnel
                         ═══════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 0: ONBOARDING                                                        │
│  ────────────────────                                                       │
│  • Input: Raw founder idea                                                  │
│  • Agents: O1, GV1, GV2, S1 (4 agents)                                     │
│  • Output: Founder's Brief                                                  │
│  • HITL: approve_founders_brief                                             │
│  • Purpose: Capture hypothesis (NOT validate)                               │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 1: VPC DISCOVERY                                                     │
│  ──────────────────────                                                     │
│  • Input: Founder's Brief                                                   │
│  • Agents: E1, D1-D4, J1-J2, PAIN_*, GAIN_*, V1-V3, W1-W2, FIT_* (18 agents)│
│  • Output: Validated VPC (fit ≥ 70)                                        │
│  • HITL: approve_experiment_plan, approve_pricing_test, approve_vpc_compl  │
│  • Purpose: Discover customer reality, design value                         │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 2: DESIRABILITY                                                      │
│  ─────────────────────                                                      │
│  • Input: Validated VPC                                                     │
│  • Agents: F1-F3, P1-P3, G1-G3 (9 agents)                                  │
│  • Output: STRONG_COMMITMENT signal                                         │
│  • HITL: approve_campaign_launch, approve_spend_increase, approve_desr_gate│
│  • Purpose: Test "Do customers want it?" with real behavior                 │
│  • Pivots: SEGMENT_PIVOT, VALUE_PIVOT                                       │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 3: FEASIBILITY                                                       │
│  ────────────────────                                                       │
│  • Input: Desirability evidence                                             │
│  • Agents: F1-F3, G1 (4 agents)                                            │
│  • Output: GREEN feasibility signal                                         │
│  • HITL: approve_feasibility_gate                                           │
│  • Purpose: Test "Can we build it?" with technical assessment              │
│  • Pivots: FEATURE_PIVOT (downgrade), KILL                                  │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 4: VIABILITY                                                         │
│  ──────────────────                                                         │
│  • Input: Feasibility artifact                                              │
│  • Agents: L1-L3, C1-C3, G1-G3 (9 agents)                                  │
│  • Output: PROFITABLE signal OR human decision                              │
│  • HITL: approve_viability_gate, request_human_decision                     │
│  • Purpose: Test "Can we make money?" with unit economics                   │
│  • Pivots: PRICE_PIVOT, COST_PIVOT, MODEL_PIVOT, KILL                       │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  TERMINAL: VALIDATED or KILLED                                              │
│  ────────────────────────────────                                           │
│  • Evidence trail documented                                                │
│  • Learnings captured to flywheel                                           │
│  • Final recommendation delivered                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Reference Documents

Detailed specifications extracted for standalone reference:

| Document | Purpose |
|----------|---------|
| [reference/flywheel-learning.md](./reference/flywheel-learning.md) | **Competitive moat** - shared anonymized learning system |
| [reference/api-contracts.md](./reference/api-contracts.md) | All API endpoints, webhooks, payloads |
| [reference/approval-workflows.md](./reference/approval-workflows.md) | Human-in-the-loop patterns |
| [reference/marketing-integration.md](./reference/marketing-integration.md) | Marketing site AI chat and live data |
| [reference/product-artifacts.md](./reference/product-artifacts.md) | Smart canvas architecture |
| [reference/database-schemas.md](./reference/database-schemas.md) | SQL schema definitions |
| [reference/amp-configuration.md](./reference/amp-configuration.md) | ~~Legacy platform config~~ (DEPRECATED - see ADR-002) |

### Architecture Decision Records

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-001](../adr/001-flow-to-crew-migration.md) | Flow to 3-Crew Migration | Superseded |
| [ADR-002](../adr/002-modal-serverless-migration.md) | Modal Serverless Migration | **Current** |

---

## Quick Navigation

### By Phase

- **Phase 0 (Onboarding)**: [04-phase-0-onboarding.md](./04-phase-0-onboarding.md) - Founder's Brief capture
- **Phase 1 (VPC Discovery)**: [05-phase-1-vpc-discovery.md](./05-phase-1-vpc-discovery.md) - Customer Profile + Value Map
- **Phase 2 (Desirability)**: [06-phase-2-desirability.md](./06-phase-2-desirability.md) - "Do they want it?"
- **Phase 3 (Feasibility)**: [07-phase-3-feasibility.md](./07-phase-3-feasibility.md) - "Can we build it?"
- **Phase 4 (Viability)**: [08-phase-4-viability.md](./08-phase-4-viability.md) - "Can we make money?"

### By Topic

- **Architecture**: [01-ecosystem.md](./01-ecosystem.md)
- **AI Founders**: [02-organization.md](./02-organization.md) (canonical source)
- **VPD Methodology**: [03-methodology.md](./03-methodology.md) (Test Cards, Learning Cards, SAY vs DO)
- **Innovation Physics**: [concepts/innovation-physics.md](../concepts/innovation-physics.md) (non-linear routing)
- **Flywheel Learning**: [reference/flywheel-learning.md](./reference/flywheel-learning.md) (competitive moat)
- **Modal Deployment**: [ADR-002](../adr/002-modal-serverless-migration.md) (current target)
- **Legacy platform**: [reference/amp-configuration.md](./reference/amp-configuration.md) (DEPRECATED)
- **API Integration**: [reference/api-contracts.md](./reference/api-contracts.md)
- **HITL Approvals**: [reference/approval-workflows.md](./reference/approval-workflows.md)
- **Current Status**: [09-status.md](./09-status.md)

### By Task

- **"I'm new, where do I start?"** → Read 00 → 01 → 02 → 03 → (phase you're working on) → 09
- **"What is VPD/Value Proposition Design?"** → [03-methodology.md](./03-methodology.md)
- **"I'm implementing a specific phase"** → Go to that phase document (04-08)
- **"I need to integrate with CrewAI API"** → [reference/api-contracts.md](./reference/api-contracts.md)
- **"I'm implementing approval UI"** → [reference/approval-workflows.md](./reference/approval-workflows.md)
- **"I want to understand the learning system"** → [reference/flywheel-learning.md](./reference/flywheel-learning.md)
- **"How do routers and pivots work?"** → [03-methodology.md](./03-methodology.md) (Innovation Physics section)
- **"What's the current status?"** → [09-status.md](./09-status.md)
- **"Who owns what?"** → [02-organization.md](./02-organization.md)

---

## Archive

Previous versions of specifications preserved for reference:

| Document | Notes |
|----------|-------|
| [archive/03-validation-spec.md](./archive/03-validation-spec.md) | Original monolithic validation spec (Phase 2-4 combined) |
| [archive/05-phase-0-1-specification.md](./archive/05-phase-0-1-specification.md) | Original Phase 0+1 combined spec |

---

## Downstream Repositories

These repositories consume this architecture:

- **Product App**: `app.startupai.site`
  - Docs: `app.startupai.site/docs/`
  - Blockers: `app.startupai.site/docs/work/cross-repo-blockers.md`
- **Marketing Site**: `startupai.site`
  - Docs: `startupai.site/docs/`
  - Blockers: `startupai.site/docs/work/cross-repo-blockers.md`

---

## Cross-References

- Work tracking: `../work/` (backlog, phases, roadmap)
- Environment setup: `../deployment/environments.md`
- Conceptual thinking: `../concepts/innovation-physics.md`

---

**Last Updated**: 2026-01-08

**Latest Changes**:
- Modal serverless migration proposed (ADR-002)
- Legacy CrewAI deployment deprecated
- Added Architecture Decision Records section
- Fixed Phase 1 agent IDs (PAIN_*, GAIN_*, FIT_*)
- Previous: Restructured to separate phase documents (04-08)
