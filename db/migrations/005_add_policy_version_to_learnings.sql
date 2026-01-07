-- ============================================
-- Migration 005: Add Policy Version to Learnings
-- ============================================
-- Extends the learnings table to track which policy version
-- was active when the learning was captured.
--
-- Run this migration after 004_experiment_outcomes.sql
-- ============================================

-- Add policy_version column to learnings table
ALTER TABLE learnings
ADD COLUMN IF NOT EXISTS policy_version TEXT DEFAULT 'yaml_baseline';

-- Add experiment_id for linking to experiment_outcomes
ALTER TABLE learnings
ADD COLUMN IF NOT EXISTS experiment_id TEXT;

-- Add experiment_type for filtering
ALTER TABLE learnings
ADD COLUMN IF NOT EXISTS experiment_type TEXT;

-- Create index on policy_version for policy analysis
CREATE INDEX IF NOT EXISTS idx_learnings_policy_version ON learnings(policy_version);

-- Create index on experiment_id for joining
CREATE INDEX IF NOT EXISTS idx_learnings_experiment_id ON learnings(experiment_id);

-- Composite index for policy + phase analysis
CREATE INDEX IF NOT EXISTS idx_learnings_policy_phase ON learnings(policy_version, phase);

-- ============================================
-- Update search function to include policy filtering
-- ============================================
DROP FUNCTION IF EXISTS search_learnings(vector(1536), FLOAT, INT, TEXT, TEXT, TEXT);

CREATE OR REPLACE FUNCTION search_learnings(
    query_embedding vector(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5,
    filter_phase TEXT DEFAULT NULL,
    filter_type TEXT DEFAULT NULL,
    filter_industry TEXT DEFAULT NULL,
    filter_policy_version TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    title TEXT,
    description TEXT,
    context_abstract TEXT,
    learning_type TEXT,
    phase TEXT,
    industry TEXT,
    policy_version TEXT,
    tags TEXT[],
    confidence_score FLOAT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        l.id,
        l.title,
        l.description,
        l.context_abstract,
        l.learning_type,
        l.phase,
        l.industry,
        l.policy_version,
        l.tags,
        l.confidence_score,
        1 - (l.embedding <=> query_embedding) AS similarity
    FROM learnings l
    WHERE
        1 - (l.embedding <=> query_embedding) > match_threshold
        AND (filter_phase IS NULL OR l.phase = filter_phase)
        AND (filter_type IS NULL OR l.learning_type = filter_type)
        AND (filter_industry IS NULL OR l.industry = filter_industry)
        AND (filter_policy_version IS NULL OR l.policy_version = filter_policy_version)
    ORDER BY l.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ============================================
-- View for policy-attributed learning counts
-- ============================================
CREATE OR REPLACE VIEW learnings_by_policy AS
SELECT
    policy_version,
    learning_type,
    phase,
    COUNT(*) as learning_count,
    AVG(confidence_score) as avg_confidence,
    COUNT(*) FILTER (WHERE validated_by_outcome = true) as validated_count
FROM learnings
GROUP BY policy_version, learning_type, phase;

-- Comments
COMMENT ON COLUMN learnings.policy_version IS 'Policy version active when learning was captured';
COMMENT ON COLUMN learnings.experiment_id IS 'Link to experiment_outcomes for attribution';
COMMENT ON VIEW learnings_by_policy IS 'Learning counts segmented by policy version';
