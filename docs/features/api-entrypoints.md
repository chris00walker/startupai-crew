---
document_type: feature-audit
status: active
last_verified: 2026-01-13
---

# API Entrypoints

## Purpose
Complete documentation of the Modal FastAPI endpoints that power the StartupAI validation engine.

## Quick Reference

| Method | Endpoint | Purpose | Auth | Status |
|--------|----------|---------|------|--------|
| POST | `/kickoff` | Start validation run | Bearer | `active` |
| GET | `/status/{run_id}` | Get run progress | Bearer | `active` |
| POST | `/hitl/approve` | Submit HITL decision | Bearer | `active` |
| GET | `/health` | Health check | None | `active` |

**Base URL**: `https://chris00walker--startupai-validation-fastapi-app.modal.run`

---

## Authentication

### Bearer Token

**File**: `src/modal_app/app.py:166-177`

All endpoints except `/health` require bearer token authentication:

```
Authorization: Bearer <token>
```

**Environment Variable**: `WEBHOOK_BEARER_TOKEN`
**Default**: `startupai-modal-secret-2026`

**Verification Logic**:
```python
def verify_bearer_token(authorization: str = Header(...)) -> bool:
    expected = os.environ.get("WEBHOOK_BEARER_TOKEN", "startupai-modal-secret-2026")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization[7:]
    if not hmac.compare_digest(token, expected):
        raise HTTPException(status_code=401, detail="Invalid bearer token")

    return True
```

---

## Endpoints

### POST /kickoff

**Purpose**: Start a new validation run

**File**: `src/modal_app/app.py:202-247`

**Response Code**: `202 Accepted`

#### Request

**Model**: `KickoffRequest`

```typescript
interface KickoffRequest {
  project_id: string;         // UUID - Project to validate
  user_id: string;            // UUID - Requesting user
  entrepreneur_input: string; // Min 10 chars - Business description
  session_id?: string;        // UUID - Optional onboarding session reference
}
```

**Validation**:
- `entrepreneur_input` must be at least 10 characters

#### Response

**Model**: `KickoffResponse`

```typescript
interface KickoffResponse {
  run_id: string;   // UUID - Validation run ID
  status: string;   // Always "started"
  message: string;  // "Validation run initiated. Poll /status/{run_id} for progress."
}
```

#### Flow

```
[Request] → verify_bearer_token()
         → INSERT into validation_runs
         → run_validation.spawn(run_id)
         → Return 202 + run_id
```

#### Example

```bash
curl -X POST \
  "https://chris00walker--startupai-validation-fastapi-app.modal.run/kickoff" \
  -H "Authorization: Bearer startupai-modal-secret-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "550e8400-e29b-41d4-a716-446655440001",
    "entrepreneur_input": "AI-powered startup validation platform that helps founders..."
  }'
```

**Response**:
```json
{
  "run_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "started",
  "message": "Validation run initiated. Poll /status/{run_id} for progress."
}
```

---

### GET /status/{run_id}

**Purpose**: Get current status and progress of a validation run

**File**: `src/modal_app/app.py:250-308`

**Response Code**: `200 OK`

#### Parameters

| Parameter | Type | Location | Required |
|-----------|------|----------|----------|
| `run_id` | UUID | Path | Yes |

#### Response

**Model**: `StatusResponse`

```typescript
interface StatusResponse {
  run_id: string;           // UUID
  status: "pending" | "running" | "paused" | "completed" | "failed";
  current_phase: number;    // 0-4
  phase_name: string;       // Human-readable phase name
  progress: ProgressItem[]; // Array of progress events
  hitl_pending?: HITLRequest; // Pending HITL request if any
  started_at?: string;      // ISO timestamp
  updated_at?: string;      // ISO timestamp
  error_message?: string;   // Error details if failed
}

interface ProgressItem {
  id: string;
  run_id: string;
  phase: number;
  crew: string;
  agent: string;
  task: string;
  status: "started" | "completed" | "failed";
  output?: any;
  created_at: string;
}

interface HITLRequest {
  id: string;
  checkpoint_name: string;
  title: string;
  description: string;
  options: DecisionOption[];
  recommended_option: string;
  context: any;
}
```

#### Phase Mapping

| Phase | Name |
|-------|------|
| 0 | Onboarding |
| 1 | VPC Discovery |
| 2 | Desirability |
| 3 | Feasibility |
| 4 | Viability |

#### Data Sources

