"""Observability configuration tests."""

from __future__ import annotations

from fastapi import FastAPI

from smartassist import observability


def test_telemetry_is_disabled_without_connection_string(
    monkeypatch,
) -> None:
    configured = False

    def record_configuration(*, logger_name: str) -> None:
        nonlocal configured
        configured = True

    monkeypatch.delenv(observability.APPLICATION_INSIGHTS_CONNECTION_STRING, raising=False)
    monkeypatch.setattr(observability, "configure_azure_monitor", record_configuration)

    assert observability.configure_telemetry() is False
    assert configured is False


def test_telemetry_uses_smartassist_logger(
    monkeypatch,
) -> None:
    configured_loggers: list[str] = []
    instrumented_apps: list[FastAPI] = []
    app = FastAPI()

    def record_configuration(*, logger_name: str) -> None:
        configured_loggers.append(logger_name)

    def record_instrumentation(instrumented_app: FastAPI) -> None:
        instrumented_apps.append(instrumented_app)

    monkeypatch.setenv(
        observability.APPLICATION_INSIGHTS_CONNECTION_STRING,
        "InstrumentationKey=00000000-0000-0000-0000-000000000000",
    )
    monkeypatch.setattr(observability, "configure_azure_monitor", record_configuration)
    monkeypatch.setattr(
        observability.FastAPIInstrumentor,
        "instrument_app",
        record_instrumentation,
    )

    assert observability.configure_telemetry(app) is True
    assert configured_loggers == [observability.LOGGER_NAME]
    assert instrumented_apps == [app]
