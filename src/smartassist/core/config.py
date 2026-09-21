"""Typed application configuration."""

from __future__ import annotations

from enum import StrEnum
from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ModelProviderMode(StrEnum):
    """Available model provider modes."""

    STUB = "stub"
    AZURE = "azure"


class Settings(BaseSettings):
    """Environment-backed SmartAssist settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SMARTASSIST_",
        extra="ignore",
    )

    model_provider: ModelProviderMode = ModelProviderMode.STUB
    session_ttl_seconds: int = Field(default=1800, ge=60, le=86400)
    max_message_length: int = Field(default=4000, ge=1, le=32000)
    azure_openai_endpoint: str | None = None
    azure_openai_deployment: str | None = None
    azure_openai_api_version: str = "2024-10-21"
    azure_openai_api_key: str | None = None

    @model_validator(mode="after")
    def validate_azure_configuration(self) -> Settings:
        """Require endpoint and deployment when Azure mode is selected."""
        if self.model_provider is ModelProviderMode.AZURE:
            missing = [
                name
                for name, value in (
                    ("azure_openai_endpoint", self.azure_openai_endpoint),
                    ("azure_openai_deployment", self.azure_openai_deployment),
                )
                if not value
            ]
            if missing:
                raise ValueError(f"Azure model provider requires: {', '.join(missing)}")
        return self


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
