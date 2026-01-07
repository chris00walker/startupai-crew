# StartupAI Documentation

Welcome to the StartupAI CrewAI Backend documentation. This repository contains the brain of the StartupAI ecosystem - the 3-Crew/19-Agent validation engine deployed on CrewAI AMP.

## Documentation Structure

```
docs/
├── README.md                     # You are here
├── master-architecture/          # Ecosystem source of truth
│   ├── 00-introduction.md        # Quick start and orientation
│   ├── 01-ecosystem.md           # 3-service overview
│   ├── 02-organization.md        # 6 founders, 19 agents (SINGLE SOURCE)
│   ├── 03-methodology.md         # VPD framework reference
│   ├── 04-phase-0-onboarding.md  # Phase 0 specification
│   ├── 05-phase-1-vpc-discovery.md # Phase 1 specification
│   ├── 06-phase-2-desirability.md  # Phase 2 specification
│   ├── 07-phase-3-feasibility.md   # Phase 3 specification
│   ├── 08-phase-4-viability.md     # Phase 4 specification
│   ├── 09-status.md              # Current state assessment
│   └── reference/
│       ├── api-contracts.md      # All API specifications
│       ├── approval-workflows.md # HITL patterns + pivot triggers
│       ├── flywheel-learning.md  # Competitive moat learning system
│       └── database-schemas.md   # SQL schema reference
├── deployment/                   # Deployment guides
│   ├── 3-crew-deployment.md      # AMP deployment guide
│   └── environments.md           # Local/production setup
├── testing/                      # Testing documentation
├── tools/                        # Tool documentation
├── crewai-documentation/         # CrewAI reference docs (34 files)
└── work/                         # Work tracking
    ├── backlog.md                # Hypothesis queue
    ├── phases.md                 # Engineering phases
    ├── cross-repo-blockers.md    # Dependencies and downstream impacts
    └── features/                 # Feature-specific docs
```

## Quick Start

### New to StartupAI?

Read the master-architecture documents in order:

1. **[00-introduction.md](./master-architecture/00-introduction.md)** - Quick start and orientation
2. **[01-ecosystem.md](./master-architecture/01-ecosystem.md)** - How the 3 services connect
3. **[02-organization.md](./master-architecture/02-organization.md)** - The 6 AI Founders and 19 agents
4. **[03-methodology.md](./master-architecture/03-methodology.md)** - VPD framework patterns

### Understanding the Validation Flow?

Read the phase specifications:

1. **[04-phase-0-onboarding.md](./master-architecture/04-phase-0-onboarding.md)** - Founder's Brief capture
2. **[05-phase-1-vpc-discovery.md](./master-architecture/05-phase-1-vpc-discovery.md)** - VPC Discovery
3. **[06-phase-2-desirability.md](./master-architecture/06-phase-2-desirability.md)** - Desirability validation
4. **[07-phase-3-feasibility.md](./master-architecture/07-phase-3-feasibility.md)** - Feasibility validation
5. **[08-phase-4-viability.md](./master-architecture/08-phase-4-viability.md)** - Viability + Decision

### Setting Up Development?

Go directly to **[deployment/environments.md](./deployment/environments.md)** for local and production setup.

### Building a Feature?

1. Check **[09-status.md](./master-architecture/09-status.md)** - What currently works
2. Check **[work/phases.md](./work/phases.md)** - Current engineering phase
3. Review relevant reference docs in `master-architecture/reference/`

## Key Principles

### Single Source of Truth

- **Founders & Agents**: Always defined in `02-organization.md`
- **API Contracts**: Always in `reference/api-contracts.md`
- **Approval Patterns**: Always in `reference/approval-workflows.md`
- **Current Status**: Always in `09-status.md`

Other documents reference these sources - they don't duplicate the content.

### Document Hierarchy

| Level | Documents | Purpose |
|-------|-----------|---------|
| **Conceptual** | 01-ecosystem, 02-organization | What and why |
| **Methodology** | 03-methodology | VPD framework |
| **Specification** | 04-08 phase docs | How to build |
| **Reference** | reference/* | Detailed specifications |
| **Operational** | work/*, deployment/* | Day-to-day work |

## Navigation by Task

| I want to... | Go to... |
|--------------|----------|
| Understand the 3-service architecture | [01-ecosystem.md](./master-architecture/01-ecosystem.md) |
| See all founders and agents | [02-organization.md](./master-architecture/02-organization.md) |
| Learn the VPD methodology | [03-methodology.md](./master-architecture/03-methodology.md) |
| Understand a specific phase | [04-08-phase-*.md](./master-architecture/) |
| Set up my development environment | [deployment/environments.md](./deployment/environments.md) |
| Deploy to CrewAI AMP | [deployment/3-crew-deployment.md](./deployment/3-crew-deployment.md) |
| Integrate with CrewAI API | [reference/api-contracts.md](./master-architecture/reference/api-contracts.md) |
| Implement approval UI | [reference/approval-workflows.md](./master-architecture/reference/approval-workflows.md) |
| Check what's currently working | [09-status.md](./master-architecture/09-status.md) |
| See the work backlog | [work/backlog.md](./work/backlog.md) |
| Check cross-repo blockers | [work/cross-repo-blockers.md](./work/cross-repo-blockers.md) |

## Related Repositories

- **Marketing Site**: `startupai.site` - Lead capture and transparency
  - Docs: `startupai.site/docs/`
  - Work tracking: `startupai.site/docs/work/`
- **Product App**: `app.startupai.site` - Customer portal and delivery
  - Docs: `app.startupai.site/docs/`
  - Work tracking: `app.startupai.site/docs/work/`

This repository (startupai-crew) is **upstream** of both - changes here unblock downstream work.

---
**Last Updated**: 2026-01-07

**Latest Changes**: Updated for 3-Crew architecture (migrated from Flows), new VPD Phase 0-4 structure, standardized documentation.
