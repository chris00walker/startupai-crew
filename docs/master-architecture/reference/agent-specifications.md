---
purpose: Complete specification of all 43 agents with tools, configs, and output schemas
status: active
last_reviewed: 2026-01-20
vpd_compliance: true
architectural_pivot: 2026-01-19
---

# Agent Specifications

> **Architectural Pivot (2026-01-19)**: Phase 0 was simplified to Quick Start (no AI). Agent count: 45 → 43. OnboardingCrew was dissolved; GV1 and S1 moved to Phase 1 BriefGenerationCrew. See [ADR-006](../../adr/006-quick-start-architecture.md).

This document provides the complete specification for all 43 agents in the StartupAI system. Each specification includes configuration parameters, tool requirements, output schemas, and task integration details.

**Usage**: This is the authoritative reference for implementing agent configurations. Developers should be able to implement any agent without asking clarifying questions.

**Related Documents**:
- [02-organization.md](../02-organization.md) - Agent Configuration Standard
- [tool-specifications.md](./tool-specifications.md) - Tool implementation details
- [tool-mapping.md](./tool-mapping.md) - Agent-to-tool mapping matrix

---

## Table of Contents

1. [Phase 0: Quick Start (0 agents - No AI)](#phase-0-quick-start)
2. [Phase 1: VPC Discovery (20 agents)](#phase-1-vpc-discovery)
3. [Phase 2: Desirability (9 agents)](#phase-2-desirability)
4. [Phase 3: Feasibility (5 agents)](#phase-3-feasibility)
5. [Phase 4: Viability (9 agents)](#phase-4-viability)

---

## Phase 0: Quick Start

> **Architectural Pivot (2026-01-19)**: Phase 0 was simplified to Quick Start - a simple form submission with no AI. See [ADR-006](../../adr/006-quick-start-architecture.md).

**Flow**: None (form submission only)
**Crew**: None
**Agents**: 0

Phase 0 is now a **Quick Start form** that takes ~30 seconds. Users enter their business idea and optional context, then Phase 1 starts immediately.

The Founder's Brief is now AI-generated in Phase 1 by BriefGenerationCrew.

---

## ~~Phase 0: Onboarding~~ (Superseded)

<details>
<summary>Historical Reference (OnboardingCrew - Superseded Jan 19, 2026)</summary>

**Flow**: `OnboardingFlow` (deleted)
**Crew**: `OnboardingCrew` (dissolved)
**Agents**: 4 (O1, GV1, GV2, S1) - O1 and GV2 deleted; GV1 and S1 moved to Phase 1 BriefGenerationCrew

### O1 - Founder Interview Agent (DELETED)

| Attribute | Value |
|-----------|-------|
| **ID** | O1 |
| **Founder** | Sage (CSO) |
| **Crew** | OnboardingCrew |
| **Phase** | 0 (Onboarding) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | `[]` | Pure LLM - conversational interview |
| `reasoning` | True | Complex hypothesis extraction |
| `inject_date` | True | Time context for market trends |
| `max_iter` | 25 | Extended conversation depth |
| `temperature` | 0.7 | Natural dialogue flow |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| (none) | N/A | Pure LLM agent - relies on conversational reasoning |

#### Output Schema

```python
class InterviewTranscript(BaseModel):
    idea_summary: str                    # One-liner business concept
    motivation: str                      # Why founder is pursuing this
    customer_hypothesis: str             # Who they think the customer is
    problem_hypothesis: str              # What problem they're solving
    solution_hypothesis: str             # Their proposed solution
    assumptions: List[Assumption]        # Ranked assumptions to test
    success_criteria: List[str]          # What "validated" means to them
    interview_timestamp: datetime
```

#### Task Integration

- **Input**: Raw founder conversation from onboarding chat
- **Output**: Structured interview transcript for GV1/GV2 validation
- **Context**: First agent in OnboardingFlow; no upstream dependencies

---

### GV1 - Concept Validator Agent

| Attribute | Value |
|-----------|-------|
| **ID** | GV1 |
| **Founder** | Guardian (CGO) |
| **Crew** | OnboardingCrew |
| **Phase** | 0 (Onboarding) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | `[]` | Pure LLM - validation reasoning |
| `reasoning` | True | Legal/ethical analysis |
| `inject_date` | True | Current regulatory context |
| `max_iter` | 15 | Focused validation checks |
| `temperature` | 0.1 | Strict compliance checking |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| (none) | N/A | Pure LLM agent - validation through reasoning |

#### Output Schema

```python
class LegitimacyReport(BaseModel):
    is_legitimate: bool                  # Pass/fail on legitimacy
    legal_concerns: List[str]            # Regulatory/legal issues
    ethical_concerns: List[str]          # Ethical red flags
    feasibility_concerns: List[str]      # Obvious technical blockers
    sanity_check: str                    # Overall assessment
    recommendations: List[str]           # Suggestions if concerns exist
    validation_timestamp: datetime
```

#### Task Integration

- **Input**: InterviewTranscript from O1
- **Output**: LegitimacyReport for S1 brief compilation
- **Context**: Parallel with GV2; both feed into S1

---

### GV2 - Intent Verification Agent

| Attribute | Value |
|-----------|-------|
| **ID** | GV2 |
| **Founder** | Guardian (CGO) |
| **Crew** | OnboardingCrew |
| **Phase** | 0 (Onboarding) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | `[]` | Pure LLM - intent matching |
| `reasoning` | True | Nuanced intent analysis |
| `inject_date` | True | Context freshness |
| `max_iter` | 15 | Focused verification |
| `temperature` | 0.1 | Precise intent matching |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| (none) | N/A | Pure LLM agent - verification through reasoning |

#### Output Schema

```python
class IntentVerificationReport(BaseModel):
    intent_match: bool                   # Brief matches founder's actual intent
    discrepancies: List[str]             # Mismatches found
    clarifications_needed: List[str]     # Questions for founder
    confidence_score: float              # 0-1 confidence in match
    verification_timestamp: datetime
```

#### Task Integration

- **Input**: InterviewTranscript from O1
- **Output**: IntentVerificationReport for S1 brief compilation
- **Context**: Parallel with GV1; both feed into S1

---

### S1 - Brief Compiler Agent

| Attribute | Value |
|-----------|-------|
| **ID** | S1 |
| **Founder** | Sage (CSO) |
| **Crew** | OnboardingCrew |
| **Phase** | 0 (Onboarding) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | `[]` | Pure LLM - synthesis |
| `reasoning` | True | Complex document synthesis |
| `inject_date` | True | Timestamp the brief |
| `max_iter` | 20 | Thorough compilation |
| `temperature` | 0.3 | Balanced synthesis |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| (none) | N/A | Pure LLM agent - synthesis through reasoning |

#### Output Schema

```python
class FoundersBrief(BaseModel):
    project_id: str                      # Unique identifier
    idea: IdeaSummary                    # Concept, one-liner, hypothesis
    customer: CustomerHypothesis         # Segment, characteristics
    problem: ProblemHypothesis           # Problem statement, alternatives
    solution: SolutionHypothesis         # Approach, key features
    assumptions: List[RankedAssumption]  # Prioritized by risk
    success_criteria: List[str]          # What "validated" means
    founder_context: FounderContext      # Stage, resources, constraints
    legitimacy_review: LegitimacyReport  # From GV1
    intent_verification: IntentVerificationReport  # From GV2
    created_at: datetime
    status: str                          # "pending_approval", "approved"
```

#### Task Integration

- **Input**: raw_idea, hints, MarketResearch (GV1)
- **Output**: FoundersBrief for HITL approval → Phase 1 Stage B
- **Context**: Final agent in BriefGenerationCrew (Phase 1); triggers `approve_brief` HITL (Stage A)

</details>

---

## Phase 1: VPC Discovery

**Flow**: `VPCDiscoveryFlow`
**Crews**: BriefGenerationCrew (NEW), DiscoveryCrew, CustomerProfileCrew, ValueDesignCrew, WTPCrew, FitAssessmentCrew
**Agents**: 20 (includes 2 from BriefGenerationCrew)

### BriefGenerationCrew (2 agents) - NEW

> **Added (2026-01-19)**: Generates Founder's Brief from user's raw idea using AI research. Moved from Phase 0.

#### GV1 - Concept Validator Agent (Moved from Phase 0)

| Attribute | Value |
|-----------|-------|
| **ID** | GV1 |
| **Founder** | Guardian (CGO) |
| **Crew** | BriefGenerationCrew |
| **Phase** | 1 (VPC Discovery) |

**Configuration**: Same as previous Phase 0 spec. Pure LLM agent for legitimacy validation.

**Output**: LegitimacyReport for S1 brief compilation.

---

#### S1 - Brief Compiler Agent (Moved from Phase 0)

| Attribute | Value |
|-----------|-------|
| **ID** | S1 |
| **Founder** | Sage (CSO) |
| **Crew** | BriefGenerationCrew |
| **Phase** | 1 (VPC Discovery) |

**Configuration**: Same as previous Phase 0 spec. Pure LLM agent for brief synthesis.

**Output**: FoundersBrief for HITL approval → Discovery continues.

**Task Integration**:
- **Input**: User's `raw_idea` from Quick Start, AI-conducted market research (from GV1)
- **Output**: FoundersBrief for HITL `approve_brief` checkpoint (Stage A)
- **Context**: Generates Founder's Brief from research instead of extracting from conversation

---

### DiscoveryCrew (5 agents)

#### E1 - Experiment Designer Agent

| Attribute | Value |
|-----------|-------|
| **ID** | E1 |
| **Founder** | Sage (CSO) |
| **Crew** | DiscoveryCrew |
| **Phase** | 1 (VPC Discovery) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | TestCardTool, LearningCardTool, LearningRetrievalTool | Experiment design artifacts |
| `reasoning` | True | Complex experiment planning |
| `inject_date` | True | Time-bound experiments |
| `max_iter` | 25 | Iterative design refinement |
| `temperature` | 0.5 | Balanced creativity/structure |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| TestCardTool | STUB | Generate Test Card artifacts |
| LearningCardTool | STUB | Generate Learning Card artifacts |
| LearningRetrievalTool | EXISTS | Query flywheel for past learnings |

#### Output Schema

```python
class ExperimentPlan(BaseModel):
    assumptions_map: AssumptionsMap      # 2x2 prioritization matrix
    test_cards: List[TestCard]           # Experiments to run
    experiment_mix: ExperimentMix        # SAY vs DO balance
    budget_allocation: BudgetAllocation  # Cost per experiment
    timeline: Timeline                   # Execution schedule
    success_metrics: List[Metric]        # How to measure success
```

#### Task Integration

- **Input**: FoundersBrief from Phase 0
- **Output**: ExperimentPlan for D1, D2, D3 execution
- **Context**: First agent in VPCDiscoveryFlow; designs the validation approach

---

#### D1 - Customer Interview Agent

| Attribute | Value |
|-----------|-------|
| **ID** | D1 |
| **Founder** | Sage (CSO) |
| **Crew** | DiscoveryCrew |
| **Phase** | 1 (VPC Discovery) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | InterviewSchedulerTool, TranscriptionTool, InsightExtractorTool, BehaviorPatternTool | SAY evidence collection |
| `reasoning` | True | Mom Test methodology |
| `inject_date` | True | Interview timestamps |
| `max_iter` | 25 | Multiple interview cycles |
| `temperature` | 0.7 | Natural conversation |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| InterviewSchedulerTool | STUB | Schedule customer interviews |
| TranscriptionTool | STUB | Transcribe interview recordings |
| InsightExtractorTool | STUB | Extract insights from transcripts |
| BehaviorPatternTool | STUB | Identify behavioral patterns |

#### Output Schema

```python
class SAYEvidence(BaseModel):
    interviews_conducted: int
    interview_summaries: List[InterviewSummary]
    key_quotes: List[Quote]              # Verbatim customer quotes
    jobs_discovered: List[Job]           # JTBD from interviews
    pains_discovered: List[Pain]         # Pain points mentioned
    gains_discovered: List[Gain]         # Desired gains mentioned
    behavioral_patterns: List[Pattern]   # Observed behaviors
    say_confidence_score: float          # 0-1 confidence in SAY data
```

#### Task Integration

- **Input**: ExperimentPlan from E1, customer segment from FoundersBrief
- **Output**: SAYEvidence for D4 triangulation
- **Context**: Parallel with D2, D3; all feed into D4

---

#### D2 - Observation Agent

| Attribute | Value |
|-----------|-------|
| **ID** | D2 |
| **Founder** | Pulse (CMO) |
| **Crew** | DiscoveryCrew |
| **Phase** | 1 (VPC Discovery) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | TavilySearchTool, ForumScraperTool, ReviewAnalysisTool, SocialListeningTool, TrendAnalysisTool | DO-indirect evidence collection |
| `reasoning` | True | Complex evidence synthesis |
| `inject_date` | True | Time-sensitive trend data |
| `max_iter` | 25 | Multiple search iterations |
| `temperature` | 0.3 | Factual research accuracy |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| TavilySearchTool | EXISTS | Web search for market research |
| ForumScraperTool | STUB | Reddit, Quora, industry forums |
| ReviewAnalysisTool | STUB | App store, G2, Capterra reviews |
| SocialListeningTool | STUB | Twitter/X, LinkedIn monitoring |
| TrendAnalysisTool | STUB | Google Trends, keyword volumes |

#### Output Schema

```python
class DOIndirectEvidence(BaseModel):
    forum_insights: List[ForumInsight]   # Forum discussions analyzed
    review_analysis: ReviewSummary       # Review sentiment and themes
    social_signals: List[SocialSignal]   # Social media indicators
    trend_data: TrendAnalysis            # Search trends, volumes
    behavioral_evidence: List[BehavioralEvidence]
    do_indirect_score: float             # 0-1 confidence in DO-indirect
```

#### Task Integration

- **Input**: Customer segment from FoundersBrief, ExperimentPlan from E1
- **Output**: DOIndirectEvidence for D4 triangulation
- **Context**: Parallel with D1, D3; all feed into D4

---

#### D3 - CTA Test Agent

| Attribute | Value |
|-----------|-------|
| **ID** | D3 |
| **Founder** | Pulse (CMO) |
| **Crew** | DiscoveryCrew |
| **Phase** | 1 (VPC Discovery) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | AnalyticsTool, ABTestTool | DO-direct evidence collection |
| `reasoning` | True | Experiment result analysis |
| `inject_date` | True | Campaign timestamps |
| `max_iter` | 20 | Test iteration cycles |
| `temperature` | 0.3 | Precise measurement |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| AnalyticsTool | STUB | Track conversions, engagement |
| ABTestTool | STUB | Run A/B experiments |

#### Output Schema

```python
class DODirectEvidence(BaseModel):
    experiments_run: List[ExperimentResult]
    landing_page_metrics: LandingPageMetrics
    ad_performance: AdPerformance
    conversion_rates: Dict[str, float]
    cta_click_rates: Dict[str, float]
    signup_rates: Dict[str, float]
    do_direct_score: float               # 0-1 confidence in DO-direct
```

#### Task Integration

- **Input**: ExperimentPlan from E1, test artifacts from BuildCrew
- **Output**: DODirectEvidence for D4 triangulation
- **Context**: Parallel with D1, D2; all feed into D4

---

#### D4 - Evidence Triangulation Agent

| Attribute | Value |
|-----------|-------|
| **ID** | D4 |
| **Founder** | Guardian (CGO) |
| **Crew** | DiscoveryCrew |
| **Phase** | 1 (VPC Discovery) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | LearningCardTool, LearningCaptureTool | Evidence synthesis and capture |
| `reasoning` | True | Complex multi-source synthesis |
| `inject_date` | True | Timestamp learnings |
| `max_iter` | 20 | Thorough triangulation |
| `temperature` | 0.4 | Balanced synthesis |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| LearningCardTool | STUB | Generate Learning Card artifacts |
| LearningCaptureTool | EXISTS | Persist learnings to flywheel |

#### Output Schema

```python
class EvidenceSynthesis(BaseModel):
    say_evidence: SAYEvidence            # From D1
    do_indirect_evidence: DOIndirectEvidence  # From D2
    do_direct_evidence: DODirectEvidence # From D3
    triangulation_matrix: TriangulationMatrix
    say_do_alignment: float              # -1 to 1 (conflict to alignment)
    confidence_scores: ConfidenceScores
    learning_cards: List[LearningCard]   # Captured learnings
    key_insights: List[Insight]
    recommendations: List[Recommendation]
```

#### Task Integration

- **Input**: SAYEvidence (D1), DOIndirectEvidence (D2), DODirectEvidence (D3)
- **Output**: EvidenceSynthesis for CustomerProfileCrew
- **Context**: Final agent in DiscoveryCrew; feeds CustomerProfileCrew

---

### CustomerProfileCrew (6 agents)

#### J1 - JTBD Researcher Agent

| Attribute | Value |
|-----------|-------|
| **ID** | J1 |
| **Founder** | Sage (CSO) |
| **Crew** | CustomerProfileCrew |
| **Phase** | 1 (VPC Discovery) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | TavilySearchTool, ForumScraperTool, ReviewAnalysisTool | JTBD discovery |
| `reasoning` | True | Complex job identification |
| `inject_date` | True | Market context |
| `max_iter` | 25 | Thorough research |
| `temperature` | 0.3 | Factual accuracy |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| TavilySearchTool | EXISTS | Web research on job contexts |
| ForumScraperTool | STUB | Community discussions on jobs |
| ReviewAnalysisTool | STUB | What jobs reviews mention |

#### Output Schema

```python
class JTBDResearch(BaseModel):
    functional_jobs: List[Job]           # Tasks to accomplish
    emotional_jobs: List[Job]            # Feelings to achieve
    social_jobs: List[Job]               # How they want to be perceived
    supporting_jobs: List[Job]           # Context jobs (buy, learn, etc.)
    job_contexts: List[JobContext]       # When/where jobs arise
    job_evidence: Dict[str, List[Evidence]]
```

#### Task Integration

- **Input**: EvidenceSynthesis from D4, customer segment
- **Output**: JTBDResearch for J2 ranking
- **Context**: First agent in CustomerProfileCrew; parallel with PAIN_RES, GAIN_RES

---

#### J2 - Job Ranking Agent

| Attribute | Value |
|-----------|-------|
| **ID** | J2 |
| **Founder** | Sage (CSO) |
| **Crew** | CustomerProfileCrew |
| **Phase** | 1 (VPC Discovery) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | `[]` | Pure LLM - ranking logic |
| `reasoning` | True | Complex prioritization |
| `inject_date` | True | Market timing |
| `max_iter` | 15 | Focused ranking |
| `temperature` | 0.4 | Balanced evaluation |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| (none) | N/A | Pure LLM agent - ranking through reasoning |

#### Output Schema

```python
class RankedJobs(BaseModel):
    ranked_jobs: List[RankedJob]         # Ordered by importance
    ranking_methodology: str             # How ranking was done
    evidence_basis: Dict[str, Evidence]  # Supporting evidence per job
    top_3_jobs: List[Job]                # Priority jobs for Value Map
```

#### Task Integration

- **Input**: JTBDResearch from J1
- **Output**: RankedJobs for ValueDesignCrew
- **Context**: Follows J1; outputs to V1

---

#### PAIN_RES - Pain Researcher Agent

| Attribute | Value |
|-----------|-------|
| **ID** | PAIN_RES |
| **Founder** | Sage (CSO) |
| **Crew** | CustomerProfileCrew |
| **Phase** | 1 (VPC Discovery) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | TavilySearchTool, ForumScraperTool, ReviewAnalysisTool | Pain discovery |
| `reasoning` | True | Pain identification |
| `inject_date` | True | Current pain landscape |
| `max_iter` | 25 | Thorough research |
| `temperature` | 0.3 | Factual accuracy |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| TavilySearchTool | EXISTS | Web research on pain points |
| ForumScraperTool | STUB | Community complaints |
| ReviewAnalysisTool | STUB | Negative review analysis |

#### Output Schema

```python
class PainResearch(BaseModel):
    undesired_outcomes: List[Pain]       # Bad results they want to avoid
    obstacles: List[Pain]                # Things preventing job completion
    risks: List[Pain]                    # Fears and concerns
    pain_evidence: Dict[str, List[Evidence]]
    pain_severity_indicators: Dict[str, float]
```

#### Task Integration

- **Input**: EvidenceSynthesis from D4, customer segment
- **Output**: PainResearch for PAIN_RANK
- **Context**: Parallel with J1, GAIN_RES; outputs to PAIN_RANK

---

#### PAIN_RANK - Pain Ranking Agent

| Attribute | Value |
|-----------|-------|
| **ID** | PAIN_RANK |
| **Founder** | Sage (CSO) |
| **Crew** | CustomerProfileCrew |
| **Phase** | 1 (VPC Discovery) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | `[]` | Pure LLM - ranking logic |
| `reasoning` | True | Severity assessment |
| `inject_date` | True | Current context |
| `max_iter` | 15 | Focused ranking |
| `temperature` | 0.4 | Balanced evaluation |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| (none) | N/A | Pure LLM agent - ranking through reasoning |

#### Output Schema

```python
class RankedPains(BaseModel):
    ranked_pains: List[RankedPain]       # Ordered by severity
    ranking_methodology: str
    evidence_basis: Dict[str, Evidence]
    top_3_pains: List[Pain]              # Priority pains for Value Map
    extreme_pains: List[Pain]            # "Must solve" pains
```

#### Task Integration

- **Input**: PainResearch from PAIN_RES
- **Output**: RankedPains for ValueDesignCrew
- **Context**: Follows PAIN_RES; outputs to V2

---

#### GAIN_RES - Gain Researcher Agent

| Attribute | Value |
|-----------|-------|
| **ID** | GAIN_RES |
| **Founder** | Sage (CSO) |
| **Crew** | CustomerProfileCrew |
| **Phase** | 1 (VPC Discovery) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | TavilySearchTool, ForumScraperTool, ReviewAnalysisTool | Gain discovery |
| `reasoning` | True | Gain identification |
| `inject_date` | True | Current market desires |
| `max_iter` | 25 | Thorough research |
| `temperature` | 0.3 | Factual accuracy |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| TavilySearchTool | EXISTS | Web research on desired outcomes |
| ForumScraperTool | STUB | Community wishlists |
| ReviewAnalysisTool | STUB | Positive review analysis |

#### Output Schema

```python
class GainResearch(BaseModel):
    required_gains: List[Gain]           # Expected minimum outcomes
    expected_gains: List[Gain]           # Standard desires
    desired_gains: List[Gain]            # Nice-to-haves
    unexpected_gains: List[Gain]         # Delighters
    gain_evidence: Dict[str, List[Evidence]]
```

#### Task Integration

- **Input**: EvidenceSynthesis from D4, customer segment
- **Output**: GainResearch for GAIN_RANK
- **Context**: Parallel with J1, PAIN_RES; outputs to GAIN_RANK

---

#### GAIN_RANK - Gain Ranking Agent

| Attribute | Value |
|-----------|-------|
| **ID** | GAIN_RANK |
| **Founder** | Sage (CSO) |
| **Crew** | CustomerProfileCrew |
| **Phase** | 1 (VPC Discovery) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | `[]` | Pure LLM - ranking logic |
| `reasoning` | True | Importance assessment |
| `inject_date` | True | Current context |
| `max_iter` | 15 | Focused ranking |
| `temperature` | 0.4 | Balanced evaluation |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| (none) | N/A | Pure LLM agent - ranking through reasoning |

#### Output Schema

```python
class RankedGains(BaseModel):
    ranked_gains: List[RankedGain]       # Ordered by relevance
    ranking_methodology: str
    evidence_basis: Dict[str, Evidence]
    top_3_gains: List[Gain]              # Priority gains for Value Map
    essential_gains: List[Gain]          # "Must have" gains
```

#### Task Integration

- **Input**: GainResearch from GAIN_RES
- **Output**: RankedGains for ValueDesignCrew
- **Context**: Follows GAIN_RES; outputs to V3

---

### ValueDesignCrew (3 agents)

#### V1 - Solution Designer Agent

| Attribute | Value |
|-----------|-------|
| **ID** | V1 |
| **Founder** | Forge (CTO) |
| **Crew** | ValueDesignCrew |
| **Phase** | 1 (VPC Discovery) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | CanvasBuilderTool | Value Map design |
| `reasoning` | True | Creative solution design |
| `inject_date` | True | Current technology context |
| `max_iter` | 25 | Iterative design |
| `temperature` | 0.7 | Creative exploration |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| CanvasBuilderTool | STUB | Generate VPC visualizations |

#### Output Schema

```python
class ProductsAndServices(BaseModel):
    products: List[Product]              # What we offer
    services: List[Service]              # Supporting services
    digital_products: List[DigitalProduct]
    physical_products: List[PhysicalProduct]
    job_coverage: Dict[str, List[str]]   # Which jobs each addresses
```

#### Task Integration

- **Input**: RankedJobs from J2, EvidenceSynthesis from D4
- **Output**: ProductsAndServices for FitAssessmentCrew
- **Context**: First agent in ValueDesignCrew; parallel with V2, V3

---

#### V2 - Pain Reliever Designer Agent

| Attribute | Value |
|-----------|-------|
| **ID** | V2 |
| **Founder** | Forge (CTO) |
| **Crew** | ValueDesignCrew |
| **Phase** | 1 (VPC Discovery) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | CanvasBuilderTool | Pain reliever design |
| `reasoning` | True | Creative pain relief design |
| `inject_date` | True | Current solution landscape |
| `max_iter` | 25 | Iterative design |
| `temperature` | 0.7 | Creative exploration |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| CanvasBuilderTool | STUB | Generate VPC visualizations |

#### Output Schema

```python
class PainRelievers(BaseModel):
    relievers: List[PainReliever]        # How we address pains
    pain_coverage: Dict[str, List[str]]  # Which pains each addresses
    relief_intensity: Dict[str, str]     # "eliminates", "reduces", "minimizes"
    evidence_basis: Dict[str, Evidence]
```

#### Task Integration

- **Input**: RankedPains from PAIN_RANK, EvidenceSynthesis from D4
- **Output**: PainRelievers for FitAssessmentCrew
- **Context**: Parallel with V1, V3; outputs to FIT_SCORE

---

#### V3 - Gain Creator Designer Agent

| Attribute | Value |
|-----------|-------|
| **ID** | V3 |
| **Founder** | Forge (CTO) |
| **Crew** | ValueDesignCrew |
| **Phase** | 1 (VPC Discovery) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | CanvasBuilderTool | Gain creator design |
| `reasoning` | True | Creative gain creation design |
| `inject_date` | True | Current opportunity landscape |
| `max_iter` | 25 | Iterative design |
| `temperature` | 0.7 | Creative exploration |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| CanvasBuilderTool | STUB | Generate VPC visualizations |

#### Output Schema

```python
class GainCreators(BaseModel):
    creators: List[GainCreator]          # How we create gains
    gain_coverage: Dict[str, List[str]]  # Which gains each addresses
    creation_intensity: Dict[str, str]   # "creates", "enhances", "enables"
    evidence_basis: Dict[str, Evidence]
```

#### Task Integration

- **Input**: RankedGains from GAIN_RANK, EvidenceSynthesis from D4
- **Output**: GainCreators for FitAssessmentCrew
- **Context**: Parallel with V1, V2; outputs to FIT_SCORE

---

### WTPCrew (2 agents)

#### W1 - Pricing Experiment Agent

| Attribute | Value |
|-----------|-------|
| **ID** | W1 |
| **Founder** | Ledger (CFO) |
| **Crew** | WTPCrew |
| **Phase** | 1 (VPC Discovery) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | ABTestTool, AnalyticsTool | WTP experiments |
| `reasoning` | True | Pricing strategy analysis |
| `inject_date` | True | Current market pricing |
| `max_iter` | 20 | Multiple pricing tests |
| `temperature` | 0.3 | Precise measurement |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| ABTestTool | STUB | Price point A/B tests |
| AnalyticsTool | STUB | Track conversion by price |

#### Output Schema

```python
class WTPExperiments(BaseModel):
    van_westendorp: VanWestendorpResults  # Price sensitivity analysis
    conjoint_analysis: ConjointResults    # Feature/price tradeoffs
    ab_test_results: List[PriceABTest]
    optimal_price_range: PriceRange
    price_elasticity: float
```

#### Task Integration

- **Input**: ProductsAndServices from V1, customer segment
- **Output**: WTPExperiments for W2
- **Context**: First agent in WTPCrew; outputs to W2

---

#### W2 - Payment Test Agent

| Attribute | Value |
|-----------|-------|
| **ID** | W2 |
| **Founder** | Ledger (CFO) |
| **Crew** | WTPCrew |
| **Phase** | 1 (VPC Discovery) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | AnalyticsTool | Payment behavior tracking |
| `reasoning` | True | Payment pattern analysis |
| `inject_date` | True | Current payment trends |
| `max_iter` | 20 | Multiple payment tests |
| `temperature` | 0.3 | Precise measurement |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| AnalyticsTool | STUB | Track payment completions |

#### Output Schema

```python
class PaymentTests(BaseModel):
    preorder_results: PreorderResults
    crowdfunding_signals: CrowdfundingSignals
    loi_results: LOIResults              # Letters of Intent
    actual_payment_rate: float
    payment_friction_analysis: FrictionAnalysis
    wtp_confidence: float                # 0-1 confidence in WTP
```

#### Task Integration

- **Input**: WTPExperiments from W1, test artifacts
- **Output**: PaymentTests for FitAssessmentCrew
- **Context**: Follows W1; outputs to FIT_SCORE

---

### FitAssessmentCrew (2 agents)

#### FIT_SCORE - Fit Analyst Agent

| Attribute | Value |
|-----------|-------|
| **ID** | FIT_SCORE |
| **Founder** | Compass (CPO) |
| **Crew** | FitAssessmentCrew |
| **Phase** | 1 (VPC Discovery) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | MethodologyCheckTool | Fit scoring methodology |
| `reasoning` | True | Complex fit analysis |
| `inject_date` | True | Current context |
| `max_iter` | 20 | Thorough scoring |
| `temperature` | 0.3 | Precise scoring |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| MethodologyCheckTool | EXISTS | Validate VPD compliance |

#### Output Schema

```python
class FitAssessment(BaseModel):
    customer_profile: CustomerProfile     # Jobs, Pains, Gains
    value_map: ValueMap                   # Products, Relievers, Creators
    fit_score: int                        # 0-100
    job_coverage: float                   # % of top jobs addressed
    pain_coverage: float                  # % of top pains addressed
    gain_coverage: float                  # % of top gains addressed
    fit_analysis: str                     # Detailed explanation
    gaps: List[Gap]                       # Uncovered areas
    strengths: List[Strength]             # Strong alignments
    wtp_validation: WTPValidation         # From W1, W2
    recommendation: str                   # "proceed" or "iterate"
```

#### Task Integration

- **Input**: All CustomerProfileCrew outputs, all ValueDesignCrew outputs, WTPCrew outputs
- **Output**: FitAssessment for FIT_ROUTE
- **Context**: First agent in FitAssessmentCrew; triggers `approve_discovery_output` HITL (Stage B)

---

#### FIT_ROUTE - Iteration Router Agent

| Attribute | Value |
|-----------|-------|
| **ID** | FIT_ROUTE |
| **Founder** | Compass (CPO) |
| **Crew** | FitAssessmentCrew |
| **Phase** | 1 (VPC Discovery) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | `[]` | Pure LLM - routing decision |
| `reasoning` | True | Complex routing logic |
| `inject_date` | True | Current context |
| `max_iter` | 15 | Focused routing |
| `temperature` | 0.2 | Deterministic routing |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| (none) | N/A | Pure LLM agent - routing through reasoning |

#### Output Schema

```python
class IterationRouting(BaseModel):
    fit_score: int                        # From FIT_SCORE
    threshold_met: bool                   # fit_score >= 70
    route_decision: str                   # "proceed_phase_2" or "iterate_crew_X"
    iteration_target: Optional[str]       # Which crew to revisit
    iteration_focus: Optional[str]        # What to improve
    iteration_count: int                  # How many iterations so far
    max_iterations_warning: bool          # Approaching limit
```

#### Task Integration

- **Input**: FitAssessment from FIT_SCORE
- **Output**: IterationRouting for flow control
- **Context**: Final agent in Phase 1; routes to Phase 2 or back to iteration

---

## Phase 2: Desirability

**Flow**: `DesirabilityFlow`
**Crews**: BuildCrew, GrowthCrew, GovernanceCrew
**Agents**: 9

### BuildCrew (3 agents)

#### F1 - UX/UI Designer Agent

| Attribute | Value |
|-----------|-------|
| **ID** | F1 |
| **Founder** | Forge (CTO) |
| **Crew** | BuildCrew |
| **Phase** | 2 (Desirability) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | ComponentLibraryScraperTool | Design asset access |
| `reasoning` | True | Creative design thinking |
| `inject_date` | True | Current design trends |
| `max_iter` | 25 | Iterative design |
| `temperature` | 0.8 | High creativity |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| ComponentLibraryScraperTool | STUB | Access shadcn/ui components |

#### Output Schema

```python
class DesignArtifacts(BaseModel):
    wireframes: List[Wireframe]
    mockups: List[Mockup]
    component_specs: List[ComponentSpec]
    design_rationale: str
    conversion_optimization: ConversionOptimization
```

#### Task Integration

- **Input**: ValueMap from Phase 1, EvidenceSynthesis
- **Output**: DesignArtifacts for F2
- **Context**: First agent in BuildCrew; outputs to F2

---

#### F2 - Frontend Developer Agent

| Attribute | Value |
|-----------|-------|
| **ID** | F2 |
| **Founder** | Forge (CTO) |
| **Crew** | BuildCrew |
| **Phase** | 2 (Desirability) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | LandingPageGeneratorTool, CodeValidatorTool | LP generation |
| `reasoning` | True | Code generation logic |
| `inject_date` | True | Current framework versions |
| `max_iter` | 25 | Iterative development |
| `temperature` | 0.5 | Balanced code generation |
| `output_pydantic` | LandingPageBuild | Structured output validation |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| LandingPageGeneratorTool | LLM-Based | Generate landing page HTML with Tailwind CSS |
| CodeValidatorTool | EXISTS | Validate generated code structure |

> **Note**: LandingPageGeneratorTool uses template-based generation with LLM copy. See [tool-specifications.md](./tool-specifications.md#landingpagegeneratortool) for full schema.

#### Output Schema

```python
class LandingPageBuild(BaseModel):
    html: str                             # Complete HTML with Tailwind
    sections: List[str]                   # Sections included (hero, features, etc.)
    tracking_enabled: bool                # Whether analytics JS included
    form_enabled: bool                    # Whether signup form included
    validation_result: ValidationResult
    build_status: str                     # "success" or "error"
    preview_url: Optional[str]
```

#### Task Integration

- **Input**: DesignArtifacts from F1
- **Output**: LandingPageBuild for F3
- **Context**: Follows F1; outputs to F3

---

#### F3 - Backend Developer Agent

| Attribute | Value |
|-----------|-------|
| **ID** | F3 |
| **Founder** | Forge (CTO) |
| **Crew** | BuildCrew |
| **Phase** | 2 (Desirability) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | LandingPageDeploymentTool | Netlify deployment |
| `reasoning` | True | Deployment logic |
| `inject_date` | True | Current infrastructure |
| `max_iter` | 20 | Deployment iterations |
| `temperature` | 0.3 | Precise deployment |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| LandingPageDeploymentTool | EXISTS | Deploy to Netlify |

#### Output Schema

```python
class DeploymentResult(BaseModel):
    deploy_id: str
    site_url: str
    deploy_status: str                    # "success" or "failed"
    ssl_status: str
    analytics_configured: bool
    tracking_pixels: List[str]
```

#### Task Integration

- **Input**: LandingPageBuild from F2
- **Output**: DeploymentResult for GrowthCrew
- **Context**: Final agent in BuildCrew; outputs to P1

---

### GrowthCrew (3 agents)

#### P1 - Ad Creative Agent

| Attribute | Value |
|-----------|-------|
| **ID** | P1 |
| **Founder** | Pulse (CMO) |
| **Crew** | GrowthCrew |
| **Phase** | 2 (Desirability) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | AdCreativeGeneratorTool, AdPlatformTool | Creative generation + platform integration |
| `reasoning` | True | Creative ad generation |
| `inject_date` | True | Current ad trends |
| `max_iter` | 25 | Multiple creative variants |
| `temperature` | 0.8 | High creativity |
| `output_pydantic` | AdCreatives | Structured output validation |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| AdCreativeGeneratorTool | LLM-Based | Generate platform-specific ad copy variants |
| AdPlatformTool | STUB | Create and manage ad campaigns (Meta/Google) |

> **Note**: AdCreativeGeneratorTool enforces platform character limits. See [tool-specifications.md](./tool-specifications.md#adcreativegeneratortool) for constraints per platform.

#### Output Schema

```python
class AdCreatives(BaseModel):
    platform: str                         # meta | google | linkedin | tiktok
    ad_variants: List[AdVariant]          # Generated variants with platform constraints
    headlines: List[str]                  # Platform-appropriate headlines
    descriptions: List[str]               # Platform-appropriate descriptions
    ctas: List[str]                       # Call-to-action options
    character_counts_validated: bool      # All variants within limits
    targeting: TargetingConfig
    budget_allocation: BudgetAllocation
```

#### Task Integration

- **Input**: DeploymentResult from F3, customer segment
- **Output**: AdCreatives for P2
- **Context**: First agent in GrowthCrew; triggers `approve_campaign_launch` HITL

---

#### P2 - Communications Agent

| Attribute | Value |
|-----------|-------|
| **ID** | P2 |
| **Founder** | Pulse (CMO) |
| **Crew** | GrowthCrew |
| **Phase** | 2 (Desirability) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | AdCreativeGeneratorTool, AdPlatformTool, BudgetGuardrailsTool | Creative iteration + execution + budget control |
| `reasoning` | True | Campaign optimization |
| `inject_date` | True | Current market context |
| `max_iter` | 25 | Campaign iterations |
| `temperature` | 0.6 | Balanced creativity |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| AdCreativeGeneratorTool | LLM-Based | Generate variant ad copy for A/B testing |
| AdPlatformTool | STUB | Execute and monitor campaigns (Meta/Google) |
| BudgetGuardrailsTool | EXISTS | Enforce spend limits with HITL approval |

> **Note**: P2 can generate new ad variants to replace underperforming creatives during campaign execution.

#### Output Schema

```python
class CampaignExecution(BaseModel):
    campaigns: List[Campaign]
    active_variants: List[AdVariant]      # Currently running ad variants
    daily_spend: Dict[str, float]
    total_spend: float
    budget_remaining: float               # From BudgetGuardrailsTool
    impressions: int
    clicks: int
    ctr: float
    cost_per_click: float
```

#### Task Integration

- **Input**: AdCreatives from P1 (after HITL approval)
- **Output**: CampaignExecution for P3
- **Context**: Follows P1; triggers `approve_spend_increase` HITL if needed

---

#### P3 - Analytics Agent

| Attribute | Value |
|-----------|-------|
| **ID** | P3 |
| **Founder** | Pulse (CMO) |
| **Crew** | GrowthCrew |
| **Phase** | 2 (Desirability) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | AnalyticsTool | Metrics analysis |
| `reasoning` | True | Complex signal analysis |
| `inject_date` | True | Real-time data |
| `max_iter` | 20 | Analysis iterations |
| `temperature` | 0.2 | Precise measurement |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| AnalyticsTool | STUB | Track and analyze metrics |

#### Output Schema

```python
class DesirabilitySignal(BaseModel):
    signal_strength: str                  # "WEAK", "MODERATE", "STRONG_COMMITMENT"
    metrics: DesirabilityMetrics
    conversion_funnel: ConversionFunnel
    statistical_significance: bool
    confidence_interval: Tuple[float, float]
    recommendation: str
```

#### Task Integration

- **Input**: CampaignExecution from P2, DeploymentResult from F3
- **Output**: DesirabilitySignal for GovernanceCrew
- **Context**: Final agent in GrowthCrew; triggers `approve_desirability_gate` HITL

---

### GovernanceCrew (3 agents)

#### G1 - QA Agent

| Attribute | Value |
|-----------|-------|
| **ID** | G1 |
| **Founder** | Guardian (CGO) |
| **Crew** | GovernanceCrew |
| **Phase** | 2 (Desirability) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | MethodologyCheckTool, GuardianReviewTool | QA validation |
| `reasoning` | True | Complex QA logic |
| `inject_date` | True | Current standards |
| `max_iter` | 20 | Thorough validation |
| `temperature` | 0.1 | Strict validation |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| MethodologyCheckTool | EXISTS | Validate VPD compliance |
| GuardianReviewTool | EXISTS | Governance review checklist |

#### Output Schema

```python
class QAReport(BaseModel):
    methodology_compliance: bool
    quality_score: float                  # 0-1
    issues_found: List[Issue]
    recommendations: List[str]
    gate_ready: bool
```

#### Task Integration

- **Input**: DesirabilitySignal from P3, all Phase 2 artifacts
- **Output**: QAReport for G2
- **Context**: First agent in GovernanceCrew; outputs to G2

---

#### G2 - Security Agent

| Attribute | Value |
|-----------|-------|
| **ID** | G2 |
| **Founder** | Guardian (CGO) |
| **Crew** | GovernanceCrew |
| **Phase** | 2 (Desirability) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | PrivacyGuardTool | PII protection |
| `reasoning` | True | Security analysis |
| `inject_date` | True | Current compliance requirements |
| `max_iter` | 15 | Focused security check |
| `temperature` | 0.1 | Strict security |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| PrivacyGuardTool | EXISTS | PII detection and scrubbing |

#### Output Schema

```python
class SecurityReport(BaseModel):
    pii_found: bool
    pii_locations: List[PIILocation]
    scrubbing_performed: bool
    compliance_status: str                # "compliant", "needs_review"
    security_issues: List[SecurityIssue]
```

#### Task Integration

- **Input**: QAReport from G1, all Phase 2 data
- **Output**: SecurityReport for G3
- **Context**: Follows G1; outputs to G3

---

#### G3 - Audit Agent

| Attribute | Value |
|-----------|-------|
| **ID** | G3 |
| **Founder** | Guardian (CGO) |
| **Crew** | GovernanceCrew |
| **Phase** | 2 (Desirability) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | LearningCaptureTool | Audit trail persistence |
| `reasoning` | True | Audit analysis |
| `inject_date` | True | Timestamp audit |
| `max_iter` | 15 | Focused audit |
| `temperature` | 0.1 | Strict audit |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| LearningCaptureTool | EXISTS | Persist audit trail |

#### Output Schema

```python
class AuditReport(BaseModel):
    phase_summary: PhaseSummary
    decisions_logged: List[Decision]
    evidence_chain: EvidenceChain
    compliance_attestation: bool
    audit_timestamp: datetime
    flywheel_captured: bool
```

#### Task Integration

- **Input**: QAReport from G1, SecurityReport from G2
- **Output**: AuditReport for Phase 3
- **Context**: Final agent in Phase 2 GovernanceCrew

---

## Phase 3: Feasibility

**Flow**: `FeasibilityFlow`
**Crews**: BuildCrew (reused), GovernanceCrew (reused)
**Agents**: 5

### BuildCrew (3 agents, reused with different context)

#### F1 - UX/UI Designer Agent (Feasibility Context)

| Attribute | Value |
|-----------|-------|
| **ID** | F1 |
| **Founder** | Forge (CTO) |
| **Crew** | BuildCrew |
| **Phase** | 3 (Feasibility) |

#### Configuration

Same as Phase 2, but with feasibility context.

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | ComponentLibraryScraperTool | Requirements analysis |
| `reasoning` | True | Feature mapping |
| `inject_date` | True | Current tech landscape |
| `max_iter` | 20 | Feature analysis |
| `temperature` | 0.5 | Balanced analysis |

#### Output Schema (Feasibility Context)

```python
class FeatureRequirements(BaseModel):
    features: List[Feature]
    ui_complexity: str                    # "low", "medium", "high"
    component_requirements: List[ComponentRequirement]
    design_system_gaps: List[str]
```

#### Task Integration

- **Input**: ValueMap from Phase 1, DesirabilitySignal from Phase 2
- **Output**: FeatureRequirements for F2
- **Context**: Feature scoping for feasibility assessment

---

#### F2 - Frontend Developer Agent (Feasibility Context)

| Attribute | Value |
|-----------|-------|
| **ID** | F2 |
| **Founder** | Forge (CTO) |
| **Crew** | BuildCrew |
| **Phase** | 3 (Feasibility) |

#### Configuration

Same as Phase 2, but with feasibility context.

#### Output Schema (Feasibility Context)

```python
class FrontendFeasibility(BaseModel):
    feasibility_score: float              # 0-1
    complexity_assessment: str
    timeline_estimate: str
    tech_stack_compatibility: bool
    risks: List[TechRisk]
```

#### Task Integration

- **Input**: FeatureRequirements from F1
- **Output**: FrontendFeasibility for F3
- **Context**: Frontend feasibility assessment

---

#### F3 - Backend Developer Agent (Feasibility Context)

| Attribute | Value |
|-----------|-------|
| **ID** | F3 |
| **Founder** | Forge (CTO) |
| **Crew** | BuildCrew |
| **Phase** | 3 (Feasibility) |

#### Configuration

Same as Phase 2, but with feasibility context.

#### Output Schema (Feasibility Context)

```python
class FeasibilitySignal(BaseModel):
    signal: str                           # "RED", "YELLOW", "GREEN"
    frontend_feasibility: FrontendFeasibility
    backend_feasibility: BackendFeasibility
    integration_risks: List[IntegrationRisk]
    resource_requirements: ResourceRequirements
    timeline_estimate: TimelineEstimate
    confidence: float                     # 0-1
```

#### Task Integration

- **Input**: FrontendFeasibility from F2
- **Output**: FeasibilitySignal for GovernanceCrew
- **Context**: Final feasibility assessment; triggers `approve_feasibility_gate` HITL

---

### GovernanceCrew (2 agents)

#### G1 - QA Agent (Phase 3)

Same as Phase 2 G1, validating feasibility artifacts.

#### G2 - Security Agent (Phase 3)

Same as Phase 2 G2, reviewing architecture security.

---

## Phase 4: Viability

**Flow**: `ViabilityFlow`
**Crews**: FinanceCrew, SynthesisCrew, GovernanceCrew
**Agents**: 9

### FinanceCrew (3 agents)

#### L1 - Financial Controller Agent

| Attribute | Value |
|-----------|-------|
| **ID** | L1 |
| **Founder** | Ledger (CFO) |
| **Crew** | FinanceCrew |
| **Phase** | 4 (Viability) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | UnitEconomicsModelsTool, BusinessModelClassifierTool, FinancialDataTool | Financial analysis |
| `reasoning` | True | Complex financial modeling |
| `inject_date` | True | Current market rates |
| `max_iter` | 25 | Iterative modeling |
| `temperature` | 0.2 | Precise calculations |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| UnitEconomicsModelsTool | EXISTS | Calculate CAC, LTV, margins |
| BusinessModelClassifierTool | EXISTS | Classify business model type |
| FinancialDataTool | STUB | Fetch financial benchmarks |

#### Output Schema

```python
class UnitEconomics(BaseModel):
    cac: float                            # Customer Acquisition Cost
    ltv: float                            # Lifetime Value
    ltv_cac_ratio: float                  # Target: > 3.0
    payback_period_months: int
    gross_margin: float
    contribution_margin: float
    business_model_type: str
    benchmark_comparison: BenchmarkComparison
```

#### Task Integration

- **Input**: DesirabilitySignal from Phase 2, FeasibilitySignal from Phase 3
- **Output**: UnitEconomics for L2, L3
- **Context**: First agent in FinanceCrew

---

#### L2 - Legal & Compliance Agent

| Attribute | Value |
|-----------|-------|
| **ID** | L2 |
| **Founder** | Ledger (CFO) |
| **Crew** | FinanceCrew |
| **Phase** | 4 (Viability) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | TavilySearchTool | Regulatory research |
| `reasoning` | True | Legal analysis |
| `inject_date` | True | Current regulations |
| `max_iter` | 20 | Compliance research |
| `temperature` | 0.2 | Precise compliance |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| TavilySearchTool | EXISTS | Research regulatory requirements |

#### Output Schema

```python
class ComplianceReport(BaseModel):
    regulatory_requirements: List[Requirement]
    compliance_gaps: List[Gap]
    licensing_needed: List[License]
    data_privacy_requirements: List[Requirement]
    estimated_compliance_cost: float
    compliance_timeline: str
```

#### Task Integration

- **Input**: UnitEconomics from L1, business context
- **Output**: ComplianceReport for L3
- **Context**: Parallel with L1 analysis

---

#### L3 - Economics Reviewer Agent

| Attribute | Value |
|-----------|-------|
| **ID** | L3 |
| **Founder** | Ledger (CFO) |
| **Crew** | FinanceCrew |
| **Phase** | 4 (Viability) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | BudgetGuardrailsTool | Budget validation |
| `reasoning` | True | Economic review |
| `inject_date` | True | Current market conditions |
| `max_iter` | 20 | Thorough review |
| `temperature` | 0.2 | Precise validation |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| BudgetGuardrailsTool | EXISTS | Validate budget constraints |

#### Output Schema

```python
class ViabilitySignal(BaseModel):
    signal: str                           # "UNPROFITABLE", "MARGINAL", "PROFITABLE"
    unit_economics: UnitEconomics
    compliance_report: ComplianceReport
    runway_projection: RunwayProjection
    break_even_analysis: BreakEvenAnalysis
    investment_required: float
    risk_assessment: RiskAssessment
    confidence: float                     # 0-1
```

#### Task Integration

- **Input**: UnitEconomics from L1, ComplianceReport from L2
- **Output**: ViabilitySignal for SynthesisCrew
- **Context**: Final agent in FinanceCrew; triggers `approve_viability_gate` HITL

---

### SynthesisCrew (3 agents)

#### C1 - Product PM Agent

| Attribute | Value |
|-----------|-------|
| **ID** | C1 |
| **Founder** | Compass (CPO) |
| **Crew** | SynthesisCrew |
| **Phase** | 4 (Viability) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | LearningRetrievalTool | Historical context |
| `reasoning` | True | Complex synthesis |
| `inject_date` | True | Current context |
| `max_iter` | 25 | Thorough synthesis |
| `temperature` | 0.4 | Balanced synthesis |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| LearningRetrievalTool | EXISTS | Query past learnings |

#### Output Schema

```python
class EvidenceSynthesis(BaseModel):
    desirability_summary: DesirabilitySignal
    feasibility_summary: FeasibilitySignal
    viability_summary: ViabilitySignal
    overall_confidence: float             # 0-1
    key_learnings: List[Learning]
    pivot_options: List[PivotOption]
    proceed_rationale: str
    recommendation: str                   # "pivot", "proceed", "stop"
```

#### Task Integration

- **Input**: All Phase 1-4 outputs
- **Output**: EvidenceSynthesis for C2
- **Context**: First agent in SynthesisCrew

---

#### C2 - Human Approval Agent

| Attribute | Value |
|-----------|-------|
| **ID** | C2 |
| **Founder** | Compass (CPO) |
| **Crew** | SynthesisCrew |
| **Phase** | 4 (Viability) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | ViabilityApprovalTool | HITL orchestration |
| `reasoning` | True | Decision framing |
| `inject_date` | True | Decision timestamp |
| `max_iter` | 15 | Focused decision |
| `temperature` | 0.3 | Clear decision framing |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| ViabilityApprovalTool | STUB | Orchestrate final decision |

#### Output Schema

```python
class HumanDecisionRequest(BaseModel):
    synthesis: EvidenceSynthesis
    decision_options: List[DecisionOption]
    evidence_summary: str
    risk_summary: str
    timeline_implications: Dict[str, str]
    decision_required_by: datetime
```

#### Task Integration

- **Input**: EvidenceSynthesis from C1
- **Output**: HumanDecisionRequest for HITL
- **Context**: Triggers `request_human_decision` HITL

---

#### C3 - Roadmap Writer Agent

| Attribute | Value |
|-----------|-------|
| **ID** | C3 |
| **Founder** | Compass (CPO) |
| **Crew** | SynthesisCrew |
| **Phase** | 4 (Viability) |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | LearningCaptureTool | Document learnings |
| `reasoning` | True | Roadmap planning |
| `inject_date` | True | Planning timeline |
| `max_iter` | 20 | Thorough documentation |
| `temperature` | 0.5 | Balanced planning |

#### Tools Specification

| Tool | Status | Purpose |
|------|--------|---------|
| LearningCaptureTool | EXISTS | Persist learnings and decision |

#### Output Schema

```python
class ValidationRoadmap(BaseModel):
    decision: str                         # "pivot", "proceed", "stop"
    next_steps: List[NextStep]
    pivot_direction: Optional[PivotDirection]
    proceed_milestones: Optional[List[Milestone]]
    learnings_captured: List[Learning]
    flywheel_contribution: FlywheelContribution
    final_report_url: str
```

#### Task Integration

- **Input**: Human decision from C2
- **Output**: ValidationRoadmap (final output)
- **Context**: Final agent in entire validation flow

---

### GovernanceCrew (3 agents)

#### G1, G2, G3 - Phase 4 Governance

Same as Phase 2 governance agents, providing final validation, security review, and audit trail for the complete validation cycle.

---

## Summary Statistics

> **Updated (2026-01-19)**: Agent count reduced from 45 to 43 due to Quick Start pivot. O1 and GV2 deleted.

| Metric | Count |
|--------|-------|
| **Total Agents** | 43 |
| **Pure LLM Agents** | 11 (no tools needed) |
| **Tool-Equipped Agents** | 32 |
| **Existing Tools (ready to wire)** | 13 |
| **Stub Tools (need implementation)** | 20 |

### Agents by Founder

| Founder | Agent Count |
|---------|-------------|
| Sage (CSO) | 11 |
| Forge (CTO) | 9 |
| Pulse (CMO) | 8 |
| Compass (CPO) | 6 |
| Guardian (CGO) | 7 |
| Ledger (CFO) | 5 |

### Agents by Tool Category

| Category | Agent Count | Notes |
|----------|-------------|-------|
| Research Tools | 8 | D2, J1, PAIN_RES, GAIN_RES, etc. |
| Build Tools | 6 | F1, F2, F3 |
| Growth Tools | 6 | P1, P2, P3, D3 |
| Finance Tools | 3 | L1, L2, L3 |
| Governance Tools | 6 | G1, G2, G3 |
| Pure LLM | 13 | No external tools |

---

## Related Documents

- [02-organization.md](../02-organization.md) - Agent Configuration Standard
- [tool-specifications.md](./tool-specifications.md) - Detailed tool specifications
- [tool-mapping.md](./tool-mapping.md) - Complete agent-to-tool mapping
- [observability-architecture.md](./observability-architecture.md) - Tool debugging and monitoring
- [agentic-tool-framework.md](./agentic-tool-framework.md) - Tool testing requirements
- Phase documents (04-08) - Phase-specific agent details

---

## Change Log

| Date | Change | Rationale |
|------|--------|-----------|
| 2026-01-10 | Updated F2 with LandingPageGeneratorTool, output_pydantic | Template-based LP with LLM copy generation |
| 2026-01-10 | Updated P1, P2 with AdCreativeGeneratorTool | Platform-specific ad copy with character limits |
| 2026-01-10 | Added output_pydantic to asset generation agents | Structured output validation |
| 2026-01-10 | Added observability-architecture.md reference | All tools now emit observability data |
| 2026-01-09 | Initial creation with all 45 agent specifications | Bullet-proof architecture before code implementation |
