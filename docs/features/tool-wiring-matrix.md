---
document_type: feature-audit
status: active
last_verified: 2026-01-13
---

# Tool Wiring Matrix

## Purpose
Complete inventory of all 18 shared tools and their wiring status across 45 agents in the validation engine.

## Quick Reference

### Tool Inventory

| # | Tool | Category | Wired Agents | Status |
|---|------|----------|--------------|--------|
| 1 | TavilySearchTool | Research | 3 | `active` |
| 2 | CustomerResearchTool | Research | 0 | `available` |
| 3 | ForumSearchTool | Customer Research | 0 | `available` |
| 4 | ReviewAnalysisTool | Customer Research | 0 | `available` |
| 5 | SocialListeningTool | Customer Research | 0 | `available` |
| 6 | TrendAnalysisTool | Customer Research | 0 | `available` |
| 7 | TranscriptionTool | Advanced Analysis | 1 | `active` |
| 8 | InsightExtractorTool | Advanced Analysis | 1 | `active` |
| 9 | BehaviorPatternTool | Advanced Analysis | 1 | `active` |
| 10 | ABTestTool | Advanced Analysis | 3 | `active` |
| 11 | AnalyticsTool | Analytics | 3 | `active` |
| 12 | AnonymizerTool | Privacy | 3 | `active` |
| 13 | AdPlatformTool | Analytics | 2 | `active` |
| 14 | CalendarTool | Analytics | 0 | `available` |
| 15 | CanvasBuilderTool | LLM Tools | 5 | `active` |
| 16 | TestCardTool | LLM Tools | 4 | `active` |
| 17 | LearningCardTool | LLM Tools | 3 | `active` |
| 18 | MethodologyCheckTool | Governance | 4 | `active` |
| 19 | LandingPageDeploymentTool | Deployment | 1 | `active` |

**Summary**: 19 tools, 14 wired, 5 available but unused

### Wiring Status

| Status | Count | Agents | Tools Wired |
|--------|-------|--------|-------------|
| Wired | 27 | 60% | 1-4 tools |
| Empty | 18 | 40% | 0 tools |

---

## Tools by Category

### Research Tools

**File**: `src/shared/tools/web_search.py`

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| TavilySearchTool | Web search via Tavily API | `query: str` | `SearchResult[]` |
| CustomerResearchTool | Customer-focused research | `segment: str, query: str` | `WebSearchOutput` |

**Wiring**:
- TavilySearchTool → D3 (Market Researcher), CP1 (Job Excavator), CP3 (Pain Excavator), CP5 (Gain Excavator)
- CustomerResearchTool → Not wired

### Customer Research Tools

**File**: `src/shared/tools/customer_research.py`

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| ForumSearchTool | Search forums (Reddit, etc.) | `query: str, subreddits: list` | `ForumSearchOutput` |
| ReviewAnalysisTool | Analyze product reviews | `product: str, platform: str` | `ReviewAnalysisOutput` |
| SocialListeningTool | Monitor social media | `keywords: list, platforms: list` | `SocialListeningOutput` |
| TrendAnalysisTool | Analyze market trends | `topic: str, timeframe: str` | `TrendAnalysisOutput` |

**Wiring**: All available but not yet wired to any agents.

### Advanced Analysis Tools

**File**: `src/shared/tools/advanced_analysis.py`

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| TranscriptionTool | Audio → Text transcription | `audio_url: str` | `TranscriptionOutput` |
| InsightExtractorTool | Extract insights from text | `text: str, focus: str` | `InsightExtractionOutput` |
| BehaviorPatternTool | Identify behavior patterns | `data: dict` | `BehaviorPatternOutput` |
| ABTestTool | Design/run A/B tests | `hypothesis: str, variants: list` | `ABTestResult` |

**Wiring**:
- TranscriptionTool → D2 (Evidence Miner)
- InsightExtractorTool → D5 (Insight Synthesizer)
- BehaviorPatternTool → D4 (Behavior Analyst)
- ABTestTool → WTP1 (Pricing Test Designer), GR1 (Campaign Strategist), GR2 (Campaign Runner)

### Analytics & Privacy Tools

**File**: `src/shared/tools/analytics_privacy.py`

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| AnalyticsTool | Fetch analytics data | `source: str, metrics: list` | `AnalyticsOutput` |
| AnonymizerTool | Anonymize PII | `data: dict` | `AnonymizationResult` |
| AdPlatformTool | Ad platform metrics | `platform: str, campaign_id: str` | `AdPlatformOutput` |
| CalendarTool | Find interview slots | `duration: int, participants: list` | `CalendarOutput` |

**Wiring**:
- AnalyticsTool → WTP2 (Pricing Analyst), GR3 (Signal Analyst), F1 (Margin Calculator)
- AnonymizerTool → DGV2 (Privacy Guardian), FGV2 (Security Auditor), VGV2 (Compliance Auditor)
- AdPlatformTool → GR1 (Campaign Strategist), GR2 (Campaign Runner)
- CalendarTool → Not wired

