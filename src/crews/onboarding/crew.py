"""
OnboardingCrew - Phase 0: Founder's Brief Creation

This crew transforms the Founder's raw idea into a structured Founder's Brief,
the prime artifact that informs all subsequent validation phases.

Two-Layer Architecture:
- Layer 1: "Alex" chat (Vercel AI SDK in product app) conducts conversational interview
- Layer 2: This crew (OnboardingCrew) validates and compiles the Founder's Brief

Agents:
- O1: Interview Gap Analyzer Agent (Sage) - Analyzes Alex conversation for completeness
- GV1: Concept Validator Agent (Guardian) - Legitimacy screening
- GV2: Intent Verification Agent (Guardian) - Verifies capture accuracy
- S1: Brief Compiler Agent (Sage) - Synthesizes into Founder's Brief

HITL Checkpoint: approve_founders_brief

@story US-AB01
"""

from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task

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
    def o1_interview_gap_analyzer(self) -> Agent:
        """O1: Interview Gap Analyzer - Analyzes Alex conversation for completeness."""
        return Agent(
            config=self.agents_config["o1_interview_gap_analyzer"],
            tools=[],  # No tools needed - analyzes provided transcript
            reasoning=True,  # Step-by-step analysis of transcript gaps
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.3),  # Lower temp for consistent analysis
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def gv1_concept_validator(self) -> Agent:
        """GV1: Concept Validator Agent - Screens for legitimacy."""
        return Agent(
            config=self.agents_config["gv1_concept_validator"],
            tools=[],
            reasoning=True,  # Rigorous QA decisions
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.1),
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def gv2_intent_verification(self) -> Agent:
        """GV2: Intent Verification Agent - Ensures accurate capture."""
        return Agent(
            config=self.agents_config["gv2_intent_verification"],
            tools=[],
            reasoning=True,  # Rigorous verification
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.1),
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def s1_brief_compiler(self) -> Agent:
        """S1: Brief Compiler Agent - Synthesizes the Founder's Brief."""
        return Agent(
            config=self.agents_config["s1_brief_compiler"],
            tools=[],
            reasoning=False,  # Straightforward synthesis
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.7),
            verbose=True,
            allow_delegation=False,
        )

    # =========================================================================
    # TASKS
    # =========================================================================

    @task
    def analyze_interview_gaps(self) -> Task:
        """Analyze Alex conversation transcript for gaps in the 7 interview areas."""
        return Task(
            config=self.tasks_config["analyze_interview_gaps"],
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
        1. O1 analyzes Alex conversation for gaps (transcript already collected by product app)
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


def run_onboarding_crew(
    entrepreneur_input: str,
    conversation_transcript: str = "",
    user_type: str = "founder",
) -> FoundersBrief:
    """
    Execute the OnboardingCrew to generate a Founder's Brief.

    Two-layer architecture:
    - Layer 1: "Alex" chat in product app collects the conversation_transcript
    - Layer 2: This crew validates and compiles the Founder's Brief

    Args:
        entrepreneur_input: Extracted data from Alex interview (structured summary)
        conversation_transcript: Full conversation history from Alex chat (JSON)
        user_type: "founder" or "consultant"

    Returns:
        FoundersBrief: Structured brief ready for HITL approval
    """
    crew = OnboardingCrew()
    result = crew.crew().kickoff(
        inputs={
            "entrepreneur_input": entrepreneur_input,
            "conversation_transcript": conversation_transcript,
            "user_type": user_type,
        }
    )
    return result.pydantic
