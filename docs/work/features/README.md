---
purpose: "Feature-specific documentation for crew implementations"
status: "archived"
last_reviewed: "2026-01-07"
---

# Features

> **Note**: This directory contains historical feature documentation from the original 8-crew architecture (Nov 2025). The project has migrated to the Modal canonical architecture (5 flows / 14 crews / 45 agents). The legacy 3-crew setup is deprecated.

## Current Architecture

The Modal canonical architecture is documented in:
- **[02-organization.md](../../master-architecture/02-organization.md)** - 6 founders, 45 agents
- **[09-status.md](../../master-architecture/09-status.md)** - Current implementation status

### Legacy 3 Crews (Deprecated)

| Crew | Repository | Agents | Status |
|------|------------|--------|--------|
| **Crew 1: Intake** | `startupai-crew` | 4 (S1, S2, S3, G1) | ✅ DEPLOYED |
| **Crew 2: Validation** | `startupai-crew-validation` | 12 | ✅ DEPLOYED |
| **Crew 3: Decision** | `startupai-crew-decision` | 3 | ✅ DEPLOYED |

## Archived Feature Docs

The subdirectories here (service-crew/, analysis-crew/, etc.) document the **original 8-crew design**. They're kept for historical reference but no longer reflect the current implementation.

| Directory | Original Purpose | Current Status |
|-----------|-----------------|----------------|
| service-crew/ | Sage intake flow | → Now in Crew 1 |
| analysis-crew/ | Sage research | → Now in Crew 2 |
| governance-crew/ | Guardian oversight | → Split across all crews |
| build-crew/ | Forge MVP generation | → Now in Crew 2 |
| growth-crew/ | Pulse experiments | → Now in Crew 2 |
| finance-crew/ | Ledger viability | → Now in Crew 2 |
| synthesis-crew/ | Compass decisions | → Now in Crew 3 |

## For Current Implementation

See the phase specifications in `master-architecture/`:
- [04-phase-0-onboarding.md](../../master-architecture/04-phase-0-onboarding.md)
- [05-phase-1-vpc-discovery.md](../../master-architecture/05-phase-1-vpc-discovery.md)
- [06-phase-2-desirability.md](../../master-architecture/06-phase-2-desirability.md)
- [07-phase-3-feasibility.md](../../master-architecture/07-phase-3-feasibility.md)
- [08-phase-4-viability.md](../../master-architecture/08-phase-4-viability.md)

---
*Last Updated: 2026-01-07*
*Note: Marked as archived after migration to Modal canonical architecture*
