# StartupAI Tools

Custom tools extending CrewAI agent capabilities for the validation flow.

## Overview

Tools are organized by crew deployment:

- **Crew 1 (Intake)**: `src/intake_crew/tools/` - This repository
- **Crew 2 (Validation)**: `startupai-crew-validation` repository
- **Crew 3 (Decision)**: `startupai-crew-decision` repository

All tools follow CrewAI's `BaseTool` pattern.

## Crew 1 Tools (This Repo)

Located in `src/intake_crew/tools/`:

| Tool | File | Purpose | Used By |
|------|------|---------|---------|
| **TavilySearchTool** | `web_search.py` | Web research via Tavily API | S2 (Strategist) |
| **CustomerResearchTool** | `web_search.py` | Customer segment insights | S2 (Strategist) |
| **MethodologyCheckTool** | `methodology_check.py` | VPC/BMC structure validation | G1 (QA) |

### Environment Variables (Crew 1)

| Variable | Required For | Description |
|----------|--------------|-------------|
| `OPENAI_API_KEY` | All agents | OpenAI API key |
| `TAVILY_API_KEY` | Web search tools | Tavily API key |

## Tool Categories (All Crews)

### Research Tools
- `TavilySearchTool` - General web search
- `CompetitorResearchTool` - Competitor analysis
- `MarketResearchTool` - Market size and trends
- `CustomerResearchTool` - Customer segment insights

### Validation Tools
- `MethodologyCheckTool` - VPC/BMC structure validation
- `GuardianReviewTool` - Auto-QA for creatives
- `ViabilityApprovalTool` - Unit economics analysis (HITL)

### Financial Tools
- `IndustryBenchmarkTool` - Industry benchmark data
- `UnitEconomicsCalculatorTool` - CAC/LTV calculations
- `BusinessModelClassifier` - Auto-classification of business type
- `UnitEconomicsModels` - 10 model-specific CAC/LTV

### Build Tools
- `LandingPageGeneratorTool` - Landing page generation
- `CodeValidatorTool` - HTML/accessibility validation
- `LandingPageDeploymentTool` - Netlify deployment

### Flywheel Tools
- `FlywheelInsightsTool` - Industry/stage pattern retrieval
- `OutcomeTrackerTool` - Prediction tracking
- `LearningCaptureTool` - Learning capture
- `LearningRetrievalTool` - Learning retrieval

### Privacy & Compliance
- `PrivacyGuardTool` - PII detection, compliance
- `AnonymizerTool` - PII anonymization

### Orchestration
- `InvokeCrewAIAutomationTool` - Crew-to-crew chaining
- `PolicyBandit` - UCB bandit for A/B testing
- `BudgetGuardrails` - Budget enforcement
- `DecisionLogger` - Audit trail persistence

## Tool Development Guidelines

### Creating a New Tool

1. Create file in `src/intake_crew/tools/`
2. Extend `BaseTool` or use `@tool` decorator:

```python
from crewai.tools import BaseTool
from pydantic import Field

class MyTool(BaseTool):
    name: str = "my_tool"
    description: str = "What this tool does and when to use it"

    def _run(self, input_param: str) -> str:
        """Execute the tool."""
        return result
```

3. Export from `__init__.py`
4. Wire to relevant agent in `config/agents.yaml`

### Best Practices

- **Clear descriptions**: Agents select tools based on descriptions
- **Typed inputs/outputs**: Use Pydantic models for complex data
- **Error handling**: Return clear error messages, don't crash
- **Rate limiting**: Respect external API limits
- **Caching**: Cache expensive operations where appropriate

## Related Documents

- [03-methodology.md](../master-architecture/03-methodology.md) - VPD framework
- [reference/flywheel-learning.md](../master-architecture/reference/flywheel-learning.md) - Learning system architecture
- [CLAUDE.md](../../CLAUDE.md) - Environment variable reference

---

**Last Updated**: 2026-01-07
**Status**: Tools distributed across 3 crew repositories
