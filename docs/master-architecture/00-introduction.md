---
purpose: Repository introduction, architecture overview, and quick start
status: active
last_reviewed: 2025-11-21
---

# StartupAI Crew - Introduction & Architecture

## Overview

**CrewAI Flows-based validation engine for delivering Fortune 500-quality strategic analysis**

This repository contains the brain of the StartupAI ecosystem - a multi-crew orchestration system that powers the AI Founders team. It implements 8 specialized crews with 18 specialist agents, coordinated through CrewAI Flows to deliver desirability, feasibility, and viability validation.

## Design Principles

### 1. Service/Commercial Model
Organized around the customer, not a linear pipeline:
- **Service Side**: Customer intake and brief capture
- **Commercial Side**: Value delivery through analysis and validation
- **Compass**: Balances competing interests, synthesizes evidence
- **Guardian**: Governance oversight across all functions

### 2. Gated Validation
Validation is sequential, not parallel:
```
[Test Cycles] → DESIRABILITY GATE → [Test Cycles] → FEASIBILITY GATE → [Test Cycles] → VIABILITY GATE
```

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
| **Pulse** | CGrO | Growth, market signals, desirability evidence |
| **Compass** | CPO | Balance, synthesis, pivot/proceed |
| **Guardian** | CGoO | Governance, accountability, oversight |
| **Ledger** | CFO | Finance, viability, compliance |

## 8 Crews Architecture

> **Single Source**: See [02-organization.md](./02-organization.md) for complete agent details per crew.

### Phase 1: Service Side + Desirability Validation

#### 1. Service Crew (Sage owns)
**Purpose**: Intake and brief capture
- Customer Service Agent, Founder Onboarding Agent, Consultant Onboarding Agent
- **Output**: Client Brief

#### 2. Analysis Crew (Sage)
**Purpose**: Customer and competitor analysis
- Customer Researcher, Competitor Analyst
- **Output**: VPC components ready for testing

#### 3. Governance Crew (Guardian) - Phase 1
**Purpose**: Quality validation before proceeding
- QA Agent
- **Output**: QA Pass/Fail with feedback

### Phase 2: Commercial Side + Build/Test

#### 4. Build Crew (Forge)
**Purpose**: Create testable artifacts
- UX/UI Designer, Frontend Developer, Backend Developer
- **Output**: Deployed testable artifacts with tracking

#### 5. Growth Crew (Pulse)
**Purpose**: Run experiments, collect signals
- Ad Creative Agent, Communications Agent, Social Media Analyst
- **Output**: Desirability evidence (quantitative + qualitative)

#### 6. Synthesis Crew (Compass)
**Purpose**: Integrate evidence, recommend pivot/proceed
- Project Manager
- **Output**: Evidence synthesis with recommendation

### Phase 3: Governance + Viability

#### 7. Finance Crew (Ledger)
**Purpose**: Validate business model viability
- Financial Controller, Legal & Compliance Agent
- **Output**: Viability assessment with financial model

#### 8. Enhanced Governance Crew (Guardian)
**Purpose**: Full audit trail and compliance
- Audit Agent, Security Agent, QA Agent
- **Output**: Audit report with compliance status

## CrewAI Flows Implementation

### Flow State Management

```python
from crewai.flow.flow import Flow, start, listen, router
from pydantic import BaseModel

class ValidationState(BaseModel):
    id: str
    brief: ClientBrief
    customer_profiles: List[CustomerProfile] = []
    competitor_analysis: CompetitorReport = None
    qa_status: str = "pending"
    evidence: List[Evidence] = []
    recommendation: str = None
```

### Phase 1 Flow Structure

```python
class Phase1Flow(Flow[ValidationState]):

    @start()
    def capture_brief(self):
        """Service Crew captures client context"""
        result = ServiceCrew().crew().kickoff(inputs={...})
        self.state.brief = result.pydantic

    @listen(capture_brief)
    def analyze_customers(self):
        """Analysis Crew researches customer segments"""
        result = AnalysisCrew().crew().kickoff(inputs={...})
        self.state.customer_profiles = result.pydantic

    @listen(analyze_customers)
    def analyze_competitors(self):
        """Analysis Crew maps competitive landscape"""
        result = AnalysisCrew().crew().kickoff(inputs={...})
        self.state.competitor_analysis = result.pydantic

    @listen(analyze_competitors)
    def governance_review(self):
        """Guardian QA gate"""
        result = GovernanceCrew().crew().kickoff(inputs={...})
        self.state.qa_status = result.status

    @router(governance_review)
    def qa_gate(self):
        if self.state.qa_status == "passed":
            return "approved"
        return "needs_revision"

    @listen("approved")
    def output_deliverables(self):
        """Compile Phase 1 outputs"""
        return self.state
```

## File Structure

```
src/startupai/
├── flows/
│   ├── __init__.py
│   ├── internal_validation_flow.py
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
  "entrepreneur_input": "Detailed description of startup idea, target customers, and business context"
}
```

## Outputs

Structured deliverables per phase:

### Phase 1 (Desirability)
- Client Brief (structured business context)
- Customer Profiles (Jobs/Pains/Gains per segment)
- Competitor Analysis (positioning map)
- Value Proposition Canvas
- Assumption Backlog (prioritized)
- QA Report

### Phase 2 (Feasibility)
- Test Artifacts (landing pages, ads, prototypes)
- Evidence Report (signals collected)
- Assumption Validation (validated/invalidated)
- Pivot/Proceed Recommendation

### Phase 3 (Viability)
- Feasibility Report
- Viability Model (unit economics)
- Audit Trail
- Flywheel Entry (methodology improvements)

## Deployment

### Current Deployment
- **UUID**: `b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b`
- **URL**: `https://startupai-b4d5c1dd-27e2-4163-b9fb-a18ca06ca-4f4192a6.crewai.com`
- **Platform**: CrewAI AMP

### Commands

```bash
# Install dependencies
uv sync

# Run locally
crewai run

# Deploy
crewai deploy push --uuid b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b

# Check status
crewai deploy status --uuid b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b

# View logs
crewai deploy logs --uuid b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b
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
- **Technical Specification**: [03-validation-spec.md](./03-validation-spec.md)
- **Current State**: [04-status.md](./04-status.md)
- **API Contracts**: [reference/api-contracts.md](./reference/api-contracts.md)
- **Approval Workflows**: [reference/approval-workflows.md](./reference/approval-workflows.md)
- **Validation Backlog**: [../work/backlog.md](../work/backlog.md)

## Support

- CrewAI Docs: https://docs.crewai.com
- CrewAI Dashboard: https://app.crewai.com
- GitHub Issues: https://github.com/chris00walker/startupai-crew/issues

---

**Status**: Rebuilding from 6-agent crew to 8-crew/18-agent Flows architecture
**Last Updated**: 2025-11-21
