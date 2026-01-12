# Multi-Environment Setup Guide

**StartupAI Crew** - CrewAI Automation Environment Management

---

## 🎯 Overview

This repository is a **CrewAI Flows backend** with two environments:

| Environment | Purpose | Platform | Config File |
|------------|---------|----------|-------------|
| **Local** | Development and testing | Local machine | `.env` |
| **Production** | Live AI workflows | Modal Serverless | Modal Dashboard |

**Note:** There is no staging environment for CrewAI deployments - they run either locally or in production on Modal.

---

## 🚀 Quick Start Commands

### Local Development & Testing
```bash
# Install dependencies
uv sync

# Modal local dev (hot reload)
modal serve src/modal_app/app.py

# Optional: run a flow locally
crewai run
```

**Use for:** Testing flows, debugging tools, validating prompts

---

### Production Deployment
```bash
# Deploy to Modal
modal deploy src/modal_app/app.py
```

**Use for:** Live AI workflows accessible via HTTPS API

---

## 📁 Environment File Structure

```
startupai-crew/
├── .env.example          # Template (committed to git)
├── .env                  # Local development (gitignored) ⭐ YOU CREATE THIS
├── src/
│   ├── modal_app/                      # Modal FastAPI entry points
│   │   ├── app.py                      # API endpoints
│   │   └── phases/                     # Phase functions (0-4)
│   ├── crews/                          # 14 crews
│   ├── state/                          # Pydantic state + persistence
│   └── shared/                         # Tools + schemas
├── docs/
│   ├── innovation-physics.md           # Strategyzer methodology & router logic
│   └── master-architecture/            # Ecosystem source of truth
└── pyproject.toml                      # Python dependencies
```

**⚠️ IMPORTANT:** You must create `.env` from `.env.example` for local testing

---

## 🔧 Environment Configuration Details

### Local Development (.env)

**Purpose:** Test CrewAI workflows on your local machine

**Required Variables:**
```bash
# LLM Provider (REQUIRED)
OPENAI_API_KEY=sk-...

# Optional Alternative Providers
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# Environment
NODE_ENV=development
LOG_LEVEL=debug
```

**How to Create:**
```bash
# 1. Copy example
cp .env.example .env

# 2. Edit with your API key
nano .env

# 3. Add your OpenAI key
OPENAI_API_KEY=sk-your-actual-key-here

# 4. Save and exit
```

**Runs:** `crewai run` (uses local Python environment)

---

### Production (Modal Dashboard)

**Purpose:** Live AI workflows accessible via HTTPS

**Configuration Location:** Modal Dashboard  
**URL:** https://modal.com/apps

**Current Deployment:**
- **App URL:** `https://chris00walker--startupai-validation-fastapi-app.modal.run`
- **Status:** 🟢 Online
- **Organization:** StartupAI (`8f17470f-7841-4079-860d-de91ed5d1091`)

**Environment Variables Set in Modal Secrets:**
- `OPENAI_API_KEY` - Primary LLM provider
- `ANTHROPIC_API_KEY` - Fallback LLM provider (optional)
- `TAVILY_API_KEY` - Web research for market intelligence (recommended)
- `SUPABASE_URL` - Supabase project URL for persistence (`https://eqxropalhxjeyvfcoyxg.supabase.co`)
- `SUPABASE_KEY` - Supabase service role key for direct database access
- `STARTUPAI_WEBHOOK_URL` - Unified webhook for all flow results (`https://app.startupai.site/api/crewai/webhook`)
- `STARTUPAI_WEBHOOK_BEARER_TOKEN` - Bearer token for webhook authentication (shared with product app)
- `NETLIFY_ACCESS_TOKEN` - Netlify personal access token for landing page deployment

**Deployment:** `modal deploy src/modal_app/app.py`

---

## 🔐 Secret Management

### Local Development

**Option 1: Direct .env File (Simplest)**
```bash
# Create .env
cp .env.example .env

# Add your key directly
echo "OPENAI_API_KEY=sk-your-key" >> .env
```

**Option 2: Using direnv (Recommended for multi-repo)**
```bash
# If you use direnv with ~/.secrets/startupai
# CrewAI will automatically load OPENAI_API_KEY

# Setup (one-time)
brew install direnv  # or: apt install direnv
eval "$(direnv hook bash)"  # add to ~/.bashrc

# The .env file will load from centralized secrets
```

