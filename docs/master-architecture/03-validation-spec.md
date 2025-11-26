---
purpose: Core validation flow technical specification
status: planning
last_reviewed: 2025-11-21
---

# StartupAI Internal Validation System - Technical Specification

## Document Purpose

This document provides the complete technical specification for building StartupAI's internal validation system using CrewAI Flows. The goal is for StartupAI to "eat its own dog food" - validating its own business model before offering the service to clients.

**Status**: Planning Complete
**Created**: 2025-11-21
**Context Source**: [02-organization.md](./02-organization.md) contains the conceptual organization this spec implements

---

## Background & Rationale

### Why Build for Ourselves First

StartupAI's value proposition is helping startups validate desirability, feasibility, and viability through AI-powered analysis. If we cannot use our own system to validate our own business model, we cannot credibly offer it to clients.

**The Flywheel Effect**:
- StartupAI validates its own VPC and BMC using the system
- System captures learnings from our validation cycles
- Methodology improves based on real experience
- Clients benefit from battle-tested process
- Client learnings feed back into methodology

### Key Insight: Gated Validation

Validation is **gated**, not parallel:

```
[Test Cycles] → DESIRABILITY GATE → [Test Cycles] → FEASIBILITY GATE → [Test Cycles] → VIABILITY GATE
```

StartupAI's first product iteration focuses on **desirability validation** - the first gate all startups must pass. Feasibility and viability capabilities come later.

---

## Organizational Structure Summary

> **Single Source**: See [02-organization.md](./02-organization.md) for complete founder details, agents, and organizational structure.

### Service/Commercial Model

```
                    GUARDIAN (Board Chair)
                    Accountability for governance
                           │
    ┌──────────────────────┼──────────────────────┐
    │                      │                      │
SERVICE SIDE            COMPASS             COMMERCIAL SIDE
(Customer-Facing)      (Balance)           (Value Delivery)

Sage owns:            Project Manager      Sage, Forge, Pulse, Ledger
• Customer Service                         (flat peers)
• Founder Onboarding
• Consultant Onboarding
        │
        └──→ [Client Brief] ──────→
```

### The 6 AI Founders

| Founder | Role | Primary Domain |
|---------|------|----------------|
| **Sage** | CSO | Strategy, VPC design, owns Service Side |
| **Forge** | CTO | Build, technical feasibility |
| **Pulse** | CGO | Growth, market signals, desirability evidence |
| **Compass** | CPO | Balance, synthesis, pivot/proceed |
| **Guardian** | CGO | Governance, accountability, oversight |
| **Ledger** | CFO | Finance, viability, compliance |

### 18 Specialist Agents

**Service Side (Sage owns)**: Customer Service, Founder Onboarding, Consultant Onboarding

**Commercial Side**:
- Sage: Customer Researcher, Competitor Analyst
- Forge: UX/UI Designer, Frontend Developer, Backend Developer
- Pulse: Ad Creative, Communications, Social Media Analyst
- Compass: Project Manager
- Ledger: Financial Controller, Legal & Compliance

**Governance (Guardian)**: Audit Agent, Security Agent, Quality Assurance Agent

---

## CrewAI Architecture Decisions

### Why Flows + Crews

CrewAI provides two complementary systems:

- **Crews**: Autonomous agent teams that collaborate on tasks
- **Flows**: Event-driven orchestration that coordinates multiple crews

For StartupAI's Service/Commercial model:
- Each "side" or founder domain = separate Crew
- Flow orchestrates handoffs between crews
- Routers implement Guardian's governance gates
- Structured state carries the Client Brief through the system

### Key CrewAI Features Used

| Requirement | CrewAI Feature |
|-------------|----------------|
| Service → Commercial handoff | `@listen()` decorators chain crews |
| Guardian governance gates | `@router()` with conditional routing |
| Client Brief schema | Structured State with Pydantic |
| Audit trail | `@persist` decorator for SQLite storage |
| Founder as manager | `manager_agent` in hierarchical process |
| Compass synthesis | Router that evaluates all outcomes |

### Process Types

- **Sequential**: Tasks flow in order within a crew
- **Hierarchical**: Manager agent delegates and validates (used where founders oversee agents)
- **Flows**: Orchestrate between crews with routing logic

---

## Tool Definitions

The following tools provide specialized capabilities to agents across all crews:

### Pulse Crew Tools (Desirability Experiments)

```python
class CopywritingTool:
    """Generate ad variants for multi-platform testing"""
    def generate_ads(
        self,
        brief: dict,
        vpc: dict,
        variant_tag: str,
        platforms: List[Platform],
        variants_per_platform: int = 2,
    ) -> List[dict]:
        """
        Returns: List of ad objects with headline, body, cta per platform
        """
        raise NotImplementedError

class LandingPageGeneratorTool:
    """Generate landing page code variants"""
    def generate_pages(
        self,
        vpc: dict,
        offer_variant: str,
        num_variants: int = 2,
    ) -> List[dict]:
        """
        Returns: List of page specs (HTML + routing) for A/B testing
        """
        raise NotImplementedError

class LandingPageDeploymentTool:
    """Deploy landing pages to Vercel/Netlify"""
    def deploy_page_variants(
        self,
        pages: List[dict],
        provider: str,
        base_url: str,
        project_id: str,
    ) -> List[dict]:
        """
        Returns: Deployed page descriptors with URLs
        """
        raise NotImplementedError

class ExperimentDeployTool:
    """Deploy A/B tests across multiple platforms"""
    def deploy(
        self,
        ad_variants: List[dict],
        landing_page_variants: List[dict],
        platform_budgets: List[PlatformBudgetConfig],
    ) -> Dict:
        """
        Returns: experiment_id and platform_campaign_ids mapping
        """
        raise NotImplementedError

class AnalyticsTool:
    """Collect metrics from analytics platforms"""
    def collect_desirability_metrics(
        self,
        experiment_id: str,
        platform: Platform,
    ) -> DesirabilityMetrics:
        """
        Returns: Populated DesirabilityMetrics from GA/PostHog/ads APIs
        """
        raise NotImplementedError
```

### Forge Crew Tools (Feasibility Assessment)

```python
class ComponentLibraryScraper:
    """Generate wireframe/component layout from VPC"""
    def generate_layout_spec(self, vpc: dict, lite: bool = False) -> dict:
        """
        Produce layout spec using approved UI components
        """
        raise NotImplementedError

class TechStackValidator:
    """Evaluate technical feasibility and cost"""
    def assess(self, layout_spec: dict, backend_requirements: dict) -> Dict:
        """
        Returns: FeasibilitySignal, cost estimates, feature constraints
        """
        raise NotImplementedError
```

### Ledger Crew Tools (Viability Analysis)

```python
class PythonREPLTool:
    """Calculate unit economics"""
    def eval_unit_economics(self, inputs: dict) -> Dict:
        """
        Inputs: { cac, ltv, tam, margin_pct, churn }
        Returns: { viability_flag, payback_months }
        """
        raise NotImplementedError

class CostTrackingTool:
    """Track validation run costs"""
    def get_validation_run_cost(self, project_id: str) -> float:
        """
        Returns: USD cost of current AMP validation run (tokens + infra)
        """
        raise NotImplementedError
```

### Guardian Crew Tools (Quality & Compliance)

```python
class GuardianReviewTool:
    """Automatic QA checks for creatives"""
    def check_creatives(self, ads: List[dict], pages: List[dict]) -> Dict:
        """
        Returns: issues list, ad_flags, page_flags with ok/reject/hitl status
        """
        raise NotImplementedError
```

### Compass Crew Tools (HITL Workflows)

```python
class ApprovalRequestTool:
    """Trigger HITL approval workflows"""
    def request_approval(
        self,
        approval_type: str,
        context: dict,
        options: List[dict],
    ) -> CompassHitlRequest:
        """
        Sends webhook to product app, pauses flow, returns task_id for /resume
        """
        raise NotImplementedError
```

---

## Creative Approval Workflow (Guardian + HITL)

### Overview

All ad creatives and landing pages go through a two-stage approval process before deployment:

