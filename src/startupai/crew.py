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
    
    Agents:
    - Research Agent: Evidence discovery and synthesis
    - Analysis Agent: Pattern recognition and insights
    - Reporting Agent: Professional report generation
    
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
        """Research Agent - Evidence discovery and synthesis."""
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
    def reporting_agent(self) -> Agent:
        """Reporting Agent - Professional report generation."""
        return Agent(
            config=self.agents_config['reporting_agent'], # type: ignore[index]
            verbose=True,
        )
    
    @task
    def research_task(self) -> Task:
        """Task for researching the strategic question."""
        return Task(
            config=self.tasks_config['research_task'], # type: ignore[index]
            agent=self.research_agent(),
        )
    
    @task
    def analysis_task(self) -> Task:
        """Task for analyzing research findings."""
        return Task(
            config=self.tasks_config['analysis_task'], # type: ignore[index]
            agent=self.analysis_agent(),
        )
    
    @task
    def report_task(self) -> Task:
        """Task for generating the final report."""
        return Task(
            config=self.tasks_config['report_task'], # type: ignore[index]
            agent=self.reporting_agent(),
            output_file='output/strategic_analysis.md',
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
