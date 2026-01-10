# Supabase Documentation Index

Quick reference for Supabase database and backend patterns used in the StartupAI ecosystem.

**Last Updated**: 2026-01-09
**Supabase JS SDK**: v2.x
**MCP Tools Available**: Yes (8+ tools)

## Cache Status

| Metric | Value |
|--------|-------|
| **Last Full Sync** | 2026-01-09 |
| **Staleness Threshold** | 30 days |
| **Total Cached Files** | 8 |
| **Missing Topics** | 4 (see below) |
| **Cache Manifest** | `MANIFEST.json` |

> **Self-Learning Cache**: This documentation cache automatically updates when new content is fetched from online sources. Check MANIFEST.json for detailed tracking.

---

## Quick Topic Reference

| Topic | File | Key Content |
|-------|------|-------------|
| **Row Level Security** | `rls.md` | Policies, `auth.uid()`, `USING`/`WITH CHECK` |
| **Realtime** | `realtime.md` | Channels, Postgres Changes, Broadcast, Presence |
| **Migrations** | `migrations.md` | Schema migrations, `supabase db` commands |
| **MCP Tools** | `mcp-tools.md` | Available MCP tools, usage patterns |
| **CLI Reference** | `cli-reference.md` | `supabase init`, `db push`, `functions deploy` |
| **StartupAI Patterns** | `startupai-patterns.md` | State persistence, HITL tables, schema |

---

## Quick Lookup by Keyword

| Keyword/Pattern | Go To |
|-----------------|-------|
| RLS, Row Level Security, policy | `rls.md` |
| `auth.uid()`, `auth.jwt()`, authentication | `rls.md` |
| `USING`, `WITH CHECK`, policy syntax | `rls.md` |
| Realtime, subscription, channel | `realtime.md` |
| Broadcast, Presence, Postgres Changes | `realtime.md` |
| `.subscribe()`, `.on()`, WebSocket | `realtime.md` |
| Migration, schema, `db push`, `db pull` | `migrations.md` |
| `supabase migration new`, version control | `migrations.md` |
| MCP, `mcp__supabase__*`, tool | `mcp-tools.md` |
| `execute_sql`, `apply_migration`, `list_tables` | `mcp-tools.md` |
| CLI, `supabase init`, `supabase start` | `cli-reference.md` |
| Edge Functions, `functions deploy` | `cli-reference.md` |
| HITL, validation_runs, approval_queue | `startupai-patterns.md` |
| State persistence, checkpoint, Supabase | `startupai-patterns.md` |

---

## StartupAI-Specific Patterns

For StartupAI's Supabase usage, these are the most relevant:

1. **State Persistence** -> `startupai-patterns.md`
   - `validation_runs`, `hitl_requests`, phase state

2. **Realtime Updates** -> `realtime.md`
   - WebSocket subscriptions for UI progress

3. **RLS Policies** -> `rls.md`
   - User data isolation, project ownership

4. **MCP Tools** -> `mcp-tools.md`
   - `execute_sql`, `apply_migration` for development

---

## Topics NOT in This Cache

This cache covers ~8 essential patterns. For these topics, **use WebFetch** or MCP tools:

| Topic | Online URL / MCP Tool |
|-------|----------------------|
| Auth | https://supabase.com/docs/guides/auth |
| Storage | https://supabase.com/docs/guides/storage |
| Edge Functions | https://supabase.com/docs/guides/functions |
| pgvector | `mcp__supabase__search_docs` with "pgvector" |

**For comprehensive searches**:
```
mcp__supabase__search_docs: "your topic here"
```

---

## MCP Tools Available

The following Supabase MCP tools are available for direct use:

| Tool | Purpose |
|------|---------|
| `mcp__supabase__list_tables` | List all tables in database |
| `mcp__supabase__list_extensions` | List enabled extensions |
| `mcp__supabase__execute_sql` | Run SQL queries |
| `mcp__supabase__apply_migration` | Apply schema migrations |
| `mcp__supabase__search_docs` | Search Supabase documentation |
| `mcp__supabase__list_migrations` | List applied migrations |
| `mcp__supabase__list_projects` | List Supabase projects |
| `mcp__supabase__get_advisors` | Get database advisors |

---

## External Resources

- **Official Docs**: https://supabase.com/docs
- **Dashboard**: https://supabase.com/dashboard
- **GitHub**: https://github.com/supabase/supabase
- **Discord**: https://discord.supabase.com

---

## Usage Tips

1. **Before implementing**: Read the relevant doc file first
2. **Use MCP tools**: Prefer `mcp__supabase__search_docs` for comprehensive searches
3. **Check StartupAI patterns**: Reference `startupai-patterns.md` for ecosystem-specific guidance
4. **If topic not found**: Use WebFetch or MCP search
