"""Conversation application service."""

from __future__ import annotations

from datetime import timedelta
from hashlib import sha256
from uuid import UUID

from smartassist.core.config import Settings
from smartassist.core.routing import RoutingPolicy
from smartassist.core.specialists import SpecialistRegistry
from smartassist.domain.errors import (
    ConversationTerminalError,
    IdempotencyConflictError,
    MessageTooLargeError,
)
from smartassist.domain.models import (
    Category,
    ConversationCreatedResponse,
    ConversationRecord,
    ConversationState,
    CreateConversationRequest,
    CustomerMessageRequest,
    Disposition,
    MessageRecord,
    MessageResponse,
    ModelResult,
    RoutingOutcome,
    SpecialistRequest,
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
        specialist_registry: SpecialistRegistry,
        settings: Settings,
    ) -> None:
        self._repository = repository
        self._model_provider = model_provider
        self._specialist_registry = specialist_registry
        self._routing_policy = RoutingPolicy(settings.routing_minimum_confidence)
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
            classification = await self._model_provider.classify(
                conversation, request.content
            )
            decision = self._routing_policy.evaluate(classification)
            if decision.outcome is RoutingOutcome.CLARIFY:
                result = ModelResult(
                    content=decision.customer_message
                    or "Could you provide more detail about your request?",
                    state=ConversationState.AWAITING_CLARIFICATION,
                    disposition=Disposition.CLARIFICATION_REQUIRED,
                    category=classification.category or Category.GENERAL,
                    specialist_id="routing-policy",
                )
            elif decision.outcome is RoutingOutcome.ESCALATE:
                result = ModelResult(
                    content=decision.customer_message
                    or "Human support is required for this request.",
                    state=ConversationState.ESCALATION_REQUIRED,
                    disposition=Disposition.ESCALATION_REQUIRED,
                    category=classification.category or Category.GENERAL,
                    specialist_id="routing-policy",
                )
            else:
                if decision.category is None:
                    raise RuntimeError("A routed decision must include a category.")
                specialist = self._specialist_registry.resolve(decision.category)
                specialist_response = await specialist.handle(
                    SpecialistRequest(
                        conversation_id=conversation.conversation_id,
                        category=decision.category,
                        current_message=request.content,
                        conversation_context=[
                            item.content for item in conversation.messages[-6:]
                        ],
                        request_metadata={
                            "correlation_id": str(correlation_id),
                            "classifier_version": classification.classifier_version,
                            "classifier_prompt_version": classification.prompt_version,
                            "routing_reason": decision.reason_code,
                        },
                    )
                )
                result = ModelResult(
                    content=specialist_response.content,
                    state=_state_for_disposition(specialist_response.disposition),
                    disposition=specialist_response.disposition,
                    category=decision.category,
                    specialist_id=(
                        f"{specialist_response.specialist_id}:"
                        f"{specialist_response.specialist_version}"
                    ),
                )
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


def _state_for_disposition(disposition: Disposition) -> ConversationState:
    if disposition is Disposition.CLARIFICATION_REQUIRED:
        return ConversationState.AWAITING_CLARIFICATION
    if disposition is Disposition.ESCALATION_REQUIRED:
        return ConversationState.ESCALATION_REQUIRED
    if disposition is Disposition.RESOLVED:
        return ConversationState.RESOLVED
    if disposition in {Disposition.RETRYABLE_ERROR, Disposition.FAILED}:
        return ConversationState.FAILED
    return ConversationState.ACTIVE
