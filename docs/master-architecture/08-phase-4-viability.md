# Phase 4: Viability Validation

**Version**: 1.0.0
**Status**: Active
**Last Updated**: 2026-01-06
**Methodology Reference**: [03-methodology.md](./03-methodology.md)

---

## Purpose

Determine whether the validated, feasible value proposition **can make money**. This is the "Survival Equation" that validates the business model will generate sustainable economics.

### What This Phase IS About

- Unit economics calculation (CAC, LTV, margins)
- Business model validation
- TAM analysis
- Profitability assessment
- Final PROCEED / PIVOT / KILL decision

### What This Phase Is NOT About

- Customer validation (Phase 1-2)
- Technical feasibility (Phase 3)
- Scaling and growth optimization (post-validation)

### Entry Criteria

- Phase 3 complete: `feasibility_signal == GREEN` (or successful downgrade)
- `approve_feasibility_gate` HITL passed
- Technical approach validated

### Exit Criteria

- `viability_signal == PROFITABLE` → PROCEED
- `viability_signal == UNDERWATER/ZOMBIE_MARKET` → HITL decision required
- `request_human_decision` HITL passed with final recommendation

---

## ViabilityFlow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       VIABILITY FLOW                                         │
│                                                                              │
│  Entry: GREEN feasibility signal from Phase 3                               │
│  Exit: VALIDATED or KILLED with evidence-based recommendation               │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                    ┌───────────────────────────────┐                        │
│                    │  Feasibility Artifact         │                        │
│                    │  (From Phase 3)               │                        │
│                    └───────────────┬───────────────┘                        │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      FINANCE CREW (Ledger)                            │  │
│  │                                                                       │  │
│  │  ┌────────────────────────────────────────────────────────────┐     │  │
│  │  │  L1: FINANCIAL CONTROLLER                                   │     │  │
│  │  │                                                             │     │  │
│  │  │  • Calculate Customer Acquisition Cost (CAC)                │     │  │
│  │  │  • Calculate Lifetime Value (LTV)                           │     │  │
│  │  │  • Compute LTV:CAC ratio                                    │     │  │
│  │  │  • Estimate gross margins                                   │     │  │
│  │  │  • Calculate payback period                                 │     │  │
│  │  │  • Set VIABILITY_SIGNAL                                     │     │  │
│  │  └────────────────────────────────────────────────────────────┘     │  │
│  │                                    │                                  │  │
│  │                                    ▼                                  │  │
│  │  ┌────────────────────────────────────────────────────────────┐     │  │
│  │  │  L2: LEGAL & COMPLIANCE                                     │     │  │
│  │  │                                                             │     │  │
│  │  │  • Flag regulatory constraints affecting viability          │     │  │
│  │  │  • Identify compliance costs                                │     │  │
│  │  │  • Assess legal risks                                       │     │  │
│  │  └────────────────────────────────────────────────────────────┘     │  │
│  │                                    │                                  │  │
│  │                                    ▼                                  │  │
│  │  ┌────────────────────────────────────────────────────────────┐     │  │
│  │  │  L3: ECONOMICS REVIEWER                                     │     │  │
│  │  │                                                             │     │  │
│  │  │  • Validate unit economics assumptions                      │     │  │
│  │  │  • Apply business model-specific benchmarks                 │     │  │
│  │  │  • Document decision rationale                              │     │  │
│  │  │  • Capture learnings to flywheel                            │     │  │
│  │  └────────────────────────────────────────────────────────────┘     │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    │                                         │
│                                    ▼                                         │
│                    ┌───────────────────────────────┐                        │
│                    │  VIABILITY ASSESSMENT         │                        │
│                    │                               │                        │
│                    │  Unit Economics:              │                        │
│                    │  • CAC: $[Amount]             │                        │
│                    │  • LTV: $[Amount]             │                        │
│                    │  • LTV:CAC: [Ratio]           │                        │
│                    │  • Gross Margin: [%]          │                        │
│                    │  • Payback: [Months]          │                        │
│                    │                               │                        │
│                    │  TAM Analysis:                │                        │
│                    │  • Market Size: $[Amount]     │                        │
│                    │  • Addressable: $[Amount]     │                        │
│                    └───────────────┬───────────────┘                        │
│                                    │                                         │
│                                    ▼                                         │
│                         ┌─────────────────────┐                             │
│                         │  VIABILITY          │                             │
│                         │  ROUTER             │                             │
│                         └─────────┬───────────┘                             │
│                                   │                                          │
│          ┌────────────────────────┼────────────────────────┐                │
│          │                        │                        │                 │
│     [PROFITABLE]          [UNDERWATER]           [ZOMBIE_MARKET]            │
│          │                        │                        │                 │
│          ▼                        └────────────┬───────────┘                │
│   ┌─────────────────┐                          │                            │
│   │ VALIDATED!      │                          ▼                            │
│   │                 │               ┌─────────────────────────┐             │
│   │ Business model  │               │  STRATEGIC PIVOT        │             │
│   │ works!          │               │  REQUIRED                │             │
│   │                 │               │                         │             │
│   │ Proceed to      │               │  CAC > LTV or           │             │
│   │ execution       │               │  TAM too small          │             │
│   └────────┬────────┘               │                         │             │
│            │                        │  Requires HITL          │             │
│            │                        └───────────┬─────────────┘             │
│            │                                    │                            │
│            │                                    ▼                            │
│            │         ┌──────────────────────────────────────────────┐       │
│            │         │                SYNTHESIS CREW (Compass)       │       │
│            │         │                                               │       │
│            │         │  ┌────────────────────────────────────────┐  │       │
│            │         │  │  C1: PRODUCT PM                         │  │       │
│            │         │  │                                         │  │       │
│            │         │  │  Synthesize all evidence:               │  │       │
│            │         │  │  • Phase 1: VPC fit score              │  │       │
│            │         │  │  • Phase 2: Desirability signals       │  │       │
│            │         │  │  • Phase 3: Feasibility constraints    │  │       │
│            │         │  │  • Phase 4: Unit economics             │  │       │
│            │         │  │                                         │  │       │
│            │         │  │  Propose options with evidence          │  │       │
│            │         │  └────────────────────────────────────────┘  │       │
│            │         │                         │                     │       │
│            │         │                         ▼                     │       │
│            │         │  ┌────────────────────────────────────────┐  │       │
│            │         │  │  C2: HUMAN APPROVAL                     │  │       │
│            │         │  │                                         │  │       │
│            │         │  │  HITL: request_human_decision           │  │       │
│            │         │  │                                         │  │       │
│            │         │  │  Present options:                       │  │       │
│            │         │  │  1. PRICE_PIVOT: Raise prices          │  │       │
│            │         │  │     → Re-test desirability             │  │       │
│            │         │  │                                         │  │       │
│            │         │  │  2. COST_PIVOT: Reduce costs           │  │       │
│            │         │  │     → Re-run feasibility               │  │       │
│            │         │  │                                         │  │       │
│            │         │  │  3. MODEL_PIVOT: Change business model │  │       │
│            │         │  │     → Return to Phase 1                │  │       │
│            │         │  │                                         │  │       │
│            │         │  │  4. KILL: Terminate project            │  │       │
│            │         │  └────────────────────────────────────────┘  │       │
│            │         │                         │                     │       │
│            │         │                         ▼                     │       │
│            │         │  ┌────────────────────────────────────────┐  │       │
│            │         │  │  C3: ROADMAP WRITER                     │  │       │
│            │         │  │                                         │  │       │
│            │         │  │  Document decision:                     │  │       │
│            │         │  │  • Evidence trail                       │  │       │
│            │         │  │  • Decision rationale                   │  │       │
│            │         │  │  • Next steps                           │  │       │
│            │         │  │  • Flywheel learnings                   │  │       │
│            │         │  └────────────────────────────────────────┘  │       │
│            │         └──────────────────────────────────────────────┘       │
│            │                                    │                            │
│            │                    ┌───────────────┼───────────────┐           │
│            │                    │               │               │            │
│            │             [PRICE_PIVOT]   [COST_PIVOT]     [KILL]            │
│            │                    │               │               │            │
│            │                    ▼               ▼               ▼            │
│            │              Return to       Return to       PROJECT           │
│            │              Phase 2         Phase 3         KILLED            │
│            │              Desirability    Feasibility                       │
│            │                                                                 │
│            │                                                                 │
│            ▼                                                                 │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                      GOVERNANCE CREW (Guardian)                      │  │
│   │                                                                      │  │
│   │  G1: QA Agent - Final validation compliance                         │  │
│   │  G2: Security Agent - PII scrubbing                                 │  │
│   │  G3: Audit Agent - Persist learnings to flywheel                    │  │
│   │                                                                      │  │
│   │  Output: Audit trail + flywheel entry                               │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                         │
│                                    ▼                                         │
│                    ┌───────────────────────────────┐                        │
│                    │  TERMINAL STATE               │                        │
│                    │                               │                        │
│                    │  VALIDATED or KILLED          │                        │
│                    │  with evidence-based          │                        │
│                    │  recommendation               │                        │
│                    └───────────────────────────────┘                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Agent Specifications

