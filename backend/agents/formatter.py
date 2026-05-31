from crewai import Agent, Task
from backend.agents.base import VoCoAgent


class FormatterAgent(VoCoAgent):
    name = "formatter"
    role = "Output Formatter"
    goal = "Convert technical analysis into a clear, structured output for enterprise users."
    backstory = """You are an expert at communicating technical findings to enterprise stakeholders.
    You create concise summaries, clear action items, and business impact statements.
    You format for readability — no walls of text.
    Your output must be directly actionable."""

    def get_crewai_agent(self) -> Agent:
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            verbose=True,
            max_iter=1,
            allow_delegation=False
        )

    def get_task_description(self) -> str:
        return """Format the complete analysis into this exact structure:

        SUMMARY: [1-2 sentences. What happened and what is the root cause.]

        ROOT_CAUSE: [One clear sentence.]

        CONTRIBUTING_FACTORS:
        - [Factor 1]
        - [Factor 2]
        - [Factor 3]

        REASONING_CHAIN:
        - OBSERVE: [...]
        - CORRELATE: [...]
        - ANALYZE: [...]
        - CONCLUDE: [...]

        ACTIONS:
        - IMMEDIATE ([timeframe]): [Specific action]
        - SHORT_TERM ([timeframe]): [Specific action]
        - LONG_TERM ([timeframe]): [Specific action]

        CONFIDENCE: [0.0-1.0]
        BUSINESS_IMPACT: [One sentence on business risk if not resolved]

        Do not deviate from this format. It is parsed by the frontend."""

    def get_expected_output(self) -> str:
        return "Structured output in exact format above"

    def create_task(self, agent: Agent, context: list) -> Task:
        return Task(
            description=self.get_task_description(),
            agent=agent,
            context=context,
            expected_output=self.get_expected_output()
        )
