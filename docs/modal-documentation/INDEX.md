# Modal Documentation Index

Quick reference for Modal serverless deployment patterns used in the StartupAI ecosystem.

**Last Updated**: 2026-01-09
**Modal Version**: v0.73+

## Cache Status

| Metric | Value |
|--------|-------|
| **Last Full Sync** | 2026-01-09 |
| **Staleness Threshold** | 30 days |
| **Total Cached Files** | 9 |
| **Missing Topics** | 5 (see below) |
| **Cache Manifest** | `MANIFEST.json` |

> **Self-Learning Cache**: This documentation cache automatically updates when new content is fetched from online sources. Check MANIFEST.json for detailed tracking.

---

## Quick Topic Reference

| Topic | File | Key Content |
|-------|------|-------------|
| **Functions** | `functions.md` | `@app.function`, timeout, retries, CPU/memory |
| **Web Endpoints** | `web-endpoints.md` | `@modal.asgi_app`, FastAPI, CORS, auth |
| **Images** | `images.md` | Container images, `pip_install`, `add_local_dir` |
| **Secrets** | `secrets.md` | `modal.Secret`, environment variables |
| **Deployment** | `deployment.md` | CI/CD patterns, environments, GitHub Actions |
| **CLI Reference** | `cli-reference.md` | `modal deploy`, `serve`, `run`, `secret`, `app` |
| **GPUs** | `gpus.md` | GPU types (A100, H100, T4), multi-GPU, CUDA |
| **StartupAI Patterns** | `startupai-patterns.md` | HITL checkpoint-resume, architecture |

---

## Quick Lookup by Keyword

| Keyword/Pattern | Go To |
|-----------------|-------|
| `@app.function`, `@modal.function` | `functions.md` |
| `timeout`, `retries`, `cpu`, `memory` | `functions.md` |
| `@modal.asgi_app`, `@modal.fastapi_endpoint` | `web-endpoints.md` |
| FastAPI, CORS, authentication | `web-endpoints.md` |
| `modal.Image`, `pip_install`, container | `images.md` |
| `add_local_dir`, `debian_slim` | `images.md` |
| `modal.Secret`, environment variables | `secrets.md` |
| `modal deploy`, `modal serve`, `modal run` | `cli-reference.md` |
| `modal secret`, `modal app`, `modal environment` | `cli-reference.md` |
| GitHub Actions, CI/CD | `deployment.md` |
| `--env`, environments | `deployment.md` |
| GPU, CUDA, A100, H100, T4, L40S | `gpus.md` |
| multi-GPU, distributed training | `gpus.md` |
| HITL, checkpoint, resume | `startupai-patterns.md` |
| Supabase integration | `startupai-patterns.md` |

---

## StartupAI-Specific Patterns

For StartupAI's Modal deployment, these are the most relevant:

1. **HITL Checkpoint Pattern** → `startupai-patterns.md`
   - Save state to Supabase, terminate container, resume on approval

2. **FastAPI Web Endpoints** → `web-endpoints.md`
   - `/kickoff`, `/status/{run_id}`, `/hitl/approve`

3. **Long-Running Functions** → `functions.md`
   - 1-hour timeout for LLM operations

4. **Secrets Management** → `secrets.md`
   - `startupai-secrets` with API keys

---

## Topics NOT in This Cache

This cache covers ~9 essential patterns. For these topics, **use WebFetch**:

| Topic | Online URL |
|-------|------------|
| Volumes | https://modal.com/docs/guide/volumes |
| Networking | https://modal.com/docs/guide/network-file-systems |
| Sandboxes | https://modal.com/docs/guide/sandbox |
| Scaling | https://modal.com/docs/guide/scale |
| Regions | https://modal.com/docs/guide/region-selection |

**For comprehensive searches**:
```
WebFetch: https://modal.com/llms-full.txt
Prompt: "Find information about {specific topic}"
```

---

## External Resources

- **Official Docs**: https://modal.com/docs/guide
- **LLM-Friendly Full Docs**: https://modal.com/llms-full.txt
- **Examples**: https://github.com/modal-labs/modal-examples
- **Dashboard**: https://modal.com/apps

---

## Usage Tips

1. **Before implementing**: Read the relevant doc file first
2. **Check StartupAI patterns**: Reference `startupai-patterns.md` for ecosystem-specific guidance
3. **If topic not found**: Use WebFetch to modal.com/docs/guide/{topic}
4. **For comprehensive search**: Use WebFetch to modal.com/llms-full.txt
