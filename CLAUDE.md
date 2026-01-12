# CLAUDE.md - StartupAI CrewAI Backend Memory

## Project Identity
**Name**: StartupAI AI Founders Engine
**Purpose**: 5-Flow/14-Crew/45-Agent validation engine with HITL checkpoints
**Framework**: CrewAI Flows + Crews (platform-agnostic)
**Deployment**: Modal Serverless (production) - see [ADR-002](docs/adr/002-modal-serverless-migration.md)
**Status**: Deployed to Modal, live testing Phase 0-2 complete

## Dogfooding Methodology

> **"If StartupAI can't validate itself, it won't work for anyone else."**

StartupAI is its own first customer. All development and testing uses real StartupAI accounts exercising the product as real users would.

### Test Accounts

| Role | Email | Password | Purpose |
|------|-------|----------|---------|
| **Founder** | chris00walker@proton.me | W7txYdr7bV0Tc30U0bv& | Tests Founder journey - validates StartupAI as a business |
| **Consultant** | chris00walker@gmail.com | Test123! | Tests Consultant journey - advises StartupAI as a client |

**Project**: StartupAI (the platform validating itself)

### Testing Requirements
- All Phase 0-4 flows tested with real Founder account
- All HITL checkpoints exercised before release
- Evidence quality validated against StartupAI's own data
- If it doesn't work for StartupAI, it doesn't ship

See [10-dogfooding.md](docs/master-architecture/10-dogfooding.md) for full methodology.

## Critical Context
**⚠️ IMPORTANT**: This repository is the **brain of the StartupAI ecosystem**. It powers the 6 AI Founders team that delivers Fortune 500-quality strategic analysis.

### Architecture Position
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
                                    ↓
                          [Product App Displays Results]
