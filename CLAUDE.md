# CLAUDE.md - StartupAI CrewAI Backend Memory

## Project Identity
**Name**: StartupAI AI Founders Engine
**Purpose**: 3-Crew/19-Agent validation engine with HITL checkpoints
**Framework**: CrewAI Crews (type="crew") - migrated from Flows
**Deployment**: CrewAI AMP Platform
**Status**: 3-Crew architecture DEPLOYED to AMP

## Critical Context
**⚠️ IMPORTANT**: This repository is the **brain of the StartupAI ecosystem**. It powers the 6 AI Founders team that delivers Fortune 500-quality strategic analysis.

### Architecture Position
```
[Product App] → [Onboarding: Vercel AI SDK] → Collects business data
                                    ↓
                          [3-Crew Pipeline]
  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
  │ CREW 1: INTAKE  │──▶│ CREW 2: VALID.  │──▶│ CREW 3: DECIDE  │
  │ (4 agents, 1HITL)│   │ (12 agents, 5HITL)│  │ (3 agents, 1HITL)│
  └─────────────────┘   └─────────────────┘   └─────────────────┘
                                    ↓
                       [Structured Reports → Supabase]
                                    ↓
                          [Product App Displays Results]
```

### Why 3 Crews (Not Flows)
AMP handles `type = "crew"` reliably but has issues with `type = "flow"`. The 3-Crew design:
- Preserves gated validation phases (Desirability → Feasibility → Viability)
- Enables conditional routing via task `context` dependencies
- Supports HITL approval workflows at 7 checkpoints

### Master Architecture
**Source of Truth**: `docs/master-architecture/`
- `01-ecosystem.md` - Three-service overview
- `02-organization.md` - 6 founders, 18 agents
- `03-validation-spec.md` - **AUTHORITATIVE BLUEPRINT** (complete implementation spec)
- `04-status.md` - Honest assessment
- `reference/api-contracts.md` - All API specifications
- `reference/approval-workflows.md` - HITL patterns

### CrewAI Documentation
**Location**: `docs/crewai-documentation/` (34 files, comprehensive reference)
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
# CREW 1: INTAKE (this repo, deployed to AMP)
src/intake_crew/
├── __init__.py
├── crew.py                     # 4 agents: S1, S2, S3, G1
├── main.py                     # Entry point
└── config/
    ├── agents.yaml             # Agent definitions
    └── tasks.yaml              # 6 tasks (1 HITL)

# CREWS 2 & 3 (require separate repos for AMP deployment)
startupai-crews/
├── crew-2-validation/          # 12 agents, 21 tasks (5 HITL)
└── crew-3-decision/            # 3 agents, 5 tasks (1 HITL)

# Archived Flow architecture
archive/flow-architecture/      # Original Flow-based code

docs/
├── 3-crew-deployment.md        # Deployment guide
├── architecture.md             # This repo's architecture
├── environments.md             # Environment setup
└── master-architecture/        # ECOSYSTEM SOURCE OF TRUTH

pyproject.toml                  # type = "crew" for AMP
uv.lock                         # Locked dependencies
```

## Core Commands
```bash
# Setup
uv sync                         # Install dependencies

# Authentication
crewai login                    # One-time setup per machine
# Creates ~/.config/crewai/settings.json with org credentials

# Local Development
crewai run                      # Test workflow locally (requires OPENAI_API_KEY in .env)

# Deployment
crewai deploy status --uuid 6b1e5c4d-e708-4921-be55-08fcb0d1e94b
crewai deploy push --uuid 6b1e5c4d-e708-4921-be55-08fcb0d1e94b
crewai deploy logs --uuid 6b1e5c4d-e708-4921-be55-08fcb0d1e94b

# Git workflow
git add .
git commit -m "Update agents/tasks"
git push origin main
crewai deploy push --uuid 6b1e5c4d-e708-4921-be55-08fcb0d1e94b
```

## Deployment Configuration

### 3-Crew Deployments (Active)
| Crew | Repository | UUID | Token | URL |
|------|------------|------|-------|-----|
| Crew 1: Intake | `chris00walker/startupai-crew` | `6b1e5c4d-e708-4921-be55-08fcb0d1e94b` | `db9f9f4c1a7a` | `https://startupai-6b1e5c4d-e708-4921-be55-08fcb0d1e-922bcddb.crewai.com` |
| Crew 2: Validation | `chris00walker/startupai-crew-validation` | `9d84b14f-bd06-4868-baee-e23484a4fcc2` | `3330a624bd66` | `https://startupai-validation-crew-9d84b14f-bd06-486-218c4c9d.crewai.com` |
| Crew 3: Decision | `chris00walker/startupai-crew-decision` | `7da95dc8-7bb5-4c90-925b-2861fa9cba20` | `988cc694f297` | `https://startupai-decision-crew-7da95dc8-7bb5-4c-7f70a58e.crewai.com` |

