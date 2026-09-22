"""FastAPI application factory and routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID, uuid4

from fastapi import FastAPI, Header, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from smartassist.core.config import ModelProviderMode, Settings, get_settings
from smartassist.core.service import ConversationService
from smartassist.core.specialists import ModelSpecialist, SpecialistRegistry
from smartassist.domain.errors import SmartAssistError
from smartassist.domain.models import (
    Category,
    ConversationCreatedResponse,
    CreateConversationRequest,
    CustomerMessageRequest,
    ErrorDetail,
    ErrorResponse,
    HealthResponse,
    MessageResponse,
)
from smartassist.infrastructure.model_provider import (
    AzureOpenAIModelProvider,
    StubModelProvider,
)
from smartassist.infrastructure.repository import InMemoryConversationRepository


def _correlation_id(value: UUID | None) -> UUID:
    return value or uuid4()


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create a configured SmartAssist application."""
    application_settings = settings or get_settings()
    repository = InMemoryConversationRepository()
    provider = (
        AzureOpenAIModelProvider(application_settings)
        if application_settings.model_provider is ModelProviderMode.AZURE
        else StubModelProvider()
    )
    registry = SpecialistRegistry()
    registry.register(
        ModelSpecialist(
            Category.BILLING,
            "billing",
            "Provide only grounded billing-policy assistance.",
            provider,
        )
    )
    registry.register(
        ModelSpecialist(
            Category.TECH_SUPPORT,
            "tech-support",
            "Provide grounded technical troubleshooting with concise next steps.",
            provider,
        )
    )
    registry.register(
        ModelSpecialist(
            Category.GENERAL,
            "general",
            "Provide concise assistance for supported general inquiries.",
            provider,
        )
    )
    service = ConversationService(repository, provider, registry, application_settings)
    app = FastAPI(title="SmartAssist API", version="1.0.0")
    app.state.service = service

    @app.exception_handler(SmartAssistError)
    async def handle_domain_error(
        request: Request, exc: SmartAssistError
    ) -> JSONResponse:
        correlation_id = _correlation_id(_read_correlation_id(request))
        body = ErrorResponse(
            error=ErrorDetail(
                code=exc.code,
                message=str(exc),
                correlation_id=correlation_id,
            )
        )
        return JSONResponse(status_code=exc.status_code, content=body.model_dump(mode="json"))

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        correlation_id = _correlation_id(_read_correlation_id(request))
        body = ErrorResponse(
            error=ErrorDetail(
                code="invalid_request",
                message="Request validation failed.",
                correlation_id=correlation_id,
            )
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=body.model_dump(mode="json"),
        )

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse(status="healthy")

    @app.get("/ready", response_model=HealthResponse)
    async def ready() -> HealthResponse:
        return HealthResponse(status="ready")

    @app.post(
        "/api/v1/conversations",
        response_model=ConversationCreatedResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_conversation(
        body: CreateConversationRequest,
        x_correlation_id: Annotated[UUID | None, Header()] = None,
    ) -> ConversationCreatedResponse:
        correlation_id = _correlation_id(x_correlation_id)
        return await service.create_conversation(body, correlation_id)

    @app.post(
        "/api/v1/conversations/{conversation_id}/messages",
        response_model=MessageResponse,
    )
    async def process_message(
        conversation_id: UUID,
        body: CustomerMessageRequest,
        x_correlation_id: Annotated[UUID | None, Header()] = None,
        idempotency_key: Annotated[str | None, Header(max_length=128)] = None,
    ) -> MessageResponse:
        correlation_id = _correlation_id(x_correlation_id)
        return await service.process_message(
            conversation_id,
            body,
            correlation_id,
            idempotency_key,
        )

    return app


def _read_correlation_id(request: Request) -> UUID | None:
    value = request.headers.get("x-correlation-id")
    if not value:
        return None
    try:
        return UUID(value)
    except ValueError:
        return None


app = create_app()