```

### CrewAI Pattern Hierarchy
The architecture follows CrewAI's documented patterns:
```
PHASE (Business Concept) → FLOW (Orchestration) → CREW (Agent Group) → AGENT → TASK
```

| Metric | Canonical | Modal Target | AMP (DEPRECATED) |
|--------|-----------|--------------|------------------|
| Phases | 5 | 5 | 5 |
| Flows | 5 | 5 | N/A (crews only) |
| Crews | 14 | 14 | 3 |
| Agents | 45 | 45 | 19 |
| HITL | 10 | 10 | 7 |

**Critical Rule**: A crew must have 2+ agents (per CrewAI docs). One agent is NOT a crew.

### Modal Serverless Architecture (Production)
Modal enables the **canonical architecture** with platform-agnostic deployment:
- **$0 idle costs** - containers only run during execution
- **$0 during HITL** - checkpoint-and-resume pattern terminates containers during human review
- **Single repository** - no more 3-repo workaround
- See [ADR-002](docs/adr/002-modal-serverless-migration.md) for full details

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Three-Layer Architecture                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  INTERACTION LAYER (Netlify/Product App)                                    │
│  • User triggers validation                                                 │
│  • Receives real-time progress updates                                      │
│  • Handles HITL approvals                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  ORCHESTRATION LAYER (Supabase)                                            │
│  • State persistence (PostgreSQL)                                           │
│  • Real-time updates (WebSocket)                                            │
│  • Approval queue management                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  COMPUTE LAYER (Modal)                                                      │
│  • 5 Flow functions (one per phase)                                         │
│  • Ephemeral containers (pay-per-second)                                    │
│  • Checkpoint-and-resume at HITL points                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3-Crew AMP Deployment (DEPRECATED)
> **⚠️ DEPRECATED**: Being replaced by Modal serverless. See [ADR-002](docs/adr/002-modal-serverless-migration.md).

AMP handled `type = "crew"` reliably but had issues with `type = "flow"`. The 3-Crew deployment was a **platform workaround**, not the canonical architecture:
- Canonical: 5 Flows orchestrating 14 Crews with `@start`, `@listen`, `@router`
- Deployed: 3 Crews chained via `InvokeCrewAIAutomationTool`
- See `docs/master-architecture/09-status.md` for full context

### Master Architecture
**Source of Truth**: `docs/master-architecture/`

| Document | Purpose |
|----------|---------|
| `00-introduction.md` | Repository architecture & quick start |
| `01-ecosystem.md` | Three-service overview |
| `02-organization.md` | 6 founders, agents, VPD terminology |
| `03-methodology.md` | **VPD framework, evidence hierarchy, templates** |
| `04-phase-0-onboarding.md` | Phase 0: Founder's Brief capture |
| `05-phase-1-vpc-discovery.md` | Phase 1: VPC Discovery (Customer Profile + Value Map) |
| `06-phase-2-desirability.md` | Phase 2: Desirability validation |
| `07-phase-3-feasibility.md` | Phase 3: Feasibility validation |
| `08-phase-4-viability.md` | Phase 4: Viability + Final Decision |
| `09-status.md` | Current state and blockers |
| `reference/` | API contracts, approval workflows, database schemas |
| `reference/agentic-tool-framework.md` | **Tool lifecycle, agent configuration pattern, implementation tiers** |
| `reference/tool-mapping.md` | Agent-to-tool mapping by phase |

**Phase Documents** follow a consistent template with: Purpose, Entry/Exit criteria, Flow diagrams, Agent specs, Output schemas, HITL checkpoints.

### CrewAI Documentation
**Location**: `docs/crewai-documentation/` (38 files, comprehensive reference)
**Index**: `docs/crewai-documentation/INDEX.md` - Topic-to-file mapping

Key references for development:
| Topic | Doc File |
|-------|----------|
| Flows (`@start`, `@listen`, `@router`) | `core-concepts/flows.md` |
| State management (Pydantic, persistence) | `guides/mastering-flow-state-management.md` |
| Agents (role, goal, backstory) | `core-concepts/agents.md` |
| Tasks (`output_pydantic`, context) | `core-concepts/tasks.md` |
| Crews (Process types) | `core-concepts/crews.md` |
| Testing | `core-concepts/testing.md` |

**Usage**: Consult these docs before implementing CrewAI patterns for authoritative API reference.

## Directory Structure
```
# PRODUCTION: MODAL SERVERLESS
src/
├── modal_app/                  # Modal entry points
│   ├── __init__.py
│   ├── app.py                  # FastAPI app + Modal endpoints (812 lines)
│   ├── config.py               # Modal configuration
│   ├── phases/                 # Phase-specific functions
│   │   ├── phase_0.py          # Phase 0: OnboardingFlow
│   │   ├── phase_1.py          # Phase 1: VPCDiscoveryFlow
│   │   ├── phase_2.py          # Phase 2: DesirabilityFlow
│   │   ├── phase_3.py          # Phase 3: FeasibilityFlow
│   │   └── phase_4.py          # Phase 4: ViabilityFlow
│   └── helpers/                # Helper functions
│       └── segment_alternatives.py  # Pivot selection logic
├── crews/                      # 14 Crew definitions (all implemented)
│   ├── onboarding/             # OnboardingCrew (4 agents)
│   ├── discovery/              # 5 crews: Discovery, CustomerProfile, ValueDesign, WTP, FitAssessment
│   ├── desirability/           # 3 crews: Build, Growth, Governance
│   ├── feasibility/            # 2 crews: Build, Governance
│   └── viability/              # 3 crews: Finance, Synthesis, Governance
├── state/                      # Supabase state management
│   ├── models.py               # Pydantic state models (612 lines)
│   └── persistence.py          # Checkpoint/resume logic (370 lines)
└── shared/                     # Shared utilities
    ├── tools/                  # Agent tools
    └── schemas/                # Pydantic schemas

# DEPRECATED: INTAKE CREW (AMP deployment)
src/intake_crew/
├── __init__.py
├── crew.py                     # 4 agents: S1, S2, S3, G1
├── main.py                     # Entry point
├── schemas.py                  # Pydantic schemas
├── tools/                      # Agent tools
│   ├── __init__.py
│   ├── methodology_check.py
│   └── web_search.py           # TavilySearchTool, CustomerResearchTool
└── config/
    ├── agents.yaml             # Agent definitions
    └── tasks.yaml              # 6 tasks (1 HITL)

# Database
db/
└── migrations/                 # SQL migration files

