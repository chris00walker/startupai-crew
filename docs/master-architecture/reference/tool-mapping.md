---
purpose: Complete agent-to-tool mapping matrix across all phases
status: active
last_reviewed: 2026-01-09
vpd_compliance: true
---

# Agent-to-Tool Mapping

This document defines the complete mapping from agents to their assigned tools, output schemas, and implementation status.

> **Reference Documents:**
> - [tool-specifications.md](./tool-specifications.md) - Detailed tool specifications and schemas
> - [agent-specifications.md](./agent-specifications.md) - Complete agent configurations
> - [agentic-tool-framework.md](./agentic-tool-framework.md) - Tool lifecycle and implementation tiers

> **Architecture (2026-01-09)**: MCP-first approach using Model Context Protocol for unified tool access, deployed on Modal serverless. See [tool-specifications.md](./tool-specifications.md) for full MCP architecture.

---

## Tool Implementation Categories

| Category | Count | Description |
|----------|-------|-------------|
| **EXISTS** | 13 | Implemented and ready to wire |
| **MCP External** | 4 | Use existing MCP servers (Meta Ads, Google Ads, Calendar, Fetch) |
| **MCP Custom** | 10 | Build as FastMCP tools on Modal |
| **LLM-Based** | 8 | Structured LLM output with Pydantic |
| **TOTAL** | 35 | All tools across 43 agents |

> **Observability**: All tools emit observability data. See [observability-architecture.md](./observability-architecture.md) for debugging workflows and database schema.

---

## Complete Mapping Matrix

### Phase 0: Quick Start

> **Architectural Update (2026-01-19)**: Phase 0 was simplified to Quick Start with no AI agents. See [ADR-006](../../adr/006-quick-start-architecture.md).

**Phase 0 Summary:**
- 0 agents (no AI)
- User submits form (raw_idea + hints)
- Phase 1 triggered immediately

---

### Phase 1: VPC Discovery + Brief Generation

> **Note**: Phase 1 now includes BriefGenerationCrew (GV1, S1) which generates the Founder's Brief from research.

#### BriefGenerationCrew (Stage A)

| Agent | Tools | MCP Category | Output Schema |
|-------|-------|--------------|---------------|
| GV1 | GuardianReviewTool, WebSearchTool | EXISTS (1), MCP External (1) | MarketResearchReport |
| S1 | LearningRetrievalTool | EXISTS | FoundersBrief |

#### DiscoveryCrew

| Agent | Tools | MCP Category | Output Schema |
|-------|-------|--------------|---------------|
| E1 | TestCardTool, LearningCardTool, LearningRetrievalTool | LLM-Based (2), EXISTS (1) | ExperimentPlan |
| D1 | InterviewSchedulerTool, TranscriptionTool, InsightExtractorTool, BehaviorPatternTool | MCP External (1), MCP Custom (3) | SAYEvidence |
| D2 | TavilySearchTool, ForumScraperTool, ReviewAnalysisTool, SocialListeningTool, TrendAnalysisTool | EXISTS (1), MCP Custom (4) | DOIndirectEvidence |
| D3 | AnalyticsTool, ABTestTool, AdPlatformTool | MCP Custom (2), MCP External (1) | DODirectEvidence |
| D4 | `[]` (Pure LLM) | N/A | TriangulatedEvidence |

#### CustomerProfileCrew

| Agent | Tools | MCP Category | Output Schema |
|-------|-------|--------------|---------------|
| J1 | TavilySearchTool, ForumScraperTool, ReviewAnalysisTool | EXISTS (1), MCP Custom (2) | JobResearch |
| J2 | `[]` (Pure LLM) | N/A | RankedJobs |
| PAIN_RES | TavilySearchTool, ForumScraperTool, ReviewAnalysisTool | EXISTS (1), MCP Custom (2) | PainResearch |
| PAIN_RANK | `[]` (Pure LLM) | N/A | RankedPains |
| GAIN_RES | TavilySearchTool, ForumScraperTool, ReviewAnalysisTool | EXISTS (1), MCP Custom (2) | GainResearch |
| GAIN_RANK | `[]` (Pure LLM) | N/A | RankedGains |

#### ValueDesignCrew

| Agent | Tools | MCP Category | Output Schema |
|-------|-------|--------------|---------------|
| V1 | CanvasBuilderTool | LLM-Based | SolutionDesign |
| V2 | CanvasBuilderTool | LLM-Based | PainRelieverDesign |
| V3 | CanvasBuilderTool | LLM-Based | GainCreatorDesign |

