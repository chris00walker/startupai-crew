---
purpose: Repository introduction, architecture overview, and quick start
status: active
last_reviewed: 2026-01-07
vpd_compliance: true
---

# StartupAI Crew - Introduction & Architecture

## Overview

**VPD-compliant validation engine for delivering Fortune 500-quality strategic analysis**

This repository contains the brain of the StartupAI ecosystem - a multi-phase crew orchestration system that powers the AI Founders team. It implements the **Value Proposition Design (VPD)** framework by Osterwalder & Pigneur using CrewAI Flows to deliver Problem-Solution Fit, Desirability, Feasibility, and Viability validation.

> **VPD Framework Compliance**: This system implements patterns from *Value Proposition Design*, *Testing Business Ideas*, and *Business Model Generation*. See [03-methodology.md](./03-methodology.md) for VPD framework reference and phase documents (04-08) for detailed implementation.

## Design Principles

### 1. Service/Commercial Model
Organized around the customer, not a linear pipeline:
- **Service Side**: Customer intake and brief capture
- **Commercial Side**: Value delivery through analysis and validation
- **Compass**: Balances competing interests, synthesizes evidence
- **Guardian**: Governance oversight across all functions

### 2. Gated Validation
Validation follows the Strategyzer methodology with four gates:
```
VALUE PROPOSITION DESIGN → [Test Cycles] → VPC GATE → [Test Cycles] → DESIRABILITY GATE → [Test Cycles] → FEASIBILITY GATE → [Test Cycles] → VIABILITY GATE
```

**Key principles:**
- **VPD comes first**: You must design and validate the Value Proposition Canvas (Customer Profile + Value Map) before testing desirability. There's no point asking "do they want it?" until you've validated you're targeting the correct customer segment.
- **Test cycles at every stage**: Each phase requires iterative testing. VPD itself requires cycles to achieve Problem-Solution Fit (fit score ≥ 70).
- **Non-linear with pivots**: This is NOT a straight linear process. At any point, a critical failure in Testing Business Ideas can force a pivot (SEGMENT_PIVOT, VALUE_PIVOT, FEATURE_PIVOT, PRICE_PIVOT, COST_PIVOT, MODEL_PIVOT) that loops back to an earlier phase.
- **Gates are checkpoints**: Each gate (`approve_vpc_completion`, `approve_desirability_gate`, `approve_feasibility_gate`, `approve_viability_gate`) requires evidence-based validation before proceeding.

### 3. Flows + Crews Architecture
- **Crews**: Autonomous agent teams that collaborate on tasks
- **Flows**: Event-driven orchestration that coordinates crews
- **Routers**: Implement governance gates with conditional routing
- **Structured State**: Pydantic models carry data through the system

## Ecosystem Position

```
┌─────────────────────┐
│   AI Founders Core  │
│   (startupai-crew)  │  ← THIS REPOSITORY
│  CrewAI Flows Engine│
└──────────┬──────────┘
           │
┌──────────┼──────────────┐
│          │              │
▼          │              ▼
┌──────────────┐   │    ┌──────────────┐
│startupai.site│   │    │app.startupai │
│  Marketing   │   │    │   .site      │
│  (Netlify)   │   │    │  (Netlify)   │
└──────────────┘   │    └──────────────┘
                   │
                   ▼
           ┌─────────────┐
           │  Supabase   │
           │   Shared DB │
           └─────────────┘
```

## The 6 AI Founders

> **Single Source**: See [02-organization.md](./02-organization.md) for complete founder details, responsibilities, and organizational structure.

| Founder | Title | Primary Domain |
|---------|-------|----------------|
| **Sage** | CSO | Strategy, VPC design, owns Service Side |
| **Forge** | CTO | Build, technical feasibility |
| **Pulse** | CMO | Marketing, market signals, desirability evidence |
| **Compass** | CPO | Balance, synthesis, pivot/proceed |
| **Guardian** | CGO | Governance, accountability, oversight |
| **Ledger** | CFO | Finance, viability, compliance |

