---
purpose: Modal serverless platform configuration and capabilities reference
status: active
last_reviewed: 2026-01-08
vpd_compliance: true
---

# Modal Serverless Platform Configuration

> **Architecture Decision**: See [ADR-002](../../adr/002-modal-serverless-migration.md) for the rationale behind choosing Modal serverless.

This document specifies what Modal provides out-of-the-box, what StartupAI must configure, and what must be implemented in code.

---

## What Modal Provides (No Custom Implementation Needed)

Modal handles these concerns natively:

| Capability | Modal Feature | Notes |
|------------|---------------|-------|
| **Ephemeral containers** | `@modal.function` | Python containers spin up on demand |
| **Auto-scaling** | Built-in | 0 → 1000+ containers automatically |
| **Pay-per-second billing** | Default | $0.047/core-hour, $0 when idle |
| **Long-running execution** | Up to 24h | No Lambda-style timeout limits |
| **Web endpoints** | `@modal.web_endpoint` | HTTP(S) API without separate gateway |
| **Scheduled functions** | `@modal.periodic` | Cron-style scheduled execution |
| **Secret management** | `modal secret create` | Encrypted environment variables |
| **Dashboard and logging** | Modal Console | Built-in observability |
| **GPU support** | Optional | Available for future LLM self-hosting |

---

## What StartupAI Must Configure

### Modal Secrets

Configure via Modal CLI or dashboard:

```bash
# Create secrets for StartupAI
modal secret create startupai-secrets \
  OPENAI_API_KEY=sk-... \
  SUPABASE_URL=https://eqxropalhxjeyvfcoyxg.supabase.co \
  SUPABASE_KEY=eyJ... \
  STARTUPAI_WEBHOOK_BEARER_TOKEN=startupai-webhook-secret-2024 \
  TAVILY_API_KEY=tvly-... \
  NETLIFY_ACCESS_TOKEN=xxx
```

| Secret | Purpose | Required |
|--------|---------|----------|
| `OPENAI_API_KEY` | LLM API access (GPT-4) | Yes |
| `SUPABASE_URL` | Database connection | Yes |
| `SUPABASE_KEY` | Service role key (not anon) | Yes |
| `STARTUPAI_WEBHOOK_BEARER_TOKEN` | API authentication | Yes |
| `TAVILY_API_KEY` | Web search tool | Yes |
| `NETLIFY_ACCESS_TOKEN` | Landing page deployment | Optional |

### Modal App Configuration

In `src/modal_app/app.py`:

```python
import modal

app = modal.App(
    name="startupai-crew",
    secrets=[modal.Secret.from_name("startupai-secrets")]
)

# Image with dependencies
image = modal.Image.debian_slim().pip_install(
    "crewai>=0.63.0",
    "supabase>=2.0.0",
    "openai>=1.0.0",
    "tavily-python>=0.3.0",
    "pydantic>=2.0.0"
)
```

---

## Function Mapping

Each validation flow maps to a Modal function:

| Modal Function | Purpose | Phase | Timeout |
|----------------|---------|-------|---------|
| `@web_endpoint /kickoff` | Start validation | - | 30s |
| `@web_endpoint /status/{run_id}` | Check progress | - | 10s |
| `@web_endpoint /hitl/approve` | Resume after approval | - | 30s |
| `@function phase_0_onboarding` | OnboardingFlow | 0 | 10min |
| `@function phase_1_vpc_discovery` | VPCDiscoveryFlow | 1 | 30min |
| `@function phase_2_desirability` | DesirabilityFlow | 2 | 20min |
| `@function phase_3_feasibility` | FeasibilityFlow | 3 | 15min |
| `@function phase_4_viability` | ViabilityFlow | 4 | 20min |
| `@periodic hitl_expiration_check` | Expire stale approvals | - | 5min |

### Example Function Definitions

```python
@app.function(image=image, timeout=600)
def phase_0_onboarding(run_id: str, project_id: str, founder_input: str):
    """Execute Phase 0: Founder's Brief capture."""
    from src.crews.phase0.onboarding_crew import OnboardingCrew

    crew = OnboardingCrew()
    result = crew.kickoff(inputs={"founder_input": founder_input})

    # Persist to Supabase
    persist_phase_output(run_id, phase=0, output=result)

    # Check for HITL checkpoint
    if requires_hitl("approve_founders_brief", result):
        checkpoint_and_terminate(run_id, "approve_founders_brief", result)

    return result

@app.web_endpoint(method="POST")
def kickoff(request: dict):
    """Start a new validation run."""
    run_id = create_validation_run(request["project_id"])

    # Spawn async execution
    phase_0_onboarding.spawn(
        run_id=run_id,
        project_id=request["project_id"],
        founder_input=request["entrepreneur_input"]
    )

    return {"run_id": run_id, "status": "started"}

@app.scheduled(cron="0 */6 * * *")  # Every 6 hours
def hitl_expiration_check():
    """Expire HITL requests older than 7 days."""
    expire_stale_hitl_requests()
```

---

## What StartupAI Must Implement

### State Persistence Layer

Modal functions must read/write state to Supabase:

