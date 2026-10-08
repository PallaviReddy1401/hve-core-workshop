"""Microsoft Agent Framework provider tests."""

from __future__ import annotations

import asyncio
from datetime import timedelta
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest

from smartassist.core.config import ModelProviderMode, Settings
from smartassist.domain.errors import ModelUnavailableError
from smartassist.domain.models import (
    Category,
    ClassificationResult,
    ConversationRecord,
    DataClassification,
    Disposition,
    SpecialistRequest,
    SpecialistResponse,
    utc_now,
)
from smartassist.infrastructure import model_provider
from smartassist.infrastructure.model_provider import (
    SPECIALIST_INSTRUCTIONS,
    AgentFrameworkModelProvider,
)


class FakeAgent:
    """Capture agent construction and return configured typed values."""

    created: list[FakeAgent] = []

    def __init__(
        self,
        client: object,
        instructions: str | None = None,
        *,
        name: str | None = None,
        **_: Any,
    ) -> None:
        self.client = client
        self.instructions = instructions
        self.name = name
        self.value: object | None = None
        self.calls: list[tuple[object, object]] = []
        self.active_calls = 0
        self.maximum_active_calls = 0
        self.created.append(self)

    async def run(
        self, messages: object, *, options: object = None, **_: Any
    ) -> SimpleNamespace:
        self.calls.append((messages, options))
        self.active_calls += 1
        self.maximum_active_calls = max(self.maximum_active_calls, self.active_calls)
        await asyncio.sleep(0)
        self.active_calls -= 1
        return SimpleNamespace(value=self.value)


@pytest.fixture
def provider(
    monkeypatch: pytest.MonkeyPatch,
) -> AgentFrameworkModelProvider:
    FakeAgent.created = []
    shared_client = object()
    monkeypatch.setattr(model_provider, "Agent", FakeAgent)
    monkeypatch.setattr(
        model_provider,
        "FoundryChatClient",
        lambda **_: shared_client,
    )
    monkeypatch.setattr(model_provider, "DefaultAzureCredential", lambda: object())
    return AgentFrameworkModelProvider(
        Settings(
            model_provider=ModelProviderMode.FOUNDRY,
            foundry_project_endpoint=(
                "https://example.services.ai.azure.com/api/projects/demo"
            ),
            foundry_model_deployment_name="gpt-4o",
        )
    )


def _agent(name: str) -> FakeAgent:
    return next(agent for agent in FakeAgent.created if agent.name == name)


def _conversation() -> ConversationRecord:
    return ConversationRecord(
        data_classification=DataClassification.SYNTHETIC,
        expires_at=utc_now() + timedelta(minutes=5),
    )


def test_provider_creates_router_and_three_specialists(
    provider: AgentFrameworkModelProvider,
) -> None:
    del provider

    assert {agent.name for agent in FakeAgent.created} == {
        "SmartAssistRouter",
        "SmartAssistBilling",
        "SmartAssistTechnicalSupport",
        "SmartAssistGeneral",
    }
    assert len({id(agent.client) for agent in FakeAgent.created}) == 1


@pytest.mark.asyncio
async def test_router_returns_typed_classification(
    provider: AgentFrameworkModelProvider,
) -> None:
    expected = ClassificationResult(
        category=Category.BILLING,
        confidence=0.95,
        ambiguous=False,
        multi_domain=False,
        escalation_required=False,
        reason_code="billing_policy",
        classifier_version="test",
        prompt_version="test",
    )
    router = _agent("SmartAssistRouter")
    router.value = expected

    result = await provider.classify(_conversation(), "What is the refund policy?")

    assert result is expected
    assert router.calls[0][1] == {"response_format": ClassificationResult}


@pytest.mark.asyncio
async def test_specialist_returns_typed_contract_response(
    provider: AgentFrameworkModelProvider,
) -> None:
    billing = _agent("SmartAssistBilling")
    billing.value = SpecialistResponse(
        specialist_id="ignored-by-provider",
        specialist_version="ignored",
        content="Payments may require processing time.",
        disposition=Disposition.ANSWERED,
        evidence_references=["billing-payment-processing-v1"],
        prompt_version="ignored",
    )
    request = SpecialistRequest(
        conversation_id=uuid4(),
        category=Category.BILLING,
        current_message="How long does payment processing take?",
        approved_evidence=[
            "billing-payment-processing-v1: Payments may require processing time."
        ],
    )

    result = await provider.respond(
        request,
        specialist_id="billing",
        specialist_version="1.0",
        instructions=SPECIALIST_INSTRUCTIONS[Category.BILLING],
        prompt_version="1.0",
    )

    assert result.specialist_id == "billing"
    assert result.specialist_version == "1.0"
    assert result.prompt_version == "1.0"
    assert billing.calls[0][1] == {"response_format": SpecialistResponse}


@pytest.mark.asyncio
async def test_invalid_typed_output_is_explicit(
    provider: AgentFrameworkModelProvider,
) -> None:
    _agent("SmartAssistRouter").value = None

    with pytest.raises(
        ModelUnavailableError,
        match="classification dependency returned an invalid result",
    ):
        await provider.classify(_conversation(), "Help")


@pytest.mark.asyncio
async def test_shared_router_agent_calls_are_serialized(
    provider: AgentFrameworkModelProvider,
) -> None:
    router = _agent("SmartAssistRouter")
    router.value = ClassificationResult(
        category=Category.GENERAL,
        confidence=1,
        ambiguous=False,
        multi_domain=False,
        escalation_required=False,
        reason_code="general",
        classifier_version="test",
        prompt_version="test",
    )

    await asyncio.gather(
        provider.classify(_conversation(), "First"),
        provider.classify(_conversation(), "Second"),
    )

    assert router.maximum_active_calls == 1