## Phase-Based Architecture

> **Single Source**: See [02-organization.md](./02-organization.md) for complete agent details and [04-phase-0-onboarding.md](./04-phase-0-onboarding.md) / [05-phase-1-vpc-discovery.md](./05-phase-1-vpc-discovery.md) for Phase 0-1 implementation.

### Phase 0: Onboarding (Founder's Brief)

**Purpose**: Capture business hypothesis and create Founder's Brief

| Crew | Agents | Output |
|------|--------|--------|
| Interview Crew | O1 (Founder Interview Agent) | Structured interview responses |
| QA Crew | G1, G2 (Concept Validator, Intent Verifier) | Legitimacy + intent validation |
| Brief Compilation Crew | S1 (Brief Compiler) | **Founder's Brief** |

**HITL**: `approve_founders_brief` - Founder approves brief before Phase 1

### Phase 1: VPC Discovery (Customer Profile + Value Map)

**Purpose**: Discover customer reality and design value using VPD framework

| Flow | Agents | Output |
|------|--------|--------|
| Segment Discovery | E1, D1, D2, D3, D4 | Validated customer segment |
| Jobs Discovery | J1, J2 | Ranked Jobs-to-be-Done |
| Pains Discovery | P1, P2 | Ranked customer pains |
| Gains Discovery | G1, G2 | Ranked customer gains |
| Value Map Design | V1, V2, V3 | Products, Pain Relievers, Gain Creators |
| Willingness to Pay | W1, W2 | WTP validation |
| Fit Assessment | F1, F2 | **Validated VPC** (fit score ≥ 70) |

**HITL**: `approve_experiment_plan`, `approve_pricing_test`, `approve_vpc_completion`

### Phase 2: Desirability + Feasibility Validation

**Purpose**: Build testable artifacts and validate with real customers

| Crew | Agents | Output |
|------|--------|--------|
| Build Crew (Forge) | UX/UI Designer, Frontend Dev, Backend Dev | Testable artifacts |
| Growth Crew (Pulse) | Ad Creative, Communications, Social Analyst | Desirability evidence |
| Synthesis Crew (Compass) | Project Manager | Evidence synthesis |
| Governance Crew (Guardian) | QA Agent | Phase gate validation |

### Phase 3: Viability + Final Decision

**Purpose**: Validate business model economics and make final recommendation

| Crew | Agents | Output |
|------|--------|--------|
| Finance Crew (Ledger) | Financial Controller, Legal & Compliance | Viability assessment |
| Enhanced Governance (Guardian) | Audit Agent, Security Agent, QA Agent | Audit report |
| Decision Crew (Compass) | Decision Agents | Final pivot/proceed recommendation |

## CrewAI Flows Implementation

### Flow State Management

The ValidationState carries **Innovation Physics signals** for evidence-driven routing:

```python
from crewai.flow.flow import Flow, start, listen, router
from pydantic import BaseModel
from enum import Enum

# Innovation Physics Signals
class EvidenceStrength(str, Enum):
    STRONG = "strong"      # >60% positive + behavioral commitment
    WEAK = "weak"          # 30-60% or verbal only
    NONE = "none"          # <30% or negative

class PivotRecommendation(str, Enum):
    SEGMENT_PIVOT = "segment_pivot"    # Change customer segment
    VALUE_PIVOT = "value_pivot"        # Change value proposition
    FEATURE_PIVOT = "feature_pivot"    # Downgrade features
    NO_PIVOT = "no_pivot"

class ValidationState(BaseModel):
    id: str
    business_idea: str
    # Evidence signals for routing
    evidence_strength: EvidenceStrength = EvidenceStrength.NONE
    pivot_recommendation: PivotRecommendation = PivotRecommendation.NO_PIVOT
    human_input_required: bool = False
    # Customer analysis
    customer_profiles: Dict[str, CustomerProfile] = {}
    desirability_evidence: Optional[DesirabilityEvidence] = None
```

