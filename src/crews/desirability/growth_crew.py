"""
GrowthCrew - Phase 2: Desirability - Ad Campaigns and Evidence Collection

This crew runs ad campaigns and collects desirability evidence.

Agents:
- P1: Ad Creative Agent (Pulse) - Create ad variants
- P2: Communications Agent (Pulse) - Write copy variants
- P3: Analytics Agent (Pulse) - Run experiments, compute signals

HITL Checkpoints:
- approve_campaign_launch - Before running ads
- approve_spend_increase - Before budget increases
"""

from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task

from shared.tools import ABTestTool
from src.state.models import DesirabilityEvidence


@CrewBase
class GrowthCrew:
    """
    GrowthCrew runs experiments and collects desirability evidence.

    Produces:
    - Ad creative variants
    - Copy variants
    - Experiment results
    - Desirability signals (problem_resonance, zombie_ratio)
    """

    agents_config = "config/growth_agents.yaml"
    tasks_config = "config/growth_tasks.yaml"

    # =========================================================================
    # AGENTS
    # =========================================================================

    @agent
    def p1_ad_creative(self) -> Agent:
        """P1: Ad Creative Agent - Creates ad variants."""
        return Agent(
            config=self.agents_config["p1_ad_creative"],
            tools=[
                ABTestTool(),
            ],
            reasoning=False,  # Creative work
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.8),  # Creative
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def p2_communications(self) -> Agent:
        """P2: Communications Agent - Writes copy."""
        return Agent(
            config=self.agents_config["p2_communications"],
            tools=[
                ABTestTool(),
            ],
            reasoning=False,  # Copywriting
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.8),  # Creative
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def p3_analytics(self) -> Agent:
        """P3: Analytics Agent - Runs experiments."""
        return Agent(
            config=self.agents_config["p3_analytics"],
            tools=[],
            reasoning=False,  # Experiment execution
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
    def create_ad_variants(self) -> Task:
        """Create ad creative variants."""
        return Task(config=self.tasks_config["create_ad_variants"])

    @task
    def write_copy_variants(self) -> Task:
        """Write copy variants for ads and LP."""
        return Task(config=self.tasks_config["write_copy_variants"])

    @task
    def configure_experiments(self) -> Task:
        """Configure experiment setup."""
        return Task(config=self.tasks_config["configure_experiments"])

    @task
    def run_experiments(self) -> Task:
        """Run experiments and collect data."""
        return Task(config=self.tasks_config["run_experiments"])

    @task
    def compute_desirability_signals(self) -> Task:
        """Compute Innovation Physics signals."""
        return Task(
            config=self.tasks_config["compute_desirability_signals"],
            output_pydantic=DesirabilityEvidence,
        )

    # =========================================================================
    # CREW
    # =========================================================================

    @crew
    def crew(self) -> Crew:
        """
        Creates the GrowthCrew with sequential process.

        Task Flow:
        1. P1 creates ad variants
        2. P2 writes copy variants
        3. P3 configures experiments
        4. [HITL: approve_campaign_launch]
        5. P3 runs experiments
        6. P3 computes desirability signals
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
