---
purpose: Three-service ecosystem architecture overview
status: active
last_reviewed: 2025-11-21
---

# StartupAI Ecosystem - Master Architecture

## Overview

StartupAI is a three-service ecosystem where AI Founders (this repository) serve as the decision engine, with two web interfaces providing transparency and delivery.

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

## What's Implemented (Reality)

### Authentication Flow
```
Marketing Site                    Product App
     │                                │
     │ [Sign Up Button]               │
     │         │                      │
     └─────────┼──────────────────────┘
               │
               ▼
     ┌─────────────────┐
     │  Supabase Auth  │
     │   (GitHub OAuth)│
     └────────┬────────┘
              │
              ▼
     ┌─────────────────┐
     │  Product App    │
     │ /auth/callback  │
     └─────────────────┘
```
**Status**: Working end-to-end

### Analysis Workflow
```
Product App                      CrewAI AMP
     │                                │
     │ [Complete Onboarding]          │
     │         │                      │
     │ POST /api/crewai/analyze       │
     │ ─────────────────────────────► │
     │                                │
     │         (async processing)     │
     │                                │
     │ GET /status/{kickoff_id}       │
     │ ─────────────────────────────► │
     │                                │
     │ GET /results                   │
     │ ◄───────────────────────────── │
     └────────────────────────────────┘
```
**Status**: Implemented (15% tools functional, LLM-based analysis works)

### Data Storage
```
Product App → Supabase ← CrewAI Results (manual/future)
```
**Status**: Partial - app writes to Supabase, CrewAI results storage not automated

---

## What's NOT Implemented (Hypotheses to Validate)

### Real-time Activity Feed
```
Marketing Site ◄──── Activity Feed API ────► CrewAI AMP
```
**Status**: NOT IMPLEMENTED
- No `/api/v1/agents/activity` endpoint exists
- No webhooks for real-time updates
- Marketing site cannot display live agent work

**Hypothesis**: Real-time agent activity increases user trust and conversion

### Trust Metrics API
```
Marketing Site ◄──── Trust Metrics API ────► CrewAI AMP
```
**Status**: NOT IMPLEMENTED
- No `/api/v1/metrics/public` endpoint exists
- No aggregated success metrics available

**Hypothesis**: Public metrics (analyses completed, satisfaction scores) drive signups

### Automated Result Storage
```
CrewAI AMP ────► Supabase (entrepreneur_briefs, analysis_results)
```
**Status**: NOT IMPLEMENTED
- Results stay in CrewAI AMP
- Manual export required to get results into Supabase

**Hypothesis**: Automated storage enables dashboard features and retention

---

## API Contracts

For detailed API specifications, see **[reference/api-contracts.md](./reference/api-contracts.md)**.

### Summary

| Service | Endpoints | Status |
|---------|-----------|--------|
| CrewAI AMP | `/inputs`, `/kickoff`, `/status`, `/resume` | Working |
| Marketing → App | Auth redirect with plan param | Working |
| Activity Feed | `GET /api/v1/agents/activity` | NOT IMPLEMENTED |
| Metrics | `GET /api/v1/metrics/public` | NOT IMPLEMENTED |

---

## Approval Workflows

For detailed HITL patterns, see **[reference/approval-workflows.md](./reference/approval-workflows.md)**.

### Summary

Human-in-the-loop approvals require bidirectional communication:
1. CrewAI task pauses with `human_input: true`
2. Webhook notifies product app
3. User approves/rejects in UI
4. Product app calls `/resume`
5. Flow continues

**Implementation Status**: CrewAI side available, product app side NOT IMPLEMENTED.

---

## Environment Configuration

### Shared Resources
| Resource | Used By | Purpose |
|----------|---------|---------|
| Supabase Project | Marketing, Product | Auth, Database |
| OpenAI API Key | CrewAI | LLM inference |

### Service-Specific
| Service | Key Variables |
|---------|---------------|
| Marketing | `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_APP_URL` |
| Product | `NEXT_PUBLIC_SUPABASE_URL`, `CREW_CONTRACT_BEARER` |
| CrewAI | `OPENAI_API_KEY` (in CrewAI dashboard) |

---

## Build Order Principles

Since StartupAI uses lean validation (not waterfall), build order is determined by:

1. **What hypothesis needs validation next?**
2. **What's the minimum build to test it?**
3. **What did we learn? Pivot or persevere?**

See `docs/work/backlog.md` for the current hypothesis queue.

---

## Related Documents

- `02-organization.md` - Flat founder team & workflow agents
- `04-status.md` - Detailed status of each service
- `../work/backlog.md` - Hypothesis-driven feature backlog
- `reference/api-contracts.md` - All API specifications
- `reference/approval-workflows.md` - HITL patterns
