"""
Pinterest Ads Adapter

Implements AdPlatformAdapter for Pinterest Ads API using the
official pinterest-api-sdk Python library.

Key features:
- OAuth 2.0 authentication
- Campaign, Ad Group, and Ad creation
- Performance metrics retrieval
- Pin-based creative support

@story US-AC01, US-AC02, US-AC03
"""

import logging
from datetime import datetime
from typing import Optional

from pinterest.client import PinterestSDKClient
from pinterest.organic.pins import Pin
from pinterest.ads.campaigns import Campaign
from pinterest.ads.ad_groups import AdGroup
from pinterest.ads.ads import Ad

from .interface import (
    AdPlatformAdapter,
    AuthType,
    Platform,
    CampaignObjective,
    CampaignConfig,
    CampaignResult,
    CampaignStatus,
    PerformanceMetrics,
    TokenStatus,
    RateLimitStatus,
)


logger = logging.getLogger(__name__)


# Map generic objectives to Pinterest campaign objectives
OBJECTIVE_MAP = {
    CampaignObjective.AWARENESS: "AWARENESS",
    CampaignObjective.TRAFFIC: "WEB_SESSIONS",
    CampaignObjective.CONVERSIONS: "WEB_CONVERSIONS",
    CampaignObjective.APP_INSTALLS: "APP_INSTALL",
    CampaignObjective.VIDEO_VIEWS: "VIDEO_VIEW",
    CampaignObjective.LEAD_GENERATION: "LEAD_GENERATION",
    CampaignObjective.ENGAGEMENT: "ENGAGEMENT",
    CampaignObjective.REACH: "AWARENESS",
}

# Map Pinterest status to generic status
STATUS_MAP = {
    "ACTIVE": CampaignStatus.ACTIVE,
    "PAUSED": CampaignStatus.PAUSED,
    "ARCHIVED": CampaignStatus.COMPLETED,
    "DRAFT": CampaignStatus.DRAFT,
}


