-- ============================================
-- Migration 002: Validation Events Table
-- ============================================
-- Stores the event log for audit trail, debugging, and replay.
-- Implements event sourcing pattern for the validation flow.
--
-- Run this migration after 001_flow_executions.sql
-- ============================================

-- Create the validation_events table
CREATE TABLE IF NOT EXISTS validation_events (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign key to flow_executions
    project_id TEXT NOT NULL REFERENCES flow_executions(project_id) ON DELETE CASCADE,

    -- Event metadata
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    event_type TEXT NOT NULL,

    -- State snapshots for transitions
    from_state JSONB,
    to_state JSONB,

    -- Event details
    reason TEXT,
    triggered_by TEXT,

    -- Evidence at time of event
    evidence_snapshot JSONB,

    -- Additional metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_validation_events_project_id ON validation_events(project_id);
CREATE INDEX IF NOT EXISTS idx_validation_events_timestamp ON validation_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_validation_events_event_type ON validation_events(event_type);
CREATE INDEX IF NOT EXISTS idx_validation_events_triggered_by ON validation_events(triggered_by);

-- Composite index for filtering by project and type
CREATE INDEX IF NOT EXISTS idx_validation_events_project_type ON validation_events(project_id, event_type);

-- Add Row Level Security (RLS)
ALTER TABLE validation_events ENABLE ROW LEVEL SECURITY;

-- Policy: Allow all operations for authenticated service role
CREATE POLICY "Service role has full access" ON validation_events
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Comments for documentation
COMMENT ON TABLE validation_events IS 'Event log for validation flow audit and replay';
COMMENT ON COLUMN validation_events.event_type IS 'Type: flow_started, phase_transition, router_decision, pivot_initiated, etc.';
COMMENT ON COLUMN validation_events.from_state IS 'State before the event (for transitions)';
COMMENT ON COLUMN validation_events.to_state IS 'State after the event (for transitions)';
COMMENT ON COLUMN validation_events.evidence_snapshot IS 'Evidence at the time of the decision';
