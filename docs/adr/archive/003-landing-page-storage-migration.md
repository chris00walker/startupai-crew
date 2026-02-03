# ADR-003: Migration from Netlify to Supabase Storage for Landing Pages

**Status**: Implemented
**Date**: 2026-01-10
**Decision Makers**: Chris Walker, Claude AI Assistant
**Context**: Landing page deployment for Phase 2 Desirability validation
**Related**: [ADR-002](./002-modal-serverless-migration.md) (Modal serverless architecture)

## Summary

Replace Netlify API integration with Supabase Storage for deploying temporary landing page artifacts during validation experiments. This aligns the hosting solution with the actual requirement: temporary, ephemeral pages for collecting validation feedback.

## Context

### The Problem

The `LandingPageDeploymentTool` was implemented to deploy landing pages to Netlify for A/B testing during Phase 2 Desirability validation. However, during testing we discovered:

1. **API Authentication Failure**: The Netlify Personal Access Token exhibited unusual permissions:
   - Could CREATE sites (201 Created)
   - Could NOT LIST sites (401 Unauthorized)
   - Could NOT DEPLOY to sites (401 Unauthorized)
   - Could NOT GET user info (401 Unauthorized)

2. **Architecture Mismatch**: Netlify is designed for permanent hosting with CI/CD pipelines, custom domains, and production traffic. Our landing pages are:
   - **Temporary**: Hours to days lifespan
   - **Ephemeral**: Created for validation, deleted when experiment ends
   - **Low traffic**: Only validation participants (~10-100 views)
   - **Programmatically generated**: No build pipeline needed

3. **Complexity vs Need**: The 522-line Netlify implementation includes:
   - Site creation logic
   - ZIP and digest-based upload methods
   - Error handling for site name conflicts
   - Timestamp-based unique naming

This is significant infrastructure for pages that exist for hours.

### Root Cause Analysis

We were "fitting a square peg into a round hole" - using a permanent hosting platform for temporary artifacts. The architectural need is:

```
[Agent generates HTML] → [Store somewhere public] → [Get URL] → [Collect feedback]
```

Netlify adds complexity we don't need:
- Site creation/management
- API authentication scopes
- Permanent infrastructure
- Cleanup overhead (orphaned sites)

## Decision

**Replace Netlify with Supabase Storage for landing page deployment.**

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     LANDING PAGE VALIDATION FLOW                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [F2: Frontend Agent]                                                       │
│         │                                                                   │
│         ▼ generates HTML with embedded tracking                             │
│  ┌──────────────────┐                                                       │
│  │ LandingPageDeploy│                                                       │
│  │ Tool (rewritten) │                                                       │
│  └────────┬─────────┘                                                       │
│           │                                                                 │
│           ▼                                                                 │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ Supabase Storage (public bucket: landing-pages)                      │  │
│  │                                                                      │  │
│  │ {run_id}/{variant_id}.html                                          │  │
│  │ {run_id}/{variant_id}.html                                          │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│           │                                                                 │
│           ▼                                                                 │
│  Public URL: https://{project}.supabase.co/storage/v1/object/public/       │
│              landing-pages/{run_id}/{variant_id}.html                       │
│                                                                             │
│  [User visits page]                                                         │
│         │                                                                   │
│         ├──▶ Page view tracked via embedded JS → lp_pageviews table        │
│         │                                                                   │
│         ▼ fills form                                                        │
│  ┌──────────────────┐      ┌──────────────────┐                            │
│  │ Form submit JS   │ ───▶ │ Supabase Edge    │                            │
│  │ (embedded in LP) │      │ Function         │                            │
│  └──────────────────┘      └────────┬─────────┘                            │
│                                     │                                       │
│                                     ▼                                       │
│                           ┌──────────────────┐                              │
│                           │ lp_submissions   │                              │
│                           │ table            │                              │
│                           └──────────────────┘                              │
│                                                                             │
│  [Cleanup: Delete storage files when validation run expires]               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Why Supabase Storage

| Requirement | Supabase Storage |
|-------------|------------------|
| **Public URLs** | ✅ Public buckets serve files via CDN |
| **Simplicity** | ✅ Upload file → get URL (no site creation) |
| **Temporary files** | ✅ Delete file = cleanup complete |
| **Already in stack** | ✅ Using Supabase for all state |
| **Cost** | ✅ Included in existing Supabase plan |
| **CDN** | ✅ Global CDN for fast delivery |
| **Form handling** | ✅ Edge Functions + direct table insert |

### Alternatives Considered

#### Option A: Fix Netlify Token (Rejected)
- **Pros**: Keep existing implementation
- **Cons**: Still over-engineered for temporary pages; requires Netlify support; doesn't address architecture mismatch

#### Option B: Modal Web Endpoints (Deferred)
- **Pros**: Zero additional infrastructure; already deployed
- **Cons**: Adds latency (~50-100ms); `*.modal.run` URLs; more complex for static HTML
- **Decision**: Good backup option if Supabase Storage has limitations

#### Option C: Supabase Storage (Selected)
- **Pros**: Simplest solution; already in stack; CDN-backed; natural cleanup
- **Cons**: Long URLs; form handling requires Edge Function
- **Decision**: Best fit for temporary validation artifacts

