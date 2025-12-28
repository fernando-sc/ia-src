"""RAI Assessment CLI - Command line interface for Responsible AI assessments."""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

import click

from ia_src.rai.models import SystemProfile


def load_system_profile(file_path: str) -> SystemProfile:
    """Load system profile from JSON or YAML file."""
    path = Path(file_path)

    if not path.exists():
        raise click.ClickException(f"File not found: {file_path}")

    content = path.read_text()

    if path.suffix in (".yaml", ".yml"):
        try:
            import yaml
            data = yaml.safe_load(content)
        except ImportError:
            raise click.ClickException("PyYAML required for YAML files: pip install pyyaml")
    else:
        data = json.loads(content)

    return SystemProfile(**data)


def get_llm_provider():
    """Get configured LLM provider."""
    # Try to get from environment or config
    import os

    # Try Anthropic first
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        try:
            from ia_src.llm.anthropic_provider import AnthropicProvider
            return AnthropicProvider(api_key=api_key)
        except ImportError:
            pass

    # Try OpenAI
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        try:
            from ia_src.llm.openai_provider import OpenAIProvider
            return OpenAIProvider(api_key=api_key)
        except ImportError:
            pass

    # Return a mock provider for demonstration
    from ia_src.rai.cli.mock_provider import MockLLMProvider
    click.echo("Warning: No API key found. Using mock LLM provider.", err=True)
    return MockLLMProvider()


@click.group()
@click.version_option(version="0.1.0", prog_name="rai")
def rai():
    """RAI Assessment CLI - Responsible AI evaluation tools.

    Evaluate AI systems for compliance with responsible AI principles:
    Accountability, Transparency, Fairness, Security, Robustness, and Alignment.
    """
    pass


@rai.command()
@click.option(
    "--system-profile", "-s",
    required=True,
    type=click.Path(exists=True),
    help="Path to system profile JSON/YAML file",
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    default="rai_assessment.json",
    help="Output file path",
)
@click.option(
    "--format", "-f",
    type=click.Choice(["json", "markdown"]),
    default="json",
    help="Output format",
)
@click.option(
    "--principles", "-p",
    multiple=True,
    type=click.Choice([
        "accountability", "transparency", "fairness",
        "security", "robustness", "alignment", "all"
    ]),
    default=["all"],
    help="Principles to evaluate",
)
def assess(system_profile: str, output: str, format: str, principles: tuple):
    """Run RAI assessment on an AI system.

    Example:
        rai assess -s system_profile.json -o report.json
    """
    click.echo(f"Loading system profile from {system_profile}...")

    try:
        profile = load_system_profile(system_profile)
        click.echo(f"System: {profile.name}")
        click.echo(f"Risk Level: {profile.risk_level.value}")
    except Exception as e:
        raise click.ClickException(f"Failed to load profile: {e}")

    click.echo("\nRunning RAI assessment...")

    # Run assessment
    asyncio.run(_run_assessment(profile, output, format, list(principles)))


async def _run_assessment(
    profile: SystemProfile,
    output: str,
    format: str,
    principles: list[str],
):
    """Run the assessment asynchronously."""
    from ia_src.rai.orchestration import RAIRunner

    llm_provider = get_llm_provider()
    runner = RAIRunner(llm_provider)

    # Run assessment
    report = await runner.run_assessment(
        profile,
        principles=None if "all" in principles else principles,
    )

    # Output results
    if format == "json":
        output_data = report.model_dump(mode="json")
        Path(output).write_text(json.dumps(output_data, indent=2, default=str))
    else:
        # Generate markdown
        from ia_src.rai.tools import ReportGeneratorTool
        generator = ReportGeneratorTool()
        result = await generator.execute(
            report_type="summary",
            data={
                "system_name": profile.name,
                "overall_score": report.calculate_overall_score(),
                "evaluations": [
                    {
                        "principle": e.principle.value,
                        "score": e.score,
                        "status": e.compliance_status.value,
                    }
                    for e in report.principle_evaluations
                ],
                "recommendation": report.overall_recommendation,
            },
        )
        if result.success:
            Path(output).write_text(result.output["content"])

    click.echo(f"\nAssessment complete. Results saved to: {output}")
    click.echo(f"Overall Score: {report.calculate_overall_score():.2f}")
    click.echo(f"Recommendation: {report.overall_recommendation}")


