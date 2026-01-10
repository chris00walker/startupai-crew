---
purpose: Strategic framework for agentic tool architecture and autonomous capabilities
status: active
last_reviewed: 2026-01-09
vpd_compliance: true
---

# Agentic Tool Framework

This document defines the strategic framework for enabling autonomous agent capabilities in the StartupAI validation engine. It covers tool lifecycle design, agent configuration patterns, and the path to full agentic autonomy.

> **Context**: The StartupAI validation engine uses CrewAI agents that need to perform real-world actions—researching markets, generating landing pages, deploying artifacts, and analyzing results. This framework ensures agents have the tools they need to operate autonomously within defined guardrails.

---

## Guiding Principles

### 1. Lifecycle Coverage

Every agent capability should cover the **complete lifecycle** of its domain:

```
RESEARCH → DESIGN → BUILD → DEPLOY → MEASURE → LEARN
```

A landing page agent that can generate HTML but not deploy it is only 50% useful. A research agent that can search but not synthesize is incomplete.

### 2. Evidence Over Hallucination

Agents must produce **evidence-based outputs**, not LLM hallucinations:

| Output Type | Without Tools | With Tools |
|-------------|---------------|------------|
| Market Research | Plausible but invented data | Real search results with citations |
| Competitor Analysis | Generic observations | Actual competitor URLs and features |
| Landing Pages | Code that might work | Deployed URLs with analytics |
| Unit Economics | Made-up numbers | Calculations based on real CAC/LTV |

### 3. Fail-Safe by Default

Tools that take real-world actions (deploy, spend money, send emails) must have:
- **HITL checkpoints** before execution
- **Budget guardrails** with hard limits
- **Rollback capabilities** for reversibility
- **Audit trails** for accountability

### 4. Composability

Tools should be composable—an agent should be able to use multiple tools in sequence to accomplish complex tasks:

```python
# Agent workflow: Research → Generate → Validate → Deploy
results = TavilySearchTool.run("competitor landing pages SaaS")
html = LandingPageGeneratorTool.run(brief=results, template="saas-hero")
validation = CodeValidatorTool.run(html)
if validation.passed:
    url = NetlifyDeployTool.run(html)
```

---

## Tool Lifecycle Categories

### Category 1: Research & Planning

**Purpose**: Gather real-world information before making decisions.

| Tool | Source | Description | Target Agents |
|------|--------|-------------|---------------|
| `TavilySearchTool` | crewai_tools | Web search with relevance scoring | D2, J1, PAIN_RES, GAIN_RES |
| `SerperDevTool` | crewai_tools | Google search API wrapper | Alternative to Tavily |
| `WebsiteSearchTool` | crewai_tools | Crawl specific websites | D2 for competitor analysis |
| `CustomerResearchTool` | Custom | JTBD-focused multi-search | S2, J1 |
| `SocialListeningTool` | Custom | Monitor social platforms | D2 |
| `ReviewAnalysisTool` | Custom | Analyze product reviews | D2, PAIN_RES |
| `TrendAnalysisTool` | Custom | Google Trends integration | D2 |

**Agent Configuration Pattern**:
```python
@agent
def observation_agent(self) -> Agent:
    return Agent(
        config=self.agents_config["d2_observation_agent"],
        tools=[
            TavilySearchTool(),
            WebsiteSearchTool(),
        ],
        reasoning=True,      # Enable planning for multi-step research
        inject_date=True,    # Research must be time-aware
        max_iter=30,         # Allow more iterations for thorough research
        verbose=True,
        llm=LLM(model="openai/gpt-4o", temperature=0.3),  # Lower temp for factual
    )
```

---

### Category 2: Design & Asset Generation

**Purpose**: Create visual and content assets for validation experiments.

| Tool | Source | Description | Target Agents |
|------|--------|-------------|---------------|
| `DalleTool` | crewai_tools | Generate images via DALL-E | P1 (Ad Creative) |
| `FileReadTool` | crewai_tools | Read brand guidelines, templates | F1 (UX Designer) |
| `LandingPageGeneratorTool` | Custom | Generate landing page HTML/React | F2 (Frontend Dev) |
| `AdCreativeGeneratorTool` | Custom | Generate ad copy + image prompts | P1 (Ad Creative) |

