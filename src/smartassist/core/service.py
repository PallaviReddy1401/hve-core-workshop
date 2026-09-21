"""Conversation application service."""

from __future__ import annotations

from datetime import timedelta
from hashlib import sha256
from uuid import UUID

from smartassist.core.config import Settings
from smartassist.domain.errors import (
    ConversationTerminalError,
    IdempotencyConflictError,
    MessageTooLargeError,
)
from smartassist.domain.models import (
    ConversationCreatedResponse,
    ConversationRecord,
    ConversationState,
    CreateConversationRequest,
    CustomerMessageRequest,
    MessageRecord,
    MessageResponse,
    utc_now,
)
from smartassist.infrastructure.model_provider import ModelProvider
from smartassist.infrastructure.repository import ConversationRepository, IdempotencyRecord

TERMINAL_STATES = {
    ConversationState.ESCALATION_REQUIRED,
    ConversationState.RESOLVED,
    ConversationState.FAILED,
    ConversationState.EXPIRED,
}


class ConversationService:
    """Coordinate conversation lifecycle, storage, and model execution."""

    def __init__(
        self,
        repository: ConversationRepository,
        model_provider: ModelProvider,
        settings: Settings,
    ) -> None:
        self._repository = repository
        self._model_provider = model_provider
        self._settings = settings

    async def create_conversation(
        self, request: CreateConversationRequest, correlation_id: UUID
    ) -> ConversationCreatedResponse:
        """Create a new isolated conversation."""
        now = utc_now()
        conversation = ConversationRecord(
            data_classification=request.data_classification,
            expires_at=now + timedelta(seconds=self._settings.session_ttl_seconds),
            created_at=now,
            updated_at=now,
        )
        await self._repository.create(conversation)
        return ConversationCreatedResponse(
            conversation_id=conversation.conversation_id,
            state=conversation.state,
            created_at=conversation.created_at,
            expires_at=conversation.expires_at,
            correlation_id=correlation_id,
        )

    async def process_message(
        self,
        conversation_id: UUID,
        request: CustomerMessageRequest,
        correlation_id: UUID,
        idempotency_key: str | None,
    ) -> MessageResponse:
        """Process one logical message under a conversation-scoped lock."""
        if len(request.content) > self._settings.max_message_length:
            raise MessageTooLargeError(
                f"Message exceeds the {self._settings.max_message_length}-character limit."
            )
        fingerprint = sha256(request.content.encode("utf-8")).hexdigest()
        async with self._repository.lock(conversation_id):
            conversation = await self._repository.get(conversation_id)
            if conversation.state in TERMINAL_STATES:
                raise ConversationTerminalError(
                    f"Conversation is in terminal state '{conversation.state.value}'."
                )
            if idempotency_key:
                prior = await self._repository.get_idempotency(
                    conversation_id, idempotency_key
                )
                if prior:
                    if prior.fingerprint != fingerprint:
                        raise IdempotencyConflictError(
                            "Idempotency key was already used for different content."
                        )
                    return prior.response

            customer_message = MessageRecord(sender="customer", content=request.content)
            result = await self._model_provider.generate(conversation, request.content)
            assistant_message = MessageRecord(sender="assistant", content=result.content)
            now = utc_now()
            conversation.messages.extend([customer_message, assistant_message])
            conversation.state = result.state
            conversation.updated_at = now
            await self._repository.save(conversation)

            response = MessageResponse(
                conversation_id=conversation_id,
                assistant_message=result.content,
                state=result.state,
                disposition=result.disposition,
                category=result.category,
                specialist_id=result.specialist_id,
                message_id=assistant_message.message_id,
                timestamp=assistant_message.timestamp,
                correlation_id=correlation_id,
            )
            if idempotency_key:
                await self._repository.save_idempotency(
                    conversation_id,
                    idempotency_key,
                    IdempotencyRecord(fingerprint=fingerprint, response=response),
                )
            return response