1. **Guardian Automatic Review**: QA checks for banned terms, formatting issues, broken links
2. **Human Approval (Optional)**: If Guardian flags issues or finds potential problems, HITL approval is required

### State Management

Per-artifact approval tracking:
- `approval_status`: `DRAFT` → `PENDING_REVIEW` → `APPROVED`/`REJECTED`
- `human_approval_status`: `NOT_REQUIRED`, `PENDING`, `APPROVED`, `REJECTED`
- `human_comment`: Feedback from approver

Global state tracking:
- `state.human_approval_status`: Tracks overall HITL requirement
- `state.human_comment`: Founder's decision rationale

### Workflow Steps

#### Step 1: Pulse Generates Creatives
```python
# In PulseCrew.kickoff()
ad_variants = self.copywriter.generate_ads(...)
landing_page_variants = self.landing_gen.generate_pages(...)

# All start as DRAFT
for ad in ad_variants:
    ad.approval_status = ArtifactApprovalStatus.DRAFT
```

#### Step 2: Guardian Automatic Review
```python
# GuardianCrew.review_creatives()
guardian_result = self.guardian.check_creatives(ads, pages)

# Returns:
# {
#   "issues": ["ad_2: aggressive revenue claim"],
#   "ad_flags": {
#     "ad_1": {"status": "ok"},
#     "ad_2": {"status": "hitl", "reasons": ["unverified claim"]}
#   },
#   "page_flags": {
#     "lp_1": {"status": "ok"},
#     "lp_2": {"status": "ok"}
#   },
#   "hitl_required": True
# }
```

#### Step 3: Conditional HITL Pause
```python
if guardian_result.hitl_required:
    # Mark experiment as pending review
    experiment.approval_status = ArtifactApprovalStatus.PENDING_REVIEW
    state.human_approval_status = HumanApprovalStatus.PENDING

    # Send webhook to product app
    compass.request_approval(
        approval_type="creative_review",
        context={
            "experiment_id": experiment.id,
            "ads": ad_variants,
            "pages": landing_page_variants,
            "guardian_issues": guardian_result.issues
        },
        options=[
            {"label": "Approve All", "action": "approve_all"},
            {"label": "Approve Selected", "action": "approve_selected"},
            {"label": "Reject and Regenerate", "action": "regenerate"}
        ]
    )

    # Flow pauses at await_creative_approval
    return "await_creative_approval"
```

#### Step 4: Human Decision via /resume
```json
POST /resume
{
  "run_id": "run_123",
  "task_id": "guardian_creative_approval",
  "inputs": {
    "creative_decision": {
      "ads": {
        "ad_1": "approve",
        "ad_2": "reject"
      },
      "landing_pages": {
        "lp_1": "approve",
        "lp_2": "approve"
      }
    },
    "artifact_comments": {
      "ad_2": "Too aggressive claim; remove revenue guarantee."
    },
    "comment": "Proceed with ad_1 + both LPs",
    "meta": {
      "approved_by": "founder@example.com",
      "timestamp": "2025-11-25T10:40:00Z"
    }
  }
}
```

#### Step 5: Apply Decision and Resume Flow
```python
# CompassCrew.apply_creative_decision_from_resume()
def apply_creative_decision_from_resume(state: StartupValidationState, payload: dict):
    decision = payload["inputs"]["creative_decision"]

    # Update ad variant statuses
    for ad in state.desirability_experiments[-1].ad_variants:
        if ad.id in decision["ads"]:
            if decision["ads"][ad.id] == "approve":
                ad.approval_status = ArtifactApprovalStatus.APPROVED
                ad.human_approval_status = HumanApprovalStatus.APPROVED
            else:
                ad.approval_status = ArtifactApprovalStatus.REJECTED
                ad.human_approval_status = HumanApprovalStatus.REJECTED

    # Update global state
    state.human_approval_status = HumanApprovalStatus.APPROVED
    state.human_comment = payload["inputs"]["comment"]

    # Flow resumes at route_after_desirability
```

### Result: Only Approved Creatives Deploy

When Pulse deploys experiments, it only includes artifacts with `approval_status == APPROVED`:

```python
# ExperimentDeployTool.deploy()
approved_ads = [ad for ad in ad_variants if ad.approval_status == ArtifactApprovalStatus.APPROVED]
approved_pages = [lp for lp in landing_page_variants if lp.approval_status == ArtifactApprovalStatus.APPROVED]

if not approved_ads or not approved_pages:
    # Not enough approved creatives → regenerate or kill experiment
    return {"error": "insufficient_approved_creatives"}
```

---

## Phase 1: Service Side + Desirability Validation

**Objective**: Intake StartupAI's own business context → Analyze customers/competitors → Validate desirability assumptions

### Crews to Build

#### 1. Service Crew (Sage owns)

**Purpose**: Onboard StartupAI itself as the "client"

**Agents**:
- Customer Service Agent - Not needed for internal use
- Founder Onboarding Agent - Captures StartupAI's business context
- Consultant Onboarding Agent - Not needed for internal use

**For internal validation, simplify to**:
- Internal Onboarding Agent - Structured interview for StartupAI's own VPC/BMC

**Output**: StartupAI Client Brief

**Client Brief Schema**:
```python
class StartupAIBrief(BaseModel):
    id: str
    business_idea: str = "AI-powered startup validation platform"
    customer_segments: List[str] = ["Founders", "Consultants/Agencies"]
    problem_statement: str
    current_stage: str
    key_assumptions: List[Assumption]
    validation_goals: List[str]

class Assumption(BaseModel):
    statement: str
    category: str  # desirability, feasibility, viability
    priority: int
    evidence_needed: str
```

#### 2. Analysis Crew (Sage)

**Purpose**: Analyze StartupAI's customers and competitors

**Agents**:
- Customer Researcher
  - Analyze Founders segment: Jobs, Pains, Gains
  - Analyze Consultants segment: Jobs, Pains, Gains
  - Output: Customer Profiles for both segments

- Competitor Analyst
  - Traditional consulting ($3-10K, 2-4 weeks)
  - DIY tool stack ($300+/mo, 80+ hrs/mo)
  - Other AI validation tools
  - Output: Competitive positioning map

**Output**: VPC components ready for testing

#### 3. Governance Crew (Guardian) - Phase 1 Version

**Purpose**: Validate analysis quality before proceeding

**Agents**:
- QA Agent
  - Framework compliance check (VPC structure)
  - Logical consistency
  - Completeness validation

**Output**: QA Pass/Fail with feedback

### Unified Flow Architecture

> **Note**: The implementation uses a single `StartupValidationFlow` class that orchestrates all three validation phases (Desirability, Feasibility, Viability) with non-linear routing based on Innovation Physics signals.
>
> **Complete Implementation**: See `docs/drafts/master-spec.md` lines 421-796 and `docs/strategyzer-physics.md` for full router logic.

