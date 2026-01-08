"""
DiscoveryCrew - Phase 1: VPC Discovery - Segment Validation + Evidence Collection

This crew validates the customer segment and collects SAY + DO evidence.

Agents:
- E1: Experiment Designer (Sage) - Design experiment mix using Test Cards
- D1: Customer Interview Agent (Sage) - SAY evidence collection (Mom Test)
- D2: Observation Agent (Pulse) - DO-indirect evidence (reviews, forums, trends)
- D3: CTA Test Agent (Pulse) - DO-direct evidence (landing pages, ads)
- D4: Evidence Triangulation Agent (Guardian) - Synthesize SAY vs DO
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class DiscoveryCrew:
    """
    DiscoveryCrew handles segment validation and evidence collection.

    Produces:
    - Assumptions Map (prioritized)
    - Test Cards (experiment designs)
    - Interview Insights (SAY evidence)
    - Behavioral Evidence (DO-indirect)
    - CTA Results (DO-direct)
    - Evidence Synthesis (triangulated)
    """

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # =========================================================================
    # AGENTS
    # =========================================================================

    @agent
    def e1_experiment_designer(self) -> Agent:
        """E1: Experiment Designer - Designs validation experiments."""
        return Agent(
            config=self.agents_config["e1_experiment_designer"],
            verbose=True,
        )

    @agent
    def d1_customer_interview(self) -> Agent:
        """D1: Customer Interview Agent - SAY evidence collection."""
        return Agent(
            config=self.agents_config["d1_customer_interview"],
            verbose=True,
        )

    @agent
    def d2_observation_agent(self) -> Agent:
        """D2: Observation Agent - DO-indirect evidence."""
        return Agent(
            config=self.agents_config["d2_observation_agent"],
            verbose=True,
        )

    @agent
    def d3_cta_test_agent(self) -> Agent:
        """D3: CTA Test Agent - DO-direct evidence."""
        return Agent(
            config=self.agents_config["d3_cta_test_agent"],
            verbose=True,
        )

    @agent
    def d4_evidence_triangulation(self) -> Agent:
        """D4: Evidence Triangulation Agent - Synthesizes evidence."""
        return Agent(
            config=self.agents_config["d4_evidence_triangulation"],
            verbose=True,
        )

    # =========================================================================
    # TASKS
    # =========================================================================

    @task
    def map_assumptions(self) -> Task:
        """Map assumptions on 2×2 matrix and prioritize."""
        return Task(config=self.tasks_config["map_assumptions"])

    @task
    def design_test_cards(self) -> Task:
        """Design Test Cards for top assumptions."""
        return Task(config=self.tasks_config["design_test_cards"])

    @task
    def conduct_discovery_interviews(self) -> Task:
        """Conduct Mom Test interviews for SAY evidence."""
        return Task(config=self.tasks_config["conduct_discovery_interviews"])

    @task
    def mine_behavioral_evidence(self) -> Task:
        """Mine DO-indirect evidence from observations."""
        return Task(config=self.tasks_config["mine_behavioral_evidence"])

    @task
    def execute_cta_experiments(self) -> Task:
        """Execute CTA tests for DO-direct evidence."""
        return Task(config=self.tasks_config["execute_cta_experiments"])

    @task
    def triangulate_evidence(self) -> Task:
        """Synthesize SAY vs DO evidence."""
        return Task(config=self.tasks_config["triangulate_evidence"])

    # =========================================================================
    # CREW
    # =========================================================================

    @crew
    def crew(self) -> Crew:
        """
        Creates the DiscoveryCrew with sequential process.

        Task Flow:
        1. E1 maps assumptions and designs Test Cards
        2. D1 conducts discovery interviews (SAY)
        3. D2 mines behavioral evidence (DO-indirect)
        4. D3 executes CTA experiments (DO-direct)
        5. D4 triangulates all evidence
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