### Crew Chaining Environment Variables
**Crew 1** needs these in AMP dashboard:
- `CREW_2_URL` = `https://startupai-validation-crew-9d84b14f-bd06-486-218c4c9d.crewai.com`
- `CREW_2_BEARER_TOKEN` = `3330a624bd66`

**Crew 2** needs these in AMP dashboard:
- `CREW_3_URL` = `https://startupai-decision-crew-7da95dc8-7bb5-4c-7f70a58e.crewai.com`
- `CREW_3_BEARER_TOKEN` = `988cc694f297`

**Organization**: StartupAI (`8f17470f-7841-4079-860d-de91ed5d1091`)
**Dashboard**: https://app.crewai.com/deployments

### Deployment Guide
See `docs/3-crew-deployment.md` for full deployment instructions.

## Environment Variables
### Local Development (`.env`)
```env
OPENAI_API_KEY=sk-...                    # Required for local testing
TAVILY_API_KEY=tvly-...                  # For web search tool
SUPABASE_URL=https://xxx.supabase.co     # Supabase project URL
SUPABASE_KEY=eyJ...                      # Supabase service role key
STARTUPAI_WEBHOOK_URL=https://app.startupai.site/api/crewai/webhook
STARTUPAI_WEBHOOK_BEARER_TOKEN=xxx       # Shared webhook auth token
NETLIFY_ACCESS_TOKEN=xxx                 # Netlify personal access token for LP deployment
```

### CrewAI AMP Deployment (Dashboard → Environment Variables)
```env
OPENAI_API_KEY=sk-...                    # OpenAI API key
TAVILY_API_KEY=tvly-...                  # Tavily API key for web search
SUPABASE_URL=https://eqxropalhxjeyvfcoyxg.supabase.co
SUPABASE_KEY=eyJ...                      # Supabase service role key (from dashboard)
STARTUPAI_WEBHOOK_URL=https://app.startupai.site/api/crewai/webhook
STARTUPAI_WEBHOOK_BEARER_TOKEN=startupai-webhook-secret-2024
NETLIFY_ACCESS_TOKEN=xxx                 # Netlify personal access token for LP deployment
```

**⚠️ CRITICAL**: `.env` files are NOT used by deployed crews. All environment variables must be set in the CrewAI AMP dashboard.

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
| **Pulse** | CGO | Growth, market signals |
| **Compass** | CPO | Balance, synthesis, pivot/proceed |
| **Guardian** | CGO | Governance, accountability |
| **Ledger** | CFO | Finance, viability |

### 3 Crews / 19 Agents
**Crew 1 (Intake)**: 4 agents - Sage S1/S2/S3, Guardian G1
**Crew 2 (Validation)**: 12 agents - Pulse P1/P2/P3, Forge F1/F2/F3, Ledger L1/L2/L3, Guardian G1/G2/G3
**Crew 3 (Decision)**: 3 agents - Compass C1/C2/C3

### 7 HITL Checkpoints
| Crew | Checkpoint | Purpose |
|------|------------|---------|
| 1 | `approve_intake_to_validation` | Gate: Intake → Validation |
| 2 | `approve_campaign_launch` | Ad creative approval |
| 2 | `approve_spend_increase` | Budget approval |
| 2 | `approve_desirability_gate` | Gate: Desirability → Feasibility |
| 2 | `approve_feasibility_gate` | Gate: Feasibility → Viability |
| 2 | `approve_viability_gate` | Gate: Viability → Decision |
| 3 | `request_human_decision` | Final pivot/proceed decision |

### Gated Validation Flow
```
CREW 1 → [HITL] → CREW 2: Desirability → [HITL] → Feasibility → [HITL] → Viability → [HITL] → CREW 3 → [HITL]
```

Orchestrated with `InvokeCrewAIAutomationTool` for crew-to-crew chaining.