**Agent Configuration Pattern**:
```python
@agent
def ad_creative_agent(self) -> Agent:
    return Agent(
        config=self.agents_config["p1_ad_creative"],
        tools=[
            DalleTool(),
            FileReadTool(directory="./brand-assets"),
        ],
        reasoning=True,      # Plan creative strategy before generating
        inject_date=True,
        max_iter=20,
        verbose=True,
        llm=LLM(model="openai/gpt-4o", temperature=0.8),  # Higher temp for creativity
    )
```

**DALL-E Integration Notes**:
- Requires `OPENAI_API_KEY` with DALL-E access
- Image generation adds ~$0.04-0.08 per image (DALL-E 3)
- Consider caching generated images in Supabase Storage
- Brand guidelines should constrain style (colors, typography)

---

### Category 3: Code Generation & Validation

**Purpose**: Write, validate, and test code artifacts.

| Tool | Source | Description | Target Agents |
|------|--------|-------------|---------------|
| `CodeInterpreterTool` | crewai_tools | Execute Python code in sandbox | F2, F3 |
| `FileWriteTool` | Custom | Write files to project directory | F2 (Frontend Dev) |
| `DirectoryReadTool` | crewai_tools | Read project structure | F2, F3 |
| `CodeValidatorTool` | Custom | Lint, type-check, validate code | F3 (Backend Dev) |

**Agent Configuration Pattern**:
```python
@agent
def frontend_developer(self) -> Agent:
    return Agent(
        config=self.agents_config["f2_frontend_developer"],
        tools=[
            CodeInterpreterTool(),
            FileWriteTool(base_path="./generated"),
            DirectoryReadTool(directory="./templates"),
        ],
        allow_code_execution=True,
        code_execution_mode="safe",  # Docker sandbox
        reasoning=True,
        inject_date=True,
        max_iter=25,
        max_execution_time=300,  # 5 min timeout for code gen
        verbose=True,
        llm=LLM(model="openai/gpt-4o", temperature=0.2),  # Low temp for code
    )
```

**FileWriteTool Implementation**:
```python
from crewai.tools import tool

@tool("Write File")
def file_write_tool(filepath: str, content: str) -> str:
    """
    Write content to a file. Use for generating HTML, CSS, TSX files.

    Args:
        filepath: Relative path from project root (e.g., "pages/landing.tsx")
        content: File content to write

    Returns:
        Confirmation message with full path
    """
    import os
    from pathlib import Path

    base_path = Path(os.environ.get("GENERATED_FILES_PATH", "./generated"))
    full_path = base_path / filepath

    # Security: Prevent path traversal
    if ".." in filepath:
        return "Error: Path traversal not allowed"

    # Create parent directories
    full_path.parent.mkdir(parents=True, exist_ok=True)

    # Write file
    full_path.write_text(content)

    return f"Successfully wrote {len(content)} bytes to {full_path}"
```

---

### Category 4: Deployment & Infrastructure

**Purpose**: Deploy artifacts to production environments.

| Tool | Source | Description | Target Agents |
|------|--------|-------------|---------------|
| `ComposioToolSet` | Composio | Pre-built GitHub, Netlify, Vercel integrations | F3 |
| `NetlifyDeployTool` | Custom | Deploy to Netlify via API | F3 (Backend Dev) |
| `GitHubPushTool` | Composio | Push code to repository | F3 |
| `ShellTool` | crewai_tools | Run terminal commands (use with caution) | F3 |

**Composio vs Custom Decision Matrix**:

| Factor | Composio | Custom |
|--------|----------|--------|
| Setup Time | Minutes | Hours |
| Authentication | Handled | Manual OAuth/API key |
| Maintenance | Third-party | Self-maintained |
| Cost | $29/month (Team) | Free (dev time) |
| Flexibility | Pre-defined actions | Full control |
| Error Handling | Built-in | Manual |

**Recommendation**: Use **Composio** for Netlify/Vercel/GitHub integrations. The time saved justifies the cost, and authentication is handled securely.