### LLM-Based Tools

**File**: `src/shared/tools/llm_tools.py`

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| CanvasBuilderTool | Build canvas elements | `element_type: str, data: dict` | `CanvasBuilderOutput` |
| TestCardTool | Design test cards | `hypothesis: str, experiment_type: str` | `TestCardOutput` |
| LearningCardTool | Capture learnings | `test_card_id: str, outcome: dict` | `LearningCardOutput` |

**Wiring**:
- CanvasBuilderTool → VD1 (Pain Reliever Designer), VD2 (Gain Creator Designer), VD3 (Feature Specifier), B1 (Creative Designer), B2 (Code Generator)
- TestCardTool → D1 (Experiment Designer), B1 (Creative Designer), B2 (Code Generator), GR1 (Campaign Strategist)
- LearningCardTool → D1 (Experiment Designer), DGV3 (Decision Logger)

### Governance Tools

**File**: `src/shared/tools/methodology_check.py`

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| MethodologyCheckTool | Validate VPD methodology | `canvas: dict` | `MethodologyCheckResult` |

**Wiring**: FA1 (VPC Fit Scorer), DGV1 (Methodology Auditor), FGV1 (Risk Assessor), VGV1 (Quality Auditor)

### Deployment Tools

**File**: `src/shared/tools/landing_page_deploy.py`

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| LandingPageDeploymentTool | Deploy LP to Netlify | `html: str, site_name: str` | `DeploymentResult` |

**Wiring**: B3 (Landing Page Deployer)

---

## Agent-Tool Wiring by Phase

### Phase 0: OnboardingCrew

| Agent | ID | Tools |
|-------|-----|-------|
| Founder Interview | O1 | `[]` |
| Concept Validator | GV1 | `[]` |
| Intent Verification | GV2 | `[]` |
| Brief Compiler | S1 | `[]` |

**Gap**: No tools wired. Could benefit from MethodologyCheckTool for validation.

### Phase 1: VPCDiscoveryFlow

#### DiscoveryCrew

| Agent | ID | Tools |
|-------|-----|-------|
| Experiment Designer | D1 | `[TestCardTool, LearningCardTool]` |
| Evidence Miner | D2 | `[TranscriptionTool, InsightExtractorTool]` |
| Market Researcher | D3 | `[TavilySearchTool, ReviewAnalysisTool, SocialListeningTool]` |
| Behavior Analyst | D4 | `[BehaviorPatternTool, AnalyticsTool]` |
| Insight Synthesizer | D5 | `[InsightExtractorTool]` |

#### CustomerProfileCrew

| Agent | ID | Tools |
|-------|-----|-------|
| Job Excavator | CP1 | `[TavilySearchTool, ForumSearchTool]` |
| Job Ranker | CP2 | `[]` |
| Pain Excavator | CP3 | `[TavilySearchTool, ReviewAnalysisTool]` |
| Pain Ranker | CP4 | `[]` |
| Gain Excavator | CP5 | `[TavilySearchTool, TrendAnalysisTool]` |
| Gain Ranker | CP6 | `[]` |

#### ValueDesignCrew

| Agent | ID | Tools |
|-------|-----|-------|
| Pain Reliever Designer | VD1 | `[CanvasBuilderTool]` |
| Gain Creator Designer | VD2 | `[CanvasBuilderTool]` |
| Feature Specifier | VD3 | `[CanvasBuilderTool]` |

#### WTPCrew

| Agent | ID | Tools |
|-------|-----|-------|
| Pricing Test Designer | WTP1 | `[ABTestTool, TestCardTool]` |
| Pricing Analyst | WTP2 | `[AnalyticsTool, InsightExtractorTool]` |

#### FitAssessmentCrew

| Agent | ID | Tools |
|-------|-----|-------|
| VPC Fit Scorer | FA1 | `[MethodologyCheckTool]` |
| Gate Recommender | FA2 | `[]` |

### Phase 2: DesirabilityFlow

#### BuildCrew

| Agent | ID | Tools |
|-------|-----|-------|
| Creative Designer | B1 | `[CanvasBuilderTool, TestCardTool]` |
| Code Generator | B2 | `[CanvasBuilderTool, TestCardTool]` |
| Landing Page Deployer | B3 | `[LandingPageDeploymentTool]` |

#### GrowthCrew

| Agent | ID | Tools |
|-------|-----|-------|
| Campaign Strategist | GR1 | `[ABTestTool, AdPlatformTool, TestCardTool]` |
| Campaign Runner | GR2 | `[ABTestTool, AdPlatformTool]` |
| Signal Analyst | GR3 | `[AnalyticsTool, LearningCardTool]` |

#### GovernanceCrew (Desirability)

| Agent | ID | Tools |
|-------|-----|-------|
| Methodology Auditor | DGV1 | `[MethodologyCheckTool]` |
| Privacy Guardian | DGV2 | `[AnonymizerTool]` |
| Decision Logger | DGV3 | `[LearningCardTool]` |

