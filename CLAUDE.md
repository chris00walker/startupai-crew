# CLAUDE.md - StartupAI CrewAI Backend Memory

## Project Identity
**Name**: StartupAI AI Founders Engine
**Purpose**: 8-crew/18-agent validation engine with CrewAI Flows
**Framework**: CrewAI Flows (Python)
**Deployment**: CrewAI AMP Platform
**Status**: Rebuilding to Flows architecture

## Critical Context
**⚠️ IMPORTANT**: This repository is the **brain of the StartupAI ecosystem**. It powers the 6 AI Founders team that delivers Fortune 500-quality strategic analysis.

### Architecture Position
```
[Product App] → [Onboarding: Vercel AI SDK] → Collects business data
                                    ↓
                          [CrewAI Flows Engine]
                     8 Crews / 18 Specialist Agents
                                    ↓
                       [Structured Reports → Supabase]
                                    ↓
                          [Product App Displays Results]
```

### Master Architecture
**Source of Truth**: `docs/master-architecture/`
- `01-ecosystem.md` - Three-service overview
- `02-organization.md` - 6 founders, 18 agents
- `03-validation-spec.md` - **AUTHORITATIVE BLUEPRINT** (complete implementation spec)
- `04-status.md` - Honest assessment
- `reference/api-contracts.md` - All API specifications
- `reference/approval-workflows.md` - HITL patterns

## Directory Structure
```
src/startupai/
├── flows/                      # CrewAI Flows orchestration
│   ├── founder_validation_flow.py
│   └── state_schemas.py
├── crews/                      # 8 specialized crews
│   ├── service/
│   ├── analysis/
│   ├── governance/
│   ├── build/
│   ├── growth/
│   ├── synthesis/
│   └── finance/
└── tools/                      # Shared tools

docs/
├── architecture.md             # This repo's architecture
├── environments.md             # Environment setup
└── master-architecture/        # ECOSYSTEM SOURCE OF TRUTH

pyproject.toml                  # Dependencies
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
crewai deploy status --uuid b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b
crewai deploy push --uuid b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b
crewai deploy logs --uuid b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b

# Git workflow
git add .
git commit -m "Update agents/tasks"
git push origin main
crewai deploy push --uuid b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b
```

## Deployment Configuration
**Current Deployment**:
- UUID: `b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b`
- Token: `<your-deployment-token>` (stored in CrewAI dashboard)
- Public URL: `https://startupai-b4d5c1dd-27e2-4163-b9fb-a18ca06ca-4f4192a6.crewai.com`
- Organization: StartupAI (`8f17470f-7841-4079-860d-de91ed5d1091`)
- GitHub Repo: `chris00walker/startupai-crew`
- Branch: `main`

**Dashboard**: https://app.crewai.com/deployments

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

### 8 Crews / 18 Agents
**Service Side**: Service Crew (Sage)
**Commercial Side**: Analysis, Build, Growth, Synthesis, Finance Crews
**Governance**: Governance Crew (Guardian)

### Gated Validation Flow
```
[Test Cycles] → DESIRABILITY GATE → [Test Cycles] → FEASIBILITY GATE → [Test Cycles] → VIABILITY GATE
```

Orchestrated with CrewAI Flows using `@listen` and `@router` decorators.

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
curl https://startupai-b4d5c1dd-27e2-4163-b9fb-a18ca06ca-4f4192a6.crewai.com/inputs \
  -H "Authorization: Bearer <your-deployment-token>"

# Kickoff workflow
curl -X POST https://startupai-b4d5c1dd-27e2-4163-b9fb-a18ca06ca-4f4192a6.crewai.com/kickoff \
  -H "Authorization: Bearer <your-deployment-token>" \
  -H "Content-Type: application/json" \
  -d '{"entrepreneur_input": "Business idea..."}'

# Check status
curl https://startupai-b4d5c1dd-27e2-4163-b9fb-a18ca06ca-4f4192a6.crewai.com/status/{kickoff_id} \
  -H "Authorization: Bearer <your-deployment-token>"
```

## Integration with Product App
**Frontend Trigger**: User completes onboarding → POST to `/api/crewai/analyze`

**Backend Proxy**:
```typescript
// Product app API route
export async function POST(req: Request) {
  const { entrepreneur_input } = await req.json();
  
  const response = await fetch(
    'https://startupai-b4d5c1dd-27e2-4163-b9fb-a18ca06ca-4f4192a6.crewai.com/kickoff',
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
**Last Updated**: 2025-11-21
**Maintainer**: Chris Walker
**Status**: Rebuilding to 8-crew/18-agent Flows architecture
**Critical Note**: This is the BRAIN of the StartupAI ecosystem
