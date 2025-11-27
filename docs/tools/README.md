# StartupAI Tools

Custom tools extending CrewAI agent capabilities for the validation flow.

## Overview

The tools package (`src/startupai/tools/`) provides specialized capabilities for research, analysis, MVP generation, HITL workflows, flywheel learning, and privacy protection. All tools follow CrewAI's `BaseTool` pattern.

## Implemented Tools (18 Total)

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
| **LandingPageDeploymentTool** | `landing_page_deploy.py` | Netlify deployment integration | Build Crew |
| **GuardianReviewTool** | `guardian_review.py` | Auto-QA for creatives (HITL) | Governance Crew |
| **MethodologyCheckTool** | `methodology_check.py` | VPC/BMC structure validation | Governance Crew |
| **ViabilityApprovalTool** | `viability_approval.py` | Unit economics analysis (HITL) | Finance Crew |
| **FlywheelInsightsTool** | `flywheel_insights.py` | Industry/stage pattern retrieval | Governance Crew |
| **OutcomeTrackerTool** | `flywheel_insights.py` | Prediction tracking with feedback | Governance Crew |
| **PrivacyGuardTool** | `privacy_guard.py` | PII detection, compliance, sanitization | Governance Crew |
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

#### Landing Page Deployment (`landing_page_deploy.py`)

Deploys landing pages to Netlify for live A/B testing.

```python
from startupai.tools import LandingPageDeploymentTool, deploy_landing_page

# As CrewAI tool
tool = LandingPageDeploymentTool()

# As standalone function
result = deploy_landing_page(
    html_content="<html>...</html>",
    site_name="my-startup-test",
    netlify_token="..."
)
# Returns: DeploymentResult with url, deploy_id, etc.
```

**Environment**: Requires `NETLIFY_TOKEN`

---

### HITL (Human-in-the-Loop) Tools

#### Guardian Review (`guardian_review.py`)

Auto-QA for landing pages and ad creatives before deployment.

```python
from startupai.tools import GuardianReviewTool, review_landing_page, ReviewDecision

# As CrewAI tool
tool = GuardianReviewTool()

# As standalone function
result = review_landing_page(
    artifact_id="lp_1",
    html_content="<html>...",
    business_context={"business_idea": "..."}
)
# result.decision: AUTO_APPROVED, NEEDS_HUMAN_REVIEW, REJECTED
```

**Checks**:
- Compliance issues (medical claims, financial promises)
- Brand safety (profanity, controversial content)
- Accessibility requirements
- Legal disclaimers

---

#### Methodology Check (`methodology_check.py`)

Validates VPC (Value Proposition Canvas) and BMC (Business Model Canvas) structure.

```python
from startupai.tools import MethodologyCheckTool, check_vpc, check_bmc

# As CrewAI tool
tool = MethodologyCheckTool()

# As standalone function
result = check_vpc(vpc_data)  # Returns MethodologyCheckResult
result = check_bmc(bmc_data)
```

**Validates**:
- Required sections present
- Cross-section consistency
- Completeness scoring

---

#### Viability Approval (`viability_approval.py`)

Analyzes unit economics and generates pivot recommendations for human decision.

```python
from startupai.tools import ViabilityApprovalTool, analyze_viability

# As CrewAI tool
tool = ViabilityApprovalTool()

# As standalone function
result = analyze_viability(
    cac=150.0,
    ltv=300.0,
    gross_margin=0.70,
    monthly_churn=0.05
)
# result.status: PROFITABLE, MARGINAL, UNDERWATER
# result.pivot_options: List of recommended pivots
```

**Output**: `ViabilityApprovalResult` with status, confidence, pivot recommendations

---

### Flywheel Learning Tools

#### Flywheel Insights (`flywheel_insights.py`)

Retrieves industry/stage patterns and cross-validation learnings.

```python
from startupai.tools import FlywheelInsightsTool, get_flywheel_insights

# As CrewAI tool
tool = FlywheelInsightsTool()

# As standalone function
insights = get_flywheel_insights(
    industry="saas_b2b",
    stage="problem_validated"
)
```

**Features**:
- Industry-specific patterns (SaaS B2B, marketplace, fintech, etc.)
- Stage-specific guidance (ideation → PMF → scaling)
- Cross-validation context retrieval

---

#### Outcome Tracker (`flywheel_insights.py`)

Tracks predictions and outcomes for model improvement.

```python
from startupai.tools import OutcomeTrackerTool, track_prediction, record_prediction_outcome

# As CrewAI tool
tool = OutcomeTrackerTool()

# As standalone function
prediction_id = track_prediction(
    validation_id="val_123",
    prediction_type="desirability_outcome",
    predicted_outcome="proceed",
    confidence=0.85
)

# Later, record actual outcome
record_prediction_outcome(
    prediction_id=prediction_id,
    actual_outcome="proceed",
    variance_notes="Matched prediction"
)
```

**Database**: Uses `predictions` table (pgvector) for outcome tracking

---

### Privacy & Compliance Tools

#### Privacy Guard (`privacy_guard.py`)

PII detection, compliance checking, and content sanitization.

```python
from startupai.tools import PrivacyGuardTool, check_privacy, sanitize_for_flywheel

# As CrewAI tool
tool = PrivacyGuardTool()

# Check content for privacy violations
result = check_privacy("Contact john@example.com for details")
# result.is_safe: False
# result.violations: [PrivacyViolation(type="email", ...)]

# Sanitize for Flywheel storage
clean = sanitize_for_flywheel("Email: john@test.com")
# Returns: "Email: [EMAIL]"
```

**Features**:
- PII detection (email, phone, SSN, credit cards, API keys)
- Compliance framework checks (GDPR, CCPA, HIPAA)
- Sensitivity classification (PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED)
- Cross-validation privacy boundaries
- Audit trail generation

---

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
- **Testing**: Add tests in `tests/integration/`

---

## Crew → Tool Mapping

| Crew | Tools |
|------|-------|
| **Analysis Crew** | TavilySearchTool, CompetitorResearchTool, MarketResearchTool, CustomerResearchTool |
| **Finance Crew** | IndustryBenchmarkTool, UnitEconomicsCalculatorTool, ViabilityApprovalTool |
| **Build Crew** | LandingPageGeneratorTool, CodeValidatorTool, LandingPageDeploymentTool |
| **Governance Crew** | GuardianReviewTool, MethodologyCheckTool, FlywheelInsightsTool, OutcomeTrackerTool, PrivacyGuardTool, AnonymizerTool |
| **All Crews** | LearningCaptureTool, LearningRetrievalTool |

---

## Environment Variables

| Variable | Required For | Description |
|----------|--------------|-------------|
| `TAVILY_API_KEY` | Web search tools | Tavily API key |
| `SUPABASE_URL` | Learning/Flywheel tools | Supabase project URL |
| `SUPABASE_KEY` | Learning/Flywheel tools | Supabase service role key |
| `OPENAI_API_KEY` | Learning tools | For embedding generation |
| `NETLIFY_TOKEN` | Deployment tool | Netlify API token |

---

## Related Documents

- [`../master-architecture/03-validation-spec.md`](../master-architecture/03-validation-spec.md) - Authoritative technical spec
- [`../master-architecture/reference/flywheel-learning.md`](../master-architecture/reference/flywheel-learning.md) - Learning system architecture

---

**Last Updated**: 2025-11-26
**Status**: 18 tools implemented and deployed (Phase 2D complete)
