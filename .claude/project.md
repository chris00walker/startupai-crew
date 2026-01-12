# .claude/project.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**StartupAI CrewAI Backend** (`startupai-crew`) - Modal serverless 5-flow/14-crew/45-agent validation engine with HITL checkpoints. Part of the StartupAI platform microservices architecture:

- **startupai.site** (Marketing) - Convert prospects to customers
- **app.startupai.site** (Product) - Next.js frontend application
- **startupai-crew** (AI Backend) - CrewAI validation engine (Modal) ← **THIS REPO**

**Canonical Deployment**: Modal Serverless (CrewAI AMP is deprecated).

**Tech Stack:**
- Python: 3.11+
- CrewAI: Flows + Crews
- Package Manager: uv
- Deployment: Modal Serverless
- State/Orchestration: Supabase Postgres + Realtime
- Testing: pytest

## Development Commands

### Setup and Installation

```bash
git clone https://github.com/chris00walker/startupai-crew.git
cd startupai-crew
uv sync
```

### Local Development

```bash
# Modal local dev (hot reload)
modal serve src/modal_app/app.py

# Optional: run CrewAI locally for flow debugging
crewai run
```

### Deployment (Modal)

```bash
modal deploy src/modal_app/app.py
```

**Production URL**:
- https://chris00walker--startupai-validation-fastapi-app.modal.run

## Architecture (Canonical)

**5 Phases / 14 Crews / 45 Agents with HITL**

| Phase | Flow | Crews | Agents |
|------|------|-------|--------|
| 0 | OnboardingFlow | OnboardingCrew | 4 |
| 1 | VPCDiscoveryFlow | 5 crews | 18 |
| 2 | DesirabilityFlow | 3 crews | 9 |
| 3 | FeasibilityFlow | 2 crews | 4 |
| 4 | ViabilityFlow | 3 crews | 9 |

**Key Principles:**
- HITL checkpoints with checkpoint-and-resume (Supabase state)
- External tools for evidence (Tavily, landing page deployment, analytics)
- Modal containers terminate during HITL ($0 idle)

## Project Structure

```
src/
├── modal_app/                  # Modal entry points (FastAPI)
│   ├── app.py                  # API endpoints
│   ├── phases/                 # Phase functions (0-4)
│   └── helpers/                # Shared helpers
├── crews/                      # 14 crew definitions
├── state/                      # Supabase state models + persistence
└── shared/
    ├── tools/                  # Agent tools
    └── schemas/                # Pydantic schemas
```

## Environment Variables

**Local `.env` (for local runs):**
```bash
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_KEY=eyJ...
NETLIFY_ACCESS_TOKEN=...
```

**Modal Secrets (production):** set via `modal secret create startupai-secrets ...`

## Integration with Product Platform

**Modal Endpoints:**
```
POST /kickoff         # Start validation (returns run_id)
GET  /status/{run_id} # Check progress
POST /hitl/approve    # Resume after human approval
GET  /health          # Health check
```

**Product App Flow:**
1. Product app calls `/api/crewai/analyze`
2. Next.js route proxies to Modal `/kickoff`
3. Modal writes progress to Supabase (`validation_runs`, `validation_progress`)
4. Modal triggers HITL via Supabase + webhook to `/api/crewai/webhook`
5. Product app displays progress + approvals

## Key Documentation

- `docs/master-architecture/` (ecosystem source of truth)
- `docs/work/phases.md` (phase criteria and blockers)
- `docs/adr/002-modal-serverless-migration.md` (Modal migration)

