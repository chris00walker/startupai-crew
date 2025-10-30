# StartupAI Crew - Pure CrewAI Automation

**Standalone CrewAI automation for strategic business analysis**

This is a pure, standalone CrewAI automation designed exclusively for deployment on the CrewAI AMP platform. It operates independently with no external dependencies on frontend or backend systems.

---

## 🏗️ Architecture

**6-Agent Value Proposition Design Workflow:**
1. **Onboarding Agent** - Startup Consultant & Interviewer - Guides entrepreneurs through structured onboarding
2. **Customer Researcher** - Customer Insight Analyst - Identifies target customer Jobs, Pains, and Gains
3. **Competitor Analyst** - Market & Competitor Strategist - Maps competitive landscape and differentiation
4. **Value Designer** - Value Proposition Architect - Synthesizes insights into Value Proposition Canvas
5. **Validation Agent** - Experiment Designer & Validation Strategist - Develops 3-tier Validation Roadmap
6. **QA Agent** - Quality Assurance & Model Validation Specialist - Verifies framework compliance

**Pure LLM-Based:**
- No external tools or API dependencies
- Pure reasoning using agent knowledge bases
- Sequential process for comprehensive analysis

---

## 🚀 Quick Start (New Machine Setup)

### 1. Clone Repository
```bash
git clone https://github.com/chris00walker/startupai-crew.git
cd startupai-crew
```

### 2. Install Dependencies
```bash
uv sync
```

### 3. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...
```

### 4. Authenticate with CrewAI
```bash
# First time on new machine
crewai login

# This creates ~/.config/crewai/settings.json with:
# - Organization: StartupAI
# - Org UUID: 8f17470f-7841-4079-860d-de91ed5d1091
```

### 5. Connect to Existing Deployment
```bash
# Check deployment status
crewai deploy status --uuid b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b

# Deploy updates
crewai deploy push --uuid b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b
```

---

## 📦 Deployment Information

**Current Deployment:**
- **UUID:** `b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b`
- **Token:** `f4cc39d92520`
- **Public URL:** `https://startupai-b4d5c1dd-27e2-4163-b9fb-a18ca06ca-4f4192a6.crewai.com`
- **Organization:** StartupAI (`8f17470f-7841-4079-860d-de91ed5d1091`)
- **GitHub Repo:** `chris00walker/startupai-crew`
- **Branch:** `main`
- **Status:** ✅ Online

**Previous Deployment (Deprecated):**
- **UUID:** `4e368758-a5e9-4b5d-9379-cb7621e044bc` (linked to wrong repository)

**Dashboard:** https://app.crewai.com/deployments

---

## 🔑 Authentication & Environment Setup

### Global CrewAI Configuration
CrewAI stores authentication globally (not per-project):

**Location:** `~/.config/crewai/settings.json`

**To authenticate on a new machine:**
```bash
crewai login
```

This will:
1. Open browser for authentication
2. Save credentials to `~/.config/crewai/settings.json`
3. Link to StartupAI organization

### Environment Variables

**For Local Development:**
```bash
# Create .env file from example
cp .env.example .env

# Add your API key
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
```

**For CrewAI AMP Deployment:**
- Go to https://app.crewai.com/deployments
- Select "Startupai" deployment
- Navigate to "Environment Variables" tab
- Add: `OPENAI_API_KEY=sk-your-key-here`

⚠️ **IMPORTANT:** Local `.env` files are NOT used by deployed crews. Environment variables must be set in the CrewAI dashboard.

---

## 📂 Repository Structure

```
startupai-crew/
├── src/
│   └── startupai/
│       ├── __init__.py
│       ├── crew.py              # Main crew definition (@CrewBase)
│       └── config/
│           ├── agents.yaml      # 6 agent configurations
│           └── tasks.yaml       # 6 task definitions
├── .env.example                 # Environment template
├── .gitignore
├── ARCHITECTURE.md              # Detailed architecture docs
├── README.md                    # This file
├── pyproject.toml               # Project metadata (pure crewai)
└── uv.lock                      # Dependency lock file
```

