# Approval Flow Testing Guide

## Overview

This guide documents how to test the HITL (Human-in-the-Loop) approval flow in StartupAI. The approval flow allows the Modal validation engine to pause and wait for human approval before proceeding.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        HITL Approval Flow                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. MODAL (Validation Engine)                                               │
│     └─> Checkpoint reached (e.g., approve_segment_pivot)                   │
│         └─> Writes approval request to Supabase                            │
│         └─> Terminates container ($0 during HITL)                          │
│                                                                              │
│  2. SUPABASE (State Persistence)                                            │
│     └─> approval_requests table updated                                    │
│         └─> Realtime event triggers                                         │
│                                                                              │
│  3. PRODUCT APP (User Interface)                                            │
│     └─> GET /api/approvals?status=pending                                  │
│         └─> Displays approval request to user                              │
│         └─> User reviews and makes decision                                 │
│         └─> PATCH /api/approvals/{id}                                      │
│             └─> Updates Supabase                                            │
│             └─> Calls Modal resume endpoint                                 │
│                                                                              │
│  4. MODAL (Resume Execution)                                                │
│     └─> POST /hitl/approve                                                  │
│         └─> Loads state from Supabase                                       │
│         └─> Resumes flow from checkpoint                                    │
│         └─> Continues validation                                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## API Endpoints

### 1. List Approvals

**Endpoint**: `GET /api/approvals`

**Purpose**: Fetch approval requests for the authenticated user.

**Query Parameters**:
- `status` (optional): Filter by status (`pending`, `approved`, `rejected`, `all`). Default: `pending`
- `limit` (optional): Number of results per page. Default: `20`
- `offset` (optional): Pagination offset. Default: `0`

**Authentication**:
- Cookie-based (browser flow)
- Bearer token (API/testing): `Authorization: Bearer <supabase_access_token>`

**Response**:
```json
{
  "approvals": [
    {
      "id": "2868edc7-0c6f-4201-a6bb-384cee995410",
      "execution_id": "1c789c9b-317e-4749-94b6-17a455e0c772",
      "task_id": "approve_segment_pivot",
      "user_id": "9b86cca7-86e0-4210-a92f-aa67ef6e86c7",
      "project_id": "project-uuid",
      "approval_type": "segment_pivot",
      "owner_role": "compass",
      "title": "Pivot to Alternative Customer Segment?",
      "description": "...",
      "task_output": { ... },
      "evidence_summary": { ... },
      "options": [
        {
          "id": "segment_1",
          "label": "Tech-Forward Small Business Owners",
          "description": "..."
        },
        {
          "id": "segment_2",
          "label": "Professional Services Firms",
          "description": "..."
        }
      ],
      "status": "pending",
      "created_at": "2026-01-12T10:00:00Z",
      "updated_at": "2026-01-12T10:00:00Z"
    }
  ],
  "client_approvals": [],
  "pagination": {
    "total": 1,
    "own_count": 1,
    "client_count": 0,
    "limit": 20,
    "offset": 0
  }
}
```

### 2. Get Approval Details

**Endpoint**: `GET /api/approvals/{id}`

**Purpose**: Fetch details for a specific approval request.

**Authentication**: Same as List Approvals

**Response**: Single approval object (same structure as list)

### 3. Submit Approval Decision

**Endpoint**: `PATCH /api/approvals/{id}`

**Purpose**: Approve or reject an approval request.

**Authentication**: Same as List Approvals

**Request Body**:
```json
{
  "action": "approve",  // or "reject"
  "decision": "segment_1",  // Optional: the chosen option ID
  "feedback": "I think segment 1 is the better target"  // Optional
}
```

**Response**:
```json
{
  "success": true,
  "approval": { ... },  // Updated approval object
  "message": "Approval approved successfully"
}
```

**Side Effects**:
1. Updates `approval_requests` table in Supabase
2. Records action in `approval_history` table
3. **Calls Modal resume endpoint** (if approved)

### 4. Modal Resume Endpoint

**Endpoint**: `POST https://chris00walker--startupai-validation-fastapi-app.modal.run/hitl/approve`

**Purpose**: Resume validation execution after HITL approval.

**Authentication**: `Authorization: Bearer <MODAL_AUTH_TOKEN>`

**Request Body**:
```json
{
  "run_id": "1c789c9b-317e-4749-94b6-17a455e0c772",
  "checkpoint": "approve_segment_pivot",
  "decision": "segment_1",
  "feedback": "I think segment 1 is the better target",
  "decided_by": "9b86cca7-86e0-4210-a92f-aa67ef6e86c7"
}
```

**Response**:
```json
{
  "status": "resumed",
  "run_id": "1c789c9b-317e-4749-94b6-17a455e0c772",
  "checkpoint": "approve_segment_pivot"
}
```

## Testing with the Test Script

### Prerequisites

1. **Supabase Access Token**: You need a valid Supabase access token for the test user.

   To get the token:
   - Log in to the Product App as the test user
   - Open browser DevTools > Application > Local Storage
   - Find the Supabase auth token

   Or use Supabase CLI:
   ```bash
   supabase auth login
   ```

2. **Environment Variables**:
   ```bash
   export SUPABASE_ACCESS_TOKEN="your-token-here"
   export APP_URL="https://d92f884b-1113-4821-b0a5-54bb8ff8612a.netlify.app"
   export USER_ID="9b86cca7-86e0-4210-a92f-aa67ef6e86c7"
   export APPROVAL_ID="2868edc7-0c6f-4201-a6bb-384cee995410"
   export RUN_ID="1c789c9b-317e-4749-94b6-17a455e0c772"
   export CHECKPOINT="approve_segment_pivot"
   ```

