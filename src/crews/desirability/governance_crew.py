"""
GovernanceCrew - Phase 2/3/4: Governance and Oversight

This crew provides QA, security, and audit for validation phases.
Reused across Desirability, Feasibility, and Viability phases.

Agents:
- G1: QA Agent (Guardian) - Methodology compliance, creative QA
- G2: Security Agent (Guardian) - PII protection
- G3: Audit Agent (Guardian) - Decision logging

Guardian's role is oversight (board-level), not execution.

@story US-ADB05
"""

from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task

from shared.tools import MethodologyCheckTool, AnonymizerTool, LearningCardTool


@CrewBase
class GovernanceCrew:
    """
    GovernanceCrew provides oversight and governance.

    Produces:
    - QA reports (methodology compliance)
    - Security assessments (PII scrubbing)
    - Audit trails (decision logs)
    """

    agents_config = "config/governance_agents.yaml"
    tasks_config = "config/governance_tasks.yaml"

    # =========================================================================
    # AGENTS
    # =========================================================================

    @agent
    def g1_qa_agent(self) -> Agent:
        """G1: QA Agent - Methodology and creative QA."""
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
        """G2: Security Agent - PII protection."""
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
        """G3: Audit Agent - Decision logging."""
        return Agent(
            config=self.agents_config["g3_audit_agent"],
            tools=[LearningCardTool()],  # Capture learnings from decisions
            reasoning=False,  # Straightforward logging
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
    def methodology_compliance_check(self) -> Task:
        """Check methodology compliance."""
        return Task(config=self.tasks_config["methodology_compliance_check"])

    @task
    def creative_qa(self) -> Task:
        """QA creative assets (brand safety, accuracy)."""
        return Task(config=self.tasks_config["creative_qa"])

    @task
    def security_review(self) -> Task:
        """Review for PII and security concerns."""
        return Task(config=self.tasks_config["security_review"])

    @task
    def log_decisions(self) -> Task:
        """Log decisions for audit trail."""
        return Task(config=self.tasks_config["log_decisions"])

    # =========================================================================
    # CREW
    # =========================================================================

    @crew
    def crew(self) -> Crew:
        """
        Creates the GovernanceCrew with sequential process.

        Task Flow:
        1. G1 checks methodology compliance
        2. G1 QAs creative assets
        3. G2 reviews for security/PII
        4. G3 logs decisions
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
