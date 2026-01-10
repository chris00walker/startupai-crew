# Supabase MCP Tools

Reference for Supabase Model Context Protocol (MCP) tools available in Claude Code.

## Overview

MCP tools provide direct access to Supabase operations without CLI commands. These tools are integrated into Claude Code and can be used in conversations.

## Available Tools

| Tool | Purpose | Pre-approved |
|------|---------|--------------|
| `mcp__supabase__list_tables` | List all tables in database | Yes |
| `mcp__supabase__list_extensions` | List enabled extensions | Yes |
| `mcp__supabase__execute_sql` | Run SQL queries | Yes |
| `mcp__supabase__apply_migration` | Apply schema migrations | Yes |
| `mcp__supabase__search_docs` | Search Supabase documentation | Yes |
| `mcp__supabase__list_migrations` | List applied migrations | Yes |
| `mcp__supabase__list_projects` | List Supabase projects | Yes |
| `mcp__supabase__get_advisors` | Get database advisors/recommendations | Yes |

## Tool Details

### mcp__supabase__list_tables

List all tables in the database with their schemas.

**Use when**: Need to see database structure, verify table exists, explore schema.

**Example output**:
```
Tables:
- public.projects
- public.validation_runs
- public.hitl_requests
- public.user_profiles
- auth.users
```

### mcp__supabase__list_extensions

List all enabled PostgreSQL extensions.

**Use when**: Checking if extension is available (pgvector, PostGIS, etc.).

**Example output**:
```
Extensions:
- uuid-ossp (public)
- pgcrypto (public)
- vector (public)
- pg_stat_statements (extensions)
```

### mcp__supabase__execute_sql

Execute arbitrary SQL queries against the database.

**Use when**: Running SELECT queries, checking data, debugging.

**Parameters**:
- `query`: SQL query to execute

**Examples**:
```sql
-- List columns in a table
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'validation_runs';

-- Check row counts
SELECT
  (SELECT COUNT(*) FROM projects) as projects,
  (SELECT COUNT(*) FROM validation_runs) as runs;

-- Query specific data
SELECT id, status, current_phase
FROM validation_runs
WHERE status = 'running'
LIMIT 10;
```

### mcp__supabase__apply_migration

Apply a schema migration to the database.

**Use when**: Creating tables, adding columns, modifying schema.

**Parameters**:
- `name`: Migration name (descriptive, snake_case)
- `query`: SQL migration to apply

**Example**:
```sql
-- Name: add_hitl_priority_column
-- Query:
ALTER TABLE hitl_requests
ADD COLUMN priority TEXT DEFAULT 'normal'
CHECK (priority IN ('low', 'normal', 'high', 'urgent'));

CREATE INDEX idx_hitl_priority ON hitl_requests(priority);
```

### mcp__supabase__search_docs

Search Supabase documentation for specific topics.

**Use when**: Need official documentation on Supabase features.

**Parameters**:
- `query`: Search query

**Example queries**:
- "Row Level Security policies"
- "pgvector similarity search"
- "Realtime subscriptions"
- "Edge Functions deployment"

### mcp__supabase__list_migrations

List all applied migrations with timestamps.

**Use when**: Checking migration history, debugging deployment issues.

**Example output**:
```
Migrations:
- 20240101000000_initial_schema (applied: 2024-01-01)
- 20240115120000_add_validation_runs (applied: 2024-01-15)
- 20240120090000_add_hitl_requests (applied: 2024-01-20)
```

### mcp__supabase__list_projects

List all Supabase projects in the organization.

**Use when**: Finding project IDs, verifying project exists.

### mcp__supabase__get_advisors

Get database performance and security recommendations.

**Use when**: Optimizing database, checking for issues.

## Common Workflows

### Exploring Database Structure

```
1. mcp__supabase__list_tables
   → See all tables

2. mcp__supabase__execute_sql
   Query: SELECT * FROM information_schema.columns
          WHERE table_name = 'validation_runs'
   → See column details

3. mcp__supabase__execute_sql
   Query: SELECT * FROM validation_runs LIMIT 5
   → Sample data
```

### Adding a New Column

```
1. mcp__supabase__list_tables
   → Verify table exists

2. mcp__supabase__apply_migration
   Name: add_progress_percent_column
   Query: ALTER TABLE validation_runs
          ADD COLUMN progress_percent INTEGER DEFAULT 0;

3. mcp__supabase__execute_sql
   Query: SELECT column_name FROM information_schema.columns
          WHERE table_name = 'validation_runs'
   → Verify column added
```

### Checking RLS Policies

```
mcp__supabase__execute_sql
Query:
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies
WHERE schemaname = 'public';
```

### Looking Up Documentation

```
mcp__supabase__search_docs
Query: "pgvector similarity search with embeddings"

mcp__supabase__search_docs
Query: "Row Level Security best practices"
```

## StartupAI Usage Patterns

### Check Validation Run Status

```sql
-- Using execute_sql
SELECT id, status, current_phase,
       phase_state->>'current_crew' as current_crew,
       updated_at
FROM validation_runs
WHERE status IN ('running', 'awaiting_approval')
ORDER BY updated_at DESC;
```

### View HITL Queue

```sql
SELECT hr.id, hr.checkpoint_name, hr.status,
       vr.project_id, p.name as project_name
FROM hitl_requests hr
JOIN validation_runs vr ON hr.run_id = vr.id
JOIN projects p ON vr.project_id = p.id
WHERE hr.status = 'pending'
ORDER BY hr.created_at;
```

### Check Table Sizes

```sql
SELECT
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname || '.' || tablename)) as size,
  n_live_tup as row_count
FROM pg_tables
JOIN pg_stat_user_tables ON tablename = relname
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname || '.' || tablename) DESC;
```

## Best Practices

1. **Use search_docs first** - Check documentation before implementing
2. **Preview migrations** - Review SQL before applying
3. **Use descriptive migration names** - Make history readable
4. **Query carefully in production** - Large queries can impact performance
5. **Check advisors regularly** - Catch issues early

## Limitations

- MCP tools operate on the connected Supabase project
- Large result sets may be truncated
- DDL operations require appropriate permissions
- Some operations may require dashboard access

## External Resources

- [Supabase MCP Server](https://github.com/supabase/supabase-mcp)
- [MCP Protocol](https://modelcontextprotocol.io/)
