# Master Architecture

This directory contains the **ecosystem source of truth** for StartupAI's multi-phase crew architecture.

> **VPD Framework**: StartupAI implements the Value Proposition Design (VPD) framework by Osterwalder/Pigneur. Phase 0-1 specification provides the authoritative VPD implementation.

## Reading Order

Start here and progress through the numbered documents:

| Order | Document | Purpose | When to Read |
|-------|----------|---------|--------------|
| 0 | [00-introduction.md](./00-introduction.md) | This repo's architecture & quick start | First - get oriented |
| 1 | [01-ecosystem.md](./01-ecosystem.md) | 3-service architecture overview | Second - understand the system |
| 2 | [02-organization.md](./02-organization.md) | 6 founders, agents, VPD terminology | Third - understand the team |
| 3 | **[05-phase-0-1-specification.md](./05-phase-0-1-specification.md)** | **Phase 0-1 VPD implementation** | **Before implementing Phase 0/1** |
| 4 | [03-validation-spec.md](./03-validation-spec.md) | Phase 2+ validation flow | When building validation crews |
| 4.5 | [../innovation-physics.md](../innovation-physics.md) | Non-linear routing logic | When understanding pivot decisions |
| 5 | [04-status.md](./04-status.md) | Current state and blockers | Before starting any work |

## Reference Documents

Detailed specifications extracted for standalone reference:

| Document | Purpose |
|----------|---------|
| [reference/flywheel-learning.md](./reference/flywheel-learning.md) | **Competitive moat** - shared anonymized learning system |
| [reference/amp-configuration.md](./reference/amp-configuration.md) | CrewAI AMP platform config and capabilities |
| [reference/api-contracts.md](./reference/api-contracts.md) | All API endpoints, webhooks, payloads |
| [reference/approval-workflows.md](./reference/approval-workflows.md) | Human-in-the-loop patterns |
| [reference/marketing-integration.md](./reference/marketing-integration.md) | Marketing site AI chat and live data |
| [reference/product-artifacts.md](./reference/product-artifacts.md) | Smart canvas architecture |
| [reference/database-schemas.md](./reference/database-schemas.md) | SQL schema definitions |

## Quick Navigation

### By Topic

- **Architecture**: 01-ecosystem.md
- **AI Founders**: 02-organization.md (canonical source)
- **Phase 0-1 Agents**: 02-organization.md (O1, G1, G2, S1 + 18 Phase 1 agents)
- **VPD Framework**: 05-phase-0-1-specification.md (Value Proposition Design implementation)
- **Phase 0 (Onboarding)**: 05-phase-0-1-specification.md (Founder's Brief capture)
- **Phase 1 (VPC Discovery)**: 05-phase-0-1-specification.md (Customer Profile + Value Map)
- **Phase 2+ Validation**: 03-validation-spec.md (Desirability → Feasibility → Viability)
- **Innovation Physics**: ../innovation-physics.md (non-linear routing)
- **Flywheel Learning**: reference/flywheel-learning.md (competitive moat)
- **AMP Platform**: reference/amp-configuration.md
- **API Integration**: reference/api-contracts.md
- **HITL Approvals**: reference/approval-workflows.md
- **What Works Today**: 04-status.md

### By Task

- **"I'm new, where do I start?"** → Read 00 → 01 → 02 → 05 → 03 → 04 in order
- **"I'm implementing Phase 0 or 1"** → 05-phase-0-1-specification.md (VPD framework)
- **"What is VPD/Value Proposition Design?"** → 05-phase-0-1-specification.md
- **"I need to integrate with CrewAI API"** → reference/api-contracts.md
- **"I'm implementing approval UI"** → reference/approval-workflows.md
- **"I want to understand the learning system"** → reference/flywheel-learning.md
- **"I'm configuring AMP deployment"** → reference/amp-configuration.md
- **"What's the current status?"** → 04-status.md
- **"Who owns what?"** → 02-organization.md
- **"How do routers and pivots work?"** → ../innovation-physics.md
- **"Why did the flow route to pivot?"** → 03-validation-spec.md (Innovation Physics section)

## Cross-References

- Work tracking: `../work/` (backlog, phases, roadmap)
- Environment setup: `../environments.md`
- Other repos reference this directory as source of truth

## Downstream Repositories

These repositories consume this architecture:

- **Product App**: `app.startupai.site`
  - Docs: `app.startupai.site/docs/`
  - Blockers: `app.startupai.site/docs/work/cross-repo-blockers.md`
- **Marketing Site**: `startupai.site`
  - Docs: `startupai.site/docs/`
  - Blockers: `startupai.site/docs/work/cross-repo-blockers.md`

---
**Last Updated**: 2026-01-05

**Latest Changes**: VPD framework alignment, Phase 0-1 specification integration, updated navigation.
