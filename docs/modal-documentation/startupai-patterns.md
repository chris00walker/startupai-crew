# StartupAI Modal Patterns

Ecosystem-specific patterns for the StartupAI Modal deployment.

---

## Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        StartupAI Architecture                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  INTERACTION LAYER (Netlify/Product App)                                    │
│  • User triggers validation via app.startupai.site                          │
│  • Receives real-time progress updates via Supabase Realtime                │
│  • Handles HITL approvals with UI                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  ORCHESTRATION LAYER (Supabase)                                             │
│  • State persistence (validation_runs table)                                │
│  • Real-time updates (WebSocket via Realtime)                               │
│  • Approval queue (hitl_requests table)                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  COMPUTE LAYER (Modal)                                                      │
│  • 5 Phase functions (one per phase)                                        │
│  • Ephemeral containers (pay-per-second)                                    │
│  • Checkpoint-and-resume at HITL points ($0 while waiting)                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## HITL Checkpoint-and-Resume Pattern

The key cost optimization: **terminate containers during human review**.

### Flow

```
1. Phase executes until HITL checkpoint
2. State saved to Supabase
3. Container terminates ($0 cost while waiting)
4. Human reviews and approves via Product App
5. Approval webhook triggers new container
6. New container loads state and continues
```

### Implementation

```python
@app.function(
    secrets=[modal.Secret.from_name("startupai-secrets")],
    timeout=3600,
)
def run_validation(run_id: str):
    supabase = get_supabase()

    # Get current state
    run = supabase.table("validation_runs").select("*").eq(
        "id", run_id
    ).single().execute().data

    current_phase = run["current_phase"]
    phase_state = run.get("phase_state", {})

    # Execute phase
    result = execute_phase(current_phase, run_id, phase_state)

    # Check for HITL checkpoint
    if result.get("hitl_checkpoint"):
        checkpoint = result["hitl_checkpoint"]

        # 1. Save state to Supabase
        supabase.table("validation_runs").update({
            "hitl_state": checkpoint,
            "status": "paused",
            "phase_state": result.get("state", {}),
        }).eq("id", run_id).execute()

        # 2. Create HITL request for UI
        supabase.table("hitl_requests").insert({
            "run_id": run_id,
            "checkpoint_name": checkpoint,
            "phase": current_phase,
            "title": result.get("hitl_title"),
            "description": result.get("hitl_description"),
            "context": result.get("hitl_context", {}),
            "options": result.get("hitl_options"),
            "recommended_option": result.get("hitl_recommended"),
        }).execute()

        # 3. Container terminates here - $0 while waiting
        return {"status": "paused", "checkpoint": checkpoint}

    # Continue to next phase...
```

### Resume Function

```python
@app.function(
    secrets=[modal.Secret.from_name("startupai-secrets")],
    timeout=3600,
)
def resume_from_checkpoint(run_id: str, checkpoint: str):
    """Resume validation after HITL approval."""
    # Delegate to main orchestrator
    return run_validation.local(run_id)
```

### HITL Approval Endpoint

```python
@web_app.post("/hitl/approve")
async def hitl_approve(request: HITLApproveRequest):
    supabase = get_supabase()

    # Update HITL request status
    supabase.table("hitl_requests").update({
        "status": request.decision,
        "decision_at": datetime.now(timezone.utc).isoformat(),
    }).eq("run_id", str(request.run_id)).eq(
        "checkpoint_name", request.checkpoint
    ).execute()

    # Update run status
    supabase.table("validation_runs").update({
        "hitl_state": None,
        "status": "running",
    }).eq("id", str(request.run_id)).execute()

    # Spawn new container to continue
    resume_from_checkpoint.spawn(str(request.run_id), request.checkpoint)

    return {"status": "resumed"}
```

---

## Modal App Configuration

### app.py Structure

```python
import modal
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Image with all dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "crewai>=0.80.0",
        "crewai-tools>=0.14.0",
        "fastapi>=0.115.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "supabase>=2.0.0",
        "openai>=1.0.0",
        "tavily-python>=0.3.0",
        "httpx>=0.27.0",
    )
    .add_local_dir("src", remote_path="/root/src")
)

# Modal App
app = modal.App(
    name="startupai-validation",
    image=image,
    secrets=[modal.Secret.from_name("startupai-secrets")],
)

# FastAPI app with CORS
web_app = FastAPI(title="StartupAI Validation API")
web_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.startupai.site",
        "https://startupai.site",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount FastAPI to Modal
@app.function()
@modal.asgi_app()
def fastapi_app():
    return web_app
```

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/kickoff` | POST | Start validation run |
| `/status/{run_id}` | GET | Check progress |
| `/hitl/approve` | POST | Resume after approval |
| `/health` | GET | Health check |

### Kickoff Request

```python
class KickoffRequest(BaseModel):
    project_id: UUID
    user_id: UUID
    entrepreneur_input: str = Field(..., min_length=10)
    session_id: Optional[UUID] = None