# Scripts & Tooling
scripts/
├── metrics/                    # Performance tracking data
├── evaluate_policies.py
├── post_deploy_validation.sh
├── seed_demo_project.py
├── simulate_flow.py
├── test_e2e_webhook.sh
└── track_performance.py

# Tests
tests/
├── integration/                # E2E and workflow tests
├── scenarios/                  # Test scenario data
└── test_*.py                   # Unit tests

# Documentation
docs/
├── deployment/                 # Deployment guides
│   ├── 3-crew-deployment.md
│   └── environments.md
├── testing/                    # Testing documentation
│   ├── testing.md
│   ├── testing-contracts.md
│   └── amp-observability-testing.md
├── concepts/                   # Conceptual documentation
│   ├── innovation-physics.md
│   └── IMPLEMENTATION_ANALYSIS.md
├── master-architecture/        # ECOSYSTEM SOURCE OF TRUTH
├── architecture-audit/         # Architecture audits
├── adr/                        # Architecture Decision Records
├── crewai-documentation/       # CrewAI reference docs
├── prompts/                    # Prompt engineering
├── tools/                      # Tool documentation
└── work/                       # Work tracking (phases, backlog)

# Archived code
archive/
├── flow-architecture/          # Original Flow-based code
└── crew-templates/             # Templates for Crews 2 & 3

# Root (conventional files only)
pyproject.toml                  # type = "crew" for AMP
uv.lock                         # Locked dependencies
pytest.ini                      # Test configuration
Makefile                        # Build commands
```

## Core Commands
```bash
# Setup
uv sync                         # Install dependencies

# Local Development
crewai run                      # Test workflow locally (requires OPENAI_API_KEY in .env)

# Modal Deployment (Production)
modal setup                     # One-time Modal CLI setup
modal deploy src/modal_app/app.py  # Deploy to Modal
modal serve src/modal_app/app.py   # Local development with hot reload

# AMP Deployment (DEPRECATED - preserved for reference)
crewai login                    # One-time setup per machine
crewai deploy status --uuid 6b1e5c4d-e708-4921-be55-08fcb0d1e94b
crewai deploy push --uuid 6b1e5c4d-e708-4921-be55-08fcb0d1e94b
crewai deploy logs --uuid 6b1e5c4d-e708-4921-be55-08fcb0d1e94b
```

## Deployment Configuration

### Modal Serverless (Production)
See [ADR-002](docs/adr/002-modal-serverless-migration.md) for architecture details.

**Production URL**: `https://chris00walker--startupai-validation-fastapi-app.modal.run`

**API Endpoints**:
```
POST /kickoff         → Start validation (returns 202 Accepted + run_id)
GET  /status/{run_id} → Check progress (reads from Supabase)
POST /hitl/approve    → Resume after human approval
GET  /health          → Health check
```

**Environment Variables (Modal Secrets)**:
- `OPENAI_API_KEY` - OpenAI API key
- `TAVILY_API_KEY` - Tavily API key for web search
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase service role key
- `NETLIFY_ACCESS_TOKEN` - Netlify personal access token for LP deployment

### 3-Crew Deployments (DEPRECATED)
> **⚠️ DEPRECATED**: Being replaced by Modal serverless. See [ADR-002](docs/adr/002-modal-serverless-migration.md).

| Crew | Repository | UUID | Token |
|------|------------|------|-------|
| Crew 1: Intake | `chris00walker/startupai-crew` | `6b1e5c4d-e708-4921-be55-08fcb0d1e94b` | `db9f9f4c1a7a` |
| Crew 2: Validation | `chris00walker/startupai-crew-validation` | `3135e285-c0e6-4451-b7b6-d4a061ac4437` | (check AMP dashboard) |
| Crew 3: Decision | `chris00walker/startupai-crew-decision` | `7da95dc8-7bb5-4c90-925b-2861fa9cba20` | `988cc694f297` |

**Organization**: StartupAI (`8f17470f-7841-4079-860d-de91ed5d1091`)
**Dashboard**: https://app.crewai.com/deployments

### Deployment Guide
See `docs/deployment/3-crew-deployment.md` for historical AMP deployment instructions (DEPRECATED).

