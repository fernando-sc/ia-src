"""Base agent implementation."""

from abc import ABC, abstractmethod
from typing import Any

from ia_src.core.context import Context
from ia_src.core.message import Message


class Agent(ABC):
    """Base class for all agents."""

    def __init__(self, name: str, description: str = "") -> None:
        self.name = name
        self.description = description
        self._tools: list[Any] = []

    def add_tool(self, tool: Any) -> None:
        """Add a tool to the agent."""
        self._tools.append(tool)

    @abstractmethod
    async def run(self, message: Message, context: Context) -> Message:
        """Execute the agent with a given message and context."""
        ...

    @abstractmethod
    async def step(self, context: Context) -> Message | None:
        """Execute a single step of the agent."""
        ...
