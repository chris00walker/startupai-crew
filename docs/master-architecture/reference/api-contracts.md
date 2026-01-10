---
purpose: API endpoint contracts for all StartupAI services
status: active
last_reviewed: 2026-01-08
vpd_compliance: true
---

# API Contracts

All API endpoints, webhooks, and payloads for StartupAI services.

> **VPD Framework**: This API implements the Value Proposition Design (VPD) framework by Osterwalder/Pigneur. See phase documents for authoritative specifications:
> - [04-phase-0-onboarding.md](../04-phase-0-onboarding.md) - Founder's Brief capture
> - [05-phase-1-vpc-discovery.md](../05-phase-1-vpc-discovery.md) - VPC Discovery
> - [06-phase-2-desirability.md](../06-phase-2-desirability.md) - Desirability validation
> - [07-phase-3-feasibility.md](../07-phase-3-feasibility.md) - Feasibility validation
> - [08-phase-4-viability.md](../08-phase-4-viability.md) - Viability validation

---

## Modal Serverless API (Target Architecture)

> **Status**: Target architecture per [ADR-002](../../adr/002-modal-serverless-migration.md). Replaces CrewAI AMP endpoints.

**Base URL**: `https://startupai-crew--{endpoint}.modal.run`

### Endpoints

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/kickoff` | POST | Start validation run | Planned |
| `/status/{run_id}` | GET | Check progress (reads Supabase) | Planned |
| `/hitl/approve` | POST | Resume after human approval | Planned |

### Kickoff Request (Modal)

```bash
curl -X POST https://startupai-crew--kickoff.modal.run \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "uuid",
    "user_id": "uuid",
    "entrepreneur_input": "Business idea description..."
  }'
```

### Kickoff Response

```json
{
  "run_id": "uuid",
  "status": "started",
  "message": "Validation run initiated"
}
```

**HTTP Status**: 202 Accepted (async processing)

### Status Request (Modal)

```bash
curl https://startupai-crew--status.modal.run/{run_id} \
  -H "Authorization: Bearer {token}"
```

### Status Response

```json
{
  "run_id": "uuid",
  "status": "running|paused|completed|failed",
  "current_phase": 1,
  "progress": [
    {
      "phase": 0,
      "crew": "OnboardingCrew",
      "task": "founder_interview",
      "status": "completed",
      "progress_pct": 100
    },
    {
      "phase": 1,
      "crew": "DiscoveryCrew",
      "task": "segment_discovery",
      "status": "in_progress",
      "progress_pct": 45
    }
  ],
  "hitl_pending": null,
  "started_at": "2026-01-08T10:00:00Z",
  "updated_at": "2026-01-08T10:15:00Z"
}
```

### HITL Approve Request (Modal)

```bash
curl -X POST https://startupai-crew--hitl-approve.modal.run \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "run_id": "uuid",
    "checkpoint": "approve_founders_brief",
    "decision": "approved",
    "feedback": "Optional human feedback"
  }'
```

### HITL Approve Response

```json
{
  "status": "resumed",
  "next_phase": 1,
  "message": "Validation resumed from checkpoint"
}
```

### Authentication

All Modal endpoints require bearer token authentication:
```
Authorization: Bearer {STARTUPAI_WEBHOOK_BEARER_TOKEN}
```

---

## Phase 0: Onboarding API

Phase 0 captures the Founder's Brief through structured interview and validation.

### Endpoints

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/interview/start` | POST | Start founder interview session | Planned |
| `/interview/continue` | POST | Continue multi-turn interview | Planned |
| `/brief/create` | POST | Create new Founder's Brief | Planned |
| `/brief/{brief_id}` | GET | Retrieve Founder's Brief | Planned |
| `/brief/{brief_id}` | PUT | Update Founder's Brief | Planned |
| `/brief/{brief_id}/approve` | POST | Founder approves brief → Phase 1 | Planned |

