"""
FitAssessmentCrew - Phase 1 Stage B: VPC Discovery - Fit Scoring + Iteration Routing

This crew scores Problem-Solution Fit and routes based on result.

Agents:
- FIT_SCORE: Fit Analyst (Compass) - Score Customer Profile <-> Value Map fit
- FIT_ROUTE: Iteration Router (Compass) - Route by fit score

HITL Checkpoint: approve_discovery_output (when fit >= 70)

@story US-AD09
"""

from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task

from src.state.models import FitAssessment
from shared.tools import MethodologyCheckTool


@CrewBase
class FitAssessmentCrew:
    """
    FitAssessmentCrew scores fit and determines routing.

    Produces:
    - Fit Score (0-100)
    - Jobs/Pains/Gains addressed percentages
    - Routing decision (SEGMENT_PIVOT, ITERATE_*, VPC_COMPLETE)
    """

    agents_config = "config/fit_assessment_agents.yaml"
    tasks_config = "config/fit_assessment_tasks.yaml"

    # =========================================================================
    # AGENTS
    # =========================================================================

    @agent
    def fit_score_analyst(self) -> Agent:
        """FIT_SCORE: Fit Analyst - Scores Problem-Solution Fit."""
        return Agent(
            config=self.agents_config["fit_score_analyst"],
            tools=[MethodologyCheckTool()],  # VPC validation tool
            reasoning=True,
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.2),  # Analytical
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def fit_route_agent(self) -> Agent:
        """FIT_ROUTE: Iteration Router - Routes by fit score."""
        return Agent(
            config=self.agents_config["fit_route_agent"],
            tools=[],
            reasoning=False,  # Simple routing decision
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
    def calculate_fit_score(self) -> Task:
        """Calculate Problem-Solution Fit score."""
        return Task(config=self.tasks_config["calculate_fit_score"])

    @task
    def determine_routing(self) -> Task:
        """Determine routing based on fit score."""
        return Task(config=self.tasks_config["determine_routing"])

    @task
    def compile_fit_assessment(self) -> Task:
        """Compile final fit assessment."""
        return Task(
            config=self.tasks_config["compile_fit_assessment"],
            output_pydantic=FitAssessment,
        )

    # =========================================================================
    # CREW
    # =========================================================================

    @crew
    def crew(self) -> Crew:
        """
        Creates the FitAssessmentCrew with sequential process.

        Task Flow:
        1. FIT_SCORE calculates fit score
        2. FIT_ROUTE determines routing
        3. Compile FitAssessment

        Routing Logic:
        - fit < 40: SEGMENT_PIVOT (wrong customer)
        - 40 <= fit < 70: ITERATE_* (refine)
        - fit >= 70: VPC_COMPLETE (proceed to Phase 2)
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