### Finance Crew (Ledger)

#### L1: Financial Controller Agent

| Attribute | Value |
|-----------|-------|
| **ID** | L1 |
| **Name** | Financial Controller Agent |
| **Founder** | Ledger |
| **Role** | Calculate unit economics and set viability signal |
| **Goal** | Determine if business model is sustainable |

**Tasks:**
1. `calculate_cac` - Customer Acquisition Cost from experiment data
2. `calculate_ltv` - Lifetime Value from pricing and churn estimates
3. `compute_ltv_cac_ratio` - Key viability metric
4. `estimate_gross_margins` - Revenue minus COGS
5. `calculate_payback_period` - Months to recover CAC
6. `analyze_tam` - Total Addressable Market
7. `set_viability_signal` - PROFITABLE, UNDERWATER, or ZOMBIE_MARKET

**Tools:**
- `PythonREPLTool` - Financial calculations
- `CostTrackingTool` - Track actual costs
- `AnalyticsTool` - Query experiment metrics
- `UnitEconomicsModels` - 10 business model templates

**Viability Signal Logic:**
```python
def set_viability_signal(self, metrics: ViabilityMetrics) -> ViabilitySignal:
    ltv_cac_ratio = metrics.ltv_usd / metrics.cac_usd if metrics.cac_usd > 0 else 0

    # PROFITABLE: LTV:CAC > 3:1 (healthy)
    if ltv_cac_ratio >= 3.0:
        return ViabilitySignal.PROFITABLE

    # ZOMBIE_MARKET: Profitable but TAM too small
    if ltv_cac_ratio >= 1.0 and metrics.tam_annual_revenue_potential_usd < 1_000_000:
        return ViabilitySignal.ZOMBIE_MARKET

    # UNDERWATER: CAC > LTV
    return ViabilitySignal.UNDERWATER
```

