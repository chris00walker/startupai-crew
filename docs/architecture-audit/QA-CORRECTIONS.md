# Audit Quality Assurance - Corrections

**Date**: 2026-01-06
**Issue**: Original audit contained several inaccuracies that need correction

---

## Critical Correction #1: Onboarding Architecture

### Original Audit Claimed:
> "Uses Agentuity agent, NOT interview-based"
> "Agentuity agent-driven conversational flow"

### Actual Truth:
The onboarding uses **Vercel AI SDK** (`streamText` from `ai` package), NOT Agentuity.

**Code Flow**:
```
OnboardingWizardV2.tsx
├── /api/onboarding/start → Creates session in Supabase (NO external call)
├── /api/chat → Vercel AI SDK (streamText) with OpenAI
└── /api/onboarding/complete → Creates project, triggers CrewAI
```

**Evidence**:
1. `OnboardingWizardV2.tsx:312` calls `/api/chat` for conversation
2. `/api/chat/route.ts:1` imports `streamText` from Vercel AI SDK
3. `/api/onboarding/start/route.ts` has `resolveAgentUrl()` function that is **NEVER CALLED** - it's dead code

### Dead Code Found:
The following Agentuity references are **DEAD CODE** that should be removed:

```
frontend/src/app/api/onboarding/start/route.ts:143-157 - resolveAgentUrl() never called
frontend/src/app/api/onboarding/message/route.ts:223-235 - resolveAgentUrl() dead path
frontend/src/components/onboarding/index.ts:1 - "Legacy V1 components (Agentuity integration)"
```

### Stale Documentation Found:
```
docs/specs/agentuity-integration.md - Marked deprecated but still exists
docs/ops/environments.md:392 - AGENTUITY_AGENT_URL documented but not used
docs/reports/ui-crewai-wiring-audit.md:142-143 - Claims Agentuity, incorrect
docs/archive/completion-reports/ONBOARDING_INTEGRATION_COMPLETE.md - All Agentuity references
docs/incidents/ONBOARDING_FIX_INSTRUCTIONS.md - Agentuity references
```

---

## Critical Correction #2: API Route Analysis

### Original Audit Claimed:
> `/api/onboarding/start` - "Uses Agentuity agent"
> `/api/onboarding/message` - "Streaming AI conversation via Agentuity"

### Actual Truth:
- `/api/onboarding/start` - Creates session in **Supabase only**, no external API call
- `/api/onboarding/message` - **NOT USED** by OnboardingWizardV2 (uses `/api/chat` instead)
- `/api/chat` - **This is the actual conversation handler** using Vercel AI SDK

The V2 component (`OnboardingWizardV2.tsx`) uses a different API path than the audit examined.

---

## Correction #3: Phantom Table Status

### Original Audit Claimed:
> "value_proposition_canvas - PHANTOM (Drizzle but no migration)"

### Reality Check Needed:
While the Drizzle schema exists, we should verify if there's an API route that creates this table on-demand or if the frontend actually tries to use it.

**Finding**: `/api/vpc/[projectId]/route.ts` EXISTS and attempts to query this table. This will fail at runtime because the table doesn't exist.

---

## Correction #4: Drizzle Schema Location

### Original Audit Claimed:
> "10+ tables missing Drizzle schemas"

### More Accurate Statement:
The schemas may exist but not be **exported from the index file**. Need to verify:
1. Do individual schema files exist?
2. Are they exported from `frontend/src/db/schema/index.ts`?

---

## Summary of Audit Quality Issues

| Issue | Severity | Impact |
|-------|----------|--------|
| Agentuity claim incorrect | HIGH | Misrepresents entire onboarding architecture |
| Dead code not identified | MEDIUM | Clutters codebase, confuses future audits |
| V1 vs V2 component confusion | HIGH | Audit examined wrong code path |
| Stale docs not flagged for deletion | LOW | Documentation debt |

---

## Corrected Onboarding Architecture

```
USER FLOW (ACTUAL):

[User] → OnboardingWizardV2.tsx
            │
            ├─ POST /api/onboarding/start
            │     └─ Creates session in onboarding_sessions table
            │     └─ Returns sessionId, stage info (NO external API)
            │
            ├─ POST /api/chat (LOOP for each message)
            │     └─ Uses Vercel AI SDK (streamText)
            │     └─ Uses OpenAI gpt-4o model
            │     └─ Has AI tools: assessQuality, advanceStage, completeOnboarding
            │     └─ Streams response back
            │
            └─ POST /api/onboarding/complete
                  └─ Creates entrepreneur_briefs
                  └─ Creates projects
                  └─ Triggers CrewAI /kickoff (fire-and-forget)
```

