---
purpose: Track learnings from live Modal testing with real LLM calls
status: active
last_updated: 2026-01-10
---

# Modal Live Testing Learnings

This document captures issues discovered, fixes applied, and lessons learned during live testing of the Modal serverless deployment with **real LLM calls** (not mocked crews).

> **Context**: Unit tests (185) and E2E integration tests (17) use mocked crews. Live testing exposes real-world issues with LLM outputs, template interpolation, and data flow.

---

## Testing Sessions

### Session 1: 2026-01-09 (Phase 0→2 Live Test)

**Validation Run ID**: `5f10f61a-3e48-48e0-bdac-8fa6e38eaec6`
**Business Context**: AI chatbot for SMB e-commerce customer support

#### Issues Discovered & Fixed

| # | Issue | Root Cause | Fix | Commit |
|---|-------|------------|-----|--------|
| 1 | HITL approval re-runs same phase | `resume_from_checkpoint` didn't increment `current_phase` | Increment phase before spawning resume | `46c7da6` |
| 2 | Template variable 'assumptions_to_test' not found | CrewAI interpolates `{var}` at kickoff, not runtime | Remove context-dependent template vars | `46c7da6` |
| 3 | Customer Profile completely wrong | Agents never saw `{founders_brief}` - hallucinated generic output | Add template vars back with clear section headers | `b96e7a7` |
| 4 | Phase 2 'key_messaging' not found | Same template interpolation issue in Phase 2 tasks | Fix Phase 2 task files (build, growth, governance) | `346e02e` |
| 5 | HITL always shows `approve_desirability_gate` | No signal-based routing - proceeds even with NO_INTEREST | Implement signal-based checkpoint routing | `e6ce56b` |
| 6 | **Segment pivot doesn't change segment** | Agents re-run discovery with no guidance on new segment | Propose alternatives + founder selects | `e54a2d2` |

#### Key Learnings

**1. CrewAI Template Variable Timing**
```
WRONG: Use {context_var} in task description expecting it from previous task
RIGHT: Only use {input_var} in task description for values passed as crew inputs
       Use "context" task property to reference previous tasks
```

**2. Template Variable Best Practices**
- First task in each crew MUST include input data with clear section headers
- Use `==========` separators to make inputs visually distinct for LLMs
- Add "YOUR TASK:" section after inputs to focus agent attention

**3. HITL Phase Advancement**
- Must increment `current_phase` BEFORE spawning resume function
- Validation run state must be updated atomically

**4. Signal-Based Routing (VPD Compliance)**
- HITL checkpoints must differ based on validation signals
- NO_INTEREST → `approve_segment_pivot` (not `approve_desirability_gate`)
- MILD_INTEREST → `approve_value_pivot`
- STRONG_COMMITMENT → `approve_desirability_gate` (proceed to Phase 3)

#### Phase Results

**Phase 0 (Onboarding)**: PASSED
- Founder's Brief captured correctly
- HITL `approve_founders_brief` worked

**Phase 1 (VPC Discovery)**: PASSED (after fix)
- First run: Wrong customer segment (hallucinated "SmartFit Wellness App")
- After fix: Correct alignment ("SmartAssist AI Customer Support Platform")
- Fit Score: 83/100

**Phase 2 (Desirability)**: PASSED (after fix)
- Signal: NO_INTEREST (simulated data)
- Problem Resonance: 7.4% (below 30% threshold)
- Zombie Ratio: 82.7% (above 70% threshold)
- Correct checkpoint: `approve_segment_pivot`

**Pivot Loopback Test**: PASSED
- Approved `approve_segment_pivot` with decision `approved`
- HITL handler correctly returned `status: "pivot"`, `next_phase: 1`
- Phase 1 re-ran with all 5 crews completing successfully:
  - DiscoveryCrew: 14:18:38 → 14:20:36
  - CustomerProfileCrew: 14:20:37 → 14:23:25
  - ValueDesignCrew: 14:23:25 → 14:25:34
  - WTPCrew: → 14:26:53
  - FitAssessmentCrew: 14:26:53 → 14:27:22
