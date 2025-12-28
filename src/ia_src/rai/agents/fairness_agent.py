"""Fairness Agent for RAI assessments."""

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


class FairnessAgent(RAIAgent):
    """Agent for bias detection and fairness evaluation.

    Evaluates:
    - Bias in training data and model outputs
    - Fairness metrics across protected groups
    - Data representativeness
    - Equity considerations
    - Accessibility and inclusion
    """

    def __init__(self, llm_provider: LLMProvider) -> None:
        super().__init__(
            name="FairnessAgent",
            principle=Principle.FAIRNESS,
            llm_provider=llm_provider,
            description="Detects bias, evaluates fairness metrics, ensures equitable outcomes",
        )

    def _build_system_prompt(self) -> str:
        return """You are an AI Fairness Specialist focused on ensuring AI systems operate equitably.

## Your Expertise Areas

### 1. BIAS DETECTION
- Protected attribute analysis (race, gender, age, disability, religion, etc.)
- Proxy variable identification
- Historical bias in training data
- Sampling bias detection
- Label bias identification
- Algorithmic amplification of existing biases

### 2. FAIRNESS METRICS
- Demographic parity / Statistical parity
- Equalized odds
- Equal opportunity
- Calibration across groups
- Individual fairness measures
- Counterfactual fairness

### 3. DATA REPRESENTATIVENESS
- Population coverage analysis
- Underrepresented group identification
- Data balancing recommendations
- Intersectional analysis
- Geographic representation

### 4. EQUITY CONSIDERATIONS
- Disparate impact analysis (80% rule)
- Outcome distribution analysis
- Access equity
- Socioeconomic impact assessment
- Historical disadvantage consideration

### 5. ACCESSIBILITY & INCLUSION
- Accessibility for persons with disabilities
- Language and cultural inclusivity
- Digital divide considerations
- Universal design principles

## Evaluation Approach
1. Analyze data and model for bias indicators
2. Calculate relevant fairness metrics
3. Assess representativeness of training data
4. Evaluate potential disparate impacts
5. Check accessibility considerations

Provide specific, actionable recommendations for improving fairness."""

    async def evaluate(
        self,
        system_profile: SystemProfile,
        context: Context,
    ) -> PrincipleEvaluation:
        """Evaluate fairness aspects of the AI system."""
        findings: list[Finding] = []
        strengths: list[str] = []
        weaknesses: list[str] = []
        metrics: dict = {}
        score = 1.0

        # Check 1: Affected populations identified
        if not system_profile.affected_populations:
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-001",
                    category="equity",
                    severity=Severity.HIGH,
                    description="Affected populations not identified - cannot assess fairness across groups",
                    recommendation="Conduct stakeholder analysis to identify all affected groups including vulnerable populations",
                    remediation_effort=RemediationEffort.MEDIUM,
                )
            )
            weaknesses.append("No affected populations identified for fairness analysis")
            score -= 0.25
        else:
            strengths.append(
                f"{len(system_profile.affected_populations)} affected groups identified"
            )
            metrics["affected_groups_count"] = len(system_profile.affected_populations)

        # Check 2: Training data description for representativeness
        if not system_profile.training_data_description:
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-002",
                    category="data_quality",
                    severity=Severity.HIGH,
                    description="Training data not documented - cannot assess data representativeness",
                    recommendation="Document training data sources, demographics, and collection methodology",
                    remediation_effort=RemediationEffort.MEDIUM,
                )
            )
            weaknesses.append("Cannot assess data representativeness without documentation")
            score -= 0.2
        else:
            strengths.append("Training data sources documented")

        # Check 3: System type specific fairness concerns
        high_risk_types = ["classification", "recommendation", "nlp"]
        if system_profile.system_type.value in high_risk_types:
            if system_profile.risk_level.value == "low":
                findings.append(
                    Finding(
                        finding_id=f"{self._generate_evaluation_id()}-003",
                        category="risk_assessment",
                        severity=Severity.MEDIUM,
                        description=f"{system_profile.system_type.value} systems often have fairness implications - verify risk assessment",
                        recommendation="Review risk classification considering fairness implications for affected groups",
                        remediation_effort=RemediationEffort.LOW,
                    )
                )
                score -= 0.1

        # Check 4: Known limitations include fairness considerations
        fairness_terms = ["bias", "fair", "discriminat", "equit", "disparate"]
        has_fairness_limitations = any(
            any(term in lim.lower() for term in fairness_terms)
            for lim in system_profile.known_limitations
        )
        if not has_fairness_limitations and system_profile.known_limitations:
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-004",
                    category="documentation",
                    severity=Severity.MEDIUM,
                    description="Known limitations don't address fairness concerns",
                    recommendation="Document any known fairness limitations or bias risks",
                    remediation_effort=RemediationEffort.LOW,
                )
            )
            score -= 0.1
        elif has_fairness_limitations:
            strengths.append("Fairness considerations documented in limitations")

        # Check 5: High-risk classification fairness requirements
        if system_profile.is_high_risk_eu_ai_act:
            # High-risk systems need rigorous fairness assessment
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-005",
                    category="compliance",
                    severity=Severity.MEDIUM,
                    description="High-risk system requires formal bias testing and fairness metrics",
                    recommendation="Implement systematic fairness testing with documented metrics and thresholds",
                    remediation_effort=RemediationEffort.HIGH,
                )
            )
            weaknesses.append("High-risk system needs enhanced fairness verification")
            score -= 0.1

        # Check 6: Industry-specific fairness requirements
        sensitive_industries = ["finance", "healthcare", "employment", "education", "criminal_justice", "housing"]
        if system_profile.industry_sector and any(
            ind in system_profile.industry_sector.lower() for ind in sensitive_industries
        ):
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-006",
                    category="compliance",
                    severity=Severity.HIGH,
                    description=f"{system_profile.industry_sector} sector has heightened fairness requirements",
                    recommendation="Review sector-specific anti-discrimination regulations and implement appropriate controls",
                    remediation_effort=RemediationEffort.HIGH,
                )
            )
            score -= 0.1

        # Use tools if available
        bias_tool = next((t for t in self._tools if t.name == "bias_detection"), None)
        if bias_tool:
            data_path = context.get_variable("data_path")
            if data_path:
                try:
                    result = await bias_tool.execute(
                        data_path=data_path,
                        protected_attributes=context.get_variable("protected_attributes", []),
                    )
                    if result.success:
                        metrics.update(result.output.get("metrics", {}))
                except Exception:
                    pass

        score = max(0.0, min(1.0, score))

        return PrincipleEvaluation(
            evaluation_id=self._generate_evaluation_id(),
            principle=Principle.FAIRNESS,
            evaluator_agent=self.name,
            compliance_status=self._determine_compliance_status(score),
            score=score,
            confidence=0.75,  # Lower confidence when we can't access actual data
            findings=findings,
            strengths=strengths,
            weaknesses=weaknesses,
            metrics_collected=metrics,
            methodology="Profile analysis + bias detection tools (when available)",
            artifacts_reviewed=["system_profile"],
            limitations=["Full bias analysis requires access to training data and model outputs"],
        )

    async def generate_recommendations(
        self,
        evaluation: PrincipleEvaluation,
        context: Context,
    ) -> list[str]:
        """Generate fairness recommendations."""
        recommendations = []

        for finding in evaluation.findings:
            recommendations.append(finding.recommendation)

        if evaluation.score < 0.7:
            recommendations.extend([
                "Implement fairness metrics monitoring (demographic parity, equalized odds)",
                "Conduct regular bias audits with diverse testing teams",
                "Review data collection processes for sampling bias",
                "Establish fairness thresholds and automated alerts",
            ])

        if evaluation.score < 0.5:
            recommendations.extend([
                "Engage external fairness audit from qualified third party",
                "Implement bias mitigation techniques (re-sampling, re-weighting, adversarial debiasing)",
                "Create fairness review board with diverse representation",
                "Develop remediation process for identified bias issues",
            ])

        return recommendations
