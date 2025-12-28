"""Framework configuration."""

import os
from dataclasses import dataclass


@dataclass
class Settings:
    """Framework settings."""

    anthropic_api_key: str = ""
    openai_api_key: str = ""
    default_model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096
    temperature: float = 0.7

    @classmethod
    def from_env(cls) -> "Settings":
        """Load settings from environment variables."""
        return cls(
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            default_model=os.getenv("IA_DEFAULT_MODEL", "claude-sonnet-4-20250514"),
            max_tokens=int(os.getenv("IA_MAX_TOKENS", "4096")),
            temperature=float(os.getenv("IA_TEMPERATURE", "0.7")),
        )


settings = Settings.from_env()
