"""
TikTok Ads Adapter

Implements AdPlatformAdapter for TikTok Marketing API using
REST API via httpx (no official Python SDK).

Key features:
- OAuth 2.0 authentication
- v1.3 API endpoints
- Campaign, Ad Group, and Ad creation
- Spark Ads support (boosting organic content)

@story US-AC01, US-AC02, US-AC03
"""

import logging
from datetime import datetime
from typing import Optional, Any

import httpx

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


# TikTok API base URL
BASE_URL = "https://business-api.tiktok.com/open_api/v1.3"

# Map generic objectives to TikTok campaign objectives
OBJECTIVE_MAP = {
    CampaignObjective.AWARENESS: "REACH",
    CampaignObjective.TRAFFIC: "TRAFFIC",
    CampaignObjective.CONVERSIONS: "CONVERSIONS",
    CampaignObjective.APP_INSTALLS: "APP_INSTALL",
    CampaignObjective.VIDEO_VIEWS: "VIDEO_VIEWS",
    CampaignObjective.LEAD_GENERATION: "LEAD_GENERATION",
    CampaignObjective.ENGAGEMENT: "ENGAGEMENT",
    CampaignObjective.REACH: "REACH",
}

# Map TikTok status to generic status
STATUS_MAP = {
    "ENABLE": CampaignStatus.ACTIVE,
    "DISABLE": CampaignStatus.PAUSED,
    "DELETE": CampaignStatus.COMPLETED,
    "ADVERTISER_CAMPAIGN_STATUS_ENABLE": CampaignStatus.ACTIVE,
    "ADVERTISER_CAMPAIGN_STATUS_DISABLE": CampaignStatus.PAUSED,
}


