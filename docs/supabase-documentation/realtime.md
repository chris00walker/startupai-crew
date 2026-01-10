# Supabase Realtime

Guide to Supabase Realtime for live data synchronization, messaging, and presence tracking.

## Overview

Supabase Realtime extends PostgreSQL with WebSocket-based features:

| Feature | Purpose |
|---------|---------|
| **Postgres Changes** | Listen to database INSERT/UPDATE/DELETE events |
| **Broadcast** | Low-latency pub/sub messaging between clients |
| **Presence** | Track and sync online user state |

## Quick Start

```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

// Subscribe to changes
const channel = supabase
  .channel('my-channel')
  .on('postgres_changes',
    { event: '*', schema: 'public', table: 'messages' },
    (payload) => console.log('Change:', payload)
  )
  .subscribe()
```

## Postgres Changes

Listen to database modifications in real-time.

### Subscribe to All Changes

```typescript
const channel = supabase
  .channel('db-changes')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'validation_runs' },
    (payload) => {
      console.log('Change type:', payload.eventType)
      console.log('New data:', payload.new)
      console.log('Old data:', payload.old)
    }
  )
  .subscribe()
```

### Subscribe to Specific Events

```typescript
// INSERT only
.on('postgres_changes',
  { event: 'INSERT', schema: 'public', table: 'messages' },
  handleInsert
)

// UPDATE only
.on('postgres_changes',
  { event: 'UPDATE', schema: 'public', table: 'messages' },
  handleUpdate
)

// DELETE only
.on('postgres_changes',
  { event: 'DELETE', schema: 'public', table: 'messages' },
  handleDelete
)
```

### Filter by Column Value

```typescript
// Only listen to changes for specific project
const channel = supabase
  .channel('project-updates')
  .on(
    'postgres_changes',
    {
      event: 'UPDATE',
      schema: 'public',
      table: 'validation_runs',
      filter: 'project_id=eq.abc-123'
    },
    handleProjectUpdate
  )
  .subscribe()
```

### Enable Realtime on Table

Realtime must be enabled per-table in Supabase dashboard or via SQL:

```sql
-- Enable via publication
ALTER PUBLICATION supabase_realtime ADD TABLE validation_runs;

-- Or for specific columns only (reduces payload size)
ALTER PUBLICATION supabase_realtime ADD TABLE validation_runs (id, status, phase);
```

## Broadcast

Low-latency pub/sub messaging between clients (no database involved).

### Send Messages

```typescript
const channel = supabase.channel('room-1')

// Subscribe first
await channel.subscribe()

// Send to all subscribers
channel.send({
  type: 'broadcast',
  event: 'cursor-move',
  payload: { x: 100, y: 200, user_id: 'user-123' }
})
```

### Receive Messages

```typescript
const channel = supabase
  .channel('room-1')
  .on('broadcast', { event: 'cursor-move' }, (payload) => {
    console.log('Cursor moved:', payload)
  })
  .subscribe()
```

### Use Cases

- Cursor tracking in collaborative apps
- Typing indicators
- Real-time notifications
- Game state synchronization

## Presence

Track and synchronize online user state across clients.

### Track User State

```typescript
const channel = supabase.channel('online-users')

// Track current user
await channel.subscribe(async (status) => {
  if (status === 'SUBSCRIBED') {
    await channel.track({
      user_id: 'user-123',
      online_at: new Date().toISOString(),
      status: 'online'
    })
  }
})
```

### Listen to Presence Changes

```typescript
const channel = supabase
  .channel('online-users')
  .on('presence', { event: 'sync' }, () => {
    const state = channel.presenceState()
    console.log('Online users:', state)
  })
  .on('presence', { event: 'join' }, ({ key, newPresences }) => {
    console.log('User joined:', newPresences)
  })
  .on('presence', { event: 'leave' }, ({ key, leftPresences }) => {
    console.log('User left:', leftPresences)
  })
  .subscribe()
```

### Update Presence

```typescript
// Update current user's state
await channel.track({
  user_id: 'user-123',
  status: 'away'
})
```

## Channel Management

### Unsubscribe

```typescript
// Unsubscribe from specific channel
await supabase.removeChannel(channel)

// Unsubscribe from all channels
await supabase.removeAllChannels()
```

### Channel Status

```typescript
channel.subscribe((status) => {
  switch (status) {
    case 'SUBSCRIBED':
      console.log('Connected!')
      break
    case 'CHANNEL_ERROR':
      console.log('Error connecting')
      break
    case 'TIMED_OUT':
      console.log('Connection timed out')
      break
    case 'CLOSED':
      console.log('Channel closed')
      break
  }
})
```

## StartupAI Pattern: Validation Progress

Real-time progress updates for validation runs:

```typescript
// Subscribe to validation run updates
const subscribeToValidation = (runId: string, onUpdate: (data: any) => void) => {
  return supabase
    .channel(`validation-${runId}`)
    .on(
      'postgres_changes',
      {
        event: 'UPDATE',
        schema: 'public',
        table: 'validation_runs',
        filter: `id=eq.${runId}`
      },
      (payload) => onUpdate(payload.new)
    )
    .subscribe()
}

// Usage in React
useEffect(() => {
  const channel = subscribeToValidation(runId, (data) => {
    setPhase(data.current_phase)
    setStatus(data.status)
    setProgress(data.progress_percent)
  })

  return () => {
    supabase.removeChannel(channel)
  }
}, [runId])
```

## Performance Tips

1. **Filter server-side** - Use `filter` parameter to reduce traffic
2. **Limit columns** - Only publish needed columns in publication
3. **Use Broadcast for ephemeral data** - Don't persist cursor positions
4. **Debounce Presence updates** - Don't track on every keystroke
5. **Clean up channels** - Always unsubscribe on component unmount

## RLS and Realtime

Realtime respects RLS policies:

```sql
-- Users only receive changes for their own projects
CREATE POLICY "Realtime: own projects only"
ON validation_runs
FOR SELECT
TO authenticated
USING (project_id IN (
  SELECT id FROM projects WHERE owner_id = auth.uid()
));
```

## External Resources

- [Supabase Realtime Docs](https://supabase.com/docs/guides/realtime)
- [Realtime GitHub](https://github.com/supabase/realtime)
- [Realtime Quickstart](https://supabase.com/docs/guides/realtime/quickstart)