### Interview Start Request
```bash
curl -X POST https://startupai-...crewai.com/interview/start \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "founder_input": "Initial business idea description...",
    "project_id": "uuid"
  }'
```

### Interview Continue Request
```bash
curl -X POST https://startupai-...crewai.com/interview/continue \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "uuid",
    "response": "Founder response to interview question..."
  }'
```

### Founder's Brief Response
```json
{
  "brief_id": "uuid",
  "project_id": "uuid",
  "status": "draft|pending_approval|approved",
  "founders_brief": {
    "the_idea": {
      "concept": "One-sentence description",
      "one_liner": "Elevator pitch"
    },
    "problem_hypothesis": {
      "who": "Target customer description",
      "what": "Problem they face",
      "current_alternatives": ["Alternative 1", "Alternative 2"]
    },
    "customer_hypothesis": {
      "segment": "Primary customer segment",
      "characteristics": ["Characteristic 1", "Characteristic 2"]
    },
    "solution_hypothesis": {
      "approach": "How the solution works",
      "key_features": ["Feature 1", "Feature 2"]
    },
    "key_assumptions": [
      {"assumption": "...", "risk_level": "high|medium|low", "testable": true}
    ],
    "success_criteria": {
      "problem_resonance_target": 0.50,
      "zombie_ratio_max": 0.30,
      "fit_score_target": 70
    }
  },
  "qa_report": {
    "concept_legitimacy": "pass|fail",
    "intent_verification": "pass|fail",
    "issues": []
  }
}
```

### Create Brief Request
```bash
curl -X POST https://startupai-...crewai.com/brief/create \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "uuid",
    "concept": "AI-powered validation for startup ideas",
    "one_liner": "Stop building products nobody wants",
    "target_who": "Early-stage SaaS founders",
    "target_what": "Wasting months building unvalidated products",
    "current_alternatives": ["Customer interviews", "Surveys", "Guesswork"],
    "customer_segment": "Technical founders at seed stage",
    "customer_characteristics": ["Technical background", "Limited time", "Bootstrap budget"],
    "solution_approach": "Automated validation experiments with AI analysis",
    "key_features": ["Landing page generation", "Ad testing", "Evidence synthesis"],
    "key_assumptions": [
      {"assumption": "Founders will trust AI recommendations", "risk_level": "high", "testable": true},
      {"assumption": "Ad testing provides reliable demand signal", "risk_level": "medium", "testable": true}
    ]
  }'
```

### Update Brief Request
```bash
curl -X PUT https://startupai-...crewai.com/brief/{brief_id} \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "concept": "Updated concept description",
    "key_assumptions": [
      {"assumption": "Updated assumption", "risk_level": "high", "testable": true}
    ]
  }'
```

### Brief Approval Request
```bash
curl -X POST https://startupai-...crewai.com/brief/{brief_id}/approve \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "approval_decision": "approve|reject|revise",
    "feedback": "Optional founder feedback"
  }'
```

---

## Phase 1+: Validation API (CrewAI AMP Endpoints)