### Production (Modal)

**Set via Modal secrets:**
1. Create secret: `modal secret create startupai-secrets OPENAI_API_KEY=sk-...`
2. Add other keys (SUPABASE_URL, SUPABASE_KEY, TAVILY_API_KEY, NETLIFY_ACCESS_TOKEN)
3. Deploy: `modal deploy src/modal_app/app.py`

**Security:**
- Secrets encrypted at rest
- Never exposed in logs
- Automatically injected at runtime

---

## 🧪 Testing

### Pytest Test Suite

The project has comprehensive pytest coverage for flows, persistence, events, and decision logging.

```bash
# Run all tests (304+ tests)
make test

# Run with verbose output
make test-v

# Run with coverage report
make test-cov

# Quick smoke test (fastest tests)
make smoke
```

**Targeted Test Commands:**
```bash
# Flow routing tests (gate routers)
make test-flows

# Persistence layer tests
make test-persistence

# Schema validation tests
make test-schemas
```

### Integration Tests

Integration tests require `OPENAI_API_KEY` because they instantiate actual CrewAI crews:

```bash
# Ensure .env has OPENAI_API_KEY
cat .env | grep OPENAI_API_KEY

# Run all tests including integration
uv run python -m pytest tests/ -v

# Integration tests will be SKIPPED if OPENAI_API_KEY is not set
```

**Note:** 10 integration tests are skipped without `OPENAI_API_KEY`. These test tool wiring to crews/agents and are safe to run locally with your API key.

### CrewAI Quality Benchmarks

Use `crewai test` for quality scoring (requires OpenAI API):

```bash
# Quick benchmark (3 iterations)
make benchmark

# Full benchmark (5 iterations)
make benchmark-full
```

This runs the crew multiple times and scores outputs 0-10 for quality regression detection.

### Test Crew Locally Before Deployment
```bash
# 1. Ensure .env exists with OPENAI_API_KEY
cat .env | grep OPENAI_API_KEY

# 2. Run crew
crewai run

# 3. Verify output
# Should see agents executing tasks (5 flows, 14 crews, 45 agents when fully deployed)

# 4. Check for errors
# All tasks should complete successfully
```

### Test Production Deployment
```bash
# 1. Deploy
modal deploy src/modal_app/app.py

# 2. Test health
curl https://chris00walker--startupai-validation-fastapi-app.modal.run/health

# 3. Test kickoff
curl -X POST https://chris00walker--startupai-validation-fastapi-app.modal.run/kickoff \
  -H "Content-Type: application/json" \
  -d '{"project_id":"test","entrepreneur_input":"SaaS for developers"}'
```

---

## 🔄 Deployment Workflow

### First-Time Setup (New Machine)
```bash
# 1. Clone repo
git clone https://github.com/chris00walker/startupai-crew.git
cd startupai-crew

# 2. Install dependencies
uv sync

# 3. Create .env
cp .env.example .env
nano .env  # Add OPENAI_API_KEY

# 4. Authenticate with Modal
modal setup

# 5. Test locally
modal serve src/modal_app/app.py

# 6. Deploy to production
modal deploy src/modal_app/app.py
```

### Regular Development Workflow
```bash
# 1. Make changes to agents or tasks
nano src/crews/...

# 2. Test locally
modal serve src/modal_app/app.py

# 3. If works, commit
git add .
git commit -m "feat: improved agent prompts"
git push

# 4. Deploy to production
modal deploy src/modal_app/app.py

# 5. Verify deployment
curl https://chris00walker--startupai-validation-fastapi-app.modal.run/health
```

---

## 🌐 Modal Authentication

### Login Process
```bash
# First time on new machine
modal setup

# This will:
# 1. Open browser
# 2. Authenticate with Modal
# 3. Save credentials to Modal config (~/.modal.toml)
# 4. Link to StartupAI account
```

**You only need to login once per machine!**

---

## 🎯 Environment Selection Guide

### Use **Local** when:
- ✅ Developing new agents
- ✅ Testing task workflows
- ✅ Debugging agent prompts
- ✅ Validating tool integrations
- ✅ Iterating on agent personalities