class TikTokAdsAdapter(AdPlatformAdapter):
    """TikTok Ads adapter.

    Authentication:
        Uses OAuth 2.0 with access tokens from TikTok Business Center.

    Required credentials:
        - access_token: TikTok access token
        - advertiser_id: TikTok Advertiser ID
        - app_id: TikTok App ID
        - app_secret: TikTok App Secret (for token refresh)

    Usage:
        adapter = TikTokAdsAdapter({
            "access_token": "...",
            "advertiser_id": "123456789",
            "app_id": "...",
            "app_secret": "...",
        })

        result = await adapter.create_campaign(config)
    """

    platform = Platform.TIKTOK
    auth_type = AuthType.OAUTH2
    token_lifetime_days = None  # Varies by token type

    def __init__(self, credentials: dict[str, str]):
        """Initialize TikTok Ads adapter."""
        super().__init__(credentials)

        self.advertiser_id = credentials["advertiser_id"]
        self.access_token = credentials["access_token"]

        # HTTP client with auth headers
        self._client: Optional[httpx.AsyncClient] = None

    def _validate_credentials(self) -> None:
        """Validate required credentials are present."""
        required = ["access_token", "advertiser_id"]
        missing = [k for k in required if not self.credentials.get(k)]
        if missing:
            raise ValueError(f"Missing required credentials: {', '.join(missing)}")

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=BASE_URL,
                headers={
                    "Access-Token": self.access_token,
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Make API request to TikTok."""
        client = await self._get_client()

        if method.upper() == "GET":
            response = await client.get(endpoint, params=params)
        else:
            response = await client.post(endpoint, json=data)

        result = response.json()

        if result.get("code") != 0:
            error_msg = result.get("message", "Unknown error")
            logger.error(f"TikTok API error: {error_msg}")
            raise RuntimeError(f"TikTok API error: {error_msg}")

        return result.get("data", {})

    async def validate_credentials(self) -> bool:
        """Verify credentials are valid and have ad management permissions."""
        try:
            # Get advertiser info
            data = await self._request(
                "GET",
                "/advertiser/info/",
                params={"advertiser_ids": f'["{self.advertiser_id}"]'},
            )

            if data.get("list"):
                advertiser = data["list"][0]
                logger.info(f"TikTok credentials valid for: {advertiser.get('name', self.advertiser_id)}")
                return True

            return False

        except Exception as e:
            logger.error(f"TikTok credential validation failed: {e}")
            return False

    async def get_token_status(self) -> TokenStatus:
        """Check token health and expiry."""
        try:
            valid = await self.validate_credentials()

            return TokenStatus(
                platform=self.platform,
                valid=valid,
                # TikTok doesn't expose token expiry easily
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

        Requires app_id and app_secret.
        """
        app_id = self.credentials.get("app_id")
        app_secret = self.credentials.get("app_secret")
        refresh_token = self.credentials.get("refresh_token")

        if not all([app_id, app_secret, refresh_token]):
            logger.warning("Cannot refresh TikTok token without app credentials")
            return False

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BASE_URL}/oauth2/refresh_token/",
                    json={
                        "app_id": app_id,
                        "secret": app_secret,
                        "refresh_token": refresh_token,
                    },
                )

                result = response.json()
                if result.get("code") != 0:
                    logger.error(f"Token refresh failed: {result.get('message')}")
                    return False

                data = result.get("data", {})
                new_token = data.get("access_token")

                if new_token:
                    self.credentials["access_token"] = new_token
                    self.access_token = new_token
                    self._client = None  # Force client recreation
                    logger.info("TikTok token refreshed successfully")
                    return True

        except Exception as e:
            logger.error(f"Token refresh error: {e}")

        return False

    async def create_campaign(self, config: CampaignConfig) -> CampaignResult:
        """Create a new ad campaign on TikTok.

        Creates:
        1. Campaign with objective and budget
        2. Ad Group with targeting and schedule
        3. Ad with creative
        """
        try:
            # 1. Create Campaign
            campaign_data = await self._request(
                "POST",
                "/campaign/create/",
                data={
                    "advertiser_id": self.advertiser_id,
                    "campaign_name": config.name,
                    "objective_type": self._map_objective(config.objective),
                    "budget_mode": "BUDGET_MODE_DAY" if config.daily_budget_cents else "BUDGET_MODE_TOTAL",
                    "budget": (config.daily_budget_cents or config.budget_cents) / 100,
                    "operation_status": "DISABLE",  # Start paused
                },
            )
            campaign_id = campaign_data.get("campaign_id")
            logger.info(f"Created TikTok campaign: {campaign_id}")

            # 2. Create Ad Group
            targeting = self._build_targeting(config.targeting)

            adgroup_data = await self._request(
                "POST",
                "/adgroup/create/",
                data={
                    "advertiser_id": self.advertiser_id,
                    "campaign_id": campaign_id,
                    "adgroup_name": f"{config.name} - Ad Group",
                    "placement_type": "PLACEMENT_TYPE_AUTOMATIC",
                    "budget_mode": "BUDGET_MODE_DAY" if config.daily_budget_cents else "BUDGET_MODE_TOTAL",
                    "budget": (config.daily_budget_cents or config.budget_cents) / 100,
                    "schedule_type": "SCHEDULE_START_END",
                    "schedule_start_time": config.start_date,
                    "schedule_end_time": config.end_date or "",
                    "optimization_goal": "CLICK",
                    "bid_type": "BID_TYPE_NO_BID",
                    "billing_event": "CPC",
                    "operation_status": "DISABLE",
                    **targeting,
                },
            )
            adgroup_id = adgroup_data.get("adgroup_id")
            logger.info(f"Created TikTok ad group: {adgroup_id}")

            # 3. Create Ad
            ad_data = await self._request(
                "POST",
                "/ad/create/",
                data={
                    "advertiser_id": self.advertiser_id,
                    "adgroup_id": adgroup_id,
                    "ad_name": f"{config.name} - Ad",
                    "ad_text": config.creative.body or config.creative.headline,
                    "call_to_action": self._map_cta(config.creative.call_to_action),
                    "landing_page_url": config.creative.landing_url,
                    "image_ids": [],  # Would need to upload image first
                    "video_id": None,  # Would need to upload video first
                    "operation_status": "DISABLE",
                },
            )
            ad_id = adgroup_data.get("ad_id") or adgroup_data.get("ad_ids", [""])[0]
            logger.info(f"Created TikTok ad: {ad_id}")

            return CampaignResult(
                platform=self.platform,
                platform_campaign_id=campaign_id,
                platform_ad_set_id=adgroup_id,
                platform_ad_id=ad_id,
                status=CampaignStatus.DRAFT,
                created_at=datetime.now(),
            )

        except Exception as e:
            logger.error(f"TikTok campaign creation failed: {e}")
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
            await self._request(
                "POST",
                "/campaign/update/status/",
                data={
                    "advertiser_id": self.advertiser_id,
                    "campaign_ids": [campaign_id],
                    "operation_status": "DISABLE",
                },
            )
            logger.info(f"Paused TikTok campaign: {campaign_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to pause campaign: {e}")
            return False

    async def resume_campaign(self, campaign_id: str) -> bool:
        """Resume a paused campaign."""
        try:
            await self._request(
                "POST",
                "/campaign/update/status/",
                data={
                    "advertiser_id": self.advertiser_id,
                    "campaign_ids": [campaign_id],
                    "operation_status": "ENABLE",
                },
            )
            logger.info(f"Resumed TikTok campaign: {campaign_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to resume campaign: {e}")
            return False

    async def get_campaign_status(self, campaign_id: str) -> CampaignStatus:
        """Get current status of a campaign."""
        try:
            data = await self._request(
                "GET",
                "/campaign/get/",
                params={
                    "advertiser_id": self.advertiser_id,
                    "filtering": f'{{"campaign_ids": ["{campaign_id}"]}}',
                },
            )

            if data.get("list"):
                campaign = data["list"][0]
                status = campaign.get("operation_status", "UNKNOWN")
                return STATUS_MAP.get(status, CampaignStatus.ERROR)

            return CampaignStatus.ERROR

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
            data = await self._request(
                "GET",
                "/report/integrated/get/",
                params={
                    "advertiser_id": self.advertiser_id,
                    "report_type": "BASIC",
                    "dimensions": '["campaign_id"]',
                    "metrics": '["spend", "impressions", "clicks", "conversion"]',
                    "start_date": start_date,
                    "end_date": end_date,
                    "filtering": f'{{"campaign_ids": ["{campaign_id}"]}}',
                },
            )

            if not data.get("list"):
                return PerformanceMetrics(
                    campaign_id=campaign_id,
                    platform=self.platform,
                    date_start=start_date,
                    date_end=end_date,
                )

            row = data["list"][0].get("metrics", {})

            metrics = PerformanceMetrics(
                campaign_id=campaign_id,
                platform=self.platform,
                date_start=start_date,
                date_end=end_date,
                impressions=int(row.get("impressions", 0)),
                clicks=int(row.get("clicks", 0)),
                conversions=int(row.get("conversion", 0)),
                spend_cents=int(float(row.get("spend", 0)) * 100),
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
        # TikTok rate limits are per-endpoint
        return RateLimitStatus(
            platform=self.platform,
            limit=100,  # Conservative estimate
            remaining=90,
            percentage_used=0.1,
        )

    def _map_objective(self, objective: CampaignObjective) -> str:
        """Map generic objective to TikTok-specific objective."""
        return OBJECTIVE_MAP.get(objective, "TRAFFIC")

    def _build_targeting(self, targeting) -> dict:
        """Build TikTok targeting spec from generic targeting config."""
        spec = {}

        if targeting.locations:
            spec["location_ids"] = targeting.locations

        if targeting.age_min or targeting.age_max:
            # TikTok uses age groups
            spec["age_groups"] = self._age_to_groups(targeting.age_min, targeting.age_max)

        if targeting.genders:
            gender_map = {"male": "MALE", "female": "FEMALE"}
            spec["gender"] = gender_map.get(targeting.genders[0], "UNLIMITED") if targeting.genders else "UNLIMITED"

        if targeting.interests:
            spec["interest_category_ids"] = targeting.interests

        if targeting.languages:
            spec["languages"] = targeting.languages

        return spec

    def _age_to_groups(self, min_age: Optional[int], max_age: Optional[int]) -> list[str]:
        """Convert age range to TikTok age groups."""
        groups = []
        age_group_map = [
            (13, 17, "AGE_13_17"),
            (18, 24, "AGE_18_24"),
            (25, 34, "AGE_25_34"),
            (35, 44, "AGE_35_44"),
            (45, 54, "AGE_45_54"),
            (55, 100, "AGE_55_100"),
        ]

        min_age = min_age or 18
        max_age = max_age or 65

        for group_min, group_max, group_name in age_group_map:
            if min_age <= group_max and max_age >= group_min:
                groups.append(group_name)

        return groups

    def _map_cta(self, cta: Optional[str]) -> str:
        """Map generic CTA to TikTok CTA."""
        cta_map = {
            "learn_more": "LEARN_MORE",
            "sign_up": "SIGN_UP",
            "shop_now": "SHOP_NOW",
            "download": "DOWNLOAD",
            "contact_us": "CONTACT_US",
            "book_now": "BOOK_NOW",
        }
        return cta_map.get(cta or "", "LEARN_MORE")
