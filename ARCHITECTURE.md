# StartupAI Crew - Architecture Documentation

## Overview

**Pure, standalone CrewAI automation for strategic business analysis**

This repository contains a completely decoupled CrewAI automation designed exclusively for deployment on CrewAI AMP. It has zero external dependencies and operates independently of any frontend, backend, or database systems.

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
│           ├── agents.yaml      # 3 agent configurations
│           └── tasks.yaml       # 3 task definitions
├── pyproject.toml               # Minimal dependencies
├── uv.lock                      # Reproducible builds
├── README.md                    # User documentation
├── ARCHITECTURE.md              # This file
└── .gitignore
```

## Agents (3 Total)

### 1. Research Agent
- **Role:** Strategic Research Analyst
- **Goal:** Research and synthesize information to answer strategic questions
- **Tools:** None (pure LLM reasoning)
- **Max Iterations:** 15

### 2. Analysis Agent
- **Role:** Strategic Insights Analyst  
- **Goal:** Analyze research findings and extract actionable insights
- **Tools:** None (pure LLM reasoning)
- **Max Iterations:** 15

### 3. Reporting Agent
- **Role:** Strategic Report Writer
- **Goal:** Generate comprehensive professional reports
- **Tools:** None (pure LLM reasoning)
- **Max Iterations:** 10

## Tasks (Sequential Workflow)

```
┌──────────────┐
│ research_task│  Comprehensive strategic research
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ analysis_task│  SWOT analysis and insights
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  report_task │  Professional markdown report
└──────────────┘
```

## Inputs

The crew accepts two input parameters:

```json
{
  "strategic_question": "The business question to analyze",
  "project_context": "Background information about the project"
}
```

## Output

Professional strategic analysis report saved to `output/strategic_analysis.md`:

```markdown
# Executive Summary
...

# Research Findings
...

# Strategic Insights
...

# SWOT Analysis
...

# Recommendations
...

# Implementation Plan
...

# Conclusion
...
```

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
