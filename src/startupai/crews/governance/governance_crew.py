"""
Governance Crew - Led by Guardian (CGO).
Handles quality assurance, compliance, and accountability.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class GovernanceCrew:
    """
    Guardian's Governance Crew for quality and compliance.

    This crew performs quality audits, monitors process compliance,
    and captures learnings for the Flywheel system.
    """

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def qa_auditor(self) -> Agent:
        return Agent(
            config=self.agents_config['qa_auditor'],
            verbose=True
        )

    @agent
    def compliance_monitor(self) -> Agent:
        return Agent(
            config=self.agents_config['compliance_monitor'],
            verbose=True
        )

    @agent
    def accountability_tracker(self) -> Agent:
        return Agent(
            config=self.agents_config['accountability_tracker'],
            verbose=True
        )

    @task
    def quality_review(self) -> Task:
        return Task(
            config=self.tasks_config['quality_review']
        )

    @task
    def final_audit(self) -> Task:
        return Task(
            config=self.tasks_config['final_audit']
        )

    @task
    def track_progress(self) -> Task:
        return Task(
            config=self.tasks_config['track_progress']
        )

    @task
    def capture_learnings(self) -> Task:
        return Task(
            config=self.tasks_config['capture_learnings']
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Governance Crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
