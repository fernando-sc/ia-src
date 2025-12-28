"""Base RAI agent implementation."""

from abc import abstractmethod
from typing import Any
import uuid

from ia_src.core.base_agent import Agent
from ia_src.core.context import Context
from ia_src.core.message import Message, Role
from ia_src.llm.base_provider import LLMProvider
from ia_src.rai.models import (
    ComplianceStatus,
    Principle,
    PrincipleEvaluation,
    SystemProfile,
)


class RAIAgent(Agent):
    """Base class for all RAI specialized agents."""

    def __init__(
        self,
        name: str,
        principle: Principle,
        llm_provider: LLMProvider,
        description: str = "",
    ) -> None:
        """Initialize RAI agent.

        Args:
            name: Agent name
            principle: The RAI principle this agent evaluates
            llm_provider: LLM provider for AI-powered analysis
            description: Agent description
        """
        super().__init__(name, description)
        self.principle = principle
        self.llm_provider = llm_provider
        self._system_prompt = self._build_system_prompt()

    @abstractmethod
    def _build_system_prompt(self) -> str:
        """Build the system prompt for this agent's specialty.

        Each specialized agent should override this to provide
        domain-specific expertise and evaluation guidelines.
        """
        ...

    @abstractmethod
    async def evaluate(
        self,
        system_profile: SystemProfile,
        context: Context,
    ) -> PrincipleEvaluation:
        """Evaluate an AI system against this agent's principle.

        Args:
            system_profile: The AI system to evaluate
            context: Execution context with additional variables

        Returns:
            PrincipleEvaluation with findings, score, and recommendations
        """
        ...

    @abstractmethod
    async def generate_recommendations(
        self,
        evaluation: PrincipleEvaluation,
        context: Context,
    ) -> list[str]:
        """Generate actionable recommendations based on evaluation.

        Args:
            evaluation: The completed evaluation
            context: Execution context

        Returns:
            List of actionable recommendation strings
        """
        ...

    async def run(self, message: Message, context: Context) -> Message:
        """Execute the agent with routing to appropriate method.

        Routes based on message intent:
        - evaluate: Run principle evaluation
        - recommend: Generate recommendations
        - query: General LLM-powered response
        """
        intent = self._parse_intent(message)

        if intent == "evaluate":
            system_profile = context.get_variable("system_profile")
            if not system_profile:
                return Message.assistant(
                    "Error: No system profile provided in context. "
                    "Please set 'system_profile' variable before evaluation."
                )
            evaluation = await self.evaluate(system_profile, context)
            context.set_variable(f"{self.principle.value}_evaluation", evaluation)
            return Message.assistant(self._format_evaluation_summary(evaluation))

        elif intent == "recommend":
            evaluation = context.get_variable(f"{self.principle.value}_evaluation")
            if not evaluation:
                return Message.assistant(
                    f"Error: No {self.principle.value} evaluation found. "
                    "Please run evaluation first."
                )
            recommendations = await self.generate_recommendations(evaluation, context)
            return Message.assistant(self._format_recommendations(recommendations))

        else:
            # General query - use LLM
            return await self._llm_response(message, context)

    async def step(self, context: Context) -> Message | None:
        """Execute a single evaluation step.

        Used for iterative execution by AgentRunner.
        Returns None when complete.
        """
        # Check if we have work to do
        if not context.get_variable("system_profile"):
            return None

        if context.get_variable(f"{self.principle.value}_complete"):
            return None

        # Run evaluation
        system_profile = context.get_variable("system_profile")
        evaluation = await self.evaluate(system_profile, context)
        context.set_variable(f"{self.principle.value}_evaluation", evaluation)
        context.set_variable(f"{self.principle.value}_complete", True)

        return Message.assistant(
            f"Completed {self.principle.value} evaluation. "
            f"Score: {evaluation.score:.2f}, "
            f"Status: {evaluation.compliance_status.value}"
        )

    def _parse_intent(self, message: Message) -> str:
        """Parse the intent from a message."""
        content_lower = message.content.lower()
        if "evaluate" in content_lower or "assess" in content_lower:
            return "evaluate"
        elif "recommend" in content_lower or "suggestion" in content_lower:
            return "recommend"
        return "query"

    async def _llm_response(self, message: Message, context: Context) -> Message:
        """Get LLM response for general queries."""
        messages = [
            Message.system(self._system_prompt),
            *context.messages[-10:],  # Last 10 messages for context
            message,
        ]
        response = await self.llm_provider.generate(
            messages, tools=[t.get_schema() for t in self._tools] if self._tools else None
        )
        return Message.assistant(response.content)

    def _determine_compliance_status(self, score: float) -> ComplianceStatus:
        """Determine compliance status from score."""
        if score >= 0.9:
            return ComplianceStatus.COMPLIANT
        elif score >= 0.6:
            return ComplianceStatus.PARTIALLY_COMPLIANT
        else:
            return ComplianceStatus.NON_COMPLIANT

    def _generate_evaluation_id(self) -> str:
        """Generate unique evaluation ID."""
        return f"{self.principle.value[:3].upper()}-{uuid.uuid4().hex[:8]}"

    def _format_evaluation_summary(self, evaluation: PrincipleEvaluation) -> str:
        """Format evaluation as readable summary."""
        summary = f"""## {self.principle.value.title()} Evaluation Summary

**Score:** {evaluation.score:.2f}/1.00
**Status:** {evaluation.compliance_status.value.replace('_', ' ').title()}
**Confidence:** {evaluation.confidence:.0%}

### Findings ({len(evaluation.findings)})
"""
        for finding in evaluation.findings[:5]:  # Top 5 findings
            summary += f"- [{finding.severity.value.upper()}] {finding.description}\n"

        if evaluation.strengths:
            summary += "\n### Strengths\n"
            for s in evaluation.strengths[:3]:
                summary += f"- {s}\n"

        if evaluation.weaknesses:
            summary += "\n### Weaknesses\n"
            for w in evaluation.weaknesses[:3]:
                summary += f"- {w}\n"

        return summary

    def _format_recommendations(self, recommendations: list[str]) -> str:
        """Format recommendations as readable list."""
        output = f"## {self.principle.value.title()} Recommendations\n\n"
        for i, rec in enumerate(recommendations, 1):
            output += f"{i}. {rec}\n"
        return output


class RAIAgentError(Exception):
    """Exception raised by RAI agents."""

    def __init__(self, agent_name: str, message: str) -> None:
        self.agent_name = agent_name
        super().__init__(f"[{agent_name}] {message}")
