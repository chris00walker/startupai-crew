---
purpose: Database schema definitions for all services
status: mostly-implemented
last_reviewed: 2025-11-27
---

# Database Schemas

This document consolidates all SQL schema definitions used across the StartupAI ecosystem.

> **Implementation Status**: Many tables are now deployed. See status indicators below.
> **Authoritative Spec**: `../03-validation-spec.md` contains the complete state architecture.

## Approval System Tables

**Status**: ✅ Deployed (migration `20251126000002_approval_requests.sql`)

### Approval Requests

```sql
-- Approval requests
CREATE TABLE approval_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id),
  approval_type TEXT NOT NULL,  -- 'campaign', 'spend', 'contact', etc.
  status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'rejected', 'modified'
  urgency TEXT DEFAULT 'normal', -- 'low', 'normal', 'high', 'critical'
  blocks_workflow BOOLEAN DEFAULT true,

  -- Request details
  title TEXT NOT NULL,
  description TEXT,
  context JSONB,                 -- AI's reasoning and evidence
  requested_action JSONB,        -- What AI wants to do
  alternatives JSONB,            -- Other options considered

  -- Resolution
  resolved_by UUID REFERENCES users(id),
  resolved_at TIMESTAMPTZ,
  resolution_notes TEXT,
  modifications JSONB,           -- Changes made by approver

  -- Escalation
  escalation_level INTEGER DEFAULT 0,
  escalated_to UUID REFERENCES users(id),

  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Approval Preferences

```sql
-- User delegation preferences
CREATE TABLE approval_preferences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  project_id UUID REFERENCES projects(id), -- NULL for global defaults

  approval_type TEXT NOT NULL,
  auto_approve BOOLEAN DEFAULT false,
  auto_approve_conditions JSONB,  -- e.g., {"max_spend": 50, "min_qa_score": 0.9}
  notification_channels TEXT[],   -- ['in_app', 'email', 'sms']
  escalation_contact UUID REFERENCES users(id),

  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, project_id, approval_type)
);
```

## Marketing Site Tables

**Status**: ❌ NOT DEPLOYED (marketing site still uses mock data)

### Platform Metrics

```sql
-- Aggregated platform statistics
CREATE TABLE platform_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  metric_name TEXT NOT NULL,          -- 'validations_completed', 'mvps_built', etc.
  metric_value INTEGER NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Public Activity Log

```sql
-- Anonymized recent agent activities
CREATE TABLE public_activity_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  founder_id TEXT NOT NULL,           -- 'sage', 'forge', etc.
  activity_type TEXT NOT NULL,        -- 'analysis', 'build', 'validation'
  description TEXT NOT NULL,          -- Anonymized activity description
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Founder Stats

```sql
-- Per-founder performance metrics
CREATE TABLE founder_stats (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  founder_id TEXT NOT NULL UNIQUE,
  analyses_completed INTEGER DEFAULT 0,
  accuracy_rate DECIMAL(5,2),
  avg_response_time INTERVAL,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Product App Core Tables

**Status**: ✅ Mostly Deployed (12 migrations in Supabase)

> Note: Check `frontend/src/db/schema/` in the product app for current Drizzle implementations.

### Projects

```sql
CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  name TEXT NOT NULL,
  description TEXT,
  stage TEXT DEFAULT 'desirability', -- 'desirability', 'feasibility', 'viability'
  status TEXT DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Hypotheses

```sql
CREATE TABLE hypotheses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id),
  statement TEXT NOT NULL,
  category TEXT NOT NULL,  -- 'desirability', 'feasibility', 'viability'
  priority INTEGER DEFAULT 0,
  status TEXT DEFAULT 'untested', -- 'untested', 'testing', 'validated', 'invalidated'
  evidence_needed TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Evidence

