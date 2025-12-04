# .claude/project.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**StartupAI CrewAI Backend** (`startupai-crew`) - Pure Python automation crew that transforms startup ideas into Fortune 500-quality strategic analysis using a 6-agent pipeline. Part of the StartupAI platform microservices architecture:

- **startupai.site** (Marketing) - Convert prospects to customers
- **app.startupai.site** (Product) - Next.js frontend application
- **startupai-crew** (AI Backend) - CrewAI value proposition automation ← **THIS REPO**

**Tech Stack:**
- Python: 3.10+ (minimum required version)
- CrewAI: 1.2.1 (only production dependency)
- Package Manager: uv (modern Python package manager)
- Deployment: CrewAI AMP (cloud-hosted platform)
- Testing: pytest 7.4.0 (dev dependency)

## Development Commands

### Setup and Installation

```bash
# Clone and navigate
git clone https://github.com/chris00walker/startupai-crew.git
cd startupai-crew

# Install dependencies using uv (recommended)
uv sync

# OR use traditional pip
pip install -e ".[dev]"  # Installs with dev dependencies

# Authenticate with CrewAI (first time on new machine)
crewai login
```

### Local Development

```bash
# Create environment file
cp .env.example .env

# Add your OpenAI API key
echo "OPENAI_API_KEY=sk-your-key" >> .env

# Test locally (interactive mode)
crewai run

# Run with custom input
crewai run --input "Your startup idea here"

# Run tests (if tests are added)
pytest tests/
```

### Deployment to CrewAI AMP

```bash
# First-time deployment
crewai deploy create

# Subsequent deployments (push code to production)
crewai deploy push --uuid 6b1e5c4d-e708-4921-be55-08fcb0d1e94b

# Check deployment status
crewai deploy status --uuid 6b1e5c4d-e708-4921-be55-08fcb0d1e94b

# View logs
crewai deploy logs --uuid 6b1e5c4d-e708-4921-be55-08fcb0d1e94b

# List all deployments
crewai deploy list
```

**Production Deployment Details:**
- **UUID:** 6b1e5c4d-e708-4921-be55-08fcb0d1e94b
- **Token:** `<your-deployment-token>` (stored in CrewAI dashboard)
- **Public API URL:** https://startupai-6b1e5c4d-e708-4921-be55-08fcb0d1e-922bcddb.crewai.com
- **Organization:** StartupAI (8f17470f-7841-4079-860d-de91ed5d1091)
- **Status:** Online ✅
- **Dashboard:** https://app.crewai.com/deployments

## Architecture

### 6-Agent Sequential Pipeline

**Value Proposition Design Focus:**
This crew transforms startup ideas into validated value propositions using a systematic approach based on Value Proposition Design, Testing Business Ideas, and Business Model Generation frameworks.

**Agent Pipeline (Sequential Execution):**

1. **Onboarding Agent** (Startup Consultant & Interviewer)
   - **Goal:** Guide entrepreneurs through structured onboarding
   - **Output:** Entrepreneur Brief (JSON)
   - **Max Iterations:** 10
   - **Questions:** Customer segments, problems, product vision, differentiators, competitors, channels, assets, budget, timeline

2. **Customer Researcher Agent** (Customer Insight Analyst)
   - **Goal:** Identify target customer Jobs, Pains, and Gains
   - **Output:** Customer Profile (Jobs/Pains/Gains)
   - **Max Iterations:** 10
   - **Focus:** Functional, social, emotional customer jobs; pain points; required/expected/desired gains

3. **Competitor Analyst Agent** (Market & Competitor Strategist)
   - **Goal:** Map competitive landscape and differentiation opportunities
   - **Output:** Competitor Analysis Report + Positioning Map
   - **Max Iterations:** 8
   - **Deliverables:** Competitive benchmarking, white space identification

4. **Value Designer Agent** (Value Proposition Architect)
   - **Goal:** Synthesize insights into Value Proposition Canvas
   - **Output:** Value Proposition Canvas + Statement
   - **Max Iterations:** 10
   - **Produces:** Value Map, Pain Relievers, Gain Creators, Value Proposition Statement

5. **Validation Agent** (Experiment Designer & Validation Strategist)
   - **Goal:** Develop 3-tier Validation Roadmap
   - **Output:** Validation Roadmap with evidence tests
   - **Max Iterations:** 8
   - **Framework:** Testing Business Ideas (weak, medium, strong evidence tests)

6. **QA Agent** (Quality Assurance & Model Validation Specialist)
   - **Goal:** Verify framework compliance and logical consistency
   - **Output:** QA Report + Pass/Fail recommendation
   - **Max Iterations:** 5
   - **Checks:** Value Proposition Design, Testing Business Ideas, Business Model Generation compliance

**Key Architecture Principles:**
- **Pure LLM-Based:** No external tools or APIs (web search, databases, etc.)
- **Sequential Processing:** Each task waits for previous task completion
- **YAML-Driven Configuration:** All agents and tasks defined in config files
- **No Delegation:** Agents work independently (allow_delegation: false)

