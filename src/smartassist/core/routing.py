"""Typed classification and deterministic routing policy."""

from __future__ import annotations

from smartassist.domain.models import (
    ClassificationResult,
    RoutingDecision,
    RoutingOutcome,
)


class RoutingPolicy:
    """Apply deterministic gates after model-assisted classification."""

    def __init__(self, minimum_confidence: float) -> None:
        self._minimum_confidence = minimum_confidence

    def evaluate(self, classification: ClassificationResult) -> RoutingDecision:
        """Return one approved route, clarification, or escalation outcome."""
        if classification.escalation_required:
            return RoutingDecision(
                outcome=RoutingOutcome.ESCALATE,
                reason_code=classification.reason_code,
                customer_message=(
                    "I cannot safely complete this request automatically. "
                    "Human support is required."
                ),
            )
        if classification.multi_domain:
            return RoutingDecision(
                outcome=RoutingOutcome.CLARIFY,
                reason_code="multiple_categories",
                customer_message=classification.clarification_question
                or "Which part should we address first: billing or technical support?",
            )
        if (
            classification.category is None
            or classification.ambiguous
            or classification.confidence < self._minimum_confidence
        ):
            return RoutingDecision(
                outcome=RoutingOutcome.CLARIFY,
                reason_code="classification_uncertain",
                customer_message=classification.clarification_question
                or "Could you provide more detail so I can route your request correctly?",
            )
        return RoutingDecision(
            outcome=RoutingOutcome.ROUTE,
            category=classification.category,
            reason_code=classification.reason_code,
        )
