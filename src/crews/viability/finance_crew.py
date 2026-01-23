"""
FinanceCrew - Phase 4: Viability - Unit Economics

This crew calculates unit economics and determines business viability.

Agents:
- L1: Financial Controller (Ledger) - Calculate CAC, LTV, margins
- L2: Legal & Compliance (Ledger) - Regulatory constraints
- L3: Economics Reviewer (Ledger) - Validate assumptions, benchmarks

@story US-AVB01
"""

from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task

from shared.tools import AnalyticsTool
from src.state.models import ViabilityEvidence


@CrewBase
class FinanceCrew:
    """
    FinanceCrew calculates unit economics and viability.

    Produces:
    - CAC calculation
    - LTV calculation
    - LTV:CAC ratio
    - Viability signal (PROFITABLE/MARGINAL/UNDERWATER)
    """

    agents_config = "config/finance_agents.yaml"
    tasks_config = "config/finance_tasks.yaml"

    # =========================================================================
    # AGENTS
    # =========================================================================

    @agent
    def l1_financial_controller(self) -> Agent:
        """L1: Financial Controller - Unit economics."""
        return Agent(
            config=self.agents_config["l1_financial_controller"],
            tools=[
                AnalyticsTool(),
            ],
            reasoning=True,  # Analyzes financial data from experiments
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.2),  # Financial precision
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def l2_legal_compliance(self) -> Agent:
        """L2: Legal & Compliance - Regulatory review."""
        return Agent(
            config=self.agents_config["l2_legal_compliance"],
            tools=[],
            reasoning=False,  # Compliance check
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.1),  # Strict compliance
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def l3_economics_reviewer(self) -> Agent:
        """L3: Economics Reviewer - Validation."""
        return Agent(
            config=self.agents_config["l3_economics_reviewer"],
            tools=[],
            reasoning=False,  # Assumption validation
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.2),  # Analytical
            verbose=True,
            allow_delegation=False,
        )

    # =========================================================================
    # TASKS
    # =========================================================================

    @task
    def calculate_cac(self) -> Task:
        """Calculate Customer Acquisition Cost."""
        return Task(config=self.tasks_config["calculate_cac"])

    @task
    def calculate_ltv(self) -> Task:
        """Calculate Lifetime Value."""
        return Task(config=self.tasks_config["calculate_ltv"])

    @task
    def compute_ltv_cac_ratio(self) -> Task:
        """Compute LTV:CAC ratio and key metrics."""
        return Task(config=self.tasks_config["compute_ltv_cac_ratio"])

    @task
    def analyze_tam(self) -> Task:
        """Analyze Total Addressable Market."""
        return Task(config=self.tasks_config["analyze_tam"])

    @task
    def identify_regulatory_constraints(self) -> Task:
        """Identify regulatory and compliance constraints."""
        return Task(config=self.tasks_config["identify_regulatory_constraints"])

    @task
    def validate_assumptions(self) -> Task:
        """Validate unit economics assumptions."""
        return Task(config=self.tasks_config["validate_assumptions"])

    @task
    def set_viability_signal(self) -> Task:
        """Set viability signal (PROFITABLE/MARGINAL/UNDERWATER)."""
        return Task(
            config=self.tasks_config["set_viability_signal"],
            output_pydantic=ViabilityEvidence,
        )

    # =========================================================================
    # CREW
    # =========================================================================

    @crew
    def crew(self) -> Crew:
        """
        Creates the FinanceCrew with sequential process.

        Task Flow:
        1. L1 calculates CAC from experiment data
        2. L1 calculates LTV from pricing
        3. L1 computes LTV:CAC ratio
        4. L1 analyzes TAM
        5. L2 identifies regulatory constraints
        6. L3 validates assumptions against benchmarks
        7. L1 sets viability signal
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
