---
document_type: feature-audit
status: active
last_verified: 2026-01-19
architectural_pivot: 2026-01-19
---

# Crew-Agent-Task Matrix

> **Architectural Pivot (2026-01-19)**: Phase 0 was simplified to Quick Start - no AI, no agents. Agent count: 45 → 43. See [ADR-006](../adr/006-quick-start-architecture.md).

## Purpose
Complete per-phase breakdown of all 14 Crews with their 43 Agents, Tasks, and Tool wiring.

## Summary Statistics

| Metric | Canonical | Implemented | Gap |
|--------|-----------|-------------|-----|
| Crews | 14 | 14 | 0 |
| Agents | 43 | 43 | 0 |
| Tasks | ~66 | 66 | 0 |
| Agents with tools | - | 22 | - |
| Agents without tools | - | 21 | - |

## Crew Distribution by Phase

| Phase | Crews | Agents | Tasks | Status |
|-------|-------|--------|-------|--------|
| 0 | 0 | 0 | 0 | `Quick Start (no AI)` |
| 1 | 6 | 20 | 25 | `active` |
| 2 | 3 | 9 | 12 | `active` |
| 3 | 2 | 5 | 13 | `active` |
| 4 | 3 | 9 | 16 | `active` |

---

## Phase 0: Quick Start (No AI)

> **Architectural Pivot (2026-01-19)**: Phase 0 was simplified to Quick Start - a single form input. See [ADR-006](../adr/006-quick-start-architecture.md).
>
> **No AI in Phase 0**: The 7-stage conversation and OnboardingCrew were removed. Users enter a business idea (1-3 sentences) and optionally upload a pitch deck. Phase 1 starts immediately.

### No Crews in Phase 0

Phase 0 has **no AI, no crews, no agents, no HITL checkpoints**.

| Metric | Value |
|--------|-------|
| Crews | 0 |
| Agents | 0 |
| Duration | ~30 seconds |
| AI Cost | $0 |

### Deprecated: OnboardingCrew

~~**File**: `src/crews/onboarding/crew.py`~~

The following agents were removed or moved:

| Agent ID | Previous Role | Status |
|----------|---------------|--------|
| O1 | Interview Gap Analyzer | **DELETED** |
| GV1 | Concept Validator | **Moved to Phase 1 BriefGenerationCrew** |
| GV2 | Intent Verification | **DELETED** |
| S1 | Brief Compiler | **Moved to Phase 1 BriefGenerationCrew** |

---

## Phase 1: VPC Discovery + Brief Generation

### BriefGenerationCrew (NEW)
**File**: `src/crews/discovery/brief_generation_crew.py` (planned)
**Purpose**: Generate Founder's Brief from AI research (replaces Phase 0 interview)
**Process**: Sequential

| Agent ID | Role | Founder | Tools | Reasoning | Status |
|----------|------|---------|-------|-----------|--------|
| GV1 | Concept Validator | Guardian | `[]` | Yes | `placeholder` |
| S1 | Brief Compiler | Sage | `[]` | No | `placeholder` |

**Tasks**:
| Task | Agent | Output |
|------|-------|--------|
| `validate_concept_legitimacy` | GV1 | Legitimacy check |
| `compile_founders_brief` | S1 | `FoundersBrief` (Pydantic) |

**HITL Checkpoint**: `approve_discovery_output` (combined Brief + VPC review)

---

### DiscoveryCrew
**File**: `src/crews/discovery/discovery_crew.py`
**Purpose**: Segment validation and SAY/DO evidence collection
**Process**: Sequential

| Agent ID | Role | Founder | Tools | Reasoning | Status |
|----------|------|---------|-------|-----------|--------|
| E1 | Experiment Designer | Sage | `TestCardTool`, `LearningCardTool` | Yes | `wired` |
| D1 | Customer Interview | Sage | `TranscriptionTool`, `InsightExtractorTool`, `CalendarTool` | Yes | `wired` |
| D2 | Observation Agent | Pulse | `TavilySearchTool`, `ForumSearchTool`, `ReviewAnalysisTool`, `SocialListeningTool`, `TrendAnalysisTool`, `BehaviorPatternTool` | Yes | `wired` |
| D3 | CTA Test Agent | Pulse | `BehaviorPatternTool`, `ABTestTool`, `AnalyticsTool`, `AdPlatformTool` | Yes | `wired` |
| D4 | Evidence Triangulation | Guardian | `InsightExtractorTool`, `BehaviorPatternTool`, `LearningCardTool` | Yes | `wired` |

