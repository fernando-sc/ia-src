"""Context management for agent execution."""

from dataclasses import dataclass, field
from typing import Any

from ia_src.core.message import Message


@dataclass
class Context:
    """Execution context for agents."""

    messages: list[Message] = field(default_factory=list)
    variables: dict[str, Any] = field(default_factory=dict)
    max_iterations: int = 100
    current_iteration: int = 0

    def add_message(self, message: Message) -> None:
        """Add a message to the context."""
        self.messages.append(message)

    def get_variable(self, key: str, default: Any = None) -> Any:
        """Get a variable from the context."""
        return self.variables.get(key, default)

    def set_variable(self, key: str, value: Any) -> None:
        """Set a variable in the context."""
        self.variables[key] = value

    def increment_iteration(self) -> bool:
        """Increment iteration count. Returns False if max reached."""
        self.current_iteration += 1
        return self.current_iteration < self.max_iterations