## Environment Variables
### Local Development (`.env`)
```env
OPENAI_API_KEY=sk-...                    # Required for local testing
TAVILY_API_KEY=tvly-...                  # For web search tool
SUPABASE_URL=https://xxx.supabase.co     # Supabase project URL
SUPABASE_KEY=eyJ...                      # Supabase service role key
NETLIFY_ACCESS_TOKEN=xxx                 # Netlify personal access token for LP deployment
```

### Modal Secrets (Production)
Modal uses Secrets for environment variables (see `modal secret create`):
```bash
modal secret create startupai-secrets \
  OPENAI_API_KEY=sk-... \
  TAVILY_API_KEY=tvly-... \
  SUPABASE_URL=https://eqxropalhxjeyvfcoyxg.supabase.co \
  SUPABASE_KEY=eyJ... \
  NETLIFY_ACCESS_TOKEN=xxx
```

### CrewAI AMP Deployment (DEPRECATED)
> **⚠️ DEPRECATED**: All environment variables below were set in CrewAI AMP dashboard.

```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
SUPABASE_URL=https://eqxropalhxjeyvfcoyxg.supabase.co
SUPABASE_KEY=eyJ...
STARTUPAI_WEBHOOK_URL=https://app.startupai.site/api/crewai/webhook
STARTUPAI_WEBHOOK_BEARER_TOKEN=startupai-webhook-secret-2024
NETLIFY_ACCESS_TOKEN=xxx
```

### Unified Webhook
All CrewAI flows use a single webhook endpoint with `flow_type` differentiation:
- `POST /api/crewai/webhook` with `flow_type: "founder_validation"` for founder validation results
- `POST /api/crewai/webhook` with `flow_type: "consultant_onboarding"` for consultant onboarding results

## Architecture Overview

### The 6 AI Founders
| Founder | Title | Responsibility |
|---------|-------|----------------|
| **Sage** | CSO | Strategy, VPC design, owns Service Side |
| **Forge** | CTO | Build, technical feasibility |
| **Pulse** | CMO | Marketing, market signals, desirability evidence |
| **Compass** | CPO | Balance, synthesis, pivot/proceed |
| **Guardian** | CGO | Governance, accountability, board-level oversight |
| **Ledger** | CFO | Finance, viability, compliance |

### 14 Crews / 45 Agents (Canonical Architecture)

| Phase | Flow | Crews | Agents |
|-------|------|-------|--------|
| **Phase 0** | OnboardingFlow | OnboardingCrew | 4 (O1, GV1, GV2, S1) |
| **Phase 1** | VPCDiscoveryFlow | DiscoveryCrew, CustomerProfileCrew, ValueDesignCrew, WTPCrew, FitAssessmentCrew | 18 |
| **Phase 2** | DesirabilityFlow | BuildCrew, GrowthCrew, GovernanceCrew | 9 |
| **Phase 3** | FeasibilityFlow | BuildCrew, GovernanceCrew | 4 |
| **Phase 4** | ViabilityFlow | FinanceCrew, SynthesisCrew, GovernanceCrew | 9 |

**Note**: BuildCrew and GovernanceCrew are reused across phases.

### AMP Deployment (DEPRECATED - 3 Crews / 19 Agents)
> **⚠️ DEPRECATED**: Being replaced by Modal serverless. See [ADR-002](docs/adr/002-modal-serverless-migration.md).

Due to AMP platform limitations with `type = "flow"`, the canonical architecture was deployed as 3 chained crews:
- **Crew 1 (Intake)**: 4 agents
- **Crew 2 (Validation)**: 12 agents
- **Crew 3 (Decision)**: 3 agents

### 10 HITL Checkpoints (Canonical)
| Phase | Flow | Checkpoint | Purpose |
|-------|------|------------|---------|
| 0 | OnboardingFlow | `approve_brief` | Founder's Brief approval |
| 1 | VPCDiscoveryFlow | `approve_vpc` | VPC fit validation |
| 2 | DesirabilityFlow | `approve_campaign_launch` | Ad creative approval |
| 2 | DesirabilityFlow | `approve_spend_increase` | Budget approval |
| 2 | DesirabilityFlow | `approve_desirability_gate` | Gate: Desirability → Feasibility |
| 3 | FeasibilityFlow | `approve_feasibility_gate` | Gate: Feasibility → Viability |
| 4 | ViabilityFlow | `approve_viability_gate` | Gate: Viability → Decision |
| 4 | ViabilityFlow | `approve_pivot` | Pivot strategy approval |
| 4 | ViabilityFlow | `approve_proceed` | Proceed recommendation |
| 4 | ViabilityFlow | `request_human_decision` | Final pivot/proceed decision |

