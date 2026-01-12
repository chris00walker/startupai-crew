# LLM Coordination Protocol (Canonical)

This document is the single source of truth for multi-agent coordination across
StartupAI repos. All `CLAUDE.md` files should link here instead of duplicating
protocol content.

## Ownership
- **Coordination decisions**: Codex (planner for cross-repo work)
- **Master-architecture docs**: Codex

## Workflow

### Before Starting Work
1. Check `docs/master-architecture/ai-work-queue.md` for assigned tasks
2. Review `docs/master-architecture/llm-handoff.md` for current context

### While Working
- Use branch isolation (never share branches between agents)
- Record the active branch name in the handoff

### When Stopping
Update `docs/master-architecture/llm-handoff.md` with:
- Goal and current status
- Files touched and commits
- Tests run (or "not run")
- Blockers/questions
- Context for next agent (key decisions, rationale, watch-outs)
- Next steps

## Repo Assignment
| Repo | Primary Agent | Notes |
|------|---------------|-------|
| `startupai-crew` | Codex | Backend + Modal + CrewAI |
| `app.startupai.site` | Claude Code | Product app (Next.js) |
| `startupai.site` | Assigned per task | Marketing site |
