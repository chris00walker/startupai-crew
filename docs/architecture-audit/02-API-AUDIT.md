# API Routes Audit Report

**Repository**: `/home/chris/projects/app.startupai.site`
**Date**: 2026-01-06
**Auditor**: Sub-Agent 2 (Backend Developer)

---

## Executive Summary

- **Total API Routes**: 34 active endpoints
- **Architecture**: Split between App Router (newer) and Pages Router

### Critical Finding

**The 05-spec describes endpoints that DON'T EXIST**. The actual implementation uses an Agentuity agent-driven conversational flow, not interview-based APIs.

---

## Endpoints Inventory

### Onboarding System (7 endpoints)

| Path | Methods | Auth | Purpose |
|------|---------|------|---------|
| `/api/onboarding/start` | POST | Required | Initialize session (Agentuity agent) |
| `/api/onboarding/message` | POST | Required | AI conversation (streaming) |
| `/api/onboarding/status` | GET | Required | Session state |
| `/api/onboarding/complete` | POST | Required | Finalize, create project, kickoff CrewAI |
| `/api/onboarding/recover` | POST | Required | Manual CrewAI trigger for stuck sessions |
| `/api/onboarding/abandon` | POST | Required | Mark session abandoned |

### CrewAI Integration (4 endpoints)

| Path | Methods | Auth | Purpose |
|------|---------|------|---------|
| `/api/crewai/webhook` | POST | Bearer | UNIFIED webhook for all flows |
| `/api/crewai/status` | GET | Required | Poll kickoff status |
| `/api/crewai/results` | POST | Bearer | LEGACY - use webhook |
| `/api/crewai/consultant` | POST | Bearer | Consultant onboarding results |

### Approval System (3 endpoints)

| Path | Methods | Auth | Purpose |
|------|---------|------|---------|
| `/api/approvals` | GET | Required | List approvals |
| `/api/approvals/[id]` | GET, PATCH | Required | Get/decide approval |
| `/api/approvals/webhook` | POST | Bearer | CrewAI posts approval requests |

### VPC Operations (2 endpoints)

| Path | Methods | Auth | Purpose |
|------|---------|------|---------|
| `/api/vpc/[projectId]` | GET, POST | Required | Get/upsert VPC segments |
| `/api/vpc/[projectId]/initialize` | POST | Required | Initialize VPC |

### Analysis (1 endpoint)

| Path | Methods | Auth | Purpose |
|------|---------|------|---------|
| `/api/analyze` | POST | Required | Trigger CrewAI analysis |

### Project Management (1 endpoint)

| Path | Methods | Auth | Purpose |
|------|---------|------|---------|
| `/api/projects/create` | POST | Required | Create project manually |

### Assistant/Chat (4 endpoints)

| Path | Methods | Auth | Purpose |
|------|---------|------|---------|
| `/api/assistant/chat` | POST | Required | Dashboard AI support (streaming) |
| `/api/assistant/history` | GET | Required | Conversation history |
| `/api/consultant/chat` | POST | Required | Consultant onboarding AI |
| `/api/chat` | POST | Required | General chat |

### Consultant Platform (8 endpoints)

| Path | Methods | Auth | Purpose |
|------|---------|------|---------|
| `/api/clients` | GET, POST | Required | List/create clients |
| `/api/clients/[id]` | GET | Required | Client details |
| `/api/clients/[id]/discovery` | POST | Required | Client discovery data |
| `/api/clients/[id]/tasks` | GET | Required | Client tasks |
| `/api/clients/[id]/artefacts` | GET | Required | Client artefacts |
| `/api/consultant/onboarding` | POST | Bearer | Consultant onboarding webhook |
| `/api/consultant/onboarding/start` | POST | Required | Start consultant onboarding |
| `/api/consultant/onboarding/complete` | POST | Required | Complete consultant onboarding |

### Public APIs (2 endpoints)

| Path | Methods | Auth | Purpose |
|------|---------|------|---------|
| `/api/v1/public/activity` | GET | None | Public activity feed |
| `/api/v1/public/metrics` | GET | None | Public metrics |

### Utility (2 endpoints)

| Path | Methods | Auth | Purpose |
|------|---------|------|---------|
| `/api/health` | GET, POST | None | Health check |
| `/api/auth/logout` | GET | Required | Logout |

---

## Key Endpoint Details

### POST /api/onboarding/start

