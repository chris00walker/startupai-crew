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
crewai deploy push --uuid b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b

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
│   └── startupai_crew/
│       ├── config/
│       │   ├── agents.yaml    # Agent definitions
│       │   └── tasks.yaml     # Task definitions
│       └── crew.py            # Main crew orchestration
└── pyproject.toml            # Python dependencies
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
- **UUID:** `b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b`
- **Token:** `f4cc39d92520`
- **Public API:** `https://startupai-b4d5c1dd-27e2-4163-b9fb-a18ca06ca-4f4192a6.crewai.com`
- **Status:** 🟢 Online
- **Organization:** StartupAI (`8f17470f-7841-4079-860d-de91ed5d1091`)

**Environment Variables Set in Dashboard:**
- `OPENAI_API_KEY` - Primary LLM provider
- `ANTHROPIC_API_KEY` - Fallback LLM provider (optional)

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
2. Click deployment: `b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b`
3. Go to: Settings → Environment Variables
4. Add: `OPENAI_API_KEY` = `sk-your-key`
5. Save and redeploy

**Security:**
- Secrets encrypted at rest
- Never exposed in logs
- Automatically injected at runtime

---

## 🧪 Testing

### Test Locally Before Deployment
```bash
# 1. Ensure .env exists with OPENAI_API_KEY
cat .env | grep OPENAI_API_KEY

# 2. Run crew
crewai run

# 3. Verify output
# Should see 6 agents executing tasks

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
curl -X POST https://startupai-b4d5c1dd-27e2-4163-b9fb-a18ca06ca-4f4192a6.crewai.com \
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

### 6-Agent Workflow
```
Research Coordinator → Evidence Discovery
Strategic Analyst → Pattern Recognition  
Evidence Validator → Quality Verification
Strategic Synthesizer → Insight Combination
Report Generator → Professional Reports
Workflow Orchestrator → Quality Control
```

### Pure LLM-Based
- No external tools or APIs
- Pure reasoning using agent knowledge bases
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
AGENTUITY_AGENT_URL=https://startupai-b4d5c1dd-27e2-4163-b9fb-a18ca06ca-4f4192a6.crewai.com
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

**Last Updated:** October 30, 2025  
**Repository:** startupai-crew  
**Environment Version:** 1.0.0  
**Platform:** CrewAI AMP (Cloud-Hosted)  
**Deployment UUID:** b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b
