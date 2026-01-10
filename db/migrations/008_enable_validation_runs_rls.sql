-- Migration: Enable RLS on Modal serverless tables
-- Date: 2026-01-10
-- Purpose: Production security for validation_runs, validation_progress, hitl_requests
--
-- Security Model:
-- - Service role (Modal backend) has full access via service_role JWT
-- - Users can only access their own validation runs
-- - Related tables (progress, hitl) join through validation_runs

-- =============================================================================
-- validation_runs: Enable RLS with user-scoped access
-- =============================================================================

ALTER TABLE validation_runs ENABLE ROW LEVEL SECURITY;

-- Service role bypass (for Modal backend operations using service_role key)
CREATE POLICY "Service role has full access on validation_runs"
    ON validation_runs FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

-- Users can view their own runs
CREATE POLICY "Users can view own validation runs"
    ON validation_runs FOR SELECT
    USING (user_id = auth.uid());

-- Users can insert their own runs (via frontend kickoff)
CREATE POLICY "Users can insert own validation runs"
    ON validation_runs FOR INSERT
    WITH CHECK (user_id = auth.uid());

-- =============================================================================
-- validation_progress: Enable RLS (join through validation_runs.run_id)
-- =============================================================================

ALTER TABLE validation_progress ENABLE ROW LEVEL SECURITY;

-- Service role bypass
CREATE POLICY "Service role has full access on validation_progress"
    ON validation_progress FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

-- Users can view progress for their own runs
CREATE POLICY "Users can view own validation progress"
    ON validation_progress FOR SELECT
    USING (
        run_id IN (
            SELECT id FROM validation_runs WHERE user_id = auth.uid()
        )
    );

-- =============================================================================
-- hitl_requests: Enable RLS (join through validation_runs.run_id)
-- =============================================================================

ALTER TABLE hitl_requests ENABLE ROW LEVEL SECURITY;

-- Service role bypass
CREATE POLICY "Service role has full access on hitl_requests"
    ON hitl_requests FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

-- Users can view HITL requests for their own runs
CREATE POLICY "Users can view own hitl requests"
    ON hitl_requests FOR SELECT
    USING (
        run_id IN (
            SELECT id FROM validation_runs WHERE user_id = auth.uid()
        )
    );

-- Users can update HITL requests for their own runs (approve/reject)
CREATE POLICY "Users can update own hitl requests"
    ON hitl_requests FOR UPDATE
    USING (
        run_id IN (
            SELECT id FROM validation_runs WHERE user_id = auth.uid()
        )
    )
    WITH CHECK (
        run_id IN (
            SELECT id FROM validation_runs WHERE user_id = auth.uid()
        )
    );
