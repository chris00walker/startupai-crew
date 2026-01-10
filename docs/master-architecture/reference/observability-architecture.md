---
purpose: "Architectural specification for system observability"
status: "active"
created: "2026-01-10"
last_reviewed: "2026-01-10"
vpd_compliance: true
---

# Observability Architecture

This document specifies the observability architecture for the StartupAI AI Founders Engine. Observability is a **first-class architectural concern** - the 6 AI Founders operate autonomously, and without proper observability we cannot diagnose failures, verify evidence quality, or improve agent performance.

> **Implementation Note**: This specification should be implemented before deploying new tools or crews to production.

---

## Why Observability Matters

The VPD methodology requires **evidence-based validation**. Agents collect evidence, generate artifacts, and make recommendations. Without observability:

| Problem | Impact |
|---------|--------|
| Agent fails silently | Validation stuck, user frustrated |
| Tool returns placeholder | Evidence quality compromised |
| Crew times out | No insight into what went wrong |
| LLM hallucinates | Can't verify output quality |

**Goal**: Modal developer can diagnose any failing agent in < 5 minutes.

---

## Event Taxonomy

All observable events follow a consistent taxonomy:

### Lifecycle Events

| Event | When | Data |
|-------|------|------|
| `run_start` | Validation run begins | run_id, project_id, user_id |
| `run_complete` | Validation run ends | run_id, status, duration_ms |
| `phase_start` | Phase begins | run_id, phase, timestamp |
| `phase_complete` | Phase ends | run_id, phase, signal, duration_ms |
| `crew_start` | Crew kickoff | run_id, phase, crew, timestamp |
| `crew_complete` | Crew finishes | run_id, phase, crew, output_summary |
| `task_start` | Task begins | run_id, crew, task, agent |
| `task_complete` | Task ends | run_id, crew, task, output |

### Agent Events

| Event | When | Data |
|-------|------|------|
| `agent_step` | Agent reasoning step | run_id, agent, thought, action |
| `agent_tool_call` | Agent invokes tool | run_id, agent, tool, input |
| `agent_tool_result` | Tool returns | run_id, agent, tool, output, duration_ms |
| `agent_error` | Agent encounters error | run_id, agent, error_type, message, stack_trace |

### HITL Events

| Event | When | Data |
|-------|------|------|
| `hitl_checkpoint` | HITL checkpoint reached | run_id, checkpoint, context |
| `hitl_approval` | Human approves | run_id, checkpoint, decision, user_id |
| `hitl_rejection` | Human rejects | run_id, checkpoint, decision, reason |
| `hitl_timeout` | Approval expires | run_id, checkpoint, expired_at |

---

## Database Schema

### Tables

```sql
-- Agent reasoning steps (captures verbose output)
CREATE TABLE agent_steps (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id UUID NOT NULL REFERENCES validation_runs(id) ON DELETE CASCADE,
  phase INTEGER NOT NULL,
  crew TEXT NOT NULL,
  agent TEXT NOT NULL,
  task TEXT,
  step_number INTEGER NOT NULL,
  thought TEXT,                 -- Agent's reasoning
  action TEXT,                  -- Tool call or delegation
  action_input JSONB,           -- Tool parameters
  observation TEXT,             -- Tool result
  duration_ms INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tool execution log
CREATE TABLE tool_executions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id UUID NOT NULL REFERENCES validation_runs(id) ON DELETE CASCADE,
  agent_step_id UUID REFERENCES agent_steps(id),
  tool_name TEXT NOT NULL,
  tool_input JSONB NOT NULL,
  tool_output JSONB,
  output_type TEXT,             -- success | error | placeholder | timeout
  error TEXT,
  stack_trace TEXT,
  duration_ms INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Error logs with full context
CREATE TABLE error_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id UUID REFERENCES validation_runs(id) ON DELETE CASCADE,
  phase INTEGER,
  crew TEXT,
  agent TEXT,
  task TEXT,
  error_type TEXT NOT NULL,     -- crew_error | tool_error | llm_error | timeout | validation
  error_message TEXT NOT NULL,
  stack_trace TEXT,
  context JSONB,                -- Additional debugging context
  recovered BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for efficient queries
CREATE INDEX idx_agent_steps_run ON agent_steps(run_id);
CREATE INDEX idx_agent_steps_agent ON agent_steps(agent);
CREATE INDEX idx_tool_executions_run ON tool_executions(run_id);
CREATE INDEX idx_tool_executions_tool ON tool_executions(tool_name);
CREATE INDEX idx_error_logs_run ON error_logs(run_id);
CREATE INDEX idx_error_logs_type ON error_logs(error_type);

-- Enable Realtime for instant debugging
ALTER PUBLICATION supabase_realtime ADD TABLE agent_steps;
ALTER PUBLICATION supabase_realtime ADD TABLE tool_executions;
ALTER PUBLICATION supabase_realtime ADD TABLE error_logs;
```

