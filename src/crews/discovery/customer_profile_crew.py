"""
CustomerProfileCrew - Phase 1: VPC Discovery - Jobs, Pains, Gains Discovery

This crew researches and ranks customer Jobs, Pains, and Gains to build
the Customer Profile (right side of Value Proposition Canvas).

Agents:
- J1: JTBD Researcher (Sage) - Discover jobs (functional, emotional, social)
- J2: Job Ranking Agent (Sage) - Rank jobs by importance
- PAIN_RES: Pain Researcher (Sage) - Discover pains
- PAIN_RANK: Pain Ranking Agent (Sage) - Rank pains by severity
- GAIN_RES: Gain Researcher (Sage) - Discover gains
- GAIN_RANK: Gain Ranking Agent (Sage) - Rank gains by importance
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from pydantic import BaseModel
from typing import Optional

from src.state.models import CustomerProfile


@CrewBase
class CustomerProfileCrew:
    """
    CustomerProfileCrew builds the Customer Profile from VPD framework.

    Produces CustomerProfile with:
    - Ranked Jobs (functional, emotional, social)
    - Ranked Pains (by severity)
    - Ranked Gains (by importance)
    """

    agents_config = "config/customer_profile_agents.yaml"
    tasks_config = "config/customer_profile_tasks.yaml"

    # =========================================================================
    # AGENTS
    # =========================================================================

    @agent
    def j1_jtbd_researcher(self) -> Agent:
        """J1: JTBD Researcher - Discovers customer jobs."""
        return Agent(
            config=self.agents_config["j1_jtbd_researcher"],
            verbose=True,
        )

    @agent
    def j2_job_ranking(self) -> Agent:
        """J2: Job Ranking Agent - Ranks jobs by importance."""
        return Agent(
            config=self.agents_config["j2_job_ranking"],
            verbose=True,
        )

    @agent
    def pain_researcher(self) -> Agent:
        """PAIN_RES: Pain Researcher - Discovers customer pains."""
        return Agent(
            config=self.agents_config["pain_researcher"],
            verbose=True,
        )

    @agent
    def pain_ranking(self) -> Agent:
        """PAIN_RANK: Pain Ranking Agent - Ranks pains by severity."""
        return Agent(
            config=self.agents_config["pain_ranking"],
            verbose=True,
        )

    @agent
    def gain_researcher(self) -> Agent:
        """GAIN_RES: Gain Researcher - Discovers customer gains."""
        return Agent(
            config=self.agents_config["gain_researcher"],
            verbose=True,
        )

    @agent
    def gain_ranking(self) -> Agent:
        """GAIN_RANK: Gain Ranking Agent - Ranks gains by importance."""
        return Agent(
            config=self.agents_config["gain_ranking"],
            verbose=True,
        )

    # =========================================================================
    # TASKS
    # =========================================================================

    @task
    def discover_jobs(self) -> Task:
        """Discover all customer jobs using JTBD methodology."""
        return Task(config=self.tasks_config["discover_jobs"])

    @task
    def rank_jobs(self) -> Task:
        """Rank jobs by importance."""
        return Task(config=self.tasks_config["rank_jobs"])

    @task
    def discover_pains(self) -> Task:
        """Discover customer pains."""
        return Task(config=self.tasks_config["discover_pains"])

    @task
    def rank_pains(self) -> Task:
        """Rank pains by severity."""
        return Task(config=self.tasks_config["rank_pains"])

    @task
    def discover_gains(self) -> Task:
        """Discover customer gains."""
        return Task(config=self.tasks_config["discover_gains"])

    @task
    def rank_gains(self) -> Task:
        """Rank gains by importance."""
        return Task(config=self.tasks_config["rank_gains"])

    @task
    def compile_customer_profile(self) -> Task:
        """Compile final Customer Profile."""
        return Task(
            config=self.tasks_config["compile_customer_profile"],
            output_pydantic=CustomerProfile,
        )

    # =========================================================================
    # CREW
    # =========================================================================

    @crew
    def crew(self) -> Crew:
        """
        Creates the CustomerProfileCrew with sequential process.

        Task Flow:
        1. J1 discovers jobs → J2 ranks jobs
        2. PAIN_RES discovers pains → PAIN_RANK ranks pains
        3. GAIN_RES discovers gains → GAIN_RANK ranks gains
        4. Compile into CustomerProfile
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
