# StartupAI Crew - Architecture Documentation

## Overview

**Pure, standalone CrewAI automation for Value Proposition Design**

This repository contains a completely decoupled CrewAI automation designed exclusively for deployment on CrewAI AMP. It implements a 6-agent workflow for helping entrepreneurs design and validate value propositions. It has zero external dependencies and operates independently of any frontend, backend, or database systems.

## Design Principles

### 1. **Pure Automation**
- No frontend coupling
- No backend integration
- No database dependencies
- No custom tools requiring external APIs
- Pure LLM-based reasoning and analysis

### 2. **Minimal Dependencies**
```toml
dependencies = [
    "crewai>=0.80.0",  # Only core CrewAI package
]
```

### 3. **Microservices Architecture**
```
┌─────────────────────┐
│  startupai.site     │  ← Marketing site (separate repo)
└─────────────────────┘

┌─────────────────────┐
│ app.startupai.site  │  ← Product platform (separate repo)
│  (Next.js Frontend) │     Calls CrewAI via REST API
└──────────┬──────────┘
           │ HTTP/REST
           ▼
┌─────────────────────┐
│   CrewAI AMP        │  ← Managed platform
│                     │
│  ┌───────────────┐  │
│  │ startupai-crew│  │  ← THIS REPOSITORY (pure automation)
│  └───────────────┘  │
└─────────────────────┘
```

## Repository Structure

```
startupai-crew/
├── src/
│   └── startupai/
│       ├── __init__.py
│       ├── crew.py              # Main crew definition (@CrewBase)
│       └── config/
│           ├── agents.yaml      # 6 agent configurations
│           └── tasks.yaml       # 6 task definitions
├── pyproject.toml               # Minimal dependencies (crewai>=0.80.0)
├── uv.lock                      # Reproducible builds
├── README.md                    # User documentation
├── ARCHITECTURE.md              # This file
├── CLAUDE.md                    # AI assistant instructions
├── ENVIRONMENTS.md              # Deployment environment guide
└── .gitignore
```

## Agents (6 Total)

**Purpose:** Guides entrepreneurs through Value Proposition Design using proven frameworks (Value Proposition Canvas, Jobs-to-be-Done, Strategyzer methodology)

### 1. Onboarding Agent
- **Role:** Startup Consultant & Interviewer
- **Goal:** Guide entrepreneurs through structured onboarding to extract essential business context
- **Tools:** None (pure LLM reasoning)
- **Max Iterations:** 10
- **Focus:** Collect startup idea, target customers, problem understanding, and business context

### 2. Customer Researcher
- **Role:** Customer Insight Analyst
- **Goal:** Identify target customer Jobs, Pains, and Gains following JTBD framework
- **Tools:** None (pure LLM reasoning)
- **Max Iterations:** 10
- **Focus:** Customer profile with Jobs (functional, social, emotional), Pains (obstacles, risks, undesired outcomes), Gains (required, expected, desired)

### 3. Competitor Analyst
- **Role:** Market & Competitor Strategist
- **Goal:** Map competitive landscape and identify differentiation opportunities
- **Tools:** None (pure LLM reasoning)
- **Max Iterations:** 8
- **Focus:** Competitor analysis report, positioning map, white space identification

### 4. Value Designer
- **Role:** Value Proposition Architect
- **Goal:** Synthesize insights into complete Value Proposition Canvas
- **Tools:** None (pure LLM reasoning)
- **Max Iterations:** 10
- **Focus:** Products & Services, Pain Relievers, Gain Creators, Value Proposition Statement

### 5. Validation Agent
- **Role:** Experiment Designer & Validation Strategist
- **Goal:** Develop 3-tier Validation Roadmap with prioritized experiments
- **Tools:** None (pure LLM reasoning)
- **Max Iterations:** 8
- **Focus:**
  - **Tier 1:** Smoke tests (landing pages, prototypes, pre-orders)
  - **Tier 2:** Problem interviews, solution interviews
  - **Tier 3:** MVPs, pilot programs, concierge tests
  - Includes success metrics and validation criteria

### 6. QA Agent
- **Role:** Quality Assurance & Model Validation Specialist
- **Goal:** Verify framework compliance and logical consistency
- **Tools:** None (pure LLM reasoning)
- **Max Iterations:** 5
- **Focus:** Quality assessment, completeness check, pass/fail recommendation with improvement suggestions
- **Tools:** None (pure LLM reasoning)
- **Max Iterations:** 10