### Row-Level Security

```sql
-- RLS policies for multi-tenant isolation
ALTER TABLE agent_steps ENABLE ROW LEVEL SECURITY;
ALTER TABLE tool_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE error_logs ENABLE ROW LEVEL SECURITY;

-- Users can view observability data for their own runs
CREATE POLICY "Users can view own agent_steps" ON agent_steps
  FOR SELECT USING (
    run_id IN (
      SELECT id FROM validation_runs
      WHERE project_id IN (
        SELECT id FROM projects WHERE user_id = auth.uid()
      )
    )
  );

-- Service role can insert (used by Modal)
CREATE POLICY "Service can insert agent_steps" ON agent_steps
  FOR INSERT WITH CHECK (true);

-- Similar policies for tool_executions and error_logs
```

---

## CrewAI Callback Specification

### ObservabilityCallbackHandler

```python
"""
Observability callback handler for CrewAI crews.

Usage:
    from shared.observability import ObservabilityCallbackHandler

    crew = Crew(
        agents=[...],
        tasks=[...],
        callbacks=[ObservabilityCallbackHandler(run_id, supabase_client)]
    )
"""

from typing import Any, Optional
from crewai.callbacks import BaseCallback
from supabase import Client
import traceback
import time
import json

class ObservabilityCallbackHandler(BaseCallback):
    """Captures agent steps, tool executions, and errors for debugging."""

    def __init__(self, run_id: str, supabase: Client, phase: int, crew: str):
        self.run_id = run_id
        self.supabase = supabase
        self.phase = phase
        self.crew = crew
        self.step_number = 0
        self.current_agent = None
        self.current_task = None
        self.current_step_id = None

    def on_agent_start(self, agent: str, task: str):
        """Called when an agent begins a task."""
        self.current_agent = agent
        self.current_task = task
        self.step_number = 0

    def on_step_start(self, thought: str):
        """Called at the start of an agent reasoning step."""
        self.step_number += 1
        start_time = time.time()

        result = self.supabase.table("agent_steps").insert({
            "run_id": self.run_id,
            "phase": self.phase,
            "crew": self.crew,
            "agent": self.current_agent,
            "task": self.current_task,
            "step_number": self.step_number,
            "thought": thought,
        }).execute()

        self.current_step_id = result.data[0]["id"] if result.data else None
        self._step_start_time = start_time

    def on_step_end(self, action: str, action_input: dict, observation: str):
        """Called at the end of an agent reasoning step."""
        if self.current_step_id:
            duration_ms = int((time.time() - self._step_start_time) * 1000)

            self.supabase.table("agent_steps").update({
                "action": action,
                "action_input": action_input,
                "observation": observation[:10000],  # Truncate large outputs
                "duration_ms": duration_ms,
            }).eq("id", self.current_step_id).execute()

    def on_tool_start(self, tool_name: str, tool_input: dict):
        """Called when a tool is invoked."""
        self._tool_start_time = time.time()
        self._tool_name = tool_name
        self._tool_input = tool_input

    def on_tool_end(self, tool_output: Any, output_type: str = "success"):
        """Called when a tool returns."""
        duration_ms = int((time.time() - self._tool_start_time) * 1000)

        self.supabase.table("tool_executions").insert({
            "run_id": self.run_id,
            "agent_step_id": self.current_step_id,
            "tool_name": self._tool_name,
            "tool_input": self._tool_input,
            "tool_output": self._serialize_output(tool_output),
            "output_type": output_type,
            "duration_ms": duration_ms,
        }).execute()

    def on_tool_error(self, error: Exception):
        """Called when a tool fails."""
        duration_ms = int((time.time() - self._tool_start_time) * 1000)

        self.supabase.table("tool_executions").insert({
            "run_id": self.run_id,
            "agent_step_id": self.current_step_id,
            "tool_name": self._tool_name,
            "tool_input": self._tool_input,
            "output_type": "error",
            "error": str(error),
            "stack_trace": traceback.format_exc(),
            "duration_ms": duration_ms,
        }).execute()

        self._log_error("tool_error", str(error), traceback.format_exc())

    def on_task_complete(self, task: str, output: Any):
        """Called when a task completes."""
        # Task completion is logged via validation_progress table
        pass

    def on_crew_error(self, error: Exception):
        """Called when a crew encounters an error."""
        self._log_error("crew_error", str(error), traceback.format_exc())

    def _log_error(self, error_type: str, message: str, stack_trace: str):
        """Log error to error_logs table."""
        self.supabase.table("error_logs").insert({
            "run_id": self.run_id,
            "phase": self.phase,
            "crew": self.crew,
            "agent": self.current_agent,
            "task": self.current_task,
            "error_type": error_type,
            "error_message": message,
            "stack_trace": stack_trace,
            "context": {
                "step_number": self.step_number,
                "step_id": self.current_step_id,
            },
        }).execute()

    def _serialize_output(self, output: Any) -> dict:
        """Serialize tool output for storage."""
        if hasattr(output, "model_dump"):
            return output.model_dump()
        if isinstance(output, dict):
            return output
        return {"raw": str(output)[:10000]}
```

