# StartupAI Dynamic Master Architecture

> **Phase 0 Reference**: This document covers Phase 1+ (Desirability → Feasibility → Viability) validation. Phase 0 (Onboarding) and Phase 1 (VPC Discovery) specifications are in [05-phase-0-1-specification.md](./05-phase-0-1-specification.md).

> **VPD Framework**: This validation flow implements patterns from *Value Proposition Design*, *Testing Business Ideas*, and *Business Model Generation* by Osterwalder/Pigneur. Signals like `problem_resonance` and `zombie_ratio` map to VPD Customer Profile validation.

---

## 1\) Agent & Crew Manifest

### 1.1 Crews & Agents (18 total)

| Crew | Agent ID | Agent Name | Role / Responsibilities | Concrete Tools | AMP Config Notes |
| :---- | :---- | :---- | :---- | :---- | :---- |
| Sage | S1 | FounderOnboardingAgent | Convert founder input into `StartupAIBrief`, initial hypothesis set, and project metadata. | `BriefParserTool`, `LearningRetrievalTool` | `memory=true`, `external_memory=supabase_pgvector`, `human_input=false` |
| Sage | S2 | CustomerResearchAgent | Run customer/problem research, identify pains, jobs, segments. | `WebSearchTool`, `LearningRetrievalTool`, `ComparisonMatrixTool` | `memory=true`, `external_memory=supabase_pgvector` |
| Sage | S3 | ValueDesignerAgent | Construct/iterate Value Proposition Canvas; rewrite value map on loops. | `CanvasBuilderTool`, `LearningRetrievalTool` | `memory=true`, `external_memory=supabase_pgvector` |
| Pulse | P1 | AdCreativeAgent | Generate ad concepts, visual directions, hooks for desirability tests. | `CopywritingTool`, `ImageGenerationTool`, `LearningRetrievalTool` | `memory=true`, `external_memory=supabase_pgvector` |
| Pulse | P2 | CommsAgent | Generate landing page copy, email sequences, messaging variants. | `CopywritingTool`, `TemplateEngineTool`, `LearningRetrievalTool` | `memory=true`, `external_memory=supabase_pgvector` |
| Pulse | P3 | AnalyticsAgent | Deploy experiments, call analytics, compute desirability metrics & `DesirabilitySignal`. | `ExperimentDeployTool`, `AnalyticsTool`, `PlatformConfigTool` (internal helper) | `memory=true`, `human_input=false` |
| Forge | F1 | UXUIDesignerAgent | Produce UX spec / component layout from VPC, including “lite” variant on downgrade. | `ComponentLibraryScraper`, `CanvasBuilderTool` | `memory=true`, `external_memory=supabase_pgvector` |
| Forge | F2 | FrontendDevAgent | Generate & persist landing/MVP code (Next.js/React) for experiments. | `FileReadTool`, `FileWriteTool`, `LandingPageDeploymentTool` | `memory=true` |
| Forge | F3 | BackendDevAgent | Evaluate APIs/infra, run feasibility checks, mark constraints and removed features. | `TechStackValidator`, `APIIntegrationTool` | `memory=true` |
| Ledger | L1 | FinancialControllerAgent | Compute CAC/LTV, unit economics, margin, TAM viability; set `ViabilitySignal`. | `PythonREPLTool`, `CostTrackingTool`, `AnalyticsTool` | `memory=true`, `human_input=false` |
| Ledger | L2 | LegalComplianceAgent | Flag regulatory constraints that might impact feasibility/viability (no routing logic, stored in state). | `RegulatorySearchTool` | `human_input=false` |
| Ledger | L3 | EconomicsReviewerAgent | Sanity-check unit economics assumptions, document decision rationale to memory. | `LearningCaptureTool`, `PythonREPLTool` | `memory=true`, `external_memory=supabase_pgvector` |
| Guardian | G1 | QAAgent | Run methodology/consistency checks on VPC/BMC; enforce gates \+ creative QA; pre-HITL checks. | `MethodologyCheckTool`, `GuardianReviewTool` | `human_input=true` (can block progression) |
| Guardian | G2 | SecurityAgent | Strip PII from logs, artifacts, experiment data before long-term memory. | `PrivacyGuardTool`, `AnonymizerTool` | `memory=false`, `external_memory=none` |
| Guardian | G3 | AuditAgent | Persist anonymized learnings and decision logs to Flywheel / Supabase. | `LearningCaptureTool`, `FileWriteTool` | `memory=true`, `external_memory=supabase_pgvector` |
| Compass | C1 | ProductPMAgent | Read state, synthesize votes, propose pivot/proceed/kill options. | `StateInspectionTool`, `SynthesisTool` | `memory=true` |
| Compass | C2 | HumanApprovalAgent | Present options to human, manage HITL prompts, integrate `/resume` decisions (creatives \+ viability). | `ApprovalRequestTool` | `memory=true`, `human_input=true` |
| Compass | C3 | RoadmapWriterAgent | Document pivot decisions and update roadmap artifacts. | `LearningCaptureTool`, `FileWriteTool` | `memory=true`, `external_memory=supabase_pgvector` |

> **Phase 0/1 Agents**: Phase 0 (Onboarding) uses agents O1, G1, G2, S1. Phase 1 (VPC Discovery) uses agents E1, D1-D4, J1-J2, P1-P2, G1-G2, V1-V3, W1-W2, F1-F2. See [05-phase-0-1-specification.md](./05-phase-0-1-specification.md) and [02-organization.md](./02-organization.md) for complete definitions.

### 1.2 Mapping Flow Steps → Crew \+ Agent \+ Task

| Flow Method / Step | Crew | Primary Agents | AMP Task ID | Description |
| :---- | :---- | :---- | :---- | :---- |
| `intake_and_hypothesis` | Sage | S1, S2, S3 | `sage_intake_and_vpc` | Parse brief, research customer/problem, write initial VPC. |
| `run_desirability_experiments` | Pulse | P1, P2, P3 \+ G1/C2 | `pulse_run_desirability` | Generate ads \+ LP variants, run Guardian+HITL creative approvals, deploy experiments, compute metrics & signal. |
| `revise_segment_after_no_interest` | Sage | S2, S3 | `sage_adjust_segment` | On `NO_INTEREST`, pivot segment & update VPC. |
| `revise_value_prop_after_weak_interest` | Sage | S3 | `sage_adjust_value_map` | On `WEAK_INTEREST`, modify value map/offer and update VPC. |
| `run_feasibility_assessment` | Forge | F1, F2, F3 | `forge_build_and_assess_feasibility` | Build MVP/LP, run tech/cost constraints, set `FeasibilitySignal`. |
| `downgrade_and_retest_desirability` | Forge+Pulse | F1,F3 then P1–P3 | `forge_downgrade_scope`, `pulse_run_desirability` | Remove constrained features, mark `downgrade_active`, re-run desirability loop. |
| `run_viability_analysis` | Ledger | L1, L2, L3 | `ledger_unit_economics` | Compute CAC/LTV, TAM, margin, set `ViabilitySignal`. |
| `request_viability_decision_from_human` | Compass | C1, C2 | `compass_viability_decision` | Present `price_pivot`, `cost_pivot`, `kill` options via HITL webhook. |
| `apply_viability_decision` | Compass | C2, C3 | `compass_apply_viability_decision` | Write pivot decision into state and route accordingly. |
| `guardian_phase_gate` (per phase) | Guardian | G1, G2, G3 | `guardian_phase_gate` | QA/gov gate; can block or allow phase transitions; logs to learning store. |

---

## 2\) State Architecture

### 2.1 Enums

from enum import Enum

from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, HttpUrl

class Phase(str, Enum):

    IDEATION \= "ideation"

    DESIRABILITY \= "desirability"

    FEASIBILITY \= "feasibility"

    VIABILITY \= "viability"

    VALIDATED \= "validated"

    KILLED \= "killed"

class RiskAxis(str, Enum):

    DESIRABILITY \= "desirability"

    FEASIBILITY \= "feasibility"

    VIABILITY \= "viability"

class ProblemFit(str, Enum):

    UNKNOWN \= "unknown"

    NO\_FIT \= "no\_fit"

    PARTIAL\_FIT \= "partial\_fit"

    STRONG\_FIT \= "strong\_fit"

class DesirabilitySignal(str, Enum):

    NO\_SIGNAL \= "no\_signal"

    NO\_INTEREST \= "no\_interest"                \# low traffic / low signup

    WEAK\_INTEREST \= "weak\_interest"            \# high CTR, low conversion

    STRONG\_COMMITMENT \= "strong\_commitment"    \# strong signup/preorder evidence

