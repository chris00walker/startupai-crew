---
purpose: Phase 2 specification - Desirability validation (do customers want it?)
status: active
last_reviewed: 2026-01-07
vpd_compliance: true
---

# Phase 2: Desirability Validation

> **Methodology Reference**: See [03-methodology.md](./03-methodology.md) for VPD framework patterns.

## Purpose

Test whether customers **actually want** the value proposition designed in Phase 1. This is the "Truth Engine" that validates the Value Proposition Canvas against real market behavior.

### What This Phase IS About

- Building testable artifacts (landing pages, ads, MVPs)
- Running growth experiments with real traffic
- Collecting DO evidence (clicks, signups, payments)
- Computing Innovation Physics signals (`problem_resonance`, `zombie_ratio`)
- Achieving STRONG_COMMITMENT before proceeding

### What This Phase Is NOT About

- Technical feasibility (Phase 3)
- Unit economics and profitability (Phase 4)
- Scaling or growth (post-validation)

### Entry Criteria

- Phase 1 complete: VPC approved with fit ≥ 70
- `approve_vpc_completion` HITL passed
- Customer Profile and Value Map validated

### Exit Criteria

- `desirability_signal == STRONG_COMMITMENT`
- `problem_resonance ≥ 0.3` (30% of target audience resonates)
- `zombie_ratio < 0.7` (commitment is real, not just interest)
- `approve_desirability_gate` HITL passed

---

## CrewAI Pattern Mapping

> **Pattern Reference**: See [00-introduction.md](./00-introduction.md) for CrewAI pattern hierarchy.

| Pattern | This Phase |
|---------|------------|
| **Phase** | Phase 2: Desirability Validation (business concept) |
| **Flow** | `DesirabilityFlow` (orchestrates 3 crews) |
| **Crews** | `BuildCrew`, `GrowthCrew`, `GovernanceCrew` |
| **Agents** | 9 total (F1-F3, P1-P3, G1-G3) |

### Crew Composition

| Crew | Agents | Purpose |
|------|--------|---------|
| **BuildCrew** | F1, F2, F3 | Build landing pages and testable artifacts |
| **GrowthCrew** | P1, P2, P3 | Run ad campaigns, collect desirability evidence |
| **GovernanceCrew** | G1, G2, G3 | QA validation, security, audit |

---

