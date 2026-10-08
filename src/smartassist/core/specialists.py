"""Versioned specialist contract, model-backed implementation, and registry."""

from __future__ import annotations

from typing import Protocol

from smartassist.core.specialist_policy import SpecialistResponsePolicy
from smartassist.domain.models import Category, SpecialistRequest, SpecialistResponse

SPECIALIST_CONTRACT_VERSION = "1.0"


class SpecialistProvider(Protocol):
    """Model boundary used by registered specialists."""

    async def respond(
        self,
        request: SpecialistRequest,
        *,
        specialist_id: str,
        specialist_version: str,
        instructions: str,
        prompt_version: str,
    ) -> SpecialistResponse: ...


class Specialist(Protocol):
    """Contract implemented by every specialist."""

    category: Category
    specialist_id: str
    specialist_version: str
    contract_version: str

    async def handle(self, request: SpecialistRequest) -> SpecialistResponse: ...


class ModelSpecialist:
    """Specialist that delegates bounded generation to the model provider."""

    contract_version = SPECIALIST_CONTRACT_VERSION

    def __init__(
        self,
        category: Category,
        specialist_id: str,
        instructions: str,
        provider: SpecialistProvider,
        *,
        specialist_version: str = "1.0",
        prompt_version: str = "1.0",
        response_policy: SpecialistResponsePolicy | None = None,
    ) -> None:
        self.category = category
        self.specialist_id = specialist_id
        self.specialist_version = specialist_version
        self._instructions = instructions
        self._provider = provider
        self._prompt_version = prompt_version
        self._response_policy = response_policy

    async def handle(self, request: SpecialistRequest) -> SpecialistResponse:
        """Validate the request contract and return a validated response."""
        if request.contract_version != self.contract_version:
            raise ValueError(
                f"Unsupported specialist contract version: {request.contract_version}"
            )
        if request.category is not self.category:
            raise ValueError(
                f"Specialist '{self.specialist_id}' does not support "
                f"'{request.category.value}'."
            )
        prepared_request = (
            self._response_policy.prepare(request) if self._response_policy else request
        )
        response = await self._provider.respond(
            prepared_request,
            specialist_id=self.specialist_id,
            specialist_version=self.specialist_version,
            instructions=self._instructions,
            prompt_version=self._prompt_version,
        )
        if response.contract_version != self.contract_version:
            raise ValueError(
                f"Unsupported specialist response version: {response.contract_version}"
            )
        if response.specialist_id != self.specialist_id:
            raise ValueError(
                f"Unexpected specialist response identity: {response.specialist_id}"
            )
        if response.specialist_version != self.specialist_version:
            raise ValueError(
                f"Unexpected specialist response version: {response.specialist_version}"
            )
        if self._response_policy:
            response = self._response_policy.enforce(response)
        return response


class SpecialistRegistry:
    """Resolve category-specific specialists without business-logic coupling."""

    def __init__(self) -> None:
        self._specialists: dict[Category, Specialist] = {}

    def register(self, specialist: Specialist) -> None:
        """Register one contract-compatible specialist for a category."""
        if specialist.contract_version != SPECIALIST_CONTRACT_VERSION:
            raise ValueError(
                f"Unsupported specialist contract version: {specialist.contract_version}"
            )
        if specialist.category in self._specialists:
            raise ValueError(
                f"A specialist is already registered for '{specialist.category.value}'."
            )
        self._specialists[specialist.category] = specialist

    def resolve(self, category: Category) -> Specialist:
        """Resolve the registered specialist for a category."""
        try:
            return self._specialists[category]
        except KeyError as exc:
            raise ValueError(
                f"No specialist is registered for '{category.value}'."
            ) from exc
