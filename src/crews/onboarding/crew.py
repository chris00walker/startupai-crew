"""
OnboardingCrew - Phase 0: Founder's Brief Creation

This crew transforms the Founder's raw idea into a structured Founder's Brief,
the prime artifact that informs all subsequent validation phases.

Agents:
- O1: Founder Interview Agent (Sage) - Conducts 7-area discovery interview
- GV1: Concept Validator Agent (Guardian) - Legitimacy screening
- GV2: Intent Verification Agent (Guardian) - Verifies capture accuracy
- S1: Brief Compiler Agent (Sage) - Synthesizes into Founder's Brief

HITL Checkpoint: approve_founders_brief
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from pydantic import BaseModel
from typing import Optional

from src.state.models import FoundersBrief


@CrewBase
class OnboardingCrew:
    """
    OnboardingCrew handles Phase 0: transforming founder input into structured brief.

    This crew is the entry point for all validation runs. It conducts interviews,
    validates legitimacy, verifies intent, and compiles the Founder's Brief.
    """

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # =========================================================================
    # AGENTS
    # =========================================================================

    @agent
    def o1_founder_interview(self) -> Agent:
        """O1: Founder Interview Agent - Conducts comprehensive discovery interview."""
        return Agent(
            config=self.agents_config["o1_founder_interview"],
            verbose=True,
        )

    @agent
    def gv1_concept_validator(self) -> Agent:
        """GV1: Concept Validator Agent - Screens for legitimacy."""
        return Agent(
            config=self.agents_config["gv1_concept_validator"],
            verbose=True,
        )

    @agent
    def gv2_intent_verification(self) -> Agent:
        """GV2: Intent Verification Agent - Ensures accurate capture."""
        return Agent(
            config=self.agents_config["gv2_intent_verification"],
            verbose=True,
        )

    @agent
    def s1_brief_compiler(self) -> Agent:
        """S1: Brief Compiler Agent - Synthesizes the Founder's Brief."""
        return Agent(
            config=self.agents_config["s1_brief_compiler"],
            verbose=True,
        )

    # =========================================================================
    # TASKS
    # =========================================================================

    @task
    def conduct_founder_interview(self) -> Task:
        """Conduct comprehensive 7-area interview with the founder."""
        return Task(
            config=self.tasks_config["conduct_founder_interview"],
        )

    @task
    def validate_concept_legitimacy(self) -> Task:
        """Validate concept is legal, ethical, feasible, and sane."""
        return Task(
            config=self.tasks_config["validate_concept_legitimacy"],
        )

    @task
    def verify_intent_capture(self) -> Task:
        """Verify that founder's intent was accurately captured."""
        return Task(
            config=self.tasks_config["verify_intent_capture"],
        )

    @task
    def compile_founders_brief(self) -> Task:
        """Compile all inputs into the structured Founder's Brief."""
        return Task(
            config=self.tasks_config["compile_founders_brief"],
            output_pydantic=FoundersBrief,
        )

    # =========================================================================
    # CREW
    # =========================================================================

    @crew
    def crew(self) -> Crew:
        """
        Creates the OnboardingCrew with sequential process.

        Task Flow:
        1. O1 conducts founder interview
        2. GV1 validates concept legitimacy
        3. GV2 verifies intent capture
        4. S1 compiles the Founder's Brief

        The crew produces a FoundersBrief Pydantic model as output.
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )


def run_onboarding_crew(entrepreneur_input: str) -> FoundersBrief:
    """
    Execute the OnboardingCrew to generate a Founder's Brief.

    Args:
        entrepreneur_input: The founder's raw idea description

    Returns:
        FoundersBrief: Structured brief ready for HITL approval
    """
    crew = OnboardingCrew()
    result = crew.crew().kickoff(
        inputs={
            "entrepreneur_input": entrepreneur_input,
        }
    )
    return result.pydantic
