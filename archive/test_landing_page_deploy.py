#!/usr/bin/env python3
"""
Direct test script for LandingPageDeploymentTool.

Tests the tool in Modal's deployed environment where NETLIFY_ACCESS_TOKEN
is available. This script verifies:
1. The tool can create a real Netlify site
2. The returned URL is accessible (HTTP 200)
3. The HTML content is actually deployed

Usage:
    # Via Modal (production secrets available):
    modal run scripts/test_landing_page_deploy.py

    # Locally (requires NETLIFY_ACCESS_TOKEN in .env):
    python scripts/test_landing_page_deploy.py
"""

import os
import sys
import logging
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import modal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Modal Setup (for `modal run` execution)
# -----------------------------------------------------------------------------

# Modal app for testing
app = modal.App("test-landing-page-deploy")

# Image with dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "crewai[tools]",
        "pydantic",
        "httpx",
        "requests",
    )
    .add_local_dir(
        "/home/chris/projects/startupai-crew/src",
        remote_path="/root/src"
    )
)

# -----------------------------------------------------------------------------
# Test HTML Content
# -----------------------------------------------------------------------------

TEST_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Landing Page - StartupAI</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }}
        .container {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 3rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        h1 {{
            font-size: 3rem;
            margin: 0 0 1rem 0;
            background: linear-gradient(to right, #fff, #f0f0f0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        p {{
            font-size: 1.25rem;
            line-height: 1.6;
            opacity: 0.9;
        }}
        .cta {{
            display: inline-block;
            margin-top: 2rem;
            padding: 1rem 2rem;
            background: white;
            color: #667eea;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 600;
            transition: transform 0.2s;
        }}
        .cta:hover {{
            transform: translateY(-2px);
        }}
        .meta {{
            margin-top: 2rem;
            padding-top: 2rem;
            border-top: 1px solid rgba(255, 255, 255, 0.2);
            font-size: 0.9rem;
            opacity: 0.7;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Validate Your Startup Idea</h1>
        <p>
            Test landing page deployed via LandingPageDeploymentTool.
            This page verifies that the tool can successfully create
            Netlify sites and deploy HTML content.
        </p>
        <p>
            If you can see this page, the deployment was successful!
        </p>
        <a href="#" class="cta">Get Early Access</a>
        <div class="meta">
            Deployed: {deployed_at}<br>
            Test ID: {test_id}
        </div>
    </div>
</body>
</html>"""

# -----------------------------------------------------------------------------
# Test Functions
# -----------------------------------------------------------------------------

@app.function(
    image=image,
    secrets=[modal.Secret.from_name("startupai-secrets")],
    timeout=300,  # 5 minutes for deployment + verification
)
def test_deployment():
    """
    Test the LandingPageDeploymentTool with a real Netlify deployment.
    """
    from shared.tools.landing_page_deploy import LandingPageDeploymentTool
    import httpx
    
    logger.info("Starting LandingPageDeploymentTool test...")
    
    # Check environment
    netlify_token = os.environ.get("NETLIFY_ACCESS_TOKEN")
    if not netlify_token:
        logger.error("NETLIFY_ACCESS_TOKEN not found in environment!")
        return {
            "success": False,
            "error": "NETLIFY_ACCESS_TOKEN not available in Modal secrets"
        }
    
    logger.info("NETLIFY_ACCESS_TOKEN found in environment")
    
    # Prepare test data
    test_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    project_id = "test-deploy"
    variant_id = f"test-{test_id}"
    
    html_content = TEST_HTML.format(
        deployed_at=datetime.now().isoformat(),
        test_id=test_id
    )
    
    logger.info(f"Test ID: {test_id}")
    logger.info(f"Project ID: {project_id}")
    logger.info(f"Variant ID: {variant_id}")
    
    # Create tool instance
    tool = LandingPageDeploymentTool()
    
    # Execute deployment
    logger.info("Deploying landing page to Netlify...")
    result_str = tool._run(
        html=html_content,
        project_id=project_id,
        variant_id=variant_id,
    )
    
    logger.info("Deployment result:")
    logger.info(result_str)
    
    # Parse the result to extract URL
    if "Landing Page Deployed Successfully" in result_str:
        # Extract URL from formatted output
        for line in result_str.split("\n"):
            if "**Live URL:**" in line:
                deployed_url = line.split("**Live URL:**")[1].strip()
                logger.info(f"Extracted URL: {deployed_url}")
                
                # Verify the deployed page is accessible
                logger.info("Verifying deployed page accessibility...")
                try:
                    with httpx.Client(timeout=30.0) as client:
                        response = client.get(deployed_url)
                        
                        logger.info(f"HTTP Status: {response.status_code}")
                        
                        if response.status_code == 200:
                            logger.info("SUCCESS: Page is accessible!")
                            
                            # Check if our test content is present
                            if "Validate Your Startup Idea" in response.text:
                                logger.info("SUCCESS: Test content verified in deployed page!")
                                return {
                                    "success": True,
                                    "deployed_url": deployed_url,
                                    "test_id": test_id,
                                    "http_status": response.status_code,
                                    "content_verified": True,
                                }
                            else:
                                logger.warning("Content verification failed - expected text not found")
                                return {
                                    "success": True,
                                    "deployed_url": deployed_url,
                                    "test_id": test_id,
                                    "http_status": response.status_code,
                                    "content_verified": False,
                                    "warning": "Expected content not found in page"
                                }
                        else:
                            logger.error(f"HTTP error: {response.status_code}")
                            return {
                                "success": False,
                                "deployed_url": deployed_url,
                                "test_id": test_id,
                                "http_status": response.status_code,
                                "error": f"HTTP {response.status_code}"
                            }
                
                except Exception as e:
                    logger.error(f"Failed to verify deployment: {str(e)}")
                    return {
                        "success": False,
                        "deployed_url": deployed_url,
                        "test_id": test_id,
                        "error": f"Verification failed: {str(e)}"
                    }
    
    # Deployment failed
    logger.error("Deployment failed")
    return {
        "success": False,
        "test_id": test_id,
        "error": "Deployment failed - check result output above",
        "result": result_str
    }

@app.local_entrypoint()
def main():
    """
    Local entrypoint for `modal run` command.
    """
    print("\n" + "="*70)
    print("LandingPageDeploymentTool Test Suite")
    print("="*70 + "\n")
    
    print("Running deployment test...")
    result = test_deployment.remote()
    
    print("\n" + "="*70)
    print("Test Results")
    print("="*70)
    print(f"\nSuccess: {result['success']}")
    
    if result['success']:
        print(f"Deployed URL: {result['deployed_url']}")
        print(f"Test ID: {result['test_id']}")
        print(f"HTTP Status: {result['http_status']}")
        print(f"Content Verified: {result['content_verified']}")
        print("\nYou can visit the deployed page at:")
        print(f"  {result['deployed_url']}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    print("\n" + "="*70 + "\n")
    
    return result

# -----------------------------------------------------------------------------
# Local Execution (without Modal)
# -----------------------------------------------------------------------------

def test_local():
    """
    Test locally without Modal (requires NETLIFY_ACCESS_TOKEN in environment).
    """
    print("\n" + "="*70)
    print("LandingPageDeploymentTool Local Test")
    print("="*70 + "\n")
    
    from shared.tools.landing_page_deploy import LandingPageDeploymentTool
    import httpx
    
    # Check environment
    netlify_token = os.environ.get("NETLIFY_ACCESS_TOKEN")
    if not netlify_token:
        print("ERROR: NETLIFY_ACCESS_TOKEN not found in environment!")
        print("Please set it in your .env file or export it:")
        print("  export NETLIFY_ACCESS_TOKEN=your_token_here")
        return {"success": False, "error": "NETLIFY_ACCESS_TOKEN not set"}
    
    print("NETLIFY_ACCESS_TOKEN found in environment")
    
    # Prepare test data
    test_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    project_id = "test-deploy-local"
    variant_id = f"test-{test_id}"
    
    html_content = TEST_HTML.format(
        deployed_at=datetime.now().isoformat(),
        test_id=test_id
    )
    
    print(f"Test ID: {test_id}")
    print(f"Project ID: {project_id}")
    print(f"Variant ID: {variant_id}")
    
    # Create tool instance
    tool = LandingPageDeploymentTool()
    
    # Execute deployment
    print("\nDeploying landing page to Netlify...")
    result_str = tool._run(
        html=html_content,
        project_id=project_id,
        variant_id=variant_id,
    )
    
    print("\nDeployment result:")
    print(result_str)
    
    # Parse the result to extract URL
    if "Landing Page Deployed Successfully" in result_str:
        for line in result_str.split("\n"):
            if "**Live URL:**" in line:
                deployed_url = line.split("**Live URL:**")[1].strip()
                print(f"\nExtracted URL: {deployed_url}")
                
                # Verify the deployed page is accessible
                print("\nVerifying deployed page accessibility...")
                try:
                    with httpx.Client(timeout=30.0) as client:
                        response = client.get(deployed_url)
                        
                        print(f"HTTP Status: {response.status_code}")
                        
                        if response.status_code == 200:
                            print("SUCCESS: Page is accessible!")
                            
                            if "Validate Your Startup Idea" in response.text:
                                print("SUCCESS: Test content verified in deployed page!")
                                return {
                                    "success": True,
                                    "deployed_url": deployed_url,
                                    "test_id": test_id,
                                }
                            else:
                                print("WARNING: Expected content not found in page")
                                return {
                                    "success": True,
                                    "deployed_url": deployed_url,
                                    "test_id": test_id,
                                    "warning": "Content verification failed"
                                }
                        else:
                            print(f"ERROR: HTTP {response.status_code}")
                            return {
                                "success": False,
                                "deployed_url": deployed_url,
                                "error": f"HTTP {response.status_code}"
                            }
                
                except Exception as e:
                    print(f"ERROR: Failed to verify deployment: {str(e)}")
                    return {
                        "success": False,
                        "deployed_url": deployed_url,
                        "error": f"Verification failed: {str(e)}"
                    }
    
    print("\nERROR: Deployment failed")
    return {"success": False, "error": "Deployment failed"}

if __name__ == "__main__":
    # When run directly (python scripts/test_landing_page_deploy.py)
    # Use local testing without Modal
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    
    # Load .env if available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("python-dotenv not installed, skipping .env file loading")
    
    result = test_local()
    
    print("\n" + "="*70)
    print("Test Complete")
    print("="*70 + "\n")
    
    sys.exit(0 if result.get("success") else 1)
