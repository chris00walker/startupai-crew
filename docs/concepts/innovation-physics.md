# Innovation Physics Implementation

---
purpose: Maps Strategyzer Innovation Physics principles to StartupAI implementation
status: reference
last_reviewed: 2025-11-27
---

## Overview

This document describes how Innovation Physics principles (Strategyzer methodologies) are integrated into the StartupAI validation engine. It is **fully aligned** with the complete architecture specification in `03-validation-spec.md`.

**Relationship to Other Docs:**
- `03-validation-spec.md`: Complete technical specification (state, crews, tools, routers)
- `innovation-physics.md` (this doc): Innovation Physics principles mapped to implementation

This implementation transforms the StartupAI CrewAI Flow from a linear validation process into a dynamic, evidence-driven system where routing decisions are based on computed metrics (`problem_resonance`, `zombie_ratio`, `unit_economics_status`) rather than sequential steps.

## Key Innovation Physics Rules → Implementation Mapping

### Phase 1: Desirability (The "Truth" Engine)

#### The Problem-Solution Filter
- **Innovation Physics Rule**: Customer interest < 30% regarding the problem
- **Implementation**: `if problem_resonance < 0.3` in `route_after_desirability()`
- **State Updates**:
  - `pivot_recommendation = PivotType.SEGMENT_PIVOT`
  - `last_pivot_type = PivotType.SEGMENT_PIVOT`
- **Action**: Calls `SageCrew().adjust_segment()` → loops back to desirability
- **Logic**: Don't change the solution; change the audience

#### The Product-Market Filter (Zombie Detection)
- **Innovation Physics Rule**: High traffic but low commitment (zombie ratio >= 70%)
- **Implementation**: `if problem_resonance >= 0.3 and zombie_ratio >= 0.7`
- **Metrics**:
  - `problem_resonance` = (clicks + signups) / impressions
  - `zombie_ratio` = (clicks - signups) / clicks
- **State Updates**:
  - `pivot_recommendation = PivotType.VALUE_PIVOT`
  - `commitment_type` = VERBAL_INTEREST (not SKIN_IN_GAME)
- **Action**: Calls `SageCrew().adjust_value_map()` → loops back to desirability
- **Logic**: The audience is right, but the promise is wrong

### Phase 2: Feasibility (The "Reality" Check)

#### The Downgrade Protocol
- **Innovation Physics Rule**: Feature technically impossible or too expensive
- **Implementation**: `if feasibility_signal == FeasibilitySignal.ORANGE_CONSTRAINED`
- **State Updates**:
  - `last_pivot_type = PivotType.FEATURE_PIVOT`
  - `downgrade_active = True`
- **Action**: Calls `ForgeCrew().apply_downgrade_to_vpc()` → re-tests desirability with "lite" version
- **Logic**: Must verify customers still want the product without that feature

### Phase 3: Viability (The "Survival" Equation)

#### The Unit Economics Trigger (Strategic Pivot)
- **Innovation Physics Rule**: CAC > LTV (underwater unit economics)
- **Implementation**: `if viability_signal in (ViabilitySignal.UNDERWATER, ViabilitySignal.ZOMBIE_MARKET)`
- **State Updates**:
  - `pivot_recommendation = PivotType.MODEL_PIVOT` (fundamental model change)
  - `human_input_required = True`
  - `human_approval_status = HumanApprovalStatus.PENDING`
  - `unit_economics_status = UnitEconomicsStatus.UNDERWATER`
- **Action**: Calls `CompassCrew().request_viability_decision()` → pauses for HITL
- **HITL Options**:
  1. `PRICE_PIVOT`: Increase price → re-test desirability
  2. `COST_PIVOT`: Reduce costs → re-run feasibility
  3. `KILL`: Terminate project
- **Resume**: `/resume` endpoint writes `pending_pivot_type` and routes accordingly

## File Structure

