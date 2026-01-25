"""
Google Ads Adapter

Implements AdPlatformAdapter for Google Ads API using the
official google-ads Python client library.

Key features:
- OAuth 2.0 + Developer Token authentication
- Access tier detection (Test/Basic/Standard)
- Campaign, Ad Group, and Ad creation
- Performance metrics retrieval
- MCC (Manager Account) support

@story US-AC01, US-AC02, US-AC03
"""

import logging
from datetime import datetime
from typing import Optional

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.protobuf import field_mask_pb2

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


# Map generic objectives to Google Ads campaign types and bidding strategies
OBJECTIVE_MAP = {
    CampaignObjective.AWARENESS: ("DISPLAY", "TARGET_CPM"),
    CampaignObjective.TRAFFIC: ("SEARCH", "TARGET_CPC"),
    CampaignObjective.CONVERSIONS: ("SEARCH", "TARGET_CPA"),
    CampaignObjective.APP_INSTALLS: ("APP", "TARGET_CPA"),
    CampaignObjective.VIDEO_VIEWS: ("VIDEO", "TARGET_CPV"),
    CampaignObjective.LEAD_GENERATION: ("SEARCH", "TARGET_CPA"),
    CampaignObjective.ENGAGEMENT: ("DISPLAY", "TARGET_CPC"),
    CampaignObjective.REACH: ("DISPLAY", "TARGET_CPM"),
}

# Map Google Ads status to generic status
STATUS_MAP = {
    "ENABLED": CampaignStatus.ACTIVE,
    "PAUSED": CampaignStatus.PAUSED,
    "REMOVED": CampaignStatus.COMPLETED,
    "UNKNOWN": CampaignStatus.ERROR,
    "UNSPECIFIED": CampaignStatus.ERROR,
}


class GoogleAccessTier:
    """Google Ads API access tiers."""
    TEST = "test"           # 15,000 operations/day
    BASIC = "basic"         # 1,500 operations/day (per-customer)
    STANDARD = "standard"   # Higher limits


