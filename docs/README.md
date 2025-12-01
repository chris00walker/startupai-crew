# StartupAI Documentation

Welcome to the StartupAI CrewAI Backend documentation. This repository contains the brain of the StartupAI ecosystem - the 8-crew/18-agent validation engine.

## Documentation Structure

```
docs/
├── README.md                     # You are here
├── environments.md               # Local/production setup
├── innovation-physics.md         # Non-linear routing logic (Innovation Physics)
├── master-architecture/          # Ecosystem source of truth
│   ├── 00-introduction.md        # This repo's architecture & quick start
│   ├── 01-ecosystem.md           # 3-service overview
│   ├── 02-organization.md        # 6 founders, 18 agents (SINGLE SOURCE)
│   ├── 03-validation-spec.md     # Core validation flow + Innovation Physics
│   ├── 04-status.md              # Current state assessment
│   └── reference/
│       ├── api-contracts.md      # All API specifications
│       ├── approval-workflows.md # HITL patterns + pivot triggers
│       ├── flywheel-learning.md  # Competitive moat learning system
│       ├── marketing-integration.md   # Marketing site AI
│       ├── product-artifacts.md       # Smart canvas architecture
│       └── database-schemas.md        # SQL schema reference
├── tools/                        # Tool documentation
└── work/                         # Work tracking
    ├── backlog.md                # Hypothesis queue
    ├── phases.md                 # Engineering phases
    └── roadmap.md                # Quarterly roadmap
```

## Quick Start

### New to StartupAI?

Read the master-architecture documents in order:

1. **[00-introduction.md](./master-architecture/00-introduction.md)** - This repository's architecture and commands
2. **[01-ecosystem.md](./master-architecture/01-ecosystem.md)** - How the 3 services connect
3. **[02-organization.md](./master-architecture/02-organization.md)** - The 6 AI Founders and 18 agents
4. **[03-validation-spec.md](./master-architecture/03-validation-spec.md)** - How to build the validation flow

### Setting Up Development?

Go directly to **[environments.md](./environments.md)** for local and production setup.

### Building a Feature?

1. Check **[04-status.md](./master-architecture/04-status.md)** - What currently works
2. Check **[work/phases.md](./work/phases.md)** - Current engineering phase
3. Review relevant reference docs in `master-architecture/reference/`

## Key Principles

### Single Source of Truth

- **Founders & Agents**: Always defined in `02-organization.md`
- **API Contracts**: Always in `reference/api-contracts.md`
- **Approval Patterns**: Always in `reference/approval-workflows.md`

Other documents reference these sources - they don't duplicate the content.

### Document Hierarchy

| Level | Documents | Purpose |
|-------|-----------|---------|
| **Conceptual** | 01-ecosystem, 02-organization | What and why |
| **Implementation** | 03-validation-spec, 00-introduction | How to build |
| **Reference** | reference/* | Detailed specifications |
| **Operational** | environments, work/* | Day-to-day work |

## Navigation by Task

| I want to... | Go to... |
|--------------|----------|
| Understand the 3-service architecture | [01-ecosystem.md](./master-architecture/01-ecosystem.md) |
| See all founders and agents | [02-organization.md](./master-architecture/02-organization.md) |
| Build a crew or flow | [03-validation-spec.md](./master-architecture/03-validation-spec.md) |
| Understand router and pivot logic | [innovation-physics.md](./innovation-physics.md) |
| Set up my development environment | [environments.md](./environments.md) |
| Integrate with CrewAI API | [reference/api-contracts.md](./master-architecture/reference/api-contracts.md) |
| Implement approval UI | [reference/approval-workflows.md](./master-architecture/reference/approval-workflows.md) |
| Check what's currently working | [04-status.md](./master-architecture/04-status.md) |
| See the work backlog | [work/backlog.md](./work/backlog.md) |

## Related Repositories

- **Marketing Site**: `startupai.site` - Lead capture and transparency
  - Docs: `startupai.site/docs/`
  - Work tracking: `startupai.site/docs/work/`
- **Product App**: `app.startupai.site` - Customer portal and delivery
  - Docs: `app.startupai.site/docs/`
  - Work tracking: `app.startupai.site/docs/work/`

This repository (startupai-crew) is **upstream** of both - changes here unblock downstream work.

---
**Last Updated**: 2025-12-01

**Latest Changes**: README updates across ecosystem, standardized crew documentation.