class FeasibilitySignal(str, Enum):

    UNKNOWN \= "unknown"

    GREEN \= "green"                            \# feasible

    ORANGE\_CONSTRAINED \= "orange\_constrained"  \# feasible only w/ scope reduction

    RED\_IMPOSSIBLE \= "red\_impossible"          \# infeasible

class ViabilitySignal(str, Enum):

    UNKNOWN \= "unknown"

    PROFITABLE \= "profitable"                  \# CAC \< LTV

    UNDERWATER \= "underwater"                  \# CAC \> LTV

    ZOMBIE\_MARKET \= "zombie\_market"            \# CAC\<LTV but TAM too small

class PivotType(str, Enum):

    NONE \= "none"

    SEGMENT\_PIVOT \= "segment\_pivot"

    VALUE\_PIVOT \= "value\_pivot"

    CHANNEL\_PIVOT \= "channel\_pivot"

    PRICE\_PIVOT \= "price\_pivot"

    COST\_PIVOT \= "cost\_pivot"

    KILL \= "kill"

class HumanApprovalStatus(str, Enum):

    NOT\_REQUIRED \= "not\_required"

    PENDING \= "pending"

    APPROVED \= "approved"

    REJECTED \= "rejected"

    OVERRIDDEN \= "overridden"

class ArtifactApprovalStatus(str, Enum):

    DRAFT \= "draft"

    PENDING\_REVIEW \= "pending\_review"

    APPROVED \= "approved"

    REJECTED \= "rejected"

class Platform(str, Enum):

    META \= "meta"

    TIKTOK \= "tiktok"

    LINKEDIN \= "linkedin"

    GOOGLE\_SEARCH \= "google\_search"

    GOOGLE\_DISPLAY \= "google\_display"

### 2.1.1 Area 3: Policy Versioning Enums

class PolicyVersion(str, Enum):
    """Policy versions for A/B testing experiment configurations."""
    YAML_BASELINE = "yaml_baseline"     # Static YAML-based configuration
    RETRIEVAL_V1 = "retrieval_v1"       # Retrieval-augmented configuration

### 2.1.2 Area 6: Budget Guardrails Enums

class EnforcementMode(str, Enum):
    """Budget enforcement modes."""
    HARD = "hard"   # Block execution if budget exceeded
    SOFT = "soft"   # Warn but allow continuation

class BudgetStatus(str, Enum):
    """Budget status for spend tracking."""
    OK = "ok"               # Under budget
    WARNING = "warning"     # 80%+ of budget
    EXCEEDED = "exceeded"   # 100%+ of budget
    KILL = "kill"           # 120%+ critical limit

class DecisionType(str, Enum):
    """Types of decisions logged for audit trail."""
    CREATIVE_APPROVAL = "creative_approval"
    VIABILITY_APPROVAL = "viability_approval"
    PIVOT_DECISION = "pivot_decision"
    BUDGET_DECISION = "budget_decision"
    POLICY_SELECTION = "policy_selection"
    HUMAN_APPROVAL = "human_approval"

class ActorType(str, Enum):
    """Actor types for decision attribution."""
    AI_AGENT = "ai_agent"
    HUMAN_FOUNDER = "human_founder"
    SYSTEM = "system"

### 2.1.3 Area 7: Business Model Viability Enums

class BusinessModelType(str, Enum):
    """Business model types for viability calculations."""
    SAAS_B2B_SMB = "saas_b2b_smb"
    SAAS_B2B_MIDMARKET = "saas_b2b_midmarket"
    SAAS_B2B_ENTERPRISE = "saas_b2b_enterprise"
    SAAS_B2C_FREEMIUM = "saas_b2c_freemium"
    SAAS_B2C_SUBSCRIPTION = "saas_b2c_subscription"
    ECOMMERCE_DTC = "ecommerce_dtc"
    ECOMMERCE_MARKETPLACE = "ecommerce_marketplace"
    FINTECH_B2B = "fintech_b2b"
    FINTECH_B2C = "fintech_b2c"
    CONSULTING = "consulting"
    UNKNOWN = "unknown"

### 2.2 Supporting Models for Experiments & Artifacts

class DesirabilityMetrics(BaseModel):

    experiment\_id: str

    platform: Platform

    ad\_ids: List\[str\] \= \[\]

    landing\_page\_url: Optional\[HttpUrl\] \= None

    impressions: int \= 0

    clicks: int \= 0

    signups: int \= 0

    spend\_usd: float \= 0.0

    ctr: float \= 0.0             \# computed: clicks / impressions

    conversion\_rate: float \= 0.0 \# signups / clicks

class FeasibilityArtifact(BaseModel):

    build\_id: str

    mvp\_url: Optional\[HttpUrl\] \= None

    api\_cost\_estimate\_monthly\_usd: float \= 0.0

    infra\_cost\_estimate\_monthly\_usd: float \= 0.0

    removed\_features: List\[str\] \= \[\]

    retained\_features: List\[str\] \= \[\]

    technical\_complexity\_score: int \= 0  \# 1–10

    notes: Optional\[str\] \= None

class ViabilityMetrics(BaseModel):

    cac\_usd: float \= 0.0

    ltv\_usd: float \= 0.0

    gross\_margin\_pct: float \= 0.0

    tam\_annual\_revenue\_potential\_usd: float \= 0.0

    monthly\_churn\_pct: float \= 0.0

    payback\_months: float \= 0.0

    # Area 7 additions: Business model-specific breakdown
    business_model_type: Optional[BusinessModelType] = None
    cac_breakdown: Optional[Dict[str, float]] = None  # {"paid": 150, "organic": 50}
    ltv_breakdown: Optional[Dict[str, float]] = None  # {"subscription": 800, "upsell": 200}
    ltv_cac_ratio: float = 0.0
    model_specific_metrics: Optional[Dict[str, Any]] = None  # Model-specific fields

#### Phase 1 artifacts (ads, LPs, config, approvals)

class AdVariant(BaseModel):

    id: str

    platform: Platform

    headline: str

    body: str

    cta: str

    asset\_url: Optional\[HttpUrl\] \= None

    approval\_status: ArtifactApprovalStatus \= ArtifactApprovalStatus.DRAFT

    human\_approval\_status: HumanApprovalStatus \= HumanApprovalStatus.NOT\_REQUIRED

    human\_comment: Optional\[str\] \= None

class LandingPageVariant(BaseModel):

    id: str

    variant\_tag: str  \# baseline, lite\_scope, price\_test\_A, etc.

    preview\_url: Optional\[HttpUrl\] \= None

    deployed\_url: Optional\[HttpUrl\] \= None

    hosting\_provider: Optional\[str\] \= None  \# vercel, netlify, etc.

    route\_path: Optional\[str\] \= None        \# "/v1", "/v1-lite", etc.

    approval\_status: ArtifactApprovalStatus \= ArtifactApprovalStatus.DRAFT

    human\_approval\_status: HumanApprovalStatus \= HumanApprovalStatus.NOT\_REQUIRED

    human\_comment: Optional\[str\] \= None

class PlatformBudgetConfig(BaseModel):

    platform: Platform

    duration\_days: int

    total\_budget\_usd: float

    min\_impressions: int

    target\_cpc\_usd: Optional\[float\] \= None

    audience\_spec: Dict\[str, Any\] \= Field(default\_factory=dict)

class ExperimentRoutingConfig(BaseModel):

    experiment\_id: Optional\[str\] \= None

    platform\_campaign\_ids: Dict\[Platform, List\[str\]\] \= Field(default\_factory=dict)

    platform\_budgets: List\[PlatformBudgetConfig\] \= Field(default\_factory=list)

class DesirabilityExperimentRun(BaseModel):

    id: str

    downgrade\_active: bool \= False

    ad\_variants: List\[AdVariant\] \= Field(default\_factory=list)

    landing\_page\_variants: List\[LandingPageVariant\] \= Field(default\_factory=list)

    routing: ExperimentRoutingConfig \= Field(

        default\_factory=ExperimentRoutingConfig

    )

    per\_platform\_metrics: List\[DesirabilityMetrics\] \= Field(default\_factory=list)

    aggregate\_metrics: Optional\[DesirabilityMetrics\] \= None

    approval\_status: ArtifactApprovalStatus \= ArtifactApprovalStatus.DRAFT

    guardian\_issues: List\[str\] \= Field(default\_factory=list)

### 2.3 StartupValidationState