## DesirabilityFlow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       DESIRABILITY FLOW                                      │
│                                                                              │
│  Entry: Validated VPC from Phase 1                                          │
│  Exit: STRONG_COMMITMENT signal OR pivot recommendation                     │
│                                                                              │
│  Flow: DesirabilityFlow                                                      │
│  Crews: BuildCrew, GrowthCrew, GovernanceCrew                               │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                    ┌───────────────────────────────┐                        │
│                    │     Validated VPC             │                        │
│                    │     (From Phase 1)            │                        │
│                    └───────────────┬───────────────┘                        │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      BUILD CREW (Forge)                               │  │
│  │                                                                       │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐         │  │
│  │  │ F1: UX/UI      │  │ F2: Frontend   │  │ F3: Backend    │         │  │
│  │  │ Designer       │  │ Developer      │  │ Developer      │         │  │
│  │  │                │  │                │  │                │         │  │
│  │  │ Design LP      │  │ Build LP       │  │ Deploy LP      │         │  │
│  │  │ wireframes     │  │ (Next.js)      │  │ (Netlify)      │         │  │
│  │  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘         │  │
│  │          │                   │                   │                   │  │
│  │          └───────────────────┼───────────────────┘                   │  │
│  │                              │                                        │  │
│  │                              ▼                                        │  │
│  │                    ┌─────────────────────┐                           │  │
│  │                    │  Landing Page       │                           │  │
│  │                    │  Variants           │                           │  │
│  │                    └─────────────────────┘                           │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      GROWTH CREW (Pulse)                              │  │
│  │                                                                       │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐         │  │
│  │  │ P1: Ad         │  │ P2: Comms      │  │ P3: Analytics  │         │  │
│  │  │ Creative       │  │ Agent          │  │ Agent          │         │  │
│  │  │                │  │                │  │                │         │  │
│  │  │ Create ad      │  │ Write copy     │  │ Deploy & track │         │  │
│  │  │ variants       │  │ variants       │  │ experiments    │         │  │
│  │  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘         │  │
│  │          │                   │                   │                   │  │
│  │          └───────────────────┼───────────────────┘                   │  │
│  │                              │                                        │  │
│  │                              ▼                                        │  │
│  │                    ┌─────────────────────┐                           │  │
│  │                    │  Ad Variants +      │                           │  │
│  │                    │  Experiment Config  │                           │  │
│  │                    └─────────────────────┘                           │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    │                                         │
│                                    ▼                                         │
│                    ┌───────────────────────────────┐                        │
│                    │  HITL: approve_campaign_launch│                        │
│                    │                               │                        │
│                    │  Review: Ads, LP, Budget      │                        │
│                    └───────────────┬───────────────┘                        │
│                                    │                                         │
│                          ┌─────────┴─────────┐                              │
│                       REJECT              APPROVE                            │
│                          │                   │                               │
│                          ▼                   ▼                               │
│                   Revise creatives    Run experiments                        │
│                          │                   │                               │
│                          └─────────┬─────────┘                              │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      GOVERNANCE CREW (Guardian)                       │  │
│  │                                                                       │  │
│  │  G1: QA Agent                                                        │  │
│  │  ├── Methodology compliance check                                    │  │
│  │  ├── Creative QA (brand safety, accuracy)                            │  │
│  │  └── Pre-deployment validation                                       │  │
│  │                                                                       │  │
│  │  G2: Security Agent                                                  │  │
│  │  └── Strip PII from experiment data                                  │  │
│  │                                                                       │  │
│  │  G3: Audit Agent                                                     │  │
│  │  └── Log experiment setup and decisions                              │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    │                                         │
│                                    ▼                                         │
│                    ┌───────────────────────────────┐                        │
│                    │  EXPERIMENT EXECUTION         │                        │
│                    │                               │                        │
│                    │  • Deploy ads to platforms    │                        │
│                    │  • Track impressions, clicks  │                        │
│                    │  • Track signups, conversions │                        │
│                    │  • Compute metrics            │                        │
│                    └───────────────┬───────────────┘                        │
│                                    │                                         │
│                                    ▼                                         │
│                    ┌───────────────────────────────┐                        │
│                    │  COMPUTE INNOVATION PHYSICS   │                        │
│                    │                               │                        │
│                    │  problem_resonance =          │                        │
│                    │    (clicks + signups)         │                        │
│                    │    / impressions              │                        │
│                    │                               │                        │
│                    │  zombie_ratio =               │                        │
│                    │    (clicks - signups)         │                        │
│                    │    / clicks                   │                        │
│                    └───────────────┬───────────────┘                        │
│                                    │                                         │
│                                    ▼                                         │
│                         ┌─────────────────────┐                             │
│                         │  DESIRABILITY       │                             │
│                         │  ROUTER             │                             │
│                         └─────────┬───────────┘                             │
│                                   │                                          │
│          ┌────────────────────────┼────────────────────────┐                │
│          │                        │                        │                 │
│   [pr < 0.3]            [pr ≥ 0.3 && zr ≥ 0.7]   [STRONG_COMMITMENT]        │
│          │                        │                        │                 │
│          ▼                        ▼                        ▼                 │
│   SEGMENT_PIVOT            VALUE_PIVOT           ┌─────────────────────┐   │
│   (Wrong audience)         (Wrong promise)       │ approve_desirability│   │
│          │                        │              │ _gate (HITL)        │   │
│          ▼                        ▼              └──────────┬──────────┘   │
│   Loop to Sage            Loop to Sage                     │                │
│   adjust_segment()        adjust_value_map()        APPROVE│REJECT          │
│          │                        │                        │    │           │
│          │                        │                        ▼    │           │
│          └────────────────────────┴─────────── Proceed to   ◄───┘           │
│                                                Phase 3                       │
│                                                Feasibility                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Agent Specifications