#### WTPCrew

| Agent | Tools | MCP Category | Output Schema |
|-------|-------|--------------|---------------|
| W1 | ABTestTool, AnalyticsTool | MCP Custom (2) | PricingTestResult |
| W2 | LandingPageGeneratorTool, AnalyticsTool | EXISTS (1), MCP Custom (1) | PaymentTestResult |

#### FitAssessmentCrew

| Agent | Tools | MCP Category | Output Schema |
|-------|-------|--------------|---------------|
| FIT_SCORE | MethodologyCheckTool | EXISTS | FitScoreResult |
| FIT_ROUTE | `[]` (Pure LLM) | N/A | RoutingDecision |

**Phase 1 Summary:**
- 20 agents total (18 VPC + 2 BriefGenerationCrew)
- 8 pure LLM agents (no tools)
- 12 tool-equipped agents
- Tool breakdown: 6 EXISTS, 11 MCP Custom, 3 MCP External, 5 LLM-Based

---

### Phase 2: Desirability

#### BuildCrew

| Agent | Tools | MCP Category | Output Schema |
|-------|-------|--------------|---------------|
| F1 | ComponentLibraryScraperTool | LLM-Based (hardcoded registry) | DesignSpec |
| F2 | LandingPageGeneratorTool, CodeValidatorTool | EXISTS (2) | GeneratedLandingPage |
| F3 | LandingPageDeploymentTool | EXISTS | DeployedAsset |

#### GrowthCrew

| Agent | Tools | MCP Category | Output Schema |
|-------|-------|--------------|---------------|
| P1 | AdCreativeGeneratorTool, AdPlatformTool | LLM-Based (1), MCP External (1) | AdCreatives |
| P2 | AdCreativeGeneratorTool, AdPlatformTool, BudgetGuardrailsTool | LLM-Based (1), MCP External (1), EXISTS (1) | CampaignExecution |
| P3 | AnalyticsTool | MCP Custom | DesirabilityMetrics |

#### GovernanceCrew

| Agent | Tools | MCP Category | Output Schema |
|-------|-------|--------------|---------------|
| G1 | MethodologyCheckTool, GuardianReviewTool | EXISTS (2) | QAReport |
| G2 | PrivacyGuardTool | EXISTS | PIIAuditReport |
| G3 | LearningCaptureTool | EXISTS | AuditTrail |

**Phase 2 Summary:**
- 9 agents total
- 0 pure LLM agents (no tools)
- 9 tool-equipped agents
- Tool breakdown: 8 EXISTS, 2 MCP External, 1 MCP Custom, 3 LLM-Based

---

### Phase 3: Feasibility

#### BuildCrew (Reused)

| Agent | Tools | MCP Category | Output Schema |
|-------|-------|--------------|---------------|
| F1 | ComponentLibraryScraperTool | LLM-Based (hardcoded registry) | FeatureRequirements |
| F2 | CodeValidatorTool | EXISTS | FrontendAssessment |
| F3 | TechStackValidator, APIIntegrationTool, CostEstimatorTool | LLM-Based (3) | FeasibilityAssessment |

#### GovernanceCrew (Reused)

| Agent | Tools | MCP Category | Output Schema |
|-------|-------|--------------|---------------|
| G1 | MethodologyCheckTool, GuardianReviewTool | EXISTS (2) | GateValidation |
| G2 | PrivacyGuardTool | EXISTS | SecurityReview |

**Phase 3 Summary:**
- 5 agents total
- 0 pure LLM agents (no tools)
- 5 tool-equipped agents
- Tool breakdown: 4 EXISTS, 4 LLM-Based

---

### Phase 4: Viability

#### FinanceCrew

| Agent | Tools | MCP Category | Output Schema |
|-------|-------|--------------|---------------|
| L1 | UnitEconomicsModelsTool, AnalyticsTool, CostTrackingTool | EXISTS (1), MCP Custom (1), LLM-Based (1) | ViabilityMetrics |
| L2 | RegulatorySearchTool | MCP External (Fetch) + LLM | RegulatoryConstraints |
| L3 | BusinessModelClassifierTool, LearningCaptureTool, BudgetGuardrailsTool | EXISTS (3) | AssumptionValidation |

#### SynthesisCrew

