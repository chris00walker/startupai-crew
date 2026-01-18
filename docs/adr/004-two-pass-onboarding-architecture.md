# ADR-004: Two-Pass Onboarding Architecture (Backend-Driven Assessment)

**Status**: Implemented (Errata Fixed - see Changelog 2026-01-16)
**Date**: 2026-01-16
**Decision Makers**: Chris Walker, Claude AI Assistant
**Context**: Onboarding stage progression reliability
**Related**: [Plan: async-mixing-ritchie.md](/home/chris/.claude/plans/async-mixing-ritchie.md)
**Evolution**: [ADR-005: State-First Synchronized Loop](./005-state-first-synchronized-loop.md) - Proposed successor addressing concurrency and serverless durability

## Summary

Replace unreliable LLM tool-calling for stage progression with deterministic backend-driven quality assessment. The LLM handles conversation only (Pass 1), while the backend always runs structured assessment (Pass 2) after each response.

## Context

### The Problem

The onboarding chat relied on the LLM calling `assessQuality`, `advanceStage`, and `completeOnboarding` tools to track progress and advance stages. Analysis of session `cf0d5e8f` revealed critical reliability issues:

| Metric | Value |
|--------|-------|
| Overall tool call rate | **18%** (4/22 assistant messages) |
| Stage 4 tool call rate | **7%** (1/15 messages) |
| Result | Session stuck at Stage 4 with 42% progress |

**Root Cause**: Using `toolChoice: 'auto'` lets the LLM decide when to call tools. As conversation context grows, the LLM increasingly ignores tool instructions, prioritizing conversational responses over structured assessment.

### Previous Fix Attempts (All Failed)

| Attempt | Theory | Fix | Result |
|---------|--------|-----|--------|
| Prompt reorder | "Text first" wrong | Changed to "tools first" | Failed |
| prepareStep | Need guaranteed steps | Added step control | Failed |
| toolChoice: 'required' | 'auto' too weak | Forced tools | Broke text generation |
| OpenRouter switch | Provider issue | Changed providers | Tool rate still low |

**Key Insight**: This is an architectural anti-pattern - using non-deterministic agents for state management. The LLM should handle conversation; the backend should handle state transitions.

## Decision

**Implement Two-Pass Architecture**: Separate conversation generation from quality assessment.

### Architecture

```
Pass 1: Conversation (streaming)     Pass 2: Assessment (deterministic)
┌─────────────────────────────────┐  ┌─────────────────────────────────┐
│ LLM generates response          │  │ Backend ALWAYS calls            │
│ NO tools, just conversation     │→ │ generateObject for quality      │
│ Streams to user immediately     │  │ assessment after response       │
└─────────────────────────────────┘  └─────────────────────────────────┘
                                                    ↓
                                     ┌─────────────────────────────────┐
                                     │ Deterministic state machine     │
                                     │ - Merge extractedData → brief   │
                                     │ - Update stage_progress         │
                                     │ - Auto-advance if threshold     │
                                     │ - Trigger CrewAI at Stage 7     │
                                     └─────────────────────────────────┘
```

### Implementation

**New Module**: `/frontend/src/lib/onboarding/quality-assessment.ts`

```typescript
// Core functions
export async function assessConversationQuality(
  stage: number,
  history: ConversationMessage[],
  existingBrief: Record<string, unknown>
): Promise<QualityAssessment | null>

export function shouldAdvanceStage(
  assessment: QualityAssessment,
  currentStage: number
): boolean

export function isOnboardingComplete(
  assessment: QualityAssessment,
  currentStage: number
): boolean

export function mergeExtractedData(
  existingBrief: Record<string, unknown>,
  extractedData: Record<string, unknown> | undefined
): Record<string, unknown>

export function hashMessageForIdempotency(
  sessionId: string,
  messageIndex: number,
  stage: number,
  userMessage: string
): string
```

**ConversationMessage Interface**:

```typescript
// Messages stored in conversation_history must include timestamp for UI rendering
export interface ConversationMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  stage?: number;      // Stage tag for assessment filtering
  timestamp?: string;  // ISO timestamp for UI display (REQUIRED for proper rendering)
}
```

**Quality Assessment Schema**:

```typescript
const qualityAssessmentSchema = z.object({
  coverage: z.number().min(0).max(1),
  clarity: z.enum(['high', 'medium', 'low']),
  completeness: z.enum(['complete', 'partial', 'insufficient']),
  notes: z.string(),
  extractedData: z.object({
    business_concept: z.string().optional(),
    target_customers: z.array(z.string()).optional(),
    // ... all 25+ stage-specific fields
  }).optional(),
  // Stage 7 completion: MUST have .min(3) to prevent completion stall
  keyInsights: z.array(z.string()).min(3).optional(),
  recommendedNextSteps: z.array(z.string()).min(3).optional(),
});
```

### Key Design Decisions

1. **Provider**: OpenRouter with `claude-3.5-haiku` for assessment
   - Fast (~200-400ms), cheap (~$0.0003/call)
   - Excellent at structured output extraction
   - Same provider as conversation (no additional API key)

2. **Idempotency**: Hash-based key using `sessionId + messageIndex + stage + userMessage`
   - Prevents duplicate assessments on retry
   - Different hash for identical messages at different stages

3. **Atomic Completion**: Supabase conditional update for CrewAI trigger
   - `.is('stage_data->completion', null)` ensures single trigger
   - Database-level atomicity prevents race conditions

4. **Retry Strategy**: Exponential backoff with 3 retries
   - 1s, 2s, 4s delays (capped at 5s)
   - Failure marker stored for admin monitoring
   - Never blocks user conversation

