# Approval Workflows

Human-in-the-loop (HITL) patterns for StartupAI's gated validation system.

## Overview

Certain AI decisions require human approval before proceeding. This document consolidates all approval workflow documentation from across the master architecture.

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

## Approval Types & Ownership

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
# From internal_validation_flow.py

@router(test_desirability)
def desirability_gate(self) -> str:
    # SEGMENT PIVOT: Low problem resonance
    if evidence.problem_resonance < 0.3:
        self.state.pivot_recommendation = PivotRecommendation.SEGMENT_PIVOT
        self.state.human_input_required = True
        self.state.human_input_reason = "Customer segment shows low interest"
        return "segment_pivot_required"

    # VALUE PIVOT: High traffic, low commitment (zombie)
    elif evidence.traffic_quality == "High" and zombie_ratio < 0.1:
        self.state.pivot_recommendation = PivotRecommendation.VALUE_PIVOT
        self.state.human_input_required = True
        self.state.human_input_reason = "High traffic but low commitment"
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
| Product app webhook receiver | ❌ NOT IMPLEMENTED |
| Product app approval UI | ❌ NOT IMPLEMENTED |
| Product app resume client | ❌ NOT IMPLEMENTED |
| Notification escalation | ❌ NOT IMPLEMENTED |
| Auto-approve rules | ❌ NOT IMPLEMENTED |

---

## Related Documents

- API payloads: `api-contracts.md`
- Founder ownership: `../02-organization.md`
- Implementation details: `../03-validation-spec.md`

---
**Last Updated**: 2025-11-22

**Latest Changes**: Added Innovation Physics pivot triggers (Segment, Value, Feature Downgrade, Strategic) and router code examples.
