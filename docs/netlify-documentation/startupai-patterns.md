# StartupAI Netlify Patterns

Netlify patterns specific to the StartupAI ecosystem, including product app deployment, webhook integration, and edge triggers.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  StartupAI Three-Layer Architecture                             │
├─────────────────────────────────────────────────────────────────┤
│  INTERACTION LAYER (Netlify)                                    │
│  • Marketing site: startupai.site                               │
│  • Product app: app.startupai.site                              │
│  • User triggers validation                                     │
│  • Receives real-time progress updates                          │
│  • Handles HITL approvals                                       │
├─────────────────────────────────────────────────────────────────┤
│  ORCHESTRATION LAYER (Supabase)                                │
│  • State persistence (PostgreSQL)                               │
│  • Real-time updates (WebSocket)                                │
│  • Approval queue management                                    │
├─────────────────────────────────────────────────────────────────┤
│  COMPUTE LAYER (Modal)                                          │
│  • 5 Flow functions (one per phase)                             │
│  • Ephemeral containers (pay-per-second)                        │
│  • Checkpoint-and-resume at HITL points                         │
└─────────────────────────────────────────────────────────────────┘
```

## StartupAI Sites

### Marketing Site

- **Domain**: startupai.site
- **Netlify Site**: `startupai-site`
- **Repository**: `chris00walker/startupai.site`
- **Purpose**: Lead capture, marketing content

### Product App

- **Domain**: app.startupai.site
- **Netlify Site**: `app-startupai-site`
- **Repository**: `chris00walker/app.startupai.site`
- **Framework**: Next.js 15
- **Purpose**: User dashboard, validation workflow, results

## Environment Variables

### Product App (app.startupai.site)

```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://eqxropalhxjeyvfcoyxg.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# Modal API
MODAL_API_URL=https://chris00walker--startupai-validation-fastapi-app.modal.run

# CrewAI Webhook (for receiving results)
CREWAI_WEBHOOK_SECRET=startupai-webhook-secret-2024

# Feature Flags
NEXT_PUBLIC_ENABLE_VALIDATION=true
NEXT_PUBLIC_ENABLE_HITL=true
```

### Context-Specific Configuration

```toml
# netlify.toml

[build]
  command = "npm run build"
  publish = ".next"

[build.environment]
  NODE_VERSION = "20"

[context.production.environment]
  NEXT_PUBLIC_API_URL = "https://chris00walker--startupai-validation-fastapi-app.modal.run"
  NEXT_PUBLIC_SUPABASE_URL = "https://eqxropalhxjeyvfcoyxg.supabase.co"

[context.deploy-preview.environment]
  NEXT_PUBLIC_API_URL = "https://staging-api.startupai.site"
  NEXT_PUBLIC_SUPABASE_URL = "https://eqxropalhxjeyvfcoyxg.supabase.co"
```

## API Routes

### CrewAI Webhook Handler

Receives results from Modal/CrewAI validation engine:

```typescript
// app/api/crewai/webhook/route.ts

import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
)

export async function POST(req: Request) {
  // Verify webhook secret
  const authHeader = req.headers.get('authorization')
  if (authHeader !== `Bearer ${process.env.CREWAI_WEBHOOK_SECRET}`) {
    return new Response('Unauthorized', { status: 401 })
  }

  const payload = await req.json()
  const { flow_type, run_id, status, result } = payload

  // Update validation run
  await supabase
    .from('validation_runs')
    .update({
      status,
      final_report: result,
      completed_at: status === 'completed' ? new Date().toISOString() : null,
      updated_at: new Date().toISOString()
    })
    .eq('id', run_id)

  return Response.json({ received: true })
}
```

### Validation Kickoff

Triggers Modal validation engine:

```typescript
// app/api/crewai/analyze/route.ts

export async function POST(req: Request) {
  const { project_id, entrepreneur_input } = await req.json()

  // Create validation run record
  const { data: run } = await supabase
    .from('validation_runs')
    .insert({
      project_id,
      status: 'pending'
    })
    .select()
    .single()

  // Trigger Modal
  const response = await fetch(`${process.env.MODAL_API_URL}/kickoff`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      run_id: run.id,
      project_id,
      entrepreneur_input
    })
  })

  if (!response.ok) {
    throw new Error('Failed to start validation')
  }

  return Response.json({ run_id: run.id, status: 'started' })
}
```

### HITL Approval

Handles human approval decisions:

```typescript
// app/api/crewai/approve/route.ts

