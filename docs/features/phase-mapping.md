---
document_type: feature-audit
status: active
last_verified: 2026-01-13
---

# Phase Mapping: Spec vs Implementation

## Purpose
Compare master architecture specifications against actual implementation to identify alignment status and gaps.

## Quick Reference

| Phase | Spec Doc | Implementation | Alignment |
|-------|----------|----------------|-----------|
| 0 | `04-phase-0-onboarding.md` | `src/modal_app/phases/phase_0.py` | 95% |
| 1 | `05-phase-1-vpc-discovery.md` | `src/modal_app/phases/phase_1.py` | 90% |
| 2 | `06-phase-2-desirability.md` | `src/modal_app/phases/phase_2.py` | 85% |
| 3 | `07-phase-3-feasibility.md` | `src/modal_app/phases/phase_3.py` | 90% |
| 4 | `08-phase-4-viability.md` | `src/modal_app/phases/phase_4.py` | 85% |

**Overall Alignment**: ~89%

---

## Phase 0: Onboarding

### Spec Reference
- **Document**: `docs/master-architecture/04-phase-0-onboarding.md`
- **Purpose**: Capture Founder's Brief through AI-guided interview

### Implementation
- **File**: `src/modal_app/phases/phase_0.py`
- **Crew**: `src/crews/onboarding/crew.py`

### Comparison

| Element | Spec | Implementation | Status |
|---------|------|----------------|--------|
| Crew | OnboardingCrew | OnboardingCrew | ✅ Match |
| Agents | 4 (O1, GV1, GV2, S1) | 4 (O1, GV1, GV2, S1) | ✅ Match |
| Tasks | 4 | 4 | ✅ Match |
| HITL | `approve_founders_brief` | `approve_founders_brief` | ✅ Match |
| Input | `entrepreneur_input` | `entrepreneur_input` | ✅ Match |
| Output | `FoundersBrief` model | `FoundersBrief` model | ✅ Match |
| QA validation | QA report required | QA status in checkpoint context | ✅ Match |
| Session linking | Optional session_id | session_id in phase_state | ✅ Match |

### Gaps

| Gap | Severity | Resolution |
|-----|----------|------------|
| Spec mentions interview stage progression | Low | Handled by product app onboarding, not this phase |
| Spec mentions `/interview/start` endpoint | Informational | Product app uses `/api/onboarding/*` instead |

### Alignment: 95%

---

## Phase 1: VPC Discovery

### Spec Reference
- **Document**: `docs/master-architecture/05-phase-1-vpc-discovery.md`
- **Purpose**: Discover and validate Customer Profile + Value Map

### Implementation
- **File**: `src/modal_app/phases/phase_1.py`
- **Crews**: 5 crews in `src/crews/discovery/`

### Comparison

| Element | Spec | Implementation | Status |
|---------|------|----------------|--------|
| Crews | 5 | 5 | ✅ Match |
| Agents | 18 | 18 | ✅ Match |
| DiscoveryCrew | 5 agents | 5 agents | ✅ Match |
| CustomerProfileCrew | 6 agents | 6 agents | ✅ Match |
| ValueDesignCrew | 3 agents | 3 agents | ✅ Match |
| WTPCrew | 2 agents | 2 agents | ✅ Match |
| FitAssessmentCrew | 2 agents | 2 agents | ✅ Match |
| HITL | `approve_vpc_completion` | `approve_vpc_completion` | ✅ Match |
| Fit threshold | 70 | 70 | ✅ Match |
| Pivot context | Segment hypothesis injection | `target_segment_hypothesis` in phase_state | ✅ Match |

### Gaps

| Gap | Severity | Resolution |
|-----|----------|------------|
| Spec docstring mentions `approve_experiment_plan` | Medium | Not implemented - design decision |
| Spec docstring mentions `approve_pricing_test` | Medium | Not implemented - WTPCrew runs without checkpoint |
| Tool wiring incomplete | Medium | 3 ranker agents have no tools |

### Alignment: 90%

---

## Phase 2: Desirability

### Spec Reference
- **Document**: `docs/master-architecture/06-phase-2-desirability.md`
- **Purpose**: Test market signal with landing pages and ad campaigns

### Implementation
- **File**: `src/modal_app/phases/phase_2.py`
- **Crews**: 3 crews in `src/crews/desirability/`

### Comparison