### Phase 3: FeasibilityFlow

#### FeasibilityBuildCrew

| Agent | ID | Tools |
|-------|-----|-------|
| Feature Mapper | FB1 | `[]` |
| Technical Assessor | FB2 | `[]` |
| Cost Estimator | FB3 | `[]` |

**Gap**: No tools wired. Could benefit from AnalyticsTool for cost estimation.

#### FeasibilityGovernanceCrew

| Agent | ID | Tools |
|-------|-----|-------|
| Risk Assessor | FGV1 | `[MethodologyCheckTool]` |
| Security Auditor | FGV2 | `[AnonymizerTool]` |

### Phase 4: ViabilityFlow

#### FinanceCrew

| Agent | ID | Tools |
|-------|-----|-------|
| Margin Calculator | F1 | `[AnalyticsTool, AdPlatformTool]` |
| Compliance Checker | F2 | `[]` |
| Assumption Auditor | F3 | `[]` |

#### SynthesisCrew

| Agent | ID | Tools |
|-------|-----|-------|
| Evidence Synthesizer | SY1 | `[]` |
| HITL Presenter | SY2 | `[]` |
| Report Generator | SY3 | `[]` |

**Gap**: No tools wired. Could benefit from LearningCardTool for synthesis.

#### ViabilityGovernanceCrew

| Agent | ID | Tools |
|-------|-----|-------|
| Quality Auditor | VGV1 | `[MethodologyCheckTool]` |
| Compliance Auditor | VGV2 | `[AnonymizerTool]` |
| Final Logger | VGV3 | `[]` |

---

## Wiring Summary by Tool

| Tool | Agents Wired | Phases |
|------|--------------|--------|
| TavilySearchTool | D3, CP1, CP3, CP5 | 1 |
| TranscriptionTool | D2 | 1 |
| InsightExtractorTool | D2, D5, WTP2 | 1 |
| BehaviorPatternTool | D4 | 1 |
| ABTestTool | WTP1, GR1, GR2 | 1, 2 |
| AnalyticsTool | D4, WTP2, GR3, F1 | 1, 2, 4 |
| AnonymizerTool | DGV2, FGV2, VGV2 | 2, 3, 4 |
| AdPlatformTool | GR1, GR2, F1 | 2, 4 |
| CanvasBuilderTool | VD1, VD2, VD3, B1, B2 | 1, 2 |
| TestCardTool | D1, WTP1, B1, B2, GR1 | 1, 2 |
| LearningCardTool | D1, GR3, DGV3 | 1, 2 |
| MethodologyCheckTool | FA1, DGV1, FGV1, VGV1 | 1, 2, 3, 4 |
| LandingPageDeploymentTool | B3 | 2 |

---

## Gaps / TODOs

### Unwired Tools (Available)

| Tool | Suggested Agents |
|------|------------------|
| CustomerResearchTool | D3 (Market Researcher) |
| ForumSearchTool | CP1 (Job Excavator) - partially wired |
| ReviewAnalysisTool | CP3 (Pain Excavator) - partially wired |
| SocialListeningTool | D3 (Market Researcher) |
| TrendAnalysisTool | CP5 (Gain Excavator) - partially wired |
| CalendarTool | D1 (Experiment Designer) for interview scheduling |

### Agents with Empty Tools

| Phase | Crew | Agents Missing Tools |
|-------|------|---------------------|
| 0 | OnboardingCrew | O1, GV1, GV2, S1 (4) |
| 1 | CustomerProfileCrew | CP2, CP4, CP6 (3) |
| 1 | FitAssessmentCrew | FA2 (1) |
| 3 | FeasibilityBuildCrew | FB1, FB2, FB3 (3) |
| 4 | FinanceCrew | F2, F3 (2) |
| 4 | SynthesisCrew | SY1, SY2, SY3 (3) |
| 4 | ViabilityGovernanceCrew | VGV3 (1) |

**Total**: 17 agents with empty tools arrays

### Priority Wiring Recommendations

1. **High Priority** (blocking core functionality):
   - Phase 3 FeasibilityBuildCrew needs technical research tools
   - Phase 4 SynthesisCrew needs LearningCardTool for evidence synthesis

2. **Medium Priority** (enhanced capability):
   - OnboardingCrew could use MethodologyCheckTool for early validation
   - Ranker agents (CP2, CP4, CP6) could use AnalyticsTool

3. **Low Priority** (nice to have):
   - CalendarTool for interview scheduling in D1
   - CustomerResearchTool as alternative to TavilySearchTool

---

## Related Documents

- [crew-agent-task-matrix.md](./crew-agent-task-matrix.md) - Agent details
- [phase-mapping.md](./phase-mapping.md) - Phase specifications
- [../master-architecture/reference/agentic-tool-framework.md](../master-architecture/reference/agentic-tool-framework.md) - Tool lifecycle
- [../master-architecture/reference/tool-mapping.md](../master-architecture/reference/tool-mapping.md) - Canonical tool mapping
