"""
SynthesisCrew - Phase 4: Viability - Evidence Synthesis and Decision

This crew synthesizes evidence and manages final HITL decisions.

Agents:
- C1: Product PM (Compass) - Synthesize evidence, propose options
- C2: Human Approval Agent (Compass) - Manage HITL decision
- C3: Roadmap Writer (Compass) - Document decision and next steps

@story US-AG13
"""

from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class SynthesisCrew:
    """
    SynthesisCrew synthesizes evidence and manages final decisions.

    Produces:
    - Evidence synthesis
    - Decision options
    - HITL presentation
    - Final decision documentation
    - Flywheel learnings
    """

    agents_config = "config/synthesis_agents.yaml"
    tasks_config = "config/synthesis_tasks.yaml"

    # =========================================================================
    # AGENTS
    # =========================================================================

    @agent
    def c1_product_pm(self) -> Agent:
        """C1: Product PM - Evidence synthesis."""
        return Agent(
            config=self.agents_config["c1_product_pm"],
            tools=[],
            reasoning=False,  # Synthesis without tools
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.7),  # Synthesis/strategy
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def c2_human_approval(self) -> Agent:
        """C2: Human Approval Agent - HITL management."""
        return Agent(
            config=self.agents_config["c2_human_approval"],
            tools=[],
            reasoning=False,  # HITL presentation
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.5),
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def c3_roadmap_writer(self) -> Agent:
        """C3: Roadmap Writer - Documentation."""
        return Agent(
            config=self.agents_config["c3_roadmap_writer"],
            tools=[],
            reasoning=False,  # Documentation
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.7),  # Synthesis
            verbose=True,
            allow_delegation=False,
        )

    # =========================================================================
    # TASKS
    # =========================================================================

    @task
    def synthesize_evidence(self) -> Task:
        """Synthesize all phase evidence."""
        return Task(config=self.tasks_config["synthesize_evidence"])

    @task
    def propose_options(self) -> Task:
        """Generate pivot/proceed options."""
        return Task(config=self.tasks_config["propose_options"])

    @task
    def present_viability_decision(self) -> Task:
        """Present options for HITL decision."""
        return Task(config=self.tasks_config["present_viability_decision"])

    @task
    def document_decision(self) -> Task:
        """Document the final decision."""
        return Task(config=self.tasks_config["document_decision"])

    @task
    def capture_learnings(self) -> Task:
        """Capture learnings for flywheel."""
        return Task(config=self.tasks_config["capture_learnings"])

    # =========================================================================
    # CREW
    # =========================================================================

    @crew
    def crew(self) -> Crew:
        """
        Creates the SynthesisCrew with sequential process.

        Task Flow:
        1. C1 synthesizes all phase evidence
        2. C1 proposes pivot/proceed options
        3. C2 presents for HITL decision
        4. C3 documents the decision
        5. C3 captures learnings for flywheel
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
