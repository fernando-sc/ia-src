"""Security Agent for RAI assessments."""

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


class SecurityAgent(RAIAgent):
    """Agent for security and privacy assessment.

    Evaluates:
    - Data privacy compliance
    - Security vulnerabilities
    - Adversarial robustness
    - Incident response readiness
    - Access control mechanisms
    """

    def __init__(self, llm_provider: LLMProvider) -> None:
        super().__init__(
            name="SecurityAgent",
            principle=Principle.SECURITY,
            llm_provider=llm_provider,
            description="Assesses privacy compliance, identifies vulnerabilities, recommends safeguards",
        )

    def _build_system_prompt(self) -> str:
        return """You are an AI Security & Privacy Specialist focused on protecting AI systems and data.

## Your Expertise Areas

### 1. PRIVACY BY DESIGN
- Data minimization assessment
- Purpose limitation verification
- Consent mechanism review
- Data retention policies
- Anonymization/pseudonymization
- Privacy-enhancing technologies (differential privacy, federated learning)

### 2. SECURITY VULNERABILITIES
- Model vulnerability analysis
- Adversarial attack vectors (evasion, poisoning, extraction)
- Model inversion risks
- Membership inference attacks
- Data poisoning risks
- Prompt injection (for LLMs)

### 3. DATA PROTECTION COMPLIANCE
- GDPR compliance (Articles 5-22)
- LGPD (Brazil) requirements
- CCPA (California) requirements
- HIPAA (healthcare)
- PCI-DSS (financial)
- Sector-specific requirements

### 4. ACCESS CONTROL
- Authentication mechanisms
- Authorization models
- Role-based access control
- Audit logging
- Privileged access management

### 5. INCIDENT RESPONSE
- Breach detection capabilities
- Incident response procedures
- Notification requirements
- Recovery procedures
- Forensic capabilities

## Evaluation Approach
1. Assess data protection measures
2. Identify security vulnerabilities
3. Verify compliance with privacy regulations
4. Evaluate access control adequacy
5. Check incident response readiness

Provide specific security and privacy recommendations."""

    async def evaluate(
        self,
        system_profile: SystemProfile,
        context: Context,
    ) -> PrincipleEvaluation:
        """Evaluate security and privacy aspects of the AI system."""
        findings: list[Finding] = []
        strengths: list[str] = []
        weaknesses: list[str] = []
        score = 1.0

        # Check 1: Privacy regulations in applicable regulations
        privacy_regs = ["gdpr", "lgpd", "ccpa", "hipaa", "privacy"]
        has_privacy_reg = any(
            any(reg in r.lower() for reg in privacy_regs)
            for r in system_profile.applicable_regulations
        )

        if not has_privacy_reg and system_profile.input_data_types:
            # System processes data but no privacy regulations identified
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-001",
                    category="privacy",
                    severity=Severity.HIGH,
                    description="No privacy regulations identified for data-processing system",
                    recommendation="Identify and document applicable privacy regulations (GDPR, LGPD, CCPA, etc.)",
                    remediation_effort=RemediationEffort.MEDIUM,
                )
            )
            weaknesses.append("Privacy compliance not addressed")
            score -= 0.2
        elif has_privacy_reg:
            strengths.append("Privacy regulations identified and documented")

        # Check 2: Sensitive data types
        sensitive_types = ["personal", "pii", "health", "financial", "biometric", "location"]
        processes_sensitive = any(
            any(st in dt.lower() for st in sensitive_types)
            for dt in system_profile.input_data_types
        )

        if processes_sensitive:
            if system_profile.risk_level.value == "low":
                findings.append(
                    Finding(
                        finding_id=f"{self._generate_evaluation_id()}-002",
                        category="risk",
                        severity=Severity.HIGH,
                        description="System processes sensitive data but classified as low risk",
                        recommendation="Review risk classification - sensitive data processing typically requires elevated security",
                        remediation_effort=RemediationEffort.LOW,
                    )
                )
                weaknesses.append("Risk classification may underestimate security requirements")
                score -= 0.2

        # Check 3: Training data privacy
        if system_profile.training_data_description:
            desc_lower = system_profile.training_data_description.lower()
            if any(st in desc_lower for st in sensitive_types):
                findings.append(
                    Finding(
                        finding_id=f"{self._generate_evaluation_id()}-003",
                        category="privacy",
                        severity=Severity.MEDIUM,
                        description="Training data may contain sensitive information",
                        recommendation="Verify appropriate consent, anonymization, and data protection measures for training data",
                        remediation_effort=RemediationEffort.HIGH,
                    )
                )
                score -= 0.1

        # Check 4: High-risk EU AI Act security requirements
        if system_profile.is_high_risk_eu_ai_act:
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-004",
                    category="compliance",
                    severity=Severity.MEDIUM,
                    description="High-risk system requires enhanced security measures under EU AI Act",
                    recommendation="Implement cybersecurity measures per EU AI Act Article 15, including resilience to attacks",
                    remediation_effort=RemediationEffort.HIGH,
                )
            )
            score -= 0.1

        # Check 5: Model type security considerations
        if system_profile.system_type.value == "generative":
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-005",
                    category="security",
                    severity=Severity.MEDIUM,
                    description="Generative AI systems have unique security risks (prompt injection, jailbreaking)",
                    recommendation="Implement input validation, output filtering, and prompt injection defenses",
                    remediation_effort=RemediationEffort.HIGH,
                )
            )
            weaknesses.append("Generative AI security risks require special attention")
            score -= 0.1

        # Check 6: Sector-specific security requirements
        high_security_sectors = ["healthcare", "finance", "government", "defense", "critical_infrastructure"]
        if system_profile.industry_sector and any(
            sec in system_profile.industry_sector.lower() for sec in high_security_sectors
        ):
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-006",
                    category="compliance",
                    severity=Severity.HIGH,
                    description=f"{system_profile.industry_sector} sector has heightened security requirements",
                    recommendation="Review and implement sector-specific security frameworks and certifications",
                    remediation_effort=RemediationEffort.HIGH,
                )
            )
            score -= 0.1

        score = max(0.0, min(1.0, score))

        return PrincipleEvaluation(
            evaluation_id=self._generate_evaluation_id(),
            principle=Principle.SECURITY,
            evaluator_agent=self.name,
            compliance_status=self._determine_compliance_status(score),
            score=score,
            confidence=0.75,
            findings=findings,
            strengths=strengths,
            weaknesses=weaknesses,
            methodology="Profile analysis + security checklist",
            artifacts_reviewed=["system_profile"],
            limitations=["Full security assessment requires technical vulnerability testing"],
        )

    async def generate_recommendations(
        self,
        evaluation: PrincipleEvaluation,
        context: Context,
    ) -> list[str]:
        """Generate security and privacy recommendations."""
        recommendations = []

        for finding in evaluation.findings:
            recommendations.append(finding.recommendation)

        if evaluation.score < 0.7:
            recommendations.extend([
                "Conduct Data Protection Impact Assessment (DPIA)",
                "Implement comprehensive access control with audit logging",
                "Establish incident response plan for AI-specific incidents",
                "Review data retention policies and implement secure deletion",
            ])

        if evaluation.score < 0.5:
            recommendations.extend([
                "Engage security firm for penetration testing of AI system",
                "Implement adversarial robustness testing (red-teaming)",
                "Deploy privacy-enhancing technologies (differential privacy, encryption)",
                "Create security operations playbook for AI system monitoring",
            ])

        return recommendations
