# Cross-Repo Testing Contracts

This document defines the testing responsibilities and contracts between the CrewAI backend and the Product App.

## Overview

The StartupAI ecosystem spans two repositories that communicate via webhooks:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATA FLOW                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  CrewAI Backend                 →  Product App                              │
│  (startupai-crew)                  (app.startupai.site)                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Flow executes                  4. Webhook received                      │
│  2. Generates deliverables         5. Parsed & validated                    │
│  3. POST to webhook ──────────→    6. Persisted to Supabase                 │
│                                    7. Dashboard displays                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Testing Responsibilities

### CrewAI Backend (this repo) Verifies:

| Test | File | What It Verifies |
|------|------|------------------|
| Webhook HTTP delivery | `tests/test_webhook_delivery.py` | POST is made with correct URL, headers, timeout |
| Payload structure | `tests/test_webhook_delivery.py` | Payload matches `FounderValidationPayload` contract |
| Evidence fields | `tests/test_webhook_delivery.py` | All `gate_scores` fields present (problem_resonance, cac, ltv, etc.) |
| Error handling | `tests/test_webhook_delivery.py` | Timeouts and failures handled gracefully |
| Contract schema | `src/startupai/webhooks/contracts.py` | Pydantic models for payload validation |

### Product App (app.startupai.site) Must Verify:

| Test | Suggested File | What It Should Verify |
|------|----------------|----------------------|
| Webhook receipt | `__tests__/api/crewai-webhook.test.ts` | Handler parses payload correctly |
| Persistence | `__tests__/api/crewai-webhook.test.ts` | Data written to all tables |
| Reports table | `__tests__/api/crewai-webhook.test.ts` | validation_report → reports |
| Evidence table | `__tests__/api/crewai-webhook.test.ts` | evidence.* → evidence (3 rows) |
| Gate scores table | `__tests__/api/crewai-webhook.test.ts` | evidence metrics → gate_scores (3 rows) |
| Dashboard queries | `__tests__/dashboard/*.test.tsx` | UI displays persisted data |

## Webhook Payload Contract

### Endpoint
```
POST /api/crewai/webhook
Authorization: Bearer {STARTUPAI_WEBHOOK_BEARER_TOKEN}
Content-Type: application/json
```

### Payload Schema (Python)

See: `src/startupai/webhooks/contracts.py`

```python
class FounderValidationPayload(BaseModel):
    flow_type: str = "founder_validation"
    project_id: str
    user_id: str
    kickoff_id: str
    session_id: Optional[str]
    validation_report: ValidationReportPayload
    value_proposition_canvas: Dict[str, Any]
    evidence: EvidencePayload
    qa_report: Optional[QAReportPayload]
    completed_at: str  # ISO timestamp
```

### Equivalent TypeScript/Zod Schema

The product app should implement matching Zod schemas:

```typescript
// lib/contracts/crewai-webhook.ts
import { z } from 'zod';

export const DesirabilityEvidenceSchema = z.object({
  problem_resonance: z.number().min(0).max(1),
  zombie_ratio: z.number().min(0).max(1),
  commitment_depth: z.enum(['none', 'verbal', 'skin_in_game']),
  conversion_rate: z.number().min(0).max(1),
  traffic_quality: z.enum(['High', 'Medium', 'Low']).optional(),
  key_learnings: z.array(z.string()),
  tested_segments: z.array(z.string()),
  impressions: z.number(),
  clicks: z.number(),
  signups: z.number(),
  spend_usd: z.number(),
});

export const FeasibilityEvidenceSchema = z.object({
  core_features_feasible: z.record(z.string()),
  technical_risks: z.array(z.string()),
  skill_requirements: z.array(z.string()),
  estimated_effort: z.string().optional(),
  downgrade_required: z.boolean(),
  downgrade_impact: z.string().optional(),
  removed_features: z.array(z.string()),
  alternative_approaches: z.array(z.string()),
  monthly_cost_estimate_usd: z.number(),
});

export const ViabilityEvidenceSchema = z.object({
  cac: z.number().min(0),
  ltv: z.number().min(0),
  ltv_cac_ratio: z.number().min(0),
  gross_margin: z.number().min(0).max(1),
  payback_months: z.number().min(0),
  break_even_customers: z.number().int().min(0),
  tam_usd: z.number().min(0),
  market_share_target: z.number().min(0).max(1),
  viability_assessment: z.string().optional(),
});

export const FounderValidationPayloadSchema = z.object({
  flow_type: z.literal('founder_validation'),
  project_id: z.string().uuid(),
  user_id: z.string().uuid(),
  kickoff_id: z.string(),
  session_id: z.string().optional().nullable(),
  validation_report: z.object({
    id: z.string(),
    business_idea: z.string().optional(),
    validation_outcome: z.string().optional(),
    evidence_summary: z.string().optional(),
    pivot_recommendation: z.string().optional(),
    next_steps: z.array(z.string()),
  }),
  value_proposition_canvas: z.record(z.any()),
  evidence: z.object({
    desirability: DesirabilityEvidenceSchema.optional().nullable(),
    feasibility: FeasibilityEvidenceSchema.optional().nullable(),
    viability: ViabilityEvidenceSchema.optional().nullable(),
  }),
  qa_report: z.object({
    status: z.enum(['passed', 'failed', 'conditional', 'escalated']),
    framework_compliance: z.boolean(),
    logical_consistency: z.boolean(),
    completeness: z.boolean(),
    specific_issues: z.array(z.string()),
    required_changes: z.array(z.string()),
    confidence_score: z.number().min(0).max(1),
  }).optional().nullable(),
  completed_at: z.string(),
});
```

