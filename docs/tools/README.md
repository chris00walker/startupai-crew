# CrewAI Tools Documentation

This directory documents the planned custom tools for CrewAI agents.

## Current Status

**Tools are not yet implemented.** The crew currently operates with pure LLM-based agents without custom tools.

## Planned Tools

The following tools will be created in `src/startupai/tools/` when implemented:

### web_search.py (Planned)
**Purpose**: Web search capabilities for research tasks

**Will be used by**:
- Customer Researcher (segment research)
- Competitor Analyst (market research)

---

### analytics.py (Planned)
**Purpose**: Analytics and data processing for experiment results

**Will be used by**:
- Social Media Analyst (engagement metrics)
- Project Manager (evidence aggregation)

---

### report_generator.py (Planned)
**Purpose**: Generate structured reports from analysis results

**Will be used by**:
- QA Agent (quality reports)
- All crews (output formatting)

---

## Tool Development Guidelines

### Creating a New Tool

1. Create `src/startupai/tools/` directory
2. Create a new file for the tool
3. Use the CrewAI tool decorator pattern:

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

4. Register the tool in the relevant agent's configuration

### Tool Best Practices

- **Clear descriptions**: Agents select tools based on descriptions
- **Typed inputs/outputs**: Use type hints for reliability
- **Error handling**: Return clear error messages
- **Rate limiting**: Respect external API limits
- **Caching**: Cache expensive operations where appropriate

### Assigning Tools to Agents

Tools are assigned in `src/startupai/config/agents.yaml`:

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

- [02-organization.md](../master-architecture/02-organization.md) - Which agents will use which tools
- [03-validation-spec.md](../master-architecture/03-validation-spec.md) - How tools fit in the flow

---

**Last Updated**: November 21, 2025
**Status**: Planning phase - tools not yet implemented
