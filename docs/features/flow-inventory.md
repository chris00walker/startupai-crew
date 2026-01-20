---
document_type: feature-audit
status: active
last_verified: 2026-01-19
architectural_pivot: 2026-01-19
---

# Flow Inventory

> **Architectural Pivot (2026-01-19)**: Phase 0 was simplified to Quick Start - no OnboardingFlow. See [ADR-006](../adr/006-quick-start-architecture.md).

## Purpose
Authoritative inventory of all 4 Flows in the StartupAI validation engine with entry/exit criteria and HITL checkpoints.

## Quick Reference

| Phase | Flow | Crews | Agents | HITL Checkpoint | Status |
|-------|------|-------|--------|-----------------|--------|
| 0 | ~~OnboardingFlow~~ | 0 | 0 | None | `Quick Start (no AI)` |
| 1 | VPCDiscoveryFlow | 6 | 20 | `approve_discovery_output` | `active` |
| 2 | DesirabilityFlow | 3 | 9 | `approve_desirability_gate` / `approve_segment_pivot` / `approve_value_pivot` | `active` |
| 3 | FeasibilityFlow | 2 | 5 | `approve_feasibility_gate` | `active` |
| 4 | ViabilityFlow | 3 | 9 | `request_human_decision` | `active` |

**Totals**: 4 Flows, 14 Crews, 43 Agents, 10 HITL Checkpoints (Phase 0 has no HITL)

---

## Phase 0: Quick Start (No AI)

> **Architectural Pivot (2026-01-19)**: Phase 0 was simplified to Quick Start. See [ADR-006](../adr/006-quick-start-architecture.md).

### No OnboardingFlow

Phase 0 is now a **simple form submission** - no AI, no flows, no crews.

| Metric | Value |
|--------|-------|
| Duration | ~30 seconds |
| AI Cost | $0 |
| Crews | None |
| Agents | None |
| HITL Checkpoints | None |

### Entry Criteria
- User submits Quick Start form with `raw_idea` (min 10 chars)
- Optional: `additional_context` (pitch deck text or notes)

### Exit Criteria
- Form submitted successfully
- Project created in database
- Phase 1 triggered automatically

### Output
- `raw_idea`: User's business idea text
- `additional_context`: Optional supplementary context
- `project_id`: Created project UUID
- → **Phase 1 starts immediately**

---

## Phase 1: VPCDiscoveryFlow + Brief Generation

**File**: `src/modal_app/phases/phase_1.py`

### Entry Criteria
- `raw_idea` from Quick Start form (Phase 0)
- Optional: `additional_context` (pitch deck text or notes)
- Optional: `pivot_context` if looping from Phase 2 segment pivot

### Crews Executed
1. **BriefGenerationCrew** (2 agents) - Generates Founder's Brief from research (NEW)
   - GV1: Concept Validator (moved from Phase 0)
   - S1: Brief Compiler (moved from Phase 0)
2. **DiscoveryCrew** (5 agents) - Segment discovery and research
3. **CustomerProfileCrew** (6 agents) - Jobs, Pains, Gains extraction
4. **ValueDesignCrew** (3 agents) - Pain Relievers, Gain Creators
5. **WTPCrew** (2 agents) - Willingness-to-pay analysis
6. **FitAssessmentCrew** (2 agents) - VPC fit scoring

### Brief Generation (NEW)
BriefGenerationCrew generates the Founder's Brief from:
1. User's `raw_idea` (Quick Start input)
2. Market research (AI-conducted)
3. Competitor analysis (AI-conducted)

### Pivot Context Handling
If `pivot_type == "segment_pivot"` (from Phase 2):
- Injects `target_segment_hypothesis` into research
- Prevents rediscovery of failed segment
- File reference: `phase_1.py:57-80`

### HITL Checkpoint: `approve_discovery_output` (Combined Brief + VPC)

| Option | Label | Description | Next Action |
|--------|-------|-------------|-------------|
| `approve` | Approve | Brief and VPC are accurate, proceed | → Continue Phase 1 |
| `edit` | Save Edits | User edited brief before approving | → Continue Phase 1 |
| `reject` | Start Over | Research is fundamentally wrong | → Return to Quick Start |

**Default Recommendation**: `approve` if fit_score >= 70, else `edit`

### Gate Condition
- `fit_score >= 70` required to proceed to Phase 2

### Exit Criteria
- Human approval of discovery output (Brief + VPC)
- Fit score meets threshold (70)

