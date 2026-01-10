# Supabase Migrations

Guide to database schema migrations and version control with Supabase CLI.

## Overview

Supabase migrations are SQL files that track schema changes over time, enabling:
- Version-controlled database schema
- Reproducible deployments across environments
- Team collaboration on schema changes
- Rollback capabilities

## Migration Files

Migrations are stored in `supabase/migrations/` with timestamped filenames:

```
supabase/
├── migrations/
│   ├── 20240101000000_initial_schema.sql
│   ├── 20240115120000_add_validation_runs.sql
│   └── 20240120090000_add_hitl_requests.sql
└── config.toml
```

## Core Commands

### Initialize Project

```bash
# Initialize Supabase in current directory
supabase init

# Creates supabase/ directory with config.toml
```

### Link to Remote Project

```bash
# Link local to remote Supabase project
supabase link --project-ref <project-id>

# Project ID from: supabase.com/dashboard/project/PROJECT_ID
```

### Create New Migration

```bash
# Create empty migration file
supabase migration new add_user_profiles

# Creates: supabase/migrations/20240120120000_add_user_profiles.sql
```

### Apply Migrations Locally

```bash
# Start local Supabase stack
supabase start

# Apply pending migrations to local database
supabase db reset  # Resets and applies all migrations
```

### Push to Remote

```bash
# Push local migrations to remote project
supabase db push

# With dry-run (preview changes)
supabase db push --dry-run
```

### Pull Remote Schema

```bash
# Pull remote schema as migration
supabase db pull

# Creates migration file from remote schema diff
```

### Diff Schema

```bash
# Show diff between local and remote
supabase db diff

# Output diff as migration file
supabase db diff --file add_new_table
```

## Migration File Structure

```sql
-- supabase/migrations/20240120120000_add_validation_runs.sql

-- Create table
CREATE TABLE IF NOT EXISTS validation_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  status TEXT NOT NULL DEFAULT 'pending',
  current_phase INTEGER DEFAULT 0,
  phase_state JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE validation_runs ENABLE ROW LEVEL SECURITY;

-- Create policy
CREATE POLICY "Users view own validation runs"
ON validation_runs FOR SELECT
TO authenticated
USING (
  project_id IN (
    SELECT id FROM projects WHERE owner_id = auth.uid()
  )
);

-- Create index
CREATE INDEX idx_validation_runs_project_id
ON validation_runs(project_id);

-- Add trigger for updated_at
CREATE TRIGGER update_validation_runs_updated_at
  BEFORE UPDATE ON validation_runs
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
```

## Common Patterns

### Adding a Column

```sql
-- Add nullable column (no data migration needed)
ALTER TABLE profiles ADD COLUMN avatar_url TEXT;

-- Add column with default (safe for existing rows)
ALTER TABLE profiles ADD COLUMN is_verified BOOLEAN DEFAULT false;
```

### Adding Foreign Key

```sql
-- Add reference column
ALTER TABLE validation_runs
ADD COLUMN owner_id UUID REFERENCES auth.users(id);

-- Backfill existing data
UPDATE validation_runs vr
SET owner_id = p.owner_id
FROM projects p
WHERE vr.project_id = p.id;

-- Make NOT NULL after backfill
ALTER TABLE validation_runs
ALTER COLUMN owner_id SET NOT NULL;
```

### Creating Index

```sql
-- Standard B-tree index
CREATE INDEX idx_runs_status ON validation_runs(status);

-- Composite index
CREATE INDEX idx_runs_project_status
ON validation_runs(project_id, status);

-- Partial index (only index certain rows)
CREATE INDEX idx_runs_pending
ON validation_runs(created_at)
WHERE status = 'pending';
```

### Adding RLS Policy

```sql
-- Enable RLS first
ALTER TABLE my_table ENABLE ROW LEVEL SECURITY;

-- Then create policies
CREATE POLICY "policy_name"
ON my_table FOR SELECT
TO authenticated
USING (condition);
```

## Seeding Data

```bash
# Seed file location
supabase/seed.sql

# Run seeds after migrations
supabase db reset  # Applies migrations then seeds
```

```sql
-- supabase/seed.sql
INSERT INTO categories (name, slug) VALUES
  ('Technology', 'technology'),
  ('Business', 'business'),
  ('Marketing', 'marketing');
```

## Working with Types

### Generate TypeScript Types

```bash
# From local database
supabase gen types typescript --local > src/types/database.ts

# From remote database
supabase gen types typescript --project-id <project-id> > src/types/database.ts
```

### Using Generated Types

```typescript
import { Database } from './types/database'

type ValidationRun = Database['public']['Tables']['validation_runs']['Row']
type InsertValidationRun = Database['public']['Tables']['validation_runs']['Insert']
type UpdateValidationRun = Database['public']['Tables']['validation_runs']['Update']
```

## Migration Best Practices

### 1. Keep Migrations Small
```sql
-- Good: Single focused change
ALTER TABLE profiles ADD COLUMN bio TEXT;

-- Bad: Multiple unrelated changes in one file
```

### 2. Make Migrations Idempotent
```sql
-- Use IF NOT EXISTS / IF EXISTS
CREATE TABLE IF NOT EXISTS my_table (...);
DROP TABLE IF EXISTS old_table;
CREATE INDEX IF NOT EXISTS idx_name ON table(column);
```

### 3. Test Locally First
```bash
# Always test locally before pushing
supabase db reset
# Run app, verify behavior
supabase db push --dry-run
supabase db push
```

### 4. Handle Data Migrations Carefully
```sql
-- 1. Add new column as nullable
ALTER TABLE users ADD COLUMN display_name TEXT;

-- 2. Backfill data
UPDATE users SET display_name = COALESCE(nickname, email);

-- 3. Add constraint after backfill
ALTER TABLE users ALTER COLUMN display_name SET NOT NULL;
```

## Troubleshooting

### Migration Conflicts
```bash
# List applied migrations
supabase migration list

# Check remote migration history
supabase db remote migrations

# Force repair (dangerous - use carefully)
supabase migration repair --status applied 20240120120000
```

### Reset Local Database
```bash
# Full reset (drops all data)
supabase db reset

# Keep data but reapply migrations
supabase db reset --keep-data
```

### Debugging Migration Errors
```bash
# Run with verbose output
supabase db push --debug

# Check logs
supabase logs --service db
```

## CI/CD Integration

```yaml
# GitHub Actions example
- name: Setup Supabase CLI
  uses: supabase/setup-cli@v1

- name: Link project
  run: supabase link --project-ref ${{ secrets.SUPABASE_PROJECT_ID }}
  env:
    SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}

- name: Run migrations
  run: supabase db push
```

## External Resources

- [Supabase CLI Docs](https://supabase.com/docs/guides/cli)
- [Database Migrations Guide](https://supabase.com/docs/guides/cli/managing-environments)
- [Local Development](https://supabase.com/docs/guides/cli/local-development)
