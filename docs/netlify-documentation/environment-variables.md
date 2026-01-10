# Netlify Environment Variables

Guide to managing environment variables in Netlify for secure configuration across contexts.

## Overview

Netlify environment variables store sensitive configuration values that your site needs to build and run. They can be scoped to specific contexts (production, preview, branch) and are injected during build and at runtime.

## Setting Environment Variables

### Via Netlify UI

1. Go to **Site configuration** > **Environment variables**
2. Click **Add a variable**
3. Enter key and value
4. Select scopes and contexts

### Via CLI

```bash
# Set variable
netlify env:set KEY value

# Set with specific context
netlify env:set KEY value --context production
netlify env:set KEY value --context deploy-preview
netlify env:set KEY value --context branch-deploy

# Get variable
netlify env:get KEY

# List all variables
netlify env:list

# Delete variable
netlify env:unset KEY

# Import from .env file
netlify env:import .env
```

### Via API / MCP

```
mcp__netlify__set_env_vars: { site_id: "xxx", variables: { KEY: "value" } }
mcp__netlify__get_env_vars: { site_id: "xxx" }
mcp__netlify__delete_env_var: { site_id: "xxx", key: "KEY" }
```

## Scopes

Environment variables can be limited to specific parts of your site:

| Scope | Description |
|-------|-------------|
| **Builds** | Available during build process |
| **Functions** | Available in serverless functions |
| **Post processing** | Available during post-processing |
| **Runtime** | Available to Edge Functions |

**Default**: All scopes enabled

## Contexts

Variables can be set for specific deploy contexts:

| Context | Description |
|---------|-------------|
| **All** | All deploys |
| **Production** | Production branch only |
| **Deploy Preview** | Pull request previews |
| **Branch Deploy** | Specific branch deploys |
| **Dev** | Local development (`netlify dev`) |

## Context-Specific Values

Same variable, different values per context:

```toml
# netlify.toml

[context.production.environment]
  API_URL = "https://api.startupai.site"

[context.deploy-preview.environment]
  API_URL = "https://staging-api.startupai.site"

[context.branch-deploy.environment]
  API_URL = "https://dev-api.startupai.site"
```

## Built-in Variables

Netlify provides these variables automatically:

| Variable | Description |
|----------|-------------|
| `NETLIFY` | Always `true` on Netlify |
| `BUILD_ID` | Unique build identifier |
| `CONTEXT` | Deploy context (production, deploy-preview, etc.) |
| `DEPLOY_ID` | Unique deploy identifier |
| `DEPLOY_PRIME_URL` | Unique URL for this deploy |
| `DEPLOY_URL` | URL of the deploy (may include branch subdomain) |
| `URL` | Primary site URL |
| `SITE_ID` | Netlify site ID |
| `SITE_NAME` | Site name |
| `BRANCH` | Git branch being deployed |
| `HEAD` | Git branch of HEAD |
| `COMMIT_REF` | Git commit SHA |
| `PULL_REQUEST` | PR number (if deploy preview) |
| `REVIEW_ID` | Review ID (if deploy preview) |
| `REPOSITORY_URL` | Git repository URL |

## Accessing Variables

### In Build

```bash
# In build command
echo $API_URL
```

### In Serverless Functions

```javascript
// netlify/functions/api.js
export const handler = async (event) => {
  const apiKey = process.env.API_KEY;
  // Use apiKey
};
```

### In Edge Functions

```typescript
// netlify/edge-functions/api.ts
export default async (request: Request, context: Context) => {
  const apiKey = Deno.env.get("API_KEY");
  // Use apiKey
};
```

### In Frontend (Build Time)

```javascript
// Next.js - must prefix with NEXT_PUBLIC_
const apiUrl = process.env.NEXT_PUBLIC_API_URL;

// Vite - must prefix with VITE_
const apiUrl = import.meta.env.VITE_API_URL;
```

## Sensitive Variables

For secrets that should never appear in logs:

1. Mark as **Sensitive** in UI
2. Values hidden in deploy logs
3. Cannot be read via API after creation
4. Can only be overwritten, not read

## Variable Precedence

From highest to lowest priority:

1. **netlify.toml** context-specific
2. **UI** context-specific
3. **UI** all contexts
4. **Team-level** variables (Enterprise)
5. **Built-in** Netlify variables

## StartupAI Environment Variables

Common variables for StartupAI product app:

```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://eqxropalhxjeyvfcoyxg.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# Modal API
MODAL_API_URL=https://chris00walker--startupai-validation-fastapi-app.modal.run

# CrewAI Webhook
CREWAI_WEBHOOK_SECRET=startupai-webhook-secret-2024

# Feature Flags
NEXT_PUBLIC_ENABLE_VALIDATION=true
```

## Local Development

```bash
# Create .env for local development
cat > .env.local << EOF
NEXT_PUBLIC_SUPABASE_URL=https://eqxropalhxjeyvfcoyxg.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
EOF

# Use with netlify dev
netlify dev
# Variables from UI + .env.local available
```

## Best Practices

1. **Never commit secrets** - Use .gitignore for .env files
2. **Use NEXT_PUBLIC_ prefix** - For client-side Next.js variables
3. **Scope appropriately** - Limit to needed contexts
4. **Mark sensitive** - Secrets should be marked sensitive
5. **Context-specific URLs** - Different APIs for prod/staging
6. **Document variables** - README or .env.example

## External Resources

- [Environment Variables Docs](https://docs.netlify.com/environment-variables/overview/)
- [Build Environment Variables](https://docs.netlify.com/configure-builds/environment-variables/)
- [Functions Environment Variables](https://docs.netlify.com/functions/environment-variables/)