**Tasks**:
| Task | Agent | Output |
|------|-------|--------|
| `map_assumptions` | E1 | Assumptions Map |
| `design_test_cards` | E1 | Test Cards |
| `conduct_discovery_interviews` | D1 | SAY evidence |
| `mine_behavioral_evidence` | D2 | DO-indirect evidence |
| `execute_cta_experiments` | D3 | DO-direct evidence |
| `triangulate_evidence` | D4 | Evidence synthesis |

### CustomerProfileCrew
**File**: `src/crews/discovery/customer_profile_crew.py`
**Purpose**: Jobs, Pains, Gains extraction (Customer Profile side of VPC)
**Process**: Sequential

| Agent ID | Role | Founder | Tools | Reasoning | Status |
|----------|------|---------|-------|-----------|--------|
| J1 | JTBD Researcher | Sage | `TavilySearchTool`, `ForumSearchTool`, `ReviewAnalysisTool` | Yes | `wired` |
| J2 | Job Ranking | Sage | `[]` | No | `placeholder` |
| PAIN_RES | Pain Researcher | Sage | `TavilySearchTool`, `ForumSearchTool`, `ReviewAnalysisTool` | Yes | `wired` |
| PAIN_RANK | Pain Ranking | Sage | `[]` | No | `placeholder` |
| GAIN_RES | Gain Researcher | Sage | `TavilySearchTool`, `ForumSearchTool`, `ReviewAnalysisTool` | Yes | `wired` |
| GAIN_RANK | Gain Ranking | Sage | `[]` | No | `placeholder` |

**Tasks**:
| Task | Agent | Output |
|------|-------|--------|
| `discover_jobs` | J1 | Job list |
| `rank_jobs` | J2 | Ranked jobs |
| `discover_pains` | PAIN_RES | Pain list |
| `rank_pains` | PAIN_RANK | Ranked pains |
| `discover_gains` | GAIN_RES | Gain list |
| `rank_gains` | GAIN_RANK | Ranked gains |
| `compile_customer_profile` | All | `CustomerProfile` (Pydantic) |

### ValueDesignCrew
**File**: `src/crews/discovery/value_design_crew.py`
**Purpose**: Design Value Map (Products, Pain Relievers, Gain Creators)
**Process**: Sequential

| Agent ID | Role | Founder | Tools | Reasoning | Status |
|----------|------|---------|-------|-----------|--------|
| V1 | Solution Designer | Forge | `CanvasBuilderTool` | No | `wired` |
| V2 | Pain Reliever Designer | Forge | `CanvasBuilderTool` | No | `wired` |
| V3 | Gain Creator Designer | Forge | `CanvasBuilderTool` | No | `wired` |

**Tasks**:
| Task | Agent | Output |
|------|-------|--------|
| `design_products_services` | V1 | Product list |
| `design_pain_relievers` | V2 | Pain relievers |
| `design_gain_creators` | V3 | Gain creators |
| `compile_value_map` | All | `ValueMap` (Pydantic) |

### WTPCrew
**File**: `src/crews/discovery/wtp_crew.py`
**Purpose**: Willingness-to-pay validation
**Process**: Sequential

| Agent ID | Role | Founder | Tools | Reasoning | Status |
|----------|------|---------|-------|-----------|--------|
| W1 | Pricing Experiment | Ledger | `ABTestTool`, `AnalyticsTool` | Yes | `wired` |
| W2 | Payment Test | Ledger | `AnalyticsTool` | Yes | `wired` |

**Tasks**:
| Task | Agent | Output |
|------|-------|--------|
| `design_wtp_experiments` | W1 | WTP experiments |
| `execute_payment_tests` | W2 | Payment results |
| `synthesize_wtp_evidence` | W1/W2 | WTP synthesis |

### FitAssessmentCrew
**File**: `src/crews/discovery/fit_assessment_crew.py`
**Purpose**: VPC fit scoring and routing
**Process**: Sequential

| Agent ID | Role | Founder | Tools | Reasoning | Status |
|----------|------|---------|-------|-----------|--------|
| FIT_SCORE | Fit Analyst | Compass | `MethodologyCheckTool` | Yes | `wired` |
| FIT_ROUTE | Iteration Router | Compass | `[]` | No | `placeholder` |

**Tasks**:
| Task | Agent | Output |
|------|-------|--------|
| `calculate_fit_score` | FIT_SCORE | Fit score (0-100) |
| `determine_routing` | FIT_ROUTE | Routing decision |
| `compile_fit_assessment` | All | `FitAssessment` (Pydantic) |

---

## Phase 2: Desirability

### BuildCrew
**File**: `src/crews/desirability/build_crew.py`
**Purpose**: Build landing pages and testable artifacts
**Process**: Sequential

