# Approval Flow Testing Summary

## Quick Reference

**Your Current Test Case:**
- **Approval ID**: `2868edc7-0c6f-4201-a6bb-384cee995410`
- **Run ID**: `1c789c9b-317e-4749-94b6-17a455e0c772`
- **Checkpoint**: `approve_segment_pivot`
- **User ID**: `9b86cca7-86e0-4210-a92f-aa67ef6e86c7`
- **User Email**: `chris00walker@proton.me`
- **App URL**: `https://d92f884b-1113-4821-b0a5-54bb8ff8612a.netlify.app`

## How the Approval Flow Works

### 1. Frontend Fetches Approvals

**Hook**: `useApprovals` (`frontend/src/hooks/useApprovals.ts`)

```typescript
const { approvals, approve, reject } = useApprovals('pending');
```

**API Call**:
```
GET /api/approvals?status=pending
```

**Features**:
- Cookie-based auth (browser) OR Bearer token (API/testing)
- Supabase Realtime subscription for live updates
- Separate lists for own approvals and client approvals (consultants)

### 2. User Reviews Approval

**Page**: `/approvals` (`frontend/src/app/approvals/page.tsx`)

**Components**:
- `ApprovalList` - Lists all pending approvals
- `ApprovalDetailModal` - Shows approval details and decision options

**Data Displayed**:
- Title and description from AI
- Task output and evidence summary
- Multiple choice options (if applicable)
- Project context

### 3. User Submits Decision

**Action**: User clicks "Approve" or "Reject"

**API Call**:
```
PATCH /api/approvals/{id}
Body: {
  "action": "approve" | "reject",
  "decision": "segment_1",  // Optional: chosen option
  "feedback": "User's reasoning"  // Optional
}
```

**Route**: `frontend/src/app/api/approvals/[id]/route.ts`

**What Happens**:
1. Validates request (auth, status, access)
2. Updates `approval_requests` table in Supabase
3. Records action in `approval_history` table
4. **If approved**: Calls Modal resume endpoint
5. Returns success response

### 4. Modal Resumes Execution

**Endpoint**:
```
POST https://chris00walker--startupai-validation-fastapi-app.modal.run/hitl/approve
```

**Request Body**:
```json
{
  "run_id": "1c789c9b-317e-4749-94b6-17a455e0c772",
  "checkpoint": "approve_segment_pivot",
  "decision": "segment_1",
  "feedback": "User's reasoning",
  "decided_by": "9b86cca7-86e0-4210-a92f-aa67ef6e86c7"
}
```

**What Modal Does**:
1. Loads saved state from Supabase
2. Resumes flow from checkpoint
3. Continues validation with user's decision
4. Updates progress in Supabase

## Testing Methods

### Method 1: Browser UI (Recommended)

1. Navigate to: `https://d92f884b-1113-4821-b0a5-54bb8ff8612a.netlify.app/approvals`
2. Log in as: `chris00walker@proton.me`
3. View pending approvals
4. Click on approval to see details
5. Choose option and click "Approve"
6. Observe:
   - Approval disappears from list
   - Network tab shows API calls
   - Modal logs show resume

### Method 2: Quick Test Script

```bash
# Get your Supabase access token first
# (from browser DevTools > Application > Local Storage > sb-*-auth-token)

export SUPABASE_ACCESS_TOKEN="your-token-here"

# Run the test
cd /home/chris/projects/startupai-crew
./scripts/quick_approval_test.sh
```

### Method 3: Full Test Script

```bash
export SUPABASE_ACCESS_TOKEN="your-token-here"
export APP_URL="https://d92f884b-1113-4821-b0a5-54bb8ff8612a.netlify.app"
export APPROVAL_ID="2868edc7-0c6f-4201-a6bb-384cee995410"
export RUN_ID="1c789c9b-317e-4749-94b6-17a455e0c772"
export CHECKPOINT="approve_segment_pivot"

./scripts/test_approval_flow.sh
```

### Method 4: Manual cURL

```bash
# 1. List pending approvals
curl -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
  "https://d92f884b-1113-4821-b0a5-54bb8ff8612a.netlify.app/api/approvals?status=pending" \
  | jq '.'

# 2. Get approval details
curl -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
  "https://d92f884b-1113-4821-b0a5-54bb8ff8612a.netlify.app/api/approvals/2868edc7-0c6f-4201-a6bb-384cee995410" \
  | jq '.'

# 3. Submit approval
curl -X PATCH \
  -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approve",
    "decision": "segment_1",
    "feedback": "Test approval"
  }' \
  "https://d92f884b-1113-4821-b0a5-54bb8ff8612a.netlify.app/api/approvals/2868edc7-0c6f-4201-a6bb-384cee995410" \
  | jq '.'
```

## API Routes Summary

### Product App (Netlify)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/approvals` | List approvals (own + client) |
| GET | `/api/approvals/{id}` | Get approval details |
| PATCH | `/api/approvals/{id}` | Submit approval decision |
| POST | `/api/approvals/webhook` | Receive approval requests from Modal |

**Source**: `/home/chris/projects/app.startupai.site/frontend/src/app/api/approvals/`

### Modal (Serverless)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/hitl/approve` | Resume validation after approval |
| GET | `/status/{run_id}` | Get validation status |

**Source**: `/home/chris/projects/startupai-crew/src/modal_app/app.py`

## Environment Variables

### Product App (.env.local)

