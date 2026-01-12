#!/bin/bash
# Quick Approval Flow Test
# 
# Simple script to test approval flow with your current pending approval

set -e

# Configuration (update these with your values)
APP_URL="https://d92f884b-1113-4821-b0a5-54bb8ff8612a.netlify.app"
APPROVAL_ID="2868edc7-0c6f-4201-a6bb-384cee995410"

# Check for access token
if [ -z "$SUPABASE_ACCESS_TOKEN" ]; then
  echo "❌ ERROR: SUPABASE_ACCESS_TOKEN not set"
  echo ""
  echo "To get your token:"
  echo "1. Log in to https://d92f884b-1113-4821-b0a5-54bb8ff8612a.netlify.app"
  echo "2. Open DevTools > Application > Local Storage"
  echo "3. Look for 'sb-*-auth-token'"
  echo "4. Copy the 'access_token' value"
  echo ""
  echo "Then run:"
  echo '  export SUPABASE_ACCESS_TOKEN="your-token-here"'
  exit 1
fi

echo "Testing Approval Flow"
echo "====================="
echo ""

# Test 1: Get approval details
echo "1. Fetching approval details..."
RESPONSE=$(curl -s \
  -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
  "${APP_URL}/api/approvals/${APPROVAL_ID}")

echo "$RESPONSE" | jq '.' || echo "$RESPONSE"
echo ""

# Check status
STATUS=$(echo "$RESPONSE" | jq -r '.status' 2>/dev/null)

if [ "$STATUS" = "null" ]; then
  echo "❌ Failed to fetch approval (check token)"
  exit 1
fi

echo "Status: $STATUS"
echo ""

if [ "$STATUS" = "pending" ]; then
  read -p "Approval is pending. Submit approval? (y/n): " -n 1 -r
  echo ""
  
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "2. Submitting approval..."
    
    SUBMIT_RESPONSE=$(curl -s \
      -X PATCH \
      -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
      -H "Content-Type: application/json" \
      -d '{
        "action": "approve",
        "decision": "segment_1",
        "feedback": "Approved via quick test script"
      }' \
      "${APP_URL}/api/approvals/${APPROVAL_ID}")
    
    echo "$SUBMIT_RESPONSE" | jq '.' || echo "$SUBMIT_RESPONSE"
    echo ""
    echo "✅ Approval submitted!"
  else
    echo "Skipped approval submission"
  fi
else
  echo "⚠️  Approval is not pending (status: $STATUS)"
fi

echo ""
echo "Done!"
