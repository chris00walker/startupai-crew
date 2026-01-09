---
purpose: Track learnings from live Modal testing with real LLM calls
status: active
last_updated: 2026-01-09
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
2. **Continue to Phase 2 (round 2)**: Approve `approve_vpc_completion` to test Phase 2 with pivoted segment
3. **Test override_proceed**: Verify force-proceed works despite pivot signal
4. **Test iterate**: Verify Phase 2 re-runs with same hypothesis
5. **Phase 3 live test**: After desirability gate passes
6. **Phase 4 live test**: Full viability assessment

---

## Related Documents

- [ADR-002: Modal Serverless Migration](../adr/002-modal-serverless-migration.md)
- [phases.md](./phases.md) - Engineering phase status
- [09-status.md](../master-architecture/09-status.md) - Ecosystem status
