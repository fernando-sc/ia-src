"""Responsible AI (RAI) Multi-Agent Framework.

A comprehensive framework for AI system assessment based on six principles:
- Accountability
- Transparency
- Fairness & Inclusion
- Security & Privacy
- Reliability & Robustness
- Alignment

Example usage:
    from ia_src.rai import RAIRunner, SystemProfile

    profile = SystemProfile(
        system_id="my-system",
        name="My AI System",
        description="An AI system for classification",
        system_type="classification",
        owner="Team Name",
    )

    runner = RAIRunner.create_default(llm_provider)
    report = await runner.run_assessment(profile)
"""

from ia_src.rai.agents import (
    AccountabilityAgent,
    AIAAgent,
    AlignmentAgent,
    FairnessAgent,
    LifecycleAgent,
    OrchestratorAgent,
    RAIAgent,
    RobustnessAgent,
    SecurityAgent,
    TransparencyAgent,
)
from ia_src.rai.models import (
    AIAReport,
    ComplianceStatus,
    Finding,
    LifecyclePhase,
    Principle,
    PrincipleEvaluation,
    RiskAssessment,
    RiskLevel,
    Severity,
    SystemProfile,
)
from ia_src.rai.orchestration import RAIRunner
from ia_src.rai.tools import (
    BiasDetectionTool,
    ComplianceTool,
    DataProfilerTool,
    ExplainabilityTool,
    ReportGeneratorTool,
)

__all__ = [
    # Runner
    "RAIRunner",
    # Agents
    "RAIAgent",
    "AccountabilityAgent",
    "TransparencyAgent",
    "FairnessAgent",
    "SecurityAgent",
    "RobustnessAgent",
    "AlignmentAgent",
    "AIAAgent",
    "LifecycleAgent",
    "OrchestratorAgent",
    # Models
    "SystemProfile",
    "PrincipleEvaluation",
    "RiskAssessment",
    "AIAReport",
    "Principle",
    "ComplianceStatus",
    "Severity",
    "Finding",
    "RiskLevel",
    "LifecyclePhase",
    # Tools
    "BiasDetectionTool",
    "ExplainabilityTool",
    "ComplianceTool",
    "ReportGeneratorTool",
    "DataProfilerTool",
]
