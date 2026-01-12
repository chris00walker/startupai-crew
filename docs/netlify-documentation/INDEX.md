# Netlify Documentation Index

Quick reference for Netlify deployment and edge computing patterns used in the StartupAI ecosystem.

**Last Updated**: 2026-01-09
**Netlify CLI**: v17+
**MCP Tools Available**: Yes (43+ tools)

## Cache Status

| Metric | Value |
|--------|-------|
| **Last Full Sync** | 2026-01-09 |
| **Staleness Threshold** | 30 days |
| **Total Cached Files** | 8 |
| **Missing Topics** | 3 (see below) |
| **Cache Manifest** | `MANIFEST.json` |

> **Self-Learning Cache**: This documentation cache automatically updates when new content is fetched from online sources. Check MANIFEST.json for detailed tracking.

---

## Quick Topic Reference

| Topic | File | Key Content |
|-------|------|-------------|
| **Edge Functions** | `edge-functions.md` | Deno runtime, geolocation, middleware |
| **Environment Variables** | `environment-variables.md` | Scopes, contexts, secrets |
| **Deployment** | `deployment.md` | Deploy commands, contexts, previews |
| **MCP Tools** | `mcp-tools.md` | Available MCP tools, usage patterns |
| **CLI Reference** | `cli-reference.md` | `netlify deploy`, `dev`, `env`, `functions` |
| **API Deployment Methods** | `api-deployment-methods.md` | File digest vs ZIP, authentication, 401 errors |
| **StartupAI Patterns** | `startupai-patterns.md` | Product app architecture, edge triggers |

---

## Quick Lookup by Keyword

| Keyword/Pattern | Go To |
|-----------------|-------|
| Edge Function, Deno, middleware | `edge-functions.md` |
| geolocation, A/B testing, personalization | `edge-functions.md` |
| Environment variable, secret, context | `environment-variables.md` |
| `NETLIFY_*`, build context, scopes | `environment-variables.md` |
| Deploy, production, preview, draft | `deployment.md` |
| `netlify deploy --prod`, branch deploys | `deployment.md` |
| MCP, `mcp__netlify__*`, tool | `mcp-tools.md` |
| create_deploy, get_site, list_sites | `mcp-tools.md` |
| CLI, `netlify dev`, `netlify link` | `cli-reference.md` |
| `netlify functions`, `netlify env` | `cli-reference.md` |
| API, file digest, ZIP upload, programmatic | `api-deployment-methods.md` |
| 401 error, authentication, personal access token | `api-deployment-methods.md` |
| StartupAI, product app, app.startupai.site | `startupai-patterns.md` |
| Webhook, CrewAI integration | `startupai-patterns.md` |

---

## StartupAI-Specific Patterns

For StartupAI's Netlify usage, these are the most relevant:

1. **Product App Deployment** -> `startupai-patterns.md`
   - `app.startupai.site` on Netlify

2. **Environment Variables** -> `environment-variables.md`
   - API keys, Supabase URL, webhook tokens

3. **Edge Functions** -> `edge-functions.md`
   - Geolocation, middleware patterns

4. **MCP Tools** -> `mcp-tools.md`
   - `create_deploy`, `get_site` for automation

---

## Topics NOT in This Cache

This cache covers ~8 essential patterns. For these topics, **use WebFetch** or MCP tools:

| Topic | Online URL / MCP Tool |
|-------|----------------------|
| Forms | https://docs.netlify.com/forms/setup/ |
| Identity | https://docs.netlify.com/integrations/identity/ |
| Split Testing | https://docs.netlify.com/site-deploys/split-testing/ |

**For comprehensive searches**:
```
mcp__netlify__search_docs: "your topic here"
```

---

## MCP Tools Available

The following Netlify MCP tools are available for direct use:

| Tool | Purpose |
|------|---------|
| `mcp__netlify__list_sites` | List all Netlify sites |
| `mcp__netlify__get_site` | Get site details |
| `mcp__netlify__create_deploy` | Create new deployment |
| `mcp__netlify__get_deploy` | Get deploy status |
| `mcp__netlify__list_deploys` | List site deployments |
| `mcp__netlify__get_env_vars` | Get environment variables |
| `mcp__netlify__set_env_vars` | Set environment variables |
| `mcp__netlify__delete_env_var` | Delete environment variable |
| `mcp__netlify__netlify-coding-rules` | Netlify best practices |

---

## External Resources

- **Official Docs**: https://docs.netlify.com
- **CLI Docs**: https://cli.netlify.com
- **App Dashboard**: https://app.netlify.com
- **Edge Functions Examples**: https://edge-functions-examples.netlify.app

---

## Usage Tips

1. **Before implementing**: Read the relevant doc file first
2. **Use MCP tools**: Prefer MCP tools for site management
3. **Check StartupAI patterns**: Reference `startupai-patterns.md` for ecosystem-specific guidance
4. **If topic not found**: Use WebFetch to docs.netlify.com
