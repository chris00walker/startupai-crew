# StartupAI Crew - AI Founders Engine

**4-Flow/14-Crew/43-Agent validation engine powering the AI Founders team**

This repository is the brain of the StartupAI ecosystem - a validation pipeline that delivers Fortune 500-quality strategic analysis through 6 AI Founders and 43 specialist agents.

> **Current Focus**: Phase 1-4 testing. Quick Start Architecture ([ADR-006](docs/adr/006-quick-start-architecture.md)) implemented - Phase 0 is now a simple form submission with no AI.

> **Architectural Pivot (2026-01-19)**: Phase 0 was simplified to Quick Start. Agent count: 45 → 43 (O1, GV2 deleted). OnboardingFlow deleted. Founder's Brief now AI-generated in Phase 1 by BriefGenerationCrew.

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

### Canonical Architecture (4 Flows / 14 Crews / 43 Agents)

| Phase | Flow | Crews | Agents |
|-------|------|-------|--------|
| **0** | (Quick Start) | None | 0 (no AI) |
| **1** | VPCDiscoveryFlow | BriefGeneration, Discovery, CustomerProfile, ValueDesign, WTP, FitAssessment | 20 |
| **2** | DesirabilityFlow | Build, Growth, Governance | 9 |
| **3** | FeasibilityFlow | Build, Governance | 5 |
| **4** | ViabilityFlow | Finance, Synthesis, Governance | 9 |

### Gated Validation (VPD Framework)

```
Phase 0 (Quick Start - 30 sec form) →
Phase 1 (VPC Discovery + Brief) → [HITL: approve_discovery_output] →
Phase 2 (Desirability) → [HITL: signal-dependent] →
Phase 3 (Feasibility) → [HITL: approve_feasibility_gate] →
Phase 4 (Viability) → [HITL: request_human_decision] → Decision
```

---

## Deployment Architecture

### Production: Modal Serverless

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

### Legacy: 3-Crew Workaround (Deprecated)

> **Status**: Being phased out due to platform reliability issues. See [ADR-001](docs/adr/001-flow-to-crew-migration.md) and [ADR-002](docs/adr/002-modal-serverless-migration.md).

The legacy 3-crew deployment is deprecated but remains for reference:
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
uv run python -c "from src.crews.discovery.brief_generation_crew import BriefGenerationCrew; print(BriefGenerationCrew())"

# Or use Modal local development (after Modal setup)
modal serve src/modal_app/app.py
```

---

## Repository Structure

```
startupai-crew/
├── src/
│   ├── modal_app/                # Modal serverless deployment (Production)
│   │   ├── app.py                # FastAPI + Modal endpoints (812 lines)
│   │   ├── config.py             # Modal configuration
│   │   ├── phases/               # Phase-specific functions (phase_0.py - phase_4.py)
│   │   └── helpers/              # Pivot selection, segment alternatives
│   │
│   ├── crews/                    # 14 Crew definitions (all implemented)
│   │   ├── discovery/            # 6 crews: BriefGeneration, Discovery, CustomerProfile, ValueDesign, WTP, FitAssessment
│   │   ├── desirability/         # 3 crews: Build, Growth, Governance
│   │   ├── feasibility/          # 2 crews: Build, Governance
│   │   └── viability/            # 3 crews: Finance, Synthesis, Governance
│   │
│   ├── state/                    # Supabase state management
│   │   ├── models.py             # Pydantic state models (612 lines)
│   │   └── persistence.py        # Checkpoint/resume logic (370 lines)
│   │
│   └── intake_crew/              # DEPRECATED: Legacy Crew 1
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
├── archive/                      # Deprecated legacy deployment code
│   ├── amp-deployment/
│   └── flow-architecture/
├── CLAUDE.md                     # AI context
├── pyproject.toml                # Dependencies
└── modal.toml                    # Modal configuration
```

---

## API Integration (Modal)

**Production URL**: `https://chris00walker--startupai-validation-fastapi-app.modal.run`

```bash
# Kickoff validation
curl -X POST https://chris00walker--startupai-validation-fastapi-app.modal.run/kickoff \
  -H "Content-Type: application/json" \
  -d '{"project_id": "...", "entrepreneur_input": "Business idea..."}'

# Check status
curl https://chris00walker--startupai-validation-fastapi-app.modal.run/status/{run_id}

# Approve HITL checkpoint
curl -X POST https://chris00walker--startupai-validation-fastapi-app.modal.run/hitl/approve \
  -H "Content-Type: application/json" \
  -d '{"run_id": "...", "checkpoint": "approve_brief", "decision": "approved"}'

# Health check
curl https://chris00walker--startupai-validation-fastapi-app.modal.run/health
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

**Phase 0 - Quick Start:**
- Raw idea + optional context (form input, ~30 seconds)
- → Phase 1 starts immediately

**Phase 1 - VPC Discovery + Brief Generation:**
- Founder's Brief (AI-generated from research)
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

> **Modal Migration COMPLETE.** Quick Start Architecture ([ADR-006](docs/adr/006-quick-start-architecture.md)) implemented. Live testing Phase 1-2 validated. See [ADR-002](docs/adr/002-modal-serverless-migration.md) for architecture details.

**Canonical Architecture:**
- 5 Phases, 4 Flows, 14 Crews, 43 Agents, 10 HITL checkpoints (Phase 0 has none)

**Migration Status:**
- [x] Infrastructure setup (Modal account, Supabase tables)
- [x] Code migration (modal_app/, crews/, state/)
- [x] Testing (678+ tests: crew tests + E2E integration)
- [x] Deployment (Production URL live)
- [x] Quick Start Architecture implemented ([ADR-006](docs/adr/006-quick-start-architecture.md))
- [x] Live testing Phase 1-2 (issues fixed)
- [ ] Live testing Phase 3-4

**Quick Start Pivot (2026-01-19):**
- [x] Phase 0 simplified to form submission (no AI, no conversation)
- [x] OnboardingFlow deleted, BriefGenerationCrew added to Phase 1
- [x] Agent count reduced: 45 → 43 (O1, GV2 deleted)
- [x] HITL checkpoint: `approve_discovery_output` (combined Brief + VPC)

**What Changed:**
- FROM: Legacy 3-crew deployment (3 repos, InvokeCrewAIAutomationTool chaining)
- TO: Modal serverless (1 repo, native Python orchestration)
- FROM: 7-stage AI conversation (20-25 min)
- TO: Quick Start form (~30 seconds)

---

**Status:** Modal Deployed, Quick Start Implemented
**Last Updated:** 2026-01-20
**License:** Proprietary - StartupAI Platform
