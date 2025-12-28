"""Orchestrator Agent for coordinating RAI assessments."""

from typing import Any

from ia_src.core.base_agent import Agent
from ia_src.core.context import Context
from ia_src.core.message import Message
from ia_src.llm.base_provider import LLMProvider
from ia_src.rai.agents.base_rai_agent import RAIAgent
from ia_src.rai.models import (
    AIAReport,
    Principle,
    PrincipleEvaluation,
    SystemProfile,
)


class OrchestratorAgent(Agent):
    """Coordinates all RAI specialized agents.

    Responsibilities:
    - Route requests to appropriate agents
    - Coordinate multi-agent assessments
    - Aggregate results into unified reports
    - Manage assessment workflow
    """

    def __init__(
        self,
        llm_provider: LLMProvider,
        principle_agents: dict[str, RAIAgent] | None = None,
        aia_agent: Agent | None = None,
        lifecycle_agent: Agent | None = None,
    ) -> None:
        super().__init__(
            name="RAIOrchestratorAgent",
            description="Coordinates RAI assessments across all specialized agents",
        )
        self.llm_provider = llm_provider
        self.principle_agents = principle_agents or {}
        self.aia_agent = aia_agent
        self.lifecycle_agent = lifecycle_agent
        self._task_queue: list[dict[str, Any]] = []

    def register_principle_agent(self, principle: str, agent: RAIAgent) -> None:
        """Register a principle agent."""
        self.principle_agents[principle] = agent

    def set_aia_agent(self, agent: Agent) -> None:
        """Set the AIA agent."""
        self.aia_agent = agent

    def set_lifecycle_agent(self, agent: Agent) -> None:
        """Set the lifecycle agent."""
        self.lifecycle_agent = agent

    async def run(self, message: Message, context: Context) -> Message:
        """Route request to appropriate agent(s) and aggregate results."""
        intent = await self._classify_intent(message)

        if intent == "full_assessment":
            return await self._run_full_assessment(context)
        elif intent == "principle_evaluation":
            principle = self._extract_principle(message.content)
            if principle:
                return await self._run_principle_evaluation(principle, context)
            return Message.assistant(
                "Please specify which principle to evaluate: "
                "accountability, transparency, fairness, security, robustness, or alignment"
            )
        elif intent == "aia":
            return await self._run_aia(context)
        elif intent == "lifecycle":
            return await self._run_lifecycle_check(context)
        else:
            return await self._route_to_best_agent(message, context)

    async def step(self, context: Context) -> Message | None:
        """Process next task in queue."""
        if not self._task_queue:
            return None

        task = self._task_queue.pop(0)
        agent = task["agent"]
        task_message = task.get("message", Message.user("evaluate"))

        result = await agent.run(task_message, context)
        return result

    async def _run_full_assessment(self, context: Context) -> Message:
        """Run comprehensive RAI assessment across all principles."""
        system_profile: SystemProfile | None = context.get_variable("system_profile")
        if not system_profile:
            return Message.assistant(
                "Error: No system profile in context. "
                "Please set 'system_profile' variable before assessment."
            )

        results: list[PrincipleEvaluation] = []
        status_messages = []

        # Run all principle evaluations
        for principle_name, agent in self.principle_agents.items():
            try:
                evaluation = await agent.evaluate(system_profile, context)
                results.append(evaluation)
                context.set_variable(f"{principle_name}_evaluation", evaluation)
                status_messages.append(
                    f"- {principle_name.title()}: {evaluation.score:.2f} "
                    f"({evaluation.compliance_status.value})"
                )
            except Exception as e:
                status_messages.append(f"- {principle_name.title()}: Error - {str(e)}")

        # Store all evaluations
        context.set_variable("principle_evaluations", results)

        # Generate AIA report if agent available
        if self.aia_agent:
            try:
                aia_message = Message.user("full assessment")
                await self.aia_agent.run(aia_message, context)
            except Exception as e:
                status_messages.append(f"- AIA: Error - {str(e)}")

        # Generate summary
        summary = self._generate_summary(results, context)

        return Message.assistant(
            f"# RAI Assessment Complete\n\n"
            f"**System:** {system_profile.name}\n\n"
            f"## Principle Evaluations\n\n"
            + "\n".join(status_messages)
            + f"\n\n{summary}"
        )

    async def _run_principle_evaluation(
        self,
        principle: str,
        context: Context,
    ) -> Message:
        """Run evaluation for a single principle."""
        agent = self.principle_agents.get(principle.lower())
        if not agent:
            return Message.assistant(
                f"No agent registered for principle: {principle}. "
                f"Available: {', '.join(self.principle_agents.keys())}"
            )

        system_profile = context.get_variable("system_profile")
        if not system_profile:
            return Message.assistant("Error: No system profile in context.")

        evaluation = await agent.evaluate(system_profile, context)
        context.set_variable(f"{principle}_evaluation", evaluation)

        return Message.assistant(agent._format_evaluation_summary(evaluation))

    async def _run_aia(self, context: Context) -> Message:
        """Run Algorithmic Impact Assessment."""
        if not self.aia_agent:
            return Message.assistant("AIA agent not configured.")

        return await self.aia_agent.run(Message.user("full assessment"), context)

    async def _run_lifecycle_check(self, context: Context) -> Message:
        """Run lifecycle phase check."""
        if not self.lifecycle_agent:
            return Message.assistant("Lifecycle agent not configured.")

        return await self.lifecycle_agent.run(Message.user("status"), context)

    async def _classify_intent(self, message: Message) -> str:
        """Classify the user's intent."""
        content_lower = message.content.lower()

        if "full assessment" in content_lower or "comprehensive" in content_lower:
            return "full_assessment"
        elif "aia" in content_lower or "impact assessment" in content_lower:
            return "aia"
        elif "lifecycle" in content_lower or "phase" in content_lower:
            return "lifecycle"
        elif any(
            p in content_lower
            for p in [
                "accountability",
                "transparency",
                "fairness",
                "security",
                "robustness",
                "alignment",
            ]
        ):
            return "principle_evaluation"

        return "general"

    def _extract_principle(self, content: str) -> str | None:
        """Extract principle name from message."""
        content_lower = content.lower()
        principles = [
            "accountability",
            "transparency",
            "fairness",
            "security",
            "robustness",
            "alignment",
        ]
        for p in principles:
            if p in content_lower:
                return p
        return None

    async def _route_to_best_agent(
        self,
        message: Message,
        context: Context,
    ) -> Message:
        """Use LLM to determine best agent for the query."""
        routing_prompt = f"""Given this user query about AI responsibility:

"{message.content}"

Which specialized agent should handle this?
- AccountabilityAgent: governance, responsibility, audits, compliance oversight
- TransparencyAgent: explainability, documentation, communication
- FairnessAgent: bias, equity, fairness metrics, discrimination
- SecurityAgent: privacy, vulnerabilities, data protection, security
- RobustnessAgent: reliability, performance, testing, monitoring
- AlignmentAgent: human oversight, ethics, value alignment

Return ONLY the principle name (accountability, transparency, fairness, security, robustness, or alignment)."""

        try:
            response = await self.llm_provider.generate([Message.user(routing_prompt)])
            principle = response.content.strip().lower()

            # Clean up response
            for p in ["accountability", "transparency", "fairness", "security", "robustness", "alignment"]:
                if p in principle:
                    principle = p
                    break

            agent = self.principle_agents.get(principle)
            if agent:
                return await agent.run(message, context)

        except Exception:
            pass

        return Message.assistant(
            "I can help with RAI assessments. Please specify:\n"
            "- 'full assessment' for comprehensive evaluation\n"
            "- 'aia' for Algorithmic Impact Assessment\n"
            "- 'lifecycle' for phase management\n"
            "- Or specify a principle: accountability, transparency, fairness, "
            "security, robustness, alignment"
        )

    def _generate_summary(
        self,
        evaluations: list[PrincipleEvaluation],
        context: Context,
    ) -> str:
        """Generate executive summary of assessment."""
        if not evaluations:
            return "No evaluations completed."

        avg_score = sum(e.score for e in evaluations) / len(evaluations)
        min_score = min(e.score for e in evaluations)
        min_principle = min(evaluations, key=lambda e: e.score)

        # Count findings by severity
        critical = sum(
            1 for e in evaluations for f in e.findings if f.severity.value == "critical"
        )
        high = sum(
            1 for e in evaluations for f in e.findings if f.severity.value == "high"
        )

        status = (
            "Compliant"
            if avg_score >= 0.9
            else "Partially Compliant"
            if avg_score >= 0.6
            else "Non-Compliant"
        )

        summary = f"""## Summary

**Overall Score:** {avg_score:.2f}/1.00
**Status:** {status}
**Lowest Principle:** {min_principle.principle.value.title()} ({min_score:.2f})

**Findings:**
- Critical: {critical}
- High: {high}
"""

        if critical > 0 or high > 0:
            summary += "\n### Priority Recommendations\n"
            for e in evaluations:
                for f in e.findings:
                    if f.severity.value in ("critical", "high"):
                        summary += f"- [{f.severity.value.upper()}] {f.recommendation}\n"
                        if len([
                            x for x in evaluations
                            for y in x.findings
                            if y.severity.value in ("critical", "high")
                        ]) >= 5:
                            break

        # Get AIA recommendation if available
        aia_report: AIAReport | None = context.get_variable("aia_report")
        if aia_report:
            summary += f"\n**AIA Recommendation:** {aia_report.overall_recommendation.replace('_', ' ').title()}"

        return summary

    async def get_assessment_status(self, context: Context) -> dict[str, Any]:
        """Get current assessment status."""
        evaluations = context.get_variable("principle_evaluations", [])
        aia_report = context.get_variable("aia_report")

        return {
            "principles_evaluated": len(evaluations),
            "total_principles": len(self.principle_agents),
            "aia_complete": aia_report is not None,
            "evaluations": [
                {
                    "principle": e.principle.value,
                    "score": e.score,
                    "status": e.compliance_status.value,
                }
                for e in evaluations
            ],
            "overall_score": (
                sum(e.score for e in evaluations) / len(evaluations)
                if evaluations
                else None
            ),
        }