```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://eqxropalhxjeyvfcoyxg.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# Modal Integration
MODAL_HITL_APPROVE_URL=https://chris00walker--startupai-validation-fastapi-app.modal.run/hitl/approve
MODAL_AUTH_TOKEN=startupai-modal-secret-2026

# Webhook Auth
CREW_CONTRACT_BEARER=startupai-webhook-secret-2024
```

### Modal (Secrets)

```bash
# Set via: modal secret create startupai-secrets ...
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
SUPABASE_URL=https://eqxropalhxjeyvfcoyxg.supabase.co
SUPABASE_KEY=eyJ...
NETLIFY_ACCESS_TOKEN=xxx
```

## Decision Value Mapping

The Product App and Modal use different decision values:

### Frontend Decision Values
- `"approve"` - Generic approval
- `"reject"` - Generic rejection
- `"segment_1"`, `"segment_2"`, etc. - Specific segment choices
- `"override_proceed"` - Override and proceed
- `"iterate"` - Iterate on current approach

### Modal Expected Values
- `"approved"` - Generic approval
- `"rejected"` - Generic rejection
- `"segment_1"` through `"segment_9"` - Segment choices
- `"custom_segment"` - Custom segment
- `"override_proceed"` - Override proceed
- `"iterate"` - Iterate

**Mapping** (handled in API route):
```typescript
const modalDecision = body.decision === 'approve' ? 'approved' :
                      body.decision === 'reject' ? 'rejected' :
                      body.decision || 'approved';
```

## Database Tables

### approval_requests

```sql
id                   uuid PRIMARY KEY
execution_id         text NOT NULL  -- run_id from Modal
task_id              text NOT NULL  -- checkpoint name
kickoff_id           text
user_id              uuid NOT NULL  -- owner
project_id           uuid
approval_type        text NOT NULL  -- segment_pivot, gate_progression, etc.
owner_role           text NOT NULL  -- compass, ledger, pulse, guardian, forge
title                text NOT NULL
description          text NOT NULL
task_output          jsonb
evidence_summary     jsonb
options              jsonb          -- Multiple choice options
status               text NOT NULL  -- pending, approved, rejected
decision             text           -- Chosen option ID
human_feedback       text           -- User's reasoning
decided_by           uuid           -- Who decided
decided_at           timestamptz
auto_approvable      boolean
auto_approve_reason  text
created_at           timestamptz
updated_at           timestamptz
```

### approval_history

```sql
id                   uuid PRIMARY KEY
approval_request_id  uuid NOT NULL
action               text NOT NULL  -- created, viewed, approved, rejected, auto_approved
actor_id             uuid
actor_type           text NOT NULL  -- user, system
details              jsonb
created_at           timestamptz
```

## Troubleshooting

### Issue: 401 Unauthorized

**Cause**: Invalid or expired Supabase access token

**Solution**: 
1. Log in to Product App
2. Open DevTools > Application > Local Storage
3. Find `sb-eqxropalhxjeyvfcoyxg-auth-token`
4. Copy `access_token` value
5. `export SUPABASE_ACCESS_TOKEN="..."`

### Issue: 403 Access Denied

**Cause**: User doesn't own the approval

**Solution**: Verify `user_id` matches approval's `user_id`

### Issue: 400 Already Decided

**Cause**: Approval already approved or rejected

**Solution**: Create new approval or reset in Supabase

### Issue: Modal Resume Not Called

**Cause**: Environment variables not configured

**Solution**: Check Product App `.env.local`:
```bash
MODAL_HITL_APPROVE_URL=https://chris00walker--startupai-validation-fastapi-app.modal.run/hitl/approve
MODAL_AUTH_TOKEN=startupai-modal-secret-2026
```

## Verification Checklist

- [ ] Approval fetched successfully
- [ ] Approval details displayed correctly
- [ ] Approval submission accepted (200 OK)
- [ ] Supabase `approval_requests` updated
- [ ] Supabase `approval_history` recorded
- [ ] Modal `/hitl/approve` called
- [ ] Modal logs show resume
- [ ] Validation continues in Modal
- [ ] Frontend shows updated status (via Realtime)

## Next Steps

1. **Test with Browser UI** - Most realistic user experience
2. **Test with Script** - Automated verification
3. **Check Modal Logs** - Verify resume happened
4. **Query Supabase** - Verify database updates
5. **Test All Checkpoints** - See `CLAUDE.md` for 10 HITL checkpoints
6. **Test Error Cases** - Network failures, invalid decisions
7. **Test Consultant Flow** - Consultant approving for client
8. **Test Auto-Approve** - Configure preferences and test

## Related Files

### Frontend (app.startupai.site)
```
frontend/src/app/approvals/page.tsx              # Approvals dashboard
frontend/src/app/api/approvals/route.ts          # List approvals
frontend/src/app/api/approvals/[id]/route.ts     # Get/submit approval
frontend/src/app/api/approvals/webhook/route.ts  # Receive from Modal
frontend/src/hooks/useApprovals.ts               # Approval hook
frontend/src/components/approvals/               # UI components
```

### Backend (startupai-crew)
```
src/modal_app/app.py                             # Modal entry point
src/modal_app/phases/*.py                        # Phase flows
src/state/persistence.py                         # Checkpoint/resume
src/state/models.py                              # State models
```

### Documentation
```
docs/testing/approval-flow-testing.md            # Full testing guide
docs/adr/002-modal-serverless-migration.md       # Architecture
docs/master-architecture/reference/approval-workflow.md  # Workflow spec
```

---

**Last Updated**: 2026-01-12
**Maintainer**: Chris Walker
