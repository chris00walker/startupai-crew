# StartupAI Crew - AI Founders Engine

**CrewAI Flows-based validation engine powering the AI Founders team**

This repository is the brain of the StartupAI ecosystem - a multi-crew orchestration system that delivers Fortune 500-quality strategic analysis through 6 AI Founders and 18 specialist agents.

---

## Architecture

### The 6 AI Founders

| Founder | Title | Responsibility |
|---------|-------|----------------|
| **Sage** | CSO | Strategy, VPC design, owns Service Side |
| **Forge** | CTO | Build, technical feasibility |
| **Pulse** | CGO | Growth, market signals, desirability evidence |
| **Compass** | CPO | Balance, synthesis, pivot/proceed |
| **Guardian** | CGO | Governance, accountability, oversight |
| **Ledger** | CFO | Finance, viability, compliance |

### 8 Crews / 18 Agents

**Service Side (Sage owns):**
- Service Crew: Customer Service, Founder Onboarding, Consultant Onboarding

**Commercial Side:**
- Analysis Crew (Sage): Customer Researcher, Competitor Analyst
- Build Crew (Forge): UX/UI Designer, Frontend Developer, Backend Developer
- Growth Crew (Pulse): Ad Creative, Communications, Social Media Analyst
- Synthesis Crew (Compass): Project Manager
- Finance Crew (Ledger): Financial Controller, Legal & Compliance

**Governance (Guardian):**
- Governance Crew: Audit Agent, Security Agent, QA Agent

### Gated Validation

```
[Test Cycles] → DESIRABILITY GATE → [Test Cycles] → FEASIBILITY GATE → [Test Cycles] → VIABILITY GATE
```

**Technology:** CrewAI Flows with `@listen` and `@router` decorators for crew orchestration and governance gates.

---

## Ecosystem

```
┌─────────────────────┐
│   AI Founders Core  │  ← THIS REPOSITORY
│   (startupai-crew)  │
│  CrewAI Flows Engine│
└──────────┬──────────┘
           │
    ┌──────┼──────┐
    │      │      │
    ▼      ▼      ▼
Marketing  DB   Product
  Site          App
```

**Master Architecture:** See `docs/master-architecture/` for ecosystem source of truth.

---

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/chris00walker/startupai-crew.git
cd startupai-crew
```

### 2. Install Dependencies
```bash
uv sync
```

### 3. Configure Environment
```bash
cp .env.example .env
# Add OPENAI_API_KEY=sk-...
```

### 4. Authenticate with CrewAI
```bash
crewai login
```

### 5. Run Locally
```bash
crewai run
```

---

## Deployment

**Current Deployment:**
- **UUID:** `b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b`
- **URL:** `https://startupai-b4d5c1dd-27e2-4163-b9fb-a18ca06ca-4f4192a6.crewai.com`
- **Token:** `f4cc39d92520`
- **Dashboard:** https://app.crewai.com/deployments

### Commands

```bash
# Deploy updates
crewai deploy push --uuid b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b

# Check status
crewai deploy status --uuid b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b

# View logs
crewai deploy logs --uuid b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b
```

---

## Inputs & Outputs

### Input
```json
{
  "entrepreneur_input": "Detailed description of startup idea, target customers, and business context"
}
```

### Output (Per Phase)

**Phase 1 - Desirability:**
- Client Brief
- Customer Profiles (Jobs/Pains/Gains)
- Competitor Analysis
- Value Proposition Canvas
- Assumption Backlog
- QA Report

**Phase 2 - Feasibility:**
- Test Artifacts
- Evidence Report
- Pivot/Proceed Recommendation

**Phase 3 - Viability:**
- Viability Model
- Audit Trail
- Flywheel Entry

---

## API Integration

```bash
# Get inputs schema
curl https://startupai-...crewai.com/inputs \
  -H "Authorization: Bearer f4cc39d92520"

# Kickoff workflow
curl -X POST https://startupai-...crewai.com/kickoff \
  -H "Authorization: Bearer f4cc39d92520" \
  -H "Content-Type: application/json" \
  -d '{"entrepreneur_input": "Business idea..."}'

# Check status
curl https://startupai-...crewai.com/status/{kickoff_id} \
  -H "Authorization: Bearer f4cc39d92520"
```

---

## Repository Structure

```
startupai-crew/
├── src/startupai/
│   ├── flows/                      # CrewAI Flows orchestration
│   │   ├── internal_validation_flow.py
│   │   └── state_schemas.py
│   ├── crews/                      # 8 specialized crews
│   │   ├── service/
│   │   ├── analysis/
│   │   ├── governance/
│   │   ├── build/
│   │   ├── growth/
│   │   ├── synthesis/
│   │   └── finance/
│   └── tools/                      # 18 tools (see docs/tools/README.md)
│       ├── web_search.py           # Tavily-powered research
│       ├── financial_data.py       # Industry benchmarks
│       ├── landing_page.py         # Landing page generation
│       ├── guardian_review.py      # HITL creative review
│       ├── viability_approval.py   # HITL viability decisions
│       ├── flywheel_insights.py    # Cross-validation learning
│       ├── privacy_guard.py        # PII/compliance protection
│       └── ...
├── tests/integration/              # 192 integration tests
├── docs/
│   ├── master-architecture/        # ECOSYSTEM SOURCE OF TRUTH
│   ├── tools/                      # Tool documentation
│   └── work/                       # Work tracking
├── CLAUDE.md                       # AI context
└── pyproject.toml                  # Dependencies
```

---

## Related Repositories

- **Marketing Site:** [startupai.site](https://github.com/chris00walker/startupai.site) - Lead capture & transparency
- **Product App:** [app.startupai.site](https://github.com/chris00walker/app.startupai.site) - Delivery portal

---

## Documentation

- **Docs Index:** `docs/README.md`
- **Master Architecture:** `docs/master-architecture/`
- **CrewAI Docs:** https://docs.crewai.com

---

## Troubleshooting

### "Authentication failed"
```bash
crewai login
```

### "No OPENAI_API_KEY"
- Local: Check `.env` file
- Deployed: Set in CrewAI dashboard → Environment Variables

### "Crew not found"
```bash
crewai deploy list
```

---

## Support

- **CrewAI Docs:** https://docs.crewai.com
- **Dashboard:** https://app.crewai.com
- **Issues:** https://github.com/chris00walker/startupai-crew/issues

---

## Current Status

> **Phase 2D Complete:** Core validation flow with HITL workflows, flywheel learning, and privacy protection. See [04-status.md](docs/master-architecture/04-status.md) for detailed status.

**Implemented (Phases 1A-2D):**
- Flow orchestration with 3-phase gated validation (Innovation Physics routers)
- State management with `@persist()` decorators at 9 checkpoints
- 18 tools implemented (research, financial, build, HITL, flywheel, privacy)
- Real web research (TavilySearchTool)
- Real financial analysis (IndustryBenchmarkTool, UnitEconomicsCalculatorTool)
- Landing page generation + Netlify deployment
- HITL creative approval workflow (GuardianReviewTool)
- HITL viability decision workflow (ViabilityApprovalTool)
- Flywheel learning system (FlywheelInsightsTool, OutcomeTrackerTool)
- Privacy protection (PrivacyGuardTool with GDPR/CCPA/HIPAA checks)
- 192 integration tests passing

**Not Yet Implemented:**
- Real ad platform integration (Meta/Google APIs) - deferred
- Real experiment tracking and analytics
- Production webhook integration with product app

---

**Status:** Phase 2D complete - ~80% overall
**Last Updated:** November 26, 2025
**License:** Proprietary - StartupAI Platform
