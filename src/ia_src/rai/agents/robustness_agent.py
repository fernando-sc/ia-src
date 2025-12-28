"""Robustness Agent for RAI assessments."""

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


class RobustnessAgent(RAIAgent):
    """Agent for reliability and robustness evaluation.

    Evaluates:
    - System reliability and availability
    - Performance consistency
    - Error handling and recovery
    - Drift detection capabilities
    - Edge case handling
    """

    def __init__(self, llm_provider: LLMProvider) -> None:
        super().__init__(
            name="RobustnessAgent",
            principle=Principle.ROBUSTNESS,
            llm_provider=llm_provider,
            description="Evaluates reliability, performance consistency, and system resilience",
        )

    def _build_system_prompt(self) -> str:
        return """You are an AI Robustness Specialist focused on ensuring AI systems operate reliably.

## Your Expertise Areas

### 1. RELIABILITY
- System availability requirements
- Failure mode analysis
- Recovery procedures
- Redundancy mechanisms
- Graceful degradation

### 2. PERFORMANCE CONSISTENCY
- Output stability across similar inputs
- Performance under load
- Latency requirements
- Throughput consistency
- Resource utilization

### 3. ERROR HANDLING
- Input validation
- Graceful error handling
- Fallback mechanisms
- Error logging and monitoring
- User-facing error communication

### 4. DRIFT DETECTION
- Data drift monitoring
- Concept drift detection
- Model performance degradation
- Retraining triggers
- Continuous validation

### 5. EDGE CASES
- Boundary condition handling
- Out-of-distribution detection
- Anomaly handling
- Stress testing results
- Adversarial input resilience

### 6. OPERATIONAL EXCELLENCE
- Monitoring and alerting
- Logging completeness
- SLA compliance
- Capacity planning
- Disaster recovery

## Evaluation Approach
1. Assess reliability requirements and measures
2. Evaluate performance monitoring capabilities
3. Review error handling and fallback procedures
4. Check drift detection mechanisms
5. Verify edge case handling

Provide actionable recommendations for improving robustness."""

    async def evaluate(
        self,
        system_profile: SystemProfile,
        context: Context,
    ) -> PrincipleEvaluation:
        """Evaluate robustness aspects of the AI system."""
        findings: list[Finding] = []
        strengths: list[str] = []
        weaknesses: list[str] = []
        score = 1.0

        # Check 1: Known limitations documented
        if not system_profile.known_limitations:
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-001",
                    category="documentation",
                    severity=Severity.HIGH,
                    description="No known limitations documented - critical for understanding failure modes",
                    recommendation="Document known limitations, failure modes, and edge cases",
                    remediation_effort=RemediationEffort.MEDIUM,
                )
            )
            weaknesses.append("Failure modes not documented")
            score -= 0.2
        else:
            strengths.append(f"{len(system_profile.known_limitations)} limitations documented")

        # Check 2: System in operation phase should have monitoring
        if system_profile.current_phase.value in ["deployment", "operation_monitoring"]:
            if not context.get_variable("monitoring_configured", False):
                findings.append(
                    Finding(
                        finding_id=f"{self._generate_evaluation_id()}-002",
                        category="operations",
                        severity=Severity.HIGH,
                        description="System in production phase without confirmed monitoring",
                        recommendation="Implement comprehensive monitoring for performance, drift, and errors",
                        remediation_effort=RemediationEffort.MEDIUM,
                    )
                )
                weaknesses.append("Monitoring status not confirmed for production system")
                score -= 0.2

        # Check 3: Version management
        if system_profile.version == "1.0.0":
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-003",
                    category="operations",
                    severity=Severity.LOW,
                    description="Version appears to be initial - verify version control and rollback capabilities",
                    recommendation="Implement semantic versioning with documented change history and rollback procedures",
                    remediation_effort=RemediationEffort.LOW,
                )
            )
            score -= 0.05

        # Check 4: Critical system types need higher robustness
        critical_types = ["autonomous", "generative"]
        if system_profile.system_type.value in critical_types:
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-004",
                    category="risk",
                    severity=Severity.MEDIUM,
                    description=f"{system_profile.system_type.value} systems require enhanced robustness measures",
                    recommendation="Implement comprehensive testing including adversarial inputs and edge cases",
                    remediation_effort=RemediationEffort.HIGH,
                )
            )
            score -= 0.1

        # Check 5: High-risk systems robustness requirements
        if system_profile.is_high_risk_eu_ai_act:
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-005",
                    category="compliance",
                    severity=Severity.MEDIUM,
                    description="High-risk system must meet EU AI Act accuracy and robustness requirements",
                    recommendation="Document performance metrics and implement continuous performance monitoring per Article 15",
                    remediation_effort=RemediationEffort.HIGH,
                )
            )
            score -= 0.1

        # Check 6: Deployment date without last assessment
        if system_profile.deployment_date and not system_profile.last_assessment_date:
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-006",
                    category="operations",
                    severity=Severity.MEDIUM,
                    description="Deployed system without recorded assessment - may indicate drift",
                    recommendation="Establish regular assessment schedule to detect performance degradation",
                    remediation_effort=RemediationEffort.MEDIUM,
                )
            )
            weaknesses.append("No recorded post-deployment assessment")
            score -= 0.15

        # Check 7: Industry reliability requirements
        high_reliability_sectors = ["healthcare", "finance", "transportation", "energy", "telecommunications"]
        if system_profile.industry_sector and any(
            sec in system_profile.industry_sector.lower() for sec in high_reliability_sectors
        ):
            strengths.append(f"Operating in {system_profile.industry_sector} - high reliability expected")
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-007",
                    category="compliance",
                    severity=Severity.LOW,
                    description=f"{system_profile.industry_sector} sector typically has strict availability requirements",
                    recommendation="Review sector-specific reliability standards and SLA requirements",
                    remediation_effort=RemediationEffort.MEDIUM,
                )
            )

        score = max(0.0, min(1.0, score))

        return PrincipleEvaluation(
            evaluation_id=self._generate_evaluation_id(),
            principle=Principle.ROBUSTNESS,
            evaluator_agent=self.name,
            compliance_status=self._determine_compliance_status(score),
            score=score,
            confidence=0.70,
            findings=findings,
            strengths=strengths,
            weaknesses=weaknesses,
            methodology="Profile analysis + operational checklist",
            artifacts_reviewed=["system_profile"],
            limitations=["Full robustness assessment requires performance testing data"],
        )

    async def generate_recommendations(
        self,
        evaluation: PrincipleEvaluation,
        context: Context,
    ) -> list[str]:
        """Generate robustness recommendations."""
        recommendations = []

        for finding in evaluation.findings:
            recommendations.append(finding.recommendation)

        if evaluation.score < 0.7:
            recommendations.extend([
                "Implement data and concept drift monitoring with automated alerts",
                "Establish performance baselines and degradation thresholds",
                "Create comprehensive test suite including edge cases and adversarial inputs",
                "Document and test fallback procedures for system failures",
            ])

        if evaluation.score < 0.5:
            recommendations.extend([
                "Conduct chaos engineering exercises to test system resilience",
                "Implement automated performance regression testing in CI/CD",
                "Establish SLAs with clear availability and performance targets",
                "Create runbooks for common failure scenarios",
            ])

        return recommendations
