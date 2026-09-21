"""Configuration validation tests."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from smartassist.core.config import ModelProviderMode, Settings


def test_stub_configuration_needs_no_cloud_credentials() -> None:
    settings = Settings(model_provider=ModelProviderMode.STUB)

    assert settings.model_provider is ModelProviderMode.STUB


def test_azure_configuration_requires_endpoint_and_deployment() -> None:
    with pytest.raises(ValidationError):
        Settings(model_provider=ModelProviderMode.AZURE)

