"""
Budget Pool Manager

Platform-agnostic budget tracking, allocation, and overspend prevention.
Integrates with Supabase ad_budget_pools and ad_campaigns tables.

@story US-AC05, US-AM05
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field
import httpx

from .interface import Platform


logger = logging.getLogger(__name__)


class BudgetStatus(Enum):
    """Budget pool status."""
    HEALTHY = "healthy"           # > 50% remaining
    LOW = "low"                   # 20-50% remaining
    CRITICAL = "critical"         # < 20% remaining
    EXHAUSTED = "exhausted"       # 0% remaining
    OVERSPENT = "overspent"       # Negative balance (error state)


class AllocationResult(Enum):
    """Result of budget allocation request."""
    APPROVED = "approved"
    INSUFFICIENT_FUNDS = "insufficient_funds"
    EXCEEDS_CAMPAIGN_LIMIT = "exceeds_campaign_limit"
    EXCEEDS_DAILY_LIMIT = "exceeds_daily_limit"
    POOL_EXHAUSTED = "pool_exhausted"
    USER_NOT_FOUND = "user_not_found"
    ERROR = "error"


class BudgetPool(BaseModel):
    """User's ad budget pool."""
    user_id: str
    total_allocated_cents: int = 0
    total_spent_cents: int = 0
    available_balance_cents: int = 0
    rollover_cents: int = 0
    rollover_expires_at: Optional[datetime] = None
    last_allocation_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    @property
    def status(self) -> BudgetStatus:
        """Calculate current budget status."""
        if self.total_allocated_cents == 0:
            return BudgetStatus.EXHAUSTED

        remaining_pct = self.available_balance_cents / self.total_allocated_cents

        if remaining_pct <= 0:
            return BudgetStatus.EXHAUSTED if self.available_balance_cents == 0 else BudgetStatus.OVERSPENT
        elif remaining_pct < 0.2:
            return BudgetStatus.CRITICAL
        elif remaining_pct < 0.5:
            return BudgetStatus.LOW
        else:
            return BudgetStatus.HEALTHY

    @property
    def utilization_percentage(self) -> float:
        """Calculate budget utilization percentage."""
        if self.total_allocated_cents == 0:
            return 0.0
        return (self.total_spent_cents / self.total_allocated_cents) * 100


class AllocationRequest(BaseModel):
    """Request to allocate budget for a campaign."""
    user_id: str
    project_id: str
    campaign_name: str
    platform: Platform
    requested_cents: int = Field(..., gt=0)
    daily_limit_cents: Optional[int] = None
    hypothesis_id: Optional[str] = None


class AllocationResponse(BaseModel):
    """Response from budget allocation request."""
    result: AllocationResult
    allocated_cents: int = 0
    campaign_id: Optional[str] = None
    remaining_balance_cents: int = 0
    message: str = ""


class SpendUpdate(BaseModel):
    """Record of spend against a campaign budget."""
    campaign_id: str
    platform: Platform
    spend_cents: int = Field(..., ge=0)
    timestamp: datetime = Field(default_factory=datetime.now)


class BudgetConfig(BaseModel):
    """Global budget configuration (from admin settings)."""
    allocation_percentage: int = Field(30, ge=10, le=50, description="% of subscription for ads")
    per_campaign_limit_cents: int = Field(5000, description="Max $50 per campaign")
    daily_spend_limit_cents: int = Field(2500, description="Max $25 daily across all campaigns")
    rollover_enabled: bool = True
    rollover_expires_days: int = 90
    min_statistical_sample: int = Field(100, description="Min impressions for valid results")
    auto_pause_on_exhaustion: bool = True


