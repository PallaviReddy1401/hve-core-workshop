"""Routing policy and specialist extensibility tests."""

from __future__ import annotations

from smartassist.core.routing import RoutingPolicy
from smartassist.core.specialists import SPECIALIST_CONTRACT_VERSION, SpecialistRegistry
from smartassist.domain.models import (
    Category,
    ClassificationResult,
    Disposition,
    RoutingOutcome,
    SpecialistRequest,
    SpecialistResponse,
)


def classification(**updates: object) -> ClassificationResult:
    """Create a valid classification with selected overrides."""
    values: dict[str, object] = {
        "category": Category.GENERAL,
        "confidence": 0.95,
        "ambiguous": False,
        "multi_domain": False,
        "escalation_required": False,
        "reason_code": "supported",
        "classifier_version": "test-1",
        "prompt_version": "test-1",
    }
    values.update(updates)
    return ClassificationResult.model_validate(values)


def test_low_confidence_does_not_fall_back_to_general() -> None:
    decision = RoutingPolicy(0.7).evaluate(classification(confidence=0.4))

    assert decision.outcome is RoutingOutcome.CLARIFY
    assert decision.category is None


def test_multi_domain_request_requires_clarification() -> None:
    decision = RoutingPolicy(0.7).evaluate(classification(multi_domain=True))

    assert decision.outcome is RoutingOutcome.CLARIFY
    assert decision.reason_code == "multiple_categories"


def test_policy_escalation_takes_precedence() -> None:
    decision = RoutingPolicy(0.7).evaluate(
        classification(escalation_required=True, reason_code="sensitive_operation")
    )

    assert decision.outcome is RoutingOutcome.ESCALATE
    assert decision.reason_code == "sensitive_operation"


class TestSpecialist:
    """Contract-compatible specialist used to prove registry extensibility."""

    category = Category.GENERAL
    specialist_id = "test-specialist"
    specialist_version = "1.0"
    contract_version = SPECIALIST_CONTRACT_VERSION

    async def handle(self, request: SpecialistRequest) -> SpecialistResponse:
        return SpecialistResponse(
            specialist_id=self.specialist_id,
            specialist_version=self.specialist_version,
            content="test response",
            disposition=Disposition.ANSWERED,
            prompt_version="test-1",
        )


def test_specialist_registers_without_existing_business_logic_changes() -> None:
    registry = SpecialistRegistry()
    specialist = TestSpecialist()

    registry.register(specialist)

    assert registry.resolve(Category.GENERAL) is specialist
