# CrewAI Tools Documentation

This directory documents the custom tools available to CrewAI agents.

## Available Tools

The following tools are defined in `src/startupai/tools/`:

### web_search.py
**Purpose**: Web search capabilities for research tasks

**Used by**:
- Customer Researcher (segment research)
- Competitor Analyst (market research)

**Status**: Planned

---

### analytics.py
**Purpose**: Analytics and data processing for experiment results

**Used by**:
- Social Media Analyst (engagement metrics)
- Project Manager (evidence aggregation)

**Status**: Planned

---

### report_generator.py
**Purpose**: Generate structured reports from analysis results

**Used by**:
- QA Agent (quality reports)
- All crews (output formatting)

**Status**: Planned

---

## Tool Development Guidelines

### Creating a New Tool

1. Create a new file in `src/startupai/tools/`
2. Use the CrewAI tool decorator pattern:

```python
from crewai_tools import tool

@tool("Tool Name")
def tool_function(input_param: str) -> str:
    """
    Tool description for the agent to understand when to use it.

    Args:
        input_param: Description of input

    Returns:
        Description of output
    """
    # Implementation
    return result
```

3. Register the tool in the relevant agent's configuration

### Tool Best Practices

- **Clear descriptions**: Agents select tools based on descriptions
- **Typed inputs/outputs**: Use type hints for reliability
- **Error handling**: Return clear error messages
- **Rate limiting**: Respect external API limits
- **Caching**: Cache expensive operations where appropriate

### Assigning Tools to Agents

Tools are assigned in `config/agents.yaml`:

```yaml
customer_researcher:
  role: Customer Researcher
  tools:
    - web_search
    - analytics
```

## Implementation Priority

1. **report_generator.py** - Needed for all crews to produce structured output
2. **web_search.py** - Needed for Analysis Crew research capabilities
3. **analytics.py** - Needed for Growth Crew experiment analysis

---

## Related Documents

- [02-organization.md](../master-architecture/02-organization.md) - Which agents use which tools
- [03-validation-spec.md](../master-architecture/03-validation-spec.md) - How tools fit in the flow

---
**Last Updated**: 2025-11-21
