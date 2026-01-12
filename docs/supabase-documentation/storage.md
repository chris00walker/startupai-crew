# Supabase Storage

Supabase Storage provides S3-compatible object storage with CDN delivery and fine-grained access control.

**Source**: https://supabase.com/docs/guides/storage
**Fetched**: 2026-01-10

---

## Overview

Supabase Storage is designed for user-generated content, media libraries, and asset management. It supports files of any size with:

- **Global CDN delivery** - Serve assets with lightning-fast performance from over 285 cities worldwide
- **Direct URL access for files** - Public or authenticated access
- **Fine-grained Access Control** - Row-level security and custom policies

## Capabilities

### File Serving
- Supports files of any size
- Direct URL access to stored files
- Global CDN with 285+ edge locations

### Access Control
- Row-level security (RLS) policies
- Custom policies for fine-grained permissions
- Public bucket support (exact configuration not documented in overview)

### Performance
- Lightning-fast global delivery via CDN
- Optimized for media and asset delivery
- Specific metrics (latency, throughput) not provided

## Limitations for Landing Page Hosting

**Not covered in official docs**:
- Static HTML hosting capabilities (not explicitly mentioned)
- Custom domain support (not documented)
- Index file handling (e.g., `index.html` for directories)
- Public bucket configuration details

## Primary Use Cases

Storage is positioned for:
- User-generated content
- Media libraries
- Asset management

**Not designed for**:
- Static site hosting
- HTML landing page serving

## Key Takeaway

Supabase Storage is a general-purpose file storage solution optimized for media and assets. The documentation does not position it as a static site hosting platform. For landing pages, consider:
1. Netlify (primary hosting)
2. Supabase Edge Functions (dynamic HTML generation)
3. Traditional static hosting solutions

---

## Related Documentation

- [Edge Functions](./edge-functions.md) - Alternative for dynamic HTML serving
- [Netlify Docs](../netlify-documentation/) - Primary landing page hosting
- [StartupAI Patterns](./startupai-patterns.md) - Deployment tracking