```python
from crewai.flow.flow import Flow, start, listen, router

class StartupValidationFlow(Flow[StartupValidationState]):

    # ---------- PHASE 0: INTAKE & VPC (Sage + Guardian) ----------

    @start()
    def intake_and_hypothesis(self):
        """Sage creates VPC, Guardian validates quality"""
        sage = SageCrew()
        guardian = GuardianCrew()

        sage_result = sage.kickoff_intake_and_vpc(
            project_id=self.state.project_id
        )

        self.state.phase = Phase.IDEATION
        self.state.problem_fit = sage_result.problem_fit
        self.state.current_segment = sage_result.segment
        self.state.current_value_prop = sage_result.value_prop
        self.state.vpc_document_url = sage_result.vpc_document_url
        self.state.bmc_document_url = sage_result.bmc_document_url

        gate_result = guardian.phase_gate(
            phase="ideation",
            vpc_url=self.state.vpc_document_url,
            bmc_url=self.state.bmc_document_url,
        )

        self.state.guardian_last_issues = gate_result.issues

        if not gate_result.passed:
            # Loop Sage until Guardian is satisfied
            return "intake_and_hypothesis"

        return "run_desirability_experiments"

    # ---------- PHASE 1: DESIRABILITY LOOP (Pulse + Guardian + Sage) ----------

    @listen("run_desirability_experiments")
    def run_desirability_experiments(self):
        """
        Generate ads/LP variants, run Guardian + optional HITL approvals,
        deploy campaigns, collect metrics and compute desirability signal.
        """
        self.state.phase = Phase.DESIRABILITY
        self.state.current_risk_axis = RiskAxis.DESIRABILITY

        pulse = PulseCrew()
        result = pulse.kickoff(
            inputs={
                "project_id": self.state.project_id,
                "vpc_url": self.state.vpc_document_url,
                "downgrade_active": self.state.downgrade_active,
            }
        )

        self.state.desirability_signal = result.signal
        self.state.desirability_experiments.append(result.experiment_run)

        return "route_after_desirability"

    @router("route_after_desirability")
    def route_after_desirability(self):
        """Innovation Physics routing: Problem-Solution & Product-Market filters"""
        signal = self.state.desirability_signal

        # Problem-Solution Filter: Low problem resonance → segment pivot
        if signal == DesirabilitySignal.NO_INTEREST:
            self.state.last_pivot_type = PivotType.SEGMENT_PIVOT
            SageCrew().adjust_segment(
                project_id=self.state.project_id,
                vpc_url=self.state.vpc_document_url,
            )
            return "run_desirability_experiments"

        # Product-Market Filter + Zombie Detection: Good resonance but low commitment → value pivot
        if signal == DesirabilitySignal.WEAK_INTEREST:
            self.state.last_pivot_type = PivotType.VALUE_PIVOT
            SageCrew().adjust_value_map(
                project_id=self.state.project_id,
                vpc_url=self.state.vpc_document_url,
            )
            return "run_desirability_experiments"

        # Strong commitment → proceed to feasibility
        if signal == DesirabilitySignal.STRONG_COMMITMENT:
            return "run_feasibility_assessment"

        # NO_SIGNAL or unexpected → iterate creatives again
        return "run_desirability_experiments"

    # ---------- PHASE 2: FEASIBILITY LOOP (Forge + Pulse) ----------

    @listen("run_feasibility_assessment")
    def run_feasibility_assessment(self):
        """Forge assesses technical feasibility"""
        self.state.phase = Phase.FEASIBILITY
        self.state.current_risk_axis = RiskAxis.FEASIBILITY

        forge = ForgeCrew()
        result = forge.kickoff(
            inputs={
                "project_id": self.state.project_id,
                "vpc_url": self.state.vpc_document_url,
            }
        )

        self.state.feasibility_signal = result.feasibility_flag
        self.state.last_feasibility_artifact = result.artifact

        return "route_after_feasibility"

    @router("route_after_feasibility")
    def route_after_feasibility(self):
        """Downgrade Protocol: Technical constraints force value prop iteration"""
        flag = self.state.feasibility_signal

        if flag == FeasibilitySignal.GREEN:
            return "run_viability_analysis"

        # ORANGE_CONSTRAINED: Feature downgrade required → re-test desirability
        if flag == FeasibilitySignal.ORANGE_CONSTRAINED:
            self.state.last_pivot_type = PivotType.COST_PIVOT
            self.state.downgrade_active = True
            ForgeCrew().apply_downgrade_to_vpc(
                project_id=self.state.project_id,
                vpc_url=self.state.vpc_document_url,
                artifact=self.state.last_feasibility_artifact,
            )
            return "run_desirability_experiments"  # Re-test with "lite" version

        # RED_IMPOSSIBLE: Kill the project
        if flag == FeasibilitySignal.RED_IMPOSSIBLE:
            self.state.phase = Phase.KILLED
            self.state.last_pivot_type = PivotType.KILL
            return "terminal_killed"

        # UNKNOWN → re-run feasibility with adjustments
        return "run_feasibility_assessment"

    # ---------- PHASE 3: VIABILITY LOOP (Ledger + Compass) ----------

    @listen("run_viability_analysis")
    def run_viability_analysis(self):
        """Ledger calculates unit economics"""
        self.state.phase = Phase.VIABILITY
        self.state.current_risk_axis = RiskAxis.VIABILITY

        ledger = LedgerCrew()
        result = ledger.kickoff(
            inputs={
                "project_id": self.state.project_id,
                "experiments": [e.dict() for e in self.state.desirability_experiments],
                "artifact": (
                    self.state.last_feasibility_artifact.dict()
                    if self.state.last_feasibility_artifact
                    else None
                ),
            }
        )

        self.state.viability_signal = result.viability_flag
        self.state.last_viability_metrics = result.metrics

        return "route_after_viability"

    @router("route_after_viability")
    def route_after_viability(self):
        """Unit Economics Trigger: CAC/LTV imbalance → strategic pivot (HITL required)"""
        signal = self.state.viability_signal

        if signal == ViabilitySignal.PROFITABLE:
            self.state.phase = Phase.VALIDATED
            self.state.last_pivot_type = PivotType.NONE
            return "terminal_validated"

        # UNDERWATER/ZOMBIE_MARKET: CAC > LTV → requires human decision
        if signal in (ViabilitySignal.UNDERWATER, ViabilitySignal.ZOMBIE_MARKET):
            self.state.human_approval_status = HumanApprovalStatus.PENDING
            self.state.pending_pivot_type = PivotType.NONE

            compass = CompassCrew()
            hitl = compass.request_viability_decision(
                project_id=self.state.project_id,
                viability_metrics=self.state.last_viability_metrics,
                experiments=self.state.desirability_experiments,
            )

            self.state.last_human_decision_task_id = hitl.task_id
            self.state.last_human_decision_run_id = hitl.run_id

            return "await_viability_decision"

        return "run_viability_analysis"

    @listen("await_viability_decision")
    def await_viability_decision(self):
        """Pause for HITL decision via /resume endpoint"""
        return "route_after_viability_decision"

    @router("route_after_viability_decision")
    def route_after_viability_decision(self):
        """Execute human decision: price up, cost down, or kill"""
        pivot = self.state.pending_pivot_type

        if pivot == PivotType.PRICE_PIVOT:
            self.state.last_pivot_type = PivotType.PRICE_PIVOT
            self.state.phase = Phase.DESIRABILITY
            self.state.current_risk_axis = RiskAxis.DESIRABILITY
            return "run_desirability_experiments"  # Re-test willingness-to-pay

        if pivot == PivotType.COST_PIVOT:
            self.state.last_pivot_type = PivotType.COST_PIVOT
            self.state.phase = Phase.FEASIBILITY
            self.state.current_risk_axis = RiskAxis.FEASIBILITY
            return "run_feasibility_assessment"  # Reduce feature scope

        if pivot == PivotType.KILL:
            self.state.phase = Phase.KILLED
            self.state.last_pivot_type = PivotType.KILL
            return "terminal_killed"

        # Safety default: kill if no valid decision
        self.state.phase = Phase.KILLED
        self.state.last_pivot_type = PivotType.KILL
        return "terminal_killed"

    # ---------- TERMINALS ----------

    @listen("terminal_validated")
    def terminal_validated(self):
        """Project passed all three gates"""
        GuardianCrew().final_audit(self.state)
        return None

    @listen("terminal_killed")
    def terminal_killed(self):
        """Project terminated"""
        GuardianCrew().log_termination(self.state)
        return None
```

### Phase 1 Success Criteria

- [ ] StartupAI Brief captured with business context
- [ ] Customer Profile for Founders (Jobs/Pains/Gains)
- [ ] Customer Profile for Consultants (Jobs/Pains/Gains)
- [ ] Competitor Analysis with positioning
- [ ] Key assumptions identified and prioritized
- [ ] Guardian QA passes analysis quality
- [ ] Desirability experiment designs ready

### Phase 1 Deliverables

1. **StartupAI VPC** - Value Proposition Canvas for both segments
2. **Assumption Backlog** - Prioritized list of desirability assumptions
3. **Experiment Designs** - How to test each assumption
4. **QA Report** - Guardian's validation of analysis quality

---

## Phase 2: Commercial Side + Build/Test Capabilities

**Objective**: Build testable artifacts → Run desirability experiments → Synthesize evidence → Pivot/Proceed

### Crews to Build

#### 4. Build Crew (Forge)

