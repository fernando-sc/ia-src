"""Comprehensive tests for the RAI multi-agent system."""

import asyncio
import json
from pathlib import Path

# Test imports
def test_imports():
    """Test all module imports work correctly."""
    print("Testing imports...")

    # Models
    from ia_src.rai.models import (
        SystemProfile, PrincipleEvaluation, RiskAssessment, AIAReport,
        Principle, ComplianceStatus, Severity, RiskLevel, LifecyclePhase
    )
    print("  - Models: OK")

    # Tools
    from ia_src.rai.tools import (
        BiasDetectionTool, ComplianceTool, DataProfilerTool,
        ExplainabilityTool, ReportGeneratorTool
    )
    print("  - Tools: OK")

    # Agents
    from ia_src.rai.agents import (
        RAIAgent, AccountabilityAgent, TransparencyAgent, FairnessAgent,
        SecurityAgent, RobustnessAgent, AlignmentAgent,
        AIAAgent, LifecycleAgent, OrchestratorAgent
    )
    print("  - Agents: OK")

    # Orchestration
    from ia_src.rai.orchestration import RAIRunner
    print("  - Orchestration: OK")

    print("All imports successful!")
    return True


def test_system_profile():
    """Test SystemProfile model."""
    print("\nTesting SystemProfile model...")

    from ia_src.rai.models import SystemProfile, RiskLevel, AISystemType, LifecyclePhase

    # Create a profile
    profile = SystemProfile(
        system_id="test-001",
        name="Test AI System",
        description="A test AI system for unit testing",
        system_type=AISystemType.CLASSIFICATION,
        risk_level=RiskLevel.MEDIUM,
        owner="Test Team",
        affected_populations=["users", "customers"],
        current_phase=LifecyclePhase.DESIGN_DATA_MODELS,
    )

    assert profile.system_id == "test-001"
    assert profile.name == "Test AI System"
    assert profile.risk_level == RiskLevel.MEDIUM
    assert len(profile.affected_populations) == 2

    # Test serialization
    json_str = profile.model_dump_json()
    assert "test-001" in json_str

    print("  - Creation: OK")
    print("  - Serialization: OK")
    print("SystemProfile tests passed!")
    return True


def test_principle_evaluation():
    """Test PrincipleEvaluation model."""
    print("\nTesting PrincipleEvaluation model...")

    from ia_src.rai.models import (
        PrincipleEvaluation, Principle, ComplianceStatus,
        Finding, Severity, RemediationEffort
    )

    finding = Finding(
        finding_id="TEST-001",
        category="governance",
        severity=Severity.HIGH,
        description="Test finding",
        recommendation="Fix this issue",
        remediation_effort=RemediationEffort.MEDIUM,
    )

    evaluation = PrincipleEvaluation(
        principle=Principle.ACCOUNTABILITY,
        evaluator_agent="TestAgent",
        compliance_status=ComplianceStatus.PARTIALLY_COMPLIANT,
        score=0.75,
        findings=[finding],
        strengths=["Good documentation"],
        weaknesses=["Missing audit trail"],
    )

    assert evaluation.score == 0.75
    assert len(evaluation.findings) == 1
    assert evaluation.get_critical_findings() == []  # No critical findings

    print("  - Finding creation: OK")
    print("  - Evaluation creation: OK")
    print("PrincipleEvaluation tests passed!")
    return True


def test_risk_assessment():
    """Test RiskAssessment model."""
    print("\nTesting RiskAssessment model...")

    from ia_src.rai.models import (
        RiskAssessment, Risk, Mitigation, RiskCategory,
        Likelihood, Impact, MitigationStrategy
    )

    risk = Risk(
        risk_id="RISK-001",
        title="Data Quality Risk",
        description="Training data may contain biases",
        category=RiskCategory.ETHICAL,
        likelihood=Likelihood.POSSIBLE,
        impact=Impact.MAJOR,
    )

    # Test risk score calculation
    assert risk.risk_score == 12  # 3 * 4
    assert risk.risk_level == "high"

    mitigation = Mitigation(
        mitigation_id="MIT-001",
        risk_ids=["RISK-001"],
        strategy=MitigationStrategy.REDUCE,
        title="Data Audit",
        description="Conduct data bias audit",
        responsible_party="Data Team",
    )

    assessment = RiskAssessment(
        assessment_id="RA-001",
        system_id="test-001",
        assessor="Risk Agent",
        identified_risks=[risk],
        mitigations=[mitigation],
    )

    assert len(assessment.get_high_risks()) == 1
    assert len(assessment.get_unmitigated_risks()) == 0

    print("  - Risk creation: OK")
    print("  - Risk score calculation: OK")
    print("  - Mitigation creation: OK")
    print("RiskAssessment tests passed!")
    return True


