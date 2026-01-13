# LandingPageDeploymentTool Testing Guide

## Overview

This guide documents how to test the `LandingPageDeploymentTool` which deploys HTML landing pages to Netlify for Phase 2 desirability validation experiments.

## Testing Options

### Option 1: Modal Testing (Recommended - Production Secrets Available)

**Best for**: Testing with real Netlify API credentials in the same environment as production

**Prerequisites**:
- Modal CLI installed (`pip install modal`)
- Modal authentication configured (`modal setup`)
- `startupai-secrets` Modal secret configured with `NETLIFY_ACCESS_TOKEN`

**Command**:
```bash
# From startupai-crew root directory
modal run scripts/test_landing_page_deploy.py
```

**What it does**:
1. Spins up a Modal container with production secrets
2. Creates a test landing page with unique timestamp ID
3. Deploys to Netlify using the tool
4. Verifies the deployed URL is accessible (HTTP 200)
5. Checks that the HTML content is correct
6. Returns detailed test results

**Expected Output**:
```
======================================================================
LandingPageDeploymentTool Test Suite
======================================================================

Running deployment test...

======================================================================
Test Results
======================================================================

Success: True
Deployed URL: https://startupai-test-deploy-test-20260110-143052-abc12345.netlify.app
Test ID: 20260110-143052
HTTP Status: 200
Content Verified: True

You can visit the deployed page at:
  https://startupai-test-deploy-test-20260110-143052-abc12345.netlify.app

======================================================================
```

### Option 2: Local Testing (Requires .env Setup)

**Best for**: Quick iteration without Modal overhead

**Prerequisites**:
- Python 3.11+
- Dependencies installed (`uv sync`)
- `.env` file with `NETLIFY_ACCESS_TOKEN` set

**Setup**:
```bash
# Add to .env file
echo "NETLIFY_ACCESS_TOKEN=your_netlify_token_here" >> .env
```

**Command**:
```bash
# From startupai-crew root directory
python scripts/test_landing_page_deploy.py
```

**What it does**:
Same as Modal testing, but runs locally using environment variables from `.env`

### Option 3: Unit Tests (Mocked API - No Real Deployments)

**Best for**: CI/CD and fast iteration without API calls

**Prerequisites**:
- Python 3.11+
- pytest installed

**Command**:
```bash
# Run all landing page deployment tests
pytest tests/tools/test_landing_page_deploy.py -v

# Run specific test class
pytest tests/tools/test_landing_page_deploy.py::TestLandingPageDeploymentToolWithMocks -v
```

**What it does**:
- Tests tool logic without real API calls
- Uses mocked HTTP responses
- Validates input/output schemas
- Tests error handling

## Verification Checklist

When testing the tool, verify:

- [ ] Tool can create a new Netlify site
- [ ] Returned URL follows pattern: `https://{site-name}.netlify.app`
- [ ] Deployed page is accessible (HTTP 200)
- [ ] HTML content matches what was deployed
- [ ] Site name sanitization works (lowercase, hyphens, no special chars)
- [ ] Error handling works when token is missing
- [ ] Deploy time is logged

## Test HTML Content

The test script deploys a styled landing page with:
- Gradient background
- Call-to-action button
- Deployment metadata (timestamp, test ID)
- Responsive design

**Visual appearance**:
- Purple gradient background (#667eea → #764ba2)
- White glassmorphic container
- Large heading: "Validate Your Startup Idea"
- Explanatory text about the test
- White CTA button
- Deployment metadata in footer

## Troubleshooting

### Error: "NETLIFY_ACCESS_TOKEN not found"

**Modal testing**:
```bash
# Check if secret exists
modal secret list | grep startupai-secrets

# If missing, create it
modal secret create startupai-secrets \
  NETLIFY_ACCESS_TOKEN=your_token_here \
  OPENAI_API_KEY=sk-... \
  SUPABASE_URL=https://... \
  SUPABASE_KEY=eyJ...
```

**Local testing**:
```bash
# Check if .env has the token
grep NETLIFY_ACCESS_TOKEN .env

# If missing, add it
echo "NETLIFY_ACCESS_TOKEN=your_token_here" >> .env
```

### Error: "Site creation failed"

**Possible causes**:
1. Invalid Netlify token (expired or wrong permissions)
2. Network connectivity issues
3. Netlify API rate limiting

**Solutions**:
1. Generate new token at https://app.netlify.com/user/applications/personal
2. Check internet connection
3. Wait a few minutes if rate limited

### Error: "HTTP 404" when verifying deployed page

**Possible causes**:
1. DNS propagation delay (Netlify takes a few seconds)
2. Deploy didn't complete successfully

**Solutions**:
1. Add retry logic with delay (tool handles this)
2. Check Netlify dashboard for deploy status

### Error: "Neither httpx nor requests library available"

**Solution**:
```bash
# Install dependencies
uv sync

# Or manually
pip install httpx requests
```

## Integration with Phase 2 Validation

The `LandingPageDeploymentTool` is wired to the **F3 (Forge)** agent in `BuildCrew`:

```python
# src/crews/desirability/build_crew.py
@agent
def f3_agent(self) -> Agent:
    return Agent(
        config=self.agents_config["f3_agent"],
        tools=[
            LandingPageDeploymentTool(),  # NEW: Deploy landing pages
            # ... other tools
        ],
        # ... config
    )
```

**When to use**:
- Phase 2: Desirability validation
- After `plan_lp` task generates landing page variants
- F3 deploys each variant to get live URLs
- URLs used for A/B testing in subsequent tasks

## Next Steps

After successful testing:

1. **Phase A complete** - Tool is wired and tested
2. **Phase B** - Wire remaining Phase 2 tools:
   - Google Ads API tool for campaign deployment
   - Stripe checkout tool for payment processing
3. **Phase C** - Implement analytics and privacy tools
4. **Phase D** - Full Phase 2 E2E validation test

## Related Documentation

- Tool implementation: `/home/chris/projects/startupai-crew/src/shared/tools/landing_page_deploy.py`
- Unit tests: `/home/chris/projects/startupai-crew/tests/tools/test_landing_page_deploy.py`
- BuildCrew integration: `/home/chris/projects/startupai-crew/src/crews/desirability/build_crew.py`
- Phase work tracking: `/home/chris/projects/startupai-crew/docs/work/phases.md`
- Netlify API docs: https://docs.netlify.com/api/get-started/

---

**Last Updated**: 2026-01-10
**Status**: Phase A complete - Tool wired and ready for testing
