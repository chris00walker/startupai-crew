# Supabase Edge Functions

Supabase Edge Functions are server-side TypeScript functions distributed globally for low-latency operations.

**Source**: https://supabase.com/docs/guides/functions
**Fetched**: 2026-01-10

---

## Overview

Edge Functions are **server-side TypeScript functions** that handle HTTP requests with global distribution. They're optimized for short-lived, idempotent operations rather than traditional web hosting.

## Capabilities

### Execution Model
- Globally distributed for low-latency
- Short-lived, idempotent operations
- HTTP request handling (can return any content type)

### Performance
- Optimized for low-latency operations
- **Cold starts are possible** - design for short-lived tasks
- Not suitable for long-running processes

### Database Integration
- Special handling required for Postgres connections
- Treat Postgres as a remote, pooled service
- Database connections require connection pooling

## Deployment Workflow

Three deployment methods:
1. **Supabase Dashboard** - UI-based deployment
2. **CLI** - `supabase functions serve` (local dev) + `supabase functions deploy`
3. **MCP** - Model Context Protocol integration

Local development provides production parity for faster iteration.

## Limitations

### Not Designed For
- Full webpage serving (heavy processing)
- Long-running operations
- Always-on web servers

### Key Constraints
- Cold starts on first invocation
- Limited to serverless-friendly workloads
- Database connection overhead
- No persistent state (use Supabase Database)

## Recommended Use Cases

Edge Functions excel for:
- **Webhook receivers** (Stripe, GitHub)
- **Image/Open Graph generation** (dynamic metadata)
- **Transactional emails** (SendGrid, Resend)
- **Bot endpoints** (Discord, Slack, Telegram)
- **AI inference orchestration** (OpenAI, Anthropic)

## HTML Response Capability

**Not explicitly documented**, but Edge Functions can return any HTTP response type, including HTML. However:

- Positioned for specific tasks, not full page serving
- Cold start overhead on first invocation
- No static file optimization (compared to CDN)

**For traditional webpage serving, use traditional hosting** (Netlify, Vercel, Cloudflare Pages).

## Custom Domain Support

**Not documented in overview** - check full Edge Functions documentation for custom domain configuration.

---

## StartupAI Context

For landing page deployment, Edge Functions could theoretically serve HTML but are **not the right tool** for this use case:

1. **Cold starts** - First page load may be slow
2. **No static optimization** - No CDN caching of HTML assets
3. **Positioned for serverless tasks** - Not static hosting

**Recommendation**: Use Netlify for landing pages, use Edge Functions for:
- Webhook processing (experiment results)
- Dynamic Open Graph image generation
- Email notification triggers

---

## Related Documentation

- [Storage](./storage.md) - Alternative for static file hosting
- [Netlify Docs](../netlify-documentation/) - Primary landing page hosting
- [StartupAI Patterns](./startupai-patterns.md) - Deployment tracking