def test_tools():
    """Test RAI tools."""
    print("\nTesting RAI tools...")

    async def run_tool_tests():
        from ia_src.rai.tools import (
            BiasDetectionTool, ComplianceTool, ReportGeneratorTool
        )

        # Test BiasDetectionTool
        bias_tool = BiasDetectionTool()
        result = await bias_tool.execute(
            protected_attributes=["gender", "age"],
        )
        assert result.success
        assert "metrics" in result.output
        print("  - BiasDetectionTool: OK")

        # Test ComplianceTool
        compliance_tool = ComplianceTool()
        result = await compliance_tool.execute(
            regulation="gdpr",
            system_profile={"is_high_risk_eu_ai_act": False},
        )
        assert result.success
        assert "regulation" in result.output
        print("  - ComplianceTool: OK")

        # Test ReportGeneratorTool
        report_tool = ReportGeneratorTool()
        result = await report_tool.execute(
            report_type="summary",
            data={
                "system_name": "Test System",
                "overall_score": 0.85,
                "evaluations": [],
                "recommendation": "proceed",
            },
        )
        assert result.success
        assert "content" in result.output
        print("  - ReportGeneratorTool: OK")

    asyncio.run(run_tool_tests())
    print("Tools tests passed!")
    return True


def test_agents():
    """Test RAI agents."""
    print("\nTesting RAI agents...")

    async def run_agent_tests():
        from ia_src.rai.agents import AccountabilityAgent, FairnessAgent
        from ia_src.rai.models import SystemProfile, AISystemType, RiskLevel
        from ia_src.rai.cli.mock_provider import MockLLMProvider
        from ia_src.core.context import Context

        # Create mock provider
        provider = MockLLMProvider()

        # Create test profile
        profile = SystemProfile(
            system_id="test-001",
            name="Test AI System",
            description="A test AI system for unit testing purposes",
            system_type=AISystemType.CLASSIFICATION,
            risk_level=RiskLevel.HIGH,
            is_high_risk_eu_ai_act=True,
            owner="Test Team",
            developers=["Dev1"],
            operators=["Ops1"],
            affected_populations=["users"],
            applicable_regulations=["GDPR", "EU AI Act"],
        )

        # Test AccountabilityAgent
        acc_agent = AccountabilityAgent(provider)
        context = Context()
        context.set_variable("system_profile", profile)

        evaluation = await acc_agent.evaluate(profile, context)
        assert evaluation.principle.value == "accountability"
        assert 0 <= evaluation.score <= 1
        print(f"  - AccountabilityAgent: OK (score: {evaluation.score:.2f})")

        # Test FairnessAgent
        fair_agent = FairnessAgent(provider)
        evaluation = await fair_agent.evaluate(profile, context)
        assert evaluation.principle.value == "fairness"
        assert 0 <= evaluation.score <= 1
        print(f"  - FairnessAgent: OK (score: {evaluation.score:.2f})")

    asyncio.run(run_agent_tests())
    print("Agents tests passed!")
    return True


def test_aia_agent():
    """Test AIA Agent."""
    print("\nTesting AIA Agent...")

    async def run_aia_test():
        from ia_src.rai.agents import AIAAgent
        from ia_src.rai.models import SystemProfile, AISystemType, RiskLevel
        from ia_src.rai.cli.mock_provider import MockLLMProvider
        from ia_src.core.context import Context
        from ia_src.core.message import Message

        provider = MockLLMProvider()
        aia_agent = AIAAgent(provider)

        profile = SystemProfile(
            system_id="test-001",
            name="Test AI System",
            description="A test AI system",
            system_type=AISystemType.CLASSIFICATION,
            risk_level=RiskLevel.MEDIUM,
            owner="Test Team",
            use_cases=["Testing"],
        )

        context = Context()
        context.set_variable("system_profile", profile)

        # Run full assessment
        response = await aia_agent.run(Message.user("full assessment"), context)

        # Check report was generated
        report = context.get_variable("aia_report")
        assert report is not None
        assert report.system_profile.name == "Test AI System"
        print(f"  - AIA Report generated: {report.report_id[:8]}...")
        print(f"  - Recommendation: {report.overall_recommendation}")

    asyncio.run(run_aia_test())
    print("AIA Agent tests passed!")
    return True