**Composio Integration Pattern**:
```python
from composio_crewai import ComposioToolSet, Action

composio_toolset = ComposioToolSet()

# Get specific Netlify actions
netlify_tools = composio_toolset.get_tools(
    actions=[
        Action.NETLIFY_DEPLOY_SITE,
        Action.NETLIFY_GET_DEPLOY_STATUS,
        Action.NETLIFY_ROLLBACK_DEPLOY,
    ]
)

@agent
def backend_developer(self) -> Agent:
    return Agent(
        config=self.agents_config["f3_backend_developer"],
        tools=netlify_tools + [CodeValidatorTool()],
        reasoning=True,
        inject_date=True,
        max_iter=20,
        verbose=True,
        llm=LLM(model="openai/gpt-4o", temperature=0.2),
    )
```

**Custom NetlifyDeployTool** (if not using Composio):
```python
from crewai.tools import tool
import httpx
import os

@tool("Deploy to Netlify")
def netlify_deploy_tool(site_name: str, files: dict) -> str:
    """
    Deploy files to Netlify.

    Args:
        site_name: Netlify site name (e.g., "startupai-landing-abc123")
        files: Dict of {filepath: content} to deploy

    Returns:
        Deployed URL or error message
    """
    token = os.environ["NETLIFY_ACCESS_TOKEN"]

    # Create deploy
    response = httpx.post(
        f"https://api.netlify.com/api/v1/sites/{site_name}/deploys",
        headers={"Authorization": f"Bearer {token}"},
        json={"files": files}
    )

    if response.status_code == 200:
        deploy = response.json()
        return f"Deployed to: {deploy['ssl_url']}"
    else:
        return f"Deploy failed: {response.text}"
```

---

### Category 5: Analytics & Measurement

**Purpose**: Collect and analyze experiment metrics.

| Tool | Source | Description | Target Agents |
|------|--------|-------------|---------------|
| `AnalyticsTool` | Custom | Query GA4/PostHog for metrics | P3 (Analytics) |
| `ABTestResultsTool` | Custom | Analyze A/B test outcomes | P3 |
| `ConversionTrackerTool` | Custom | Track funnel conversions | P3 |
| `AdPlatformTool` | Custom | Meta/Google Ads API | D3 (CTA Test) |

**Agent Configuration Pattern**:
```python
@agent
def analytics_agent(self) -> Agent:
    return Agent(
        config=self.agents_config["p3_analytics"],
        tools=[
            AnalyticsTool(),
            ABTestResultsTool(),
        ],
        reasoning=True,      # Analyze patterns in data
        inject_date=True,    # Time-series awareness
        max_iter=25,
        verbose=True,
        llm=LLM(model="openai/gpt-4o", temperature=0.1),  # Very low for analysis
    )
```

**Innovation Physics Signal Computation**:
```python
@tool("Compute Desirability Signals")
def compute_signals_tool(impressions: int, clicks: int, signups: int) -> dict:
    """
    Compute Innovation Physics signals from experiment data.

    Returns:
        Dict with problem_resonance, zombie_ratio, and signal interpretation
    """
    problem_resonance = (clicks + signups) / impressions if impressions > 0 else 0
    zombie_ratio = (clicks - signups) / clicks if clicks > 0 else 0

    # Signal interpretation
    if problem_resonance < 0.3:
        signal = "SEGMENT_PIVOT"
        interpretation = "Wrong audience - problem doesn't resonate"
    elif zombie_ratio >= 0.7:
        signal = "VALUE_PIVOT"
        interpretation = "Right problem, wrong solution - high zombie ratio"
    else:
        signal = "STRONG_COMMITMENT"
        interpretation = "Problem resonates and solution attracts commitment"

    return {
        "problem_resonance": round(problem_resonance, 3),
        "zombie_ratio": round(zombie_ratio, 3),
        "signal": signal,
        "interpretation": interpretation,
    }
```

---

### Category 6: Governance & Learning

**Purpose**: Ensure quality, security, and capture learnings.

