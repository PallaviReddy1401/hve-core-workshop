"""Focused specialist grounding, safety, and contract tests."""

from __future__ import annotations

from uuid import uuid4

import pytest

from smartassist.core.specialist_policy import default_specialist_policy
from smartassist.core.specialists import ModelSpecialist
from smartassist.domain.models import (
    Category,
    Disposition,
    SpecialistRequest,
    SpecialistResponse,
    SpecialistScope,
)


class ScriptedProvider:
    """Return a selected structured response and capture the grounded request."""

    def __init__(self, response: SpecialistResponse) -> None:
        self.response = response
        self.request: SpecialistRequest | None = None

    async def respond(
        self,
        request: SpecialistRequest,
        *,
        specialist_id: str,
        specialist_version: str,
        instructions: str,
        prompt_version: str,
    ) -> SpecialistResponse:
        self.request = request
        return self.response


def request(category: Category, *, contract_version: str = "1.0") -> SpecialistRequest:
    return SpecialistRequest(
        contract_version=contract_version,
        conversation_id=uuid4(),
        category=category,
        current_message="Test customer request",
        approved_evidence=["caller-injected: This must not be trusted."],
    )


def response(
    specialist_id: str,
    *,
    disposition: Disposition,
    content: str,
    evidence_references: list[str] | None = None,
    escalation_reason: str | None = None,
    policy_scope: SpecialistScope = SpecialistScope.SUPPORTED,
    contract_version: str = "1.0",
) -> SpecialistResponse:
    return SpecialistResponse(
        contract_version=contract_version,
        specialist_id=specialist_id,
        specialist_version="1.0",
        content=content,
        disposition=disposition,
        policy_scope=policy_scope,
        evidence_references=evidence_references or [],
        escalation_reason=escalation_reason,
        prompt_version="1.0",
    )


def specialist(
    category: Category, provider: ScriptedProvider, specialist_id: str
) -> ModelSpecialist:
    return ModelSpecialist(
        category,
        specialist_id,
        "Test policy instructions.",
        provider,
        response_policy=default_specialist_policy(category),
    )


@pytest.mark.asyncio
async def test_billing_policy_answer_is_grounded_in_approved_evidence() -> None:
    provider = ScriptedProvider(
        response(
            "billing",
            disposition=Disposition.ANSWERED,
            content="Payments may require processing time before they are reflected.",
            evidence_references=["billing-payment-processing-v1"],
        )
    )

    result = await specialist(Category.BILLING, provider, "billing").handle(
        request(Category.BILLING)
    )

    assert result.disposition is Disposition.ANSWERED
    assert result.evidence_references == ["billing-payment-processing-v1"]
    assert provider.request is not None
    assert provider.request.approved_evidence[0].startswith(
        "billing-payment-processing-v1:"
    )
    assert all(
        not item.startswith("caller-injected:") for item in provider.request.approved_evidence
    )


@pytest.mark.asyncio
async def test_billing_account_facts_are_removed_during_required_escalation() -> None:
    provider = ScriptedProvider(
        response(
            "billing",
            disposition=Disposition.ANSWERED,
            content="Your balance is $42 and a refund was submitted.",
            evidence_references=["billing-payment-processing-v1"],
            policy_scope=SpecialistScope.ACCOUNT_SPECIFIC,
        )
    )

    result = await specialist(Category.BILLING, provider, "billing").handle(
        request(Category.BILLING)
    )

    assert result.disposition is Disposition.ESCALATION_REQUIRED
    assert result.escalation_reason == "account_specific_billing"
    assert "$42" not in result.content
    assert "cannot access or verify account-specific billing facts" in result.content
    assert "no handoff has been initiated" in result.content


@pytest.mark.asyncio
async def test_restricted_billing_operation_is_deterministically_escalated() -> None:
    provider = ScriptedProvider(
        response(
            "billing",
            disposition=Disposition.ANSWERED,
            content="I completed the disputed-charge refund.",
            evidence_references=["billing-refund-policy-v1"],
            policy_scope=SpecialistScope.RESTRICTED_OPERATION,
        )
    )

    result = await specialist(Category.BILLING, provider, "billing").handle(
        request(Category.BILLING)
    )

    assert result.disposition is Disposition.ESCALATION_REQUIRED
    assert result.escalation_reason == "restricted_billing_operation"
    assert "cannot perform billing changes" in result.content
    assert "completed" not in result.content