**Full Details**: See `docs/master-architecture/03-validation-spec.md` (authoritative implementation blueprint)

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
```bash
# Get deployment inputs schema
curl https://startupai-6b1e5c4d-e708-4921-be55-08fcb0d1e-922bcddb.crewai.com/inputs \
  -H "Authorization: Bearer db9f9f4c1a7a"

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

**Backend Proxy**:
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
- **Tools**: List of available tools (currently pure LLM-based)

### Task Configuration
- **YAML Format**: `config/tasks.yaml` defines all tasks
- **Description**: Detailed instructions
- **Expected Output**: Clear deliverable format
- **Agent**: Assigned agent from `agents.yaml`

## Implementation Roadmap

### Phase 1: Service Side + Desirability (Current)
1. Create state schemas (`state_schemas.py`)
2. Build Service Crew
3. Build Analysis Crew
4. Build Governance Crew (Phase 1)
5. Create Phase 1 Flow

### Phase 2: Commercial Side + Build/Test
1. Build Crew, Growth Crew, Synthesis Crew
2. Add pivot/proceed router logic
3. Implement evidence synthesis

### Phase 3: Governance + Viability
1. Finance Crew
2. Enhanced Governance Crew
3. Flywheel learning capture

**Detailed Plan**: See `docs/master-architecture/03-validation-spec.md`

## Troubleshooting
### "Repository wrong" error
**Cause**: CrewAI dashboard linked to wrong GitHub repo  
**Fix**: Check GitHub integration in CrewAI dashboard, verify `chris00walker/startupai-crew`

### Authentication failed
**Cause**: `~/.config/crewai/settings.json` missing or invalid  
**Fix**: Run `crewai login` to re-authenticate

### Local run fails with "OPENAI_API_KEY not set"
**Cause**: `.env` file missing or incomplete  
**Fix**: Copy `.env.example` to `.env` and add API key

### Deployment push fails
**Cause**: Wrong deployment UUID or expired token
**Fix**: Run `crewai deploy list` to verify UUID

### AMP returns `source: memory` without executing
**Cause**: AMP infrastructure-level caching returns cached results before code runs
**Status**: KNOWN ISSUE - awaiting CrewAI support response
**Symptoms**:
- `/kickoff` returns immediately with `{"state":"SUCCESS","result":"founder_validation","source":"memory"}`
- Dashboard Traces show "Waiting for events to load..." (flow never executes)
- Happens even with unique `cache_buster` in request body
**Workarounds attempted** (code-level - all deployed):
- Added `execution_id` with uuid4() default to state model
- Added `cache_buster` field injected in kickoff()
- Set `cache=False` on all 18 agents across 7 crew files
**Next step**: Contact CrewAI support about disabling AMP memory/caching at infrastructure level

## Related Repositories
- Marketing Site: `startupai.site` (lead capture)
- Product Platform: `app.startupai.site` (frontend + backend)

## Cross-Repo Coordination

**⚠️ This repo is UPSTREAM of all others.** Changes here unblock downstream repos.

### Before Starting Work
- Check `docs/work/cross-repo-blockers.md` for current dependencies
- Review `docs/work/phases.md` for Phase completion criteria

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

**Current blocker**: Phase 1 completion criteria in `docs/work/phases.md`

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

### Available Skills
See `~/.claude/skills/` for cross-repo skills:
- **frontend-design**: Creative UI design guidance emphasizing distinctive aesthetics (typography, bold colors, motion, atmospheric backgrounds) - avoid generic "AI slop" patterns
- **cross-repo-sync**: Update blocker files across all 3 repos
- **quality-gate**: Comprehensive pre-commit checks (lint, type-check, test, build)
- **crewai-integration-check**: Validate CrewAI API contracts and deployment connectivity

### Usage
Agents are automatically invoked based on context and trigger words in their descriptions. For architecture and system design questions, the software-architect agent provides strategic technical guidance. Skills are discovered and used when relevant to the current task.

## Documentation

### Master Architecture (Ecosystem Source of Truth)
- `docs/master-architecture/01-ecosystem.md` - Three-service overview
- `docs/master-architecture/02-organization.md` - 6 founders, 18 agents
- `docs/master-architecture/03-validation-spec.md` - Technical blueprint
- `docs/master-architecture/04-status.md` - Status assessment
- `docs/master-architecture/reference/` - API contracts, approval workflows

### Service-Specific
- Architecture: `docs/architecture.md`
- Environments: `docs/environments.md`
- CrewAI Docs: https://docs.crewai.com

---
**Last Updated**: 2026-01-04
**Maintainer**: Chris Walker
**Status**: 3-Crew architecture DEPLOYED to AMP
**Critical Note**: This is the BRAIN of the StartupAI ecosystem

### Migration Notes (2025-12-05)
- Migrated from `type = "flow"` to `type = "crew"` (AMP compatibility)
- Flow-based code archived to `archive/flow-architecture/`
- Crew 1 at root level, Crews 2 & 3 require separate repos
- See `docs/3-crew-deployment.md` for deployment steps

### Deployment Notes (2026-01-04)
- All 3 crews deployed to AMP and online
- Crew chaining implemented with `InvokeCrewAIAutomationTool`
- Separate GitHub repos: `startupai-crew`, `startupai-crew-validation`, `startupai-crew-decision`
- Environment variables for chaining must be set in AMP dashboard (see above)
