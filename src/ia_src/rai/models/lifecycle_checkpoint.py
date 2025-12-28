"""Lifecycle checkpoint models for AI system phase management."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .system_profile import LifecyclePhase


class VerificationCriterion(BaseModel):
    """A single verification criterion for a checkpoint."""

    criterion_id: str
    description: str
    verification_method: str = Field(default="")
    passed: bool = Field(default=False)
    evidence: Optional[str] = None
    notes: Optional[str] = None


class PhaseCheckpoint(BaseModel):
    """Checkpoint within a lifecycle phase."""

    checkpoint_id: str = Field(..., description="Unique checkpoint identifier")
    phase: LifecyclePhase = Field(..., description="Lifecycle phase")
    checkpoint_name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="What this checkpoint verifies")

    # Requirements
    required_artifacts: list[str] = Field(
        default_factory=list, description="Artifacts required for this checkpoint"
    )
    required_approvals: list[str] = Field(
        default_factory=list, description="Approvals needed"
    )

    # Verification
    verification_criteria: list[VerificationCriterion] = Field(default_factory=list)

    # Status
    passed: bool = Field(default=False)
    blocked: bool = Field(default=False)
    blocking_reasons: list[str] = Field(default_factory=list)

    # Metadata
    verification_date: Optional[datetime] = None
    verified_by: Optional[str] = None
    notes: str = Field(default="")

    @property
    def all_criteria_passed(self) -> bool:
        """Check if all verification criteria are passed."""
        if not self.verification_criteria:
            return True
        return all(c.passed for c in self.verification_criteria)

    def get_failed_criteria(self) -> list[VerificationCriterion]:
        """Get list of failed criteria."""
        return [c for c in self.verification_criteria if not c.passed]


class PhaseTransition(BaseModel):
    """Record of a phase transition."""

    transition_id: str
    from_phase: LifecyclePhase
    to_phase: LifecyclePhase
    transition_date: datetime = Field(default_factory=datetime.utcnow)
    authorized_by: str
    checkpoints_verified: list[str] = Field(
        default_factory=list, description="Checkpoint IDs that were verified"
    )
    notes: str = Field(default="")
    conditions: list[str] = Field(
        default_factory=list, description="Conditions attached to transition"
    )


class LifecycleStatus(BaseModel):
    """Current lifecycle status of an AI system."""

    system_id: str
    current_phase: LifecyclePhase
    phase_entry_date: datetime = Field(default_factory=datetime.utcnow)

    # Checkpoints for current phase
    current_phase_checkpoints: list[PhaseCheckpoint] = Field(default_factory=list)

    # History
    phase_transitions: list[PhaseTransition] = Field(default_factory=list)

    # Status
    ready_for_next_phase: bool = Field(default=False)
    blocking_issues: list[str] = Field(default_factory=list)

    # Next steps
    pending_actions: list[str] = Field(default_factory=list)
    next_phase: Optional[LifecyclePhase] = None

    def get_incomplete_checkpoints(self) -> list[PhaseCheckpoint]:
        """Get checkpoints that haven't passed yet."""
        return [cp for cp in self.current_phase_checkpoints if not cp.passed]

    def calculate_phase_completion(self) -> float:
        """Calculate completion percentage for current phase."""
        if not self.current_phase_checkpoints:
            return 1.0
        passed = sum(1 for cp in self.current_phase_checkpoints if cp.passed)
        return passed / len(self.current_phase_checkpoints)


