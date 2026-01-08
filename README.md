# StartupAI Crew - AI Founders Engine

**5-Flow/14-Crew/45-Agent validation engine powering the AI Founders team**

This repository is the brain of the StartupAI ecosystem - a validation pipeline that delivers Fortune 500-quality strategic analysis through 6 AI Founders and 45 specialist agents.

> **Architecture Migration in Progress**: Migrating from CrewAI AMP to Modal serverless. See [ADR-002](docs/adr/002-modal-serverless-migration.md) for details.

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

### Canonical Architecture (5 Flows / 14 Crews / 45 Agents)

| Phase | Flow | Crews | Agents |
|-------|------|-------|--------|
| **0** | OnboardingFlow | OnboardingCrew | 4 (O1, GV1, GV2, S1) |
| **1** | VPCDiscoveryFlow | Discovery, CustomerProfile, ValueDesign, WTP, FitAssessment | 18 |
| **2** | DesirabilityFlow | Build, Growth, Governance | 9 |
| **3** | FeasibilityFlow | Build, Governance | 5 |
| **4** | ViabilityFlow | Finance, Synthesis, Governance | 9 |

### Gated Validation (VPD Framework)

```
Phase 0 (Onboarding) → [HITL] →
Phase 1 (VPC Discovery) → [HITL] →
Phase 2 (Desirability) → [HITL] →
Phase 3 (Feasibility) → [HITL] →
Phase 4 (Viability) → [HITL] → Decision
```

---

## Deployment Architecture

### Target: Modal Serverless (Proposed)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      INTERACTION LAYER (Netlify)                             │
│  Edge Functions trigger Modal, return 202 Accepted immediately              │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
┌─────────────────────────────────┼───────────────────────────────────────────┐
│                    ORCHESTRATION LAYER (Supabase)                            │
│  PostgreSQL (state) + Realtime (WebSocket UI updates) + RLS (multi-tenant)  │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
┌─────────────────────────────────┼───────────────────────────────────────────┐
│                       COMPUTE LAYER (Modal)                                  │
│  Ephemeral Python containers • Pay-per-second • Long-running (hours OK)     │
│  CrewAI executes here → writes progress to Supabase → container terminates  │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Benefits:**
- $0 idle costs (pay only when running)
- $0 during HITL waiting (containers terminate, resume on approval)
- Auto-scaling (0 → 1000+ concurrent validations)
- Platform-agnostic (runs anywhere Python runs)

### Legacy: CrewAI AMP (Deprecated)

> **Status**: Being phased out due to platform reliability issues. See [ADR-001](docs/adr/001-flow-to-crew-migration.md) and [ADR-002](docs/adr/002-modal-serverless-migration.md).

The 3-Crew AMP deployment is deprecated but remains deployed for reference:
- Crew 1: `startupai-crew` (this repo)
- Crew 2: `startupai-crew-validation`
- Crew 3: `startupai-crew-decision`

---

## Ecosystem

```
┌─────────────────────┐
│   AI Founders Core  │  ← THIS REPOSITORY
│   (startupai-crew)  │
│   Modal Serverless  │
└──────────┬──────────┘
           │
    ┌──────┼──────┐
    │      │      │
    ▼      ▼      ▼
Marketing  DB   Product
  Site          App
(Netlify) (Supa) (Netlify)
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
# Add OPENAI_API_KEY, SUPABASE_URL, SUPABASE_KEY, etc.
```

### 4. Run Locally
```bash
# Test a crew directly
uv run python -c "from src.crews.onboarding.crew import OnboardingCrew; print(OnboardingCrew())"

# Or use Modal local development (after Modal setup)
modal serve src/modal_app/app.py
```

---

## Repository Structure