**Purpose**: Create testable artifacts for desirability validation

**Agents**:
- UX/UI Designer
  - Design landing pages for Founders
  - Design landing pages for Consultants
  - Design key user flows

- Frontend Developer
  - Implement landing pages
  - Build interactive prototypes

- Backend Developer
  - API for data collection
  - Analytics integration

**Output**: Deployed testable artifacts with tracking

#### 5. Growth Crew (Pulse)

**Purpose**: Run experiments and collect desirability signals

**Agents**:
- Ad Creative Agent
  - Ad copy variations for Founders
  - Ad copy variations for Consultants
  - Landing page copy

- Communications Agent
  - Email sequences
  - Content marketing pieces

- Social Media Analyst
  - Track engagement signals
  - Sentiment analysis
  - Conversion metrics

**Output**: Desirability evidence (quantitative + qualitative)

#### 6. Synthesis Crew (Compass)

**Purpose**: Integrate evidence and recommend pivot/proceed

**Agents**:
- Project Manager
  - Aggregate evidence across experiments
  - Track against assumptions
  - Prepare pivot/proceed analysis

**Output**: Evidence synthesis with recommendation

### Phase 2 Flow Structure

> **Note**: Phase 2 (Desirability experiments + Build/Test) is now integrated into the unified `StartupValidationFlow` above. See `run_desirability_experiments()` and `route_after_desirability()` methods.

### Phase 2 Success Criteria

- [ ] Landing pages deployed for both segments
- [ ] Ad campaigns run with real spend
- [ ] Quantitative signals collected (CTR, conversions)
- [ ] Qualitative feedback gathered
- [ ] Evidence synthesized against assumptions
- [ ] Compass delivers pivot/proceed recommendation
- [ ] If pivot: clear direction for VPC iteration

### Phase 2 Deliverables

1. **Test Artifacts** - Landing pages, ads, prototypes
2. **Evidence Report** - All signals collected with analysis
3. **Assumption Validation** - Which assumptions validated/invalidated
4. **Pivot/Proceed Recommendation** - Compass's synthesis

---

## Phase 3: Governance + Viability + Full Loop

**Objective**: Complete governance oversight → Viability validation → Flywheel capture

### Crews to Build

#### 7. Finance Crew (Ledger)

**Purpose**: Validate viability of StartupAI's business model

**Agents**:
- Financial Controller
  - Track actual costs of validation cycles
  - Calculate unit economics
  - Model pricing scenarios

- Legal & Compliance Agent
  - Terms of service
  - Data privacy compliance
  - Regulatory requirements

**Output**: Viability assessment with financial model

#### 8. Enhanced Governance Crew (Guardian)

**Purpose**: Full audit trail and compliance

**Agents**:
- Audit Agent
  - Process compliance verification
  - Decision trail documentation
  - Accountability tracking

- Security Agent
  - Data privacy review
  - Security assessment
  - Risk monitoring

- QA Agent (enhanced)
  - Cross-crew quality checks
  - Methodology compliance

**Output**: Audit report with compliance status

### Phase 3 Flow Structure

> **Note**: Phase 3 (Feasibility + Viability + Governance) is now integrated into the unified `StartupValidationFlow` above. See `run_feasibility_assessment()`, `route_after_feasibility()`, `run_viability_analysis()`, and `route_after_viability()` methods.

### Phase 3 Success Criteria

- [ ] Feasibility confirmed for core value proposition
- [ ] Unit economics calculated and viable
- [ ] Pricing validated with willingness-to-pay data
- [ ] Full audit trail documented
- [ ] Security and compliance verified
- [ ] Flywheel learnings captured
- [ ] Methodology improvements documented

### Phase 3 Deliverables

1. **Feasibility Report** - Can we build this?
2. **Viability Model** - Unit economics, pricing, runway
3. **Audit Trail** - Full compliance documentation
4. **Flywheel Entry** - Learnings for methodology improvement
5. **Methodology Updates** - Improvements based on experience

---

## Experiment Configuration & Platform Selection

### Configuration Models

The `ExperimentConfigResolver` determines which advertising platforms to use based on customer segment type (B2B vs B2C):

```python
class ProjectExperimentConfig(BaseModel):
    variants_per_platform: int = 2
    landing_page_variants: int = 2
    landing_page_provider: str = "vercel"
    base_url_template: str = "https://startupai-{project_id}.vercel.app"
    platform_budgets: List[PlatformBudgetConfig] = Field(default_factory=list)

class ExperimentConfigResolver:
    """
    Reads VPC/BMC to decide:
      - B2B vs B2C
      - Platforms (LinkedIn/Google for B2B, Meta/TikTok for B2C)
      - Budgets, duration, targeting
    """

    def __init__(self, config_path: str = "config/experiments.yaml"):
        self.config_path = config_path

    def resolve_from_vpc(self, vpc: dict) -> ProjectExperimentConfig:
        segment_type = vpc.get("segment_type", "b2c").lower()

        if segment_type == "b2b":
            platform_budgets = [
                PlatformBudgetConfig(
                    platform=Platform.LINKEDIN,
                    duration_days=7,
                    total_budget_usd=400.0,
                    min_impressions=3000,
                    target_cpc_usd=5.0,
                    audience_spec={"job_titles": ["CTO", "VP Engineering"]},
                ),
                PlatformBudgetConfig(
                    platform=Platform.GOOGLE_SEARCH,
                    duration_days=7,
                    total_budget_usd=600.0,
                    min_impressions=5000,
                    target_cpc_usd=4.0,
                    audience_spec={"keywords": ["enterprise ecommerce", "b2b saas"]},
                ),
            ]
        else:  # B2C
            platform_budgets = [
                PlatformBudgetConfig(
                    platform=Platform.META,
                    duration_days=5,
                    total_budget_usd=400.0,
                    min_impressions=5000,
                    target_cpc_usd=1.5,
                    audience_spec={"interests": ["online shopping", "fashion"]},
                ),
                PlatformBudgetConfig(
                    platform=Platform.TIKTOK,
                    duration_days=5,
                    total_budget_usd=200.0,
                    min_impressions=3000,
                    target_cpc_usd=1.0,
                    audience_spec={"interests": ["startups", "side hustles"]},
                ),
            ]

        return ProjectExperimentConfig(
            variants_per_platform=2,
            landing_page_variants=2,
            landing_page_provider="vercel",
            base_url_template="https://startupai-{project_id}.vercel.app",
            platform_budgets=platform_budgets,
        )
```

### YAML Configuration Example

```yaml
# config/experiments.yaml
defaults:
  variants_per_platform: 2
  landing_page_variants: 2
  landing_page_provider: "vercel"
  base_url_template: "https://startupai-{project_id}.vercel.app"

segments:
  b2b:
    platforms:
      - platform: linkedin
        duration_days: 7
        total_budget_usd: 400
        min_impressions: 3000
        target_cpc_usd: 5.0
        audience_spec:
          job_titles: ["CTO", "VP Engineering", "Head of Product"]
          company_size: ["50-200", "200-1000"]

      - platform: google_search
        duration_days: 7
        total_budget_usd: 600
        min_impressions: 5000
        target_cpc_usd: 4.0
        audience_spec:
          keywords: ["b2b ecommerce", "b2b saas platform"]

  b2c:
    platforms:
      - platform: meta
        duration_days: 5
        total_budget_usd: 400
        min_impressions: 5000
        target_cpc_usd: 1.5
        audience_spec:
          interests: ["online shopping", "fashion"]

      - platform: tiktok
        duration_days: 5
        total_budget_usd: 200
        min_impressions: 3000
        target_cpc_usd: 1.0
        audience_spec:
          interests: ["startups", "side hustles"]
```

**Usage**: `PulseCrew.kickoff()` calls `ExperimentConfigResolver.resolve_from_vpc(vpc)` to get platform budgets, then passes them to `ExperimentDeployTool.deploy()` for campaign creation.

---

## Innovation Physics - Non-Linear Flow Logic

> **Implementation**: See `src/startupai/flows/internal_validation_flow.py` and `docs/INNOVATION_PHYSICS_README.md`

