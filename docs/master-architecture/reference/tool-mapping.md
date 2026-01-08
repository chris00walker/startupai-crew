---
purpose: Agent-to-tool assignments across all phases
status: active
last_reviewed: 2026-01-06
vpd_compliance: true
---

# Tool-to-Agent Mapping

This document defines which tools are assigned to which agents across all phases of the StartupAI validation engine.

> **Source of Truth**: This is the authoritative reference for tool assignments. Crew configurations (`agents.yaml`) should match these specifications.

---

## Tool Inventory

### Deployed Tools (Crew 1)

| Tool | Module | Description | Status |
|------|--------|-------------|--------|
| `TavilySearchTool` | `src/intake_crew/tools/web_search.py` | Web search via Tavily API | ✅ Deployed |
| `CustomerResearchTool` | `src/intake_crew/tools/web_search.py` | JTBD-focused customer research | ✅ Deployed |
| `MethodologyCheckTool` | `src/intake_crew/tools/methodology_check.py` | VPC structure validation | ✅ Deployed |

### Archived Tools (Available for Migration)

| Tool | Archive Location | Description | Target Crew |
|------|------------------|-------------|-------------|
| `LandingPageGeneratorTool` | `archive/flow-architecture/startupai/tools/landing_page.py` | Generate landing pages | Crew 2 (F2) |
| `LandingPageDeploymentTool` | `archive/flow-architecture/startupai/tools/landing_page_deploy.py` | Deploy to Netlify | Crew 2 (F2) |
| `GuardianReviewTool` | `archive/flow-architecture/startupai/tools/guardian_review.py` | Creative QA review | Crew 2 (G1) |
| `PrivacyGuardTool` | `archive/flow-architecture/startupai/tools/privacy_guard.py` | PII detection/stripping | Crew 2 (G2) |
| `UnitEconomicsModelsTool` | `archive/flow-architecture/startupai/tools/unit_economics_models.py` | 10 business model calculators | Crew 2 (L1) |
| `BusinessModelClassifierTool` | `archive/flow-architecture/startupai/tools/business_model_classifier.py` | Auto-classify business model | Crew 2 (L1) |
| `LearningCaptureTool` | `archive/flow-architecture/startupai/tools/learning_capture.py` | Flywheel learning storage | Crew 3 (C3) |
| `LearningRetrievalTool` | `archive/flow-architecture/startupai/tools/learning_retrieval.py` | RAG-based pattern retrieval | Phase 0 (O1) |
| `FlywheelInsightsTool` | `archive/flow-architecture/startupai/tools/flywheel_insights.py` | Query flywheel patterns | All Phases |
| `PolicyBanditTool` | `archive/flow-architecture/startupai/tools/policy_bandit.py` | UCB policy selection | Crew 2 |
| `ExperimentConfigResolverTool` | `archive/flow-architecture/startupai/tools/experiment_config_resolver.py` | Resolve experiment configs | Crew 2 |
| `BudgetGuardrailsTool` | `archive/flow-architecture/startupai/tools/budget_guardrails.py` | Budget limit enforcement | Crew 2 (L1) |
| `ViabilityApprovalTool` | `archive/flow-architecture/startupai/tools/viability_approval.py` | Viability gate checks | Crew 2 (L3) |
| `FinancialDataTool` | `archive/flow-architecture/startupai/tools/financial_data.py` | Financial data retrieval | Crew 2 (L1) |
| `CodeValidatorTool` | `archive/flow-architecture/startupai/tools/code_validator.py` | Code quality checks | Crew 2 (F3) |
| `AnonymizerTool` | `archive/flow-architecture/startupai/tools/anonymizer.py` | Data anonymization | Crew 3 (C3) |

### Planned Tools (Not Yet Built)

