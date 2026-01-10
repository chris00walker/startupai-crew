"""
WTPCrew - Phase 1: VPC Discovery - Willingness to Pay Validation

This crew validates that customers will pay for the proposed value.

Agents:
- W1: Pricing Experiment Agent (Ledger) - Design WTP experiments
- W2: Payment Test Agent (Ledger) - Execute payment tests

HITL Checkpoint: approve_pricing_test (before any real money is involved)
"""

from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task

from shared.tools import ABTestTool, AnalyticsTool


@CrewBase
class WTPCrew:
    """
    WTPCrew validates Willingness to Pay through experiments.

    Produces:
    - WTP experiment designs (Van Westendorp, conjoint, A/B)
    - Payment test results (mock sales, pre-orders)
    - WTP validation verdict
    """

    agents_config = "config/wtp_agents.yaml"
    tasks_config = "config/wtp_tasks.yaml"

    # =========================================================================
    # AGENTS
    # =========================================================================

    @agent
    def w1_pricing_experiment(self) -> Agent:
        """W1: Pricing Experiment Agent - Designs WTP experiments."""
        return Agent(
            config=self.agents_config["w1_pricing_experiment"],
            tools=[
                ABTestTool(),
                AnalyticsTool(),
            ],
            reasoning=True,  # Analyzes pricing experiment results
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.5),
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def w2_payment_test(self) -> Agent:
        """W2: Payment Test Agent - Executes payment tests."""
        return Agent(
            config=self.agents_config["w2_payment_test"],
            tools=[
                AnalyticsTool(),
            ],
            reasoning=True,  # Analyzes payment test results
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.3),
            verbose=True,
            allow_delegation=False,
        )

    # =========================================================================
    # TASKS
    # =========================================================================

    @task
    def design_wtp_experiments(self) -> Task:
        """Design WTP experiments (Van Westendorp, conjoint, A/B)."""
        return Task(config=self.tasks_config["design_wtp_experiments"])

    @task
    def execute_payment_tests(self) -> Task:
        """Execute payment tests (requires HITL approval for real money)."""
        return Task(config=self.tasks_config["execute_payment_tests"])

    @task
    def synthesize_wtp_evidence(self) -> Task:
        """Synthesize WTP validation results."""
        return Task(config=self.tasks_config["synthesize_wtp_evidence"])

    # =========================================================================
    # CREW
    # =========================================================================

    @crew
    def crew(self) -> Crew:
        """
        Creates the WTPCrew with sequential process.

        Task Flow:
        1. W1 designs WTP experiments
        2. [HITL: approve_pricing_test if real $ involved]
        3. W2 executes payment tests
        4. Synthesize WTP evidence
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
