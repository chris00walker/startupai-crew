"""
ViabilityGovernanceCrew - Phase 4: Viability - Final Governance

This crew provides final validation, security scrubbing, and audit.

Agents:
- G1: QA Agent (Guardian) - Final validation compliance
- G2: Security Agent (Guardian) - PII scrubbing
- G3: Audit Agent (Guardian) - Persist learnings to flywheel

@story US-AVB05
"""

from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task

from shared.tools import MethodologyCheckTool, AnonymizerTool


@CrewBase
class ViabilityGovernanceCrew:
    """
    ViabilityGovernanceCrew provides final governance and audit.

    Produces:
    - Final validation compliance report
    - PII scrubbing verification
    - Audit trail
    - Flywheel persistence confirmation
    """

    agents_config = "config/governance_agents.yaml"
    tasks_config = "config/governance_tasks.yaml"

    # =========================================================================
    # AGENTS
    # =========================================================================

    @agent
    def g1_qa_agent(self) -> Agent:
        """G1: QA Agent - Final validation."""
        return Agent(
            config=self.agents_config["g1_qa_agent"],
            tools=[MethodologyCheckTool()],  # VPC validation tool
            reasoning=True,
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.1),  # Strict QA
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def g2_security_agent(self) -> Agent:
        """G2: Security Agent - PII scrubbing."""
        return Agent(
            config=self.agents_config["g2_security_agent"],
            tools=[AnonymizerTool()],
            reasoning=True,  # PII detection and anonymization
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.1),  # Strict QA
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def g3_audit_agent(self) -> Agent:
        """G3: Audit Agent - Flywheel persistence."""
        return Agent(
            config=self.agents_config["g3_audit_agent"],
            tools=[],
            reasoning=False,  # Persistence/logging
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.1),  # Strict QA
            verbose=True,
            allow_delegation=False,
        )

    # =========================================================================
    # TASKS
    # =========================================================================

    @task
    def final_validation_check(self) -> Task:
        """Final validation compliance check."""
        return Task(config=self.tasks_config["final_validation_check"])

    @task
    def scrub_pii(self) -> Task:
        """Scrub PII from outputs before persistence."""
        return Task(config=self.tasks_config["scrub_pii"])

    @task
    def create_audit_trail(self) -> Task:
        """Create complete audit trail."""
        return Task(config=self.tasks_config["create_audit_trail"])

    @task
    def persist_to_flywheel(self) -> Task:
        """Persist learnings to flywheel."""
        return Task(config=self.tasks_config["persist_to_flywheel"])

    # =========================================================================
    # CREW
    # =========================================================================

    @crew
    def crew(self) -> Crew:
        """
        Creates the ViabilityGovernanceCrew with sequential process.

        Task Flow:
        1. G1 performs final validation check
        2. G2 scrubs PII from outputs
        3. G3 creates audit trail
        4. G3 persists learnings to flywheel
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
