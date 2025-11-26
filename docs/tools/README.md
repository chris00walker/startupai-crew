# StartupAI Tools

Custom tools extending CrewAI agent capabilities for the validation flow.

## Overview

The tools package (`src/startupai/tools/`) provides specialized capabilities for research, analysis, MVP generation, and flywheel learning. All tools follow CrewAI's `BaseTool` pattern.

## Implemented Tools

| Tool | File | Purpose | Used By |
|------|------|---------|---------|
| **TavilySearchTool** | `web_search.py` | Web research via Tavily API | Analysis Crew |
| **CompetitorResearchTool** | `web_search.py` | Competitor analysis and positioning | Analysis Crew |
| **MarketResearchTool** | `web_search.py` | Market size and trends research | Analysis Crew |
| **CustomerResearchTool** | `web_search.py` | Customer segment insights | Analysis Crew |
| **IndustryBenchmarkTool** | `financial_data.py` | Industry benchmark data | Finance Crew |
| **UnitEconomicsCalculatorTool** | `financial_data.py` | CAC/LTV calculations | Finance Crew |
| **LandingPageGeneratorTool** | `landing_page.py` | A/B test landing page generation | Build Crew |
| **CodeValidatorTool** | `code_validator.py` | HTML/accessibility/security validation | Build Crew |
| **LearningCaptureTool** | `learning_capture.py` | Flywheel learning capture | All Crews |
| **LearningRetrievalTool** | `learning_retrieval.py` | Flywheel learning retrieval | All Crews |
| **AnonymizerTool** | `anonymizer.py` | PII anonymization for learnings | Learning Pipeline |

---

## Tool Categories

### Web Research Tools (`web_search.py`)

Powered by Tavily API for real-time web research.

```python
from startupai.tools import TavilySearchTool, web_search

# As CrewAI tool
tool = TavilySearchTool()

# As standalone function
results = web_search("B2B SaaS market trends 2024")
```

**Tools**:
- `TavilySearchTool` - General web search
- `CompetitorResearchTool` - Competitor analysis with positioning insights
- `MarketResearchTool` - Market size, trends, and dynamics
- `CustomerResearchTool` - Customer segment research

**Environment**: Requires `TAVILY_API_KEY`

---

### Financial Data Tools (`financial_data.py`)

Industry benchmarks and unit economics calculations.

```python
from startupai.tools import IndustryBenchmarkTool, get_industry_benchmarks

# As CrewAI tool
tool = IndustryBenchmarkTool()

# As standalone function
benchmarks = get_industry_benchmarks("B2B SaaS", "healthcare")
```

**Tools**:
- `IndustryBenchmarkTool` - Retrieves industry benchmarks from domain_expertise table
- `UnitEconomicsCalculatorTool` - Calculates CAC, LTV, LTV/CAC ratio

**Database**: Queries `domain_expertise` table (20 rows seeded with industry data)

---

### MVP Generation Tools

#### Landing Page Generator (`landing_page.py`)

Generates Tailwind CSS landing page variants for A/B testing.

```python
from startupai.tools import LandingPageGeneratorTool, generate_landing_pages

# As CrewAI tool
tool = LandingPageGeneratorTool()

# As standalone function
variants = generate_landing_pages(
    headline="Transform Your Business",
    subheadline="AI-powered validation",
    cta_text="Get Started",
    style="modern"  # modern, corporate, startup, minimal
)
```

**Output**: Complete HTML with Tailwind CSS, ready for deployment

---

#### Code Validator (`code_validator.py`)

Validates generated HTML for deployment readiness.

```python
from startupai.tools import CodeValidatorTool, validate_html, is_deployment_ready

# As CrewAI tool
tool = CodeValidatorTool()

# As standalone function
result = validate_html(html_content)
ready = is_deployment_ready(result)
```

**Checks**:
- HTML syntax validation
- WCAG 2.1 AA accessibility (alt text, form labels, color contrast)
- Security vulnerabilities (XSS, unsafe URLs)
- SEO requirements (title, meta description)
- Best practices (DOCTYPE, charset, viewport)

---

### Flywheel Learning Tools

#### Learning Capture (`learning_capture.py`)

Captures anonymized learnings after validation phases.

```python
from startupai.tools import LearningCaptureTool

tool = LearningCaptureTool()
result = tool._run(
    learning_type="pattern",  # pattern, outcome, domain
    title="High zombie ratio in B2B requires enterprise positioning",
    description="When problem_resonance > 0.7 but zombie_ratio > 0.8...",
    context={"industry": "B2B SaaS", "stage": "seed"},
    founder="compass",
    phase="desirability",
    tags=["zombie_ratio", "value_pivot"],
    confidence_score=0.92
)
```

---

#### Learning Retrieval (`learning_retrieval.py`)

Retrieves relevant learnings for agent context.

```python
from startupai.tools import LearningRetrievalTool

tool = LearningRetrievalTool()
learnings = tool._run(
    query="Desirability patterns for B2B SaaS",
    founder="pulse",
    learning_type="pattern",
    industry="B2B SaaS",
    limit=5
)
```

**Database**: Uses pgvector similarity search on `learnings` table

---

#### Anonymizer (`anonymizer.py`)

Strips PII before storing learnings.

```python
from startupai.tools import AnonymizerTool, anonymize_text

# As CrewAI tool
tool = AnonymizerTool()

# As standalone function
clean_text = anonymize_text(
    "John Smith at Acme Corp raised $5M",
    entities={"John Smith": "founder", "Acme Corp": "company"}
)
# Output: "the founder at the company raised early-stage funding"
```

---

## Tool Development Guidelines

### Creating a New Tool

1. Create file in `src/startupai/tools/`
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
4. Wire to relevant crew/agent

### Best Practices

- **Clear descriptions**: Agents select tools based on descriptions
- **Typed inputs/outputs**: Use Pydantic models for complex data
- **Error handling**: Return clear error messages, don't crash
- **Rate limiting**: Respect external API limits
- **Caching**: Cache expensive operations where appropriate
- **Testing**: Add tests in `tests/tools/`

---

## Crew → Tool Mapping

| Crew | Tools |
|------|-------|
| **Analysis Crew** | TavilySearchTool, CompetitorResearchTool, MarketResearchTool, CustomerResearchTool |
| **Finance Crew** | IndustryBenchmarkTool, UnitEconomicsCalculatorTool |
| **Build Crew** | LandingPageGeneratorTool, CodeValidatorTool |
| **All Crews** | LearningCaptureTool, LearningRetrievalTool |

---

## Environment Variables

| Variable | Required For | Description |
|----------|--------------|-------------|
| `TAVILY_API_KEY` | Web search tools | Tavily API key |
| `SUPABASE_URL` | Learning tools | Supabase project URL |
| `SUPABASE_KEY` | Learning tools | Supabase service role key |
| `OPENAI_API_KEY` | Learning tools | For embedding generation |

---

## Related Documents

- [`../master-architecture/03-validation-spec.md`](../master-architecture/03-validation-spec.md) - Authoritative technical spec
- [`../master-architecture/reference/flywheel-learning.md`](../master-architecture/reference/flywheel-learning.md) - Learning system architecture

---

**Last Updated**: 2025-11-26
**Status**: 11 tools implemented and deployed