class StartupValidationState(BaseModel):

    \# Identity & bookkeeping

    project\_id: str

    iteration: int \= 0

    phase: Phase \= Phase.IDEATION

    current\_risk\_axis: RiskAxis \= RiskAxis.DESIRABILITY

    \# Problem / solution fit (Sage)

    problem\_fit: ProblemFit \= ProblemFit.UNKNOWN

    current\_segment: Optional\[str\] \= None

    current\_value\_prop: Optional\[str\] \= None

    vpc\_document\_url: Optional\[HttpUrl\] \= None

    bmc\_document\_url: Optional\[HttpUrl\] \= None

    \# Signals

    desirability\_signal: DesirabilitySignal \= DesirabilitySignal.NO\_SIGNAL

    feasibility\_signal: FeasibilitySignal \= FeasibilitySignal.UNKNOWN

    viability\_signal: ViabilitySignal \= ViabilitySignal.UNKNOWN

    \# Desirability artifacts & experiments (Pulse)

    desirability\_experiments: List\[DesirabilityExperimentRun\] \= Field(

        default\_factory=list

    )

    downgrade\_active: bool \= False  \# true if 'lite' / downgraded value prop tests are active

    \# Feasibility artifacts (Forge)

    last\_feasibility\_artifact: Optional\[FeasibilityArtifact\] \= None

    \# Viability metrics (Ledger)

    last\_viability\_metrics: Optional\[ViabilityMetrics\] \= None

    \# Pivot \+ routing state

    last\_pivot\_type: PivotType \= PivotType.NONE

    pending\_pivot\_type: PivotType \= PivotType.NONE

    \# Global human approvals

    human\_approval\_status: HumanApprovalStatus \= HumanApprovalStatus.NOT\_REQUIRED

    human\_comment: Optional\[str\] \= None

    \# HITL bookkeeping (both creatives \+ viability)

    last\_human\_decision\_task\_id: Optional\[str\] \= None

    last\_human\_decision\_run\_id: Optional\[str\] \= None

    \# Guardian / governance metadata

    guardian\_last\_issues: List\[str\] \= Field(default\_factory=list)

    audit\_log\_ids: List\[str\] \= Field(default\_factory=list)

    class Config:

        arbitrary\_types\_allowed \= True

---

## 3\) Execution Logic (Flow)

from crewai.flow.flow import Flow, start, listen, router

from .state import (

    StartupValidationState,

    DesirabilitySignal,

    FeasibilitySignal,

    ViabilitySignal,

    PivotType,

    Phase,

    RiskAxis,

    HumanApprovalStatus,

)

from .crews import SageCrew, PulseCrew, ForgeCrew, LedgerCrew, CompassCrew, GuardianCrew

class StartupValidationFlow(Flow\[StartupValidationState\]):

    \# \---------- PHASE 1+: Receives Founder's Brief from Phase 0 (Sage \+ Guardian) \----------
    \# NOTE: Phase 0 (OnboardingFlow) creates the Founder's Brief via agents O1, G1, G2, S1.
    \#       See 05-phase-0-1-specification.md for Phase 0/1 implementation.

    @start()

    def intake\_and\_hypothesis(self):
        \# Receives Founder's Brief from Phase 0 (approve_founders_brief HITL checkpoint)

        sage \= SageCrew()

        guardian \= GuardianCrew()

        sage\_result \= sage.kickoff\_intake\_and\_vpc(

            project\_id=self.state.project\_id

        )

        self.state.phase \= Phase.IDEATION

        self.state.problem\_fit \= sage\_result.problem\_fit

        self.state.current\_segment \= sage\_result.segment

        self.state.current\_value\_prop \= sage\_result.value\_prop

        self.state.vpc\_document\_url \= sage\_result.vpc\_document\_url

        self.state.bmc\_document\_url \= sage\_result.bmc\_document\_url

        gate\_result \= guardian.phase\_gate(

            phase="ideation",

            vpc\_url=self.state.vpc\_document\_url,

            bmc\_url=self.state.bmc\_document\_url,

        )

        self.state.guardian\_last\_issues \= gate\_result.issues

        if not gate\_result.passed:

            \# Loop Sage until Guardian is satisfied

            return "intake\_and\_hypothesis"

        return "run\_desirability\_experiments"

    \# \---------- PHASE 1: DESIRABILITY LOOP (Pulse \+ Guardian \+ Sage) \----------

    @listen("run\_desirability\_experiments")

    def run\_desirability\_experiments(self):

        """

        Generate ads/LP variants, run Guardian \+ optional HITL approvals,

        deploy campaigns, collect metrics and compute desirability signal.

        """

        self.state.phase \= Phase.DESIRABILITY

        self.state.current\_risk\_axis \= RiskAxis.DESIRABILITY

        pulse \= PulseCrew()

        result \= pulse.kickoff(

            inputs={

                "project\_id": self.state.project\_id,

                "vpc\_url": self.state.vpc\_document\_url,

                "downgrade\_active": self.state.downgrade\_active,

            },

            state=self.state,

        )

        \# Pulse returns fully-populated experiment run \+ signal

        self.state.desirability\_signal \= result.signal

        self.state.desirability\_experiments.append(result.experiment\_run)

        \# If Pulse detected pending HITL (creative approval), pause routing.

        if self.state.human\_approval\_status \== HumanApprovalStatus.PENDING:

            return "await\_creative\_approval"

        return "route\_after\_desirability"

    @listen("await\_creative\_approval")

    def await\_creative\_approval(self):

        """

        Placeholder node for AMP's human\_input pause on creative approval.

        /resume will update StartupValidationState (via CompassCrew) and then resume here.

        """

        return "route\_after\_desirability"

    @router("route\_after\_desirability")

    def route\_after\_desirability(self):

        signal \= self.state.desirability\_signal

        if signal \== DesirabilitySignal.NO\_INTEREST:

            self.state.last\_pivot\_type \= PivotType.SEGMENT\_PIVOT

            SageCrew().adjust\_segment(

                project\_id=self.state.project\_id,

                vpc\_url=self.state.vpc\_document\_url,

            )

            return "run\_desirability\_experiments"

        if signal \== DesirabilitySignal.WEAK\_INTEREST:

            self.state.last\_pivot\_type \= PivotType.VALUE\_PIVOT

            SageCrew().adjust\_value\_map(

                project\_id=self.state.project\_id,

                vpc\_url=self.state.vpc\_document\_url,

            )

            return "run\_desirability\_experiments"

        if signal \== DesirabilitySignal.STRONG\_COMMITMENT:

            return "run\_feasibility\_assessment"

        \# NO\_SIGNAL or any unexpected → iterate creatives again

        return "run\_desirability\_experiments"

    \# \---------- PHASE 2: FEASIBILITY LOOP (Forge \+ Pulse) \----------

    @listen("run\_feasibility\_assessment")

    def run\_feasibility\_assessment(self):

        self.state.phase \= Phase.FEASIBILITY

        self.state.current\_risk\_axis \= RiskAxis.FEASIBILITY

        forge \= ForgeCrew()

        result \= forge.kickoff(

            inputs={

                "project\_id": self.state.project\_id,

                "vpc\_url": self.state.vpc\_document\_url,

            }

        )

        self.state.feasibility\_signal \= result.feasibility\_flag

        self.state.last\_feasibility\_artifact \= result.artifact

        return "route\_after\_feasibility"

    @router("route\_after\_feasibility")

    def route\_after\_feasibility(self):

        flag \= self.state.feasibility\_signal

        if flag \== FeasibilitySignal.GREEN:

            return "run\_viability\_analysis"

        if flag \== FeasibilitySignal.ORANGE\_CONSTRAINED:

            self.state.last\_pivot\_type \= PivotType.COST\_PIVOT

            self.state.downgrade\_active \= True

            ForgeCrew().apply\_downgrade\_to\_vpc(

                project\_id=self.state.project\_id,

                vpc\_url=self.state.vpc\_document\_url,

                artifact=self.state.last\_feasibility\_artifact,

            )

            return "run\_desirability\_experiments"

        if flag \== FeasibilitySignal.RED\_IMPOSSIBLE:

            self.state.phase \= Phase.KILLED

            self.state.last\_pivot\_type \= PivotType.KILL

            return "terminal\_killed"

        \# UNKNOWN → re-run feasibility with adjustments

        return "run\_feasibility\_assessment"

    \# \---------- PHASE 3: VIABILITY LOOP (Ledger \+ Compass) \----------

    @listen("run\_viability\_analysis")

    def run\_viability\_analysis(self):

        self.state.phase \= Phase.VIABILITY

        self.state.current\_risk\_axis \= RiskAxis.VIABILITY

        ledger \= LedgerCrew()

        result \= ledger.kickoff(

            inputs={

                "project\_id": self.state.project\_id,

                "experiments": \[

                    e.dict() for e in self.state.desirability\_experiments

                \],

                "artifact": (

                    self.state.last\_feasibility\_artifact.dict()

                    if self.state.last\_feasibility\_artifact

                    else None

                ),

            }

        )

        self.state.viability\_signal \= result.viability\_flag

        self.state.last\_viability\_metrics \= result.metrics

        return "route\_after\_viability"

    @router("route\_after\_viability")

    def route\_after\_viability(self):

        signal \= self.state.viability\_signal

        if signal \== ViabilitySignal.PROFITABLE:

            self.state.phase \= Phase.VALIDATED

            self.state.last\_pivot\_type \= PivotType.NONE

            return "terminal\_validated"

        if signal in (ViabilitySignal.UNDERWATER, ViabilitySignal.ZOMBIE\_MARKET):

            self.state.human\_approval\_status \= HumanApprovalStatus.PENDING

            self.state.pending\_pivot\_type \= PivotType.NONE

            compass \= CompassCrew()

            hitl \= compass.request\_viability\_decision(

                project\_id=self.state.project\_id,

                viability\_metrics=self.state.last\_viability\_metrics,

                experiments=self.state.desirability\_experiments,

            )

            self.state.last\_human\_decision\_task\_id \= hitl.task\_id

            self.state.last\_human\_decision\_run\_id \= hitl.run\_id

            return "await\_viability\_decision"

        return "run\_viability\_analysis"

    @listen("await\_viability\_decision")

    def await\_viability\_decision(self):

        return "route\_after\_viability\_decision"

    @router("route\_after\_viability\_decision")

    def route\_after\_viability\_decision(self):

        pivot \= self.state.pending\_pivot\_type

        if pivot \== PivotType.PRICE\_PIVOT:

            self.state.last\_pivot\_type \= PivotType.PRICE\_PIVOT

            self.state.phase \= Phase.DESIRABILITY

            self.state.current\_risk\_axis \= RiskAxis.DESIRABILITY

            return "run\_desirability\_experiments"

        if pivot \== PivotType.COST\_PIVOT:

            self.state.last\_pivot\_type \= PivotType.COST\_PIVOT

            self.state.phase \= Phase.FEASIBILITY

            self.state.current\_risk\_axis \= RiskAxis.FEASIBILITY

            return "run\_feasibility\_assessment"

        if pivot \== PivotType.KILL:

            self.state.phase \= Phase.KILLED

            self.state.last\_pivot\_type \= PivotType.KILL

            return "terminal\_killed"

        \# safety default

        self.state.phase \= Phase.KILLED

        self.state.last\_pivot\_type \= PivotType.KILL

        return "terminal\_killed"

    \# \---------- TERMINALS \----------

    @listen("terminal\_validated")

    def terminal\_validated(self):

        GuardianCrew().final\_audit(self.state)

        return None

    @listen("terminal\_killed")

    def terminal\_killed(self):

        GuardianCrew().log\_termination(self.state)

        return None

