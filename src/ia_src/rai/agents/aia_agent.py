"""Algorithmic Impact Assessment Agent."""

import uuid
from datetime import datetime
from typing import Any

from ia_src.core.base_agent import Agent
from ia_src.core.context import Context
from ia_src.core.message import Message
from ia_src.llm.base_provider import LLMProvider
from ia_src.rai.models import (
    AIAReport,
    AIASection1_SystemContext,
    AIASection2_DataAndModel,
    AIASection3_ImpactAnalysis,
    AIASection4_RiskMitigation,
    AIASection5_Governance,
    AIASection6_Monitoring,
    DataSource,
    DecisionRight,
    ImpactItem,
    MonitoringMetric,
    PrincipleEvaluation,
    RiskAssessment,
    StakeholderImpact,
    SystemProfile,
)


class AIAAgent(Agent):
    """Agent that conducts Algorithmic Impact Assessments.

    Generates comprehensive AIA reports following the 6-section
    structure defined in the RAI framework.
    """

    def __init__(self, llm_provider: LLMProvider) -> None:
        super().__init__(
            name="AIAAgent",
            description="Conducts comprehensive Algorithmic Impact Assessments",
        )
        self.llm_provider = llm_provider
        self._current_section = 0
        self._sections = [
            "context",
            "data_model",
            "impact",
            "risk_mitigation",
            "governance",
            "monitoring",
        ]

    async def run(self, message: Message, context: Context) -> Message:
        """Execute full AIA or respond to queries."""
        content_lower = message.content.lower()

        if "full assessment" in content_lower or "complete aia" in content_lower:
            return await self._run_full_assessment(context)
        elif "section" in content_lower:
            section_num = self._extract_section_number(message.content)
            if section_num:
                return await self._run_section(section_num, context)
        elif "report" in content_lower or "generate" in content_lower:
            return await self._generate_report_message(context)

        # Default: provide status or help
        return Message.assistant(self._get_status_message(context))

    async def step(self, context: Context) -> Message | None:
        """Execute one section of the AIA at a time."""
        if self._current_section >= len(self._sections):
            # All sections complete, compile final report
            await self._compile_report(context)
            return Message.assistant(
                "AIA complete. Report generated and stored in context."
            )

        system_profile = context.get_variable("system_profile")
        if not system_profile:
            return Message.assistant(
                "Error: No system profile in context. "
                "Please set 'system_profile' variable before running AIA."
            )

        section_name = self._sections[self._current_section]
        result = await self._assess_section(section_name, system_profile, context)
        context.set_variable(f"aia_section_{section_name}", result)
        self._current_section += 1

        return Message.assistant(
            f"Completed AIA Section {self._current_section}: "
            f"{section_name.replace('_', ' ').title()}"
        )

    async def _run_full_assessment(self, context: Context) -> Message:
        """Run complete AIA assessment."""
        system_profile = context.get_variable("system_profile")
        if not system_profile:
            return Message.assistant(
                "Error: No system profile in context. "
                "Please set 'system_profile' variable before running AIA."
            )

        results = []
        for section_name in self._sections:
            result = await self._assess_section(section_name, system_profile, context)
            context.set_variable(f"aia_section_{section_name}", result)
            results.append(f"- Section: {section_name.replace('_', ' ').title()}")

        report = await self._compile_report(context)
        context.set_variable("aia_report", report)

        return Message.assistant(
            f"# AIA Assessment Complete\n\n"
            f"**System:** {system_profile.name}\n"
            f"**Report ID:** {report.report_id}\n\n"
            f"## Sections Completed:\n" + "\n".join(results) + "\n\n"
            f"**Recommendation:** {report.overall_recommendation}"
        )

    async def _run_section(self, section_num: int, context: Context) -> Message:
        """Run specific section of AIA."""
        if section_num < 1 or section_num > len(self._sections):
            return Message.assistant(
                f"Invalid section number. Must be 1-{len(self._sections)}."
            )

        system_profile = context.get_variable("system_profile")
        if not system_profile:
            return Message.assistant("Error: No system profile in context.")

        section_name = self._sections[section_num - 1]
        result = await self._assess_section(section_name, system_profile, context)
        context.set_variable(f"aia_section_{section_name}", result)

        return Message.assistant(
            f"Completed Section {section_num}: {section_name.replace('_', ' ').title()}"
        )

    async def _assess_section(
        self,
        section: str,
        system_profile: SystemProfile,
        context: Context,
    ) -> Any:
        """Assess a specific AIA section."""
        section_handlers = {
            "context": self._assess_context,
            "data_model": self._assess_data_model,
            "impact": self._assess_impact,
            "risk_mitigation": self._assess_risk_mitigation,
            "governance": self._assess_governance,
            "monitoring": self._assess_monitoring,
        }

        handler = section_handlers.get(section)
        if handler:
            return await handler(system_profile, context)
        raise ValueError(f"Unknown section: {section}")

    async def _assess_context(
        self,
        system_profile: SystemProfile,
        context: Context,
    ) -> AIASection1_SystemContext:
        """Assess Section 1: System Context and Purpose."""
        # Build stakeholder impacts
        stakeholder_impacts = []
        for pop in system_profile.affected_populations:
            stakeholder_impacts.append(
                StakeholderImpact(
                    stakeholder_group=pop,
                    relationship="subject",
                    positive_impacts=["Potential benefit from AI-assisted decisions"],
                    negative_impacts=["Potential for biased or incorrect decisions"],
                    impact_magnitude="moderate",
                )
            )

        return AIASection1_SystemContext(
            business_problem=system_profile.description,
            business_justification=f"AI solution for: {system_profile.description}",
            intended_use_cases=system_profile.use_cases or ["Not specified"],
            expected_benefits=[
                "Improved efficiency",
                "Consistent decision-making",
                "Scalability",
            ],
            stakeholder_impacts=stakeholder_impacts,
            scope_boundaries=f"System type: {system_profile.system_type.value}",
            out_of_scope=system_profile.prohibited_uses or [],
            alternatives_considered=["Manual process", "Rule-based system"],
            ai_necessity_justification="AI enables automated processing at scale",
        )

    async def _assess_data_model(
        self,
        system_profile: SystemProfile,
        context: Context,
    ) -> AIASection2_DataAndModel:
        """Assess Section 2: Data and Model Assessment."""
        data_sources = []
        if system_profile.training_data_description:
            data_sources.append(
                DataSource(
                    name="Training Data",
                    description=system_profile.training_data_description,
                    data_type="structured",
                    collection_method="Not specified",
                )
            )

        return AIASection2_DataAndModel(
            data_sources=data_sources,
            data_quality_assessment="Requires detailed data profiling",
            representativeness_analysis="Requires population comparison",
            model_selection_rationale=f"Selected {system_profile.model_architecture or 'model type not specified'}",
            model_architecture=system_profile.model_architecture or "Not specified",
            training_methodology="To be documented",
            validation_approach="To be documented",
            known_limitations=system_profile.known_limitations or [],
        )

    async def _assess_impact(
        self,
        system_profile: SystemProfile,
        context: Context,
    ) -> AIASection3_ImpactAnalysis:
        """Assess Section 3: Impact Analysis."""
        positive_impacts = [
            ImpactItem(
                description="Efficiency improvements in processing",
                affected_groups=["operators", "organization"],
                magnitude="moderate",
            ),
            ImpactItem(
                description="Consistency in decision-making",
                affected_groups=system_profile.affected_populations,
                magnitude="moderate",
            ),
        ]

        negative_impacts = [
            ImpactItem(
                description="Potential for automated errors affecting individuals",
                affected_groups=system_profile.affected_populations,
                magnitude="moderate" if system_profile.risk_level.value != "high" else "high",
            ),
        ]

        if system_profile.is_high_risk_eu_ai_act:
            negative_impacts.append(
                ImpactItem(
                    description="High-risk system may significantly impact fundamental rights",
                    affected_groups=system_profile.affected_populations,
                    magnitude="high",
                )
            )

        return AIASection3_ImpactAnalysis(
            positive_impacts=positive_impacts,
            negative_impacts=negative_impacts,
            potential_unintended_consequences=[
                "Automation bias in operators",
                "Over-reliance on AI decisions",
            ],
            disproportionate_impacts=["Requires fairness analysis"],
            equity_considerations="Requires detailed equity assessment",
        )

    async def _assess_risk_mitigation(
        self,
        system_profile: SystemProfile,
        context: Context,
    ) -> AIASection4_RiskMitigation:
        """Assess Section 4: Risk Mitigation Measures."""
        risk_assessment = context.get_variable("risk_assessment")

        return AIASection4_RiskMitigation(
            risk_assessment=risk_assessment,
            technical_safeguards=[
                "Input validation",
                "Output monitoring",
                "Access controls",
            ],
            procedural_safeguards=[
                "Regular audits",
                "Incident response procedures",
            ],
            human_oversight_mechanisms=[
                "Human review for high-stakes decisions",
                "Override capabilities",
            ],
            human_intervention_points=[
                "Pre-deployment approval",
                "Flagged decision review",
            ],
            fallback_procedures=[
                "Manual processing fallback",
                "Graceful degradation",
            ],
        )

    async def _assess_governance(
        self,
        system_profile: SystemProfile,
        context: Context,
    ) -> AIASection5_Governance:
        """Assess Section 5: Governance and Accountability."""
        decision_rights = [
            DecisionRight(
                role="System Owner",
                responsibilities=["Overall accountability", "Approval of changes"],
                authority_level="High",
            ),
            DecisionRight(
                role="Operations Team",
                responsibilities=["Day-to-day operation", "Incident response"],
                authority_level="Medium",
            ),
        ]

        return AIASection5_Governance(
            accountability_framework=f"Owner: {system_profile.owner}",
            decision_rights=decision_rights,
            escalation_procedures="To be documented",
            audit_trail_mechanisms=["Decision logging", "Version control"],
            incident_response_plan="To be developed",
            documentation_practices=[
                "Model documentation",
                "Change logs",
                "Audit records",
            ],
        )

    async def _assess_monitoring(
        self,
        system_profile: SystemProfile,
        context: Context,
    ) -> AIASection6_Monitoring:
        """Assess Section 6: Ongoing Monitoring and Review."""
        performance_metrics = [
            MonitoringMetric(
                name="Accuracy",
                description="Model prediction accuracy",
                threshold=">=90%",
                frequency="Daily",
            ),
            MonitoringMetric(
                name="Latency",
                description="Response time",
                threshold="<500ms p95",
                frequency="Real-time",
            ),
        ]

        fairness_metrics = [
            MonitoringMetric(
                name="Demographic Parity",
                description="Outcome rates across groups",
                threshold="Within 80% rule",
                frequency="Weekly",
            ),
        ]

        return AIASection6_Monitoring(
            performance_metrics=performance_metrics,
            fairness_metrics=fairness_metrics,
            monitoring_frequency="Continuous for critical metrics",
            review_schedule="Quarterly comprehensive review",
            review_triggers=[
                "Performance degradation >10%",
                "Fairness metric violation",
                "Significant model update",
                "Regulatory change",
            ],
            feedback_mechanisms=["User feedback form", "Operator reports"],
            decommissioning_criteria=[
                "Performance below acceptable threshold",
                "Regulatory non-compliance",
                "Replacement by improved system",
            ],
        )

    async def _compile_report(self, context: Context) -> AIAReport:
        """Compile all sections into final AIA report."""
        system_profile: SystemProfile = context.get_variable("system_profile")

        # Get all sections
        section1 = context.get_variable("aia_section_context")
        section2 = context.get_variable("aia_section_data_model")
        section3 = context.get_variable("aia_section_impact")
        section4 = context.get_variable("aia_section_risk_mitigation")
        section5 = context.get_variable("aia_section_governance")
        section6 = context.get_variable("aia_section_monitoring")

        # Get principle evaluations if available
        principle_evaluations: list[PrincipleEvaluation] = context.get_variable(
            "principle_evaluations", []
        )

        # Determine recommendation
        recommendation = self._determine_recommendation(
            system_profile, principle_evaluations, context
        )

        # Build conditions for approval if needed
        conditions = []
        if recommendation == "proceed_with_conditions":
            conditions = self._determine_conditions(principle_evaluations)

        report = AIAReport(
            report_id=str(uuid.uuid4()),
            system_profile=system_profile,
            section1_context=section1,
            section2_data_model=section2,
            section3_impact=section3,
            section4_risk_mitigation=section4,
            section5_governance=section5,
            section6_monitoring=section6,
            principle_evaluations=principle_evaluations,
            overall_recommendation=recommendation,
            conditions_for_approval=conditions,
            executive_summary=self._generate_executive_summary(
                system_profile, principle_evaluations, recommendation
            ),
            assessment_team=[self.name],
        )

        return report

    def _determine_recommendation(
        self,
        system_profile: SystemProfile,
        evaluations: list[PrincipleEvaluation],
        context: Context,
    ) -> str:
        """Determine overall AIA recommendation."""
        if not evaluations:
            return "requires_further_assessment"

        avg_score = sum(e.score for e in evaluations) / len(evaluations)
        min_score = min(e.score for e in evaluations)

        # Critical threshold violations
        critical_findings = sum(
            1 for e in evaluations for f in e.findings if f.severity.value == "critical"
        )

        if critical_findings > 0 or min_score < 0.3:
            return "do_not_proceed"
        elif avg_score >= 0.8 and min_score >= 0.6:
            return "proceed"
        elif avg_score >= 0.5:
            return "proceed_with_conditions"
        else:
            return "requires_further_assessment"

    def _determine_conditions(
        self,
        evaluations: list[PrincipleEvaluation],
    ) -> list[str]:
        """Determine conditions for conditional approval."""
        conditions = []
        for e in evaluations:
            if e.score < 0.7:
                conditions.append(
                    f"Address {e.principle.value} gaps before deployment"
                )
            for f in e.findings:
                if f.severity.value in ("high", "critical"):
                    conditions.append(f.recommendation)
        return conditions[:5]  # Limit to top 5

    def _generate_executive_summary(
        self,
        system_profile: SystemProfile,
        evaluations: list[PrincipleEvaluation],
        recommendation: str,
    ) -> str:
        """Generate executive summary."""
        if evaluations:
            avg_score = sum(e.score for e in evaluations) / len(evaluations)
            score_text = f"Overall RAI score: {avg_score:.2f}/1.00"
        else:
            score_text = "RAI evaluation pending"

        return (
            f"This Algorithmic Impact Assessment evaluates {system_profile.name}, "
            f"a {system_profile.system_type.value} system classified as "
            f"{system_profile.risk_level.value} risk. {score_text}. "
            f"Recommendation: {recommendation.replace('_', ' ').title()}."
        )

    async def _generate_report_message(self, context: Context) -> Message:
        """Generate report and return as message."""
        report = context.get_variable("aia_report")
        if not report:
            report = await self._compile_report(context)
            context.set_variable("aia_report", report)

        return Message.assistant(
            f"# AIA Report Generated\n\n"
            f"**Report ID:** {report.report_id}\n"
            f"**System:** {report.system_profile.name}\n"
            f"**Recommendation:** {report.overall_recommendation}\n\n"
            f"## Executive Summary\n{report.executive_summary}"
        )

    def _get_status_message(self, context: Context) -> str:
        """Get current AIA status."""
        completed = [s for s in self._sections if context.get_variable(f"aia_section_{s}")]
        return (
            f"AIA Status: {len(completed)}/{len(self._sections)} sections complete.\n"
            f"Completed: {', '.join(completed) if completed else 'None'}\n"
            f"Use 'full assessment' to run complete AIA or 'section N' for specific section."
        )

    def _extract_section_number(self, content: str) -> int | None:
        """Extract section number from message."""
        import re
        match = re.search(r'section\s*(\d+)', content.lower())
        if match:
            return int(match.group(1))
        return None
