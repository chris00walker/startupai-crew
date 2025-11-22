"""
Analysis Crew - Led by Sage (CSO).
Analyzes customer segments and competitive landscape.
"""

from crewai import Crew, Agent, Task
from crewai.project import CrewBase


class AnalysisCrew(CrewBase):
    """Sage's Analysis Crew for customer and competitor research."""

    def crew(self) -> Crew:
        """Create the Analysis Crew."""
        # Placeholder implementation
        customer_researcher = Agent(
            role="Customer Researcher",
            goal="Analyze customer Jobs, Pains, and Gains",
            backstory="Expert in customer development and Jobs-to-be-Done framework"
        )

        competitor_analyst = Agent(
            role="Competitor Analyst",
            goal="Map competitive landscape and positioning",
            backstory="Expert in competitive analysis and market positioning"
        )

        customer_task = Task(
            description="Research customer segment and create profile",
            expected_output="Customer Profile with Jobs, Pains, Gains",
            agent=customer_researcher
        )

        competitor_task = Task(
            description="Analyze competitors and market positioning",
            expected_output="Competitive analysis report",
            agent=competitor_analyst
        )

        return Crew(
            agents=[customer_researcher, competitor_analyst],
            tasks=[customer_task, competitor_task],
            verbose=True
        )