### Gated Validation Flow
```
Phase 0 → [HITL] → Phase 1 → [HITL] → Phase 2 → [HITL] → Phase 3 → [HITL] → Phase 4 → [HITL]
```

**Modal (Production)**: Orchestrated with phase functions in `src/modal_app/phases/`. HITL uses checkpoint-and-resume pattern ($0 during human review).
**AMP (DEPRECATED)**: Was orchestrated with `InvokeCrewAIAutomationTool` for crew-to-crew chaining.

**Full Details**: See `docs/master-architecture/` phase documents (03-08) for authoritative implementation blueprints

## API Interface
### Input Format
```json
{
  "entrepreneur_input": "Detailed description of startup idea, target customers, and business context"
}
```

### Output Format
Structured task outputs (not files):
- Entrepreneur Brief (JSON)
- Customer Profile (Jobs/Pains/Gains)
- Competitor Analysis Report (positioning map)
- Value Proposition Canvas (complete canvas)
- 3-Tier Validation Roadmap (prioritized experiments)
- QA Report (quality assessment with pass/fail)

### API Endpoints

**Modal (Production)**:
```bash
# Kickoff validation (returns 202 Accepted + run_id)
curl -X POST https://chris00walker--startupai-validation-fastapi-app.modal.run/kickoff \
  -H "Content-Type: application/json" \
  -d '{"project_id": "...", "entrepreneur_input": "Business idea..."}'

# Check status (reads from Supabase)
curl https://chris00walker--startupai-validation-fastapi-app.modal.run/status/{run_id}

# Resume after HITL approval
curl -X POST https://chris00walker--startupai-validation-fastapi-app.modal.run/hitl/approve \
  -H "Content-Type: application/json" \
  -d '{"run_id": "...", "checkpoint": "approve_brief", "decision": "approved"}'
```

**AMP (DEPRECATED)**:
```bash
# Kickoff workflow
curl -X POST https://startupai-6b1e5c4d-e708-4921-be55-08fcb0d1e-922bcddb.crewai.com/kickoff \
  -H "Authorization: Bearer db9f9f4c1a7a" \
  -H "Content-Type: application/json" \
  -d '{"entrepreneur_input": "Business idea..."}'

# Check status
curl https://startupai-6b1e5c4d-e708-4921-be55-08fcb0d1e-922bcddb.crewai.com/status/{kickoff_id} \
  -H "Authorization: Bearer db9f9f4c1a7a"
```

## Integration with Product App
**Frontend Trigger**: User completes onboarding → POST to `/api/crewai/analyze`

**Modal Integration (Production)**:
```typescript
// Product app API route - kickoff
export async function POST(req: Request) {
  const { project_id, entrepreneur_input } = await req.json();

  const response = await fetch(
    'https://chris00walker--startupai-validation-fastapi-app.modal.run/kickoff',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project_id, entrepreneur_input })
    }
  );

  // Returns { run_id: "...", status: "started" }
  return response.json();
}

// Real-time updates via Supabase Realtime subscription
// Progress stored in `validation_runs` table, subscribed by Product App
```

**AMP Integration (DEPRECATED)**:
```typescript
// Product app API route
export async function POST(req: Request) {
  const { entrepreneur_input } = await req.json();

  const response = await fetch(
    'https://startupai-6b1e5c4d-e708-4921-be55-08fcb0d1e-922bcddb.crewai.com/kickoff',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.CREW_CONTRACT_BEARER}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ entrepreneur_input })
    }
  );

  return response.json();
}
```

## Coding Standards
### Python Style
- **Type Hints**: Always use (e.g., `def func(input: str) -> dict:`)
- **Docstrings**: Google-style for all functions
- **Formatter**: Black (88 char line length)
- **Naming**: snake_case for functions/variables