---

## 4\) Crew & Task Orchestration Layer

### 4.1 Result Models

class SageIntakeResult(BaseModel):

    problem\_fit: ProblemFit

    segment: str

    value\_prop: str

    vpc\_document\_url: HttpUrl

    bmc\_document\_url: HttpUrl

class GuardianGateResult(BaseModel):

    passed: bool

    issues: List\[str\] \= \[\]

class GuardianCreativeReviewResult(BaseModel):

    ad\_variants: List\[AdVariant\]

    landing\_page\_variants: List\[LandingPageVariant\]

    issues: List\[str\] \= \[\]

    hitl\_required: bool \= False

class PulseDesirabilityResult(BaseModel):

    signal: DesirabilitySignal

    experiment\_run: DesirabilityExperimentRun

class ForgeFeasibilityResult(BaseModel):

    feasibility\_flag: FeasibilitySignal

    artifact: FeasibilityArtifact

class LedgerViabilityResult(BaseModel):

    viability\_flag: ViabilitySignal

    metrics: ViabilityMetrics

class CompassHitlRequest(BaseModel):

    run\_id: str

    task\_id: str

### 4.2 Tool Stubs (including LP deployment \+ multi-platform experiments)

class CopywritingTool:

    def generate\_ads(

        self,

        brief: dict,

        vpc: dict,

        variant\_tag: str,

        platforms: List\[Platform\],

        variants\_per\_platform: int \= 2,

    ) \-\> List\[dict\]:

        """

        Inputs:

          \- brief: parsed StartupAIBrief

          \- vpc: structured VPC JSON

          \- variant\_tag: "baseline", "lite\_scope", etc.

          \- platforms: list of platforms to create ads for

          \- variants\_per\_platform: number of variants for split-testing

        Returns:

          \- List of ad objects:

            {

              "id": str,

              "platform": str (Platform value),

              "headline": str,

              "body": str,

              "cta": str

            }

        """

        raise NotImplementedError

class LandingPageGeneratorTool:

    def generate\_pages(

        self,

        vpc: dict,

        offer\_variant: str,

        num\_variants: int \= 2,

    ) \-\> List\[dict\]:

        """

        Inputs:

          \- vpc: structured VPC JSON

          \- offer\_variant: label for variant (e.g. "baseline", "lite\_scope")

          \- num\_variants: for A/B/C split tests

        Returns:

          \- List of page specs (NOT yet deployed):

            {

              "id": str,

              "variant\_tag": str,

              "html": str,

              "route\_path": str  \# e.g., "/v1", "/v1-lite"

            }

        """

        raise NotImplementedError

class LandingPageDeploymentTool:

    def deploy\_page\_variants(

        self,

        pages: List\[dict\],

        provider: str,

        base\_url: str,

        project\_id: str,

    ) \-\> List\[dict\]:

        """

        Inputs:

          \- pages: list from LandingPageGeneratorTool.generate\_pages

          \- provider: "vercel" | "netlify" | ...

          \- base\_url: e.g. "https://startupai-${project\_id}.vercel.app"

          \- project\_id: used for naming

        Returns:

          \- List of deployed page descriptors:

            {

              "id": str,

              "variant\_tag": str,

              "hosting\_provider": str,

              "route\_path": str,

              "deployed\_url": str

            }

        """

        raise NotImplementedError

class ExperimentDeployTool:

    def deploy(

        self,

        ad\_variants: List\[dict\],

        landing\_page\_variants: List\[dict\],

        platform\_budgets: List\[PlatformBudgetConfig\],

    ) \-\> Dict:

        """

        Inputs:

          \- ad\_variants: \[{ id, platform, headline, body, cta, ... }\]

          \- landing\_page\_variants: \[{ id, deployed\_url, variant\_tag, ... }\]

          \- platform\_budgets: list of PlatformBudgetConfig

        Returns:

          \- {

              "experiment\_id": str,

              "platform\_campaign\_ids": {

                 "\<platform\>": \["campaign\_id1", "campaign\_id2", ...\]

              },

              "ad\_ids": {

                 "\<platform\>": \["ad\_id1", "ad\_id2", ...\]

              }

            }

        """

        raise NotImplementedError

class AnalyticsTool:

    def collect\_desirability\_metrics(

        self,

        experiment\_id: str,

        platform: Platform,

    ) \-\> DesirabilityMetrics:

        """

        Inputs:

          \- experiment\_id: ID from ExperimentDeployTool

          \- platform: target platform

        Returns:

          \- DesirabilityMetrics populated from analytics (GA/PostHog/ads APIs)

        """

        raise NotImplementedError

class ComponentLibraryScraper:

    def generate\_layout\_spec(self, vpc: dict, lite: bool \= False) \-\> dict:

        """

        Produce a wireframe/component layout spec from VPC using approved UI components.

        """

        raise NotImplementedError

class TechStackValidator:

    def assess(self, layout\_spec: dict, backend\_requirements: dict) \-\> Dict:

        """

        Evaluate technical feasibility and cost.

        Returns:

          {

            "feasibility\_flag": FeasibilitySignal,

            "api\_cost\_estimate\_monthly\_usd": float,

            "infra\_cost\_estimate\_monthly\_usd": float,

            "removed\_features": \[str\],

            "retained\_features": \[str\],

            "technical\_complexity\_score": int,

          }

        """

        raise NotImplementedError

class PythonREPLTool:

    def eval\_unit\_economics(self, inputs: dict) \-\> Dict:

        """

        Inputs:

          \- { "cac": float, "ltv": float, "tam": float, "margin\_pct": float, "churn": float }

        Returns:

          \- { "viability\_flag": ViabilitySignal, "payback\_months": float }

        """

        raise NotImplementedError

class CostTrackingTool:

    def get\_validation\_run\_cost(self, project\_id: str) \-\> float:

        """

        Returns USD cost of the current AMP validation run (tokens, infra).

        """

        raise NotImplementedError