@rai.command()
@click.option(
    "--system-profile", "-s",
    required=True,
    type=click.Path(exists=True),
    help="Path to system profile JSON/YAML file",
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    default="aia_report.md",
    help="Output file path",
)
@click.option(
    "--interactive/--non-interactive", "-i",
    default=False,
    help="Run in interactive mode",
)
def aia(system_profile: str, output: str, interactive: bool):
    """Generate Algorithmic Impact Assessment report.

    Example:
        rai aia -s system_profile.json -o aia_report.md
    """
    click.echo(f"Loading system profile from {system_profile}...")

    try:
        profile = load_system_profile(system_profile)
        click.echo(f"System: {profile.name}")
    except Exception as e:
        raise click.ClickException(f"Failed to load profile: {e}")

    click.echo("\nGenerating AIA report...")
    asyncio.run(_run_aia(profile, output))


async def _run_aia(profile: SystemProfile, output: str):
    """Run AIA asynchronously."""
    from ia_src.rai.orchestration import RAIRunner
    from ia_src.rai.tools import ReportGeneratorTool

    llm_provider = get_llm_provider()
    runner = RAIRunner(llm_provider)

    report = await runner.run_aia(profile)

    # Generate markdown report
    generator = ReportGeneratorTool()
    result = await generator.execute(
        report_type="aia",
        data={
            "report_id": report.report_id,
            "system_name": profile.name,
            "system_id": profile.system_id,
            "owner": profile.owner,
            "risk_level": profile.risk_level.value,
            "current_phase": profile.current_phase.value,
            "recommendation": report.overall_recommendation,
            "evaluations": [
                {
                    "principle": e.principle.value,
                    "score": e.score,
                    "status": e.compliance_status.value,
                    "findings": [
                        {"severity": f.severity.value, "description": f.description}
                        for f in e.findings
                    ],
                }
                for e in report.principle_evaluations
            ],
        },
        output_format="markdown",
    )

    if result.success:
        Path(output).write_text(result.output["content"])
        click.echo(f"\nAIA report generated: {output}")
    else:
        raise click.ClickException(f"Failed to generate report: {result.error}")


@rai.command()
@click.option(
    "--system-profile", "-s",
    required=True,
    type=click.Path(exists=True),
    help="Path to system profile JSON/YAML file",
)
@click.option(
    "--phase", "-p",
    type=click.Choice([
        "business_understanding", "design_data_models", "validation_verification",
        "deployment", "operation_monitoring", "shutdown"
    ]),
    help="Specific phase to check",
)
def lifecycle(system_profile: str, phase: str | None):
    """Check lifecycle phase compliance and checkpoints.

    Example:
        rai lifecycle -s system_profile.json
    """
    click.echo(f"Loading system profile from {system_profile}...")

    try:
        profile = load_system_profile(system_profile)
        click.echo(f"System: {profile.name}")
        click.echo(f"Current Phase: {profile.current_phase.value}")
    except Exception as e:
        raise click.ClickException(f"Failed to load profile: {e}")

    asyncio.run(_run_lifecycle(profile))


async def _run_lifecycle(profile: SystemProfile):
    """Run lifecycle check asynchronously."""
    from ia_src.rai.orchestration import RAIRunner

    llm_provider = get_llm_provider()
    runner = RAIRunner(llm_provider)

    status = await runner.check_lifecycle(profile)

    click.echo(f"\nCurrent Phase: {status.get('current_phase', 'Unknown')}")
    click.echo(f"Completion: {status.get('completion', 0):.0%}")
    click.echo(f"Ready for Next Phase: {'Yes' if status.get('ready_for_next') else 'No'}")

    if status.get("next_phase"):
        click.echo(f"Next Phase: {status['next_phase']}")

    incomplete = status.get("incomplete_checkpoints", [])
    if incomplete:
        click.echo(f"\nIncomplete Checkpoints ({len(incomplete)}):")
        for cp in incomplete:
            click.echo(f"  - {cp}")


@rai.command()
@click.option(
    "--regulation", "-r",
    required=True,
    type=click.Choice(["gdpr", "eu_ai_act", "lgpd", "all"]),
    help="Regulation to check",
)
@click.option(
    "--system-profile", "-s",
    required=True,
    type=click.Path(exists=True),
    help="Path to system profile JSON/YAML file",
)
@click.option(
    "--evidence", "-e",
    type=click.Path(exists=True),
    help="Path to compliance evidence file",
)
def compliance(regulation: str, system_profile: str, evidence: str | None):
    """Check regulatory compliance.

    Example:
        rai compliance -r eu_ai_act -s system_profile.json
    """
    click.echo(f"Checking {regulation.upper()} compliance...")

    try:
        profile = load_system_profile(system_profile)
    except Exception as e:
        raise click.ClickException(f"Failed to load profile: {e}")

    evidence_data = {}
    if evidence:
        evidence_data = json.loads(Path(evidence).read_text())

    asyncio.run(_run_compliance(regulation, profile, evidence_data))


