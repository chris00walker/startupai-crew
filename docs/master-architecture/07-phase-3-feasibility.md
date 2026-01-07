# Phase 3: Feasibility Validation

**Version**: 1.0.0
**Status**: Active
**Last Updated**: 2026-01-06
**Methodology Reference**: [03-methodology.md](./03-methodology.md)

---

## Purpose

Determine whether the validated value proposition **can be built** with available resources, technology, and constraints. This is the "Reality Check" that bridges customer desire with technical capability.

### What This Phase IS About

- Technical architecture assessment
- Build vs Buy decisions
- Cost estimation (development, infrastructure, maintenance)
- Constraint identification (technical, regulatory, resource)
- Downgrade protocol if constraints block features

### What This Phase Is NOT About

- Customer validation (Phase 1-2)
- Unit economics and profitability (Phase 4)
- Actual product development (post-validation)

### Entry Criteria

- Phase 2 complete: `desirability_signal == STRONG_COMMITMENT`
- `approve_desirability_gate` HITL passed
- Problem resonance ≥ 0.3, zombie ratio < 0.7

### Exit Criteria

- `feasibility_signal == GREEN` (fully feasible) OR
- `feasibility_signal == ORANGE_CONSTRAINED` with successful downgrade retest
- `approve_feasibility_gate` HITL passed

### Exit to Kill

- `feasibility_signal == RED_IMPOSSIBLE` → Project killed

---

## FeasibilityFlow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       FEASIBILITY FLOW                                       │
│                                                                              │
│  Entry: STRONG_COMMITMENT from Phase 2                                      │
│  Exit: GREEN signal OR successful downgrade retest                          │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                    ┌───────────────────────────────┐                        │
│                    │  Desirability Evidence        │                        │
│                    │  (From Phase 2)               │                        │
│                    └───────────────┬───────────────┘                        │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      BUILD CREW (Forge)                               │  │
│  │                                                                       │  │
│  │  ┌────────────────────────────────────────────────────────────┐     │  │
│  │  │  F1: UX/UI DESIGNER                                         │     │  │
│  │  │                                                             │     │  │
│  │  │  • Extract feature requirements from VPC                    │     │  │
│  │  │  • Map to technical components                              │     │  │
│  │  │  • Identify UI/UX complexity                                │     │  │
│  │  │  • Design "lite" version for downgrade protocol             │     │  │
│  │  └────────────────────────────────────────────────────────────┘     │  │
│  │                                    │                                  │  │
│  │                                    ▼                                  │  │
│  │  ┌────────────────────────────────────────────────────────────┐     │  │
│  │  │  F2: FRONTEND DEVELOPER                                     │     │  │
│  │  │                                                             │     │  │
│  │  │  • Assess frontend complexity                               │     │  │
│  │  │  • Identify required frameworks/libraries                   │     │  │
│  │  │  • Estimate development effort                              │     │  │
│  │  │  • Flag frontend constraints                                │     │  │
│  │  └────────────────────────────────────────────────────────────┘     │  │
│  │                                    │                                  │  │
│  │                                    ▼                                  │  │
│  │  ┌────────────────────────────────────────────────────────────┐     │  │
│  │  │  F3: BACKEND DEVELOPER                                      │     │  │
│  │  │                                                             │     │  │
│  │  │  • Assess backend architecture requirements                 │     │  │
│  │  │  • Evaluate API integrations needed                         │     │  │
│  │  │  • Estimate infrastructure costs                            │     │  │
│  │  │  • Flag technical constraints                               │     │  │
│  │  │  • Set FEASIBILITY_SIGNAL                                   │     │  │
│  │  └────────────────────────────────────────────────────────────┘     │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    │                                         │
│                                    ▼                                         │
│                    ┌───────────────────────────────┐                        │
│                    │  FEASIBILITY ASSESSMENT       │                        │
│                    │                               │                        │
│                    │  Compile:                     │                        │
│                    │  • Technical complexity score │                        │
│                    │  • Development cost estimate  │                        │
│                    │  • Infrastructure cost        │                        │
│                    │  • Constraints list           │                        │
│                    │  • Removed features (if any)  │                        │
│                    └───────────────┬───────────────┘                        │
│                                    │                                         │
│                                    ▼                                         │
│                         ┌─────────────────────┐                             │
│                         │  FEASIBILITY        │                             │
│                         │  ROUTER             │                             │
│                         └─────────┬───────────┘                             │
│                                   │                                          │
│          ┌────────────────────────┼────────────────────────┐                │
│          │                        │                        │                 │
│       [GREEN]           [ORANGE_CONSTRAINED]        [RED_IMPOSSIBLE]        │
│          │                        │                        │                 │
│          │                        │                        │                 │
│          ▼                        ▼                        ▼                 │
│   ┌─────────────────┐    ┌──────────────────┐     ┌─────────────────┐      │
│   │ Proceed to      │    │ DOWNGRADE        │     │ PROJECT KILLED  │      │
│   │ Phase 4         │    │ PROTOCOL         │     │                 │      │
│   │ Viability       │    │                  │     │ Technical       │      │
│   └────────┬────────┘    │ F1: Design lite  │     │ impossibility   │      │
│            │             │ F3: Remove       │     │ is a valid      │      │
│            │             │     features     │     │ learning        │      │
│            │             │                  │     └─────────────────┘      │
│            │             │ Mark:            │                               │
│            │             │ downgrade_active │                               │
│            │             │ = True           │                               │
│            │             └────────┬─────────┘                               │
│            │                      │                                          │
│            │                      ▼                                          │
│            │             ┌──────────────────┐                               │
│            │             │ RE-TEST          │                               │
│            │             │ DESIRABILITY     │                               │
│            │             │                  │                               │
│            │             │ Run Phase 2 with │                               │
│            │             │ "lite" version   │                               │
│            │             │                  │                               │
│            │             │ Do customers     │                               │
│            │             │ still want it?   │                               │
│            │             └────────┬─────────┘                               │
│            │                      │                                          │
│            │            ┌─────────┴─────────┐                               │
│            │            │                   │                                │
│            │      [Still wanted]     [Not wanted]                           │
│            │            │                   │                                │
│            │            ▼                   ▼                                │
│            │      Continue to        VALUE_PIVOT                            │
│            │      Phase 4            or KILL                                │
│            │            │                                                    │
│            └────────────┴────────────────────────────────────────────────►  │
│                                                                              │
│                    ┌───────────────────────────────┐                        │
│                    │  HITL: approve_feasibility_   │                        │
│                    │        gate                   │                        │
│                    │                               │                        │
│                    │  Review:                      │                        │
│                    │  • Technical assessment       │                        │
│                    │  • Cost estimates             │                        │
│                    │  • Constraints                │                        │
│                    │  • Downgrade status           │                        │
│                    └───────────────────────────────┘                        │
│                                    │                                         │
│                                    ▼                                         │
│                              Proceed to                                      │
│                              Phase 4: Viability                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Agent Specifications

