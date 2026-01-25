"""
BriefGenerationCrew - Phase 1 Stage A: Generate Founder's Brief from raw idea

This crew transforms a raw idea and hints into a structured Founder's Brief.
Part of the Quick Start flow (replacing the conversational onboarding).

Agents:
- GV1: Concept Validator (Guardian) - Screens for legitimate business concepts
- S1: Brief Compiler (Scribe) - Compiles brief WITH web research using TavilySearchTool

Data Flow:
    raw_idea + hints -> GV1 (legitimacy check, no tools)
                     -> S1 (brief compilation WITH TavilySearchTool)
                     -> FoundersBrief output

@story US-AB01
"""

from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task

from shared.tools import TavilySearchTool
from src.state.models import FoundersBrief


@CrewBase
class BriefGenerationCrew:
    """
    BriefGenerationCrew generates a Founder's Brief from raw idea + hints.

    Quick Start Flow:
    1. GV1 validates concept legitimacy (no tools - just reasoning)
    2. S1 compiles the Founder's Brief WITH web research (uses TavilySearchTool)

    Output: FoundersBrief Pydantic model ready for HITL approval
    """

    agents_config = "config/brief_agents.yaml"
    tasks_config = "config/brief_tasks.yaml"

    # =========================================================================
    # AGENTS
    # =========================================================================

    @agent
    def gv1_concept_validator(self) -> Agent:
        """GV1: Concept Validator - Screens for legitimate business concepts."""
        return Agent(
            config=self.agents_config["gv1_concept_validator"],
            tools=[],  # No tools needed - just reasoning
            reasoning=True,  # Uses extended thinking for thorough analysis
            inject_date=True,
            max_iter=15,
            llm=LLM(model="openai/gpt-4o", temperature=0.3),
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def s1_brief_compiler(self) -> Agent:
        """S1: Brief Compiler - Compiles Founder's Brief with web research."""
        return Agent(
            config=self.agents_config["s1_brief_compiler"],
            tools=[TavilySearchTool()],  # Web search for market research
            reasoning=True,  # Synthesizes research into structured brief
            inject_date=True,
            max_iter=25,  # More iterations for research + compilation
            llm=LLM(model="openai/gpt-4o", temperature=0.5),
            verbose=True,
            allow_delegation=False,
        )

    # =========================================================================
    # TASKS
    # =========================================================================

    @task
    def validate_concept_legitimacy(self) -> Task:
        """Validate that the business concept is legitimate."""
        return Task(config=self.tasks_config["validate_concept_legitimacy"])

    @task
    def compile_founders_brief(self) -> Task:
        """Compile the Founder's Brief with web research."""
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
        Creates the BriefGenerationCrew with sequential process.

        Task Flow:
        1. GV1 validates concept legitimacy
        2. S1 compiles Founder's Brief (with TavilySearchTool for research)
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