async def _run_compliance(
    regulation: str,
    profile: SystemProfile,
    evidence: dict[str, Any],
):
    """Run compliance check asynchronously."""
    from ia_src.rai.tools import ComplianceTool

    tool = ComplianceTool()
    result = await tool.execute(
        regulation=regulation,
        system_profile=profile.model_dump(),
        evidence=evidence,
    )

    if result.success:
        output = result.output
        click.echo(f"\nRegulation: {output.get('regulation', regulation)}")
        click.echo(f"Overall Status: {output.get('overall_status', 'N/A')}")

        if "requirements" in output:
            click.echo(f"\nRequirements Checked: {len(output['requirements'])}")
            for req in output.get("compliant", []):
                click.echo(f"  [OK] {req.get('title', req.get('article', 'Unknown'))}")
            for req in output.get("non_compliant", []):
                click.echo(f"  [!!] {req.get('title', req.get('article', 'Unknown'))}")
    else:
        raise click.ClickException(f"Compliance check failed: {result.error}")


@rai.group()
def report():
    """Report generation commands."""
    pass


@report.command()
@click.option(
    "--assessment", "-a",
    required=True,
    type=click.Path(exists=True),
    help="Path to assessment results JSON",
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    default="report.md",
    help="Output file path",
)
@click.option(
    "--format", "-f",
    type=click.Choice(["markdown", "html", "json"]),
    default="markdown",
    help="Output format",
)
@click.option(
    "--type", "-t",
    type=click.Choice(["aia", "audit", "summary"]),
    default="summary",
    help="Report type",
)
def generate(assessment: str, output: str, format: str, type: str):
    """Generate a report from assessment results.

    Example:
        rai report generate -a assessment.json -f markdown -t summary
    """
    click.echo(f"Generating {type} report...")

    data = json.loads(Path(assessment).read_text())
    asyncio.run(_generate_report(data, output, format, type))


async def _generate_report(
    data: dict[str, Any],
    output: str,
    format: str,
    report_type: str,
):
    """Generate report asynchronously."""
    from ia_src.rai.tools import ReportGeneratorTool

    tool = ReportGeneratorTool()
    result = await tool.execute(
        report_type=report_type,
        data=data,
        output_format=format,
    )

    if result.success:
        Path(output).write_text(result.output["content"])
        click.echo(f"Report generated: {output}")
    else:
        raise click.ClickException(f"Report generation failed: {result.error}")


@rai.command()
@click.option(
    "--output", "-o",
    type=click.Path(),
    default="system_profile.json",
    help="Output file path",
)
def init(output: str):
    """Initialize a new system profile template.

    Example:
        rai init -o my_system.json
    """
    template = {
        "system_id": "my-ai-system-001",
        "name": "My AI System",
        "description": "Description of what the AI system does",
        "version": "1.0.0",
        "system_type": "classification",
        "risk_level": "medium",
        "is_high_risk_eu_ai_act": False,
        "model_architecture": "e.g., RandomForest, Transformer, CNN",
        "training_data_description": "Description of training data sources",
        "input_data_types": ["text", "numeric"],
        "output_data_types": ["classification"],
        "owner": "Team or Person Name",
        "developers": ["Developer 1", "Developer 2"],
        "operators": ["Operations Team"],
        "affected_populations": ["Users", "Customers"],
        "current_phase": "design_data_models",
        "applicable_regulations": ["GDPR"],
        "industry_sector": "e.g., finance, healthcare",
        "use_cases": ["Use case 1", "Use case 2"],
        "known_limitations": ["Limitation 1"],
        "prohibited_uses": ["Do not use for X"],
    }

    Path(output).write_text(json.dumps(template, indent=2))
    click.echo(f"System profile template created: {output}")
    click.echo("Edit this file with your system's details, then run:")
    click.echo(f"  rai assess -s {output}")


def main():
    """Main entry point."""
    rai()


if __name__ == "__main__":
    main()
