---
purpose: Three-service ecosystem architecture overview
status: active
last_reviewed: 2026-01-08
vpd_compliance: true
---

# StartupAI Ecosystem Architecture

## Overview

StartupAI is a **three-layer ecosystem** that delivers **Value Proposition Design (VPD)** validation through AI Founders. The architecture separates concerns across Interaction (Netlify), Orchestration (Supabase), and Compute (Modal) layers.

> **VPD Framework**: This ecosystem implements the Strategyzer methodology. See [03-methodology.md](./03-methodology.md) for framework details.
>
> **Modal Migration**: Per [ADR-002](../adr/002-modal-serverless-migration.md), the compute layer has migrated from CrewAI AMP to Modal serverless.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       THREE-LAYER ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   INTERACTION LAYER (Netlify)                                               │
│   ───────────────────────────                                               │
│   ┌─────────────────────┐         ┌─────────────────────┐                   │
│   │   startupai.site    │         │ app.startupai.site  │                   │
│   │  Marketing & Trust  │         │ Product & Delivery  │                   │
│   │  - Lead capture     │         │  - Onboarding UI    │                   │
│   │  - AI team display  │         │  - HITL approvals   │                   │
│   └─────────────────────┘         │  - Results display  │                   │
│                                   └──────────┬──────────┘                   │
│                                              │                              │
├──────────────────────────────────────────────┼──────────────────────────────┤
│                                              │                              │
│   ORCHESTRATION LAYER (Supabase)             │                              │
│   ───────────────────────────────            │                              │
│   ┌──────────────────────────────────────────┼───────────────────┐          │
│   │                         PostgreSQL       │                   │          │
│   │  - validation_runs (state persistence)   │                   │          │
│   │  - validation_progress (Realtime → UI) ◄─┘                   │          │
│   │  - hitl_requests (checkpoint/resume)                         │          │
│   │  - founders_briefs, vpc_*, experiments                       │          │
│   │                                                              │          │
│   │  Realtime Engine: WebSocket push to Product App              │          │
│   └───────────────────────────────┬──────────────────────────────┘          │
│                                   │                                         │
├───────────────────────────────────┼─────────────────────────────────────────┤
│                                   │                                         │
│   COMPUTE LAYER (Modal)           │                                         │
│   ─────────────────────           │                                         │
│   ┌───────────────────────────────┼─────────────────────────────┐           │
│   │                               ▼                             │           │
│   │   AI Founders Core (startupai-crew)                         │           │
│   │   - Ephemeral Python containers (pay-per-second)            │           │
│   │   - 5 Flows, 14 Crews, 45 Agents, 10 HITL                   │           │
│   │   - Writes progress directly to Supabase                    │           │
│   │   - $0 during HITL waits (checkpoint-and-resume)            │           │
│   │                                                             │           │
│   │   Endpoints:                                                │           │
│   │   - POST /kickoff → Start validation                        │           │
│   │   - GET /status/{run_id} → Check progress                   │           │
│   │   - POST /hitl/approve → Resume after human approval        │           │
│   └─────────────────────────────────────────────────────────────┘           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Service Definitions

### AI Founders Core (`startupai-crew`)
**The Brain** - Pure automation delivering strategic business analysis

- **Technology**: CrewAI, Python, deployed on **Modal serverless**
- **Input**: Entrepreneur business context (text)
- **Output**: 6-part strategic analysis (Value Proposition Canvas, Validation Roadmap, etc.)
- **Communication**: REST API via Modal web endpoints (kickoff, status, hitl/approve)
- **State**: Persisted to Supabase, enabling checkpoint-and-resume for HITL

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

Each validation phase involves specific services across the three layers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         VALIDATION FLOW                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   PRODUCT APP              MODAL (Compute)             SUPABASE             │
│   ───────────              ───────────────             ────────             │
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

### Synchronous (Request/Response via Modal)
```
Product App ──POST /kickoff──────► Modal (returns 202 Accepted)
Product App ──GET /status/{run_id}► Modal (reads from Supabase)
Product App ──POST /hitl/approve──► Modal (resumes checkpoint)
```

### Real-time (Supabase Realtime)
```
Modal ──INSERT validation_progress──► Supabase ──WebSocket──► Product App UI
Modal ──INSERT hitl_requests────────► Supabase ──WebSocket──► Product App UI
```

### Shared State (Supabase PostgreSQL)
```
Product App ◄──────► Supabase ◄────── Modal
                    (validation_runs, progress, HITL state, results)
```

**Key Pattern**: Modal writes progress directly to Supabase, enabling real-time UI updates via Supabase Realtime. No webhook from compute layer to Product App.

---

## API Contracts

For detailed API specifications, see **[reference/api-contracts.md](./reference/api-contracts.md)**.

| Integration | Endpoint Pattern | Purpose |
|-------------|------------------|---------|
| **Kickoff** | `POST /kickoff` | Start validation (returns 202 + run_id) |
| **Status** | `GET /status/{run_id}` | Check progress (reads Supabase) |
| **HITL Approve** | `POST /hitl/approve` | Resume after human approval |

> **Note**: All endpoints served by Modal. No webhook callback pattern - Modal writes directly to Supabase, Product App subscribes via Realtime.

---

## Approval Workflows (HITL)

For detailed patterns, see **[reference/approval-workflows.md](./reference/approval-workflows.md)**.

```
Modal (Compute)                      Supabase                    Product App
      │                                  │                           │
      │ HITL checkpoint reached          │                           │
      │ ────INSERT hitl_requests────────►│                           │
      │                                  │ ───Realtime WebSocket────►│
      │ Container terminates             │                           │ User reviews
      X ($0 while waiting)               │                           │ User approves
                                         │                           │
                                         │ ◄───POST /hitl/approve─── │
      │ New container spawns             │                           │
      │ ◄────Read approved state─────────│                           │
      │ Resumes from checkpoint          │                           │
      └──────────────────────────────────┴───────────────────────────┘
```

**Key Benefit**: $0 compute cost during human review (containers terminate, state in Supabase).

---

## Related Documents

### Architecture
- [00-introduction.md](./00-introduction.md) - Quick start and orientation
- [02-organization.md](./02-organization.md) - 6 AI Founders and agents
- [03-methodology.md](./03-methodology.md) - VPD framework reference
- [ADR-002](../adr/002-modal-serverless-migration.md) - Modal serverless migration decision

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
- [reference/modal-configuration.md](./reference/modal-configuration.md) - Modal platform configuration

---

**Last Updated**: 2026-01-08

**Latest Changes (2026-01-08 - Modal migration alignment)**:
- Updated main diagram to show three-layer architecture (Netlify → Supabase → Modal)
- Updated Service Definitions to reference Modal serverless
- Updated Communication Patterns to show Supabase Realtime pattern
- Updated API Contracts table with Modal endpoints
- Updated Approval Workflows diagram for checkpoint-and-resume pattern
- Added link to ADR-002 in Related Documents
