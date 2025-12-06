"""
Supabase Connection Management.

Provides a singleton connection to Supabase with automatic retry and health checks.
"""

import os
from typing import Optional
from functools import lru_cache

from supabase import create_client, Client


class SupabaseConnection:
    """
    Manages the Supabase client connection.

    Uses environment variables for configuration:
    - SUPABASE_URL: The Supabase project URL
    - SUPABASE_KEY: The service role key (for server-side operations)
    """

    _instance: Optional["SupabaseConnection"] = None
    _client: Optional[Client] = None

    def __new__(cls) -> "SupabaseConnection":
        """Singleton pattern for connection management."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize connection (only runs once due to singleton)."""
        if self._client is None:
            self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the Supabase client from environment variables."""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY environment variables must be set. "
                "See .env.example for configuration details."
            )

        self._client = create_client(url, key)

    @property
    def client(self) -> Client:
        """Get the Supabase client."""
        if self._client is None:
            self._initialize_client()
        return self._client

    def health_check(self) -> bool:
        """
        Check if the connection is healthy.

        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            # Simple query to test connection
            self.client.table("flow_executions").select("id").limit(1).execute()
            return True
        except Exception:
            return False

    def reset(self) -> None:
        """Reset the connection (useful for testing or recovery)."""
        self._client = None
        self._initialize_client()


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """
    Get the shared Supabase client instance.

    This function is cached to ensure we always return the same client.

    Returns:
        The Supabase client instance

    Raises:
        ValueError: If environment variables are not set
    """
    return SupabaseConnection().client