class GuardianReviewTool:

    def check\_creatives(self, ads: List\[dict\], pages: List\[dict\]) \-\> Dict:

        """

        Automatic QA checks: banned terms, formatting, broken links, etc.

        Returns:

          {

            "issues": \[str\],

            "ad\_flags": { ad\_id: { "status": "ok"|"reject"|"hitl", "reasons": \[str\] } },

            "page\_flags": { page\_id: { "status": "ok"|"reject"|"hitl", "reasons": \[str\] } },

          }

        """

        raise NotImplementedError

### 4.3 PulseCrew

from .config import ExperimentConfigResolver  \# defined in section 5

class PulseCrew:

    def \_\_init\_\_(self):

        self.copywriter \= CopywritingTool()

        self.landing\_gen \= LandingPageGeneratorTool()

        self.lp\_deploy \= LandingPageDeploymentTool()

        self.deployer \= ExperimentDeployTool()

        self.analytics \= AnalyticsTool()

        self.guardian \= GuardianCrew()

        self.config\_resolver \= ExperimentConfigResolver()

    def kickoff(

        self,

        inputs: dict,

        state: StartupValidationState,

    ) \-\> PulseDesirabilityResult:

        """

        Orchestration for Desirability experiment:

        1\) Resolve platform \+ budget config from brief/BMC.

        2\) Generate ad variants per platform.

        3\) Generate landing page variants.

        4\) Deploy landing page variants (Vercel/Netlify).

        5\) Guardian automatic review of creatives.

        6\) Optional HITL creative approval via Compass.

        7\) If approved, deploy A/B tests per platform.

        8\) Collect metrics, compute signal.

        """

        project\_id: str \= inputs\["project\_id"\]

        vpc\_url: str \= inputs\["vpc\_url"\]

        downgrade\_active: bool \= inputs.get("downgrade\_active", False)

        \# TODO: load VPC JSON from storage

        vpc \= {"project\_id": project\_id}

        variant\_tag \= "lite\_scope" if downgrade\_active else "baseline"

        \# 1\) Resolve experiment configuration

        exp\_cfg \= self.config\_resolver.resolve\_from\_vpc(vpc=vpc)

        platforms \= \[cfg.platform for cfg in exp\_cfg.platform\_budgets\]

        \# 2\) Generate ad variants per platform

        ad\_dicts \= self.copywriter.generate\_ads(

            brief={"project\_id": project\_id},

            vpc=vpc,

            variant\_tag=variant\_tag,

            platforms=platforms,

            variants\_per\_platform=exp\_cfg.variants\_per\_platform,

        )

        ad\_variants: List\[AdVariant\] \= \[

            AdVariant(

                id=a\["id"\],

                platform=Platform(a\["platform"\]),

                headline=a\["headline"\],

                body=a\["body"\],

                cta=a\["cta"\],

                approval\_status=ArtifactApprovalStatus.DRAFT,

            )

            for a in ad\_dicts

        \]

        \# 3\) Generate landing page variants (not yet deployed)

        page\_specs \= self.landing\_gen.generate\_pages(

            vpc=vpc,

            offer\_variant=variant\_tag,

            num\_variants=exp\_cfg.landing\_page\_variants,

        )

        lp\_variants: List\[LandingPageVariant\] \= \[

            LandingPageVariant(

                id=p\["id"\],

                variant\_tag=p\["variant\_tag"\],

                route\_path=p.get("route\_path"),

                approval\_status=ArtifactApprovalStatus.DRAFT,

            )

            for p in page\_specs

        \]

        \# 4\) Deploy landing pages to Vercel/Netlify

        deployed\_pages \= self.lp\_deploy.deploy\_page\_variants(

            pages=page\_specs,

            provider=exp\_cfg.landing\_page\_provider,

            base\_url=exp\_cfg.base\_url\_template.format(project\_id=project\_id),

            project\_id=project\_id,

        )

        id\_to\_deployed \= {p\["id"\]: p for p in deployed\_pages}

        for lp in lp\_variants:

            deployed \= id\_to\_deployed\[lp.id\]

            lp.hosting\_provider \= deployed\["hosting\_provider"\]

            lp.route\_path \= deployed\["route\_path"\]

            lp.deployed\_url \= deployed\["deployed\_url"\]

        \# 5\) Guardian automatic review

        review \= self.guardian.review\_creatives(

            ad\_variants=ad\_variants,

            landing\_pages=lp\_variants,

            project\_id=project\_id,

        )

        self.\_apply\_creative\_review(review, ad\_variants, lp\_variants, state)

        \# If HITL required, mark state and return NO\_SIGNAL with draft experiment

        if review.hitl\_required:

            state.human\_approval\_status \= HumanApprovalStatus.PENDING

            experiment\_run \= DesirabilityExperimentRun(

                id=f"{project\_id}-des-{len(state.desirability\_experiments)+1}",

                downgrade\_active=downgrade\_active,

                ad\_variants=ad\_variants,

                landing\_page\_variants=lp\_variants,

                approval\_status=ArtifactApprovalStatus.PENDING\_REVIEW,

                guardian\_issues=review.issues,

            )

            return PulseDesirabilityResult(

                signal=DesirabilitySignal.NO\_SIGNAL,

                experiment\_run=experiment\_run,

            )

        \# 6\) If Guardian auto-approves all creatives, mark them APPROVED

        experiment\_run \= DesirabilityExperimentRun(

            id=f"{project\_id}-des-{len(state.desirability\_experiments)+1}",

            downgrade\_active=downgrade\_active,

            ad\_variants=ad\_variants,

            landing\_page\_variants=lp\_variants,

            approval\_status=ArtifactApprovalStatus.APPROVED,

        )

        \# 7\) Deploy A/B tests per platform

        deployment \= self.deployer.deploy(

            ad\_variants=\[a.dict() for a in ad\_variants\],

            landing\_page\_variants=\[lp.dict() for lp in lp\_variants\],

            platform\_budgets=exp\_cfg.platform\_budgets,

        )

        routing \= ExperimentRoutingConfig(

            experiment\_id=deployment\["experiment\_id"\],

            platform\_campaign\_ids={

                Platform(k): v for k, v in deployment\["platform\_campaign\_ids"\].items()

            },

            platform\_budgets=exp\_cfg.platform\_budgets,

        )

        experiment\_run.routing \= routing

        \# 8\) Collect metrics per platform

        per\_platform\_metrics: List\[DesirabilityMetrics\] \= \[\]

        total\_impr \= total\_clicks \= total\_signups \= total\_spend \= 0.0

        for cfg in exp\_cfg.platform\_budgets:

            m \= self.analytics.collect\_desirability\_metrics(

                experiment\_id=routing.experiment\_id,

                platform=cfg.platform,

            )

            per\_platform\_metrics.append(m)

            total\_impr \+= m.impressions

            total\_clicks \+= m.clicks

            total\_signups \+= m.signups

            total\_spend \+= m.spend\_usd

        aggregate \= DesirabilityMetrics(

            experiment\_id=routing.experiment\_id,

            platform=Platform.META,  \# placeholder; aggregate

            impressions=int(total\_impr),

            clicks=int(total\_clicks),

            signups=int(total\_signups),

            spend\_usd=float(total\_spend),

        )

        if aggregate.impressions \> 0:

            aggregate.ctr \= aggregate.clicks / aggregate.impressions

        if aggregate.clicks \> 0:

            aggregate.conversion\_rate \= aggregate.signups / aggregate.clicks

        experiment\_run.per\_platform\_metrics \= per\_platform\_metrics

        experiment\_run.aggregate\_metrics \= aggregate

        \# map metrics \-\> signal

        signal \= self.\_compute\_desirability\_signal(aggregate)

        return PulseDesirabilityResult(signal=signal, experiment\_run=experiment\_run)

    @staticmethod

    def \_apply\_creative\_review(

        review: GuardianCreativeReviewResult,

        ad\_variants: List\[AdVariant\],

        lp\_variants: List\[LandingPageVariant\],

        state: StartupValidationState,

    ) \-\> None:

        ad\_flags \= {a.id: "ok" for a in \[\*ad\_variants\]}

        page\_flags \= {p.id: "ok" for p in \[\*lp\_variants\]}

        \# review.ad\_variants / review.landing\_page\_variants already have statuses;

        \# just copy them over:

        id\_to\_ad \= {a.id: a for a in review.ad\_variants}

        id\_to\_lp \= {p.id: p for p in review.landing\_page\_variants}

        for i, a in enumerate(ad\_variants):

            updated \= id\_to\_ad.get(a.id, a)

            ad\_variants\[i\] \= updated

        for i, lp in enumerate(lp\_variants):

            updated \= id\_to\_lp.get(lp.id, lp)

            lp\_variants\[i\] \= updated

        state.guardian\_last\_issues \= review.issues

    @staticmethod

    def \_compute\_desirability\_signal(metrics: DesirabilityMetrics) \-\> DesirabilitySignal:

        if metrics.impressions \== 0:

            return DesirabilitySignal.NO\_SIGNAL

        ctr \= metrics.ctr

        conv \= metrics.conversion\_rate

        if ctr \< 0.02 and conv \< 0.05:

            return DesirabilitySignal.NO\_INTEREST

        if ctr \>= 0.02 and conv \< 0.05:

            return DesirabilitySignal.WEAK\_INTEREST

        if metrics.signups \>= 5:

            return DesirabilitySignal.STRONG\_COMMITMENT

        return DesirabilitySignal.WEAK\_INTEREST

