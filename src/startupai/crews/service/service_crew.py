"""
Service Crew - Led by Sage (CSO).
Handles entrepreneur onboarding and initial brief capture.
"""

from crewai import Crew, Agent, Task
from crewai.project import CrewBase


class ServiceCrew(CrewBase):
    """Sage's Service Crew for client onboarding."""

    def crew(self) -> Crew:
        """Create the Service Crew."""
        # Placeholder implementation
        agent = Agent(
            role="Founder Onboarding Agent",
            goal="Capture entrepreneur input and create structured brief",
            backstory="Expert in understanding startup ideas and translating them to structured format"
        )

        task = Task(
            description="Capture and structure the entrepreneur's business idea",
            expected_output="Structured brief with business idea, segments, and assumptions",
            agent=agent
        )

        return Crew(
            agents=[agent],
            tasks=[task],
            verbose=True
        )