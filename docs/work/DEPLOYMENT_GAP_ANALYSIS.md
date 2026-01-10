---
created: 2026-01-10
status: SUPERSEDED
priority: P0
impact: Phase 2 Desirability evidence is fabricated
resolved: 2026-01-10
superseded_by: ADR-003 (Supabase Storage migration)
---

# BuildCrew Deployment Gap Analysis

## Problem Statement

The BuildCrew in Phase 2 Desirability claims to deploy landing pages to Netlify for A/B testing, but **no actual deployments are happening**. The claimed URLs return "Site not Found":

- Variant A: https://startup-validator-a.netlify.app
- Variant B: https://startup-validator-b.netlify.app

**Impact**: Phase 2 Desirability testing requires REAL landing pages with analytics to generate valid market signals. Without real deployments, all desirability evidence is fabricated.

---

## Investigation Results

### 1. Sites Do NOT Exist

Checked Netlify and the claimed sites do not exist. The BuildCrew is hallucinating deployment URLs.

### 2. BuildCrew Configuration

**File**: `/home/chris/projects/startupai-crew/src/crews/desirability/build_crew.py`

**Current State**:
```python
@agent
def f3_backend_developer(self) -> Agent:
    """F3: Backend Developer - Deploys artifacts."""
    return Agent(
        config=self.agents_config["f3_backend_developer"],
        tools=[CalendarTool(), MethodologyCheckTool()],  # WRONG TOOLS!
        reasoning=False,
        inject_date=True,
        max_iter=25,
        llm=LLM(model="openai/gpt-4o", temperature=0.2),
        verbose=True,
        allow_delegation=False,
    )
```

**Problem**: F3 (Backend/DevOps) has `CalendarTool` and `MethodologyCheckTool`, neither of which deploy anything.

**Expected Tools** (from `/tool-mapping.md`):
```python
tools=[LandingPageDeploymentTool()]  # EXISTS in archive
```

### 3. Deployment Tool EXISTS in Archive

**File**: `/home/chris/projects/startupai-crew/archive/flow-architecture/startupai/tools/landing_page_deploy.py`

This is a **complete, production-ready tool** with:
- Netlify API integration
- Site creation
- HTML deployment
- A/B variant support
- Error handling
- httpx and requests support

**Features**:
- Creates new Netlify sites or deploys to existing
- Generates unique site names (startupai-{project_id}-{variant_id})
- Handles SHA1-based digest deploy API
- Returns live URLs
- Comprehensive error reporting

### 4. Task Definitions

**File**: `/home/chris/projects/startupai-crew/src/crews/desirability/config/build_tasks.yaml`

Tasks are correctly defined:
```yaml
deploy_artifacts:
  description: >
    Deploy the landing pages to Netlify for validation experiments.
  expected_output: >
    Deployment report with:
    - Live URLs for each variant
    - Analytics dashboard access
    - Form submission webhook URLs
  agent: f3_backend_developer
```

**Problem**: The agent has the right instructions but NO tool to execute them.

### 5. Agent Configuration

**File**: `/home/chris/projects/startupai-crew/src/crews/desirability/config/build_agents.yaml`

F3 backstory correctly defines deployment responsibilities:
```yaml
f3_backend_developer:
  backstory: >
    You handle deployment and backend setup for validation experiments.
    You ensure that:
    - Landing pages deploy to Netlify successfully
    - Analytics tracking is properly configured
    - Form submissions are captured
```

**Problem**: Agent knows WHAT to do but has NO tools to DO it.

---

## Root Cause

**Tool Wiring Gap**: The BuildCrew has structure (agents, tasks, backstories) but **F3 agent is missing the deployment tool**. This is a clear example of the broader issue documented in `CLAUDE.md`:

> **⚠️ TOOL WIRING GAP**: Modal crews have structure but most agents lack tools. See `docs/work/phases.md` for fix plan.

---

## Solution

### Quick Fix (Wire Existing Tool)

**Action**: Move `LandingPageDeploymentTool` from archive to active tools and wire to F3 agent.

**Steps**:

1. **Move tool to shared tools**:
   ```bash
   cp archive/flow-architecture/startupai/tools/landing_page_deploy.py \
      src/shared/tools/landing_page_deploy.py
   ```