### Wiring to Crews

Every crew must include the observability callback:

```python
from shared.observability import ObservabilityCallbackHandler

def run_build_crew(run_id: str, state: dict, supabase: Client) -> str:
    """Run BuildCrew with observability."""
    callback = ObservabilityCallbackHandler(
        run_id=run_id,
        supabase=supabase,
        phase=2,
        crew="BuildCrew"
    )

    crew = BuildCrew().crew()
    crew.callbacks = [callback]

    result = crew.kickoff(inputs=state)
    return result.raw
```

---

## Tool Observability Pattern

All tools should use the observability wrapper for consistent logging:

```python
from functools import wraps
from typing import Callable
import time
import traceback

def observable_tool(func: Callable) -> Callable:
    """
    Decorator that adds observability to tool execution.

    Usage:
        class MyTool(BaseTool):
            @observable_tool
            def _run(self, **kwargs) -> str:
                # Tool implementation
                ...
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        tool_name = getattr(self, "name", func.__name__)
        start_time = time.time()

        try:
            result = func(self, *args, **kwargs)
            duration_ms = int((time.time() - start_time) * 1000)

            # Log success (if callback available)
            if hasattr(self, "_observability_callback"):
                self._observability_callback.on_tool_end(result, "success")

            return result

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)

            # Log error (if callback available)
            if hasattr(self, "_observability_callback"):
                self._observability_callback.on_tool_error(e)

            raise

    return wrapper
```

### Placeholder Detection

Tools that return placeholder content should be detected:

```python
PLACEHOLDER_PATTERNS = [
    "placeholder",
    "not implemented",
    "stub",
    "mock data",
    "sample",
    "example output",
    "TODO",
]

def detect_placeholder(output: str) -> bool:
    """Detect if tool output is placeholder content."""
    output_lower = output.lower()
    return any(pattern in output_lower for pattern in PLACEHOLDER_PATTERNS)

def validate_tool_output(tool_name: str, output: Any) -> tuple[bool, str]:
    """
    Validate that tool output is real, not placeholder.

    Returns:
        (is_valid, message)
    """
    if output is None:
        return False, "Tool returned None"

    output_str = str(output)

    if detect_placeholder(output_str):
        return False, f"Tool {tool_name} returned placeholder content"

    if len(output_str) < 10:
        return False, f"Tool {tool_name} returned suspiciously short output"

    return True, "Valid"
```