> **Full Implementation**: See `src/startupai/flows/state_schemas.py`

### VPD Flow Example (Phase 0-1)

The flow implements **VPD framework patterns** with evidence-driven routing:

```python
class OnboardingFlow(Flow[OnboardingState]):
    """Phase 0: Capture Founder's Brief"""

    @start()
    def conduct_founder_interview(self):
        """O1 Agent: 7-area discovery interview"""
        result = InterviewCrew().crew().kickoff(inputs={...})
        self.state.interview_responses = result.pydantic

    @listen(conduct_founder_interview)
    def validate_concept(self):
        """G1 Agent: Legitimacy screening"""
        result = QACrew().crew().kickoff(inputs={...})
        self.state.qa_status = result.pydantic

    @listen(validate_concept)
    def compile_founders_brief(self):
        """S1 Agent: Synthesize Founder's Brief"""
        result = BriefCompilationCrew().crew().kickoff(inputs={...})
        self.state.founders_brief = result.pydantic
        # HITL: approve_founders_brief


class VPCDiscoveryFlow(Flow[VPCState]):
    """Phase 1: Discover Customer Profile + Design Value Map"""

    @start()
    def design_experiments(self):
        """E1 Agent: Assumptions Mapping → Test Cards"""
        # Prioritize assumptions by importance × evidence weakness
        pass

    @listen(design_experiments)
    def run_discovery(self):
        """D1-D4 Agents: Multi-source evidence collection"""
        # D1: Customer interviews (SAY)
        # D2: Observation (DO - indirect)
        # D3: CTA tests (DO - direct)
        # D4: Evidence triangulation
        pass

    @router(run_discovery)
    def fit_assessment(self) -> str:
        """F1 Agent: Score Problem-Solution Fit"""
        if self.state.fit_score >= 70:
            return "vpc_complete"  # approve_vpc_completion HITL
        elif self.state.fit_score < 40:
            return "segment_pivot"  # Wrong customer
        else:
            return "iterate"  # Refine value map
```

> **Full Implementation**: See [04-phase-0-onboarding.md](./04-phase-0-onboarding.md) and [05-phase-1-vpc-discovery.md](./05-phase-1-vpc-discovery.md) for complete flow specifications

## File Structure

```
src/startupai/
├── flows/
│   ├── __init__.py
│   ├── founder_validation_flow.py
│   └── state_schemas.py
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
│   │   └── ...
│   │
│   ├── build/
│   │   └── ...
│   │
│   ├── growth/
│   │   └── ...
│   │
│   ├── synthesis/
│   │   └── ...
│   │
│   └── finance/
│       └── ...
│
├── tools/
│   ├── web_search.py
│   ├── analytics.py
│   └── report_generator.py
│
└── knowledge/
    └── flywheel_learnings.json
```

## Inputs

```json
{
  "founder_input": "Initial business idea description for Phase 0 interview"
}
```

> **Note**: Phase 0 conducts a structured 7-area interview. The `founder_input` seeds the interview but comprehensive context is gathered through dialogue.

## Outputs

Structured deliverables per phase:

### Phase 0 (Onboarding)
- **Founder's Brief** (structured hypothesis capture):
  - The Idea (concept, one-liner)
  - Problem Hypothesis (who, what, alternatives)
  - Customer Hypothesis (segment, characteristics)
  - Solution Hypothesis (approach, features)
  - Key Assumptions (ranked by risk)
  - Success Criteria (founder-defined validation goals)
- QA Report (concept legitimacy + intent verification)

### Phase 1 (VPC Discovery)
- **Validated Value Proposition Canvas**:
  - Customer Profile (Jobs, Pains, Gains - ranked and evidence-backed)
  - Value Map (Products, Pain Relievers, Gain Creators)
- Test Cards (experiment designs with pass/fail criteria)
- Learning Cards (experiment results with implications)
- Fit Score (≥ 70 for Phase 1 exit)
- Evidence Summary (SAY vs DO triangulation)

