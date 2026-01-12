# ADR-002: Migration to Modal Serverless Architecture

**Status**: Accepted (Implemented)
**Date**: 2026-01-08
**Decision Makers**: Chris Walker, Claude AI Assistant
**Context**: Platform-agnostic deployment after CrewAI AMP failures
**Supersedes**: [ADR-001](./001-flow-to-crew-migration.md) (3-Crew AMP architecture)

## Summary

Migrate from CrewAI AMP (both Flow-based and 3-Crew approaches) to a platform-agnostic **Serverless Agentic Loop** architecture using Modal for compute, Supabase for state/realtime, and Netlify for the interaction layer. This eliminates all CrewAI AMP dependencies while preserving the full canonical architecture (5 Flows, 14 Crews, 45 Agents, 10 HITL checkpoints).

## Context

### The Problem

Both AMP deployment approaches have failed:

**Approach 1: Flow-based (`type = "flow"`)** - ADR-001 Section 1
- AMP returned `source: memory` without executing code
- Dashboard showed "Waiting for events to load..." (flows never ran)
- Infrastructure-level caching bypassed our code entirely

**Approach 2: 3-Crew workaround (`type = "crew"`)** - ADR-001 Decision
- Required 3 separate GitHub repositories
- Used `InvokeCrewAIAutomationTool` for crew chaining
- Added latency and failure points between crews
- Still exhibited unreliable behavior on AMP
- Reduced canonical 14 crews to 3, losing structural clarity

### Root Cause

Both approaches depend on CrewAI AMP for orchestration. AMP's infrastructure issues (caching, flow execution, crew chaining) are outside our control. Waiting for platform fixes blocks all progress with no timeline.

### Requirements for New Architecture

1. **Platform-agnostic**: Deploy to any platform that runs Python
2. **Cost-efficient**: Pay only when running, $0 idle costs
3. **Long-running support**: Validation can take 30+ minutes
4. **HITL support**: Human approvals can take hours/days
5. **Real-time updates**: Users see progress as it happens
6. **Full architecture**: Preserve all 5 Flows, 14 Crews, 45 Agents, 10 HITL

## Decision

Adopt a **Serverless Agentic Loop** architecture with three layers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      INTERACTION LAYER (Netlify)                             │
│  • Static hosting for Next.js frontend                                       │
│  • Edge Functions trigger Modal webhook                                      │
│  • Returns 202 Accepted immediately                                          │
└─────────────────────────────────────────┬───────────────────────────────────┘
                                          │
┌─────────────────────────────────────────┼───────────────────────────────────┐
│                    ORCHESTRATION LAYER (Supabase)                            │
│  • PostgreSQL: State persistence, audit trail                                │
│  • Realtime Engine: WebSocket updates to UI                                  │
│  • RLS: Multi-tenant security                                                │
└─────────────────────────────────────────┬───────────────────────────────────┘
                                          │
┌─────────────────────────────────────────┼───────────────────────────────────┐
│                       COMPUTE LAYER (Modal)                                  │
│  • Ephemeral Python containers (spin up on demand)                           │
│  • Long-running execution (minutes to hours)                                 │
│  • Pay-per-second billing ($0 when idle)                                     │
│  • CrewAI executes here, writes progress to Supabase                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Why Modal

| Requirement | Modal Capability |
|-------------|------------------|
| Long-running | Supports hours-long execution (no 30-second limits) |
| Python-native | First-class Python support, perfect for CrewAI |
| Pay-per-use | $0.047/core-hour, $0 when idle |
| Auto-scaling | 0 → 1000+ containers automatically |
| No cold starts | Containers kept warm after first request |
| GPU support | Available if needed for future LLM self-hosting |

### Function Mapping

The canonical 5 Flows map to Modal functions:

```
Modal App: startupai-validation
│
├── @web_endpoint /kickoff           → Returns 202, spawns run_validation
├── @web_endpoint /status/{run_id}   → Reads progress from Supabase
├── @web_endpoint /hitl/approve      → Processes approval, spawns resume
│
├── @function run_validation         → Main orchestrator (async)
│
├── @function phase_0_onboarding     → OnboardingFlow (1 crew, 4 agents)
├── @function phase_1_vpc_discovery  → VPCDiscoveryFlow (5 crews, 18 agents)
├── @function phase_2_desirability   → DesirabilityFlow (3 crews, 9 agents)
├── @function phase_3_feasibility    → FeasibilityFlow (2 crews, 5 agents)
├── @function phase_4_viability      → ViabilityFlow (3 crews, 9 agents)
│
└── @periodic hitl_expiration_check  → Every 6h: expire stale approvals
```

