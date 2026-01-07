# Multi-Environment Setup Guide

**StartupAI Crew** - CrewAI Automation Environment Management

---

## 🎯 Overview

This repository is a **pure CrewAI automation** with two environments:

| Environment | Purpose | Platform | Config File |
|------------|---------|----------|-------------|
| **Local** | Development and testing | Local machine | `.env` |
| **Production** | Live AI workflows | CrewAI AMP Cloud | CrewAI Dashboard |

**Note:** There is no staging environment for CrewAI deployments - they run either locally or in production on CrewAI AMP platform.

---

## 🚀 Quick Start Commands

### Local Development & Testing
```bash
# Install dependencies
uv sync

# Run crew locally
crewai run

# Test with custom input
crewai run --input "Analyze startup idea: SaaS for developers"
```

**Use for:** Testing agent workflows, debugging tools, validating prompts

---

### Production Deployment
```bash
# Deploy to CrewAI AMP
crewai deploy push

# Or deploy with specific UUID
crewai deploy push --uuid 6b1e5c4d-e708-4921-be55-08fcb0d1e94b

# Check deployment status
crewai deploy status
```

**Use for:** Live AI workflows accessible via HTTPS API

---

## 📁 Environment File Structure

```
startupai-crew/
├── .env.example          # Template (committed to git)
├── .env                  # Local development (gitignored) ⭐ YOU CREATE THIS
├── src/
│   └── startupai/
│       ├── flows/                      # Innovation Physics orchestration
│       │   ├── state_schemas.py        # Validation signals & state
│       │   └── founder_validation_flow.py  # Non-linear routers
│       ├── crews/                      # 8 specialized crews
│       │   ├── service/
│       │   ├── analysis/
│       │   ├── build/
│       │   ├── growth/
│       │   ├── synthesis/              # Pivot decision logic
│       │   ├── finance/
│       │   └── governance/
│       └── main.py                     # Entry point
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

### Production (CrewAI AMP Dashboard)

**Purpose:** Live AI workflows accessible via HTTPS

**Configuration Location:** CrewAI Dashboard  
**URL:** https://app.crewai.com/deployments

**Current Deployment:**
- **UUID:** `6b1e5c4d-e708-4921-be55-08fcb0d1e94b`
- **Token:** `<your-deployment-token>` (stored in CrewAI dashboard)
- **Public API:** `https://startupai-6b1e5c4d-e708-4921-be55-08fcb0d1e-922bcddb.crewai.com`
- **Status:** 🟢 Online
- **Organization:** StartupAI (`8f17470f-7841-4079-860d-de91ed5d1091`)

**Environment Variables Set in Dashboard:**
- `OPENAI_API_KEY` - Primary LLM provider
- `ANTHROPIC_API_KEY` - Fallback LLM provider (optional)
- `TAVILY_API_KEY` - Web research for market intelligence (recommended)
- `SUPABASE_URL` - Supabase project URL for persistence (`https://eqxropalhxjeyvfcoyxg.supabase.co`)
- `SUPABASE_KEY` - Supabase service role key for direct database access
- `STARTUPAI_WEBHOOK_URL` - Unified webhook for all flow results (`https://app.startupai.site/api/crewai/webhook`)
- `STARTUPAI_WEBHOOK_BEARER_TOKEN` - Bearer token for webhook authentication (shared with product app)
- `NETLIFY_ACCESS_TOKEN` - Netlify personal access token for landing page deployment

**Deployment:** Automatic on `crewai deploy push` or GitHub integration

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

### Production (CrewAI AMP)

**Set via Dashboard:**
1. Visit: https://app.crewai.com/deployments
2. Click deployment: `6b1e5c4d-e708-4921-be55-08fcb0d1e94b`
3. Go to: Settings → Environment Variables
4. Add: `OPENAI_API_KEY` = `sk-your-key`
5. Save and redeploy

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
# Should see agents executing tasks (8 crews, 18 agents when fully deployed)

# 4. Check for errors
# All tasks should complete successfully
```

### Test Production Deployment
```bash
# 1. Deploy
crewai deploy push

# 2. Get API endpoint from output
# Public API URL: https://startupai-...crewai.com

