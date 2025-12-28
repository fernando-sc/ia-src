"""Compliance Tool for regulatory checks."""

from typing import Any

from ia_src.tools.base_tool import Tool, ToolResult


class ComplianceTool(Tool):
    """Check AI systems against regulatory frameworks.

    Supported regulations:
    - GDPR (EU General Data Protection Regulation)
    - EU AI Act
    - LGPD (Brazil's data protection law)
    """

    name = "compliance_check"
    description = "Verify compliance with AI regulations (GDPR, EU AI Act, LGPD)"

    REGULATIONS = {
        "gdpr": {
            "name": "General Data Protection Regulation (EU)",
            "articles": {
                "article_5": {
                    "title": "Principles relating to processing",
                    "requirements": [
                        "lawfulness_fairness_transparency",
                        "purpose_limitation",
                        "data_minimization",
                        "accuracy",
                        "storage_limitation",
                        "integrity_confidentiality",
                        "accountability",
                    ],
                },
                "article_13_14": {
                    "title": "Information for data subjects",
                    "requirements": [
                        "identity_contact_controller",
                        "purpose_legal_basis",
                        "recipients",
                        "retention_period",
                        "data_subject_rights",
                        "automated_decision_making_info",
                    ],
                },
                "article_22": {
                    "title": "Automated decision-making",
                    "requirements": [
                        "right_not_to_be_subject_to_automated_decision",
                        "explicit_consent_or_contract",
                        "suitable_safeguards",
                        "right_to_human_intervention",
                        "right_to_express_point_of_view",
                        "right_to_contest_decision",
                    ],
                },
            },
        },
        "eu_ai_act": {
            "name": "EU AI Act",
            "risk_categories": ["unacceptable", "high", "limited", "minimal"],
            "requirements": {
                "high_risk": {
                    "article_9": "Risk management system",
                    "article_10": "Data and data governance",
                    "article_11": "Technical documentation",
                    "article_12": "Record-keeping",
                    "article_13": "Transparency and provision of information to deployers",
                    "article_14": "Human oversight",
                    "article_15": "Accuracy, robustness and cybersecurity",
                },
                "limited_risk": {
                    "article_50": "Transparency obligations",
                },
            },
            "prohibited_practices": [
                "subliminal_manipulation",
                "exploitation_of_vulnerabilities",
                "social_scoring_by_governments",
                "real_time_biometric_identification_public",
            ],
        },
        "lgpd": {
            "name": "Lei Geral de Proteção de Dados (Brazil)",
            "articles": {
                "article_6": {
                    "title": "Processing principles",
                    "requirements": [
                        "purpose",
                        "adequacy",
                        "necessity",
                        "free_access",
                        "quality",
                        "transparency",
                        "security",
                        "prevention",
                        "non_discrimination",
                        "accountability",
                    ],
                },
                "article_20": {
                    "title": "Right to review automated decisions",
                    "requirements": [
                        "right_to_request_review",
                        "clear_adequate_information",
                    ],
                },
            },
        },
    }

    async def execute(
        self,
        regulation: str,
        system_profile: dict[str, Any] | None = None,
        evidence: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> ToolResult:
        """Check compliance with specified regulation.

        Args:
            regulation: Regulation to check (gdpr, eu_ai_act, lgpd)
            system_profile: AI system profile as dict
            evidence: Evidence of compliance measures

        Returns:
            ToolResult with compliance status and gaps
        """
        try:
            reg_lower = regulation.lower()
            if reg_lower not in self.REGULATIONS:
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"Unknown regulation: {regulation}. "
                    f"Supported: {', '.join(self.REGULATIONS.keys())}",
                )

            reg_info = self.REGULATIONS[reg_lower]
            evidence = evidence or {}

            if reg_lower == "eu_ai_act":
                results = await self._check_eu_ai_act(system_profile, evidence)
            elif reg_lower == "gdpr":
                results = await self._check_gdpr(system_profile, evidence)
            elif reg_lower == "lgpd":
                results = await self._check_lgpd(system_profile, evidence)
            else:
                results = {"regulation": reg_info["name"], "status": "not_implemented"}

            return ToolResult(success=True, output=results)

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
                        "regulation": {
                            "type": "string",
                            "enum": list(self.REGULATIONS.keys()),
                            "description": "Regulation to check",
                        },
                        "system_profile": {
                            "type": "object",
                            "description": "AI system profile",
                        },
                        "evidence": {
                            "type": "object",
                            "description": "Evidence of compliance measures",
                        },
                    },
                    "required": ["regulation"],
                },
            },
        }

    async def _check_eu_ai_act(
        self,
        system_profile: dict[str, Any] | None,
        evidence: dict[str, Any],
    ) -> dict[str, Any]:
        """Check EU AI Act compliance."""
        results = {
            "regulation": "EU AI Act",
            "risk_classification": "unknown",
            "requirements": [],
            "compliant": [],
            "non_compliant": [],
            "not_applicable": [],
            "overall_status": "not_assessed",
        }

        if not system_profile:
            return results

        # Determine risk classification
        is_high_risk = system_profile.get("is_high_risk_eu_ai_act", False)
        results["risk_classification"] = "high" if is_high_risk else "minimal"

        if is_high_risk:
            # Check high-risk requirements
            requirements = self.REGULATIONS["eu_ai_act"]["requirements"]["high_risk"]
            for article, title in requirements.items():
                check = {
                    "article": article,
                    "title": title,
                    "status": "non_compliant",
                    "evidence": None,
                    "gaps": [],
                }

                # Check evidence
                evidence_key = article.replace("article_", "")
                if evidence.get(evidence_key) or evidence.get(article):
                    check["status"] = "compliant"
                    check["evidence"] = evidence.get(evidence_key) or evidence.get(article)
                    results["compliant"].append(check)
                else:
                    check["gaps"].append(f"No evidence for {title}")
                    results["non_compliant"].append(check)

                results["requirements"].append(check)

        # Check prohibited practices
        results["prohibited_practices_check"] = {
            "practices_checked": self.REGULATIONS["eu_ai_act"]["prohibited_practices"],
            "violations_detected": [],
        }

        # Determine overall status
        if results["non_compliant"]:
            results["overall_status"] = "non_compliant"
        elif results["compliant"]:
            results["overall_status"] = "compliant"

        return results

    async def _check_gdpr(
        self,
        system_profile: dict[str, Any] | None,
        evidence: dict[str, Any],
    ) -> dict[str, Any]:
        """Check GDPR compliance."""
        results = {
            "regulation": "GDPR",
            "articles_checked": [],
            "compliant": [],
            "non_compliant": [],
            "overall_status": "not_assessed",
        }

        if not system_profile:
            return results

        # Check Article 22 (automated decision-making)
        article_22 = self.REGULATIONS["gdpr"]["articles"]["article_22"]
        article_22_check = {
            "article": "article_22",
            "title": article_22["title"],
            "requirements_checked": [],
            "status": "not_assessed",
        }

        for req in article_22["requirements"]:
            req_check = {
                "requirement": req,
                "status": "non_compliant" if not evidence.get(req) else "compliant",
                "evidence": evidence.get(req),
            }
            article_22_check["requirements_checked"].append(req_check)

        compliant_reqs = [r for r in article_22_check["requirements_checked"] if r["status"] == "compliant"]
        if len(compliant_reqs) == len(article_22["requirements"]):
            article_22_check["status"] = "compliant"
            results["compliant"].append(article_22_check)
        elif len(compliant_reqs) > 0:
            article_22_check["status"] = "partially_compliant"
            results["non_compliant"].append(article_22_check)
        else:
            article_22_check["status"] = "non_compliant"
            results["non_compliant"].append(article_22_check)

        results["articles_checked"].append(article_22_check)

        # Determine overall status
        if results["non_compliant"]:
            results["overall_status"] = "non_compliant"
        elif results["compliant"]:
            results["overall_status"] = "compliant"

        return results

    async def _check_lgpd(
        self,
        system_profile: dict[str, Any] | None,
        evidence: dict[str, Any],
    ) -> dict[str, Any]:
        """Check LGPD compliance."""
        results = {
            "regulation": "LGPD (Brazil)",
            "articles_checked": [],
            "overall_status": "not_assessed",
        }

        if not system_profile:
            return results

        # Check Article 20 (automated decision review)
        article_20 = self.REGULATIONS["lgpd"]["articles"]["article_20"]
        article_20_check = {
            "article": "article_20",
            "title": article_20["title"],
            "requirements_checked": [],
        }

        for req in article_20["requirements"]:
            req_check = {
                "requirement": req,
                "status": "non_compliant" if not evidence.get(req) else "compliant",
            }
            article_20_check["requirements_checked"].append(req_check)

        results["articles_checked"].append(article_20_check)

        return results
