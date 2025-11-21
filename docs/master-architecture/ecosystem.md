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

## API Contracts (What Actually Exists)

### CrewAI AMP Endpoints (REAL)
| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/inputs` | GET | Schema for input parameters | Working |
| `/kickoff` | POST | Start analysis workflow | Working |
| `/status/{id}` | GET | Check execution status | Working |

**Base URL**: `https://startupai-b4d5c1dd-27e2-4163-b9fb-a18ca06ca-4f4192a6.crewai.com`

### Marketing → App Contracts (REAL)
| Contract | Implementation | Status |
|----------|---------------|--------|
| Auth redirect with plan | Query param `?plan=professional` | Working |
| Shared Supabase instance | Same project, different clients | Working |

### Aspirational Contracts (NOT IMPLEMENTED)
These were documented but do not exist:
- `GET /api/v1/agents/activity`
- `GET /api/v1/metrics/public`
- `POST /api/v1/analysis/start` (it's `/kickoff`)

---

## Approval Workflow Communication

Human-in-the-loop (HITL) approvals require bidirectional communication between CrewAI AMP and the product app.

### Approval Flow Architecture

```
┌─────────────────┐                    ┌─────────────────┐
│   CrewAI AMP    │                    │   Product App   │
│   (startupai-   │                    │  (app.startupai │
│    crew)        │                    │    .site)       │
└────────┬────────┘                    └────────┬────────┘
         │                                      │
         │ 1. Task with human_input: true       │
         │    → Flow pauses                     │
         │                                      │
         │ 2. Webhook POST                      │
         │ ─────────────────────────────────►   │
         │    {execution_id, task_id,           │
         │     task_output}                     │
         │                                      │
         │                              3. Store in approval_requests
         │                              4. Show ApprovalDetailModal
         │                              5. User decides
         │                                      │
         │ 6. POST /resume                      │
         │ ◄─────────────────────────────────   │
         │    {execution_id, task_id,           │
         │     human_feedback, is_approve}      │
         │                                      │
         │ 7. Flow resumes                      │
         │    → Router routes based on          │
         │       approval status                │
         └──────────────────────────────────────┘
```

### API Contracts: Approval Workflow

#### Webhook (CrewAI → Product App)
```
POST https://app.startupai.site/api/approvals/webhook
Content-Type: application/json
Authorization: Bearer {webhook-secret}

{
  "execution_id": "uuid-of-flow-execution",
  "task_id": "uuid-of-paused-task",
  "crew_name": "governance",
  "task_name": "qa_gate_review",
  "task_output": {
    "approval_type": "stage_gate",
    "title": "Desirability Gate Approval",
    "context": {
      "project_id": "uuid",
      "evidence_summary": "...",
      "qa_score": 0.85,
      "assumptions_tested": 5,
      "assumptions_validated": 4
    },
    "recommendation": "proceed",
    "alternatives": [
      {"action": "proceed", "rationale": "Strong evidence"},
      {"action": "retry", "rationale": "Address weak areas"},
      {"action": "pivot", "rationale": "Fundamental issues"}
    ]
  }
}
```

#### Resume (Product App → CrewAI)
```
POST https://startupai-...crewai.com/resume
Content-Type: application/json
Authorization: Bearer {crew-token}

{
  "execution_id": "uuid-of-flow-execution",
  "task_id": "uuid-of-paused-task",
  "human_feedback": "Approved with note: Focus on pricing validation next",
  "is_approve": true,
  "humanInputWebhook": {
    "url": "https://app.startupai.site/api/approvals/webhook",
    "authentication": {
      "strategy": "bearer",
      "token": "{webhook-secret}"
    }
  }
}
```

### Approval Types & Blocking Behavior

| Approval Type | Blocking | Primary Owner | CrewAI Task Location |
|---------------|----------|---------------|----------------------|
| Spend Increases | Yes | Ledger | Build/Growth Crew |
| Campaign Launch | Yes | Pulse | Growth Crew |
| Direct Customer Contact | Yes | Pulse | Growth Crew |
| Stage Gate Progression | Yes | Guardian | Governance Crew |
| Pivot Recommendations | Yes | Compass | Synthesis Crew |
| Third-Party Data Sharing | No (Parallel) | Guardian | Governance Crew |

### Product App Responsibilities

1. **Webhook Receiver** (`/api/approvals/webhook`)
   - Validate webhook authentication
   - Store approval request in `approval_requests` table
   - Check auto-approve rules in `approval_preferences`
   - If auto-approve: immediately call `/resume`
   - Else: send notifications (in-app, email)

2. **Approval UI**
   - `ApprovalQueue.tsx` - Dashboard view of pending approvals
   - `ApprovalDetailModal.tsx` - Full context and decision interface
   - Show: what AI wants, evidence, risks, alternatives

3. **Resume Client** (`/services/crewai-client.ts`)
   - Call CrewAI `/resume` endpoint with user decision
   - Include webhook config for subsequent approvals
   - Handle errors and retries

4. **Notification Escalation**
   - Cron job checks for aging approvals
   - Escalate: in-app → email (15min) → SMS (24hr) → backup (48hr)

### Status

| Component | Status |
|-----------|--------|
| CrewAI `human_input` support | ✅ Available in CrewAI AMP |
| CrewAI webhook delivery | ✅ Available in CrewAI AMP |
| CrewAI `/resume` endpoint | ✅ Available in CrewAI AMP |
| Product app webhook receiver | ❌ NOT IMPLEMENTED |
| Product app approval UI | ❌ NOT IMPLEMENTED |
| Product app resume client | ❌ NOT IMPLEMENTED |
| Notification escalation | ❌ NOT IMPLEMENTED |
| Auto-approve rules | ❌ NOT IMPLEMENTED |

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

See `validation-backlog.md` for the current hypothesis queue.

---

## Related Documents

- `organizational-structure.md` - Flat founder team & workflow agents
- `current-state.md` - Detailed status of each service
- `validation-backlog.md` - Hypothesis-driven feature backlog
