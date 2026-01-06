# Approval Workflows

Human-in-the-loop (HITL) patterns for StartupAI's gated validation system.

> **VPD Framework**: Approval workflows implement governance patterns from the Value Proposition Design framework. See [05-phase-0-1-specification.md](../05-phase-0-1-specification.md) for Phase 0-1 HITL specification.

## Overview

Certain AI decisions require human approval before proceeding. This document consolidates all approval workflow documentation from across the master architecture.

## Phase Structure

| Phase | Gate | Approvals | Purpose |
|-------|------|-----------|---------|
| **Phase 0** | Onboarding → VPC Discovery | 1 | Validate Founder's Brief before analysis |
| **Phase 1** | VPC Discovery → Validation | 3 | Experiment approval, pricing tests, VPC completion |
| **Phase 2+** | Desirability → Feasibility → Viability | 7 | Campaign, spend, stage gates, pivots |

## Approval Flow Architecture

```
┌─────────────────┐                    ┌─────────────────┐
│   CrewAI AMP    │                    │   Product App   │
│   (startupai-   │                    │  (app.startupai │
│    crew)        │                    │    .site)       │
└────────┬────────┘                    └────────┬────────┘
         │                                      │
         │ 1. Task with human_input: true       │
         │    → Flow pauses                     │
         │                                      │
         │ 2. Webhook POST                      │
         │ ─────────────────────────────────►   │
         │    {execution_id, task_id,           │
         │     task_output}                     │
         │                                      │
         │                              3. Store in approval_requests
         │                              4. Show ApprovalDetailModal
         │                              5. User decides
         │                                      │
         │ 6. POST /resume                      │
         │ ◄─────────────────────────────────   │
         │    {execution_id, task_id,           │
         │     human_feedback, is_approve}      │
         │                                      │
         │ 7. Flow resumes                      │
         │    → Router routes based on          │
         │       approval status                │
         └──────────────────────────────────────┘
```

---

## Phase 0: Onboarding Approvals

Phase 0 has a single critical approval checkpoint gating entry to Phase 1.

| Approval Type | Approver | Agents | Task | Rationale |
|---------------|----------|--------|------|-----------|
| `approve_founders_brief` | Founder + Guardian | O1, G1, G2, S1 | brief_approval | Ensure Brief accurately captures founder intent before analysis |

### Founder's Brief Approval Context

The approval request includes:
- **The Idea**: Concept and one-liner
- **Problem Hypothesis**: Who, what, current alternatives
- **Customer Hypothesis**: Segment, characteristics
- **Solution Hypothesis**: Approach, key features
- **Key Assumptions**: Ranked by risk level
- **Success Criteria**: Target metrics (problem_resonance, zombie_ratio, fit_score)
- **QA Report**: Concept legitimacy + intent verification status

### Approval Decisions

| Decision | Next Action |
|----------|-------------|
| **Approve** | Proceed to Phase 1 VPC Discovery |
| **Revise** | Return to interview for clarification |
| **Reject** | Close project (concept fails legitimacy check) |

---

## Phase 1: VPC Discovery Approvals

Phase 1 has three approval checkpoints for experiment governance.

| Approval Type | Approver | Agents | Task | Rationale |
|---------------|----------|--------|------|-----------|
| `approve_experiment_plan` | Founder + Guardian | E1 | experiment_approval | Validate test designs before execution |
| `approve_pricing_test` | Founder + Ledger | W1 | pricing_approval | Pricing tests require founder consent |
| `approve_vpc_completion` | Founder + Guardian | F1, F2 | vpc_gate_approval | Confirm fit score ≥70 before Phase 2 |

### Experiment Plan Approval Context

The approval request includes:
- **Test Cards**: Hypothesis, test method, metrics, pass/fail criteria
- **Resource Requirements**: Time, cost, tools needed
- **Assumption Priority**: Which assumptions this tests
- **Expected Evidence**: SAY vs DO classification

### VPC Completion Approval Context

The approval request includes:
- **Fit Score**: Current score (≥70 required)
- **Customer Profile**: Validated Jobs, Pains, Gains
- **Value Map**: Products/Services, Pain Relievers, Gain Creators
- **Evidence Summary**: Experiments run, pass/fail rates
- **Recommendation**: Proceed to Phase 2 or iterate

---

## Phase 2+: Validation Approvals

| Approval Type | Blocking | Primary Owner | CrewAI Task Location | Rationale |
|---------------|----------|---------------|----------------------|-----------|
| Spend Increases | Yes | Ledger | Build/Growth Crew | Budget accountability |
| Campaign Launch | Yes | Pulse | Growth Crew | Brand/reputation protection |
| Direct Customer Contact | Yes | Pulse | Growth Crew | Relationship management |
| Stage Gate Progression | Yes | Guardian | Governance Crew | Quality assurance |
| Pivot Recommendations | Yes | Compass | Synthesis Crew | Strategic alignment |
| Third-Party Data Sharing | No (Parallel) | Guardian | Governance Crew | Security/compliance |
| **Segment Pivot** | Yes | Compass | Flow Router | Evidence shows wrong audience |
| **Value Pivot** | Yes | Compass | Flow Router | Evidence shows wrong promise |
| **Feature Downgrade** | Yes | Forge | Flow Router | Technical impossibility |
| **Strategic Pivot** | Yes | Compass | Flow Router | Unit economics failure |

