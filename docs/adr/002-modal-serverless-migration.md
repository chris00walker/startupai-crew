# ADR-002: Migration to Modal Serverless Architecture

**Status**: Proposed
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

1. **Cost Structure**: ~$0.06/run Modal compute + ~$2-5 OpenAI tokens = $2.06-5.06/validation
2. **Latency**: Similar to AMP (Modal has no cold starts after first request)
3. **Debugging**: Different tools (Modal dashboard vs AMP dashboard)

## Cost Comparison

### Modal (Recommended)

```
CPU: $0.047/core-hour
Memory: $0.008/GiB-hour

Per validation run (typical):
- Phase 0: 2 min @ 2 cores = $0.003
- Phase 1: 15 min @ 2 cores = $0.023
- Phase 2: 10 min @ 2 cores = $0.015
- Phase 3: 5 min @ 2 cores = $0.008
- Phase 4: 8 min @ 2 cores = $0.012
Total compute: ~$0.06/run

Free tier: $30/month (~500 runs)
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

### Phase 1: Infrastructure Setup (Day 1)
- [ ] Create Modal account and organization
- [ ] Configure secrets in Modal dashboard (OPENAI_API_KEY, SUPABASE_*, etc.)
- [ ] Run Supabase migrations for new tables
- [ ] Enable Realtime on progress/HITL tables

### Phase 2: Code Migration (Days 2-3)
- [ ] Create `src/modal_app/` directory structure
- [ ] Implement `app.py` with web endpoints
- [ ] Port phase functions from existing crews
- [ ] Implement state persistence helpers
- [ ] Implement HITL checkpoint/resume logic

### Phase 3: Testing (Days 4-5)
- [ ] Unit tests for state serialization
- [ ] Integration tests for Modal endpoints
- [ ] E2E test with real validation run
- [ ] HITL checkpoint flow testing
- [ ] Load testing (10 concurrent runs)

### Phase 4: Deployment & Cutover (Day 6)
- [ ] Deploy Modal app: `modal deploy src/modal_app/app.py`
- [ ] Update product app to use Modal endpoints
- [ ] Update Netlify edge functions
- [ ] Run E2E verification with production data
- [ ] Archive AMP deployment code to `archive/amp-deployment/`
- [ ] Update CLAUDE.md with new deployment instructions

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

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Modal downtime | Low | High | Implement retry logic, monitor status page |
| State corruption | Low | High | Pydantic validation, transactional DB updates |
| HITL race conditions | Medium | Medium | Idempotent approvals, optimistic locking |
| Cost overruns | Low | Low | Set Modal spend alerts, monitor usage |
| Learning curve | Medium | Low | Modal has excellent docs, Python-native |

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Deployment success rate | >99% | Modal dashboard |
| E2E validation completion | >95% | Supabase query |
| HITL checkpoint reliability | 100% | No lost approvals |
| Cost per validation | <$6 | Modal billing |
| UI update latency | <500ms | Realtime subscription |

## Related Documents

- [ADR-001: Flow to 3-Crew Migration](./001-flow-to-crew-migration.md) - Superseded by this ADR
- `docs/master-architecture/09-status.md` - Current implementation status
- `docs/deployment/3-crew-deployment.md` - To be deprecated
- Modal Documentation: https://modal.com/docs/guide

## Changelog

| Date | Change |
|------|--------|
| 2026-01-08 | Initial proposal |