```

### HITL Approve Request

```python
class HITLApproveRequest(BaseModel):
    run_id: UUID
    checkpoint: str
    decision: str  # approved, rejected, segment_1, custom_segment, etc.
    feedback: Optional[str] = None
    custom_segment_data: Optional[dict] = None
```

---

## Supabase Integration

### State Persistence

```python
_supabase_client = None

def get_supabase():
    """Lazy-initialize Supabase client."""
    global _supabase_client
    if _supabase_client is None:
        from supabase import create_client
        import os

        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_KEY"]
        _supabase_client = create_client(url, key)

    return _supabase_client
```

### Progress Updates

```python
def update_progress(run_id: str, phase: int, message: str, progress_pct: int):
    """Write progress update for Realtime subscription."""
    supabase = get_supabase()

    supabase.table("validation_progress").insert({
        "run_id": run_id,
        "phase": phase,
        "message": message,
        "progress_pct": progress_pct,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }).execute()
```

---

## Phase Execution Pattern

### Phase Function Structure

```python
# src/modal_app/phases/phase_2.py

def execute(run_id: str, state: dict) -> dict:
    """Execute Phase 2: Desirability validation."""
    from src.state import update_progress
    from src.crews.desirability import run_growth_crew

    # Update progress
    update_progress(run_id, 2, "Starting desirability validation", 0)

    # Run crews
    result = run_growth_crew(state)

    # Determine signal
    signal = determine_signal(result)

    # Check for HITL checkpoint
    if signal == "no_interest":
        return {
            "hitl_checkpoint": "approve_segment_pivot",
            "hitl_title": "Segment Pivot Required",
            "hitl_description": "No interest detected. Choose alternative segment.",
            "hitl_options": ["segment_1", "segment_2", "custom_segment"],
            "hitl_recommended": "segment_1",
            "hitl_context": {
                "signal": signal,
                "segment_alternatives": generate_alternatives(state),
            },
            "state": {**state, "signal": signal},
        }

    # Continue to next phase
    update_progress(run_id, 2, "Desirability validation complete", 100)
    return {"state": {**state, "desirability_result": result}}
```

---

## Secrets Required

```bash
modal secret create startupai-secrets \
  OPENAI_API_KEY=sk-... \
  TAVILY_API_KEY=tvly-... \
  SUPABASE_URL=https://eqxropalhxjeyvfcoyxg.supabase.co \
  SUPABASE_KEY=eyJ... \
  WEBHOOK_BEARER_TOKEN=startupai-modal-secret-2026 \
  NETLIFY_ACCESS_TOKEN=xxx
```

---

## Key Files

| File | Purpose |
|------|---------|
| `src/modal_app/app.py` | Main Modal app entry point |
| `src/modal_app/phases/phase_0.py` | Onboarding phase |
| `src/modal_app/phases/phase_1.py` | VPC Discovery phase |
| `src/modal_app/phases/phase_2.py` | Desirability phase |
| `src/modal_app/phases/phase_3.py` | Feasibility phase |
| `src/modal_app/phases/phase_4.py` | Viability phase |
| `src/state/models.py` | Pydantic state models |
| `src/crews/` | CrewAI crew definitions |

---

## Deployment Commands

```bash
# Development
modal serve src/modal_app/app.py

# Deploy to dev environment
modal deploy --env dev src/modal_app/app.py

# Deploy to production
modal deploy src/modal_app/app.py

# Check deployment
curl https://chris00walker--startupai-validation-fastapi-app.modal.run/health
```

---

## Debugging

### View Logs

```bash
modal app logs startupai-validation
```

### Local Testing

```python
# Test phase execution locally
if __name__ == "__main__":
    from src.modal_app.phases import phase_0

    result = phase_0.execute("test-run", {
        "entrepreneur_input": "Test business idea..."
    })
    print(result)
```

---

## Related

- [Functions](functions.md) - Function configuration
- [Web Endpoints](web-endpoints.md) - API endpoint patterns
- [Secrets](secrets.md) - Secret management
- [Deployment](deployment.md) - CI/CD workflow
