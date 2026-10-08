"""Configuration validation tests."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from smartassist.core.config import ModelProviderMode, Settings


def test_stub_configuration_needs_no_cloud_credentials() -> None:
    settings = Settings(model_provider=ModelProviderMode.STUB)

    assert settings.model_provider is ModelProviderMode.STUB


def test_foundry_configuration_requires_project_and_model() -> None:
    with pytest.raises(ValidationError):
        Settings(model_provider=ModelProviderMode.FOUNDRY)


def test_foundry_configuration_accepts_project_and_model() -> None:
    settings = Settings(
        model_provider=ModelProviderMode.FOUNDRY,
        foundry_project_endpoint="https://example.services.ai.azure.com/api/projects/demo",
        foundry_model_deployment_name="gpt-4o",
    )

    assert settings.model_provider is ModelProviderMode.FOUNDRY
    assert settings.foundry_model_deployment_name == "gpt-4o"
