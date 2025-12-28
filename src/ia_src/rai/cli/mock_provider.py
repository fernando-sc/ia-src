"""Mock LLM provider for demonstration without API keys."""

from typing import Any

from ia_src.core.message import Message
from ia_src.llm.base_provider import LLMProvider, LLMResponse


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing and demonstration.

    Returns reasonable default responses without requiring
    actual API calls.
    """

    async def generate(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a mock response."""
        # Extract the last user message
        last_message = ""
        for msg in reversed(messages):
            if msg.role.value == "user":
                last_message = msg.content
                break

        # Generate contextual mock response
        content = self._generate_mock_content(last_message)

        return LLMResponse(
            content=content,
            tool_calls=[],
            usage={"prompt_tokens": 100, "completion_tokens": 50},
        )

    async def stream(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Stream is not supported for mock provider."""
        response = await self.generate(messages, tools, **kwargs)
        yield response.content

    def _generate_mock_content(self, query: str) -> str:
        """Generate mock content based on query."""
        query_lower = query.lower()

        if "accountability" in query_lower:
            return (
                "Based on the accountability analysis, the system has clear ownership "
                "but could improve governance documentation and audit mechanisms."
            )
        elif "transparency" in query_lower:
            return (
                "The transparency assessment indicates documentation gaps. "
                "Consider implementing model cards and improving stakeholder communication."
            )
        elif "fairness" in query_lower:
            return (
                "Fairness analysis suggests reviewing data representativeness "
                "and implementing bias detection across protected attributes."
            )
        elif "security" in query_lower:
            return (
                "Security assessment recommends strengthening access controls "
                "and implementing privacy-by-design principles."
            )
        elif "robustness" in query_lower:
            return (
                "Robustness evaluation indicates need for comprehensive testing "
                "and monitoring for model drift."
            )
        elif "alignment" in query_lower:
            return (
                "Alignment review suggests implementing human oversight mechanisms "
                "and establishing clear escalation procedures."
            )
        else:
            return (
                "Analysis complete. The system shows areas of strength and opportunities "
                "for improvement across responsible AI principles."
            )
