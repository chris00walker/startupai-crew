# 3-Crew AMP Deployment Guide

This document explains the new 3-crew architecture and how to deploy it to CrewAI AMP.

## Architecture Overview

The original Flow-based architecture has been migrated to a 3-Crew design because CrewAI AMP handles `type = "crew"` reliably but has issues with `type = "flow"`.

```
┌─────────────────────┐     ┌─────────────────────┐     ┌────────────────┐
│   CREW 1: INTAKE    │────▶│ CREW 2: VALIDATION  │────▶│ CREW 3: DECIDE │
│   (4 agents)        │     │ ENGINE (12 agents)  │     │ (3 agents)     │
└─────────────────────┘     └─────────────────────┘     └────────────────┘
```

## Repository Structure

Due to AMP always deploying from git repo root, each crew requires its own repository:

| Crew | Repository | Status |
|------|------------|--------|
| Crew 1: Intake | `startupai-crew` (this repo) | Root-level, ready to deploy |
| Crew 2: Validation | Requires new repo | Code at `startupai-crews/crew-2-validation/` |
| Crew 3: Decision | Requires new repo | Code at `startupai-crews/crew-3-decision/` |

## Crew 1: Intake (This Repo)

### Structure
```
src/intake_crew/
├── __init__.py
├── crew.py          # 4 agents (S1, S2, S3, G1)
├── main.py          # Entry point
└── config/
    ├── agents.yaml  # Agent definitions
    └── tasks.yaml   # 6 tasks including 1 HITL
```

### Agents
- **S1 (FounderOnboardingAgent)**: Parse founder input into structured brief
- **S2 (CustomerResearchAgent)**: Research using JTBD methodology
- **S3 (ValueDesignerAgent)**: Create Value Proposition Canvas
- **G1 (QAAgent)**: Quality assurance and human approval gate

### HITL Checkpoint
- `approve_intake_to_validation`: Human reviews brief and VPC before proceeding

### Tools

Crew 1 agents have the following tools wired:

| Agent | Tools | Purpose |
|-------|-------|---------|
| S2 (CustomerResearch) | `TavilySearchTool`, `CustomerResearchTool` | Web search for customer research |
| G1 (QA) | `InvokeCrewAIAutomationTool` | Triggers Crew 2 after approval |

### Deploy Crew 1
```bash
# Login (one-time)
crewai login

# Deploy
crewai deploy push --uuid <existing-uuid>
# OR create new deployment
crewai deploy create

# Set environment variables in dashboard
# - OPENAI_API_KEY
# - TAVILY_API_KEY (required for web search tools)
# - CREW_2_URL (after deploying Crew 2)
# - CREW_2_BEARER_TOKEN
```

## Crew 2: Validation (Separate Repo Required)

### Create New Repository
1. Create `startupai-crew-validation` repo on GitHub
2. Copy `startupai-crews/crew-2-validation/` contents to new repo root
3. Deploy to AMP

### Agents (12 total)
- **Pulse**: P1 (AdCreative), P2 (Comms), P3 (Analytics)
- **Forge**: F1 (UXUIDesigner), F2 (FrontendDev), F3 (BackendDev)
- **Ledger**: L1 (FinancialController), L2 (LegalCompliance), L3 (EconomicsReviewer)
- **Guardian**: G1 (QA), G2 (Security), G3 (Audit)

### HITL Checkpoints (5 total)
1. `approve_campaign_launch`: Approve ad creatives
2. `approve_spend_increase`: Approve experiment budget
3. `approve_desirability_gate`: Gate from Desirability → Feasibility
4. `approve_feasibility_gate`: Gate from Feasibility → Viability
5. `approve_viability_gate`: Gate from Viability → Decision

## Crew 3: Decision (Separate Repo Required)

### Create New Repository
1. Create `startupai-crew-decision` repo on GitHub
2. Copy `startupai-crews/crew-3-decision/` contents to new repo root
3. Deploy to AMP

### Agents (3 total)
- **C1 (ProductPMAgent)**: Synthesize evidence, propose options
- **C2 (HumanApprovalAgent)**: Present to human for decision
- **C3 (RoadmapWriterAgent)**: Document decisions, update roadmap

### HITL Checkpoint
- `request_human_decision`: Final pivot/proceed decision

## Crew Chaining with InvokeCrewAIAutomationTool

After all crews are deployed, configure the chain:

### In Crew 1 (Intake)
```python
from crewai.tools import InvokeCrewAIAutomationTool

validation_crew_invoker = InvokeCrewAIAutomationTool(
    automation_url=os.getenv("CREW_2_URL"),
    bearer_token=os.getenv("CREW_2_BEARER_TOKEN"),
)
```

### In Crew 2 (Validation)
```python
decision_crew_invoker = InvokeCrewAIAutomationTool(
    automation_url=os.getenv("CREW_3_URL"),
    bearer_token=os.getenv("CREW_3_BEARER_TOKEN"),
)
```

## Data Flow

```
CREW 1 OUTPUT (to Crew 2):
{
  "brief": {...},
  "vpc": {...},
  "customer_profile": {...},
  "qa_result": {"passed": true}
}

CREW 2 OUTPUT (to Crew 3):
{
  "desirability_signal": "STRONG_COMMITMENT",
  "feasibility_signal": "GREEN",
  "viability_signal": "PROFITABLE",
  "learnings": [...]
}

CREW 3 OUTPUT (final):
{
  "recommendation": "proceed",
  "human_decision": "proceed",
  "roadmap_update": {...}
}
```

## Previous Deployment IDs (May Need Recreation)

From previous deploy attempts (before restructure):
- Crew 1: `7a73e75d-b611-4780-8f99-a05fca9b44bb` (Token: `13a07597a155`)
- Crew 2: `06d6a951-67ef-4936-b6d8-6fcaf5801b68` (Token: `6e274e9be0db`)
- Crew 3: `5a4330ef-0394-441d-bc2f-d458fde7ec06` (Token: `b07cee1f4637`)

**Note**: These may need to be recreated since the project structure has changed.

## Archived Code

The original Flow-based architecture has been archived to:
```
archive/flow-architecture/
├── startupai/           # Original Flow code
└── main.py              # Original entry point
```

This can be restored if needed, but the Crew architecture is recommended for AMP deployment.
