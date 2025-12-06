"""
StartupAI Persistence Layer.

Provides state persistence and event sourcing for the validation flow.
"""

from startupai.persistence.connection import get_supabase_client, SupabaseConnection
from startupai.persistence.state_repository import (
    StateRepository,
    SupabaseStateRepository,
)
from startupai.persistence.events import ValidationEvent, EventType

__all__ = [
    "get_supabase_client",
    "SupabaseConnection",
    "StateRepository",
    "SupabaseStateRepository",
    "ValidationEvent",
    "EventType",
]