| Tool | Description | Target Agent |
|------|-------------|--------------|
| `ConversationTool` | Multi-turn dialogue management | Phase 0 (O1) |
| `NoteStructurerTool` | Structure free-form interview notes | Phase 0 (O1) |
| `InterviewSchedulerTool` | Schedule customer interviews | Phase 1 (D1) |
| `TranscriptionTool` | Transcribe interview recordings | Phase 1 (D1) |
| `InsightExtractorTool` | Extract insights from transcripts | Phase 1 (D1) |
| `BehaviorPatternTool` | Identify SAY vs DO discrepancies | Phase 1 (D1) |
| `SocialListeningTool` | Monitor social platforms | Phase 1 (D2) |
| `ForumScraperTool` | Extract forum discussions | Phase 1 (D2) |
| `ReviewAnalysisTool` | Analyze product reviews | Phase 1 (D2) |
| `TrendAnalysisTool` | Analyze search trends | Phase 1 (D2) |
| `LandingPageBuilderTool` | Create test landing pages | Phase 1 (D3) |
| `AdPlatformTool` | Run Meta/Google ads | Phase 1 (D3) |
| `AnalyticsTool` | Collect experiment metrics | Phase 1 (D3) |
| `ABTestTool` | Run split tests | Phase 1 (D3) |
| `TestCardTool` | Generate TBI Test Cards | Phase 1 (E1) |
| `LearningCardTool` | Capture TBI Learning Cards | Phase 1 (E1) |
| `InvokeCrewAIAutomationTool` | Crew-to-crew chaining | Crew 1 (G1), Crew 2 (G3) |

---

## Phase 0: Onboarding Agent Tools

| Agent ID | Agent Name | Founder | Tools |
|----------|------------|---------|-------|
| O1 | Founder Interview Agent | Sage | `ConversationTool`, `NoteStructurerTool`, `LearningRetrievalTool` |
| GV1 | Concept Validator Agent | Guardian | *(Pure LLM - no tools)* |
| GV2 | Intent Verification Agent | Guardian | *(Pure LLM - no tools)* |
| S1 | Brief Compiler Agent | Sage | *(Pure LLM - no tools)* |

**Notes:**
- O1 is the only Phase 0 agent requiring tools
- GV1/GV2/S1 use LLM reasoning for validation and synthesis

---

## Phase 1: VPC Discovery Agent Tools

### Segment Discovery Flow

| Agent ID | Agent Name | Founder | Tools |
|----------|------------|---------|-------|
| E1 | Experiment Designer | Sage | `TestCardTool`, `LearningCardTool`, `LearningRetrievalTool` |
| D1 | Customer Interview Agent | Sage | `InterviewSchedulerTool`, `TranscriptionTool`, `InsightExtractorTool`, `BehaviorPatternTool` |
| D2 | Observation Agent | Pulse | `SocialListeningTool`, `ForumScraperTool`, `ReviewAnalysisTool`, `TrendAnalysisTool` |
| D3 | CTA Test Agent | Pulse | `LandingPageBuilderTool`, `AdPlatformTool`, `AnalyticsTool`, `ABTestTool`, `TestCardTool`, `LearningCardTool` |
| D4 | Evidence Triangulation Agent | Guardian | *(Pure LLM - evidence synthesis)* |

### Jobs/Pains/Gains Discovery Flows

| Agent ID | Agent Name | Founder | Tools |
|----------|------------|---------|-------|
| J1 | JTBD Researcher | Sage | `TavilySearchTool`, `ForumScraperTool`, `ReviewAnalysisTool` |
| J2 | Job Ranking Agent | Sage | *(Pure LLM - ranking synthesis)* |
| P1 | Pain Researcher | Sage | `TavilySearchTool`, `ForumScraperTool`, `ReviewAnalysisTool` |
| P2 | Pain Ranking Agent | Sage | *(Pure LLM - ranking synthesis)* |
| G1 | Gain Researcher | Sage | `TavilySearchTool`, `ForumScraperTool`, `ReviewAnalysisTool` |
| G2 | Gain Ranking Agent | Sage | *(Pure LLM - ranking synthesis)* |

### Value Map & Fit Flows

| Agent ID | Agent Name | Founder | Tools |
|----------|------------|---------|-------|
| V1 | Solution Designer | Forge | *(Pure LLM - design synthesis)* |
| V2 | Pain Reliever Designer | Forge | *(Pure LLM - design synthesis)* |
| V3 | Gain Creator Designer | Forge | *(Pure LLM - design synthesis)* |
| W1 | Pricing Experiment Agent | Ledger | `ABTestTool`, `AnalyticsTool` |
| W2 | Payment Test Agent | Ledger | `LandingPageBuilderTool`, `AnalyticsTool` |
| F1 | Fit Analyst | Compass | `MethodologyCheckTool` |
| F2 | Iteration Router | Compass | *(Pure LLM - routing decision)* |

