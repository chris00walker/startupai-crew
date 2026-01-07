# Analysis Crew Implementation

> **ARCHIVED (2026-01-07)**: This documents the original 8-crew architecture. The project has migrated to a 3-Crew architecture. Analysis Crew functionality is now part of **Crew 2 (Validation)** in `startupai-crew-validation` repository. See [02-organization.md](../../../master-architecture/02-organization.md) for current architecture.

## Overview (Historical)

The Analysis Crew handled customer and competitor research. Part of Sage's (CSO) commercial side responsibilities.

**Status:** Archived - Migrated to Crew 2

## Agents (2)

### 1. Customer Researcher
Jobs, Pains, Gains analysis using JTBD framework.

**Tools:**
- `TavilySearchTool` - Real-time web research via Tavily API
- `CustomerResearchTool` - Customer segment insights

**Responsibilities:**
- Identify customer jobs-to-be-done
- Map customer pains
- Discover customer gains
- Segment analysis

### 2. Competitor Analyst
Competitive landscape mapping and differentiation.

**Tools:**
- `TavilySearchTool` - Real-time competitor research
- `CompetitorResearchTool` - Competitor positioning analysis
- `MarketResearchTool` - Market size and trends

**Responsibilities:**
- Map competitive landscape
- Identify differentiation opportunities
- Analyze competitor positioning
- Market sizing

## Tasks

| Task | Description | Agent |
|------|-------------|-------|
| `research_customers` | JTBD framework analysis | customer_researcher |
| `identify_customer_segments` | Segment target customers | customer_researcher |
| `map_jobs_pains_gains` | Full VPC customer side | customer_researcher |
| `research_competitors` | Competitive analysis | competitor_analyst |
| `map_positioning` | Positioning strategy | competitor_analyst |
| `analyze_market_size` | TAM/SAM/SOM analysis | competitor_analyst |

## Output

- **Customer Profiles** - Jobs/Pains/Gains per segment
- **Competitor Analysis** - Positioning map with differentiation opportunities
- **Market Analysis** - Size, trends, and opportunity assessment

## Implementation Files

```
src/startupai/crews/analysis/
├── config/
│   ├── agents.yaml           # 2 agent definitions
│   └── tasks.yaml            # 6 task definitions
└── analysis_crew.py          # Crew with 4 tools wired
```

## Test Coverage

```
tests/integration/
├── test_analysis_crew.py     # Customer/competitor research tests
└── test_tavily_integration.py # Tavily API integration tests
```

## Phase Delivered

- **Phase 1A:** Full research workflow with TavilySearchTool for real web research

---
**Spec**: `docs/master-architecture/03-methodology.md`
**Last Updated**: 2026-01-07 (archived)
