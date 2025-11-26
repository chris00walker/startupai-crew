"""
StartupAI Webhooks Package.

Provides webhook handlers for Human-in-the-Loop (HITL) workflows,
including creative approvals and viability decisions.
"""

from startupai.webhooks.resume_handler import (
    ResumeHandler,
    ResumePayload,
    CreativeApprovalPayload,
    ViabilityDecisionPayload,
    ApprovalType,
    parse_resume_payload,
)

__all__ = [
    "ResumeHandler",
    "ResumePayload",
    "CreativeApprovalPayload",
    "ViabilityDecisionPayload",
    "ApprovalType",
    "parse_resume_payload",
]
