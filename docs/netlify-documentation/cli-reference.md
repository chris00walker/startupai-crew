# Netlify CLI Reference

Complete command reference for the Netlify CLI.

## Installation

```bash
# Global installation
npm install -g netlify-cli

# Local installation (for CI)
npm install netlify-cli --save-dev

# Via Homebrew
brew install netlify-cli
```

## Authentication

```bash
# Interactive login (opens browser)
netlify login

# Using access token
export NETLIFY_AUTH_TOKEN="your_token"

# Check authentication status
netlify status

# Logout
netlify logout
```

## Site Management

### Link Project

```bash
# Link current directory to Netlify site
netlify link

# Link by site name
netlify link --name your-site-name

# Link by site ID
netlify link --id abc123

# Unlink project
netlify unlink
```

### Site Operations

```bash
# List all sites
netlify sites:list

# Create new site
netlify sites:create

# Create with specific name
netlify sites:create --name my-site

# Delete site (interactive)
netlify sites:delete

# Open site in browser
netlify open
netlify open:site

# Open admin dashboard
netlify open:admin
```

## Local Development

```bash
# Start local dev server
netlify dev

# Start with live reload
netlify dev --live

# Start on specific port
netlify dev --port 8888

# Start with edge functions
netlify dev --edge

# Start with specific framework detection
netlify dev --framework next
```

## Building

```bash
# Run local build
netlify build

# Dry run (preview changes)
netlify build --dry

# Build for specific context
netlify build --context production
netlify build --context deploy-preview
netlify build --context branch-deploy
```

## Deployment

### Manual Deploy

```bash
# Deploy draft (preview URL)
netlify deploy

# Deploy to production
netlify deploy --prod
netlify deploy -p

# Deploy specific directory
netlify deploy --dir=dist
netlify deploy --dir=build --prod

# Deploy with message
netlify deploy --message "Fix login bug"

# Deploy with custom alias
netlify deploy --alias preview-feature-x

# Deploy with build
netlify deploy --build --prod
```

### Deploy Controls

```bash
# Lock deploys (stop auto-deploy)
netlify deploy:lock

# Unlock deploys
netlify deploy:unlock

# Watch deploy progress
netlify watch
```

## Environment Variables

```bash
# List all variables
netlify env:list

# Get specific variable
netlify env:get KEY_NAME

# Set variable (all contexts)
netlify env:set KEY_NAME value

# Set for specific context
netlify env:set KEY_NAME value --context production
netlify env:set KEY_NAME value --context deploy-preview
netlify env:set KEY_NAME value --context branch:staging

# Set from .env file
netlify env:import .env

# Export to .env file
netlify env:export

# Delete variable
netlify env:unset KEY_NAME

# Clone variables from another site
netlify env:clone --from other-site
```

## Functions

### Serverless Functions

```bash
# List deployed functions
netlify functions:list

# Create new function
netlify functions:create
netlify functions:create --name my-function

# Invoke function locally
netlify functions:invoke my-function

# Invoke with data
netlify functions:invoke my-function --payload '{"key": "value"}'

# Serve functions locally
netlify functions:serve

# Build functions
netlify functions:build
```

### Edge Functions

```bash
# List edge functions
netlify edge-functions:list

# Serve edge functions locally (via dev)
netlify dev --edge
```

## Logs

```bash
# Stream deploy logs
netlify logs

# Stream function logs
netlify logs:function function-name

# Deploy logs
netlify logs:deploy
```

## CI/CD Setup

```bash
# Initialize continuous deployment
netlify init

# Manual setup (GitLab, Bitbucket, Azure DevOps)
netlify init --manual

# Clone and link in one command
netlify clone owner/repo
```

## Addons

```bash
# List available addons
netlify addons:list

# Create addon
netlify addons:create addon-name

# Delete addon
netlify addons:delete addon-name
```

## Configuration

### netlify.toml

```toml
# Build settings
[build]
  command = "npm run build"
  publish = "dist"
  functions = "netlify/functions"

[build.environment]
  NODE_VERSION = "20"

# Redirects
[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200

# Headers
[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"

# Edge functions
[[edge_functions]]
  function = "auth"
  path = "/api/*"

# Plugins
[[plugins]]
  package = "@netlify/plugin-nextjs"
```

## Telemetry

```bash
# Disable telemetry
netlify --telemetry-disable

# Enable telemetry
netlify --telemetry-enable
```

## Help

```bash
# General help
netlify help
netlify --help

# Command-specific help
netlify deploy --help
netlify env --help
```

## Quick Reference Card

| Command | Purpose |
|---------|---------|
| `netlify login` | Authenticate |
| `netlify link` | Link project to site |
| `netlify dev` | Start local dev |
| `netlify build` | Run local build |
| `netlify deploy` | Deploy draft |
| `netlify deploy --prod` | Deploy to production |
| `netlify env:list` | List env vars |
| `netlify env:set KEY value` | Set env var |
| `netlify functions:list` | List functions |
| `netlify logs` | Stream logs |
| `netlify open` | Open site |
| `netlify status` | Check status |

## Environment Variables

The CLI uses these environment variables:

| Variable | Purpose |
|----------|---------|
| `NETLIFY_AUTH_TOKEN` | API authentication token |
| `NETLIFY_SITE_ID` | Default site ID |

## Configuration Files

| File | Location |
|------|----------|
| `netlify.toml` | Project root |
| CLI config | `~/.config/netlify/config.json` (Linux/macOS) |
| CLI config | `%AppData%\Roaming\netlify\Config\config.json` (Windows) |

## External Resources

- [CLI Documentation](https://cli.netlify.com)
- [CLI GitHub](https://github.com/netlify/cli)
- [netlify.toml Reference](https://docs.netlify.com/configure-builds/file-based-configuration/)