| Agent | Tools | MCP Category | Output Schema |
|-------|-------|--------------|---------------|
| C1 | StateInspectionTool, SynthesisTool | LLM-Based (2) | EvidenceSynthesis |
| C2 | ViabilityApprovalTool | LLM-Based (HITL) | HITLDecision |
| C3 | LearningCaptureTool, FileWriteTool | EXISTS (2) | DecisionDocumentation |

#### GovernanceCrew (Reused)

| Agent | Tools | MCP Category | Output Schema |
|-------|-------|--------------|---------------|
| G1 | MethodologyCheckTool, GuardianReviewTool | EXISTS (2) | FinalQA |
| G2 | PrivacyGuardTool | EXISTS | PIIScrubbing |
| G3 | LearningCaptureTool, AuditTrailTool | EXISTS (1), LLM-Based (1) | FlywheelEntry |

**Phase 4 Summary:**
- 9 agents total
- 0 pure LLM agents (no tools)
- 9 tool-equipped agents
- Tool breakdown: 9 EXISTS, 1 MCP Custom, 1 MCP External, 5 LLM-Based

---

## Implementation Status Summary

### By Phase (MCP Architecture)

| Phase | Agents | Pure LLM | Tool-Equipped | EXISTS | MCP Custom | MCP External | LLM-Based |
|-------|--------|----------|---------------|--------|------------|--------------|-----------|
| Phase 0 | 4 | 2 | 2 | 2 | 0 | 0 | 2 |
| Phase 1 | 18 | 7 | 11 | 5 | 11 | 2 | 5 |
| Phase 2 | 9 | 0 | 9 | 8 | 1 | 2 | 3 |
| Phase 3 | 5 | 0 | 5 | 4 | 0 | 0 | 4 |
| Phase 4 | 9 | 0 | 9 | 9 | 1 | 1 | 5 |
| **TOTAL** | **45** | **9** | **36** | **28** | **13** | **5** | **19** |

### By Tool Category (MCP Architecture)

| Category | EXISTS | MCP Custom | MCP External | LLM-Based | Implementation |
|----------|--------|------------|--------------|-----------|----------------|
| Research Tools | 2 | 4 | 1 | 0 | FastMCP on Modal |
| Interview Tools | 0 | 2 | 1 | 0 | FastMCP + Calendar MCP |
| Design Tools | 3 | 0 | 0 | 2 | LLM structured output |
| Asset Generation | 0 | 0 | 0 | 2 | Template + LLM (LP, Ads) |
| Growth Tools | 1 | 2 | 2 | 0 | Meta/Google Ads MCP |
| Governance Tools | 5 | 1 | 0 | 0 | EXISTS + Presidio MCP |
| Finance Tools | 4 | 1 | 1 | 0 | EXISTS + Fetch MCP |
| Learning Tools | 2 | 0 | 0 | 6 | LLM structured output |
| **TOTAL** | **17** | **10** | **5** | **10** | |

**Note:** Unique tool count: 35 (13 EXISTS, 10 MCP Custom, 4 MCP External, 8 LLM-Based)

### Agent Type Distribution

| Type | Count | Percentage |
|------|-------|------------|
| Pure LLM (no tools) | 9 | 20% |
| Tool-equipped | 36 | 80% |
| **Total Agents** | 45 | 100% |

---

## Tool-to-Agent Reverse Mapping

### EXISTS Tools (Ready to Wire)

| Tool | Target Agents | Phase(s) | Location |
|------|---------------|----------|----------|
| TavilySearchTool | D2, J1, PAIN_RES, GAIN_RES | 1 | `src/shared/tools/web_search.py` |
| CustomerResearchTool | D1, D2, J1 | 1 | `src/shared/tools/web_search.py` |
| MethodologyCheckTool | G1, FIT_SCORE | 1, 2, 3, 4 | `src/shared/tools/methodology_check.py` |
| LandingPageGeneratorTool | F2, W2 | 1, 2 | `src/crews/desirability/build_crew/tools/` |
| LandingPageDeploymentTool | F3 | 2 | `src/crews/desirability/build_crew/tools/` |
| CodeValidatorTool | F2, F3 | 2, 3 | `src/shared/tools/code_validator.py` |
| GuardianReviewTool | GV1, G1 | 0, 2, 3, 4 | `src/shared/tools/guardian_review.py` |
| PrivacyGuardTool | G2 | 2, 3, 4 | `src/shared/tools/privacy_guard.py` |
| UnitEconomicsModelsTool | L1 | 4 | `src/shared/tools/unit_economics.py` |
| BusinessModelClassifierTool | L1, L3 | 4 | `src/shared/tools/business_model.py` |
| BudgetGuardrailsTool | L3, P2 | 2, 4 | `src/shared/tools/budget_guardrails.py` |
| LearningCaptureTool | E1, D4, L3, C3, G3 | 1, 4 | `src/shared/tools/learning_capture.py` |
| LearningRetrievalTool | O1, E1, S1 | 0, 1 | `src/shared/tools/learning_retrieval.py` |

