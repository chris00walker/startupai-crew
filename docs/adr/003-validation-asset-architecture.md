# ADR-003: Validation Asset Architecture

**Status**: Approved
**Date**: 2026-02-02 (Updated: 2026-02-03)
**Decision Makers**: Chris Walker, System Architect, AI Engineer, Frontend Developer, UI Designer, Content Strategist, Data Engineer
**Context**: Landing page and ad creative generation for Phase 2 Desirability validation
**Related**: [ADR-002](./002-modal-serverless-migration.md), [tool-specifications.md](../master-architecture/reference/tool-specifications.md)

## Summary

Define a unified architecture for generating validation campaign assets (landing pages and ad creatives) using the **"Assembly, Not Generation"** principle: AI generates copy, templates provide structure.

## Context

### The Problem

Phase 2 Desirability validation requires:
1. **Landing pages** for A/B testing value propositions
2. **Ad creatives** for driving traffic to landing pages
3. **Rapid iteration** as hypotheses are tested and refined
4. **Platform compliance** across Meta, Google, LinkedIn, TikTok

The naive approach—asking an LLM to generate raw HTML or image layouts—produces:
- "Div soup" with broken layouts
- Inconsistent styling ("AI slop" aesthetic)
- Platform spec violations (wrong dimensions, missing elements)
- Unprofessional appearance that hurts conversion rates

### Root Cause

> "The biggest mistake is asking an LLM to write raw HTML from scratch."

LLMs excel at **language** (headlines, copy, CTAs) but struggle with **structure** (layouts, spacing, visual hierarchy). The architecture must play to AI strengths while using proven design patterns for structure.

## Decision

### Core Principle: Assembly, Not Generation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ASSEMBLY, NOT GENERATION                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ❌ WRONG: LLM generates raw HTML/images                                    │
│     "Generate a landing page for my SaaS product"                           │
│     → Broken layouts, inconsistent styling, unprofessional                  │
│                                                                             │
│  ✅ RIGHT: LLM generates copy, templates provide structure                  │
│     "Generate headline, subheadline, and 3 pain points for this VPC"        │
│     → Professional copy injected into proven, tested templates              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VALIDATION ASSET PIPELINE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  INPUT                                                                      │
│  ─────                                                                      │
│  Value Proposition Canvas (VPC)                                             │
│  • Customer segment                                                         │
│  • Pains, gains, jobs                                                       │
│  • Value propositions                                                       │
│                                                                             │
│        │                                                                    │
│        ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     BLUEPRINT PATTERN                                │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  STRATEGIST         COPYWRITER         ASSEMBLER        VALIDATOR   │   │
│  │  ───────────        ──────────         ─────────        ─────────   │   │
│  │  Selects which      Generates          Selects          Validates   │   │
│  │  sections/formats   compelling copy    templates,       structure,  │   │
│  │  based on VPC       per platform tone  injects copy,    stores      │   │
│  │                                        fetches assets   blueprint   │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│        │                                                                    │
│        ▼                                                                    │
│  ┌──────────────────────────┐    ┌──────────────────────────┐              │
│  │    LANDING PAGES         │    │    AD CREATIVES          │              │
│  ├──────────────────────────┤    ├──────────────────────────┤              │
│  │ Template: Tailwind UI    │    │ Template: Canva (API)    │              │
│  │ Output: HTML             │    │ Output: Images           │              │
│  │ Storage: Supabase        │    │ Storage: Supabase        │              │
│  │ Deploy: Public URL       │    │ Deploy: Ad Platform APIs │              │
│  └──────────────────────────┘    └──────────────────────────┘              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Landing Page Architecture

### Template Procurement

**Decision**: Tailwind UI ($299) - unanimous team recommendation.

| Option | Cost | HSL Variable Support | Recommendation |
|--------|------|---------------------|----------------|
| **Tailwind UI** | $299 one-time | Native (same pattern as our design system) | **Selected** |
| Cruip | $149 one-time | Requires adaptation | Not selected |

**Rationale**: Our design system uses HSL CSS variables (`--primary: 220 70% 45%`). Tailwind UI templates use the identical pattern, eliminating conversion friction. The $150 premium is justified by reduced integration effort.

### Component Registry

The `LandingPageGeneratorTool` uses a fixed registry of **10 pre-built sections**:

| Component | Props | Use Case |
|-----------|-------|----------|
| `HeroSection` | headline, subheadline, cta_text, cta_url, image_keyword | Above the fold |
| `PainPoints` | pains: [{icon, title, description}] | Problem agitation |
| `SolutionSection` | headline, description, image_keyword | Bridge to solution |
| `FeatureGrid` | features: [{icon, title, description}] | 3-4 key features |
| `TrustBadges` | headline?, badges: [{type, value, image_keyword?}] | Social proof (logos, metrics) |
| `Testimonials` | testimonials: [{quote, name, role, avatar_keyword}] | Customer proof |
| `PricingCard` | plan_name, price, features, cta_text | WTP validation |
| `FAQ` | items: [{question, answer}] | Objection handling |
| `CTASection` | headline, subheadline, cta_text, form_enabled | Final conversion |
| `Footer` | company_name, links: [{label, url}] | Navigation |

### Blueprint JSON Schema

Shared TypeScript type for cross-repo consistency:

```typescript
// Location: app.startupai.site/src/types/landing-page.d.ts
// Also exported from: startupai-crew/src/shared/types/

import { z } from 'zod';

export const BlueprintSchema = z.object({
  version: z.literal('1.0'),
  sections: z.array(z.object({
    component: z.enum([
      'HeroSection', 'PainPoints', 'SolutionSection', 'FeatureGrid',
      'TrustBadges', 'Testimonials', 'PricingCard', 'FAQ', 'CTASection', 'Footer'
    ]),
    props: z.record(z.unknown()),
    order: z.number()
  })),
  brandTokens: z.object({
    primary: z.string(),      // HSL: "220 70% 45%"
    accent: z.string(),       // HSL: "160 84% 39%"
    background: z.string(),
    foreground: z.string(),
    radius: z.string()        // e.g., "0.5rem"
  }),
  images: z.array(z.object({
    keyword: z.string(),
    url: z.string().url(),
    source: z.enum(['unsplash', 'dalle', 'uploaded'])
  })),
  metadata: z.object({
    generatedAt: z.string().datetime(),
    vpcId: z.string().uuid(),
    variantName: z.string()
  })
});

export type Blueprint = z.infer<typeof BlueprintSchema>;
```

### Design Token Injection

**Method**: Inline CSS variables at assembly time.

```html
<!-- Injected at top of assembled HTML -->
<style>
  :root {
    --primary: 220 70% 45%;
    --primary-foreground: 0 0% 100%;
    --accent: 160 84% 39%;
    --accent-foreground: 0 0% 100%;
    --background: 0 0% 100%;
    --foreground: 222 47% 11%;
    --muted: 210 40% 96%;
    --muted-foreground: 215 16% 47%;
    --border: 214 32% 91%;
    --radius: 0.5rem;
  }
</style>
```

**Rationale**: Inline CSS vars enable offline/static deployment without external dependencies. Brand tokens are injected from `globals.css` at assembly time.

### Template Storage

| Asset Type | Location | Rationale |
|------------|----------|-----------|
| Template source files | `startupai-crew/src/templates/landing/` | Version controlled with code |
| Component registry | `startupai-crew/src/shared/registries/` | Loaded at runtime |
| Assembled HTML | Supabase Storage `landing-pages` bucket | Public URLs for validation |
| Blueprint JSON | Supabase `landing_page_variants.blueprint` | Re-generation without full pipeline |

### Deployed Page Storage

**Decision**: Use Supabase Storage instead of Netlify for deployed landing pages.

**Rationale**:
- Landing pages are temporary (hours to days lifespan)
- Low traffic (10-100 validation participants)
- No build pipeline needed
- Natural cleanup when validation run expires
- Already using Supabase for all state

**Architecture**:
```
[Assembled HTML] → Supabase Storage (public bucket)
                 → Public URL: {project}.supabase.co/storage/v1/object/public/
                               landing-pages/{run_id}/{variant_id}.html
```

### Image Resolution

Progressive pattern with budget controls:

| Pass | Source | Cost | Budget Control |
|------|--------|------|----------------|
| **First** | Unsplash API | Free | 50 req/hour (cache in Supabase) |
| **Backup** | Pexels API | Free | 200 req/hour fallback |
| **Second** | DALL-E 3 | $0.04/image | `image_budget_cents` parameter |

