"""
Meta (Facebook/Instagram) Ads Adapter

Implements AdPlatformAdapter for Meta Marketing API using the
facebook-business SDK.

Key features:
- OAuth 2.0 authentication with 60-day token lifecycle
- Campaign, Ad Set, and Ad creation
- Performance metrics retrieval
- Rate limit monitoring

@story US-AC01, US-AC02, US-AC03
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.exceptions import FacebookRequestError

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


# Map generic objectives to Meta campaign objectives
OBJECTIVE_MAP = {
    CampaignObjective.AWARENESS: Campaign.Objective.outcome_awareness,
    CampaignObjective.TRAFFIC: Campaign.Objective.outcome_traffic,
    CampaignObjective.CONVERSIONS: Campaign.Objective.outcome_sales,
    CampaignObjective.APP_INSTALLS: Campaign.Objective.outcome_app_promotion,
    CampaignObjective.VIDEO_VIEWS: Campaign.Objective.outcome_awareness,
    CampaignObjective.LEAD_GENERATION: Campaign.Objective.outcome_leads,
    CampaignObjective.ENGAGEMENT: Campaign.Objective.outcome_engagement,
    CampaignObjective.REACH: Campaign.Objective.outcome_awareness,
}

# Map Meta status to generic status
STATUS_MAP = {
    "ACTIVE": CampaignStatus.ACTIVE,
    "PAUSED": CampaignStatus.PAUSED,
    "DELETED": CampaignStatus.COMPLETED,
    "ARCHIVED": CampaignStatus.COMPLETED,
    "PENDING_REVIEW": CampaignStatus.PENDING_REVIEW,
    "DISAPPROVED": CampaignStatus.REJECTED,
    "PREAPPROVED": CampaignStatus.PENDING_REVIEW,
    "PENDING_BILLING_INFO": CampaignStatus.ERROR,
    "CAMPAIGN_PAUSED": CampaignStatus.PAUSED,
    "ADSET_PAUSED": CampaignStatus.PAUSED,
}


class MetaAdsAdapter(AdPlatformAdapter):
    """Meta (Facebook/Instagram) Ads adapter.

    Authentication:
        Uses OAuth 2.0 with long-lived access tokens.
        Tokens expire after 60 days and must be refreshed.

    Required credentials:
        - access_token: Long-lived user access token
        - ad_account_id: Ad account ID (format: act_123456789)
        - app_id: Facebook App ID (optional, for token refresh)
        - app_secret: Facebook App Secret (optional, for token refresh)
        - business_manager_id: Business Manager ID (optional)

    Usage:
        adapter = MetaAdsAdapter({
            "access_token": "EAA...",
            "ad_account_id": "act_123456789",
        })

        result = await adapter.create_campaign(config)
    """

    platform = Platform.META
    auth_type = AuthType.OAUTH2
    token_lifetime_days = 60  # Meta tokens expire in 60 days

    def __init__(self, credentials: dict[str, str]):
        """Initialize Meta Ads adapter."""
        super().__init__(credentials)

        # Initialize Facebook Ads API
        self.api = FacebookAdsApi.init(
            app_id=credentials.get("app_id"),
            app_secret=credentials.get("app_secret"),
            access_token=credentials["access_token"],
        )

        # Get ad account
        self.ad_account_id = credentials["ad_account_id"]
        if not self.ad_account_id.startswith("act_"):
            self.ad_account_id = f"act_{self.ad_account_id}"

        self.ad_account = AdAccount(self.ad_account_id)
        self.business_manager_id = credentials.get("business_manager_id")

        # Track token issue time (if provided)
        self._token_issued_at: Optional[datetime] = None
        if "token_issued_at" in credentials:
            self._token_issued_at = datetime.fromisoformat(credentials["token_issued_at"])

    def _validate_credentials(self) -> None:
        """Validate required credentials are present."""
        required = ["access_token", "ad_account_id"]
        missing = [k for k in required if not self.credentials.get(k)]
        if missing:
            raise ValueError(f"Missing required credentials: {', '.join(missing)}")

    async def validate_credentials(self) -> bool:
        """Verify credentials are valid and have ad management permissions."""
        try:
            # Try to read ad account info
            account = self.ad_account.api_get(
                fields=["name", "account_status", "capabilities"]
            )

            # Check account is active (status 1 = active)
            if account.get("account_status") != 1:
                logger.warning(f"Meta ad account not active: status={account.get('account_status')}")
                return False

            logger.info(f"Meta credentials valid for account: {account.get('name')}")
            return True

        except FacebookRequestError as e:
            logger.error(f"Meta credential validation failed: {e.api_error_message()}")
            return False

    async def get_token_status(self) -> TokenStatus:
        """Check token health and expiry."""
        try:
            # Debug token to check validity
            from facebook_business.adobjects.user import User

            me = User(fbid="me")
            debug_info = me.api_get(fields=["id", "name"])

            # Calculate expiry based on issued time
            expires_at = None
            if self._token_issued_at:
                expires_at = self._token_issued_at + timedelta(days=self.token_lifetime_days)

            return TokenStatus.from_expiry(
                platform=self.platform,
                expires_at=expires_at,
                valid=True,
            )

        except FacebookRequestError as e:
            return TokenStatus(
                platform=self.platform,
                valid=False,
                error_message=e.api_error_message(),
            )

    async def refresh_token(self) -> bool:
        """Refresh OAuth token.

        Meta tokens can be exchanged for new long-lived tokens
        if app_id and app_secret are provided.
        """
        app_id = self.credentials.get("app_id")
        app_secret = self.credentials.get("app_secret")

        if not app_id or not app_secret:
            logger.warning("Cannot refresh Meta token without app_id and app_secret")
            return False

        try:
            import httpx

            # Exchange for new long-lived token
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://graph.facebook.com/v19.0/oauth/access_token",
                    params={
                        "grant_type": "fb_exchange_token",
                        "client_id": app_id,
                        "client_secret": app_secret,
                        "fb_exchange_token": self.credentials["access_token"],
                    },
                )

                if response.status_code != 200:
                    logger.error(f"Token refresh failed: {response.text}")
                    return False

                data = response.json()
                new_token = data.get("access_token")

                if new_token:
                    # Update credentials and API
                    self.credentials["access_token"] = new_token
                    self._token_issued_at = datetime.now()

                    self.api = FacebookAdsApi.init(
                        app_id=app_id,
                        app_secret=app_secret,
                        access_token=new_token,
                    )

                    logger.info("Meta token refreshed successfully")
                    return True

        except Exception as e:
            logger.error(f"Token refresh error: {e}")

        return False

    async def create_campaign(self, config: CampaignConfig) -> CampaignResult:
        """Create a new ad campaign on Meta.

        Creates:
        1. Campaign with objective and budget
        2. Ad Set with targeting and schedule
        3. Ad Creative with image/video and copy
        4. Ad linking creative to ad set
        """
        try:
            # 1. Create Campaign
            campaign = self.ad_account.create_campaign(
                params={
                    Campaign.Field.name: config.name,
                    Campaign.Field.objective: self._map_objective(config.objective),
                    Campaign.Field.status: Campaign.Status.paused,  # Start paused
                    Campaign.Field.special_ad_categories: [],
                }
            )
            campaign_id = campaign.get_id()
            logger.info(f"Created Meta campaign: {campaign_id}")

            # 2. Create Ad Set
            targeting = self._build_targeting(config.targeting)

            adset_params = {
                AdSet.Field.name: f"{config.name} - Ad Set",
                AdSet.Field.campaign_id: campaign_id,
                AdSet.Field.billing_event: AdSet.BillingEvent.impressions,
                AdSet.Field.optimization_goal: AdSet.OptimizationGoal.reach,
                AdSet.Field.daily_budget: config.daily_budget_cents if config.daily_budget_cents else None,
                AdSet.Field.lifetime_budget: config.budget_cents if not config.daily_budget_cents else None,
                AdSet.Field.start_time: config.start_date,
                AdSet.Field.targeting: targeting,
                AdSet.Field.status: AdSet.Status.paused,
            }

            if config.end_date:
                adset_params[AdSet.Field.end_time] = config.end_date

            # Remove None values
            adset_params = {k: v for k, v in adset_params.items() if v is not None}

            adset = self.ad_account.create_ad_set(params=adset_params)
            adset_id = adset.get_id()
            logger.info(f"Created Meta ad set: {adset_id}")

            # 3. Create Ad Creative
            creative_params = {
                AdCreative.Field.name: f"{config.name} - Creative",
                AdCreative.Field.object_story_spec: {
                    "page_id": self.credentials.get("page_id", ""),
                    "link_data": {
                        "link": config.creative.landing_url,
                        "message": config.creative.body or "",
                        "name": config.creative.headline,
                        "call_to_action": {
                            "type": self._map_cta(config.creative.call_to_action),
                            "value": {"link": config.creative.landing_url},
                        },
                    },
                },
            }

            if config.creative.image_url:
                creative_params[AdCreative.Field.object_story_spec]["link_data"]["picture"] = config.creative.image_url

            creative = self.ad_account.create_ad_creative(params=creative_params)
            creative_id = creative.get_id()
            logger.info(f"Created Meta creative: {creative_id}")

            # 4. Create Ad
            ad = self.ad_account.create_ad(
                params={
                    Ad.Field.name: f"{config.name} - Ad",
                    Ad.Field.adset_id: adset_id,
                    Ad.Field.creative: {"creative_id": creative_id},
                    Ad.Field.status: Ad.Status.paused,
                }
            )
            ad_id = ad.get_id()
            logger.info(f"Created Meta ad: {ad_id}")

            return CampaignResult(
                platform=self.platform,
                platform_campaign_id=campaign_id,
                platform_ad_set_id=adset_id,
                platform_ad_id=ad_id,
                status=CampaignStatus.DRAFT,
                created_at=datetime.now(),
            )

        except FacebookRequestError as e:
            logger.error(f"Meta campaign creation failed: {e.api_error_message()}")
            return CampaignResult(
                platform=self.platform,
                platform_campaign_id="",
                status=CampaignStatus.ERROR,
                created_at=datetime.now(),
                error_message=e.api_error_message(),
            )

    async def pause_campaign(self, campaign_id: str) -> bool:
        """Pause an active campaign."""
        try:
            campaign = Campaign(campaign_id)
            campaign.api_update(params={Campaign.Field.status: Campaign.Status.paused})
            logger.info(f"Paused Meta campaign: {campaign_id}")
            return True
        except FacebookRequestError as e:
            logger.error(f"Failed to pause campaign: {e.api_error_message()}")
            return False

    async def resume_campaign(self, campaign_id: str) -> bool:
        """Resume a paused campaign."""
        try:
            campaign = Campaign(campaign_id)
            campaign.api_update(params={Campaign.Field.status: Campaign.Status.active})
            logger.info(f"Resumed Meta campaign: {campaign_id}")
            return True
        except FacebookRequestError as e:
            logger.error(f"Failed to resume campaign: {e.api_error_message()}")
            return False

    async def get_campaign_status(self, campaign_id: str) -> CampaignStatus:
        """Get current status of a campaign."""
        try:
            campaign = Campaign(campaign_id)
            data = campaign.api_get(fields=["effective_status"])
            status = data.get("effective_status", "UNKNOWN")
            return STATUS_MAP.get(status, CampaignStatus.ERROR)
        except FacebookRequestError:
            return CampaignStatus.ERROR

    async def get_performance(
        self,
        campaign_id: str,
        start_date: str,
        end_date: str,
    ) -> PerformanceMetrics:
        """Fetch performance metrics for a campaign."""
        try:
            campaign = Campaign(campaign_id)
            insights = campaign.get_insights(
                params={
                    "time_range": {
                        "since": start_date,
                        "until": end_date,
                    },
                },
                fields=[
                    AdsInsights.Field.impressions,
                    AdsInsights.Field.clicks,
                    AdsInsights.Field.conversions,
                    AdsInsights.Field.spend,
                    AdsInsights.Field.reach,
                    AdsInsights.Field.frequency,
                    AdsInsights.Field.ctr,
                    AdsInsights.Field.cpc,
                    AdsInsights.Field.cpm,
                ],
            )

            if not insights:
                return PerformanceMetrics(
                    campaign_id=campaign_id,
                    platform=self.platform,
                    date_start=start_date,
                    date_end=end_date,
                )

            data = insights[0]

            metrics = PerformanceMetrics(
                campaign_id=campaign_id,
                platform=self.platform,
                date_start=start_date,
                date_end=end_date,
                impressions=int(data.get("impressions", 0)),
                clicks=int(data.get("clicks", 0)),
                conversions=int(data.get("conversions", 0)),
                spend_cents=int(float(data.get("spend", 0)) * 100),
                reach=int(data.get("reach", 0)),
                frequency=float(data.get("frequency", 0)),
                raw_data=dict(data),
            )

            metrics.calculate_derived_metrics()
            return metrics

        except FacebookRequestError as e:
            logger.error(f"Failed to get performance: {e.api_error_message()}")
            return PerformanceMetrics(
                campaign_id=campaign_id,
                platform=self.platform,
                date_start=start_date,
                date_end=end_date,
            )

    async def get_rate_limit_status(self) -> RateLimitStatus:
        """Check current rate limit status.

        Meta uses app-level rate limiting based on:
        - Active ads count
        - Account tier
        """
        try:
            # Get account info which includes rate limit headers
            account = self.ad_account.api_get(fields=["name"])

            # Meta doesn't expose rate limits directly in API responses
            # Use conservative estimates based on tier
            # Standard tier: 190,000 + 400 * active_ads per hour

            return RateLimitStatus(
                platform=self.platform,
                limit=200000,  # Conservative estimate
                remaining=180000,  # Assume 10% used
                percentage_used=0.1,
            )

        except FacebookRequestError:
            return RateLimitStatus(
                platform=self.platform,
                limit=0,
                remaining=0,
                percentage_used=1.0,
            )

    def _map_objective(self, objective: CampaignObjective) -> str:
        """Map generic objective to Meta-specific objective."""
        return OBJECTIVE_MAP.get(objective, Campaign.Objective.outcome_traffic)

    def _build_targeting(self, targeting) -> dict:
        """Build Meta targeting spec from generic targeting config."""
        spec = {}

        if targeting.locations:
            spec["geo_locations"] = {
                "countries": targeting.locations,
            }

        if targeting.age_min:
            spec["age_min"] = targeting.age_min
        if targeting.age_max:
            spec["age_max"] = targeting.age_max

        if targeting.genders:
            # Meta: 1 = male, 2 = female
            gender_map = {"male": 1, "female": 2}
            spec["genders"] = [gender_map.get(g, 0) for g in targeting.genders if g in gender_map]

        if targeting.interests:
            # Would need to lookup interest IDs from Meta API
            spec["flexible_spec"] = [{"interests": targeting.interests}]

        if targeting.languages:
            spec["locales"] = targeting.languages

        return spec

    def _map_cta(self, cta: Optional[str]) -> str:
        """Map generic CTA to Meta CTA type."""
        cta_map = {
            "learn_more": "LEARN_MORE",
            "sign_up": "SIGN_UP",
            "shop_now": "SHOP_NOW",
            "book_now": "BOOK_TRAVEL",
            "download": "DOWNLOAD",
            "get_quote": "GET_QUOTE",
            "contact_us": "CONTACT_US",
        }
        return cta_map.get(cta or "", "LEARN_MORE")
