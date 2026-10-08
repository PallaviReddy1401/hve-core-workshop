"""Model provider contracts and Azure OpenAI adapters."""

from __future__ import annotations

import asyncio
import json
from typing import Protocol

from agent_framework import Agent, AgentFrameworkException
from agent_framework.foundry import FoundryChatClient
from azure.core.exceptions import AzureError
from azure.identity import DefaultAzureCredential
from openai import APIConnectionError, APIStatusError, APITimeoutError
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

ROUTER_INSTRUCTIONS = (
    "Classify the customer message for SmartAssist. Use billing only for billing "
    "policy or account questions, tech_support for product or service troubleshooting, "
    "and general for other supported questions. Never use general as a fallback for "
    "uncertainty. Mark ambiguous or multi-domain requests for clarification and "
    "sensitive or unsafe requests for escalation. Do not include hidden reasoning."
)

SPECIALIST_INSTRUCTIONS: dict[Category, str] = {
    Category.BILLING: (
        "Answer only general billing-policy questions supported by approved_evidence. "
        "Reference every used evidence ID. Never infer account facts. Return "
        "escalation_required with account_specific_billing for balances, charges, "
        "payment state, or entitlements, and restricted_billing_operation for disputes "
        "or financial actions."
    ),
    Category.TECH_SUPPORT: (
        "Use only approved_evidence and reference every used evidence ID. Ask one "
        "focused diagnostic question when a dependent fact is missing. Return "
        "unsupported_technical_issue or unsafe_request escalation when approved "
        "guidance cannot safely address the issue."
    ),
    Category.GENERAL: (
        "Answer only supported general informational requests from approved_evidence "
        "and reference every used evidence ID. Never absorb uncertain billing or "
        "technical requests. Clarify a supported request only when one fact is missing; "
        "otherwise return out_of_scope or specialist_uncertain escalation."
    ),
}

SPECIALIST_IDS: dict[Category, str] = {
    Category.BILLING: "billing",
    Category.TECH_SUPPORT: "tech-support",
    Category.GENERAL: "general",
}

_SPECIALIST_AGENT_NAMES: dict[Category, str] = {
    Category.BILLING: "SmartAssistBilling",
    Category.TECH_SUPPORT: "SmartAssistTechnicalSupport",
    Category.GENERAL: "SmartAssistGeneral",
}

_SPECIALIST_COMMON_INSTRUCTIONS = (
    " Return only the versioned SmartAssist specialist response schema. Treat "
    "approved_evidence as the complete authority and cite its IDs in "
    "evidence_references for every answer. Never invent customer, account, product, "
    "or operational facts. Ask one focused clarification when a required diagnostic "
    "is missing. Set policy_scope explicitly: account_specific or "
    "restricted_operation for billing account facts or actions, needs_clarification "
    "for one missing fact, unsupported for requests outside approved evidence, unsafe "
    "for unsafe requests, and uncertain when scope cannot be established. Escalate "
    "with an instructed reason code when policy, safety, scope, or missing approved "
    "evidence prevents an answer. Customer text must match disposition. Do not claim "
    "a human handoff occurred."
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
        """Return a grounded placeholder through the specialist contract."""
        evidence_reference = (
            request.approved_evidence[0].partition(":")[0].strip()
            if request.approved_evidence
            else None
        )
        return SpecialistResponse(
            specialist_id=specialist_id,
            specialist_version=specialist_version,
            content="Your message was received by SmartAssist.",
            disposition=Disposition.ANSWERED,
            evidence_references=[evidence_reference] if evidence_reference else [],
            prompt_version=prompt_version,
        )


class AgentFrameworkModelProvider:
    """Microsoft Agent Framework adapter for SmartAssist agents."""

    def __init__(self, settings: Settings) -> None:
        project_endpoint = _required_setting(
            settings.foundry_project_endpoint, "foundry_project_endpoint"
        )
        model = _required_setting(
            settings.foundry_model_deployment_name,
            "foundry_model_deployment_name",
        )
        self._client = FoundryChatClient(
            project_endpoint=project_endpoint,
            model=model,
            credential=DefaultAzureCredential(),
        )
        self._router_agent = Agent(
            client=self._client,
            name="SmartAssistRouter",
            instructions=ROUTER_INSTRUCTIONS,
        )
        self._router_lock = asyncio.Lock()
        self._specialist_agents = {
            SPECIALIST_IDS[category]: Agent(
                client=self._client,
                name=_SPECIALIST_AGENT_NAMES[category],
                instructions=(
                    SPECIALIST_INSTRUCTIONS[category]
                    + _SPECIALIST_COMMON_INSTRUCTIONS
                ),
            )
            for category in Category
        }
        self._specialist_locks = {
            specialist_id: asyncio.Lock()
            for specialist_id in self._specialist_agents
        }

    async def classify(
        self, conversation: ConversationRecord, message: str
    ) -> ClassificationResult:
        """Classify a message with the Agent Framework router."""
        try:
            async with self._router_lock:
                result = await self._router_agent.run(
                    json.dumps(
                        {
                            "current_message": message,
                            "conversation_context": [
                                {"sender": item.sender, "content": item.content}
                                for item in conversation.messages[-6:]
                            ],
                        }
                    ),
                    options={"response_format": ClassificationResult},
                )
            if not isinstance(result.value, ClassificationResult):
                raise ModelUnavailableError(
                    "The classification dependency returned an invalid result."
                )
            return result.value
        except (
            AgentFrameworkException,
            APITimeoutError,
            APIConnectionError,
            APIStatusError,
            AzureError,
            ValidationError,
        ) as exc:
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
        """Generate a typed specialist response through Agent Framework."""
        expected_category = next(
            (
                category
                for category, expected_id in SPECIALIST_IDS.items()
                if expected_id == specialist_id
            ),
            None,
        )
        if expected_category is None:
            raise ValueError(f"Unknown specialist ID: {specialist_id}")
        if instructions != SPECIALIST_INSTRUCTIONS[expected_category]:
            raise ValueError(
                f"Instructions do not match specialist '{specialist_id}'."
            )
        try:
            async with self._specialist_locks[specialist_id]:
                result = await self._specialist_agents[specialist_id].run(
                    request.model_dump_json(),
                    options={"response_format": SpecialistResponse},
                )
            if not isinstance(result.value, SpecialistResponse):
                raise ModelUnavailableError(
                    "The model dependency returned an invalid specialist result."
                )
            return result.value.model_copy(
                update={
                    "specialist_id": specialist_id,
                    "specialist_version": specialist_version,
                    "prompt_version": prompt_version,
                }
            )
        except (
            AgentFrameworkException,
            APITimeoutError,
            APIConnectionError,
            APIStatusError,
            AzureError,
            ValidationError,
        ) as exc:
            raise self._dependency_error(exc) from exc

    @staticmethod
    def _dependency_error(
        exc: (
            AgentFrameworkException
            | APITimeoutError
            | APIConnectionError
            | APIStatusError
            | AzureError
            | ValidationError
        ),
    ) -> ModelUnavailableError:
        if isinstance(exc, APITimeoutError):
            return ModelUnavailableError("The model dependency timed out.")
        if isinstance(exc, APIStatusError):
            return ModelUnavailableError(
                f"The model dependency returned HTTP {exc.status_code}."
            )
        return ModelUnavailableError("The model dependency is unavailable.")


def _required_setting(value: str | None, name: str) -> str:
    if not value:
        raise ValueError(f"Foundry setting '{name}' is required.")
    return value