**Budget Enforcement**: `LandingPageGeneratorTool` accepts `image_budget_cents` parameter (default: 100 = $1.00 max per page).

---

## Ad Creative Architecture

### Canva Partnership Strategy

**Decision**: Pursue Canva API partnership for programmatic template editing.

| Approach | Status | Capability |
|----------|--------|------------|
| **Canva Connect API** | Requires Partner access | Programmatic template editing |
| Manual HITL (interim) | Available now | AI generates copy → human applies in Canva |

**Partnership Path**:
1. Apply for Canva Developer Partner Program
2. Implement Connect API integration for template slot filling
3. Enable automated brand kit application

**Interim Workflow** (until API access):
```
VPC → Copywriter generates copy → HITL checkpoint
    → Human applies copy to Canva template
    → Export images → Supabase Storage
    → Platform submission
```

**Canva Brand Kit Setup** (Required):
- Primary color: #2563eb (from HSL 220 70% 45%)
- Accent color: #10b981 (from HSL 160 84% 39%)
- Fonts: System UI (body), Georgia (headings) or approved Canva substitutes
- Logo lockups uploaded

### Platform Specifications

Templates must comply with platform-specific requirements.

#### Meta (Facebook + Instagram)

| Format | Dimensions | Aspect Ratio | Max Text |
|--------|------------|--------------|----------|
| Feed Image | 1200×628 | 1.91:1 | 20% of image |
| Square | 1080×1080 | 1:1 | 20% of image |
| Story | 1080×1920 | 9:16 | 20% of image |
| Carousel | 1080×1080 | 1:1 | 20% per card |

**Copy Limits**:

| Field | Recommended | Maximum | Notes |
|-------|-------------|---------|-------|
| Headline | 40 chars | 255 chars | Truncates on mobile after 40 |
| Primary text | 125 chars | 1024 chars | Truncates on mobile after 125 |
| Description | 30 chars | 255 chars | Truncates after 30 |

#### Google Ads

| Format | Dimensions | Notes |
|--------|------------|-------|
| Responsive Display | Multiple (auto) | Provide 1200×628, 1200×1200, 1200×300 |
| Search | Text only | See copy limits below |
| Discovery | 1200×628, 1200×1200 | Similar to Meta |

**Copy Limits**:

| Field | Limit | Notes |
|-------|-------|-------|
| Headline | 30 chars × 3 | Three variants required |
| Long headline | 90 chars | For responsive display |
| Description | 90 chars × 2 | Two variants required |
| Business name | 25 chars | |

#### LinkedIn

| Format | Dimensions | Notes |
|--------|------------|-------|
| Sponsored Content | 1200×627 | 1.91:1 ratio |
| Carousel | 1080×1080 | Up to 10 cards |
| Message Ads | 300×250 | Banner only |
| Text Ads | 100×100 | Thumbnail + text |

**Copy Limits**:

| Field | Recommended | Maximum | Notes |
|-------|-------------|---------|-------|
| Headline | 70 chars | 200 chars | 70 optimal for engagement |
| Intro text | 150 chars | 600 chars | 150 recommended |

#### TikTok

| Format | Dimensions | Notes |
|--------|------------|-------|
| In-Feed | 1080×1920 | 9:16, **video strongly preferred** |
| TopView | 1080×1920 | First ad user sees |

**Copy Limits**:

| Field | Limit | Notes |
|-------|-------|-------|
| Caption | 250 chars | |
| Display name | 20 chars | |

**Note**: Static images significantly underperform on TikTok. Defer TikTok until video generation is in scope.

### Platform Prioritization

| Priority | Platform | Rationale |
|----------|----------|-----------|
| 1st | **Meta** | Broad reach, forgiving review, same formats as LinkedIn |
| 2nd | **LinkedIn** | B2B essential, same image formats as Meta |
| 3rd | Google | Intent-based, requires keyword research |
| 4th | TikTok | Requires video capability |

**First Customer**: Implement Meta and LinkedIn only.

### Copywriter Tone Parameter

The Copywriter agent adjusts tone per platform:

| Platform | Tone | Example |
|----------|------|---------|
| Meta | Conversational, benefit-driven | "Stop wasting hours on..." |
| Google | Direct, keyword-rich | "Validate startup ideas fast" |
| LinkedIn | Professional, data-driven | "73% of startups fail due to..." |
| TikTok | Casual, trend-aware | "POV: You finally validated your idea" |

