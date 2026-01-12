#!/bin/bash
# Test Approval Flow
# 
# Tests the HITL approval flow end-to-end:
# 1. Fetch pending approvals
# 2. Get approval details
# 3. Submit approval decision
# 4. Verify Modal receives the approval

set -e

# Configuration
APP_URL="${APP_URL:-https://d92f884b-1113-4821-b0a5-54bb8ff8612a.netlify.app}"
USER_ID="${USER_ID:-9b86cca7-86e0-4210-a92f-aa67ef6e86c7}"
APPROVAL_ID="${APPROVAL_ID:-2868edc7-0c6f-4201-a6bb-384cee995410}"
RUN_ID="${RUN_ID:-1c789c9b-317e-4749-94b6-17a455e0c772}"
CHECKPOINT="${CHECKPOINT:-approve_segment_pivot}"

# Get Supabase access token (you need to provide this)
if [ -z "$SUPABASE_ACCESS_TOKEN" ]; then
  echo "ERROR: SUPABASE_ACCESS_TOKEN environment variable not set"
  echo "Please authenticate with Supabase and get your access token"
  echo ""
  echo "Example:"
  echo '  export SUPABASE_ACCESS_TOKEN="your-token-here"'
  exit 1
fi

echo "=========================================="
echo "Testing StartupAI Approval Flow"
echo "=========================================="
echo ""

# Test 1: Fetch pending approvals
echo "1. Fetching pending approvals..."
echo "   GET ${APP_URL}/api/approvals?status=pending"
echo ""

APPROVALS_RESPONSE=$(curl -s -w "\n%{http_code}" \
  -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
  "${APP_URL}/api/approvals?status=pending")

HTTP_CODE=$(echo "$APPROVALS_RESPONSE" | tail -n1)
APPROVALS_BODY=$(echo "$APPROVALS_RESPONSE" | sed '$d')

echo "   Response Code: ${HTTP_CODE}"
echo "   Response Body:"
echo "$APPROVALS_BODY" | jq '.' 2>/dev/null || echo "$APPROVALS_BODY"
echo ""

if [ "$HTTP_CODE" != "200" ]; then
  echo "   ❌ FAILED: Expected 200, got ${HTTP_CODE}"
  exit 1
fi

echo "   ✅ SUCCESS: Fetched approvals"
echo ""

# Test 2: Get specific approval details
echo "2. Fetching approval details..."
echo "   GET ${APP_URL}/api/approvals/${APPROVAL_ID}"
echo ""

APPROVAL_RESPONSE=$(curl -s -w "\n%{http_code}" \
  -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
  "${APP_URL}/api/approvals/${APPROVAL_ID}")

HTTP_CODE=$(echo "$APPROVAL_RESPONSE" | tail -n1)
APPROVAL_BODY=$(echo "$APPROVAL_RESPONSE" | sed '$d')

echo "   Response Code: ${HTTP_CODE}"
echo "   Response Body:"
echo "$APPROVAL_BODY" | jq '.' 2>/dev/null || echo "$APPROVAL_BODY"
echo ""

if [ "$HTTP_CODE" != "200" ]; then
  echo "   ❌ FAILED: Expected 200, got ${HTTP_CODE}"
  exit 1
fi

echo "   ✅ SUCCESS: Fetched approval details"
echo ""

# Test 3: Check approval status
APPROVAL_STATUS=$(echo "$APPROVAL_BODY" | jq -r '.status' 2>/dev/null)

if [ "$APPROVAL_STATUS" = "pending" ]; then
  echo "3. Approval is pending - ready to approve"
  echo ""
  
  # Ask user if they want to submit approval
  read -p "   Do you want to submit the approval? (y/n): " -n 1 -r
  echo ""
  
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "4. Submitting approval..."
    echo "   PATCH ${APP_URL}/api/approvals/${APPROVAL_ID}"
    echo ""
    
    # Submit approval with segment_1 decision
    APPROVAL_SUBMIT=$(curl -s -w "\n%{http_code}" \
      -X PATCH \
      -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
      -H "Content-Type: application/json" \
      -d "{
        \"action\": \"approve\",
        \"decision\": \"segment_1\",
        \"feedback\": \"Test approval via script\"
      }" \
      "${APP_URL}/api/approvals/${APPROVAL_ID}")
    
    HTTP_CODE=$(echo "$APPROVAL_SUBMIT" | tail -n1)
    SUBMIT_BODY=$(echo "$APPROVAL_SUBMIT" | sed '$d')
    
    echo "   Response Code: ${HTTP_CODE}"
    echo "   Response Body:"
    echo "$SUBMIT_BODY" | jq '.' 2>/dev/null || echo "$SUBMIT_BODY"
    echo ""
    
    if [ "$HTTP_CODE" != "200" ]; then
      echo "   ❌ FAILED: Expected 200, got ${HTTP_CODE}"
      exit 1
    fi
    
    echo "   ✅ SUCCESS: Approval submitted"
    echo ""
    
    echo "5. Verify approval was sent to Modal..."
    echo "   The Product App should have called:"
    echo "   POST https://chris00walker--startupai-validation-fastapi-app.modal.run/hitl/approve"
    echo "   With payload:"
    echo "   {"
    echo "     \"run_id\": \"${RUN_ID}\","
    echo "     \"checkpoint\": \"${CHECKPOINT}\","
    echo "     \"decision\": \"segment_1\","
    echo "     \"feedback\": \"Test approval via script\","
    echo "     \"decided_by\": \"${USER_ID}\""
    echo "   }"
    echo ""
    echo "   Check Modal logs for confirmation."
    echo ""
  else
    echo ""
    echo "   Skipping approval submission"
    echo ""
  fi
else
  echo "3. Approval status: ${APPROVAL_STATUS}"
  echo "   ⚠️  Approval is not pending - cannot approve"
  echo ""
fi

echo "=========================================="
echo "Test Complete"
echo "=========================================="