| Tool | Source | Description | Target Agents |
|------|--------|-------------|---------------|
| `MethodologyCheckTool` | Custom | Validate VPC against Strategyzer | G1 (QA) |
| `GuardianReviewTool` | Custom | Creative QA and brand safety | G1 (QA) |
| `PrivacyGuardTool` | Custom | PII detection and scrubbing | G2 (Security) |
| `LearningCaptureTool` | Custom | Store patterns in flywheel | G3 (Audit), C3 |
| `LearningRetrievalTool` | Custom | RAG-based pattern retrieval | O1, C1 |
| `BudgetGuardrailsTool` | Custom | Enforce spend limits | L1 (Finance) |

**Agent Configuration Pattern**:
```python
@agent
def qa_agent(self) -> Agent:
    return Agent(
        config=self.agents_config["g1_qa_agent"],
        tools=[
            MethodologyCheckTool(),
            GuardianReviewTool(),
        ],
        reasoning=True,      # Plan review strategy
        inject_date=True,
        max_iter=20,
        verbose=True,
        llm=LLM(model="openai/gpt-4o", temperature=0.1),  # Strict for QA
    )
```

---

## Agent Configuration Standard

All agents MUST follow this configuration pattern (the "IntakeCrew Pattern"):

```python
from crewai import Agent, LLM

@agent
def agent_name(self) -> Agent:
    return Agent(
        # REQUIRED: Configuration
        config=self.agents_config["agent_name"],

        # REQUIRED: Tools (empty list if pure LLM)
        tools=[Tool1(), Tool2()],

        # REQUIRED: Reasoning (True for complex tasks)
        reasoning=True,

        # REQUIRED: Date injection (always True for StartupAI)
        inject_date=True,

        # REQUIRED: Iteration limit
        max_iter=25,

        # REQUIRED: Explicit LLM configuration
        llm=LLM(
            model="openai/gpt-4o",
            temperature=0.7,  # Adjust per agent role
        ),

        # OPTIONAL: Code execution (only for dev agents)
        allow_code_execution=False,
        code_execution_mode="safe",

        # OPTIONAL: Execution timeout
        max_execution_time=300,

        # STANDARD: Always True
        verbose=True,
        allow_delegation=False,
    )
```

### Temperature Guidelines

| Agent Role | Temperature | Rationale |
|------------|-------------|-----------|
| Research/Analysis | 0.1-0.3 | Factual accuracy over creativity |
| Code Generation | 0.1-0.2 | Syntactic correctness critical |
| QA/Governance | 0.1 | Strict, consistent evaluation |
| Design/Creative | 0.7-0.9 | Encourage creative exploration |
| Strategy/Synthesis | 0.5-0.7 | Balance insight with coherence |

### Reasoning Guidelines

Enable `reasoning=True` for agents that need to:
- Plan multi-step tool usage
- Synthesize information from multiple sources
- Make complex decisions with trade-offs
- Reflect before acting

Disable `reasoning=False` for agents that:
- Perform straightforward transformations
- Follow rigid templates
- Have single-step tasks

---

## Implementation Tiers

### Tier 1: Immediate (Week 1)
**Goal**: Enable evidence-based research across all crews.

| Task | Effort | Impact |
|------|--------|--------|
| Migrate `src/intake_crew/tools/` → `src/shared/tools/` | 1h | Unblocks all tiers |
| Apply IntakeCrew pattern to all 45 agents | 2h | Consistent configuration |
| Wire `TavilySearchTool` to D2, J1, PAIN_RES, GAIN_RES | 1h | Real research data |
| Wire `MethodologyCheckTool` to G1 agents | 1h | VPC validation |

**Deliverable**: Research and QA agents produce evidence-based outputs.

### Tier 2: Near-term (Week 2)
**Goal**: Enable design and asset generation.

| Task | Effort | Impact |
|------|--------|--------|
| Add `DalleTool` to P1 (Ad Creative) | 1h | Real visual assets |
| Add `FileReadTool` to F1 (UX Designer) | 1h | Template access |
| Add `CodeInterpreterTool` to F2 (Frontend) | 2h | Code execution |
| Implement `FileWriteTool` custom tool | 2h | File generation |

**Deliverable**: BuildCrew can generate complete landing page artifacts.

### Tier 3: Mid-term (Week 3)
**Goal**: Enable autonomous deployment.

