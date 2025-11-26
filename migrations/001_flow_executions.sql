-- ============================================
-- Migration 001: Flow Executions Table
-- ============================================
-- Stores the full state of validation flows with indexed columns
-- for efficient querying and filtering.
--
-- Run this migration in Supabase SQL Editor:
-- https://app.supabase.com/project/YOUR_PROJECT/sql
-- ============================================

-- Create the flow_executions table
CREATE TABLE IF NOT EXISTS flow_executions (
    -- Primary key (auto-generated UUID)
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Project identifier (unique, used as foreign key)
    project_id TEXT NOT NULL UNIQUE,

    -- Indexed columns for efficient querying
    phase TEXT NOT NULL DEFAULT 'ideation',
    current_risk_axis TEXT DEFAULT 'desirability',
    iteration INTEGER DEFAULT 0,

    -- Signal columns for filtering
    desirability_signal TEXT DEFAULT 'no_signal',
    feasibility_signal TEXT DEFAULT 'unknown',
    viability_signal TEXT DEFAULT 'unknown',

    -- Full state as JSONB (for complex queries and full reconstruction)
    full_state JSONB NOT NULL,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_flow_executions_phase ON flow_executions(phase);
CREATE INDEX IF NOT EXISTS idx_flow_executions_updated_at ON flow_executions(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_flow_executions_signals ON flow_executions(
    desirability_signal,
    feasibility_signal,
    viability_signal
);

-- Create GIN index for JSONB queries
CREATE INDEX IF NOT EXISTS idx_flow_executions_full_state ON flow_executions USING GIN (full_state);

-- Add trigger to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_flow_executions_updated_at ON flow_executions;
CREATE TRIGGER update_flow_executions_updated_at
    BEFORE UPDATE ON flow_executions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add Row Level Security (RLS)
ALTER TABLE flow_executions ENABLE ROW LEVEL SECURITY;

-- Policy: Allow all operations for authenticated service role
-- In production, you may want more granular policies
CREATE POLICY "Service role has full access" ON flow_executions
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Comments for documentation
COMMENT ON TABLE flow_executions IS 'Stores validation flow state with signal-based routing';
COMMENT ON COLUMN flow_executions.project_id IS 'Unique identifier for the validation project';
COMMENT ON COLUMN flow_executions.phase IS 'Current phase: ideation, desirability, feasibility, viability, validated, killed';
COMMENT ON COLUMN flow_executions.current_risk_axis IS 'Risk being tested: desirability, feasibility, viability';
COMMENT ON COLUMN flow_executions.full_state IS 'Complete StartupValidationState as JSON';