### Build Crew (Forge)

#### F1: UX/UI Designer Agent

| Attribute | Value |
|-----------|-------|
| **ID** | F1 |
| **Name** | UX/UI Designer Agent |
| **Founder** | Forge |
| **Role** | Design landing pages and MVP interfaces from VPC |
| **Goal** | Create high-converting designs that clearly communicate value proposition |

**Tasks:**
1. `design_landing_page` - Create wireframes and component layouts
2. `design_lite_variant` - Create reduced-scope version for downgrades
3. `specify_ux_requirements` - Document interaction patterns

**Tools:**
- `ComponentLibraryScraper` - Reference design systems
- `CanvasBuilderTool` - Generate design specs from VPC

---

#### F2: Frontend Developer Agent

| Attribute | Value |
|-----------|-------|
| **ID** | F2 |
| **Name** | Frontend Developer Agent |
| **Founder** | Forge |
| **Role** | Build landing pages and MVP frontends |
| **Goal** | Generate production-ready code quickly for experiments |

**Tasks:**
1. `build_landing_page` - Generate Next.js/React code
2. `integrate_analytics` - Add tracking pixels
3. `build_signup_flow` - Create conversion funnel

**Tools:**
- `LandingPageGeneratorTool` - AI-powered LP generation
- `FileWriteTool` - Write code files
- `CodeValidatorTool` - Validate generated code

---

#### F3: Backend Developer Agent

| Attribute | Value |
|-----------|-------|
| **ID** | F3 |
| **Name** | Backend Developer Agent |
| **Founder** | Forge |
| **Role** | Deploy and configure backend infrastructure |
| **Goal** | Get testable artifacts live quickly |

**Tasks:**
1. `deploy_landing_page` - Deploy to Netlify/Vercel
2. `configure_webhooks` - Set up conversion tracking
3. `manage_environment` - Configure environment variables

**Tools:**
- `LandingPageDeploymentTool` - Netlify deployment
- `APIIntegrationTool` - Connect services

---

### Growth Crew (Pulse)

#### P1: Ad Creative Agent

| Attribute | Value |
|-----------|-------|
| **ID** | P1 |
| **Name** | Ad Creative Agent |
| **Founder** | Pulse |
| **Role** | Generate ad creative variants for testing |
| **Goal** | Create compelling ads that test different value propositions |

**Tasks:**
1. `generate_ad_variants` - Create multiple ad versions
2. `optimize_for_platform` - Adapt for Meta, Google, LinkedIn, TikTok
3. `test_headlines` - A/B test messaging

**Tools:**
- `CopywritingTool` - Generate ad copy
- `ImageGenerationTool` - Create ad visuals
- `LearningRetrievalTool` - Apply learnings from past campaigns

---

#### P2: Communications Agent

| Attribute | Value |
|-----------|-------|
| **ID** | P2 |
| **Name** | Communications Agent |
| **Founder** | Pulse |
| **Role** | Generate landing page copy and messaging |
| **Goal** | Create persuasive copy that converts visitors |

**Tasks:**
1. `write_landing_page_copy` - Headlines, benefits, CTAs
2. `write_email_sequences` - Follow-up nurture flows
3. `create_messaging_variants` - Test different angles

**Tools:**
- `CopywritingTool` - Generate copy
- `TemplateEngineTool` - Apply templates

---

#### P3: Analytics Agent

| Attribute | Value |
|-----------|-------|
| **ID** | P3 |
| **Name** | Analytics Agent |
| **Founder** | Pulse |
| **Role** | Deploy experiments and compute desirability metrics |
| **Goal** | Collect accurate behavioral data for routing decisions |

