# ADR-001: Migration from Flow Architecture to 3-Crew Architecture

**Status**: Superseded by [ADR-002](./002-modal-serverless-migration.md)
**Date**: 2025-12-05
**Decision Makers**: Chris Walker, Claude AI Assistant
**Context**: CrewAI managed-platform deployment compatibility (legacy)
**Last Audited**: 2026-01-06 - Claims verified against CrewAI documentation

> **Historical Note**: This ADR documents a legacy 3-crew workaround on the managed CrewAI platform. The canonical architecture is Modal serverless (see ADR-002).

## Summary

Migrate StartupAI from a single `type = "flow"` project to a 3-Crew architecture using `type = "crew"` projects, due to managed-platform compatibility issues with Flow-based deployments.

## Context

### The Problem

The original StartupAI architecture used CrewAI Flows with:
- `type = "flow"` in `pyproject.toml`
- `@start`, `@listen`, and `@router` decorators for orchestration
- 8 crews with 18 agents in a single monolithic flow
- State management via Pydantic models and `@persist()` decorators

**Managed-Platform Deployment Issue** *(empirically observed, not officially documented)*: When deployed to the managed CrewAI platform, the platform:
1. Incorrectly parsed `type = "flow"` projects expecting 14 YAML inputs instead of Flow's `kickoff(inputs)` pattern
2. Returned `source: memory` without executing code (infrastructure-level caching issue)
3. Dashboard traces showed "Waiting for events to load..." indicating the flow never executed