## Tasks (Sequential Workflow)

```
┌────────────────────┐
│ onboarding_task    │  Structured interview with entrepreneur
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ customer_research  │  Jobs, Pains, Gains analysis
│ _task              │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ competitor_        │  Competitive landscape mapping
│ analysis_task      │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ value_design_task  │  Value Proposition Canvas creation
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ validation_task    │  3-tier experiment roadmap
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ qa_task            │  Quality assurance check
└────────────────────┘
```

## Inputs

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

## Output

The crew returns structured task outputs (not a file):

1. **Entrepreneur Brief** (JSON) - Structured onboarding data
2. **Customer Profile** - Jobs, Pains, and Gains analysis
3. **Competitor Analysis Report** - Competitive landscape with positioning map
4. **Value Proposition Canvas** - Complete canvas with value statement
5. **3-Tier Validation Roadmap** - Prioritized experiments and metrics
6. **QA Report** - Quality assessment with pass/fail recommendation

**Format:** Task outputs returned as structured data via CrewAI API

## Deployment

### Initial Deployment

```bash
# From project root
crewai deploy create

# Follow prompts for:
# - Crew name: startupai
# - GitHub repository: chris00walker/startupai-crew
```

### Redeployment

```bash
crewai deploy push --uuid <deployment-uuid>
```

### GitHub Auto-Deploy

Configure in CrewAI AMP Dashboard:
1. Go to https://app.crewai.com/deployments
2. Select "startupai" crew
3. Settings → GitHub Integration
4. Connect repository: `chris00walker/startupai-crew`
5. Branch: `main`
6. Enable auto-deploy on push

## API Integration

### Get Inputs Schema
```bash
curl https://your-crew-url.crewai.com/inputs \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Kickoff Execution
```bash
curl -X POST https://your-crew-url.crewai.com/kickoff \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "strategic_question": "How should we expand into the European market?",
    "project_context": "B2B SaaS company, $5M ARR, US-based"
  }'
```

### Check Status
```bash
curl https://your-crew-url.crewai.com/status/{kickoff_id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Development

### Local Setup

```bash
# Install dependencies
uv sync

# Run crew locally
crewai run
```

### Testing

```bash
# Unit tests (if added)
pytest tests/

# Integration test via CrewAI CLI
crewai test
```

## Benefits of This Architecture

### ✅ Clean Separation
- CrewAI automation is completely decoupled
- Frontend integration happens via REST API only
- No shared code or dependencies

### ✅ Independent Deployment
- Deploy crew changes without touching frontend
- Deploy frontend changes without touching crew
- True microservices independence

### ✅ Minimal Complexity
- Single dependency (crewai)
- No external tools to maintain
- Pure LLM-based reasoning

### ✅ Easy GitHub Auto-Deploy
- Dedicated repository for CrewAI
- Push to main → automatic deployment
- No mixed concerns in deployment pipeline

### ✅ Scalability
- CrewAI AMP handles scaling automatically
- No infrastructure to manage
- Pay only for execution time

## Future Enhancements

### Phase 1: Add Tools (Optional)
Once pure automation works, can add:
- Web search tool (built-in CrewAI tools)
- File operations tool
- Custom lightweight tools

### Phase 2: Advanced Features
- Streaming responses
- Webhook notifications
- Custom error handling
- Metrics and monitoring

### Phase 3: Multi-Crew System
- Specialized crews for different domains
- Crew orchestration
- Cross-crew communication

## Migration Notes

### From app.startupai.site Integration

**Before:** Tightly coupled
```
app.startupai.site/
├── frontend/        (Next.js)
├── backend/         (FastAPI + CrewAI)
├── src/startupai/   (CrewAI crew)
└── database/        (Supabase)
```

**After:** Loosely coupled microservices
```
app.startupai.site/      (Next.js only)
  └── calls REST API

startupai-crew/          (Pure CrewAI)
  └── standalone automation
```

### Integration Points

**Frontend → CrewAI:**
```typescript
// app.startupai.site/frontend/src/lib/crewai.ts
const response = await fetch(CREWAI_API_URL + '/kickoff', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${CREWAI_TOKEN}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    strategic_question: userInput.question,
    project_context: userInput.context
  })
});
```

## Support

For issues or questions:
- CrewAI Docs: https://docs.crewai.com
- CrewAI AMP Dashboard: https://app.crewai.com
- GitHub Issues: https://github.com/chris00walker/startupai-crew/issues

## License

Proprietary - StartupAI Platform