```
src/startupai/
├── flows/
│   ├── __init__.py
│   ├── state_schemas.py              # Complete state with Innovation Physics metrics
│   │                                 # - StartupValidationState (with problem_resonance, zombie_ratio)
│   │                                 # - All enums (Phase, Signals, PivotType, etc.)
│   │                                 # - Artifact models (AdVariant, LandingPageVariant, etc.)
│   ├── founder_validation_flow.py   # StartupValidationFlow with @router logic
│   └── consultant_onboarding_flow.py # Consultant onboarding flow
│
├── crews/
│   ├── service/                   # Sage (S1, S2, S3)
│   │   └── service_crew.py        # VPC design, segment/value pivots
│   ├── analysis/                  # Pulse (P1, P2, P3)
│   │   └── analysis_crew.py       # Desirability experiments, evidence computation
│   ├── build/                     # Forge (F1, F2, F3)
│   │   └── build_crew.py          # Feasibility, MVP build, downgrade protocol
│   ├── growth/                    # Growth (market expansion)
│   │   └── growth_crew.py         # Ad campaigns, communications
│   ├── synthesis/                 # Compass (C1, C2, C3)
│   │   └── synthesis_crew.py      # HITL approvals, pivot synthesis
│   ├── finance/                   # Ledger (L1, L2, L3)
│   │   └── finance_crew.py        # Viability, unit economics
│   └── governance/                # Guardian (G1, G2, G3)
│       └── governance_crew.py     # QA, creative review, audit
│
├── tools/                         # 24+ shared tools across crews
│   ├── tavily_search_tool.py      # Real web research
│   ├── landing_page_generator.py  # LP generation
│   ├── landing_page_deployment.py # Netlify deployment
│   ├── policy_bandit.py           # A/B policy selection (Area 3)
│   ├── budget_guardrails.py       # Budget enforcement (Area 6)
│   ├── unit_economics_models.py   # 10 business models (Area 7)
│   └── ...
│
├── persistence/                   # State & event persistence
│   ├── state_repository.py        # Supabase state storage
│   ├── events.py                  # ValidationEvent tracking
│   └── decision_log.py            # Decision audit trail
│
└── main.py                        # Entry point / kickoff
```

## State Schema Signals

The `StartupValidationState` carries these Innovation Physics signals (aligned with complete architecture):

### Core Signals (from 03-validation-spec.md)
- **Phase**: IDEATION, DESIRABILITY, FEASIBILITY, VIABILITY, VALIDATED, KILLED
- **current_risk_axis**: DESIRABILITY, FEASIBILITY, VIABILITY
- **desirability_signal**: NO_SIGNAL, NO_INTEREST, WEAK_INTEREST, STRONG_COMMITMENT
- **feasibility_signal**: UNKNOWN, GREEN, ORANGE_CONSTRAINED, RED_IMPOSSIBLE
- **viability_signal**: UNKNOWN, PROFITABLE, UNDERWATER, ZOMBIE_MARKET

### Innovation Physics Evidence Metrics
- **evidence_strength**: EvidenceStrength.NONE, WEAK, STRONG
- **commitment_type**: CommitmentType.NONE, VERBAL_INTEREST, LOW_STAKE, SKIN_IN_GAME
- **problem_resonance**: float (0.0-1.0) - fraction of visitors resonating with problem
- **zombie_ratio**: float (0.0-1.0) - fraction of "interested but not committed" visitors
- **unit_economics_status**: UnitEconomicsStatus.UNKNOWN, PROFITABLE, MARGINAL, UNDERWATER

### Pivot & Decision State
- **pivot_recommendation**: PivotType - NONE, SEGMENT_PIVOT, VALUE_PIVOT, CHANNEL_PIVOT, PRICE_PIVOT, COST_PIVOT, MODEL_PIVOT, FEATURE_PIVOT, KILL
- **last_pivot_type**: PivotType - tracks last executed pivot
- **pending_pivot_type**: PivotType - for HITL approval workflows
- **human_input_required**: bool - true when HITL approval needed

## Router Logic

The flow uses `@router` decorators implementing Innovation Physics filters:

### Desirability Router (Problem-Solution & Product-Market Filters)

```python
@router("route_after_desirability")
def route_after_desirability(self):
    pr = self.state.problem_resonance
    zr = self.state.zombie_ratio
    signal = self.state.desirability_signal

    # 1) Problem–Solution filter (Innovation Physics):
    #    Customer interest < 30% regarding the problem → segment pivot
    if pr < 0.3:
        self.state.pivot_recommendation = PivotType.SEGMENT_PIVOT
        self.state.last_pivot_type = PivotType.SEGMENT_PIVOT
        SageCrew().adjust_segment(
            project_id=self.state.project_id,
            vpc_url=self.state.vpc_document_url,
        )
        return "run_desirability_experiments"

    # 2) Product–Market filter + Zombie Detection:
    #    Good problem resonance but shallow commitment (many zombies) → value pivot
    if pr >= 0.3 and zr >= 0.7:
        self.state.pivot_recommendation = PivotType.VALUE_PIVOT
        self.state.last_pivot_type = PivotType.VALUE_PIVOT
        SageCrew().adjust_value_map(
            project_id=self.state.project_id,
            vpc_url=self.state.vpc_document_url,
        )
        return "run_desirability_experiments"

    # 3) Strong commitment → proceed to Feasibility
    if signal == DesirabilitySignal.STRONG_COMMITMENT:
        self.state.pivot_recommendation = PivotType.NONE
        return "run_feasibility_assessment"

    # 4) Fallback: use legacy signal routing (NO_INTEREST, WEAK_INTEREST)
    # ... additional logic for backwards compatibility
```

