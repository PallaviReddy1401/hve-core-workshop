"""Domain exceptions and stable error metadata."""

from __future__ import annotations


class SmartAssistError(Exception):
    """Base exception for expected product failures."""

    status_code = 500
    code = "service_failure"


class ConversationNotFoundError(SmartAssistError):
    """Raised when a conversation does not exist."""

    status_code = 404
    code = "conversation_not_found"


class ConversationExpiredError(SmartAssistError):
    """Raised when a conversation has expired."""

    status_code = 410
    code = "conversation_expired"


class ConversationTerminalError(SmartAssistError):
    """Raised when a terminal conversation receives another message."""

    status_code = 409
    code = "conversation_terminal"


class IdempotencyConflictError(SmartAssistError):
    """Raised when one idempotency key is reused for different content."""

    status_code = 409
    code = "idempotency_conflict"


class ModelUnavailableError(SmartAssistError):
    """Raised when the configured model dependency is unavailable."""

    status_code = 503
    code = "model_unavailable"


class MessageTooLargeError(SmartAssistError):
    """Raised when a message exceeds the configured product limit."""

    status_code = 413
    code = "message_too_large"
