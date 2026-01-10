# Netlify MCP Tools

Reference for Netlify Model Context Protocol (MCP) tools available in Claude Code.

## Overview

MCP tools provide direct access to Netlify operations without CLI commands. These tools are integrated into Claude Code and can be used in conversations.

## Available Tools

| Tool | Purpose | Pre-approved |
|------|---------|--------------|
| `mcp__netlify__list_sites` | List all Netlify sites | Yes |
| `mcp__netlify__get_site` | Get site details | Yes |
| `mcp__netlify__create_site` | Create new site | No |
| `mcp__netlify__delete_site` | Delete site | No |
| `mcp__netlify__list_deploys` | List site deployments | Yes |
| `mcp__netlify__get_deploy` | Get deploy details | Yes |
| `mcp__netlify__create_deploy` | Create deployment | Yes |
| `mcp__netlify__cancel_deploy` | Cancel in-progress deploy | No |
| `mcp__netlify__get_env_vars` | Get environment variables | Yes |
| `mcp__netlify__set_env_vars` | Set environment variables | Yes |
| `mcp__netlify__delete_env_var` | Delete environment variable | Yes |
| `mcp__netlify__list_forms` | List site forms | Yes |
| `mcp__netlify__get_form_submissions` | Get form submissions | Yes |
| `mcp__netlify__netlify-coding-rules` | Netlify best practices | Yes |

## Tool Details

### mcp__netlify__list_sites

List all sites in the connected Netlify account.

**Use when**: Finding site IDs, checking site existence, overview of sites.

**Example output**:
```json
[
  {
    "id": "abc123",
    "name": "startupai-site",
    "url": "https://startupai.site",
    "admin_url": "https://app.netlify.com/sites/startupai-site"
  },
  {
    "id": "def456",
    "name": "app-startupai-site",
    "url": "https://app.startupai.site",
    "admin_url": "https://app.netlify.com/sites/app-startupai-site"
  }
]
```

### mcp__netlify__get_site

Get detailed information about a specific site.

**Parameters**:
- `site_id`: Site ID or name

**Use when**: Need site details, checking configuration, finding deploy settings.

### mcp__netlify__list_deploys

List deployments for a site.

**Parameters**:
- `site_id`: Site ID or name
- `state`: Filter by state (optional): `ready`, `building`, `error`

**Use when**: Checking deploy history, finding deploy IDs, monitoring status.

### mcp__netlify__get_deploy

Get details about a specific deployment.

**Parameters**:
- `deploy_id`: Deploy ID

**Use when**: Checking deploy status, viewing deploy logs, debugging failures.

### mcp__netlify__create_deploy

Create a new deployment for a site.

**Parameters**:
- `site_id`: Site ID
- `dir`: Directory to deploy (local path)
- `production`: Boolean, deploy to production (default: false)
- `message`: Deploy message (optional)

**Use when**: Deploying sites, manual deployments.

### mcp__netlify__get_env_vars

Get environment variables for a site.

**Parameters**:
- `site_id`: Site ID

**Use when**: Checking current configuration, auditing variables.

**Note**: Sensitive values may be redacted.

### mcp__netlify__set_env_vars

Set environment variables for a site.

**Parameters**:
- `site_id`: Site ID
- `variables`: Object of key-value pairs

**Example**:
```json
{
  "site_id": "abc123",
  "variables": {
    "API_URL": "https://api.example.com",
    "DEBUG": "false"
  }
}
```

### mcp__netlify__delete_env_var

Delete an environment variable.

**Parameters**:
- `site_id`: Site ID
- `key`: Variable name to delete

### mcp__netlify__list_forms

List forms for a site.

**Parameters**:
- `site_id`: Site ID

**Use when**: Finding form IDs, checking form configuration.

### mcp__netlify__get_form_submissions

Get submissions for a specific form.

**Parameters**:
- `form_id`: Form ID
- `per_page`: Results per page (optional)

### mcp__netlify__netlify-coding-rules

Get Netlify best practices and coding rules.

**Use when**: Learning Netlify patterns, checking best practices.

## Common Workflows

### Check Site Status

```
1. mcp__netlify__list_sites
   → Get site ID

2. mcp__netlify__get_site: { site_id: "abc123" }
   → Get site details

3. mcp__netlify__list_deploys: { site_id: "abc123", state: "ready" }
   → Check recent deploys
```

### Deploy to Production

```
1. mcp__netlify__list_sites
   → Find site ID

2. mcp__netlify__create_deploy: {
     site_id: "abc123",
     dir: "./dist",
     production: true,
     message: "Release v1.2.3"
   }
   → Deploy to production

3. mcp__netlify__get_deploy: { deploy_id: "xyz789" }
   → Check deploy status
```

### Update Environment Variables

```
1. mcp__netlify__get_env_vars: { site_id: "abc123" }
   → View current variables

2. mcp__netlify__set_env_vars: {
     site_id: "abc123",
     variables: {
       "NEW_API_URL": "https://new-api.example.com"
     }
   }
   → Add/update variable

3. mcp__netlify__delete_env_var: {
     site_id: "abc123",
     key: "OLD_VAR"
   }
   → Remove old variable
```

### Monitor Deployment

```
1. mcp__netlify__list_deploys: { site_id: "abc123" }
   → Get latest deploy ID

2. mcp__netlify__get_deploy: { deploy_id: "xyz789" }
   → Check status, view logs
```

## StartupAI Sites

### Marketing Site
- **Name**: `startupai-site`
- **URL**: https://startupai.site
- **Repo**: `chris00walker/startupai.site`

### Product App
- **Name**: `app-startupai-site`
- **URL**: https://app.startupai.site
- **Repo**: `chris00walker/app.startupai.site`

### Common Operations

```
# Check product app deploys
mcp__netlify__list_deploys: { site_id: "app-startupai-site" }

# Update webhook URL
mcp__netlify__set_env_vars: {
  site_id: "app-startupai-site",
  variables: {
    "MODAL_API_URL": "https://chris00walker--startupai-validation-fastapi-app.modal.run"
  }
}
```

## Best Practices

1. **Use site names** - More readable than IDs
2. **Check before deploying** - Review env vars first
3. **Use deploy messages** - Document what changed
4. **Monitor builds** - Check status after deploy
5. **Don't expose secrets** - Mark sensitive variables

## Limitations

- Some operations require elevated permissions
- Sensitive values may be redacted in responses
- Rate limits apply to API calls
- Some tools require confirmation

## External Resources

- [Netlify API Docs](https://docs.netlify.com/api/get-started/)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [Netlify CLI](https://cli.netlify.com)