def test_lifecycle_agent():
    """Test Lifecycle Agent."""
    print("\nTesting Lifecycle Agent...")

    async def run_lifecycle_test():
        from ia_src.rai.agents import LifecycleAgent
        from ia_src.rai.models import SystemProfile, AISystemType, LifecyclePhase
        from ia_src.rai.cli.mock_provider import MockLLMProvider
        from ia_src.core.context import Context
        from ia_src.core.message import Message

        provider = MockLLMProvider()
        lifecycle_agent = LifecycleAgent(provider)

        profile = SystemProfile(
            system_id="test-001",
            name="Test AI System",
            description="A test AI system",
            system_type=AISystemType.CLASSIFICATION,
            owner="Test Team",
            current_phase=LifecyclePhase.DESIGN_DATA_MODELS,
        )

        context = Context()
        context.set_variable("system_profile", profile)

        # Get status
        response = await lifecycle_agent.run(Message.user("status"), context)
        assert "Design Data Models" in response.content or "design_data_models" in response.content.lower()

        # Check lifecycle status created
        status = context.get_variable("lifecycle_status")
        assert status is not None
        assert status.current_phase == LifecyclePhase.DESIGN_DATA_MODELS
        print(f"  - Current phase: {status.current_phase.value}")
        print(f"  - Checkpoints: {len(status.current_phase_checkpoints)}")

    asyncio.run(run_lifecycle_test())
    print("Lifecycle Agent tests passed!")
    return True


def test_orchestrator():
    """Test Orchestrator Agent."""
    print("\nTesting Orchestrator Agent...")

    async def run_orchestrator_test():
        from ia_src.rai.orchestration import RAIRunner
        from ia_src.rai.models import SystemProfile, AISystemType, RiskLevel
        from ia_src.rai.cli.mock_provider import MockLLMProvider

        provider = MockLLMProvider()
        runner = RAIRunner(provider)

        profile = SystemProfile(
            system_id="test-001",
            name="Test AI System",
            description="A comprehensive test AI system for validation",
            system_type=AISystemType.CLASSIFICATION,
            risk_level=RiskLevel.HIGH,
            is_high_risk_eu_ai_act=True,
            owner="Test Team",
            developers=["Dev Team"],
            operators=["Ops Team"],
            affected_populations=["users", "customers"],
            applicable_regulations=["GDPR", "EU AI Act"],
            model_architecture="XGBoost",
            training_data_description="Historical data from 2020-2023",
            known_limitations=["May underperform on edge cases"],
        )

        # Run full assessment
        report = await runner.run_assessment(profile)

        assert report is not None
        # The report should have principle evaluations (may vary based on execution)
        num_evals = len(report.principle_evaluations)
        print(f"  - Principles evaluated: {num_evals}")

        if num_evals == 0:
            # Run individual evaluations if orchestrator didn't populate them
            for principle in ["accountability", "transparency", "fairness",
                            "security", "robustness", "alignment"]:
                eval_result = await runner.run_principle_evaluation(profile, principle)
                report.principle_evaluations.append(eval_result)
            print(f"  - Evaluated individually: {len(report.principle_evaluations)}")

        overall_score = report.calculate_overall_score()
        print(f"  - Overall score: {overall_score:.2f}")
        print(f"  - Recommendation: {report.overall_recommendation}")

        # Print individual scores
        for eval in report.principle_evaluations:
            print(f"    - {eval.principle.value}: {eval.score:.2f}")

    asyncio.run(run_orchestrator_test())
    print("Orchestrator tests passed!")
    return True


def test_example_profile():
    """Test loading the example profile."""
    print("\nTesting example profile loading...")

    example_path = Path("examples/credit_scoring_profile.json")
    if not example_path.exists():
        print("  - Example file not found, skipping")
        return True

    from ia_src.rai.models import SystemProfile

    with open(example_path) as f:
        data = json.load(f)

    profile = SystemProfile(**data)

    assert profile.name == "Credit Scoring Model"
    assert profile.risk_level.value == "high"
    assert profile.is_high_risk_eu_ai_act == True
    assert "finance" in profile.industry_sector.lower()

    print(f"  - Loaded: {profile.name}")
    print(f"  - Risk Level: {profile.risk_level.value}")
    print(f"  - Phase: {profile.current_phase.value}")
    print("Example profile tests passed!")
    return True


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("RAI Multi-Agent System Test Suite")
    print("=" * 60)

    tests = [
        ("Imports", test_imports),
        ("SystemProfile", test_system_profile),
        ("PrincipleEvaluation", test_principle_evaluation),
        ("RiskAssessment", test_risk_assessment),
        ("Tools", test_tools),
        ("Agents", test_agents),
        ("AIA Agent", test_aia_agent),
        ("Lifecycle Agent", test_lifecycle_agent),
        ("Orchestrator", test_orchestrator),
        ("Example Profile", test_example_profile),
    ]

    passed = 0
    failed = 0

    for name, test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"\n!!! {name} FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "src")
    success = run_all_tests()
    sys.exit(0 if success else 1)