---

#### L2: Legal & Compliance Agent

| Attribute | Value |
|-----------|-------|
| **ID** | L2 |
| **Name** | Legal & Compliance Agent |
| **Founder** | Ledger |
| **Role** | Identify regulatory and compliance constraints |
| **Goal** | Flag viability risks from legal/regulatory requirements |

**Tasks:**
1. `identify_regulatory_constraints` - Industry-specific regulations
2. `estimate_compliance_costs` - Cost of compliance
3. `assess_legal_risks` - Liability exposure

**Tools:**
- `RegulatorySearchTool` - Research regulations

---

#### L3: Economics Reviewer Agent

| Attribute | Value |
|-----------|-------|
| **ID** | L3 |
| **Name** | Economics Reviewer Agent |
| **Founder** | Ledger |
| **Role** | Validate assumptions and document learnings |
| **Goal** | Ensure unit economics are sound and capture insights |

**Tasks:**
1. `validate_assumptions` - Sanity check inputs
2. `apply_benchmarks` - Compare to industry standards
3. `document_rationale` - Explain calculations
4. `capture_learnings` - Feed flywheel

**Tools:**
- `IndustryBenchmarkTool` - Industry comparisons
- `LearningCaptureTool` - Flywheel persistence
- `BusinessModelClassifier` - Identify business model type