## Consequences

### Positive

1. **Simplified implementation**: ~100 lines vs 522 lines
2. **No authentication complexity**: Supabase client already authenticated
3. **Natural data lifecycle**: Files deleted with validation run
4. **Unified stack**: All data in Supabase (state, submissions, files)
5. **Cost reduction**: No additional platform costs

### Negative

1. **URL format**: `*.supabase.co/storage/...` less memorable than `*.netlify.app`
   - *Mitigation*: Not user-facing for long; validation participants use link directly
2. **Form handling overhead**: Need Edge Function for submissions
   - *Mitigation*: One-time setup; reusable across all landing pages
3. **No custom domains**: Cannot use branded URLs
   - *Mitigation*: Not required for validation experiments

### Neutral

1. **Netlify relationship preserved**: Keep using Netlify for marketing site and product app
2. **Implementation effort**: 6-7 hours (acceptable for architectural improvement)

## Implementation Plan

### Phase 1: Supabase Resources (1 hour)

1. Create public bucket `landing-pages`
2. Create tables:
   - `landing_page_variants` (metadata)
   - `lp_submissions` (form data)
   - `lp_pageviews` (analytics)
3. Create RLS policies
4. Create Edge Function `capture-submission`

### Phase 2: Tool Rewrite (3 hours)

1. Rewrite `LandingPageDeploymentTool` to use Supabase Storage
2. Update HTML template with tracking JS
3. Add form submission handler JS
4. Add cleanup method for expired variants

### Phase 3: Integration (2 hours)

1. Update F2/F3 agent tool configuration
2. Test deployment and form capture
3. Verify analytics tracking
4. End-to-end validation test

### Phase 4: Cleanup (1 hour)

1. Archive Netlify implementation
2. Remove NETLIFY_ACCESS_TOKEN from Modal secrets (optional - may keep for other uses)
3. Update documentation

## Data Model

```sql
-- Landing page variants (metadata)
CREATE TABLE landing_page_variants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id UUID NOT NULL REFERENCES validation_runs(id) ON DELETE CASCADE,
  variant_name TEXT NOT NULL,
  storage_path TEXT NOT NULL,
  public_url TEXT NOT NULL,
  html_hash TEXT,  -- For detecting changes
  created_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ,
  metadata JSONB DEFAULT '{}'
);

-- Form submissions
CREATE TABLE lp_submissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  variant_id UUID REFERENCES landing_page_variants(id) ON DELETE CASCADE,
  email TEXT,
  form_data JSONB,
  user_agent TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Page views (for Innovation Physics metrics)
CREATE TABLE lp_pageviews (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  variant_id UUID REFERENCES landing_page_variants(id) ON DELETE CASCADE,
  session_id TEXT,
  user_agent TEXT,
  referrer TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for analytics queries
CREATE INDEX idx_lp_submissions_variant ON lp_submissions(variant_id);
CREATE INDEX idx_lp_pageviews_variant ON lp_pageviews(variant_id);
CREATE INDEX idx_lp_variants_run ON landing_page_variants(run_id);
```

## Metrics

### Success Criteria

1. Landing page deployment succeeds (HTTP 200 on public URL)
2. Form submissions captured in `lp_submissions` table
3. Page views tracked in `lp_pageviews` table
4. Implementation < 150 lines (vs 522 current)
5. No external API authentication issues

### Monitoring

- Supabase Storage usage (should be minimal)
- Edge Function invocations
- Table row counts for submissions/pageviews

## References

- [Supabase Storage Documentation](https://supabase.com/docs/guides/storage)
- [Supabase Edge Functions](https://supabase.com/docs/guides/functions)
- [ADR-002: Modal Serverless Migration](./002-modal-serverless-migration.md)
- [Phase 2 Desirability Spec](../master-architecture/06-phase-2-desirability.md)
- [DEPLOYMENT_GAP_ANALYSIS.md](../work/DEPLOYMENT_GAP_ANALYSIS.md) - Original investigation

## Changelog

| Date | Change |
|------|--------|
| 2026-01-10 | Initial ADR created after team architecture discussion |
| 2026-01-10 | **Implementation complete**: Migration 009 applied, tool rewritten, tests passing |

## Implementation Notes (2026-01-10)

The implementation deviated slightly from the original plan:

1. **No Edge Function needed**: Form submissions are handled via client-side JavaScript that directly inserts into Supabase tables using RLS policies (anonymous INSERT allowed).

2. **Simplified tracking**: Client-side JS for both pageviews and form submissions, eliminating the need for a separate Edge Function.

3. **Files created/modified**:
   - `db/migrations/009_landing_page_tables.sql` - Tables with RLS policies
   - `src/shared/tools/landing_page_deploy.py` - Rewrote (~150 lines vs 522)
   - `tests/tools/test_landing_page_deploy.py` - 34 tests passing
   - `archive/netlify-landing-page-deploy.py` - Old implementation archived

4. **Manual step required**: The `landing-pages` storage bucket must be created via Supabase Dashboard (no MCP tool available for storage bucket creation).