---

## Debugging Workflow

### Scenario: Agent Fails Silently

1. **Check validation_runs table**
   ```sql
   SELECT status, error_message, current_phase
   FROM validation_runs
   WHERE id = 'run-uuid';
   ```

2. **Check error_logs for details**
   ```sql
   SELECT error_type, error_message, stack_trace, crew, agent
   FROM error_logs
   WHERE run_id = 'run-uuid'
   ORDER BY created_at DESC;
   ```

3. **Trace agent reasoning**
   ```sql
   SELECT step_number, thought, action, observation
   FROM agent_steps
   WHERE run_id = 'run-uuid' AND agent = 'F2'
   ORDER BY step_number;
   ```

### Scenario: Tool Returns Bad Data

1. **Check tool executions**
   ```sql
   SELECT tool_name, tool_input, tool_output, output_type, duration_ms
   FROM tool_executions
   WHERE run_id = 'run-uuid'
   ORDER BY created_at DESC;
   ```

2. **Filter by output type**
   ```sql
   SELECT * FROM tool_executions
   WHERE run_id = 'run-uuid' AND output_type IN ('error', 'placeholder');
   ```

### Scenario: Crew Takes Too Long

1. **Check step durations**
   ```sql
   SELECT agent, AVG(duration_ms) as avg_ms, MAX(duration_ms) as max_ms
   FROM agent_steps
   WHERE run_id = 'run-uuid'
   GROUP BY agent
   ORDER BY avg_ms DESC;
   ```

2. **Check tool durations**
   ```sql
   SELECT tool_name, AVG(duration_ms), COUNT(*)
   FROM tool_executions
   WHERE run_id = 'run-uuid'
   GROUP BY tool_name
   ORDER BY AVG(duration_ms) DESC;
   ```

---

## Log Retention Policy

| Table | Retention | Rationale |
|-------|-----------|-----------|
| `agent_steps` | 30 days | Debugging recent runs |
| `tool_executions` | 30 days | Debugging recent runs |
| `error_logs` | 90 days | Post-mortem analysis |
| `validation_progress` | Indefinite | User-visible history |

### Cleanup Job

```sql
-- Run weekly via scheduled function
DELETE FROM agent_steps
WHERE created_at < NOW() - INTERVAL '30 days';

DELETE FROM tool_executions
WHERE created_at < NOW() - INTERVAL '30 days';

DELETE FROM error_logs
WHERE created_at < NOW() - INTERVAL '90 days';
```

---

## Integration with Supabase Realtime

Observability tables are enabled for Realtime, allowing live debugging:

```typescript
// Subscribe to agent steps for a run
const subscription = supabase
  .channel('agent-steps')
  .on(
    'postgres_changes',
    {
      event: 'INSERT',
      schema: 'public',
      table: 'agent_steps',
      filter: `run_id=eq.${runId}`,
    },
    (payload) => {
      console.log('Agent step:', payload.new);
    }
  )
  .subscribe();
```

---

## Metrics & Alerting

### Key Metrics

| Metric | Source | Alert Threshold |
|--------|--------|-----------------|
| `tool_error_rate` | tool_executions | > 5% |
| `crew_error_rate` | error_logs | > 2% |
| `avg_phase_duration` | validation_progress | > 30 min |
| `placeholder_rate` | tool_executions | > 0% |

### Alerting (Future)

Integration with Modal's Slack alerting or external services:
- Alert on high error rates
- Alert on placeholder detection
- Alert on abnormal durations

---

## Related Documents

- [tool-specifications.md](./tool-specifications.md) - Tool definitions and schemas
- [agentic-tool-framework.md](./agentic-tool-framework.md) - Tool lifecycle and testing
- [modal-configuration.md](./modal-configuration.md) - Modal logging configuration
- [database-schemas.md](./database-schemas.md) - Complete database schema reference

---

**Last Updated**: 2026-01-10