---

### Synthesis Crew (Compass)

#### C1: Product PM Agent

| Attribute | Value |
|-----------|-------|
| **ID** | C1 |
| **Name** | Product PM Agent |
| **Founder** | Compass |
| **Role** | Synthesize evidence and propose decision options |
| **Goal** | Create clear, evidence-based recommendations |

**Tasks:**
1. `synthesize_evidence` - Compile all phase evidence
2. `propose_options` - Generate pivot/proceed options
3. `rank_recommendations` - Order by evidence strength

**Tools:**
- `StateInspectionTool` - Read full state
- `SynthesisTool` - Evidence aggregation

---

#### C2: Human Approval Agent

| Attribute | Value |
|-----------|-------|
| **ID** | C2 |
| **Name** | Human Approval Agent |
| **Founder** | Compass |
| **Role** | Present options and manage HITL decision |
| **Goal** | Get human decision on strategic pivot |

**Tasks:**
1. `present_viability_decision` - Display options to human
2. `collect_decision` - Record human choice
3. `route_based_on_decision` - Direct flow accordingly

**Tools:**
- `ApprovalRequestTool` - HITL interface

---

#### C3: Roadmap Writer Agent

| Attribute | Value |
|-----------|-------|
| **ID** | C3 |
| **Name** | Roadmap Writer Agent |
| **Founder** | Compass |
| **Role** | Document decisions and update roadmap |
| **Goal** | Create clear record of decision and next steps |

**Tasks:**
1. `document_decision` - Record what was decided
2. `update_roadmap` - Next steps if proceeding
3. `write_postmortem` - Learnings if killing
4. `persist_to_flywheel` - Capture for future projects

**Tools:**
- `LearningCaptureTool` - Flywheel persistence
- `FileWriteTool` - Document generation

---

## Innovation Physics Routing

### Viability Router Logic

```python
@router("route_after_viability")
def route_after_viability(self):
    signal = self.state.viability_signal

    # PROFITABLE: Business model works!
    if signal == ViabilitySignal.PROFITABLE:
        self.state.phase = Phase.VALIDATED
        self.state.last_pivot_type = PivotType.NONE
        return "terminal_validated"

    # UNDERWATER or ZOMBIE_MARKET: Strategic pivot required
    if signal in (ViabilitySignal.UNDERWATER, ViabilitySignal.ZOMBIE_MARKET):
        self.state.human_approval_status = HumanApprovalStatus.PENDING
        self.state.human_input_required = True
        self.state.pivot_recommendation = PivotType.MODEL_PIVOT

        # Request human decision
        compass = CompassCrew()
        compass.request_viability_decision(
            project_id=self.state.project_id,
            metrics=self.state.viability_metrics,
            options=["PRICE_PIVOT", "COST_PIVOT", "MODEL_PIVOT", "KILL"],
        )
        return "await_viability_decision"
```

### Strategic Pivot Options

| Pivot | Trigger | Action | Next Step |
|-------|---------|--------|-----------|
| **PRICE_PIVOT** | LTV too low | Increase price | Re-test Phase 2 Desirability |
| **COST_PIVOT** | CAC too high | Reduce costs | Re-run Phase 3 Feasibility |
| **MODEL_PIVOT** | Fundamental issue | Change business model | Return to Phase 1 |
| **KILL** | No viable path | Terminate project | Document learnings |

---

## Output Schemas

### Viability Metrics