---

## Recommendations

### Immediate Actions

1. **Delete dead Agentuity code**:
   - Remove `resolveAgentUrl()` from `/api/onboarding/start/route.ts`
   - Remove `resolveAgentUrl()` from `/api/onboarding/message/route.ts`
   - Delete or update `docs/specs/agentuity-integration.md`
   - Clean `AGENTUITY_AGENT_URL` from environment documentation

2. **Update Evolution Plan**:
   - Correct the API section to reflect `/api/chat` as the conversation handler
   - Remove all Agentuity references

3. **Archive V1 Components**:
   - Move `OnboardingWizard.tsx` (V1) to archive
   - Move `ConversationInterface.tsx` (V1) to archive
   - Keep only V2 components active

### Documentation Updates

The following audit documents need correction:
- `02-API-AUDIT.md` - Fix onboarding endpoint descriptions
- `EVOLUTION-PLAN.md` - Fix API section

---

## Additional Finding: V1 Component Dead Code

### V1 vs V2 Component Usage

**Active (V2)**:
- `/app/onboarding/page.tsx` → imports `OnboardingWizardV2`
- `/app/onboarding/founder/page.tsx` → imports `OnboardingWizardV2`
- Uses `/api/chat` for conversation (Vercel AI SDK)

**Dead (V1)**:
- `OnboardingWizard.tsx` (V1) - NOT imported by any page
- Uses `/api/onboarding/message/` (Agentuity path)
- Only referenced by tests that are testing dead code

**Dead API Route**:
- `/api/onboarding/message/route.ts` - 500+ lines of code that is NEVER CALLED in production
- All tests that reference it are testing dead code paths

### Tests Testing Dead Code

The following test files test V1 behavior that is NOT used in production:

```
frontend/src/__tests__/api-contracts/endpoint-validation.test.tsx - Tests /api/onboarding/message/
frontend/src/__tests__/user-journey/success-metrics.test.tsx - Tests V1 flow
frontend/src/components/onboarding/__tests__/OnboardingWizard.test.tsx - Tests V1 component
```

---

## Verification Commands

To verify the actual architecture:

```bash
# Find what actually calls the onboarding APIs
grep -r "api/onboarding" frontend/src/components/ --include="*.tsx"

# Find Vercel AI SDK usage
grep -r "streamText\|from 'ai'" frontend/src/app/api/ --include="*.ts"

# Find dead Agentuity code
grep -ri "agentuity" frontend/src/app/api/ --include="*.ts"

# Check which onboarding component is used in pages
grep -r "OnboardingWizard" frontend/src/app/ --include="*.tsx"
```

---

## Files to Delete or Archive

### Definitely Delete (Dead Code):
```
frontend/src/app/api/onboarding/message/route.ts - 500+ lines, never called
frontend/src/components/onboarding/OnboardingWizard.tsx - V1, not used
frontend/src/components/onboarding/ConversationInterface.tsx - V1, not used
docs/specs/agentuity-integration.md - Deprecated, delete
```

### Archive (Stale Tests):
```
frontend/src/__tests__/api-contracts/endpoint-validation.test.tsx - Tests dead endpoint
frontend/src/components/onboarding/__tests__/OnboardingWizard.test.tsx - Tests V1
```

### Clean Up:
```
frontend/src/components/onboarding/index.ts - Remove V1 exports
docs/ops/environments.md - Remove AGENTUITY_AGENT_URL
```

---

## Corrected Counts

### Original Audit Claimed:
> "34 API endpoints exist"

### Corrected:
- 34 API routes exist in code
- But `/api/onboarding/message/` is **DEAD** (never called)
- Effective active endpoints: **33**

### Original Audit Claimed:
> "7 onboarding endpoints"

### Corrected:
- `/api/onboarding/start` - ACTIVE (creates session)
- `/api/onboarding/message` - **DEAD** (V1 only, not used)
- `/api/onboarding/status` - ACTIVE
- `/api/onboarding/complete` - ACTIVE
- `/api/onboarding/recover` - ACTIVE
- `/api/onboarding/abandon` - ACTIVE

Effective onboarding endpoints: **5** (plus `/api/chat` for conversation)