| Task | Effort | Impact |
|------|--------|--------|
| Integrate Composio for Netlify/GitHub | 4h | Deployment capability |
| OR: Implement custom `NetlifyDeployTool` | 6h | Alternative approach |
| Add `CodeValidatorTool` to F3 | 2h | Pre-deploy validation |
| Implement deployment HITL checkpoint | 2h | Human approval before deploy |

**Deliverable**: BuildCrew can deploy landing pages autonomously (with HITL).

### Tier 4: Full Autonomy (Week 4+)
**Goal**: Close the loop with analytics and learning.

| Task | Effort | Impact |
|------|--------|--------|
| Implement `AnalyticsTool` (PostHog/GA4) | 4h | Real metrics |
| Implement `ABTestResultsTool` | 3h | Experiment analysis |
| Wire flywheel tools (Capture, Retrieval) | 3h | Learning loop |
| Implement `AdPlatformTool` (Meta/Google) | 8h+ | Real ad experiments |

**Deliverable**: Complete autonomous validation loop.

---

## Tool Implementation Checklist

> **Reference**: See [tool-specifications.md](./tool-specifications.md) for detailed specifications of each tool.

### Tier 1: Evidence-Based Research (Week 1)

| Tool | Status | Spec Location | Target Agents | Effort |
|------|--------|---------------|---------------|--------|
| TavilySearchTool | WIRE | tool-specifications.md#tavilysearchtool | D2, J1, PAIN_RES, GAIN_RES | 1h |
| CustomerResearchTool | WIRE | tool-specifications.md#customerresearchtool | D1, D2, J1 | 1h |
| MethodologyCheckTool | WIRE | tool-specifications.md#methodologychecktool | G1, FIT_SCORE | 1h |
| ForumScraperTool | BUILD | tool-specifications.md#forumscrapertool | D2, J1, PAIN_RES, GAIN_RES | 4h |
| ReviewAnalysisTool | BUILD | tool-specifications.md#reviewanalysistool | D2, J1, PAIN_RES, GAIN_RES | 4h |

**Tier 1 Total**: 11h

### Tier 2: Design & Asset Generation (Week 2)

| Tool | Status | Spec Location | Target Agents | Effort |
|------|--------|---------------|---------------|--------|
| LandingPageGeneratorTool | WIRE | tool-specifications.md#landingpagegeneratortool | F2, W2 | 1h |
| LandingPageDeploymentTool | WIRE | tool-specifications.md#landingpagedeploymenttool | F3 | 1h |
| CodeValidatorTool | WIRE | tool-specifications.md#codevalidatortool | F2, F3 | 1h |
| ComponentLibraryScraperTool | BUILD | tool-specifications.md#componentlibraryscrapertool | F1 | 4h |
| CanvasBuilderTool | BUILD | tool-specifications.md#canvasbuildertool | V1, V2, V3 | 6h |
| TestCardTool | BUILD | tool-specifications.md#testcardtool | E1 | 3h |
| LearningCardTool | BUILD | tool-specifications.md#learningcardtool | E1, D4 | 3h |

**Tier 2 Total**: 19h

### Tier 3: Growth & Testing (Week 3)

| Tool | Status | Spec Location | Target Agents | Effort |
|------|--------|---------------|---------------|--------|
| ABTestTool | BUILD | tool-specifications.md#abtesttool | P1, P2, W1 | 6h |
| AdPlatformTool | BUILD | tool-specifications.md#adplatformtool | P1, P2, P3, D3 | 10h |
| AnalyticsTool | BUILD | tool-specifications.md#analyticstool | P3, D3, L1 | 6h |
| InterviewSchedulerTool | BUILD | tool-specifications.md#interviewschedulertool | D1 | 4h |
| TranscriptionTool | BUILD | tool-specifications.md#transcriptiontool | D1 | 4h |
| InsightExtractorTool | BUILD | tool-specifications.md#insightextractortool | D1, D4 | 6h |

**Tier 3 Total**: 36h

### Tier 4: Governance & Finance (Week 4)

