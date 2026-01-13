#!/bin/bash
# Quick curl-based test for LandingPageDeploymentTool via Modal endpoint
# This tests the tool through the deployed Modal API (if exposed as an endpoint)

set -e

echo "======================================================================="
echo "LandingPageDeploymentTool - Quick Curl Test"
echo "======================================================================="
echo ""

# Check if NETLIFY_ACCESS_TOKEN is set
if [ -z "$NETLIFY_ACCESS_TOKEN" ]; then
    echo "ERROR: NETLIFY_ACCESS_TOKEN environment variable not set"
    echo ""
    echo "Please set it:"
    echo "  export NETLIFY_ACCESS_TOKEN=your_token_here"
    echo ""
    exit 1
fi

echo "NETLIFY_ACCESS_TOKEN found in environment"
echo ""

# Generate test data
TEST_ID=$(date +%Y%m%d-%H%M%S)
PROJECT_ID="test-deploy-curl"
VARIANT_ID="test-${TEST_ID}"

echo "Test ID: ${TEST_ID}"
echo "Project ID: ${PROJECT_ID}"
echo "Variant ID: ${VARIANT_ID}"
echo ""

# Test HTML content
HTML='<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Curl Test - StartupAI</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
        }
        h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
    </style>
</head>
<body>
    <h1>Curl Test Deployment</h1>
    <p>Deployed: '"$(date -Iseconds)"'</p>
    <p>Test ID: '"${TEST_ID}"'</p>
</body>
</html>'

echo "Deploying via Python script (direct tool invocation)..."
echo ""

# Use Python to directly invoke the tool
python3 << EOFPYTHON
import os
import sys

sys.path.insert(0, '/home/chris/projects/startupai-crew/src')

from shared.tools.landing_page_deploy import LandingPageDeploymentTool

html = '''${HTML}'''
project_id = '${PROJECT_ID}'
variant_id = '${VARIANT_ID}'

tool = LandingPageDeploymentTool()
result = tool._run(
    html=html,
    project_id=project_id,
    variant_id=variant_id,
)

print(result)

# Extract URL if successful
if "Landing Page Deployed Successfully" in result:
    for line in result.split("\n"):
        if "**Live URL:**" in line:
            url = line.split("**Live URL:**")[1].strip()
            print("\n" + "="*70)
            print("SUCCESS: Page deployed!")
            print("="*70)
            print(f"\nVisit: {url}")
            print("")
            
            # Quick verification with curl
            import subprocess
            try:
                curl_result = subprocess.run(
                    ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', url],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                status_code = curl_result.stdout
                print(f"HTTP Status: {status_code}")
                if status_code == "200":
                    print("✓ Page is accessible!")
                else:
                    print(f"✗ Unexpected status code: {status_code}")
            except Exception as e:
                print(f"Could not verify with curl: {e}")
else:
    print("\n" + "="*70)
    print("DEPLOYMENT FAILED")
    print("="*70)
    print("")
EOFPYTHON

echo ""
echo "======================================================================="
echo "Test complete"
echo "======================================================================="
