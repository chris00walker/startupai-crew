---
purpose: "CrewAI AMP platform configuration and capabilities reference"
status: "active"
last_reviewed: "2025-11-21"
---

# CrewAI AMP Platform Configuration

This document clarifies what CrewAI AMP provides out-of-the-box versus what StartupAI must configure or implement.

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

**Base URL**: `https://startupai-b4d5c1dd-27e2-4163-b9fb-a18ca06ca-4f4192a6.crewai.com`

**Bearer Token**: `<your-deployment-token>` (stored in dashboard)

### Endpoints

```bash
# Get input schema
curl https://[base-url]/inputs \
  -H "Authorization: Bearer [token]"

# Start validation
curl -X POST https://[base-url]/kickoff \
  -H "Authorization: Bearer [token]" \
  -H "Content-Type: application/json" \
  -d '{"entrepreneur_input": "Business idea..."}'

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
crewai deploy status --uuid b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b

# Push new version
crewai deploy push --uuid b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b

# View logs
crewai deploy logs --uuid b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b

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

### Budget Targets
- **Phase 1 run**: ~50K tokens ($1-2)
- **Full validation**: ~100K tokens ($3-5)
- **Monthly cap**: Set alerts in dashboard

---

## References

- [CLAUDE.md](../../../CLAUDE.md) - Deployment details
- [03-validation-spec.md](../03-validation-spec.md) - Flow architecture
- [flywheel-learning.md](./flywheel-learning.md) - Learning system
- [approval-workflows.md](./approval-workflows.md) - HITL patterns
- CrewAI AMP documentation: https://docs.crewai.com

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-11-21 | Initial configuration reference | Claude + Chris |
