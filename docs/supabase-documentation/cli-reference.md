# Supabase CLI Reference

Complete command reference for the Supabase CLI.

## Installation

```bash
# macOS
brew install supabase/tap/supabase

# npm (cross-platform)
npm install -g supabase

# Linux (deb)
sudo apt install supabase
```

## Authentication

```bash
# Login to Supabase
supabase login

# Check login status
supabase projects list
```

## Project Setup

### Initialize Local Project

```bash
# Initialize Supabase in current directory
supabase init

# Creates:
# supabase/
# ├── config.toml
# ├── migrations/
# └── seed.sql
```

### Link to Remote Project

```bash
# Link local project to remote
supabase link --project-ref <project-id>

# Project ID from dashboard URL:
# supabase.com/dashboard/project/PROJECT_ID

# With password prompt
supabase link --project-ref abc123 --password
```

### Unlink Project

```bash
supabase unlink
```

## Local Development

### Start Local Stack

```bash
# Start all Supabase services locally
supabase start

# Services started:
# - PostgreSQL (port 54322)
# - Studio (port 54323)
# - API (port 54321)
# - Auth (port 54321)
# - Realtime
# - Storage
```

### Stop Local Stack

```bash
# Stop all services
supabase stop

# Stop and remove volumes (reset data)
supabase stop --no-backup
```

### Check Status

```bash
supabase status

# Output:
#   API URL: http://localhost:54321
#   DB URL: postgresql://postgres:postgres@localhost:54322/postgres
#   Studio URL: http://localhost:54323
#   Anon key: eyJ...
#   Service role key: eyJ...
```

## Database Commands

### Migrations

```bash
# Create new migration
supabase migration new <name>
# Creates: supabase/migrations/TIMESTAMP_name.sql

# List migrations
supabase migration list

# Repair migration status
supabase migration repair --status applied <timestamp>
supabase migration repair --status reverted <timestamp>
```

### Database Operations

```bash
# Show local/remote diff
supabase db diff

# Save diff as migration
supabase db diff --file <name>

# Push migrations to remote
supabase db push

# Preview push (dry run)
supabase db push --dry-run

# Pull remote schema
supabase db pull

# Reset local database (reapply all migrations + seeds)
supabase db reset

# Reset keeping data
supabase db reset --keep-data

# Execute SQL against remote
supabase db execute --sql "SELECT * FROM users LIMIT 10"
```

### Seed Data

```bash
# Seeds are in supabase/seed.sql
# Applied automatically after migrations on reset
supabase db reset
```

## Edge Functions

### Create Function

```bash
# Create new Edge Function
supabase functions new <name>

# Creates: supabase/functions/<name>/index.ts
```

### Local Development

```bash
# Serve functions locally
supabase functions serve

# Serve specific function
supabase functions serve <name>

# With environment variables
supabase functions serve --env-file .env.local
```

### Deploy Functions

```bash
# Deploy all functions
supabase functions deploy

# Deploy specific function
supabase functions deploy <name>

# Deploy without JWT verification
supabase functions deploy <name> --no-verify-jwt
```

### Manage Functions

```bash
# List deployed functions
supabase functions list

# Delete function
supabase functions delete <name>
```

## Secrets Management

```bash
# Set secret(s)
supabase secrets set KEY=value
supabase secrets set KEY1=value1 KEY2=value2

# List secrets
supabase secrets list

# Unset secret
supabase secrets unset KEY
```

## Type Generation

```bash
# Generate TypeScript types from local database
supabase gen types typescript --local > src/types/database.ts

# Generate from remote database
supabase gen types typescript --project-id <id> > src/types/database.ts

# Generate from linked project
supabase gen types typescript --linked > src/types/database.ts
```

## Branching (Preview Branches)

```bash
# List branches
supabase branches list

# Create branch
supabase branches create <name>

# Delete branch
supabase branches delete <name>

# Switch to branch
supabase branches switch <name>
```

## Inspection Commands

```bash
# Inspect database
supabase inspect db <query>

# View service logs
supabase logs
supabase logs --service api
supabase logs --service auth
supabase logs --service db
supabase logs --service realtime
supabase logs --service storage
```

## Testing

```bash
# Run pgTAP tests
supabase test db

# Run specific test file
supabase test db --file tests/my_test.sql
```

## Configuration

### config.toml

```toml
# supabase/config.toml

[api]
port = 54321
schemas = ["public", "graphql_public"]
extra_search_path = ["public", "extensions"]
max_rows = 1000

[db]
port = 54322
major_version = 15

[studio]
port = 54323

[auth]
site_url = "http://localhost:3000"
additional_redirect_urls = ["http://localhost:3000"]

[auth.email]
enable_signup = true
enable_confirmations = false
```

## CI/CD Commands

```bash
# For automated deployments
supabase link --project-ref $PROJECT_ID
supabase db push

# Using access token (no interactive login)
SUPABASE_ACCESS_TOKEN=xxx supabase db push
```

## Troubleshooting

### Debug Mode

```bash
# Run any command with debug output
supabase --debug <command>
supabase --debug db push
```

### Common Issues

```bash
# Docker not running
supabase start
# Error: Cannot connect to Docker daemon
# Fix: Start Docker Desktop

# Port conflicts
supabase start
# Error: Port 54321 already in use
# Fix: Stop other services or change port in config.toml

# Migration conflicts
supabase db push
# Error: Migration xyz already applied
# Fix: supabase migration repair --status reverted xyz
```

### Reset Everything

```bash
# Nuclear option - reset all local data
supabase stop --no-backup
supabase start
supabase db reset
```

## Quick Reference Card

| Command | Purpose |
|---------|---------|
| `supabase init` | Initialize project |
| `supabase start` | Start local stack |
| `supabase stop` | Stop local stack |
| `supabase status` | Show local URLs/keys |
| `supabase link` | Link to remote project |
| `supabase db push` | Push migrations to remote |
| `supabase db pull` | Pull remote schema |
| `supabase db diff` | Show schema diff |
| `supabase db reset` | Reset local database |
| `supabase migration new` | Create migration |
| `supabase gen types` | Generate TypeScript types |
| `supabase functions deploy` | Deploy Edge Functions |
| `supabase secrets set` | Set secrets |

## External Resources

- [Supabase CLI Docs](https://supabase.com/docs/reference/cli)
- [CLI GitHub](https://github.com/supabase/cli)
- [Local Development Guide](https://supabase.com/docs/guides/cli/local-development)