| Agent ID | Role | Founder | Tools | Reasoning | Status |
|----------|------|---------|-------|-----------|--------|
| F1 | UX/UI Designer | Forge | `CanvasBuilderTool`, `TestCardTool` | No | `wired` |
| F2 | Frontend Developer | Forge | `CanvasBuilderTool`, `TestCardTool` | No | `wired` |
| F3 | Backend Developer | Forge | `LandingPageDeploymentTool` | No | `wired` |

**Tasks**:
| Task | Agent | Output |
|------|-------|--------|
| `design_landing_page` | F1 | Wireframes |
| `build_landing_page` | F2 | Built pages |
| `deploy_artifacts` | F3 | Deployed URLs |

### GrowthCrew
**File**: `src/crews/desirability/growth_crew.py`
**Purpose**: Ad campaigns and desirability evidence collection
**Process**: Sequential

| Agent ID | Role | Founder | Tools | Reasoning | Status |
|----------|------|---------|-------|-----------|--------|
| P1 | Ad Creative | Pulse | `ABTestTool`, `AdPlatformTool` | No | `wired` |
| P2 | Communications | Pulse | `ABTestTool`, `AdPlatformTool` | No | `wired` |
| P3 | Analytics | Pulse | `AnalyticsTool`, `AdPlatformTool` | Yes | `wired` |

**Tasks**:
| Task | Agent | Output |
|------|-------|--------|
| `create_ad_variants` | P1 | Ad creatives |
| `write_copy_variants` | P2 | Copy variants |
| `configure_experiments` | P3 | Experiment config |
| `run_experiments` | P3 | Experiment data |
| `compute_desirability_signals` | P3 | `DesirabilityEvidence` (Pydantic) |

### GovernanceCrew
**File**: `src/crews/desirability/governance_crew.py`
**Purpose**: QA, security, and audit (reused across phases)
**Process**: Sequential

| Agent ID | Role | Founder | Tools | Reasoning | Status |
|----------|------|---------|-------|-----------|--------|
| G1 | QA Agent | Guardian | `MethodologyCheckTool` | Yes | `wired` |
| G2 | Security Agent | Guardian | `AnonymizerTool` | Yes | `wired` |
| G3 | Audit Agent | Guardian | `LearningCardTool` | No | `wired` |

**Tasks**:
| Task | Agent | Output |
|------|-------|--------|
| `methodology_compliance_check` | G1 | Compliance report |
| `creative_qa` | G1 | Creative QA |
| `security_review` | G2 | Security assessment |
| `log_decisions` | G3 | Audit trail |

---

## Phase 3: Feasibility

### FeasibilityBuildCrew
**File**: `src/crews/feasibility/build_crew.py`
**Purpose**: Technical feasibility assessment (different from Phase 2 BuildCrew)
**Process**: Sequential

| Agent ID | Role | Founder | Tools | Reasoning | Status |
|----------|------|---------|-------|-----------|--------|
| F1 | Requirements Analyst | Forge | `[]` | No | `placeholder` |
| F2 | Frontend Assessor | Forge | `[]` | No | `placeholder` |
| F3 | Backend Assessor | Forge | `[]` | No | `placeholder` |

**Tasks**:
| Task | Agent | Output |
|------|-------|--------|
| `extract_feature_requirements` | F1 | Feature requirements |
| `assess_ui_complexity` | F1 | UI complexity score |
| `design_lite_variant` | F1 | Lite variant design |
| `assess_frontend_complexity` | F2 | Frontend assessment |
| `identify_framework_requirements` | F2 | Framework list |
| `assess_backend_architecture` | F3 | Backend assessment |
| `evaluate_api_integrations` | F3 | API evaluation |
| `estimate_costs` | F3 | Cost estimates |
| `set_feasibility_signal` | F3 | `FeasibilityEvidence` (Pydantic) |

### FeasibilityGovernanceCrew
**File**: `src/crews/feasibility/governance_crew.py`
**Purpose**: Feasibility gate validation (G1, G2 only - no G3)
**Process**: Sequential

| Agent ID | Role | Founder | Tools | Reasoning | Status |
|----------|------|---------|-------|-----------|--------|
| G1 | QA Agent | Guardian | `MethodologyCheckTool` | Yes | `wired` |
| G2 | Security Agent | Guardian | `AnonymizerTool` | Yes | `wired` |

**Tasks**:
| Task | Agent | Output |
|------|-------|--------|
| `validate_assessment_methodology` | G1 | Methodology validation |
| `verify_constraint_documentation` | G1 | Constraint docs |
| `review_architecture_security` | G2 | Security review |
| `confirm_gate_readiness` | G1 | Gate readiness |

---

## Phase 4: Viability

### FinanceCrew
**File**: `src/crews/viability/finance_crew.py`
**Purpose**: Unit economics calculation
**Process**: Sequential

