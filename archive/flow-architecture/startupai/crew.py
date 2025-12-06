"""
StartupAI Value Proposition Design Crew - Pure AMP Implementation
Transforms startup ideas into validated, evidence-based value propositions
Designed to run exclusively on CrewAI AMP platform
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class StartupAICrew:
    """
    StartupAI Value Proposition Design Crew - Pure Implementation
    
    Standalone CrewAI automation for AMP deployment.
    No external dependencies (Supabase, frontend, custom tools).
    
    6 Specialized Agents:
    - Onboarding Agent: Entrepreneur interview and brief creation
    - Customer Researcher: Customer Jobs, Pains, Gains discovery
    - Competitor Analyst: Market positioning and differentiation
    - Value Designer: Value Proposition Canvas creation
    - Validation Agent: 3-tier validation roadmap design
    - QA Agent: Quality assurance and framework compliance
    
    Inputs:
    - entrepreneur_input: Founder's startup idea and context
    
    Output:
    - Complete Value Proposition Design package with validation roadmap
    """
    
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    
    @agent
    def onboarding_agent(self) -> Agent:
        """Onboarding Agent - Entrepreneur interview and brief creation."""
        return Agent(
            config=self.agents_config['onboarding_agent'], # type: ignore[index]
            verbose=True,
        )
    
    @agent
    def customer_researcher(self) -> Agent:
        """Customer Researcher - Customer profile development."""
        return Agent(
            config=self.agents_config['customer_researcher'], # type: ignore[index]
            verbose=True,
        )
    
    @agent
    def competitor_analyst(self) -> Agent:
        """Competitor Analyst - Market positioning analysis."""
        return Agent(
            config=self.agents_config['competitor_analyst'], # type: ignore[index]
            verbose=True,
        )
    
    @agent
    def value_designer(self) -> Agent:
        """Value Designer - Value Proposition Canvas creation."""
        return Agent(
            config=self.agents_config['value_designer'], # type: ignore[index]
            verbose=True,
        )
    
    @agent
    def validation_agent(self) -> Agent:
        """Validation Agent - 3-tier validation roadmap design."""
        return Agent(
            config=self.agents_config['validation_agent'], # type: ignore[index]
            verbose=True,
        )
    
    @agent
    def qa_agent(self) -> Agent:
        """QA Agent - Quality assurance and framework compliance."""
        return Agent(
            config=self.agents_config['qa_agent'], # type: ignore[index]
            verbose=True,
        )
    
    @task
    def onboarding_task(self) -> Task:
        """Task for conducting entrepreneur onboarding."""
        return Task(
            config=self.tasks_config['onboarding_task'], # type: ignore[index]
            agent=self.onboarding_agent(),
        )
    
    @task
    def customer_research_task(self) -> Task:
        """Task for researching customer profile."""
        return Task(
            config=self.tasks_config['customer_research_task'], # type: ignore[index]
            agent=self.customer_researcher(),
        )
    
    @task
    def competitor_analysis_task(self) -> Task:
        """Task for analyzing competitive landscape."""
        return Task(
            config=self.tasks_config['competitor_analysis_task'], # type: ignore[index]
            agent=self.competitor_analyst(),
        )
    
    @task
    def value_design_task(self) -> Task:
        """Task for designing value proposition."""
        return Task(
            config=self.tasks_config['value_design_task'], # type: ignore[index]
            agent=self.value_designer(),
        )
    
    @task
    def validation_task(self) -> Task:
        """Task for creating validation roadmap."""
        return Task(
            config=self.tasks_config['validation_task'], # type: ignore[index]
            agent=self.validation_agent(),
        )
    
    @task
    def qa_task(self) -> Task:
        """Task for quality assurance review."""
        return Task(
            config=self.tasks_config['qa_task'], # type: ignore[index]
            agent=self.qa_agent(),
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
