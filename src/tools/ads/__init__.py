"""
Ad Platform Tools Package

Unified interface and adapters for managing ad campaigns across multiple platforms.
Supports Meta, Google, TikTok, LinkedIn, X (Twitter), and Pinterest.

@story US-AC01, US-AC02, US-AC03, US-AC04, US-AC05
"""

from .interface import (
    AdPlatformAdapter,
    AuthType,
    Platform,
    CampaignObjective,
    CampaignStatus,
    CampaignConfig,
    CampaignResult,
    PerformanceMetrics,
    TokenStatus,
    RateLimitStatus,
    TargetingConfig,
    CreativeConfig,
)
from .budget import BudgetPoolManager, BudgetConfig, BudgetPool, AllocationRequest, AllocationResponse

# Lazy imports for platform adapters (SDKs may not be installed)
def __getattr__(name: str):
    """Lazy import adapters to handle missing SDKs gracefully."""
    adapters = {
        "MetaAdsAdapter": ".meta",
        "GoogleAdsAdapter": ".google",
        "TikTokAdsAdapter": ".tiktok",
        "LinkedInAdsAdapter": ".linkedin",
        "XAdsAdapter": ".x",
        "PinterestAdsAdapter": ".pinterest",
    }

    if name in adapters:
        import importlib
        module = importlib.import_module(adapters[name], package=__name__)
        return getattr(module, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Interface
    "AdPlatformAdapter",
    "AuthType",
    "Platform",
    "CampaignObjective",
    "CampaignStatus",
    "CampaignConfig",
    "CampaignResult",
    "PerformanceMetrics",
    "TokenStatus",
    "RateLimitStatus",
    "TargetingConfig",
    "CreativeConfig",
    # Budget
    "BudgetPoolManager",
    "BudgetConfig",
    "BudgetPool",
    "AllocationRequest",
    "AllocationResponse",
    # Adapters (lazy loaded)
    "MetaAdsAdapter",
    "GoogleAdsAdapter",
    "TikTokAdsAdapter",
    "LinkedInAdsAdapter",
    "XAdsAdapter",
    "PinterestAdsAdapter",
]