- New fit score: 72/100 (vs 83/100 in first run)
- Pivot context preserved in phase_state:
  - `pivot_type: segment_pivot`
  - `pivot_reason: "Pivot approved - target different customer segment"`
  - `pivot_from_phase: 2`
- New HITL: `approve_vpc_completion` (ready to proceed to Phase 2 again)

---

### Session 2: 2026-01-10 (Post-Tool Integration Test)

**Validation Run ID**: `52fe3efa-59b6-4c28-9f82-abd1d0d55b4b`
**Business Context**: AI chatbot for SMB e-commerce customer support (same as Session 1)
**Key Difference**: Tool-wired code deployed (15 tools, 35+ agents)

#### Deployment

Modal redeployed with tool integration code:
- 15 tools implemented (Phases A-D)
- 35+ agents wired with tools
- 681 tests passing

#### Phase Results

**Phase 0 (Onboarding)**: ✅ PASSED
- OnboardingCrew completed in ~47 seconds
- Founder's Brief generated with full VPD structure:
  - `the_idea`: One-liner, description, inspiration, unique_insight
  - `problem_hypothesis`: Problem statement, who has it, alternatives, why they fail
  - `customer_hypothesis`: Primary segment, characteristics, where to find
  - `solution_hypothesis`: Proposed solution, key features, differentiation
  - `key_assumptions`: 2 testable assumptions with risk levels
  - `success_criteria`: Target metrics, deal breakers, fit score targets
- QA Status: PASS (legitimacy check passed)
- HITL `approve_founders_brief` → Approved

**Phase 1 (VPC Discovery)**: ✅ PASSED (after fixes)
- First attempt: CustomerProfileCrew failed with `JobType` enum error
- Second attempt: CustomerProfileCrew failed with `GainRelevance` enum error
- After enum fixes: All 5 crews completed successfully
  - DiscoveryCrew → CustomerProfileCrew → ValueDesignCrew → WTPCrew → FitAssessmentCrew
- HITL `approve_vpc_completion` → Approved (fit score: 78/100)

**Phase 2 (Desirability)**: ✅ PASSED
- Signal: NO_INTEREST (problem resonance below threshold)
- HITL `approve_segment_pivot` → Selected "Healthcare Online Platforms"
- Pivot back to Phase 1 with new segment

**Phase 1 (Pivot Run)**: ✅ PASSED
- All 5 crews completed with new segment (Healthcare Online Platforms)
- CustomerProfileCrew succeeded with fixed enums
- HITL `approve_vpc_completion` → Approved
- Advancing to Phase 2 (second attempt)

