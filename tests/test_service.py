"""Conversation service behavior tests."""

from __future__ import annotations

import asyncio
from datetime import timedelta
from uuid import uuid4

import pytest

from smartassist.core.config import Settings
from smartassist.core.service import ConversationService
from smartassist.core.specialists import ModelSpecialist, SpecialistRegistry
from smartassist.domain.errors import ConversationTerminalError, ModelUnavailableError
from smartassist.domain.models import (
    Category,
    ClassificationResult,
    ConversationRecord,
    ConversationState,
    CustomerMessageRequest,
    DataClassification,
    Disposition,
    SpecialistRequest,
    SpecialistResponse,
    utc_now,
)
from smartassist.infrastructure.repository import InMemoryConversationRepository


class CoordinatedProvider:
    """Provider that exposes concurrent entry for serialization tests."""

    def __init__(self) -> None:
        self.active_calls = 0
        self.maximum_active_calls = 0

    async def classify(
        self, conversation: ConversationRecord, message: str
    ) -> ClassificationResult:
        return ClassificationResult(
            category=Category.GENERAL,
            confidence=1,
            ambiguous=False,
            multi_domain=False,
            escalation_required=False,
            reason_code="test",
            classifier_version="test",
            prompt_version="test",
        )

    async def respond(
        self,
        request: SpecialistRequest,
        *,
        specialist_id: str,
        specialist_version: str,
        instructions: str,
        prompt_version: str,
    ) -> SpecialistResponse:
        self.active_calls += 1
        self.maximum_active_calls = max(self.maximum_active_calls, self.active_calls)
        await asyncio.sleep(0.01)
        self.active_calls -= 1
        return SpecialistResponse(
            specialist_id=specialist_id,
            specialist_version=specialist_version,
            content=f"received:{request.current_message}",
            disposition=Disposition.ANSWERED,
            prompt_version=prompt_version,
        )


class FailingProvider:
    """Provider that returns an explicit dependency failure."""

    async def classify(
        self, conversation: ConversationRecord, message: str
    ) -> ClassificationResult:
        raise ModelUnavailableError("Model unavailable.")

    async def respond(
        self,
        request: SpecialistRequest,
        *,
        specialist_id: str,
        specialist_version: str,
        instructions: str,
        prompt_version: str,
    ) -> SpecialistResponse:
        raise ModelUnavailableError("Model unavailable.")


async def create_record(
    repository: InMemoryConversationRepository,
    *,
    state: ConversationState = ConversationState.ACTIVE,
) -> ConversationRecord:
    """Create a test conversation record."""
    record = ConversationRecord(
        data_classification=DataClassification.SYNTHETIC,
        state=state,
        expires_at=utc_now() + timedelta(minutes=5),
    )
    await repository.create(record)
    return record


def create_registry(provider: CoordinatedProvider | FailingProvider) -> SpecialistRegistry:
    """Create the default test specialist registry."""
    registry = SpecialistRegistry()
    for category in Category:
        registry.register(
            ModelSpecialist(
                category,
                f"{category.value}-test",
                "Test specialist.",
                provider,
            )
        )
    return registry


@pytest.mark.asyncio
async def test_same_conversation_requests_are_serialized() -> None:
    repository = InMemoryConversationRepository()
    provider = CoordinatedProvider()
    service = ConversationService(
        repository, provider, create_registry(provider), Settings()
    )
    record = await create_record(repository)

    await asyncio.gather(
        service.process_message(
            record.conversation_id,
            CustomerMessageRequest(content="one"),
            uuid4(),
            None,
        ),
        service.process_message(
            record.conversation_id,
            CustomerMessageRequest(content="two"),
            uuid4(),
            None,
        ),
    )

    assert provider.maximum_active_calls == 1
    stored = await repository.get(record.conversation_id)
    assert len(stored.messages) == 4


@pytest.mark.asyncio
async def test_terminal_conversation_rejects_new_message() -> None:
    repository = InMemoryConversationRepository()
    provider = CoordinatedProvider()
    service = ConversationService(
        repository, provider, create_registry(provider), Settings()
    )
    record = await create_record(repository, state=ConversationState.RESOLVED)

    with pytest.raises(ConversationTerminalError):
        await service.process_message(
            record.conversation_id,
            CustomerMessageRequest(content="continue"),
            uuid4(),
            None,
        )


@pytest.mark.asyncio
async def test_provider_failure_does_not_persist_messages() -> None:
    repository = InMemoryConversationRepository()
    provider = FailingProvider()
    service = ConversationService(
        repository, provider, create_registry(provider), Settings()
    )
    record = await create_record(repository)

    with pytest.raises(ModelUnavailableError):
        await service.process_message(
            record.conversation_id,
            CustomerMessageRequest(content="fail"),
            uuid4(),
            None,
        )

    stored = await repository.get(record.conversation_id)
    assert stored.messages == []
