"""Principle evaluation models for RAI assessments."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class Principle(str, Enum):
    """The six fundamental RAI principles."""

    ACCOUNTABILITY = "accountability"
    TRANSPARENCY = "transparency"
    FAIRNESS = "fairness"
    SECURITY = "security"
    ROBUSTNESS = "robustness"
    ALIGNMENT = "alignment"


class ComplianceStatus(str, Enum):
    """Compliance status for a principle."""

    COMPLIANT = "compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    NOT_ASSESSED = "not_assessed"


class Severity(str, Enum):
    """Severity levels for findings."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RemediationEffort(str, Enum):
    """Effort required for remediation."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Finding(BaseModel):
    """Individual finding within an evaluation."""

    finding_id: str = Field(..., description="Unique finding identifier")
    category: str = Field(..., description="Category of the finding")
    severity: Severity = Field(..., description="Severity level")
    description: str = Field(..., description="Detailed description of the finding")
    evidence: Optional[str] = Field(
        default=None, description="Evidence supporting the finding"
    )
    recommendation: str = Field(..., description="Recommended action")
    remediation_effort: RemediationEffort = Field(
        ..., description="Effort required to remediate"
    )
    affected_objective: Optional[str] = Field(
        default=None, description="RAI objective affected"
    )


class Recommendation(BaseModel):
    """Actionable recommendation."""

    recommendation_id: str
    priority: Severity = Field(..., description="Priority level")
    title: str
    description: str
    implementation_steps: list[str] = Field(default_factory=list)
    expected_impact: str = Field(default="")
    resources_required: Optional[str] = None


class PrincipleEvaluation(BaseModel):
    """Evaluation results for a single RAI principle."""

    # Identification
    evaluation_id: str = Field(default="")
    principle: Principle
    evaluation_date: datetime = Field(default_factory=datetime.utcnow)
    evaluator_agent: str = Field(..., description="Name of the evaluating agent")

    # Scoring
    compliance_status: ComplianceStatus = Field(default=ComplianceStatus.NOT_ASSESSED)
    score: float = Field(
        ..., ge=0.0, le=1.0, description="Compliance score from 0 to 1"
    )
    confidence: float = Field(
        default=0.8, ge=0.0, le=1.0, description="Confidence in the evaluation"
    )

    # Findings
    findings: list[Finding] = Field(default_factory=list)
    strengths: list[str] = Field(
        default_factory=list, description="Identified strengths"
    )
    weaknesses: list[str] = Field(
        default_factory=list, description="Identified weaknesses"
    )

    # Recommendations
    recommendations: list[Recommendation] = Field(default_factory=list)
    immediate_actions: list[str] = Field(
        default_factory=list, description="Actions needed immediately"
    )
    long_term_improvements: list[str] = Field(
        default_factory=list, description="Long-term improvement suggestions"
    )

    # Evidence and metrics
    artifacts_reviewed: list[str] = Field(
        default_factory=list, description="Artifacts examined during evaluation"
    )
    metrics_collected: dict[str, Any] = Field(
        default_factory=dict, description="Quantitative metrics collected"
    )

    # Methodology
    methodology: str = Field(default="", description="Evaluation methodology used")
    limitations: list[str] = Field(
        default_factory=list, description="Limitations of the evaluation"
    )

    model_config = {"extra": "allow"}

    def get_critical_findings(self) -> list[Finding]:
        """Return only critical severity findings."""
        return [f for f in self.findings if f.severity == Severity.CRITICAL]

    def get_high_priority_recommendations(self) -> list[Recommendation]:
        """Return high and critical priority recommendations."""
        return [
            r
            for r in self.recommendations
            if r.priority in (Severity.HIGH, Severity.CRITICAL)
        ]
