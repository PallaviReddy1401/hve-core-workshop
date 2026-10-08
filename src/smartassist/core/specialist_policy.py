"""Approved MVP evidence and deterministic specialist response policy."""

from __future__ import annotations

from dataclasses import dataclass

from smartassist.domain.models import (
    Category,
    Disposition,
    SpecialistRequest,
    SpecialistResponse,
    SpecialistScope,
)

APPROVED_EVIDENCE: dict[Category, tuple[str, ...]] = {
    Category.BILLING: (
        "billing-payment-processing-v1: Payments may require processing time before "
        "a completed payment is reflected.",
        "billing-refund-policy-v1: Refund eligibility is governed by the published "
        "terms for the purchased service.",
    ),
    Category.TECH_SUPPORT: (
        "technical-connectivity-v1: For a connectivity issue, first record the exact "
        "error, affected client, and whether the service status is healthy.",
        "technical-client-recovery-v1: After recording diagnostics, retry the request "
        "once and restart the affected client before further troubleshooting.",
    ),
    Category.GENERAL: (
        "general-smartassist-scope-v1: SmartAssist provides supported billing-policy, "
        "technical troubleshooting, and general product-information assistance.",
        "general-privacy-v1: SmartAssist MVP accepts only synthetic or deidentified "
        "conversation data.",
    ),
}

_ALLOWED_ESCALATION_REASONS: dict[Category, frozenset[str]] = {
    Category.BILLING: frozenset(
        {
            "account_specific_billing",
            "restricted_billing_operation",
            "approved_evidence_unavailable",
            "unsafe_request",
        }
    ),
    Category.TECH_SUPPORT: frozenset(
        {
            "unsupported_technical_issue",
            "approved_evidence_unavailable",
            "unsafe_request",
        }
    ),
    Category.GENERAL: frozenset(
        {
            "out_of_scope",
            "specialist_uncertain",
            "approved_evidence_unavailable",
            "unsafe_request",
        }
    ),
}

_ESCALATION_MESSAGES: dict[str, str] = {
    "account_specific_billing": (
        "I cannot access or verify account-specific billing facts. Human support is "
        "required; no handoff has been initiated."
    ),
    "restricted_billing_operation": (
        "I cannot perform billing changes, disputes, payments, refunds, or other "
        "financial actions. Human support is required; no handoff has been initiated."
    ),
    "unsupported_technical_issue": (
        "The approved technical guidance does not cover this issue. Human support is "
        "required; no handoff has been initiated."
    ),
    "out_of_scope": (
        "This request is outside the approved general-assistance scope. Human support "
        "is required; no handoff has been initiated."
    ),
    "specialist_uncertain": (
        "I cannot safely determine that this is a supported general request. Human "
        "support is required; no handoff has been initiated."
    ),
    "unsafe_request": (
        "I cannot safely assist with this request. Human support is required; no "
        "handoff has been initiated."
    ),
    "approved_evidence_unavailable": (
        "I do not have approved evidence to answer this request. Human support is "
        "required; no handoff has been initiated."
    ),
}


def _evidence_id(evidence: str) -> str:
    return evidence.partition(":")[0].strip()


@dataclass(frozen=True)
class SpecialistResponsePolicy:
    """Prepare grounded requests and normalize responses to safe dispositions."""

    category: Category
    approved_evidence: tuple[str, ...]

    def prepare(self, request: SpecialistRequest) -> SpecialistRequest:
        """Replace caller-supplied evidence with the approved category package."""
        return request.model_copy(update={"approved_evidence": list(self.approved_evidence)})

    def enforce(self, response: SpecialistResponse) -> SpecialistResponse:
        """Apply evidence, escalation, and customer-text invariants."""
        if response.policy_scope is SpecialistScope.NEEDS_CLARIFICATION:
            return self._clarification(response)
        if response.disposition is Disposition.CLARIFICATION_REQUIRED:
            return self._clarification(response)
        forced_reason = self._forced_escalation_reason(response.policy_scope)
        if forced_reason:
            return self._escalation(response, forced_reason)
        if response.disposition is Disposition.ESCALATION_REQUIRED:
            return self._escalation(response, response.escalation_reason)
        if response.disposition in {Disposition.ANSWERED, Disposition.RESOLVED}:
            approved_ids = {_evidence_id(item) for item in self.approved_evidence}
            references = set(response.evidence_references)
            if not references or not references.issubset(approved_ids):
                return self._escalation(response, "approved_evidence_unavailable")
            return response.model_copy(update={"escalation_reason": None})
        if response.disposition is Disposition.RETRYABLE_ERROR:
            return response.model_copy(
                update={
                    "content": "I could not complete this request. Please try again.",
                    "evidence_references": [],
                    "escalation_reason": None,
                }
            )
        return response.model_copy(
            update={
                "content": "I could not complete this request.",
                "evidence_references": [],
                "escalation_reason": None,
            }
        )

    def _forced_escalation_reason(self, scope: SpecialistScope) -> str | None:
        if scope is SpecialistScope.UNSAFE:
            return "unsafe_request"
        if self.category is Category.BILLING:
            if scope is SpecialistScope.ACCOUNT_SPECIFIC:
                return "account_specific_billing"
            if scope is SpecialistScope.RESTRICTED_OPERATION:
                return "restricted_billing_operation"
            if scope in {SpecialistScope.UNSUPPORTED, SpecialistScope.UNCERTAIN}:
                return "approved_evidence_unavailable"
        if self.category is Category.TECH_SUPPORT:
            if scope is not SpecialistScope.SUPPORTED:
                return "unsupported_technical_issue"
        if self.category is Category.GENERAL:
            if scope in {
                SpecialistScope.ACCOUNT_SPECIFIC,
                SpecialistScope.RESTRICTED_OPERATION,
                SpecialistScope.UNSUPPORTED,
            }:
                return "out_of_scope"
            if scope is SpecialistScope.UNCERTAIN:
                return "specialist_uncertain"
        return None

    def _clarification(self, response: SpecialistResponse) -> SpecialistResponse:
        return response.model_copy(
            update={
                "content": self._clarification_text(response.content),
                "disposition": Disposition.CLARIFICATION_REQUIRED,
                "evidence_references": [],
                "escalation_reason": None,
            }
        )

    def _escalation(
        self, response: SpecialistResponse, requested_reason: str | None
    ) -> SpecialistResponse:
        allowed_reasons = _ALLOWED_ESCALATION_REASONS[self.category]
        reason = (
            requested_reason
            if requested_reason in allowed_reasons
            else "approved_evidence_unavailable"
        )
        return response.model_copy(
            update={
                "content": _ESCALATION_MESSAGES[reason],
                "disposition": Disposition.ESCALATION_REQUIRED,
                "evidence_references": [],
                "escalation_reason": reason,
            }
        )

    @staticmethod
    def _clarification_text(content: str) -> str:
        question = content.strip()
        if not question.endswith("?"):
            question = f"{question.rstrip('.')}?"
        return f"To continue safely, I need one detail: {question}"


def default_specialist_policy(category: Category) -> SpecialistResponsePolicy:
    """Build the immutable MVP policy for a registered category."""
    return SpecialistResponsePolicy(category, APPROVED_EVIDENCE[category])
