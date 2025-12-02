#!/bin/bash
# =============================================================================
# E2E Webhook Test Script
# =============================================================================
# Tests the full flow: CrewAI Kickoff → Validation → Webhook → Supabase
#
# Prerequisites:
#   - jq installed (sudo apt install jq)
#   - SUPABASE_URL and SUPABASE_KEY environment variables set
#   - CrewAI AMP env vars configured
#
# Usage:
#   ./scripts/test_e2e_webhook.sh              # Interactive mode
#   ./scripts/test_e2e_webhook.sh --quick      # Quick webhook test only
#   ./scripts/test_e2e_webhook.sh --full       # Full E2E with Supabase verification
#
# =============================================================================

set -e

# Configuration
CREWAI_URL="https://startupai-b4d5c1dd-27e2-4163-b9fb-a18ca06ca-4f4192a6.crewai.com"
CREWAI_TOKEN="${CREW_CONTRACT_BEARER:-f4cc39d92520}"
WEBHOOK_URL="https://app-startupai-site.netlify.app/api/crewai/webhook"
WEBHOOK_TOKEN="${STARTUPAI_WEBHOOK_BEARER_TOKEN:-startupai-webhook-secret-2024}"

# Supabase configuration (from environment)
SUPABASE_URL="${SUPABASE_URL:-}"
SUPABASE_KEY="${SUPABASE_KEY:-}"

# Test identifiers (unique per run)
TEST_RUN_ID="e2e-$(date +%s)"
TEST_PROJECT_ID="e2e-test-${TEST_RUN_ID}"
TEST_USER_ID="e2e-user-${TEST_RUN_ID}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Parse arguments
MODE="interactive"
if [ "$1" = "--quick" ]; then
    MODE="quick"
elif [ "$1" = "--full" ]; then
    MODE="full"
fi

echo -e "${BLUE}=============================================${NC}"
echo -e "${BLUE}  StartupAI E2E Webhook Test${NC}"
echo -e "${BLUE}=============================================${NC}"
echo -e "Mode: ${CYAN}$MODE${NC}"
echo -e "Test Run ID: ${CYAN}$TEST_RUN_ID${NC}"
echo ""

# -----------------------------------------------------------------------------
# Helper: Verify Supabase Configuration
# -----------------------------------------------------------------------------
verify_supabase_config() {
    if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
        echo -e "${YELLOW}⚠️  Supabase credentials not configured${NC}"
        echo "   Set SUPABASE_URL and SUPABASE_KEY environment variables"
        echo "   Supabase verification will be skipped"
        return 1
    fi
    return 0
}

# -----------------------------------------------------------------------------
# Helper: Query Supabase
# -----------------------------------------------------------------------------
query_supabase() {
    local table="$1"
    local filter="$2"

    curl -s "${SUPABASE_URL}/rest/v1/${table}?${filter}" \
        -H "apikey: ${SUPABASE_KEY}" \
        -H "Authorization: Bearer ${SUPABASE_KEY}"
}

# -----------------------------------------------------------------------------
# Helper: Count Records
# -----------------------------------------------------------------------------
count_records() {
    local table="$1"
    local filter="$2"

    local result=$(query_supabase "$table" "$filter")
    echo "$result" | jq 'length' 2>/dev/null || echo "0"
}

# -----------------------------------------------------------------------------
# Step 1: Test Webhook Endpoint Directly
# -----------------------------------------------------------------------------
echo -e "${YELLOW}Step 1: Testing webhook endpoint with contract-compliant payload...${NC}"

# Create a payload matching the FounderValidationPayload contract
TEST_PAYLOAD=$(cat <<EOF
{
  "flow_type": "founder_validation",
  "project_id": "${TEST_PROJECT_ID}",
  "user_id": "${TEST_USER_ID}",
  "kickoff_id": "kick-${TEST_RUN_ID}",
  "session_id": null,
  "validation_report": {
    "id": "rpt-${TEST_RUN_ID}",
    "business_idea": "E2E Test: AI-powered logistics platform",
    "validation_outcome": "PROCEED",
    "evidence_summary": "E2E test validation - strong signals across all dimensions",
    "pivot_recommendation": null,
    "next_steps": ["Build MVP", "Find first customer", "E2E test step"]
  },
  "value_proposition_canvas": {
    "Test Segment": {
      "customer_profile": {
        "segment_name": "Test Segment",
        "jobs": [{"functional": "Test job", "importance": 8}],
        "pains": ["Test pain"],
        "gains": ["Test gain"]
      },
      "value_map": {
        "products_services": ["Test product"],
        "pain_relievers": {"Test pain": "Test reliever"},
        "gain_creators": {"Test gain": "Test creator"}
      }
    }
  },
  "evidence": {
    "desirability": {
      "problem_resonance": 0.75,
      "conversion_rate": 0.12,
      "commitment_depth": "skin_in_game",
      "zombie_ratio": 0.15,
      "traffic_quality": "High",
      "key_learnings": ["E2E test learning"],
      "tested_segments": ["Test Segment"],
      "impressions": 1000,
      "clicks": 150,
      "signups": 12,
      "spend_usd": 100.0
    },
    "feasibility": {
      "core_features_feasible": {"feature1": "fully_feasible"},
      "technical_risks": ["E2E test risk"],
      "skill_requirements": ["E2E tester"],
      "estimated_effort": "1 week",
      "downgrade_required": false,
      "downgrade_impact": null,
      "removed_features": [],
      "alternative_approaches": [],
      "monthly_cost_estimate_usd": 50.0
    },
    "viability": {
      "cac": 100.0,
      "ltv": 1200.0,
      "ltv_cac_ratio": 12.0,
      "gross_margin": 0.70,
      "payback_months": 2.0,
      "break_even_customers": 10,
      "tam_usd": 1000000000.0,
      "market_share_target": 0.01,
      "viability_assessment": "E2E test - excellent unit economics"
    }
  },
  "qa_report": {
    "status": "passed",
    "framework_compliance": true,
    "logical_consistency": true,
    "completeness": true,
    "specific_issues": [],
    "required_changes": [],
    "confidence_score": 0.95
  },
  "completed_at": "$(date -Iseconds)"
}
EOF
)