# 3. Test via curl
curl -X POST https://startupai-6b1e5c4d-e708-4921-be55-08fcb0d1e-922bcddb.crewai.com \
  -H "Content-Type: application/json" \
  -d '{"startup": "SaaS for developers"}'

# 4. Verify response contains analysis
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

# 4. Authenticate with CrewAI
crewai login
# Opens browser, logs you into StartupAI organization

# 5. Test locally
crewai run

# 6. Deploy to production
crewai deploy push
```

### Regular Development Workflow
```bash
# 1. Make changes to agents or tasks
nano src/startupai_crew/config/agents.yaml

# 2. Test locally
crewai run

# 3. If works, commit
git add .
git commit -m "feat: improved agent prompts"
git push

# 4. Deploy to production
crewai deploy push

# 5. Verify deployment
crewai deploy status
```

---

## 🌐 CrewAI AMP Authentication

### Global Configuration
CrewAI stores authentication **globally** (not per-project):

**Location:** `~/.config/crewai/settings.json`

**Content:**
```json
{
  "organization_id": "8f17470f-7841-4079-860d-de91ed5d1091",
  "organization_name": "StartupAI",
  "user_email": "your@email.com"
}
```

### Login Process
```bash
# First time on new machine
crewai login

# This will:
# 1. Open browser
# 2. Authenticate with CrewAI
# 3. Save credentials to ~/.config/crewai/settings.json
# 4. Link to StartupAI organization
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
crewai whoami

# Should show:
# Organization: StartupAI
# UUID: 8f17470f-7841-4079-860d-de91ed5d1091

# If not authenticated
crewai login

# Try deploy again
crewai deploy push
```

### Production: "API returns 500 error"
```bash
# Check deployment logs
crewai deploy logs

# Verify environment variables set in dashboard
# Visit: https://app.crewai.com/deployments
# Check: Settings → Environment Variables
# Ensure OPENAI_API_KEY is set
```

---

## 🏗️ Architecture

### 8 Crews / 18 Agents

> **Single Source**: See [master-architecture/02-organization.md](./master-architecture/02-organization.md) for complete agent details.

**Phase 1**: Service Crew, Analysis Crew, Governance Crew
**Phase 2**: Build Crew, Growth Crew, Synthesis Crew
**Phase 3**: Finance Crew, Enhanced Governance Crew

### Tool-Equipped Agents
- **Web Research**: Tavily-powered search for market intelligence
- **Financial Analysis**: Industry benchmarks (CAC/LTV) and unit economics calculators
- **Learning System**: Captures validation insights for continuous improvement
- Sequential processing for comprehensive analysis
- All agents use OpenAI GPT models

---

## 🔗 Integration with Other Repos

### App Platform (app.startupai.site)
**Calls CrewAI via HTTPS:**
```typescript
// frontend/src/lib/agentuity.ts
const AGENTUITY_AGENT_URL = process.env.AGENTUITY_AGENT_URL;

const response = await fetch(AGENTUITY_AGENT_URL, {
  method: 'POST',
  body: JSON.stringify({ startup: userInput })
});
```

**Environment Variable:**
```bash
# app.startupai.site/frontend/.env.local
AGENTUITY_AGENT_URL=https://startupai-6b1e5c4d-e708-4921-be55-08fcb0d1e-922bcddb.crewai.com
```

### Marketing Site (startupai.site)
- No direct integration
- Marketing site → Auth → App platform → CrewAI

---

## ✅ Checklist: Environment Setup Complete

- [ ] `.env` created from `.env.example`
- [ ] `OPENAI_API_KEY` added to `.env`
- [ ] `uv sync` completed successfully
- [ ] `crewai run` executes without errors
- [ ] `crewai login` completed (one-time)
- [ ] `crewai whoami` shows StartupAI organization
- [ ] `crewai deploy push` completes successfully
- [ ] Production API tested with curl
- [ ] `AGENTUITY_AGENT_URL` configured in app.startupai.site

---

**Last Updated:** 2025-12-02
**Repository:** startupai-crew
**Environment Version:** 1.2.0
**Platform:** CrewAI AMP (Cloud-Hosted)
**Deployment UUID:** 6b1e5c4d-e708-4921-be55-08fcb0d1e94b
