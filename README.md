# StartupAI Crew - Pure CrewAI Automation

**Standalone CrewAI automation for strategic business analysis**

This is a pure, standalone CrewAI automation designed exclusively for deployment on the CrewAI AMP platform. It has no external dependencies and operates independently of any frontend or backend systems.

## Architecture

**Pure LLM-Based Analysis:**
- 3 specialized agents using pure reasoning (no external tools)
- Sequential workflow: Research → Analysis → Report
- Standalone automation with no database or API dependencies

## Agents

1. **Research Agent** - Strategic research and information synthesis
2. **Analysis Agent** - Pattern recognition and insights extraction  
3. **Reporting Agent** - Professional report generation

## Deployment

**CrewAI AMP Deployment:**
```bash
crewai deploy push --uuid <deployment-uuid>
```

**Repository Structure:**
```
startupai-crew/
├── src/
│   └── startupai/
│       ├── crew.py           # Main crew definition
│       ├── __init__.py
│       └── config/
│           ├── agents.yaml   # Agent configurations
│           └── tasks.yaml    # Task definitions
├── pyproject.toml            # Project metadata & dependencies
├── uv.lock                   # Dependency lock file
└── README.md
```

## Inputs

- `strategic_question`: The business question to analyze
- `project_context`: Background information about the project

## Output

Professional strategic analysis report in markdown format, saved to `output/strategic_analysis.md`

## Integration

This crew is designed to be called via CrewAI AMP's REST API:

```bash
# Get inputs schema
curl https://your-crew-url.crewai.com/inputs

# Kickoff crew execution
curl -X POST https://your-crew-url.crewai.com/kickoff \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"strategic_question": "...", "project_context": "..."}'
```

## Development

**Install dependencies:**
```bash
uv sync
```

**Run locally:**
```bash
crewai run
```

## License

Proprietary - StartupAI Platform
