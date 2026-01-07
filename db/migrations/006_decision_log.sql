-- ============================================
-- Migration 006: Decision Log Table
-- ============================================
-- Stores decision rationale for audit trail and HITL workflows.
-- Supports budget guardrails with escalation/override tracking.
--
-- Run this migration after 005_add_policy_version_to_learnings.sql
-- ============================================

-- Create decision type enum-like constraint
-- decision_type values: budget_check, budget_escalation, budget_override,
--                       human_approval, router_decision, policy_selection

-- Create the decision_log table
CREATE TABLE IF NOT EXISTS decision_log (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Project reference
    project_id TEXT NOT NULL REFERENCES flow_executions(project_id) ON DELETE CASCADE,

    -- Decision identification
    decision_type TEXT NOT NULL,  -- budget_check, budget_escalation, human_approval, etc.
    decision_point TEXT NOT NULL,  -- Where in the flow this decision occurred

    -- Decision details
    decision TEXT NOT NULL,  -- approved, rejected, escalated, overridden, etc.
    rationale TEXT,  -- Human or system explanation

    -- Budget-specific fields (Area 6)
    enforcement_mode TEXT,  -- hard, soft
    budget_limit_usd FLOAT,
    current_spend_usd FLOAT,
    threshold_pct FLOAT,  -- What threshold triggered this (0.8, 1.2, etc.)

    -- Actor information
    actor_type TEXT NOT NULL,  -- system, human, guardian_agent
    actor_id TEXT,  -- User ID for human decisions, agent name for system

    -- Context snapshot
    context_snapshot JSONB DEFAULT '{}'::jsonb,  -- State at decision time

    -- Override tracking
    is_override BOOLEAN DEFAULT FALSE,
    override_reason TEXT,
    overridden_by TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_decision_log_project_id ON decision_log(project_id);
CREATE INDEX IF NOT EXISTS idx_decision_log_decision_type ON decision_log(decision_type);
CREATE INDEX IF NOT EXISTS idx_decision_log_decision ON decision_log(decision);
CREATE INDEX IF NOT EXISTS idx_decision_log_actor_type ON decision_log(actor_type);
CREATE INDEX IF NOT EXISTS idx_decision_log_created_at ON decision_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_decision_log_is_override ON decision_log(is_override) WHERE is_override = TRUE;

-- Composite index for budget analysis
CREATE INDEX IF NOT EXISTS idx_decision_log_budget ON decision_log(decision_type, enforcement_mode)
    WHERE decision_type IN ('budget_check', 'budget_escalation', 'budget_override');

-- Composite index for project + type queries
CREATE INDEX IF NOT EXISTS idx_decision_log_project_type ON decision_log(project_id, decision_type);

-- Add Row Level Security (RLS)
ALTER TABLE decision_log ENABLE ROW LEVEL SECURITY;

-- Policy: Allow all operations for authenticated service role
CREATE POLICY "Service role has full access" ON decision_log
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- ============================================
-- Function to log a decision
-- ============================================
CREATE OR REPLACE FUNCTION log_decision(
    p_project_id TEXT,
    p_decision_type TEXT,
    p_decision_point TEXT,
    p_decision TEXT,
    p_actor_type TEXT,
    p_rationale TEXT DEFAULT NULL,
    p_actor_id TEXT DEFAULT NULL,
    p_enforcement_mode TEXT DEFAULT NULL,
    p_budget_limit_usd FLOAT DEFAULT NULL,
    p_current_spend_usd FLOAT DEFAULT NULL,
    p_threshold_pct FLOAT DEFAULT NULL,
    p_context_snapshot JSONB DEFAULT '{}'::jsonb,
    p_is_override BOOLEAN DEFAULT FALSE,
    p_override_reason TEXT DEFAULT NULL,
    p_overridden_by TEXT DEFAULT NULL
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    new_id UUID;
BEGIN
    INSERT INTO decision_log (
        project_id, decision_type, decision_point, decision,
        rationale, actor_type, actor_id,
        enforcement_mode, budget_limit_usd, current_spend_usd, threshold_pct,
        context_snapshot, is_override, override_reason, overridden_by
    ) VALUES (
        p_project_id, p_decision_type, p_decision_point, p_decision,
        p_rationale, p_actor_type, p_actor_id,
        p_enforcement_mode, p_budget_limit_usd, p_current_spend_usd, p_threshold_pct,
        p_context_snapshot, p_is_override, p_override_reason, p_overridden_by
    )
    RETURNING id INTO new_id;

    RETURN new_id;
END;
$$;

-- ============================================
-- View for budget decision summary
-- ============================================
CREATE OR REPLACE VIEW budget_decisions_summary AS
SELECT
    project_id,
    enforcement_mode,
    COUNT(*) FILTER (WHERE decision = 'approved') as approved_count,
    COUNT(*) FILTER (WHERE decision = 'rejected') as rejected_count,
    COUNT(*) FILTER (WHERE decision = 'escalated') as escalated_count,
    COUNT(*) FILTER (WHERE is_override = TRUE) as override_count,
    MAX(current_spend_usd) as max_spend_usd,
    MAX(threshold_pct) as max_threshold_triggered
FROM decision_log
WHERE decision_type IN ('budget_check', 'budget_escalation', 'budget_override')
GROUP BY project_id, enforcement_mode;

-- ============================================
-- View for override audit trail
-- ============================================
CREATE OR REPLACE VIEW override_audit AS
SELECT
    id,
    project_id,
    decision_type,
    decision_point,
    decision,
    rationale,
    override_reason,
    overridden_by,
    actor_type,
    created_at
FROM decision_log
WHERE is_override = TRUE
ORDER BY created_at DESC;

-- Comments for documentation
COMMENT ON TABLE decision_log IS 'Audit trail for system and human decisions including budget guardrails';
COMMENT ON COLUMN decision_log.decision_type IS 'Type: budget_check, budget_escalation, human_approval, router_decision, policy_selection';
COMMENT ON COLUMN decision_log.enforcement_mode IS 'Budget enforcement mode: hard, soft';
COMMENT ON COLUMN decision_log.actor_type IS 'Who made the decision: system, human, guardian_agent';
COMMENT ON FUNCTION log_decision IS 'Helper to insert decision log entries';
COMMENT ON VIEW budget_decisions_summary IS 'Aggregated budget decision metrics per project';
COMMENT ON VIEW override_audit IS 'Filtered view of all override decisions for audit';