### Feasibility Router (Downgrade Protocol)

```python
@router("route_after_feasibility")
def route_after_feasibility(self):
    flag = self.state.feasibility_signal

    if flag == FeasibilitySignal.GREEN:
        return "run_viability_analysis"

    # ORANGE_CONSTRAINED: Feature downgrade required
    if flag == FeasibilitySignal.ORANGE_CONSTRAINED:
        self.state.last_pivot_type = PivotType.FEATURE_PIVOT  # Innovation Physics
        self.state.downgrade_active = True
        ForgeCrew().apply_downgrade_to_vpc(...)
        return "run_desirability_experiments"  # Re-test with downgraded version

    if flag == FeasibilitySignal.RED_IMPOSSIBLE:
        self.state.phase = Phase.KILLED
        self.state.last_pivot_type = PivotType.KILL
        return "terminal_killed"
```

### Viability Router (Strategic Pivot Trigger)

```python
@router("route_after_viability")
def route_after_viability(self):
    signal = self.state.viability_signal

    if signal == ViabilitySignal.PROFITABLE:
        self.state.phase = Phase.VALIDATED
        self.state.last_pivot_type = PivotType.NONE
        return "terminal_validated"

    # CAC > LTV: Strategic pivot required (Innovation Physics)
    if signal in (ViabilitySignal.UNDERWATER, ViabilitySignal.ZOMBIE_MARKET):
        self.state.human_approval_status = HumanApprovalStatus.PENDING
        self.state.human_input_required = True  # Innovation Physics flag
        self.state.pivot_recommendation = PivotType.MODEL_PIVOT  # Fundamental change

        compass = CompassCrew()
        hitl = compass.request_viability_decision(...)
        return "await_viability_decision"
```

## Evidence Computation (Innovation Physics Metrics)

The system computes Innovation Physics metrics from raw experiment data:

```python
def compute_desirability_evidence(aggregate: DesirabilityMetrics) -> dict:
    # Problem resonance = fraction of visitors who click or signup
    if aggregate.impressions <= 0:
        problem_resonance = 0.0
    else:
        problem_resonance = (
            (aggregate.clicks + aggregate.signups) / float(aggregate.impressions)
        )

    # Zombie ratio = "interested but not committed" / interested
    if aggregate.clicks <= 0:
        zombie_ratio = 0.0
    else:
        zombie_ratio = max(
            0.0,
            (aggregate.clicks - aggregate.signups) / float(aggregate.clicks),
        )

    # Evidence strength based on Innovation Physics intuition
    if problem_resonance >= 0.5:
        evidence_strength = EvidenceStrength.STRONG
    elif problem_resonance >= 0.1:
        evidence_strength = EvidenceStrength.WEAK
    else:
        evidence_strength = EvidenceStrength.NONE

    # Commitment type: depth of commitment, not just clicks
    if aggregate.signups >= 10:
        commitment_type = CommitmentType.SKIN_IN_GAME
    elif aggregate.signups >= 1:
        commitment_type = CommitmentType.LOW_STAKE
    elif aggregate.clicks > 0:
        commitment_type = CommitmentType.VERBAL_INTEREST
    else:
        commitment_type = CommitmentType.NONE

    return {
        "problem_resonance": problem_resonance,
        "zombie_ratio": zombie_ratio,
        "evidence_strength": evidence_strength,
        "commitment_type": commitment_type,
    }
```

**Integration**: `PulseCrew.kickoff()` calls this after collecting aggregate metrics and propagates values to both `DesirabilityExperimentRun` and `PulseDesirabilityResult`.

## Human Input Integration

When pivots are triggered, the system sets `human_input_required=True` with a specific reason, enabling HITL (Human-in-the-Loop) approval workflows:

- **Creative Approval**: `human_approval_status = PENDING` → `human_input_required = True`
- **Viability Decision**: CAC/LTV imbalance → `human_input_required = True` + `pivot_recommendation = MODEL_PIVOT`

## Compass Synthesis & HITL Integration

The `CompassCrew` (Synthesis Crew) manages two types of human-in-the-loop approvals:

### 1. Creative Approval (Desirability Phase)
- **Trigger**: Guardian QA flags creatives for human review
- **Agents**: C2 (HumanApprovalAgent) presents ads/landing pages
- **State updates**: Updates `AdVariant` and `LandingPageVariant` approval statuses
- **Resume endpoint**: `/resume` with `creative_decision` payload