**Tasks:**
1. `deploy_experiments` - Launch ad campaigns
2. `collect_metrics` - Gather impressions, clicks, signups
3. `compute_signals` - Calculate `problem_resonance`, `zombie_ratio`
4. `set_desirability_signal` - Determine STRONG_COMMITMENT vs WEAK_INTEREST

**Tools:**
- `ExperimentDeployTool` - Launch campaigns
- `AnalyticsTool` - Query analytics platforms
- `PolicyBandit` - A/B test configurations

---

### Governance Crew (Guardian)

#### G1: QA Agent

| Attribute | Value |
|-----------|-------|
| **ID** | G1 |
| **Name** | QA Agent |
| **Founder** | Guardian |
| **Role** | Quality assurance and methodology compliance |
| **Goal** | Ensure experiments are valid and creatives are appropriate |

**Tasks:**
1. `validate_experiment_design` - Check methodology compliance
2. `review_creatives` - Brand safety, accuracy, claims validation
3. `pre_deployment_check` - Final QA before launch

**Tools:**
- `MethodologyCheckTool` - VPD compliance
- `GuardianReviewTool` - Creative review

---

## Innovation Physics Routing

### Desirability Router Logic

```python
@router("route_after_desirability")
def route_after_desirability(self):
    pr = self.state.problem_resonance
    zr = self.state.zombie_ratio
    signal = self.state.desirability_signal

    # Problem-Solution Filter (Innovation Physics)
    # Customer interest < 30% regarding the problem
    if pr < 0.3:
        self.state.pivot_recommendation = PivotType.SEGMENT_PIVOT
        self.state.last_pivot_type = PivotType.SEGMENT_PIVOT
        # Wrong audience - change who we're targeting
        SageCrew().adjust_segment(
            project_id=self.state.project_id,
            vpc_url=self.state.vpc_document_url,
        )
        return "run_desirability_experiments"

    # Product-Market Filter + Zombie Detection
    # Good problem resonance but shallow commitment
    if pr >= 0.3 and zr >= 0.7:
        self.state.pivot_recommendation = PivotType.VALUE_PIVOT
        self.state.last_pivot_type = PivotType.VALUE_PIVOT
        # Right audience, wrong promise - change value proposition
        SageCrew().adjust_value_map(
            project_id=self.state.project_id,
            vpc_url=self.state.vpc_document_url,
        )
        return "run_desirability_experiments"

    # Strong commitment - proceed to Feasibility
    if signal == DesirabilitySignal.STRONG_COMMITMENT:
        self.state.pivot_recommendation = PivotType.NONE
        return "run_feasibility_assessment"

    # Fallback for edge cases
    return "iterate_desirability"
```

### Signal Computation

```python
def compute_desirability_evidence(aggregate: DesirabilityMetrics) -> dict:
    """Compute Innovation Physics metrics from raw experiment data."""

    # Problem resonance = fraction resonating with problem
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

    # Evidence strength based on Innovation Physics
    if problem_resonance >= 0.5:
        evidence_strength = EvidenceStrength.STRONG
    elif problem_resonance >= 0.1:
        evidence_strength = EvidenceStrength.WEAK
    else:
        evidence_strength = EvidenceStrength.NONE

    # Commitment type: depth of commitment
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

---

## Output Schemas

### Desirability Evidence

```python
class DesirabilityMetrics(BaseModel):
    experiment_id: str
    platform: Platform
    ad_ids: List[str] = []
    landing_page_url: Optional[HttpUrl] = None

    # Raw metrics
    impressions: int = 0
    clicks: int = 0
    signups: int = 0
    spend_usd: float = 0.0

    # Computed metrics
    ctr: float = 0.0              # clicks / impressions
    conversion_rate: float = 0.0  # signups / clicks