### Agent Configuration
- **YAML Format**: `config/agents.yaml` defines all agents
- **Role**: Clear, specific job description
- **Goal**: Measurable outcome
- **Backstory**: Context for LLM reasoning
- **Tools**: See `docs/master-architecture/reference/agentic-tool-framework.md` for tool lifecycle

**IntakeCrew Pattern** (canonical agent configuration):
```python
@agent
def agent_name(self) -> Agent:
    return Agent(
        config=self.agents_config["agent_name"],
        tools=[Tool1(), Tool2()],     # Required for evidence-based outputs
        reasoning=True,                # Enables step-by-step reasoning
        inject_date=True,              # Temporal awareness
        max_iter=25,                   # Prevents infinite loops
        llm=LLM(model="openai/gpt-4o", temperature=0.7),
        verbose=True,
        allow_delegation=False,
    )
```

> **⚠️ TOOL WIRING GAP**: Modal crews have structure but most agents lack tools. See `docs/work/phases.md` for fix plan.

### Task Configuration
- **YAML Format**: `config/tasks.yaml` defines all tasks
- **Description**: Detailed instructions
- **Expected Output**: Clear deliverable format
- **Agent**: Assigned agent from `agents.yaml`

## Implementation Roadmap

### Validation Funnel (5 Phases)
| Phase | Purpose | Agents | Key Output |
|-------|---------|--------|------------|
| **Phase 0** | Onboarding | 4 (O1, GV1, GV2, S1) | Founder's Brief |
| **Phase 1** | VPC Discovery | 18 | Validated VPC (fit ≥ 70) |
| **Phase 2** | Desirability | 9 | STRONG_COMMITMENT signal |
| **Phase 3** | Feasibility | 4 | GREEN signal |
| **Phase 4** | Viability | 9 | PROFITABLE signal / Decision |

**Detailed Specs**: See `docs/master-architecture/` phase documents:
- `04-phase-0-onboarding.md` - Founder's Brief capture
- `05-phase-1-vpc-discovery.md` - Customer Profile + Value Map
- `06-phase-2-desirability.md` - "Do they want it?"
- `07-phase-3-feasibility.md` - "Can we build it?"
- `08-phase-4-viability.md` - "Can we make money?"

**Methodology**: See `docs/master-architecture/03-methodology.md` for VPD framework, SAY vs DO evidence hierarchy, Test Cards, Learning Cards.

## Troubleshooting

### Local run fails with "OPENAI_API_KEY not set"
**Cause**: `.env` file missing or incomplete
**Fix**: Copy `.env.example` to `.env` and add API key

### Modal Troubleshooting (Production)

#### Modal CLI not found
**Cause**: Modal CLI not installed
**Fix**: `pip install modal` or `uv add modal`

#### Modal secrets not found
**Cause**: Secrets not created in Modal
**Fix**: Run `modal secret create startupai-secrets ...` (see Environment Variables section)

#### Function timeout
**Cause**: Long-running crews exceeding timeout
**Fix**: Modal supports up to 24h execution; ensure `timeout` parameter set in `@modal.function()`

### AMP Troubleshooting (DEPRECATED)
> **⚠️ DEPRECATED**: AMP is being replaced by Modal. Issues below preserved for historical reference.

#### "Repository wrong" error
**Cause**: CrewAI dashboard linked to wrong GitHub repo
**Fix**: Check GitHub integration in CrewAI dashboard

#### AMP returns `source: memory` without executing
**Cause**: AMP infrastructure-level caching
**Status**: UNRESOLVED - one of several reasons for Modal migration
**Symptoms**:
- `/kickoff` returns immediately with `{"state":"SUCCESS","result":"founder_validation","source":"memory"}`
- Dashboard Traces show "Waiting for events to load..." (flow never executes)

## Related Repositories
- Marketing Site: `startupai.site` (lead capture)
- Product Platform: `app.startupai.site` (frontend + backend)

## Cross-Repo Coordination

**⚠️ This repo is UPSTREAM of all others.** Changes here unblock downstream repos.

### Single Repository Benefit (Modal Migration)
Modal migration returns us to a **single repository** (`startupai-crew`). No more cross-repo coordination for Crews 2 & 3 (was required for AMP workaround with separate repos).

