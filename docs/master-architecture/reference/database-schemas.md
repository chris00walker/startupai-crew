---
purpose: Database schema definitions for all services
status: partially-implemented
last_reviewed: 2025-11-26
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
**Last Updated**: 2025-11-26

**Latest Changes**: Updated implementation status indicators. Approval tables and most product app tables are now deployed.
