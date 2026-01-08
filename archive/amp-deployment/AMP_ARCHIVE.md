# CrewAI AMP Deployment Archive

**Archived**: 2026-01-08
**Reason**: Migrating to Modal Serverless per [ADR-002](../../docs/adr/002-modal-serverless-migration.md)
**Status**: DEPRECATED - Do not use

---

## Organization

**Organization Name**: StartupAI
**Organization ID**: `8f17470f-7841-4079-860d-de91ed5d1091`
**Dashboard**: https://app.crewai.com/deployments

---

## Crew Deployments

### Crew 1: Intake (Main Repository)

| Property | Value |
|----------|-------|
| **Repository** | `chris00walker/startupai-crew` |
| **UUID** | `6b1e5c4d-e708-4921-be55-08fcb0d1e94b` |
| **Token** | `db9f9f4c1a7a` |
| **API URL** | `https://startupai-6b1e5c4d-e708-4921-be55-08fcb0d1e-922bcddb.crewai.com` |
| **Agents** | 4 (O1, GV1, GV2, S1) |
| **Type** | `crew` |

### Crew 2: Validation Engine

| Property | Value |
|----------|-------|
| **Repository** | `chris00walker/startupai-crew-validation` |
| **UUID** | `3135e285-c0e6-4451-b7b6-d4a061ac4437` |
| **Token** | (check AMP dashboard before deletion) |
| **Agents** | 12 |
| **Type** | `crew` |

### Crew 3: Decision

| Property | Value |
|----------|-------|
| **Repository** | `chris00walker/startupai-crew-decision` |
| **UUID** | `7da95dc8-7bb5-4c90-925b-2861fa9cba20` |
| **Token** | `988cc694f297` |
| **Agents** | 3 |
| **Type** | `crew` |

---

## Environment Variables (Set in AMP Dashboard)

```env
# API Keys
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...

# Supabase
SUPABASE_URL=https://eqxropalhxjeyvfcoyxg.supabase.co
SUPABASE_KEY=eyJ...

# Webhooks (Product App receives CrewAI results)
STARTUPAI_WEBHOOK_URL=https://app.startupai.site/api/crewai/webhook
STARTUPAI_WEBHOOK_BEARER_TOKEN=startupai-webhook-secret-2024

# Netlify (for LP deployment)
NETLIFY_ACCESS_TOKEN=xxx

# Crew Chaining (set in each crew's dashboard)
# Crew 1 needs:
CREW_2_URL=https://startupai-3135e285-c0e6-4451-b7b6-d4a061ac4437-xxx.crewai.com
CREW_2_BEARER_TOKEN=<crew-2-token>

# Crew 2 needs:
CREW_3_URL=https://startupai-7da95dc8-7bb5-4c90-925b-2861fa9cba20-xxx.crewai.com
CREW_3_BEARER_TOKEN=988cc694f297
```

---

## Previous Deployment IDs (Pre-Restructure)

From earlier attempts before the 3-crew structure:
- Crew 1: `7a73e75d-b611-4780-8f99-a05fca9b44bb` (Token: `13a07597a155`)
- Crew 2: `06d6a951-67ef-4936-b6d8-6fcaf5801b68` (Token: `6e274e9be0db`)
- Crew 3: `5a4330ef-0394-441d-bc2f-d458fde7ec06` (Token: `b07cee1f4637`)

---

## Crew Architecture

```
┌─────────────────────┐     ┌─────────────────────┐     ┌────────────────┐
│   CREW 1: INTAKE    │────▶│ CREW 2: VALIDATION  │────▶│ CREW 3: DECIDE │
│   (4 agents)        │     │ ENGINE (12 agents)  │     │ (3 agents)     │
└─────────────────────┘     └─────────────────────┘     └────────────────┘
         │                           │                           │
         │ InvokeCrewAI             │ InvokeCrewAI              │
         │ AutomationTool           │ AutomationTool            │
         └───────────────────────────┴───────────────────────────┘
```

---

## Canonical vs AMP Architecture

| Metric | Canonical | AMP Deployment |
|--------|-----------|----------------|
| Phases | 5 | 3 (compressed) |
| Flows | 5 | N/A (crews only) |
| Crews | 14 | 3 |
| Agents | 45 | 19 |
| HITL | 10 | 7 |
| Repos | 1 | 3 |

---

## AMP Endpoints Used

### Kickoff
```bash
curl -X POST https://startupai-6b1e5c4d-e708-4921-be55-08fcb0d1e-922bcddb.crewai.com/kickoff \
  -H "Authorization: Bearer db9f9f4c1a7a" \
  -H "Content-Type: application/json" \
  -d '{"entrepreneur_input": "Business idea..."}'
```

### Status Check
```bash
curl https://startupai-6b1e5c4d-e708-4921-be55-08fcb0d1e-922bcddb.crewai.com/status/{kickoff_id} \
  -H "Authorization: Bearer db9f9f4c1a7a"
```

### Resume (HITL)
```bash
curl -X POST https://startupai-...crewai.com/resume \
  -H "Authorization: Bearer db9f9f4c1a7a" \
  -H "Content-Type: application/json" \
  -d '{"execution_id": "...", "task_id": "...", "human_feedback": "...", "is_approve": true}'
```

---

## Known Issues (Reasons for Migration)

1. **`source: memory` bug**: AMP returned cached results without executing code
2. **Dashboard "Waiting for events"**: Flows never actually ran
3. **3-repo workaround**: Required separate repos for crew chaining
4. **Always-on costs**: Containers run during HITL waits
5. **InvokeCrewAIAutomationTool latency**: Added ~10-15s per crew transition

---

## Archived Files

```
archive/amp-deployment/
├── AMP_ARCHIVE.md              # This file
├── flow-architecture/          # Original Flow-based code
│   ├── startupai/
│   └── main.py
└── crew-templates/             # 3-Crew template code
    ├── crew-1-intake/
    ├── crew-2-validation/
    └── crew-3-decision/
```

---

## Migration Reference

- **Target Architecture**: Modal Serverless
- **ADR**: [ADR-002](../../docs/adr/002-modal-serverless-migration.md)
- **Benefits**: $0 idle, $0 during HITL, single repo, full 45-agent architecture

---

**Last Updated**: 2026-01-08
