-- ============================================
-- Migration 004: Experiment Outcomes Table
-- ============================================
-- Stores experiment outcomes for policy versioning and A/B testing.
-- Enables the Weighted Bandit policy selection algorithm.
--
-- Run this migration after 003_learnings_tables.sql
-- ============================================

-- Create the experiment_outcomes table
CREATE TABLE IF NOT EXISTS experiment_outcomes (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Project reference
    project_id TEXT NOT NULL REFERENCES flow_executions(project_id) ON DELETE CASCADE,

    -- Experiment identification
    experiment_id TEXT NOT NULL,  -- Unique identifier for this experiment run
    experiment_type TEXT NOT NULL,  -- ad_creative, landing_page, interview_question, etc.

    -- Policy versioning (Area 3)
    policy_version TEXT NOT NULL DEFAULT 'yaml_baseline',  -- yaml_baseline, retrieval_v1, etc.
    config_source TEXT,  -- Where the config came from (yaml, retrieval, hybrid)

    -- Experiment configuration snapshot
    config_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,  -- Full config at experiment time

    -- Outcomes
    primary_metric TEXT NOT NULL,  -- ctr, conversion_rate, response_rate, etc.
    primary_value FLOAT,
    secondary_metrics JSONB DEFAULT '{}'::jsonb,  -- Additional metrics

    -- Status
    status TEXT NOT NULL DEFAULT 'running',  -- running, completed, failed, cancelled

    -- Time tracking
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_experiment_outcomes_project_id ON experiment_outcomes(project_id);
CREATE INDEX IF NOT EXISTS idx_experiment_outcomes_policy_version ON experiment_outcomes(policy_version);
CREATE INDEX IF NOT EXISTS idx_experiment_outcomes_experiment_type ON experiment_outcomes(experiment_type);
CREATE INDEX IF NOT EXISTS idx_experiment_outcomes_status ON experiment_outcomes(status);
CREATE INDEX IF NOT EXISTS idx_experiment_outcomes_created_at ON experiment_outcomes(created_at DESC);

-- Composite index for policy analysis
CREATE INDEX IF NOT EXISTS idx_experiment_outcomes_policy_type ON experiment_outcomes(policy_version, experiment_type);

-- Add trigger to auto-update updated_at
DROP TRIGGER IF EXISTS update_experiment_outcomes_updated_at ON experiment_outcomes;
CREATE TRIGGER update_experiment_outcomes_updated_at
    BEFORE UPDATE ON experiment_outcomes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add Row Level Security (RLS)
ALTER TABLE experiment_outcomes ENABLE ROW LEVEL SECURITY;

-- Policy: Allow all operations for authenticated service role
CREATE POLICY "Service role has full access" ON experiment_outcomes
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- ============================================
-- Aggregation view for policy performance
-- ============================================
CREATE OR REPLACE VIEW policy_performance_summary AS
SELECT
    policy_version,
    experiment_type,
    COUNT(*) as total_experiments,
    COUNT(*) FILTER (WHERE status = 'completed') as completed_experiments,
    AVG(primary_value) FILTER (WHERE status = 'completed') as avg_primary_metric,
    STDDEV(primary_value) FILTER (WHERE status = 'completed') as stddev_primary_metric,
    MIN(primary_value) FILTER (WHERE status = 'completed') as min_primary_metric,
    MAX(primary_value) FILTER (WHERE status = 'completed') as max_primary_metric,
    MIN(created_at) as first_experiment_at,
    MAX(created_at) as last_experiment_at
FROM experiment_outcomes
GROUP BY policy_version, experiment_type;

-- ============================================
-- Function to get policy weights for bandit
-- ============================================
CREATE OR REPLACE FUNCTION get_policy_weights(
    p_experiment_type TEXT,
    p_min_samples INT DEFAULT 10,
    p_exploration_bonus FLOAT DEFAULT 0.1
)
RETURNS TABLE (
    policy_version TEXT,
    sample_count INT,
    mean_reward FLOAT,
    ucb_score FLOAT  -- Upper Confidence Bound for exploration
)
LANGUAGE plpgsql
AS $$
DECLARE
    total_samples INT;
BEGIN
    -- Get total samples for UCB calculation
    SELECT COUNT(*) INTO total_samples
    FROM experiment_outcomes
    WHERE experiment_type = p_experiment_type
    AND status = 'completed';

    RETURN QUERY
    SELECT
        eo.policy_version,
        COUNT(*)::INT as sample_count,
        AVG(eo.primary_value)::FLOAT as mean_reward,
        (AVG(eo.primary_value) + p_exploration_bonus * SQRT(LN(GREATEST(total_samples, 1)::FLOAT) / GREATEST(COUNT(*), 1)))::FLOAT as ucb_score
    FROM experiment_outcomes eo
    WHERE eo.experiment_type = p_experiment_type
    AND eo.status = 'completed'
    GROUP BY eo.policy_version
    HAVING COUNT(*) >= p_min_samples
    ORDER BY ucb_score DESC;
END;
$$;

-- Comments for documentation
COMMENT ON TABLE experiment_outcomes IS 'Experiment outcomes for policy versioning and A/B testing';
COMMENT ON COLUMN experiment_outcomes.policy_version IS 'Policy version used: yaml_baseline, retrieval_v1, etc.';
COMMENT ON COLUMN experiment_outcomes.config_snapshot IS 'Full experiment configuration at time of execution';
COMMENT ON VIEW policy_performance_summary IS 'Aggregated policy performance metrics';
COMMENT ON FUNCTION get_policy_weights IS 'UCB-based policy weights for weighted bandit selection';
