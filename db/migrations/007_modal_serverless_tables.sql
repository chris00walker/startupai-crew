-- ============================================================
-- Migration 007: Modal Serverless Tables
-- ============================================================
-- Created: 2026-01-08
-- Updated: 2026-01-08 - Added run_id, provider, phase_name, inputs, outputs
-- Purpose: Support Modal serverless architecture per ADR-002
-- Tables: validation_runs, validation_progress, hitl_requests
-- ============================================================

-- ============================================================
-- Table: validation_runs
-- Purpose: Store validation run state for checkpoint/resume
-- ============================================================
CREATE TABLE IF NOT EXISTS validation_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id TEXT UNIQUE NOT NULL,  -- External ID from Modal or AMP
    project_id UUID NOT NULL,
    user_id UUID NOT NULL,
    session_id TEXT,  -- Optional onboarding session reference

    -- Provider tracking (modal or amp)
    provider TEXT NOT NULL DEFAULT 'modal'
        CHECK (provider IN ('modal', 'amp')),

    -- Run state
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'running', 'paused', 'completed', 'failed')),
    current_phase INTEGER NOT NULL DEFAULT 0
        CHECK (current_phase >= 0 AND current_phase <= 4),
    phase_name TEXT DEFAULT 'Onboarding',

    -- Input/Output data
    inputs JSONB DEFAULT '{}',
    outputs JSONB DEFAULT '{}',

    -- Progress tracking (for UI display)
    progress JSONB DEFAULT '{}',  -- {crew, task, agent, progress_pct}

    -- Serialized state (Pydantic model JSON)
    phase_state JSONB NOT NULL DEFAULT '{}',

    -- HITL checkpoint tracking
    hitl_checkpoint JSONB,  -- Full checkpoint data for UI
    hitl_checkpoint_at TIMESTAMPTZ,

    -- Execution metadata
    modal_function_id TEXT,  -- Modal function call ID for tracing
    error TEXT,  -- Error message if failed
    retry_count INTEGER NOT NULL DEFAULT 0,

    -- Timestamps
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for validation_runs
CREATE INDEX IF NOT EXISTS idx_validation_runs_project ON validation_runs(project_id);
CREATE INDEX IF NOT EXISTS idx_validation_runs_user ON validation_runs(user_id);
CREATE INDEX IF NOT EXISTS idx_validation_runs_status ON validation_runs(status);
CREATE INDEX IF NOT EXISTS idx_validation_runs_hitl ON validation_runs(status) WHERE hitl_checkpoint IS NOT NULL;

-- ============================================================
-- Table: validation_progress
-- Purpose: Append-only progress log for real-time UI updates
-- ============================================================
CREATE TABLE IF NOT EXISTS validation_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES validation_runs(id) ON DELETE CASCADE,

    -- Progress details
    phase INTEGER NOT NULL CHECK (phase >= 0 AND phase <= 4),
    crew TEXT NOT NULL,
    task TEXT,
    agent TEXT,

    -- Status tracking
    status TEXT NOT NULL CHECK (status IN ('started', 'in_progress', 'completed', 'failed', 'skipped')),
    progress_pct INTEGER CHECK (progress_pct >= 0 AND progress_pct <= 100),

    -- Output (optional, for completed tasks)
    output JSONB,
    error_message TEXT,

    -- Timing
    duration_ms INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for validation_progress
CREATE INDEX IF NOT EXISTS idx_validation_progress_run ON validation_progress(run_id);
CREATE INDEX IF NOT EXISTS idx_validation_progress_phase ON validation_progress(run_id, phase);
CREATE INDEX IF NOT EXISTS idx_validation_progress_created ON validation_progress(created_at DESC);

-- ============================================================
-- Table: hitl_requests
-- Purpose: Human-in-the-loop checkpoint requests
-- ============================================================
CREATE TABLE IF NOT EXISTS hitl_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES validation_runs(id) ON DELETE CASCADE,

    -- Checkpoint identification
    checkpoint_name TEXT NOT NULL,
    phase INTEGER NOT NULL CHECK (phase >= 0 AND phase <= 4),

    -- Context for human review
    context JSONB NOT NULL DEFAULT '{}',
    title TEXT NOT NULL,
    description TEXT,

    -- Decision options
    options JSONB,  -- Array of {id, label, description}
    recommended_option TEXT,

    -- Approval tracking
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'approved', 'rejected', 'expired', 'auto_approved')),
    decision TEXT,
    decision_by UUID,
    decision_at TIMESTAMPTZ,
    feedback TEXT,

    -- Expiration
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '7 days'),

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for hitl_requests
CREATE INDEX IF NOT EXISTS idx_hitl_requests_run ON hitl_requests(run_id);
CREATE INDEX IF NOT EXISTS idx_hitl_requests_status ON hitl_requests(status);
CREATE INDEX IF NOT EXISTS idx_hitl_requests_expires ON hitl_requests(expires_at) WHERE status = 'pending';
CREATE UNIQUE INDEX IF NOT EXISTS idx_hitl_requests_unique_pending
    ON hitl_requests(run_id, checkpoint_name) WHERE status = 'pending';

-- ============================================================
-- Triggers: Auto-update updated_at
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_validation_runs_updated_at ON validation_runs;
CREATE TRIGGER update_validation_runs_updated_at
    BEFORE UPDATE ON validation_runs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_hitl_requests_updated_at ON hitl_requests;
CREATE TRIGGER update_hitl_requests_updated_at
    BEFORE UPDATE ON hitl_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- Enable Realtime for instant UI updates
-- ============================================================
-- Note: Run these in Supabase dashboard if ALTER PUBLICATION fails
-- ALTER PUBLICATION supabase_realtime ADD TABLE validation_progress;
-- ALTER PUBLICATION supabase_realtime ADD TABLE hitl_requests;

-- ============================================================
-- RLS Policies (Enable after testing)
-- ============================================================
-- Users can only see their own validation runs
-- ALTER TABLE validation_runs ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Users can view own validation runs"
--     ON validation_runs FOR SELECT
--     USING (user_id = auth.uid());
--
-- CREATE POLICY "Users can insert own validation runs"
--     ON validation_runs FOR INSERT
--     WITH CHECK (user_id = auth.uid());

-- ============================================================
-- Comments
-- ============================================================
COMMENT ON TABLE validation_runs IS 'Modal serverless validation run state for checkpoint/resume';
COMMENT ON TABLE validation_progress IS 'Append-only progress log for Supabase Realtime UI updates';
COMMENT ON TABLE hitl_requests IS 'Human-in-the-loop approval requests with expiration';

COMMENT ON COLUMN validation_runs.phase_state IS 'Serialized Pydantic ValidationState model';
COMMENT ON COLUMN validation_runs.hitl_checkpoint IS 'Full HITL checkpoint data for UI display';
COMMENT ON COLUMN validation_progress.progress_pct IS 'Task completion percentage 0-100';
COMMENT ON COLUMN hitl_requests.context IS 'All context needed for human to make decision';
