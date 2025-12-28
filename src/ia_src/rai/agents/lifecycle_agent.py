"""Lifecycle Agent for AI system phase management."""

from datetime import datetime
from typing import Any
import uuid

from ia_src.core.base_agent import Agent
from ia_src.core.context import Context
from ia_src.core.message import Message
from ia_src.llm.base_provider import LLMProvider
from ia_src.rai.models import (
    LifecyclePhase,
    LifecycleStatus,
    PHASE_CHECKPOINTS,
    PhaseCheckpoint,
    PhaseTransition,
    SystemProfile,
    VerificationCriterion,
)


class LifecycleAgent(Agent):
    """Agent that guides AI systems through lifecycle phases with checkpoints.

    Manages:
    - Phase-specific checkpoints
    - Transition verification
    - Phase completion tracking
    - Next actions recommendations
    """

    def __init__(self, llm_provider: LLMProvider) -> None:
        super().__init__(
            name="LifecycleAgent",
            description="Guides AI systems through lifecycle phases with RAI checkpoints",
        )
        self.llm_provider = llm_provider

    async def run(self, message: Message, context: Context) -> Message:
        """Handle lifecycle-related requests."""
        content_lower = message.content.lower()

        system_profile: SystemProfile | None = context.get_variable("system_profile")
        if not system_profile:
            return Message.assistant(
                "Error: No system profile in context. "
                "Please set 'system_profile' variable."
            )

        if "status" in content_lower:
            return await self._get_lifecycle_status(system_profile, context)
        elif "checkpoint" in content_lower:
            return await self._get_checkpoints(system_profile, context)
        elif "verify" in content_lower:
            return await self._verify_checkpoints(system_profile, context)
        elif "transition" in content_lower or "next phase" in content_lower:
            return await self._assess_transition_readiness(system_profile, context)
        elif "recommend" in content_lower or "action" in content_lower:
            return await self._get_recommendations(system_profile, context)
        else:
            return await self._get_lifecycle_status(system_profile, context)

    async def step(self, context: Context) -> Message | None:
        """Execute lifecycle verification step."""
        system_profile = context.get_variable("system_profile")
        if not system_profile:
            return None

        lifecycle_status = context.get_variable("lifecycle_status")
        if not lifecycle_status:
            lifecycle_status = self._initialize_lifecycle_status(system_profile)
            context.set_variable("lifecycle_status", lifecycle_status)
            return Message.assistant(
                f"Initialized lifecycle tracking for {system_profile.name} "
                f"at phase: {system_profile.current_phase.value}"
            )

        # Verify next incomplete checkpoint
        incomplete = lifecycle_status.get_incomplete_checkpoints()
        if incomplete:
            checkpoint = incomplete[0]
            verified = await self._verify_single_checkpoint(checkpoint, context)
            return Message.assistant(
                f"Verified checkpoint '{checkpoint.checkpoint_name}': "
                f"{'PASSED' if verified.passed else 'NOT PASSED'}"
            )

        return None

    def _initialize_lifecycle_status(
        self,
        system_profile: SystemProfile,
    ) -> LifecycleStatus:
        """Initialize lifecycle status for a system."""
        phase = system_profile.current_phase
        checkpoints = self._get_phase_checkpoints(phase)

        return LifecycleStatus(
            system_id=system_profile.system_id,
            current_phase=phase,
            current_phase_checkpoints=checkpoints,
            next_phase=self._get_next_phase(phase),
        )

    def _get_phase_checkpoints(
        self,
        phase: LifecyclePhase,
    ) -> list[PhaseCheckpoint]:
        """Get checkpoints for a specific phase."""
        checkpoint_configs = PHASE_CHECKPOINTS.get(phase, [])
        checkpoints = []

        for config in checkpoint_configs:
            criteria = [
                VerificationCriterion(
                    criterion_id=c["criterion_id"],
                    description=c["description"],
                    verification_method=c.get("verification_method", ""),
                )
                for c in config.get("verification_criteria", [])
            ]

            checkpoint = PhaseCheckpoint(
                checkpoint_id=config["checkpoint_id"],
                phase=phase,
                checkpoint_name=config["checkpoint_name"],
                description=config["description"],
                required_artifacts=config.get("required_artifacts", []),
                verification_criteria=criteria,
            )
            checkpoints.append(checkpoint)

        return checkpoints

    def _get_next_phase(self, current: LifecyclePhase) -> LifecyclePhase | None:
        """Get the next phase in the lifecycle."""
        phase_order = [
            LifecyclePhase.BUSINESS_UNDERSTANDING,
            LifecyclePhase.DESIGN_DATA_MODELS,
            LifecyclePhase.VALIDATION_VERIFICATION,
            LifecyclePhase.DEPLOYMENT,
            LifecyclePhase.OPERATION_MONITORING,
            LifecyclePhase.SHUTDOWN,
        ]
        try:
            idx = phase_order.index(current)
            if idx < len(phase_order) - 1:
                return phase_order[idx + 1]
        except ValueError:
            pass
        return None

    async def _get_lifecycle_status(
        self,
        system_profile: SystemProfile,
        context: Context,
    ) -> Message:
        """Get current lifecycle status."""
        lifecycle_status = context.get_variable("lifecycle_status")
        if not lifecycle_status:
            lifecycle_status = self._initialize_lifecycle_status(system_profile)
            context.set_variable("lifecycle_status", lifecycle_status)

        completion = lifecycle_status.calculate_phase_completion()
        incomplete = lifecycle_status.get_incomplete_checkpoints()

        status_text = f"""# Lifecycle Status: {system_profile.name}

**Current Phase:** {lifecycle_status.current_phase.value.replace('_', ' ').title()}
**Phase Completion:** {completion:.0%}
**Next Phase:** {lifecycle_status.next_phase.value.replace('_', ' ').title() if lifecycle_status.next_phase else 'N/A'}
**Ready for Transition:** {'Yes' if lifecycle_status.ready_for_next_phase else 'No'}

## Checkpoints ({len(lifecycle_status.current_phase_checkpoints)} total)

| Checkpoint | Status |
|------------|--------|
"""
        for cp in lifecycle_status.current_phase_checkpoints:
            status = "PASSED" if cp.passed else "PENDING"
            status_text += f"| {cp.checkpoint_name} | {status} |\n"

        if incomplete:
            status_text += f"\n**Incomplete Checkpoints:** {len(incomplete)}\n"

        return Message.assistant(status_text)

    async def _get_checkpoints(
        self,
        system_profile: SystemProfile,
        context: Context,
    ) -> Message:
        """Get detailed checkpoint information."""
        lifecycle_status = context.get_variable("lifecycle_status")
        if not lifecycle_status:
            lifecycle_status = self._initialize_lifecycle_status(system_profile)

        output = f"# Checkpoints for {lifecycle_status.current_phase.value.replace('_', ' ').title()}\n\n"

        for cp in lifecycle_status.current_phase_checkpoints:
            status_icon = "PASSED" if cp.passed else "PENDING"
            output += f"## {cp.checkpoint_name} [{status_icon}]\n\n"
            output += f"**Description:** {cp.description}\n\n"

            if cp.required_artifacts:
                output += "**Required Artifacts:**\n"
                for artifact in cp.required_artifacts:
                    output += f"- {artifact}\n"
                output += "\n"

            if cp.verification_criteria:
                output += "**Verification Criteria:**\n"
                for criterion in cp.verification_criteria:
                    status = "PASSED" if criterion.passed else "PENDING"
                    output += f"- [{status}] {criterion.description}\n"
                output += "\n"

        return Message.assistant(output)

    async def _verify_checkpoints(
        self,
        system_profile: SystemProfile,
        context: Context,
    ) -> Message:
        """Verify all checkpoints for current phase."""
        lifecycle_status = context.get_variable("lifecycle_status")
        if not lifecycle_status:
            lifecycle_status = self._initialize_lifecycle_status(system_profile)

        verified_checkpoints = []
        for checkpoint in lifecycle_status.current_phase_checkpoints:
            verified = await self._verify_single_checkpoint(checkpoint, context)
            verified_checkpoints.append(verified)

        lifecycle_status.current_phase_checkpoints = verified_checkpoints
        lifecycle_status.ready_for_next_phase = all(cp.passed for cp in verified_checkpoints)
        context.set_variable("lifecycle_status", lifecycle_status)

        passed = sum(1 for cp in verified_checkpoints if cp.passed)
        total = len(verified_checkpoints)

        return Message.assistant(
            f"# Checkpoint Verification Complete\n\n"
            f"**Passed:** {passed}/{total}\n"
            f"**Ready for Next Phase:** {'Yes' if lifecycle_status.ready_for_next_phase else 'No'}\n\n"
            + "\n".join(
                f"- {cp.checkpoint_name}: {'PASSED' if cp.passed else 'NOT PASSED'}"
                for cp in verified_checkpoints
            )
        )

    async def _verify_single_checkpoint(
        self,
        checkpoint: PhaseCheckpoint,
        context: Context,
    ) -> PhaseCheckpoint:
        """Verify a single checkpoint."""
        # Check for required artifacts
        missing_artifacts = []
        for artifact in checkpoint.required_artifacts:
            if not context.get_variable(artifact):
                missing_artifacts.append(artifact)

        if missing_artifacts:
            checkpoint.passed = False
            checkpoint.blocked = True
            checkpoint.blocking_reasons = [
                f"Missing artifact: {a}" for a in missing_artifacts
            ]
            return checkpoint

        # Verify criteria
        all_passed = True
        for criterion in checkpoint.verification_criteria:
            # Check if there's evidence for this criterion
            evidence = context.get_variable(f"evidence_{criterion.criterion_id}")
            if evidence:
                criterion.passed = True
                criterion.evidence = str(evidence)
            else:
                # Use heuristic: if related artifact exists, consider passed
                criterion.passed = False
                all_passed = False

        checkpoint.passed = all_passed and not missing_artifacts
        checkpoint.verification_date = datetime.utcnow()
        checkpoint.verified_by = self.name

        return checkpoint

    async def _assess_transition_readiness(
        self,
        system_profile: SystemProfile,
        context: Context,
    ) -> Message:
        """Assess readiness to transition to next phase."""
        lifecycle_status = context.get_variable("lifecycle_status")
        if not lifecycle_status:
            lifecycle_status = self._initialize_lifecycle_status(system_profile)

        incomplete = lifecycle_status.get_incomplete_checkpoints()

        if not incomplete:
            next_phase = lifecycle_status.next_phase
            if next_phase:
                return Message.assistant(
                    f"# Transition Assessment\n\n"
                    f"**Status:** READY FOR TRANSITION\n"
                    f"**Current Phase:** {lifecycle_status.current_phase.value.replace('_', ' ').title()}\n"
                    f"**Next Phase:** {next_phase.value.replace('_', ' ').title()}\n\n"
                    f"All checkpoints passed. System is ready to proceed to "
                    f"{next_phase.value.replace('_', ' ')} phase."
                )
            else:
                return Message.assistant(
                    "System is in final phase (Shutdown). No further transitions."
                )

        return Message.assistant(
            f"# Transition Assessment\n\n"
            f"**Status:** NOT READY\n"
            f"**Incomplete Checkpoints:** {len(incomplete)}\n\n"
            f"The following checkpoints must be completed before transition:\n"
            + "\n".join(f"- {cp.checkpoint_name}: {cp.notes or 'Pending'}" for cp in incomplete)
        )

    async def _get_recommendations(
        self,
        system_profile: SystemProfile,
        context: Context,
    ) -> Message:
        """Get recommended next actions."""
        lifecycle_status = context.get_variable("lifecycle_status")
        if not lifecycle_status:
            lifecycle_status = self._initialize_lifecycle_status(system_profile)

        recommendations = []

        incomplete = lifecycle_status.get_incomplete_checkpoints()
        for cp in incomplete[:3]:  # Top 3 priorities
            recommendations.append(
                f"Complete checkpoint '{cp.checkpoint_name}': {cp.description}"
            )
            for artifact in cp.required_artifacts:
                if not context.get_variable(artifact):
                    recommendations.append(f"  - Provide artifact: {artifact}")

        if lifecycle_status.ready_for_next_phase and lifecycle_status.next_phase:
            recommendations.append(
                f"Initiate transition to {lifecycle_status.next_phase.value.replace('_', ' ')} phase"
            )

        if not recommendations:
            recommendations.append("All checkpoints complete. Continue operations.")

        return Message.assistant(
            f"# Recommended Actions\n\n"
            + "\n".join(f"{i}. {r}" for i, r in enumerate(recommendations, 1))
        )

    async def record_transition(
        self,
        system_profile: SystemProfile,
        to_phase: LifecyclePhase,
        authorized_by: str,
        context: Context,
    ) -> PhaseTransition:
        """Record a phase transition."""
        lifecycle_status: LifecycleStatus = context.get_variable("lifecycle_status")
        if not lifecycle_status:
            lifecycle_status = self._initialize_lifecycle_status(system_profile)

        transition = PhaseTransition(
            transition_id=str(uuid.uuid4()),
            from_phase=lifecycle_status.current_phase,
            to_phase=to_phase,
            authorized_by=authorized_by,
            checkpoints_verified=[
                cp.checkpoint_id
                for cp in lifecycle_status.current_phase_checkpoints
                if cp.passed
            ],
        )

        # Update lifecycle status
        lifecycle_status.phase_transitions.append(transition)
        lifecycle_status.current_phase = to_phase
        lifecycle_status.phase_entry_date = datetime.utcnow()
        lifecycle_status.current_phase_checkpoints = self._get_phase_checkpoints(to_phase)
        lifecycle_status.next_phase = self._get_next_phase(to_phase)
        lifecycle_status.ready_for_next_phase = False

        context.set_variable("lifecycle_status", lifecycle_status)

        return transition
