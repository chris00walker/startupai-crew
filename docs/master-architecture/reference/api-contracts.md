# API Contracts

All API endpoints, webhooks, and payloads for StartupAI services.

## CrewAI AMP Endpoints

**Base URL**: `https://startupai-b4d5c1dd-27e2-4163-b9fb-a18ca06ca-4f4192a6.crewai.com`

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
| Product app webhook receiver | ❌ NOT IMPLEMENTED |
| Activity feed API | ❌ NOT IMPLEMENTED |
| Metrics API | ❌ NOT IMPLEMENTED |

---
**Last Updated**: 2025-11-22

**Latest Changes**: Added Innovation Physics signal fields to status response (evidence_strength, pivot_recommendation, commitment_type, unit_economics_status).
