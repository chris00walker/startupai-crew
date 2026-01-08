"""
Configuration for Modal serverless deployment.

Environment variables are loaded from Modal secrets.
"""

import os
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # OpenAI
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o", alias="OPENAI_MODEL")

    # Tavily (web search)
    tavily_api_key: str = Field(..., alias="TAVILY_API_KEY")

    # Supabase
    supabase_url: str = Field(..., alias="SUPABASE_URL")
    supabase_key: str = Field(..., alias="SUPABASE_KEY")

    # Netlify (for LP deployment in Phase 2)
    netlify_access_token: str = Field(default="", alias="NETLIFY_ACCESS_TOKEN")

    # Webhook authentication
    webhook_bearer_token: str = Field(
        default="startupai-modal-secret-2026",
        alias="WEBHOOK_BEARER_TOKEN"
    )

    # Product app URL for callbacks
    product_app_url: str = Field(
        default="https://app.startupai.site",
        alias="PRODUCT_APP_URL"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Phase configuration
PHASE_CONFIG = {
    0: {
        "name": "Onboarding",
        "flow": "OnboardingFlow",
        "crews": ["OnboardingCrew"],
        "agents": 4,
        "hitl_checkpoints": ["approve_founders_brief"],
        "timeout_seconds": 600,  # 10 minutes
    },
    1: {
        "name": "VPC Discovery",
        "flow": "VPCDiscoveryFlow",
        "crews": [
            "DiscoveryCrew",
            "CustomerProfileCrew",
            "ValueDesignCrew",
            "WTPCrew",
            "FitAssessmentCrew",
        ],
        "agents": 18,
        "hitl_checkpoints": [
            "approve_experiment_plan",
            "approve_pricing_test",
            "approve_vpc_completion",
        ],
        "timeout_seconds": 1800,  # 30 minutes
    },
    2: {
        "name": "Desirability",
        "flow": "DesirabilityFlow",
        "crews": ["BuildCrew", "GrowthCrew", "GovernanceCrew"],
        "agents": 9,
        "hitl_checkpoints": [
            "approve_campaign_launch",
            "approve_spend_increase",
            "approve_desirability_gate",
        ],
        "timeout_seconds": 1800,  # 30 minutes
    },
    3: {
        "name": "Feasibility",
        "flow": "FeasibilityFlow",
        "crews": ["BuildCrew", "GovernanceCrew"],
        "agents": 5,
        "hitl_checkpoints": ["approve_feasibility_gate"],
        "timeout_seconds": 1200,  # 20 minutes
    },
    4: {
        "name": "Viability",
        "flow": "ViabilityFlow",
        "crews": ["FinanceCrew", "SynthesisCrew", "GovernanceCrew"],
        "agents": 9,
        "hitl_checkpoints": [
            "approve_viability_gate",
            "approve_pivot",
            "approve_proceed",
            "request_human_decision",
        ],
        "timeout_seconds": 1800,  # 30 minutes
    },
}

# Total counts (canonical architecture)
TOTAL_PHASES = 5
TOTAL_FLOWS = 5
TOTAL_CREWS = 14
TOTAL_AGENTS = 45
TOTAL_HITL_CHECKPOINTS = 10
