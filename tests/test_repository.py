"""Repository isolation and concurrency tests."""

from __future__ import annotations

import asyncio
from datetime import timedelta

import pytest

from smartassist.domain.errors import ConversationExpiredError
from smartassist.domain.models import (
    ConversationRecord,
    DataClassification,
    MessageRecord,
    utc_now,
)
from smartassist.infrastructure.repository import InMemoryConversationRepository


@pytest.mark.asyncio
async def test_repository_returns_defensive_copies() -> None:
    repository = InMemoryConversationRepository()
    record = ConversationRecord(
        data_classification=DataClassification.SYNTHETIC,
        expires_at=utc_now() + timedelta(minutes=5),
    )
    await repository.create(record)

    loaded = await repository.get(record.conversation_id)
    loaded.messages.append(MessageRecord(sender="customer", content="not persisted"))
    reloaded = await repository.get(record.conversation_id)

    assert reloaded.messages == []


@pytest.mark.asyncio
async def test_conversation_locks_are_isolated() -> None:
    repository = InMemoryConversationRepository()
    first = ConversationRecord(
        data_classification=DataClassification.SYNTHETIC,
        expires_at=utc_now() + timedelta(minutes=5),
    )
    second = ConversationRecord(
        data_classification=DataClassification.SYNTHETIC,
        expires_at=utc_now() + timedelta(minutes=5),
    )
    await repository.create(first)
    await repository.create(second)
    entered: list[str] = []

    async def enter_lock(record: ConversationRecord, marker: str) -> None:
        async with repository.lock(record.conversation_id):
            entered.append(marker)
            await asyncio.sleep(0.01)

    await asyncio.gather(enter_lock(first, "first"), enter_lock(second, "second"))

    assert set(entered) == {"first", "second"}


@pytest.mark.asyncio
async def test_expired_conversation_fails_explicitly() -> None:
    repository = InMemoryConversationRepository()
    record = ConversationRecord(
        data_classification=DataClassification.DEIDENTIFIED,
        expires_at=utc_now() - timedelta(seconds=1),
    )
    await repository.create(record)

    with pytest.raises(ConversationExpiredError):
        await repository.get(record.conversation_id)