class DesirabilityExperimentRun(BaseModel):
    id: str
    downgrade_active: bool = False

    # Artifacts
    ad_variants: List[AdVariant] = []
    landing_page_variants: List[LandingPageVariant] = []

    # Config
    routing: ExperimentRoutingConfig

    # Results
    per_platform_metrics: List[DesirabilityMetrics] = []
    aggregate_metrics: Optional[DesirabilityMetrics] = None

    # Status
    approval_status: ArtifactApprovalStatus = ArtifactApprovalStatus.DRAFT
    guardian_issues: List[str] = []


class DesirabilityResult(BaseModel):
    """Phase 2 output artifact."""

    project_id: str
    experiment_runs: List[DesirabilityExperimentRun]

    # Innovation Physics signals
    problem_resonance: float
    zombie_ratio: float
    evidence_strength: EvidenceStrength
    commitment_type: CommitmentType
    desirability_signal: DesirabilitySignal

    # Pivot tracking
    pivots_executed: List[PivotType] = []
    iteration_count: int = 0

    # Exit status
    exit_ready: bool = False
```

---

## HITL Checkpoints

### `approve_campaign_launch`

| Attribute | Value |
|-----------|-------|
| **Checkpoint ID** | `approve_campaign_launch` |
| **Phase** | 2 |
| **Owner** | Pulse (P1) + Guardian (G1) |
| **Purpose** | Review ads and landing pages before spending money |
| **Required for Exit** | Yes (before each experiment run) |

---

### `approve_spend_increase`

| Attribute | Value |
|-----------|-------|
| **Checkpoint ID** | `approve_spend_increase` |
| **Phase** | 2 |
| **Owner** | Ledger |
| **Purpose** | Approve budget increases beyond initial allocation |
| **Required for Exit** | Only if budget exceeded |

---

### `approve_desirability_gate`

| Attribute | Value |
|-----------|-------|
| **Checkpoint ID** | `approve_desirability_gate` |
| **Phase** | 2 |
| **Owner** | Guardian (G1) + Founder |
| **Purpose** | Confirm desirability evidence sufficient to proceed |
| **Required for Exit** | Yes |

---

## Summary

### CrewAI Pattern Summary

| Pattern | Implementation |
|---------|----------------|
| **Phase** | Phase 2: Desirability Validation |
| **Flow** | `DesirabilityFlow` |
| **Crews** | 3 crews (see below) |

### Crew Summary

| Crew | Agents | Purpose |
|------|--------|---------|
| `BuildCrew` | F1, F2, F3 | Build landing pages and testable artifacts |
| `GrowthCrew` | P1, P2, P3 | Run ad campaigns, collect evidence |
| `GovernanceCrew` | G1, G2, G3 | QA, security, audit |

### Agent Summary

| ID | Agent | Founder | Crew | Role |
|----|-------|---------|------|------|
| F1 | UX/UI Designer | Forge | BuildCrew | Design landing pages |
| F2 | Frontend Developer | Forge | BuildCrew | Build landing pages |
| F3 | Backend Developer | Forge | BuildCrew | Deploy artifacts |
| P1 | Ad Creative | Pulse | GrowthCrew | Generate ad variants |
| P2 | Communications | Pulse | GrowthCrew | Write copy |
| P3 | Analytics | Pulse | GrowthCrew | Run experiments, compute signals |
| G1 | QA Agent | Guardian | GovernanceCrew | Methodology + creative QA |
| G2 | Security Agent | Guardian | GovernanceCrew | PII protection |
| G3 | Audit Agent | Guardian | GovernanceCrew | Decision logging |

**Phase 2 Totals:**
- Flows: 1 (`DesirabilityFlow`)
- Crews: 3
- Agents: 9
- HITL Checkpoints: 3

---

## Methodology Compliance

| Pattern | Implementation |
|---------|----------------|
| **SAY vs DO** | Phase 2 focuses on DO evidence (clicks, signups, payments) |
| **Learning Cards** | Experiment results captured with implications |
| **Evidence Hierarchy** | Prioritizes DO-CTA (weight 2-4) over SAY (weight 1) |
| **Innovation Physics** | `problem_resonance`, `zombie_ratio` computed and used for routing |
| **Pivot Logic** | SEGMENT_PIVOT, VALUE_PIVOT based on computed signals |

---

## Strategyzer Framework Mapping

Phase 2 validates the **demand-side** of the Business Model Canvas. See [03-methodology.md](./03-methodology.md) for the complete VPC → BMC framework mapping.

### BMC Blocks Validated in Phase 2

```
┌─────────────────────────────────────────────────────────────────┐
│                    BUSINESS MODEL CANVAS                        │
├─────────────┬─────────────┬───────────────┬─────────────────────┤
│ Key         │ Key         │ Value         │ Customer      │ Customer   │
│ Partners    │ Activities  │ Propositions  │ Relationships │ Segments   │
│             │             │ ████████████  │ ████████████  │ ████████████│
│             │             │ [VALIDATED]   │ [VALIDATED]   │ [VALIDATED]│
├─────────────┴─────────────┼───────────────┼───────────────┴─────┤
│ Key Resources             │               │ Channels            │
│                           │               │ ████████████████████│
│                           │               │ [VALIDATED]         │
├───────────────────────────┴───────────────┴─────────────────────┤
│ Cost Structure                 │ Revenue Streams               │
└────────────────────────────────┴────────────────────────────────┘

