# Approval Flow Testing - Quick Start

## What You Need

1. **Your Supabase Access Token**
   - Log in to: https://d92f884b-1113-4821-b0a5-54bb8ff8612a.netlify.app
   - Email: `chris00walker@proton.me`
   - Password: `W7txYdr7bV0Tc30U0bv&`
   - Open DevTools (F12) > Application > Local Storage
   - Find: `sb-eqxropalhxjeyvfcoyxg-auth-token`
   - Copy the `access_token` value

2. **Set Environment Variable**
   ```bash
   export SUPABASE_ACCESS_TOKEN="eyJhbG..."
   ```

## Quick Test (Recommended)

```bash
cd /home/chris/projects/startupai-crew
./scripts/quick_approval_test.sh
```

**What it does:**
1. Fetches your pending approval
2. Shows the details
3. Asks if you want to approve it
4. Submits the approval if you say yes

## Full Test (Comprehensive)

```bash
export SUPABASE_ACCESS_TOKEN="eyJhbG..."
./scripts/test_approval_flow.sh
```

**What it does:**
1. Lists all pending approvals
2. Gets specific approval details
3. Checks approval status
4. Prompts for approval submission
5. Verifies Modal integration
6. Documents what should happen

## Manual Testing

### 1. List Pending Approvals

```bash
curl -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
  "https://d92f884b-1113-4821-b0a5-54bb8ff8612a.netlify.app/api/approvals?status=pending" \
  | jq '.'
```

### 2. Get Approval Details

```bash
curl -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
  "https://d92f884b-1113-4821-b0a5-54bb8ff8612a.netlify.app/api/approvals/2868edc7-0c6f-4201-a6bb-384cee995410" \
  | jq '.'
```

### 3. Submit Approval

```bash
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

## Your Current Test Data

- **Approval ID**: `2868edc7-0c6f-4201-a6bb-384cee995410`
- **Run ID**: `1c789c9b-317e-4749-94b6-17a455e0c772`
- **Checkpoint**: `approve_segment_pivot`
- **Decision Options**: `segment_1`, `segment_2`, etc.

## What Happens When You Approve

```
1. Frontend submits approval
   ↓
2. Product App API route (/api/approvals/[id])
   - Updates Supabase approval_requests table
   - Records in approval_history table
   - Calls Modal /hitl/approve endpoint
   ↓
3. Modal receives resume request
   - Loads saved state from Supabase
   - Resumes flow from checkpoint
   - Continues validation with your decision
   ↓
4. Validation continues
   - Updates progress in Supabase
   - Frontend shows real-time updates (via Realtime)
```

## Verifying It Worked

### 1. Check Product App Response

Should return:
```json
{
  "success": true,
  "approval": { ... },
  "message": "Approval approved successfully"
}
```

### 2. Check Modal Logs

```bash
modal app logs startupai-validation
```

Look for:
```
[HITL] Resume request received: run_id=1c789c9b-317e-4749-94b6-17a455e0c772
[HITL] Loading state from Supabase
[HITL] Resuming from checkpoint: approve_segment_pivot
```

### 3. Check Supabase

Query in Supabase SQL Editor:
```sql
SELECT status, decision, human_feedback, decided_at 
FROM approval_requests 
WHERE id = '2868edc7-0c6f-4201-a6bb-384cee995410';
```

Should show:
- `status`: `'approved'`
- `decision`: `'segment_1'`
- `human_feedback`: Your feedback text
- `decided_at`: Timestamp

## Common Issues

### "401 Unauthorized"
- Token expired or invalid
- Get fresh token from browser

### "403 Access Denied"
- User doesn't own the approval
- Check user_id matches

### "400 Already Decided"
- Approval already processed
- Check status in Supabase

### Modal Doesn't Resume
- Check Product App env vars:
  ```
  MODAL_HITL_APPROVE_URL=https://...
  MODAL_AUTH_TOKEN=startupai-modal-secret-2026
  ```

## Documentation

- **Full Testing Guide**: `docs/testing/approval-flow-testing.md`
- **Summary**: `docs/testing/APPROVAL_FLOW_SUMMARY.md`
- **Architecture**: `docs/adr/002-modal-serverless-migration.md`
- **API Contracts**: `docs/master-architecture/reference/approval-workflow.md`

## Scripts

- `quick_approval_test.sh` - Simple test (recommended)
- `test_approval_flow.sh` - Full test with verification

---

**Questions?** Check `APPROVAL_FLOW_SUMMARY.md` for detailed explanations.
