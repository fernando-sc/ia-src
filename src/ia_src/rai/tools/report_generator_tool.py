"""Report Generator Tool for RAI assessments."""

from datetime import datetime
from typing import Any

from ia_src.tools.base_tool import Tool, ToolResult


class ReportGeneratorTool(Tool):
    """Generate formatted RAI reports.

    Supported report types:
    - aia: Algorithmic Impact Assessment
    - audit: Audit report
    - compliance: Compliance status report
    - summary: Executive summary
    """

    name = "report_generator"
    description = "Generate AIA reports, audit reports, and compliance documents"

    async def execute(
        self,
        report_type: str,
        data: dict[str, Any],
        output_format: str = "markdown",
        include_recommendations: bool = True,
        **kwargs: Any,
    ) -> ToolResult:
        """Generate a formatted report.

        Args:
            report_type: Type of report (aia, audit, compliance, summary)
            data: Report data (evaluations, findings, etc.)
            output_format: Output format (markdown, html, json)
            include_recommendations: Whether to include recommendations section

        Returns:
            ToolResult with generated report content
        """
        try:
            if report_type == "aia":
                content = self._generate_aia_report(data, output_format)
            elif report_type == "audit":
                content = self._generate_audit_report(data, output_format)
            elif report_type == "compliance":
                content = self._generate_compliance_report(data, output_format)
            elif report_type == "summary":
                content = self._generate_summary_report(data, output_format)
            else:
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"Unknown report type: {report_type}. "
                    "Supported: aia, audit, compliance, summary",
                )

            return ToolResult(
                success=True,
                output={
                    "report_type": report_type,
                    "format": output_format,
                    "content": content,
                    "generated_at": datetime.utcnow().isoformat(),
                },
            )

        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))

    def get_schema(self) -> dict[str, Any]:
        """Return JSON schema for tool parameters."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "report_type": {
                            "type": "string",
                            "enum": ["aia", "audit", "compliance", "summary"],
                            "description": "Type of report to generate",
                        },
                        "data": {
                            "type": "object",
                            "description": "Report data (evaluations, findings, etc.)",
                        },
                        "output_format": {
                            "type": "string",
                            "enum": ["markdown", "html", "json"],
                            "default": "markdown",
                        },
                        "include_recommendations": {
                            "type": "boolean",
                            "default": True,
                        },
                    },
                    "required": ["report_type", "data"],
                },
            },
        }

    def _generate_aia_report(
        self,
        data: dict[str, Any],
        output_format: str,
    ) -> str:
        """Generate Algorithmic Impact Assessment report."""
        if output_format == "json":
            import json
            return json.dumps(data, indent=2, default=str)

        report = f"""# Algorithmic Impact Assessment Report

**Report ID:** {data.get('report_id', 'N/A')}
**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
**Version:** {data.get('version', '1.0')}

---

## System Information

| Field | Value |
|-------|-------|
| **System Name** | {data.get('system_name', 'N/A')} |
| **System ID** | {data.get('system_id', 'N/A')} |
| **Owner** | {data.get('owner', 'N/A')} |
| **Risk Level** | {data.get('risk_level', 'N/A')} |
| **Current Phase** | {data.get('current_phase', 'N/A')} |

---

## Section 1: System Context and Purpose

{self._format_section(data.get('section1', {}))}

---

## Section 2: Data and Model Assessment

{self._format_section(data.get('section2', {}))}

---

## Section 3: Impact Analysis

{self._format_section(data.get('section3', {}))}

---

## Section 4: Risk Mitigation Measures

{self._format_section(data.get('section4', {}))}

---

## Section 5: Governance and Accountability

{self._format_section(data.get('section5', {}))}

---

## Section 6: Ongoing Monitoring and Review

{self._format_section(data.get('section6', {}))}

---

## Principle Evaluations

{self._format_evaluations(data.get('evaluations', []))}

---

## Overall Recommendation

**Recommendation:** {data.get('recommendation', 'Requires Further Assessment')}

{self._format_conditions(data.get('conditions', []))}

---

## Approvals

| Role | Name | Date |
|------|------|------|
"""
        for approval in data.get('approvals', []):
            report += f"| {approval.get('role', 'N/A')} | {approval.get('name', 'N/A')} | {approval.get('date', 'N/A')} |\n"

        return report

    def _generate_audit_report(
        self,
        data: dict[str, Any],
        output_format: str,
    ) -> str:
        """Generate audit report."""
        if output_format == "json":
            import json
            return json.dumps(data, indent=2, default=str)

        report = f"""# RAI Audit Report

**Audit Date:** {datetime.utcnow().strftime('%Y-%m-%d')}
**System:** {data.get('system_name', 'N/A')}
**Auditor:** {data.get('auditor', 'RAI Audit System')}

