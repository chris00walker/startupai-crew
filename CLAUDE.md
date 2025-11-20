# CLAUDE.md - StartupAI CrewAI Backend Memory

## Project Identity
**Name**: StartupAI CrewAI Backend  
**Purpose**: 6-agent strategic business analysis workflow  
**Framework**: CrewAI (Python)  
**Deployment**: CrewAI AMP Platform  
**Status**: ✅ Core workflow functional (15% tools implemented)  

## Critical Context
**⚠️ IMPORTANT**: This is NOT deprecated. CrewAI AMP is a **fundamental building block** of the StartupAI value proposition. It delivers Fortune 500-quality strategic analysis that differentiates the product.

### Architecture Position
```
[Product App] → [Onboarding: Vercel AI SDK] → Collects business data
                                    ↓
                          [CrewAI AMP Workflow]
                          6-Agent Analysis Pipeline
                                    ↓
                       [Structured Reports → Supabase]
                                    ↓
                          [Product App Displays Results]
```

## Directory Structure
```
src/startupai/
├── __init__.py
├── crew.py                     # Main @CrewBase class
└── config/
    ├── agents.yaml             # 6 agent definitions
    └── tasks.yaml              # 6 task definitions

docs/
├── architecture.md             # Detailed architecture
└── environments.md             # Environment setup

.env.example                    # Template (not used in deployment)
pyproject.toml                  # Dependencies (pure crewai)
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
- Token: `f4cc39d92520` (stored in CrewAI dashboard)
- Public URL: `https://startupai-b4d5c1dd-27e2-4163-b9fb-a18ca06ca-4f4192a6.crewai.com`
- Organization: StartupAI (`8f17470f-7841-4079-860d-de91ed5d1091`)
- GitHub Repo: `chris00walker/startupai-crew`
- Branch: `main`

**Dashboard**: https://app.crewai.com/deployments

## Environment Variables
### Local Development (`.env`)
```env
OPENAI_API_KEY=sk-...          # Required for local testing
```

### CrewAI AMP Deployment (Dashboard → Environment Variables)
```env
OPENAI_API_KEY=sk-...          # Set in CrewAI dashboard, NOT in .env
```

**⚠️ CRITICAL**: `.env` files are NOT used by deployed crews. All environment variables must be set in the CrewAI AMP dashboard.

## 6-Agent Workflow
### Agent Definitions (`config/agents.yaml`)
1. **Onboarding Agent** (Startup Consultant & Interviewer)
   - Role: Guide entrepreneurs through structured onboarding
   - Output: Entrepreneur Brief (JSON)

2. **Customer Researcher** (Customer Insight Analyst)
   - Role: Identify target customer Jobs, Pains, and Gains
   - Output: Customer Profile

3. **Competitor Analyst** (Market & Competitor Strategist)
   - Role: Map competitive landscape and differentiation
   - Output: Competitor Analysis Report

4. **Value Designer** (Value Proposition Architect)
   - Role: Synthesize insights into Value Proposition Canvas
   - Output: Value Proposition Canvas

5. **Validation Agent** (Experiment Designer & Validation Strategist)
   - Role: Develop 3-tier Validation Roadmap
   - Output: 3-Tier Validation Roadmap

6. **QA Agent** (Quality Assurance & Model Validation Specialist)
   - Role: Verify framework compliance
   - Output: QA Report (pass/fail recommendation)

### Task Flow (`config/tasks.yaml`)
Sequential execution:
```
Onboarding → Customer Research → Competitor Analysis → Value Design → Validation Planning → QA Review
```

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
  -H "Authorization: Bearer f4cc39d92520"

# Kickoff workflow
curl -X POST https://startupai-b4d5c1dd-27e2-4163-b9fb-a18ca06ca-4f4192a6.crewai.com/kickoff \
  -H "Authorization: Bearer f4cc39d92520" \
  -H "Content-Type: application/json" \
  -d '{"entrepreneur_input": "Business idea..."}'

# Check status
curl https://startupai-b4d5c1dd-27e2-4163-b9fb-a18ca06ca-4f4192a6.crewai.com/status/{kickoff_id} \
  -H "Authorization: Bearer f4cc39d92520"
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

## Known Limitations & Future Enhancements
### Current State (15% Tools Implemented)
- **Pure LLM-Based**: No external tools/APIs (web search, data retrieval)
- **Mock Data**: Some tools return placeholder responses
- **Tools Needing Implementation**:
  - `EvidenceStoreTool`: Search/retrieve validation evidence
  - `WebSearchTool`: Real-time market research
  - `ReportGeneratorTool`: Formatted output generation

### Enhancement Roadmap
1. Implement real tools (web search, data APIs)
2. Add caching for repeated analyses
3. Optimize token usage (currently ~100K tokens per run)
4. Add streaming for long-running tasks
5. Integrate with Supabase for result storage

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

## Documentation

### Master Architecture (Cross-Service)
This repository is the **single source of truth** for ecosystem architecture:
- `docs/master-architecture/ecosystem.md` - Three-service reality diagram
- `docs/master-architecture/organizational-structure.md` - Flat founder team & workflow agents
- `docs/master-architecture/current-state.md` - Honest status assessment
- `docs/master-architecture/validation-backlog.md` - Hypothesis-driven feature queue

### Service-Specific
- Architecture: `docs/architecture.md`
- Environments: `docs/environments.md`
- CrewAI Docs: https://docs.crewai.com

---
**Last Updated**: Generated by Claude Code Architect  
**Maintainer**: Chris Walker  
**Status**: Production-ready (15% tools functional, LLM-based analysis works)  
**Critical Note**: This is a FUNDAMENTAL building block, not deprecated
