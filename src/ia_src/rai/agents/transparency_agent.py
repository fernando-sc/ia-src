"""Transparency Agent for RAI assessments."""

from ia_src.core.context import Context
from ia_src.core.message import Message
from ia_src.llm.base_provider import LLMProvider
from ia_src.rai.agents.base_rai_agent import RAIAgent
from ia_src.rai.models import (
    Finding,
    Principle,
    PrincipleEvaluation,
    RemediationEffort,
    Severity,
    SystemProfile,
)


class TransparencyAgent(RAIAgent):
    """Agent for explainability and transparency evaluation.

    Evaluates:
    - Model explainability mechanisms
    - Documentation completeness
    - Stakeholder communication
    - Auditability provisions
    - Decision explanation capabilities
    """

    def __init__(self, llm_provider: LLMProvider) -> None:
        super().__init__(
            name="TransparencyAgent",
            principle=Principle.TRANSPARENCY,
            llm_provider=llm_provider,
            description="Evaluates explainability, documentation, and stakeholder communication",
        )

    def _build_system_prompt(self) -> str:
        return """You are an AI Transparency Specialist focused on ensuring AI systems are understandable and auditable.

## Your Expertise Areas

### 1. EXPLAINABILITY
- Model interpretability techniques (SHAP, LIME, attention visualization)
- Feature importance communication
- Decision path transparency
- Counterfactual explanations
- Confidence/uncertainty communication

### 2. DOCUMENTATION
- Model cards and data sheets
- Technical documentation completeness
- Version history and change logs
- Training data documentation
- Limitations and failure mode documentation

### 3. STAKEHOLDER COMMUNICATION
- User-facing explanations
- Disclosure of AI use to affected parties
- Appropriate level of technical detail
- Accessibility of information
- Multilingual considerations

### 4. AUDITABILITY
- Decision logging and traceability
- Reproducibility of outputs
- Third-party audit capability
- Evidence preservation
- Regulatory reporting readiness

### 5. PROACTIVE DISCLOSURE
- Clear labeling of AI-generated content
- Notification of automated decision-making
- Right to explanation mechanisms
- Appeals and contestation processes

## Evaluation Approach
1. Assess documentation completeness and accuracy
2. Evaluate explanation mechanisms for different stakeholders
3. Check audit trail and traceability
4. Verify stakeholder communication adequacy
5. Identify transparency gaps

Provide actionable recommendations for improving transparency."""

    async def evaluate(
        self,
        system_profile: SystemProfile,
        context: Context,
    ) -> PrincipleEvaluation:
        """Evaluate transparency aspects of the AI system."""
        findings: list[Finding] = []
        strengths: list[str] = []
        weaknesses: list[str] = []
        score = 1.0

        # Check 1: System description quality
        if len(system_profile.description) < 50:
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-001",
                    category="documentation",
                    severity=Severity.MEDIUM,
                    description="System description is too brief for adequate understanding",
                    recommendation="Provide detailed system description including purpose, functionality, and scope",
                    remediation_effort=RemediationEffort.LOW,
                )
            )
            weaknesses.append("Insufficient system documentation")
            score -= 0.1
        else:
            strengths.append("Adequate system description provided")

        # Check 2: Model architecture documented
        if not system_profile.model_architecture:
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-002",
                    category="documentation",
                    severity=Severity.MEDIUM,
                    description="Model architecture not documented",
                    recommendation="Document model architecture for technical transparency and auditability",
                    remediation_effort=RemediationEffort.MEDIUM,
                )
            )
            weaknesses.append("Missing model architecture documentation")
            score -= 0.15
        else:
            strengths.append(f"Model architecture documented: {system_profile.model_architecture}")

        # Check 3: Training data description
        if not system_profile.training_data_description:
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-003",
                    category="documentation",
                    severity=Severity.HIGH,
                    description="Training data sources not documented",
                    recommendation="Create data sheet documenting training data sources, collection methods, and limitations",
                    remediation_effort=RemediationEffort.MEDIUM,
                )
            )
            weaknesses.append("No training data documentation")
            score -= 0.2
        else:
            strengths.append("Training data sources documented")

        # Check 4: Input/Output transparency
        if not system_profile.input_data_types or not system_profile.output_data_types:
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-004",
                    category="documentation",
                    severity=Severity.MEDIUM,
                    description="Input and/or output data types not specified",
                    recommendation="Document all input and output data types for operational transparency",
                    remediation_effort=RemediationEffort.LOW,
                )
            )
            score -= 0.1
        else:
            strengths.append(
                f"Data types documented: {len(system_profile.input_data_types)} inputs, "
                f"{len(system_profile.output_data_types)} outputs"
            )

        # Check 5: Use cases documented
        if not system_profile.use_cases:
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-005",
                    category="documentation",
                    severity=Severity.LOW,
                    description="Specific use cases not documented",
                    recommendation="Document intended use cases to clarify system purpose and appropriate use",
                    remediation_effort=RemediationEffort.LOW,
                )
            )
            score -= 0.05
        else:
            strengths.append(f"{len(system_profile.use_cases)} use cases documented")

        # Check 6: Prohibited uses documented
        if not system_profile.prohibited_uses:
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-006",
                    category="documentation",
                    severity=Severity.MEDIUM,
                    description="Prohibited uses not specified",
                    recommendation="Define and document prohibited uses to prevent misuse",
                    remediation_effort=RemediationEffort.LOW,
                )
            )
            weaknesses.append("No prohibited uses documented")
            score -= 0.1
        else:
            strengths.append(f"{len(system_profile.prohibited_uses)} prohibited uses documented")

        # Check 7: Version tracking
        if system_profile.version == "1.0.0":
            # Default version might indicate lack of version management
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-007",
                    category="auditability",
                    severity=Severity.LOW,
                    description="Version appears to be default - verify version tracking is in place",
                    recommendation="Implement semantic versioning with change documentation",
                    remediation_effort=RemediationEffort.LOW,
                )
            )
            score -= 0.05

        # Ensure score is in valid range
        score = max(0.0, min(1.0, score))

        return PrincipleEvaluation(
            evaluation_id=self._generate_evaluation_id(),
            principle=Principle.TRANSPARENCY,
            evaluator_agent=self.name,
            compliance_status=self._determine_compliance_status(score),
            score=score,
            confidence=0.80,
            findings=findings,
            strengths=strengths,
            weaknesses=weaknesses,
            methodology="Documentation analysis + completeness checks",
            artifacts_reviewed=["system_profile"],
        )

    async def generate_recommendations(
        self,
        evaluation: PrincipleEvaluation,
        context: Context,
    ) -> list[str]:
        """Generate transparency recommendations."""
        recommendations = []

        for finding in evaluation.findings:
            recommendations.append(finding.recommendation)

        if evaluation.score < 0.7:
            recommendations.extend([
                "Create comprehensive Model Card following Google/Hugging Face template",
                "Implement user-facing explanation interface for AI decisions",
                "Develop Data Sheet for training datasets",
                "Establish clear AI disclosure policy for affected stakeholders",
            ])

        if evaluation.score < 0.5:
            recommendations.extend([
                "Conduct transparency gap assessment with stakeholder input",
                "Implement explainability tools (SHAP, LIME) for model interpretation",
                "Create tiered explanation system for different audience levels",
            ])

        return recommendations
