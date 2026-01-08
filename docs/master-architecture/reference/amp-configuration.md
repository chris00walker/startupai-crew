---
purpose: "CrewAI AMP platform configuration and capabilities reference"
status: "deprecated"
last_reviewed: "2026-01-08"
vpd_compliance: true
superseded_by: "modal-configuration.md"
---

# CrewAI AMP Platform Configuration

> **⚠️ DEPRECATED**: This document describes the CrewAI AMP platform configuration which is being replaced by Modal serverless.
>
> - **Replacement**: [modal-configuration.md](./modal-configuration.md)
> - **Migration Decision**: [ADR-002](../../adr/002-modal-serverless-migration.md)
>
> This document is preserved for historical reference only. Do not use for new implementations.

---

This document clarifies what CrewAI AMP provides out-of-the-box versus what StartupAI must configure or implement.

> **VPD Framework**: AMP deployment supports the multi-phase VPD architecture. See phase documents (04-08) for crew configurations.

---

## What AMP Provides (No Custom Design Needed)

### Infrastructure
- **Managed execution environment** - No server management
- **Auto-scaling** - Handles concurrent validation runs
- **GitHub integration** - Deploy on push to main branch
- **Multi-environment support** - Dev/staging/production

### API Gateway
- **Auto-generated REST API**
  - `POST /kickoff` - Start validation
  - `GET /status/{id}` - Check progress
  - `GET /inputs` - Schema discovery
- **Authentication** - Bearer token per deployment
- **Rate limiting** - Platform-managed

### Observability
- **Execution dashboard** - View all runs
- **Trace details** - Agent reasoning, task execution
- **Token metrics** - Usage per run
- **Cost estimates** - Approximate spend per run
- **Timing data** - Execution duration

### Security
- **RBAC** - Role-based access in dashboard
- **Audit logs** - Access history
- **Encrypted environment variables** - Secrets stored securely
- **Token management** - Deployment tokens

### Webhook Events
- **Event streaming** - Push notifications for:
  - Flow events (start, complete, error)
  - Crew events (kickoff, complete)
  - Task events (start, complete)
  - Agent events (reasoning, tool use)
  - LLM events (calls, responses)
  - Custom events (emit your own)

---

## What StartupAI Must Configure

### Environment Variables (AMP Dashboard)

Navigate to: **CrewAI Dashboard → Deployments → Environment Variables**

| Variable | Purpose | Required |
|----------|---------|----------|
| `OPENAI_API_KEY` | LLM API access | Yes |
| `SUPABASE_URL` | Database connection | Yes |
| `SUPABASE_KEY` | Database authentication | Yes |
| `WEBHOOK_URL` | Product app callback | For HITL |
| `WEBHOOK_SECRET` | Webhook authentication | For HITL |

**Note**: `.env` files are NOT used by deployed crews. All environment variables must be set in the AMP dashboard.

### Webhook Configuration

For Human-in-the-Loop approval workflows:

1. **Product App Webhook Endpoint**
   ```
   https://app.startupai.site/api/approvals/webhook
   ```

2. **Event Types to Enable**
   - `task.complete` - Notify on task completion
   - `flow.waiting` - HITL approval needed
   - `flow.complete` - Validation finished
   - `flow.error` - Error occurred

3. **Authentication**
   - Include `WEBHOOK_SECRET` in dashboard
   - Product app validates signature

4. **Phase 0/1 Specific Events**
   - `interview.followup_needed` - Multi-turn interview continues
   - `qa.validation_complete` - Concept/intent validation done
   - `brief.ready_for_approval` - Founder's Brief ready for HITL
   - `vpc.profile_updated` - Customer Profile element changed
   - `vpc.fit_assessed` - Fit score calculated
   - `experiment.completed` - Test Card result recorded

### GitHub Integration

1. **Repository**: `chris00walker/startupai-crew`
2. **Branch**: `main`
3. **Auto-deploy**: Enabled on push

---

## What StartupAI Must Implement

### State Persistence
AMP runs the code but doesn't manage persistence.

**We implement**:
- `@persist()` decorator placement in flows
- Storage backend choice (SQLite default or Supabase)
- State recovery logic after failures

**Phase 0 Specific Requirements**:
- **Interview State**: Preserve multi-turn conversation context
- **Founder's Brief**: Immutable once `approve_founders_brief` HITL passes
- **Brief Injection**: Phase 1 crews receive complete brief in task context

**Phase 1 Specific Requirements**:
- **VPC State**: Customer Profile and Value Map must persist across experiments
- **Experiment Traceability**: Link Learning Cards to VPC element updates
- **Fit Score History**: Track progression across iteration cycles

**Reference**: See `state_schemas.py` and Flow definitions

### Error Recovery
CrewAI retries LLM parsing errors automatically.

**We implement**:
- Custom retry logic in `@router` methods
- Graceful degradation patterns
- Partial failure handling