**CTA Vocabulary Standards**:
- Approved: "Start free trial", "Get started", "Learn more", "See how it works"
- Avoid: "Submit", "Click here", "Buy now" (too aggressive for validation)

### Ad Creative Assembly

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      AD CREATIVE ASSEMBLY FLOW                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  VPC Input                                                                  │
│      │                                                                      │
│      ▼                                                                      │
│  ┌─────────────┐                                                            │
│  │ COPYWRITER  │ Generates per platform specs:                              │
│  │             │ • Headlines (4 variants: benefit, pain, social, curiosity) │
│  │             │ • Primary text / descriptions                              │
│  │             │ • CTAs (from approved vocabulary)                          │
│  │             │ • Tone adjusted per platform                               │
│  └──────┬──────┘                                                            │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────┐                                                            │
│  │ ASSEMBLER   │ For each platform:                                         │
│  │             │ • Select template from Canva library                       │
│  │             │ • Inject copy into template slots (API or HITL)            │
│  │             │ • Apply brand colors/fonts from Brand Kit                  │
│  │             │ • Export at required dimensions                            │
│  └──────┬──────┘                                                            │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────┐                                                            │
│  │ VALIDATOR   │ Check:                                                     │
│  │             │ • Dimensions match platform spec                           │
│  │             │ • Text within recommended limits (warn if max)             │
│  │             │ • Meta: <20% text overlay                                  │
│  │             │ • Required elements present                                │
│  └──────┬──────┘                                                            │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────┐                                                            │
│  │ HITL        │ Brand review checkpoint before platform submission         │
│  │ CHECKPOINT  │ (Required for all ad creatives)                            │
│  └──────┬──────┘                                                            │
│         │                                                                   │
│         ▼                                                                   │
│  Supabase Storage → Ad Platform API submission                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Ad Creative Storage

| Asset Type | Location | Rationale |
|------------|----------|-----------|
| Template source | Canva (external) | Managed via Canva API or Brand Kit |
| Exported images | Supabase Storage `ad-creatives` bucket | Platform submission |
| Creative metadata | Supabase `ad_creatives` table | Tracking, variants |
| Platform responses | Supabase `ad_submissions` table | Approval status, IDs |

---

## Data Model

### Schema Standardization

**Decision**: All `run_id` foreign keys use UUID type with CASCADE delete.

The existing `landing_page_variants.run_id` (currently TEXT without FK) requires migration to UUID with FK constraint for consistency.

### Landing Pages

```sql
-- Landing page variants (metadata + blueprint)
CREATE TABLE landing_page_variants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id UUID NOT NULL REFERENCES validation_runs(id) ON DELETE CASCADE,
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,  -- Added for RLS
  variant_name TEXT NOT NULL,
  storage_path TEXT NOT NULL,
  public_url TEXT NOT NULL,
  blueprint JSONB,  -- Validated against BlueprintSchema
  html_hash TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ,
  metadata JSONB DEFAULT '{}'
);

-- Form submissions
CREATE TABLE lp_submissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  variant_id UUID NOT NULL REFERENCES landing_page_variants(id) ON DELETE CASCADE,
  email TEXT,
  form_data JSONB,
  user_agent TEXT,
  ip_hash TEXT,  -- For rate limiting (hashed, not raw IP)
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Page views
CREATE TABLE lp_pageviews (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  variant_id UUID NOT NULL REFERENCES landing_page_variants(id) ON DELETE CASCADE,
  session_id TEXT NOT NULL,
  user_agent TEXT,
  referrer TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_lp_variants_run ON landing_page_variants(run_id);
CREATE INDEX idx_lp_variants_project ON landing_page_variants(project_id);
CREATE INDEX idx_lp_submissions_variant ON lp_submissions(variant_id);
CREATE INDEX idx_lp_submissions_created ON lp_submissions(created_at);
CREATE INDEX idx_lp_pageviews_variant ON lp_pageviews(variant_id);
CREATE INDEX idx_lp_pageviews_session ON lp_pageviews(session_id);

-- RLS Policies
ALTER TABLE landing_page_variants ENABLE ROW LEVEL SECURITY;
ALTER TABLE lp_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE lp_pageviews ENABLE ROW LEVEL SECURITY;

-- Owners can view their variants
CREATE POLICY "lp_variants_select" ON landing_page_variants
  FOR SELECT USING (project_id IN (
    SELECT id FROM projects WHERE user_id = auth.uid()
  ));

-- Anonymous can insert submissions (public forms)
CREATE POLICY "lp_submissions_insert" ON lp_submissions
  FOR INSERT WITH CHECK (true);

-- Anonymous can insert pageviews (public tracking)
CREATE POLICY "lp_pageviews_insert" ON lp_pageviews
  FOR INSERT WITH CHECK (true);

-- Owners can view submissions for their variants
CREATE POLICY "lp_submissions_select" ON lp_submissions
  FOR SELECT USING (variant_id IN (
    SELECT id FROM landing_page_variants WHERE project_id IN (
      SELECT id FROM projects WHERE user_id = auth.uid()
    )
  ));
```