echo "Sending contract-compliant payload to webhook..."
WEBHOOK_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$WEBHOOK_URL" \
  -H "Authorization: Bearer $WEBHOOK_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$TEST_PAYLOAD")

HTTP_CODE=$(echo "$WEBHOOK_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$WEBHOOK_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
  echo -e "${GREEN}✅ Webhook responded with 200 OK${NC}"
  echo "   Response: $RESPONSE_BODY"

  # Parse response for report_id if available
  REPORT_ID=$(echo "$RESPONSE_BODY" | jq -r '.report_id // empty' 2>/dev/null)
  if [ -n "$REPORT_ID" ]; then
    echo -e "   Report ID: ${CYAN}$REPORT_ID${NC}"
  fi
else
  echo -e "${RED}❌ Webhook failed with HTTP $HTTP_CODE${NC}"
  echo "   Response: $RESPONSE_BODY"
  exit 1
fi

echo ""

# -----------------------------------------------------------------------------
# Step 2: Verify Supabase Persistence (if configured)
# -----------------------------------------------------------------------------
if [ "$MODE" = "full" ] || [ "$MODE" = "interactive" ]; then
    echo -e "${YELLOW}Step 2: Verifying Supabase persistence...${NC}"

    if verify_supabase_config; then
        echo "Waiting 2 seconds for persistence..."
        sleep 2

        # Check reports table
        echo -n "  Checking reports table... "
        REPORT_COUNT=$(count_records "reports" "project_id=eq.${TEST_PROJECT_ID}")
        if [ "$REPORT_COUNT" -ge 1 ]; then
            echo -e "${GREEN}✅ Found $REPORT_COUNT report(s)${NC}"
        else
            echo -e "${RED}❌ No reports found${NC}"
        fi

        # Check evidence table
        echo -n "  Checking evidence table... "
        EVIDENCE_COUNT=$(count_records "evidence" "project_id=eq.${TEST_PROJECT_ID}")
        if [ "$EVIDENCE_COUNT" -ge 1 ]; then
            echo -e "${GREEN}✅ Found $EVIDENCE_COUNT evidence row(s)${NC}"
        else
            echo -e "${YELLOW}⚠️  No evidence found (may not be implemented yet)${NC}"
        fi

        # Check crewai_validation_states table (supersedes gate_scores)
        echo -n "  Checking crewai_validation_states table... "
        VALIDATION_STATE_COUNT=$(count_records "crewai_validation_states" "project_id=eq.${TEST_PROJECT_ID}")
        if [ "$VALIDATION_STATE_COUNT" -ge 1 ]; then
            echo -e "${GREEN}✅ Found $VALIDATION_STATE_COUNT validation state(s)${NC}"
        else
            echo -e "${YELLOW}⚠️  No validation state found (may not be implemented yet)${NC}"
        fi

        echo ""

        # Detailed report check
        echo -e "${CYAN}Report Details:${NC}"
        REPORT_DATA=$(query_supabase "reports" "project_id=eq.${TEST_PROJECT_ID}&select=id,business_idea,validation_outcome,generated_at")
        echo "$REPORT_DATA" | jq '.[0] // "No data"' 2>/dev/null || echo "Could not parse report data"

    fi
    echo ""
fi

# -----------------------------------------------------------------------------
# Step 3: Check CrewAI AMP Status
# -----------------------------------------------------------------------------
if [ "$MODE" != "quick" ]; then
    echo -e "${YELLOW}Step 3: Checking CrewAI AMP deployment status...${NC}"

    STATUS_RESPONSE=$(curl -s -X GET "$CREWAI_URL/health" \
      -H "Authorization: Bearer $CREWAI_TOKEN" 2>/dev/null || echo '{"status": "unavailable"}')

    echo "CrewAI Health: $STATUS_RESPONSE"
    echo ""
fi

# -----------------------------------------------------------------------------
# Step 4: Optional Full Kickoff Test
# -----------------------------------------------------------------------------
if [ "$MODE" = "full" ]; then
    echo -e "${YELLOW}Step 4: Triggering CrewAI validation flow...${NC}"
    echo -e "${BLUE}NOTE: This will start a real validation flow (5-15 minutes, costs API credits).${NC}"
    echo ""

    KICKOFF_PAYLOAD=$(cat <<EOF
{
  "entrepreneur_input": "E2E Test ${TEST_RUN_ID}: A SaaS platform that helps small businesses automate their customer feedback collection and analysis using AI. Target market: SMBs with 10-50 employees.",
  "project_id": "${TEST_PROJECT_ID}-kickoff",
  "user_id": "${TEST_USER_ID}-kickoff"
}
EOF
)

    echo "Starting validation flow..."
    KICKOFF_RESPONSE=$(curl -s -X POST "$CREWAI_URL/kickoff" \
      -H "Authorization: Bearer $CREWAI_TOKEN" \
      -H "Content-Type: application/json" \
      -d "$KICKOFF_PAYLOAD")

    KICKOFF_ID=$(echo "$KICKOFF_RESPONSE" | jq -r '.kickoff_id // .id // empty' 2>/dev/null)

    if [ -n "$KICKOFF_ID" ]; then
        echo -e "${GREEN}✅ Validation started with kickoff_id: $KICKOFF_ID${NC}"
        echo ""
        echo "Polling for completion (timeout: 20 minutes)..."

        START_TIME=$(date +%s)
        TIMEOUT=1200  # 20 minutes

        while true; do
            CURRENT_TIME=$(date +%s)
            ELAPSED=$((CURRENT_TIME - START_TIME))

            if [ $ELAPSED -gt $TIMEOUT ]; then
                echo -e "${YELLOW}⚠️  Timeout waiting for completion${NC}"
                break
            fi

            STATUS=$(curl -s "$CREWAI_URL/status/$KICKOFF_ID" \
              -H "Authorization: Bearer $CREWAI_TOKEN" | jq -r '.status // "unknown"' 2>/dev/null)

            echo -ne "\r  Status: $STATUS (${ELAPSED}s elapsed)    "

            if [ "$STATUS" = "completed" ] || [ "$STATUS" = "SUCCESS" ]; then
                echo ""
                echo -e "${GREEN}✅ Flow completed!${NC}"

                # Verify Supabase after completion
                if verify_supabase_config; then
                    echo "Verifying Supabase after kickoff..."
                    sleep 5  # Wait for webhook

                    PROJECT="${TEST_PROJECT_ID}-kickoff"
                    REPORT_COUNT=$(count_records "reports" "project_id=eq.${PROJECT}")
                    EVIDENCE_COUNT=$(count_records "evidence" "project_id=eq.${PROJECT}")
                    VALIDATION_STATE_COUNT=$(count_records "crewai_validation_states" "project_id=eq.${PROJECT}")

                    echo "  Reports: $REPORT_COUNT"
                    echo "  Evidence rows: $EVIDENCE_COUNT"
                    echo "  Validation states: $VALIDATION_STATE_COUNT"
                fi
                break
            elif [ "$STATUS" = "failed" ] || [ "$STATUS" = "FAILED" ]; then
                echo ""
                echo -e "${RED}❌ Flow failed${NC}"
                break
            fi

            sleep 30
        done
    else
        echo -e "${RED}❌ Kickoff failed${NC}"
        echo "   Response: $KICKOFF_RESPONSE"
    fi
    echo ""
fi

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo -e "${BLUE}=============================================${NC}"
echo -e "${BLUE}  Test Summary${NC}"
echo -e "${BLUE}=============================================${NC}"
echo ""
echo -e "Test Run ID: ${CYAN}$TEST_RUN_ID${NC}"
echo -e "Webhook Test: $([ "$HTTP_CODE" = "200" ] && echo -e "${GREEN}PASSED${NC}" || echo -e "${RED}FAILED${NC}")"

if [ "$MODE" = "full" ] || [ "$MODE" = "interactive" ]; then
    if verify_supabase_config 2>/dev/null; then
        echo -e "Reports Table: $([ "$REPORT_COUNT" -ge 1 ] && echo -e "${GREEN}PASSED ($REPORT_COUNT)${NC}" || echo -e "${RED}FAILED${NC}")"
        echo -e "Evidence Table: $([ "$EVIDENCE_COUNT" -ge 1 ] && echo -e "${GREEN}PASSED ($EVIDENCE_COUNT)${NC}" || echo -e "${YELLOW}PENDING${NC}")"
        echo -e "Validation State: $([ "$VALIDATION_STATE_COUNT" -ge 1 ] && echo -e "${GREEN}PASSED ($VALIDATION_STATE_COUNT)${NC}" || echo -e "${YELLOW}PENDING${NC}")"
    fi
fi

echo ""
echo -e "${CYAN}Cleanup Command (to remove test data):${NC}"
echo "  DELETE FROM reports WHERE project_id LIKE 'e2e-test-%';"
echo "  DELETE FROM evidence WHERE project_id LIKE 'e2e-test-%';"
echo "  DELETE FROM crewai_validation_states WHERE project_id LIKE 'e2e-test-%';"
echo ""