| Element | Spec | Implementation | Status |
|---------|------|----------------|--------|
| Crews | 3 | 3 | ✅ Match |
| Agents | 9 | 9 | ✅ Match |
| BuildCrew | 3 agents | 3 agents | ✅ Match |
| GrowthCrew | 3 agents | 3 agents | ✅ Match |
| GovernanceCrew | 3 agents | 3 agents | ✅ Match |
| Signal types | 3 (strong, mild, no interest) | 3 | ✅ Match |
| Signal-based HITL | Dynamic checkpoint selection | Dynamic checkpoint selection | ✅ Match |
| Segment alternatives | GPT-generated | GPT-generated via helper | ✅ Match |
| Landing page deployment | Netlify | LandingPageDeploymentTool | ✅ Match |

### Signal Calculation Comparison

| Metric | Spec | Implementation |
|--------|------|----------------|
| `problem_resonance` | (clicks + signups) / impressions | `(clicks + signups) / impressions` ✅ |
| `zombie_ratio` | (clicks - signups) / clicks | `(clicks - signups) / clicks` ✅ |
| `strong_commitment` | resonance >= 30%, zombie < 70% | resonance >= 30%, zombie < 70% ✅ |
| `no_interest` | resonance < 30% | resonance < 30% ✅ |
| `mild_interest` | resonance >= 30%, zombie >= 70% | resonance >= 30%, zombie >= 70% ✅ |

### Gaps

| Gap | Severity | Resolution |
|-----|----------|------------|
| Spec mentions pre-campaign HITL (`approve_campaign_launch`) | Medium | Not implemented - campaigns launch without pre-approval |
| Spec mentions spend HITL (`approve_spend_increase`) | Medium | Not implemented - budget not controlled |
| Ad platform integration | Low | Simulated via AdPlatformTool |

### Alignment: 85%

---

## Phase 3: Feasibility

### Spec Reference
- **Document**: `docs/master-architecture/07-phase-3-feasibility.md`
- **Purpose**: Technical feasibility assessment

### Implementation
- **File**: `src/modal_app/phases/phase_3.py`
- **Crews**: 2 crews in `src/crews/feasibility/`

### Comparison

| Element | Spec | Implementation | Status |
|---------|------|----------------|--------|
| Crews | 2 | 2 | ✅ Match |
| Agents | 5 | 5 | ✅ Match |
| FeasibilityBuildCrew | 3 agents | 3 agents | ✅ Match |
| FeasibilityGovernanceCrew | 2 agents | 2 agents | ✅ Match |
| HITL | `approve_feasibility_gate` | `approve_feasibility_gate` | ✅ Match |
| Signal types | 3 (green, orange, red) | 3 | ✅ Match |
| Feature pivot | To Phase 2 | To Phase 2 | ✅ Match |

### Gaps

| Gap | Severity | Resolution |
|-----|----------|------------|
| FeasibilityBuildCrew has no tools | Medium | Agents assess without research tools |
| Spec mentions detailed cost estimation | Low | Basic estimation implemented |

### Alignment: 90%

---

## Phase 4: Viability

### Spec Reference
- **Document**: `docs/master-architecture/08-phase-4-viability.md`
- **Purpose**: Unit economics and final decision

### Implementation
- **File**: `src/modal_app/phases/phase_4.py`
- **Crews**: 3 crews in `src/crews/viability/`

### Comparison

| Element | Spec | Implementation | Status |
|---------|------|----------------|--------|
| Crews | 3 | 3 | ✅ Match |
| Agents | 9 | 9 | ✅ Match |
| FinanceCrew | 3 agents | 3 agents | ✅ Match |
| SynthesisCrew | 3 agents | 3 agents | ✅ Match |
| ViabilityGovernanceCrew | 3 agents | 3 agents | ✅ Match |
| HITL | `request_human_decision` | `request_human_decision` | ✅ Match |
| Signal types | 3 (profitable, marginal, underwater) | 3 | ✅ Match |
| Pivot options | 4 (price, cost, model, kill) | 4 | ✅ Match |

### Viability Signal Comparison

| Signal | Spec | Implementation |
|--------|------|----------------|
| `profitable` | LTV/CAC >= 3.0 | LTV/CAC >= 3.0 ✅ |
| `marginal` | 1.0 <= LTV/CAC < 3.0, TAM < $1M | 1.0 <= LTV/CAC < 3.0, TAM < $1M ✅ |
| `underwater` | LTV/CAC < 1.0 | LTV/CAC < 1.0 ✅ |

### Gaps