```python
class ViabilityMetrics(BaseModel):
    """Core unit economics metrics."""

    # Acquisition
    cac_usd: float = 0.0
    cac_breakdown: Optional[Dict[str, float]] = None  # {"paid": 150, "organic": 50}

    # Lifetime Value
    ltv_usd: float = 0.0
    ltv_breakdown: Optional[Dict[str, float]] = None  # {"subscription": 800, "upsell": 200}

    # Key Ratios
    ltv_cac_ratio: float = 0.0
    gross_margin_pct: float = 0.0
    payback_months: float = 0.0
    monthly_churn_pct: float = 0.0

    # Market
    tam_annual_revenue_potential_usd: float = 0.0

    # Business Model
    business_model_type: Optional[BusinessModelType] = None
    model_specific_metrics: Optional[Dict[str, Any]] = None


class ViabilityResult(BaseModel):
    """Phase 4 output artifact."""

    project_id: str
    metrics: ViabilityMetrics

    # Signal
    viability_signal: ViabilitySignal

    # Decision
    human_decision: Optional[str] = None
    decision_rationale: str = ""

    # Next action
    next_action: Literal["PROCEED", "PRICE_PIVOT", "COST_PIVOT", "MODEL_PIVOT", "KILL"]

    # Final status
    validation_complete: bool = False
    final_recommendation: str = ""
```

### Final Validation Report

```python
class FinalValidationReport(BaseModel):
    """Complete validation summary across all phases."""

    project_id: str
    project_name: str
    validation_started: datetime
    validation_completed: datetime

    # Phase summaries
    phase_0_summary: str  # Founder's Brief
    phase_1_summary: str  # VPC fit score
    phase_2_summary: str  # Desirability evidence
    phase_3_summary: str  # Feasibility assessment
    phase_4_summary: str  # Viability analysis

    # Evidence trail
    total_experiments_run: int
    total_pivots_executed: int
    pivot_history: List[PivotType]

    # Final metrics
    final_fit_score: float
    final_desirability_signal: DesirabilitySignal
    final_feasibility_signal: FeasibilitySignal
    final_viability_signal: ViabilitySignal

    # Unit economics
    final_cac: float
    final_ltv: float
    final_ltv_cac_ratio: float

    # Decision
    final_decision: Literal["VALIDATED", "KILLED"]
    decision_rationale: str

    # Flywheel entry
    key_learnings: List[str]
    methodology_improvements: List[str]
```

---

## HITL Checkpoints

### `approve_viability_gate`

| Attribute | Value |
|-----------|-------|
| **Checkpoint ID** | `approve_viability_gate` |
| **Phase** | 4 |
| **Owner** | Ledger (L1) + Guardian (G1) |
| **Purpose** | Confirm viability assessment before final decision |
| **Required for Exit** | Only if PROFITABLE (auto-proceeds) |

---

### `request_human_decision`

| Attribute | Value |
|-----------|-------|
| **Checkpoint ID** | `request_human_decision` |
| **Phase** | 4 |
| **Owner** | Compass (C2) |
| **Purpose** | Final strategic decision on UNDERWATER/ZOMBIE_MARKET |
| **Required for Exit** | Yes (if not PROFITABLE) |

