# API Contracts

All API endpoints, webhooks, and payloads for StartupAI services.

## CrewAI AMP Endpoints

**Base URL**: `https://startupai-6b1e5c4d-e708-4921-be55-08fcb0d1e-922bcddb.crewai.com`

### Working Endpoints

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/inputs` | GET | Schema for input parameters | Working |
| `/kickoff` | POST | Start analysis workflow | Working |
| `/status/{id}` | GET | Check execution status | Working |
| `/resume` | POST | Resume paused flow with human input | Working |

### Kickoff Request
```bash
curl -X POST https://startupai-...crewai.com/kickoff \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "entrepreneur_input": "Business idea description..."
  }'
```

### Status Response
```json
{
  "kickoff_id": "uuid",
  "status": "running|completed|failed|paused",
  "current_phase": "desirability|feasibility|viability|complete",
  "router_decision": "run_desirability_experiments|desirability_gate_passed|run_feasibility_validation|feasibility_gate_passed|run_viability_analysis|terminal_validated|terminal_killed",
  "blocking_approval_required": false,
  "result": {
    "validation_report": {
      "evidence_strength": "strong|weak|none",
      "pivot_recommendation": "segment_pivot|value_pivot|feature_pivot|strategic_pivot|no_pivot|kill",
      "human_input_required": false,
      "next_steps": ["..."]
    },
    "value_proposition_canvas": { ... },
    "evidence": {
      "desirability": {
        "problem_resonance": 0.65,
        "zombie_ratio": 0.15,
        "commitment_type": "skin_in_game|verbal|none"
      },
      "feasibility": {
        "status": "possible|constrained|impossible"
      },
      "viability": {
        "cac": 150.00,
        "ltv": 600.00,
        "ltv_cac_ratio": 4.0,
        "unit_economics_status": "profitable|marginal|underwater"
      }
    },
    "desirability_gate": {
      "passed": true,
      "evidence": {
        "problem_resonance": 0.65,
        "zombie_ratio": 0.15,
        "commitment_type": "skin_in_game"
      }
    },
    "feasibility_gate": {
      "passed": true,
      "status": "green",
      "constraints": []
    },
    "viability_gate": {
      "passed": true,
      "ltv_cac_ratio": 4.0,
      "unit_economics_status": "profitable"
    }
  }
}
```

---

## Marketing → Product App Contracts

| Contract | Implementation | Status |
|----------|---------------|--------|
| Auth redirect with plan | Query param `?plan=professional` | Working |
| Shared Supabase instance | Same project, different clients | Working |

---

## Approval Workflow API

### Webhook (CrewAI → Product App)

```
POST https://app.startupai.site/api/approvals/webhook
Content-Type: application/json
Authorization: Bearer {webhook-secret}

{
  "execution_id": "uuid-of-flow-execution",
  "task_id": "uuid-of-paused-task",
  "crew_name": "governance",
  "task_name": "qa_gate_review",
  "task_output": {
    "approval_type": "stage_gate",
    "title": "Desirability Gate Approval",
    "context": {
      "project_id": "uuid",
      "evidence_summary": "...",
      "qa_score": 0.85,
      "assumptions_tested": 5,
      "assumptions_validated": 4
    },
    "recommendation": "proceed",
    "alternatives": [
      {"action": "proceed", "rationale": "Strong evidence"},
      {"action": "retry", "rationale": "Address weak areas"},
      {"action": "pivot", "rationale": "Fundamental issues"}
    ]
  }
}
```

### Resume (Product App → CrewAI)

```
POST https://startupai-...crewai.com/resume
Content-Type: application/json
Authorization: Bearer {crew-token}

{
  "execution_id": "uuid-of-flow-execution",
  "task_id": "uuid-of-paused-task",
  "human_feedback": "Approved with note: Focus on pricing validation next",
  "is_approve": true,
  "humanInputWebhook": {
    "url": "https://app.startupai.site/api/approvals/webhook",
    "authentication": {
      "strategy": "bearer",
      "token": "{webhook-secret}"
    }
  }
}
```

---

## Area 3: Policy Versioning Patterns

### Policy Selection (Internal)
```python
from startupai.tools import select_experiment_policy, record_experiment_outcome

