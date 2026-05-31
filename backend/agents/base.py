"""Base class for all VoCo agents. Designed for CrewAI with LangGraph migration path."""

from abc import ABC, abstractmethod


class VoCoAgent(ABC):
    """
    Base class for all VoCo agents.
    Inheriting this ensures portability to LangGraph later.
    """
    name: str
    role: str
    goal: str
    backstory: str

    @abstractmethod
    def get_crewai_agent(self):
        """Return configured CrewAI Agent instance."""
        pass

    @abstractmethod
    def get_task_description(self) -> str:
        """Return CrewAI Task description."""
        pass

    @abstractmethod
    def get_expected_output(self) -> str:
        """Return expected output description for CrewAI Task."""
        pass