### 4.4 ForgeCrew

class ForgeCrew:

    def \_\_init\_\_(self):

        self.scraper \= ComponentLibraryScraper()

        self.tech\_validator \= TechStackValidator()

        \# FileWriteTool / APIIntegrationTool / LandingPageDeploymentTool would be injected here.

    def kickoff(self, inputs: dict) \-\> ForgeFeasibilityResult:

        project\_id: str \= inputs\["project\_id"\]

        vpc\_url: str \= inputs\["vpc\_url"\]

        \# TODO: load VPC JSON

        vpc \= {"project\_id": project\_id}

        layout\_spec \= self.scraper.generate\_layout\_spec(vpc=vpc, lite=False)

        backend\_requirements \= {

            "requires\_realtime": vpc.get("requires\_realtime", False),

            "requires\_external\_api": vpc.get("requires\_external\_api", True),

            "estimated\_users": vpc.get("estimated\_users", 1000),

        }

        assessment \= self.tech\_validator.assess(

            layout\_spec=layout\_spec,

            backend\_requirements=backend\_requirements,

        )

        feasibility\_flag \= assessment\["feasibility\_flag"\]

        artifact \= FeasibilityArtifact(

            build\_id=f"{project\_id}-mvp-1",

            mvp\_url=None,  \# filled by FrontendDevAgent \+ LandingPageDeploymentTool

            api\_cost\_estimate\_monthly\_usd=assessment\["api\_cost\_estimate\_monthly\_usd"\],

            infra\_cost\_estimate\_monthly\_usd=assessment\["infra\_cost\_estimate\_monthly\_usd"\],

            removed\_features=assessment\["removed\_features"\],

            retained\_features=assessment\["retained\_features"\],

            technical\_complexity\_score=assessment\["technical\_complexity\_score"\],

            notes="auto generated feasibility assessment",

        )

        return ForgeFeasibilityResult(

            feasibility\_flag=feasibility\_flag,

            artifact=artifact,

        )

    def apply\_downgrade\_to\_vpc(

        self,

        project\_id: str,

        vpc\_url: str,

        artifact: FeasibilityArtifact,

    ) \-\> None:

        """

        Mutate VPC artifact (remove features in removed\_features),

        persist new VPC version for 'lite' product for re-testing desirability.

        """

        raise NotImplementedError

### 4.5 LedgerCrew

class LedgerCrew:

    def \_\_init\_\_(self):

        self.repl \= PythonREPLTool()

        self.cost\_tracking \= CostTrackingTool()

        self.analytics \= AnalyticsTool()

    def kickoff(self, inputs: dict) \-\> LedgerViabilityResult:

        project\_id: str \= inputs\["project\_id"\]

        experiments: List\[dict\] \= inputs\["experiments"\]

        artifact: Optional\[dict\] \= inputs.get("artifact")

        \# Aggregate CAC from experiments

        total\_spend \= 0.0

        total\_signups \= 0

        for e in experiments:

            agg \= e.get("aggregate\_metrics") or {}

            total\_spend \+= agg.get("spend\_usd", 0.0)

            total\_signups \+= agg.get("signups", 0\)

        total\_signups \= total\_signups or 1

        cac \= total\_spend / total\_signups

        \# Placeholder LTV/TAM; replace w/ real financial modeling

        ltv \= 600.0

        tam \= 1\_000\_000.0

        margin\_pct \= 0.7

        churn\_pct \= 0.05

        econ\_result \= self.repl.eval\_unit\_economics(

            inputs={

                "cac": cac,

                "ltv": ltv,

                "tam": tam,

                "margin\_pct": margin\_pct,

                "churn": churn\_pct,

            }

        )

        viability\_flag \= econ\_result.get("viability\_flag", ViabilitySignal.UNKNOWN)

        payback\_months \= econ\_result.get("payback\_months", 0.0)

        metrics \= ViabilityMetrics(

            cac\_usd=cac,

            ltv\_usd=ltv,

            gross\_margin\_pct=margin\_pct \* 100.0,

            tam\_annual\_revenue\_potential\_usd=tam,

            monthly\_churn\_pct=churn\_pct \* 100.0,

            payback\_months=payback\_months,

        )

        return LedgerViabilityResult(

            viability\_flag=viability\_flag,

            metrics=metrics,

        )

### 4.6 GuardianCrew (phase gates \+ creative review)

class GuardianCrew:

    def \_\_init\_\_(self):

        self.review\_tool \= GuardianReviewTool()

        \# MethodologyCheckTool, PrivacyGuardTool, etc.

    def phase\_gate(self, phase: str, vpc\_url: str, bmc\_url: str) \-\> GuardianGateResult:

        \# Implementation uses MethodologyCheckTool

        raise NotImplementedError

    def final\_audit(self, state: StartupValidationState) \-\> None:

        \# Write learnings to Audit store

        raise NotImplementedError

    def log\_termination(self, state: StartupValidationState) \-\> None:

        \# Write kill rationale to Audit store

        raise NotImplementedError

    def review\_creatives(

        self,

        ad\_variants: List\[AdVariant\],

        landing\_pages: List\[LandingPageVariant\],

        project\_id: str,

    ) \-\> GuardianCreativeReviewResult:

        result \= self.review\_tool.check\_creatives(

            ads=\[a.dict() for a in ad\_variants\],

            pages=\[p.dict() for p in landing\_pages\],

        )

        issues \= result.get("issues", \[\])

        ad\_flags \= result.get("ad\_flags", {})

        page\_flags \= result.get("page\_flags", {})

        hitl\_required \= False

        for a in ad\_variants:

            flags \= ad\_flags.get(a.id, {"status": "ok", "reasons": \[\]})

            if flags\["status"\] \== "ok":

                a.approval\_status \= ArtifactApprovalStatus.APPROVED

            elif flags\["status"\] \== "reject":

                a.approval\_status \= ArtifactApprovalStatus.REJECTED

            elif flags\["status"\] \== "hitl":

                a.approval\_status \= ArtifactApprovalStatus.PENDING\_REVIEW

                hitl\_required \= True

        for lp in landing\_pages:

            flags \= page\_flags.get(lp.id, {"status": "ok", "reasons": \[\]})

            if flags\["status"\] \== "ok":

                lp.approval\_status \= ArtifactApprovalStatus.APPROVED

            elif flags\["status"\] \== "reject":

                lp.approval\_status \= ArtifactApprovalStatus.REJECTED

            elif flags\["status"\] \== "hitl":

                lp.approval\_status \= ArtifactApprovalStatus.PENDING\_REVIEW

                hitl\_required \= True

        return GuardianCreativeReviewResult(

            ad\_variants=ad\_variants,

            landing\_page\_variants=landing\_pages,

            issues=issues,

            hitl\_required=hitl\_required,

        )

### 4.7 CompassCrew (HITL for viability & creatives)