### Innovation Physics Pivot Triggers

The flow routers trigger approvals when evidence indicates a strategic pivot:

```python
# From founder_validation_flow.py

@router(test_desirability)
def desirability_gate(self) -> str:
    # SEGMENT PIVOT: Low problem resonance
    if evidence.problem_resonance < 0.3:
        self.state.pivot_recommendation = PivotRecommendation.SEGMENT_PIVOT
        self.state.human_input_required = True
        self.state.human_input_reason = "Customer segment shows low interest"
        return "segment_pivot_required"

    # VALUE PIVOT: Good problem resonance but high zombie ratio (70%+ interested but not committing)
    elif problem_resonance >= 0.3 and zombie_ratio >= 0.7:
        self.state.pivot_recommendation = PivotRecommendation.VALUE_PIVOT
        self.state.human_input_required = True
        self.state.human_input_reason = "Good problem resonance but high zombie ratio (70%+ not committing)"
        return "value_pivot_required"

@router(test_feasibility)
def feasibility_gate(self) -> str:
    # FEATURE DOWNGRADE: Technically impossible
    if self.state.feasibility_status == FeasibilityStatus.IMPOSSIBLE:
        self.state.human_input_required = True
        self.state.human_input_reason = "Core features technically impossible"
        return "downgrade_and_retest"

@router(test_viability)
def viability_gate(self) -> str:
    # STRATEGIC PIVOT: CAC > LTV
    if self.state.unit_economics_status == UnitEconomicsStatus.UNDERWATER:
        self.state.human_input_required = True
        self.state.human_input_reason = "Unit economics unsustainable"
        return "strategic_pivot_required"  # Choose: increase price or reduce cost
```

See `03-validation-spec.md` section "Innovation Physics - Non-Linear Flow Logic" for full router details.

### Ownership Rationale

- **Ledger owns spend** because financial accountability requires human oversight
- **Pulse owns customer-facing actions** because reputation damage is irreversible
- **Guardian owns gates** because quality standards must be maintained
- **Compass owns pivots** because strategic changes need human judgment

---

## Product App Responsibilities

### 1. Webhook Receiver (`/api/approvals/webhook`)
- Validate webhook authentication
- Store approval request in `approval_requests` table
- Check auto-approve rules in `approval_preferences`
- If auto-approve: immediately call `/resume`
- Else: send notifications (in-app, email)

### 2. Approval UI
- `ApprovalQueue.tsx` - Dashboard view of pending approvals
- `ApprovalDetailModal.tsx` - Full context and decision interface
- Show: what AI wants, evidence, risks, alternatives

### 3. Resume Client (`/services/crewai-client.ts`)
- Call CrewAI `/resume` endpoint with user decision
- Include webhook config for subsequent approvals
- Handle errors and retries

### 4. Notification Escalation
- Cron job checks for aging approvals
- Escalate: in-app → email (15min) → SMS (24hr) → backup (48hr)

---

## CrewAI Implementation

### Task Configuration
```yaml
# config/tasks.yaml
qa_gate_review:
  description: "Review phase outputs for quality and completeness"
  expected_output: "QA report with pass/fail and recommendations"
  agent: qa_agent
  human_input: true  # This triggers approval flow
```

### Flow Router
```python
@router(governance_review)
def qa_gate(self):
    if self.state.qa_status == "passed":
        return "approved"
    return "needs_revision"

@listen("approved")
def output_deliverables(self):
    return self.state
```

---

## Implementation Status

| Component | Status |
|-----------|--------|
| CrewAI `human_input` support | ✅ Available in CrewAI AMP |
| CrewAI webhook delivery | ✅ Available in CrewAI AMP |
| CrewAI `/resume` endpoint | ✅ Available in CrewAI AMP |
| Product app webhook receiver | ✅ Implemented (`/api/approvals/webhook`) |
| Product app approvals CRUD API | ✅ Implemented (`/api/approvals/`) |
| Product app `useApprovals` hook | ✅ Implemented |
| `approval_requests` table | ✅ Deployed (migration 20251126000002) |
| `approval_preferences` table | ✅ Deployed (migration 20251126000002) |
| `approval_history` table | ✅ Deployed (migration 20251126000002) |
| Product app approval UI components | ⏳ Partial (API ready, full UI pending) |
| Product app resume client | ❌ NOT IMPLEMENTED |
| Notification escalation | ❌ NOT IMPLEMENTED |
| Auto-approve rules | ❌ NOT IMPLEMENTED |

---

## Related Documents

- **Phase 0-1 Specification**: `../05-phase-0-1-specification.md` (VPD framework implementation)
- **API payloads**: `api-contracts.md`
- **Founder ownership**: `../02-organization.md`
- **Implementation details**: `../03-validation-spec.md` (Phase 2+ blueprint)

---
**Last Updated**: 2026-01-05

**Latest Changes**:
- Added Phase 0 Onboarding Approvals (approve_founders_brief)
- Added Phase 1 VPC Discovery Approvals (approve_experiment_plan, approve_pricing_test, approve_vpc_completion)
- Added approval context documentation for VPD-specific checkpoints
- Reorganized by phase structure