```
startupai-crew/
├── src/
│   ├── modal_app/                # NEW: Modal serverless deployment
│   │   ├── app.py                # Web endpoints + orchestrator
│   │   ├── phases/               # Phase-specific functions
│   │   ├── state/                # Pydantic schemas + Supabase persistence
│   │   └── utils/                # Auth, progress, HITL helpers
│   │
│   ├── crews/                    # 14 Crew definitions
│   │   ├── phase0/               # OnboardingCrew
│   │   ├── phase1/               # 5 crews (Discovery, CustomerProfile, etc.)
│   │   ├── phase2/               # 3 crews (Build, Growth, Governance)
│   │   ├── phase3/               # 2 crews (Build, Governance)
│   │   └── phase4/               # 3 crews (Finance, Synthesis, Governance)
│   │
│   └── intake_crew/              # DEPRECATED: AMP Crew 1 (archived)
│
├── db/migrations/                # SQL migration files
├── scripts/                      # Utility scripts
├── tests/                        # Test suite
├── docs/
│   ├── master-architecture/      # ECOSYSTEM SOURCE OF TRUTH
│   ├── adr/                      # Architecture Decision Records
│   │   ├── 001-flow-to-crew-migration.md (Superseded)
│   │   └── 002-modal-serverless-migration.md (Current)
│   ├── deployment/               # Deployment guides
│   └── work/                     # Work tracking
├── archive/                      # Deprecated AMP code
│   ├── amp-deployment/
│   └── flow-architecture/
├── CLAUDE.md                     # AI context
├── pyproject.toml                # Dependencies
└── modal.toml                    # Modal configuration
```

---

## API Integration (Modal)

```bash
# Kickoff validation
curl -X POST https://<your-modal-app>.modal.run/kickoff \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"project_id": "...", "entrepreneur_input": "Business idea..."}'

# Check status
curl https://<your-modal-app>.modal.run/status/{run_id} \
  -H "Authorization: Bearer <token>"

# Approve HITL checkpoint
curl -X POST https://<your-modal-app>.modal.run/hitl/approve \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"hitl_id": "...", "decision": "approved", "user_id": "..."}'
```

---

## Inputs & Outputs

### Input
```json
{
  "project_id": "uuid",
  "entrepreneur_input": "Detailed description of startup idea..."
}
```

### Output (VPD Framework Phases)

**Phase 0 - Onboarding:**
- Founder's Brief (hypothesis capture)

**Phase 1 - VPC Discovery:**
- Customer Profiles (Jobs/Pains/Gains)
- Value Map (Products/Pain Relievers/Gain Creators)
- Fit Score (≥70 to proceed)

**Phase 2 - Desirability:**
- Test Artifacts, Evidence
- Desirability Signal (STRONG_COMMITMENT required)

**Phase 3 - Feasibility:**
- Technical Assessment
- Feasibility Signal (GREEN required)

**Phase 4 - Viability:**
- Unit Economics
- Final Recommendation (VALIDATED/PIVOT/KILL)

---

## Related Repositories

- **Marketing Site:** [startupai.site](https://github.com/chris00walker/startupai.site) - Lead capture & transparency
- **Product App:** [app.startupai.site](https://github.com/chris00walker/app.startupai.site) - Delivery portal

**Development Ports (Canonical):**
- **Marketing Site** (`startupai.site`): `localhost:3000`
- **Product App** (`app.startupai.site`): `localhost:3001`
- **This repo (Modal local)**: `localhost:8000` (via `modal serve`)

---

## Documentation

- **Docs Index:** `docs/README.md`
- **Master Architecture:** `docs/master-architecture/`
- **ADRs:** `docs/adr/` (Architecture Decision Records)
- **Current Status:** `docs/master-architecture/09-status.md`
- **Modal Docs:** https://modal.com/docs/guide
- **CrewAI Docs:** https://docs.crewai.com

---

## Current Status

> **Modal Migration PROPOSED.** See [ADR-002](docs/adr/002-modal-serverless-migration.md) for full architecture and migration plan.

**Canonical Architecture:**
- 5 Phases, 5 Flows, 14 Crews, 45 Agents, 10 HITL checkpoints

**Migration Status:**
- [ ] Infrastructure setup (Modal account, Supabase tables)
- [ ] Code migration (modal_app/, crews/)
- [ ] Testing (unit, integration, E2E)
- [ ] Deployment & cutover

**What's Changing:**
- FROM: 3-Crew AMP deployment (3 repos, InvokeCrewAIAutomationTool chaining)
- TO: Modal serverless (1 repo, native Python orchestration)

---

**Status:** Modal Migration PROPOSED
**Last Updated:** 2026-01-08
**License:** Proprietary - StartupAI Platform
