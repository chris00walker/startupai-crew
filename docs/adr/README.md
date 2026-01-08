# Architectural Decision Records (ADR)

This folder contains architectural decision records for the StartupAI CrewAI backend.

## What is an ADR?

An Architectural Decision Record captures an important architectural decision along with its context and consequences. They help future developers understand why things are the way they are.

## Format

Each ADR follows this template:
- **Status**: Proposed | Accepted | Deprecated | Superseded
- **Date**: When the decision was made
- **Context**: What is the issue that we're seeing that is motivating this decision?
- **Decision**: What is the change that we're proposing or have agreed to implement?
- **Consequences**: What becomes easier or more difficult as a result of this change?

## Index

| ID | Title | Status | Date |
|----|-------|--------|------|
| [001](./001-flow-to-crew-migration.md) | Flow to 3-Crew Architecture Migration | Superseded | 2025-12-05 |
| [002](./002-modal-serverless-migration.md) | Modal Serverless Architecture Migration | Proposed | 2026-01-08 |

## Creating a New ADR

1. Copy this template:
```markdown
# ADR-XXX: Title

**Status**: Proposed
**Date**: YYYY-MM-DD
**Decision Makers**: Names
**Context**: Brief context

## Summary

One paragraph summary.

## Context

Detailed context and problem statement.

## Decision

What we decided and why.

## Consequences

### Positive
- ...

### Negative
- ...

## Alternatives Considered

What else we considered and why we rejected it.
```

2. Number sequentially (002, 003, etc.)
3. Update this README index