class GoogleAdsAdapter(AdPlatformAdapter):
    """Google Ads adapter.

    Authentication:
        Uses OAuth 2.0 with a Developer Token.
        - OAuth credentials (client_id, client_secret, refresh_token)
        - Developer Token (22-character string from Google Ads UI)
        - Customer ID (format: 123-456-7890)

    Access Tiers:
        - Test: 15,000 operations/day (test accounts only)
        - Basic: 1,500 operations/day per customer
        - Standard: Higher limits (requires approval)

    Required credentials:
        - developer_token: 22-char developer token
        - client_id: OAuth client ID
        - client_secret: OAuth client secret
        - refresh_token: OAuth refresh token
        - customer_id: Google Ads customer ID (123-456-7890)
        - login_customer_id: MCC customer ID (optional, for agency access)

    Usage:
        adapter = GoogleAdsAdapter({
            "developer_token": "xxx...",
            "client_id": "123...apps.googleusercontent.com",
            "client_secret": "...",
            "refresh_token": "1//...",
            "customer_id": "123-456-7890",
        })

        result = await adapter.create_campaign(config)
    """

    platform = Platform.GOOGLE
    auth_type = AuthType.OAUTH2
    token_lifetime_days = None  # Refresh tokens don't expire

    def __init__(self, credentials: dict[str, str]):
        """Initialize Google Ads adapter."""
        super().__init__(credentials)

        # Normalize customer ID (remove hyphens)
        self.customer_id = credentials["customer_id"].replace("-", "")
        self.login_customer_id = credentials.get("login_customer_id", "").replace("-", "") or None

        # Build google-ads client configuration
        self._config = {
            "developer_token": credentials["developer_token"],
            "client_id": credentials["client_id"],
            "client_secret": credentials["client_secret"],
            "refresh_token": credentials["refresh_token"],
            "use_proto_plus": True,
        }

        if self.login_customer_id:
            self._config["login_customer_id"] = self.login_customer_id

        # Initialize client
        self.client = GoogleAdsClient.load_from_dict(self._config)

        # Track access tier
        self._access_tier: Optional[str] = None

    def _validate_credentials(self) -> None:
        """Validate required credentials are present."""
        required = ["developer_token", "client_id", "client_secret", "refresh_token", "customer_id"]
        missing = [k for k in required if not self.credentials.get(k)]
        if missing:
            raise ValueError(f"Missing required credentials: {', '.join(missing)}")

        # Validate developer token format (22 chars)
        if len(self.credentials["developer_token"]) != 22:
            logger.warning("Developer token should be 22 characters")

    async def validate_credentials(self) -> bool:
        """Verify credentials are valid and have ad management permissions."""
        try:
            ga_service = self.client.get_service("GoogleAdsService")

            # Simple query to verify access
            query = """
                SELECT customer.id, customer.descriptive_name, customer.test_account
                FROM customer
                LIMIT 1
            """

            response = ga_service.search(customer_id=self.customer_id, query=query)

            for row in response:
                is_test = row.customer.test_account
                self._access_tier = GoogleAccessTier.TEST if is_test else GoogleAccessTier.BASIC
                logger.info(
                    f"Google Ads credentials valid for: {row.customer.descriptive_name} "
                    f"(tier: {self._access_tier})"
                )
                return True

            return False

        except GoogleAdsException as e:
            logger.error(f"Google Ads credential validation failed: {e.failure.errors[0].message}")
            return False

    async def get_token_status(self) -> TokenStatus:
        """Check token health and expiry.

        Google refresh tokens don't expire unless revoked.
        """
        try:
            # Validate by making a simple API call
            valid = await self.validate_credentials()

            return TokenStatus(
                platform=self.platform,
                valid=valid,
                expires_at=None,  # Refresh tokens don't expire
                days_until_expiry=None,
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

        Google uses refresh tokens that don't expire.
        The client library handles token refresh automatically.
        """
        # Google Ads client handles refresh automatically
        return True

    async def create_campaign(self, config: CampaignConfig) -> CampaignResult:
        """Create a new ad campaign on Google Ads.

        Creates:
        1. Campaign with budget and bidding strategy
        2. Ad Group with targeting
        3. Ad with creative
        """
        try:
            # Get services
            campaign_service = self.client.get_service("CampaignService")
            campaign_budget_service = self.client.get_service("CampaignBudgetService")
            ad_group_service = self.client.get_service("AdGroupService")
            ad_group_ad_service = self.client.get_service("AdGroupAdService")

            # 1. Create Campaign Budget
            budget_operation = self.client.get_type("CampaignBudgetOperation")
            budget = budget_operation.create
            budget.name = f"{config.name} Budget"

            # Set budget (micros = cents * 10000)
            if config.daily_budget_cents:
                budget.amount_micros = config.daily_budget_cents * 10000
                budget.delivery_method = self.client.enums.BudgetDeliveryMethodEnum.STANDARD
            else:
                # Use lifetime budget distributed over campaign duration
                budget.amount_micros = config.budget_cents * 10000
                budget.delivery_method = self.client.enums.BudgetDeliveryMethodEnum.STANDARD

            budget_response = campaign_budget_service.mutate_campaign_budgets(
                customer_id=self.customer_id,
                operations=[budget_operation],
            )
            budget_resource_name = budget_response.results[0].resource_name
            logger.info(f"Created Google Ads budget: {budget_resource_name}")

            # 2. Create Campaign
            campaign_type, bidding_strategy = OBJECTIVE_MAP.get(
                config.objective,
                ("SEARCH", "TARGET_CPC"),
            )

            campaign_operation = self.client.get_type("CampaignOperation")
            campaign = campaign_operation.create
            campaign.name = config.name
            campaign.campaign_budget = budget_resource_name
            campaign.status = self.client.enums.CampaignStatusEnum.PAUSED

            # Set campaign type
            campaign.advertising_channel_type = getattr(
                self.client.enums.AdvertisingChannelTypeEnum,
                campaign_type,
            )

            # Set bidding strategy
            if bidding_strategy == "TARGET_CPC":
                campaign.manual_cpc.enhanced_cpc_enabled = True
            elif bidding_strategy == "TARGET_CPA":
                campaign.target_cpa.target_cpa_micros = 1000000  # $1 target CPA

            # Set dates
            campaign.start_date = config.start_date.replace("-", "")
            if config.end_date:
                campaign.end_date = config.end_date.replace("-", "")

            # Set network settings for Search campaigns
            if campaign_type == "SEARCH":
                campaign.network_settings.target_google_search = True
                campaign.network_settings.target_search_network = True
                campaign.network_settings.target_content_network = False

            campaign_response = campaign_service.mutate_campaigns(
                customer_id=self.customer_id,
                operations=[campaign_operation],
            )
            campaign_resource_name = campaign_response.results[0].resource_name
            campaign_id = campaign_resource_name.split("/")[-1]
            logger.info(f"Created Google Ads campaign: {campaign_id}")

            # 3. Create Ad Group
            ad_group_operation = self.client.get_type("AdGroupOperation")
            ad_group = ad_group_operation.create
            ad_group.name = f"{config.name} - Ad Group"
            ad_group.campaign = campaign_resource_name
            ad_group.status = self.client.enums.AdGroupStatusEnum.PAUSED
            ad_group.type_ = self.client.enums.AdGroupTypeEnum.SEARCH_STANDARD

            # Set CPC bid
            ad_group.cpc_bid_micros = 100000  # $0.10 default bid

            ad_group_response = ad_group_service.mutate_ad_groups(
                customer_id=self.customer_id,
                operations=[ad_group_operation],
            )
            ad_group_resource_name = ad_group_response.results[0].resource_name
            ad_group_id = ad_group_resource_name.split("/")[-1]
            logger.info(f"Created Google Ads ad group: {ad_group_id}")

            # 4. Create Responsive Search Ad
            ad_group_ad_operation = self.client.get_type("AdGroupAdOperation")
            ad_group_ad = ad_group_ad_operation.create
            ad_group_ad.ad_group = ad_group_resource_name
            ad_group_ad.status = self.client.enums.AdGroupAdStatusEnum.PAUSED

            # Create responsive search ad
            ad = ad_group_ad.ad
            ad.final_urls.append(config.creative.landing_url)

            if config.creative.display_url:
                ad.display_url = config.creative.display_url

            # Add headlines (max 15, need at least 3)
            headline = ad.responsive_search_ad.headlines.add()
            headline.text = config.creative.headline[:30]  # Max 30 chars

            # Add more headlines if we have body text
            if config.creative.body:
                words = config.creative.body.split()
                for i in range(2):  # Add 2 more headlines
                    if words:
                        text = " ".join(words[:4])[:30]
                        words = words[4:]
                        h = ad.responsive_search_ad.headlines.add()
                        h.text = text

            # Add descriptions (max 4, need at least 2)
            if config.creative.body:
                desc = ad.responsive_search_ad.descriptions.add()
                desc.text = config.creative.body[:90]  # Max 90 chars

                # Add second description
                desc2 = ad.responsive_search_ad.descriptions.add()
                desc2.text = f"Learn more at {config.creative.landing_url}"[:90]

            ad_response = ad_group_ad_service.mutate_ad_group_ads(
                customer_id=self.customer_id,
                operations=[ad_group_ad_operation],
            )
            ad_resource_name = ad_response.results[0].resource_name
            ad_id = ad_resource_name.split("/")[-1]
            logger.info(f"Created Google Ads ad: {ad_id}")

            return CampaignResult(
                platform=self.platform,
                platform_campaign_id=campaign_id,
                platform_ad_set_id=ad_group_id,
                platform_ad_id=ad_id,
                status=CampaignStatus.DRAFT,
                created_at=datetime.now(),
            )

        except GoogleAdsException as e:
            error_msg = e.failure.errors[0].message if e.failure.errors else str(e)
            logger.error(f"Google Ads campaign creation failed: {error_msg}")
            return CampaignResult(
                platform=self.platform,
                platform_campaign_id="",
                status=CampaignStatus.ERROR,
                created_at=datetime.now(),
                error_message=error_msg,
            )

    async def pause_campaign(self, campaign_id: str) -> bool:
        """Pause an active campaign."""
        try:
            campaign_service = self.client.get_service("CampaignService")

            operation = self.client.get_type("CampaignOperation")
            campaign = operation.update
            campaign.resource_name = f"customers/{self.customer_id}/campaigns/{campaign_id}"
            campaign.status = self.client.enums.CampaignStatusEnum.PAUSED

            operation.update_mask = field_mask_pb2.FieldMask(paths=["status"])

            campaign_service.mutate_campaigns(
                customer_id=self.customer_id,
                operations=[operation],
            )

            logger.info(f"Paused Google Ads campaign: {campaign_id}")
            return True

        except GoogleAdsException as e:
            logger.error(f"Failed to pause campaign: {e.failure.errors[0].message}")
            return False

    async def resume_campaign(self, campaign_id: str) -> bool:
        """Resume a paused campaign."""
        try:
            campaign_service = self.client.get_service("CampaignService")

            operation = self.client.get_type("CampaignOperation")
            campaign = operation.update
            campaign.resource_name = f"customers/{self.customer_id}/campaigns/{campaign_id}"
            campaign.status = self.client.enums.CampaignStatusEnum.ENABLED

            operation.update_mask = field_mask_pb2.FieldMask(paths=["status"])

            campaign_service.mutate_campaigns(
                customer_id=self.customer_id,
                operations=[operation],
            )

            logger.info(f"Resumed Google Ads campaign: {campaign_id}")
            return True

        except GoogleAdsException as e:
            logger.error(f"Failed to resume campaign: {e.failure.errors[0].message}")
            return False

    async def get_campaign_status(self, campaign_id: str) -> CampaignStatus:
        """Get current status of a campaign."""
        try:
            ga_service = self.client.get_service("GoogleAdsService")

            query = f"""
                SELECT campaign.status
                FROM campaign
                WHERE campaign.id = {campaign_id}
            """

            response = ga_service.search(customer_id=self.customer_id, query=query)

            for row in response:
                status_name = row.campaign.status.name
                return STATUS_MAP.get(status_name, CampaignStatus.ERROR)

            return CampaignStatus.ERROR

        except GoogleAdsException:
            return CampaignStatus.ERROR

    async def get_performance(
        self,
        campaign_id: str,
        start_date: str,
        end_date: str,
    ) -> PerformanceMetrics:
        """Fetch performance metrics for a campaign."""
        try:
            ga_service = self.client.get_service("GoogleAdsService")

            query = f"""
                SELECT
                    campaign.id,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.conversions,
                    metrics.cost_micros,
                    metrics.ctr,
                    metrics.average_cpc,
                    metrics.average_cpm
                FROM campaign
                WHERE campaign.id = {campaign_id}
                    AND segments.date BETWEEN '{start_date}' AND '{end_date}'
            """

            response = ga_service.search(customer_id=self.customer_id, query=query)

            # Aggregate metrics
            total_impressions = 0
            total_clicks = 0
            total_conversions = 0
            total_cost_micros = 0

            for row in response:
                total_impressions += row.metrics.impressions
                total_clicks += row.metrics.clicks
                total_conversions += int(row.metrics.conversions)
                total_cost_micros += row.metrics.cost_micros

            metrics = PerformanceMetrics(
                campaign_id=campaign_id,
                platform=self.platform,
                date_start=start_date,
                date_end=end_date,
                impressions=total_impressions,
                clicks=total_clicks,
                conversions=total_conversions,
                spend_cents=total_cost_micros // 10000,  # micros to cents
            )

            metrics.calculate_derived_metrics()
            return metrics

        except GoogleAdsException as e:
            logger.error(f"Failed to get performance: {e.failure.errors[0].message}")
            return PerformanceMetrics(
                campaign_id=campaign_id,
                platform=self.platform,
                date_start=start_date,
                date_end=end_date,
            )

    async def get_rate_limit_status(self) -> RateLimitStatus:
        """Check current rate limit status.

        Google Ads uses per-customer daily limits based on access tier.
        """
        # Limits based on access tier
        tier_limits = {
            GoogleAccessTier.TEST: 15000,
            GoogleAccessTier.BASIC: 1500,
            GoogleAccessTier.STANDARD: 100000,
        }

        tier = self._access_tier or GoogleAccessTier.BASIC
        limit = tier_limits.get(tier, 1500)

        # Google doesn't expose current usage, estimate conservatively
        return RateLimitStatus(
            platform=self.platform,
            limit=limit,
            remaining=int(limit * 0.9),  # Assume 10% used
            percentage_used=0.1,
        )

    def get_access_tier(self) -> str:
        """Get current API access tier."""
        return self._access_tier or GoogleAccessTier.BASIC