**Presentation:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     VIABILITY DECISION REQUIRED                              │
│                                                                              │
│  Your validated, feasible product has a unit economics challenge.            │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  VIABILITY SIGNAL: UNDERWATER / ZOMBIE_MARKET                               │
│                                                                              │
│  UNIT ECONOMICS                                                              │
│  ├── Customer Acquisition Cost: $[CAC]                                      │
│  ├── Lifetime Value: $[LTV]                                                 │
│  ├── LTV:CAC Ratio: [Ratio] (target: ≥ 3.0)                                │
│  ├── Gross Margin: [%]                                                      │
│  └── Payback Period: [Months]                                               │
│                                                                              │
│  THE ISSUE                                                                   │
│  [UNDERWATER: CAC exceeds LTV - you lose money on every customer]           │
│  [ZOMBIE_MARKET: Unit economics work but TAM is too small to matter]        │
│                                                                              │
│  EVIDENCE SYNTHESIS                                                          │
│  [Summary of all phase evidence supporting recommendation]                  │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  YOUR OPTIONS                                                                │
│                                                                              │
│  1. PRICE PIVOT                                                              │
│     Increase prices to improve LTV                                          │
│     → We'll re-test desirability at the new price point                     │
│     Risk: Customers may not pay more                                        │
│                                                                              │
│  2. COST PIVOT                                                               │
│     Reduce costs to improve unit economics                                  │
│     → We'll re-evaluate feasibility with lower costs                        │
│     Risk: May require feature cuts                                          │
│                                                                              │
│  3. MODEL PIVOT                                                              │
│     Change fundamental business model                                        │
│     → Return to Phase 1 with new model hypothesis                           │
│     Risk: Starting over with new assumptions                                │
│                                                                              │
│  4. KILL PROJECT                                                             │
│     Terminate and document learnings                                        │
│     → Evidence captured for future projects                                 │
│     Outcome: Valuable learning, no further investment                       │
│                                                                              │
│  [PRICE PIVOT]  [COST PIVOT]  [MODEL PIVOT]  [KILL PROJECT]                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Agent Summary

| ID | Agent | Founder | Role |
|----|-------|---------|------|
| L1 | Financial Controller | Ledger | Calculate unit economics |
| L2 | Legal & Compliance | Ledger | Regulatory constraints |
| L3 | Economics Reviewer | Ledger | Validate assumptions |
| C1 | Product PM | Compass | Synthesize evidence |
| C2 | Human Approval | Compass | HITL decision |
| C3 | Roadmap Writer | Compass | Document decision |
| G1 | QA Agent | Guardian | Final validation |
| G2 | Security Agent | Guardian | PII scrubbing |
| G3 | Audit Agent | Guardian | Flywheel persistence |

**Total Phase 4 Agents: 9**
**Total Phase 4 HITL Checkpoints: 2**

---

## Business Model Classification

Viability calculations are adjusted based on business model type:

| Model Type | LTV:CAC Target | Payback Target | Key Metric |
|------------|----------------|----------------|------------|
| SaaS B2B SMB | ≥ 3:1 | ≤ 12 months | Monthly churn |
| SaaS B2B Enterprise | ≥ 4:1 | ≤ 18 months | Net revenue retention |
| SaaS B2C Freemium | ≥ 3:1 | ≤ 6 months | Conversion rate |
| eCommerce DTC | ≥ 2:1 | ≤ 3 months | Repeat purchase rate |
| Marketplace | N/A | N/A | Take rate |
| Fintech B2C | ≥ 4:1 | ≤ 12 months | Default rate |

---

## Methodology Compliance

| Pattern | Implementation |
|---------|----------------|
| **Viability Gate** | Validates "Can we make money?" |
| **Unit Economics** | CAC, LTV, LTV:CAC ratio, payback |
| **TAM Analysis** | Market size validation |
| **Strategic Pivots** | PRICE, COST, MODEL, KILL options |
| **HITL Decision** | Human makes final call on strategic pivot |
| **Flywheel Learning** | All outcomes captured for future projects |

---

## Strategyzer Framework Mapping

Phase 4 validates the **economics** of the Business Model Canvas. See [03-methodology.md](./03-methodology.md) for the complete VPC → BMC framework mapping.

### BMC Blocks Validated in Phase 4

```
┌─────────────────────────────────────────────────────────────────┐
│                    BUSINESS MODEL CANVAS                        │
├─────────────┬─────────────┬───────────────┬─────────────────────┤
│ Key         │ Key         │ Value         │ Customer      │ Customer   │
│ Partners    │ Activities  │ Propositions  │ Relationships │ Segments   │
│             │             │ ████████████  │               │            │
│             │             │ [RE-CHECKED]  │               │            │
├─────────────┴─────────────┼───────────────┼───────────────┴─────┤
│ Key Resources             │               │ Channels            │
│ █████████████████████████ │               │ ████████████████████│
│ [RE-CHECKED]              │               │ [RE-CHECKED]        │
├───────────────────────────┴───────────────┴─────────────────────┤
│ Cost Structure                 │ Revenue Streams               │
│ ██████████████████████████████ │ ████████████████████████████ │
│ [VALIDATED]                    │ [VALIDATED]                   │
└────────────────────────────────┴────────────────────────────────┘

████ = Validated in Phase 4 (Viability)
```