```sql
CREATE TABLE evidence (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hypothesis_id UUID REFERENCES hypotheses(id),
  experiment_id UUID REFERENCES experiments(id),
  evidence_type TEXT NOT NULL,  -- 'quantitative', 'qualitative'
  data JSONB NOT NULL,
  supports_hypothesis BOOLEAN,
  confidence_score DECIMAL(3,2),
  embedding VECTOR(1536),  -- For semantic search
  created_at TIMESTAMPTZ DEFAULT NOW(),

  -- Innovation Physics signal tracking
  signal_type TEXT CHECK (signal_type IN ('problem_resonance', 'zombie_ratio', 'commitment_type', 'cac', 'ltv', 'feasibility_status')),
  gate_type TEXT CHECK (gate_type IN ('desirability', 'feasibility', 'viability'))
);
```

### Experiments

```sql
CREATE TABLE experiments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id),
  name TEXT NOT NULL,
  description TEXT,
  experiment_type TEXT NOT NULL,  -- 'landing_page', 'ad_campaign', 'interview', etc.
  status TEXT DEFAULT 'draft', -- 'draft', 'running', 'completed'
  budget DECIMAL(10,2),
  metrics JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Entrepreneur Briefs

```sql
CREATE TABLE entrepreneur_briefs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id),
  business_idea TEXT NOT NULL,
  customer_segments JSONB,
  problem_statement TEXT,
  current_stage TEXT,
  key_assumptions JSONB,
  validation_goals JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Gate Scores

```sql
CREATE TABLE gate_scores (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id),
  gate_type TEXT NOT NULL,  -- 'desirability', 'feasibility', 'viability'
  score DECIMAL(5,2),
  criteria JSONB,
  passed BOOLEAN,
  feedback TEXT,
  reviewed_by TEXT,  -- 'guardian', 'qa_agent', etc.
  created_at TIMESTAMPTZ DEFAULT NOW(),

  -- Innovation Physics metrics
  problem_resonance DECIMAL(3,2),  -- 0.00-1.00: fraction of visitors resonating with problem
  zombie_ratio DECIMAL(3,2),       -- 0.00-1.00: fraction of interested-but-not-committed
  commitment_type TEXT CHECK (commitment_type IN ('none', 'verbal_interest', 'low_stake', 'skin_in_game')),
  evidence_strength TEXT CHECK (evidence_strength IN ('none', 'weak', 'strong')),
  feasibility_status TEXT CHECK (feasibility_status IN ('unknown', 'green', 'orange_constrained', 'red_impossible')),
  unit_economics_status TEXT CHECK (unit_economics_status IN ('unknown', 'profitable', 'marginal', 'underwater')),

  -- Unit economics metrics (for viability gates)
  cac_usd DECIMAL(10,2),
  ltv_usd DECIMAL(10,2),
  ltv_cac_ratio DECIMAL(5,2)
);
```

### Flow Executions

Tracks current state of validation flow execution for each project:

```sql
CREATE TABLE flow_executions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id) UNIQUE,  -- One active flow per project
  current_phase TEXT NOT NULL CHECK (current_phase IN ('ideation', 'desirability', 'feasibility', 'viability', 'validated', 'killed')),
  current_risk_axis TEXT CHECK (current_risk_axis IN ('desirability', 'feasibility', 'viability')),
  router_decision TEXT,  -- Last router decision (e.g., "run_desirability_experiments", "terminal_validated")
  blocking_approval_required BOOLEAN DEFAULT false,
  last_pivot_type TEXT,
  downgrade_active BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Area 3: Policy Versioning Tables

**Status**: ✅ Deployed (migration 004, 005) - 2025-11-27

### Experiment Outcomes

Stores experiment outcomes for policy versioning and A/B testing (UCB bandit).

```sql
-- Migration 004: experiment_outcomes
CREATE TABLE experiment_outcomes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL,
  experiment_id TEXT NOT NULL,
  experiment_type TEXT NOT NULL,  -- 'ad_creative', 'landing_page', 'pricing_test'
  policy_version TEXT NOT NULL,   -- 'yaml_baseline', 'retrieval_v1'

  -- Metrics
  primary_metric TEXT,            -- Name of primary success metric
  primary_value DECIMAL(10,4),    -- Value of primary metric
  metrics JSONB,                  -- All metrics: {"ctr": 0.032, "conversion": 0.018}
  success_score DECIMAL(5,4),     -- Normalized success score 0-1

  -- Tracking
  status TEXT DEFAULT 'running',  -- 'running', 'completed', 'cancelled'
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for policy performance queries
CREATE INDEX idx_experiment_outcomes_policy ON experiment_outcomes(policy_version, experiment_type);
CREATE INDEX idx_experiment_outcomes_status ON experiment_outcomes(status) WHERE status = 'completed';
```

### Policy Performance View

```sql
-- View for policy performance summary
CREATE VIEW policy_performance_summary AS
SELECT
  experiment_type,
  policy_version,
  COUNT(*) as sample_count,
  AVG(success_score) as avg_success,
  STDDEV(success_score) as stddev_success,
  MAX(completed_at) as last_completed
