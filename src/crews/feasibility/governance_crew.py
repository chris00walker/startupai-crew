"""
FeasibilityGovernanceCrew - Phase 3: Feasibility - Gate Validation

This crew validates the feasibility assessment and security posture.
Phase 3 version has only G1 and G2 (no G3 Audit).

Agents:
- G1: QA Agent (Guardian) - Gate validation, methodology compliance
- G2: Security Agent (Guardian) - Architecture security review
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class FeasibilityGovernanceCrew:
    """
    FeasibilityGovernanceCrew validates feasibility gate readiness.

    Produces:
    - Methodology compliance report
    - Security assessment
    - Gate readiness determination
    """

    agents_config = "config/governance_agents.yaml"
    tasks_config = "config/governance_tasks.yaml"

    # =========================================================================
    # AGENTS
    # =========================================================================

    @agent
    def g1_qa_agent(self) -> Agent:
        """G1: QA Agent - Gate validation."""
        return Agent(
            config=self.agents_config["g1_qa_agent"],
            verbose=True,
        )

    @agent
    def g2_security_agent(self) -> Agent:
        """G2: Security Agent - Architecture security review."""
        return Agent(
            config=self.agents_config["g2_security_agent"],
            verbose=True,
        )

    # =========================================================================
    # TASKS
    # =========================================================================

    @task
    def validate_assessment_methodology(self) -> Task:
        """Validate technical assessment follows VPD methodology."""
        return Task(config=self.tasks_config["validate_assessment_methodology"])

    @task
    def verify_constraint_documentation(self) -> Task:
        """Ensure all constraints are properly documented."""
        return Task(config=self.tasks_config["verify_constraint_documentation"])

    @task
    def review_architecture_security(self) -> Task:
        """Review proposed architecture security posture."""
        return Task(config=self.tasks_config["review_architecture_security"])

    @task
    def confirm_gate_readiness(self) -> Task:
        """Confirm phase exit criteria are met."""
        return Task(config=self.tasks_config["confirm_gate_readiness"])

    # =========================================================================
    # CREW
    # =========================================================================

    @crew
    def crew(self) -> Crew:
        """
        Creates the FeasibilityGovernanceCrew with sequential process.

        Task Flow:
        1. G1 validates assessment methodology
        2. G1 verifies constraint documentation
        3. G2 reviews architecture security
        4. G1 confirms gate readiness
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