class CompassCrew:

    def request\_viability\_decision(

        self,

        project\_id: str,

        viability\_metrics: ViabilityMetrics,

        experiments: List\[DesirabilityExperimentRun\],

    ) \-\> CompassHitlRequest:

        \# Call AMP SDK to create HITL task for viability decision.

        run\_id \= "run\_abc123"

        task\_id \= "compass\_viability\_decision"

        return CompassHitlRequest(run\_id=run\_id, task\_id=task\_id)

    def apply\_viability\_decision\_from\_resume(

        self,

        state: StartupValidationState,

        payload: dict,

    ) \-\> None:

        decision \= payload\["inputs"\]\["viability\_pivot\_decision"\]

        comment \= payload\["inputs"\].get("comment")

        if decision \== "price\_pivot":

            state.pending\_pivot\_type \= PivotType.PRICE\_PIVOT

        elif decision \== "cost\_pivot":

            state.pending\_pivot\_type \= PivotType.COST\_PIVOT

        elif decision \== "kill":

            state.pending\_pivot\_type \= PivotType.KILL

        else:

            state.pending\_pivot\_type \= PivotType.KILL

        state.human\_approval\_status \= HumanApprovalStatus.APPROVED

        state.human\_comment \= comment

    def apply\_creative\_decision\_from\_resume(

        self,

        state: StartupValidationState,

        payload: dict,

    ) \-\> None:

        """

        Called from creative approval /resume (Guardian \+ C2).

        Payload example defined in section 6\.

        """

        decision \= payload\["inputs"\]\["creative\_decision"\]

        comments \= payload\["inputs"\].get("artifact\_comments", {})

        \# Update last experiment's creative statuses

        if not state.desirability\_experiments:

            return

        exp \= state.desirability\_experiments\[-1\]

        for ad in exp.ad\_variants:

            status \= decision\["ads"\].get(ad.id, "approve")

            if status \== "approve":

                ad.approval\_status \= ArtifactApprovalStatus.APPROVED

                ad.human\_approval\_status \= HumanApprovalStatus.APPROVED

            elif status \== "reject":

                ad.approval\_status \= ArtifactApprovalStatus.REJECTED

                ad.human\_approval\_status \= HumanApprovalStatus.REJECTED

            ad.human\_comment \= comments.get(ad.id)

        for lp in exp.landing\_page\_variants:

            status \= decision\["landing\_pages"\].get(lp.id, "approve")

            if status \== "approve":

                lp.approval\_status \= ArtifactApprovalStatus.APPROVED

                lp.human\_approval\_status \= HumanApprovalStatus.APPROVED

            elif status \== "reject":

                lp.approval\_status \= ArtifactApprovalStatus.REJECTED

                lp.human\_approval\_status \= HumanApprovalStatus.REJECTED

            lp.human\_comment \= comments.get(lp.id)

        state.human\_approval\_status \= HumanApprovalStatus.APPROVED

        state.human\_comment \= payload\["inputs"\].get("comment")

---

## 5\) Phase 1 Experiment Configuration & Platform Selection

### 5.1 Configuration models (Python)

class ProjectExperimentConfig(BaseModel):

    variants\_per\_platform: int \= 2

    landing\_page\_variants: int \= 2

    landing\_page\_provider: str \= "vercel"

    base\_url\_template: str \= "https://startupai-{project\_id}.vercel.app"

    platform\_budgets: List\[PlatformBudgetConfig\] \= Field(default\_factory=list)

class ExperimentConfigResolver:

    """

    Reads brief/BMC/VPC to decide:

      \- B2B vs B2C

      \- Platforms

      \- Budgets, duration, targeting

    Uses YAML or DB-backed configuration.

    """

    def \_\_init\_\_(self, config\_path: str \= "config/experiments.yaml"):

        self.config\_path \= config\_path

    def resolve\_from\_vpc(self, vpc: dict) \-\> ProjectExperimentConfig:

        \# naive example: use vpc\['segment\_type'\] to select rule

        segment\_type \= vpc.get("segment\_type", "b2c").lower()

        \# TODO: load YAML

        \# Here we hardcode for clarity

        if segment\_type \== "b2b":

            pb \= \[

                PlatformBudgetConfig(

                    platform=Platform.LINKEDIN,

                    duration\_days=7,

                    total\_budget\_usd=400.0,

                    min\_impressions=3000,

                    target\_cpc\_usd=5.0,

                    audience\_spec={"job\_titles": \["CTO", "VP Engineering"\]},

                ),

                PlatformBudgetConfig(

                    platform=Platform.GOOGLE\_SEARCH,

                    duration\_days=7,

                    total\_budget\_usd=600.0,

                    min\_impressions=5000,

                    target\_cpc\_usd=4.0,

                    audience\_spec={"keywords": \["enterprise ecommerce", "b2b saas"\]},

                ),

            \]

        else:

            \# default B2C

            pb \= \[

                PlatformBudgetConfig(

                    platform=Platform.META,

                    duration\_days=5,

                    total\_budget\_usd=400.0,

                    min\_impressions=5000,

                    target\_cpc\_usd=1.5,

                    audience\_spec={"interests": \["online shopping", "fashion"\]},

                ),

                PlatformBudgetConfig(

                    platform=Platform.TIKTOK,

                    duration\_days=5,

                    total\_budget\_usd=200.0,

                    min\_impressions=3000,

                    target\_cpc\_usd=1.0,

                    audience\_spec={"interests": \["startups", "side hustles"\]},

                ),

            \]

        return ProjectExperimentConfig(

            variants\_per\_platform=2,

            landing\_page\_variants=2,

            landing\_page\_provider="vercel",

            base\_url\_template="https://startupai-{project\_id}.vercel.app",

            platform\_budgets=pb,

        )

### 5.2 YAML configuration example

\# config/experiments.yaml

defaults:

  variants\_per\_platform: 2

  landing\_page\_variants: 2

  landing\_page\_provider: "vercel"

  base\_url\_template: "https://startupai-{project\_id}.vercel.app"

segments:

  b2b:

    platforms:

      \- platform: linkedin

        duration\_days: 7

        total\_budget\_usd: 400

        min\_impressions: 3000

        target\_cpc\_usd: 5.0

        audience\_spec:

          job\_titles: \["CTO", "VP Engineering", "Head of Product"\]

          company\_size: \["50-200", "200-1000"\]

      \- platform: google\_search

        duration\_days: 7

        total\_budget\_usd: 600

        min\_impressions: 5000

        target\_cpc\_usd: 4.0

        audience\_spec:

          keywords:

            \- "b2b ecommerce"

            \- "b2b saas platform"

  b2c:

    platforms:

      \- platform: meta

        duration\_days: 5

        total\_budget\_usd: 400

        min\_impressions: 5000

        target\_cpc\_usd: 1.5

        audience\_spec:

          interests:

            \- "online shopping"

            \- "fashion"

      \- platform: tiktok

        duration\_days: 5

        total\_budget\_usd: 200

        min\_impressions: 3000

        target\_cpc\_usd: 1.0

        audience\_spec:

          interests:

            \- "startups"

            \- "side hustles"

**How it’s used:** `ExperimentConfigResolver.resolve_from_vpc` reads VPC/BMC fields like `segment_type` (b2b/b2c), then selects platform config. `PulseCrew.kickoff` passes resulting `platform_budgets` into `ExperimentDeployTool.deploy`, which maps each `PlatformBudgetConfig` to real campaign creation calls on the underlying ad APIs.

---

## 6\) Creative Approval Workflow (Guardian \+ HITL)

### 6.1 State & Enums

Already covered via:

* `ArtifactApprovalStatus`  
* `HumanApprovalStatus`  
* `AdVariant`, `LandingPageVariant`  
* `StartupValidationState.human_approval_status`, `human_comment`

Per-artifact fields:

* `approval_status` (DRAFT → PENDING\_REVIEW → APPROVED/REJECTED)  
* `human_approval_status` (+ comment)

### 6.2 GuardianCrew review \+ Pulse integration

Already implemented in section 4.3 and 4.6:

* Pulse generates drafts.  
* `GuardianCrew.review_creatives` auto-checks and sets `approval_status`.  
* If `hitl_required=True`, Pulse marks experiment as `PENDING_REVIEW` and sets global `state.human_approval_status = PENDING`.

### 6.3 AMP `/resume` payload for creative approval

**Approve some ads, reject others; allow edits:**

POST https://amp.your-domain.com/api/v1/runs/{run\_id}/resume

Authorization: Bearer \<AMP\_API\_KEY\>

Content-Type: application/json

{

  "run\_id": "run\_creative\_123",

  "task\_id": "guardian\_creative\_approval",

  "inputs": {

    "creative\_decision": {

      "ads": {

        "ad\_1": "approve",

        "ad\_2": "reject"

      },

      "landing\_pages": {

        "lp\_1": "approve",

        "lp\_2": "approve"

      }

    },

    "artifact\_comments": {

      "ad\_2": "Too aggressive claim; remove revenue guarantee.",

      "lp\_2": "Update hero image to match new brand palette."

    },

    "comment": "Proceed with ad\_1 \+ both LPs.",

    "meta": {

      "approved\_by": "founder@example.com",

      "timestamp": "2025-11-25T10:40:00Z"

    }

  }

}

### 6.4 How `/resume` is written into `StartupValidationState`

Your `/resume` HTTP handler should:

def handle\_creative\_resume(payload: dict):

    run\_id \= payload\["run\_id"\]

    task\_id \= payload\["task\_id"\]

    \# 1\) Load StartupValidationState for this project

    state \= load\_state\_from\_db(project\_id=resolve\_project\_id(run\_id))

    \# 2\) Apply creative decision

    CompassCrew().apply\_creative\_decision\_from\_resume(state, payload)

    \# 3\) Persist state

    save\_state\_to\_db(state)

    \# 4\) Trigger Flow resume at "await\_creative\_approval"

    resume\_flow(run\_id=run\_id, next\_step="await\_creative\_approval")

After resume:

