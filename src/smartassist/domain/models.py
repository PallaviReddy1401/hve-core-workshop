"""Conversation domain and API models."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


def utc_now() -> datetime:
    """Return the current UTC time."""
    return datetime.now(UTC)


class ConversationState(StrEnum):
    """Supported MVP conversation states."""

    ACTIVE = "active"
    AWAITING_CLARIFICATION = "awaiting_clarification"
    ESCALATION_REQUIRED = "escalation_required"
    RESOLVED = "resolved"
    FAILED = "failed"
    EXPIRED = "expired"


class Disposition(StrEnum):
    """Supported message dispositions."""

    ANSWERED = "answered"
    CLARIFICATION_REQUIRED = "clarification_required"
    ESCALATION_REQUIRED = "escalation_required"
    RESOLVED = "resolved"
    RETRYABLE_ERROR = "retryable_error"
    FAILED = "failed"


class Category(StrEnum):
    """Initial category values."""

    BILLING = "billing"
    TECH_SUPPORT = "tech_support"
    GENERAL = "general"


class DataClassification(StrEnum):
    """Data classifications accepted by the controlled MVP."""

    SYNTHETIC = "synthetic"
    DEIDENTIFIED = "deidentified"


class CreateConversationRequest(BaseModel):
    """Request to create an isolated conversation."""

    model_config = ConfigDict(extra="forbid")

    data_classification: DataClassification


class CustomerMessageRequest(BaseModel):
    """Customer message submitted to an existing conversation."""

    model_config = ConfigDict(extra="forbid")

    content: str = Field(min_length=1, max_length=32000)

    @field_validator("content")
    @classmethod
    def reject_blank_content(cls, value: str) -> str:
        """Reject messages containing only whitespace."""
        if not value.strip():
            raise ValueError("Message content must not be blank.")
        return value


class MessageRecord(BaseModel):
    """Stored conversation message."""

    message_id: UUID = Field(default_factory=uuid4)
    sender: str
    content: str
    timestamp: datetime = Field(default_factory=utc_now)


class ConversationRecord(BaseModel):
    """Authoritative MVP conversation record."""

    conversation_id: UUID = Field(default_factory=uuid4)
    state: ConversationState = ConversationState.ACTIVE
    data_classification: DataClassification
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    expires_at: datetime
    messages: list[MessageRecord] = Field(default_factory=list)


class ConversationCreatedResponse(BaseModel):
    """Response returned after conversation creation."""

    conversation_id: UUID
    state: ConversationState
    created_at: datetime
    expires_at: datetime
    correlation_id: UUID


class MessageResponse(BaseModel):
    """Typed response returned for a processed message."""

    conversation_id: UUID
    assistant_message: str
    state: ConversationState
    disposition: Disposition
    category: Category
    specialist_id: str
    message_id: UUID
    timestamp: datetime
    correlation_id: UUID


class ModelResult(BaseModel):
    """Typed result returned by a model provider."""

    content: str
    state: ConversationState = ConversationState.ACTIVE
    disposition: Disposition = Disposition.ANSWERED
    category: Category = Category.GENERAL
    specialist_id: str = "foundation-stub"


class ErrorDetail(BaseModel):
    """Stable API error payload."""

    code: str
    message: str
    correlation_id: UUID


class ErrorResponse(BaseModel):
    """API error response."""

    error: ErrorDetail


class HealthResponse(BaseModel):
    """Health endpoint response."""

    status: str
    service: str = "smartassist"
