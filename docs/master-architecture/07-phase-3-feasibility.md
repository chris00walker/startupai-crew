---
purpose: Phase 3 specification - Feasibility validation (can we build it?)
status: active
last_reviewed: 2026-01-07
vpd_compliance: true
---

# Phase 3: Feasibility Validation

> **Methodology Reference**: See [03-methodology.md](./03-methodology.md) for VPD framework patterns.

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

## CrewAI Pattern Mapping

> **Pattern Reference**: See [00-introduction.md](./00-introduction.md) for CrewAI pattern hierarchy.

| Pattern | This Phase |
|---------|------------|
| **Phase** | Phase 3: Feasibility Validation (business concept) |
| **Flow** | `FeasibilityFlow` (orchestrates 2 crews) |
| **Crews** | `BuildCrew`, `GovernanceCrew` |
| **Agents** | 5 total (F1-F3 reused, G1, G2) |

### Crew Composition

| Crew | Agents | Purpose |
|------|--------|---------|
| **BuildCrew** | F1, F2, F3 | Technical feasibility assessment |
| **GovernanceCrew** | G1, G2 | Gate validation + security review |

---

## FeasibilityFlow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       FEASIBILITY FLOW                                       │
│                                                                              │
│  Entry: STRONG_COMMITMENT from Phase 2                                      │
│                                                                              │
│  Flow: FeasibilityFlow                                                       │
│  Crews: BuildCrew, GovernanceCrew                                           │
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

### Governance Crew (Guardian) - Feasibility Validation

#### G1: QA Agent (Feasibility Role)

| Attribute | Value |
|-----------|-------|
| **ID** | G1 |
| **Name** | QA Agent |
| **Founder** | Guardian |
| **Role** | Validate feasibility assessment methodology and gate criteria |
| **Goal** | Ensure feasibility analysis follows VPD methodology |

**Feasibility Tasks:**
1. `validate_assessment_methodology` - Check technical assessment follows standards
2. `verify_constraint_documentation` - Ensure all constraints are properly documented
3. `confirm_gate_readiness` - Validate phase exit criteria met

---

#### G2: Security Agent (Feasibility Role)

| Attribute | Value |
|-----------|-------|
| **ID** | G2 |
| **Name** | Security Agent |
| **Founder** | Guardian |
| **Role** | Review architecture security posture |
| **Goal** | Identify security constraints and validate technical security choices |

**Feasibility Tasks:**
1. `review_architecture_security` - Assess security implications of proposed architecture
2. `identify_security_constraints` - Flag security-related technical constraints
3. `validate_data_handling` - Ensure PII/sensitive data handling is feasible

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
| **Owner** | Forge (F3) + Guardian (G1, G2) |
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

## Summary

### CrewAI Pattern Summary

| Pattern | Implementation |
|---------|----------------|
| **Phase** | Phase 3: Feasibility Validation |
| **Flow** | `FeasibilityFlow` |
| **Crews** | 2 crews (see below) |

### Crew Summary

| Crew | Agents | Purpose |
|------|--------|---------|
| `BuildCrew` | F1, F2, F3 | Technical feasibility assessment |
| `GovernanceCrew` | G1, G2 | Gate validation + security review |

### Agent Summary

| ID | Agent | Founder | Crew | Role |
|----|-------|---------|------|------|
| F1 | UX/UI Designer | Forge | BuildCrew | Map features to requirements |
| F2 | Frontend Developer | Forge | BuildCrew | Assess frontend feasibility |
| F3 | Backend Developer | Forge | BuildCrew | Assess backend feasibility, set signal |
| G1 | QA Agent | Guardian | GovernanceCrew | Gate validation |
| G2 | Security Agent | Guardian | GovernanceCrew | Architecture security review |

**Phase 3 Totals:**
- Flows: 1 (`FeasibilityFlow`)
- Crews: 2 (reusing BuildCrew from Phase 2)
- Agents: 5
- HITL Checkpoints: 1

### Agent Configuration Summary

| Agent | Crew | Tools | Temperature | Notes |
|-------|------|-------|-------------|-------|
| F1 | Build | ComponentLibraryScraperTool (STUB) | 0.6 | Feature extraction from VPC |
| F2 | Build | CodeValidatorTool (EXISTS) | 0.3 | Frontend complexity assessment |
| F3 | Build | TechStackValidator (STUB), APIIntegrationTool (STUB), CostEstimatorTool (STUB) | 0.2 | Sets FEASIBILITY_SIGNAL |
| G1 | Governance | MethodologyCheckTool (EXISTS), GuardianReviewTool (EXISTS) | 0.1 | Gate validation |
| G2 | Governance | PrivacyGuardTool (EXISTS) | 0.1 | Architecture security review |