# Select policy for experiment
policy, reason = select_experiment_policy("ad_creative")
# Returns: (PolicyVersion.YAML_BASELINE, "UCB selection: exploration bonus")

# Record outcome after experiment completes
record_experiment_outcome(
    experiment_type="ad_creative",
    policy_version=policy,
    success_score=0.85,
    metrics={"ctr": 0.032, "conversion": 0.018}
)
```

### Status Response with Policy Info
```json
{
  "status": "completed",
  "policy_version": "yaml_baseline",
  "experiment_config_source": "yaml_baseline",
  "policy_selection_reason": "UCB selection: yaml_baseline has higher confidence"
}
```

---

## Area 6: Budget Check Patterns

### Budget Check (Internal)
```python
from startupai.tools import check_spend_allowed, record_budget_override

# Pre-spend validation
result = check_spend_allowed(
    project_id="proj_123",
    requested_amount=100.0,
    budget_total=500.0,
    spent_to_date=420.0
)
# result.status: BudgetStatus.WARNING
# result.allowed: True
# result.escalation: EscalationInfo with contact details

# Record human override (if needed)
record_budget_override(
    project_id="proj_123",
    override_amount=150.0,
    rationale="Critical experiment for PMF validation"
)
```

### Decision Logging (Audit Trail)
```python
from startupai.persistence.decision_log import log_human_approval

log_human_approval(
    project_id="proj_123",
    decision_point="creative_approval",
    decision="approved",
    rationale="Landing page meets brand guidelines",
    actor_id="user_456"
)
```

---

## Area 7: Business Model Classification Patterns

### Classification (Internal)
```python
from startupai.tools import classify_from_state, get_model_for_type

# Auto-classify business model
result = classify_from_state(state)
# result.business_model_type: BusinessModelType.SAAS_B2B_SMB
# result.confidence: 0.87

# Get model-specific unit economics calculator
model = get_model_for_type(result.business_model_type)
metrics = model.calculate_metrics(input_data)
```

### Viability Response with Model Info
```json
{
  "viability_gate": {
    "passed": true,
    "business_model_type": "saas_b2b_smb",
    "ltv_cac_ratio": 4.0,
    "target_ltv_cac_ratio": 3.0,
    "payback_months": 10,
    "target_payback_months": 12,
    "unit_economics_status": "profitable",
    "model_specific_metrics": {
      "target_arpu": 99.0,
      "typical_churn": 0.05
    }
  }
}
```

---

## Aspirational Contracts (NOT IMPLEMENTED)

These were documented but do not exist yet:
- `GET /api/v1/agents/activity` - Activity feed for marketing site
- `GET /api/v1/metrics/public` - Trust metrics for marketing site

---

## Implementation Status

| Component | Status |
|-----------|--------|
| CrewAI `/kickoff` | ✅ Working |
| CrewAI `/status` | ✅ Working |
| CrewAI `/resume` | ✅ Available in CrewAI AMP |
| CrewAI webhook delivery | ✅ Available in CrewAI AMP |
| Product app unified webhook | ✅ Implemented (`/api/crewai/webhook`) |
| Product app results webhook | ✅ Implemented (`/api/crewai/results`) |
| Product app consultant webhook | ✅ Implemented (`/api/crewai/consultant`) |
| Product app approvals API | ✅ Implemented (`/api/approvals/` CRUD + webhook) |
| Activity feed API | ❌ NOT IMPLEMENTED (marketing site feature) |
| Metrics API | ❌ NOT IMPLEMENTED (marketing site feature) |

---
**Last Updated**: 2025-12-04

**Latest Changes**:
- Added Area 3 policy versioning patterns (policy selection, status response)
- Added Area 6 budget check patterns (spend validation, decision logging)
- Added Area 7 business model classification patterns (classification, viability response)