### Run the Test

```bash
cd /home/chris/projects/startupai-crew
./scripts/test_approval_flow.sh
```

### What the Test Does

1. **Fetches pending approvals** - Verifies the list endpoint works
2. **Gets approval details** - Verifies the detail endpoint works
3. **Checks approval status** - Ensures approval is pending
4. **Prompts for approval** - Asks if you want to submit
5. **Submits approval** - Sends approval decision to Product App
6. **Verifies Modal call** - Documents what should happen next

## Manual Testing via cURL

### 1. List Pending Approvals

```bash
curl -X GET \
  -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
  "https://d92f884b-1113-4821-b0a5-54bb8ff8612a.netlify.app/api/approvals?status=pending" \
  | jq '.'
```

### 2. Get Approval Details

```bash
curl -X GET \
  -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
  "https://d92f884b-1113-4821-b0a5-54bb8ff8612a.netlify.app/api/approvals/2868edc7-0c6f-4201-a6bb-384cee995410" \
  | jq '.'
```

### 3. Approve with Decision

```bash
curl -X PATCH \
  -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approve",
    "decision": "segment_1",
    "feedback": "Test approval via cURL"
  }' \
  "https://d92f884b-1113-4821-b0a5-54bb8ff8612a.netlify.app/api/approvals/2868edc7-0c6f-4201-a6bb-384cee995410" \
  | jq '.'
```

### 4. Reject with Feedback

```bash
curl -X PATCH \
  -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "reject",
    "feedback": "Not enough data to make this decision"
  }' \
  "https://d92f884b-1113-4821-b0a5-54bb8ff8612a.netlify.app/api/approvals/2868edc7-0c6f-4201-a6bb-384cee995410" \
  | jq '.'
```

## Frontend Testing

### Via Product App UI

1. **Navigate to Approvals Page**:
   ```
   https://d92f884b-1113-4821-b0a5-54bb8ff8612a.netlify.app/approvals
   ```

2. **Log in as test user**:
   - Email: `chris00walker@proton.me`
   - Password: `W7txYdr7bV0Tc30U0bv&`

3. **View pending approvals**:
   - Should see pending approval(s) listed
   - Click on an approval to view details

4. **Make a decision**:
   - Review the AI recommendation
   - Select an option (if multiple provided)
   - Add feedback (optional)
   - Click "Approve" or "Reject"

5. **Verify submission**:
   - Approval should disappear from pending list
   - Check browser DevTools Network tab for API calls
   - Verify Modal resume call was made

### Via Browser DevTools

1. Open Product App in browser
2. Open DevTools (F12)
3. Go to Network tab
4. Filter by "approvals"
5. Navigate to `/approvals` page
6. Observe API calls:
   - `GET /api/approvals?status=pending`
   - `GET /api/approvals/{id}` (when clicking approval)
   - `PATCH /api/approvals/{id}` (when approving/rejecting)

## Verifying Modal Integration

### Check Modal Logs

```bash
modal app logs startupai-validation
```

Look for:
```
[HITL] Checkpoint reached: approve_segment_pivot
[HITL] Writing approval request to Supabase
[HITL] Container terminating, awaiting approval
...
[HITL] Resume request received: run_id=1c789c9b-317e-4749-94b6-17a455e0c772
[HITL] Loading state from Supabase
[HITL] Resuming from checkpoint: approve_segment_pivot
```

### Check Supabase Tables

```sql
-- View approval requests
SELECT * FROM approval_requests 
WHERE user_id = '9b86cca7-86e0-4210-a92f-aa67ef6e86c7'
ORDER BY created_at DESC;

-- View approval history
SELECT * FROM approval_history
WHERE approval_request_id = '2868edc7-0c6f-4201-a6bb-384cee995410'
ORDER BY created_at DESC;

-- View validation run state
SELECT * FROM validation_runs
WHERE id = '1c789c9b-317e-4749-94b6-17a455e0c772';
```

## Common Issues

### 401 Unauthorized

**Cause**: Invalid or expired Supabase access token

**Fix**: Get a fresh token from the browser or Supabase CLI

### 403 Access Denied

**Cause**: User doesn't own the approval or isn't the consultant of the owner

**Fix**: Verify `user_id` matches the approval's `user_id`

### 400 Approval Already Decided

**Cause**: Approval has already been approved or rejected

**Fix**: Create a new approval request or reset the existing one in Supabase

### Modal Resume Not Called

**Cause**: Environment variables not configured in Product App

**Fix**: Verify in Product App's `.env.local`:
```
MODAL_HITL_APPROVE_URL=https://chris00walker--startupai-validation-fastapi-app.modal.run/hitl/approve
MODAL_AUTH_TOKEN=startupai-modal-secret-2026
```

## Next Steps

After verifying the approval flow works:

1. **Test all 10 HITL checkpoints** - See `CLAUDE.md` for full list
2. **Test approval preferences** - Auto-approve low-risk decisions
3. **Test consultant access** - Consultant approving for client
4. **Test Realtime updates** - Multiple browser tabs open
5. **Test error handling** - Network failures, timeouts
6. **Load test** - Multiple concurrent approvals

## Related Documentation

- **HITL Architecture**: `docs/adr/002-modal-serverless-migration.md`
- **API Contracts**: `docs/master-architecture/reference/approval-workflow.md`
- **Database Schema**: `docs/master-architecture/reference/database-schema.md`
- **Frontend Components**: `frontend/src/components/approvals/`
- **Backend API**: `frontend/src/app/api/approvals/`

---

**Last Updated**: 2026-01-12
**Maintainer**: Chris Walker
