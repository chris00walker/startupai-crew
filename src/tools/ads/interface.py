"""
Unified Ad Platform Interface

Abstract base class and shared models for all ad platform adapters.
Supports both OAuth 2.0 (Meta, Google, TikTok, LinkedIn, Pinterest) and
OAuth 1.0A (X/Twitter) authentication protocols.

@story US-AC01, US-AC02, US-AC03
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel, Field


class AuthType(Enum):
    """Authentication protocol type.

    Most platforms use OAuth 2.0, but X/Twitter requires OAuth 1.0A
    with HMAC-SHA1 request signing.
    """
    OAUTH2 = "oauth2"      # Meta, Google, TikTok, LinkedIn, Pinterest
    OAUTH1 = "oauth1"      # X/Twitter only


class Platform(Enum):
    """Supported ad platforms."""
    META = "meta"
    GOOGLE = "google"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"
    X = "x"
    PINTEREST = "pinterest"


class CampaignObjective(Enum):
    """Platform-agnostic campaign objectives.

    These map to platform-specific objectives in each adapter.
    """
    AWARENESS = "awareness"
    TRAFFIC = "traffic"
    CONVERSIONS = "conversions"
    APP_INSTALLS = "app_installs"
    VIDEO_VIEWS = "video_views"
    LEAD_GENERATION = "lead_generation"
    ENGAGEMENT = "engagement"
    REACH = "reach"


class CampaignStatus(Enum):
    """Campaign lifecycle status."""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    REJECTED = "rejected"
    ERROR = "error"


class TargetingConfig(BaseModel):
    """Audience targeting configuration."""
    locations: list[str] = Field(default_factory=list, description="Country/region codes")
    age_min: Optional[int] = Field(None, ge=13, le=65)
    age_max: Optional[int] = Field(None, ge=13, le=65)
    genders: list[str] = Field(default_factory=list, description="male, female, all")
    interests: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    custom_audiences: list[str] = Field(default_factory=list)
    excluded_audiences: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    platforms: list[str] = Field(default_factory=list, description="Device/platform targeting")

    model_config = {"extra": "allow"}  # Allow platform-specific fields


class CreativeConfig(BaseModel):
    """Ad creative configuration."""
    headline: str = Field(..., max_length=255)
    body: Optional[str] = Field(None, max_length=2000)
    call_to_action: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    landing_url: str
    display_url: Optional[str] = None

    model_config = {"extra": "allow"}  # Allow platform-specific fields


class CampaignConfig(BaseModel):
    """Campaign creation configuration."""
    name: str = Field(..., min_length=1, max_length=255)
    objective: CampaignObjective
    budget_cents: int = Field(..., gt=0, description="Total budget in cents")
    daily_budget_cents: Optional[int] = Field(None, gt=0, description="Daily budget cap in cents")
    start_date: str = Field(..., description="ISO 8601 format (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="ISO 8601 format (YYYY-MM-DD)")
    targeting: TargetingConfig
    creative: CreativeConfig

    # Optional metadata
    hypothesis_id: Optional[str] = Field(None, description="Link to StartupAI hypothesis")
    project_id: Optional[str] = Field(None, description="Link to StartupAI project")

    model_config = {"extra": "allow"}


class CampaignResult(BaseModel):
    """Result from campaign creation."""
    platform: Platform
    platform_campaign_id: str
    platform_ad_set_id: Optional[str] = None
    platform_ad_id: Optional[str] = None
    status: CampaignStatus
    created_at: datetime
    review_status: Optional[str] = None
    error_message: Optional[str] = None


class PerformanceMetrics(BaseModel):
    """Campaign performance data."""
    campaign_id: str
    platform: Platform
    date_start: str
    date_end: str

    # Core metrics
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    spend_cents: int = 0

    # Calculated metrics
    ctr: float = Field(0.0, description="Click-through rate (clicks/impressions)")
    cpc_cents: float = Field(0.0, description="Cost per click in cents")
    cpa_cents: float = Field(0.0, description="Cost per acquisition in cents")
    cpm_cents: float = Field(0.0, description="Cost per mille (1000 impressions) in cents")

    # Platform-specific metrics
    reach: Optional[int] = None
    frequency: Optional[float] = None
    video_views: Optional[int] = None
    video_completions: Optional[int] = None

    # Raw platform data
    raw_data: Optional[dict[str, Any]] = None

    def calculate_derived_metrics(self) -> None:
        """Calculate CTR, CPC, CPA, CPM from raw metrics."""
        if self.impressions > 0:
            self.ctr = self.clicks / self.impressions
            self.cpm_cents = (self.spend_cents / self.impressions) * 1000
        if self.clicks > 0:
            self.cpc_cents = self.spend_cents / self.clicks
        if self.conversions > 0:
            self.cpa_cents = self.spend_cents / self.conversions


class TokenStatus(BaseModel):
    """OAuth token health status."""
    platform: Platform
    valid: bool
    expires_at: Optional[datetime] = None
    days_until_expiry: Optional[int] = None
    needs_refresh: bool = False
    scopes: list[str] = Field(default_factory=list)
    error_message: Optional[str] = None

    @classmethod
    def from_expiry(cls, platform: Platform, expires_at: Optional[datetime], valid: bool = True) -> "TokenStatus":
        """Create TokenStatus from expiry datetime."""
        days_until = None
        needs_refresh = False

        if expires_at:
            days_until = (expires_at - datetime.now()).days
            needs_refresh = days_until < 7  # Refresh if <7 days remaining

        return cls(
            platform=platform,
            valid=valid,
            expires_at=expires_at,
            days_until_expiry=days_until,
            needs_refresh=needs_refresh,
        )


class RateLimitStatus(BaseModel):
    """Rate limit status for an API."""
    platform: Platform
    endpoint: Optional[str] = None
    limit: int
    remaining: int
    reset_at: Optional[datetime] = None
    percentage_used: float = Field(0.0, ge=0, le=1)

    @classmethod
    def from_headers(
        cls,
        platform: Platform,
        limit: int,
        remaining: int,
        reset_at: Optional[datetime] = None,
        endpoint: Optional[str] = None,
    ) -> "RateLimitStatus":
        """Create from API response headers."""
        pct = 1 - (remaining / limit) if limit > 0 else 0
        return cls(
            platform=platform,
            endpoint=endpoint,
            limit=limit,
            remaining=remaining,
            reset_at=reset_at,
            percentage_used=pct,
        )


class AdPlatformAdapter(ABC):
    """Abstract base class for all ad platform adapters.

    Each platform adapter must implement these methods to provide
    a unified interface for campaign management.

    Authentication:
    - OAuth 2.0: Meta, Google, TikTok, LinkedIn, Pinterest
    - OAuth 1.0A: X/Twitter (uses requests_oauthlib for signing)
    """

    # Override in subclass
    platform: Platform
    auth_type: AuthType = AuthType.OAUTH2

    # Token lifecycle (days) - override per platform
    token_lifetime_days: Optional[int] = None  # None = no expiry

    def __init__(self, credentials: dict[str, str]):
        """Initialize adapter with platform credentials.

        Args:
            credentials: Platform-specific credential dict.
                OAuth 2.0: {access_token, refresh_token?, client_id?, client_secret?}
                OAuth 1.0A (X): {consumer_key, consumer_secret, access_token, access_token_secret}
        """
        self.credentials = credentials
        self._validate_credentials()

    @abstractmethod
    def _validate_credentials(self) -> None:
        """Validate that required credentials are present.

        Raises:
            ValueError: If required credentials are missing.
        """
        pass

    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Verify credentials are valid and have required permissions.

        Returns:
            True if credentials are valid and have ad management permissions.
        """
        pass

    @abstractmethod
    async def get_token_status(self) -> TokenStatus:
        """Check token health and expiry.

        Returns:
            TokenStatus with validity, expiry, and refresh needs.
        """
        pass

    @abstractmethod
    async def refresh_token(self) -> bool:
        """Refresh OAuth token if supported.

        Returns:
            True if token was refreshed, False if not supported or failed.
        """
        pass

    @abstractmethod
    async def create_campaign(self, config: CampaignConfig) -> CampaignResult:
        """Create a new ad campaign on the platform.

        This typically creates:
        1. Campaign (budget, objective)
        2. Ad Set (targeting, schedule)
        3. Ad (creative)

        Args:
            config: Campaign configuration.

        Returns:
            CampaignResult with platform IDs and status.
        """
        pass

    @abstractmethod
    async def pause_campaign(self, campaign_id: str) -> bool:
        """Pause an active campaign.

        Args:
            campaign_id: Platform-specific campaign ID.

        Returns:
            True if campaign was paused successfully.
        """
        pass

    @abstractmethod
    async def resume_campaign(self, campaign_id: str) -> bool:
        """Resume a paused campaign.

        Args:
            campaign_id: Platform-specific campaign ID.

        Returns:
            True if campaign was resumed successfully.
        """
        pass

    @abstractmethod
    async def get_campaign_status(self, campaign_id: str) -> CampaignStatus:
        """Get current status of a campaign.

        Args:
            campaign_id: Platform-specific campaign ID.

        Returns:
            Current campaign status.
        """
        pass

    @abstractmethod
    async def get_performance(
        self,
        campaign_id: str,
        start_date: str,
        end_date: str,
    ) -> PerformanceMetrics:
        """Fetch performance metrics for a campaign.

        Args:
            campaign_id: Platform-specific campaign ID.
            start_date: Start date (YYYY-MM-DD).
            end_date: End date (YYYY-MM-DD).

        Returns:
            PerformanceMetrics with impressions, clicks, conversions, spend.
        """
        pass

    @abstractmethod
    async def get_rate_limit_status(self) -> RateLimitStatus:
        """Check current rate limit status.

        Returns:
            RateLimitStatus with limit, remaining, and reset time.
        """
        pass

    def _map_objective(self, objective: CampaignObjective) -> str:
        """Map generic objective to platform-specific value.

        Override in subclass to provide platform-specific mapping.
        """
        return objective.value

    def _map_status(self, platform_status: str) -> CampaignStatus:
        """Map platform-specific status to generic status.

        Override in subclass to provide platform-specific mapping.
        """
        status_map = {
            "active": CampaignStatus.ACTIVE,
            "paused": CampaignStatus.PAUSED,
            "pending": CampaignStatus.PENDING_REVIEW,
            "completed": CampaignStatus.COMPLETED,
            "rejected": CampaignStatus.REJECTED,
        }
        return status_map.get(platform_status.lower(), CampaignStatus.ERROR)