> **⚠️ DEPRECATED**: These AMP endpoints are being replaced by Modal serverless. See [Modal Serverless API](#modal-serverless-api-target-architecture) above and [ADR-002](../../adr/002-modal-serverless-migration.md) for migration details.

**Base URL**: `https://startupai-6b1e5c4d-e708-4921-be55-08fcb0d1e-922bcddb.crewai.com`

### Working Endpoints (DEPRECATED)

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
    "founder_input": "Business idea description...",
    "brief_id": "uuid-of-approved-founders-brief"
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
    "value_proposition_canvas": {
      "customer_profile": {
        "customer_jobs": [
          {
            "id": "job_uuid",
            "job_statement": "When [situation], I want to [motivation] so I can [outcome]",
            "job_type": "functional|social|emotional|supporting",
            "priority": 1,
            "validation_status": "validated|invalidated|untested",
            "confidence_score": 0.85,
            "supporting_experiments": ["exp_uuid_1", "exp_uuid_2"]
          }
        ],
        "pains": [
          {
            "id": "pain_uuid",
            "pain_statement": "Description of customer pain",
            "severity": "extreme|severe|moderate|mild",
            "priority": 1,
            "validation_status": "validated|invalidated|untested",
            "confidence_score": 0.78,
            "supporting_experiments": ["exp_uuid_3"]
          }
        ],
        "gains": [
          {
            "id": "gain_uuid",
            "gain_statement": "Description of desired gain",
            "relevance": "essential|nice_to_have|unexpected",
            "priority": 1,
            "validation_status": "validated|invalidated|untested",
            "confidence_score": 0.72,
            "supporting_experiments": ["exp_uuid_4"]
          }
        ]
      },
      "value_map": {
        "products_and_services": [
          {
            "id": "product_uuid",
            "name": "Product or service name",
            "description": "What it does",
            "addresses_jobs": ["job_uuid"]
          }
        ],
        "pain_relievers": [
          {
            "id": "reliever_uuid",
            "description": "How it relieves pain",
            "addresses_pain": "pain_uuid",
            "effectiveness": "eliminates|reduces|none",
            "validation_status": "validated|invalidated|untested"
          }
        ],
        "gain_creators": [
          {
            "id": "creator_uuid",
            "description": "How it creates gain",
            "addresses_gain": "gain_uuid",
            "effectiveness": "exceeds|meets|misses",
            "validation_status": "validated|invalidated|untested"
          }
        ]
      },
      "fit_assessment": {
        "fit_score": 72,
        "fit_status": "strong|moderate|weak|none",
        "profile_completeness": 0.85,
        "value_map_coverage": 0.78,
        "evidence_strength": "strong|weak|none"
      }
    },
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

## Phase 1: VPC Canvas API

Endpoints for managing Value Proposition Canvas during Phase 1 discovery.

### Endpoints

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/vpc/{project_id}` | GET | Get current VPC state | Planned |
| `/vpc/{project_id}/profile` | GET | Get Customer Profile elements | Planned |
| `/vpc/{project_id}/profile` | POST | Add/upsert Customer Profile element | Planned |
| `/vpc/{project_id}/valuemap` | GET | Get Value Map elements | Planned |
| `/vpc/{project_id}/valuemap` | POST | Add/upsert Value Map element | Planned |
| `/vpc/{project_id}/fit` | GET | Get current fit assessment | Planned |
| `/vpc/{project_id}/fit` | POST | Calculate/recalculate fit score | Planned |
| `/experiments` | POST | Record experiment result | Planned |
| `/experiments/{project_id}` | GET | Get experiment history | Planned |
| `/experiments/test-card` | POST | Create TBI Test Card | Planned |
| `/experiments/learning-card` | POST | Record TBI Learning Card | Planned |

### Get Customer Profile Request
```bash
curl -X GET https://startupai-...crewai.com/vpc/{project_id}/profile \
  -H "Authorization: Bearer {token}"
```

### Get Customer Profile Response
```json
{
  "project_id": "uuid",
  "jobs": [
    {
      "id": "uuid",
      "job_statement": "When [situation], I want to [motivation] so I can [outcome]",
      "job_type": "functional|social|emotional|supporting",
      "priority": 1,
      "importance_score": 4.5,
      "validation_status": "validated|invalidated|untested",
      "confidence_score": 0.85,
      "evidence_count": 3
    }
  ],
  "pains": [
    {
      "id": "uuid",
      "element_text": "Pain description",
      "pain_severity": "extreme|severe|moderate|mild",
      "priority": 1,
      "validation_status": "validated",
      "confidence_score": 0.78
    }
  ],
  "gains": [
    {
      "id": "uuid",
      "element_text": "Gain description",
      "gain_relevance": "essential|expected|nice_to_have|unexpected",
      "priority": 1,
      "validation_status": "untested",
      "confidence_score": null
    }
  ]
}
```

### Add/Upsert Customer Profile Element Request
```bash
curl -X POST https://startupai-...crewai.com/vpc/{project_id}/profile \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "element_type": "job|pain|gain",
    "element": {
      "id": "uuid (optional, for upsert)",
      "element_text": "Element statement",
      "job_type": "functional (for jobs only)",
      "job_statement": "When [situation], I want to [motivation] so I can [outcome] (for jobs)",
      "pain_severity": "extreme (for pains only)",
      "gain_relevance": "essential (for gains only)",
      "priority": 1,
      "validation_status": "validated|invalidated|untested",
      "confidence_score": 0.85
    },
    "evidence_source": {
      "experiment_id": "exp_uuid",
      "evidence_type": "interview|observation|cta_test|landing_page",
      "evidence_strength": 4
    }
  }'