| Tool | Status | Spec Location | Target Agents | Effort |
|------|--------|---------------|---------------|--------|
| GuardianReviewTool | WIRE | tool-specifications.md#guardianreviewtool | GV1, G1 | 1h |
| PrivacyGuardTool | WIRE | tool-specifications.md#privacyguardtool | G2 | 1h |
| UnitEconomicsModelsTool | WIRE | tool-specifications.md#uniteconomicsmodelstool | L1 | 1h |
| BusinessModelClassifierTool | WIRE | tool-specifications.md#businessmodelclassifiertool | L1, L3 | 1h |
| BudgetGuardrailsTool | WIRE | tool-specifications.md#budgetguardrailstool | L3, P2 | 1h |
| FinancialDataTool | BUILD | tool-specifications.md#financialdatatool | L1, L2, L3 | 4h |
| ViabilityApprovalTool | BUILD | tool-specifications.md#viabilityapprovaltool | C2 | 4h |
| TechStackValidator | BUILD | tool-specifications.md#techstackvalidator | F3 | 4h |
| APIIntegrationTool | BUILD | tool-specifications.md#apiintegrationtool | F3 | 4h |
| CostEstimatorTool | BUILD | tool-specifications.md#costestimatortool | F3 | 4h |

**Tier 4 Total**: 25h

### Tier 5: Learning & Intelligence (Ongoing)

| Tool | Status | Spec Location | Target Agents | Effort |
|------|--------|---------------|---------------|--------|
| LearningCaptureTool | WIRE | tool-specifications.md#learningcapturetool | E1, D4, L3, C3, G3 | 2h |
| LearningRetrievalTool | WIRE | tool-specifications.md#learningretrievaltool | O1, E1, S1 | 2h |
| AnonymizerTool | BUILD | tool-specifications.md#anonymizertool | Learning pipeline | 4h |
| BehaviorPatternTool | BUILD | tool-specifications.md#behaviorpatterntool | D2, D3 | 8h |
| ConversationTool | BUILD | tool-specifications.md#conversationtool | O1 | 6h |
| NoteStructurerTool | BUILD | tool-specifications.md#notestructurertool | O1 | 4h |
| SocialListeningTool | BUILD | tool-specifications.md#sociallisteningtool | D2 | 6h |
| TrendAnalysisTool | BUILD | tool-specifications.md#trendanalysistool | D2 | 4h |

**Tier 5 Total**: 36h

### Implementation Summary

| Tier | WIRE | BUILD | Total Effort |
|------|------|-------|--------------|
| Tier 1: Research | 3 | 2 | 11h |
| Tier 2: Design | 3 | 4 | 19h |
| Tier 3: Growth | 0 | 6 | 36h |
| Tier 4: Governance | 5 | 5 | 25h |
| Tier 5: Learning | 2 | 6 | 36h |
| **TOTAL** | **13** | **23** | **127h** |

**Implementation Order Priority:**
1. **Tier 1** - Unlocks evidence-based research (prerequisite for all phases)
2. **Tier 2** - Unlocks landing page generation (prerequisite for experiments)
3. **Tier 4** - Unlocks governance (can run in parallel with Tier 3)
4. **Tier 3** - Unlocks experiment execution (highest complexity)
5. **Tier 5** - Closes learning loop (ongoing improvement)

---

## Extended Agentic Capabilities

### Future Enhancement: Multi-Modal Agents

Enable agents to process images, PDFs, and other media:

```python
@agent
def multimodal_analyst(self) -> Agent:
    return Agent(
        config=self.agents_config["multimodal_analyst"],
        tools=[
            PDFReaderTool(),
            ImageAnalysisTool(),
        ],
        multimodal=True,  # Enable multimodal processing
        reasoning=True,
        inject_date=True,
        max_iter=25,
        verbose=True,
        llm=LLM(model="openai/gpt-4o", temperature=0.3),
    )
```

**Use Cases**:
- Analyze competitor landing page screenshots
- Extract data from PDF market reports
- Review ad creative images for brand compliance

### Future Enhancement: Agent Delegation

Enable specialized agents to delegate subtasks:

```python
@agent
def lead_researcher(self) -> Agent:
    return Agent(
        config=self.agents_config["lead_researcher"],
        tools=[TavilySearchTool()],
        allow_delegation=True,  # Can delegate to other agents
        reasoning=True,
        max_iter=30,
    )
```