### Project Structure

```
startupai-crew/
├── src/
│   └── startupai/
│       ├── __init__.py                 # Package exports
│       ├── crew.py                     # Main crew definition (145 lines)
│       └── config/
│           ├── agents.yaml             # 6 agent configurations
│           └── tasks.yaml              # 6 task definitions
├── pyproject.toml                      # Project metadata, dependencies
├── uv.lock                             # Reproducible dependency lockfile
├── .env.example                        # Environment template
├── .env                                # Local environment (gitignored)
├── .gitignore                          # Python + IDE patterns
├── README.md                           # User documentation (285 lines)
├── docs/
│   ├── architecture.md                 # Architecture docs (312 lines)
│   └── environments.md                 # Environment setup guide (451 lines)
└── .claude/
    └── project.md                      # This file
```

### Key Configuration Files

**agents.yaml** - Agent Definitions
- 6 agents with detailed role, goal, and backstory
- All use `verbose: true` for detailed logging
- All use `allow_delegation: false` (no inter-agent delegation)
- Max iterations: 5-10 per agent

**tasks.yaml** - Task Definitions
- 6 sequential tasks mapping to agents
- Detailed descriptions with expected outputs
- Output JSON/Markdown formats specified
- Context dependency chain defined

**crew.py** - Main Crew Class
- Uses `@CrewBase` decorator from crewai.project
- Implements `StartupAICrew` class
- 6 agent methods decorated with `@agent`
- 6 task methods decorated with `@task`
- 1 crew method decorated with `@crew` (entry point for CrewAI AMP)

### Environment Variables

**For Local Development (`.env` file):**

```bash
# REQUIRED - LLM Provider
OPENAI_API_KEY=sk-...              # Primary LLM provider (required)

# OPTIONAL - Alternative Providers
ANTHROPIC_API_KEY=sk-ant-...       # Fallback LLM (Claude models)
GOOGLE_API_KEY=...                  # Alternative LLM (Gemini models)

# Development Settings
NODE_ENV=development                # Development mode
LOG_LEVEL=debug                     # Verbose logging
```

**Local Setup with direnv:**
- Credentials loaded from `~/.secrets/startupai` via direnv
- OPENAI_API_KEY and ANTHROPIC_API_KEY automatically injected
- No secrets committed to repository

**For Production (CrewAI AMP Dashboard):**
- Set via: https://app.crewai.com/deployments
- Navigate to: Deployment → Settings → Environment Variables
- Add: `OPENAI_API_KEY` (required)
- **Important:** Local `.env` files are NOT used by deployed crews

**Global CrewAI Config:**
- Location: `~/.config/crewai/settings.json`
- Contains: Organization ID, user email, authentication tokens
- Configured via: `crewai login` (one-time per machine)

## Integration with Product Platform

### API Integration

The `app.startupai.site` Next.js application calls this crew via REST API:

**Frontend Integration Code (TypeScript):**
```typescript
// frontend/src/lib/agentuity.ts
const AGENTUITY_AGENT_URL = process.env.AGENTUITY_AGENT_URL;

const response = await fetch(AGENTUITY_AGENT_URL, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${deploymentToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    strategic_question: userInput.question,
    project_context: userInput.context
  })
});
```

**Environment Variable in app.startupai.site:**
```bash
AGENTUITY_AGENT_URL=https://startupai-6b1e5c4d-e708-4921-be55-08fcb0d1e-922bcddb.crewai.com
```

### Microservices Architecture

```
User → startupai.site (Marketing)
         ↓
     app.startupai.site (Next.js Frontend) ← Supabase Auth
         ↓ HTTP/REST
     CrewAI AMP Platform (Managed Cloud)
         ↓
     startupai-crew (This Repo - Pure Automation)
```

### API Endpoints

**POST /inputs** - Submit Input
```bash
curl -X POST \
  https://startupai-6b1e5c4d-e708-4921-be55-08fcb0d1e-922bcddb.crewai.com/inputs \
  -H "Authorization: Bearer <your-deployment-token>" \
  -H "Content-Type: application/json" \
  -d '{"strategic_question": "Should we expand?", "project_context": "B2B SaaS"}'
```

**POST /kickoff** - Start Crew Execution
```bash
curl -X POST \
  https://startupai-6b1e5c4d-e708-4921-be55-08fcb0d1e-922bcddb.crewai.com/kickoff \
  -H "Authorization: Bearer <your-deployment-token>"
```

**GET /status** - Check Execution Status
```bash
curl -X GET \
  https://startupai-6b1e5c4d-e708-4921-be55-08fcb0d1e-922bcddb.crewai.com/status \
  -H "Authorization: Bearer <your-deployment-token>"
```

## Important Conventions

### Code Organization

