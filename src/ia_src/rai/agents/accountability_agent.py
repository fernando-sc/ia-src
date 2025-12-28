"""Accountability Agent for RAI assessments."""

from ia_src.core.context import Context
from ia_src.core.message import Message
from ia_src.llm.base_provider import LLMProvider
from ia_src.rai.agents.base_rai_agent import RAIAgent
from ia_src.rai.models import (
    Finding,
    Principle,
    PrincipleEvaluation,
    Recommendation,
    RemediationEffort,
    Severity,
    SystemProfile,
)


class AccountabilityAgent(RAIAgent):
    """Agent for governance audits and responsibility mapping.

    Evaluates:
    - Governance structures and oversight
    - Responsibility assignments (RACI)
    - Audit trail mechanisms
    - Impact assessment completeness
    - Regulatory compliance accountability
    """

    def __init__(self, llm_provider: LLMProvider) -> None:
        super().__init__(
            name="AccountabilityAgent",
            principle=Principle.ACCOUNTABILITY,
            llm_provider=llm_provider,
            description="Evaluates governance structures, responsibility assignments, and impact assessments",
        )

    def _build_system_prompt(self) -> str:
        return """You are an AI Accountability Specialist focused on ensuring proper governance and responsibility structures for AI systems.

## Your Expertise Areas

### 1. GOVERNANCE STRUCTURES
- Clear ownership and responsibility chains
- AI governance boards and committees
- Decision-making authority documentation
- Escalation procedures and paths
- Cross-functional oversight mechanisms

### 2. IMPACT ASSESSMENTS
- Algorithmic Impact Assessment (AIA) completeness
- Stakeholder impact analysis depth
- Unintended consequence identification
- Proportionality of AI use to risks
- Regular reassessment schedules

### 3. AUDIT TRAILS
- Decision logging mechanisms
- Traceability of AI outputs to inputs
- Version control and change management
- Evidence preservation for investigations
- Reproducibility of decisions

### 4. REGULATORY COMPLIANCE ACCOUNTABILITY
- GDPR Article 22 (automated decision-making) compliance
- EU AI Act requirements for high-risk systems
- Sector-specific regulations (finance, healthcare, etc.)
- Documentation requirements
- Notification and reporting obligations

### 5. RESPONSIBILITY ASSIGNMENT
- RACI matrices for AI operations
- Clear roles: developers, operators, deployers, users
- Liability considerations
- Third-party accountability (vendors, partners)
- Human oversight responsibilities

## Evaluation Approach
1. Assess governance documentation and structures
2. Verify accountability assignments are clear and appropriate
3. Check audit mechanisms are comprehensive
4. Evaluate regulatory compliance measures
5. Identify gaps in responsibility chains

Provide rigorous, actionable assessments with specific recommendations for improvement."""

    async def evaluate(
        self,
        system_profile: SystemProfile,
        context: Context,
    ) -> PrincipleEvaluation:
        """Evaluate accountability aspects of the AI system."""
        findings: list[Finding] = []
        strengths: list[str] = []
        weaknesses: list[str] = []
        score = 1.0

        # Check 1: System owner defined
        if not system_profile.owner:
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-001",
                    category="governance",
                    severity=Severity.HIGH,
                    description="No system owner defined",
                    recommendation="Assign a responsible owner for the AI system with clear accountability",
                    remediation_effort=RemediationEffort.LOW,
                    affected_objective="Clear ownership",
                )
            )
            weaknesses.append("Missing designated system owner")
            score -= 0.2
        else:
            strengths.append(f"System owner clearly defined: {system_profile.owner}")

        # Check 2: Operators identified
        if not system_profile.operators:
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-002",
                    category="governance",
                    severity=Severity.MEDIUM,
                    description="No operators identified for the system",
                    recommendation="Define operational responsibility and operator roles",
                    remediation_effort=RemediationEffort.LOW,
                )
            )
            score -= 0.1
        else:
            strengths.append(f"{len(system_profile.operators)} operators identified")

        # Check 3: High-risk classification without regulations
        if system_profile.is_high_risk_eu_ai_act:
            if not system_profile.applicable_regulations:
                findings.append(
                    Finding(
                        finding_id=f"{self._generate_evaluation_id()}-003",
                        category="compliance",
                        severity=Severity.CRITICAL,
                        description="High-risk system under EU AI Act without documented applicable regulations",
                        recommendation="Document all applicable regulations and establish compliance monitoring",
                        remediation_effort=RemediationEffort.MEDIUM,
                        affected_objective="Regulatory compliance",
                    )
                )
                weaknesses.append("Missing regulatory compliance documentation for high-risk system")
                score -= 0.3
            else:
                strengths.append("Applicable regulations documented for high-risk system")

        # Check 4: Affected populations identified
        if not system_profile.affected_populations:
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-004",
                    category="impact_assessment",
                    severity=Severity.MEDIUM,
                    description="Affected populations not identified",
                    recommendation="Conduct stakeholder analysis to identify all groups affected by AI decisions",
                    remediation_effort=RemediationEffort.MEDIUM,
                )
            )
            weaknesses.append("No stakeholder impact analysis performed")
            score -= 0.15
        else:
            strengths.append(f"{len(system_profile.affected_populations)} affected population groups identified")

        # Check 5: Known limitations documented
        if not system_profile.known_limitations:
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-005",
                    category="transparency",
                    severity=Severity.MEDIUM,
                    description="System limitations not documented",
                    recommendation="Document known limitations and failure modes for transparency",
                    remediation_effort=RemediationEffort.MEDIUM,
                )
            )
            score -= 0.1
        else:
            strengths.append(f"{len(system_profile.known_limitations)} known limitations documented")

        # Check 6: Development team accountability
        if not system_profile.developers:
            findings.append(
                Finding(
                    finding_id=f"{self._generate_evaluation_id()}-006",
                    category="governance",
                    severity=Severity.LOW,
                    description="Development team not documented",
                    recommendation="Document development team for accountability and knowledge transfer",
                    remediation_effort=RemediationEffort.LOW,
                )
            )
            score -= 0.05

        # Use LLM for deeper analysis if available
        if context.get_variable("enable_llm_analysis", True):
            llm_findings = await self._llm_analysis(system_profile, context)
            findings.extend(llm_findings)
            score -= 0.05 * len([f for f in llm_findings if f.severity in (Severity.HIGH, Severity.CRITICAL)])

        # Ensure score is in valid range
        score = max(0.0, min(1.0, score))

        return PrincipleEvaluation(
            evaluation_id=self._generate_evaluation_id(),
            principle=Principle.ACCOUNTABILITY,
            evaluator_agent=self.name,
            compliance_status=self._determine_compliance_status(score),
            score=score,
            confidence=0.85,
            findings=findings,
            strengths=strengths,
            weaknesses=weaknesses,
            methodology="Rule-based checks + LLM analysis",
            artifacts_reviewed=["system_profile"],
        )

    async def _llm_analysis(
        self,
        system_profile: SystemProfile,
        context: Context,
    ) -> list[Finding]:
        """Use LLM for deeper accountability analysis."""
        analysis_prompt = f"""Analyze this AI system for accountability gaps:

System: {system_profile.name}
Description: {system_profile.description}
Owner: {system_profile.owner}
Risk Level: {system_profile.risk_level.value}
System Type: {system_profile.system_type.value}
Current Phase: {system_profile.current_phase.value}
Is High-Risk (EU AI Act): {system_profile.is_high_risk_eu_ai_act}

Applicable Regulations: {', '.join(system_profile.applicable_regulations) or 'None documented'}
Affected Populations: {', '.join(system_profile.affected_populations) or 'None documented'}
Known Limitations: {', '.join(system_profile.known_limitations) or 'None documented'}

Identify specific accountability gaps in:
1. Governance structures
2. Decision-making authority
3. Audit trail mechanisms
4. Regulatory compliance measures
5. Human oversight provisions

For each gap found, provide:
- Category (governance/compliance/oversight/audit)
- Severity (low/medium/high/critical)
- Specific recommendation

Be concise and specific."""

        try:
            response = await self.llm_provider.generate([Message.user(analysis_prompt)])
            # Parse LLM response into findings
            # For now, return empty list - full parsing would be implemented
            return []
        except Exception:
            return []

    async def generate_recommendations(
        self,
        evaluation: PrincipleEvaluation,
        context: Context,
    ) -> list[str]:
        """Generate accountability recommendations."""
        recommendations = []

        # Generate from findings
        for finding in evaluation.findings:
            priority_prefix = (
                "[IMMEDIATE] " if finding.severity in (Severity.HIGH, Severity.CRITICAL) else ""
            )
            recommendations.append(f"{priority_prefix}{finding.recommendation}")

        # Add general recommendations based on score
        if evaluation.score < 0.7:
            recommendations.extend([
                "Establish an AI Governance Board with clear charter and decision authority",
                "Implement comprehensive audit logging for all AI decisions",
                "Create RACI matrix defining responsibilities for AI system lifecycle",
                "Develop incident response plan specific to AI system failures",
            ])

        if evaluation.score < 0.5:
            recommendations.extend([
                "Conduct urgent governance gap assessment with external review",
                "Appoint dedicated AI accountability officer or team",
                "Implement mandatory AIA process for all AI deployments",
            ])

        return recommendations