The validation flow is NOT linear. Evidence signals drive routing decisions that can loop back to earlier phases or pivot strategy. This implements the Strategyzer methodology's "chaotic iteration" pattern.

### State Signals for Routing

The `ValidationState` carries these signals that determine routing:

```python
# From src/startupai/flows/state_schemas.py

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl

# Core lifecycle enums
class Phase(str, Enum):
    IDEATION = "ideation"
    DESIRABILITY = "desirability"
    FEASIBILITY = "feasibility"
    VIABILITY = "viability"
    VALIDATED = "validated"
    KILLED = "killed"

class RiskAxis(str, Enum):
    DESIRABILITY = "desirability"
    FEASIBILITY = "feasibility"
    VIABILITY = "viability"

class ProblemFit(str, Enum):
    UNKNOWN = "unknown"
    NO_FIT = "no_fit"
    PARTIAL_FIT = "partial_fit"
    STRONG_FIT = "strong_fit"

# Signal enums (computed from evidence)
class DesirabilitySignal(str, Enum):
    NO_SIGNAL = "no_signal"
    NO_INTEREST = "no_interest"           # low traffic / low signup
    WEAK_INTEREST = "weak_interest"       # high CTR, low conversion
    STRONG_COMMITMENT = "strong_commitment"  # strong signup/preorder evidence

class FeasibilitySignal(str, Enum):
    UNKNOWN = "unknown"
    GREEN = "green"                       # feasible
    ORANGE_CONSTRAINED = "orange_constrained"  # feasible only w/ scope reduction
    RED_IMPOSSIBLE = "red_impossible"     # infeasible

class ViabilitySignal(str, Enum):
    UNKNOWN = "unknown"
    PROFITABLE = "profitable"             # CAC < LTV
    UNDERWATER = "underwater"             # CAC > LTV
    ZOMBIE_MARKET = "zombie_market"       # CAC<LTV but TAM too small

# Pivot and approval enums
class PivotType(str, Enum):
    NONE = "none"
    SEGMENT_PIVOT = "segment_pivot"
    VALUE_PIVOT = "value_pivot"
    CHANNEL_PIVOT = "channel_pivot"
    PRICE_PIVOT = "price_pivot"
    COST_PIVOT = "cost_pivot"
    KILL = "kill"

class HumanApprovalStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    OVERRIDDEN = "overridden"

class ArtifactApprovalStatus(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"

# Platform enum for experiments
class Platform(str, Enum):
    META = "meta"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"
    GOOGLE_SEARCH = "google_search"
    GOOGLE_DISPLAY = "google_display"

# Legacy enums (to be deprecated in favor of Signal enums)
class EvidenceStrength(str, Enum):
    STRONG = "strong"      # >60% positive + behavioral commitment
    WEAK = "weak"          # 30-60% or verbal only
    NONE = "none"          # <30% or negative

class CommitmentType(str, Enum):
    SKIN_IN_GAME = "skin_in_game"  # Money, time, reputation
    VERBAL = "verbal"              # Only verbal interest
    NONE = "none"

class FeasibilityStatus(str, Enum):
    POSSIBLE = "possible"
    CONSTRAINED = "constrained"  # Degraded version possible
    IMPOSSIBLE = "impossible"

class UnitEconomicsStatus(str, Enum):
    PROFITABLE = "profitable"    # LTV > 3x CAC
    MARGINAL = "marginal"        # LTV = 1-3x CAC
    UNDERWATER = "underwater"    # LTV < CAC

class PivotRecommendation(str, Enum):
    SEGMENT_PIVOT = "segment_pivot"
    VALUE_PIVOT = "value_pivot"
    CHANNEL_PIVOT = "channel_pivot"
    MODEL_PIVOT = "model_pivot"
    FEATURE_PIVOT = "feature_pivot"
    NO_PIVOT = "no_pivot"
    KILL = "kill"
```

### Supporting Artifact Models

These models structure the data produced by each crew:

```python
# Desirability artifacts (Pulse)
class DesirabilityMetrics(BaseModel):
    experiment_id: str
    platform: Platform
    ad_ids: List[str] = []
    landing_page_url: Optional[HttpUrl] = None
    impressions: int = 0
    clicks: int = 0
    signups: int = 0
    spend_usd: float = 0.0
    ctr: float = 0.0              # computed: clicks / impressions
    conversion_rate: float = 0.0  # signups / clicks

class AdVariant(BaseModel):
    id: str
    platform: Platform
    headline: str
    body: str
    cta: str
    asset_url: Optional[HttpUrl] = None
    approval_status: ArtifactApprovalStatus = ArtifactApprovalStatus.DRAFT
    human_approval_status: HumanApprovalStatus = HumanApprovalStatus.NOT_REQUIRED
    human_comment: Optional[str] = None

class LandingPageVariant(BaseModel):
    id: str
    variant_tag: str  # baseline, lite_scope, price_test_A, etc.
    preview_url: Optional[HttpUrl] = None
    deployed_url: Optional[HttpUrl] = None
    hosting_provider: Optional[str] = None  # vercel, netlify, etc.
    route_path: Optional[str] = None        # "/v1", "/v1-lite", etc.
    approval_status: ArtifactApprovalStatus = ArtifactApprovalStatus.DRAFT
    human_approval_status: HumanApprovalStatus = HumanApprovalStatus.NOT_REQUIRED
    human_comment: Optional[str] = None

class PlatformBudgetConfig(BaseModel):
    platform: Platform
    duration_days: int
    total_budget_usd: float
    min_impressions: int
    target_cpc_usd: Optional[float] = None
    audience_spec: Dict[str, Any] = Field(default_factory=dict)

class ExperimentRoutingConfig(BaseModel):
    experiment_id: Optional[str] = None
    platform_campaign_ids: Dict[Platform, List[str]] = Field(default_factory=dict)
    platform_budgets: List[PlatformBudgetConfig] = Field(default_factory=list)

class DesirabilityExperimentRun(BaseModel):
    id: str
    downgrade_active: bool = False
    ad_variants: List[AdVariant] = Field(default_factory=list)
    landing_page_variants: List[LandingPageVariant] = Field(default_factory=list)
    routing: ExperimentRoutingConfig = Field(default_factory=ExperimentRoutingConfig)
    per_platform_metrics: List[DesirabilityMetrics] = Field(default_factory=list)
    aggregate_metrics: Optional[DesirabilityMetrics] = None
    approval_status: ArtifactApprovalStatus = ArtifactApprovalStatus.DRAFT
    guardian_issues: List[str] = Field(default_factory=list)

# Feasibility artifacts (Forge)
class FeasibilityArtifact(BaseModel):
    build_id: str
    mvp_url: Optional[HttpUrl] = None
    api_cost_estimate_monthly_usd: float = 0.0
    infra_cost_estimate_monthly_usd: float = 0.0
    removed_features: List[str] = []
    retained_features: List[str] = []
    technical_complexity_score: int = 0  # 1–10
    notes: Optional[str] = None

# Viability artifacts (Ledger)
class ViabilityMetrics(BaseModel):
    cac_usd: float = 0.0
    ltv_usd: float = 0.0
    gross_margin_pct: float = 0.0
    tam_annual_revenue_potential_usd: float = 0.0
    monthly_churn_pct: float = 0.0
    payback_months: float = 0.0
```

### Crew Result Models

These models define the output of each crew's `kickoff()` method:

```python
# Sage crew outputs
class SageIntakeResult(BaseModel):
    problem_fit: ProblemFit
    segment: str
    value_prop: str
    vpc_document_url: HttpUrl
    bmc_document_url: HttpUrl

# Guardian crew outputs
class GuardianGateResult(BaseModel):
    passed: bool
    issues: List[str] = []

class GuardianCreativeReviewResult(BaseModel):
    ad_variants: List[AdVariant]
    landing_page_variants: List[LandingPageVariant]
    issues: List[str] = []
    hitl_required: bool = False

# Pulse crew outputs
class PulseDesirabilityResult(BaseModel):
    signal: DesirabilitySignal
    experiment_run: DesirabilityExperimentRun

# Forge crew outputs
class ForgeFeasibilityResult(BaseModel):
    feasibility_flag: FeasibilitySignal
    artifact: FeasibilityArtifact

# Ledger crew outputs
class LedgerViabilityResult(BaseModel):
    viability_flag: ViabilitySignal
    metrics: ViabilityMetrics

# Compass crew outputs
class CompassHitlRequest(BaseModel):
    run_id: str
    task_id: str
```