**Tool Status Summary:**
- **EXISTS**: 4 tools (CodeValidatorTool, MethodologyCheckTool, GuardianReviewTool, PrivacyGuardTool)
- **STUB**: 4 tools (ComponentLibraryScraperTool, TechStackValidator, APIIntegrationTool, CostEstimatorTool)

**Configuration Notes:**
- F1-F3 are **reused from Phase 2** with different task context (feasibility assessment vs asset generation)
- Lower temperatures for analysis work (0.2-0.3) vs creative work (0.6-0.8 in Phase 2)
- G1-G2 are **reused from Phase 2** with identical configuration
- All agents have `reasoning=True`, `inject_date=True`, `max_iter=20`

---

## Methodology Compliance

| Pattern | Implementation |
|---------|----------------|
| **Feasibility Gate** | Validates "Can we build it?" before viability |
| **Downgrade Protocol** | Innovation Physics pattern for constrained features |
| **Learning Cards** | Constraints and removed features documented |
| **Evidence-Based** | Signal based on technical assessment, not intuition |

---

## Strategyzer Framework Mapping

Phase 3 validates the **supply-side** of the Business Model Canvas. See [03-methodology.md](./03-methodology.md) for the complete VPC → BMC framework mapping.

### BMC Blocks Validated in Phase 3

```
┌─────────────────────────────────────────────────────────────────┐
│                    BUSINESS MODEL CANVAS                        │
├─────────────┬─────────────┬───────────────┬─────────────────────┤
│ Key         │ Key         │ Value         │ Customer      │ Customer   │
│ Partners    │ Activities  │ Propositions  │ Relationships │ Segments   │
│ ████████████│ ████████████│ ████████████  │               │            │
│ [VALIDATED] │ [VALIDATED] │ [RE-CHECKED]  │               │            │
├─────────────┴─────────────┼───────────────┼───────────────┴─────┤
│ Key Resources             │               │ Channels            │
│ ██████████████████████████│               │                     │
│ [VALIDATED]               │               │                     │
├───────────────────────────┴───────────────┴─────────────────────┤
│ Cost Structure                 │ Revenue Streams               │
└────────────────────────────────┴────────────────────────────────┘

████ = Validated in Phase 3 (Feasibility)
```

### Evidence → BMC Block Mapping

| BMC Block | What's Validated | Evidence Source | Feasibility Signal |
|-----------|------------------|-----------------|-------------------|
| **Value Propositions** | Can we technically deliver? | Architecture assessment, constraint analysis | `feasibility_signal` |
| **Key Activities** | What must we do to deliver? | Technical breakdown, workflow mapping | Complexity scores |
| **Key Resources** | What do we need to build it? | Infrastructure audit, tooling requirements | Cost estimates |
| **Key Partners** | Who provides critical inputs? | Third-party API evaluation, supplier assessment | Integration feasibility |

### Phase 3 Exit Contribution to BMC

Upon successful Phase 3 completion, the following BMC blocks should have validated hypotheses:

1. **Key Activities** → Confirmed what operations are required to deliver the value proposition
2. **Key Resources** → Validated what assets, infrastructure, and tools are needed
3. **Key Partners** → Identified which third-party services and partnerships are essential
4. **Value Propositions** (Re-checked) → Confirmed technical feasibility of promised features

### Downgrade Impact on BMC

If `ORANGE_CONSTRAINED` signal triggers the Downgrade Protocol:

| Affected Block | Impact |
|---------------|--------|
| **Value Propositions** | Features removed or simplified |
| **Key Activities** | Scope reduced, complexity lowered |
| **Key Resources** | Resource requirements reduced |
| **Key Partners** | May eliminate need for certain partners |

The downgraded VPC must be re-tested in Phase 2 (Desirability) to confirm customers still want the constrained version before proceeding to Phase 4 (Viability).

---

## Related Documents

### Architecture
- [00-introduction.md](./00-introduction.md) - Quick start and orientation
- [01-ecosystem.md](./01-ecosystem.md) - Three-service architecture overview
- [02-organization.md](./02-organization.md) - 6 AI Founders and agents
- [03-methodology.md](./03-methodology.md) - VPD framework reference

### Phase Specifications
- [04-phase-0-onboarding.md](./04-phase-0-onboarding.md) - Quick Start onboarding
- [05-phase-1-vpc-discovery.md](./05-phase-1-vpc-discovery.md) - VPC Discovery
- [06-phase-2-desirability.md](./06-phase-2-desirability.md) - Desirability validation (previous phase)
- **Phase 3: Feasibility** - (this document)
- [08-phase-4-viability.md](./08-phase-4-viability.md) - Viability + Decision (next phase)

### Reference
- [09-status.md](./09-status.md) - Current implementation status
- [reference/api-contracts.md](./reference/api-contracts.md) - API specifications
- [reference/approval-workflows.md](./reference/approval-workflows.md) - HITL patterns