### Ad Creatives

```sql
-- Ad creative variants
CREATE TABLE ad_creatives (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id UUID NOT NULL REFERENCES validation_runs(id) ON DELETE CASCADE,
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,  -- For RLS
  platform ad_platform NOT NULL,  -- enum: 'meta', 'google', 'linkedin', 'tiktok'
  format TEXT NOT NULL,           -- 'feed', 'story', 'carousel', etc.
  variant_name TEXT NOT NULL,
  storage_path TEXT NOT NULL,
  copy JSONB NOT NULL,            -- {headline, primary_text, description, cta, tone}
  dimensions JSONB NOT NULL,      -- {width: number, height: number}
  created_at TIMESTAMPTZ DEFAULT NOW(),
  metadata JSONB DEFAULT '{}'
);

-- Ad platform submissions
CREATE TABLE ad_submissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  creative_id UUID NOT NULL REFERENCES ad_creatives(id) ON DELETE CASCADE,
  platform ad_platform NOT NULL,
  platform_ad_id TEXT,            -- ID returned by platform
  status ad_submission_status DEFAULT 'pending',  -- enum
  rejection_reason TEXT,
  submitted_at TIMESTAMPTZ DEFAULT NOW(),
  reviewed_at TIMESTAMPTZ,
  metadata JSONB DEFAULT '{}'
);

-- Enums
CREATE TYPE ad_submission_status AS ENUM ('pending', 'submitted', 'approved', 'rejected');

-- Indexes
CREATE INDEX idx_ad_creatives_run ON ad_creatives(run_id);
CREATE INDEX idx_ad_creatives_project ON ad_creatives(project_id);
CREATE INDEX idx_ad_creatives_platform ON ad_creatives(platform);
CREATE INDEX idx_ad_submissions_creative ON ad_submissions(creative_id);
CREATE INDEX idx_ad_submissions_status ON ad_submissions(status);
CREATE INDEX idx_ad_submissions_platform_status ON ad_submissions(platform, status);

-- RLS Policies
ALTER TABLE ad_creatives ENABLE ROW LEVEL SECURITY;
ALTER TABLE ad_submissions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "ad_creatives_select" ON ad_creatives
  FOR SELECT USING (project_id IN (
    SELECT id FROM projects WHERE user_id = auth.uid()
  ));

CREATE POLICY "ad_submissions_select" ON ad_submissions
  FOR SELECT USING (creative_id IN (
    SELECT id FROM ad_creatives WHERE project_id IN (
      SELECT id FROM projects WHERE user_id = auth.uid()
    )
  ));
```

### Drizzle Schema Requirements

**Action Required**: Create Drizzle schemas for all tables.

| Table | Drizzle Schema Status | Action |
|-------|----------------------|--------|
| `landing_page_variants` | Exists (needs update) | Add `project_id`, change `run_id` to UUID |
| `lp_submissions` | **Missing** | Create schema |
| `lp_pageviews` | **Missing** | Create schema |
| `ad_creatives` | **Missing** | Create schema |
| `ad_submissions` | **Missing** | Create schema |

---

## Implementation Status

### Implemented

- [x] Supabase Storage bucket `landing-pages`
- [x] Migration 009 (landing page tables - needs update)
- [x] `LandingPageDeploymentTool` rewritten (~150 lines)

### Pending - Phase 1 (Landing Pages)