**Use Cases**:
- Lead researcher delegates specific searches to specialist agents
- QA agent delegates security review to security agent
- PM delegates technical analysis to engineering agents

### Future Enhancement: Memory-Enabled Agents

Enable agents to maintain conversation context and learn from interactions:

```python
@agent
def interview_agent(self) -> Agent:
    return Agent(
        config=self.agents_config["o1_interview_agent"],
        tools=[ConversationTool()],
        memory=True,  # Maintain conversation history
        knowledge_sources=[
            InterviewKnowledgeSource(),
            CompanyKnowledgeSource(),
        ],
        reasoning=True,
        inject_date=True,
    )
```

**Use Cases**:
- Multi-turn founder interviews with context retention
- Learning from past validation outcomes
- Building company-specific knowledge over time

### Future Enhancement: Autonomous Experiment Orchestration

Full autonomous validation cycle:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AUTONOMOUS VALIDATION LOOP                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   [Research Agent] ──▶ Market research, competitor analysis          │
│         │                                                            │
│         ▼                                                            │
│   [Design Agent] ──▶ Generate landing page + ad creatives           │
│         │                                                            │
│         ▼                                                            │
│   [HITL: Approve Creatives] ◀── Human reviews before deploy          │
│         │                                                            │
│         ▼                                                            │
│   [Deploy Agent] ──▶ Push to Netlify, configure analytics           │
│         │                                                            │
│         ▼                                                            │
│   [Experiment Agent] ──▶ Run ads (Meta/Google), collect data        │
│         │                                                            │
│         ▼                                                            │
│   [HITL: Approve Spend Increase] ◀── Human approves budget          │
│         │                                                            │
│         ▼                                                            │
│   [Analytics Agent] ──▶ Compute Innovation Physics signals           │
│         │                                                            │
│         ├──▶ STRONG_COMMITMENT: Proceed to Feasibility              │
│         ├──▶ SEGMENT_PIVOT: Loop back with new segment              │
│         └──▶ VALUE_PIVOT: Loop back with new value prop             │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Security Considerations

### Tool Sandboxing

All code execution tools MUST use sandboxing:

```python
allow_code_execution=True,
code_execution_mode="safe",  # Uses Docker
max_execution_time=300,      # 5 minute timeout
```

### API Key Management

- Store all API keys in Modal Secrets or environment variables
- Never hardcode keys in tool implementations
- Use Composio for OAuth-based integrations (handles token refresh)

### Budget Guardrails

Tools that spend money MUST have guardrails:

```python
@tool("Run Ad Campaign")
def ad_campaign_tool(budget: float, campaign_config: dict) -> str:
    # Hard limit check
    MAX_SPEND = float(os.environ.get("MAX_AD_SPEND", "100"))
    if budget > MAX_SPEND:
        return f"Error: Budget ${budget} exceeds limit ${MAX_SPEND}"

    # HITL checkpoint for any real spend
    if budget > 0:
        return "HITL_REQUIRED: Approve ad spend before execution"

    # ... execute campaign
```

### PII Protection

All tools that process user data MUST strip PII before storage:

```python
@tool("Store Learning")
def store_learning_tool(learning: dict) -> str:
    # Strip PII before storage
    cleaned = PrivacyGuardTool().run(learning)

    # Store to flywheel
    supabase.table("learnings").insert(cleaned)

    return "Learning stored (PII removed)"
```

---

## Related Documents

- [tool-mapping.md](./tool-mapping.md) - Specific tool-to-agent assignments
- [flywheel-learning.md](./flywheel-learning.md) - Learning capture architecture
- [approval-workflows.md](./approval-workflows.md) - HITL checkpoint design
- [02-organization.md](../02-organization.md) - Agent definitions
- [ADR-002](../../adr/002-modal-serverless-migration.md) - Modal serverless architecture

---

**Last Updated**: 2026-01-09

**Changes (2026-01-09)**:
- Created comprehensive agentic tool framework
- Defined 6 tool lifecycle categories with examples
- Established agent configuration standard ("IntakeCrew Pattern")
- Added implementation tiers with effort estimates
- Documented Composio vs Custom decision matrix
- Added extended agentic capabilities (multimodal, delegation, memory)
- Included security considerations for production deployment
