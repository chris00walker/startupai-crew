# StartupAI Organizational Structure

## Overview

StartupAI is run by a team of AI Founders - six co-equal team members organized around the customer. They collaborate as peers to deliver strategic business analysis and validation. This document is the **single source of truth** for agent names, roles, and structure.

## Design Philosophy

### Startup Reality
Startups are temporary organizations in search of sustainable business models. The flat structure is intentional - it's all hands on deck in the search for customers, the development of products, and the formation of a winning team.

### Customer-Centric Model
Inspired by Edwin Korver's RoundMap® Customer Dynamics Lifecycle, StartupAI places the customer at the center rather than using a traditional linear funnel. All founders orient around the customer's journey and needs, engaging adaptively as required.

### Continuous Learning
AI organizations have a structural advantage over human-led companies: they learn from every interaction. This is StartupAI's moat. Learning isn't delegated to a role - it's inherent to the system.

## The AI Founders Team

### Founding Team (Flat Structure)
Six co-equal founders organized around the customer.

| Founder | Title | Responsibility |
|---------|-------|----------------|
| **Sage** | Chief Strategy Officer | Business Model Canvas, Value Proposition Design, market analysis, assumption identification |
| **Forge** | Chief Technology Officer | MVP code generation, technical architecture, deployment automation |
| **Pulse** | Chief Growth Officer | Ad campaigns, user acquisition, A/B testing, analytics tracking |
| **Compass** | Chief Product Officer | Evidence synthesis, pivot vs proceed analysis, recommendations |
| **Guardian** | Chief Governance Officer | Governance monitoring, pattern detection, security oversight |
| **Ledger** | Chief Financial Officer | Unit economics, revenue model design, pricing strategy, runway projections |

### PSIU Balance (Organizational Physics)
Following Lex Sisney's framework, the team covers all four organizational styles:

| Style | Function | Founders |
|-------|----------|----------|
| **Producer** | Drive results, ship things | Forge, Pulse |
| **Stabilizer** | Systems, consistency, discipline | Guardian, Ledger |
| **Innovator** | Strategy, vision, change | Sage |
| **Unifier** | Integration, synthesis | Compass |

### Ledger's Dual Responsibilities

**For StartupAI's clients** (the startups being analyzed):
- Unit economics analysis
- Revenue model design
- Pricing strategy recommendations
- Runway/burn rate projections
- Funding strategy alignment

**For StartupAI itself**:
- Resource allocation across founders
- ROI of capability investments
- Pricing of the service

## Customer-Centric Structure

```
                    Sage
                  (Strategy)
                      ↕

   Ledger ←───────────────────────→ Forge
  (Finance)                      (Technology)
      ↕                               ↕

            ┌─────────────┐
            │  CUSTOMER   │
            │  (Center)   │
            └─────────────┘

      ↕                               ↕
  Guardian ←───────────────────────→ Pulse
(Governance)                       (Growth)

                      ↕
                  Compass
                  (Product)
```

**Key principle**: The customer is the integrating point. All founders maintain awareness of the customer's journey and contribute when relevant - not waiting in sequence for their turn.

## Engagement Model

### Traditional Funnel (What We Don't Do)
```
Marketing → Sales → Product → Support → Renewal
```
Linear handoffs create entropy and lose customer context.

### Customer Orbit (What We Do)
All founders engage based on customer needs:

- **Early journey**: Sage leads (strategy, desirability)
- **Building phase**: Forge leads (feasibility, MVP)
- **Validation phase**: Ledger leads (viability), Pulse leads (growth testing)
- **Decision point**: Compass synthesizes all evidence
- **Throughout**: Guardian monitors governance, Ledger monitors costs

### Derisking Sequence
Following lean startup principles:
1. **Desirability** - Do customers want it? (Sage)
2. **Feasibility** - Can we build it? (Forge)
3. **Viability** - Can we make money? (Ledger)

Note: Ledger monitors cost structure throughout, then does deep viability analysis at the right moment.

## Workflow Agents (Task Executors)

Narrowly-focused agents that execute specific tasks. These are the "temps" who do the grunt work within each founder's domain.

| Workflow Agent | Founder | Task Focus |
|----------------|---------|------------|
| **Onboarding Agent** | Sage | Structured interviews, business context extraction |
| **Customer Researcher** | Sage | Jobs, Pains, Gains analysis using JTBD framework |
| **Competitor Analyst** | Sage | Competitive landscape mapping, differentiation |
| **Value Designer** | Forge | Value Proposition Canvas creation |
| **Validation Agent** | Compass | 3-tier experiment roadmap, validation planning |
| **QA Agent** | Guardian | Framework compliance, logical consistency |

**Note**: Pulse and Ledger currently have no workflow agents assigned - they represent future capability expansion.

## CrewAI Implementation

The workflow agents are implemented in CrewAI:
- `config/agents.yaml`: `onboarding_agent`, `customer_researcher`, etc.
- `config/tasks.yaml`: `onboarding_task`, `customer_research_task`, etc.

The founder layer is a conceptual model that maps to these functional implementations.

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

### When to Use Founder Names
- Marketing materials (public-facing)
- User interfaces (explaining what's happening)
- Team introductions

**Example**: "Sage is analyzing your strategic positioning..."

### When to Use Workflow Agent Names
- Technical implementation
- API responses
- Logs and debugging
- Configuration files

**Example**: `"agent": "onboarding_agent", "task": "structured_interview"`

## Future Expansion

### Additional Workflow Agents (Planned)
As capabilities grow, founders will leverage additional workflow agents:

| Founder | Future Workflow Agents |
|---------|------------------------|
| Sage | Strategy Advisor, Decision Arbitrator |
| Forge | Tech Evaluator, Architecture Reviewer |
| Pulse | Campaign Runner, Analytics Agent, A/B Tester |
| Compass | Evidence Collector, Pivot Analyzer |
| Guardian | Risk Assessor, Compliance Checker |
| Ledger | Unit Economics Analyzer, Pricing Optimizer |

---

## Change Log

| Date | Change | Rationale |
|------|--------|-----------|
| 2025-11-20 | Added Ledger as 6th founder (CFO) | Financial viability accountability |
| 2025-11-20 | Restructured to customer-centric model | RoundMap-inspired, customer as integrating point |
| 2025-11-20 | Added PSIU balance documentation | Organizational Physics principles |
| 2025-11-20 | Corrected founder roles to match marketing site | Align with startupai.site team page |
| 2025-11-20 | Reorganized to flat team structure | Reflects startup reality - co-equal founders |
| 2025-11-19 | Added founder personas | Company run by AI Founders |