# Predefined checkpoints for each phase
PHASE_CHECKPOINTS = {
    LifecyclePhase.BUSINESS_UNDERSTANDING: [
        {
            "checkpoint_id": "BU-001",
            "checkpoint_name": "Problem Definition",
            "description": "Clear articulation of the business problem and AI suitability",
            "required_artifacts": ["problem_statement", "success_criteria"],
            "verification_criteria": [
                {
                    "criterion_id": "BU-001-C1",
                    "description": "Problem is clearly defined with measurable objectives",
                    "verification_method": "Document review",
                },
                {
                    "criterion_id": "BU-001-C2",
                    "description": "AI is appropriate solution for this problem",
                    "verification_method": "Feasibility analysis",
                },
                {
                    "criterion_id": "BU-001-C3",
                    "description": "Stakeholders are identified and consulted",
                    "verification_method": "Stakeholder register review",
                },
            ],
        },
        {
            "checkpoint_id": "BU-002",
            "checkpoint_name": "Initial Risk Screening",
            "description": "Preliminary risk and impact assessment",
            "required_artifacts": ["risk_screening_form"],
            "verification_criteria": [
                {
                    "criterion_id": "BU-002-C1",
                    "description": "Risk level is determined (low/medium/high)",
                    "verification_method": "Risk assessment review",
                },
                {
                    "criterion_id": "BU-002-C2",
                    "description": "EU AI Act classification completed if applicable",
                    "verification_method": "Classification checklist",
                },
            ],
        },
    ],
    LifecyclePhase.DESIGN_DATA_MODELS: [
        {
            "checkpoint_id": "DDM-001",
            "checkpoint_name": "Data Quality Gate",
            "description": "Data quality and representativeness verification",
            "required_artifacts": ["data_profile_report", "bias_assessment"],
            "verification_criteria": [
                {
                    "criterion_id": "DDM-001-C1",
                    "description": "Data quality meets defined standards",
                    "verification_method": "Data profiling",
                },
                {
                    "criterion_id": "DDM-001-C2",
                    "description": "Data is representative of target population",
                    "verification_method": "Representation analysis",
                },
                {
                    "criterion_id": "DDM-001-C3",
                    "description": "No prohibited data usage",
                    "verification_method": "Data governance review",
                },
            ],
        },
        {
            "checkpoint_id": "DDM-002",
            "checkpoint_name": "Privacy Compliance",
            "description": "Data privacy and protection requirements met",
            "required_artifacts": ["dpia", "consent_records"],
            "verification_criteria": [
                {
                    "criterion_id": "DDM-002-C1",
                    "description": "DPIA completed for personal data processing",
                    "verification_method": "DPIA review",
                },
                {
                    "criterion_id": "DDM-002-C2",
                    "description": "Legal basis for data processing established",
                    "verification_method": "Legal review",
                },
            ],
        },
    ],
    LifecyclePhase.VALIDATION_VERIFICATION: [
        {
            "checkpoint_id": "VV-001",
            "checkpoint_name": "Model Validation",
            "description": "Model performance and fairness validation",
            "required_artifacts": ["validation_report", "fairness_metrics"],
            "verification_criteria": [
                {
                    "criterion_id": "VV-001-C1",
                    "description": "Model meets performance thresholds",
                    "verification_method": "Performance testing",
                },
                {
                    "criterion_id": "VV-001-C2",
                    "description": "Fairness metrics within acceptable bounds",
                    "verification_method": "Fairness analysis",
                },
                {
                    "criterion_id": "VV-001-C3",
                    "description": "Edge cases and failure modes documented",
                    "verification_method": "Edge case testing",
                },
            ],
        },
    ],
    LifecyclePhase.DEPLOYMENT: [
        {
            "checkpoint_id": "DEP-001",
            "checkpoint_name": "Deployment Readiness",
            "description": "System ready for production deployment",
            "required_artifacts": ["deployment_plan", "rollback_procedures"],
            "verification_criteria": [
                {
                    "criterion_id": "DEP-001-C1",
                    "description": "Infrastructure and security requirements met",
                    "verification_method": "Infrastructure review",
                },
                {
                    "criterion_id": "DEP-001-C2",
                    "description": "Monitoring and alerting configured",
                    "verification_method": "Monitoring verification",
                },
                {
                    "criterion_id": "DEP-001-C3",
                    "description": "User documentation and training complete",
                    "verification_method": "Documentation review",
                },
            ],
        },
        {
            "checkpoint_id": "DEP-002",
            "checkpoint_name": "AIA Approval",
            "description": "Algorithmic Impact Assessment approved",
            "required_artifacts": ["aia_report", "approval_record"],
            "verification_criteria": [
                {
                    "criterion_id": "DEP-002-C1",
                    "description": "AIA completed and reviewed",
                    "verification_method": "AIA review",
                },
                {
                    "criterion_id": "DEP-002-C2",
                    "description": "Governance board approval obtained",
                    "verification_method": "Approval record",
                },
            ],
        },
    ],
    LifecyclePhase.OPERATION_MONITORING: [
        {
            "checkpoint_id": "OM-001",
            "checkpoint_name": "Ongoing Monitoring Review",
            "description": "Regular monitoring and performance review",
            "required_artifacts": ["monitoring_report"],
            "verification_criteria": [
                {
                    "criterion_id": "OM-001-C1",
                    "description": "Performance within acceptable bounds",
                    "verification_method": "Performance metrics review",
                },
                {
                    "criterion_id": "OM-001-C2",
                    "description": "No significant drift detected",
                    "verification_method": "Drift analysis",
                },
                {
                    "criterion_id": "OM-001-C3",
                    "description": "User feedback addressed",
                    "verification_method": "Feedback review",
                },
            ],
        },
    ],
    LifecyclePhase.SHUTDOWN: [
        {
            "checkpoint_id": "SD-001",
            "checkpoint_name": "Decommissioning Verification",
            "description": "System properly decommissioned",
            "required_artifacts": ["decommission_record", "data_disposal_record"],
            "verification_criteria": [
                {
                    "criterion_id": "SD-001-C1",
                    "description": "Data properly disposed or archived",
                    "verification_method": "Data disposal verification",
                },
                {
                    "criterion_id": "SD-001-C2",
                    "description": "Lessons learned documented",
                    "verification_method": "Post-mortem review",
                },
            ],
        },
    ],
}
