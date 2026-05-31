from crewai import Agent, Task
from backend.agents.base import VoCoAgent


class AnalystAgent(VoCoAgent):
    name = "analyst"
    role = "Pattern Analyst"
    goal = "Find correlations and patterns across all retrieved enterprise data."
    backstory = """You are skilled at recognizing patterns across time-series and cross-system data.
    You identify which signals correlate with the problem, rank them by significance,
    and distinguish primary signals from noise. You always provide confidence scores."""

    def get_crewai_agent(self) -> Agent:
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            verbose=True,
            max_iter=2,
            allow_delegation=False
        )

    def get_task_description(self) -> str:
        return """Analyze the retrieved enterprise data to find patterns and correlations.

        For each signal, assess:
        - Does this correlate temporally with the problem? (time alignment)
        - Does this correlate across systems? (ServiceNow + Intune + Metrics)
        - What is the correlation strength? (0.0-1.0)
        - Is this a primary signal or a secondary effect?

        Rank all correlations by significance.
        Flag any anomalies (e.g. metrics far outside baseline)."""

    def get_expected_output(self) -> str:
        return "Ranked list of correlations with confidence scores and significance notes"

    def create_task(self, agent: Agent, context: list) -> Task:
        return Task(
            description=self.get_task_description(),
            agent=agent,
            context=context,
            expected_output=self.get_expected_output()
        )
