---
purpose: "Feature-specific documentation for crew and flow implementations"
status: "active"
last_reviewed: "2025-11-26"
---

# Features

This directory contains feature-specific documentation for crew and flow implementations.

Each feature should have its own folder with:
- Scope definition
- Test plan
- Implementation checklist
- Delivery notes

## Structure

```
features/
├── README.md (this file)
├── service-crew/       # Sage - intake & brief (Phase 1A)
├── analysis-crew/      # Sage - customer/competitor research (Phase 1A)
├── build-crew/         # Forge - MVP generation & deployment (Phase 1B)
├── growth-crew/        # Pulse - experiments & growth (stub)
├── finance-crew/       # Ledger - unit economics & viability (Phase 2B)
├── synthesis-crew/     # Compass - pivot/proceed decisions (Phase 1)
└── governance-crew/    # Guardian - QA, compliance, flywheel (Phase 2A-2D)
```

## Crew Status

| Crew | Owner | Status | Phase |
|------|-------|--------|-------|
| Service | Sage (CSO) | Implemented | 1A |
| Analysis | Sage (CSO) | Implemented | 1A |
| Build | Forge (CTO) | Implemented | 1B |
| Growth | Pulse (CGO) | Stub (ad APIs deferred) | - |
| Finance | Ledger (CFO) | Implemented | 2B |
| Synthesis | Compass (CPO) | Implemented | 1 |
| Governance | Guardian (CGoO) | Implemented | 2A-2D |

## Ecosystem Context

- **Master Architecture**: `../master-architecture/`
- **API Contracts**: `../master-architecture/reference/api-contracts.md`
- **Product App Features**: `app.startupai.site/docs/work/features/`
- **Marketing Site Features**: `startupai.site/docs/work/features/`