### Outputs
- `founders_brief`: AI-generated Founder's Brief
- `customer_profile`: CustomerProfile (Jobs, Pains, Gains)
- `value_map`: ValueMap (Products, Pain Relievers, Gain Creators)
- `wtp_results`: WTP analysis results
- `fit_assessment`: FitAssessment (fit_score, gate_ready)

---

## Phase 2: DesirabilityFlow

**File**: `src/modal_app/phases/phase_2.py`

### Entry Criteria
- `customer_profile` and `value_map` from Phase 1
- `founders_brief` from Phase 0

### Crews Executed
1. **BuildCrew** (3 agents) - Landing page, ad creative generation
2. **GrowthCrew** (3 agents) - Campaign execution, analytics
3. **GovernanceCrew** (3 agents) - Spend approval, quality gates

### Signal-Based Routing
Per Innovation Physics methodology:

| Signal | Condition | Checkpoint | Recommendation |
|--------|-----------|------------|----------------|
| `strong_commitment` | resonance >= 30%, zombie < 70% | `approve_desirability_gate` | Proceed |
| `no_interest` | resonance < 30% | `approve_segment_pivot` | Segment Pivot |
| `mild_interest` | resonance >= 30%, zombie >= 70% | `approve_value_pivot` | Value Pivot |

**Metrics Calculation** (phase_2.py:236-248):
- `problem_resonance`: (clicks + signups) / impressions
- `zombie_ratio`: (clicks - signups) / clicks

### HITL Checkpoint: Signal-Dependent

#### If `strong_commitment` → `approve_desirability_gate`

| Option | Label | Description | Next Action |
|--------|-------|-------------|-------------|
| `approved` | Proceed to Feasibility | Continue to Phase 3 | → Phase 3 |
| `iterate` | Run More Experiments | Gather additional evidence | → Loop Phase 2 |

#### If `no_interest` → `approve_segment_pivot`

| Option | Label | Description | Next Action |
|--------|-------|-------------|-------------|
| `segment_1` | Alternative Segment 1 | GPT-generated alternative | → Phase 1 (pivot) |
| `segment_2` | Alternative Segment 2 | GPT-generated alternative | → Phase 1 (pivot) |
| `segment_3` | Alternative Segment 3 | GPT-generated alternative | → Phase 1 (pivot) |
| `custom_segment` | Specify Different Segment | User-defined segment | → Phase 1 (pivot) |
| `override_proceed` | Override - Proceed Anyway | Ignore signal (requires justification) | → Phase 3 |
| `iterate` | Run More Experiments | Re-run with current segment | → Loop Phase 2 |

**Alternative Segments**: Generated by `generate_alternative_segments()` (src/modal_app/helpers/segment_alternatives.py:20)

#### If `mild_interest` → `approve_value_pivot`

| Option | Label | Description | Next Action |
|--------|-------|-------------|-------------|
| `approved` | Approve Value Pivot | Return to refine value prop | → Phase 1 |
| `override_proceed` | Override - Proceed Anyway | Ignore signal | → Phase 3 |
| `iterate` | Run More Experiments | Gather additional evidence | → Loop Phase 2 |

### Exit Criteria
- Human approval of desirability gate OR pivot selection
- Signal determination complete

### Outputs
- `build_results`: Landing page and ad creative artifacts
- `desirability_evidence`: DesirabilityEvidence (metrics, signal)
- `desirability_signal`: strong_commitment | no_interest | mild_interest
- `segment_alternatives`: (if no_interest) GPT-generated alternatives

---

## Phase 3: FeasibilityFlow

**File**: `src/modal_app/phases/phase_3.py`

### Entry Criteria
- `customer_profile` and `value_map` from Phase 1
- Desirability gate passed (Phase 2)

### Crews Executed
1. **FeasibilityBuildCrew** (3 agents) - Technical assessment
2. **FeasibilityGovernanceCrew** (2 agents) - Gate validation

### Signal Determination
| Signal | Condition | Recommendation |
|--------|-----------|----------------|
| `green` | Core features feasible, no downgrade | Proceed |
| `orange_constrained` | Feasible with feature downgrade | Feature Pivot |
| `red_impossible` | Core features not feasible | Kill |

### HITL Checkpoint: `approve_feasibility_gate`

| Option | Label | Description | Next Action |
|--------|-------|-------------|-------------|
| `approve` | Approve | Proceed to Viability analysis | → Phase 4 |
| `feature_pivot` | Feature Pivot | Downgrade features, re-test desirability | → Phase 2 |
| `kill` | Kill Project | Technical impossibility | → Fail |