## Database Table Mapping

### From Webhook Payload to Tables

| Payload Field | Table | Column(s) |
|---------------|-------|-----------|
| `validation_report.*` | `reports` | All columns |
| `evidence.desirability.*` | `evidence` | phase='desirability', data=JSON |
| `evidence.feasibility.*` | `evidence` | phase='feasibility', data=JSON |
| `evidence.viability.*` | `evidence` | phase='viability', data=JSON |
| Full payload | `crewai_validation_states` | All evidence fields (cac, ltv, problem_resonance, zombie_ratio, etc.) |

**Architecture Note**: The `gate_scores` table concept was superseded by `crewai_validation_states` which stores all validation data in a single row per project. The dashboard uses `useCrewAIState` hook to read from this table.

### Expected Webhook Handler Logic

```typescript
// Product app: /api/crewai/webhook/route.ts

export async function POST(req: Request) {
  const payload = FounderValidationPayloadSchema.parse(await req.json());

  // 1. Write to reports table
  const { data: report } = await supabase
    .from('reports')
    .insert({
      project_id: payload.project_id,
      user_id: payload.user_id,
      business_idea: payload.validation_report.business_idea,
      validation_outcome: payload.validation_report.validation_outcome,
      evidence_summary: payload.validation_report.evidence_summary,
      pivot_recommendation: payload.validation_report.pivot_recommendation,
      next_steps: payload.validation_report.next_steps,
      completed_at: payload.completed_at,
    })
    .select()
    .single();

  // 2. Write to evidence table (3 rows)
  const evidenceRows = [];
  if (payload.evidence.desirability) {
    evidenceRows.push({
      project_id: payload.project_id,
      report_id: report.id,
      phase: 'desirability',
      data: payload.evidence.desirability,
    });
  }
  // ... feasibility, viability

  await supabase.from('evidence').insert(evidenceRows);

  // 3. Write to gate_scores table (3 rows)
  const gateScores = [];
  if (payload.evidence.desirability) {
    gateScores.push({
      project_id: payload.project_id,
      gate_type: 'desirability',
      problem_resonance: payload.evidence.desirability.problem_resonance,
      zombie_ratio: payload.evidence.desirability.zombie_ratio,
      commitment_type: payload.evidence.desirability.commitment_depth,
    });
  }
  if (payload.evidence.viability) {
    gateScores.push({
      project_id: payload.project_id,
      gate_type: 'viability',
      cac_usd: payload.evidence.viability.cac,
      ltv_usd: payload.evidence.viability.ltv,
      ltv_cac_ratio: payload.evidence.viability.ltv_cac_ratio,
    });
  }
  // ... feasibility

  await supabase.from('gate_scores').insert(gateScores);

  return Response.json({
    report_id: report.id,
    evidence_created: evidenceRows.length,
    gate_scores_created: gateScores.length,
  });
}
```

## Verification Checklist

### Pre-Release (Both Repos)

#### CrewAI Backend
- [ ] `pytest tests/test_webhook_delivery.py` passes
- [ ] Payload includes all evidence fields
- [ ] Contract schema matches product app expectations

#### Product App
- [ ] Webhook handler tests pass
- [ ] All 3 evidence phases written to `evidence` table
- [ ] All 3 gate types written to `gate_scores` table
- [ ] Dashboard displays data from all tables

### Full E2E Verification

```bash
# 1. Start from CrewAI repo
pytest tests/test_webhook_delivery.py -v

# 2. Run manual E2E test
./scripts/test_e2e_webhook.sh --full

# 3. Verify in Supabase
# SELECT * FROM reports WHERE project_id = 'test-project' ORDER BY created_at DESC LIMIT 1;
# SELECT * FROM evidence WHERE project_id = 'test-project';
# SELECT * FROM gate_scores WHERE project_id = 'test-project';

# 4. Verify in dashboard
# Open https://app.startupai.site/dashboard/projects/test-project
# Confirm all sections display data
```

## Troubleshooting

### Webhook Not Received

1. Check CrewAI logs for HTTP errors
2. Verify `STARTUPAI_WEBHOOK_URL` is set correctly
3. Verify `STARTUPAI_WEBHOOK_BEARER_TOKEN` matches product app

### Data Missing in Tables

1. Check product app webhook handler logs
2. Verify Zod schema matches Pydantic schema
3. Check for RLS policies blocking inserts

### Gate Scores Empty

1. Verify product app extracts evidence fields correctly
2. Check that `gate_scores` persistence logic exists
3. Confirm INSERT to `gate_scores` table in handler

## Changelog

| Date | Change |
|------|--------|
| 2024-12-02 | Initial contract documentation |
