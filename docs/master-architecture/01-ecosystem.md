---
purpose: Three-service ecosystem architecture overview
status: active
last_reviewed: 2026-01-07
vpd_compliance: true
---

# StartupAI Ecosystem Architecture

## Overview

StartupAI is a three-service ecosystem that delivers **Value Proposition Design (VPD)** validation through AI Founders. The CrewAI engine serves as the decision-making brain, with two web interfaces providing customer access and result delivery.

> **VPD Framework**: This ecosystem implements the Strategyzer methodology. See [03-methodology.md](./03-methodology.md) for framework details.

```
                    ┌─────────────────────┐
                    │   AI Founders Core  │
                    │   (startupai-crew)  │
                    │  CrewAI AMP Platform│
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                │                ▼
┌─────────────────────┐        │    ┌─────────────────────┐
│   startupai.site    │        │    │ app.startupai.site  │
│  Marketing & Trust  │        │    │ Product & Delivery  │
│    (Netlify)        │        │    │    (Netlify)        │
└─────────────────────┘        │    └─────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      Supabase       │
                    │   Shared Database   │
                    └─────────────────────┘
```

## Service Definitions

### AI Founders Core (`startupai-crew`)
**The Brain** - Pure automation delivering strategic business analysis

- **Technology**: CrewAI, Python, deployed on CrewAI AMP
- **Input**: Entrepreneur business context (text)
- **Output**: 6-part strategic analysis (Value Proposition Canvas, Validation Roadmap, etc.)
- **Communication**: REST API (kickoff, status, results)

### Marketing Interface (`startupai.site`)
**The Transparency Layer** - Public-facing lead capture and AI team visibility

- **Technology**: Next.js 15, Static Export, deployed on Netlify
- **Purpose**: Show how AI Founders work, capture leads, route to product
- **Communication**: Supabase Auth (signup → redirect to app)

### Product Interface (`app.startupai.site`)
**The Delivery Layer** - Customer portal for validation delivery

- **Technology**: Next.js 15, Vercel AI SDK, deployed on Netlify
- **Purpose**: Onboarding, trigger analysis, display results
- **Communication**: REST to CrewAI, read/write to Supabase

---

## Phase-to-Service Mapping

Each validation phase involves specific services:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         VALIDATION FLOW                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   PRODUCT APP              CREWAI AMP                  SUPABASE             │
│   ───────────              ──────────                  ────────             │
│                                                                              │
│   ┌─────────────┐                                                           │
│   │ Onboarding  │ ──────► Phase 0: Founder's Brief                          │
│   │ UI Forms    │         (Sage, Guardian)                                  │
│   └─────────────┘                │                                          │
│                                  ▼                                          │
│                          Phase 1: VPC Discovery ──────► Customer Profile    │
│                          (Sage, Forge, Ledger)    │    Value Map stored     │
│                                  │                └──► Flywheel: Discovery  │
│                                  ▼                     learnings            │
│   ┌─────────────┐        Phase 2: Desirability                              │
│   │ Approval UI │ ◄────► (Forge, Pulse, Guardian) │                         │
│   │ HITL Modal  │        Landing pages, ads       └──► Flywheel: Campaign   │
│   └─────────────┘                │                     learnings            │
│                                  ▼                                          │
│                          Phase 3: Feasibility ──────► Cost estimates        │
│                          (Forge, Guardian)       │    Constraints stored    │
│                                  │               └──► Flywheel: Technical   │
│                                  ▼                    learnings             │
│   ┌─────────────┐        Phase 4: Viability                                 │
│   │ Results     │ ◄───── (Ledger, Compass, Guardian)                        │
│   │ Dashboard   │        Final recommendation    └──► Flywheel: Economics   │
│   └─────────────┘                │                    learnings             │
│                                  ▼                                          │
│                          ┌─────────────────┐                                │
│                          │ VALIDATED/KILLED│ ──────► Flywheel: Outcome      │
│                          └─────────────────┘         summary + patterns     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Flywheel Learning**: Captured at every test cycle, not just final outcome. Each phase contributes Learning Cards that improve methodology for future validations. See [reference/flywheel-learning.md](./reference/flywheel-learning.md).

| Phase | Primary Service | Data Flow | Flywheel Captures |
|-------|-----------------|-----------|-------------------|
| **0: Onboarding** | Product App | App → CrewAI (kickoff) | - |
| **1: VPC Discovery** | CrewAI | CrewAI → Supabase (VPC) | Discovery learnings |
| **2: Desirability** | CrewAI | CrewAI ↔ App (HITL) | Campaign learnings |
| **3: Feasibility** | CrewAI | CrewAI → Supabase (costs) | Technical learnings |
| **4: Viability** | CrewAI | CrewAI → App (results) | Economics learnings |
| **Terminal** | All | Final storage | Outcome patterns |

---

## Communication Patterns

### Synchronous (Request/Response)
```
Product App ──POST /kickoff──► CrewAI AMP
Product App ──GET /status────► CrewAI AMP
```

### Asynchronous (Webhooks)
```
CrewAI AMP ──POST /webhook──► Product App (HITL triggers, results)
```

### Shared State
```
Product App ──────► Supabase ◄────── CrewAI AMP
                   (projects, briefs, results)
```

---

## API Contracts

For detailed API specifications, see **[reference/api-contracts.md](./reference/api-contracts.md)**.

| Integration | Endpoint Pattern | Purpose |
|-------------|------------------|---------|
| **Kickoff** | `POST /kickoff` | Start validation workflow |
| **Status** | `GET /status/{id}` | Poll for completion |
| **Resume** | `POST /resume` | Continue after HITL approval |
| **Webhook** | `POST /api/crewai/webhook` | Async notifications to Product App |

---

## Approval Workflows (HITL)

For detailed patterns, see **[reference/approval-workflows.md](./reference/approval-workflows.md)**.

```
CrewAI AMP                           Product App
    │                                     │
    │ Task pauses (human_input: true)     │
    │ ──────── POST /webhook ───────────► │
    │                                     │ User reviews in UI
    │                                     │ User approves/rejects
    │ ◄─────── POST /resume ───────────── │
    │ Flow continues                      │
    └─────────────────────────────────────┘
```

---

## Related Documents

### Architecture
- [00-introduction.md](./00-introduction.md) - Quick start and orientation
- [02-organization.md](./02-organization.md) - 6 AI Founders and agents
- [03-methodology.md](./03-methodology.md) - VPD framework reference

### Phase Specifications
- [04-phase-0-onboarding.md](./04-phase-0-onboarding.md) - Founder's Brief capture
- [05-phase-1-vpc-discovery.md](./05-phase-1-vpc-discovery.md) - VPC Discovery
- [06-phase-2-desirability.md](./06-phase-2-desirability.md) - Desirability validation
- [07-phase-3-feasibility.md](./07-phase-3-feasibility.md) - Feasibility validation
- [08-phase-4-viability.md](./08-phase-4-viability.md) - Viability + Decision

### Reference
- [09-status.md](./09-status.md) - Current implementation status
- [reference/api-contracts.md](./reference/api-contracts.md) - API specifications
- [reference/approval-workflows.md](./reference/approval-workflows.md) - HITL patterns
- [reference/database-schemas.md](./reference/database-schemas.md) - Supabase schemas
