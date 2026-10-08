"""Typed models and file helpers for local SmartAssist evaluations."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

Category = Literal["billing", "tech_support", "general"]
Disposition = Literal[
    "answered",
    "clarification_required",
    "escalation_required",
    "resolved",
    "retryable_error",
    "failed",
]


class EvaluationCase(BaseModel):
    """One curated ground-truth case."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    scenario_type: str = Field(min_length=1)
    utterance: str = Field(min_length=1)
    expected_category: Category
    expected_disposition: Disposition
    safety_critical: bool
    grounding_required: bool
    reference_answer: str = Field(min_length=1)
    tags: list[str] = Field(min_length=1)


class Prediction(BaseModel):
    """One response collected from the SmartAssist API."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    http_status: int | None = None
    assistant_message: str | None = None
    category: Category | None = None
    disposition: Disposition | None = None
    state: str | None = None
    specialist_id: str | None = None
    error: str | None = None


class JudgeScores(BaseModel):
    """Optional LLM-as-judge scores for subjective quality dimensions."""

    model_config = ConfigDict(extra="forbid")

    relevance: int = Field(ge=1, le=5)
    helpfulness: int = Field(ge=1, le=5)
    groundedness: int = Field(ge=1, le=5)
    safety: int = Field(ge=1, le=5)
    rationale: str = Field(min_length=1, max_length=500)


class CaseResult(BaseModel):
    """Deterministic and optional judge results for one case."""

    id: str
    scenario_type: str
    expected_category: Category
    actual_category: Category | None
    expected_disposition: Disposition
    actual_disposition: Disposition | None
    routing_pass: bool
    disposition_pass: bool
    safety_pass: bool | None
    hallucination_safe_outcome_pass: bool | None
    assistant_message: str | None
    error: str | None
    judge: JudgeScores | None = None


class MetricSummary(BaseModel):
    """Metric value, numerator, denominator, target, and gate result."""

    value: float
    numerator: int
    denominator: int
    target: float | None = None
    passed: bool | None = None


class EvaluationReport(BaseModel):
    """Complete local evaluation output."""

    dataset_cases: int
    prediction_cases: int
    primary_metrics: dict[str, MetricSummary]
    secondary_metrics: dict[str, MetricSummary]
    cases: list[CaseResult]


EVALUATION_CASES = TypeAdapter(list[EvaluationCase])
PREDICTIONS = TypeAdapter(list[Prediction])


def load_cases(path: Path) -> list[EvaluationCase]:
    """Load and validate a ground-truth dataset."""
    return EVALUATION_CASES.validate_json(path.read_text(encoding="utf-8"))


def load_predictions(path: Path) -> list[Prediction]:
    """Load and validate API predictions."""
    return PREDICTIONS.validate_json(path.read_text(encoding="utf-8"))


def write_predictions(path: Path, predictions: list[Prediction]) -> None:
    """Write predictions as formatted JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        PREDICTIONS.dump_json(predictions, indent=2).decode("utf-8") + "\n",
        encoding="utf-8",
    )


def write_dataset_csv(path: Path, cases: list[EvaluationCase]) -> None:
    """Write a review-friendly CSV copy of a validated dataset."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "id",
                "scenario_type",
                "utterance",
                "expected_category",
                "expected_disposition",
                "safety_critical",
                "grounding_required",
                "reference_answer",
                "tags",
            ],
        )
        writer.writeheader()
        for case in cases:
            row = case.model_dump()
            row["tags"] = "|".join(case.tags)
            writer.writerow(row)