---

## 🎯 Inputs & Outputs

### Inputs
The crew accepts entrepreneur input describing their startup idea:

```python
{
  "entrepreneur_input": "Detailed description of the startup idea, target customers, and business context"
}
```

**Example:**
```python
{
  "entrepreneur_input": "I want to build a B2B SaaS platform that helps small manufacturing companies track their equipment maintenance. My target customers are facilities managers at companies with 50-200 employees who currently use spreadsheets and struggle with unexpected equipment failures."
}
```

### Output
The crew returns structured task outputs (not a file):

1. **Entrepreneur Brief** (JSON) - Structured onboarding data
2. **Customer Profile** - Jobs, Pains, and Gains analysis
3. **Competitor Analysis Report** - Competitive landscape with positioning map
4. **Value Proposition Canvas** - Complete canvas with value statement
5. **3-Tier Validation Roadmap** - Prioritized experiments and metrics
6. **QA Report** - Quality assessment with pass/fail recommendation

**Format:** Task outputs returned as structured data, not markdown files

---

## 🔌 API Integration

### Get Inputs Schema
```bash
curl https://startupai-b4d5c1dd-27e2-4163-b9fb-a18ca06ca-4f4192a6.crewai.com/inputs \
  -H "Authorization: Bearer f4cc39d92520"
```

### Kickoff Crew Execution
```bash
curl -X POST https://startupai-b4d5c1dd-27e2-4163-b9fb-a18ca06ca-4f4192a6.crewai.com/kickoff \
  -H "Authorization: Bearer f4cc39d92520" \
  -H "Content-Type: application/json" \
  -d '{
    "entrepreneur_input": "I want to build a B2B SaaS platform that helps small manufacturing companies track their equipment maintenance. Target customers are facilities managers at 50-200 employee companies."
  }'
```

### Check Execution Status
```bash
curl https://startupai-b4d5c1dd-27e2-4163-b9fb-a18ca06ca-4f4192a6.crewai.com/status/{kickoff_id} \
  -H "Authorization: Bearer f4cc39d92520"
```

---

## 💻 Local Development

### Test Locally
```bash
# Make sure .env file has OPENAI_API_KEY
crewai run
```

### Deploy Changes
```bash
# Commit and push to GitHub
git add .
git commit -m "your changes"
git push origin main

# Deploy to CrewAI AMP
crewai deploy push --uuid b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b
```

### View Logs
```bash
crewai deploy logs --uuid b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b
```

### Check Status
```bash
crewai deploy status --uuid b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b
```

---

## 🆘 Troubleshooting

### "Authentication failed"
```bash
# Re-authenticate
crewai login
```

### "Crew not found"
```bash
# Verify you're using the correct UUID
crewai deploy list
```

### "No OPENAI_API_KEY"
```bash
# For local development: check .env file
cat .env

# For deployed crew: check dashboard environment variables
# https://app.crewai.com/deployments → Startupai → Environment Variables
```

### "Wrong agents showing in dashboard"
This means the deployment is pulling from the wrong repository:
1. Check GitHub integration in CrewAI dashboard
2. Verify it points to `chris00walker/startupai-crew`
3. May need to create fresh deployment if incorrectly configured

---

## 🔗 Related Repositories

- **Marketing Site:** https://github.com/chris00walker/startupai.site
- **Product Platform:** https://github.com/chris00walker/app.startupai.site
- **This Crew:** https://github.com/chris00walker/startupai-crew

**Architecture:** Microservices (frontend → CrewAI AMP API → this crew)

---

## 📄 License

Proprietary - StartupAI Platform

---

## 📞 Support

- **CrewAI Docs:** https://docs.crewai.com
- **CrewAI AMP Dashboard:** https://app.crewai.com
- **GitHub Issues:** https://github.com/chris00walker/startupai-crew/issues