```python
# src/modal_app/state/persistence.py

from supabase import create_client
import os

def get_supabase():
    return create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_KEY"]
    )

def create_validation_run(project_id: str) -> str:
    """Create a new validation run record."""
    supabase = get_supabase()
    result = supabase.table('validation_runs').insert({
        'project_id': project_id,
        'status': 'running',
        'current_phase': 0
    }).execute()
    return result.data[0]['id']

def log_progress(run_id: str, phase: int, crew: str, task: str, status: str, pct: int):
    """Log progress (triggers Realtime to UI)."""
    supabase = get_supabase()
    supabase.table('validation_progress').insert({
        'run_id': run_id,
        'phase': phase,
        'crew': crew,
        'task': task,
        'status': status,
        'progress_pct': pct
    }).execute()

def persist_phase_output(run_id: str, phase: int, output: dict):
    """Persist phase output to validation_runs.phase_state."""
    supabase = get_supabase()
    # Get current state
    current = supabase.table('validation_runs').select('phase_state').eq('id', run_id).single().execute()
    phase_state = current.data['phase_state'] or {}
    phase_state[f'phase_{phase}'] = output

    supabase.table('validation_runs').update({
        'phase_state': phase_state,
        'current_phase': phase + 1
    }).eq('id', run_id).execute()
```

### HITL Checkpoint Pattern

The checkpoint-and-resume pattern for human approvals:

```python
# src/modal_app/state/hitl.py

def checkpoint_and_terminate(run_id: str, checkpoint: str, context: dict):
    """
    Checkpoint state and terminate container.
    Container will be resumed by /hitl/approve endpoint.
    """
    supabase = get_supabase()

    # Insert HITL request
    supabase.table('hitl_requests').insert({
        'run_id': run_id,
        'checkpoint_name': checkpoint,
        'phase': get_current_phase(run_id),
        'context': context
    }).execute()

    # Update run status to paused
    supabase.table('validation_runs').update({
        'status': 'paused',
        'hitl_state': checkpoint
    }).eq('id', run_id).execute()

    # Container terminates here - $0 cost while waiting
    # Resume triggered by POST /hitl/approve

def resume_from_checkpoint(run_id: str, checkpoint: str, decision: str, feedback: str):
    """Resume execution after human approval."""
    supabase = get_supabase()

    # Mark HITL request as resolved
    supabase.table('hitl_requests').update({
        'status': decision,  # approved|rejected
        'decision_feedback': feedback,
        'resolved_at': 'now()'
    }).eq('run_id', run_id).eq('checkpoint_name', checkpoint).execute()

    # Update run status
    supabase.table('validation_runs').update({
        'status': 'running',
        'hitl_state': None
    }).eq('id', run_id).execute()

    # Spawn next phase
    next_phase = get_next_phase(checkpoint)
    spawn_phase_function(run_id, next_phase)
```

### Error Recovery

```python
def handle_phase_error(run_id: str, phase: int, error: Exception):
    """Handle errors during phase execution."""
    supabase = get_supabase()

    # Log error
    log_progress(run_id, phase, "error", str(error), "failed", 0)

    # Update run status
    supabase.table('validation_runs').update({
        'status': 'failed',
        'phase_state': {
            **get_current_state(run_id),
            'error': {
                'phase': phase,
                'message': str(error),
                'timestamp': datetime.utcnow().isoformat()
            }
        }
    }).eq('id', run_id).execute()
```

---

## CLI Commands Reference

```bash
# Setup
modal setup                              # One-time CLI setup
modal token new                          # Generate new API token

# Secrets
modal secret create startupai-secrets \
  OPENAI_API_KEY=sk-... \
  SUPABASE_URL=https://...
modal secret list                        # List secrets
modal secret update startupai-secrets KEY=value

# Development
modal serve src/modal_app/app.py         # Local dev with hot reload
modal run src/modal_app/app.py::kickoff --input '{"entrepreneur_input": "..."}'

# Deployment
modal deploy src/modal_app/app.py        # Deploy to production

# Monitoring
modal app logs startupai-crew            # View logs
modal app list                           # List deployments
modal app stop startupai-crew            # Stop app
```

---

## Cost Structure

| Resource | Price | Typical Usage |
|----------|-------|---------------|
| CPU | $0.047/core-hour | 2 cores per function |
| Memory | $0.008/GiB-hour | 4 GiB typical |
| GPU | $0.80/hour (T4) | Not currently used |
| Free tier | $30/month | ~500 validation runs |
| Typical run | ~$0.06 | 40 min total execution |

### Cost Breakdown per Validation

```
Phase 0:  2 min @ 2 cores = $0.003
Phase 1: 15 min @ 2 cores = $0.023
Phase 2: 10 min @ 2 cores = $0.015
Phase 3:  5 min @ 2 cores = $0.008
Phase 4:  8 min @ 2 cores = $0.012
─────────────────────────────────
Total compute:              $0.06/run
HITL wait time:             $0.00 (container terminated)
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `SecretNotFound` | Secret not created | Run `modal secret create startupai-secrets ...` |
| Function timeout | Execution exceeded limit | Increase `timeout` parameter in `@modal.function` |
| Import error | Missing dependency | Add to `image.pip_install()` |
| Supabase connection | Invalid credentials | Check `SUPABASE_URL` and `SUPABASE_KEY` in secrets |

### Debugging

```bash
# View function logs
modal app logs startupai-crew --filter phase_0

# Test function locally
modal run src/modal_app/app.py::phase_0_onboarding \
  --run-id "test-123" \
  --project-id "proj-456" \
  --founder-input "Test business idea"

# Check deployment status
modal app list
```

---

## Related Documents

- [ADR-002: Modal Serverless Migration](../../adr/002-modal-serverless-migration.md) - Architecture decision
- [database-schemas.md](./database-schemas.md) - Modal tables (validation_runs, validation_progress, hitl_requests)
- [api-contracts.md](./api-contracts.md) - Modal API endpoints
- [approval-workflows.md](./approval-workflows.md) - HITL checkpoint patterns
- [01-ecosystem.md](../01-ecosystem.md) - Three-layer architecture overview

---

**Last Updated**: 2026-01-08

**Changelog**:
| Date | Change |
|------|--------|
| 2026-01-08 | Initial creation - Modal platform configuration reference |