---

## Phase 2+: Deployed Crew Agent Tools

### Crew 1: Intake (4 Agents)

| Agent ID | Agent Name | Founder | Tools | Status |
|----------|------------|---------|-------|--------|
| S1 | Founder Onboarding | Sage | *(Pure LLM)* | ✅ Deployed |
| S2 | Customer Research | Sage | `TavilySearchTool`, `CustomerResearchTool` | ✅ Deployed |
| S3 | Value Designer | Sage | *(Pure LLM)* | ✅ Deployed |
| G1 | QA Agent | Guardian | `MethodologyCheckTool`, `InvokeCrewAIAutomationTool` | ✅ Deployed |

**Configuration**: `src/intake_crew/config/agents.yaml`

### Crew 2: Validation (12 Agents)

| Agent ID | Agent Name | Founder | Tools | Status |
|----------|------------|---------|-------|--------|
| P1 | Ad Creative Designer | Pulse | `LandingPageGeneratorTool` | ⏳ Pending |
| P2 | Comms Manager | Pulse | *(Pure LLM)* | ✅ Code complete |
| P3 | Analytics Tracker | Pulse | `AnalyticsTool` | ⏳ Pending |
| F1 | UX/UI Designer | Forge | *(Pure LLM)* | ✅ Code complete |
| F2 | Frontend Developer | Forge | `LandingPageGeneratorTool`, `LandingPageDeploymentTool` | ⏳ Pending |
| F3 | Backend Developer | Forge | `CodeValidatorTool` | ⏳ Pending |
| L1 | Financial Controller | Ledger | `UnitEconomicsModelsTool`, `BusinessModelClassifierTool`, `BudgetGuardrailsTool`, `FinancialDataTool` | ⏳ Pending |
| L2 | Legal Compliance | Ledger | *(Pure LLM)* | ✅ Code complete |
| L3 | Economics Reviewer | Ledger | `ViabilityApprovalTool` | ⏳ Pending |
| G1 | QA Reviewer | Guardian | `GuardianReviewTool`, `MethodologyCheckTool` | ⏳ Pending |
| G2 | Security Analyst | Guardian | `PrivacyGuardTool` | ⏳ Pending |
| G3 | Audit Agent | Guardian | `InvokeCrewAIAutomationTool` | ⏳ Pending |

**Configuration**: `startupai-crews/crew-2-validation/src/validation_crew/config/agents.yaml`

### Crew 3: Decision (3 Agents)

| Agent ID | Agent Name | Founder | Tools | Status |
|----------|------------|---------|-------|--------|
| C1 | Product PM | Compass | `LearningRetrievalTool` | ⏳ Pending |
| C2 | Human Approval | Compass | *(HITL agent - no tools)* | ✅ Code complete |
| C3 | Roadmap Writer | Compass | `LearningCaptureTool`, `AnonymizerTool` | ⏳ Pending |

**Configuration**: `startupai-crews/crew-3-decision/src/decision_crew/config/agents.yaml`

---

## Tool Wiring Priority

Based on EVOLUTION-PLAN Stage 3, tools should be wired in this priority order:

### Priority 1: Core Validation Tools
| Tool | Agent | Impact |
|------|-------|--------|
| `TavilySearchTool` | Crew 1 S2 | ✅ Already wired |
| `MethodologyCheckTool` | Crew 1 G1 | ✅ Already wired |
| `LandingPageGeneratorTool` | Crew 2 F2 | Enables MVP generation |
| `LandingPageDeploymentTool` | Crew 2 F2 | Enables Netlify deploy |

### Priority 2: Governance Tools
| Tool | Agent | Impact |
|------|-------|--------|
| `GuardianReviewTool` | Crew 2 G1 | Creative QA |
| `PrivacyGuardTool` | Crew 2 G2 | PII protection |
| `InvokeCrewAIAutomationTool` | Crew 1 G1, Crew 2 G3 | Crew chaining |

