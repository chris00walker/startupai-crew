"""
Governance Crew - Led by Guardian (CGO).
Handles quality assurance, compliance, and accountability.

Now equipped with Flywheel learning tools for pattern capture!
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# Import learning tools for Flywheel system
from startupai.tools.learning_capture import LearningCaptureTool
from startupai.tools.learning_retrieval import LearningRetrievalTool
from startupai.tools.anonymizer import AnonymizerTool


@CrewBase
class GovernanceCrew:
    """
    Guardian's Governance Crew for quality and compliance.

    This crew performs quality audits, monitors process compliance,
    and captures learnings for the Flywheel system.

    Now uses learning tools for:
    - Anonymizing PII before storage
    - Capturing validation patterns and outcomes
    - Retrieving relevant past learnings for QA
    """

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        """Initialize crew with Flywheel learning tools."""
        self._learning_capture_tool = LearningCaptureTool()
        self._learning_retrieval_tool = LearningRetrievalTool()
        self._anonymizer_tool = AnonymizerTool()

    @agent
    def qa_auditor(self) -> Agent:
        return Agent(
            config=self.agents_config['qa_auditor'],
            tools=[self._learning_retrieval_tool],
            verbose=True
        )

    @agent
    def compliance_monitor(self) -> Agent:
        return Agent(
            config=self.agents_config['compliance_monitor'],
            tools=[self._anonymizer_tool],
            verbose=True
        )

    @agent
    def accountability_tracker(self) -> Agent:
        return Agent(
            config=self.agents_config['accountability_tracker'],
            tools=[
                self._learning_capture_tool,
                self._learning_retrieval_tool,
                self._anonymizer_tool,
            ],
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
