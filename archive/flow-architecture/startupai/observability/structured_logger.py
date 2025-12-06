"""
Structured Logger for StartupAI Validation Flow.

Provides consistent, structured logging with support for:
- JSON output for aggregation
- Event-based logging
- Context propagation
- Performance metrics
"""

import json
import logging
import sys
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
from functools import lru_cache


class LogLevel(str, Enum):
    """Log severity levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class EventType(str, Enum):
    """Types of structured events."""
    # Flow lifecycle
    FLOW_START = "flow_start"
    FLOW_COMPLETE = "flow_complete"
    FLOW_ERROR = "flow_error"

    # Phase management
    PHASE_TRANSITION = "phase_transition"
    PHASE_START = "phase_start"
    PHASE_COMPLETE = "phase_complete"

    # Router decisions
    ROUTER_DECISION = "router_decision"
    ROUTER_ERROR = "router_error"

    # Crew execution
    CREW_START = "crew_start"
    CREW_COMPLETE = "crew_complete"
    CREW_ERROR = "crew_error"

    # Tool calls
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    TOOL_ERROR = "tool_error"

    # HITL events
    HITL_PAUSE = "hitl_pause"
    HITL_RESUME = "hitl_resume"
    HITL_DECISION = "hitl_decision"

    # Evidence
    EVIDENCE_COLLECTED = "evidence_collected"
    SIGNAL_UPDATED = "signal_updated"

    # Performance
    PERFORMANCE_METRIC = "performance_metric"


class StructuredLogger:
    """
    Structured logger with context propagation.

    Usage:
        logger = StructuredLogger(project_id="val_123")
        logger.log_event(EventType.FLOW_START, {"phase": "ideation"})
        logger.log_router_decision("desirability_gate", "proceed_to_feasibility", state_dict)
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        name: str = "startupai",
        json_output: bool = True,
        log_level: LogLevel = LogLevel.INFO,
    ):
        """
        Initialize the structured logger.

        Args:
            project_id: Optional project ID for context
            name: Logger name
            json_output: If True, output JSON formatted logs
            log_level: Minimum log level
        """
        self.project_id = project_id
        self.name = name
        self.json_output = json_output
        self._context: Dict[str, Any] = {}

        # Set up Python logger
        self._logger = logging.getLogger(name)
        self._logger.setLevel(getattr(logging, log_level.value.upper()))

        # Remove existing handlers
        self._logger.handlers = []

        # Add handler
        handler = logging.StreamHandler(sys.stdout)
        if json_output:
            handler.setFormatter(JsonFormatter())
        else:
            handler.setFormatter(
                logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
            )
        self._logger.addHandler(handler)

    def set_context(self, **kwargs) -> None:
        """Set context that will be included in all logs."""
        self._context.update(kwargs)

    def clear_context(self) -> None:
        """Clear the context."""
        self._context = {}

    def log_event(
        self,
        event_type: EventType,
        data: Optional[Dict[str, Any]] = None,
        level: LogLevel = LogLevel.INFO,
    ) -> None:
        """
        Log a structured event.

        Args:
            event_type: The type of event
            data: Additional data to include
            level: Log level
        """
        record = {
            "event_type": event_type.value,
            "timestamp": datetime.now().isoformat(),
            "project_id": self.project_id,
            **self._context,
            **(data or {}),
        }

        log_method = getattr(self._logger, level.value)
        log_method(json.dumps(record) if self.json_output else f"{event_type.value}: {data}")

    def log_flow_start(self, entrepreneur_input: str, phase: str) -> None:
        """Log flow start event."""
        self.log_event(
            EventType.FLOW_START,
            {
                "phase": phase,
                "input_length": len(entrepreneur_input),
            },
        )

    def log_phase_transition(
        self,
        from_phase: str,
        to_phase: str,
        triggered_by: str,
        reason: Optional[str] = None,
    ) -> None:
        """Log phase transition event."""
        self.log_event(
            EventType.PHASE_TRANSITION,
            {
                "from_phase": from_phase,
                "to_phase": to_phase,
                "triggered_by": triggered_by,
                "reason": reason,
            },
        )

    def log_router_decision(
        self,
        router: str,
        decision: str,
        state: Dict[str, Any],
        reason: Optional[str] = None,
    ) -> None:
        """Log router decision event."""
        # Extract key signals from state
        signals = {
            "desirability_signal": state.get("desirability_signal"),
            "feasibility_signal": state.get("feasibility_signal"),
            "viability_signal": state.get("viability_signal"),
            "iteration": state.get("iteration"),
        }

        self.log_event(
            EventType.ROUTER_DECISION,
            {
                "router": router,
                "decision": decision,
                "signals": signals,
                "reason": reason,
            },
        )

    def log_crew_start(self, crew_name: str, task: Optional[str] = None) -> None:
        """Log crew execution start."""
        self.log_event(
            EventType.CREW_START,
            {
                "crew": crew_name,
                "task": task,
            },
        )

    def log_crew_complete(
        self,
        crew_name: str,
        duration_ms: float,
        success: bool = True,
        result_summary: Optional[str] = None,
    ) -> None:
        """Log crew execution completion."""
        self.log_event(
            EventType.CREW_COMPLETE if success else EventType.CREW_ERROR,
            {
                "crew": crew_name,
                "duration_ms": duration_ms,
                "success": success,
                "result_summary": result_summary,
            },
            level=LogLevel.INFO if success else LogLevel.ERROR,
        )

    def log_tool_call(
        self,
        tool_name: str,
        inputs: Dict[str, Any],
        agent: Optional[str] = None,
    ) -> None:
        """Log tool invocation."""
        self.log_event(
            EventType.TOOL_CALL,
            {
                "tool": tool_name,
                "agent": agent,
                "input_keys": list(inputs.keys()),
            },
            level=LogLevel.DEBUG,
        )

    def log_tool_result(
        self,
        tool_name: str,
        success: bool,
        duration_ms: float,
        result_summary: Optional[str] = None,
    ) -> None:
        """Log tool result."""
        self.log_event(
            EventType.TOOL_RESULT if success else EventType.TOOL_ERROR,
            {
                "tool": tool_name,
                "success": success,
                "duration_ms": duration_ms,
                "result_summary": result_summary,
            },
            level=LogLevel.INFO if success else LogLevel.WARNING,
        )

    def log_hitl_pause(
        self,
        reason: str,
        pending_decision: str,
        options: Optional[list] = None,
    ) -> None:
        """Log HITL pause event."""
        self.log_event(
            EventType.HITL_PAUSE,
            {
                "reason": reason,
                "pending_decision": pending_decision,
                "options": options,
            },
            level=LogLevel.WARNING,
        )

    def log_error(
        self,
        error_code: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        recoverable: bool = False,
    ) -> None:
        """Log error event."""
        self.log_event(
            EventType.FLOW_ERROR,
            {
                "error_code": error_code,
                "message": message,
                "recoverable": recoverable,
                "context": context,
            },
            level=LogLevel.ERROR,
        )

    def log_performance(
        self,
        metric_name: str,
        value: float,
        unit: str = "ms",
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Log performance metric."""
        self.log_event(
            EventType.PERFORMANCE_METRIC,
            {
                "metric": metric_name,
                "value": value,
                "unit": unit,
                "tags": tags,
            },
            level=LogLevel.DEBUG,
        )


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logs."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        try:
            # Try to parse the message as JSON
            data = json.loads(record.getMessage())
            data["level"] = record.levelname.lower()
            return json.dumps(data)
        except json.JSONDecodeError:
            # Fallback for non-JSON messages
            return json.dumps({
                "level": record.levelname.lower(),
                "message": record.getMessage(),
                "timestamp": datetime.now().isoformat(),
            })


@lru_cache(maxsize=10)
def get_logger(
    project_id: Optional[str] = None,
    name: str = "startupai",
    json_output: bool = True,
) -> StructuredLogger:
    """
    Get a cached logger instance.

    Args:
        project_id: Optional project ID
        name: Logger name
        json_output: Whether to output JSON

    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(
        project_id=project_id,
        name=name,
        json_output=json_output,
    )