### Build Crew (Forge) - Feasibility Assessment

#### F1: UX/UI Designer Agent (Feasibility Role)

| Attribute | Value |
|-----------|-------|
| **ID** | F1 |
| **Name** | UX/UI Designer Agent |
| **Founder** | Forge |
| **Role** | Map VPC features to technical requirements |
| **Goal** | Translate value map into buildable specifications |

**Feasibility Tasks:**
1. `extract_feature_requirements` - List features from VPC Value Map
2. `assess_ui_complexity` - Score 1-10 UI complexity
3. `design_lite_variant` - Minimal viable feature set for downgrade

---

#### F2: Frontend Developer Agent (Feasibility Role)

| Attribute | Value |
|-----------|-------|
| **ID** | F2 |
| **Name** | Frontend Developer Agent |
| **Founder** | Forge |
| **Role** | Assess frontend technical feasibility |
| **Goal** | Identify frontend constraints and estimate effort |

**Feasibility Tasks:**
1. `assess_frontend_complexity` - Evaluate build difficulty
2. `identify_framework_requirements` - Required libraries/frameworks
3. `estimate_frontend_effort` - Developer hours estimate
4. `flag_frontend_constraints` - Technical blockers

---

#### F3: Backend Developer Agent (Feasibility Role)

| Attribute | Value |
|-----------|-------|
| **ID** | F3 |
| **Name** | Backend Developer Agent |
| **Founder** | Forge |
| **Role** | Assess backend architecture and set feasibility signal |
| **Goal** | Determine technical viability and infrastructure costs |

**Feasibility Tasks:**
1. `assess_backend_architecture` - Evaluate complexity
2. `evaluate_api_integrations` - Required third-party services
3. `estimate_infrastructure_costs` - Monthly hosting/API costs
4. `identify_technical_constraints` - Blockers, limitations
5. `set_feasibility_signal` - GREEN, ORANGE, or RED

**Tools:**
- `TechStackValidator` - Validate architecture choices
- `APIIntegrationTool` - Check API availability/costs
- `CostEstimatorTool` - Calculate infrastructure costs

---

## Innovation Physics Routing

### Feasibility Router Logic

```python
@router("route_after_feasibility")
def route_after_feasibility(self):
    signal = self.state.feasibility_signal

    # GREEN: Fully feasible - proceed
    if signal == FeasibilitySignal.GREEN:
        return "run_viability_analysis"

    # ORANGE: Constrained - downgrade protocol
    if signal == FeasibilitySignal.ORANGE_CONSTRAINED:
        self.state.last_pivot_type = PivotType.FEATURE_PIVOT
        self.state.downgrade_active = True

        # Apply downgrade
        ForgeCrew().apply_downgrade_to_vpc(
            project_id=self.state.project_id,
            vpc_url=self.state.vpc_document_url,
            constraints=self.state.feasibility_artifact.removed_features,
        )

        # Must re-test desirability with downgraded version
        return "run_desirability_experiments"

    # RED: Impossible - kill
    if signal == FeasibilitySignal.RED_IMPOSSIBLE:
        self.state.phase = Phase.KILLED
        self.state.last_pivot_type = PivotType.KILL
        return "terminal_killed"
```

