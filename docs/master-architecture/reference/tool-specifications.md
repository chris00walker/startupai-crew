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
| **LLM-Based** | 8 | Structured output with Pydantic (includes Asset Generation) |
| **TOTAL** | 35 | All tools across 45 agents |

### Asset Generation Tools (NEW)

| Tool | Purpose | Agents |
|------|---------|--------|
| **LandingPageGeneratorTool** | Generate landing page HTML from VPC data | F2 |
| **AdCreativeGeneratorTool** | Generate platform-specific ad copy variants | P1, P2 |

See full specifications below.

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
| **Status** | LLM-Based (Blueprint + Assembly) |
| **Location** | `src/shared/tools/landing_page_generator.py` |
| **Category** | Asset Generation |

**Purpose**: Generate deployable landing page HTML from VPC data using a structured blueprint pattern.

**Architecture**: Assembly, not Generation.

> "The biggest mistake is asking an LLM to write raw HTML from scratch. This leads to 'div soup,' broken layouts, and inconsistent styling."

The tool uses a **Component Registry** of pre-built, responsive Tailwind sections. The LLM doesn't write code—it selects components and generates copy to "hydrate" them.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    BLUEPRINT PATTERN                                 │
├─────────────────────────────────────────────────────────────────────┤
│  1. VPC Input → STRATEGIST → Page structure (which sections)        │
│  2. Structure → COPYWRITER → Compelling copy per section            │
│  3. Copy → ASSEMBLER → Select components, inject copy, fetch assets │
│  4. Assembly → VALIDATOR → Check structure, store blueprint + HTML  │
└─────────────────────────────────────────────────────────────────────┘
```

**Why Blueprint Pattern**:
- **No hallucinated code**: Components are pre-built and tested
- **Re-generation**: Store JSON blueprint in DB, HTML in Storage
- **Editing**: Change one section without re-running full agent chain
- **No "AI look"**: Design tokens enforce consistent spacing, colors, typography
- **Asset resolution**: Keywords → Unsplash API → Verified URLs

---

#### Component Registry

The agent can ONLY use components from this registry. Each component is a pre-built, mobile-responsive Tailwind section.

| Component | Props | Use Case |
|-----------|-------|----------|
| `HeroSection` | headline, subheadline, cta_text, cta_url, image_keyword | Above the fold |
| `PainPoints` | pains: [{icon, title, description}] | Problem agitation |
| `SolutionSection` | headline, description, image_keyword | Bridge to solution |
| `FeatureGrid` | features: [{icon, title, description}] | 3-4 key features |
| `Testimonials` | testimonials: [{quote, name, role, avatar_keyword}] | Social proof |
| `PricingCard` | plan_name, price, features, cta_text | WTP validation |
| `FAQ` | items: [{question, answer}] | Objection handling |
| `CTASection` | headline, subheadline, cta_text, form_enabled | Final conversion |
| `Footer` | company_name, links: [{label, url}] | Navigation |

**Icon Constraints** (Lucide subset to prevent hallucination):
```
Zap, Check, Star, Shield, Clock, Users, TrendingUp, Target,
Heart, Award, Rocket, Globe, Lock, Mail, Phone, MapPin,
ChevronRight, ArrowRight, Sparkles, Lightbulb
```

---

#### Input Schema

```python
class LandingPageInput(BaseModel):
    """Input for landing page generation."""
    # From VPC
    value_proposition: str      # Core VP from Value Map
    target_customer: str        # Customer segment description
    pain_points: list[str]      # Top 3 pains being addressed
    gain_creators: list[str]    # Top 3 gains being created

    # Page configuration
    product_name: str           # Name of product/service
    cta_text: str               # Call-to-action text
    variant_id: str             # A/B test variant identifier

    # Style tokens
    style: str = "modern"       # modern | minimal | bold | warm
    primary_color: str = "#3b82f6"  # Brand primary color

    # Optional sections
    include_testimonials: bool = False
    include_pricing: bool = False
    include_faq: bool = False
```

---

#### Blueprint Schema (Stored in Supabase DB)

The blueprint is the **source of truth** for the page. It enables re-generation without re-running the full agent chain.

```python
class ThemeConfig(BaseModel):
    """Design tokens for consistent styling."""
    primary_color: str          # e.g., "#3b82f6"
    secondary_color: str        # e.g., "#10b981"
    font_family: str            # e.g., "Inter"
    border_radius: str          # e.g., "rounded-lg"
    spacing: str                # e.g., "relaxed" | "compact"

class SectionConfig(BaseModel):
    """Configuration for a single page section."""
    type: str                   # Must match Component Registry
    content: dict               # Props for the component
    order: int                  # Position on page

class ImageAsset(BaseModel):
    """Resolved image asset."""
    keyword: str                # Original keyword for Unsplash
    url: str                    # Resolved Unsplash URL
    alt_text: str               # Accessibility text

