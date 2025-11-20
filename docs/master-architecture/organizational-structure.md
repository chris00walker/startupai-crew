# StartupAI Organizational Structure

## Overview

StartupAI is run by AI Founders - a C-suite of AI executives who lead functional teams of specialized agents. This document is the **single source of truth** for agent names, roles, and hierarchy.

## The AI Founders Team

### Executive Layer (C-Suite)
Strategic decision-makers who oversee functional areas.

| Executive | Title | Responsibility |
|-----------|-------|----------------|
| **Sage** | CEO | Strategic vision, positioning, overall direction |
| **Forge** | CTO | Technical architecture, product design, feasibility |
| **Pulse** | CMO | Market analysis, customer insights, competitive intelligence |
| **Compass** | COO | Operations planning, validation execution, resource allocation |
| **Guardian** | Chief of Staff | Quality assurance, meta-governance, consistency |

### Functional Layer (Agents)
Specialized workers who execute tasks within their domain.

| Agent | Reports To | Role |
|-------|-----------|------|
| **Onboarding Agent** | Sage (CEO) | Structured interviews, business context extraction |
| **Customer Researcher** | Pulse (CMO) | Jobs, Pains, Gains analysis using JTBD framework |
| **Competitor Analyst** | Pulse (CMO) | Competitive landscape mapping, differentiation |
| **Value Designer** | Forge (CTO) | Value Proposition Canvas creation, product/service design |
| **Validation Agent** | Compass (COO) | 3-tier experiment roadmap, validation planning |
| **QA Agent** | Guardian (Chief of Staff) | Framework compliance, logical consistency, quality gates |

## Organizational Chart

```
                          ┌─────────┐
                          │  Sage   │
                          │  (CEO)  │
                          └────┬────┘
                               │
        ┌──────────┬───────────┼───────────┬──────────┐
        │          │           │           │          │
   ┌────┴────┐ ┌───┴───┐ ┌────┴────┐ ┌────┴────┐ ┌───┴────┐
   │  Forge  │ │ Pulse │ │ Compass │ │Guardian │ │  Sage  │
   │  (CTO)  │ │ (CMO) │ │  (COO)  │ │ (CoS)   │ │ Direct │
   └────┬────┘ └───┬───┘ └────┬────┘ └────┬────┘ └───┬────┘
        │          │          │           │          │
        ▼          ▼          ▼           ▼          ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌────────┐ ┌─────────┐
   │  Value  │ │Customer │ │Validation│ │   QA   │ │Onboarding│
   │Designer │ │Researcher│ │  Agent  │ │ Agent  │ │  Agent  │
   └─────────┘ └─────────┘ └─────────┘ └────────┘ └─────────┘
               ┌─────────┐
               │Competitor│
               │ Analyst │
               └─────────┘
```

## Workflow Execution

When an analysis runs, executives orchestrate their functional agents:

### Value Proposition Design Workflow (Current)

```
1. Sage → Onboarding Agent
   "Gather business context and startup details"

2. Pulse → Customer Researcher
   "Identify target customer Jobs, Pains, Gains"

3. Pulse → Competitor Analyst
   "Map competitive landscape and differentiation"

4. Forge → Value Designer
   "Synthesize into Value Proposition Canvas"

5. Compass → Validation Agent
   "Create 3-tier validation roadmap"

6. Guardian → QA Agent
   "Verify framework compliance and quality"
```

### Task Output Chain

```
Onboarding Agent    → Entrepreneur Brief (JSON)
        ↓
Customer Researcher → Customer Profile (Jobs/Pains/Gains)
        ↓
Competitor Analyst  → Competitive Analysis Report
        ↓
Value Designer      → Value Proposition Canvas
        ↓
Validation Agent    → 3-Tier Validation Roadmap
        ↓
QA Agent           → Quality Report (Pass/Fail)
```

## Naming Conventions

### When to Use C-Suite Names
- Marketing materials (public-facing)
- User interfaces (explaining what's happening)
- Strategic documentation
- Team introductions

**Example**: "Sage, our CEO Agent, will review your strategic positioning..."

### When to Use Functional Names
- Technical implementation
- API responses
- Logs and debugging
- Configuration files

**Example**: `"agent": "onboarding_agent", "task": "structured_interview"`

### API Response Mapping

```json
{
  "executive": "Sage",
  "agent": "onboarding_agent",
  "task": "onboarding_task",
  "status": "completed"
}
```

## Future Expansion

### Additional Agents (Planned)
As StartupAI grows, executives may lead additional agents:

| Executive | Future Agents |
|-----------|---------------|
| Sage | Strategy Advisor, Decision Arbitrator |
| Forge | Tech Evaluator, Architecture Reviewer |
| Pulse | Market Monitor, Customer Interviewer |
| Compass | Resource Allocator, Timeline Manager |
| Guardian | Risk Assessor, Compliance Checker |

### Multi-Workflow Support
Different workflows may use different agent combinations:

- **Quick Validation**: Onboarding → Customer Researcher → Validation Agent
- **Deep Analysis**: Full 6-agent workflow
- **Competitive Focus**: Competitor Analyst → Value Designer → QA Agent

## Integration Notes

### Marketing Site (`startupai.site`)
Should display C-suite personas for user understanding:
- "Meet the AI Founders Team"
- "Sage is analyzing your market positioning..."

### Product App (`app.startupai.site`)
Should use both for appropriate context:
- UI: "Forge (CTO) is designing your value proposition"
- Logs: `[value_designer] Processing task...`

### CrewAI Implementation (`startupai-crew`)
Configuration uses functional names:
- `config/agents.yaml`: `onboarding_agent`, `customer_researcher`, etc.
- `config/tasks.yaml`: `onboarding_task`, `customer_research_task`, etc.

---

## Change Log

| Date | Change | Rationale |
|------|--------|-----------|
| 2025-11-20 | Established C-suite → Agent hierarchy | Unified naming across repos |
| 2025-11-19 | Added C-suite personas | Company run by AI Founders |