FROM experiment_outcomes
WHERE status = 'completed'
GROUP BY experiment_type, policy_version;
```

### Policy Weights Function

```sql
-- UCB bandit weight calculation
CREATE OR REPLACE FUNCTION get_policy_weights(
  p_experiment_type TEXT,
  p_min_samples INTEGER DEFAULT 10,
  p_exploration_bonus DECIMAL DEFAULT 0.1
)
RETURNS TABLE(
  policy_version TEXT,
  weight DECIMAL,
  sample_count INTEGER,
  avg_success DECIMAL,
  ucb_score DECIMAL
) AS $$
BEGIN
  RETURN QUERY
  WITH policy_stats AS (
    SELECT
      eo.policy_version,
      COUNT(*)::INTEGER as samples,
      AVG(eo.success_score) as mean_success,
      STDDEV(eo.success_score) as std_success
    FROM experiment_outcomes eo
    WHERE eo.experiment_type = p_experiment_type
      AND eo.status = 'completed'
    GROUP BY eo.policy_version
  ),
  total AS (
    SELECT SUM(samples) as total_samples FROM policy_stats
  )
  SELECT
    ps.policy_version,
    CASE
      WHEN ps.samples < p_min_samples THEN 1.0  -- Explore under-sampled
      ELSE ps.mean_success + p_exploration_bonus * SQRT(LN(t.total_samples) / ps.samples)
    END as weight,
    ps.samples as sample_count,
    ps.mean_success as avg_success,
    ps.mean_success + p_exploration_bonus * SQRT(LN(COALESCE(t.total_samples, 1)) / GREATEST(ps.samples, 1)) as ucb_score
  FROM policy_stats ps
  CROSS JOIN total t;
END;
$$ LANGUAGE plpgsql;
```

### Learnings Policy Version Extension

```sql
-- Migration 005: Add policy_version to learnings table
ALTER TABLE learnings
ADD COLUMN policy_version TEXT,
ADD COLUMN experiment_id TEXT,
ADD COLUMN experiment_type TEXT;

-- Index for policy-filtered learning retrieval
CREATE INDEX idx_learnings_policy ON learnings(policy_version);
```

---

## Area 6: Decision Logging Tables

**Status**: ✅ Deployed (migration 006) - 2025-11-27

### Decision Log

Stores decision rationales for audit trail and compliance.

```sql
-- Migration 006: decision_log
CREATE TABLE decision_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL,

  -- Decision context
  decision_type TEXT NOT NULL,      -- 'creative_approval', 'viability_approval', 'pivot_decision', 'budget_decision', 'policy_selection'
  decision_point TEXT NOT NULL,     -- Where in flow (e.g., 'creative_gate', 'viability_gate')
  decision TEXT NOT NULL,           -- The actual decision made
  rationale TEXT,                   -- Why this decision was made

  -- Actor
  actor_type TEXT NOT NULL,         -- 'ai_agent', 'human_founder', 'system'
  actor_id TEXT,                    -- User ID or agent name

  -- Context snapshot
  context_snapshot JSONB,           -- State at decision time

  -- Budget tracking (for budget decisions)
  budget_total DECIMAL(10,2),
  budget_spent DECIMAL(10,2),
  budget_requested DECIMAL(10,2),

  -- Audit
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_decision_log_project ON decision_log(project_id);
CREATE INDEX idx_decision_log_type ON decision_log(decision_type);
CREATE INDEX idx_decision_log_actor ON decision_log(actor_type, actor_id);
```

### Budget Decisions View

```sql
-- View for budget decision summary
CREATE VIEW budget_decisions_summary AS
SELECT
  project_id,
  COUNT(*) as total_budget_decisions,
  SUM(CASE WHEN decision = 'approved' THEN 1 ELSE 0 END) as approved_count,
  SUM(CASE WHEN decision = 'rejected' THEN 1 ELSE 0 END) as rejected_count,
  SUM(CASE WHEN decision = 'override' THEN 1 ELSE 0 END) as override_count,
  MAX(budget_spent) as max_spent,
  AVG(budget_spent / NULLIF(budget_total, 0)) as avg_utilization