- **Run state**: `validation_runs` table
- **Progress**: `validation_progress` table (ordered by `created_at`)
- **HITL**: `hitl_requests` table (status = pending)

#### Example

```bash
curl -X GET \
  "https://chris00walker--startupai-validation-fastapi-app.modal.run/status/f47ac10b-58cc-4372-a567-0e02b2c3d479" \
  -H "Authorization: Bearer startupai-modal-secret-2026"
```

**Response**:
```json
{
  "run_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "running",
  "current_phase": 1,
  "phase_name": "VPC Discovery",
  "progress": [
    {
      "id": "abc123",
      "phase": 0,
      "crew": "OnboardingCrew",
      "agent": "O1-FounderInterview",
      "task": "founder_interview",
      "status": "completed",
      "created_at": "2026-01-13T10:00:00Z"
    }
  ],
  "hitl_pending": null,
  "started_at": "2026-01-13T09:55:00Z",
  "updated_at": "2026-01-13T10:05:00Z"
}
```

---

### POST /hitl/approve

**Purpose**: Submit human decision for HITL checkpoint and resume validation

**File**: `src/modal_app/app.py:311-569`

**Response Code**: `200 OK`

#### Request

**Model**: `HITLApproveRequest`

```typescript
interface HITLApproveRequest {
  run_id: string;           // UUID - Validation run ID
  checkpoint: string;       // Checkpoint name (e.g., "approve_founders_brief")
  decision: Decision;       // Selected decision
  feedback?: string;        // Optional human feedback
  custom_segment_data?: {   // Required if decision is "custom_segment"
    segment_name: string;
    segment_description?: string;
  };
}

type Decision =
  | "approved"           // Proceed to next phase
  | "rejected"           // Stop and pause workflow
  | "override_proceed"   // Override pivot signal, proceed anyway
  | "iterate"            // Re-run current phase
  | "segment_1"          // Select alternative segment 1
  | "segment_2"          // Select alternative segment 2
  | "segment_3"          // Select alternative segment 3
  | "custom_segment";    // Custom segment hypothesis
```

#### Response

**Model**: `HITLApproveResponse`

```typescript
interface HITLApproveResponse {
  status: "resumed" | "rejected" | "pivot" | "iterate";
  next_phase?: number;
  pivot_type?: "segment_pivot" | "value_pivot";
  message: string;
}
```

#### Decision Handling Matrix

| Decision | Response Status | Next Phase | Notes |
|----------|-----------------|------------|-------|
| `approved` | `resumed` | `current + 1` | Standard progression |
| `approved` (pivot checkpoint) | `pivot` | `1` | Returns to Phase 1 |
| `segment_*` | `pivot` | `1` | Segment pivot with selection |
| `custom_segment` | `pivot` | `1` | Custom segment hypothesis |
| `override_proceed` | `resumed` | `current + 1` | Override recorded |
| `iterate` | `iterate` | `current` | Re-run same phase |
| `rejected` | `rejected` | `null` | Workflow paused |

#### Example: Standard Approval

```bash
curl -X POST \
  "https://chris00walker--startupai-validation-fastapi-app.modal.run/hitl/approve" \
  -H "Authorization: Bearer startupai-modal-secret-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "run_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "checkpoint": "approve_founders_brief",
    "decision": "approved",
    "feedback": "Brief looks comprehensive, proceed."
  }'
```

**Response**:
```json
{
  "status": "resumed",
  "next_phase": 1,
  "message": "Validation resumed from checkpoint 'approve_founders_brief'. Advancing to Phase 1."
}
```

#### Example: Segment Pivot

```bash
curl -X POST \
  "https://chris00walker--startupai-validation-fastapi-app.modal.run/hitl/approve" \
  -H "Authorization: Bearer startupai-modal-secret-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "run_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "checkpoint": "approve_segment_pivot",
    "decision": "segment_2",
    "feedback": "Enterprise segment looks more promising."
  }'
```

**Response**:
```json
{
  "status": "pivot",
  "next_phase": 1,
  "pivot_type": "segment_pivot",
  "message": "Segment pivot approved. Targeting 'Enterprise IT Directors' in Phase 1."
}
```

---

### GET /health

**Purpose**: Health check endpoint (no authentication required)

**File**: `src/modal_app/app.py:572-575`

**Response Code**: `200 OK`

#### Response

```json
{
  "status": "healthy",
  "service": "startupai-validation"
}
```

#### Example

