# Row Level Security (RLS)

Comprehensive guide to PostgreSQL Row Level Security in Supabase for fine-grained data access control.

## Overview

RLS is a PostgreSQL feature that enables granular authorization by automatically filtering database queries based on user identity. Supabase integrates RLS with authentication to provide end-to-end security from browser to database.

**Critical Rule**: RLS must ALWAYS be enabled on any tables stored in an exposed schema (default: `public`).

## Enabling RLS

```sql
-- Enable RLS on existing table
ALTER TABLE table_name ENABLE ROW LEVEL SECURITY;

-- Tables created via Supabase dashboard have RLS enabled automatically
```

## Policy Syntax

```sql
CREATE POLICY policy_name
ON table_name
FOR operation           -- SELECT, INSERT, UPDATE, DELETE, ALL
TO role                 -- anon, authenticated, or custom role
USING (condition)       -- Filter existing rows (reads/updates/deletes)
WITH CHECK (condition); -- Validate new/modified rows (inserts/updates)
```

## Authentication Roles

Supabase maps requests to two Postgres roles:

| Role | Description |
|------|-------------|
| `anon` | Unauthenticated users (no access token) |
| `authenticated` | Logged-in users with valid JWT |

## Helper Functions

### auth.uid()
Returns the current user's UUID from the JWT. Returns `null` for unauthenticated requests.

```sql
-- Get current user ID
SELECT auth.uid();

-- Use in policy
CREATE POLICY "Users read own data"
ON profiles FOR SELECT
TO authenticated
USING (auth.uid() = user_id);
```

### auth.jwt()
Access JWT claims for advanced authorization.

```sql
-- Access custom claims
SELECT auth.jwt()->>'role';

-- Check MFA level
WHERE (auth.jwt()->>'aal') = 'aal2'
```

**Warning**: `raw_user_meta_data` can be modified by users. Store authorization data in `raw_app_meta_data` instead.

## Common Policy Patterns

### SELECT (Read) Policy

```sql
-- Users can only read their own data
CREATE POLICY "Users view own data"
ON profiles
FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

-- Public read access
CREATE POLICY "Public read access"
ON posts
FOR SELECT
TO anon, authenticated
USING (published = true);
```

### INSERT Policy

```sql
-- Users can only insert their own data
CREATE POLICY "Users create own profiles"
ON profiles
FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);
```

### UPDATE Policy

```sql
-- Users can only update their own data
-- USING: checks current row
-- WITH CHECK: validates new values
CREATE POLICY "Users update own profile"
ON profiles
FOR UPDATE
TO authenticated
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);
```

### DELETE Policy

```sql
-- Users can only delete their own data
CREATE POLICY "Users delete own profile"
ON profiles
FOR DELETE
TO authenticated
USING (auth.uid() = user_id);
```

## Advanced Patterns

### Project-Based Access (StartupAI Pattern)

```sql
-- Users can access projects they own or are members of
CREATE POLICY "Project access"
ON validation_runs
FOR SELECT
TO authenticated
USING (
  project_id IN (
    SELECT id FROM projects WHERE owner_id = auth.uid()
    UNION
    SELECT project_id FROM project_members WHERE user_id = auth.uid()
  )
);
```

### Role-Based Access

```sql
-- Admin access
CREATE POLICY "Admin full access"
ON all_tables
FOR ALL
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM user_roles
    WHERE user_id = auth.uid()
    AND role = 'admin'
  )
);
```

### Service Role Bypass

```sql
-- Create a role that bypasses RLS for administrative tasks
ALTER ROLE service_role WITH BYPASSRLS;
```

**Warning**: Never expose service role credentials in client-side code.

## Performance Optimization

### 1. Index Policy Columns

```sql
-- Add indexes on columns used in policies
CREATE INDEX idx_profiles_user_id ON profiles(user_id);
CREATE INDEX idx_projects_owner_id ON projects(owner_id);
```

### 2. Cache auth.uid()

```sql
-- Wrap in SELECT for caching
CREATE POLICY "Optimized policy"
ON profiles FOR SELECT
TO authenticated
USING (user_id = (SELECT auth.uid()));
```

### 3. Specify Roles Explicitly

```sql
-- Specify role to avoid unnecessary policy evaluation
CREATE POLICY "Authenticated only"
ON private_data FOR SELECT
TO authenticated  -- Not TO public
USING (auth.uid() = owner_id);
```

### 4. Add Explicit Filters in Queries

```sql
-- Client-side: always include ownership filter
const { data } = await supabase
  .from('profiles')
  .select('*')
  .eq('user_id', userId);  // Match policy condition
```

## Null Handling

When `auth.uid()` returns null (unauthenticated):

```sql
-- This fails silently (null = anything is always false)
USING (auth.uid() = user_id)

-- Explicit null check for clarity
USING (auth.uid() IS NOT NULL AND auth.uid() = user_id)
```

## Views and RLS

Views bypass RLS by default. In PostgreSQL 15+:

```sql
-- Force RLS on view's underlying tables
CREATE VIEW my_view
WITH (security_invoker = true)
AS SELECT * FROM my_table;
```

## Testing Policies

```sql
-- Test as specific user
SET request.jwt.claims = '{"sub": "user-uuid-here"}';
SET ROLE authenticated;

-- Run query
SELECT * FROM profiles;

-- Reset
RESET ROLE;
```

## Common Mistakes

1. **Forgetting to enable RLS** - All public tables MUST have RLS enabled
2. **Using `TO public`** - Be explicit with `TO anon` or `TO authenticated`
3. **Not indexing policy columns** - Causes slow queries on large tables
4. **Trusting `raw_user_meta_data`** - Users can modify this; use `raw_app_meta_data`
5. **Circular dependencies** - Policy references table that references policy

## External Resources

- [Supabase RLS Docs](https://supabase.com/docs/guides/auth/row-level-security)
- [PostgreSQL RLS Docs](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
