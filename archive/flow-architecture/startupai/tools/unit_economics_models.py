"""
Unit Economics Models for Business Model-Specific Viability.

Implements a hierarchy of models for different business types:
SaaS (B2B/B2C), E-commerce (DTC/Marketplace), Fintech, Consulting.

Area 7 Implementation: Phase 2 & 3 Depth - Business Model-Specific Viability
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, Tuple
from datetime import datetime

from pydantic import BaseModel, Field

from startupai.flows.state_schemas import (
    BusinessModelType,
    ViabilityMetrics,
)
from startupai.models.tool_contracts import ToolResult


# =======================================================================================
# DATA MODELS
# =======================================================================================

class UnitEconomicsInput(BaseModel):
    """Input data for unit economics calculation."""
    # Revenue metrics
    average_order_value: Optional[float] = None
    monthly_recurring_revenue: Optional[float] = None
    average_contract_value: Optional[float] = None
    transactions_per_customer_per_year: Optional[float] = None

    # Cost metrics
    cost_of_goods_sold_pct: Optional[float] = None
    marketing_spend_usd: Optional[float] = None
    new_customers: Optional[int] = None
    sales_cycle_days: Optional[int] = None

    # Retention metrics
    monthly_churn_pct: Optional[float] = None
    annual_churn_pct: Optional[float] = None
    customer_lifespan_months: Optional[float] = None

    # Platform-specific (marketplaces)
    take_rate_pct: Optional[float] = None
    gmv_usd: Optional[float] = None

    # Fintech-specific
    default_rate_pct: Optional[float] = None
    net_interest_margin_pct: Optional[float] = None


class BenchmarkData(BaseModel):
    """Industry benchmark data for comparison."""
    healthy_ltv_cac_ratio: float = 3.0
    healthy_gross_margin_pct: float = 60.0
    healthy_payback_months: float = 12.0
    source: str = "industry_standard"
    last_updated: datetime = Field(default_factory=datetime.now)


# =======================================================================================
# BASE MODEL CLASS
# =======================================================================================

class UnitEconomicsModel(ABC):
    """
    Abstract base class for unit economics calculations.

    Each business model type has different formulas for CAC, LTV,
    and viability assessment.
    """

    model_type: BusinessModelType
    benchmarks: BenchmarkData

    def __init__(self, benchmarks: Optional[BenchmarkData] = None):
        """Initialize with optional custom benchmarks."""
        self.benchmarks = benchmarks or self._default_benchmarks()

    @abstractmethod
    def _default_benchmarks(self) -> BenchmarkData:
        """Return default benchmarks for this model type."""
        pass

    @abstractmethod
    def calculate_cac(self, inputs: UnitEconomicsInput) -> Tuple[float, Dict[str, float]]:
        """
        Calculate Customer Acquisition Cost.

        Returns:
            Tuple of (cac_value, breakdown_dict)
        """
        pass

    @abstractmethod
    def calculate_ltv(self, inputs: UnitEconomicsInput) -> Tuple[float, Dict[str, float]]:
        """
        Calculate Lifetime Value.

        Returns:
            Tuple of (ltv_value, breakdown_dict)
        """
        pass

    @abstractmethod
    def calculate_gross_margin(self, inputs: UnitEconomicsInput) -> float:
        """Calculate gross margin percentage."""
        pass

    def calculate_metrics(self, inputs: UnitEconomicsInput) -> ToolResult[ViabilityMetrics]:
        """
        Calculate all unit economics metrics.

        Returns:
            ToolResult containing ViabilityMetrics
        """
        try:
            # Calculate core metrics
            cac, cac_breakdown = self.calculate_cac(inputs)
            ltv, ltv_breakdown = self.calculate_ltv(inputs)
            gross_margin = self.calculate_gross_margin(inputs)

            # Derived metrics
            ltv_cac_ratio = ltv / cac if cac > 0 else 0.0
            payback_months = self._calculate_payback(inputs, cac)

            # Monthly churn (normalize from annual if needed)
            monthly_churn = inputs.monthly_churn_pct or (
                (inputs.annual_churn_pct / 12) if inputs.annual_churn_pct else 0.0
            )

            metrics = ViabilityMetrics(
                cac_usd=cac,
                ltv_usd=ltv,
                ltv_cac_ratio=ltv_cac_ratio,
                gross_margin_pct=gross_margin,
                monthly_churn_pct=monthly_churn,
                payback_months=payback_months,
                cac_breakdown=cac_breakdown,
                ltv_breakdown=ltv_breakdown,
                business_model_type=self.model_type,
                model_assumptions=self._get_model_assumptions(inputs),
                benchmark_source=self.benchmarks.source,
            )

            return ToolResult.success(
                data=metrics,
                model_type=self.model_type.value,
            )

        except Exception as e:
            return ToolResult.failure(
                message=f"Metrics calculation failed: {str(e)}",
                code="METRICS_CALCULATION_ERROR",
            )

    def _calculate_payback(self, inputs: UnitEconomicsInput, cac: float) -> float:
        """Calculate payback period in months."""
        # Default implementation - subclasses may override
        if inputs.monthly_recurring_revenue and inputs.monthly_recurring_revenue > 0:
            gross_margin = self.calculate_gross_margin(inputs) / 100
            monthly_contribution = inputs.monthly_recurring_revenue * gross_margin
            return cac / monthly_contribution if monthly_contribution > 0 else 0.0
        return 0.0

    def _get_model_assumptions(self, inputs: UnitEconomicsInput) -> Dict[str, Any]:
        """Get the assumptions used in calculations."""
        return {
            'model_type': self.model_type.value,
            'benchmarks': {
                'healthy_ltv_cac': self.benchmarks.healthy_ltv_cac_ratio,
                'healthy_gross_margin': self.benchmarks.healthy_gross_margin_pct,
                'healthy_payback_months': self.benchmarks.healthy_payback_months,
            },
        }

    def assess_viability(self, metrics: ViabilityMetrics) -> str:
        """
        Assess viability signal based on metrics.

        Returns:
            Signal: 'profitable', 'underwater', 'zombie_market', 'unknown'
        """
        if metrics.ltv_cac_ratio >= self.benchmarks.healthy_ltv_cac_ratio:
            if metrics.gross_margin_pct >= self.benchmarks.healthy_gross_margin_pct:
                return 'profitable'
            else:
                return 'zombie_market'  # Good acquisition but poor unit economics
        elif metrics.ltv_cac_ratio > 1.0:
            return 'underwater'  # Losing money but may be recoverable
        else:
            return 'unknown' if metrics.ltv_cac_ratio == 0 else 'underwater'


# =======================================================================================
# SAAS MODELS
# =======================================================================================

class SaaSB2BSMBModel(UnitEconomicsModel):
    """Unit economics for SaaS B2B SMB businesses."""

    model_type = BusinessModelType.SAAS_B2B_SMB

    def _default_benchmarks(self) -> BenchmarkData:
        return BenchmarkData(
            healthy_ltv_cac_ratio=3.0,
            healthy_gross_margin_pct=70.0,
            healthy_payback_months=12.0,
            source="saas_b2b_smb_benchmarks",
        )

    def calculate_cac(self, inputs: UnitEconomicsInput) -> Tuple[float, Dict[str, float]]:
        """SMB CAC: Marketing spend / new customers (lower touch sales)."""
        if inputs.new_customers and inputs.new_customers > 0:
            marketing_cac = (inputs.marketing_spend_usd or 0) / inputs.new_customers
            # SMB has minimal sales cost
            sales_cac = marketing_cac * 0.2  # 20% of marketing for light sales touch
            total_cac = marketing_cac + sales_cac
            return total_cac, {
                'marketing': marketing_cac,
                'sales': sales_cac,
            }
        return 0.0, {}

    def calculate_ltv(self, inputs: UnitEconomicsInput) -> Tuple[float, Dict[str, float]]:
        """SMB LTV: MRR * Gross Margin * Customer Lifespan."""
        mrr = inputs.monthly_recurring_revenue or 0
        gross_margin = (100 - (inputs.cost_of_goods_sold_pct or 30)) / 100
        lifespan = inputs.customer_lifespan_months or (
            1 / (inputs.monthly_churn_pct / 100) if inputs.monthly_churn_pct else 24
        )
        ltv = mrr * gross_margin * lifespan
        return ltv, {
            'monthly_contribution': mrr * gross_margin,
            'lifespan_months': lifespan,
        }

    def calculate_gross_margin(self, inputs: UnitEconomicsInput) -> float:
        """Standard SaaS gross margin calculation."""
        cogs = inputs.cost_of_goods_sold_pct or 30.0  # Default 30% for SaaS
        return 100 - cogs


class SaaSB2BMidMarketModel(UnitEconomicsModel):
    """Unit economics for SaaS B2B Mid-Market businesses."""

    model_type = BusinessModelType.SAAS_B2B_MIDMARKET

    def _default_benchmarks(self) -> BenchmarkData:
        return BenchmarkData(
            healthy_ltv_cac_ratio=4.0,  # Higher bar for mid-market
            healthy_gross_margin_pct=75.0,
            healthy_payback_months=18.0,  # Longer allowed
            source="saas_b2b_midmarket_benchmarks",
        )

    def calculate_cac(self, inputs: UnitEconomicsInput) -> Tuple[float, Dict[str, float]]:
        """Mid-market CAC: Higher sales cost, longer cycle."""
        if inputs.new_customers and inputs.new_customers > 0:
            marketing_cac = (inputs.marketing_spend_usd or 0) / inputs.new_customers
            # Mid-market has significant sales involvement
            sales_cac = marketing_cac * 0.8  # 80% of marketing for sales
            cycle_cost = (inputs.sales_cycle_days or 45) * 50  # $50/day sales cost assumption
            total_cac = marketing_cac + sales_cac + cycle_cost
            return total_cac, {
                'marketing': marketing_cac,
                'sales': sales_cac,
                'sales_cycle_cost': cycle_cost,
            }
        return 0.0, {}

    def calculate_ltv(self, inputs: UnitEconomicsInput) -> Tuple[float, Dict[str, float]]:
        """Mid-market LTV with expansion revenue assumption."""
        mrr = inputs.monthly_recurring_revenue or 0
        gross_margin = (100 - (inputs.cost_of_goods_sold_pct or 25)) / 100
        lifespan = inputs.customer_lifespan_months or (
            1 / (inputs.monthly_churn_pct / 100) if inputs.monthly_churn_pct else 36
        )
        # Assume 20% annual expansion for mid-market
        expansion_factor = 1.2
        ltv = mrr * gross_margin * lifespan * expansion_factor
        return ltv, {
            'monthly_contribution': mrr * gross_margin,
            'lifespan_months': lifespan,
            'expansion_factor': expansion_factor,
        }

    def calculate_gross_margin(self, inputs: UnitEconomicsInput) -> float:
        cogs = inputs.cost_of_goods_sold_pct or 25.0
        return 100 - cogs


class SaaSB2BEnterpriseModel(UnitEconomicsModel):
    """Unit economics for SaaS B2B Enterprise businesses."""

    model_type = BusinessModelType.SAAS_B2B_ENTERPRISE

    def _default_benchmarks(self) -> BenchmarkData:
        return BenchmarkData(
            healthy_ltv_cac_ratio=5.0,  # Highest bar
            healthy_gross_margin_pct=80.0,
            healthy_payback_months=24.0,  # Longer acceptable
            source="saas_b2b_enterprise_benchmarks",
        )

    def calculate_cac(self, inputs: UnitEconomicsInput) -> Tuple[float, Dict[str, float]]:
        """Enterprise CAC: High-touch sales, long cycle, POC costs."""
        if inputs.new_customers and inputs.new_customers > 0:
            marketing_cac = (inputs.marketing_spend_usd or 0) / inputs.new_customers
            # Enterprise is sales-led
            sales_cac = marketing_cac * 2.0  # 2x marketing for enterprise sales
            cycle_cost = (inputs.sales_cycle_days or 90) * 100  # $100/day sales cost
            poc_cost = 5000  # POC/pilot cost assumption
            total_cac = marketing_cac + sales_cac + cycle_cost + poc_cost
            return total_cac, {
                'marketing': marketing_cac,
                'sales': sales_cac,
                'sales_cycle_cost': cycle_cost,
                'poc_cost': poc_cost,
            }
        return 0.0, {}

    def calculate_ltv(self, inputs: UnitEconomicsInput) -> Tuple[float, Dict[str, float]]:
        """Enterprise LTV: ACV-based with significant expansion."""
        acv = inputs.average_contract_value or (inputs.monthly_recurring_revenue or 0) * 12
        gross_margin = (100 - (inputs.cost_of_goods_sold_pct or 20)) / 100
        lifespan_years = (inputs.customer_lifespan_months or 48) / 12
        # Assume 30% annual expansion for enterprise
        expansion_factor = 1.3
        ltv = acv * gross_margin * lifespan_years * expansion_factor
        return ltv, {
            'annual_contribution': acv * gross_margin,
            'lifespan_years': lifespan_years,
            'expansion_factor': expansion_factor,
        }

    def calculate_gross_margin(self, inputs: UnitEconomicsInput) -> float:
        cogs = inputs.cost_of_goods_sold_pct or 20.0
        return 100 - cogs


class SaaSB2CFreemiumModel(UnitEconomicsModel):
    """Unit economics for SaaS B2C Freemium businesses."""

    model_type = BusinessModelType.SAAS_B2C_FREEMIUM

    def _default_benchmarks(self) -> BenchmarkData:
        return BenchmarkData(
            healthy_ltv_cac_ratio=3.0,
            healthy_gross_margin_pct=65.0,
            healthy_payback_months=6.0,  # Shorter for B2C
            source="saas_b2c_freemium_benchmarks",
        )

    def calculate_cac(self, inputs: UnitEconomicsInput) -> Tuple[float, Dict[str, float]]:
        """B2C Freemium: Include free user acquisition cost."""
        if inputs.new_customers and inputs.new_customers > 0:
            # Assume 5% conversion from free to paid
            free_to_paid_rate = 0.05
            cost_per_free_user = (inputs.marketing_spend_usd or 0) / inputs.new_customers
            cac = cost_per_free_user / free_to_paid_rate
            return cac, {
                'cost_per_free_user': cost_per_free_user,
                'free_to_paid_rate': free_to_paid_rate,
            }
        return 0.0, {}

    def calculate_ltv(self, inputs: UnitEconomicsInput) -> Tuple[float, Dict[str, float]]:
        """B2C LTV: Lower ARPU, higher churn."""
        mrr = inputs.monthly_recurring_revenue or 0
        gross_margin = (100 - (inputs.cost_of_goods_sold_pct or 35)) / 100
        lifespan = inputs.customer_lifespan_months or (
            1 / (inputs.monthly_churn_pct / 100) if inputs.monthly_churn_pct else 12
        )
        ltv = mrr * gross_margin * lifespan
        return ltv, {
            'monthly_contribution': mrr * gross_margin,
            'lifespan_months': lifespan,
        }

    def calculate_gross_margin(self, inputs: UnitEconomicsInput) -> float:
        cogs = inputs.cost_of_goods_sold_pct or 35.0
        return 100 - cogs


class SaaSB2CSubscriptionModel(SaaSB2CFreemiumModel):
    """Unit economics for SaaS B2C Subscription (no freemium)."""

    model_type = BusinessModelType.SAAS_B2C_SUBSCRIPTION

    def calculate_cac(self, inputs: UnitEconomicsInput) -> Tuple[float, Dict[str, float]]:
        """B2C Subscription: Direct acquisition, no freemium conversion."""
        if inputs.new_customers and inputs.new_customers > 0:
            cac = (inputs.marketing_spend_usd or 0) / inputs.new_customers
            return cac, {'direct_acquisition': cac}
        return 0.0, {}


# =======================================================================================
# E-COMMERCE MODELS
# =======================================================================================

class EcommerceDTCModel(UnitEconomicsModel):
    """Unit economics for Direct-to-Consumer E-commerce."""

    model_type = BusinessModelType.ECOMMERCE_DTC

    def _default_benchmarks(self) -> BenchmarkData:
        return BenchmarkData(
            healthy_ltv_cac_ratio=3.0,
            healthy_gross_margin_pct=50.0,  # Lower for physical goods
            healthy_payback_months=6.0,
            source="ecommerce_dtc_benchmarks",
        )

    def calculate_cac(self, inputs: UnitEconomicsInput) -> Tuple[float, Dict[str, float]]:
        """DTC CAC: Marketing spend / new customers."""
        if inputs.new_customers and inputs.new_customers > 0:
            cac = (inputs.marketing_spend_usd or 0) / inputs.new_customers
            return cac, {'marketing': cac}
        return 0.0, {}

    def calculate_ltv(self, inputs: UnitEconomicsInput) -> Tuple[float, Dict[str, float]]:
        """DTC LTV: AOV * Purchases/Year * Lifespan * Margin."""
        aov = inputs.average_order_value or 0
        purchases_per_year = inputs.transactions_per_customer_per_year or 2
        gross_margin = (100 - (inputs.cost_of_goods_sold_pct or 50)) / 100
        lifespan_years = (inputs.customer_lifespan_months or 24) / 12
        ltv = aov * purchases_per_year * gross_margin * lifespan_years
        return ltv, {
            'annual_revenue': aov * purchases_per_year,
            'annual_contribution': aov * purchases_per_year * gross_margin,
            'lifespan_years': lifespan_years,
        }

    def calculate_gross_margin(self, inputs: UnitEconomicsInput) -> float:
        cogs = inputs.cost_of_goods_sold_pct or 50.0
        return 100 - cogs


class EcommerceMarketplaceModel(UnitEconomicsModel):
    """Unit economics for Marketplace E-commerce."""

    model_type = BusinessModelType.ECOMMERCE_MARKETPLACE

    def _default_benchmarks(self) -> BenchmarkData:
        return BenchmarkData(
            healthy_ltv_cac_ratio=4.0,
            healthy_gross_margin_pct=70.0,  # Higher - no COGS, just take rate
            healthy_payback_months=12.0,
            source="ecommerce_marketplace_benchmarks",
        )

    def calculate_cac(self, inputs: UnitEconomicsInput) -> Tuple[float, Dict[str, float]]:
        """Marketplace CAC: Both buyer and seller acquisition."""
        if inputs.new_customers and inputs.new_customers > 0:
            buyer_cac = (inputs.marketing_spend_usd or 0) / inputs.new_customers
            # Assume seller acquisition is 2x buyer
            seller_cac = buyer_cac * 2
            # Weighted average (assume 80% buyers, 20% sellers)
            blended_cac = buyer_cac * 0.8 + seller_cac * 0.2
            return blended_cac, {
                'buyer_cac': buyer_cac,
                'seller_cac': seller_cac,
                'blended': blended_cac,
            }
        return 0.0, {}

    def calculate_ltv(self, inputs: UnitEconomicsInput) -> Tuple[float, Dict[str, float]]:
        """Marketplace LTV: GMV * Take Rate * Lifespan."""
        gmv = inputs.gmv_usd or inputs.average_order_value or 0
        take_rate = (inputs.take_rate_pct or 15) / 100
        transactions = inputs.transactions_per_customer_per_year or 4
        lifespan_years = (inputs.customer_lifespan_months or 36) / 12
        ltv = gmv * take_rate * transactions * lifespan_years
        return ltv, {
            'annual_gmv': gmv * transactions,
            'annual_revenue': gmv * take_rate * transactions,
            'lifespan_years': lifespan_years,
        }

    def calculate_gross_margin(self, inputs: UnitEconomicsInput) -> float:
        # Marketplaces have high margin - mostly platform costs
        return inputs.take_rate_pct or 70.0


# =======================================================================================
# FINTECH MODELS
# =======================================================================================

class FintechB2BModel(UnitEconomicsModel):
    """Unit economics for B2B Fintech."""

    model_type = BusinessModelType.FINTECH_B2B

    def _default_benchmarks(self) -> BenchmarkData:
        return BenchmarkData(
            healthy_ltv_cac_ratio=5.0,  # Higher for fintech
            healthy_gross_margin_pct=60.0,
            healthy_payback_months=18.0,
            source="fintech_b2b_benchmarks",
        )

    def calculate_cac(self, inputs: UnitEconomicsInput) -> Tuple[float, Dict[str, float]]:
        """B2B Fintech: High compliance and sales costs."""
        if inputs.new_customers and inputs.new_customers > 0:
            marketing_cac = (inputs.marketing_spend_usd or 0) / inputs.new_customers
            compliance_cost = 2000  # Compliance/underwriting per customer
            sales_cac = marketing_cac * 1.5
            total_cac = marketing_cac + sales_cac + compliance_cost
            return total_cac, {
                'marketing': marketing_cac,
                'sales': sales_cac,
                'compliance': compliance_cost,
            }
        return 0.0, {}

    def calculate_ltv(self, inputs: UnitEconomicsInput) -> Tuple[float, Dict[str, float]]:
        """B2B Fintech LTV: Revenue minus expected losses."""
        mrr = inputs.monthly_recurring_revenue or 0
        gross_margin = (100 - (inputs.cost_of_goods_sold_pct or 40)) / 100
        default_rate = (inputs.default_rate_pct or 2) / 100
        lifespan = inputs.customer_lifespan_months or 36
        ltv = mrr * gross_margin * (1 - default_rate) * lifespan
        return ltv, {
            'monthly_contribution': mrr * gross_margin,
            'expected_loss_rate': default_rate,
            'lifespan_months': lifespan,
        }

    def calculate_gross_margin(self, inputs: UnitEconomicsInput) -> float:
        cogs = inputs.cost_of_goods_sold_pct or 40.0
        return 100 - cogs


class FintechB2CModel(UnitEconomicsModel):
    """Unit economics for B2C Fintech."""

    model_type = BusinessModelType.FINTECH_B2C

    def _default_benchmarks(self) -> BenchmarkData:
        return BenchmarkData(
            healthy_ltv_cac_ratio=4.0,
            healthy_gross_margin_pct=50.0,
            healthy_payback_months=12.0,
            source="fintech_b2c_benchmarks",
        )

    def calculate_cac(self, inputs: UnitEconomicsInput) -> Tuple[float, Dict[str, float]]:
        """B2C Fintech: Digital acquisition + KYC costs."""
        if inputs.new_customers and inputs.new_customers > 0:
            marketing_cac = (inputs.marketing_spend_usd or 0) / inputs.new_customers
            kyc_cost = 15  # KYC/verification per customer
            total_cac = marketing_cac + kyc_cost
            return total_cac, {
                'marketing': marketing_cac,
                'kyc': kyc_cost,
            }
        return 0.0, {}

    def calculate_ltv(self, inputs: UnitEconomicsInput) -> Tuple[float, Dict[str, float]]:
        """B2C Fintech LTV: Transaction fees or NIM."""
        mrr = inputs.monthly_recurring_revenue or 0
        nim = inputs.net_interest_margin_pct or 0
        gross_margin = (100 - (inputs.cost_of_goods_sold_pct or 50)) / 100
        default_rate = (inputs.default_rate_pct or 5) / 100
        lifespan = inputs.customer_lifespan_months or 24

        # Use MRR or NIM-based calculation
        if mrr > 0:
            ltv = mrr * gross_margin * (1 - default_rate) * lifespan
        else:
            # NIM-based (lending)
            avg_balance = 1000  # Assumed average balance
            monthly_nim = (nim / 100) / 12 * avg_balance
            ltv = monthly_nim * (1 - default_rate) * lifespan

        return ltv, {
            'default_adjusted': 1 - default_rate,
            'lifespan_months': lifespan,
        }

    def calculate_gross_margin(self, inputs: UnitEconomicsInput) -> float:
        cogs = inputs.cost_of_goods_sold_pct or 50.0
        return 100 - cogs


# =======================================================================================
# CONSULTING MODEL
# =======================================================================================

class ConsultingModel(UnitEconomicsModel):
    """Unit economics for Consulting/Services businesses."""

    model_type = BusinessModelType.CONSULTING

    def _default_benchmarks(self) -> BenchmarkData:
        return BenchmarkData(
            healthy_ltv_cac_ratio=5.0,
            healthy_gross_margin_pct=40.0,  # Lower - people costs
            healthy_payback_months=6.0,
            source="consulting_benchmarks",
        )

    def calculate_cac(self, inputs: UnitEconomicsInput) -> Tuple[float, Dict[str, float]]:
        """Consulting CAC: BD and proposal costs."""
        if inputs.new_customers and inputs.new_customers > 0:
            bd_cost = (inputs.marketing_spend_usd or 0) / inputs.new_customers
            proposal_cost = (inputs.sales_cycle_days or 30) * 200  # $200/day BD cost
            total_cac = bd_cost + proposal_cost
            return total_cac, {
                'business_development': bd_cost,
                'proposal_cost': proposal_cost,
            }
        return 0.0, {}

    def calculate_ltv(self, inputs: UnitEconomicsInput) -> Tuple[float, Dict[str, float]]:
        """Consulting LTV: Project value * repeat rate."""
        project_value = inputs.average_contract_value or 50000
        gross_margin = (100 - (inputs.cost_of_goods_sold_pct or 60)) / 100
        repeat_rate = 2.0  # Assume 2 projects per client
        ltv = project_value * gross_margin * repeat_rate
        return ltv, {
            'project_contribution': project_value * gross_margin,
            'repeat_rate': repeat_rate,
        }

    def calculate_gross_margin(self, inputs: UnitEconomicsInput) -> float:
        cogs = inputs.cost_of_goods_sold_pct or 60.0  # High people costs
        return 100 - cogs


# =======================================================================================
# MODEL REGISTRY
# =======================================================================================

MODEL_REGISTRY: Dict[BusinessModelType, type] = {
    BusinessModelType.SAAS_B2B_SMB: SaaSB2BSMBModel,
    BusinessModelType.SAAS_B2B_MIDMARKET: SaaSB2BMidMarketModel,
    BusinessModelType.SAAS_B2B_ENTERPRISE: SaaSB2BEnterpriseModel,
    BusinessModelType.SAAS_B2C_FREEMIUM: SaaSB2CFreemiumModel,
    BusinessModelType.SAAS_B2C_SUBSCRIPTION: SaaSB2CSubscriptionModel,
    BusinessModelType.ECOMMERCE_DTC: EcommerceDTCModel,
    BusinessModelType.ECOMMERCE_MARKETPLACE: EcommerceMarketplaceModel,
    BusinessModelType.FINTECH_B2B: FintechB2BModel,
    BusinessModelType.FINTECH_B2C: FintechB2CModel,
    BusinessModelType.CONSULTING: ConsultingModel,
}


def get_model_for_type(model_type: BusinessModelType) -> UnitEconomicsModel:
    """
    Factory function to get the appropriate model.

    Args:
        model_type: The business model type

    Returns:
        Instantiated model for that type
    """
    model_class = MODEL_REGISTRY.get(model_type)
    if model_class is None:
        # Default to SaaS B2B SMB as generic fallback
        model_class = SaaSB2BSMBModel
    return model_class()


def calculate_unit_economics(
    model_type: BusinessModelType,
    inputs: UnitEconomicsInput,
) -> ToolResult[ViabilityMetrics]:
    """
    Convenience function to calculate unit economics.

    Args:
        model_type: Business model type
        inputs: Input data for calculations

    Returns:
        ToolResult containing ViabilityMetrics
    """
    model = get_model_for_type(model_type)
    return model.calculate_metrics(inputs)
