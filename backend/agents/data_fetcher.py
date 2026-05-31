from crewai import Agent, Task
from backend.agents.base import VoCoAgent
from backend.tools import all_tools


class DataFetcherAgent(VoCoAgent):
    name = "data_fetcher"
    role = "Enterprise Data Fetcher"
    goal = "Retrieve complete, relevant data from all enterprise systems for the question asked."
    backstory = """You are an expert at querying enterprise systems.
    You systematically pull from ServiceNow, M365, Intune, infrastructure metrics,
    and incident context to build a complete picture. You never miss a relevant signal."""

    def get_crewai_agent(self) -> Agent:
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            tools=all_tools,
            verbose=True,
            max_iter=3,
            allow_delegation=False
        )

    def get_task_description(self) -> str:
        return """Query ALL enterprise systems for data about: {question}

        You MUST retrieve from each system:
        - ServiceNow: incidents, ticket counts, SLA status, business impact
        - M365: enrollment metrics, failure rates, error codes
        - Intune: device states, provisioning status, retry history
        - Infrastructure Metrics: DNS latency, network health, failover state
        - Incident Context: timeline, alert history, team communication

        Return all raw data. Do not interpret yet — just gather."""

    def get_expected_output(self) -> str:
        return "Complete aggregated data from all 5 enterprise systems"

    def create_task(self, agent: Agent) -> Task:
        return Task(
            description=self.get_task_description(),
            agent=agent,
            expected_output=self.get_expected_output()
        )