**Default Recommendation**: `approve` if signal == green, else derived from signal

### Exit Criteria
- Human approval of feasibility gate
- Technical assessment complete

### Outputs
- `feasibility_evidence`: FeasibilityEvidence (costs, constraints, signal)
- `feasibility_signal`: green | orange_constrained | red_impossible

---

## Phase 4: ViabilityFlow

**File**: `src/modal_app/phases/phase_4.py`

### Entry Criteria
- All prior phase outputs (founders_brief, customer_profile, value_map, wtp_results, desirability_evidence, feasibility_evidence)
- Feasibility gate passed (Phase 3)

### Crews Executed
1. **FinanceCrew** (3 agents) - CAC/LTV, pricing, market sizing
2. **SynthesisCrew** (3 agents) - Evidence synthesis, decision recommendation
3. **ViabilityGovernanceCrew** (3 agents) - Final audit, flywheel

### Signal Determination
| Signal | Condition | Recommendation |
|--------|-----------|----------------|
| `profitable` | LTV/CAC >= 3.0 | Proceed |
| `marginal` | 1.0 <= LTV/CAC < 3.0, TAM < $1M | Strategic Pivot |
| `underwater` | LTV/CAC < 1.0 | Strategic Pivot |

### HITL Checkpoint: `request_human_decision`

| Option | Label | Description | Next Action |
|--------|-------|-------------|-------------|
| `proceed` | Proceed | Validation complete - move to execution | → Complete |
| `price_pivot` | Price Pivot | Increase prices, re-test desirability | → Phase 2 |
| `cost_pivot` | Cost Pivot | Reduce costs, re-assess feasibility | → Phase 3 |
| `model_pivot` | Model Pivot | Change business model | → Phase 1 |
| `kill` | Kill Project | No viable path forward | → Fail |

**Default Recommendation**: `proceed` if signal == profitable, else `price_pivot`

### Exit Criteria
- Human decision on final action
- All evidence synthesized

### Outputs
- `viability_evidence`: ViabilityEvidence (CAC, LTV, ratio, market sizing)
- `viability_signal`: profitable | marginal | underwater
- `synthesis_results`: Evidence synthesis
- `pivot_recommendation`: no_pivot | strategic_pivot
- `final_decision`: proceed | pivot | kill
- `decision_rationale`: Human-readable explanation

---

## Flow Orchestration

### Sequential Execution
```
Quick Start (30 sec) → Phase 1 → [HITL approve_discovery_output] →
Phase 2 → [HITL signal-dependent] → Phase 3 → [HITL approve_feasibility_gate] →
Phase 4 → [HITL request_human_decision] → COMPLETE
```

### Pivot Loopbacks
| Pivot Type | From | To | State Preserved |
|------------|------|-----|-----------------|
| Segment Pivot | Phase 2 | Phase 1 | founders_brief, target_segment_hypothesis |
| Value Pivot | Phase 2 | Phase 1 | founders_brief, failed_segment |
| Feature Pivot | Phase 3 | Phase 2 | VPC outputs |
| Price Pivot | Phase 4 | Phase 2 | VPC outputs, feasibility_evidence |
| Cost Pivot | Phase 4 | Phase 3 | All prior evidence |
| Model Pivot | Phase 4 | Phase 1 | founders_brief only |

### Container Termination at HITL
Per ADR-002 (Modal serverless architecture):
- Container terminates after HITL checkpoint created
- $0 cost during human review
- Container resumes on `/hitl/approve` webhook
- State checkpointed to Supabase

---

## Gaps / TODOs

- [ ] Phase 1 docstring says "HITL Checkpoints: approve_experiment_plan, approve_pricing_test, approve_vpc_completion" but only `approve_vpc_completion` is implemented (phase_1.py:371)
- [ ] Phase 2 has 3 potential checkpoints but routing is signal-dependent (no unconditional pre-campaign checkpoint)
- [ ] Phase 4 docstring lists `approve_viability_gate`, `approve_pivot`, `approve_proceed`, `request_human_decision` but only `request_human_decision` is implemented (phase_4.py:322)

---

## Related Documents

- [crew-agent-task-matrix.md](./crew-agent-task-matrix.md) - Crew and agent details
- [hitl-checkpoint-map.md](./hitl-checkpoint-map.md) - HITL checkpoint details
- [api-entrypoints.md](./api-entrypoints.md) - Modal API endpoints
- [integration-contracts.md](./integration-contracts.md) - Product app integration