### Complete State Schema

The `StartupValidationState` contains all 31 fields that track the validation flow:

```python
# From src/startupai/flows/state_schemas.py

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from enum import Enum

class StartupValidationState(BaseModel):

    # Identity & bookkeeping
    project_id: str
    iteration: int = 0
    phase: Phase = Phase.IDEATION
    current_risk_axis: RiskAxis = RiskAxis.DESIRABILITY

    # Problem / solution fit (Sage)
    problem_fit: ProblemFit = ProblemFit.UNKNOWN
    current_segment: Optional[str] = None
    current_value_prop: Optional[str] = None
    vpc_document_url: Optional[HttpUrl] = None
    bmc_document_url: Optional[HttpUrl] = None

    # Signals
    desirability_signal: DesirabilitySignal = DesirabilitySignal.NO_SIGNAL
    feasibility_signal: FeasibilitySignal = FeasibilitySignal.UNKNOWN
    viability_signal: ViabilitySignal = ViabilitySignal.UNKNOWN

    # Desirability artifacts & experiments (Pulse)
    desirability_experiments: List[DesirabilityExperimentRun] = Field(
        default_factory=list
    )
    downgrade_active: bool = False  # true if 'lite' / downgraded value prop tests are active

    # Feasibility artifacts (Forge)
    last_feasibility_artifact: Optional[FeasibilityArtifact] = None

    # Viability metrics (Ledger)
    last_viability_metrics: Optional[ViabilityMetrics] = None

    # Pivot + routing state
    last_pivot_type: PivotType = PivotType.NONE
    pending_pivot_type: PivotType = PivotType.NONE

    # Global human approvals
    human_approval_status: HumanApprovalStatus = HumanApprovalStatus.NOT_REQUIRED
    human_comment: Optional[str] = None

    # HITL bookkeeping (both creatives + viability)
    last_human_decision_task_id: Optional[str] = None
    last_human_decision_run_id: Optional[str] = None

    # Guardian / governance metadata
    guardian_last_issues: List[str] = Field(default_factory=list)
    audit_log_ids: List[str] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True
```

**State Fields Breakdown**:

| Field | Type | Purpose | Updated By |
|-------|------|---------|------------|
| `project_id` | str | Links to Supabase projects table | System |
| `iteration` | int | Counts number of pivot loops | Routers |
| `phase` | Phase enum | Current validation phase | Routers |
| `current_risk_axis` | RiskAxis enum | Which risk we're validating | Routers |
| `problem_fit` | ProblemFit enum | Sage's assessment of problem-solution fit | Sage |
| `current_segment` | str | Active customer segment under test | Sage |
| `current_value_prop` | str | Active value proposition | Sage |
| `vpc_document_url` | HttpUrl | Link to VPC artifact | Sage |
| `bmc_document_url` | HttpUrl | Link to BMC artifact | Sage |
| `desirability_signal` | DesirabilitySignal enum | Computed from experiment metrics | Pulse |
| `feasibility_signal` | FeasibilitySignal enum | Technical feasibility assessment | Forge |
| `viability_signal` | ViabilitySignal enum | Unit economics assessment | Ledger |
| `desirability_experiments` | List[DesirabilityExperimentRun] | All experiments run | Pulse |
| `downgrade_active` | bool | Flag indicating "lite" version testing | Forge |
| `last_feasibility_artifact` | FeasibilityArtifact | Build artifacts and constraints | Forge |
| `last_viability_metrics` | ViabilityMetrics | CAC, LTV, margin calculations | Ledger |
| `last_pivot_type` | PivotType enum | Last executed pivot | Routers |
| `pending_pivot_type` | PivotType enum | Pivot awaiting approval | Compass |
| `human_approval_status` | HumanApprovalStatus enum | Current HITL status | Compass |
| `human_comment` | str | User feedback on approval | Compass |
| `last_human_decision_task_id` | str | CrewAI task ID for HITL | Compass |
| `last_human_decision_run_id` | str | CrewAI run ID for HITL | Compass |
| `guardian_last_issues` | List[str] | QA issues found | Guardian |
| `audit_log_ids` | List[str] | Audit trail IDs | Guardian |

### Phase 1 Router: Desirability Gate

**The Problem-Solution Filter:**
- Signal: `problem_resonance < 0.3` (customer doesn't care about the problem)
- Action: Route to `segment_pivot_required`
- Logic: Don't change the solution; change the audience

**The Product-Market Filter:**
- Signal: `problem_resonance >= 0.3` but `zombie_ratio >= 0.7`
- Action: Route to `value_pivot_required`
- Logic: The audience is right (they care about the problem), but the promise is wrong (70%+ interested but not committing = "zombies")

```python
@router(test_desirability)
def desirability_gate(self) -> str:
    evidence = self.state.desirability_evidence
    zombie_ratio = self.state.calculate_zombie_ratio()

    # PROBLEM-SOLUTION FILTER
    if evidence.problem_resonance < 0.3:
        self.state.pivot_recommendation = PivotRecommendation.SEGMENT_PIVOT
        self.state.human_input_required = True
        return "segment_pivot_required"

    # PRODUCT-MARKET FILTER
    elif evidence.problem_resonance >= 0.3 and zombie_ratio >= 0.7:
        self.state.pivot_recommendation = PivotRecommendation.VALUE_PIVOT
        self.state.human_input_required = True
        return "value_pivot_required"

    elif self.state.evidence_strength == EvidenceStrength.STRONG:
        return "proceed_to_feasibility"

    else:
        return "compass_synthesis_required"
```

### Phase 2 Router: Feasibility Gate

**The Downgrade Protocol:**
- Signal: `feasibility_status == IMPOSSIBLE`
- Action: Route to `downgrade_and_retest`
- Logic: Must verify customers still want the product without that feature

```python
@router(test_feasibility)
def feasibility_gate(self) -> str:
    if self.state.feasibility_status == FeasibilityStatus.IMPOSSIBLE:
        self.state.human_input_required = True
        return "downgrade_and_retest"  # Re-test desirability with degraded version

    elif self.state.feasibility_status == FeasibilityStatus.CONSTRAINED:
        return "test_degraded_desirability"

    elif self.state.feasibility_status == FeasibilityStatus.POSSIBLE:
        return "proceed_to_viability"
```

### Phase 3 Router: Viability Gate

**The Unit Economics Trigger:**
- Signal: `unit_economics_status == UNDERWATER` (CAC > LTV)
- Action: Route to `strategic_pivot_required`
- Options: 1) Increase Price (test willingness), 2) Reduce Cost (reduce features)

```python
@router(test_viability)
def viability_gate(self) -> str:
    if self.state.unit_economics_status == UnitEconomicsStatus.UNDERWATER:
        self.state.human_input_required = True
        return "strategic_pivot_required"  # Compass decides: price up or cost down

    elif self.state.unit_economics_status == UnitEconomicsStatus.MARGINAL:
        return "optimize_economics"

    elif self.state.unit_economics_status == UnitEconomicsStatus.PROFITABLE:
        return "validation_complete"
```

### Human-in-the-Loop Integration

When `human_input_required=True`, the flow pauses for strategic decisions. There are two types of HITL workflows:

#### 1. Creative Approval (Desirability Phase)
See **Creative Approval Workflow** section above for full details.

#### 2. Viability Decision (Viability Phase)

When unit economics fail (`CAC > LTV` or `TAM too small`), Compass presents strategic options to the founder:

