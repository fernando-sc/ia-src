"""Alignment Agent for RAI assessments."""

from ia_src.core.context import Context
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


class AlignmentAgent(RAIAgent):
    """Agent for human alignment and ethics evaluation.

    Evaluates:
    - Human oversight mechanisms
    - Value alignment
    - Ethical considerations
    - Human-in-the-loop provisions
    - Societal impact assessment
    """

    def __init__(self, llm_provider: LLMProvider) -> None:
        super().__init__(
            name="AlignmentAgent",
            principle=Principle.ALIGNMENT,
            llm_provider=llm_provider,
            description="Evaluates human oversight, ethics, and value alignment",
        )

    def _build_system_prompt(self) -> str:
        return """You are an AI Alignment Specialist focused on ensuring AI systems remain aligned with human values.

## Your Expertise Areas

### 1. HUMAN OVERSIGHT
- Human-in-the-loop (HITL) mechanisms
- Human-on-the-loop supervision
- Override capabilities
- Escalation to human decision-makers
- Meaningful human control

### 2. VALUE ALIGNMENT
- Alignment with organizational values
- Alignment with societal norms
- Cultural considerations
- Ethical framework alignment
- Avoiding harmful objectives

### 3. ETHICS BY DESIGN
- Ethical considerations in system design
- Moral implications of decisions
- Respect for human autonomy
- Dignity and rights considerations
- Beneficial outcomes focus

### 4. SOCIETAL IMPACT
- Broader societal consequences
- Environmental considerations
- Economic impact (employment, inequality)
- Democratic implications
- Long-term effects

### 5. PROHIBITED USES
- Clear definition of prohibited applications
- Safeguards against misuse
- Dual-use considerations
- Harm prevention mechanisms
- Content policies (for generative AI)

### 6. HUMAN-CENTERED DESIGN
- User autonomy preservation
- Informed consent
- User control over AI decisions
- Transparency of AI involvement
- Appeal and contestation rights

## Evaluation Approach
1. Assess human oversight mechanisms
2. Evaluate alignment with stated values
3. Review ethical considerations in design
4. Check safeguards against misuse
5. Verify human-centered design principles

Provide recommendations for strengthening alignment with human values."""

    async def evaluate(
        self,
        system_profile: SystemProfile,
        context: Context,
    ) -> PrincipleEvaluation:
        """Evaluate alignment aspects of the AI system."""
        findings: list[Finding] = []
        strengths: list[str] = []
        weaknesses: list[str] = []
        score = 1.0

        # Check 1: Prohibited uses defined
        if not system_profile.prohibited_uses:
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-001",
                    category="governance",
                    severity=Severity.MEDIUM,
                    description="No prohibited uses defined for the system",
                    recommendation="Define and document prohibited uses to prevent misuse and establish boundaries",
                    remediation_effort=RemediationEffort.LOW,
                )
            )
            weaknesses.append("No use restrictions documented")
            score -= 0.15
        else:
            strengths.append(f"{len(system_profile.prohibited_uses)} prohibited uses defined")

        # Check 2: Affected populations and their involvement
        if system_profile.affected_populations:
            if len(system_profile.affected_populations) > 0:
                strengths.append("Affected populations identified for human-centered design")
            # Note: Ideally we'd check if they were consulted
        else:
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-002",
                    category="human_centered",
                    severity=Severity.HIGH,
                    description="No affected populations identified - limits human-centered design",
                    recommendation="Identify affected populations and consider their needs in design and operation",
                    remediation_effort=RemediationEffort.MEDIUM,
                )
            )
            weaknesses.append("Human-centered design not evident without stakeholder identification")
            score -= 0.2

        # Check 3: Autonomous systems need stronger oversight
        if system_profile.system_type.value == "autonomous":
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-003",
                    category="oversight",
                    severity=Severity.CRITICAL,
                    description="Autonomous system requires robust human oversight mechanisms",
                    recommendation="Implement human-on-the-loop supervision with ability to intervene, stop, or override",
                    remediation_effort=RemediationEffort.HIGH,
                )
            )
            weaknesses.append("Autonomous operation increases alignment risk")
            score -= 0.25

        # Check 4: Generative AI alignment considerations
        if system_profile.system_type.value == "generative":
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-004",
                    category="alignment",
                    severity=Severity.HIGH,
                    description="Generative AI has unique alignment challenges (hallucination, harmful content)",
                    recommendation="Implement content filtering, output validation, and user feedback mechanisms",
                    remediation_effort=RemediationEffort.HIGH,
                )
            )
            score -= 0.15

        # Check 5: High-risk system oversight requirements
        if system_profile.is_high_risk_eu_ai_act:
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-005",
                    category="compliance",
                    severity=Severity.HIGH,
                    description="EU AI Act requires human oversight for high-risk AI systems",
                    recommendation="Implement human oversight measures per Article 14, including ability to override AI decisions",
                    remediation_effort=RemediationEffort.HIGH,
                )
            )
            score -= 0.1

        # Check 6: Decision-making impact
        decision_types = ["classification", "recommendation"]
        if system_profile.system_type.value in decision_types:
            if "decision" in system_profile.description.lower() or "score" in system_profile.description.lower():
                findings.append(
                    Finding(
                        finding_id=f"{self._generate_evaluation_id()}-006",
                        category="ethics",
                        severity=Severity.MEDIUM,
                        description="System appears to make decisions affecting individuals",
                        recommendation="Ensure affected individuals have right to explanation, appeal, and human review",
                        remediation_effort=RemediationEffort.MEDIUM,
                    )
                )
                score -= 0.1

        # Check 7: Sensitive industry ethical requirements
        sensitive_industries = ["healthcare", "criminal_justice", "employment", "credit", "housing", "education"]
        if system_profile.industry_sector and any(
            ind in system_profile.industry_sector.lower() for ind in sensitive_industries
        ):
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-007",
                    category="ethics",
                    severity=Severity.HIGH,
                    description=f"{system_profile.industry_sector} sector has heightened ethical implications",
                    recommendation="Review sector-specific ethical guidelines and implement enhanced oversight",
                    remediation_effort=RemediationEffort.HIGH,
                )
            )
            weaknesses.append(f"Sensitive sector ({system_profile.industry_sector}) requires careful ethical review")
            score -= 0.1

        # Check 8: Use case alignment
        if system_profile.use_cases:
            strengths.append(f"{len(system_profile.use_cases)} intended use cases documented for alignment")
        else:
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-008",
                    category="alignment",
                    severity=Severity.LOW,
                    description="Intended use cases not documented",
                    recommendation="Document intended use cases to ensure system use aligns with intended purpose",
                    remediation_effort=RemediationEffort.LOW,
                )
            )
            score -= 0.05

        score = max(0.0, min(1.0, score))

        return PrincipleEvaluation(
            evaluation_id=self._generate_evaluation_id(),
            principle=Principle.ALIGNMENT,
            evaluator_agent=self.name,
            compliance_status=self._determine_compliance_status(score),
            score=score,
            confidence=0.75,
            findings=findings,
            strengths=strengths,
            weaknesses=weaknesses,
            methodology="Profile analysis + ethical considerations checklist",
            artifacts_reviewed=["system_profile"],
            limitations=["Full alignment assessment requires stakeholder engagement and ethical review"],
        )

    async def generate_recommendations(
        self,
        evaluation: PrincipleEvaluation,
        context: Context,
    ) -> list[str]:
        """Generate alignment recommendations."""
        recommendations = []

        for finding in evaluation.findings:
            recommendations.append(finding.recommendation)

        if evaluation.score < 0.7:
            recommendations.extend([
                "Implement human-in-the-loop for high-stakes decisions",
                "Establish ethics review board or committee for AI decisions",
                "Create user feedback mechanism for continuous alignment improvement",
                "Document and communicate AI limitations to all stakeholders",
            ])

        if evaluation.score < 0.5:
            recommendations.extend([
                "Conduct comprehensive ethical impact assessment with diverse stakeholders",
                "Implement kill switch or pause mechanism for autonomous operations",
                "Engage ethics experts and affected community representatives",
                "Establish regular alignment audits with external review",
            ])

        return recommendations
