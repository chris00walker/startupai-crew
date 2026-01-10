---
purpose: Master tool specification reference for all 33 agent tools
status: active
last_reviewed: 2026-01-09
vpd_compliance: true
---

# Tool Specifications

> **Reference Document**: This is the authoritative specification for all agent tools in the StartupAI validation engine.
>
> **Architecture (2026-01-09)**: MCP-first approach using Model Context Protocol for unified tool access, deployed on Modal serverless.

## Architecture Overview

### MCP-First Design

StartupAI uses the [Model Context Protocol (MCP)](https://modelcontextprotocol.io) as the unified interface for agent tools, following the same pattern as OpenRouter for LLMs.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Modal Serverless                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  StartupAI Custom MCP Server (FastMCP + stateless HTTP)    │    │
│  │  Deployed: modal deploy src/mcp_server/app.py              │    │
│  │                                                             │    │
│  │  Custom Tools:                                              │    │
│  │  - forum_search (asyncpraw + HuggingFace)                  │    │
│  │  - review_analysis (google-play-scraper)                   │    │
│  │  - trend_analysis (trendspyg)                              │    │
│  │  - transcribe_audio (faster-whisper)                       │    │
│  │  - extract_insights (HuggingFace BART)                     │    │
│  └────────────────────────────────────────────────────────────┘    │
│                              │                                       │
│  ┌───────────────────────────┴───────────────────────────────┐     │
│  │              CrewAI Agents (MCP Clients)                   │     │
│  │              Use mcp-use or langchain-mcp                  │     │
│  └───────────────────────────────────────────────────────────┘     │
│                              │                                       │
├──────────────────────────────┼───────────────────────────────────────┤
│  External MCP Servers        │                                       │
│  ┌──────────┐ ┌──────────┐ ┌┴─────────┐ ┌──────────┐ ┌──────────┐  │
│  │ Supabase │ │ Netlify  │ │ Meta Ads │ │Google Ads│ │ Calendar │  │
│  │ (config) │ │ (config) │ │ (remote) │ │ (remote) │ │ (remote) │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Why MCP-First?

| Benefit | Description |
|---------|-------------|
| **Unified Interface** | Single protocol for all tools (like OpenRouter for LLMs) |
| **Modal Compatible** | Stateless HTTP transport works perfectly with serverless |
| **Open Standard** | Linux Foundation project, backed by Anthropic + OpenAI |
| **Free** | No per-call charges, just compute costs |
| **Composable** | Mix external MCP servers with custom tools |

### Tool Categories

| Category | Implementation | Cost |
|----------|----------------|------|
| **External MCP Servers** | Pre-built community servers | FREE |
| **Custom MCP Tools** | FastMCP on Modal | FREE (compute only) |
| **Local Libraries** | Direct Python imports | FREE |

---

## Tool Summary

| Category | Count | Description |
|----------|-------|-------------|
| **EXISTS** | 13 | Implemented and ready to wire |
| **MCP External** | 4 | Use existing MCP servers |
| **MCP Custom** | 10 | Build as FastMCP tools on Modal |
| **Local Library** | 6 | Direct Python imports |
| **TOTAL** | 33 | All tools across 45 agents |

---

## External MCP Servers (4)

These tools use pre-built MCP servers from the community.

### AdPlatformTool (Meta)

| Attribute | Value |
|-----------|-------|
| **Status** | MCP External |
| **MCP Server** | [pipeboard-co/meta-ads-mcp](https://github.com/pipeboard-co/meta-ads-mcp) |
| **Alternative** | [gomarble-ai/facebook-ads-mcp-server](https://github.com/gomarble-ai/facebook-ads-mcp-server) |
| **Cost** | FREE (API access) |

**Capabilities:**
- Create advertising campaigns
- Get performance insights
- Manage ad creatives
- Analyze ad sets

**Configuration:**
```json
{
  "mcpServers": {
    "meta-ads": {
      "command": "uvx",
      "args": ["meta-ads-mcp"],
      "env": {
        "META_ACCESS_TOKEN": "${META_ACCESS_TOKEN}"
      }
    }
  }
}
```

**Target Agents:** P1, P2, P3, D3

---

### AdPlatformTool (Google)

| Attribute | Value |
|-----------|-------|
| **Status** | MCP External |
| **MCP Server** | [cohnen/google-ads-mcp](https://www.pulsemcp.com/servers/cohnen-google-ads) |
| **Cost** | FREE (API access) |

**Capabilities:**
- Query campaign data via GAQL
- Get performance metrics
- Analyze ad groups

**Target Agents:** P1, P2, P3

---

### InterviewSchedulerTool

| Attribute | Value |
|-----------|-------|
| **Status** | MCP External |
| **MCP Server** | Google Calendar MCP (community) |
| **Alternative** | [LangChain Google Calendar](https://python.langchain.com/docs/integrations/tools/google_calendar/) |
| **Cost** | FREE |

**Capabilities:**
- Create calendar events
- Check availability
- Send invites

**Target Agents:** D1

---

### WebFetchTool

| Attribute | Value |
|-----------|-------|
| **Status** | MCP External |
| **MCP Server** | [Official Fetch Server](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch) |
| **Cost** | FREE |

**Capabilities:**
- Fetch web content
- Convert HTML to markdown
- Handle redirects

**Target Agents:** D2, Research agents

---

## Custom MCP Tools on Modal (10)

These tools are built using FastMCP and deployed on Modal as a single stateless MCP server.

### Modal MCP Server Setup

**File:** `src/mcp_server/app.py`

```python
from fastmcp import FastMCP
from fastapi import FastAPI
import modal

# Create MCP server
mcp = FastMCP("StartupAI Research Tools")

# Define tools (see individual specs below)
@mcp.tool()
async def forum_search(query: str, subreddit: str = "startups") -> dict:
    """Search Reddit forums for customer insights."""
    # Implementation using asyncpraw
    ...

@mcp.tool()
async def analyze_reviews(app_id: str, platform: str = "google_play") -> dict:
    """Analyze app store reviews for pain points."""
    # Implementation using google-play-scraper
    ...

# Stateless HTTP transport for Modal
mcp_app = mcp.http_app(transport="streamable-http", stateless_http=True)
fastapi_app = FastAPI(lifespan=mcp_app.router.lifespan_context)
fastapi_app.mount("/mcp", mcp_app)

# Modal deployment
app = modal.App("startupai-mcp-tools")

image = modal.Image.debian_slim().pip_install(
    "fastmcp",
    "asyncpraw",
    "google-play-scraper",
    "app-store-scraper",
    "trendspyg",
    "transformers",
    "torch",
    "faster-whisper",
    "beautifulsoup4",
)

@app.function(image=image)
@modal.asgi_app()
def serve():
    return fastapi_app
```

**Deployment:**
```bash
modal deploy src/mcp_server/app.py
# URL: https://chris00walker--startupai-mcp-tools.modal.run/mcp/
```

---

### ForumScraperTool

| Attribute | Value |
|-----------|-------|
| **Status** | MCP Custom |
| **MCP Tool Name** | `forum_search` |
| **Implementation** | asyncpraw + HuggingFace sentiment |
| **Cost** | FREE |

**MCP Tool Definition:**
```python
@mcp.tool()
async def forum_search(
    query: str,
    subreddits: list[str] = ["startups", "entrepreneur"],
    max_posts: int = 50,
    include_sentiment: bool = True
) -> dict:
    """
    Search Reddit forums for customer insights and pain points.

    Args:
        query: Search keywords
        subreddits: List of subreddits to search
        max_posts: Maximum posts to return
        include_sentiment: Whether to analyze sentiment

    Returns:
        Dict with posts, sentiment distribution, and pain point summary
    """
```

**Dependencies:**
```python
import asyncpraw
from transformers import pipeline

reddit = asyncpraw.Reddit(
    client_id=os.environ["REDDIT_CLIENT_ID"],
    client_secret=os.environ["REDDIT_CLIENT_SECRET"],
    user_agent="StartupAI Research Bot"
)

sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
)
```

**Target Agents:** D2, J1, PAIN_RES, GAIN_RES

---

### ReviewAnalysisTool

| Attribute | Value |
|-----------|-------|
| **Status** | MCP Custom |
| **MCP Tool Name** | `analyze_reviews` |
| **Implementation** | google-play-scraper + app-store-scraper + HuggingFace |
| **Cost** | FREE |

**MCP Tool Definition:**
```python
@mcp.tool()
async def analyze_reviews(
    app_id: str,
    platform: str = "google_play",  # or "app_store"
    max_reviews: int = 100,
    extract_pain_points: bool = True
) -> dict:
    """
    Analyze app store reviews for competitor research.

    Args:
        app_id: App identifier (package name or App Store ID)
        platform: "google_play" or "app_store"
        max_reviews: Maximum reviews to analyze
        extract_pain_points: Whether to extract pain points

    Returns:
        Dict with reviews, ratings, pain points, and sentiment
    """
```

**Dependencies:**
```python
from google_play_scraper import reviews, Sort
from app_store_scraper import AppStore
```

**Target Agents:** D2, J1, PAIN_RES, GAIN_RES

---

### SocialListeningTool

| Attribute | Value |
|-----------|-------|
| **Status** | MCP Custom |
| **MCP Tool Name** | `social_listen` |
| **Implementation** | DuckDuckGo Search + HuggingFace |
| **Cost** | FREE |

**MCP Tool Definition:**
```python
@mcp.tool()
async def social_listen(
    keywords: list[str],
    sources: list[str] = ["web", "news"],
    max_results: int = 20
) -> dict:
    """
    Monitor web and news for social signals about keywords.

    Args:
        keywords: Keywords to monitor
        sources: DuckDuckGo backends ("web", "news")
        max_results: Maximum results per source

    Returns:
        Dict with signals, trending topics, and sentiment summary
    """
```

**Dependencies:**
```python
from duckduckgo_search import DDGS
```

**Target Agents:** D2

---

### TrendAnalysisTool

| Attribute | Value |
|-----------|-------|
| **Status** | MCP Custom |
| **MCP Tool Name** | `analyze_trends` |
| **Implementation** | trendspyg |
| **Cost** | FREE |

**MCP Tool Definition:**
```python
@mcp.tool()
async def analyze_trends(
    keywords: list[str],
    region: str = "US",
    timeframe: str = "today 12-m"
) -> dict:
    """
    Analyze Google Trends data for market momentum.

    Args:
        keywords: Keywords to analyze (max 5)
        region: Geographic region code
        timeframe: Time range for analysis

    Returns:
        Dict with interest over time, related queries, and momentum
    """
```

**Dependencies:**
```python
from trendspyg import TrendReq
```

**Target Agents:** D2

---

### TranscriptionTool

| Attribute | Value |
|-----------|-------|
| **Status** | MCP Custom |
| **MCP Tool Name** | `transcribe_audio` |
| **Implementation** | faster-whisper (local) |
| **Cost** | FREE |

**MCP Tool Definition:**
```python
@mcp.tool()
async def transcribe_audio(
    audio_url: str,
    language: str = "en",
    model_size: str = "base"
) -> dict:
    """
    Transcribe audio file using Whisper.

    Args:
        audio_url: URL or Modal volume path to audio file
        language: Language code
        model_size: Whisper model size ("tiny", "base", "small")

    Returns:
        Dict with full transcript, segments, and duration
    """
```

**Dependencies:**
```python
from faster_whisper import WhisperModel

model = WhisperModel(model_size, device="cpu", compute_type="int8")
```

**Target Agents:** D1

---

### InsightExtractorTool

| Attribute | Value |
|-----------|-------|
| **Status** | MCP Custom |
| **MCP Tool Name** | `extract_insights` |
| **Implementation** | HuggingFace BART + LLM |
| **Cost** | FREE |

**MCP Tool Definition:**
```python
@mcp.tool()
async def extract_insights(
    transcript: str,
    focus: list[str] = ["pain_points", "jobs", "gains"]
) -> dict:
    """
    Extract structured insights from interview transcripts.

    Args:
        transcript: Full interview transcript
        focus: Types of insights to extract

    Returns:
        Dict with categorized insights and quotes
    """
```

**Dependencies:**
```python
from transformers import pipeline

classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)
```

**Target Agents:** D1, D4

---

### BehaviorPatternTool

| Attribute | Value |
|-----------|-------|
| **Status** | MCP Custom |
| **MCP Tool Name** | `identify_patterns` |
| **Implementation** | HuggingFace + scikit-learn |
| **Cost** | FREE |

**MCP Tool Definition:**
```python
@mcp.tool()
async def identify_patterns(
    evidence_items: list[str],
    pattern_type: str = "behavior"
) -> dict:
    """
    Identify behavioral patterns from evidence items.

    Args:
        evidence_items: List of evidence texts
        pattern_type: Type of pattern to identify

    Returns:
        Dict with patterns, frequencies, and implications
    """
```

**Target Agents:** D2, D3

---

### ABTestTool

| Attribute | Value |
|-----------|-------|
| **Status** | MCP Custom |
| **MCP Tool Name** | `run_ab_test` |
| **Implementation** | GrowthBook + scipy |
| **Cost** | FREE |

**MCP Tool Definition:**
```python
@mcp.tool()
async def run_ab_test(
    test_name: str,
    control_data: dict,
    variant_data: dict,
    metric: str
) -> dict:
    """
    Analyze A/B test results for statistical significance.

    Args:
        test_name: Name of the experiment
        control_data: Control group metrics
        variant_data: Variant group metrics
        metric: Primary metric to analyze

    Returns:
        Dict with significance, uplift, and recommendation
    """
```

**Dependencies:**
```python
from scipy import stats
from growthbook import GrowthBook
```

**Target Agents:** P1, P2, W1

---

### AnalyticsTool

| Attribute | Value |
|-----------|-------|
| **Status** | MCP Custom |
| **MCP Tool Name** | `get_analytics` |
| **Implementation** | Netlify API / PostHog |
| **Cost** | FREE |

**MCP Tool Definition:**
```python
@mcp.tool()
async def get_analytics(
    site_id: str,
    date_range: tuple[str, str],
    metrics: list[str] = ["pageviews", "visitors"]
) -> dict:
    """
    Get analytics data for a landing page.

    Args:
        site_id: Netlify site ID
        date_range: Start and end dates
        metrics: Metrics to retrieve

    Returns:
        Dict with metrics, time series, and conversion data
    """
```

**Target Agents:** P3, D3, L1, W1, W2

---

### AnonymizerTool

| Attribute | Value |
|-----------|-------|
| **Status** | MCP Custom |
| **MCP Tool Name** | `anonymize_data` |
| **Implementation** | Microsoft Presidio |
| **Cost** | FREE |

**MCP Tool Definition:**
```python
@mcp.tool()
async def anonymize_data(
    content: str,
    entity_types: list[str] = ["PERSON", "EMAIL", "PHONE"]
) -> dict:
    """
    Anonymize PII for flywheel storage.

    Args:
        content: Text to anonymize
        entity_types: Types of entities to redact

    Returns:
        Dict with anonymized content and replacements log
    """
```

**Dependencies:**
```python
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
```

**Target Agents:** Learning pipeline

---

## Existing Tools (13)

These tools are already implemented and ready to wire.

### TavilySearchTool

| Attribute | Value |
|-----------|-------|
| **Status** | EXISTS |
| **Location** | `src/shared/tools/web_search.py` |
| **MCP Alternative** | Can wrap as MCP tool or use directly |

**Target Agents:** D2, J1, PAIN_RES, GAIN_RES

---

### CustomerResearchTool

| Attribute | Value |
|-----------|-------|
| **Status** | EXISTS |
| **Location** | `src/shared/tools/web_search.py` |

**Target Agents:** D1, D2, J1

---

### MethodologyCheckTool

| Attribute | Value |
|-----------|-------|
| **Status** | EXISTS |
| **Location** | `src/shared/tools/methodology_check.py` |

**Target Agents:** G1, FIT_SCORE

---

### LandingPageGeneratorTool

| Attribute | Value |
|-----------|-------|
| **Status** | EXISTS |
| **Location** | `src/crews/desirability/build_crew/tools/` |

**Target Agents:** F2

---

### LandingPageDeploymentTool

| Attribute | Value |
|-----------|-------|
| **Status** | EXISTS |
| **Location** | `src/crews/desirability/build_crew/tools/` |

**Target Agents:** F3

---

### CodeValidatorTool

| Attribute | Value |
|-----------|-------|
| **Status** | EXISTS |
| **Location** | `src/shared/tools/code_validator.py` |

**Target Agents:** F2

---

### GuardianReviewTool

| Attribute | Value |
|-----------|-------|
| **Status** | EXISTS |
| **Location** | `src/shared/tools/guardian_review.py` |

**Target Agents:** G1, GV1

---

### PrivacyGuardTool

| Attribute | Value |
|-----------|-------|
| **Status** | EXISTS |
| **Location** | `src/shared/tools/privacy_guard.py` |

**Target Agents:** G2

---

### UnitEconomicsModelsTool

| Attribute | Value |
|-----------|-------|
| **Status** | EXISTS |
| **Location** | `src/shared/tools/unit_economics.py` |

**Target Agents:** L1

---

### BusinessModelClassifierTool

| Attribute | Value |
|-----------|-------|
| **Status** | EXISTS |
| **Location** | `src/shared/tools/business_model.py` |

**Target Agents:** L1, L3

---

### BudgetGuardrailsTool

| Attribute | Value |
|-----------|-------|
| **Status** | EXISTS |
| **Location** | `src/shared/tools/budget_guardrails.py` |

**Target Agents:** L3, P2

---

### LearningCaptureTool

| Attribute | Value |
|-----------|-------|
| **Status** | EXISTS |
| **Location** | `src/shared/tools/learning_capture.py` |

**Target Agents:** E1, D4, L3, C3, G3

---

### LearningRetrievalTool

| Attribute | Value |
|-----------|-------|
| **Status** | EXISTS |
| **Location** | `src/shared/tools/learning_retrieval.py` |

**Target Agents:** O1, E1, S1

---

## LLM-Based Tools (6)

These tools use structured LLM output with no external dependencies.

### TestCardTool

| Attribute | Value |
|-----------|-------|
| **Status** | LLM + Supabase |
| **Implementation** | Structured output with Pydantic |
| **Cost** | FREE (uses existing LLM) |

**Target Agents:** E1

---

### LearningCardTool

| Attribute | Value |
|-----------|-------|
| **Status** | LLM + Supabase |
| **Implementation** | Structured output with Pydantic |
| **Cost** | FREE |

**Target Agents:** E1, D4

---

### CanvasBuilderTool

| Attribute | Value |
|-----------|-------|
| **Status** | LLM + Supabase |
| **Implementation** | Structured output for VPC/BMC |
| **Cost** | FREE |

**Target Agents:** V1, V2, V3

---

### ConversationTool

| Attribute | Value |
|-----------|-------|
| **Status** | LLM |
| **Implementation** | Structured conversation prompts |
| **Cost** | FREE |

**Target Agents:** O1

---

### NoteStructurerTool

| Attribute | Value |
|-----------|-------|
| **Status** | LLM |
| **Implementation** | Structured output for VPD format |
| **Cost** | FREE |

**Target Agents:** O1

---

### ViabilityApprovalTool

| Attribute | Value |
|-----------|-------|
| **Status** | LLM + Supabase HITL |
| **Implementation** | Decision framing with approval workflow |
| **Cost** | FREE |

**Target Agents:** C2

---

## Using MCP Tools in CrewAI

### Option 1: mcp-use Library

```python
from mcp_use import MCPClient
from crewai import Agent, Tool

# Connect to StartupAI MCP server on Modal
mcp_client = MCPClient(
    url="https://chris00walker--startupai-mcp-tools.modal.run/mcp/",
    transport="streamable-http"
)

# Get tools from MCP server
mcp_tools = mcp_client.get_tools()

# Use in CrewAI agent
agent = Agent(
    role="Market Researcher",
    goal="Gather customer insights",
    tools=mcp_tools,
    ...
)
```

### Option 2: LangChain MCP Integration

```python
from langchain_mcp import MCPToolkit

toolkit = MCPToolkit(
    server_url="https://chris00walker--startupai-mcp-tools.modal.run/mcp/"
)

# Get LangChain-compatible tools
tools = toolkit.get_tools()
```

### Option 3: Direct MCP Client

```python
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async with streamablehttp_client(
    "https://chris00walker--startupai-mcp-tools.modal.run/mcp/"
) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()

        # List available tools
        tools = await session.list_tools()

        # Call a tool
        result = await session.call_tool(
            "forum_search",
            {"query": "startup validation", "subreddits": ["startups"]}
        )
```

---

## Dependencies

### Modal MCP Server Image

```python
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    # MCP framework
    "fastmcp>=0.1.0",
    "mcp>=1.0.0",

    # Research tools
    "asyncpraw>=7.7.0",
    "google-play-scraper>=1.2.0",
    "app-store-scraper>=0.3.0",
    "trendspyg>=0.1.0",
    "duckduckgo-search>=4.0.0",
    "beautifulsoup4>=4.12.0",

    # NLP tools
    "transformers>=4.35.0",
    "torch>=2.0.0",

    # Audio tools
    "faster-whisper>=0.10.0",

    # Analytics tools
    "growthbook>=1.0.0",
    "scipy>=1.11.0",
    "scikit-learn>=1.3.0",

    # Privacy tools
    "presidio-analyzer>=2.2.0",
    "presidio-anonymizer>=2.2.0",
)
```

### Environment Variables

```env
# Reddit (free - reddit.com/prefs/apps)
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret

# Meta Ads (free - developers.facebook.com)
META_ACCESS_TOKEN=your_access_token

# Google (free - Google Cloud Console)
GOOGLE_ADS_DEVELOPER_TOKEN=your_token
GOOGLE_CALENDAR_CREDENTIALS=path/to/credentials.json

# Existing (already configured)
OPENAI_API_KEY=...
TAVILY_API_KEY=...
SUPABASE_URL=...
SUPABASE_KEY=...
NETLIFY_ACCESS_TOKEN=...
```

---

## Implementation Roadmap

### Week 1: Core MCP Server

| Task | Effort | Status |
|------|--------|--------|
| Create `src/mcp_server/app.py` with FastMCP | 4h | TODO |
| Implement `forum_search` tool | 3h | TODO |
| Implement `analyze_reviews` tool | 3h | TODO |
| Implement `social_listen` tool | 2h | TODO |
| Implement `analyze_trends` tool | 2h | TODO |
| Deploy to Modal | 1h | TODO |
| **Week 1 Total** | **15h** | |

### Week 2: Advanced Tools

| Task | Effort | Status |
|------|--------|--------|
| Implement `transcribe_audio` tool | 3h | TODO |
| Implement `extract_insights` tool | 4h | TODO |
| Implement `identify_patterns` tool | 4h | TODO |
| Implement `run_ab_test` tool | 3h | TODO |
| **Week 2 Total** | **14h** | |

### Week 3: Analytics & Privacy

| Task | Effort | Status |
|------|--------|--------|
| Implement `get_analytics` tool | 3h | TODO |
| Implement `anonymize_data` tool | 2h | TODO |
| Connect external MCP servers (Meta, Google Ads) | 4h | TODO |
| Integration testing | 4h | TODO |
| **Week 3 Total** | **13h** | |

### Week 4: CrewAI Integration

| Task | Effort | Status |
|------|--------|--------|
| Add MCP client to CrewAI agents | 4h | TODO |
| Wire existing tools to agents | 4h | TODO |
| End-to-end testing | 4h | TODO |
| Documentation | 2h | TODO |
| **Week 4 Total** | **14h** | |

**Total Implementation:** 56 hours

---

## Cost Summary

| Category | Monthly Cost |
|----------|--------------|
| Modal compute (MCP server) | ~$5-10 (serverless) |
| External MCP servers | $0 |
| HuggingFace (local inference) | $0 |
| Open source libraries | $0 |
| Existing LLM (GPT-4o) | Already budgeted |
| **TOTAL ADDITIONAL** | **~$5-10** |

---

## Related Documents

- [tool-mapping.md](./tool-mapping.md) - Agent-to-tool mapping matrix
- [agent-specifications.md](./agent-specifications.md) - Agent configurations
- [agentic-tool-framework.md](./agentic-tool-framework.md) - Tool lifecycle framework
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Modal MCP Example](https://modal.com/docs/examples/mcp_server_stateless)

---

## Change Log

| Date | Change | Rationale |
|------|--------|-----------|
| 2026-01-09 | Adopted MCP-first architecture | Unified tool interface like OpenRouter for LLMs |
| 2026-01-09 | Added Modal MCP server pattern | Stateless HTTP works with serverless |
| 2026-01-09 | Categorized tools: External MCP, Custom MCP, Existing, LLM-based | Clear implementation paths |
| 2026-01-09 | Reduced implementation effort to 56h | MCP abstraction simplifies integration |