**Webhook Payload to Product App:**
```json
POST https://app.startupai.site/api/approvals/webhook
{
  "execution_id": "flow_run_456",
  "task_id": "compass_viability_decision",
  "crew_name": "compass",
  "task_name": "request_viability_decision",
  "task_output": {
    "approval_type": "strategic_pivot",
    "title": "Unit Economics Require Strategic Decision",
    "context": {
      "project_id": "proj_789",
      "viability_signal": "underwater",
      "metrics": {
        "cac_usd": 250.00,
        "ltv_usd": 180.00,
        "ltv_cac_ratio": 0.72,
        "gross_margin_pct": 65.0,
        "monthly_churn_pct": 8.0,
        "payback_months": 18.5
      },
      "evidence_summary": "Strong desirability (problem_resonance: 0.72), feasible build, but CAC ($250) > LTV ($180). Options: increase price or reduce cost."
    },
    "options": [
      {
        "action": "price_pivot",
        "label": "Increase Price",
        "description": "Test 2x price point to improve LTV",
        "rationale": "Good problem resonance suggests price elasticity",
        "next_step": "run_desirability_experiments with new pricing"
      },
      {
        "action": "cost_pivot",
        "label": "Reduce Costs",
        "description": "Simplify features to reduce CAC",
        "rationale": "Downgrade non-essential features to lower acquisition costs",
        "next_step": "downgrade_and_retest_desirability"
      },
      {
        "action": "kill",
        "label": "Kill Project",
        "description": "Economics are fundamentally broken",
        "rationale": "No viable path to profitability",
        "next_step": "terminal_killed"
      }
    ]
  }
}
```

**Resume Payload (Founder Decision):**
```json
POST https://startupai-...crewai.com/resume
{
  "execution_id": "flow_run_456",
  "task_id": "compass_viability_decision",
  "human_feedback": "Let's test 2x pricing. The problem resonance is strong enough that customers may pay more.",
  "is_approve": true,
  "selected_option": "price_pivot",
  "modifications": {
    "test_price_multipliers": [1.5, 2.0, 2.5],
    "duration_days": 7
  },
  "humanInputWebhook": {
    "url": "https://app.startupai.site/api/approvals/webhook",
    "authentication": {
      "strategy": "bearer",
      "token": "webhook_secret_xyz"
    }
  }
}
```

**Flow Handling:**
```python
@listen("await_viability_decision")
def await_viability_decision(self):
    """Process human decision from /resume"""
    # Decision is injected into state by /resume handler
    decision = self.state.pending_pivot_type

    if decision == PivotType.PRICE_PIVOT:
        # Update VPC with new pricing
        SageCrew().adjust_pricing(
            project_id=self.state.project_id,
            vpc_url=self.state.vpc_document_url,
            price_multiplier=2.0
        )
        # Re-test desirability with new price
        return "run_desirability_experiments"

    elif decision == PivotType.COST_PIVOT:
        # Trigger feature downgrade
        self.state.downgrade_active = True
        ForgeCrew().apply_downgrade_to_vpc(...)
        return "run_desirability_experiments"

    elif decision == PivotType.KILL:
        self.state.phase = Phase.KILLED
        return "terminal_killed"
```

### Pivot History & Learning

All pivots are tracked for Flywheel learning:

```python
self.state.add_pivot_to_history(
    PivotRecommendation.SEGMENT_PIVOT,
    f"Low problem resonance ({evidence.problem_resonance:.1%})"
)
```

---

## Implementation File Structure

```
src/startupai/
├── flows/
│   ├── __init__.py
│   ├── internal_validation_flow.py    # Combined flow
│   └── state_schemas.py               # Pydantic models
│
├── crews/
│   ├── service/
│   │   ├── config/
│   │   │   ├── agents.yaml
│   │   │   └── tasks.yaml
│   │   └── service_crew.py
│   │
│   ├── analysis/
│   │   ├── config/
│   │   │   ├── agents.yaml
│   │   │   └── tasks.yaml
│   │   └── analysis_crew.py
│   │
│   ├── governance/
│   │   ├── config/
│   │   │   ├── agents.yaml
│   │   │   └── tasks.yaml
│   │   └── governance_crew.py
│   │
│   ├── build/
│   │   ├── config/
│   │   │   ├── agents.yaml
│   │   │   └── tasks.yaml
│   │   └── build_crew.py
│   │
│   ├── growth/
│   │   ├── config/
│   │   │   ├── agents.yaml
│   │   │   └── tasks.yaml
│   │   └── growth_crew.py
│   │
│   ├── synthesis/
│   │   ├── config/
│   │   │   ├── agents.yaml
│   │   │   └── tasks.yaml
│   │   └── synthesis_crew.py
│   │
│   └── finance/
│       ├── config/
│       │   ├── agents.yaml
│       │   └── tasks.yaml
│       └── finance_crew.py
│
├── tools/
│   ├── web_search.py
│   ├── analytics.py
│   └── report_generator.py
│
└── knowledge/
    └── flywheel_learnings.json
```

---

## Extended Architecture Documentation

The following sections have been extracted into focused reference documents:

- **[Marketing Site AI Integration](./reference/marketing-integration.md)** - Chat widgets, live data, founder-specific conversations
- **[Product App Smart Artifacts](./reference/product-artifacts.md)** - Canvas architecture, approval checkpoints, framework wiring
- **[Database Schemas](./reference/database-schemas.md)** - SQL definitions for all tables

---

## CrewAI AMP Configuration

### Overview

The validation system deploys to CrewAI AMP (Agentic Management Platform) with the following configuration structure:

```
startupai-crew/
├── src/startupai/
│   ├── flows/
│   │   ├── internal_validation_flow.py  # StartupValidationFlow class
│   │   └── state_schemas.py             # All Pydantic models
│   ├── crews/
│   │   ├── sage/
│   │   │   ├── config/
│   │   │   │   ├── agents.yaml  # Sage's 3 agents
│   │   │   │   └── tasks.yaml   # Sage's tasks
│   │   │   └── sage_crew.py     # SageCrew implementation
│   │   ├── pulse/              # Similar structure
│   │   ├── forge/
│   │   ├── ledger/
│   │   ├── guardian/
│   │   └── compass/
│   └── tools/                   # Custom tool implementations
├── pyproject.toml              # Dependencies
└── crewai_config.yaml          # AMP deployment config
```

### Key Configuration Files

**`crewai_config.yaml`** (Deployment Settings):
```yaml
deployment:
  uuid: "b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b"
  flow_entry_point: "src.startupai.flows.internal_validation_flow.StartupValidationFlow"

environment_variables:
  - OPENAI_API_KEY  # Set in CrewAI dashboard, NOT in .env

webhooks:
  human_input:
    enabled: true
    default_url: "https://app.startupai.site/api/approvals/webhook"
```

**`agents.yaml`** Example (Pulse Crew):
```yaml
# src/startupai/crews/pulse/config/agents.yaml
pulse_ad_creative_agent:
  role: "Ad Creative Specialist"
  goal: "Generate compelling ad variants for multi-platform testing"
  backstory: "Expert in direct response copywriting with deep understanding of platform-specific best practices"
  tools:
    - copywriting_tool
    - image_generation_tool
  memory: true
  external_memory: supabase_pgvector

pulse_analytics_agent:
  role: "Analytics & Signal Computation"
  goal: "Collect metrics and compute Innovation Physics signals"
  backstory: "Data analyst specializing in startup validation metrics and evidence-based decision making"
  tools:
    - analytics_tool
    - experiment_deploy_tool
  memory: true
  human_input: false
```

**`tasks.yaml`** Example (Pulse Crew):
```yaml
# src/startupai/crews/pulse/config/tasks.yaml
generate_ad_variants:
  description: "Generate {variants_per_platform} ad variants per platform based on VPC"
  expected_output: "List of AdVariant objects with headline, body, CTA"
  agent: pulse_ad_creative_agent
  context:
    - vpc_url
    - variant_tag

collect_desirability_metrics:
  description: "Collect experiment metrics from all platforms and compute desirability signal"
  expected_output: "DesirabilitySignal enum with supporting metrics"
  agent: pulse_analytics_agent
  context:
    - experiment_id
    - platform_budgets
```

### Agent → Tool Mapping

