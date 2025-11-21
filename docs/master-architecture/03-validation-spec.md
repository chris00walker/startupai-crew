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

### Phase 1 Flow Structure

```python
from crewai.flow.flow import Flow, start, listen, router
from pydantic import BaseModel

class InternalValidationState(BaseModel):
    id: str
    brief: StartupAIBrief
    founder_profile: CustomerProfile = None
    consultant_profile: CustomerProfile = None
    competitor_analysis: CompetitorReport = None
    qa_status: str = "pending"
    qa_feedback: str = ""

class Phase1Flow(Flow[InternalValidationState]):

    @start()
    def capture_startupai_brief(self):
        """Onboard StartupAI as our own client"""
        result = ServiceCrew().crew().kickoff(
            inputs={"context": "StartupAI internal validation"}
        )
        self.state.brief = result.pydantic

    @listen(capture_startupai_brief)
    def analyze_founder_segment(self):
        """Customer research for Founders"""
        result = AnalysisCrew().crew().kickoff(
            inputs={
                "segment": "Founders",
                "brief": self.state.brief.dict()
            }
        )
        self.state.founder_profile = result.pydantic

    @listen(capture_startupai_brief)
    def analyze_consultant_segment(self):
        """Customer research for Consultants"""
        result = AnalysisCrew().crew().kickoff(
            inputs={
                "segment": "Consultants",
                "brief": self.state.brief.dict()
            }
        )
        self.state.consultant_profile = result.pydantic

    @listen(analyze_founder_segment, analyze_consultant_segment)
    def analyze_competitors(self):
        """Competitive landscape analysis"""
        result = AnalysisCrew().crew().kickoff(
            inputs={
                "task": "competitor_analysis",
                "brief": self.state.brief.dict()
            }
        )
        self.state.competitor_analysis = result.pydantic

    @listen(analyze_competitors)
    def governance_review(self):
        """Guardian QA gate"""
        result = GovernanceCrew().crew().kickoff(
            inputs={
                "brief": self.state.brief.dict(),
                "founder_profile": self.state.founder_profile.dict(),
                "consultant_profile": self.state.consultant_profile.dict(),
                "competitor_analysis": self.state.competitor_analysis.dict()
            }
        )
        self.state.qa_status = result.status
        self.state.qa_feedback = result.feedback

    @router(governance_review)
    def qa_gate(self):
        if self.state.qa_status == "passed":
            return "approved"
        return "needs_revision"

    @listen("needs_revision")
    def revise_analysis(self):
        """Loop back with QA feedback"""
        # Re-run analysis with feedback
        pass

    @listen("approved")
    def output_phase1_deliverables(self):
        """Compile Phase 1 outputs"""
        return {
            "vpc_founders": self.state.founder_profile,
            "vpc_consultants": self.state.consultant_profile,
            "competitor_map": self.state.competitor_analysis,
            "assumptions_to_test": self.state.brief.key_assumptions
        }
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

```python
class Phase2Flow(Flow[InternalValidationState]):

    @listen("approved")  # From Phase 1
    def design_experiments(self):
        """Design desirability experiments"""
        result = SynthesisCrew().crew().kickoff(
            inputs={
                "task": "experiment_design",
                "assumptions": self.state.brief.key_assumptions,
                "segments": ["Founders", "Consultants"]
            }
        )
        self.state.experiment_designs = result.pydantic

    @listen(design_experiments)
    def build_test_artifacts(self):
        """Forge builds MVPs for testing"""
        result = BuildCrew().crew().kickoff(
            inputs={
                "experiments": self.state.experiment_designs,
                "segments": ["Founders", "Consultants"]
            }
        )
        self.state.artifacts = result.pydantic

    @listen(build_test_artifacts)
    def run_growth_experiments(self):
        """Pulse runs desirability tests"""
        result = GrowthCrew().crew().kickoff(
            inputs={
                "artifacts": self.state.artifacts,
                "experiments": self.state.experiment_designs,
                "budget": "$450-525 per segment"
            }
        )
        self.state.evidence = result.pydantic

    @listen(run_growth_experiments)
    def synthesize_evidence(self):
        """Compass synthesizes and recommends"""
        result = SynthesisCrew().crew().kickoff(
            inputs={
                "task": "evidence_synthesis",
                "evidence": self.state.evidence,
                "assumptions": self.state.brief.key_assumptions
            }
        )
        self.state.synthesis = result.pydantic
        self.state.recommendation = result.recommendation

    @router(synthesize_evidence)
    def pivot_proceed_gate(self):
        if self.state.recommendation == "proceed":
            return "proceed_to_feasibility"
        elif self.state.recommendation == "pivot":
            return "pivot_and_retry"
        return "need_more_evidence"

    @listen("pivot_and_retry")
    def design_pivot(self):
        """Redesign VPC based on evidence and retry"""
        # Loop back to Phase 1 with pivot insights
        pass

    @listen("proceed_to_feasibility")
    def output_phase2_deliverables(self):
        """Compile Phase 2 outputs"""
        return {
            "evidence_report": self.state.evidence,
            "synthesis": self.state.synthesis,
            "recommendation": self.state.recommendation,
            "validated_assumptions": [...],
            "invalidated_assumptions": [...]
        }
```

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

```python
class Phase3Flow(Flow[InternalValidationState]):

    @listen("proceed_to_feasibility")  # From Phase 2
    def feasibility_assessment(self):
        """Can we build what we're promising?"""
        result = BuildCrew().crew().kickoff(
            inputs={
                "task": "feasibility_assessment",
                "validated_vp": self.state.synthesis.validated_value_prop
            }
        )
        self.state.feasibility = result.pydantic

    @listen(feasibility_assessment)
    def viability_analysis(self):
        """Can we make money doing this?"""
        result = FinanceCrew().crew().kickoff(
            inputs={
                "costs": self.state.actual_costs,
                "pricing": self.state.pricing_tests,
                "market_size": self.state.market_analysis
            }
        )
        self.state.viability = result.pydantic

    @listen(viability_analysis)
    def final_governance_audit(self):
        """Guardian's comprehensive review"""
        result = GovernanceCrew().crew().kickoff(
            inputs={
                "task": "final_audit",
                "full_state": self.state.dict()
            }
        )
        self.state.audit_report = result.pydantic

    @router(final_governance_audit)
    def guardian_final_gate(self):
        if self.state.audit_report.passed:
            return "validated"
        return "remediation_needed"

    @listen("validated")
    def capture_flywheel_learnings(self):
        """Record learnings for methodology improvement"""
        # Store in persistent knowledge base
        self.state.flywheel_entry = {
            "cycle_id": self.state.id,
            "assumptions_tested": [...],
            "evidence_patterns": [...],
            "methodology_improvements": [...],
            "timestamp": datetime.now()
        }
        return self.state
```

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

## References

- [02-organization.md](./02-organization.md) - Organizational structure (single source)
- [01-ecosystem.md](./01-ecosystem.md) - Three-service architecture
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
