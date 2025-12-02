#!/bin/bash
#
# Post-Deploy Validation Script
# Runs a test scenario against deployed CrewAI AMP to verify deployment health
#
# Usage:
#   ./scripts/post_deploy_validation.sh
#   ./scripts/post_deploy_validation.sh --scenario happy-path-b2b-saas
#
# Environment variables required:
#   CREW_UUID - CrewAI deployment UUID
#   CREW_TOKEN - CrewAI deployment bearer token
#
# Exit codes:
#   0 - Validation passed
#   1 - Validation failed
#   2 - Validation timed out
#   3 - Configuration error

set -e

# Configuration
CREW_UUID="${CREW_UUID:-b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b}"
CREW_BASE_URL="https://startupai-${CREW_UUID//-/}-4f4192a6.crewai.com"
MAX_WAIT_SECONDS=300
POLL_INTERVAL=10

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default test scenario
DEFAULT_SCENARIO='{
  "entrepreneur_input": "AI-powered project management tool for remote software teams. Target: 10-50 person startups. Problem: Existing tools too complex. Solution: AI auto-assigns tasks based on skills and availability. Price: $15/user/month.",
  "project_id": "post-deploy-validation"
}'

# Parse arguments
SCENARIO_NAME="${1:-default}"

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check required environment variables
if [ -z "$CREW_TOKEN" ]; then
    log_error "CREW_TOKEN environment variable not set"
    log_info "Set it with: export CREW_TOKEN=your-deployment-token"
    exit 3
fi

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    log_error "jq is required but not installed"
    log_info "Install with: sudo apt install jq (Ubuntu) or brew install jq (macOS)"
    exit 3
fi

log_info "Starting post-deploy validation"
log_info "Deployment URL: $CREW_BASE_URL"
log_info "Scenario: $SCENARIO_NAME"

# Step 1: Check deployment status
log_info "Checking deployment status..."
STATUS_RESPONSE=$(curl -s "${CREW_BASE_URL}/health" 2>/dev/null || echo '{"status": "unknown"}')

if echo "$STATUS_RESPONSE" | jq -e '.status == "healthy"' > /dev/null 2>&1; then
    log_info "Deployment is healthy"
else
    log_warn "Could not verify deployment health, proceeding anyway..."
fi

# Step 2: Trigger test execution
log_info "Triggering test execution..."

KICKOFF_RESPONSE=$(curl -s -X POST \
    "${CREW_BASE_URL}/kickoff" \
    -H "Authorization: Bearer ${CREW_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "$DEFAULT_SCENARIO")

# Check for kickoff errors
if echo "$KICKOFF_RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
    ERROR_MSG=$(echo "$KICKOFF_RESPONSE" | jq -r '.error')
    log_error "Kickoff failed: $ERROR_MSG"
    exit 1
fi

KICKOFF_ID=$(echo "$KICKOFF_RESPONSE" | jq -r '.kickoff_id // .id // empty')

if [ -z "$KICKOFF_ID" ]; then
    log_error "Failed to get kickoff_id from response"
    log_error "Response: $KICKOFF_RESPONSE"
    exit 1
fi

log_info "Kickoff ID: $KICKOFF_ID"

# Step 3: Poll for completion
log_info "Waiting for completion (max ${MAX_WAIT_SECONDS}s)..."

ELAPSED=0
while [ $ELAPSED -lt $MAX_WAIT_SECONDS ]; do
    STATUS_RESPONSE=$(curl -s \
        "${CREW_BASE_URL}/status/${KICKOFF_ID}" \
        -H "Authorization: Bearer ${CREW_TOKEN}")

    STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status // "unknown"')

    case "$STATUS" in
        "completed"|"success"|"finished")
            log_info "Execution completed successfully!"

            # Extract metrics if available
            DURATION=$(echo "$STATUS_RESPONSE" | jq -r '.duration_seconds // .duration // "N/A"')
            TOKENS=$(echo "$STATUS_RESPONSE" | jq -r '.total_tokens // .token_usage // "N/A"')

            log_info "Duration: ${DURATION}s"
            log_info "Tokens: ${TOKENS}"

            echo ""
            log_info "✅ Post-deploy validation PASSED"
            exit 0
            ;;
        "failed"|"error")
            ERROR_MSG=$(echo "$STATUS_RESPONSE" | jq -r '.error // .message // "Unknown error"')
            log_error "Execution failed: $ERROR_MSG"
            echo ""
            log_error "❌ Post-deploy validation FAILED"
            exit 1
            ;;
        "running"|"in_progress"|"pending"|"queued")
            printf "."
            ;;
        *)
            log_warn "Unknown status: $STATUS"
            ;;
    esac

    sleep $POLL_INTERVAL
    ELAPSED=$((ELAPSED + POLL_INTERVAL))
done

echo ""
log_error "Validation timed out after ${MAX_WAIT_SECONDS} seconds"
log_error "Last status: $STATUS"
log_error "Kickoff ID: $KICKOFF_ID (check AMP dashboard for details)"
echo ""
log_error "⚠️ Post-deploy validation TIMED OUT"
exit 2
