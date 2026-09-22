"""Model provider contracts and Azure OpenAI adapters."""

from __future__ import annotations

import json
from typing import Protocol

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import APIConnectionError, APIStatusError, APITimeoutError, AsyncAzureOpenAI
from pydantic import ValidationError

from smartassist.core.config import Settings
from smartassist.domain.errors import ModelUnavailableError
from smartassist.domain.models import (
    Category,
    ClassificationResult,
    ConversationRecord,
    Disposition,
    SpecialistRequest,
    SpecialistResponse,
)


class ModelProvider(Protocol):
    """Boundary for classification and specialist response generation."""

    async def classify(
        self, conversation: ConversationRecord, message: str
    ) -> ClassificationResult: ...

    async def respond(
        self,
        request: SpecialistRequest,
        *,
        specialist_id: str,
        specialist_version: str,
        instructions: str,
        prompt_version: str,
    ) -> SpecialistResponse: ...


class StubModelProvider:
    """Deterministic provider for local development and tests."""

    async def classify(
        self, conversation: ConversationRecord, message: str
    ) -> ClassificationResult:
        """Return a safe general route without keyword classification."""
        return ClassificationResult(
            category=Category.GENERAL,
            confidence=1,
            ambiguous=False,
            multi_domain=False,
            escalation_required=False,
            reason_code="local_stub",
            classifier_version="stub-1.0",
            prompt_version="stub-1.0",
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
        """Return a safe placeholder through the specialist contract."""
        return SpecialistResponse(
            specialist_id=specialist_id,
            specialist_version=specialist_version,
            content="Your message was received by SmartAssist.",
            disposition=Disposition.ANSWERED,
            prompt_version=prompt_version,
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

    async def classify(
        self, conversation: ConversationRecord, message: str
    ) -> ClassificationResult:
        """Classify a message with schema-constrained Azure OpenAI chat."""
        try:
            response = await self._client.chat.completions.create(
                model=self._deployment,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Classify the customer message for SmartAssist. Use billing only "
                            "for billing policy or account questions, tech_support for product "
                            "or service troubleshooting, and general for other supported "
                            "questions. Never use general as a fallback for uncertainty. Mark "
                            "ambiguous or multi-domain requests for clarification and sensitive "
                            "or unsafe requests for escalation. Do not include hidden reasoning."
                        ),
                    },
                    {"role": "user", "content": message},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "smartassist_classification",
                        "strict": True,
                        "schema": ClassificationResult.model_json_schema(),
                    },
                },
            )
            content = response.choices[0].message.content
            if not content:
                raise ModelUnavailableError(
                    "The classification dependency returned no content."
                )
            return ClassificationResult.model_validate_json(content)
        except (ValidationError, json.JSONDecodeError, IndexError) as exc:
            raise ModelUnavailableError(
                "The classification dependency returned an invalid result."
            ) from exc
        except (APITimeoutError, APIConnectionError, APIStatusError) as exc:
            raise self._dependency_error(exc) from exc

    async def respond(
        self,
        request: SpecialistRequest,
        *,
        specialist_id: str,
        specialist_version: str,
        instructions: str,
        prompt_version: str,
    ) -> SpecialistResponse:
        """Generate a validated specialist response through Azure OpenAI chat."""
        try:
            response = await self._client.chat.completions.create(
                model=self._deployment,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            f"{instructions} Return only the versioned SmartAssist specialist "
                            "response schema. Ask a focused clarification when required facts "
                            "are missing. Escalate when policy or missing approved evidence "
                            "prevents a safe answer. Do not claim a human handoff occurred."
                        ),
                    },
                    {"role": "user", "content": request.model_dump_json()},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "smartassist_specialist_response",
                        "strict": True,
                        "schema": SpecialistResponse.model_json_schema(),
                    },
                },
            )
            content = response.choices[0].message.content
            if not content:
                raise ModelUnavailableError("The model dependency returned no content.")
            result = SpecialistResponse.model_validate_json(content)
            return result.model_copy(
                update={
                    "specialist_id": specialist_id,
                    "specialist_version": specialist_version,
                    "prompt_version": prompt_version,
                }
            )
        except (ValidationError, json.JSONDecodeError, IndexError) as exc:
            raise ModelUnavailableError(
                "The model dependency returned an invalid specialist result."
            ) from exc
        except (APITimeoutError, APIConnectionError, APIStatusError) as exc:
            raise self._dependency_error(exc) from exc

    @staticmethod
    def _dependency_error(
        exc: APITimeoutError | APIConnectionError | APIStatusError,
    ) -> ModelUnavailableError:
        if isinstance(exc, APITimeoutError):
            return ModelUnavailableError("The model dependency timed out.")
        if isinstance(exc, APIStatusError):
            return ModelUnavailableError(
                f"The model dependency returned HTTP {exc.status_code}."
            )
        return ModelUnavailableError("The model dependency is unavailable.")
