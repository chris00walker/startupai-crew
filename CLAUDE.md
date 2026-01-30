# CLAUDE.md - StartupAI AI Founders Engine

## Quick Reference
- **Purpose**: 5-Flow/14-Crew/45-Agent validation engine with HITL checkpoints
- **Framework**: CrewAI Flows + Crews
- **Deployment**: Modal Serverless (production)
- **Status**: Deployed, live testing Phase 0-2 complete
- **CLI Tools**: See `~/.claude/CLAUDE.md`
- **Master Architecture**: [`docs/master-architecture/`](docs/master-architecture/) (ecosystem source of truth)
- **Testing**: TDD with JDTD methodology - see [`app.startupai.site/docs/testing/`](../app.startupai.site/docs/testing/)

## Architecture
```
[Product App] → [Onboarding: Vercel AI SDK] → Collects business data
                                    ↓
                     [5-Flow / 14-Crew Pipeline]
  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
  │ PHASE 0      │──▶│ PHASE 1      │──▶│ PHASE 2      │──▶│ PHASE 3      │──▶│ PHASE 4      │
  │ Onboarding   │   │ VPC Discovery│   │ Desirability │   │ Feasibility  │   │ Viability    │
  │ 1 crew, 4 ag │   │ 5 crews,18 ag│   │ 3 crews, 9 ag│   │ 2 crews, 5 ag│   │ 3 crews, 9 ag│
  └──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘
                                    ↓
                       [Structured Reports → Supabase]
```

**Pattern Hierarchy**: `PHASE → FLOW → CREW → AGENT → TASK`

**Rule**: A crew must have 2+ agents (one agent is NOT a crew).

## 6 AI Founders
| Founder | Title | Responsibility |
|---------|-------|----------------|
| Sage | CSO | Strategy, VPC design |
| Forge | CTO | Build, technical feasibility |
| Pulse | CMO | Marketing, desirability evidence |
| Compass | CPO | Synthesis, pivot/proceed |
| Guardian | CGO | Governance, board-level oversight |
| Ledger | CFO | Finance, viability |

## Directory Structure
```
src/
├── modal_app/           # Modal entry points
│   ├── app.py           # FastAPI + Modal endpoints
│   └── phases/          # phase_0.py through phase_4.py
├── crews/               # 14 Crew definitions
├── state/               # Pydantic models, persistence
└── shared/              # Tools, schemas

tests/                   # Unit + integration tests
docs/master-architecture/ # ECOSYSTEM SOURCE OF TRUTH
```

## Commands
```bash
uv sync                              # Install dependencies
crewai run                           # Test locally
modal deploy src/modal_app/app.py    # Deploy to Modal
modal serve src/modal_app/app.py     # Local dev with hot reload
```

## Package Management

Use `pnpm` for installs, upgrades, and scripts in Node.js subprojects. Avoid `npm` for dependency changes.
When asked to upgrade dependencies, default to `pnpm up -L` unless a task specifies otherwise.

## Modal API (Production)
**URL**: `https://chris00walker--startupai-validation-fastapi-app.modal.run`

```bash
POST /kickoff         # Start validation (returns run_id)
GET  /status/{run_id} # Check progress
POST /hitl/approve    # Resume after human approval
GET  /health          # Health check
```

## 10 HITL Checkpoints
| Phase | Checkpoint | Purpose |
|-------|------------|---------|
| 0 | `approve_brief` | Founder's Brief approval |
| 1 | `approve_vpc` | VPC fit validation |
| 2 | `approve_campaign_launch` | Ad creative approval |
| 2 | `approve_spend_increase` | Budget approval |
| 2 | `approve_desirability_gate` | Gate: D → F |
| 3 | `approve_feasibility_gate` | Gate: F → V |
| 4 | `approve_viability_gate` | Gate: V → Decision |
| 4 | `approve_pivot` | Pivot strategy |
| 4 | `approve_proceed` | Proceed recommendation |
| 4 | `request_human_decision` | Final decision |

## Coding Standards

### Python
- Type hints always: `def func(input: str) -> dict:`
- Google-style docstrings
- Black formatter (88 char)
- snake_case naming

### Agent Configuration
```python
@agent
def agent_name(self) -> Agent:
    return Agent(
        config=self.agents_config["agent_name"],
        tools=[Tool1(), Tool2()],
        reasoning=True,
        max_iter=25,
        llm=LLM(model="openai/gpt-4o", temperature=0.7),
    )
```

## Environment Variables
```bash
# Modal Secrets (production)
modal secret create startupai-secrets \
  OPENAI_API_KEY=sk-... \
  TAVILY_API_KEY=tvly-... \
  SUPABASE_URL=https://xxx.supabase.co \
  SUPABASE_KEY=eyJ...
```

## Cross-Repo
- **This repo is UPSTREAM** - changes here unblock downstream
- **Downstream**: `app.startupai.site` → `startupai.site`
- **Blockers**: `docs/work/cross-repo-blockers.md`

## Documentation
```
docs/master-architecture/     # ECOSYSTEM SOURCE OF TRUTH
├── 00-introduction.md        # Quick start
├── 01-ecosystem.md           # Three-service overview
├── 02-organization.md        # 6 founders, agents
├── 03-methodology.md         # VPD framework
├── 04-08-phase-*.md          # Phase specs
├── 09-status.md              # Current state
└── reference/                # API contracts

docs/crewai-documentation/    # CrewAI reference (38 files)
docs/adr/                     # Architecture decisions
```

**AMP deployment is deprecated** - see `docs/adr/002-modal-serverless-migration.md` for migration rationale.

## ExecPlans

- Use an ExecPlan (see `.agent/PLANS.md`) for complex features, cross-layer integrations, or significant refactors.
- ExecPlans are living documents; keep them updated as work progresses.
- When executing an ExecPlan, proceed milestone by milestone without asking for "next steps" between milestones unless blocked or scope changes.

---
**Last Updated**: 2026-01-20
**Architecture**: 5 Flows / 14 Crews / 45 Agents / 10 HITL