class LandingPageBlueprint(BaseModel):
    """
    JSON blueprint stored in Supabase DB.
    Enables editing and re-generation without full agent run.
    """
    # Metadata
    project_id: str
    variant_id: str
    created_at: datetime

    # Design
    theme: ThemeConfig

    # Structure
    sections: list[SectionConfig]

    # Assets (resolved from keywords)
    images: list[ImageAsset]

    # Copy (for easy editing)
    copy: dict[str, str]        # section_id → generated copy
```

---

#### Output Schema

```python
class LandingPageOutput(BaseModel):
    """
    Output from landing page generation.
    Blueprint stored in DB, HTML stored in Storage.
    """
    # The blueprint (for re-generation)
    blueprint: LandingPageBlueprint
    blueprint_stored: bool      # Saved to Supabase DB

    # The HTML (for deployment)
    html: str                   # Complete HTML with Tailwind CDN
    html_url: str               # Supabase Storage URL

    # Validation
    sections_rendered: list[str]
    assets_resolved: bool       # All images fetched successfully
    tracking_enabled: bool      # Analytics JS injected
    form_enabled: bool          # Signup form included
    validation_errors: list[str] = []
```

---

#### Asset Resolution

Images are resolved OUTSIDE the LLM to prevent hallucinated URLs.

```python
class AssetResolver:
    """Resolve image keywords to verified Unsplash URLs."""

    UNSPLASH_ACCESS_KEY = os.environ["UNSPLASH_ACCESS_KEY"]

    def resolve(self, keyword: str) -> ImageAsset:
        """
        Fetch a real image URL from Unsplash API.

        Example: "startup team working" → verified Unsplash URL
        """
        response = httpx.get(
            "https://api.unsplash.com/search/photos",
            params={"query": keyword, "per_page": 1},
            headers={"Authorization": f"Client-ID {self.UNSPLASH_ACCESS_KEY}"}
        )

        if response.status_code == 200 and response.json()["results"]:
            photo = response.json()["results"][0]
            return ImageAsset(
                keyword=keyword,
                url=photo["urls"]["regular"],
                alt_text=photo["alt_description"] or keyword
            )

        # Fallback to placeholder
        return ImageAsset(
            keyword=keyword,
            url=f"https://placehold.co/800x600?text={keyword.replace(' ', '+')}",
            alt_text=keyword
        )
```

---

#### Implementation Flow

```python
class LandingPageGeneratorTool(BaseTool):
    """
    Generate landing page using Blueprint pattern.

    Flow:
    1. Generate page structure (which sections)
    2. Generate copy for each section
    3. Resolve image keywords → Unsplash URLs
    4. Assemble HTML from component templates
    5. Store blueprint in DB, HTML in Storage
    """

    name: str = "landing_page_generator"
    description: str = "Generate a landing page from VPC data using blueprint pattern"
    args_schema: type[BaseModel] = LandingPageInput

    # Component templates (pre-built Tailwind HTML)
    COMPONENTS: dict[str, str] = {
        "HeroSection": load_template("hero.html"),
        "PainPoints": load_template("pain_points.html"),
        "FeatureGrid": load_template("features.html"),
        # ... etc
    }

    def _run(self, **kwargs) -> LandingPageOutput:
        input_data = LandingPageInput(**kwargs)

        # 1. Strategist: Determine page structure
        sections = self._plan_structure(input_data)

        # 2. Copywriter: Generate compelling copy
        copy = self._generate_copy(input_data, sections)

        # 3. Asset Resolver: Keywords → Real URLs
        images = self._resolve_assets(sections)

        # 4. Assembler: Inject copy into templates
        html = self._assemble_html(sections, copy, images, input_data)

        # 5. Create blueprint
        blueprint = LandingPageBlueprint(
            project_id=input_data.project_id,
            variant_id=input_data.variant_id,
            created_at=datetime.now(),
            theme=self._create_theme(input_data),
            sections=sections,
            images=images,
            copy=copy
        )

        # 6. Store blueprint in DB
        self._store_blueprint(blueprint)

        # 7. Store HTML in Storage
        html_url = self._upload_html(html, input_data.variant_id)

        return LandingPageOutput(
            blueprint=blueprint,
            blueprint_stored=True,
            html=html,
            html_url=html_url,
            sections_rendered=[s.type for s in sections],
            assets_resolved=all(img.url for img in images),
            tracking_enabled=True,
            form_enabled=True
        )
```

---

#### Validation Rules

| Rule | Check | Failure Action |
|------|-------|----------------|
| **Component exists** | `section.type in COMPONENTS` | Reject unknown component |
| **Icon valid** | `icon in ALLOWED_ICONS` | Replace with fallback icon |
| **Image resolved** | `image.url is not placeholder` | Log warning, use placeholder |
| **HTML valid** | BeautifulSoup parse succeeds | Raise validation error |
| **CTA exists** | At least one CTASection | Add default CTA |
| **Form configured** | Form action → Supabase | Inject correct endpoint |
| **Tracking injected** | Analytics script present | Inject PostHog/GA |

---

#### Database Schema

```sql
-- Blueprint storage for re-generation
CREATE TABLE landing_page_blueprints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id),
    variant_id TEXT NOT NULL,
    blueprint JSONB NOT NULL,          -- Full LandingPageBlueprint
    html_url TEXT,                      -- Supabase Storage URL
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(project_id, variant_id)
);