**Example**:
```python
@router(governance_review)
def qa_gate(self):
    if self.state.qa_status == "passed":
        return "approved"
    elif self.state.retry_count < 3:
        self.state.retry_count += 1
        return "needs_revision"
    else:
        return "manual_review"  # Escalate to human
```

### Memory/Learning System
AMP provides basic in-memory buffers.

**We implement**:
- Flywheel learning capture tools
- Anonymization pipeline
- Supabase pgvector retrieval

**Reference**: See [flywheel-learning.md](./flywheel-learning.md)

### Cost Tracking
AMP shows costs but doesn't enforce budgets.

**We implement**:
- Token budget tracking per validation
- Alert thresholds
- Model selection strategy

---

## AMP Dashboard Checklist

### Initial Setup
- [ ] Link GitHub repository
- [ ] Set deployment UUID
- [ ] Configure bearer token
- [ ] Set all environment variables
- [ ] Enable webhook events (if using HITL)

### Per-Deployment
- [ ] Verify environment variables updated
- [ ] Test `/kickoff` endpoint
- [ ] Check logs for errors
- [ ] Verify webhook delivery (if configured)

### Monitoring
- [ ] Review execution costs weekly
- [ ] Check error rates
- [ ] Audit token usage trends
- [ ] Verify trace quality

---

## API Endpoints Reference

### Production Deployment

**Base URL**: `https://startupai-6b1e5c4d-e708-4921-be55-08fcb0d1e-922bcddb.crewai.com`

**Bearer Token**: `<your-deployment-token>` (stored in dashboard)

### Endpoints

```bash
# Get input schema
curl https://[base-url]/inputs \
  -H "Authorization: Bearer [token]"

# Start validation (Phase 1+ with approved brief)
curl -X POST https://[base-url]/kickoff \
  -H "Authorization: Bearer [token]" \
  -H "Content-Type: application/json" \
  -d '{"founder_input": "Business idea...", "brief_id": "uuid"}'

# Check status
curl https://[base-url]/status/{kickoff_id} \
  -H "Authorization: Bearer [token]"
```

### Status Response

```json
{
  "status": "running|complete|error",
  "result": {...},
  "errors": [...],
  "started_at": "2025-11-21T10:00:00Z",
  "completed_at": "2025-11-21T10:15:00Z"
}
```

---

## CLI Commands Reference

```bash
# Authentication (one-time per machine)
crewai login

# Check deployment status
crewai deploy status --uuid 6b1e5c4d-e708-4921-be55-08fcb0d1e94b

# Push new version
crewai deploy push --uuid 6b1e5c4d-e708-4921-be55-08fcb0d1e94b

# View logs
crewai deploy logs --uuid 6b1e5c4d-e708-4921-be55-08fcb0d1e94b

# Local testing (requires .env with OPENAI_API_KEY)
crewai run
```

---

## Troubleshooting

### "Environment variable not found"
**Cause**: Variable set in `.env` but not in AMP dashboard
**Fix**: Add to Dashboard → Environment Variables

### "Webhook delivery failed"
**Cause**: Product app endpoint not reachable
**Fix**: Check product app is deployed, verify URL in dashboard

### "Token usage spike"
**Cause**: Agent loops or verbose prompts
**Fix**: Check task definitions, add early termination conditions

### "Status stuck at running"
**Cause**: Long-running task or deadlock
**Fix**: Check logs for errors, verify all crews complete properly

---

## Cost Optimization

### Model Selection Strategy
- **GPT-4**: Complex reasoning tasks (Compass synthesis, Guardian QA)
- **GPT-3.5-Turbo**: Structured extraction (data parsing, formatting)
- **text-embedding-ada-002**: Learning embeddings

### Token Reduction
- Keep prompts focused and specific
- Use structured output formats
- Cache repeated analyses
- Limit agent verbosity

### Budget Targets by Phase
- **Phase 0 interview**: ~10K tokens ($0.30)
- **Phase 0 with follow-ups**: ~25K tokens ($0.75)
- **Phase 1 VPC Discovery**: ~50K tokens ($1-2)
- **Phase 2+ validation**: ~50K tokens ($1-2)
- **Full validation (all phases)**: ~125K tokens ($4-6)
- **Monthly cap**: Set alerts in dashboard

---

## References

- [CLAUDE.md](../../../CLAUDE.md) - Deployment details
- [05-phase-0-1-specification.md](../05-phase-0-1-specification.md) - Phase 0-1 VPD specification
- [03-validation-spec.md](../03-validation-spec.md) - Phase 2+ flow architecture
- [flywheel-learning.md](./flywheel-learning.md) - Learning system
- [approval-workflows.md](./approval-workflows.md) - HITL patterns
- CrewAI AMP documentation: https://docs.crewai.com

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-11-21 | Initial configuration reference | Claude + Chris |
| 2025-12-04 | Update deployment UUID and URL | Claude + Chris |
| 2026-01-05 | Add Phase 0/1 webhook events, state persistence, cost estimates | Claude + Chris |