class BudgetPoolManager:
    """Manages ad budget pools for all users.

    Responsibilities:
    - Track budget allocation from subscriptions
    - Allocate budget to campaigns with limits
    - Record spend and update balances
    - Handle rollover of unused budget
    - Prevent overspend

    Usage:
        manager = BudgetPoolManager(supabase_url, supabase_key)

        # Check available budget
        pool = await manager.get_pool(user_id)

        # Allocate budget for campaign
        response = await manager.allocate(AllocationRequest(...))

        # Record spend
        await manager.record_spend(SpendUpdate(...))
    """

    def __init__(
        self,
        supabase_url: str,
        supabase_service_key: str,
        config: Optional[BudgetConfig] = None,
    ):
        """Initialize budget manager.

        Args:
            supabase_url: Supabase project URL.
            supabase_service_key: Supabase service role key.
            config: Budget configuration (uses defaults if not provided).
        """
        self.supabase_url = supabase_url.rstrip("/")
        self.supabase_key = supabase_service_key
        self.config = config or BudgetConfig()
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=f"{self.supabase_url}/rest/v1",
                headers={
                    "apikey": self.supabase_key,
                    "Authorization": f"Bearer {self.supabase_key}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation",
                },
                timeout=30.0,
            )
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def get_pool(self, user_id: str) -> Optional[BudgetPool]:
        """Get user's budget pool.

        Args:
            user_id: User UUID.

        Returns:
            BudgetPool if exists, None otherwise.
        """
        client = await self._get_client()

        response = await client.get(
            "/ad_budget_pools",
            params={"user_id": f"eq.{user_id}", "select": "*"},
        )

        if response.status_code != 200:
            logger.error(f"Failed to get budget pool: {response.text}")
            return None

        data = response.json()
        if not data:
            return None

        row = data[0]
        return BudgetPool(
            user_id=row["user_id"],
            total_allocated_cents=int(Decimal(str(row["total_allocated"])) * 100),
            total_spent_cents=int(Decimal(str(row["total_spent"])) * 100),
            available_balance_cents=int(Decimal(str(row["available_balance"])) * 100),
            rollover_cents=int(Decimal(str(row.get("rollover_amount", 0) or 0)) * 100),
            rollover_expires_at=row.get("rollover_expires_at"),
            last_allocation_at=row.get("last_allocation_at"),
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00")),
        )

    async def create_pool(self, user_id: str, initial_allocation_cents: int = 0) -> BudgetPool:
        """Create a new budget pool for a user.

        Args:
            user_id: User UUID.
            initial_allocation_cents: Initial budget allocation in cents.

        Returns:
            Created BudgetPool.
        """
        client = await self._get_client()

        response = await client.post(
            "/ad_budget_pools",
            json={
                "user_id": user_id,
                "total_allocated": initial_allocation_cents / 100,
                "total_spent": 0,
            },
        )

        if response.status_code not in (200, 201):
            raise RuntimeError(f"Failed to create budget pool: {response.text}")

        row = response.json()[0]
        return BudgetPool(
            user_id=row["user_id"],
            total_allocated_cents=int(Decimal(str(row["total_allocated"])) * 100),
            total_spent_cents=int(Decimal(str(row["total_spent"])) * 100),
            available_balance_cents=int(Decimal(str(row["available_balance"])) * 100),
            rollover_cents=0,
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00")),
        )

    async def add_allocation(self, user_id: str, amount_cents: int) -> bool:
        """Add budget allocation to user's pool (e.g., from subscription).

        Args:
            user_id: User UUID.
            amount_cents: Amount to add in cents.

        Returns:
            True if successful.
        """
        pool = await self.get_pool(user_id)

        if pool is None:
            # Create new pool with allocation
            await self.create_pool(user_id, amount_cents)
            return True

        client = await self._get_client()

        new_total = pool.total_allocated_cents + amount_cents

        response = await client.patch(
            "/ad_budget_pools",
            params={"user_id": f"eq.{user_id}"},
            json={
                "total_allocated": new_total / 100,
                "updated_at": datetime.now().isoformat(),
            },
        )

        return response.status_code == 200

    async def allocate(self, request: AllocationRequest) -> AllocationResponse:
        """Allocate budget for a new campaign.

        Checks:
        1. User has a budget pool
        2. Sufficient balance available
        3. Request doesn't exceed per-campaign limit
        4. Request doesn't exceed daily limit (if set)

        Args:
            request: Allocation request details.

        Returns:
            AllocationResponse with result and details.
        """
        # Get user's pool
        pool = await self.get_pool(request.user_id)

        if pool is None:
            return AllocationResponse(
                result=AllocationResult.USER_NOT_FOUND,
                message=f"No budget pool found for user {request.user_id}",
            )

        # Check pool status
        if pool.status == BudgetStatus.EXHAUSTED:
            return AllocationResponse(
                result=AllocationResult.POOL_EXHAUSTED,
                remaining_balance_cents=0,
                message="Budget pool is exhausted. Renew subscription for more ad budget.",
            )

        # Check per-campaign limit
        if request.requested_cents > self.config.per_campaign_limit_cents:
            return AllocationResponse(
                result=AllocationResult.EXCEEDS_CAMPAIGN_LIMIT,
                remaining_balance_cents=pool.available_balance_cents,
                message=f"Requested ${request.requested_cents/100:.2f} exceeds campaign limit of ${self.config.per_campaign_limit_cents/100:.2f}",
            )

        # Check available balance
        if request.requested_cents > pool.available_balance_cents:
            return AllocationResponse(
                result=AllocationResult.INSUFFICIENT_FUNDS,
                remaining_balance_cents=pool.available_balance_cents,
                message=f"Insufficient funds. Available: ${pool.available_balance_cents/100:.2f}, Requested: ${request.requested_cents/100:.2f}",
            )

        # Check daily limit
        if request.daily_limit_cents and request.daily_limit_cents > self.config.daily_spend_limit_cents:
            return AllocationResponse(
                result=AllocationResult.EXCEEDS_DAILY_LIMIT,
                remaining_balance_cents=pool.available_balance_cents,
                message=f"Daily limit ${request.daily_limit_cents/100:.2f} exceeds max ${self.config.daily_spend_limit_cents/100:.2f}",
            )

        # Create campaign record
        client = await self._get_client()

        campaign_response = await client.post(
            "/ad_campaigns",
            json={
                "user_id": request.user_id,
                "project_id": request.project_id,
                "hypothesis_id": request.hypothesis_id,
                "platform": request.platform.value,
                "status": "draft",
                "budget_allocated": request.requested_cents / 100,
                "budget_spent": 0,
                "creative_data": {"name": request.campaign_name},
            },
        )

        if campaign_response.status_code not in (200, 201):
            logger.error(f"Failed to create campaign: {campaign_response.text}")
            return AllocationResponse(
                result=AllocationResult.ERROR,
                remaining_balance_cents=pool.available_balance_cents,
                message="Failed to create campaign record",
            )

        campaign_data = campaign_response.json()[0]
        campaign_id = campaign_data["id"]

        logger.info(
            f"Allocated ${request.requested_cents/100:.2f} for campaign {campaign_id} "
            f"on {request.platform.value} for user {request.user_id}"
        )

        return AllocationResponse(
            result=AllocationResult.APPROVED,
            allocated_cents=request.requested_cents,
            campaign_id=campaign_id,
            remaining_balance_cents=pool.available_balance_cents - request.requested_cents,
            message=f"Allocated ${request.requested_cents/100:.2f} for {request.campaign_name}",
        )

    async def record_spend(self, update: SpendUpdate) -> bool:
        """Record spend against a campaign.

        Updates both the campaign's budget_spent and the user's pool total_spent.

        Args:
            update: Spend update details.

        Returns:
            True if successful.
        """
        client = await self._get_client()

        # Get campaign to find user and current spend
        campaign_response = await client.get(
            "/ad_campaigns",
            params={"id": f"eq.{update.campaign_id}", "select": "*"},
        )

        if campaign_response.status_code != 200 or not campaign_response.json():
            logger.error(f"Campaign not found: {update.campaign_id}")
            return False

        campaign = campaign_response.json()[0]
        user_id = campaign["user_id"]
        current_spend = int(Decimal(str(campaign["budget_spent"])) * 100)
        new_spend = current_spend + update.spend_cents

        # Update campaign spend
        await client.patch(
            "/ad_campaigns",
            params={"id": f"eq.{update.campaign_id}"},
            json={
                "budget_spent": new_spend / 100,
                "updated_at": datetime.now().isoformat(),
            },
        )

        # Update pool total spent
        pool = await self.get_pool(user_id)
        if pool:
            new_pool_spent = pool.total_spent_cents + update.spend_cents
            await client.patch(
                "/ad_budget_pools",
                params={"user_id": f"eq.{user_id}"},
                json={
                    "total_spent": new_pool_spent / 100,
                    "updated_at": datetime.now().isoformat(),
                },
            )

            # Check if auto-pause needed
            if self.config.auto_pause_on_exhaustion:
                remaining = pool.total_allocated_cents - new_pool_spent
                if remaining <= 0:
                    logger.warning(f"Budget exhausted for user {user_id}, auto-pausing campaigns")
                    # This would trigger pause across all active campaigns
                    # Implementation depends on campaign orchestration

        logger.info(
            f"Recorded ${update.spend_cents/100:.2f} spend for campaign {update.campaign_id}"
        )

        return True

    async def get_daily_spend(self, user_id: str, date: Optional[str] = None) -> int:
        """Get total spend for a user on a specific date.

        Args:
            user_id: User UUID.
            date: Date string (YYYY-MM-DD), defaults to today.

        Returns:
            Total spend in cents for the date.
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        client = await self._get_client()

        # Query performance snapshots for the date
        response = await client.get(
            "/ad_performance_snapshots",
            params={
                "select": "spend,campaign_id,ad_campaigns!inner(user_id)",
                "ad_campaigns.user_id": f"eq.{user_id}",
                "snapshot_at": f"gte.{date}T00:00:00",
            },
        )

        if response.status_code != 200:
            return 0

        data = response.json()
        total = sum(int(Decimal(str(row.get("spend", 0))) * 100) for row in data)

        return total

    async def check_daily_limit(self, user_id: str, additional_cents: int = 0) -> bool:
        """Check if user is within daily spend limit.

        Args:
            user_id: User UUID.
            additional_cents: Additional spend to check.

        Returns:
            True if within limit, False if would exceed.
        """
        daily_spend = await self.get_daily_spend(user_id)
        return (daily_spend + additional_cents) <= self.config.daily_spend_limit_cents

    async def process_rollover(self, user_id: str) -> int:
        """Process rollover of unused budget from previous period.

        Called when subscription renews.

        Args:
            user_id: User UUID.

        Returns:
            Amount rolled over in cents.
        """
        if not self.config.rollover_enabled:
            return 0

        pool = await self.get_pool(user_id)
        if pool is None:
            return 0

        rollover_amount = pool.available_balance_cents
        if rollover_amount <= 0:
            return 0

        client = await self._get_client()

        # Calculate expiry date
        from datetime import timedelta
        expires_at = datetime.now() + timedelta(days=self.config.rollover_expires_days)

        await client.patch(
            "/ad_budget_pools",
            params={"user_id": f"eq.{user_id}"},
            json={
                "rollover_amount": rollover_amount / 100,
                "rollover_expires_at": expires_at.isoformat(),
                "updated_at": datetime.now().isoformat(),
            },
        )

        logger.info(
            f"Rolled over ${rollover_amount/100:.2f} for user {user_id}, "
            f"expires {expires_at.strftime('%Y-%m-%d')}"
        )

        return rollover_amount