```

### Get Value Map Request
```bash
curl -X GET https://startupai-...crewai.com/vpc/{project_id}/valuemap \
  -H "Authorization: Bearer {token}"
```

### Get Value Map Response
```json
{
  "project_id": "uuid",
  "products_services": [
    {
      "id": "uuid",
      "element_text": "Product or service name",
      "description": "What it does",
      "addresses_jobs": ["job_uuid_1", "job_uuid_2"],
      "validation_status": "validated"
    }
  ],
  "pain_relievers": [
    {
      "id": "uuid",
      "element_text": "How it relieves pain",
      "addresses_profile_element": "pain_uuid",
      "effectiveness": "eliminates|reduces|none",
      "validation_status": "validated",
      "confidence_score": 0.82
    }
  ],
  "gain_creators": [
    {
      "id": "uuid",
      "element_text": "How it creates gain",
      "addresses_profile_element": "gain_uuid",
      "effectiveness": "exceeds|meets|misses",
      "validation_status": "untested"
    }
  ]
}
```

### Add/Upsert Value Map Element Request
```bash
curl -X POST https://startupai-...crewai.com/vpc/{project_id}/valuemap \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "element_type": "product_service|pain_reliever|gain_creator",
    "element": {
      "id": "uuid (optional, for upsert)",
      "element_text": "Element description",
      "description": "Detailed description (for products/services)",
      "addresses_profile_element": "uuid of job/pain/gain being addressed",
      "effectiveness": "eliminates|reduces|none|exceeds|meets|misses",
      "validation_status": "validated|invalidated|untested",
      "confidence_score": 0.85
    }
  }'
```

### Calculate Fit Score Request
```bash
curl -X POST https://startupai-...crewai.com/vpc/{project_id}/fit \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "include_wtp": true,
    "recalculate": true
  }'
```

### Record Experiment Result
```bash
curl -X POST https://startupai-...crewai.com/experiments \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "uuid",
    "experiment_type": "customer_interview|landing_page|ad_test|prototype_test|price_test",
    "tbi_experiment_id": "T1.1",
    "hypothesis_tested": "Customers prioritize X over Y",
    "test_card": {
      "hypothesis": "We believe...",
      "test": "To verify, we will...",
      "metric": "We measure...",
      "criteria": "We are right if..."
    },
    "learning_card": {
      "observation": "We observed...",
      "learning": "From that we learned...",
      "decisions_actions": "Therefore we will..."
    },
    "result": {
      "passed": true,
      "confidence": 0.85,
      "sample_size": 25,
      "evidence_strength": 4,
      "say_vs_do": "do"
    },
    "vpc_updates": [
      {"element_type": "job", "element_id": "uuid", "new_status": "validated"}
    ]
  }'
