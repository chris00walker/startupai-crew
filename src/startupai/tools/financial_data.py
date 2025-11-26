"""
Financial Data Tools for StartupAI.

Provides industry benchmark data and unit economics calculations
for viability analysis.

These tools provide realistic benchmark data for CAC, LTV, gross margins,
and other key financial metrics based on industry and business model.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

from startupai.models.tool_contracts import ToolResult


# =======================================================================================
# BENCHMARK DATA MODELS
# =======================================================================================

class IndustryBenchmarks(BaseModel):
    """Industry benchmark metrics."""
    industry: str
    business_model: str
    avg_cac_usd: float = Field(description="Average Customer Acquisition Cost")
    cac_range_low: float = Field(description="Low end of CAC range")
    cac_range_high: float = Field(description="High end of CAC range")
    avg_ltv_usd: float = Field(description="Average Lifetime Value")
    ltv_range_low: float = Field(description="Low end of LTV range")
    ltv_range_high: float = Field(description="High end of LTV range")
    avg_ltv_cac_ratio: float = Field(description="Average LTV/CAC ratio")
    target_ltv_cac_ratio: float = Field(description="Target LTV/CAC for healthy unit economics")
    avg_gross_margin_pct: float = Field(description="Average gross margin percentage")
    avg_payback_months: int = Field(description="Average CAC payback period in months")
    avg_churn_rate_pct: float = Field(description="Average monthly churn rate")
    data_source: str = Field(description="Source of benchmark data")
    data_year: int = Field(description="Year of benchmark data")


class UnitEconomicsResult(BaseModel):
    """Calculated unit economics."""
    cac: float
    ltv: float
    ltv_cac_ratio: float
    gross_margin_pct: float
    payback_months: float
    viability_signal: str = Field(description="profitable, underwater, or zombie_market")
    recommendation: str
    comparison_to_benchmark: Dict[str, str] = Field(default_factory=dict)


# =======================================================================================
# BENCHMARK DATABASE (Curated from Public Sources)
# =======================================================================================

# Benchmark data curated from public sources:
# - OpenView SaaS Benchmarks 2024
# - KeyBanc SaaS Survey
# - ProfitWell Benchmarks
# - FirstMark Capital research
# - Various industry reports

INDUSTRY_BENCHMARKS = {
    # B2B SaaS
    "b2b_saas_smb": IndustryBenchmarks(
        industry="B2B SaaS",
        business_model="SMB (<100 employees)",
        avg_cac_usd=250,
        cac_range_low=100,
        cac_range_high=500,
        avg_ltv_usd=2000,
        ltv_range_low=1000,
        ltv_range_high=5000,
        avg_ltv_cac_ratio=8.0,
        target_ltv_cac_ratio=3.0,
        avg_gross_margin_pct=75,
        avg_payback_months=6,
        avg_churn_rate_pct=5.0,
        data_source="OpenView SaaS Benchmarks 2024",
        data_year=2024,
    ),
    "b2b_saas_midmarket": IndustryBenchmarks(
        industry="B2B SaaS",
        business_model="Mid-Market (100-1000 employees)",
        avg_cac_usd=3500,
        cac_range_low=1500,
        cac_range_high=8000,
        avg_ltv_usd=35000,
        ltv_range_low=15000,
        ltv_range_high=80000,
        avg_ltv_cac_ratio=10.0,
        target_ltv_cac_ratio=3.0,
        avg_gross_margin_pct=80,
        avg_payback_months=12,
        avg_churn_rate_pct=2.5,
        data_source="KeyBanc SaaS Survey 2024",
        data_year=2024,
    ),
    "b2b_saas_enterprise": IndustryBenchmarks(
        industry="B2B SaaS",
        business_model="Enterprise (1000+ employees)",
        avg_cac_usd=15000,
        cac_range_low=8000,
        cac_range_high=40000,
        avg_ltv_usd=180000,
        ltv_range_low=80000,
        ltv_range_high=500000,
        avg_ltv_cac_ratio=12.0,
        target_ltv_cac_ratio=3.0,
        avg_gross_margin_pct=85,
        avg_payback_months=18,
        avg_churn_rate_pct=1.5,
        data_source="KeyBanc SaaS Survey 2024",
        data_year=2024,
    ),

    # B2C SaaS
    "b2c_saas_freemium": IndustryBenchmarks(
        industry="B2C SaaS",
        business_model="Freemium Consumer",
        avg_cac_usd=25,
        cac_range_low=5,
        cac_range_high=80,
        avg_ltv_usd=120,
        ltv_range_low=40,
        ltv_range_high=300,
        avg_ltv_cac_ratio=4.8,
        target_ltv_cac_ratio=3.0,
        avg_gross_margin_pct=70,
        avg_payback_months=3,
        avg_churn_rate_pct=8.0,
        data_source="ProfitWell Benchmarks 2024",
        data_year=2024,
    ),
    "b2c_saas_subscription": IndustryBenchmarks(
        industry="B2C SaaS",
        business_model="Subscription Consumer",
        avg_cac_usd=50,
        cac_range_low=20,
        cac_range_high=150,
        avg_ltv_usd=250,
        ltv_range_low=100,
        ltv_range_high=600,
        avg_ltv_cac_ratio=5.0,
        target_ltv_cac_ratio=3.0,
        avg_gross_margin_pct=65,
        avg_payback_months=4,
        avg_churn_rate_pct=6.0,
        data_source="ProfitWell Benchmarks 2024",
        data_year=2024,
    ),

    # E-commerce
    "ecommerce_dtc": IndustryBenchmarks(
        industry="E-commerce",
        business_model="Direct-to-Consumer",
        avg_cac_usd=45,
        cac_range_low=15,
        cac_range_high=100,
        avg_ltv_usd=150,
        ltv_range_low=50,
        ltv_range_high=400,
        avg_ltv_cac_ratio=3.3,
        target_ltv_cac_ratio=3.0,
        avg_gross_margin_pct=40,
        avg_payback_months=2,
        avg_churn_rate_pct=0,  # N/A for transactional
        data_source="Shopify E-commerce Benchmarks 2024",
        data_year=2024,
    ),
    "ecommerce_marketplace": IndustryBenchmarks(
        industry="E-commerce",
        business_model="Marketplace",
        avg_cac_usd=30,
        cac_range_low=10,
        cac_range_high=80,
        avg_ltv_usd=200,
        ltv_range_low=60,
        ltv_range_high=500,
        avg_ltv_cac_ratio=6.7,
        target_ltv_cac_ratio=3.0,
        avg_gross_margin_pct=25,
        avg_payback_months=3,
        avg_churn_rate_pct=0,
        data_source="a16z Marketplace Benchmarks",
        data_year=2024,
    ),

    # Fintech
    "fintech_b2b": IndustryBenchmarks(
        industry="Fintech",
        business_model="B2B Financial Services",
        avg_cac_usd=800,
        cac_range_low=300,
        cac_range_high=2000,
        avg_ltv_usd=8000,
        ltv_range_low=3000,
        ltv_range_high=20000,
        avg_ltv_cac_ratio=10.0,
        target_ltv_cac_ratio=3.0,
        avg_gross_margin_pct=70,
        avg_payback_months=8,
        avg_churn_rate_pct=3.0,
        data_source="FirstMark Capital Fintech Research",
        data_year=2024,
    ),
    "fintech_b2c": IndustryBenchmarks(
        industry="Fintech",
        business_model="Consumer Financial App",
        avg_cac_usd=35,
        cac_range_low=10,
        cac_range_high=100,
        avg_ltv_usd=180,
        ltv_range_low=50,
        ltv_range_high=400,
        avg_ltv_cac_ratio=5.1,
        target_ltv_cac_ratio=3.0,
        avg_gross_margin_pct=60,
        avg_payback_months=4,
        avg_churn_rate_pct=7.0,
        data_source="FirstMark Capital Fintech Research",
        data_year=2024,
    ),

    # Professional Services
    "consulting_boutique": IndustryBenchmarks(
        industry="Professional Services",
        business_model="Boutique Consulting",
        avg_cac_usd=2000,
        cac_range_low=500,
        cac_range_high=5000,
        avg_ltv_usd=25000,
        ltv_range_low=10000,
        ltv_range_high=100000,
        avg_ltv_cac_ratio=12.5,
        target_ltv_cac_ratio=3.0,
        avg_gross_margin_pct=50,
        avg_payback_months=6,
        avg_churn_rate_pct=15.0,  # Project-based
        data_source="Industry analysis",
        data_year=2024,
    ),

    # Default / Generic
    "default": IndustryBenchmarks(
        industry="General",
        business_model="Mixed",
        avg_cac_usd=500,
        cac_range_low=100,
        cac_range_high=2000,
        avg_ltv_usd=3000,
        ltv_range_low=500,
        ltv_range_high=10000,
        avg_ltv_cac_ratio=6.0,
        target_ltv_cac_ratio=3.0,
        avg_gross_margin_pct=60,
        avg_payback_months=8,
        avg_churn_rate_pct=5.0,
        data_source="Industry averages",
        data_year=2024,
    ),
}


# =======================================================================================
# INDUSTRY BENCHMARK TOOL
# =======================================================================================

class IndustryBenchmarkTool(BaseTool):
    """
    Tool for retrieving industry benchmark data.

    Returns CAC, LTV, gross margin, and other key metrics
    based on industry and business model.
    """

    name: str = "industry_benchmarks"
    description: str = """
    Get industry benchmark data for unit economics comparison.

    Returns benchmark CAC, LTV, LTV/CAC ratio, gross margins, and other
    key financial metrics for the specified industry and business model.

    Available industries:
    - B2B SaaS (SMB, Mid-Market, Enterprise)
    - B2C SaaS (Freemium, Subscription)
    - E-commerce (DTC, Marketplace)
    - Fintech (B2B, B2C)
    - Professional Services (Consulting)

    Input should be a description of the industry/business model
    (e.g., "B2B SaaS for mid-market companies", "DTC e-commerce brand").
    """

    def _run(self, industry_description: str) -> str:
        """
        Get benchmark data for the specified industry.

        Args:
            industry_description: Description of industry and business model

        Returns:
            Formatted benchmark data
        """
        # Match to benchmark category
        benchmark_key = self._match_industry(industry_description.lower())
        benchmark = INDUSTRY_BENCHMARKS.get(benchmark_key, INDUSTRY_BENCHMARKS["default"])

        return self._format_benchmark(benchmark)

    async def _arun(self, industry_description: str) -> str:
        """Async version - delegates to sync."""
        return self._run(industry_description)

    def _match_industry(self, description: str) -> str:
        """Match description to benchmark category."""
        desc = description.lower()

        # B2B SaaS matching
        if "saas" in desc or "software" in desc:
            if "b2b" in desc or "business" in desc or "enterprise" in desc:
                if "enterprise" in desc or "large" in desc or "1000" in desc:
                    return "b2b_saas_enterprise"
                elif "mid" in desc or "medium" in desc or "100" in desc:
                    return "b2b_saas_midmarket"
                else:
                    return "b2b_saas_smb"
            elif "b2c" in desc or "consumer" in desc:
                if "freemium" in desc:
                    return "b2c_saas_freemium"
                else:
                    return "b2c_saas_subscription"

        # E-commerce matching
        if "ecommerce" in desc or "e-commerce" in desc or "retail" in desc:
            if "marketplace" in desc:
                return "ecommerce_marketplace"
            else:
                return "ecommerce_dtc"

        # Fintech matching
        if "fintech" in desc or "financial" in desc or "banking" in desc:
            if "b2b" in desc or "business" in desc:
                return "fintech_b2b"
            else:
                return "fintech_b2c"

        # Professional services
        if "consulting" in desc or "professional service" in desc or "agency" in desc:
            return "consulting_boutique"

        return "default"

    def _format_benchmark(self, benchmark: IndustryBenchmarks) -> str:
        """Format benchmark data for agent consumption."""
        return f"""## Industry Benchmarks: {benchmark.industry} - {benchmark.business_model}