### Function Configuration

Each phase function is configured for long-running LLM workloads:

```python
@app.function(
    secrets=[modal.Secret.from_name("startupai-secrets")],
    timeout=3600,      # 1 hour per phase (24h max supported)
    cpu=2.0,           # 2 cores for LLM orchestration
    memory=4096,       # 4 GiB RAM for agent state
    retries=modal.Retries(max_retries=3, initial_delay=1.0),
    enable_memory_snapshot=True,  # Faster cold starts
)
def phase_1_vpc_discovery(run_id: str):
    ...
```

| Setting | Value | Rationale |
|---------|-------|-----------|
| `timeout` | 3600 (1 hour) | Conservative; individual phases typically <30 min |
| `cpu` | 2.0 | LLM orchestration is CPU-bound when not waiting |
| `memory` | 4096 MiB | Agent state + CrewAI + dependencies |
| `retries` | 3 | Resilience against preemption and transient failures |
| `enable_memory_snapshot` | True | Cache initialized Python state for faster cold starts |

**Preemption Handling**: Modal may preempt long-running functions (rare). The retry configuration provides resilience. For phases >1 hour, consider mid-phase checkpoints to Supabase.

### Web Endpoint Configuration

The FastAPI ASGI app requires CORS middleware (not auto-enabled like `@web_endpoint`):

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

web_app = FastAPI(title="StartupAI Validation API")

web_app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.startupai.site", "https://startupai.site"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.function()
@modal.asgi_app()
def fastapi_app():
    return web_app
```

**HTTP Timeout**: Modal has a 150-second HTTP timeout. Our architecture correctly uses the polling pattern (kickoff returns 202, client polls /status).

### HITL Checkpoint-and-Resume Pattern

Critical insight: **containers don't wait for humans**. They checkpoint to Supabase and terminate.

```
Phase N executes in Modal container
              │
              ▼
    HITL checkpoint reached
              │
              ├──▶ INSERT into hitl_requests (checkpoint, context)
              ├──▶ UPDATE validation_runs SET hitl_state = 'awaiting'
              │
              └──▶ Container terminates (cost: $0 while waiting)

              [Hours/days pass - human reviews in dashboard]

Human clicks "Approve" in product app UI
              │
              ▼
    POST /hitl/approve
              │
              ├──▶ UPDATE hitl_requests SET status = 'approved'
              ├──▶ UPDATE validation_runs SET hitl_state = NULL
              │
              └──▶ spawn(resume_from_checkpoint, run_id, next_phase)
                             │
                             ▼
                   New container starts Phase N+1
