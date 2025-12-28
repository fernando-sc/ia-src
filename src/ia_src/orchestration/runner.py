"""Agent orchestration and execution."""

from typing import Any

from ia_src.core.base_agent import Agent
from ia_src.core.context import Context
from ia_src.core.message import Message


class AgentRunner:
    """Orchestrates agent execution."""

    def __init__(self, agent: Agent, max_iterations: int = 100) -> None:
        self.agent = agent
        self.max_iterations = max_iterations

    async def run(self, initial_message: Message) -> list[Message]:
        """Run the agent until completion."""
        context = Context(max_iterations=self.max_iterations)
        context.add_message(initial_message)

        results: list[Message] = []
        response = await self.agent.run(initial_message, context)
        results.append(response)

        return results

    async def run_loop(self, initial_message: Message) -> list[Message]:
        """Run agent in a loop until it signals completion."""
        context = Context(max_iterations=self.max_iterations)
        context.add_message(initial_message)

        results: list[Message] = []

        while context.increment_iteration():
            response = await self.agent.step(context)
            if response is None:
                break
            results.append(response)
            context.add_message(response)

        return results
