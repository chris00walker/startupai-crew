-- ============================================
-- Migration 003: Learnings Tables with pgvector
-- ============================================
-- Stores anonymized learnings for the Flywheel system.
-- Uses pgvector for semantic similarity search.
--
-- PREREQUISITE: Enable pgvector extension in Supabase dashboard:
-- Database > Extensions > vector
--
-- Run this migration after 002_validation_events.sql
-- ============================================

-- Enable pgvector extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the learnings table
CREATE TABLE IF NOT EXISTS learnings (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Learning metadata
    learning_type TEXT NOT NULL,  -- pattern, outcome, domain
    founder TEXT NOT NULL,        -- Anonymized founder identifier
    phase TEXT NOT NULL,          -- Phase where learning was captured
    industry TEXT,                -- Optional industry classification

    -- Learning content
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    context_abstract TEXT NOT NULL,  -- Anonymized, abstracted context

    -- Tags for filtering
    tags TEXT[] DEFAULT '{}',

    -- Vector embedding for similarity search (OpenAI text-embedding-3-small: 1536 dimensions)
    embedding vector(1536),

    -- Confidence and validation
    confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
    validated_by_outcome BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_learnings_type ON learnings(learning_type);
CREATE INDEX IF NOT EXISTS idx_learnings_phase ON learnings(phase);
CREATE INDEX IF NOT EXISTS idx_learnings_industry ON learnings(industry);
CREATE INDEX IF NOT EXISTS idx_learnings_tags ON learnings USING GIN (tags);
CREATE INDEX IF NOT EXISTS idx_learnings_created_at ON learnings(created_at DESC);

-- Create IVFFlat index for vector similarity search
-- Lists parameter: sqrt(num_rows) to 2*sqrt(num_rows) is recommended
-- Starting with 100 lists, adjust as data grows
CREATE INDEX IF NOT EXISTS idx_learnings_embedding ON learnings
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Add trigger to auto-update updated_at
DROP TRIGGER IF EXISTS update_learnings_updated_at ON learnings;
CREATE TRIGGER update_learnings_updated_at
    BEFORE UPDATE ON learnings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add Row Level Security (RLS)
ALTER TABLE learnings ENABLE ROW LEVEL SECURITY;

-- Policy: Allow all operations for authenticated service role
CREATE POLICY "Service role has full access" ON learnings
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- ============================================
-- Helper function for similarity search
-- ============================================
CREATE OR REPLACE FUNCTION search_learnings(
    query_embedding vector(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5,
    filter_phase TEXT DEFAULT NULL,
    filter_type TEXT DEFAULT NULL,
    filter_industry TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    title TEXT,
    description TEXT,
    context_abstract TEXT,
    learning_type TEXT,
    phase TEXT,
    industry TEXT,
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
        l.tags,
        l.confidence_score,
        1 - (l.embedding <=> query_embedding) AS similarity
    FROM learnings l
    WHERE
        1 - (l.embedding <=> query_embedding) > match_threshold
        AND (filter_phase IS NULL OR l.phase = filter_phase)
        AND (filter_type IS NULL OR l.learning_type = filter_type)
        AND (filter_industry IS NULL OR l.industry = filter_industry)
    ORDER BY l.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Comments for documentation
COMMENT ON TABLE learnings IS 'Anonymized learnings for Flywheel competitive moat';
COMMENT ON COLUMN learnings.learning_type IS 'Type: pattern, outcome, domain';
COMMENT ON COLUMN learnings.context_abstract IS 'Anonymized and abstracted context for privacy';
COMMENT ON COLUMN learnings.embedding IS 'OpenAI text-embedding-3-small vector for similarity search';
COMMENT ON FUNCTION search_learnings IS 'Semantic similarity search for relevant learnings';
