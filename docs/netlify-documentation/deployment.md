# Netlify Deployment

Guide to deploying sites on Netlify including continuous deployment, deploy contexts, and manual deploys.

## Deployment Methods

### Continuous Deployment (Git)

Automatic deploys when you push to your repository:

1. **Connect repository** in Netlify UI or via CLI
2. **Configure build settings** in `netlify.toml`
3. **Push to trigger deploy**

```toml
# netlify.toml
[build]
  command = "npm run build"
  publish = ".next"          # Output directory
  functions = "netlify/functions"

[build.environment]
  NODE_VERSION = "20"
```

### CLI Deploy

```bash
# Deploy to draft URL (preview)
netlify deploy

# Deploy to production
netlify deploy --prod

# Deploy specific directory
netlify deploy --dir=dist --prod

# Deploy with build
netlify deploy --build --prod
```

### API / MCP Deploy

```
mcp__netlify__create_deploy: {
  site_id: "xxx",
  dir: "./dist",
  production: true
}
```

## Deploy Contexts

| Context | Branch | URL | Purpose |
|---------|--------|-----|---------|
| **Production** | main/master | site.com | Live site |
| **Deploy Preview** | PR branches | deploy-preview-123.site.netlify.app | PR testing |
| **Branch Deploy** | Feature branches | branch-name--site.netlify.app | Branch testing |

### Configure Contexts

```toml
# netlify.toml

# Production settings
[context.production]
  command = "npm run build:prod"
  environment = { NODE_ENV = "production" }

# Deploy preview settings
[context.deploy-preview]
  command = "npm run build:staging"
  environment = { NODE_ENV = "staging" }

# Branch deploy settings
[context.branch-deploy]
  command = "npm run build:dev"

# Specific branch settings
[context.staging]
  command = "npm run build:staging"
```

## Deploy Notifications

Configure notifications in **Site configuration** > **Deploy notifications**:

- **Slack** - Deploy status to channel
- **Email** - Deploy complete/failed emails
- **Webhook** - Custom HTTP callbacks
- **GitHub** - Commit status updates

## Build Settings

### Build Command

```toml
[build]
  command = "npm run build"
```

Common framework commands:
- **Next.js**: `next build`
- **Vite**: `vite build`
- **Astro**: `astro build`
- **Create React App**: `react-scripts build`

### Publish Directory

```toml
[build]
  publish = "dist"    # Vite, Astro
  publish = ".next"   # Next.js
  publish = "build"   # CRA
  publish = "out"     # Next.js static export
```

### Node Version

```toml
[build.environment]
  NODE_VERSION = "20"
  NPM_VERSION = "10"
```

Or use `.nvmrc`:
```
20
```

## Deploy Locking

Prevent automatic deploys:

```bash
# Lock deploys (stop auto-deploy)
netlify deploy:lock

# Unlock deploys
netlify deploy:unlock
```

## Rollbacks

Roll back to a previous deploy:

1. **UI**: Site deploys > Select deploy > **Publish deploy**
2. **CLI**: Not directly supported, use UI

## Draft vs Production

| Type | Command | URL | Purpose |
|------|---------|-----|---------|
| **Draft** | `netlify deploy` | Random subdomain | Testing before prod |
| **Production** | `netlify deploy --prod` | Your domain | Live site |

### Draft Deploy Workflow

```bash
# 1. Deploy draft
netlify deploy --dir=dist
# Returns: https://64abc123--your-site.netlify.app

# 2. Test draft URL

# 3. If good, promote to production
netlify deploy --prod --dir=dist
```

## Atomic Deploys

All deploys are atomic:
- New files uploaded
- DNS switched atomically
- Old version available until switch
- Instant rollback possible

## Deploy Hooks

Trigger deploys without Git push:

1. **Create hook**: Site configuration > Build hooks > Add build hook
2. **POST to hook URL**:
```bash
curl -X POST https://api.netlify.com/build_hooks/YOUR_HOOK_ID
```

3. **With payload**:
```bash
curl -X POST -d '{"trigger_title":"Manual deploy"}' \
  https://api.netlify.com/build_hooks/YOUR_HOOK_ID
```

## Build Plugins

Extend build process with plugins:

```toml
# netlify.toml
[[plugins]]
  package = "@netlify/plugin-nextjs"

[[plugins]]
  package = "netlify-plugin-cache"
  [plugins.inputs]
    paths = [".cache", "node_modules/.cache"]
```

## Skipping Deploys

Skip deploy for specific commits:

```bash
git commit -m "Update README [skip netlify]"
# Or
git commit -m "Docs only [skip ci]"
```

## Deploy Logs

View build and deploy logs:

```bash
# Stream logs during build
netlify watch

# View recent deploys
netlify deploys

# Open deploy in browser
netlify open:site
```

## StartupAI Deployment

**Sites**:
- `startupai.site` - Marketing site
- `app.startupai.site` - Product app

**Production Branch**: `main`

**Environment Contexts**:
```toml
[context.production.environment]
  NEXT_PUBLIC_API_URL = "https://chris00walker--startupai-validation-fastapi-app.modal.run"

[context.deploy-preview.environment]
  NEXT_PUBLIC_API_URL = "https://staging-api.startupai.site"
```

## External Resources

- [Deploys Overview](https://docs.netlify.com/site-deploys/overview/)
- [Build Configuration](https://docs.netlify.com/configure-builds/overview/)
- [Deploy Contexts](https://docs.netlify.com/site-deploys/deploy-contexts/)
- [Build Plugins](https://docs.netlify.com/integrations/build-plugins/)