| Agent ID | Role | Founder | Tools | Reasoning | Status |
|----------|------|---------|-------|-----------|--------|
| L1 | Financial Controller | Ledger | `AnalyticsTool` | Yes | `wired` |
| L2 | Legal & Compliance | Ledger | `[]` | No | `placeholder` |
| L3 | Economics Reviewer | Ledger | `[]` | No | `placeholder` |

**Tasks**:
| Task | Agent | Output |
|------|-------|--------|
| `calculate_cac` | L1 | CAC |
| `calculate_ltv` | L1 | LTV |
| `compute_ltv_cac_ratio` | L1 | LTV:CAC ratio |
| `analyze_tam` | L1 | TAM/SAM/SOM |
| `identify_regulatory_constraints` | L2 | Regulatory constraints |
| `validate_assumptions` | L3 | Assumption validation |
| `set_viability_signal` | L1 | `ViabilityEvidence` (Pydantic) |

### SynthesisCrew
**File**: `src/crews/viability/synthesis_crew.py`
**Purpose**: Evidence synthesis and final decision management
**Process**: Sequential

| Agent ID | Role | Founder | Tools | Reasoning | Status |
|----------|------|---------|-------|-----------|--------|
| C1 | Product PM | Compass | `[]` | No | `placeholder` |
| C2 | Human Approval | Compass | `[]` | No | `placeholder` |
| C3 | Roadmap Writer | Compass | `[]` | No | `placeholder` |

**Tasks**:
| Task | Agent | Output |
|------|-------|--------|
| `synthesize_evidence` | C1 | Evidence synthesis |
| `propose_options` | C1 | Decision options |
| `present_viability_decision` | C2 | HITL presentation |
| `document_decision` | C3 | Decision doc |
| `capture_learnings` | C3 | Flywheel learnings |

### ViabilityGovernanceCrew
**File**: `src/crews/viability/governance_crew.py`
**Purpose**: Final governance, audit, and flywheel persistence
**Process**: Sequential

| Agent ID | Role | Founder | Tools | Reasoning | Status |
|----------|------|---------|-------|-----------|--------|
| G1 | QA Agent | Guardian | `MethodologyCheckTool` | Yes | `wired` |
| G2 | Security Agent | Guardian | `AnonymizerTool` | Yes | `wired` |
| G3 | Audit Agent | Guardian | `[]` | No | `placeholder` |

**Tasks**:
| Task | Agent | Output |
|------|-------|--------|
| `final_validation_check` | G1 | Final validation |
| `scrub_pii` | G2 | PII scrubbing |
| `create_audit_trail` | G3 | Audit trail |
| `persist_to_flywheel` | G3 | Flywheel persistence |

---

## CrewAI Compliance Check

**Rule**: Every crew must have 2+ agents (per CrewAI documentation)

| Crew | Agents | Compliant |
|------|--------|-----------|
| ~~OnboardingCrew~~ | ~~4~~ | ~~Removed (Quick Start)~~ |
| BriefGenerationCrew | 2 | Yes |
| DiscoveryCrew | 5 | Yes |
| CustomerProfileCrew | 6 | Yes |
| ValueDesignCrew | 3 | Yes |
| WTPCrew | 2 | Yes |
| FitAssessmentCrew | 2 | Yes |
| BuildCrew | 3 | Yes |
| GrowthCrew | 3 | Yes |
| GovernanceCrew | 3 | Yes |
| FeasibilityBuildCrew | 3 | Yes |
| FeasibilityGovernanceCrew | 2 | Yes |
| FinanceCrew | 3 | Yes |
| SynthesisCrew | 3 | Yes |
| ViabilityGovernanceCrew | 3 | Yes |

**All 14 crews are compliant.**

---

## Gaps / TODOs

### Tool Wiring Gaps
- **BriefGenerationCrew**: Both agents have `tools=[]` (placeholder) - pure LLM reasoning by design
- **FeasibilityBuildCrew**: All 3 agents have `tools=[]` - may need code analysis tools
- **SynthesisCrew**: All 3 agents have `tools=[]` - pure reasoning agents
- **ViabilityGovernanceCrew G3**: Has `tools=[]` - may need LearningCardTool like Phase 2 G3

### Reused Crews Note
- **GovernanceCrew** pattern is reused across phases with variations:
  - Phase 2: G1, G2, G3 (full)
  - Phase 3: G1, G2 only (no audit)
  - Phase 4: G1, G2, G3 (full but G3 lacks tool)

---

## Related Documents

- [flow-inventory.md](./flow-inventory.md) - Flow details
- [tool-wiring-matrix.md](./tool-wiring-matrix.md) - Detailed tool mapping
- [hitl-checkpoint-map.md](./hitl-checkpoint-map.md) - HITL checkpoint details
