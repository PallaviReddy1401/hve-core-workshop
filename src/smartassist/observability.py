"""Azure Monitor OpenTelemetry configuration."""

from __future__ import annotations

import logging
import os

from azure.monitor.opentelemetry import configure_azure_monitor
from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

APPLICATION_INSIGHTS_CONNECTION_STRING = "APPLICATIONINSIGHTS_CONNECTION_STRING"
LOGGER_NAME = "smartassist"


def configure_telemetry(app: FastAPI | None = None) -> bool:
    """Configure Azure Monitor when an Application Insights connection is available."""
    if not os.getenv(APPLICATION_INSIGHTS_CONNECTION_STRING):
        return False

    configure_azure_monitor(logger_name=LOGGER_NAME)
    if app is not None:
        FastAPIInstrumentor.instrument_app(app)
    logging.getLogger(LOGGER_NAME).setLevel(logging.INFO)
    return True
