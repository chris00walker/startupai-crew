---
purpose: Supabase configuration for Modal serverless architecture
status: planning
last_reviewed: 2026-01-08
vpd_compliance: true
---

# Supabase Configuration

> **Modal Migration**: This document supports the Modal serverless architecture. See [ADR-002](../../adr/002-modal-serverless-migration.md) for migration context.

This document defines Supabase setup for the Modal serverless architecture, including Realtime, RLS policies, and migration patterns.

---

## Overview

Supabase serves as the **Orchestration Layer** in the three-layer architecture:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  INTERACTION LAYER (Netlify/Product App)                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  ORCHESTRATION LAYER (Supabase) ← THIS DOCUMENT                            │
│  • State persistence (PostgreSQL)                                           │
│  • Real-time updates (WebSocket)                                            │
│  • Approval queue management                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  COMPUTE LAYER (Modal)                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Realtime Configuration

### Tables Enabled for Realtime

| Table | Events | Purpose |
|-------|--------|---------|
| `validation_progress` | INSERT | Real-time progress updates |
| `hitl_requests` | INSERT, UPDATE | HITL approval notifications |

### Publication Setup

```sql
-- TODO: Add during implementation
-- Enable Realtime for specific tables
```

### Client Subscription Pattern

```typescript
// TODO: Add TypeScript example
// Subscribe to validation_progress for run_id
```

---

## Row Level Security (RLS)

### Policy Design Principles

1. **User isolation**: Users can only access their own projects
2. **Service role bypass**: Modal functions use service role key
3. **Minimal permissions**: Only grant what's needed

### validation_runs Policies

```sql
-- TODO: Define RLS policies
-- SELECT: user can read own projects
-- UPDATE: user can update own projects (for HITL)
```

### validation_progress Policies

```sql
-- TODO: Define RLS policies
-- SELECT: user can read own run's progress
-- INSERT: service role only (from Modal)
```

### hitl_requests Policies

```sql
-- TODO: Define RLS policies
-- SELECT: user can read own requests
-- UPDATE: user can approve own requests
-- INSERT: service role only (from Modal)
```

---

## Service Role Usage

### When to Use Service Role

- Modal functions writing to `validation_runs`
- Modal functions inserting `validation_progress`
- Modal functions creating `hitl_requests`

### Security Considerations

- Service role key **never** exposed to client
- Service role key stored in Modal Secrets
- Product app uses anon key + user JWT

---

## Edge Functions (Optional)

### Rate Limiting Wrapper

```typescript
// TODO: Consider if needed
// Wrap Modal calls with rate limiting
```

### Webhook Signature Validation

```typescript
// TODO: Consider if needed
// Validate Modal webhook signatures
```

---

## Migration SQL

See [database-schemas.md](./database-schemas.md) for table definitions.

### Modal Tables Summary

| Table | Status | Purpose |
|-------|--------|---------|
| `validation_runs` | PLANNED | Run state and phase outputs |
| `validation_progress` | PLANNED | Real-time progress events |
| `hitl_requests` | PLANNED | Approval queue |

---

## Related Documents

- [database-schemas.md](./database-schemas.md) - Table definitions and indexes
- [modal-configuration.md](./modal-configuration.md) - Modal platform setup
- [state-schemas.md](./state-schemas.md) - Pydantic state models
- [product-app-integration.md](./product-app-integration.md) - Client-side integration
- [ADR-002](../../adr/002-modal-serverless-migration.md) - Modal migration decision

---
**Last Updated**: 2026-01-08
**Status**: Planning stub - full content TBD during Modal implementation