> **Audit Note (2026-01-06)**: These specific behaviors are not documented in official CrewAI docs. However, [PR #2291](https://github.com/crewAIInc/crewAI/pull/2291) confirms Flow projects had deployment issues that required fixes, and [community reports](https://community.crewai.com/t/deployment-issue/2944) show flows working locally but failing on enterprise deployment.

### Debugging Attempts (All Failed)

Code-level workarounds attempted:
- Added `execution_id` with `uuid4()` default to state model
- Added `cache_buster` field injected in `kickoff()`
- Set `cache=False` on all 18 agents across 7 crew files
- Disabled agent caching at instantiation

**Conclusion**: The issue was at the managed-platform infrastructure level, not in our code. Per CrewAI support feedback, the managed platform handles `type = "crew"` projects reliably but has known issues with `type = "flow"`.

> **Audit Note (2026-01-06)**: The claim that `type = "crew"` works reliably while `type = "flow"` doesn't is based on operational experience and support conversations, not official documentation. CrewAI docs state both can be deployed to AOP.

## Decision

Migrate from Flow architecture to a 3-Crew Workflow-Stage Architecture:

```
┌─────────────────────┐     ┌─────────────────────┐     ┌────────────────────┐
│   CREW 1: INTAKE    │────▶│ CREW 2: VALIDATION  │────▶│ CREW 3: DECISION   │
│   4 agents, 1 HITL  │     │   12 agents, 5 HITL │     │   3 agents, 1 HITL │
└─────────────────────┘     └─────────────────────┘     └────────────────────┘
```

### Agent Distribution

| Crew | Agents | Purpose |
|------|--------|---------|
| Crew 1: Intake | S1 (FounderOnboarding), S2 (CustomerResearch), S3 (ValueDesigner), G1 (QA) | Parse input, research, create VPC, QA gate |
| Crew 2: Validation | P1-P3 (Pulse), F1-F3 (Forge), L1-L3 (Ledger), G1-G3 (Guardian) | Desirability, Feasibility, Viability phases |
| Crew 3: Decision | C1 (ProductPM), C2 (HumanApproval), C3 (RoadmapWriter) | Synthesize, decide, document |

### HITL Checkpoint Distribution

| Crew | Checkpoint | Purpose |
|------|------------|---------|
| 1 | `approve_intake_to_validation` | Gate: Intake → Validation |
| 2 | `approve_campaign_launch` | Ad creative approval |
| 2 | `approve_spend_increase` | Budget approval |
| 2 | `approve_desirability_gate` | Gate: Desirability → Feasibility |
| 2 | `approve_feasibility_gate` | Gate: Feasibility → Viability |
| 2 | `approve_viability_gate` | Gate: Viability → Decision |
| 3 | `request_human_decision` | Final pivot/proceed decision |

### Orchestration Pattern

Replace Flow's `@listen`/`@router` decorators with:
1. **Task `context` arrays** for sequencing within a crew
2. **`InvokeCrewAIAutomationTool`** for crew-to-crew chaining via managed-platform API calls

### Repository Structure

The managed platform deploys from git repo root, so each crew requires its own repository:

| Crew | Repository | Status |
|------|------------|--------|
| Crew 1: Intake | `startupai-crew` (this repo) | Ready - at root level |
| Crew 2: Validation | New repo required | Code at `startupai-crews/crew-2-validation/` |
| Crew 3: Decision | New repo required | Code at `startupai-crews/crew-3-decision/` |

## Consequences

### Positive

1. **Managed-Platform Compatibility**: `type = "crew"` projects work reliably on the managed platform
2. **Simpler Debugging**: Each crew is independently testable and deployable
3. **HITL Integration**: `human_input: true` on tasks works correctly on the managed platform
4. **Clearer Boundaries**: Explicit API contracts between crews
5. **Parallel Development**: Crews can be developed/deployed independently

### Negative

1. **Multi-Repo Complexity**: 3 repos instead of 1 monorepo
2. **Coordination Overhead**: Cross-crew changes require multi-repo updates
3. **Lost Flow Features**:
   - No `@persist()` state recovery within crews
   - No `@router` conditional branching
   - State passed via API, not shared memory
4. **Deployment Complexity**: 3 separate deployments to manage

### Neutral

1. **Agent Count**: 19 agents (vs original 18) - added G1 to Crew 1 for QA
2. **Task Count**: 32 tasks total across 3 crews
3. **Token Usage**: Similar - may be slightly higher due to API overhead

## Migration Path

1. **Phase 1** (Complete): Create 3 crew codebases in `startupai-crews/`
2. **Phase 2** (Complete): Move Crew 1 (Intake) to repo root with `type = "crew"`
3. **Phase 3** (Complete): Archive Flow code to `archive/flow-architecture/`
4. **Phase 4** (Pending): Create separate repos for Crews 2 & 3
5. **Phase 5** (Pending): Deploy all crews to the managed platform
6. **Phase 6** (Pending): Configure `InvokeCrewAIAutomationTool` for chaining

## Alternatives Considered

### 1. Fix Flow Deployment Issues
**Rejected**: Issue is at managed-platform infrastructure level, not in our code. Would require CrewAI platform changes.

### 2. Single Large Crew
**Rejected**: 19 agents in one crew would be unwieldy. Task sequencing via `context` would become complex.

### 3. Wait for Managed-Platform Flow Support
**Rejected**: No timeline from CrewAI. Would block all progress.

### 4. Self-Host CrewAI
**Rejected**: Loses managed-platform benefits (managed infrastructure, HITL, monitoring). Requires significant DevOps.

## Related Documents

- `docs/3-crew-deployment.md` - Deployment guide
- `docs/master-architecture/03-validation-spec.md` - Original architecture spec
- `docs/master-architecture/04-status.md` - Current implementation status
- `.claude/plans/cryptic-marinating-goose.md` - Detailed implementation plan

## Audit Results (2026-01-06)

This ADR was audited against official CrewAI documentation (local and online) on 2026-01-06.

### Verified Claims (Documented)

| Claim | Verification |
|-------|--------------|
| `@start`, `@listen`, `@router` decorators | ✅ Confirmed in `flows.md` |
| Pydantic state management with `Flow[State]` | ✅ Confirmed in `flows.md` and state management guide |
| `@persist()` decorator for state recovery | ✅ Confirmed in `flows.md` lines 341-424 |
| `kickoff(inputs)` pattern | ✅ Confirmed in `flows.md` |
| `human_input: true` on tasks | ✅ Confirmed in `tasks.md` line 54 |
| Task `context` arrays for sequencing | ✅ Confirmed in `tasks.md` lines 323-340 |
| `InvokeCrewAIAutomationTool` exists | ✅ Confirmed - [official docs](https://docs.crewai.com/en/tools/integration/crewaiautomationtool) |
| Tool enables crew-to-crew chaining | ✅ Confirmed - uses `POST /kickoff` and `GET /status/{id}` |

### Partially Supported Claims (Community Evidence)

| Claim | Evidence |
|-------|----------|
| Flow projects had deployment issues | [PR #2291](https://github.com/crewAIInc/crewAI/pull/2291) fixed "crewai run command issue for Flow Projects and Cloud Deployment" |
| Flow deployments can fail on enterprise | [Community report](https://community.crewai.com/t/deployment-issue/2944): flow works locally but fails on enterprise |
| Missing scripts in flow scaffolding | [Issue #2005](https://github.com/crewAIInc/crewAI/issues/2005): "Missing run_crew script in scaffolded pyproject.toml" |
| Wrong command caused flow failures | [Community](https://community.crewai.com/t/unable-to-run-crew-using-flow/1186): had to use `crewai flow kickoff` not `crewai run` |

### Unverifiable Claims (Empirical Observations)

| Claim | Status |
|-------|--------|
| Managed platform returns `source: memory` without executing | ❌ Not documented - based on our operational observation |
| `type = "crew"` works reliably, `type = "flow"` doesn't | ❌ Not documented - docs say both can be deployed |
| Managed-platform caching skips Flow execution | ❌ Not documented - [caching issues](https://community.crewai.com/t/crewai-agents-use-old-or-incorrect-input-despite-memory-reset-and-cache-clear/5484) exist but are about agent memory, not platform execution |
| Managed platform deploys from repo root (requires separate repos) | ❌ Not documented - no repo structure requirements in docs |

### Audit Conclusion

The migration decision was **operationally justified** based on:
1. Real deployment failures we experienced
2. Documented bugs in Flow project scaffolding ([PR #2291](https://github.com/crewAIInc/crewAI/pull/2291), [Issue #2005](https://github.com/crewAIInc/crewAI/issues/2005))
3. Community reports of similar Flow deployment issues

However, the ADR's **core technical claims** about managed-platform behavior (`source: memory`, infrastructure caching, `type = "flow"` incompatibility) are based on **operational experience**, not official documentation. Future readers should understand this distinction.

### Sources

- [CrewAI Run Automation Tool](https://docs.crewai.com/en/tools/integration/crewaiautomationtool)
- [Flow Run Command Fix PR #2291](https://github.com/crewAIInc/crewAI/pull/2291)
- [Community: Unable to run Crew using Flow](https://community.crewai.com/t/unable-to-run-crew-using-flow/1186)
- [Community: Deployment Issue](https://community.crewai.com/t/deployment-issue/2944)
- [Community: Agents Using Cached Inputs](https://community.crewai.com/t/crewai-agents-use-old-or-incorrect-input-despite-memory-reset-and-cache-clear/5484)
- [CrewAI CLI Documentation](https://docs.crewai.com/en/concepts/cli)
- Local docs: `docs/crewai-documentation/core-concepts/flows.md`
- Local docs: `docs/crewai-documentation/core-concepts/tasks.md`

## Changelog

| Date | Change |
|------|--------|
| 2025-12-05 | Initial decision and implementation |
| 2026-01-06 | Audited against CrewAI documentation; added verification notes |
| 2026-01-08 | Superseded by [ADR-002](./002-modal-serverless-migration.md) - Modal serverless architecture |
