# Analysis Crew Implementation

## Overview

The Analysis Crew handles customer and competitor research. Part of Sage's (CSO) commercial side responsibilities.

## Agents

1. **Customer Researcher** - Jobs, Pains, Gains analysis using JTBD framework
2. **Competitor Analyst** - Competitive landscape mapping, differentiation

## Output

- **Customer Profiles** - Jobs/Pains/Gains per segment
- **Competitor Analysis** - Positioning map with differentiation opportunities

## Implementation Files

```
src/startupai/crews/analysis/
├── config/
│   ├── agents.yaml
│   └── tasks.yaml
└── analysis_crew.py
```

## Tools

- **TavilySearchTool** - Real-time web research via Tavily API
- **CompetitorResearchTool** - Competitor analysis with positioning
- **MarketResearchTool** - Market size and trends
- **CustomerResearchTool** - Customer segment insights

## Status

**Implemented** - Phase 1A complete (TavilySearchTool wired for real web research)

---
**Spec**: `docs/master-architecture/03-validation-spec.md`
**Last Updated**: 2025-11-26