### 2. Viability Decision (Strategic Pivot)
- **Trigger**: CAC > LTV or ZOMBIE_MARKET signal
- **Agents**: C1 (ProductPMAgent) synthesizes evidence, C2 requests human decision
- **Options presented**:
  1. `PRICE_PIVOT`: Increase price → re-test desirability
  2. `COST_PIVOT`: Reduce costs → re-run feasibility
  3. `KILL`: Terminate project
- **State updates**: Sets `pending_pivot_type` and `pivot_recommendation = MODEL_PIVOT`
- **Resume endpoint**: `/resume` with `viability_pivot_decision` payload

### Evidence Synthesis Logic (Innovation Physics)
Compass synthesizes `pivot_recommendation` based on:

1. **Problem resonance** < 0.3 → SEGMENT_PIVOT
2. **Zombie ratio** >= 0.7 (with pr >= 0.3) → VALUE_PIVOT
3. **Feasibility** = ORANGE_CONSTRAINED → FEATURE_PIVOT
4. **Unit economics** = UNDERWATER/ZOMBIE_MARKET → MODEL_PIVOT (requires HITL)
5. **Feasibility** = RED_IMPOSSIBLE → KILL

## Testing the Flow

```bash
# Set up environment
export OPENAI_API_KEY=your_key_here

# Run the validation
python src/startupai/main.py
```

## Innovation Physics Principles

1. **Progress isn't linear** - Evidence drives transitions, not time
2. **Desirability without Feasibility** = Beautiful fiction
3. **Feasibility without Desirability** = Solution looking for problem
4. **Viability without both** = Unsustainable charity

## Key Differentiators from Linear Flow

1. **Dynamic Routing**: `@router` decorators use `problem_resonance`, `zombie_ratio`, and signals (not time/sequence)
2. **Pivot Logic**: 8 specific pivot types (SEGMENT, VALUE, CHANNEL, PRICE, COST, MODEL, FEATURE, KILL) for different failure modes
3. **Zombie Detection**: `commitment_type` (SKIN_IN_GAME > LOW_STAKE > VERBAL_INTEREST) and `zombie_ratio >= 0.7` threshold
4. **Downgrade Protocol**: `FeasibilitySignal.ORANGE_CONSTRAINED` → `FEATURE_PIVOT` + `downgrade_active=True` → re-test desirability
5. **Strategic Pivots**: `ViabilitySignal.UNDERWATER` → `MODEL_PIVOT` + HITL (price/cost/kill decision)
6. **Evidence-Based State**: `StartupValidationState` tracks computed metrics (`problem_resonance`, `zombie_ratio`) alongside raw signals
7. **Multi-Platform Experiments**: `PlatformBudgetConfig` per platform (Meta, TikTok, LinkedIn, Google) with targeted budgets/audiences
8. **Creative Approval Workflow**: Guardian auto-QA + optional HITL for ads/landing pages before deployment

## Implementation Status

### ✅ Fully Implemented (as of 2025-11-27)

**Architecture:**
- ✅ Complete state schema with Innovation Physics metrics (`state_schemas.py`)
- ✅ All enums and artifact models (AdVariant, LandingPageVariant, etc.)
- ✅ Flow router logic with problem_resonance/zombie_ratio filters
- ✅ HITL approval workflows (creative + viability)
- ✅ Multi-platform experiment configuration
- ✅ 14 crews / 45 agents structurally implemented (tool quality varies)

**Tools (24+ implemented):**
- ✅ Research tools: TavilySearchTool, CompetitorResearchTool, MarketResearchTool
- ✅ Build tools: LandingPageGeneratorTool, CodeValidatorTool, LandingPageDeploymentTool
- ✅ HITL tools: GuardianReviewTool, ViabilityApprovalTool
- ✅ Flywheel tools: LearningCaptureTool, LearningRetrievalTool, OutcomeTrackerTool
- ✅ Area 3: PolicyBandit, ExperimentConfigResolver (policy versioning)
- ✅ Area 6: BudgetGuardrails, DecisionLogger (budget enforcement)
- ✅ Area 7: BusinessModelClassifier, 10 UnitEconomicsModels

**Deployment:**
- ✅ Deployed to Modal serverless
- ✅ HITL checkpoints working via `/hitl/approve`
- ✅ Database migrations deployed (`validation_runs`, `validation_progress`, `hitl_requests`)

### ⚠️ Not Yet Integrated
- ❌ Ad platform APIs (Meta Business, Google Ads) - no real ad spend
- ❌ Real-time analytics integration (PostHog/GA)

---

**Innovation Physics Mantra**: Evidence drives iteration, not intuition.

---

**Last Updated**: 2025-11-27
**Related Documents**:
- `03-validation-spec.md` - Authoritative technical specification
- `approval-workflows.md` - HITL approval patterns
- `flywheel-learning.md` - Learning system architecture