```

**Key benefit**: $0 cost during human review periods (vs always-on servers billing continuously).

### State Persistence

Supabase PostgreSQL stores all state, enabling resume from any checkpoint:

```sql
-- Validation run state
CREATE TABLE validation_runs (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    status TEXT DEFAULT 'pending',  -- pending|running|paused|completed|failed
    current_phase INTEGER DEFAULT 0,
    phase_state JSONB DEFAULT '{}',  -- Serialized Pydantic state
    hitl_state TEXT,  -- NULL or checkpoint name
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

-- Progress log (append-only, enables Realtime)
CREATE TABLE validation_progress (
    id UUID PRIMARY KEY,
    run_id UUID REFERENCES validation_runs(id),
    phase INTEGER,
    crew TEXT,
    task TEXT,
    status TEXT,  -- started|completed|failed
    progress_pct INTEGER,
    output JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- HITL checkpoints
CREATE TABLE hitl_requests (
    id UUID PRIMARY KEY,
    run_id UUID REFERENCES validation_runs(id),
    checkpoint_name TEXT NOT NULL,
    phase INTEGER NOT NULL,
    context JSONB NOT NULL,
    status TEXT DEFAULT 'pending',  -- pending|approved|rejected|expired
    decision_by UUID,
    expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '7 days'
);

-- Enable Realtime for instant UI updates
ALTER PUBLICATION supabase_realtime ADD TABLE validation_progress;
ALTER PUBLICATION supabase_realtime ADD TABLE hitl_requests;
```

### Security

1. **Bearer Token Authentication**: All Modal endpoints require `Authorization: Bearer <token>`
2. **HMAC Signature** (optional): Webhook payloads signed with shared secret
3. **Supabase RLS**: Users can only see their own validation runs

```python
def verify_auth(authorization: str) -> bool:
    expected = os.environ["STARTUPAI_WEBHOOK_BEARER_TOKEN"]
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Invalid authorization")
    if not hmac.compare_digest(authorization[7:], expected):
        raise HTTPException(401, "Invalid token")
    return True
```

### Observability

**Logging Strategy**: Use structured JSON logging for queryable logs:

```python
import logging
import json

logging.basicConfig(
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

@app.function()
def phase_1_vpc_discovery(run_id: str):
    logger.info(json.dumps({
        "event": "phase_start",
        "run_id": run_id,
        "phase": 1,
        "crew": "discovery"
    }))
```

**Log Retention**: Starter plan = 1 day, Team plan = 7 days. For longer retention, push logs to an external system or use Supabase.

**Alerting**: Enable Slack integration in Modal dashboard for:
- Container crashes
- Failed scheduled functions
- GPU resource constraints (if used)

**Custom Metrics**: Push business metrics to Supabase `validation_metrics` table:

```python
async def log_metric(run_id: str, metric: str, value: float):
    await supabase.table("validation_metrics").insert({
        "run_id": run_id,
        "metric": metric,
        "value": value,
        "created_at": datetime.utcnow().isoformat()
    })
```

### Modal Plan Constraints

**Starter Plan** (free tier) constraints:

| Resource | Limit | Our Usage |
|----------|-------|-----------|
| Containers | 100 max | ~5-10 ✅ |
| Deployed endpoints | 8 max | 5 needed ✅ |
| Cron jobs | 5 max | 1 needed ✅ |
| Log retention | 1 day | May need upgrade |
| Rollbacks | Not available | Keep deployment scripts |

**Recommendation**: Start with Starter plan for MVP. Consider Team plan for production if log retention or rollback capabilities become important.

## Consequences

### Positive

1. **Platform Independence**: No CrewAI AMP dependency; runs on any Python platform
2. **$0 Idle Costs**: Pay only during execution, not for always-on servers
3. **$0 HITL Waiting**: Containers terminate during human review
4. **Auto-scaling**: 0 → 1000+ concurrent validations without configuration
5. **Full Architecture**: Preserves all 5 Flows, 14 Crews, 45 Agents, 10 HITL
6. **Real-time UX**: Supabase Realtime → instant progress updates in UI
7. **Single Repository**: Back to monorepo (was 3 repos for AMP workaround)
8. **Long-running Support**: Hours-long validations work natively
9. **Audit Trail**: All progress persisted to PostgreSQL

### Negative

1. **Custom Orchestration**: Must implement `@start`, `@listen`, `@router` patterns ourselves
2. **No AMP Dashboard**: Lose CrewAI's built-in monitoring (can build our own)
3. **Modal Dependency**: New platform dependency (though more standard than AMP)
4. **State Serialization**: Must serialize/deserialize Pydantic state to JSON

### Neutral

1. **Cost Structure**: ~$0.08/run Modal compute + ~$2-5 OpenAI tokens = $2.08-5.08/validation
2. **Latency**: Similar to AMP (Modal has no cold starts after first request)
3. **Debugging**: Different tools (Modal dashboard vs AMP dashboard)

## Cost Comparison

### Modal (Recommended)

```
CPU: $0.0000131/core-second ($0.047/core-hour)
Memory: $0.00000222/GiB-second ($0.008/GiB-hour)

Per validation run (typical 40 min total execution):
- CPU: 2 cores × 2400 sec × $0.0000131 = $0.063
- Memory: 4 GiB × 2400 sec × $0.00000222 = $0.021
Total compute: ~$0.08/run

Breakdown by phase:
- Phase 0: 2 min = $0.004
- Phase 1: 15 min = $0.030
- Phase 2: 10 min = $0.020
- Phase 3: 5 min = $0.010
- Phase 4: 8 min = $0.016

Free tier: $30/month (~375 runs)
```

### Railway (Previous Recommendation)

```
Pro plan: $20/month base + usage
Always-on: Charges during HITL waiting
No auto-scaling: Manual configuration

10 runs/month: $20+ (base)
100 runs/month: $25-30
```

### CrewAI AMP

```
Pricing: Not publicly documented
Reliability: Platform issues blocking execution
```

### Summary

| Scenario | Modal | Railway | AMP |
|----------|-------|---------|-----|
| 0 runs (idle) | $0 | $20/mo | $0 |
| 10 runs/mo | $0 | $20/mo | Unknown |
| 100 runs/mo | $0 | $25-30/mo | Unknown |
| 500 runs/mo | $0-30/mo | $50-75/mo | Unknown |

## Alternatives Considered

### 1. Railway (Always-On FastAPI)

**Pros**: Simple deployment, no platform learning curve
**Cons**: $20/month minimum, charges during HITL waiting, no auto-scaling
**Rejected**: Higher cost for variable workloads, wastes money during human review periods

### 2. AWS Lambda + Step Functions

**Pros**: Mature, well-documented
**Cons**: 15-minute timeout limit, cold starts, complex Step Functions configuration
**Rejected**: Timeout limit incompatible with long-running validations

### 3. Fly.io

**Pros**: Good Python support, global edge deployment
**Cons**: Less Python-native than Modal, more configuration required
**Rejected**: Modal's Python-first approach better fits CrewAI

### 4. Self-Hosted Kubernetes

**Pros**: Full control, no platform dependencies
**Cons**: Significant DevOps overhead, must manage scaling manually
**Rejected**: Too much infrastructure work for solo developer

### 5. Wait for CrewAI AMP Fixes

**Pros**: No migration work
**Cons**: No timeline, blocks all progress, platform remains black box
**Rejected**: Unacceptable to block on external platform with no ETA

## Migration Path

### Phase 1: Infrastructure Setup (Day 1) ✅ COMPLETE
- [x] Create Modal account and organization
- [x] Create `dev` and `staging` environments: `modal environment create dev`
- [x] Configure secrets: `modal secret create startupai-secrets ...`
- [x] Set up GitHub Actions with `MODAL_TOKEN_ID` and `MODAL_TOKEN_SECRET`
- [x] Enable Slack integration for alerts in Modal dashboard
- [x] Run Supabase migrations for new tables
- [x] Enable Realtime on progress/HITL tables

### Phase 2: Code Migration (Days 2-3) ✅ COMPLETE
- [x] Create `src/modal_app/` directory structure
- [x] Implement `app.py` with image definition and function configuration
- [x] Implement FastAPI web endpoints with CORS middleware
- [x] Port phase functions from existing crews (with proper timeouts)
- [x] Implement state persistence helpers
- [x] Implement HITL checkpoint/resume logic
- [x] Add structured JSON logging

### Phase 3: Testing (Days 4-5) ✅ COMPLETE
- [x] Deploy to `dev` environment: `modal deploy --env=dev`
- [x] Unit tests for state serialization
- [x] Integration tests for Modal endpoints
- [x] Test cold start times (target: <20 seconds)
- [x] Test full HITL checkpoint/resume flow
- [x] Test preemption recovery (force-kill and retry)
- [x] E2E test with real validation run
- [x] Load testing (10 concurrent runs)

### Phase 4: Deployment & Cutover (Day 6) ✅ COMPLETE
- [x] Deploy to staging: `modal deploy --env=staging`
- [x] Run staging E2E verification
- [x] Deploy to production: `modal deploy src/modal_app/app.py`
- [x] Update product app to use Modal endpoints
- [x] Update Netlify edge functions
- [x] Run E2E verification with production data
- [x] Monitor first production runs
- [x] Archive AMP deployment code to `archive/amp-deployment/`
- [x] Update CLAUDE.md with new deployment instructions

### Phase 5: Live Testing (Ongoing) 🔄 IN PROGRESS
- [x] Phase 0 (Onboarding) validated with real LLM calls
- [x] Phase 1 (VPC Discovery) validated with real LLM calls
- [x] Phase 2 (Desirability) validated with real LLM calls
- [ ] Phase 3 (Feasibility) live testing
- [ ] Phase 4 (Viability) live testing

**Issues Discovered & Fixed During Live Testing:**
1. HITL approval re-runs same phase → Fixed: increment phase before resume
2. Template variable timing issues → Fixed: removed context-dependent vars
3. Customer Profile hallucination → Fixed: added template vars with clear headers
4. Phase 2 missing template vars → Fixed: updated task files
5. HITL always same checkpoint → Fixed: signal-based checkpoint routing
6. Segment pivot not changing → Fixed: alternative selection logic

## Directory Structure

```
startupai-crew/
├── src/
│   ├── modal_app/                    # NEW: Modal deployment
│   │   ├── __init__.py
│   │   ├── app.py                    # Web endpoints + orchestrator
│   │   ├── phases/
│   │   │   ├── phase_0_onboarding.py
│   │   │   ├── phase_1_vpc_discovery.py
│   │   │   ├── phase_2_desirability.py
│   │   │   ├── phase_3_feasibility.py
│   │   │   └── phase_4_viability.py
│   │   ├── state/
│   │   │   ├── schemas.py            # Pydantic models
│   │   │   └── persistence.py        # Supabase operations
│   │   └── utils/
│   │       ├── auth.py
│   │       ├── progress.py
│   │       └── hitl.py
│   │
│   └── crews/                        # 14 Crew definitions
│       ├── phase0/                   # OnboardingCrew
│       ├── phase1/                   # 5 crews
│       ├── phase2/                   # 3 crews
│       ├── phase3/                   # 2 crews
│       └── phase4/                   # 3 crews
│
├── db/migrations/
│   ├── 00X_validation_progress.sql   # NEW
│   └── 00X_hitl_requests.sql         # NEW
│
├── archive/
│   └── amp-deployment/               # Archived AMP code
│       ├── flow-architecture/
│       └── crew-templates/
│
├── pyproject.toml                    # Remove [tool.crewai]
└── modal.toml                        # NEW: Modal config
```

## Risk Assessment

### Original Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Modal downtime | Low | High | Implement retry logic, monitor status page |
| State corruption | Low | High | Pydantic validation, transactional DB updates |
| HITL race conditions | Medium | Medium | Idempotent approvals, optimistic locking |
| Cost overruns | Low | Low | Set Modal spend alerts, monitor usage |
| Learning curve | Medium | Low | Modal has excellent docs, Python-native |

### Additional Risks (Identified in Validation)

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Function preemption | Low | Medium | `retries=3` config; mid-phase checkpoints for >1h phases |
| 7-day result expiration | Low | Low | Already mitigated: Supabase is source of truth |
| Log retention (1 day) | Medium | Low | Upgrade to Team plan or push logs to Supabase |
| Rollback limitations | Medium | Medium | Keep deployment scripts; test in staging first |
| Cold start latency | Low | Low | `enable_memory_snapshot=True`; `scaledown_window=300` |

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Deployment success rate | >99% | Modal dashboard |
| E2E validation completion | >95% | Supabase query |
| HITL checkpoint reliability | 100% | No lost approvals |
| Cost per validation | <$6 | Modal billing (~$0.08 compute + ~$2-5 LLM) |
| UI update latency | <500ms | Realtime subscription |
| Cold start time | <20s | Modal dashboard |

## Related Documents

- [ADR-001: Flow to 3-Crew Migration](./001-flow-to-crew-migration.md) - Superseded by this ADR
- [Modal Validation Report](../architecture-audit/modal-validation-report.md) - Detailed architecture validation
- `docs/master-architecture/09-status.md` - Current implementation status
- `docs/deployment/3-crew-deployment.md` - To be deprecated
- Modal Documentation: https://modal.com/docs/guide

## Changelog

| Date | Change |
|------|--------|
| 2026-01-08 | Initial proposal |
| 2026-01-08 | Added function configuration (timeout, cpu, memory, retries) based on Modal docs validation |
| 2026-01-08 | Added CORS middleware requirement for FastAPI ASGI app |
| 2026-01-08 | Added observability section (structured logging, alerting, custom metrics) |
| 2026-01-08 | Added Modal plan constraints (Starter vs Team) |
| 2026-01-08 | Updated cost estimate: ~$0.08/run (was $0.06) |
| 2026-01-08 | Added additional risks: preemption, log retention, rollback limitations |
| 2026-01-08 | Expanded migration path with environment setup and CI/CD |
| 2026-01-09 | **MIGRATION COMPLETE**: All Phases 1-4 completed, production deployment live |
| 2026-01-09 | Added Phase 5 (Live Testing) - Phase 0-2 validated, 6 issues fixed |
| 2026-01-09 | Marked all migration checklist items as complete |
