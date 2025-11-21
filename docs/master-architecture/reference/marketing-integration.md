---
purpose: Marketing site AI integration architecture
status: planning
last_reviewed: 2025-11-21
---

# Marketing Site AI Integration

The marketing site (startupai.site) requires AI integration to embody our transparency values and demonstrate the AI Founders' capabilities before conversion.

## Customer Service Agent

**Dual Placement Strategy**:

### 1. Floating Chat Widget
- Persistent bottom-right bubble available on all pages
- General support agent answering questions about StartupAI, pricing, features
- Implemented in site `layout.tsx` for global availability
- Uses Vercel AI SDK for streaming responses

### 2. Founder-Specific Chat in Modals
- Extend `FounderProfileCard.tsx` with tabbed interface: "Profile" | "Chat"
- Each founder responds in character based on their role:
  - **Sage**: Strategy questions, VPC design, customer insights
  - **Forge**: Technical feasibility, build considerations
  - **Pulse**: Growth tactics, market signals
  - **Compass**: Synthesis, tradeoffs, decision support
  - **Guardian**: Governance, risk, accountability
  - **Ledger**: Financial viability, unit economics
- System prompts derived from founder personality/role in `aiFounders` data

### Backend Architecture
- Netlify function: `/.netlify/functions/chat`
- Input: `{ message: string, founderId?: string, context?: string }`
- Routes to AI model with founder-specific system prompts
- Stores conversation history in Supabase for continuity

## Live Data Integration

Replace all hardcoded mock data with live platform metrics to demonstrate transparency.

### Supabase Schema (New Tables)

```sql
-- Aggregated platform statistics
CREATE TABLE platform_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  metric_name TEXT NOT NULL,          -- 'validations_completed', 'mvps_built', etc.
  metric_value INTEGER NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Anonymized recent agent activities
CREATE TABLE public_activity_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  founder_id TEXT NOT NULL,           -- 'sage', 'forge', etc.
  activity_type TEXT NOT NULL,        -- 'analysis', 'build', 'validation'
  description TEXT NOT NULL,          -- Anonymized activity description
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Per-founder performance metrics
CREATE TABLE founder_stats (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  founder_id TEXT NOT NULL UNIQUE,
  analyses_completed INTEGER DEFAULT 0,
  accuracy_rate DECIMAL(5,2),
  avg_response_time INTERVAL,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Netlify Functions (Data Layer)

**`/.netlify/functions/metrics`**
- Returns: platform stats + founder stats
- Caches responses (5-10 min TTL)
- Reduces Supabase load

**`/.netlify/functions/activities`**
- Returns: recent anonymized activities
- Filterable by founder
- Paginated results

### Frontend Data Flow

**Current State** (to replace):
```typescript
// src/data/agentActivity.ts - hardcoded
export const aiFounders = [
  { name: "Guardian", stats: { analyses: 142, accuracy: "94%" } },
  // ...
];
```

**Target State**:
```typescript
// src/data/agentActivity.ts - fetches live data
export async function getFounderStats(): Promise<FounderStats[]> {
  const response = await fetch('/.netlify/functions/metrics');
  return response.json();
}

// Components use React Query or SWR for caching
const { data: founders, isLoading } = useQuery('founders', getFounderStats);
```

### Mock Data Locations to Replace

| File | Data | Replacement |
|------|------|-------------|
| `src/data/agentActivity.ts:45-192` | `aiFounders` stats | `/.netlify/functions/metrics` |
| `src/data/agentActivity.ts:195-265` | `recentActivities` | `/.netlify/functions/activities` |
| `src/data/agentActivity.ts` | `dashboardMetrics` | `/.netlify/functions/metrics` |
| `src/app/demo/dashboard/page.tsx:29-65` | `activeWorkflows` | Keep demo data (not production) |

**Note**: Static data (names, roles, avatars, personalities) remains hardcoded. Only dynamic metrics and activities fetch from API.

## Implementation Sequence

1. **Supabase schema** - Create tables for metrics and activities
2. **Netlify functions** - Build data fetching endpoints with caching
3. **Update agentActivity.ts** - Export async fetch functions instead of static arrays
4. **Component updates** - Add loading states, error handling, async data fetching
5. **Shared chat component** - Build reusable chat UI
6. **Floating widget** - Implement global chat bubble
7. **Founder modal chat** - Add chat tab to existing modals
8. **Chat backend** - Create Netlify function with founder-specific prompts

## Data Architecture Decision

**Recommended: Netlify Functions → Supabase**

Rationale:
- Keeps marketing site self-contained and deployable
- Enables caching to reduce Supabase load
- Allows rate limiting and security at function layer
- Can be upgraded to call product app API later if needed
- Consistent with existing `/.netlify/functions/contact` pattern

---

## Related Documents

- [02-organization.md](../02-organization.md) - Founder roles and personalities
- [api-contracts.md](./api-contracts.md) - API specifications

---
**Last Updated**: 2025-11-21