**Request**:
```typescript
{
  userId?: string,
  planType: 'trial' | 'sprint' | 'founder' | 'enterprise',
  resumeSessionId?: string,
  forceNew?: boolean,
  userContext?: { referralSource?, previousExperience?, timeAvailable? }
}
```

**Response**:
```typescript
{
  success: boolean,
  sessionId: string,
  agentIntroduction: string,
  firstQuestion: string,
  estimatedDuration: string,
  stageInfo: { currentStage, totalStages, stageName, stageDescription }
}
```

**External APIs**: `AGENTUITY_AGENT_URL` or `CREW_ANALYZE_URL`
**Database**: `onboarding_sessions` (creates)

### POST /api/onboarding/complete

**Request**:
```typescript
{
  sessionId: string,
  finalConfirmation: boolean,
  entrepreneurBrief: object,
  userFeedback?: { conversationRating, clarityRating, comments }
}
```

**Response**:
```typescript
{
  success: boolean,
  workflowId: string,
  workflowTriggered: boolean,
  projectCreated: { projectId, projectName, projectUrl },
  dashboardRedirect: string
}
```

**External APIs**: CrewAI AMP (fire-and-forget kickoff)
**Database**: `entrepreneur_briefs` (upsert), `projects` (insert), `onboarding_sessions` (update)

### POST /api/crewai/webhook

**Authentication**: Bearer token (`CREW_CONTRACT_BEARER`)

**Request** (founder_validation):
```typescript
{
  flow_type: 'founder_validation',
  project_id: string,
  user_id: string,
  kickoff_id: string,
  validation_report: {
    id, business_idea, validation_outcome, evidence_summary, next_steps
  },
  value_proposition_canvas: Record<string, { customer_profile, value_map }>,
  evidence: { desirability, feasibility, viability },
  qa_report: object
}
```

**Database**:
- `reports` (insert)
- `evidence` (bulk insert)
- `projects` (update)
- `crewai_validation_states` (upsert)
- `public_activity_log` (insert)

### PATCH /api/approvals/[id]

**Request**:
```typescript
{
  action: 'approve' | 'reject',
  decision?: string,
  feedback?: string
}
```

**External APIs**: CrewAI AMP `/resume` endpoint (if approved)
**Database**: `approval_requests` (update), `approval_history` (insert)

---

## Documentation Comparison

### Expected (05-spec) vs Actual

| Expected Endpoint | Actual | Status |
|-------------------|--------|--------|
| POST /interview/start | POST /api/onboarding/start | Different contract |
| POST /interview/continue | POST /api/onboarding/message | Different structure |
| GET /brief/{id} | - | NOT IMPLEMENTED |
| POST /brief/approve | PATCH /api/approvals/[id] | Different, general system |

### Architecture Mismatch

**05-spec describes**: Interview-based system with discrete Q&A
**Actual implementation**: Agentuity agent-driven conversational flow with streaming

---

## External Service Dependencies

### Agentuity Agent (Onboarding)
- **URL**: `AGENTUITY_AGENT_URL` or `CREW_ANALYZE_URL`
- **Used by**: `/onboarding/start`, `/onboarding/message`

### CrewAI AMP (Validation)
- **URL**: `CREWAI_API_URL`
- **Token**: `CREWAI_API_TOKEN`
- **Used by**: `/onboarding/complete`, `/analyze`, `/approvals/[id]`

### OpenAI (Chat)
- **Model**: `gpt-4o-mini`
- **Used by**: `/assistant/chat`, `/consultant/chat`

### Supabase Admin
- **Used by**: `/clients` (create user accounts)

---

## Database Tables Accessed by Routes

| Table | Insert | Update | Upsert |
|-------|--------|--------|--------|
| `onboarding_sessions` | /start | /message, /complete, /abandon | - |
| `entrepreneur_briefs` | - | - | /complete, /webhook |
| `projects` | /complete, /create | /webhook, /status | - |
| `reports` | /webhook, /status | - | - |
| `evidence` | /webhook, /analyze | - | - |
| `value_proposition_canvas` | /vpc | /vpc | /vpc |
| `crewai_validation_states` | - | - | /webhook |
| `approval_requests` | - | /approvals/[id] | - |

---

## Recommendations

1. **Update 05-spec** to match actual architecture
2. **Add API versioning** (`/api/v1/*`)
3. **Implement rate limiting** for expensive AI operations
4. **Add integration tests** for critical flows
5. **Document CrewAI webhook contract** in spec