### Downgrade Protocol

The **Downgrade Protocol** is a key Innovation Physics concept:

1. **Detection**: F3 identifies features that are technically impossible or prohibitively expensive
2. **Design**: F1 creates a "lite" version without those features
3. **Mark**: `downgrade_active = True` in state
4. **Retest**: Return to Phase 2 Desirability with the lite version
5. **Validate**: Confirm customers still want the downgraded product
6. **Continue or Kill**: If still wanted, proceed to Viability; if not, pivot or kill

**Key Insight**: A product that's desirable but not feasible is a beautiful fiction. A product that's feasible but not desirable (after downgrade) is a solution without a problem.

---

## Output Schemas

### Feasibility Artifact

```python
class FeasibilityArtifact(BaseModel):
    """Phase 3 output artifact."""

    build_id: str
    project_id: str

    # MVP reference
    mvp_url: Optional[HttpUrl] = None

    # Cost estimates (monthly)
    api_cost_estimate_monthly_usd: float = 0.0
    infra_cost_estimate_monthly_usd: float = 0.0
    development_cost_estimate_usd: float = 0.0

    # Feature analysis
    removed_features: List[str] = []  # Infeasible features
    retained_features: List[str] = []  # Feasible features
    modified_features: List[str] = []  # Simplified features

    # Technical assessment
    technical_complexity_score: int = 0  # 1-10
    frontend_complexity_score: int = 0   # 1-10
    backend_complexity_score: int = 0    # 1-10

    # Constraints
    technical_constraints: List[str] = []
    regulatory_constraints: List[str] = []
    resource_constraints: List[str] = []

    # Signal
    feasibility_signal: FeasibilitySignal = FeasibilitySignal.UNKNOWN

    # Notes
    notes: Optional[str] = None


class FeasibilityResult(BaseModel):
    """Complete Phase 3 result."""

    project_id: str
    artifact: FeasibilityArtifact

    # Downgrade tracking
    downgrade_active: bool = False
    downgrade_reason: Optional[str] = None
    original_features: List[str] = []
    lite_features: List[str] = []

    # Decision trail
    assessment_notes: str = ""
    constraints_summary: str = ""

    # Exit status
    exit_ready: bool = False
    proceed_to_viability: bool = False
```

---

## HITL Checkpoints

### `approve_feasibility_gate`

| Attribute | Value |
|-----------|-------|
| **Checkpoint ID** | `approve_feasibility_gate` |
| **Phase** | 3 |
| **Owner** | Forge (F3) + Guardian (G1) |
| **Purpose** | Confirm feasibility assessment and approve technical approach |
| **Required for Exit** | Yes |

**Presentation:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     FEASIBILITY ASSESSMENT COMPLETE                          │
│                                                                              │
│  Technical evaluation of your validated value proposition.                   │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  FEASIBILITY SIGNAL: [GREEN / ORANGE / RED]                                 │
│                                                                              │
│  TECHNICAL COMPLEXITY: [Score]/10                                           │
│  ├── Frontend: [Score]/10                                                   │
│  ├── Backend: [Score]/10                                                    │
│  └── Integrations: [Count] third-party APIs                                 │
│                                                                              │
│  COST ESTIMATES (Monthly)                                                    │
│  ├── Development: $[Amount]                                                 │
│  ├── Infrastructure: $[Amount]                                              │
│  └── API Costs: $[Amount]                                                   │
│                                                                              │
│  CONSTRAINTS IDENTIFIED                                                      │
│  [List of technical/regulatory/resource constraints]                        │
│                                                                              │
│  [IF ORANGE - DOWNGRADE REQUIRED]                                           │
│  Features to remove: [List]                                                 │
│  Lite version will be re-tested for desirability                            │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  [APPROVE & CONTINUE]     [REQUEST REVIEW]     [KILL PROJECT]               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Agent Summary

| ID | Agent | Founder | Role |
|----|-------|---------|------|
| F1 | UX/UI Designer | Forge | Map features to requirements |
| F2 | Frontend Developer | Forge | Assess frontend feasibility |
| F3 | Backend Developer | Forge | Assess backend feasibility, set signal |
| G1 | QA Agent | Guardian | Gate validation |

**Total Phase 3 Agents: 4** (reusing Forge crew from Phase 2)
**Total Phase 3 HITL Checkpoints: 1**

---

## Methodology Compliance

| Pattern | Implementation |
|---------|----------------|
| **Feasibility Gate** | Validates "Can we build it?" before viability |
| **Downgrade Protocol** | Innovation Physics pattern for constrained features |
| **Learning Cards** | Constraints and removed features documented |
| **Evidence-Based** | Signal based on technical assessment, not intuition |

---

**Document Version**: 1.0.0
**Last Updated**: 2026-01-06
**Previous Phase**: [06-phase-2-desirability.md](./06-phase-2-desirability.md)
**Next Phase**: [08-phase-4-viability.md](./08-phase-4-viability.md)