export async function POST(req: Request) {
  const { hitl_id, decision, notes } = await req.json()

  // Get HITL request
  const { data: hitl } = await supabase
    .from('hitl_requests')
    .select('run_id, checkpoint_name')
    .eq('id', hitl_id)
    .single()

  // Update HITL status
  await supabase
    .from('hitl_requests')
    .update({
      status: decision,
      decision_notes: notes,
      decided_at: new Date().toISOString()
    })
    .eq('id', hitl_id)

  // Resume Modal workflow
  await fetch(`${process.env.MODAL_API_URL}/hitl/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      run_id: hitl.run_id,
      checkpoint: hitl.checkpoint_name,
      decision
    })
  })

  return Response.json({ status: 'resumed' })
}
```

## Realtime Integration

### Progress Subscription (React Component)

```typescript
// components/ValidationProgress.tsx

'use client'

import { useEffect, useState } from 'react'
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

export function ValidationProgress({ runId }: { runId: string }) {
  const [status, setStatus] = useState('pending')
  const [phase, setPhase] = useState(0)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const channel = supabase
      .channel(`validation-${runId}`)
      .on(
        'postgres_changes',
        {
          event: 'UPDATE',
          schema: 'public',
          table: 'validation_runs',
          filter: `id=eq.${runId}`
        },
        (payload) => {
          const { status, current_phase, progress_percent } = payload.new
          setStatus(status)
          setPhase(current_phase)
          setProgress(progress_percent)
        }
      )
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [runId])

  return (
    <div>
      <p>Status: {status}</p>
      <p>Phase: {phase}/4</p>
      <progress value={progress} max={100} />
    </div>
  )
}
```

## Edge Functions

### Geolocation Personalization

```typescript
// netlify/edge-functions/geo.ts

export default async (request: Request, context: Context) => {
  const country = context.geo.country?.code

  // Add geolocation to headers for app
  const response = await context.next()
  const headers = new Headers(response.headers)
  headers.set('x-geo-country', country || 'unknown')
  headers.set('x-geo-city', context.geo.city || 'unknown')

  return new Response(response.body, {
    status: response.status,
    headers
  })
}

export const config = {
  path: '/*',
  excludedPath: ['/_next/*', '/static/*']
}
```

### Authentication Middleware

```typescript
// netlify/edge-functions/auth-check.ts

export default async (request: Request, context: Context) => {
  const url = new URL(request.url)

  // Protected routes
  if (url.pathname.startsWith('/dashboard') || url.pathname.startsWith('/api/')) {
    const supabaseToken = context.cookies.get('sb-access-token')

    if (!supabaseToken) {
      return Response.redirect(new URL('/login', request.url))
    }
  }

  return context.next()
}

export const config = {
  path: ['/dashboard/*', '/api/*']
}
```

## Deployment Pipeline

### Production Deploy

```bash
# Deploy to production
netlify deploy --prod --dir=.next

# Or via Git
git push origin main
# → Automatic deploy triggered
```

### Preview Deploy

Pull requests automatically get preview URLs:
```
https://deploy-preview-123--app-startupai-site.netlify.app
```

## Build Configuration

```toml
# netlify.toml

[build]
  command = "npm run build"
  publish = ".next"
  functions = "netlify/functions"

[build.environment]
  NODE_VERSION = "20"
  NEXT_TELEMETRY_DISABLED = "1"

# Next.js plugin
[[plugins]]
  package = "@netlify/plugin-nextjs"

# Edge functions
[[edge_functions]]
  function = "geo"
  path = "/*"

[[edge_functions]]
  function = "auth-check"
  path = ["/dashboard/*", "/api/*"]

# Redirects
[[redirects]]
  from = "/api/v1/*"
  to = "/.netlify/functions/:splat"
  status = 200

# Headers
[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
```

## Monitoring

### Deploy Notifications

Configure in Site settings > Deploy notifications:
- Slack: Deploy success/failure
- Email: Failed deploys
- GitHub: Commit status

### Build Logs

```bash
# Watch build in progress
netlify watch

# View recent deploys
netlify deploys
```

## External Resources

- [Modal Patterns](../modal-documentation/startupai-patterns.md)
- [Supabase Patterns](../supabase-documentation/startupai-patterns.md)
- [ADR-002: Modal Migration](../adr/002-modal-serverless-migration.md)