* Flow goes to `route_after_desirability`.  
    
* If all ads/LPs needed for experiment are `APPROVED`, Pulse will deploy campaigns next run.  
    
* If critical creatives are `REJECTED`, you can either:  
    
  * Mark `DesirabilitySignal.NO_SIGNAL` and re-run `run_desirability_experiments`, or  
  * Add a dedicated `regenerate_creatives` step (optional extension).

---

## 7\) AMP Configuration Artifacts

### 7.1 `agents.yaml` (Pulse \+ Forge \+ Guardian/Compass HITL)

\# agents.yaml

agents:

  \- id: pulse\_ad\_creative

    name: Pulse Ad Creative Agent

    crew: pulse

    role: "AdCreativeAgent"

    tools:

      \- copywriting\_tool

      \- image\_generation\_tool

      \- learning\_retrieval\_tool

    memory: true

    external\_memory: supabase\_vector\_store

  \- id: pulse\_comms

    name: Pulse Communications Agent

    crew: pulse

    role: "CommsAgent"

    tools:

      \- copywriting\_tool

      \- template\_engine\_tool

      \- learning\_retrieval\_tool

    memory: true

    external\_memory: supabase\_vector\_store

  \- id: pulse\_analytics

    name: Pulse Analytics Agent

    crew: pulse

    role: "AnalyticsAgent"

    tools:

      \- experiment\_deploy\_tool

      \- analytics\_tool

      \- platform\_config\_tool

    memory: true

  \- id: forge\_ux\_ui

    name: Forge UX/UI Designer

    crew: forge

    role: "UXUIDesignerAgent"

    tools:

      \- component\_library\_scraper

      \- canvas\_builder\_tool

    memory: true

    external\_memory: supabase\_vector\_store

  \- id: forge\_frontend

    name: Forge Frontend Dev

    crew: forge

    role: "FrontendDevAgent"

    tools:

      \- file\_read\_tool

      \- file\_write\_tool

      \- landing\_page\_deployment\_tool

    memory: true

  \- id: forge\_backend

    name: Forge Backend Dev

    crew: forge

    role: "BackendDevAgent"

    tools:

      \- tech\_stack\_validator

      \- api\_integration\_tool

    memory: true

  \- id: guardian\_qa

    name: Guardian QA Agent

    crew: guardian

    role: "QAAgent"

    tools:

      \- methodology\_check\_tool

      \- guardian\_review\_tool

    human\_input: true

  \- id: compass\_approval

    name: Compass Human Approval Agent

    crew: compass

    role: "HumanApprovalAgent"

    tools:

      \- approval\_request\_tool

    human\_input: true

    memory: true

### 7.2 `tasks.yaml`

\# tasks.yaml

tasks:

  \- id: pulse\_generate\_ads

    agent: pulse\_ad\_creative

    description: "Generate ad concepts for desirability experiments."

    tools:

      \- copywriting\_tool

    output\_schema: AdConcepts

  \- id: pulse\_generate\_landing\_page\_copy

    agent: pulse\_comms

    description: "Generate landing page copy based on current Value Proposition Canvas."

    tools:

      \- copywriting\_tool

      \- template\_engine\_tool

    output\_schema: LandingPageCopy

  \- id: pulse\_deploy\_experiments

    agent: pulse\_analytics

    description: "Deploy ads \+ landing pages as a desirability experiment."

    tools:

      \- experiment\_deploy\_tool

    output\_schema: ExperimentDeployment

  \- id: pulse\_collect\_desirability\_metrics

    agent: pulse\_analytics

    description: "Collect metrics and compute CTR/conversion for desirability decision."

    tools:

      \- analytics\_tool

    output\_schema: DesirabilityMetrics

  \- id: guardian\_creative\_review

    agent: guardian\_qa

    description: "Run policy/QA checks on ad and landing page drafts; decide auto-approve vs HITL."

    tools:

      \- guardian\_review\_tool

    human\_input: false

    output\_schema: GuardianCreativeReview

  \- id: guardian\_creative\_approval

    agent: compass\_approval

    description: "Present creatives to human for approval/rejection and capture comments."

    tools:

      \- approval\_request\_tool

    human\_input: true

    output\_schema: CreativeApprovalDecision

  \- id: forge\_build\_layout

    agent: forge\_ux\_ui

    description: "Generate a component layout spec for MVP or landing page."

    tools:

      \- component\_library\_scraper

    output\_schema: LayoutSpec

  \- id: forge\_build\_frontend

    agent: forge\_frontend

    description: "Write and commit frontend code for MVP/landing page."

    tools:

      \- file\_write\_tool

      \- landing\_page\_deployment\_tool

    output\_schema: BuildArtifact

    human\_input: false

  \- id: forge\_assess\_feasibility

    agent: forge\_backend

    description: "Assess technical and cost feasibility for the proposed MVP."

    tools:

      \- tech\_stack\_validator

    output\_schema: FeasibilityAssessment

    human\_input: false

### 7.3 `crewai_config.yaml`

\# crewai\_config.yaml

webhooks:

  humanInputWebhook: "https://startupai.app/api/amp/human-input"

  taskWebhookUrl: "https://startupai.app/api/amp/task-events"

  stepWebhookUrl: "https://startupai.app/api/amp/step-events"

  crewWebhookUrl: "https://startupai.app/api/amp/crew-events"

memory:

  default\_store: supabase\_vector\_store

  stores:

    supabase\_vector\_store:

      type: supabase\_pgvector

      url: "https://your-supabase-project.supabase.co"

      api\_key: "${SUPABASE\_SERVICE\_KEY}"

      table: "startupai\_learning"

      embedding\_model: "text-embedding-3-small"

      index\_name: "learning\_embeddings"

crews:

  pulse:

    external\_memory: supabase\_vector\_store

  forge:

    external\_memory: supabase\_vector\_store

  sage:

    external\_memory: supabase\_vector\_store

  ledger:

    external\_memory: supabase\_vector\_store

  guardian:

    external\_memory: supabase\_vector\_store

  compass:

    external\_memory: supabase\_vector\_store

---

## 8\) HITL Integration for Viability (price\_pivot vs cost\_pivot vs kill)

### 8.1 `/resume` HTTP payloads

**Price pivot:**

{

  "run\_id": "run\_abc123",

  "task\_id": "compass\_viability\_decision",

  "inputs": {

    "viability\_pivot\_decision": "price\_pivot",

    "comment": "Increase base price by 25% and re-test desirability.",

    "meta": {

      "approved\_by": "founder@example.com",

      "timestamp": "2025-11-25T10:30:00Z"

    }

  }

}

**Cost pivot:**

{

  "run\_id": "run\_abc123",

  "task\_id": "compass\_viability\_decision",

  "inputs": {

    "viability\_pivot\_decision": "cost\_pivot",

    "comment": "Remove concierge onboarding and reduce infra budget by 40%.",

    "meta": {

      "approved\_by": "founder@example.com",

      "timestamp": "2025-11-25T10:32:00Z"

    }

  }

}

**Kill:**

{

  "run\_id": "run\_abc123",

  "task\_id": "compass\_viability\_decision",

  "inputs": {

    "viability\_pivot\_decision": "kill",

    "comment": "Market too small and CAC\>LTV even under aggressive assumptions.",

    "meta": {

      "approved\_by": "founder@example.com",

      "timestamp": "2025-11-25T10:35:00Z"

    }

  }

}

### 8.2 Flow routing based on decision

Already wired in:

* `CompassCrew.apply_viability_decision_from_resume` writes `pending_pivot_type` and `human_approval_status=APPROVED`.  
* Flow resumes at `route_after_viability_decision`, which routes:

\# in StartupValidationFlow.route\_after\_viability\_decision

if pivot \== PivotType.PRICE\_PIVOT:

    \# regression to Desirability with updated pricing config

    return "run\_desirability\_experiments"

if pivot \== PivotType.COST\_PIVOT:

    \# regression to Feasibility w/ updated cost constraints

    return "run\_feasibility\_assessment"

if pivot \== PivotType.KILL:

    return "terminal\_killed"

You now have:

* A full agent/crew manifest.  
* A concrete, Pydantic-backed `StartupValidationState` with artifacts, approvals, platform config, budgets, and routing.  
* A Flow with explicit desirability, feasibility, viability loops and regression paths.  
* Pulse/Forge/Ledger orchestration with tools and Pydantic result models.  
* A production-ready Phase 1 spec: ad \+ LP generation, approvals, deployment, metrics, platform selection, budgets/durations.  
* AMP YAML, webhook, and `/resume` contracts for both creatives and viability pivots.

You can drop these modules into `src/startupai/` and wire the remaining `NotImplementedError` sections to your actual AMP client \+ ad platform integrations.  
