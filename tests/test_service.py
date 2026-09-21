"""Conversation service behavior tests."""

from __future__ import annotations

import asyncio
from datetime import timedelta
from uuid import uuid4

import pytest

from smartassist.core.config import Settings
from smartassist.core.service import ConversationService
from smartassist.domain.errors import ConversationTerminalError, ModelUnavailableError
from smartassist.domain.models import (
    ConversationRecord,
    ConversationState,
    CustomerMessageRequest,
    DataClassification,
    ModelResult,
    utc_now,
)
from smartassist.infrastructure.repository import InMemoryConversationRepository


class CoordinatedProvider:
    """Provider that exposes concurrent entry for serialization tests."""

    def __init__(self) -> None:
        self.active_calls = 0
        self.maximum_active_calls = 0

    async def generate(
        self, conversation: ConversationRecord, message: str
    ) -> ModelResult:
        self.active_calls += 1
        self.maximum_active_calls = max(self.maximum_active_calls, self.active_calls)
        await asyncio.sleep(0.01)
        self.active_calls -= 1
        return ModelResult(content=f"received:{message}")


class FailingProvider:
    """Provider that returns an explicit dependency failure."""

    async def generate(
        self, conversation: ConversationRecord, message: str
    ) -> ModelResult:
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


@pytest.mark.asyncio
async def test_same_conversation_requests_are_serialized() -> None:
    repository = InMemoryConversationRepository()
    provider = CoordinatedProvider()
    service = ConversationService(repository, provider, Settings())
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
    service = ConversationService(repository, CoordinatedProvider(), Settings())
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
    service = ConversationService(repository, FailingProvider(), Settings())
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

