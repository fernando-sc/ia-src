"""Risk assessment models for RAI evaluations."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class RiskCategory(str, Enum):
    """Categories of AI-related risks."""

    TECHNICAL = "technical"
    ETHICAL = "ethical"
    LEGAL = "legal"
    OPERATIONAL = "operational"
    REPUTATIONAL = "reputational"
    SAFETY = "safety"
    PRIVACY = "privacy"
    SECURITY = "security"


class Likelihood(str, Enum):
    """Likelihood of risk occurrence."""

    RARE = "rare"  # 1
    UNLIKELY = "unlikely"  # 2
    POSSIBLE = "possible"  # 3
    LIKELY = "likely"  # 4
    ALMOST_CERTAIN = "almost_certain"  # 5


class Impact(str, Enum):
    """Impact severity if risk materializes."""

    NEGLIGIBLE = "negligible"  # 1
    MINOR = "minor"  # 2
    MODERATE = "moderate"  # 3
    MAJOR = "major"  # 4
    CATASTROPHIC = "catastrophic"  # 5


class MitigationStrategy(str, Enum):
    """Risk mitigation strategies."""

    AVOID = "avoid"
    REDUCE = "reduce"
    TRANSFER = "transfer"
    ACCEPT = "accept"


class Risk(BaseModel):
    """Individual risk identification and assessment."""

    risk_id: str = Field(..., description="Unique risk identifier")
    title: str = Field(..., description="Brief risk title")
    description: str = Field(..., description="Detailed risk description")
    category: RiskCategory = Field(..., description="Risk category")

    # Risk assessment (5x5 matrix)
    likelihood: Likelihood = Field(..., description="Likelihood of occurrence")
    impact: Impact = Field(..., description="Potential impact severity")

    # Affected areas
    affected_principles: list[str] = Field(
        default_factory=list, description="RAI principles affected by this risk"
    )
    affected_stakeholders: list[str] = Field(
        default_factory=list, description="Stakeholders affected if risk materializes"
    )

    # Controls
    existing_controls: list[str] = Field(
        default_factory=list, description="Controls already in place"
    )
    control_effectiveness: Optional[str] = Field(
        default=None, description="Effectiveness of existing controls"
    )

    # Residual risk
    residual_likelihood: Optional[Likelihood] = None
    residual_impact: Optional[Impact] = None

    @property
    def risk_score(self) -> int:
        """Calculate risk score (1-25) from likelihood and impact."""
        likelihood_map = {
            Likelihood.RARE: 1,
            Likelihood.UNLIKELY: 2,
            Likelihood.POSSIBLE: 3,
            Likelihood.LIKELY: 4,
            Likelihood.ALMOST_CERTAIN: 5,
        }
        impact_map = {
            Impact.NEGLIGIBLE: 1,
            Impact.MINOR: 2,
            Impact.MODERATE: 3,
            Impact.MAJOR: 4,
            Impact.CATASTROPHIC: 5,
        }
        return likelihood_map[self.likelihood] * impact_map[self.impact]

    @property
    def risk_level(self) -> str:
        """Determine risk level from score."""
        score = self.risk_score
        if score <= 4:
            return "low"
        elif score <= 9:
            return "medium"
        elif score <= 16:
            return "high"
        else:
            return "critical"


class Mitigation(BaseModel):
    """Risk mitigation measure."""

    mitigation_id: str = Field(..., description="Unique mitigation identifier")
    risk_ids: list[str] = Field(..., description="Risks this mitigation addresses")
    strategy: MitigationStrategy = Field(..., description="Mitigation strategy type")

    title: str = Field(..., description="Brief mitigation title")
    description: str = Field(..., description="Detailed description")
    implementation_steps: list[str] = Field(
        default_factory=list, description="Steps to implement the mitigation"
    )

    # Responsibility
    responsible_party: str = Field(..., description="Who is responsible")
    timeline: Optional[str] = Field(default=None, description="Implementation timeline")
    resources_required: Optional[str] = Field(
        default=None, description="Resources needed"
    )

    # Effectiveness
    effectiveness_estimate: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Estimated effectiveness (0-1)",
    )
    verification_method: Optional[str] = Field(
        default=None, description="How to verify effectiveness"
    )

    # Status
    status: str = Field(default="planned")  # planned, in_progress, completed
    completion_date: Optional[datetime] = None


class RiskAssessment(BaseModel):
    """Complete risk assessment for an AI system."""

    # Identification
    assessment_id: str = Field(..., description="Unique assessment identifier")
    system_id: str = Field(..., description="ID of the assessed system")
    assessment_date: datetime = Field(default_factory=datetime.utcnow)
    assessor: str = Field(..., description="Person/agent conducting assessment")

    # Context
    assessment_scope: str = Field(default="", description="Scope of the assessment")
    methodology: str = Field(default="", description="Methodology used")

    # Risk identification
    identified_risks: list[Risk] = Field(default_factory=list)

    # Mitigation strategies
    mitigations: list[Mitigation] = Field(default_factory=list)

    # Summary
    overall_risk_level: str = Field(default="medium")  # low, medium, high, critical
    risk_appetite_alignment: bool = Field(
        default=True, description="Whether risks align with organization's appetite"
    )

    # Recommendations
    priority_risks: list[str] = Field(
        default_factory=list, description="Risk IDs requiring immediate attention"
    )
    monitoring_recommendations: list[str] = Field(default_factory=list)

    # Review
    next_review_date: Optional[datetime] = None
    approval_status: str = Field(default="pending")  # pending, approved, rejected
    approver: Optional[str] = None
    approval_date: Optional[datetime] = None
    approval_notes: Optional[str] = None

    model_config = {"extra": "allow"}

    def get_high_risks(self) -> list[Risk]:
        """Return risks with high or critical level."""
        return [r for r in self.identified_risks if r.risk_level in ("high", "critical")]

    def get_unmitigated_risks(self) -> list[Risk]:
        """Return risks without assigned mitigations."""
        mitigated_risk_ids = set()
        for m in self.mitigations:
            mitigated_risk_ids.update(m.risk_ids)
        return [r for r in self.identified_risks if r.risk_id not in mitigated_risk_ids]

    def calculate_overall_risk_level(self) -> str:
        """Calculate overall risk level from all risks."""
        if not self.identified_risks:
            return "low"

        max_score = max(r.risk_score for r in self.identified_risks)
        avg_score = sum(r.risk_score for r in self.identified_risks) / len(
            self.identified_risks
        )

        # Weight towards max score
        weighted_score = 0.6 * max_score + 0.4 * avg_score

        if weighted_score <= 4:
            return "low"
        elif weighted_score <= 9:
            return "medium"
        elif weighted_score <= 16:
            return "high"
        else:
            return "critical"