- **YAML Configuration First:** All agent/task definitions in YAML files
- **No Hardcoding:** Never hardcode agent prompts in Python code
- **Minimal Dependencies:** Only crewai in production (pytest for dev)
- **Pure Automation:** No external tools or API integrations

### Development Workflow

1. **Modify YAML files** (`src/startupai/config/`) for agent/task changes
2. **Test locally** with `crewai run`
3. **Review output** for quality and compliance
4. **Deploy to production** with `crewai deploy push`
5. **Monitor logs** via CrewAI dashboard

### Git Workflow

- **Never force push to main** without explicit permission
- **Follow existing commit message style:** Check `git log` for patterns
- **Test locally before deploying:** Always run `crewai run` first
- **Document breaking changes:** Update docs/architecture.md and README.md

### Python Code Style

- **Type Hints:** Use Python type hints where applicable
- **Docstrings:** Document classes and methods
- **PEP 8:** Follow Python style guidelines
- **Imports:** Keep imports organized and minimal

## Key Documentation

### Repository Documentation
- **README.md** (285 lines) - Complete user guide with quick start, deployment, API integration
- **docs/architecture.md** (312 lines) - Detailed architecture documentation with agent definitions
- **docs/environments.md** (451 lines) - Multi-environment setup guide (local/production)

### External References
- **Product Platform:** `app.startupai.site` - Next.js frontend that calls this crew
- **Marketing Site:** `startupai.site` - Marketing website
- **CrewAI Docs:** https://docs.crewai.com - Official CrewAI documentation
- **CrewAI Dashboard:** https://app.crewai.com - Deployment management

### Framework Documentation
- **Value Proposition Design:** Strategyzer.com framework for value prop development
- **Testing Business Ideas:** Evidence-based validation methodology
- **Business Model Generation:** Business model canvas framework

## Common Pitfalls

1. **Don't hardcode agent definitions:** All agent config must be in agents.yaml
2. **Don't skip local testing:** Always test with `crewai run` before deploying
3. **Don't forget authentication:** All API calls require Bearer token
4. **Don't modify production directly:** Use `crewai deploy push` workflow
5. **Don't commit secrets:** Use .env for local keys, dashboard for production
6. **Don't add external tools without reason:** Keep crew pure LLM-based
7. **Don't break sequential flow:** Agents depend on previous task outputs

## Project Status

**Overall:** 100% Functional (as of October 2025)
- ✅ Agent Configuration: 100% (6 agents fully configured)
- ✅ Task Definitions: 100% (6 sequential tasks)
- ✅ Deployment: 100% (Live on CrewAI AMP)
- ✅ API Integration: 100% (Public endpoint available)
- ⚠️ Testing: 0% (No test files yet)

**Recent Updates:**
- Added comprehensive environment setup guide (docs/environments.md)
- Deployed to CrewAI AMP with public API
- Transformed from strategic analysis to Value Proposition Design focus
- Simplified to pure CrewAI automation (no external tools)

**Next Priorities:**
1. Add pytest test suite for crew validation
2. Implement response caching for common queries
3. Add error handling and retry logic
4. Create monitoring dashboard integration
5. Document output schema in detail

## Deployment Constraints

**Important Limitations:**
- **Cannot run on Netlify Functions:** Python/CrewAI incompatibility with serverless functions
- **Requires CrewAI AMP or equivalent:** AWS Bedrock AgentCore, Azure Container Apps, etc.
- **LLM API required:** OpenAI, Anthropic, or Google API key needed
- **Token authentication:** All API calls must include deployment token

**Why CrewAI AMP?**
- Managed infrastructure for Python-based crews
- Automatic scaling and load balancing
- Built-in API gateway with authentication
- Monitoring and logging dashboard
- GitHub integration for auto-deploy

## Testing

**Current Status:** No test framework implemented
- pytest 7.4.0 available as dev dependency
- No test files in repository
- Local testing via `crewai run` (manual)
- Production testing via curl commands to API

**Recommended Testing Approach:**
```bash
# Unit tests for crew configuration
pytest tests/test_crew.py

# Integration tests for API endpoints
pytest tests/test_api.py

# End-to-end tests for full pipeline
pytest tests/test_e2e.py
```

## Performance Characteristics

- **Sequential Execution:** Tasks run one after another (not parallel)
- **LLM Latency:** Response time depends on OpenAI/Anthropic API speed
- **Agent Iterations:** 5-10 iterations per agent (configured max)
- **No Built-in Timeout:** Uses CrewAI default timeout settings
- **Stateless:** Each execution is independent (no persistent state)

## Getting Help

- **Build Issues:** Check Python version (3.10+) and dependencies (`uv sync`)
- **Authentication Issues:** Run `crewai login` and verify organization access
- **Deployment Issues:** Check CrewAI dashboard logs and deployment status
- **API Issues:** Verify bearer token and endpoint URL
- **Agent Issues:** Review YAML configuration and local test output
- **Integration Issues:** Check environment variables in app.startupai.site
