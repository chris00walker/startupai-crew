"""
ValueDesignCrew - Phase 1: VPC Discovery - Value Map Design

This crew designs the Value Map (left side of Value Proposition Canvas)
to address the discovered Customer Profile.

Agents:
- V1: Solution Designer (Forge) - Design Products & Services
- V2: Pain Reliever Designer (Forge) - Design Pain Relievers
- V3: Gain Creator Designer (Forge) - Design Gain Creators
"""

from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task

from src.state.models import ValueMap


@CrewBase
class ValueDesignCrew:
    """
    ValueDesignCrew designs the Value Map from VPD framework.

    Produces ValueMap with:
    - Products & Services (addressing top jobs)
    - Pain Relievers (for severe pains)
    - Gain Creators (for important gains)
    """

    agents_config = "config/value_design_agents.yaml"
    tasks_config = "config/value_design_tasks.yaml"

    # =========================================================================
    # AGENTS
    # =========================================================================

    @agent
    def v1_solution_designer(self) -> Agent:
        """V1: Solution Designer - Designs products/services."""
        return Agent(
            config=self.agents_config["v1_solution_designer"],
            tools=[],
            reasoning=False,  # Creative design work
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.8),
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def v2_pain_reliever_designer(self) -> Agent:
        """V2: Pain Reliever Designer - Designs pain relievers."""
        return Agent(
            config=self.agents_config["v2_pain_reliever_designer"],
            tools=[],
            reasoning=False,  # Creative design work
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.8),
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def v3_gain_creator_designer(self) -> Agent:
        """V3: Gain Creator Designer - Designs gain creators."""
        return Agent(
            config=self.agents_config["v3_gain_creator_designer"],
            tools=[],
            reasoning=False,  # Creative design work
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.8),
            verbose=True,
            allow_delegation=False,
        )

    # =========================================================================
    # TASKS
    # =========================================================================

    @task
    def design_products_services(self) -> Task:
        """Design products/services that address top jobs."""
        return Task(config=self.tasks_config["design_products_services"])

    @task
    def design_pain_relievers(self) -> Task:
        """Design pain relievers for severe pains."""
        return Task(config=self.tasks_config["design_pain_relievers"])

    @task
    def design_gain_creators(self) -> Task:
        """Design gain creators for important gains."""
        return Task(config=self.tasks_config["design_gain_creators"])

    @task
    def compile_value_map(self) -> Task:
        """Compile final Value Map."""
        return Task(
            config=self.tasks_config["compile_value_map"],
            output_pydantic=ValueMap,
        )

    # =========================================================================
    # CREW
    # =========================================================================

    @crew
    def crew(self) -> Crew:
        """
        Creates the ValueDesignCrew with sequential process.

        Task Flow:
        1. V1 designs products/services for top jobs
        2. V2 designs pain relievers for severe pains
        3. V3 designs gain creators for important gains
        4. Compile into ValueMap
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