2. **Add to shared tools exports** (`src/shared/tools/__init__.py`):
   ```python
   from shared.tools.landing_page_deploy import (
       LandingPageDeploymentTool,
       deploy_landing_page,
       DeploymentResult,
   )
   
   __all__ = [
       ...
       "LandingPageDeploymentTool",
       "deploy_landing_page",
       "DeploymentResult",
   ]
   ```

3. **Wire to F3 agent** (`src/crews/desirability/build_crew.py`):
   ```python
   from shared.tools import (
       LandingPageDeploymentTool,  # ADD THIS
       CalendarTool,
       MethodologyCheckTool,
   )
   
   @agent
   def f3_backend_developer(self) -> Agent:
       """F3: Backend Developer - Deploys artifacts."""
       return Agent(
           config=self.agents_config["f3_backend_developer"],
           tools=[LandingPageDeploymentTool()],  # FIXED
           reasoning=False,
           inject_date=True,
           max_iter=25,
           llm=LLM(model="openai/gpt-4o", temperature=0.2),
           verbose=True,
           allow_delegation=False,
       )
   ```

4. **Verify environment variable** in Modal secrets:
   ```bash
   modal secret list startupai-secrets | grep NETLIFY_ACCESS_TOKEN
   ```

5. **Test deployment**:
   ```python
   from shared.tools import deploy_landing_page
   
   result = deploy_landing_page(
       html="<html><body>Test</body></html>",
       project_id="test-123",
       variant_id="variant-a"
   )
   print(result)
   # Should return live Netlify URL
   ```

**Estimated Effort**: 30 minutes

**Risk**: Low - tool is production-ready, just needs wiring

---

### Long-Term Fix (MCP Architecture)

**Phase D: MCP-First Tool Integration** (from `/docs/work/phases.md`)

Convert `LandingPageDeploymentTool` to MCP tool pattern:

1. **Create Netlify MCP tool** (`src/mcp_server/tools/netlify_deploy.py`)
2. **Deploy on Modal MCP server**
3. **Use MCP client in agents** instead of direct import
4. **Benefits**:
   - Unified tool interface (like OpenRouter for LLMs)
   - Better observability
   - Reusable across agents
   - Testable independently

**Estimated Effort**: 2-3 hours (part of broader MCP integration)

---

## Verification Plan

### After Tool Wiring

1. **Unit Test**:
   ```bash
   pytest tests/tools/test_landing_page_deploy.py -v
   ```

2. **Integration Test**:
   ```bash
   # Run BuildCrew with real Netlify deployment
   modal run src/modal_app/app.py::test_build_crew_deployment
   ```

3. **Verify URLs**:
   - Check that returned URLs are live
   - Verify HTML content matches input
   - Confirm analytics tracking code present

4. **Check Netlify Dashboard**:
   - https://app.netlify.com/sites
   - Verify new sites created
   - Check deploy logs

### Success Criteria

- [ ] F3 agent successfully deploys 2 variants to Netlify
- [ ] Both URLs return HTTP 200
- [ ] URLs follow pattern: `https://startupai-{project_id}-{variant_id}-{hash}.netlify.app`
- [ ] Analytics tracking code present in HTML
- [ ] Form submission handlers configured
- [ ] Sites visible in Netlify dashboard

---

## Impact Assessment

### Current State (Without Fix)

| Phase | Impact |
|-------|--------|
| Phase 2 Desirability | **BLOCKED** - Cannot run real experiments |
| Phase 3 Feasibility | **BLOCKED** - BuildCrew reused, same issue |
| Phase 4 Viability | Degraded - No real market signals |

### After Quick Fix

| Phase | Impact |
|-------|--------|
| Phase 2 Desirability | **UNBLOCKED** - Real landing pages deployed |
| Phase 3 Feasibility | **UNBLOCKED** - BuildCrew works correctly |
| Phase 4 Viability | Improved - Real market signals available |

---

## Related Issues

This is **one instance** of a systemic problem:

1. **TOOL WIRING GAP** (Crew-wide):
   - BuildCrew: F3 missing `LandingPageDeploymentTool`
   - GrowthCrew: P1, P2, P3 missing `AdPlatformTool`
   - DiscoveryCrew: D2 missing `ForumScraperTool`, `ReviewAnalysisTool`
   - See `/docs/master-architecture/reference/tool-mapping.md` for full gap analysis