FROM decision_log
WHERE decision_type = 'budget_decision'
GROUP BY project_id;
```

### Override Audit View

```sql
-- View for tracking human overrides
CREATE VIEW override_audit AS
SELECT
  dl.id,
  dl.project_id,
  dl.decision_type,
  dl.decision,
  dl.rationale,
  dl.actor_id,
  dl.budget_total,
  dl.budget_spent,
  dl.budget_requested,
  dl.created_at
FROM decision_log dl
WHERE dl.actor_type = 'human_founder'
  AND dl.decision IN ('override', 'approved_over_limit')
ORDER BY dl.created_at DESC;
```

### Log Decision Function

```sql
-- Convenience function for logging decisions
CREATE OR REPLACE FUNCTION log_decision(
  p_project_id UUID,
  p_decision_type TEXT,
  p_decision_point TEXT,
  p_decision TEXT,
  p_rationale TEXT,
  p_actor_type TEXT,
  p_actor_id TEXT DEFAULT NULL,
  p_context JSONB DEFAULT NULL,
  p_budget_total DECIMAL DEFAULT NULL,
  p_budget_spent DECIMAL DEFAULT NULL,
  p_budget_requested DECIMAL DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
  v_id UUID;
BEGIN
  INSERT INTO decision_log (
    project_id, decision_type, decision_point, decision, rationale,
    actor_type, actor_id, context_snapshot,
    budget_total, budget_spent, budget_requested
  ) VALUES (
    p_project_id, p_decision_type, p_decision_point, p_decision, p_rationale,
    p_actor_type, p_actor_id, p_context,
    p_budget_total, p_budget_spent, p_budget_requested
  )
  RETURNING id INTO v_id;

  RETURN v_id;
END;
$$ LANGUAGE plpgsql;
```

---

## Indexes

Recommended indexes for performance:

```sql
-- Approval queries
CREATE INDEX idx_approval_requests_project ON approval_requests(project_id);
CREATE INDEX idx_approval_requests_status ON approval_requests(status) WHERE status = 'pending';

-- Activity queries
CREATE INDEX idx_activity_log_founder ON public_activity_log(founder_id);
CREATE INDEX idx_activity_log_created ON public_activity_log(created_at DESC);

-- Evidence semantic search
CREATE INDEX idx_evidence_embedding ON evidence USING ivfflat (embedding vector_cosine_ops);

-- Hypothesis lookup
CREATE INDEX idx_hypotheses_project ON hypotheses(project_id);
CREATE INDEX idx_hypotheses_status ON hypotheses(status);
```

---

## Related Documents

- [approval-workflows.md](./approval-workflows.md) - How approvals work
- [product-artifacts.md](./product-artifacts.md) - Canvas architecture
- [api-contracts.md](./api-contracts.md) - API specifications
- [../03-validation-spec.md](../03-validation-spec.md) - Authoritative technical blueprint

---
**Last Updated**: 2025-11-27

**Latest Changes (2025-11-27 - Migrations Deployed)**:
- All CrewAI migrations deployed to Supabase: 001, 002, 004, 005, 006
- Updated status indicators from "Ready" to "Deployed"

**Previous Changes**:
- Added Area 3 tables: `experiment_outcomes`, `policy_performance_summary` view, `get_policy_weights()` function
- Added Area 6 tables: `decision_log`, `budget_decisions_summary` view, `override_audit` view, `log_decision()` function
- Added policy_version extension to learnings table (migration 005)
