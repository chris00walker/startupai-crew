"""
Governance Crew - Led by Guardian (CGO).
Handles quality assurance, compliance, and accountability.

Now equipped with:
- Flywheel learning tools for pattern capture
- HITL tools for creative and methodology review
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# Import learning tools for Flywheel system
from startupai.tools.learning_capture import LearningCaptureTool
from startupai.tools.learning_retrieval import LearningRetrievalTool
from startupai.tools.anonymizer import AnonymizerTool

# Import HITL tools for creative review
from startupai.tools.guardian_review import GuardianReviewTool
from startupai.tools.methodology_check import MethodologyCheckTool


@CrewBase
class GovernanceCrew:
    """
    Guardian's Governance Crew for quality and compliance.

    This crew performs quality audits, monitors process compliance,
    and captures learnings for the Flywheel system.

    Now uses:
    - Learning tools for anonymization and pattern capture
    - GuardianReviewTool for auto-QA of creatives (landing pages, ads)
    - MethodologyCheckTool for VPC/BMC validation
    """

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        """Initialize crew with learning and HITL tools."""
        # Flywheel learning tools
        self._learning_capture_tool = LearningCaptureTool()
        self._learning_retrieval_tool = LearningRetrievalTool()
        self._anonymizer_tool = AnonymizerTool()

        # HITL review tools
        self._guardian_review_tool = GuardianReviewTool()
        self._methodology_check_tool = MethodologyCheckTool()

    @agent
    def qa_auditor(self) -> Agent:
        return Agent(
            config=self.agents_config['qa_auditor'],
            tools=[
                self._learning_retrieval_tool,
                self._guardian_review_tool,
                self._methodology_check_tool,
            ],
            verbose=True
        )

    @agent
    def compliance_monitor(self) -> Agent:
        return Agent(
            config=self.agents_config['compliance_monitor'],
            tools=[
                self._anonymizer_tool,
                self._methodology_check_tool,
            ],
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

    @task
    def review_creatives(self) -> Task:
        return Task(
            config=self.tasks_config['review_creatives']
        )

    @task
    def validate_methodology(self) -> Task:
        return Task(
            config=self.tasks_config['validate_methodology']
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
