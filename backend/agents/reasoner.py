from crewai import Agent, Task
from backend.agents.base import VoCoAgent


class ReasonerAgent(VoCoAgent):
    name = "reasoner"
    role = "Root Cause Analyzer"
    goal = "Perform multi-hop reasoning to determine root cause. Explain WHY, not just WHAT."
    backstory = """You are an expert at root cause analysis using structured multi-hop reasoning.
    You follow a strict reasoning protocol: OBSERVE -> CORRELATE -> ANALYZE -> CONCLUDE -> RECOMMEND.
    You show every step of your reasoning. You provide confidence scores.
    You distinguish immediate causes from contributing factors."""

    def get_crewai_agent(self) -> Agent:
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            verbose=True,
            max_iter=4,
            allow_delegation=False
        )

    def get_task_description(self) -> str:
        return """Perform multi-hop root cause analysis using this exact protocol:

        1. OBSERVE: What is the impact? How many affected? When did it start?
        2. CORRELATE: Which signals align with the problem? (From analyst output)
        3. ANALYZE: Why would those signals cause this impact? Walk through the mechanism.
        4. CONCLUDE: State the primary root cause in one sentence.
        5. RECOMMEND:
           - Immediate action (minutes/hours, to stop the bleeding)
           - Same-day action (hours, to prevent recurrence today)
           - Sprint action (days/weeks, to fix root cause permanently)

        Provide an overall confidence score (0.0-1.0).
        Be specific — generic answers are not acceptable."""

    def get_expected_output(self) -> str:
        return "Root cause analysis with full reasoning chain, actions at 3 time horizons, and confidence score"

    def create_task(self, agent: Agent, context: list) -> Task:
        return Task(
            description=self.get_task_description(),
            agent=agent,
            context=context,
            expected_output=self.get_expected_output()
        )