- [ ] Update `landing_page_variants` schema (add `project_id`, change `run_id` to UUID FK)
- [ ] Create Drizzle schemas for `lp_submissions`, `lp_pageviews`
- [ ] Create directory structure (`src/templates/landing/`, `src/shared/registries/`)
- [ ] Template procurement (Tailwind UI $299)
- [ ] Component registry implementation (10 components)
- [ ] Blueprint JSON schema (shared TypeScript type)
- [ ] `LandingPageGeneratorTool` with Blueprint Pattern

### Pending - Phase 2 (Ad Creatives)

- [ ] Apply for Canva Developer Partner Program
- [ ] Create Canva Brand Kit
- [ ] Supabase Storage bucket `ad-creatives`
- [ ] Create Drizzle schemas for `ad_creatives`, `ad_submissions`
- [ ] Migration for ad creative tables
- [ ] `AdCreativeGeneratorTool` (copy generation)
- [ ] HITL checkpoint for brand review
- [ ] Meta Ads API integration
- [ ] LinkedIn Ads API integration

---

## Cost Summary

| Item | Type | Cost |
|------|------|------|
| Tailwind UI templates | One-time | $299 |
| Canva Pro | Monthly | $12.99/mo |
| DALL-E 3 (optional) | Per image | $0.04 (budget-capped) |
| Supabase Storage | Included | $0 (within plan) |
| **Total Year 1** | | ~$455 |

---

## Consequences

### Positive

1. **Professional quality**: Conversion-tested templates vs AI-generated layouts
2. **Platform compliance**: Templates enforce spec requirements
3. **Rapid iteration**: Change copy without rebuilding structure
4. **Re-generation**: Blueprint JSON enables rebuilding without full pipeline
5. **Unified storage**: All assets in Supabase (state, files, tracking)
6. **Cost-effective**: ~$455 vs $2,000-5,000 custom design
7. **Brand consistency**: Token injection ensures consistent styling
8. **Type safety**: Zod schema validates blueprint structure

### Negative

1. **Template constraints**: Limited to purchased component library
   - *Mitigation*: 10 components cover 95%+ of validation use cases
2. **Canva API dependency**: Requires partner access for full automation
   - *Mitigation*: HITL workflow available as interim solution
3. **Platform API complexity**: Each ad platform has different APIs
   - *Mitigation*: Start with Meta + LinkedIn only

### Neutral

1. **Learning curve**: Team must learn template customization
2. **Vendor relationships**: Canva partnership requires application process

---

## References

- [Tool Specifications - LandingPageGeneratorTool](../master-architecture/reference/tool-specifications.md)
- [Ad Platform Specifications](../master-architecture/reference/ad-platform-specifications.md)
- [Asset Templates User Stories](../../app.startupai.site/docs/user-experience/stories/infrastructure/asset-templates.md)
- [Phase 2 Desirability Spec](../master-architecture/06-phase-2-desirability.md)
- [Supabase Storage Documentation](https://supabase.com/docs/guides/storage)
- [Canva Connect API](https://www.canva.dev/docs/connect/)

---

## Changelog

| Date | Change |
|------|--------|
| 2026-01-10 | Original ADR-003 created (landing page storage migration) |
| 2026-01-10 | Supabase Storage implementation complete |
| 2026-02-02 | Expanded to Validation Asset Architecture |
| 2026-02-03 | **v2.0**: Incorporated team feedback. Added: Tailwind UI decision, TrustBadges component, Blueprint JSON schema, token injection mechanism, corrected platform character limits (recommended vs max), Canva partnership strategy, tone parameter, indexes and RLS policies, Drizzle schema requirements. Resolved run_id type inconsistency. |

---

## Approval

| Role | Name | Date | Decision |
|------|------|------|----------|
| Founder | Chris Walker | 2026-02-03 | Pending |
| System Architect | Claude | 2026-02-02 | Approved |
| AI Engineer | Claude | 2026-02-03 | Conditional → Approved |
| Frontend Developer | Claude | 2026-02-03 | Conditional → Approved |
| UI Designer | Claude | 2026-02-03 | Conditional → Approved |
| Content Strategist | Claude | 2026-02-03 | Conditional → Approved |
| Data Engineer | Claude | 2026-02-03 | Conditional → Approved |