2. **Phase D Roadmap** (`/docs/work/phases.md`):
   - MCP-First Tool Integration
   - 60h effort to wire all 33 tools
   - Estimated cost: $5-10/month Modal compute

---

## Recommendation

**Immediate Action**: Apply Quick Fix (30 minutes)
- Unblocks Phase 2 testing TODAY
- Low risk, high impact
- Allows real desirability experiments

**Follow-Up**: Phase D MCP Integration (60h)
- Systemic fix for all tool wiring gaps
- Better architecture long-term
- Aligns with Modal + MCP strategy

---

## Related Documents

- [tool-mapping.md](../master-architecture/reference/tool-mapping.md) - Complete agent-to-tool mapping
- [phases.md](./phases.md) - Phase D: MCP-First Tool Integration roadmap
- [agentic-tool-framework.md](../master-architecture/reference/agentic-tool-framework.md) - Tool lifecycle
- [CLAUDE.md](../../CLAUDE.md) - "⚠️ TOOL WIRING GAP" acknowledgment

---

## Change Log

| Date | Change |
|------|--------|
| 2026-01-10 | Initial analysis - BuildCrew deployment gap identified |
| 2026-01-10 | **RESOLVED** - LandingPageDeploymentTool wired to F3 agent |

---

## Resolution Details (2026-01-10)

**Fix Applied**: Quick Fix (Wire Existing Tool)

### Changes Made

1. **Copied tool to shared tools**:
   - `src/shared/tools/landing_page_deploy.py` (from archive)
   - Added `LandingPageDeployInput` args_schema for typed input validation

2. **Updated exports** (`src/shared/tools/__init__.py`):
   - Added `LandingPageDeploymentTool`, `deploy_landing_page`, `DeploymentResult`, `LandingPageDeployInput`

3. **Wired to F3 agent** (`src/crews/desirability/build_crew.py`):
   - Changed F3 tools from `[CalendarTool(), MethodologyCheckTool()]` to `[LandingPageDeploymentTool()]`

4. **Added unit tests**:
   - `tests/tools/test_landing_page_deploy.py` (25 tests)
   - Tests cover: DeploymentResult model, input schema, tool attributes, sanitization, formatting, mocked API calls, BuildCrew integration

5. **Deployed to Modal**:
   - All 686 tests passing
   - Deployed at https://chris00walker--startupai-validation-fastapi-app.modal.run

### Verification

- [ ] ~~Re-run Phase 2 and verify real Netlify URLs are created~~ SUPERSEDED
- [ ] ~~Check URLs return HTTP 200~~ SUPERSEDED
- [ ] ~~Verify sites appear in Netlify dashboard~~ SUPERSEDED

---

## SUPERSEDED (2026-01-10)

**This document is superseded by [ADR-003](../adr/003-landing-page-storage-migration.md).**

### Why Netlify Approach Was Abandoned

After implementing the "Quick Fix" above, testing revealed deeper issues:

1. **Token Permission Anomaly**: The Netlify Personal Access Token exhibited unusual behavior:
   - Could CREATE sites (201 Created)
   - Could NOT DEPLOY to sites (401 Unauthorized)
   - Could NOT LIST sites (401 Unauthorized)
   - Could NOT GET user info (401 Unauthorized)

2. **Architecture Mismatch**: Netlify is designed for permanent hosting with CI/CD pipelines. Our landing pages are:
   - Temporary (hours to days)
   - Ephemeral (created for validation, deleted after)
   - Low traffic (only validation participants)
   - Programmatically generated (no build pipeline)

3. **Square Peg, Round Hole**: We were over-engineering the solution. The 522-line Netlify implementation is overkill for temporary artifacts.

### New Approach: Supabase Storage

See [ADR-003](../adr/003-landing-page-storage-migration.md) for the accepted solution:

- **Supabase Storage** public bucket serves HTML files via CDN
- **Edge Function** captures form submissions
- **Natural cleanup** when validation run expires
- **~100 lines** vs 522 lines (simpler implementation)

The original analysis in this document correctly identified the tool wiring gap. The resolution pivoted from "fix Netlify" to "use right tool for the job."
