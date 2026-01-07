# StartupAI Crew - AI Founders Engine

**3-Crew/19-Agent validation engine powering the AI Founders team**

This repository is the brain of the StartupAI ecosystem - a multi-crew orchestration system deployed on CrewAI AMP that delivers Fortune 500-quality strategic analysis through 6 AI Founders and 19 specialist agents.

---

## Architecture

### The 6 AI Founders

| Founder | Title | Responsibility |
|---------|-------|----------------|
| **Sage** | CSO | Strategy, VPC design, owns Service Side |
| **Forge** | CTO | Build, technical feasibility |
| **Pulse** | CMO | Growth, market signals, desirability evidence |
| **Compass** | CPO | Balance, synthesis, pivot/proceed |
| **Guardian** | CGO | Governance, accountability, oversight |
| **Ledger** | CFO | Finance, viability, compliance |

### 3 Crews / 19 Agents

**Deployed on CrewAI AMP:**

| Crew | Repository | Agents | Purpose |
|------|------------|--------|---------|
| **Crew 1: Intake** | `startupai-crew` (this repo) | 4 (S1, S2, S3, G1) | VPC Discovery, brief capture |
| **Crew 2: Validation** | `startupai-crew-validation` | 12 (P1-P3, F1-F3, L1-L3, G1-G3) | D-F-V validation |
| **Crew 3: Decision** | `startupai-crew-decision` | 3 (C1, C2, C3) | Final synthesis |

### Gated Validation (VPD Framework)

```
Phase 0 (Onboarding) → Phase 1 (VPC Discovery) → [HITL] →
Phase 2 (Desirability) → [HITL] → Phase 3 (Feasibility) → [HITL] →
Phase 4 (Viability) → [HITL] → Decision
```

**Technology:** CrewAI Crews (`type="crew"`) with `InvokeCrewAIAutomationTool` for crew chaining.

---

## Ecosystem

```
┌─────────────────────┐
│   AI Founders Core  │  ← THIS REPOSITORY (Crew 1)
│   (startupai-crew)  │
│   CrewAI AMP Engine │
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

### Crew 1 (This Repo)
- **UUID:** `6b1e5c4d-e708-4921-be55-08fcb0d1e94b`
- **URL:** `https://startupai-6b1e5c4d-e708-4921-be55-08fcb0d1e-922bcddb.crewai.com`
- **Dashboard:** https://app.crewai.com/deployments

### Commands

```bash
# Deploy updates
crewai deploy push --uuid 6b1e5c4d-e708-4921-be55-08fcb0d1e94b

# Check status
crewai deploy status --uuid 6b1e5c4d-e708-4921-be55-08fcb0d1e94b

# View logs
crewai deploy logs --uuid 6b1e5c4d-e708-4921-be55-08fcb0d1e94b
```

---

## Inputs & Outputs

### Input
```json
{
  "entrepreneur_input": "Detailed description of startup idea, target customers, and business context"
}
```

### Output (VPD Framework Phases)

**Phase 0 - Onboarding:**
- Founder's Brief

**Phase 1 - VPC Discovery:**
- Customer Profiles (Jobs/Pains/Gains)
- Competitor Analysis
- Value Proposition Canvas
- Assumption Backlog
- QA Report

**Phase 2-4 - Validation:**
- Test Artifacts & Evidence
- D-F-V Scores
- Pivot/Proceed Recommendation

---

## API Integration

```bash
# Get inputs schema
curl https://startupai-...crewai.com/inputs \
  -H "Authorization: Bearer <your-deployment-token>"

# Kickoff workflow
curl -X POST https://startupai-...crewai.com/kickoff \
  -H "Authorization: Bearer <your-deployment-token>" \
  -H "Content-Type: application/json" \
  -d '{"entrepreneur_input": "Business idea..."}'

# Check status
curl https://startupai-...crewai.com/status/{kickoff_id} \
  -H "Authorization: Bearer <your-deployment-token>"
```

---

## Repository Structure

```
startupai-crew/
├── src/intake_crew/              # Crew 1: Intake (deployed to AMP)
│   ├── __init__.py
│   ├── crew.py                   # 4 agents: S1, S2, S3, G1
│   ├── main.py                   # Entry point
│   ├── schemas.py                # Pydantic output schemas
│   ├── tools/                    # Agent tools
│   │   ├── methodology_check.py
│   │   └── web_search.py         # TavilySearchTool
│   └── config/
│       ├── agents.yaml           # Agent definitions
│       └── tasks.yaml            # Task definitions
├── db/migrations/                # SQL migration files
├── scripts/                      # Utility scripts
├── tests/                        # Test suite
├── docs/
│   ├── master-architecture/      # ECOSYSTEM SOURCE OF TRUTH
│   │   ├── 00-introduction.md    # Quick start
│   │   ├── 01-ecosystem.md       # Three-service overview
│   │   ├── 02-organization.md    # 6 founders, 19 agents
│   │   ├── 03-methodology.md     # VPD framework
│   │   ├── 04-08-phase-*.md      # Phase specifications
│   │   ├── 09-status.md          # Current status
│   │   └── reference/            # API contracts, workflows
│   ├── deployment/               # Deployment guides
│   ├── testing/                  # Testing documentation
│   └── work/                     # Work tracking
├── CLAUDE.md                     # AI context
└── pyproject.toml                # Dependencies (type = "crew")
```

---

## Related Repositories

- **Marketing Site:** [startupai.site](https://github.com/chris00walker/startupai.site) - Lead capture & transparency
- **Product App:** [app.startupai.site](https://github.com/chris00walker/app.startupai.site) - Delivery portal
- **Crew 2:** [startupai-crew-validation](https://github.com/chris00walker/startupai-crew-validation) - Validation crews
- **Crew 3:** [startupai-crew-decision](https://github.com/chris00walker/startupai-crew-decision) - Decision crew

**Development Ports (Canonical):**
- **Marketing Site** (`startupai.site`): `localhost:3000`
- **Product App** (`app.startupai.site`): `localhost:3001`
- **This repo (CrewAI Backend)**: Deployed on CrewAI AMP (no local port needed)

---

## Documentation

- **Docs Index:** `docs/README.md`
- **Master Architecture:** `docs/master-architecture/`
- **Current Status:** `docs/master-architecture/09-status.md`
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

## Current Status

> **3-Crew Architecture DEPLOYED to AMP.** All 19 agents, 32 tasks, and 7 HITL checkpoints operational. See [09-status.md](docs/master-architecture/09-status.md) for detailed status.

**What Works:**
- 3-Crew architecture deployed to AMP (Crew 1, 2, 3)
- Crew chaining with `InvokeCrewAIAutomationTool`
- 7 HITL checkpoints across all crews
- Webhook persistence to Supabase
- Pydantic structured outputs (100% CrewAI best practices alignment)

**Primary Blocker:**
- E2E verification with live data

---

**Status:** 3-Crew architecture DEPLOYED (~85% overall)
**Last Updated:** 2026-01-07
**License:** Proprietary - StartupAI Platform
