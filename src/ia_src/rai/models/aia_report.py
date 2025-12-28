"""Algorithmic Impact Assessment (AIA) report models."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from .principle_evaluation import PrincipleEvaluation
from .risk_assessment import RiskAssessment
from .system_profile import SystemProfile


class StakeholderImpact(BaseModel):
    """Impact analysis for a specific stakeholder group."""

    stakeholder_group: str = Field(..., description="Name of the stakeholder group")
    relationship: str = Field(
        ..., description="Relationship to the system (user, subject, operator, etc.)"
    )
    positive_impacts: list[str] = Field(default_factory=list)
    negative_impacts: list[str] = Field(default_factory=list)
    impact_magnitude: str = Field(default="moderate")  # low, moderate, high
    mitigation_measures: list[str] = Field(default_factory=list)


class AIASection1_SystemContext(BaseModel):
    """Section 1: System Context and Purpose."""

    business_problem: str = Field(
        ..., description="Clear statement of the business problem"
    )
    business_justification: str = Field(
        default="", description="Justification for using AI"
    )
    intended_use_cases: list[str] = Field(
        default_factory=list, description="Specific intended use cases"
    )
    expected_benefits: list[str] = Field(
        default_factory=list, description="Expected benefits from the system"
    )

    # Stakeholder analysis
    stakeholder_impacts: list[StakeholderImpact] = Field(default_factory=list)

    # Scope
    scope_boundaries: str = Field(default="", description="What is in scope")
    out_of_scope: list[str] = Field(
        default_factory=list, description="What is explicitly out of scope"
    )
    geographic_scope: Optional[str] = Field(
        default=None, description="Geographic deployment scope"
    )

    # Alternatives considered
    alternatives_considered: list[str] = Field(
        default_factory=list, description="Non-AI alternatives considered"
    )
    ai_necessity_justification: str = Field(
        default="", description="Why AI is necessary"
    )


class DataSource(BaseModel):
    """Description of a data source."""

    name: str
    description: str
    data_type: str  # structured, unstructured, semi-structured
    volume: Optional[str] = None
    collection_method: str = Field(default="")
    consent_mechanism: Optional[str] = None
    retention_period: Optional[str] = None
    quality_assessment: Optional[str] = None


class AIASection2_DataAndModel(BaseModel):
    """Section 2: Data and Model Assessment."""

    # Data sources
    data_sources: list[DataSource] = Field(default_factory=list)
    data_lineage: str = Field(default="", description="Data lineage documentation")

    # Data quality
    data_quality_assessment: str = Field(
        default="", description="Overall data quality assessment"
    )
    data_quality_metrics: dict[str, Any] = Field(default_factory=dict)
    data_quality_issues: list[str] = Field(default_factory=list)

    # Representativeness
    representativeness_analysis: str = Field(
        default="", description="Analysis of data representativeness"
    )
    underrepresented_groups: list[str] = Field(default_factory=list)
    bias_in_data: list[str] = Field(
        default_factory=list, description="Known biases in data"
    )

    # Model information
    model_selection_rationale: str = Field(
        default="", description="Why this model was selected"
    )
    model_architecture: str = Field(default="")
    training_methodology: str = Field(default="")
    hyperparameters: dict[str, Any] = Field(default_factory=dict)

    # Validation
    validation_approach: str = Field(default="")
    validation_metrics: dict[str, float] = Field(default_factory=dict)
    test_set_description: str = Field(default="")

    # Limitations
    known_limitations: list[str] = Field(default_factory=list)
    edge_cases: list[str] = Field(default_factory=list)
    failure_modes: list[str] = Field(default_factory=list)


class ImpactItem(BaseModel):
    """Single impact item."""

    description: str
    affected_groups: list[str] = Field(default_factory=list)
    magnitude: str = Field(default="moderate")  # low, moderate, high
    likelihood: str = Field(default="possible")
    timeframe: str = Field(default="")  # immediate, short-term, long-term


class AIASection3_ImpactAnalysis(BaseModel):
    """Section 3: Impact Analysis."""

    # Positive impacts
    positive_impacts: list[ImpactItem] = Field(default_factory=list)

    # Negative impacts
    negative_impacts: list[ImpactItem] = Field(default_factory=list)

    # Unintended consequences
    potential_unintended_consequences: list[str] = Field(default_factory=list)
    mitigation_for_unintended: list[str] = Field(default_factory=list)

    # Disproportionate impacts
    disproportionate_impacts: list[str] = Field(
        default_factory=list, description="Groups disproportionately affected"
    )
    equity_considerations: str = Field(default="")

    # Cumulative effects
    cumulative_effects: str = Field(
        default="", description="Cumulative effects with other systems"
    )
    interaction_effects: list[str] = Field(default_factory=list)

    # Rights impact
    fundamental_rights_impact: list[str] = Field(
        default_factory=list, description="Impact on fundamental rights"
    )
    rights_mitigation_measures: list[str] = Field(default_factory=list)


class AIASection4_RiskMitigation(BaseModel):
    """Section 4: Risk Mitigation Measures."""

    # Full risk assessment
    risk_assessment: Optional[RiskAssessment] = None

    # Technical safeguards
    technical_safeguards: list[str] = Field(
        default_factory=list, description="Technical controls implemented"
    )
    technical_safeguard_details: dict[str, str] = Field(default_factory=dict)

    # Procedural safeguards
    procedural_safeguards: list[str] = Field(
        default_factory=list, description="Procedural controls implemented"
    )

    # Human oversight
    human_oversight_mechanisms: list[str] = Field(default_factory=list)
    human_intervention_points: list[str] = Field(
        default_factory=list, description="Points where humans can intervene"
    )
    override_capabilities: str = Field(default="")

    # Fallback procedures
    fallback_procedures: list[str] = Field(
        default_factory=list, description="Fallback when system fails"
    )
    degradation_handling: str = Field(
        default="", description="How graceful degradation is handled"
    )

    # Testing
    adversarial_testing: str = Field(
        default="", description="Adversarial testing conducted"
    )
    red_team_results: Optional[str] = None


class DecisionRight(BaseModel):
    """Decision right assignment."""

    role: str
    responsibilities: list[str] = Field(default_factory=list)
    authority_level: str = Field(default="")
    escalation_path: str = Field(default="")


class AIASection5_Governance(BaseModel):
    """Section 5: Governance and Accountability."""

    # Accountability framework
    accountability_framework: str = Field(
        default="", description="Overall accountability structure"
    )
    governance_body: Optional[str] = Field(
        default=None, description="Governing body for AI decisions"
    )

    # Decision rights
    decision_rights: list[DecisionRight] = Field(default_factory=list)
    raci_matrix: dict[str, dict[str, str]] = Field(
        default_factory=dict, description="RACI matrix for key activities"
    )

    # Escalation
    escalation_procedures: str = Field(default="")
    escalation_triggers: list[str] = Field(default_factory=list)

    # Audit
    audit_trail_mechanisms: list[str] = Field(default_factory=list)
    logging_requirements: list[str] = Field(default_factory=list)
    audit_frequency: str = Field(default="")

    # Incident response
    incident_response_plan: str = Field(default="")
    incident_categories: list[str] = Field(default_factory=list)
    notification_requirements: list[str] = Field(default_factory=list)

    # Documentation
    documentation_practices: list[str] = Field(default_factory=list)
    documentation_location: str = Field(default="")
    version_control: str = Field(default="")


class MonitoringMetric(BaseModel):
    """Monitoring metric definition."""

    name: str
    description: str
    threshold: Optional[str] = None
    frequency: str = Field(default="")
    responsible_party: str = Field(default="")
    alert_mechanism: str = Field(default="")


class AIASection6_Monitoring(BaseModel):
    """Section 6: Ongoing Monitoring and Review."""

    # Performance monitoring
    performance_metrics: list[MonitoringMetric] = Field(default_factory=list)
    performance_baseline: dict[str, float] = Field(default_factory=dict)

    # Fairness monitoring
    fairness_metrics: list[MonitoringMetric] = Field(default_factory=list)
    fairness_thresholds: dict[str, float] = Field(default_factory=dict)

    # Drift monitoring
    drift_detection_method: str = Field(default="")
    drift_thresholds: dict[str, float] = Field(default_factory=dict)
    drift_response_procedures: list[str] = Field(default_factory=list)

    # Review schedule
    monitoring_frequency: str = Field(default="")
    review_schedule: str = Field(default="")
    review_triggers: list[str] = Field(
        default_factory=list, description="Events triggering review"
    )

    # Feedback
    feedback_mechanisms: list[str] = Field(default_factory=list)
    complaint_handling: str = Field(default="")
    user_recourse: str = Field(
        default="", description="How users can challenge decisions"
    )

    # Continuous improvement
    continuous_improvement_process: str = Field(default="")
    retraining_triggers: list[str] = Field(default_factory=list)
    update_procedures: str = Field(default="")

    # Decommissioning
    decommissioning_criteria: list[str] = Field(default_factory=list)
    decommissioning_procedures: str = Field(default="")
    data_handling_on_decommission: str = Field(default="")


class AIARecommendation(str):
    """AIA recommendation outcomes."""

    PROCEED = "proceed"
    PROCEED_WITH_CONDITIONS = "proceed_with_conditions"
    DO_NOT_PROCEED = "do_not_proceed"
    REQUIRES_FURTHER_ASSESSMENT = "requires_further_assessment"


class AIAReport(BaseModel):
    """Complete Algorithmic Impact Assessment Report."""

    # Metadata
    report_id: str = Field(..., description="Unique report identifier")
    report_version: str = Field(default="1.0")
    created_date: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    # System being assessed
    system_profile: SystemProfile

    # AIA Sections (6 sections from the RAI framework)
    section1_context: AIASection1_SystemContext
    section2_data_model: AIASection2_DataAndModel
    section3_impact: AIASection3_ImpactAnalysis
    section4_risk_mitigation: AIASection4_RiskMitigation
    section5_governance: AIASection5_Governance
    section6_monitoring: AIASection6_Monitoring

    # Principle evaluations
    principle_evaluations: list[PrincipleEvaluation] = Field(default_factory=list)

    # Overall assessment
    overall_recommendation: str = Field(
        default="requires_further_assessment",
        description="proceed, proceed_with_conditions, do_not_proceed, requires_further_assessment",
    )
    conditions_for_approval: list[str] = Field(
        default_factory=list, description="Conditions that must be met"
    )
    blocking_issues: list[str] = Field(
        default_factory=list, description="Issues that block approval"
    )

    # Summary
    executive_summary: str = Field(default="")
    key_findings: list[str] = Field(default_factory=list)
    key_recommendations: list[str] = Field(default_factory=list)

    # Approvals
    assessment_team: list[str] = Field(default_factory=list)
    review_board_members: list[str] = Field(default_factory=list)
    review_board_approval: Optional[str] = None
    approval_date: Optional[datetime] = None

    # Compliance
    regulatory_compliance_status: dict[str, str] = Field(
        default_factory=dict, description="Status for each applicable regulation"
    )

    # Next steps
    next_review_date: Optional[datetime] = None
    follow_up_actions: list[str] = Field(default_factory=list)

    model_config = {"extra": "allow"}

    def calculate_overall_score(self) -> float:
        """Calculate overall score from principle evaluations."""
        if not self.principle_evaluations:
            return 0.0
        return sum(e.score for e in self.principle_evaluations) / len(
            self.principle_evaluations
        )

    def get_all_critical_findings(self) -> list[dict]:
        """Get all critical findings across all principle evaluations."""
        findings = []
        for eval in self.principle_evaluations:
            for finding in eval.get_critical_findings():
                findings.append(
                    {"principle": eval.principle.value, "finding": finding}
                )
        return findings