-- Enable re-generation queries
CREATE INDEX idx_blueprints_project ON landing_page_blueprints(project_id);
```

---

**Target Agents:** F2 (Frontend Developer)

**Related Tools:**
- `LandingPageDeploymentTool` - Deploys HTML to Supabase Storage
- `CodeValidatorTool` - Validates HTML structure

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

### AdCreativeGeneratorTool

| Attribute | Value |
|-----------|-------|
| **Status** | LLM-Based (NEW) |
| **Location** | `src/shared/tools/ad_creative_generator.py` |
| **Category** | Asset Generation |
| **Cost** | FREE (uses existing LLM) |

**Purpose**: Generate platform-specific ad copy variants from VPC data.

**Approach**: LLM generates ad variants with explicit character constraints. Each platform has different limits that must be validated.

**Platform Constraints**:

| Platform | Headline | Primary Text | Description | CTA |
|----------|----------|--------------|-------------|-----|
| **Meta** | 40 chars | 125 chars | 30 chars | 20 chars |
| **Google** | 30 chars | N/A | 90 chars (×2) | N/A |
| **LinkedIn** | 150 chars | 600 chars | N/A | 20 chars |
| **TikTok** | 100 chars | N/A | N/A | 20 chars |

**Input Schema**:
```python
class AdCreativeInput(BaseModel):
    """Input for ad creative generation."""
    value_proposition: str      # Core VP from VPC
    target_audience: str        # Audience description (demographics, interests)
    pain_points: list[str]      # Top pains being addressed (for hooks)
    platform: str               # meta | google | linkedin | tiktok
    tone: str = "professional"  # professional | casual | urgent | playful
    num_variants: int = 3       # Number of variants to generate (max 5)
    include_emoji: bool = False # Whether to include emoji
    focus: str = "pain"         # pain | gain | feature | social_proof
```

**Output Schema**:
```python
class AdVariant(BaseModel):
    """Single ad variant."""
    variant_id: str             # Unique variant identifier
    headline: str               # Platform-appropriate headline
    primary_text: str           # Main ad copy
    description: str            # Additional description (if platform supports)
    cta: str                    # Call-to-action text
    hook_type: str              # pain | gain | curiosity | social_proof
    character_counts: dict      # Actual counts for validation
    within_limits: bool         # Whether all limits respected

class AdCreativeOutput(BaseModel):
    """Output from ad creative generation."""
    platform: str
    variants: list[AdVariant]
    platform_constraints: dict  # Limits used for validation
    all_valid: bool             # Whether all variants within limits
    recommendations: list[str]  # Suggestions for improvement
```

**Generation Strategy**:
1. Generate 3-5 distinct angles based on VPC data
2. Each variant uses different hook type (pain, gain, curiosity, social proof)
3. Validate all character limits before returning
4. Provide recommendations for variants that exceed limits

**Validation Rules**:
- All character limits must be respected
- No prohibited content (platform policies)
- CTA must match platform options
- Variants must be distinct (not same text repeated)

**Target Agents:** P1 (Ad Creative Agent), P2 (Communications Agent)

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
- [observability-architecture.md](./observability-architecture.md) - Tool observability and debugging
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Modal MCP Example](https://modal.com/docs/examples/mcp_server_stateless)

---

## Change Log

| Date | Change | Rationale |
|------|--------|-----------|
| 2026-01-10 | **Blueprint Pattern** for LandingPageGeneratorTool | Assembly > Generation - prevents "AI slop" |
| 2026-01-10 | Added Component Registry with 9 pre-built sections | Constrained components prevent hallucinated code |
| 2026-01-10 | Added Blueprint schema (JSON stored in DB) | Enables re-generation without full agent chain |
| 2026-01-10 | Added Asset Resolution (Unsplash API) | Prevents hallucinated image URLs |
| 2026-01-10 | Added `landing_page_blueprints` table schema | Dual storage: blueprint in DB, HTML in Storage |
| 2026-01-10 | Added LandingPageGeneratorTool full specification | Asset generation gap - F2 needs tool to create HTML |
| 2026-01-10 | Added AdCreativeGeneratorTool full specification | Asset generation gap - P1/P2 need tool to create ad copy |
| 2026-01-10 | Updated Tool Summary with Asset Generation category | Clear visibility into new tools |
| 2026-01-10 | Added link to observability-architecture.md | Tool observability is architectural concern |
| 2026-01-09 | Adopted MCP-first architecture | Unified tool interface like OpenRouter for LLMs |
| 2026-01-09 | Added Modal MCP server pattern | Stateless HTTP works with serverless |
| 2026-01-09 | Categorized tools: External MCP, Custom MCP, Existing, LLM-based | Clear implementation paths |
| 2026-01-09 | Reduced implementation effort to 56h | MCP abstraction simplifies integration |
