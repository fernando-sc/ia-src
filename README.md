# RAI - Responsible AI Multi-Agent Framework

A comprehensive multi-agent system for assessing and ensuring Responsible AI practices throughout the AI lifecycle. Based on six core principles and designed for regulatory compliance with GDPR, EU AI Act, and other frameworks.

## Overview

This framework provides automated assessment of AI systems against six Responsible AI principles:

| Principle | Description |
|-----------|-------------|
| **Accountability** | Governance structures, audit trails, responsibility mapping |
| **Transparency** | Explainability, documentation, stakeholder communication |
| **Fairness** | Bias detection, demographic parity, equitable outcomes |
| **Security** | Privacy compliance, vulnerability assessment, data protection |
| **Robustness** | Reliability testing, performance monitoring, fault tolerance |
| **Alignment** | Human oversight, ethical review, value alignment |

## Features

- **10 Specialized Agents**: Principle evaluators, AIA generator, lifecycle manager, orchestrator
- **5 Analysis Tools**: Bias detection, compliance checking, explainability, reporting, data profiling
- **Algorithmic Impact Assessment (AIA)**: Complete 6-section reports per regulatory standards
- **Lifecycle Management**: Phase checkpoints from design through deployment to shutdown
- **Regulatory Compliance**: Built-in checks for GDPR, EU AI Act, LGPD
- **CLI Interface**: Command-line tools for assessments and reports

## Installation

```bash
# Clone the repository
git clone https://github.com/fernandosicos/ia-src.git
cd ia-src

# Install dependencies
pip install -e ".[rai]"
```

## Quick Start

### Define Your AI System Profile

Create a JSON file describing your AI system:

```json
{
  "system_id": "my-ai-system",
  "name": "My AI System",
  "description": "Description of what the AI system does",
  "system_type": "classification",
  "risk_level": "medium",
  "owner": "Team Name",
  "affected_populations": ["users", "customers"],
  "applicable_regulations": ["GDPR"],
  "current_phase": "design_data_models"
}
```

### Run Assessment via CLI

```bash
# Initialize a new system profile template
rai init -o my_system.json

# Run full RAI assessment
rai assess -s my_system.json -o assessment.json

# Generate Algorithmic Impact Assessment report
rai aia -s my_system.json -o aia_report.json

# Check regulatory compliance
rai compliance -s my_system.json -r gdpr

# Check lifecycle phase status
rai lifecycle -s my_system.json
```

### Programmatic Usage

```python
import asyncio
from ia_src.rai import RAIRunner, SystemProfile

# Define system profile
profile = SystemProfile(
    system_id="credit-scoring-v1",
    name="Credit Scoring Model",
    description="ML model for credit risk assessment",
    system_type="classification",
    risk_level="high",
    owner="Risk Analytics Team",
    affected_populations=["loan applicants"],
    applicable_regulations=["GDPR", "EU AI Act"]
)

# Run assessment
async def main():
    runner = RAIRunner(provider)  # Provide your LLM provider
    report = await runner.run_assessment(profile)

    print(f"Overall Score: {report.calculate_overall_score():.2f}")
    for eval in report.principle_evaluations:
        print(f"  {eval.principle.value}: {eval.score:.2f}")

asyncio.run(main())
```

## Project Structure

```
src/ia_src/rai/
├── agents/                    # Specialized RAI agents
│   ├── base_rai_agent.py      # Base class for RAI agents
│   ├── accountability_agent.py
│   ├── transparency_agent.py
│   ├── fairness_agent.py
│   ├── security_agent.py
│   ├── robustness_agent.py
│   ├── alignment_agent.py
│   ├── aia_agent.py           # Algorithmic Impact Assessment
│   ├── lifecycle_agent.py     # Lifecycle phase management
│   └── orchestrator_agent.py  # Multi-agent coordinator
├── tools/                     # Analysis tools
│   ├── bias_detection_tool.py
│   ├── compliance_tool.py
│   ├── explainability_tool.py
│   ├── report_generator_tool.py
│   └── data_profiler_tool.py
├── models/                    # Pydantic data models
│   ├── system_profile.py
│   ├── principle_evaluation.py
│   ├── risk_assessment.py
│   ├── aia_report.py
│   └── lifecycle_checkpoint.py
├── orchestration/             # Orchestration layer
│   └── rai_runner.py
└── cli/                       # Command-line interface
    └── main.py
```

## AI Lifecycle Phases

The framework supports assessment across six lifecycle phases:

1. **Business Understanding** - Problem definition and stakeholder analysis
2. **Design, Data & Models** - Architecture, data collection, model development
3. **Validation & Verification** - Testing, bias auditing, compliance checks
4. **Deployment** - Production readiness, monitoring setup
5. **Operation & Monitoring** - Continuous monitoring, incident response
6. **Shutdown** - Decommissioning, data handling, documentation

## Compliance Support

Built-in compliance checking for:

- **GDPR** - Data protection, privacy rights, consent management
- **EU AI Act** - Risk classification, transparency requirements, human oversight
- **LGPD** - Brazilian data protection requirements

## Running Tests

```bash
# Run the test suite
PYTHONPATH=src python -m pytest tests/unit/rai/test_rai_system.py -v

# Or run directly
PYTHONPATH=src python tests/unit/rai/test_rai_system.py
```

## Example

See `examples/credit_scoring_profile.json` for a complete example of a high-risk credit scoring system profile.

## License

MIT License

## Contributing

Contributions are welcome! Please read the contributing guidelines before submitting pull requests.