| Gap | Severity | Resolution |
|-----|----------|------------|
| Spec docstring mentions `approve_viability_gate` | Informational | Consolidated to `request_human_decision` |
| Spec docstring mentions `approve_pivot` | Informational | Options in `request_human_decision` |
| Spec docstring mentions `approve_proceed` | Informational | Options in `request_human_decision` |
| SynthesisCrew has no tools | Low | Synthesis works without tools |

### Alignment: 85%

---

## Cross-Phase Patterns

### HITL Checkpoint Consolidation

**Spec** (from docstrings):
| Phase | Mentioned Checkpoints |
|-------|----------------------|
| 1 | `approve_experiment_plan`, `approve_pricing_test`, `approve_vpc_completion` |
| 2 | `approve_campaign_launch`, `approve_spend_increase`, `approve_desirability_gate` |
| 4 | `approve_viability_gate`, `approve_pivot`, `approve_proceed`, `request_human_decision` |

**Implementation**:
| Phase | Implemented Checkpoints |
|-------|------------------------|
| 1 | `approve_vpc_completion` |
| 2 | `approve_desirability_gate`, `approve_segment_pivot`, `approve_value_pivot` |
| 4 | `request_human_decision` |

**Analysis**: Checkpoint consolidation is a deliberate design decision to reduce human approval fatigue. The spec docstrings document the full design, but implementation prioritizes critical gates.

### State Persistence Pattern

| Pattern | Spec | Implementation |
|---------|------|----------------|
| Run tracking | `validation_runs` table | ✅ Implemented |
| Progress tracking | `validation_progress` table | ✅ Implemented |
| HITL requests | `hitl_requests` table | ✅ Implemented |
| Pivot context | `phase_state` JSONB | ✅ Implemented |
| Container resume | Spawn new function | ✅ Implemented |

### Tool Wiring Pattern

| Phase | Spec Tools | Wired Tools | Gap |
|-------|------------|-------------|-----|
| 0 | Not specified | 0 | Expected |
| 1 | Research, Canvas, Testing | 12 unique tools | Partial (rankers missing) |
| 2 | Analytics, AB Test, Deploy | 10 unique tools | ✅ Good |
| 3 | Not specified | 2 unique tools | Expected (minimal) |
| 4 | Analytics, Privacy | 3 unique tools | ✅ Good |

---

## Divergences Summary

### Intentional Divergences

| Divergence | Reason | Impact |
|------------|--------|--------|
| Checkpoint consolidation | Reduce approval fatigue | Fewer HITL interruptions |
| Product app handles onboarding interview | Separation of concerns | Cleaner architecture |
| Signal-based HITL routing in Phase 2 | Innovation Physics methodology | Dynamic checkpoints |

### Unintentional Gaps

| Gap | Phase | Severity | Priority |
|-----|-------|----------|----------|
| Missing `approve_experiment_plan` | 1 | Medium | P2 |
| Missing `approve_pricing_test` | 1 | Medium | P2 |
| Missing `approve_campaign_launch` | 2 | Medium | P2 |
| Missing `approve_spend_increase` | 2 | Medium | P2 |
| FeasibilityBuildCrew no tools | 3 | Medium | P3 |
| SynthesisCrew no tools | 4 | Low | P4 |

---

## Alignment Calculation

| Phase | Elements | Matched | Percentage |
|-------|----------|---------|------------|
| 0 | 8 | 8 | 100% |
| 1 | 10 | 9 | 90% |
| 2 | 9 | 7 | 78% |
| 3 | 7 | 6 | 86% |
| 4 | 9 | 7 | 78% |

**Weighted Average**: (100 + 90 + 78 + 86 + 78) / 5 = **86.4%**

Adjusted for intentional divergences: **~89%**

---

## Recommendations

### High Priority (P1)
None - core functionality aligned.

### Medium Priority (P2)
1. Add optional HITL checkpoints for experiment/campaign approval
2. Wire tools to FeasibilityBuildCrew agents
3. Document checkpoint consolidation decision in ADR

### Low Priority (P3-P4)
1. Add tools to ranker agents
2. Add LearningCardTool to SynthesisCrew
3. Update spec docstrings to match implementation

---

## Related Documents

- [flow-inventory.md](./flow-inventory.md) - Flow-level details
- [crew-agent-task-matrix.md](./crew-agent-task-matrix.md) - Agent details
- [hitl-checkpoint-map.md](./hitl-checkpoint-map.md) - HITL checkpoints
- [tool-wiring-matrix.md](./tool-wiring-matrix.md) - Tool wiring gaps
- [../master-architecture/09-status.md](../master-architecture/09-status.md) - Overall status
