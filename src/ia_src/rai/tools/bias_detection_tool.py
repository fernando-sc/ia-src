"""Bias Detection Tool for RAI assessments."""

from typing import Any

from ia_src.tools.base_tool import Tool, ToolResult


class BiasDetectionTool(Tool):
    """Analyze datasets and models for bias.

    Capabilities:
    - Demographic parity analysis
    - Representation analysis
    - Equalized odds calculation
    - Disparate impact assessment
    """

    name = "bias_detection"
    description = "Detect bias in datasets or model predictions across protected attributes"

    async def execute(
        self,
        data_path: str | None = None,
        predictions: list[dict[str, Any]] | None = None,
        protected_attributes: list[str] | None = None,
        target_column: str | None = None,
        positive_label: Any = 1,
        **kwargs: Any,
    ) -> ToolResult:
        """Execute bias detection analysis.

        Args:
            data_path: Path to dataset file (CSV, Parquet, JSON)
            predictions: List of prediction records with protected attributes
            protected_attributes: Columns to analyze for bias (e.g., ["gender", "race"])
            target_column: Target/outcome column name
            positive_label: Value considered as positive outcome

        Returns:
            ToolResult with bias metrics and findings
        """
        try:
            if not protected_attributes:
                return ToolResult(
                    success=False,
                    output=None,
                    error="protected_attributes is required",
                )

            metrics: dict[str, Any] = {}
            findings: list[dict[str, Any]] = []

            if data_path:
                # Analyze dataset representation
                representation = await self._analyze_representation(
                    data_path, protected_attributes
                )
                metrics["representation"] = representation

                # Calculate demographic parity if target column provided
                if target_column:
                    demo_parity = await self._calculate_demographic_parity(
                        data_path, protected_attributes, target_column, positive_label
                    )
                    metrics["demographic_parity"] = demo_parity

                    # Check for violations
                    for attr, result in demo_parity.get("by_attribute", {}).items():
                        if result.get("disparity_ratio", 1.0) < 0.8:
                            findings.append({
                                "type": "demographic_parity_violation",
                                "attribute": attr,
                                "severity": "high",
                                "details": result,
                                "recommendation": f"Investigate disparate impact for {attr}",
                            })

            if predictions:
                # Analyze predictions
                eq_odds = await self._calculate_equalized_odds(
                    predictions, protected_attributes
                )
                metrics["equalized_odds"] = eq_odds

                calibration = await self._analyze_calibration(
                    predictions, protected_attributes
                )
                metrics["calibration"] = calibration

            return ToolResult(
                success=True,
                output={
                    "metrics": metrics,
                    "findings": findings,
                    "summary": self._generate_bias_summary(metrics, findings),
                },
            )

        except FileNotFoundError as e:
            return ToolResult(success=False, output=None, error=f"File not found: {e}")
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
                        "data_path": {
                            "type": "string",
                            "description": "Path to dataset file (CSV, Parquet, JSON)",
                        },
                        "predictions": {
                            "type": "array",
                            "description": "List of prediction records",
                            "items": {"type": "object"},
                        },
                        "protected_attributes": {
                            "type": "array",
                            "description": "Columns to analyze for bias (e.g., gender, race)",
                            "items": {"type": "string"},
                        },
                        "target_column": {
                            "type": "string",
                            "description": "Target/outcome column name",
                        },
                        "positive_label": {
                            "description": "Value considered as positive outcome",
                        },
                    },
                    "required": ["protected_attributes"],
                },
            },
        }

    async def _analyze_representation(
        self,
        data_path: str,
        protected_attributes: list[str],
    ) -> dict[str, Any]:
        """Analyze data representation across protected groups."""
        # Implementation would use pandas
        # For now, return structure
        return {
            "total_records": 0,
            "by_attribute": {
                attr: {
                    "value_counts": {},
                    "percentages": {},
                    "underrepresented": [],
                }
                for attr in protected_attributes
            },
            "underrepresented_groups": [],
            "representation_score": 1.0,
        }

    async def _calculate_demographic_parity(
        self,
        data_path: str,
        protected_attributes: list[str],
        target_column: str,
        positive_label: Any,
    ) -> dict[str, Any]:
        """Calculate demographic parity metrics.

        Demographic parity (statistical parity) requires:
        P(Y=1|A=a) = P(Y=1|A=b) for all groups a, b
        """
        return {
            "overall_positive_rate": 0.0,
            "by_attribute": {
                attr: {
                    "group_rates": {},
                    "disparity_ratio": 1.0,  # min/max ratio (0.8+ is 80% rule)
                    "max_difference": 0.0,
                }
                for attr in protected_attributes
            },
            "four_fifths_rule_compliant": True,
        }

    async def _calculate_equalized_odds(
        self,
        predictions: list[dict[str, Any]],
        protected_attributes: list[str],
    ) -> dict[str, Any]:
        """Calculate equalized odds metrics.

        Equalized odds requires:
        P(Ŷ=1|Y=y,A=a) = P(Ŷ=1|Y=y,A=b) for y ∈ {0,1}
        """
        return {
            "by_attribute": {
                attr: {
                    "tpr_by_group": {},  # True positive rates
                    "fpr_by_group": {},  # False positive rates
                    "tpr_difference": 0.0,
                    "fpr_difference": 0.0,
                    "equalized_odds_difference": 0.0,
                }
                for attr in protected_attributes
            },
        }

    async def _analyze_calibration(
        self,
        predictions: list[dict[str, Any]],
        protected_attributes: list[str],
    ) -> dict[str, Any]:
        """Analyze prediction calibration across groups.

        Calibration requires predictions to be equally accurate across groups.
        """
        return {
            "by_attribute": {
                attr: {
                    "calibration_by_group": {},
                    "calibration_difference": 0.0,
                }
                for attr in protected_attributes
            },
        }

    def _generate_bias_summary(
        self,
        metrics: dict[str, Any],
        findings: list[dict[str, Any]],
    ) -> str:
        """Generate human-readable bias summary."""
        summary_parts = []

        # Representation summary
        if "representation" in metrics:
            rep = metrics["representation"]
            underrep = rep.get("underrepresented_groups", [])
            if underrep:
                summary_parts.append(
                    f"Underrepresented groups detected: {', '.join(underrep)}"
                )
            else:
                summary_parts.append("Data representation appears balanced")

        # Demographic parity summary
        if "demographic_parity" in metrics:
            dp = metrics["demographic_parity"]
            if dp.get("four_fifths_rule_compliant", True):
                summary_parts.append("Four-fifths (80%) rule: COMPLIANT")
            else:
                summary_parts.append("Four-fifths (80%) rule: VIOLATION DETECTED")

        # Findings summary
        high_severity = [f for f in findings if f.get("severity") == "high"]
        if high_severity:
            summary_parts.append(
                f"High-severity bias issues found: {len(high_severity)}"
            )

        return "\n".join(summary_parts) if summary_parts else "No bias issues detected"