### MCP External Servers (4)

| Tool | MCP Server | Target Agents | Phase(s) |
|------|------------|---------------|----------|
| AdPlatformTool (Meta) | [pipeboard-co/meta-ads-mcp](https://github.com/pipeboard-co/meta-ads-mcp) | P1, P2, P3, D3 | 1, 2 |
| AdPlatformTool (Google) | [cohnen/google-ads-mcp](https://www.pulsemcp.com/servers/cohnen-google-ads) | P1, P2, P3 | 1, 2 |
| InterviewSchedulerTool | Google Calendar MCP (community) | D1 | 1 |
| WebFetchTool | [Official Fetch Server](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch) | D2, L2 | 1, 4 |

### MCP Custom Tools on Modal (10)

| Tool | MCP Tool Name | Implementation | Target Agents | Phase(s) |
|------|---------------|----------------|---------------|----------|
| ForumScraperTool | `forum_search` | asyncpraw + HuggingFace | D2, J1, PAIN_RES, GAIN_RES | 1 |
| ReviewAnalysisTool | `analyze_reviews` | google-play-scraper | D2, J1, PAIN_RES, GAIN_RES | 1 |
| SocialListeningTool | `social_listen` | DuckDuckGo + HuggingFace | D2 | 1 |
| TrendAnalysisTool | `analyze_trends` | trendspyg | D2 | 1 |
| TranscriptionTool | `transcribe_audio` | faster-whisper | D1 | 1 |
| InsightExtractorTool | `extract_insights` | HuggingFace BART | D1, D4 | 1 |
| BehaviorPatternTool | `identify_patterns` | HuggingFace + sklearn | D2, D3 | 1 |
| ABTestTool | `run_ab_test` | GrowthBook + scipy | P1, P2, W1 | 1, 2 |
| AnalyticsTool | `get_analytics` | Netlify API / PostHog | P3, D3, L1, W1, W2 | 1, 2, 4 |
| AnonymizerTool | `anonymize_data` | Microsoft Presidio | Learning pipeline | All |

### LLM-Based Tools (8)

| Tool | Implementation | Target Agents | Phase(s) |
|------|----------------|---------------|----------|
| TestCardTool | LLM + Supabase | E1 | 1 |
| LearningCardTool | LLM + Supabase | E1, D4 | 1 |
| CanvasBuilderTool | LLM + Supabase | V1, V2, V3 | 1 |
| ConversationTool | LLM structured output | O1 | 0 |
| NoteStructurerTool | LLM structured output | O1 | 0 |
| ViabilityApprovalTool | LLM + Supabase HITL | C2 | 4 |
| LandingPageGeneratorTool | Template + LLM copy | F2, W2 | 1, 2 |
| AdCreativeGeneratorTool | LLM + platform constraints | P1, P2 | 2 |

---

## Implementation Roadmap (MCP Architecture)

### Week 1: Core MCP Server Setup

**Goal**: Deploy FastMCP server on Modal with research tools

| Action | Tool | MCP Tool Name | Target Agents | Effort |
|--------|------|---------------|---------------|--------|
| SETUP | FastMCP server on Modal | - | All | 4h |
| BUILD | ForumScraperTool | `forum_search` | D2, J1, PAIN_RES, GAIN_RES | 3h |
| BUILD | ReviewAnalysisTool | `analyze_reviews` | D2, J1, PAIN_RES, GAIN_RES | 3h |
| BUILD | SocialListeningTool | `social_listen` | D2 | 2h |
| BUILD | TrendAnalysisTool | `analyze_trends` | D2 | 2h |
| DEPLOY | Deploy to Modal | - | - | 1h |

**MCP Server Setup:**
```bash
modal deploy src/mcp_server/app.py
# URL: https://chris00walker--startupai-mcp-tools.modal.run/mcp/
```

**Total**: 15h | **Cost**: ~$2-5 Modal compute

---

### Week 2: Advanced MCP Tools

**Goal**: Audio transcription and insight extraction

| Action | Tool | MCP Tool Name | Target Agents | Effort |
|--------|------|---------------|---------------|--------|
| BUILD | TranscriptionTool | `transcribe_audio` | D1 | 3h |
| BUILD | InsightExtractorTool | `extract_insights` | D1, D4 | 4h |
| BUILD | BehaviorPatternTool | `identify_patterns` | D2, D3 | 4h |
| BUILD | ABTestTool | `run_ab_test` | P1, P2, W1 | 3h |

**Total**: 14h | **Cost**: ~$2-5 Modal compute

---

### Week 3: Analytics & External MCP Servers

**Goal**: Connect analytics and advertising platforms

| Action | Tool | Implementation | Target Agents | Effort |
|--------|------|----------------|---------------|--------|
| BUILD | AnalyticsTool | `get_analytics` MCP tool | P3, D3, L1, W1, W2 | 3h |
| BUILD | AnonymizerTool | `anonymize_data` MCP tool | Learning pipeline | 2h |
| CONNECT | AdPlatformTool (Meta) | meta-ads-mcp server | P1, P2, P3, D3 | 2h |
| CONNECT | AdPlatformTool (Google) | google-ads-mcp server | P1, P2, P3 | 2h |
| CONNECT | InterviewSchedulerTool | Calendar MCP server | D1 | 2h |
| TEST | Integration testing | - | All | 4h |

**External MCP Configuration:**
```json
{
  "mcpServers": {
    "meta-ads": { "command": "uvx", "args": ["meta-ads-mcp"] },
    "google-ads": { "command": "uvx", "args": ["google-ads-mcp"] },
    "startupai": { "url": "https://chris00walker--startupai-mcp-tools.modal.run/mcp/" }
  }
}
```

**Total**: 13h | **Cost**: $0 (external MCP servers)

---

### Week 4: CrewAI Integration & Wiring

**Goal**: Wire all tools to agents

| Action | Tool | Implementation | Target Agents | Effort |
|--------|------|----------------|---------------|--------|
| WIRE | EXISTS tools | Connect 13 existing tools | All phases | 4h |
| WIRE | MCP tools | Add MCP client to agents | All phases | 4h |
| BUILD | LLM-Based tools | 6 structured output tools | O1, E1, V1-V3, C2 | 4h |
| TEST | End-to-end testing | Full pipeline validation | All | 4h |
| DOCS | Documentation | Update agent configs | - | 2h |

**MCP Client in CrewAI:**
```python
from mcp_use import MCPClient

mcp_client = MCPClient(
    url="https://chris00walker--startupai-mcp-tools.modal.run/mcp/",
    transport="streamable-http"
)
mcp_tools = mcp_client.get_tools()
```

**Total**: 18h | **Cost**: $0

---

## Total Implementation Summary

| Week | Focus | Hours | Cost |
|------|-------|-------|------|
| 1 | Core MCP Server | 15h | ~$2-5 |
| 2 | Advanced MCP Tools | 14h | ~$2-5 |
| 3 | External MCP + Analytics | 13h | $0 |
| 4 | CrewAI Integration | 18h | $0 |
| **TOTAL** | | **60h** | **~$5-10** |

**Cost Comparison:**
- MCP-first: ~$5-10 (Modal compute only)
- Alternative (Composio): ~$10-50/month (rate limits)
- Alternative (individual APIs): $0 but 100+ hours integration

---

## Configuration Reference

### MCP Server Environment Variables

| Environment | Variable | Purpose |
|-------------|----------|---------|
| Modal MCP Server | `REDDIT_CLIENT_ID` | Forum search tool |
| Modal MCP Server | `REDDIT_CLIENT_SECRET` | Forum search tool |
| Modal MCP Server | `OPENAI_API_KEY` | LLM-based tools |
| External MCP | `META_ACCESS_TOKEN` | Meta Ads MCP server |
| External MCP | `GOOGLE_ADS_DEVELOPER_TOKEN` | Google Ads MCP server |
| External MCP | `GOOGLE_CALENDAR_CREDENTIALS` | Calendar MCP server |
| Existing Tools | `TAVILY_API_KEY` | TavilySearchTool |
| Existing Tools | `NETLIFY_ACCESS_TOKEN` | LandingPageDeploymentTool |
| Existing Tools | `SUPABASE_URL`, `SUPABASE_KEY` | All Supabase tools |

### Modal MCP Server Dependencies

**File:** `src/mcp_server/app.py`

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

### MCP Client Configuration

**CrewAI agents connect to MCP tools via:**

```python
from mcp_use import MCPClient
from crewai import Agent, LLM

# Connect to StartupAI MCP server
mcp_client = MCPClient(
    url="https://chris00walker--startupai-mcp-tools.modal.run/mcp/",
    transport="streamable-http"
)
mcp_tools = mcp_client.get_tools()

@agent
def observation_agent(self) -> Agent:
    return Agent(
        config=self.agents_config["d2_observation_agent"],
        tools=[
            TavilySearchTool(),   # EXISTS (direct import)
            *mcp_tools,           # MCP Custom (from Modal server)
        ],
        reasoning=True,
        inject_date=True,
        max_iter=25,
        llm=LLM(model="openai/gpt-4o", temperature=0.3),
        verbose=True,
        allow_delegation=False,
    )
```

### External MCP Server Configuration

**File:** `mcp_config.json`

```json
{
  "mcpServers": {
    "meta-ads": {
      "command": "uvx",
      "args": ["meta-ads-mcp"],
      "env": { "META_ACCESS_TOKEN": "${META_ACCESS_TOKEN}" }
    },
    "google-ads": {
      "command": "uvx",
      "args": ["google-ads-mcp"],
      "env": { "GOOGLE_ADS_DEVELOPER_TOKEN": "${GOOGLE_ADS_DEVELOPER_TOKEN}" }
    },
    "calendar": {
      "command": "uvx",
      "args": ["google-calendar-mcp"],
      "env": { "GOOGLE_CALENDAR_CREDENTIALS": "${GOOGLE_CALENDAR_CREDENTIALS}" }
    },
    "startupai-tools": {
      "url": "https://chris00walker--startupai-mcp-tools.modal.run/mcp/",
      "transport": "streamable-http"
    }
  }
}
```

---

## Cost Summary

| Category | Monthly Cost |
|----------|--------------|
| Modal MCP server compute | ~$5-10 |
| External MCP servers | $0 |
| HuggingFace (on Modal) | $0 |
| Free-tier APIs | $0 |
| Existing LLM (GPT-4o) | Already budgeted |
| **TOTAL ADDITIONAL** | **~$5-10** |

---

## Related Documents

- [tool-specifications.md](./tool-specifications.md) - Detailed tool specifications with MCP architecture
- [agent-specifications.md](./agent-specifications.md) - Agent configurations
- [agentic-tool-framework.md](./agentic-tool-framework.md) - Tool lifecycle framework
- [observability-architecture.md](./observability-architecture.md) - Debugging workflows and database schema
- [../02-organization.md](../02-organization.md) - Agent Configuration Standard
- Phase documents: [04](../04-phase-0-onboarding.md), [05](../05-phase-1-vpc-discovery.md), [06](../06-phase-2-desirability.md), [07](../07-phase-3-feasibility.md), [08](../08-phase-4-viability.md)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Modal MCP Example](https://modal.com/docs/examples/mcp_server_stateless)

---

## Change Log

| Date | Change | Rationale |
|------|--------|-----------|
| 2026-01-10 | Added AdCreativeGeneratorTool to P1, P2 | Asset generation for ad campaigns |
| 2026-01-10 | Updated tool counts (33→35) | LandingPageGeneratorTool, AdCreativeGeneratorTool now LLM-Based |
| 2026-01-10 | Added Asset Generation category | Separate from Design tools |
| 2026-01-10 | Added observability-architecture.md reference | All tools now emit observability data |
| 2026-01-09 | Adopted MCP-first architecture | Unified tool interface like OpenRouter for LLMs |
| 2026-01-09 | Categorized tools: EXISTS, MCP External, MCP Custom, LLM-Based | Clear implementation paths |
| 2026-01-09 | Updated mapping tables with MCP Category column | Align with tool-specifications.md |
| 2026-01-09 | Updated roadmap for MCP implementation (60h vs 79h) | MCP abstraction reduces integration effort |
| 2026-01-09 | Added MCP client/server configuration examples | Developer-ready implementation guide |
| 2026-01-09 | Updated cost summary to ~$5-10/month | Modal compute only, no per-call fees |
| 2026-01-09 | Complete restructure with comprehensive mapping matrix | Initial architecture documentation |
