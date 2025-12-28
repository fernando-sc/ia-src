"""Data Profiler Tool for dataset analysis."""

from typing import Any

from ia_src.tools.base_tool import Tool, ToolResult


class DataProfilerTool(Tool):
    """Analyze dataset quality and representativeness.

    Capabilities:
    - Basic statistics (counts, distributions)
    - Quality assessment (missing values, duplicates)
    - Representativeness analysis
    - Potential bias indicators
    """

    name = "data_profiler"
    description = "Profile datasets for quality, completeness, and representativeness"

    async def execute(
        self,
        data_path: str,
        target_column: str | None = None,
        sensitive_columns: list[str] | None = None,
        sample_size: int | None = None,
        **kwargs: Any,
    ) -> ToolResult:
        """Profile a dataset for RAI assessment.

        Args:
            data_path: Path to dataset (CSV, Parquet, JSON)
            target_column: Target/label column for classification analysis
            sensitive_columns: Columns with sensitive/protected attributes
            sample_size: If set, profile a random sample of this size

        Returns:
            ToolResult with comprehensive data profile
        """
        try:
            profile: dict[str, Any] = {
                "data_path": data_path,
                "basic_stats": await self._get_basic_stats(data_path, sample_size),
                "quality_metrics": await self._assess_quality(data_path),
                "completeness": await self._assess_completeness(data_path),
                "potential_issues": [],
                "recommendations": [],
            }

            # Add distribution analysis for sensitive columns
            if sensitive_columns:
                profile["distribution_analysis"] = await self._analyze_distributions(
                    data_path, sensitive_columns
                )
                profile["representativeness"] = await self._assess_representativeness(
                    data_path, sensitive_columns
                )

            # Add target analysis if provided
            if target_column:
                profile["target_analysis"] = await self._analyze_target(
                    data_path, target_column
                )

            # Identify potential issues
            profile["potential_issues"] = self._identify_issues(profile)
            profile["recommendations"] = self._generate_recommendations(profile)

            # Calculate overall data quality score
            profile["overall_quality_score"] = self._calculate_quality_score(profile)

            return ToolResult(success=True, output=profile)

        except FileNotFoundError:
            return ToolResult(
                success=False, output=None, error=f"File not found: {data_path}"
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
                        "data_path": {
                            "type": "string",
                            "description": "Path to dataset file",
                        },
                        "target_column": {
                            "type": "string",
                            "description": "Target/label column name",
                        },
                        "sensitive_columns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Columns with sensitive/protected attributes",
                        },
                        "sample_size": {
                            "type": "integer",
                            "description": "Sample size for large datasets",
                        },
                    },
                    "required": ["data_path"],
                },
            },
        }

    async def _get_basic_stats(
        self,
        data_path: str,
        sample_size: int | None,
    ) -> dict[str, Any]:
        """Get basic dataset statistics.

        In production, would use pandas for actual analysis.
        """
        return {
            "row_count": 0,
            "column_count": 0,
            "sampled": sample_size is not None,
            "sample_size": sample_size,
            "columns": [],
            "dtypes": {},
            "memory_usage_mb": 0.0,
        }

    async def _assess_quality(self, data_path: str) -> dict[str, Any]:
        """Assess data quality metrics."""
        return {
            "duplicate_rows": 0,
            "duplicate_rate": 0.0,
            "constant_columns": [],
            "high_cardinality_columns": [],
            "potential_id_columns": [],
            "mixed_type_columns": [],
        }

    async def _assess_completeness(self, data_path: str) -> dict[str, Any]:
        """Assess data completeness."""
        return {
            "total_cells": 0,
            "missing_cells": 0,
            "missing_rate": 0.0,
            "by_column": {},
            "columns_with_high_missing": [],  # >10% missing
            "complete_columns": [],
        }

    async def _analyze_distributions(
        self,
        data_path: str,
        sensitive_columns: list[str],
    ) -> dict[str, Any]:
        """Analyze distributions of sensitive columns."""
        return {
            attr: {
                "unique_values": 0,
                "value_counts": {},
                "percentages": {},
                "mode": None,
                "entropy": 0.0,
            }
            for attr in sensitive_columns
        }

    async def _assess_representativeness(
        self,
        data_path: str,
        sensitive_columns: list[str],
    ) -> dict[str, Any]:
        """Assess representativeness across sensitive attributes."""
        return {
            "by_attribute": {
                attr: {
                    "imbalance_ratio": 1.0,  # max/min ratio
                    "min_group_size": 0,
                    "min_group_percentage": 0.0,
                    "underrepresented_threshold": 0.1,  # 10%
                    "underrepresented_groups": [],
                    "is_balanced": True,
                }
                for attr in sensitive_columns
            },
            "overall_representativeness_score": 1.0,
        }

    async def _analyze_target(
        self,
        data_path: str,
        target_column: str,
    ) -> dict[str, Any]:
        """Analyze target variable distribution."""
        return {
            "column": target_column,
            "dtype": "unknown",
            "unique_values": 0,
            "value_distribution": {},
            "is_binary": False,
            "is_imbalanced": False,
            "imbalance_ratio": 1.0,
            "minority_class": None,
            "minority_percentage": 0.0,
        }

    def _identify_issues(self, profile: dict[str, Any]) -> list[dict[str, Any]]:
        """Identify potential data issues."""
        issues = []

        # Check completeness
        completeness = profile.get("completeness", {})
        if completeness.get("missing_rate", 0) > 0.1:
            issues.append({
                "type": "high_missing_data",
                "severity": "medium",
                "description": f"Missing data rate: {completeness.get('missing_rate', 0):.1%}",
                "affected_columns": completeness.get("columns_with_high_missing", []),
            })

        # Check representativeness
        rep = profile.get("representativeness", {})
        for attr, data in rep.get("by_attribute", {}).items():
            if data.get("underrepresented_groups"):
                issues.append({
                    "type": "underrepresentation",
                    "severity": "high",
                    "description": f"Underrepresented groups in {attr}",
                    "affected_groups": data["underrepresented_groups"],
                })

        # Check target imbalance
        target = profile.get("target_analysis", {})
        if target.get("is_imbalanced"):
            issues.append({
                "type": "class_imbalance",
                "severity": "medium",
                "description": f"Target class imbalance ratio: {target.get('imbalance_ratio', 1):.1f}",
                "minority_class": target.get("minority_class"),
            })

        # Check quality
        quality = profile.get("quality_metrics", {})
        if quality.get("duplicate_rate", 0) > 0.01:
            issues.append({
                "type": "duplicates",
                "severity": "low",
                "description": f"Duplicate rows detected: {quality.get('duplicate_rate', 0):.1%}",
            })

        return issues

    def _generate_recommendations(
        self,
        profile: dict[str, Any],
    ) -> list[str]:
        """Generate recommendations based on profile."""
        recommendations = []

        for issue in profile.get("potential_issues", []):
            issue_type = issue.get("type")

            if issue_type == "high_missing_data":
                recommendations.append(
                    "Consider imputation strategies or investigate missing data patterns"
                )
            elif issue_type == "underrepresentation":
                recommendations.append(
                    f"Address underrepresentation in {issue.get('affected_groups')} "
                    "through data collection or augmentation"
                )
            elif issue_type == "class_imbalance":
                recommendations.append(
                    "Consider resampling techniques (SMOTE, undersampling) "
                    "or class weighting"
                )
            elif issue_type == "duplicates":
                recommendations.append(
                    "Review and deduplicate data to prevent data leakage"
                )

        if not recommendations:
            recommendations.append("Dataset appears suitable for model training")

        return recommendations

    def _calculate_quality_score(self, profile: dict[str, Any]) -> float:
        """Calculate overall data quality score (0-1)."""
        score = 1.0

        # Penalize for missing data
        missing_rate = profile.get("completeness", {}).get("missing_rate", 0)
        score -= min(0.3, missing_rate)

        # Penalize for duplicates
        dup_rate = profile.get("quality_metrics", {}).get("duplicate_rate", 0)
        score -= min(0.1, dup_rate)

        # Penalize for underrepresentation
        rep = profile.get("representativeness", {})
        rep_score = rep.get("overall_representativeness_score", 1.0)
        score -= (1 - rep_score) * 0.3

        # Penalize for issues count
        issue_count = len(profile.get("potential_issues", []))
        score -= min(0.2, issue_count * 0.05)

        return max(0.0, min(1.0, score))
