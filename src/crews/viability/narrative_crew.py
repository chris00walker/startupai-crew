"""
NarrativeSynthesisCrew - Phase 4: Pitch Narrative Generation

This crew transforms validation evidence into a Get Backed 10-slide
pitch narrative with claim-language Guardian alignment.

Agents:
- N1: Narrative Architect - Composes and finalizes the narrative
- N2: Evidence Mapper - Maps phase outputs to slide fields
- N3: Claim Guardian - Validates claims against evidence strength

@story US-NL01
"""

from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task

from src.shared.schemas.narrative import PitchNarrativeContent


@CrewBase
class NarrativeSynthesisCrew:
    """
    NarrativeSynthesisCrew transforms validation evidence into
    investor-ready pitch narratives.

    Produces:
    - Evidence-to-slide mapping with DO/SAY classification
    - Complete PitchNarrativeContent JSON (10 slides + cover + metadata)
    - Guardian-validated claims with auto-corrected language
    - Final structured output for storage in pitch_narratives.narrative_data
    """

    agents_config = "config/narrative_agents.yaml"
    tasks_config = "config/narrative_tasks.yaml"

    # =========================================================================
    # AGENTS
    # =========================================================================

    @agent
    def n1_narrative_architect(self) -> Agent:
        """N1: Narrative Architect - Composes pitch narrative."""
        return Agent(
            config=self.agents_config["n1_narrative_architect"],
            tools=[],
            reasoning=False,  # Narrative composition
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.7),  # Creative writing
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def n2_evidence_mapper(self) -> Agent:
        """N2: Evidence Mapper - Maps evidence to slide fields."""
        return Agent(
            config=self.agents_config["n2_evidence_mapper"],
            tools=[],
            reasoning=False,  # Evidence classification
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.3),  # Precise mapping
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def n3_claim_guardian(self) -> Agent:
        """N3: Claim Guardian - Validates claim-language alignment."""
        return Agent(
            config=self.agents_config["n3_claim_guardian"],
            tools=[],
            reasoning=True,  # Reasoning for claim validation
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.1),  # Strict validation
            verbose=True,
            allow_delegation=False,
        )

    # =========================================================================
    # TASKS
    # =========================================================================

    @task
    def map_evidence_to_slides(self) -> Task:
        """Map validation evidence to 10-slide framework fields."""
        return Task(config=self.tasks_config["map_evidence_to_slides"])

    @task
    def compose_narrative(self) -> Task:
        """Compose complete PitchNarrativeContent JSON."""
        return Task(config=self.tasks_config["compose_narrative"])

    @task
    def validate_claims(self) -> Task:
        """Guardian validation of all narrative claims."""
        return Task(config=self.tasks_config["validate_claims"])

    @task
    def finalize_narrative(self) -> Task:
        """Finalize narrative with Guardian corrections applied."""
        return Task(
            config=self.tasks_config["finalize_narrative"],
            output_pydantic=PitchNarrativeContent,
        )

    # =========================================================================
    # CREW
    # =========================================================================

    @crew
    def crew(self) -> Crew:
        """
        Creates the NarrativeSynthesisCrew with sequential process.

        Task Flow:
        1. N2 maps all phase evidence to 10-slide framework fields
        2. N1 composes complete PitchNarrativeContent from mapping
        3. N3 validates claims against evidence strength, auto-corrects
        4. N1 finalizes narrative with corrections → output_pydantic
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