5. **Legacy Message Handling**: Fallback for untagged messages
   - Assessment filters by `stage` tag: `history.filter(m => m.stage === stage)`
   - Pre-deployment sessions lack stage tags
   - Fallback: if no tagged messages, include all non-system messages
   - Ensures resumed legacy sessions continue to progress

## Consequences

### Positive

1. **100% deterministic** - Backend always runs assessment after each response
2. **Reliable progression** - Stage advances when threshold met, not when LLM decides
3. **Complete data extraction** - All fields captured every time
4. **Simplified prompt** - LLM focuses on conversation, no tool instructions
5. **Better user experience** - No more stuck sessions

### Negative

1. **Additional latency** - ~200-400ms for Pass 2 assessment
   - *Mitigation*: Runs in onFinish callback, doesn't block streaming
2. **Cost increase** - Additional API call per message
   - *Mitigation*: Haiku is very cheap (~$0.0003/call)
3. **Two models to maintain** - Conversation model + assessment model
   - *Mitigation*: Both use same provider (OpenRouter)

### Neutral

1. **Test changes required** - Removed tool tests, added assessment tests
2. **Prompt simplified** - Removed ~50 lines of tool instructions

## Alternatives Considered

### Option A: Fix Tool Calling (Rejected)

Continued debugging tool call issues with prompt engineering.

**Rejected because**: 10+ attempts failed. The architectural pattern is fundamentally unreliable.

### Option B: Hybrid Tools + Backend (Rejected)

Keep tools but add backend fallback when tools not called.

**Rejected because**: Complexity of maintaining both paths; tools still unpredictable.

### Option C: Deterministic Backend Only (Selected)

Remove tools entirely, let backend handle all assessment.

**Selected because**: Simplest, most reliable, no LLM state management.

## Files Modified

| File | Changes |
|------|---------|
| `lib/onboarding/quality-assessment.ts` | **NEW** - Assessment module |
| `app/api/chat/route.ts` | Removed tools, added Pass 2 |
| `lib/ai/onboarding-prompt.ts` | Removed tool instructions |
| `__tests__/lib/ai/onboarding-prompt.test.ts` | Tests for no-tools |
| `__tests__/api/chat/route.test.ts` | Backend assessment tests |

## Verification

### Automated

```bash
pnpm type-check  # No source errors
pnpm test -- --testPathPatterns="onboarding-prompt"  # 41 passed
pnpm test -- --testPathPatterns="chat/route"         # 28 passed
pnpm build       # Succeeds
```

### Manual

1. Login as Founder (chris00walker@proton.me)
2. Start new onboarding session
3. Answer Stage 1 questions thoroughly
4. Verify `stage_data.brief` populated in Supabase
5. Verify stage advances when coverage >= 0.8
6. Complete through Stage 7, verify CrewAI triggered

## Rollback Plan

If issues arise:

```bash
git revert HEAD  # Restores previous commit
```

Tools and `toolChoice: 'auto'` resume. Known 18% tool call rate issue returns, but system functional.

## References

- [Implementation Plan](/home/chris/.claude/plans/async-mixing-ritchie.md)
- [stages-config.ts](/home/chris/projects/app.startupai.site/frontend/src/lib/onboarding/stages-config.ts)
- [ADR-002: Modal Serverless Migration](./002-modal-serverless-migration.md)

## Changelog

| Date | Change |
|------|--------|
| 2026-01-16 | Initial ADR created and implementation complete |
| 2026-01-16 | **ERRATA IDENTIFIED** (post-implementation audit by Codex + manual review): |
|            | - HIGH: `ConversationMessage` missing `timestamp` field (UI shows "Invalid Date" on resume) |
|            | - MEDIUM: Schema allows < 3 items for Stage 7 arrays but completion requires >= 3 (stall risk) |
|            | - MEDIUM: Legacy sessions without stage tags have messages filtered out (undercounted coverage) |
|            | - LOW: Progress tests use local helper instead of exported function |
|            | See [Implementation Plan Errata](/home/chris/.claude/plans/async-mixing-ritchie.md#errata-2026-01-16-post-implementation-audit) for fixes |
| 2026-01-16 | **ERRATA FIXED** (commit `902ef0c`): All 4 issues resolved. 69 tests pass. |
| 2026-01-16 | **LIVE DOGFOODING FIXES** (discovered during testing with chris00walker@proton.me): |
|            | - P2 HIGH: Progress regressed after auto-advance (used new stage's 0 coverage) → Fixed in `6c6a4db` |
|            | - P3 MEDIUM: "Invalid Date" for legacy messages without timestamps → Fixed in `b1c02b9` |
|            | See [Implementation Plan](/home/chris/.claude/plans/async-mixing-ritchie.md#live-dogfooding-fixes-2026-01-16) for details |
| 2026-01-18 | **OpenRouter Auto-Router Model Selection**: |
|            | - Replaced hardcoded `claude-3.5-haiku` with `openrouter/auto` for intelligent model selection |
|            | - Enabled `require_parameters: true` for structured JSON output with response healing |
|            | - Root cause: Netlify deployment missing ANTHROPIC_API_KEY; OpenRouter fallback used Claude which has unreliable JSON output |
|            | - Solution: OpenRouter auto-router selects optimal model across 60+ providers for each task |
|            | - Files modified: `quality-assessment.ts`, `consultant-quality-assessment.ts` |
|            | See [Plan: prancy-tickling-quokka.md](/home/chris/.claude/plans/prancy-tickling-quokka.md) for context |
