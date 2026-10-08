"""Local evaluation harness tests."""

from __future__ import annotations

from pathlib import Path

from scripts.evaluation.models import (
    EvaluationCase,
    Prediction,
    load_cases,
    write_dataset_csv,
)
from scripts.evaluation.run_evaluation import score_predictions

DATASET_PATH = Path("data/evaluation/datasets/smartassist-eval-dataset.json")


def test_curated_dataset_has_required_coverage() -> None:
    cases = load_cases(DATASET_PATH)

    assert len(cases) == 45
    assert len({case.id for case in cases}) == len(cases)
    assert {case.expected_category for case in cases} == {
        "billing",
        "tech_support",
        "general",
    }
    assert {case.expected_disposition for case in cases} == {
        "answered",
        "clarification_required",
        "escalation_required",
    }
    assert sum(case.safety_critical for case in cases) >= 15
    assert {"easy", "hard", "ambiguous", "adversarial", "escalation"}.issubset(
        {case.scenario_type for case in cases}
    )


def test_perfect_predictions_pass_every_release_gate() -> None:
    cases = load_cases(DATASET_PATH)
    predictions = [
        Prediction(
            id=case.id,
            http_status=200,
            assistant_message=case.reference_answer,
            category=case.expected_category,
            disposition=case.expected_disposition,
            state="active",
            specialist_id="test",
        )
        for case in cases
    ]

    report = score_predictions(cases, predictions)

    assert all(metric.passed for metric in report.primary_metrics.values())
    assert report.secondary_metrics["disposition_accuracy"].value == 1.0
    assert report.secondary_metrics["api_success_rate"].value == 1.0


def test_missing_prediction_is_an_explicit_failure() -> None:
    case = EvaluationCase(
        id="missing-001",
        scenario_type="easy",
        utterance="What can you do?",
        expected_category="general",
        expected_disposition="answered",
        safety_critical=False,
        grounding_required=True,
        reference_answer="Describe supported assistance.",
        tags=["general"],
    )

    report = score_predictions([case], [])

    assert report.primary_metrics["routing_accuracy"].value == 0
    assert report.primary_metrics["hallucination_safe_outcome_rate"].value == 0
    assert report.cases[0].error == "Missing prediction."


def test_csv_export_preserves_all_cases(tmp_path: Path) -> None:
    cases = load_cases(DATASET_PATH)
    output = tmp_path / "dataset.csv"

    write_dataset_csv(output, cases)

    assert len(output.read_text(encoding="utf-8").splitlines()) == len(cases) + 1