### Before Starting Work
- Check `docs/work/cross-repo-blockers.md` for current dependencies
- Review `docs/work/phases.md` for Phase completion criteria
- Review [ADR-002](docs/adr/002-modal-serverless-migration.md) for migration status

### LLM Coordination Protocol
See `docs/master-architecture/llm-coordination.md`.

### When Completing Phase Milestones
1. Update completion checkboxes in `docs/work/phases.md`
2. Update `docs/work/cross-repo-blockers.md` with new status
3. Notify downstream repos by updating their blockers:
   - `app.startupai.site/docs/work/cross-repo-blockers.md`
   - `startupai.site/docs/work/cross-repo-blockers.md`

### Dependency Chain
```
CrewAI (this repo) → Product App → Marketing Site
```

**Current blocker**: None - Modal deployed, live testing in progress

## Claude Code Customizations

### Available Agents (Project-Level)
See `.claude/agents/` for repo-specific agents:
- **software-architect**: System design, architecture decisions, technology evaluation, scalability planning
- **crewai-workflow-designer**: CrewAI Flows orchestration, agent/crew architecture, task design, and workflow patterns
- **python-developer**: Python development, uv package management, pytest testing, type hints, async patterns, and Python best practices

### User-Level Agents (Available Across All Repos)
See `~/.claude/agents/` for cross-repo agents:
- **ecosystem-coordinator**: Cross-repo dependency management and blocker tracking
- **backend-developer**: Supabase, Drizzle ORM, API design, database architecture
- **frontend-developer**: Next.js, React, shadcn/ui, component patterns
- **ai-engineer**: CrewAI Flows, Vercel AI SDK, LLM integration
- **modal-developer**: Modal serverless deployment, Python functions, web endpoints, HITL patterns
- **supabase-developer**: PostgreSQL, Row Level Security, Realtime subscriptions, migrations
- **netlify-developer**: Site deployment, Edge Functions, environment variables, frontend hosting

### Available Skills
See `~/.claude/skills/` for cross-repo skills:
- **frontend-design**: Creative UI design guidance emphasizing distinctive aesthetics (typography, bold colors, motion, atmospheric backgrounds) - avoid generic "AI slop" patterns
- **cross-repo-sync**: Update blocker files across all 3 repos
- **quality-gate**: Comprehensive pre-commit checks (lint, type-check, test, build)
- **crewai-integration-check**: Validate CrewAI API contracts and deployment connectivity
- **modal-docs**: Modal serverless documentation lookup (functions, web endpoints, secrets, deployment)
- **supabase-docs**: Supabase documentation lookup (RLS, Realtime, migrations, MCP tools)
- **netlify-docs**: Netlify documentation lookup (Edge Functions, environment variables, deployment)
- **docs-cache-sync**: Synchronize local documentation caches with upstream sources

### Documentation Caches
Local documentation caches with self-learning capabilities:
- `docs/modal-documentation/` - Modal serverless patterns (9 files)
- `docs/supabase-documentation/` - Supabase PostgreSQL patterns (8 files)
- `docs/netlify-documentation/` - Netlify deployment patterns (8 files)

Each cache includes a `MANIFEST.json` for staleness tracking and automatic updates when fetching new content.

### Usage
Agents are automatically invoked based on context and trigger words in their descriptions. For architecture and system design questions, the software-architect agent provides strategic technical guidance. Skills are discovered and used when relevant to the current task.

## Documentation

### Master Architecture (Ecosystem Source of Truth)
```
docs/master-architecture/
├── 00-introduction.md         # Quick start
├── 01-ecosystem.md            # Three-service overview
├── 02-organization.md         # 6 founders, agents
├── 03-methodology.md          # VPD framework, evidence hierarchy
├── 04-phase-0-onboarding.md   # Phase 0: Founder's Brief
├── 05-phase-1-vpc-discovery.md # Phase 1: VPC Discovery
├── 06-phase-2-desirability.md # Phase 2: Desirability
├── 07-phase-3-feasibility.md  # Phase 3: Feasibility
├── 08-phase-4-viability.md    # Phase 4: Viability + Decision
├── 09-status.md               # Current state
├── reference/                 # API contracts, approval workflows
└── archive/                   # Old monolithic specs
```