████ = Validated in Phase 2 (Desirability)
```

### Evidence → BMC Block Mapping

| BMC Block | What's Validated | Evidence Source | Innovation Physics Signal |
|-----------|------------------|-----------------|---------------------------|
| **Value Propositions** | Does the value resonate? | Landing page conversions, ad engagement, signup rates | `problem_resonance ≥ 0.3` |
| **Customer Segments** | Is this the right audience? | Demographic data from converters, segment A/B tests | `problem_resonance` by segment |
| **Channels** | Can we reach them effectively? | Platform performance (Meta, Google, LinkedIn, TikTok) | CTR, CPA by channel |
| **Customer Relationships** | What relationship type works? | User engagement patterns, retention signals | `zombie_ratio < 0.7` |

### Phase 2 Exit Contribution to BMC

Upon successful Phase 2 completion, the following BMC blocks should have validated hypotheses:

1. **Value Propositions** → Confirmed that customers want the proposed value (STRONG_COMMITMENT)
2. **Customer Segments** → Validated the target audience responds positively
3. **Channels** → Identified which acquisition channels work best
4. **Customer Relationships** → Understood the preferred engagement model

These validated blocks provide the foundation for Phase 3 (Feasibility) to assess whether we can operationally deliver on these promises.

---

## Related Documents

### Architecture
- [00-introduction.md](./00-introduction.md) - Quick start and orientation
- [01-ecosystem.md](./01-ecosystem.md) - Three-service architecture overview
- [02-organization.md](./02-organization.md) - 6 AI Founders and agents
- [03-methodology.md](./03-methodology.md) - VPD framework reference

### Phase Specifications
- [04-phase-0-onboarding.md](./04-phase-0-onboarding.md) - Founder's Brief capture
- [05-phase-1-vpc-discovery.md](./05-phase-1-vpc-discovery.md) - VPC Discovery (previous phase)
- **Phase 2: Desirability** - (this document)
- [07-phase-3-feasibility.md](./07-phase-3-feasibility.md) - Feasibility validation (next phase)
- [08-phase-4-viability.md](./08-phase-4-viability.md) - Viability + Decision

### Reference
- [09-status.md](./09-status.md) - Current implementation status
- [reference/api-contracts.md](./reference/api-contracts.md) - API specifications
- [reference/approval-workflows.md](./reference/approval-workflows.md) - HITL patterns
