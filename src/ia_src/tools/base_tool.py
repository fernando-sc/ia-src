"""Base tool implementation."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolResult:
    """Result from tool execution."""

    success: bool
    output: Any
    error: str | None = None


class Tool(ABC):
    """Base class for agent tools."""

    name: str
    description: str

    @abstractmethod
    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the tool with given arguments."""
        ...

    @abstractmethod
    def get_schema(self) -> dict[str, Any]:
        """Return JSON schema for tool parameters."""
        ...
