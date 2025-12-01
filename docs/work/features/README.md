---
purpose: "Feature-specific documentation for crew and flow implementations"
status: "active"
last_reviewed: "2025-12-01"
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

| Crew | Owner | Status | Completed | Notes |
|------|-------|--------|-----------|-------|
| Service | Sage (CSO) | ✅ Complete | Nov 2025 | 3 agents, intake & brief capture |
| Analysis | Sage (CSO) | ✅ Complete | Nov 2025 | 2 agents, TavilySearchTool for real research |
| Build | Forge (CTO) | ✅ Complete | Nov 2025 | 3 agents, LandingPageGeneratorTool + Netlify deploy |
| Growth | Pulse (CGO) | ✅ Complete | Nov 2025 | 3 agents (ad platform APIs deferred) |
| Finance | Ledger (CFO) | ✅ Complete | Nov 2025 | 2 agents, UnitEconomicsCalculatorTool |
| Synthesis | Compass (CPO) | ✅ Complete | Nov 2025 | 1 agent, pivot decision logic |
| Governance | Guardian (CGoO) | ✅ Complete | Nov 2025 | 3 agents, 8 tools (HITL, Flywheel, Privacy) |

*Last verified: 2025-12-01*

## Ecosystem Context

- **Master Architecture**: `../master-architecture/`
- **API Contracts**: `../master-architecture/reference/api-contracts.md`
- **Product App Features**: `app.startupai.site/docs/work/features/`
- **Marketing Site Features**: `startupai.site/docs/work/features/`
