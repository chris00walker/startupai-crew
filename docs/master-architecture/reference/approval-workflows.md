---
purpose: Human-in-the-loop approval workflow patterns
status: active
last_reviewed: 2026-01-08
vpd_compliance: true
---

# Approval Workflows

Human-in-the-loop (HITL) patterns for StartupAI's gated validation system.

> **VPD Framework**: Approval workflows implement governance patterns from the Value Proposition Design framework. See phase documents for HITL specifications:
> - [04-phase-0-onboarding.md](../04-phase-0-onboarding.md) - Phase 0 HITL (approve_founders_brief)
> - [05-phase-1-vpc-discovery.md](../05-phase-1-vpc-discovery.md) - Phase 1 HITL (experiment, pricing, VPC completion)
> - [06-phase-2-desirability.md](../06-phase-2-desirability.md) - Phase 2 HITL (campaign, spend, gate)
> - [07-phase-3-feasibility.md](../07-phase-3-feasibility.md) - Phase 3 HITL (feasibility gate)
> - [08-phase-4-viability.md](../08-phase-4-viability.md) - Phase 4 HITL (viability gate, final decision)

## Overview

Certain AI decisions require human approval before proceeding. This document consolidates all approval workflow documentation from across the master architecture.

## Phase Structure

| Phase | Gate | Approvals | Purpose |
|-------|------|-----------|---------|
| **Phase 0** | Onboarding → VPC Discovery | 1 | Validate Founder's Brief before analysis |
| **Phase 1** | VPC Discovery → Validation | 3 | Experiment approval, pricing tests, VPC completion |
| **Phase 2+** | Desirability → Feasibility → Viability | 7 | Campaign, spend, stage gates, pivots |

## Approval Flow Architecture

### Modal Serverless Pattern (Target)

> **Architecture**: Per [ADR-002](../../adr/002-modal-serverless-migration.md), HITL uses checkpoint-and-resume pattern with $0 cost during human review.

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Modal Function │      │    Supabase     │      │   Product App   │
│  (ephemeral)    │      │  (persistent)   │      │  (app.startupai │
└────────┬────────┘      └────────┬────────┘      │    .site)       │
         │                        │               └────────┬────────┘
         │ 1. HITL checkpoint     │                        │
         │    reached             │                        │
         │                        │                        │
         │ 2. INSERT hitl_requests│                        │
         │ ───────────────────────►                        │
         │                        │                        │
         │ 3. Container terminates│                        │
         │    ($0 while waiting)  │                        │
         X                        │                        │
                                  │ 4. Realtime notifies   │
                                  │ ───────────────────────►
                                  │                        │
                                  │               5. User reviews in UI
                                  │               6. User approves
                                  │                        │
                                  │ 7. POST /hitl/approve  │
         ┌─────────────────────── │ ◄───────────────────────
         │ 8. New container       │                        │
         │    spawns              │                        │
         │                        │                        │
         │ 9. Resume from         │                        │
         │    checkpoint          │                        │
         │                        │                        │
         └────────────────────────────────────────────────────
```

**Key Benefits**:
- **$0 during human review**: Container terminates, no compute costs while waiting
- **Hours/days supported**: No timeout limits on human decisions
- **State in Supabase**: Full audit trail, Realtime updates to UI

### AMP Pattern (DEPRECATED)

> **⚠️ DEPRECATED**: Being replaced by Modal serverless. See [ADR-002](../../adr/002-modal-serverless-migration.md).

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
| `approve_founders_brief` | Founder + Guardian | O1, GV1, GV2, S1 | brief_approval | Ensure Brief accurately captures founder intent before analysis |

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

See [03-methodology.md](../03-methodology.md) section "Routing Logic (Innovation Physics)" and [concepts/innovation-physics.md](../../concepts/innovation-physics.md) for full router details.

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

- [ADR-002: Modal Serverless Migration](../../adr/002-modal-serverless-migration.md) - HITL checkpoint-and-resume architecture
- [api-contracts.md](./api-contracts.md) - API payloads including Modal `/hitl/approve`
- [database-schemas.md](./database-schemas.md) - `hitl_requests` table schema
- [modal-configuration.md](./modal-configuration.md) - Modal platform configuration
- [02-organization.md](../02-organization.md) - Founder ownership for approvals
- [04-phase-0-onboarding.md](../04-phase-0-onboarding.md) - Phase 0 HITL specification
- [05-phase-1-vpc-discovery.md](../05-phase-1-vpc-discovery.md) - Phase 1 HITL specification
- [06-phase-2-desirability.md](../06-phase-2-desirability.md) - Phase 2 HITL specification
- [07-phase-3-feasibility.md](../07-phase-3-feasibility.md) - Phase 3 HITL specification
- [08-phase-4-viability.md](../08-phase-4-viability.md) - Phase 4 HITL specification

---
**Last Updated**: 2026-01-08

**Latest Changes (2026-01-08 - Modal migration alignment)**:
- Fixed cross-references to point to phase documents (04-08) instead of archived specs
- Added Modal Serverless Pattern diagram showing checkpoint-and-resume flow
- Marked AMP Pattern as DEPRECATED
- Updated Related Documents section with links to ADR-002 and phase docs

**Previous Changes (2026-01-05)**:
- Added Phase 0 Onboarding Approvals (approve_founders_brief)
- Added Phase 1 VPC Discovery Approvals (approve_experiment_plan, approve_pricing_test, approve_vpc_completion)
- Added approval context documentation for VPD-specific checkpoints
- Reorganized by phase structure