### Priority 3: Viability Tools
| Tool | Agent | Impact |
|------|-------|--------|
| `UnitEconomicsModelsTool` | Crew 2 L1 | Business model calculations |
| `BusinessModelClassifierTool` | Crew 2 L1 | Auto-classification |
| `BudgetGuardrailsTool` | Crew 2 L1 | Budget enforcement |

### Priority 4: Flywheel Tools
| Tool | Agent | Impact |
|------|-------|--------|
| `LearningCaptureTool` | Crew 3 C3 | Pattern storage |
| `LearningRetrievalTool` | Crew 3 C1, Phase 0 O1 | Pattern retrieval |
| `AnonymizerTool` | Crew 3 C3 | Data anonymization |

---

## Tool Configuration Examples

### Adding a Tool to an Agent

In `config/agents.yaml`:

```yaml
customer_research_agent:
  role: Customer Research Analyst
  goal: Build evidence-based customer profiles
  backstory: ...
  tools:
    - TavilySearchTool
    - CustomerResearchTool
```

In `crew.py`:

```python
from crewai_tools import TavilySearchTool
from .tools.web_search import CustomerResearchTool

@agent
def customer_research_agent(self) -> Agent:
    return Agent(
        config=self.agents_config['customer_research_agent'],
        tools=[TavilySearchTool(), CustomerResearchTool()],
        reasoning=True,
        verbose=True
    )
```

### Tool Environment Variables

| Tool | Required Environment Variables |
|------|-------------------------------|
| `TavilySearchTool` | `TAVILY_API_KEY` |
| `LandingPageDeploymentTool` | `NETLIFY_ACCESS_TOKEN` |
| `FinancialDataTool` | `OPENAI_API_KEY` (for analysis) |
| All Supabase tools | `SUPABASE_URL`, `SUPABASE_KEY` |

---

## Implementation Checklist

### Crew 1 (✅ Complete)
- [x] `TavilySearchTool` wired to S2
- [x] `CustomerResearchTool` wired to S2
- [x] `MethodologyCheckTool` wired to G1
- [ ] `InvokeCrewAIAutomationTool` wired to G1 (for Crew 2 chaining)

### Crew 2 (⏳ Pending)
- [ ] `LandingPageGeneratorTool` wired to F2
- [ ] `LandingPageDeploymentTool` wired to F2
- [ ] `GuardianReviewTool` wired to G1
- [ ] `PrivacyGuardTool` wired to G2
- [ ] `UnitEconomicsModelsTool` wired to L1
- [ ] `BusinessModelClassifierTool` wired to L1
- [ ] `BudgetGuardrailsTool` wired to L1
- [ ] `ViabilityApprovalTool` wired to L3
- [ ] `CodeValidatorTool` wired to F3
- [ ] `InvokeCrewAIAutomationTool` wired to G3

### Crew 3 (⏳ Pending)
- [ ] `LearningCaptureTool` wired to C3
- [ ] `LearningRetrievalTool` wired to C1
- [ ] `AnonymizerTool` wired to C3

### Phase 0-1 (⏳ Planned)
- [ ] Build `ConversationTool` for O1
- [ ] Build `NoteStructurerTool` for O1
- [ ] Build `InterviewSchedulerTool` for D1
- [ ] Build observation tools (D2)
- [ ] Build CTA experiment tools (D3)
- [ ] Build `TestCardTool` and `LearningCardTool` for E1

---

## Related Documents

- [02-organization.md](../02-organization.md) - Agent definitions
- [05-phase-0-1-specification.md](../05-phase-0-1-specification.md) - Phase 0-1 agent specs
- [03-validation-spec.md](../03-validation-spec.md) - Phase 2+ crew specs
- [api-contracts.md](./api-contracts.md) - API specifications

---

**Last Updated**: 2026-01-06

**Latest Changes**:
- Created comprehensive tool-to-agent mapping
- Documented all archived tools with target assignments
- Added Phase 0-1 tool specifications from VPD spec
- Added implementation checklist for tool wiring
- Defined tool wiring priority order