### Phase 2 (Desirability + Feasibility)
- Test Artifacts (landing pages, ads, prototypes)
- Evidence Report (desirability signals collected)
- Feasibility Assessment (technical constraints, resource requirements)
- Pivot/Proceed Recommendation

### Phase 3 (Viability)
- Viability Model (unit economics: CAC, LTV, margins)
- Business Model Canvas (populated with validated assumptions)
- Audit Trail
- Flywheel Entry (methodology improvements for future validations)

## Deployment

### Current Deployment
- **UUID**: `6b1e5c4d-e708-4921-be55-08fcb0d1e94b`
- **URL**: `https://startupai-6b1e5c4d-e708-4921-be55-08fcb0d1e-922bcddb.crewai.com`
- **Platform**: CrewAI AMP

### Commands

```bash
# Install dependencies
uv sync

# Run locally
crewai run

# Deploy
crewai deploy push --uuid 6b1e5c4d-e708-4921-be55-08fcb0d1e94b

# Check status
crewai deploy status --uuid 6b1e5c4d-e708-4921-be55-08fcb0d1e94b

# View logs
crewai deploy logs --uuid 6b1e5c4d-e708-4921-be55-08fcb0d1e94b
```

## API Endpoints

> **Full Specification**: See [reference/api-contracts.md](./reference/api-contracts.md) for complete API documentation.

```bash
# Get inputs schema
curl https://startupai-...crewai.com/inputs \
  -H "Authorization: Bearer TOKEN"

# Kickoff workflow
curl -X POST https://startupai-...crewai.com/kickoff \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entrepreneur_input": "Business idea..."}'

# Check status
curl https://startupai-...crewai.com/status/{kickoff_id} \
  -H "Authorization: Bearer TOKEN"
```

## Development Sequence

### Immediate (Phase 1)
1. Create state schemas (`state_schemas.py`)
2. Build Service Crew (agents.yaml, tasks.yaml, service_crew.py)
3. Build Analysis Crew
4. Build Governance Crew (Phase 1)
5. Create Phase 1 Flow
6. Test with StartupAI's own business context

### Next (Phase 2)
1. Build Crew, Growth Crew, Synthesis Crew
2. Add pivot/proceed router logic
3. Implement evidence synthesis

### Future (Phase 3)
1. Finance Crew
2. Enhanced Governance Crew
3. Flywheel learning capture

## Related Documentation

- **Ecosystem Overview**: [01-ecosystem.md](./01-ecosystem.md)
- **Organizational Structure**: [02-organization.md](./02-organization.md) (single source for founders/agents)
- **VPD Methodology**: [03-methodology.md](./03-methodology.md) (framework reference, Strategyzer mapping)
- **Phase 0 (Onboarding)**: [04-phase-0-onboarding.md](./04-phase-0-onboarding.md)
- **Phase 1 (VPC Discovery)**: [05-phase-1-vpc-discovery.md](./05-phase-1-vpc-discovery.md)
- **Phase 2 (Desirability)**: [06-phase-2-desirability.md](./06-phase-2-desirability.md)
- **Phase 3 (Feasibility)**: [07-phase-3-feasibility.md](./07-phase-3-feasibility.md)
- **Phase 4 (Viability)**: [08-phase-4-viability.md](./08-phase-4-viability.md)
- **Current Status**: [09-status.md](./09-status.md)
- **API Contracts**: [reference/api-contracts.md](./reference/api-contracts.md)
- **Approval Workflows**: [reference/approval-workflows.md](./reference/approval-workflows.md)

## Support

- CrewAI Docs: https://docs.crewai.com
- CrewAI Dashboard: https://app.crewai.com
- GitHub Issues: https://github.com/chris00walker/startupai-crew/issues

---

**Status**: Multi-phase architecture with VPD framework compliance
**Last Updated**: 2026-01-07