```bash
curl "https://chris00walker--startupai-validation-fastapi-app.modal.run/health"
```

---

## Webhooks (Outbound)

Modal sends webhooks to the product app for HITL checkpoints and completion.

### HITL Webhook

**File**: `src/modal_app/app.py:766-824`

**Target**: `{PRODUCT_APP_URL}/api/crewai/webhook`

**Triggered**: When HITL checkpoint created

```typescript
interface HITLWebhookPayload {
  flow_type: "hitl_checkpoint";
  run_id: string;
  project_id: string;
  user_id: string;
  checkpoint: string;
  title: string;
  description: string;
  options: DecisionOption[];
  recommended: string;
  context: any;
  expires_at: string;  // 7 days from creation
  timestamp: string;
}
```

### Completion Webhook

**File**: `src/modal_app/app.py:827-861`

**Target**: `{PRODUCT_APP_URL}/api/crewai/webhook`

**Triggered**: When validation completes successfully

```typescript
interface CompletionWebhookPayload {
  flow_type: "founder_validation";
  run_id: string;
  status: "completed";
  result: FinalState;  // All phase outputs
}
```

---

## Scheduled Functions

### HITL Expiration Cron

**File**: `src/modal_app/app.py:868-879`

**Schedule**: Every 6 hours (`0 */6 * * *`)

**Purpose**: Expire HITL requests older than 7 days

```python
@app.function(schedule=modal.Cron("0 */6 * * *"))
def expire_stale_hitl_requests():
    """Expire HITL requests older than 7 days."""
    supabase.table("hitl_requests").update({
        "status": "expired",
    }).eq("status", "pending").lt(
        "created_at", (datetime.now() - timedelta(days=7)).isoformat()
    ).execute()
```

---

## Error Handling

### HTTP Status Codes

| Code | Condition |
|------|-----------|
| `200 OK` | Success (GET, POST /hitl/approve) |
| `202 Accepted` | Kickoff accepted (async processing) |
| `400 Bad Request` | Invalid request body or decision |
| `401 Unauthorized` | Missing or invalid bearer token |
| `404 Not Found` | Run ID not found |
| `422 Unprocessable Entity` | Validation error (Pydantic) |
| `500 Internal Server Error` | Unexpected error |

### Error Response Format

```json
{
  "detail": "Error message describing the issue"
}
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SUPABASE_URL` | Yes | - | Supabase project URL |
| `SUPABASE_KEY` | Yes | - | Supabase service role key |
| `WEBHOOK_BEARER_TOKEN` | No | `startupai-modal-secret-2026` | API auth token |
| `PRODUCT_APP_URL` | No | `https://app.startupai.site` | Product app base URL |
| `OPENAI_API_KEY` | Yes | - | OpenAI API key (for crews) |
| `TAVILY_API_KEY` | Yes | - | Tavily API key (for search) |

---

## Modal Function Configuration

**File**: `src/modal_app/app.py:50-95`

```python
app = modal.App("startupai-validation")

# FastAPI app mount
@app.function(
    image=validation_image,
    secrets=[modal.Secret.from_name("startupai-secrets")],
    timeout=3600,  # 1 hour max per request
    allow_concurrent_inputs=100,
)
@modal.asgi_app()
def fastapi_app():
    return web_app

# Background validation function
@app.function(
    image=validation_image,
    secrets=[modal.Secret.from_name("startupai-secrets")],
    timeout=86400,  # 24 hours max for full validation
)
def run_validation(run_id: str):
    # Orchestrates all 5 phases
    pass
```

---

## Rate Limits

Modal enforces these limits:

| Limit | Value |
|-------|-------|
| Concurrent inputs per function | 100 |
| Function timeout | 24 hours (validation), 1 hour (API) |
| Request body size | 6 MB |
| Response body size | 6 MB |

---

## Gaps / TODOs

- [ ] No rate limiting per user/project
- [ ] No request deduplication (same kickoff can create multiple runs)
- [ ] HMAC signature verification not implemented (bearer token only)
- [ ] No OpenAPI/Swagger documentation auto-generated
- [ ] No versioning (e.g., `/v1/kickoff`)

---

## Related Documents

- [hitl-checkpoint-map.md](./hitl-checkpoint-map.md) - HITL checkpoint details
- [state-persistence.md](./state-persistence.md) - Supabase tables
- [integration-contracts.md](./integration-contracts.md) - Product app integration
- [../deployment/environments.md](../deployment/environments.md) - Environment configuration
