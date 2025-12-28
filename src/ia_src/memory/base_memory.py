"""Base memory implementation for agents."""

from abc import ABC, abstractmethod
from typing import Any

from ia_src.core.message import Message


class Memory(ABC):
    """Base class for agent memory systems."""

    @abstractmethod
    async def store(self, key: str, value: Any) -> None:
        """Store a value in memory."""
        ...

    @abstractmethod
    async def retrieve(self, key: str) -> Any | None:
        """Retrieve a value from memory."""
        ...

    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> list[Any]:
        """Search memory for relevant items."""
        ...

    @abstractmethod
    async def add_message(self, message: Message) -> None:
        """Add a message to conversation memory."""
        ...

    @abstractmethod
    async def get_messages(self, limit: int | None = None) -> list[Message]:
        """Get messages from conversation memory."""
        ...
