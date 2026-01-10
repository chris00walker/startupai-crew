-- Migration: Landing Page Storage Tables
-- Date: 2026-01-10
-- Purpose: Support ADR-003 - Supabase Storage for landing pages
-- Tables: landing_page_variants, lp_submissions, lp_pageviews
--
-- This migration creates the infrastructure for deploying temporary landing pages
-- to Supabase Storage for A/B testing during Phase 2 Desirability validation.

-- ===========================================================================
-- LANDING PAGE VARIANTS (metadata for storage files)
-- ===========================================================================

CREATE TABLE IF NOT EXISTS landing_page_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id TEXT NOT NULL,  -- Validation run identifier (text for flexibility)
    variant_name TEXT NOT NULL,
    storage_path TEXT NOT NULL UNIQUE,
    public_url TEXT NOT NULL,
    html_hash TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'
);

COMMENT ON TABLE landing_page_variants IS 'Metadata for landing pages stored in Supabase Storage';
COMMENT ON COLUMN landing_page_variants.run_id IS 'Validation run identifier or project_id';
COMMENT ON COLUMN landing_page_variants.storage_path IS 'Path in Supabase Storage bucket (e.g., proj-123/variant-a.html)';
COMMENT ON COLUMN landing_page_variants.public_url IS 'Public CDN URL for the landing page';
COMMENT ON COLUMN landing_page_variants.html_hash IS 'SHA256 hash prefix for change detection';
COMMENT ON COLUMN landing_page_variants.expires_at IS 'Optional expiration for cleanup automation';

-- ===========================================================================
-- FORM SUBMISSIONS (email signups, CTAs)
-- ===========================================================================

CREATE TABLE IF NOT EXISTS lp_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    variant_id UUID REFERENCES landing_page_variants(id) ON DELETE CASCADE,
    email TEXT,
    form_data JSONB DEFAULT '{}',
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE lp_submissions IS 'Form submissions from landing pages (email signups, CTAs)';
COMMENT ON COLUMN lp_submissions.variant_id IS 'Landing page variant that captured this submission';
COMMENT ON COLUMN lp_submissions.email IS 'Email address if provided';
COMMENT ON COLUMN lp_submissions.form_data IS 'All form fields as JSON';

-- ===========================================================================
-- PAGE VIEWS (for Innovation Physics metrics)
-- ===========================================================================

CREATE TABLE IF NOT EXISTS lp_pageviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    variant_id UUID REFERENCES landing_page_variants(id) ON DELETE CASCADE,
    session_id TEXT,
    user_agent TEXT,
    referrer TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE lp_pageviews IS 'Page view tracking for landing page analytics';
COMMENT ON COLUMN lp_pageviews.session_id IS 'Client-generated session ID for unique visitor tracking';
COMMENT ON COLUMN lp_pageviews.referrer IS 'HTTP referrer URL';

-- ===========================================================================
-- INDEXES for analytics queries
-- ===========================================================================

CREATE INDEX IF NOT EXISTS idx_lp_variants_run ON landing_page_variants(run_id);
CREATE INDEX IF NOT EXISTS idx_lp_variants_created ON landing_page_variants(created_at);
CREATE INDEX IF NOT EXISTS idx_lp_submissions_variant ON lp_submissions(variant_id);
CREATE INDEX IF NOT EXISTS idx_lp_submissions_created ON lp_submissions(created_at);
CREATE INDEX IF NOT EXISTS idx_lp_pageviews_variant ON lp_pageviews(variant_id);
CREATE INDEX IF NOT EXISTS idx_lp_pageviews_created ON lp_pageviews(created_at);

-- ===========================================================================
-- ROW LEVEL SECURITY
-- ===========================================================================

ALTER TABLE landing_page_variants ENABLE ROW LEVEL SECURITY;
ALTER TABLE lp_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE lp_pageviews ENABLE ROW LEVEL SECURITY;

-- Service role full access (Modal backend uses service role key)
CREATE POLICY "Service role full access on landing_page_variants"
    ON landing_page_variants FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role full access on lp_submissions"
    ON lp_submissions FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role full access on lp_pageviews"
    ON lp_pageviews FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

-- Anonymous insert for client-side tracking
-- Landing page visitors use the anon key to record pageviews and form submissions
-- RLS restricts them to INSERT only - they cannot read or modify data
CREATE POLICY "Anonymous can insert submissions"
    ON lp_submissions FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Anonymous can insert pageviews"
    ON lp_pageviews FOR INSERT
    WITH CHECK (true);

-- ===========================================================================
-- TRIGGERS for updated_at (if needed in future)
-- ===========================================================================

-- Note: landing_page_variants intentionally doesn't have updated_at
-- These are write-once records; if content changes, a new record is created
