"""RAI Runner for executing multi-agent assessments."""

from typing import Any

from ia_src.core.context import Context
from ia_src.core.message import Message
from ia_src.llm.base_provider import LLMProvider
from ia_src.orchestration.runner import AgentRunner
from ia_src.rai.agents.accountability_agent import AccountabilityAgent
from ia_src.rai.agents.aia_agent import AIAAgent
from ia_src.rai.agents.alignment_agent import AlignmentAgent
from ia_src.rai.agents.fairness_agent import FairnessAgent
from ia_src.rai.agents.lifecycle_agent import LifecycleAgent
from ia_src.rai.agents.orchestrator_agent import OrchestratorAgent
from ia_src.rai.agents.robustness_agent import RobustnessAgent
from ia_src.rai.agents.security_agent import SecurityAgent
from ia_src.rai.agents.transparency_agent import TransparencyAgent
from ia_src.rai.models import (
    AIAReport,
    PrincipleEvaluation,
    SystemProfile,
)


class RAIRunner:
    """Specialized runner for RAI multi-agent system.

    Provides convenient methods for running RAI assessments
    with all agents properly configured.
    """

    def __init__(
        self,
        llm_provider: LLMProvider,
        max_iterations: int = 100,
    ) -> None:
        """Initialize RAI Runner.

        Args:
            llm_provider: LLM provider for all agents
            max_iterations: Maximum iterations for agent loops
        """
        self.llm_provider = llm_provider
        self.max_iterations = max_iterations

        # Initialize all agents
        self.principle_agents = {
            "accountability": AccountabilityAgent(llm_provider),
            "transparency": TransparencyAgent(llm_provider),
            "fairness": FairnessAgent(llm_provider),
            "security": SecurityAgent(llm_provider),
            "robustness": RobustnessAgent(llm_provider),
            "alignment": AlignmentAgent(llm_provider),
        }

        self.aia_agent = AIAAgent(llm_provider)
        self.lifecycle_agent = LifecycleAgent(llm_provider)

        # Create orchestrator with all agents
        self.orchestrator = OrchestratorAgent(
            llm_provider=llm_provider,
            principle_agents=self.principle_agents,
            aia_agent=self.aia_agent,
            lifecycle_agent=self.lifecycle_agent,
        )

        self._runner = AgentRunner(self.orchestrator, max_iterations=max_iterations)

    @classmethod
    def create_default(cls, llm_provider: LLMProvider) -> "RAIRunner":
        """Create RAI Runner with default configuration.

        Args:
            llm_provider: LLM provider to use

        Returns:
            Configured RAIRunner instance
        """
        return cls(llm_provider=llm_provider)

    async def run_assessment(
        self,
        system_profile: SystemProfile,
        principles: list[str] | None = None,
    ) -> AIAReport:
        """Run a complete RAI assessment.

        Args:
            system_profile: The AI system to assess
            principles: Optional list of principles to evaluate (defaults to all)

        Returns:
            Complete AIAReport with all evaluations
        """
        context = Context(max_iterations=self.max_iterations)
        context.set_variable("system_profile", system_profile)
        context.set_variable("requested_principles", principles or ["all"])

        # Run full assessment via orchestrator
        message = Message.user("Run full RAI assessment")
        await self.orchestrator.run(message, context)

        # Return the generated report
        report = context.get_variable("aia_report")
        if not report:
            # Generate report if not created
            await self.aia_agent.run(Message.user("full assessment"), context)
            report = context.get_variable("aia_report")

        return report

    async def run_principle_evaluation(
        self,
        system_profile: SystemProfile,
        principle: str,
    ) -> PrincipleEvaluation:
        """Run evaluation for a single principle.

        Args:
            system_profile: The AI system to evaluate
            principle: Principle to evaluate

        Returns:
            PrincipleEvaluation result
        """
        if principle.lower() not in self.principle_agents:
            raise ValueError(
                f"Unknown principle: {principle}. "
                f"Available: {', '.join(self.principle_agents.keys())}"
            )

        context = Context(max_iterations=self.max_iterations)
        context.set_variable("system_profile", system_profile)

        agent = self.principle_agents[principle.lower()]
        evaluation = await agent.evaluate(system_profile, context)

        return evaluation

    async def run_aia(
        self,
        system_profile: SystemProfile,
        include_principle_evaluations: bool = True,
    ) -> AIAReport:
        """Run Algorithmic Impact Assessment.

        Args:
            system_profile: The AI system to assess
            include_principle_evaluations: Whether to run principle evaluations

        Returns:
            AIAReport
        """
        context = Context(max_iterations=self.max_iterations)
        context.set_variable("system_profile", system_profile)

        if include_principle_evaluations:
            # Run all principle evaluations first
            evaluations = []
            for principle, agent in self.principle_agents.items():
                evaluation = await agent.evaluate(system_profile, context)
                evaluations.append(evaluation)
                context.set_variable(f"{principle}_evaluation", evaluation)
            context.set_variable("principle_evaluations", evaluations)

        # Run AIA
        await self.aia_agent.run(Message.user("full assessment"), context)

        return context.get_variable("aia_report")

    async def check_lifecycle(
        self,
        system_profile: SystemProfile,
    ) -> dict[str, Any]:
        """Check lifecycle status and checkpoints.

        Args:
            system_profile: The AI system to check

        Returns:
            Dict with lifecycle status information
        """
        context = Context(max_iterations=self.max_iterations)
        context.set_variable("system_profile", system_profile)

        await self.lifecycle_agent.run(Message.user("status"), context)

        lifecycle_status = context.get_variable("lifecycle_status")
        if lifecycle_status:
            return {
                "current_phase": lifecycle_status.current_phase.value,
                "completion": lifecycle_status.calculate_phase_completion(),
                "ready_for_next": lifecycle_status.ready_for_next_phase,
                "next_phase": (
                    lifecycle_status.next_phase.value
                    if lifecycle_status.next_phase
                    else None
                ),
                "incomplete_checkpoints": [
                    cp.checkpoint_name
                    for cp in lifecycle_status.get_incomplete_checkpoints()
                ],
            }

        return {"status": "not_initialized"}

    async def interactive_session(
        self,
        system_profile: SystemProfile,
    ) -> Context:
        """Start an interactive assessment session.

        Args:
            system_profile: The AI system to assess

        Returns:
            Context that can be used for further interactions
        """
        context = Context(max_iterations=self.max_iterations)
        context.set_variable("system_profile", system_profile)
        return context

    async def process_query(
        self,
        query: str,
        context: Context,
    ) -> str:
        """Process a query in an existing session.

        Args:
            query: User query
            context: Existing context from interactive_session

        Returns:
            Response string
        """
        message = Message.user(query)
        response = await self.orchestrator.run(message, context)
        return response.content

    def get_agent_status(self) -> dict[str, Any]:
        """Get status of all agents."""
        return {
            "orchestrator": self.orchestrator.name,
            "principle_agents": list(self.principle_agents.keys()),
            "aia_agent": self.aia_agent.name if self.aia_agent else None,
            "lifecycle_agent": self.lifecycle_agent.name if self.lifecycle_agent else None,
            "max_iterations": self.max_iterations,
        }
