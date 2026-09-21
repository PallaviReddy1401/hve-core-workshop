"""Model provider contracts and adapters."""

from __future__ import annotations

from typing import Protocol

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import APIConnectionError, APIStatusError, APITimeoutError, AsyncAzureOpenAI

from smartassist.core.config import Settings
from smartassist.domain.errors import ModelUnavailableError
from smartassist.domain.models import ConversationRecord, ModelResult


class ModelProvider(Protocol):
    """Boundary for response generation."""

    async def generate(self, conversation: ConversationRecord, message: str) -> ModelResult: ...


class StubModelProvider:
    """Deterministic provider for local development and tests."""

    async def generate(self, conversation: ConversationRecord, message: str) -> ModelResult:
        """Return a safe placeholder until specialist routing is implemented."""
        return ModelResult(
            content="Your message was received. Specialist routing is not enabled yet."
        )


class AzureOpenAIModelProvider:
    """Azure OpenAI adapter for approved Foundry model deployments."""

    def __init__(self, settings: Settings) -> None:
        if settings.azure_openai_api_key:
            self._client = AsyncAzureOpenAI(
                api_key=settings.azure_openai_api_key,
                azure_endpoint=settings.azure_openai_endpoint,
                api_version=settings.azure_openai_api_version,
            )
        else:
            credential = DefaultAzureCredential()
            token_provider = get_bearer_token_provider(
                credential, "https://cognitiveservices.azure.com/.default"
            )
            self._client = AsyncAzureOpenAI(
                azure_ad_token_provider=token_provider,
                azure_endpoint=settings.azure_openai_endpoint,
                api_version=settings.azure_openai_api_version,
            )
        self._deployment = settings.azure_openai_deployment

    async def generate(self, conversation: ConversationRecord, message: str) -> ModelResult:
        """Generate a bounded foundation response through Azure OpenAI."""
        try:
            response = await self._client.responses.create(
                model=self._deployment,
                instructions=(
                    "You are the SmartAssist foundation service. Acknowledge the request "
                    "concisely without making billing, technical, or account-specific claims."
                ),
                input=message,
            )
        except APITimeoutError as exc:
            raise ModelUnavailableError("The model dependency timed out.") from exc
        except APIConnectionError as exc:
            raise ModelUnavailableError("The model dependency is unavailable.") from exc
        except APIStatusError as exc:
            raise ModelUnavailableError(
                f"The model dependency returned HTTP {exc.status_code}."
            ) from exc
        if not response.output_text:
            raise ModelUnavailableError("The model dependency returned no content.")
        return ModelResult(content=response.output_text)