### Use **Production** when:
- ✅ Deploying for API access
- ✅ Integrating with frontend (app.startupai.site)
- ✅ Serving real users
- ✅ Production monitoring required
- ✅ Scaling to multiple concurrent requests

---

## 📦 Required Environment Variables

### Minimum Required (Local & Production)
```bash
OPENAI_API_KEY=sk-...
```

### Results Persistence & Database (Production)
These enable the flow to persist results and state to Supabase:
```bash
# Supabase connection for state persistence and learning storage
SUPABASE_URL=https://eqxropalhxjeyvfcoyxg.supabase.co
SUPABASE_KEY=eyJ...  # Service role key

# Unified webhook endpoint for all flow results (founder validation, consultant onboarding)
# Flow type is differentiated via `flow_type` field in webhook payload
STARTUPAI_WEBHOOK_URL=https://app.startupai.site/api/crewai/webhook

# Bearer token for webhook authentication (shared with product app)
STARTUPAI_WEBHOOK_BEARER_TOKEN=startupai-webhook-secret-2024

# Netlify deployment for landing pages generated by Build Crew
NETLIFY_ACCESS_TOKEN=your-netlify-token
```

### Web Research Tools (Recommended)
These enable real-time web search for market research and competitive analysis:
```bash
# Tavily API for AI-optimized web search ($0.01/search)
# Get your key at: https://tavily.com
TAVILY_API_KEY=tvly-...
```

**Used by:**
- Analysis Crew: Customer research, competitor analysis, market intelligence
- Finance Crew: Market research for financial modeling

### Optional Providers
```bash
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

### Development Only
```bash
NODE_ENV=development
LOG_LEVEL=debug
```

**See `.env.example` for complete list**

---

## 🔍 Troubleshooting

### Local: "OPENAI_API_KEY not found"
```bash
# Check .env exists
ls -la .env

# If not, create it
cp .env.example .env

# Add your key
echo "OPENAI_API_KEY=sk-your-key" >> .env

# Verify
cat .env | grep OPENAI_API_KEY
```

### Local: "No module named 'crewai'"
```bash
# Reinstall dependencies
uv sync

# Or use venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Production: "Deployment failed"
```bash
# Check authentication
modal setup

# Try deploy again
modal deploy src/modal_app/app.py
```

### Production: "API returns 500 error"
```bash
# Check deployment logs
modal app logs startupai-validation-fastapi-app

# Verify Modal secrets
modal secret list
```

---

## 🏗️ Architecture

### 14 Crews / 45 Agents

> **Single Source**: See [master-architecture/02-organization.md](./master-architecture/02-organization.md) for complete agent details.

**Phases 0-4**: Onboarding, VPC Discovery, Desirability, Feasibility, Viability

### Tool-Equipped Agents
- **Web Research**: Tavily-powered search for market intelligence
- **Financial Analysis**: Industry benchmarks (CAC/LTV) and unit economics calculators
- **Learning System**: Captures validation insights for continuous improvement
- Sequential processing for comprehensive analysis
- All agents use OpenAI GPT models

---

## 🔗 Integration with Other Repos

### App Platform (app.startupai.site)
**Calls Modal via HTTPS:**
```typescript
const response = await fetch(
  'https://chris00walker--startupai-validation-fastapi-app.modal.run/kickoff',
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ project_id, entrepreneur_input })
  }
);
```

### Marketing Site (startupai.site)
- No direct integration
- Marketing site → Auth → App platform → Modal

---

## ✅ Checklist: Environment Setup Complete

- [ ] `.env` created from `.env.example`
- [ ] `OPENAI_API_KEY` added to `.env`
- [ ] `uv sync` completed successfully
- [ ] `modal serve src/modal_app/app.py` executes without errors
- [ ] `modal setup` completed (one-time)
- [ ] `modal deploy src/modal_app/app.py` completes successfully
- [ ] Production API tested with curl
- [ ] `CREW_ANALYZE_URL` configured in app.startupai.site (if overriding)

---

**Last Updated:** 2025-12-02
**Repository:** startupai-crew
**Environment Version:** 1.2.0
**Platform:** Modal Serverless
**Production URL:** https://chris00walker--startupai-validation-fastapi-app.modal.run
