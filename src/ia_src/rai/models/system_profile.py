"""AI System Profile model for RAI assessments."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    """Risk classification levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AISystemType(str, Enum):
    """Types of AI systems."""

    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    GENERATIVE = "generative"
    RECOMMENDATION = "recommendation"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"
    AUTONOMOUS = "autonomous"
    MULTIMODAL = "multimodal"
    OTHER = "other"


class LifecyclePhase(str, Enum):
    """AI system lifecycle phases."""

    BUSINESS_UNDERSTANDING = "business_understanding"
    DESIGN_DATA_MODELS = "design_data_models"
    VALIDATION_VERIFICATION = "validation_verification"
    DEPLOYMENT = "deployment"
    OPERATION_MONITORING = "operation_monitoring"
    SHUTDOWN = "shutdown"


class SystemProfile(BaseModel):
    """AI system metadata and characteristics for RAI assessment."""

    # Identification
    system_id: str = Field(..., description="Unique identifier for the AI system")
    name: str = Field(..., description="Human-readable system name")
    description: str = Field(..., description="System purpose and functionality")
    version: str = Field(default="1.0.0")

    # Classification
    system_type: AISystemType = Field(..., description="Type of AI system")
    risk_level: RiskLevel = Field(default=RiskLevel.MEDIUM)
    is_high_risk_eu_ai_act: bool = Field(
        default=False,
        description="Whether system is high-risk under EU AI Act",
    )

    # Technical details
    model_architecture: Optional[str] = Field(
        default=None, description="Model architecture (e.g., Transformer, CNN)"
    )
    training_data_description: Optional[str] = Field(
        default=None, description="Description of training data sources"
    )
    input_data_types: list[str] = Field(
        default_factory=list, description="Types of input data processed"
    )
    output_data_types: list[str] = Field(
        default_factory=list, description="Types of outputs generated"
    )

    # Stakeholders
    owner: str = Field(..., description="System owner/responsible party")
    developers: list[str] = Field(
        default_factory=list, description="Development team members"
    )
    operators: list[str] = Field(
        default_factory=list, description="Operations team members"
    )
    affected_populations: list[str] = Field(
        default_factory=list, description="Groups affected by system decisions"
    )

    # Lifecycle
    current_phase: LifecyclePhase = Field(
        default=LifecyclePhase.BUSINESS_UNDERSTANDING
    )
    deployment_date: Optional[datetime] = None
    last_assessment_date: Optional[datetime] = None

    # Compliance context
    applicable_regulations: list[str] = Field(
        default_factory=list,
        description="Applicable regulations (e.g., GDPR, EU AI Act, LGPD)",
    )
    certifications: list[str] = Field(
        default_factory=list, description="Relevant certifications"
    )
    industry_sector: Optional[str] = Field(
        default=None, description="Industry sector (e.g., finance, healthcare)"
    )

    # Additional context
    use_cases: list[str] = Field(
        default_factory=list, description="Specific use cases for the system"
    )
    known_limitations: list[str] = Field(
        default_factory=list, description="Known system limitations"
    )
    prohibited_uses: list[str] = Field(
        default_factory=list, description="Explicitly prohibited uses"
    )

    model_config = {"extra": "allow"}