```

### Create Test Card Request (TBI Framework)
```bash
curl -X POST https://startupai-...crewai.com/experiments/test-card \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "uuid",
    "tbi_experiment_id": "T1.1",
    "hypothesis": "We believe that early-stage SaaS founders will sign up for waitlist because they struggle with customer validation",
    "test_description": "Landing page with 3-step value prop and email capture",
    "metric": "Conversion rate (signups / unique visitors)",
    "criteria": "5% conversion rate with minimum 500 visitors",
    "cost": 500.00,
    "duration_days": 7,
    "reliability": "medium",
    "tests_assumption": "Founders will trust AI recommendations",
    "tests_profile_element": "job_uuid or pain_uuid",
    "evidence_type": "do",
    "evidence_strength": 3
  }'
```

### Test Card Response
```json
{
  "test_card_id": "uuid",
  "project_id": "uuid",
  "status": "draft|approved|running|completed",
  "tbi_experiment_id": "T1.1",
  "hypothesis": "We believe...",
  "test_description": "...",
  "metric": "...",
  "criteria": "...",
  "created_at": "2026-01-06T12:00:00Z"
}
```

### Create Learning Card Request (TBI Framework)
```bash
curl -X POST https://startupai-...crewai.com/experiments/learning-card \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "test_card_id": "uuid",
    "project_id": "uuid",
    "observation": "We observed 523 unique visitors with 31 signups (5.9% conversion rate)",
    "learning": "Founders respond strongly to \"save time\" messaging; mobile conversion 2x lower than desktop",
    "decisions_actions": "Run A/B test on pricing page with time-saving emphasis",
    "passed": true,
    "confidence": 0.85,
    "sample_size": 523,
    "vpc_updates": [
      {"element_type": "job", "element_id": "uuid", "new_status": "validated", "new_confidence": 0.85}
    ]
  }'