### Evidence → BMC Block Mapping

| BMC Block | What's Validated | Evidence Source | Viability Signal |
|-----------|------------------|-----------------|------------------|
| **Cost Structure** | What does it cost to operate? | Development + infrastructure + API costs (from Phase 3) + CAC | Cost breakdown analysis |
| **Revenue Streams** | Can we generate sustainable revenue? | LTV calculation, pricing validation, churn estimates | `ltv_cac_ratio ≥ 3.0` |
| **Value Propositions** (Re-checked) | Does the value justify the cost? | Unit economics vs value delivered | Margin analysis |
| **Key Resources** (Re-checked) | Are resource costs sustainable? | Infrastructure cost vs revenue | Cost efficiency ratios |
| **Channels** (Re-checked) | Are acquisition channels profitable? | CAC by channel analysis | Channel ROI |

### Phase 4 Exit Contribution to BMC

Upon successful Phase 4 completion, the entire BMC should be validated:

1. **Cost Structure** → All operational costs identified and quantified
2. **Revenue Streams** → Pricing model validated with sustainable unit economics
3. **Complete BMC** → All 9 blocks validated across the validation funnel

### The Complete BMC Validation Sequence

| Phase | BMC Blocks | Question Answered |
|-------|-----------|-------------------|
| **Phase 1** | Customer Segments, Value Propositions | "Who has this problem? What value can we offer?" |
| **Phase 2** | + Channels, Customer Relationships | "Do they want it? How do we reach them?" |
| **Phase 3** | + Key Activities, Key Resources, Key Partners | "Can we build and deliver it?" |
| **Phase 4** | + Cost Structure, Revenue Streams | "Can we make money doing it?" |

### Strategic Pivot Impact on BMC

When viability fails, strategic pivots affect specific BMC blocks:

| Pivot | Primary BMC Impact | Secondary Impact |
|-------|-------------------|------------------|
| **PRICE_PIVOT** | Revenue Streams (pricing model) | May affect Customer Segments |
| **COST_PIVOT** | Cost Structure, Key Resources | May affect Key Activities |
| **MODEL_PIVOT** | All 9 blocks | Full BMC redesign required |

---

## Validation Funnel Summary

```
PHASE 0: ONBOARDING
├── Input: Raw idea
├── Output: Founder's Brief
└── Gate: approve_founders_brief

PHASE 1: VPC DISCOVERY
├── Input: Founder's Brief
├── Output: Validated VPC (fit ≥ 70)
└── Gate: approve_vpc_completion

PHASE 2: DESIRABILITY
├── Input: Validated VPC
├── Output: STRONG_COMMITMENT signal
├── Pivots: SEGMENT_PIVOT, VALUE_PIVOT
└── Gate: approve_desirability_gate

PHASE 3: FEASIBILITY
├── Input: Desirability evidence
├── Output: GREEN signal (or successful downgrade)
├── Pivots: FEATURE_PIVOT, KILL
└── Gate: approve_feasibility_gate

PHASE 4: VIABILITY
├── Input: Feasibility artifact
├── Output: PROFITABLE signal OR human decision
├── Pivots: PRICE_PIVOT, COST_PIVOT, MODEL_PIVOT, KILL
└── Gate: request_human_decision

TERMINAL: VALIDATED or KILLED
├── Evidence trail documented
├── Learnings captured to flywheel
└── Recommendation delivered
```

---

**Document Version**: 1.0.0
**Last Updated**: 2026-01-06
**Previous Phase**: [07-phase-3-feasibility.md](./07-phase-3-feasibility.md)
**Final Phase**: This is the terminal validation phase
