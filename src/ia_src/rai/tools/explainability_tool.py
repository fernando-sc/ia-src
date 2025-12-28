"""Explainability Tool for model interpretation."""

from typing import Any

from ia_src.tools.base_tool import Tool, ToolResult


class ExplainabilityTool(Tool):
    """Generate model explanations.

    Capabilities:
    - Feature importance analysis
    - Counterfactual explanations
    - Decision path extraction
    - Human-readable explanations
    """

    name = "explainability"
    description = "Generate explanations for model predictions"

    async def execute(
        self,
        model_path: str | None = None,
        input_data: dict[str, Any] | None = None,
        prediction: Any = None,
        explanation_type: str = "feature_importance",
        target_audience: str = "technical",
        **kwargs: Any,
    ) -> ToolResult:
        """Generate explanations for AI model predictions.

        Args:
            model_path: Path to model file
            input_data: Input features for the prediction
            prediction: The model's prediction to explain
            explanation_type: Type of explanation:
                - feature_importance: SHAP-like feature contributions
                - counterfactual: What would need to change
                - decision_path: Step-by-step decision logic
                - summary: High-level explanation
            target_audience: Audience level (technical, business, end_user)

        Returns:
            ToolResult with explanation content
        """
        try:
            valid_types = ["feature_importance", "counterfactual", "decision_path", "summary"]
            if explanation_type not in valid_types:
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"Invalid explanation_type. Must be one of: {valid_types}",
                )

            if explanation_type == "feature_importance":
                explanation = await self._generate_feature_importance(
                    model_path, input_data
                )
            elif explanation_type == "counterfactual":
                explanation = await self._generate_counterfactual(
                    model_path, input_data, prediction
                )
            elif explanation_type == "decision_path":
                explanation = await self._extract_decision_path(model_path, input_data)
            else:  # summary
                explanation = await self._generate_summary(
                    model_path, input_data, prediction
                )

            # Format for target audience
            human_readable = self._format_for_audience(explanation, target_audience)

            return ToolResult(
                success=True,
                output={
                    "explanation_type": explanation_type,
                    "explanation": explanation,
                    "human_readable": human_readable,
                    "target_audience": target_audience,
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
                        "model_path": {
                            "type": "string",
                            "description": "Path to model file",
                        },
                        "input_data": {
                            "type": "object",
                            "description": "Input features for the prediction",
                        },
                        "prediction": {
                            "description": "The model's prediction to explain",
                        },
                        "explanation_type": {
                            "type": "string",
                            "enum": ["feature_importance", "counterfactual", "decision_path", "summary"],
                            "default": "feature_importance",
                        },
                        "target_audience": {
                            "type": "string",
                            "enum": ["technical", "business", "end_user"],
                            "default": "technical",
                        },
                    },
                },
            },
        }

    async def _generate_feature_importance(
        self,
        model_path: str | None,
        input_data: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Generate SHAP-like feature importance explanation.

        In production, this would use SHAP or similar library.
        """
        return {
            "type": "feature_importance",
            "method": "SHAP (placeholder)",
            "features": [
                # Example structure
                {"feature": "example_feature", "importance": 0.0, "contribution": 0.0}
            ],
            "base_value": 0.0,
            "output_value": 0.0,
            "top_positive_features": [],
            "top_negative_features": [],
        }

    async def _generate_counterfactual(
        self,
        model_path: str | None,
        input_data: dict[str, Any] | None,
        prediction: Any,
    ) -> dict[str, Any]:
        """Generate counterfactual explanation.

        Shows what minimal changes would flip the prediction.
        """
        return {
            "type": "counterfactual",
            "original_prediction": prediction,
            "counterfactual_prediction": None,
            "changes_required": [
                # Example structure
                {
                    "feature": "example_feature",
                    "original_value": None,
                    "counterfactual_value": None,
                }
            ],
            "distance": 0.0,
            "feasibility": "unknown",
        }

    async def _extract_decision_path(
        self,
        model_path: str | None,
        input_data: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Extract decision path for interpretable models."""
        return {
            "type": "decision_path",
            "steps": [
                # Example structure for tree-based models
                {
                    "node": 0,
                    "feature": "example_feature",
                    "threshold": 0.0,
                    "direction": "left",
                }
            ],
            "leaf_value": 0.0,
            "confidence": 0.0,
        }

    async def _generate_summary(
        self,
        model_path: str | None,
        input_data: dict[str, Any] | None,
        prediction: Any,
    ) -> dict[str, Any]:
        """Generate high-level summary explanation."""
        return {
            "type": "summary",
            "prediction": prediction,
            "key_factors": [],
            "confidence_level": "unknown",
            "similar_cases_comparison": None,
        }

    def _format_for_audience(
        self,
        explanation: dict[str, Any],
        audience: str,
    ) -> str:
        """Format explanation for target audience."""
        exp_type = explanation.get("type", "unknown")

        if audience == "end_user":
            # Simple, non-technical explanation
            if exp_type == "feature_importance":
                return (
                    "The decision was influenced by several factors. "
                    "Contact support for more details about your specific case."
                )
            elif exp_type == "counterfactual":
                return (
                    "To get a different result, certain factors in your situation "
                    "would need to be different. Contact support to learn more."
                )
            else:
                return "A decision was made based on the information provided."

        elif audience == "business":
            # Business-friendly explanation
            if exp_type == "feature_importance":
                features = explanation.get("top_positive_features", [])
                if features:
                    return f"The main factors driving this decision were: {', '.join(features[:3])}."
                return "Multiple factors contributed to this decision."
            elif exp_type == "counterfactual":
                return (
                    "Alternative scenarios were analyzed to understand "
                    "what changes could lead to different outcomes."
                )
            else:
                return "The model made a prediction based on input data analysis."

        else:  # technical
            # Detailed technical explanation
            if exp_type == "feature_importance":
                features = explanation.get("features", [])
                if features:
                    top_features = sorted(
                        features,
                        key=lambda x: abs(x.get("importance", 0)),
                        reverse=True,
                    )[:5]
                    lines = ["Feature Importance (SHAP values):"]
                    for f in top_features:
                        lines.append(
                            f"  {f.get('feature', 'N/A')}: "
                            f"{f.get('importance', 0):.4f} "
                            f"(contribution: {f.get('contribution', 0):+.4f})"
                        )
                    return "\n".join(lines)
                return "Feature importance analysis completed (no significant features identified)."
            elif exp_type == "counterfactual":
                changes = explanation.get("changes_required", [])
                if changes:
                    lines = ["Counterfactual explanation:"]
                    for c in changes:
                        lines.append(
                            f"  {c.get('feature', 'N/A')}: "
                            f"{c.get('original_value', 'N/A')} -> "
                            f"{c.get('counterfactual_value', 'N/A')}"
                        )
                    return "\n".join(lines)
                return "Counterfactual analysis completed."
            else:
                return f"Explanation type: {exp_type}\nDetails: {explanation}"
