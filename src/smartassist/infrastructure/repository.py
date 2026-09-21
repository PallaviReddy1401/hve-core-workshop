"""Conversation repository contracts and in-memory implementation."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from smartassist.domain.errors import ConversationExpiredError, ConversationNotFoundError
from smartassist.domain.models import (
    ConversationRecord,
    ConversationState,
    MessageResponse,
    utc_now,
)


@dataclass(frozen=True)
class IdempotencyRecord:
    """Stored result for a logical client request."""

    fingerprint: str
    response: MessageResponse


class ConversationRepository(Protocol):
    """Persistence boundary for conversation state."""

    async def create(self, conversation: ConversationRecord) -> None: ...

    async def get(self, conversation_id: UUID) -> ConversationRecord: ...

    async def save(self, conversation: ConversationRecord) -> None: ...

    async def get_idempotency(
        self, conversation_id: UUID, key: str
    ) -> IdempotencyRecord | None: ...

    async def save_idempotency(
        self, conversation_id: UUID, key: str, record: IdempotencyRecord
    ) -> None: ...

    def lock(self, conversation_id: UUID) -> AbstractAsyncContextManager[None]: ...


class InMemoryConversationRepository:
    """Single-process conversation repository for controlled MVP validation."""

    def __init__(self) -> None:
        self._conversations: dict[UUID, ConversationRecord] = {}
        self._idempotency: dict[tuple[UUID, str], IdempotencyRecord] = {}
        self._locks: dict[UUID, asyncio.Lock] = {}
        self._map_lock = asyncio.Lock()

    async def create(self, conversation: ConversationRecord) -> None:
        """Create an isolated conversation record."""
        async with self._map_lock:
            self._conversations[conversation.conversation_id] = deepcopy(conversation)
            self._locks.setdefault(conversation.conversation_id, asyncio.Lock())

    async def get(self, conversation_id: UUID) -> ConversationRecord:
        """Get a defensive copy and enforce expiration."""
        conversation = self._conversations.get(conversation_id)
        if conversation is None:
            raise ConversationNotFoundError("Conversation was not found.")
        if self._is_expired(conversation, utc_now()):
            conversation.state = ConversationState.EXPIRED
            self._conversations[conversation_id] = conversation
            raise ConversationExpiredError("Conversation has expired.")
        return deepcopy(conversation)

    async def save(self, conversation: ConversationRecord) -> None:
        """Persist a defensive copy of an existing conversation."""
        if conversation.conversation_id not in self._conversations:
            raise ConversationNotFoundError("Conversation was not found.")
        self._conversations[conversation.conversation_id] = deepcopy(conversation)

    async def get_idempotency(
        self, conversation_id: UUID, key: str
    ) -> IdempotencyRecord | None:
        """Return a defensive copy of a prior idempotent result."""
        record = self._idempotency.get((conversation_id, key))
        return deepcopy(record) if record else None

    async def save_idempotency(
        self, conversation_id: UUID, key: str, record: IdempotencyRecord
    ) -> None:
        """Store a completed idempotent result."""
        self._idempotency[(conversation_id, key)] = deepcopy(record)

    @asynccontextmanager
    async def lock(self, conversation_id: UUID) -> AsyncIterator[None]:
        """Serialize updates for one conversation without blocking others."""
        async with self._map_lock:
            lock = self._locks.setdefault(conversation_id, asyncio.Lock())
        async with lock:
            yield

    @staticmethod
    def _is_expired(conversation: ConversationRecord, now: datetime) -> bool:
        return (
            conversation.state is not ConversationState.EXPIRED
            and now >= conversation.expires_at
        )
