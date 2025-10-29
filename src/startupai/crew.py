"""
StartupAI CrewAI Crew - Pure AMP Implementation
Standalone CrewAI automation with no external dependencies
Designed to run exclusively on CrewAI AMP platform
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class StartupAICrew:
    """
    StartupAI Evidence-Led Strategy Crew - Pure Implementation
    
    Standalone CrewAI automation for AMP deployment.
    No external dependencies (Supabase, frontend, custom tools).
    
    6 Specialized Agents:
    - Research Agent: Evidence discovery and coordination
    - Analysis Agent: Pattern recognition and insights
    - Validation Agent: Evidence quality verification
    - Synthesis Agent: Insight combination and narratives
    - Reporting Agent: Professional report generation
    - Orchestration Agent: Workflow coordination
    
    Inputs:
    - strategic_question: The business question to analyze
    - project_context: Background information about the project
    
    Output:
    - Comprehensive strategic analysis report in markdown format
    """
    
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    
    @agent
    def research_agent(self) -> Agent:
        """Research Agent - Evidence discovery and coordination."""
        return Agent(
            config=self.agents_config['research_agent'], # type: ignore[index]
            verbose=True,
        )
    
    @agent
    def analysis_agent(self) -> Agent:
        """Analysis Agent - Pattern recognition and insights."""
        return Agent(
            config=self.agents_config['analysis_agent'], # type: ignore[index]
            verbose=True,
        )
    
    @agent
    def validation_agent(self) -> Agent:
        """Validation Agent - Evidence quality verification."""
        return Agent(
            config=self.agents_config['validation_agent'], # type: ignore[index]
            verbose=True,
        )
    
    @agent
    def synthesis_agent(self) -> Agent:
        """Synthesis Agent - Insight combination."""
        return Agent(
            config=self.agents_config['synthesis_agent'], # type: ignore[index]
            verbose=True,
        )
    
    @agent
    def reporting_agent(self) -> Agent:
        """Reporting Agent - Professional report generation."""
        return Agent(
            config=self.agents_config['reporting_agent'], # type: ignore[index]
            verbose=True,
        )
    
    @agent
    def orchestration_agent(self) -> Agent:
        """Orchestration Agent - Workflow coordination."""
        return Agent(
            config=self.agents_config['orchestration_agent'], # type: ignore[index]
            verbose=True,
        )
    
    @task
    def evidence_collection_task(self) -> Task:
        """Task for evidence discovery and collection."""
        return Task(
            config=self.tasks_config['evidence_collection'], # type: ignore[index]
            agent=self.research_agent(),
        )
    
    @task
    def evidence_analysis_task(self) -> Task:
        """Task for analyzing collected evidence."""
        return Task(
            config=self.tasks_config['evidence_analysis'], # type: ignore[index]
            agent=self.analysis_agent(),
        )
    
    @task
    def evidence_validation_task(self) -> Task:
        """Task for validating evidence quality."""
        return Task(
            config=self.tasks_config['evidence_validation'], # type: ignore[index]
            agent=self.validation_agent(),
        )
    
    @task
    def insight_synthesis_task(self) -> Task:
        """Task for synthesizing insights."""
        return Task(
            config=self.tasks_config['insight_synthesis'], # type: ignore[index]
            agent=self.synthesis_agent(),
        )
    
    @task
    def report_generation_task(self) -> Task:
        """Task for generating the final report."""
        return Task(
            config=self.tasks_config['report_generation'], # type: ignore[index]
            agent=self.reporting_agent(),
            output_file='output/strategic_analysis.md',
        )
    
    @task
    def workflow_orchestration_task(self) -> Task:
        """Task for orchestrating the workflow."""
        return Task(
            config=self.tasks_config['workflow_orchestration'], # type: ignore[index]
            agent=self.orchestration_agent(),
        )
    
    @crew
    def crew(self) -> Crew:
        """
        Creates the StartupAI Crew with sequential process.
        This is the method CrewAI AMP calls.
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