| Crew | Agent | Tools | HITL Enabled |
|------|-------|-------|--------------|
| **Sage** | FounderOnboardingAgent | BriefParserTool, LearningRetrievalTool | No |
| **Sage** | CustomerResearchAgent | WebSearchTool, ComparisonMatrixTool | No |
| **Sage** | ValueDesignerAgent | CanvasBuilderTool, LearningRetrievalTool | No |
| **Pulse** | AdCreativeAgent | CopywritingTool, ImageGenerationTool | No |
| **Pulse** | CommsAgent | CopywritingTool, TemplateEngineTool | No |
| **Pulse** | AnalyticsAgent | ExperimentDeployTool, AnalyticsTool | No |
| **Forge** | UXUIDesignerAgent | ComponentLibraryScraper, CanvasBuilderTool | No |
| **Forge** | FrontendDevAgent | FileReadTool, FileWriteTool, LandingPageDeploymentTool | No |
| **Forge** | BackendDevAgent | TechStackValidator, APIIntegrationTool | No |
| **Ledger** | FinancialControllerAgent | PythonREPLTool, CostTrackingTool | No |
| **Ledger** | LegalComplianceAgent | RegulatorySearchTool | No |
| **Ledger** | EconomicsReviewerAgent | LearningCaptureTool, PythonREPLTool | No |
| **Guardian** | QAAgent | MethodologyCheckTool, GuardianReviewTool | Yes (blocks gates) |
| **Guardian** | SecurityAgent | PrivacyGuardTool, AnonymizerTool | No |
| **Guardian** | AuditAgent | LearningCaptureTool, FileWriteTool | No |
| **Compass** | ProductPMAgent | StateInspectionTool, SynthesisTool | No |
| **Compass** | HumanApprovalAgent | ApprovalRequestTool | Yes (HITL workflows) |
| **Compass** | RoadmapWriterAgent | LearningCaptureTool, FileWriteTool | No |

### Memory & External Storage

- **Agent Memory**: Enabled (`memory: true`) for all agents except SecurityAgent
- **External Memory**: `supabase_pgvector` for agents that contribute to Flywheel learning:
  - Sage agents (VPC patterns, customer insights)
  - Pulse AnalyticsAgent (experiment patterns)
  - Ledger EconomicsReviewerAgent (unit economics patterns)
  - Guardian AuditAgent (methodology improvements)
  - Compass RoadmapWriterAgent (pivot decisions)

### Deployment Commands

```bash
# Authenticate (one-time per machine)
crewai login

# Test locally (requires OPENAI_API_KEY in .env)
crewai run

# Deploy to AMP
crewai deploy push --uuid b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b

# Monitor deployment
crewai deploy logs --uuid b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b
crewai deploy status --uuid b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b
```

> **Note**: Environment variables must be set in the CrewAI AMP dashboard, not in `.env` files. The `.env` file is only used for local development.

---

## Development Sequence

### Immediate Next Steps (Phase 1)

1. **Create state schemas** (`state_schemas.py`)
   - StartupAIBrief
   - CustomerProfile
   - CompetitorAnalysis
   - QAReport

2. **Build Service Crew**
   - agents.yaml with Internal Onboarding Agent
   - tasks.yaml with brief capture task
   - service_crew.py

3. **Build Analysis Crew**
   - agents.yaml with Customer Researcher, Competitor Analyst
   - tasks.yaml with research tasks
   - analysis_crew.py

4. **Build Governance Crew (Phase 1)**
   - agents.yaml with QA Agent
   - tasks.yaml with validation task
   - governance_crew.py

5. **Create Phase 1 Flow**
   - internal_validation_flow.py
   - Wire up crews with @listen and @router

6. **Run StartupAI through Phase 1**
   - Execute flow with our own business context
   - Capture VPC for Founders and Consultants
   - Iterate until Guardian QA passes

### Dependencies

- CrewAI 1.2.1+ (installed)
- OpenAI API key (for LLM)
- Pydantic for state schemas

---

## Success Metrics

### Phase 1
- VPC completeness score (Guardian QA)
- Assumption clarity score
- Time to complete analysis

### Phase 2
- Experiments run per assumption
- Evidence quality score
- Pivot/proceed confidence level

### Phase 3
- Unit economics viability
- Audit compliance score
- Flywheel entries captured

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| 18 agents too complex | Start with core agents, expand later |
| LLM costs high | Use efficient models, cache results |
| Quality inconsistent | Guardian gates at each phase |
| Learnings not captured | Structured flywheel entry format |

---

## State Persistence & Error Recovery

### State Persistence with @persist

Use the `@persist` decorator to save flow state after critical methods:

```python
from crewai.flow.flow import Flow, persist

class Phase1Flow(Flow[InternalValidationState]):

    @start()
    @persist()  # Save state after brief capture
    def capture_startupai_brief(self):
        ...

    @listen(analyze_competitors)
    @persist()  # Save before governance review
    def governance_review(self):
        ...
```

**Storage Options**:
- Default: SQLite file (local development)
- Production: Configure for Supabase persistence

**Recovery**: On restart, flow resumes from last persisted state.

### Error Recovery Patterns

```python
@router(governance_review)
def qa_gate(self):
    if self.state.qa_status == "passed":
        return "approved"
    elif self.state.retry_count < 3:
        self.state.retry_count += 1
        return "needs_revision"  # Loop back with feedback
    else:
        return "manual_review"   # Escalate to human

@listen("manual_review")
def escalate_to_human(self):
    """Notify product app for human intervention"""
    # Emit webhook event for HITL
    self.emit_event("approval_needed", {
        "type": "qa_escalation",
        "state": self.state.dict()
    })
```

**See also**: [reference/amp-configuration.md](./reference/amp-configuration.md) for platform error handling.

---

## Flywheel Learning Integration

The Flywheel Learning System captures patterns, outcomes, and domain expertise from each validation run. This is StartupAI's competitive moat.

### Learning Capture Points

After each phase completion, capture learnings:

```python
@listen("approved")
def capture_phase_learnings(self):
    """After Guardian approves, capture learnings"""
    from startupai.tools.learning_capture import LearningCaptureTool

    learnings = self.extract_learnings_from_state()
    for learning in learnings:
        LearningCaptureTool()._run(
            learning_type=learning['type'],
            title=learning['title'],
            description=learning['description'],
            context=self.state.brief.get_abstract_context(),
            founder=learning['founder'],
            phase=self.state.current_phase
        )
```

### Learning Retrieval in Tasks

Agents query the learning database before analysis:

```yaml
customer_research_task:
  description: |
    First, query the learning database for relevant patterns:
    - Use retrieve_learnings tool
    - query: "Customer research patterns for {industry}"
    - founder: "sage"

    Use these learnings to inform your research approach.
    Then conduct customer research for the {segment} segment...
```

**Full specification**: [reference/flywheel-learning.md](./reference/flywheel-learning.md)

---

## References

- [02-organization.md](./02-organization.md) - Organizational structure (single source)
- [01-ecosystem.md](./01-ecosystem.md) - Three-service architecture
- [reference/flywheel-learning.md](./reference/flywheel-learning.md) - **Competitive moat learning system**
- [reference/amp-configuration.md](./reference/amp-configuration.md) - CrewAI AMP platform config
- [reference/approval-workflows.md](./reference/approval-workflows.md) - HITL patterns
- [reference/product-artifacts.md](./reference/product-artifacts.md) - Smart canvas architecture
- [reference/marketing-integration.md](./reference/marketing-integration.md) - Marketing site AI
- [reference/database-schemas.md](./reference/database-schemas.md) - SQL schemas
- CrewAI Flows documentation
- Value Proposition Design (Osterwalder)
- Testing Business Ideas (Bland)

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-11-21 | Initial spec created | Claude + Chris |
| 2025-11-21 | Added Marketing Site AI Integration section | Claude + Chris |
| 2025-11-21 | Added Product App Smart Artifact Architecture section | Claude + Chris |
| 2025-11-21 | Expanded to 6 approval checkpoints with full workflow architecture | Claude + Chris |
| 2025-11-21 | Added CrewAI implementation patterns for HITL approvals | Claude + Chris |
| 2025-11-21 | Split into focused docs: marketing-integration, product-artifacts, database-schemas | Claude + Chris |

---

**Next Session Pickup Point**: Begin implementing Phase 1 state schemas and Service Crew.