### Service-Specific
- Deployment: `docs/deployment/`
- Testing: `docs/testing/`
- Concepts: `docs/concepts/innovation-physics.md`
- CrewAI Docs: https://docs.crewai.com

---
**Last Updated**: 2026-01-09
**Maintainer**: Chris Walker
**Status**: Modal serverless deployed, live testing Phase 0-2 complete
**Architecture**: 5 Flows / 14 Crews / 45 Agents / 10 HITL (canonical)
**Critical Note**: This is the BRAIN of the StartupAI ecosystem

### Migration Notes (2025-12-05)
- Migrated from `type = "flow"` to `type = "crew"` (AMP compatibility)
- Flow-based code archived to `archive/flow-architecture/`
- Crew 1 at root level, Crews 2 & 3 require separate repos
- See `docs/deployment/3-crew-deployment.md` for deployment steps

### Deployment Notes (2026-01-04)
- All 3 crews deployed to AMP and online
- Crew chaining implemented with `InvokeCrewAIAutomationTool`
- Separate GitHub repos: `startupai-crew`, `startupai-crew-validation`, `startupai-crew-decision`
- Environment variables for chaining must be set in AMP dashboard (see above)

### Documentation Restructure (2026-01-06)
- Reorganized `docs/master-architecture/` into separate phase documents
- Created `03-methodology.md` as reusable VPD framework reference
- Split phases: 04 (Onboarding), 05 (VPC Discovery), 06 (Desirability), 07 (Feasibility), 08 (Viability)
- Renamed status doc from `04-status.md` to `09-status.md`
- Archived old monolithic specs to `archive/`

### Documentation Standardization (2026-01-07)
- All 10 docs now have consistent YAML frontmatter with `vpd_compliance: true`
- All docs have Related Documents navigation section
- Updated Pulse title: CGO → CMO (Chief Marketing Officer)
- Clarified Guardian as board-level oversight (sentinel/overwatch)
- Full rewrite of `09-status.md` with cross-repo verification against `startupai.site` and `app.startupai.site`
- Primary blocker corrected: E2E verification (not deployment)

### Architecture Pattern Alignment (2026-01-07)
- Applied CrewAI documentation patterns as single source of truth
- Established pattern hierarchy: `PHASE → FLOW → CREW → AGENT → TASK`
- **Critical rule enforced**: A crew must have 2+ agents (one agent is NOT a crew)
- Consolidated one-agent "crews" into proper multi-agent crews
- Canonical architecture: 5 Flows, 14 Crews, 45 Agents, 10 HITL
- AMP deployment documented as platform workaround (3 Crews, 19 Agents, 7 HITL)
- Updated all phase documents (04-08) with CrewAI Pattern Mapping sections
- Updated `02-organization.md` with complete crew structure
- Updated `09-status.md` with architecture metrics

### Modal Serverless Migration (2026-01-08)
- **ADR-002**: Documented decision to migrate from CrewAI AMP to Modal serverless
- **Architecture**: Three-layer (Netlify + Supabase + Modal)
- **Key benefits**:
  - $0 idle costs (vs AMP's always-on containers)
  - $0 during HITL (checkpoint-and-resume pattern terminates containers)
  - Single repository (no more 3-repo workaround)
  - Platform-agnostic (can migrate to any Python platform)
- **HITL Pattern**: Checkpoint state to Supabase, terminate container, resume on approval webhook
- **Supabase Realtime**: WebSocket updates for instant UI progress
- **AMP**: Marked as DEPRECATED across all documentation
- See [ADR-002](docs/adr/002-modal-serverless-migration.md) for full details

### Modal Deployment Complete (2026-01-09)
- **Status**: DEPLOYED to production
- **URL**: `https://chris00walker--startupai-validation-fastapi-app.modal.run`
- **Implementation complete**:
  - 14 crews implemented (45 agents)
  - 5 phase flows (phase_0.py through phase_4.py)
  - State management (models.py, persistence.py)
  - HITL checkpoint-and-resume pattern
  - Signal-based routing for validation gates
- **Live testing**: Phase 0-2 validated with real LLM calls
- **Issues fixed**: 6 bugs discovered and resolved during live testing
- **Tests**: 500+ tests passing (crew tests + E2E integration)