---

## Executive Summary

{data.get('executive_summary', 'No summary provided.')}

---

## Audit Scope

{data.get('scope', 'Full RAI assessment across all six principles.')}

---

## Findings Summary

| Principle | Score | Status | Critical Findings |
|-----------|-------|--------|-------------------|
"""
        for eval_data in data.get('evaluations', []):
            critical_count = len([f for f in eval_data.get('findings', []) if f.get('severity') == 'critical'])
            report += f"| {eval_data.get('principle', 'N/A')} | {eval_data.get('score', 0):.2f} | {eval_data.get('status', 'N/A')} | {critical_count} |\n"

        report += f"""
---

## Detailed Findings

"""
        for eval_data in data.get('evaluations', []):
            report += f"### {eval_data.get('principle', 'Unknown').title()}\n\n"
            for finding in eval_data.get('findings', []):
                report += f"- **[{finding.get('severity', 'N/A').upper()}]** {finding.get('description', 'N/A')}\n"
            report += "\n"

        report += """---

## Recommendations

"""
        for i, rec in enumerate(data.get('recommendations', []), 1):
            report += f"{i}. {rec}\n"

        return report

    def _generate_compliance_report(
        self,
        data: dict[str, Any],
        output_format: str,
    ) -> str:
        """Generate compliance status report."""
        if output_format == "json":
            import json
            return json.dumps(data, indent=2, default=str)

        report = f"""# Compliance Status Report

**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
**System:** {data.get('system_name', 'N/A')}

---

## Applicable Regulations

"""
        for reg in data.get('regulations', []):
            report += f"""### {reg.get('name', 'Unknown Regulation')}

**Status:** {reg.get('status', 'Not Assessed')}

| Requirement | Status | Evidence |
|-------------|--------|----------|
"""
            for req in reg.get('requirements', []):
                report += f"| {req.get('name', 'N/A')} | {req.get('status', 'N/A')} | {req.get('evidence', 'None')} |\n"
            report += "\n"

        return report

    def _generate_summary_report(
        self,
        data: dict[str, Any],
        output_format: str,
    ) -> str:
        """Generate executive summary report."""
        if output_format == "json":
            import json
            return json.dumps(data, indent=2, default=str)

        overall_score = data.get('overall_score', 0)
        status = "Compliant" if overall_score >= 0.9 else "Partially Compliant" if overall_score >= 0.6 else "Non-Compliant"

        report = f"""# RAI Assessment Executive Summary

**System:** {data.get('system_name', 'N/A')}
**Date:** {datetime.utcnow().strftime('%Y-%m-%d')}
**Overall Score:** {overall_score:.2f}/1.00
**Status:** {status}

---

## Key Findings

"""
        for finding in data.get('key_findings', [])[:5]:
            report += f"- {finding}\n"

        report += """
---

## Principle Scores

| Principle | Score | Status |
|-----------|-------|--------|
"""
        for eval_data in data.get('evaluations', []):
            report += f"| {eval_data.get('principle', 'N/A').title()} | {eval_data.get('score', 0):.2f} | {eval_data.get('status', 'N/A').replace('_', ' ').title()} |\n"

        report += f"""
---

## Recommendation

**{data.get('recommendation', 'Requires Further Assessment')}**

"""
        for condition in data.get('conditions', []):
            report += f"- {condition}\n"

        return report

    def _format_section(self, section_data: dict[str, Any]) -> str:
        """Format a section's content."""
        if isinstance(section_data, str):
            return section_data

        content = section_data.get('content', '')
        if isinstance(content, dict):
            parts = []
            for key, value in content.items():
                if isinstance(value, list):
                    parts.append(f"**{key.replace('_', ' ').title()}:**")
                    for item in value:
                        parts.append(f"- {item}")
                else:
                    parts.append(f"**{key.replace('_', ' ').title()}:** {value}")
            return "\n\n".join(parts)
        return content

    def _format_evaluations(self, evaluations: list[dict[str, Any]]) -> str:
        """Format principle evaluations."""
        if not evaluations:
            return "No evaluations available."

        output = "| Principle | Score | Status | Findings |\n"
        output += "|-----------|-------|--------|----------|\n"

        for eval_data in evaluations:
            findings_count = len(eval_data.get('findings', []))
            output += f"| {eval_data.get('principle', 'N/A').title()} | {eval_data.get('score', 0):.2f} | {eval_data.get('status', 'N/A')} | {findings_count} |\n"

        return output

    def _format_conditions(self, conditions: list[str]) -> str:
        """Format approval conditions."""
        if not conditions:
            return ""

        output = "### Conditions for Approval\n\n"
        for condition in conditions:
            output += f"- {condition}\n"
        return output