### Customer Acquisition Cost (CAC)
- **Average:** ${benchmark.avg_cac_usd:,.0f}
- **Range:** ${benchmark.cac_range_low:,.0f} - ${benchmark.cac_range_high:,.0f}

### Lifetime Value (LTV)
- **Average:** ${benchmark.avg_ltv_usd:,.0f}
- **Range:** ${benchmark.ltv_range_low:,.0f} - ${benchmark.ltv_range_high:,.0f}

### Unit Economics
- **Average LTV/CAC Ratio:** {benchmark.avg_ltv_cac_ratio:.1f}x
- **Target LTV/CAC Ratio:** {benchmark.target_ltv_cac_ratio:.1f}x (minimum for healthy unit economics)
- **Average Gross Margin:** {benchmark.avg_gross_margin_pct:.0f}%
- **Average CAC Payback:** {benchmark.avg_payback_months} months
- **Average Monthly Churn:** {benchmark.avg_churn_rate_pct:.1f}%

### Benchmark Thresholds
- **Healthy:** LTV/CAC > 3x, Payback < 12 months
- **Concerning:** LTV/CAC 1-3x, Payback 12-18 months
- **Unsustainable:** LTV/CAC < 1x, Payback > 18 months

**Data Source:** {benchmark.data_source} ({benchmark.data_year})
"""

    def get_benchmark(self, industry_description: str) -> ToolResult[IndustryBenchmarks]:
        """
        Get benchmark as structured data.

        Returns ToolResult with IndustryBenchmarks model.
        """
        try:
            benchmark_key = self._match_industry(industry_description.lower())
            benchmark = INDUSTRY_BENCHMARKS.get(benchmark_key, INDUSTRY_BENCHMARKS["default"])
            return ToolResult.success(benchmark)
        except Exception as e:
            return ToolResult.failure(str(e), code="BENCHMARK_ERROR")


# =======================================================================================
# UNIT ECONOMICS CALCULATOR TOOL
# =======================================================================================

class UnitEconomicsCalculatorTool(BaseTool):
    """
    Calculate and analyze unit economics.

    Takes raw financial inputs and calculates key metrics,
    then compares to industry benchmarks.
    """

    name: str = "calculate_unit_economics"
    description: str = """
    Calculate unit economics from financial inputs and compare to benchmarks.

    Input should be a JSON-like string with these fields:
    - arpu: Average Revenue Per User (monthly)
    - avg_customer_lifetime_months: How long customers stay
    - cac: Customer Acquisition Cost (or ad_spend and customers_acquired)
    - cogs_pct: Cost of Goods Sold as percentage of revenue
    - industry: Industry description for benchmark comparison

    Example: "arpu: 50, avg_customer_lifetime_months: 24, cac: 200, cogs_pct: 20, industry: B2B SaaS SMB"

    Returns calculated LTV, LTV/CAC ratio, gross margin, payback period,
    viability assessment, and comparison to benchmarks.
    """

    def _run(self, inputs: str) -> str:
        """
        Calculate unit economics from inputs.

        Args:
            inputs: String with financial parameters

        Returns:
            Formatted unit economics analysis
        """
        try:
            # Parse inputs
            params = self._parse_inputs(inputs)

            # Calculate metrics
            arpu = params.get("arpu", 0)
            lifetime_months = params.get("avg_customer_lifetime_months", 12)
            cogs_pct = params.get("cogs_pct", 30)

            # CAC can be provided directly or calculated
            if "cac" in params:
                cac = params["cac"]
            elif "ad_spend" in params and "customers_acquired" in params:
                ad_spend = params["ad_spend"]
                customers = params["customers_acquired"]
                cac = ad_spend / customers if customers > 0 else 0
            else:
                cac = 0

            # Calculate LTV and other metrics
            gross_margin_pct = 100 - cogs_pct
            monthly_gross_profit = arpu * (gross_margin_pct / 100)
            ltv = monthly_gross_profit * lifetime_months
            ltv_cac_ratio = ltv / cac if cac > 0 else 0
            payback_months = cac / monthly_gross_profit if monthly_gross_profit > 0 else float('inf')

            # Determine viability signal
            if ltv_cac_ratio >= 3:
                viability_signal = "profitable"
                recommendation = "proceed"
            elif ltv_cac_ratio >= 1:
                viability_signal = "underwater"
                if cac > ltv * 0.5:
                    recommendation = "cost_pivot"  # Reduce CAC
                else:
                    recommendation = "price_pivot"  # Increase price
            else:
                viability_signal = "zombie_market"
                recommendation = "kill"

            # Get benchmarks for comparison
            industry = params.get("industry", "default")
            benchmark_tool = IndustryBenchmarkTool()
            benchmark_result = benchmark_tool.get_benchmark(industry)
            benchmark = benchmark_result.data if benchmark_result.is_usable else None

            # Build comparison
            comparison = {}
            if benchmark:
                comparison["cac_vs_benchmark"] = "below average" if cac < benchmark.avg_cac_usd else "above average"
                comparison["ltv_vs_benchmark"] = "above average" if ltv > benchmark.avg_ltv_usd else "below average"
                comparison["ratio_vs_benchmark"] = "healthy" if ltv_cac_ratio >= benchmark.target_ltv_cac_ratio else "needs improvement"

            result = UnitEconomicsResult(
                cac=round(cac, 2),
                ltv=round(ltv, 2),
                ltv_cac_ratio=round(ltv_cac_ratio, 2),
                gross_margin_pct=round(gross_margin_pct, 1),
                payback_months=round(payback_months, 1) if payback_months != float('inf') else 999,
                viability_signal=viability_signal,
                recommendation=recommendation,
                comparison_to_benchmark=comparison,
            )

            return self._format_result(result, benchmark)

        except Exception as e:
            return f"Calculation error: {str(e)}"

    async def _arun(self, inputs: str) -> str:
        """Async version - delegates to sync."""
        return self._run(inputs)

    def _parse_inputs(self, inputs: str) -> Dict[str, Any]:
        """Parse input string to parameters dict."""
        params = {}
        # Simple key: value parsing
        for part in inputs.replace(",", " ").split():
            if ":" in part:
                key, value = part.split(":", 1)
                key = key.strip().lower().replace(" ", "_")
                try:
                    params[key] = float(value.strip())
                except ValueError:
                    params[key] = value.strip()
            elif "=" in part:
                key, value = part.split("=", 1)
                key = key.strip().lower().replace(" ", "_")
                try:
                    params[key] = float(value.strip())
                except ValueError:
                    params[key] = value.strip()
        return params

    def _format_result(
        self,
        result: UnitEconomicsResult,
        benchmark: Optional[IndustryBenchmarks]
    ) -> str:
        """Format unit economics result."""
        lines = [
            "## Unit Economics Analysis",
            "",
            "### Calculated Metrics",
            f"- **Customer Acquisition Cost (CAC):** ${result.cac:,.2f}",
            f"- **Lifetime Value (LTV):** ${result.ltv:,.2f}",
            f"- **LTV/CAC Ratio:** {result.ltv_cac_ratio:.2f}x",
            f"- **Gross Margin:** {result.gross_margin_pct:.1f}%",
            f"- **CAC Payback Period:** {result.payback_months:.1f} months",
            "",
            "### Viability Assessment",
            f"- **Signal:** {result.viability_signal.upper()}",
            f"- **Recommendation:** {result.recommendation.replace('_', ' ').title()}",
            "",
        ]

        if result.comparison_to_benchmark:
            lines.extend([
                "### Benchmark Comparison",
            ])
            for key, value in result.comparison_to_benchmark.items():
                formatted_key = key.replace("_", " ").title()
                lines.append(f"- {formatted_key}: {value}")

        if benchmark:
            lines.extend([
                "",
                "### Industry Context",
                f"- Industry Average CAC: ${benchmark.avg_cac_usd:,.0f}",
                f"- Industry Average LTV: ${benchmark.avg_ltv_usd:,.0f}",
                f"- Industry Average LTV/CAC: {benchmark.avg_ltv_cac_ratio:.1f}x",
                f"- Target LTV/CAC for viability: >{benchmark.target_ltv_cac_ratio:.1f}x",
            ])

        return "\n".join(lines)


# =======================================================================================
# CONVENIENCE FUNCTIONS
# =======================================================================================

def get_industry_benchmarks(industry: str) -> str:
    """Convenience function for getting industry benchmarks."""
    tool = IndustryBenchmarkTool()
    return tool._run(industry)


def calculate_unit_economics(
    arpu: float,
    avg_customer_lifetime_months: int,
    cac: float,
    cogs_pct: float = 30,
    industry: str = "default"
) -> str:
    """
    Convenience function for calculating unit economics.

    Args:
        arpu: Average Revenue Per User (monthly)
        avg_customer_lifetime_months: Customer lifetime in months
        cac: Customer Acquisition Cost
        cogs_pct: Cost of Goods Sold percentage
        industry: Industry for benchmark comparison

    Returns:
        Formatted unit economics analysis
    """
    tool = UnitEconomicsCalculatorTool()
    inputs = f"arpu:{arpu} avg_customer_lifetime_months:{avg_customer_lifetime_months} cac:{cac} cogs_pct:{cogs_pct} industry:{industry}"
    return tool._run(inputs)