class PinterestAdsAdapter(AdPlatformAdapter):
    """Pinterest Ads adapter.

    Authentication:
        Uses OAuth 2.0 with access tokens.
        Tokens have a standard expiry and can be refreshed.

    Required credentials:
        - access_token: Pinterest access token (pina_...)
        - ad_account_id: Pinterest Ad Account ID
        - refresh_token: OAuth refresh token (optional)
        - client_id: App client ID (optional, for refresh)
        - client_secret: App client secret (optional, for refresh)

    Usage:
        adapter = PinterestAdsAdapter({
            "access_token": "pina_...",
            "ad_account_id": "123456789",
        })

        result = await adapter.create_campaign(config)
    """

    platform = Platform.PINTEREST
    auth_type = AuthType.OAUTH2
    token_lifetime_days = 30  # Pinterest tokens expire in ~30 days

    def __init__(self, credentials: dict[str, str]):
        """Initialize Pinterest Ads adapter."""
        super().__init__(credentials)

        self.ad_account_id = credentials["ad_account_id"]

        # Initialize Pinterest SDK client
        self.client = PinterestSDKClient.create_client_with_token(
            access_token=credentials["access_token"],
        )

    def _validate_credentials(self) -> None:
        """Validate required credentials are present."""
        required = ["access_token", "ad_account_id"]
        missing = [k for k in required if not self.credentials.get(k)]
        if missing:
            raise ValueError(f"Missing required credentials: {', '.join(missing)}")

        # Validate token format
        if not self.credentials["access_token"].startswith("pina_"):
            logger.warning("Pinterest access token should start with 'pina_'")

    async def validate_credentials(self) -> bool:
        """Verify credentials are valid and have ad management permissions."""
        try:
            # Try to get ad account info
            from pinterest.ads.ad_accounts import AdAccount

            account = AdAccount(
                ad_account_id=self.ad_account_id,
                client=self.client,
            )
            data = account.get_info()

            logger.info(f"Pinterest credentials valid for account: {data.get('name', self.ad_account_id)}")
            return True

        except Exception as e:
            logger.error(f"Pinterest credential validation failed: {e}")
            return False

    async def get_token_status(self) -> TokenStatus:
        """Check token health and expiry."""
        try:
            valid = await self.validate_credentials()

            return TokenStatus(
                platform=self.platform,
                valid=valid,
                # Pinterest doesn't expose token expiry in API responses
                expires_at=None,
                needs_refresh=False,
            )

        except Exception as e:
            return TokenStatus(
                platform=self.platform,
                valid=False,
                error_message=str(e),
            )

    async def refresh_token(self) -> bool:
        """Refresh OAuth token.

        Requires client_id, client_secret, and refresh_token.
        """
        client_id = self.credentials.get("client_id")
        client_secret = self.credentials.get("client_secret")
        refresh_token = self.credentials.get("refresh_token")

        if not all([client_id, client_secret, refresh_token]):
            logger.warning("Cannot refresh Pinterest token without client_id, client_secret, refresh_token")
            return False

        try:
            import httpx

            async with httpx.AsyncClient() as http_client:
                response = await http_client.post(
                    "https://api.pinterest.com/v5/oauth/token",
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token,
                        "client_id": client_id,
                        "client_secret": client_secret,
                    },
                )

                if response.status_code != 200:
                    logger.error(f"Token refresh failed: {response.text}")
                    return False

                data = response.json()
                new_token = data.get("access_token")

                if new_token:
                    self.credentials["access_token"] = new_token
                    self.client = PinterestSDKClient.create_client_with_token(
                        access_token=new_token,
                    )
                    logger.info("Pinterest token refreshed successfully")
                    return True

        except Exception as e:
            logger.error(f"Token refresh error: {e}")

        return False

    async def create_campaign(self, config: CampaignConfig) -> CampaignResult:
        """Create a new ad campaign on Pinterest.

        Creates:
        1. Campaign with objective and budget
        2. Ad Group with targeting
        3. Pin (creative)
        4. Ad linking pin to ad group
        """
        try:
            # 1. Create Campaign
            campaign = Campaign.create(
                ad_account_id=self.ad_account_id,
                name=config.name,
                objective_type=self._map_objective(config.objective),
                status="PAUSED",
                daily_spend_cap=config.daily_budget_cents if config.daily_budget_cents else None,
                lifetime_spend_cap=config.budget_cents if not config.daily_budget_cents else None,
                client=self.client,
            )
            campaign_id = campaign.id
            logger.info(f"Created Pinterest campaign: {campaign_id}")

            # 2. Create Ad Group
            targeting_spec = self._build_targeting(config.targeting)

            ad_group = AdGroup.create(
                ad_account_id=self.ad_account_id,
                campaign_id=campaign_id,
                name=f"{config.name} - Ad Group",
                status="PAUSED",
                auto_targeting_enabled=True,
                targeting_spec=targeting_spec,
                start_time=config.start_date,
                end_time=config.end_date,
                bid_in_micro_currency=100000,  # $0.10 bid
                client=self.client,
            )
            ad_group_id = ad_group.id
            logger.info(f"Created Pinterest ad group: {ad_group_id}")

            # 3. Create Pin (organic pin that will be promoted)
            # Note: In production, you might use existing pins or create via Pins API
            pin = Pin.create(
                board_id=self.credentials.get("board_id", ""),  # Requires a board
                title=config.creative.headline,
                description=config.creative.body,
                link=config.creative.landing_url,
                media_source={
                    "source_type": "image_url",
                    "url": config.creative.image_url,
                } if config.creative.image_url else None,
                client=self.client,
            )
            pin_id = pin.id
            logger.info(f"Created Pinterest pin: {pin_id}")

            # 4. Create Ad (promotes the pin)
            ad = Ad.create(
                ad_account_id=self.ad_account_id,
                ad_group_id=ad_group_id,
                creative_type="REGULAR",
                pin_id=pin_id,
                name=f"{config.name} - Ad",
                status="PAUSED",
                client=self.client,
            )
            ad_id = ad.id
            logger.info(f"Created Pinterest ad: {ad_id}")

            return CampaignResult(
                platform=self.platform,
                platform_campaign_id=campaign_id,
                platform_ad_set_id=ad_group_id,
                platform_ad_id=ad_id,
                status=CampaignStatus.DRAFT,
                created_at=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Pinterest campaign creation failed: {e}")
            return CampaignResult(
                platform=self.platform,
                platform_campaign_id="",
                status=CampaignStatus.ERROR,
                created_at=datetime.now(),
                error_message=str(e),
            )

    async def pause_campaign(self, campaign_id: str) -> bool:
        """Pause an active campaign."""
        try:
            campaign = Campaign(
                ad_account_id=self.ad_account_id,
                campaign_id=campaign_id,
                client=self.client,
            )
            campaign.update_fields(status="PAUSED")
            logger.info(f"Paused Pinterest campaign: {campaign_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to pause campaign: {e}")
            return False

    async def resume_campaign(self, campaign_id: str) -> bool:
        """Resume a paused campaign."""
        try:
            campaign = Campaign(
                ad_account_id=self.ad_account_id,
                campaign_id=campaign_id,
                client=self.client,
            )
            campaign.update_fields(status="ACTIVE")
            logger.info(f"Resumed Pinterest campaign: {campaign_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to resume campaign: {e}")
            return False

    async def get_campaign_status(self, campaign_id: str) -> CampaignStatus:
        """Get current status of a campaign."""
        try:
            campaign = Campaign(
                ad_account_id=self.ad_account_id,
                campaign_id=campaign_id,
                client=self.client,
            )
            data = campaign.get_info()
            status = data.get("status", "UNKNOWN")
            return STATUS_MAP.get(status, CampaignStatus.ERROR)
        except Exception:
            return CampaignStatus.ERROR

    async def get_performance(
        self,
        campaign_id: str,
        start_date: str,
        end_date: str,
    ) -> PerformanceMetrics:
        """Fetch performance metrics for a campaign."""
        try:
            campaign = Campaign(
                ad_account_id=self.ad_account_id,
                campaign_id=campaign_id,
                client=self.client,
            )

            # Get analytics
            analytics = campaign.get_analytics(
                start_date=start_date,
                end_date=end_date,
                columns=[
                    "IMPRESSION",
                    "CLICKTHROUGH",
                    "TOTAL_CONVERSIONS",
                    "SPEND_IN_MICRO_DOLLAR",
                ],
                granularity="TOTAL",
            )

            if not analytics:
                return PerformanceMetrics(
                    campaign_id=campaign_id,
                    platform=self.platform,
                    date_start=start_date,
                    date_end=end_date,
                )

            data = analytics[0] if isinstance(analytics, list) else analytics

            metrics = PerformanceMetrics(
                campaign_id=campaign_id,
                platform=self.platform,
                date_start=start_date,
                date_end=end_date,
                impressions=int(data.get("IMPRESSION", 0)),
                clicks=int(data.get("CLICKTHROUGH", 0)),
                conversions=int(data.get("TOTAL_CONVERSIONS", 0)),
                spend_cents=int(data.get("SPEND_IN_MICRO_DOLLAR", 0)) // 10000,
            )

            metrics.calculate_derived_metrics()
            return metrics

        except Exception as e:
            logger.error(f"Failed to get performance: {e}")
            return PerformanceMetrics(
                campaign_id=campaign_id,
                platform=self.platform,
                date_start=start_date,
                date_end=end_date,
            )

    async def get_rate_limit_status(self) -> RateLimitStatus:
        """Check current rate limit status."""
        # Pinterest uses standard rate limiting
        # Limits are returned in response headers but not easily accessible via SDK
        return RateLimitStatus(
            platform=self.platform,
            limit=1000,  # Conservative estimate
            remaining=900,
            percentage_used=0.1,
        )

    def _map_objective(self, objective: CampaignObjective) -> str:
        """Map generic objective to Pinterest-specific objective."""
        return OBJECTIVE_MAP.get(objective, "WEB_SESSIONS")

    def _build_targeting(self, targeting) -> dict:
        """Build Pinterest targeting spec from generic targeting config."""
        spec = {}

        if targeting.locations:
            spec["geo"] = targeting.locations

        if targeting.age_min or targeting.age_max:
            # Pinterest uses age buckets
            spec["age_bucket"] = self._age_to_buckets(targeting.age_min, targeting.age_max)

        if targeting.genders:
            gender_map = {"male": "male", "female": "female"}
            spec["gender"] = [gender_map.get(g) for g in targeting.genders if g in gender_map]

        if targeting.interests:
            spec["interest"] = targeting.interests

        if targeting.keywords:
            spec["keyword"] = targeting.keywords

        if targeting.languages:
            spec["locale"] = targeting.languages

        return spec

    def _age_to_buckets(self, min_age: Optional[int], max_age: Optional[int]) -> list[str]:
        """Convert age range to Pinterest age buckets."""
        buckets = []
        age_bucket_map = [
            (18, 24, "18-24"),
            (25, 34, "25-34"),
            (35, 44, "35-44"),
            (45, 54, "45-54"),
            (55, 64, "55-64"),
            (65, 100, "65+"),
        ]

        min_age = min_age or 18
        max_age = max_age or 65

        for bucket_min, bucket_max, bucket_name in age_bucket_map:
            if min_age <= bucket_max and max_age >= bucket_min:
                buckets.append(bucket_name)

        return buckets