@pytest.mark.asyncio
async def test_ungrounded_billing_answer_escalates_without_fabrication() -> None:
    provider = ScriptedProvider(
        response(
            "billing",
            disposition=Disposition.ANSWERED,
            content="Your latest charge was reversed.",
        )
    )

    result = await specialist(Category.BILLING, provider, "billing").handle(
        request(Category.BILLING)
    )

    assert result.disposition is Disposition.ESCALATION_REQUIRED
    assert result.escalation_reason == "approved_evidence_unavailable"
    assert "latest charge" not in result.content


@pytest.mark.asyncio
async def test_technical_specialist_asks_one_focused_diagnostic_question() -> None:
    provider = ScriptedProvider(
        response(
            "tech-support",
            disposition=Disposition.ANSWERED,
            content="What exact error appears in the affected client",
            policy_scope=SpecialistScope.NEEDS_CLARIFICATION,
        )
    )

    result = await specialist(
        Category.TECH_SUPPORT, provider, "tech-support"
    ).handle(request(Category.TECH_SUPPORT))

    assert result.disposition is Disposition.CLARIFICATION_REQUIRED
    assert result.content == (
        "To continue safely, I need one detail: "
        "What exact error appears in the affected client?"
    )
    assert result.evidence_references == []


@pytest.mark.asyncio
async def test_technical_answer_requires_approved_grounding() -> None:
    provider = ScriptedProvider(
        response(
            "tech-support",
            disposition=Disposition.ANSWERED,
            content="Record the exact error and affected client first.",
            evidence_references=["technical-connectivity-v1"],
        )
    )

    result = await specialist(
        Category.TECH_SUPPORT, provider, "tech-support"
    ).handle(request(Category.TECH_SUPPORT))

    assert result.disposition is Disposition.ANSWERED
    assert result.evidence_references == ["technical-connectivity-v1"]


@pytest.mark.asyncio
async def test_unsupported_technical_issue_has_deterministic_escalation_text() -> None:
    provider = ScriptedProvider(
        response(
            "tech-support",
            disposition=Disposition.ANSWERED,
            content="A technician has already fixed this.",
            evidence_references=["technical-connectivity-v1"],
            policy_scope=SpecialistScope.UNSUPPORTED,
        )
    )

    result = await specialist(
        Category.TECH_SUPPORT, provider, "tech-support"
    ).handle(request(Category.TECH_SUPPORT))

    assert result.disposition is Disposition.ESCALATION_REQUIRED
    assert "approved technical guidance does not cover" in result.content
    assert "already fixed" not in result.content


@pytest.mark.asyncio
async def test_general_specialist_answers_only_supported_approved_content() -> None:
    provider = ScriptedProvider(
        response(
            "general",
            disposition=Disposition.ANSWERED,
            content="SmartAssist supports billing, technical, and general assistance.",
            evidence_references=["general-smartassist-scope-v1"],
        )
    )

    result = await specialist(Category.GENERAL, provider, "general").handle(
        request(Category.GENERAL)
    )

    assert result.disposition is Disposition.ANSWERED
    assert result.evidence_references == ["general-smartassist-scope-v1"]


@pytest.mark.asyncio
async def test_general_uncertainty_is_not_converted_to_an_answer() -> None:
    provider = ScriptedProvider(
        response(
            "general",
            disposition=Disposition.ANSWERED,
            content="I will guess an answer.",
            evidence_references=["general-smartassist-scope-v1"],
            policy_scope=SpecialistScope.UNCERTAIN,
        )
    )

    result = await specialist(Category.GENERAL, provider, "general").handle(
        request(Category.GENERAL)
    )

    assert result.disposition is Disposition.ESCALATION_REQUIRED
    assert result.escalation_reason == "specialist_uncertain"
    assert "cannot safely determine" in result.content
    assert "guess" not in result.content


@pytest.mark.asyncio
async def test_specialist_contract_and_identity_are_enforced() -> None:
    provider = ScriptedProvider(
        response(
            "wrong-specialist",
            disposition=Disposition.ANSWERED,
            content="Grounded content.",
            evidence_references=["general-smartassist-scope-v1"],
        )
    )
    registered = specialist(Category.GENERAL, provider, "general")

    with pytest.raises(ValueError, match="Unsupported specialist contract version"):
        await registered.handle(request(Category.GENERAL, contract_version="2.0"))

    with pytest.raises(ValueError, match="Unexpected specialist response identity"):
        await registered.handle(request(Category.GENERAL))