```

### Learning Card Response
```json
{
  "learning_card_id": "uuid",
  "test_card_id": "uuid",
  "project_id": "uuid",
  "observation": "...",
  "learning": "...",
  "decisions_actions": "...",
  "passed": true,
  "confidence": 0.85,
  "sample_size": 523,
  "vpc_updates_applied": 1,
  "created_at": "2026-01-06T12:00:00Z"
}
```

### Fit Assessment Response
```json
{
  "project_id": "uuid",
  "fit_score": 72,
  "fit_status": "moderate",
  "gate_ready": true,
  "profile_metrics": {
    "jobs_validated": 3,
    "jobs_total": 4,
    "pains_validated": 5,
    "pains_total": 6,
    "gains_validated": 2,
    "gains_total": 3
  },
  "value_map_metrics": {
    "pains_addressed": 5,
    "pains_total": 6,
    "gains_addressed": 2,
    "gains_total": 3
  },
  "experiment_summary": {
    "total_experiments": 12,
    "passed": 9,
    "failed": 2,
    "inconclusive": 1
  },
  "next_recommended_action": "approve_vpc_completion|run_more_experiments|segment_pivot"
}
```

---

## Aspirational Contracts (NOT IMPLEMENTED)

These were documented but do not exist yet:
- `GET /api/v1/agents/activity` - Activity feed for marketing site
- `GET /api/v1/metrics/public` - Trust metrics for marketing site

---

## Implementation Status

### Phase 0: Onboarding API
| Component | Status |
|-----------|--------|
| `/interview/start` | ⏳ Planned |
| `/interview/continue` | ⏳ Planned |
| `/brief/create` | ⏳ Planned |
| `/brief/{id}` GET | ⏳ Planned |
| `/brief/{id}` PUT | ⏳ Planned |
| `/brief/{id}/approve` | ⏳ Planned |

### Phase 1+: Validation API
| Component | Status |
|-----------|--------|
| CrewAI `/kickoff` | ✅ Working |
| CrewAI `/status` | ✅ Working |
| CrewAI `/resume` | ✅ Available in CrewAI AMP |
| CrewAI webhook delivery | ✅ Available in CrewAI AMP |

### Phase 1: VPC Canvas API
| Component | Status |
|-----------|--------|
| `/vpc/{project_id}` GET | ⏳ Planned |
| `/vpc/{project_id}/profile` GET | ⏳ Planned |
| `/vpc/{project_id}/profile` POST | ⏳ Planned |
| `/vpc/{project_id}/valuemap` GET | ⏳ Planned |
| `/vpc/{project_id}/valuemap` POST | ⏳ Planned |
| `/vpc/{project_id}/fit` GET | ⏳ Planned |
| `/vpc/{project_id}/fit` POST | ⏳ Planned |
| `/experiments` POST | ⏳ Planned |
| `/experiments/{project_id}` GET | ⏳ Planned |
| `/experiments/test-card` POST | ⏳ Planned |
| `/experiments/learning-card` POST | ⏳ Planned |

### Product App Integration
| Component | Status |
|-----------|--------|
| Product app unified webhook | ✅ Implemented (`/api/crewai/webhook`) |
| Product app results webhook | ✅ Implemented (`/api/crewai/results`) |
| Product app consultant webhook | ✅ Implemented (`/api/crewai/consultant`) |
| Product app approvals API | ✅ Implemented (`/api/approvals/` CRUD + webhook) |
| Activity feed API | ❌ NOT IMPLEMENTED (marketing site feature) |
| Metrics API | ❌ NOT IMPLEMENTED (marketing site feature) |

### Modal Serverless API
| Component | Status |
|-----------|--------|
| Modal `/kickoff` | ⏳ Planned |
| Modal `/status/{run_id}` | ⏳ Planned |
| Modal `/hitl/approve` | ⏳ Planned |

---

## Related Documents

- [ADR-002: Modal Serverless Migration](../../adr/002-modal-serverless-migration.md) - Architecture decision
- [database-schemas.md](./database-schemas.md) - Modal tables (validation_runs, validation_progress, hitl_requests)
- [modal-configuration.md](./modal-configuration.md) - Modal platform configuration
- [approval-workflows.md](./approval-workflows.md) - HITL checkpoint patterns
- [04-phase-0-onboarding.md](../04-phase-0-onboarding.md) - Phase 0 specification
- [05-phase-1-vpc-discovery.md](../05-phase-1-vpc-discovery.md) - Phase 1 specification

---
**Last Updated**: 2026-01-08

**Latest Changes (2026-01-08 - Modal migration alignment)**:
- Fixed cross-references to point to phase documents (04-08) instead of archived specs
- Added Modal Serverless API section with 3 endpoints: `/kickoff`, `/status/{run_id}`, `/hitl/approve`
- Marked AMP endpoints as DEPRECATED
- Added Modal Implementation Status section
- Added Related Documents section with links to ADR-002 and phase docs

**Previous Changes (2026-01-06 - EVOLUTION-PLAN alignment)**:
- Added `/brief/create` POST endpoint for creating Founder's Brief
- Added `/brief/{id}` PUT endpoint for updating Founder's Brief
- Updated `/brief/{id}/approve` path format (was `/brief/approve`)
- Expanded Phase 1 VPC Canvas API with GET/POST patterns:
  - `/vpc/{project_id}/profile` GET/POST (was PUT only)
  - `/vpc/{project_id}/valuemap` GET/POST (was value-map PUT only)
  - `/vpc/{project_id}/fit` GET/POST (added calculate endpoint)
- Added TBI Framework experiment endpoints:
  - `/experiments/test-card` POST with full Test Card schema
  - `/experiments/learning-card` POST with full Learning Card schema
- Added request/response examples for all new endpoints
- Updated Implementation Status with complete endpoint list

**Previous Changes (2026-01-05)**:
- Added Phase 0 Onboarding API (interview, brief, approval endpoints)
- Added Phase 1 VPC Canvas API (profile, value-map, experiments endpoints)
- Expanded VPC schema with VPD framework fields (Jobs/Pains/Gains, Pain Relievers/Gain Creators)
- Renamed `entrepreneur_input` → `founder_input`
- Added Test Card / Learning Card experiment tracking
- Updated implementation status by phase
