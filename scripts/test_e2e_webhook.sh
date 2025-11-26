#!/bin/bash
# =============================================================================
# E2E Webhook Test Script
# =============================================================================
# Tests the full flow: CrewAI Kickoff → Validation → Webhook → Supabase
#
# Prerequisites:
#   - jq installed (sudo apt install jq)
#   - CrewAI AMP env vars configured (STARTUPAI_WEBHOOK_URL, STARTUPAI_WEBHOOK_BEARER_TOKEN)
#   - Netlify CREW_CONTRACT_BEARER configured
#
# Usage:
#   ./scripts/test_e2e_webhook.sh
#
# =============================================================================

set -e

# Configuration
CREWAI_URL="https://startupai-b4d5c1dd-27e2-4163-b9fb-a18ca06ca-4f4192a6.crewai.com"
CREWAI_TOKEN="f4cc39d92520"
# Use Netlify URL (app.startupai.site DNS may not resolve from all environments)
WEBHOOK_URL="https://app-startupai-site.netlify.app/api/crewai/webhook"
WEBHOOK_TOKEN="startupai-webhook-secret-2024"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=============================================${NC}"
echo -e "${BLUE}  StartupAI E2E Webhook Test${NC}"
echo -e "${BLUE}=============================================${NC}"
echo ""

# -----------------------------------------------------------------------------
# Step 1: Test Webhook Endpoint Directly
# -----------------------------------------------------------------------------
echo -e "${YELLOW}Step 1: Testing webhook endpoint directly...${NC}"

# Create a minimal test payload
TEST_PAYLOAD=$(cat <<'EOF'
{
  "flow_type": "founder_validation",
  "project_id": "test-e2e-00000000-0000-0000-0000-000000000001",
  "user_id": "test-e2e-00000000-0000-0000-0000-000000000001",
  "kickoff_id": "test-kickoff-$(date +%s)",
  "session_id": null,
  "validation_report": {
    "id": "test-report-001",
    "business_idea": "E2E Test Business Idea",
    "validation_outcome": "PROCEED",
    "evidence_summary": "This is an E2E test - not a real validation",
    "pivot_recommendation": "None - this is a test",
    "next_steps": ["Verify webhook works", "Check Supabase", "Celebrate"]
  },
  "value_proposition_canvas": {
    "customer_segment": "Test Segment",
    "jobs": ["Test Job 1"],
    "pains": ["Test Pain 1"],
    "gains": ["Test Gain 1"],
    "products_services": ["Test Product"],
    "pain_relievers": ["Test Pain Reliever"],
    "gain_creators": ["Test Gain Creator"]
  },
  "evidence": {
    "desirability": {"signal": "STRONG", "confidence": 0.8},
    "feasibility": {"signal": "POSSIBLE", "confidence": 0.7},
    "viability": {"signal": "PROFITABLE", "confidence": 0.6}
  },
  "qa_report": {
    "quality_score": 85,
    "issues": [],
    "recommendations": ["This is a test"]
  }
}
EOF
)

echo "Sending test payload to webhook..."
WEBHOOK_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$WEBHOOK_URL" \
  -H "Authorization: Bearer $WEBHOOK_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$TEST_PAYLOAD")

HTTP_CODE=$(echo "$WEBHOOK_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$WEBHOOK_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
  echo -e "${GREEN}✅ Webhook responded with 200 OK${NC}"
  echo "   Response: $RESPONSE_BODY"
else
  echo -e "${RED}❌ Webhook failed with HTTP $HTTP_CODE${NC}"
  echo "   Response: $RESPONSE_BODY"
  echo ""
  echo -e "${YELLOW}Troubleshooting:${NC}"
  echo "   - Check Netlify logs: netlify logs --filter frontend"
  echo "   - Verify CREW_CONTRACT_BEARER is set in Netlify"
  exit 1
fi

echo ""

# -----------------------------------------------------------------------------
# Step 2: Check CrewAI AMP Status
# -----------------------------------------------------------------------------
echo -e "${YELLOW}Step 2: Checking CrewAI AMP deployment status...${NC}"

STATUS_RESPONSE=$(curl -s -X GET "$CREWAI_URL/health" \
  -H "Authorization: Bearer $CREWAI_TOKEN" 2>/dev/null || echo '{"status": "unknown"}')

echo "CrewAI Health: $STATUS_RESPONSE"

# Get inputs schema
echo ""
echo "Fetching inputs schema..."
INPUTS_RESPONSE=$(curl -s -X GET "$CREWAI_URL/inputs" \
  -H "Authorization: Bearer $CREWAI_TOKEN")

echo "Inputs schema: $INPUTS_RESPONSE"
echo ""

# -----------------------------------------------------------------------------
# Step 3: Trigger CrewAI Kickoff (Optional - Long Running)
# -----------------------------------------------------------------------------
echo -e "${YELLOW}Step 3: Triggering CrewAI validation flow...${NC}"
echo ""
echo -e "${BLUE}NOTE: This will start a real validation flow which takes 5-15 minutes.${NC}"
echo ""
read -p "Do you want to trigger a full validation? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo "Starting validation flow..."

  KICKOFF_PAYLOAD=$(cat <<'EOF'
{
  "entrepreneur_input": "E2E Test: A SaaS platform that helps small businesses automate their customer feedback collection and analysis using AI. Target market: SMBs with 10-50 employees who currently use manual survey tools.",
  "project_id": "e2e-test-project-001",
  "user_id": "e2e-test-user-001"
}
EOF
)

  KICKOFF_RESPONSE=$(curl -s -X POST "$CREWAI_URL/kickoff" \
    -H "Authorization: Bearer $CREWAI_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$KICKOFF_PAYLOAD")

  echo "Kickoff response: $KICKOFF_RESPONSE"

  # Extract kickoff_id if available
  KICKOFF_ID=$(echo "$KICKOFF_RESPONSE" | jq -r '.kickoff_id // .id // empty' 2>/dev/null)

  if [ -n "$KICKOFF_ID" ]; then
    echo -e "${GREEN}✅ Validation started with kickoff_id: $KICKOFF_ID${NC}"
    echo ""
    echo "To check status:"
    echo "  curl -s '$CREWAI_URL/status/$KICKOFF_ID' -H 'Authorization: Bearer $CREWAI_TOKEN'"
    echo ""
    echo "To view logs:"
    echo "  crewai deploy logs --uuid b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b"
  else
    echo -e "${YELLOW}⚠️  Kickoff initiated but no kickoff_id returned${NC}"
    echo "   Response: $KICKOFF_RESPONSE"
  fi
else
  echo "Skipping full validation test."
fi

echo ""

# -----------------------------------------------------------------------------
# Step 4: Summary
# -----------------------------------------------------------------------------
echo -e "${BLUE}=============================================${NC}"
echo -e "${BLUE}  Test Summary${NC}"
echo -e "${BLUE}=============================================${NC}"
echo ""
echo "Webhook Direct Test: $([ "$HTTP_CODE" = "200" ] && echo -e "${GREEN}PASSED${NC}" || echo -e "${RED}FAILED${NC}")"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Check Supabase 'reports' table for new entries"
echo "2. Check CrewAI logs: crewai deploy logs --uuid b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b"
echo "3. Check Netlify logs: netlify logs --filter frontend"
echo ""
echo -e "${BLUE}Manual Supabase Check:${NC}"
echo "  SELECT * FROM reports ORDER BY generated_at DESC LIMIT 5;"
echo ""