**Phase 2 (Retry with Healthcare Segment)**: 🔄 IN PROGRESS
- Second Phase 2 run started with pivoted segment (Healthcare Online Platforms)
- Bug fixes deployed (#10, #11, #12) - tool input validation, error handling
- BuildCrew executing (design_landing_page task running as of 15:08)

#### Issues Discovered & Fixed

| # | Issue | Root Cause | Fix | Commit |
|---|-------|------------|-----|--------|
| 7 | `JobType` enum missing `supporting` | VPD defines 4 job types, enum only had 3 | Add `SUPPORTING = "supporting"` to enum | `359abd2` |
| 8 | `GainRelevance` enum missing `expected` | VPD Kano model has 4 levels, enum only had 3 | Add `EXPECTED = "expected"` to enum | `359abd2` |
| 9 | HITL duplicate key on pivot | Old pending HITL not cancelled before creating new | Expire pending HITLs before insert | ✅ Fixed |
| 10 | AnalyticsTool expected string, got dict | LLM passes dict `{site_id: ..., days: 7}` but tool expected JSON string | Add Pydantic `args_schema` for typed input | `623322a` |
| 11 | Segment alternatives returned `[]` on error | `generate_alternative_segments()` had no error handling | Add input validation + fallback alternatives | `623322a` |
| 12 | DesirabilityEvidence JSON parsing crashed | Malformed LLM output caused JSON parse error | Add try/catch with default evidence | `623322a` |

---

## Issue Patterns

### Pattern 1: Template Interpolation at Wrong Time

**Symptom**: `Template variable 'X' not found in inputs dictionary`

**Root Cause**: CrewAI interpolates ALL `{variable}` patterns at crew kickoff time, before any tasks run. Variables that should come from task context aren't available yet.

**Solution**:
```yaml
# WRONG - {customer_profile} comes from previous task context
discover_jobs:
  description: >
    Discover jobs using profile: {customer_profile}

# RIGHT - {founders_brief} is passed as crew input, context references previous tasks
discover_jobs:
  description: >
    ==========================================================================
    FOUNDER'S BRIEF:
    ==========================================================================
    {founders_brief}

    ==========================================================================
    YOUR TASK: Discover customer jobs based on the above.
    ==========================================================================
```

### Pattern 2: LLM Hallucination When Missing Context

**Symptom**: Agents produce completely unrelated outputs

**Root Cause**: When template variables are removed (to fix interpolation errors), agents don't receive business context and hallucinate generic responses.

**Solution**: Always include business context in first task of each crew:
- `{founders_brief}` - The business idea
- `{customer_profile}` - Who we're targeting
- `{value_map}` - What we're offering

### Pattern 3: HITL Not Respecting Validation Signals

**Symptom**: System proceeds to next phase despite negative validation signal

**Root Cause**: HITL checkpoint hardcoded, doesn't route based on signal

**Solution**: Signal-based checkpoint routing:
```python
if signal == "strong_commitment":
    checkpoint = "approve_desirability_gate"  # → Phase 3
elif signal == "no_interest":
    checkpoint = "approve_segment_pivot"  # → Phase 1
else:  # mild_interest
    checkpoint = "approve_value_pivot"  # → Phase 1
```

### Pattern 4: Segment Pivot Produces Same Segment (BUG #6)

**Symptom**: After segment pivot approval, Phase 1 re-runs but produces the same customer segment

**Evidence from Live Test**:
| | Before Pivot | After Pivot |
|---|---|---|
| Segment | SMB E-commerce (Customer Support) | SMB E-commerce (Customer Support) |
| Fit Score | 83/100 | 72/100 |

**Root Cause**: Pivot context only says "target different segment" but doesn't:
1. Tell agents WHICH segment to target
2. Provide alternative segment hypotheses
3. Capture founder input on new direction

Agents re-run discovery with same founder's brief → arrive at same conclusion.

**Solution** (Implementing):
1. **Phase 2**: When NO_INTEREST signal detected, have agents propose 2-3 alternative segments with confidence scores
2. **HITL**: Present alternatives to founder, let them choose which to test next
3. **Phase 1**: Use selected segment hypothesis to guide discovery

```python
# Phase 2 segment pivot HITL options (new structure)
options = [
    {
        "id": "segment_1",
        "label": "Enterprise E-commerce (Recommended)",
        "description": "Large retailers with $50M+ revenue, dedicated support teams",
        "confidence": 0.72,
    },
    {
        "id": "segment_2",
        "label": "SaaS Customer Success Teams",
        "description": "B2B SaaS companies with 1000+ customers needing proactive support",
        "confidence": 0.65,
    },
    {
        "id": "segment_3",
        "label": "Healthcare Patient Support",
        "description": "Healthcare providers handling patient inquiries and appointments",
        "confidence": 0.48,
    },
    {
        "id": "custom",
        "label": "Specify Different Segment",
        "description": "Enter your own segment hypothesis to test",
    },
]
```

### Pattern 5: Pydantic Enum Mismatch with VPD Framework (BUG #7, #8)

**Symptom**: `Input should be 'X', 'Y' or 'Z' [type=enum]`

**Root Cause**: Pydantic model enums don't match VPD framework terminology. The framework defines more values than the code allows.

**Examples Found**:
1. `JobType` enum: Had 3 values (functional, social, emotional), VPD defines 4 (+ supporting)
2. `GainRelevance` enum: Had 3 values (essential, nice_to_have, unexpected), VPD Kano model has 4 (+ expected)

**Solution**: Align Pydantic enums with VPD framework documentation:
```python
class JobType(str, Enum):
    FUNCTIONAL = "functional"
    SOCIAL = "social"
    EMOTIONAL = "emotional"
    SUPPORTING = "supporting"  # Buyer, co-creator, transferrer jobs

class GainRelevance(str, Enum):
    ESSENTIAL = "essential"    # Must-haves
    EXPECTED = "expected"      # Baseline expectations
    NICE_TO_HAVE = "nice_to_have"  # Differentiation
    UNEXPECTED = "unexpected"  # Delighters
```

### Pattern 6: HITL Duplicate Key on Pivot (BUG #9) - FIXED

**Symptom**: `duplicate key value violates unique constraint "idx_hitl_requests_unique_pending"`

**Root Cause**: When pivoting, the old pending HITL checkpoint isn't cancelled before the system tries to create a new one for the re-run.

**Solution** (Implemented 2026-01-10): Cancel pending HITLs before creating new ones:
```python
def create_hitl_request(run_id: str, checkpoint: HITLCheckpoint) -> Optional[str]:
    supabase = get_supabase()

    try:
        # Bug #9 fix: Cancel any existing pending HITL for this checkpoint
        # Uses 'expired' status (not 'cancelled' - not in CHECK constraint)
        cancel_result = supabase.table("hitl_requests").update({
            "status": "expired",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("run_id", run_id).eq(
            "checkpoint_name", checkpoint.checkpoint_name
        ).eq("status", "pending").execute()

        if cancel_result.data:
            logger.info(json.dumps({
                "event": "hitl_expired_for_new",
                "run_id": run_id,
                "checkpoint": checkpoint.checkpoint_name,
                "expired_count": len(cancel_result.data),
            }))

        # Now create new HITL (no conflict possible)
        result = supabase.table("hitl_requests").insert({...}).execute()
```

**Files Changed**:
- `src/state/persistence.py` - Added cancel logic in `create_hitl_request()`

### Pattern 7: Tool Input Type Mismatch (BUG #10)

**Symptom**: `Input should be a valid string [type=string_type, input_value={'site_id': '...', 'days': 7}, input_type=dict]`

**Root Cause**: CrewAI tools with string-based `_run(input_data: str)` receive dict from LLM. The LLM naturally passes structured data, but the tool expects a JSON string to parse.

**Solution**: Use Pydantic `args_schema` for typed input validation:
```python
from pydantic import BaseModel, Field

class AnalyticsInput(BaseModel):
    """Input schema for AnalyticsTool."""
    site_id: str = Field(..., description="Netlify site ID")
    days: int = Field(default=7, description="Number of days to fetch")

class AnalyticsTool(BaseTool):
    name: str = "get_analytics"
    description: str = "Fetch landing page analytics..."
    args_schema: type[BaseModel] = AnalyticsInput  # CrewAI validates input

    def _run(self, site_id: str, days: int = 7) -> str:
        # Now receives typed parameters, not JSON string
        ...
```

**Files Changed**:
- `src/shared/tools/analytics_privacy.py` - Added `AnalyticsInput`, `AdPlatformInput`, `CalendarInput` schemas

### Pattern 8: Silent Fallback Hiding Errors (BUG #11)

**Symptom**: Function returns empty results `[]` but no error in logs

**Root Cause**: Error handling catches exceptions but returns empty fallback without logging

**Solution**: Add logging and meaningful fallback data:
```python
def generate_alternative_segments(...) -> list[dict]:
    # Input validation with logging
    logger.info(json.dumps({
        "event": "segment_alternatives_input",
        "founders_brief_keys": list(founders_brief.keys()) if founders_brief else [],
    }))

    if not founders_brief:
        logger.warning("called with empty founders_brief")
        return [{
            "segment_name": "Custom Segment (Missing Data)",
            "confidence": 0.0,
            "_error": "missing_founders_brief",  # Debugging marker
        }]

    try:
        # ... generation logic
    except Exception as e:
        logger.error(json.dumps({"event": "segment_alternatives_error", "error": str(e)}))
        return [{
            "segment_name": "Custom Segment (Generation Failed)",
            "_error": str(e),  # Debugging marker
        }]
```

**Files Changed**:
- `src/modal_app/helpers/segment_alternatives.py`

### Pattern 9: Phase 2 Tool Integration Gap (System Assessment 2026-01-10)

**Symptom**: 4 of 9 Phase 2 agents had `tools=[]` (44% gap)

**Discovery**: System assessment revealed BuildCrew agents (F1, F2, F3) and GovernanceCrew G3 had no tools wired.

**Solution** (Implemented 2026-01-10): Wire existing tools to agents:
```python
# build_crew.py
from shared.tools import CanvasBuilderTool, TestCardTool, CalendarTool, MethodologyCheckTool

@agent
def f1_ux_designer(self) -> Agent:
    return Agent(
        config=self.agents_config["f1_ux_designer"],
        tools=[CanvasBuilderTool(), TestCardTool()],  # Added
        ...
    )

@agent
def f2_frontend_developer(self) -> Agent:
    return Agent(
        config=self.agents_config["f2_frontend_developer"],
        tools=[CanvasBuilderTool(), TestCardTool()],  # Added
        ...
    )

@agent
def f3_backend_developer(self) -> Agent:
    return Agent(
        config=self.agents_config["f3_backend_developer"],
        tools=[CalendarTool(), MethodologyCheckTool()],  # Added
        ...
    )

# governance_crew.py
@agent
def g3_audit_agent(self) -> Agent:
    return Agent(
        config=self.agents_config["g3_audit_agent"],
        tools=[LearningCardTool()],  # Added
        ...
    )
```

**Files Changed**:
- `src/crews/desirability/build_crew.py` - F1, F2, F3 tools wired
- `src/crews/desirability/governance_crew.py` - G3 tool wired

### Pattern 10: Container Timeout Insufficient (System Assessment 2026-01-10)

**Symptom**: GovernanceCrew terminated mid-execution during Phase 2

**Discovery**: Default 1-hour timeout may be insufficient for Phase 2-4 which run 3 crews sequentially.

**Solution** (Implemented 2026-01-10): Increase timeout from 3600s to 7200s:
```python
@app.function(
    timeout=7200,  # 2 hours - Phase 2-4 can take 40+ minutes
    cpu=2.0,
    memory=4096,
    retries=modal.Retries(max_retries=2, initial_delay=1.0),
)
def run_validation(run_id: str):

@app.function(
    timeout=7200,  # 2 hours - resumed phases can run long
    ...
)
def resume_from_checkpoint(run_id: str, checkpoint: str):
```

**Files Changed**:
- `src/modal_app/app.py` - Both functions updated

---

## Modal Operations Reference

### Useful Commands

```bash
# List running containers
modal container list --json

# View container logs
modal container logs <container-id>

# List apps (deployed and ephemeral)
modal app list

# Deploy changes
modal deploy src/modal_app/app.py

# Run specific function
modal run src/modal_app/app.py::resume_from_checkpoint --run-id "UUID" --checkpoint "name"
```

### Supabase State Queries

```python
# Check validation run status
GET /validation_runs?id=eq.{run_id}

# Check HITL requests
GET /hitl_requests?run_id=eq.{run_id}&status=eq.pending

# Check progress
GET /validation_progress?run_id=eq.{run_id}&phase=eq.{phase}&order=created_at.desc
```

---

## Next Steps

1. ~~**Test pivot loopback**: Approve segment pivot, verify Phase 1 re-runs with pivot context~~ ✅ DONE
2. ~~**Continue to Phase 2 (round 2)**: Approve `approve_vpc_completion` to test Phase 2 with pivoted segment~~ ✅ DONE (2026-01-10 15:08)
3. **Monitor Phase 2 BuildCrew**: Wait for BuildCrew → GrowthCrew → GovernanceCrew to complete
4. **Test desirability gate**: Verify signal-based HITL routing with new segment
5. **Phase 3 live test**: After desirability gate passes
6. **Phase 4 live test**: Full viability assessment
7. **Test override_proceed**: Verify force-proceed works despite pivot signal
8. **Test iterate**: Verify Phase 2 re-runs with same hypothesis

---

## Related Documents

- [ADR-002: Modal Serverless Migration](../adr/002-modal-serverless-migration.md)
- [phases.md](./phases.md) - Engineering phase status
- [09-status.md](../master-architecture/09-status.md) - Ecosystem status
