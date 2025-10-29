# StartupAI Crew - Pure CrewAI Automation

**Standalone CrewAI automation for strategic business analysis**

This is a pure, standalone CrewAI automation designed exclusively for deployment on the CrewAI AMP platform. It operates independently with no external dependencies on frontend or backend systems.

---

## 🏗️ Architecture

**6-Agent Strategic Analysis Workflow:**
1. **Research Coordinator** - Evidence discovery and data collection
2. **Strategic Analyst** - Pattern recognition and insights
3. **Evidence Validator** - Quality verification and credibility assessment
4. **Strategic Synthesizer** - Insight combination into narratives
5. **Report Generator** - Professional report creation
6. **Workflow Orchestrator** - Coordination and quality control

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
crewai deploy status --uuid 4e368758-a5e9-4b5d-9379-cb7621e044bc

# Deploy updates
crewai deploy push --uuid 4e368758-a5e9-4b5d-9379-cb7621e044bc
```

---

## 📦 Deployment Information

**Current Deployment:**
- **UUID:** `4e368758-a5e9-4b5d-9379-cb7621e044bc`
- **Token:** `d2cb5ab382b5`
- **Public URL:** `https://startupai-4e368758-a5e9-4b5d-9379-cb7621e04-7f34a57c.crewai.com`
- **Organization:** StartupAI (`8f17470f-7841-4079-860d-de91ed5d1091`)
- **GitHub Repo:** `chris00walker/startupai-crew`
- **Branch:** `main`

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
The crew accepts two input parameters:

```json
{
  "strategic_question": "The business question to analyze",
  "project_context": "Background information about the project/company"
}
```

**Example:**
```json
{
  "strategic_question": "Should we expand into the European market?",
  "project_context": "B2B SaaS, $5M ARR, US-based, 50 employees"
}
```

### Output
Professional strategic analysis report saved to `output/strategic_analysis.md`:

- Executive Summary
- Research Findings
- Strategic Insights
- SWOT Analysis
- Recommendations
- Implementation Plan
- Conclusion

---

## 🔌 API Integration

### Get Inputs Schema
```bash
curl https://startupai-4e368758-a5e9-4b5d-9379-cb7621e04-7f34a57c.crewai.com/inputs \
  -H "Authorization: Bearer d2cb5ab382b5"
```

### Kickoff Crew Execution
```bash
curl -X POST https://startupai-4e368758-a5e9-4b5d-9379-cb7621e04-7f34a57c.crewai.com/kickoff \
  -H "Authorization: Bearer d2cb5ab382b5" \
  -H "Content-Type: application/json" \
  -d '{
    "strategic_question": "Should we expand into the European market?",
    "project_context": "B2B SaaS, $5M ARR, US-based"
  }'
```

### Check Execution Status
```bash
curl https://startupai-4e368758-a5e9-4b5d-9379-cb7621e04-7f34a57c.crewai.com/status/{kickoff_id} \
  -H "Authorization: Bearer d2cb5ab382b5"
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
crewai deploy push --uuid 4e368758-a5e9-4b5d-9379-cb7621e044bc
```

### View Logs
```bash
crewai deploy logs --uuid 4e368758-a5e9-4b5d-9379-cb7621e044bc
```

### Check Status
```bash
crewai deploy status --uuid 4e368758-a5e9-4b5d-9379-cb7621e044bc
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
