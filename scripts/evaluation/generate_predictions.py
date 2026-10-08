#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# SPDX-License-Identifier: MIT
"""Send evaluation utterances to a running SmartAssist API.

Usage:
    python -m scripts.evaluation.generate_predictions
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import Any

import httpx

from scripts.evaluation.models import Prediction, load_cases, write_predictions

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
DEFAULT_API_URL = "http://127.0.0.1:8000"
DEFAULT_DATASET = Path("data/evaluation/datasets/smartassist-eval-dataset.json")
DEFAULT_OUTPUT = Path("data/evaluation/results/predictions.json")

logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--api-url", default=DEFAULT_API_URL)
    parser.add_argument("--timeout", type=float, default=60.0)
    return parser


async def _predict_case(
    client: httpx.AsyncClient, api_url: str, case_id: str, utterance: str
) -> Prediction:
    create_response = await client.post(
        f"{api_url}/api/v1/conversations",
        json={"data_classification": "synthetic"},
    )
    if create_response.is_error:
        return _error_prediction(case_id, create_response)

    conversation_id = _required_string(create_response.json(), "conversation_id")
    message_response = await client.post(
        f"{api_url}/api/v1/conversations/{conversation_id}/messages",
        headers={"Idempotency-Key": f"eval-{case_id}"},
        json={"content": utterance},
    )
    if message_response.is_error:
        return _error_prediction(case_id, message_response)

    body = message_response.json()
    return Prediction(
        id=case_id,
        http_status=message_response.status_code,
        assistant_message=_required_string(body, "assistant_message"),
        category=_required_string(body, "category"),
        disposition=_required_string(body, "disposition"),
        state=_required_string(body, "state"),
        specialist_id=_required_string(body, "specialist_id"),
    )


def _required_string(body: dict[str, Any], field: str) -> str:
    value = body.get(field)
    if not isinstance(value, str) or not value:
        raise ValueError(f"API response field '{field}' must be a non-empty string.")
    return value


def _error_prediction(case_id: str, response: httpx.Response) -> Prediction:
    return Prediction(
        id=case_id,
        http_status=response.status_code,
        error=f"API request failed: {response.text}",
    )


async def run(
    dataset: Path,
    output: Path,
    api_url: str,
    request_timeout: float,
) -> int:
    """Collect one isolated API prediction for every dataset case."""
    cases = load_cases(dataset)
    predictions: list[Prediction] = []
    async with httpx.AsyncClient(timeout=request_timeout) as client:
        for index, case in enumerate(cases, start=1):
            prediction = await _predict_case(
                client, api_url.rstrip("/"), case.id, case.utterance
            )
            predictions.append(prediction)
            logger.info("Collected prediction %d/%d: %s", index, len(cases), case.id)

    write_predictions(output, predictions)
    failed = sum(prediction.error is not None for prediction in predictions)
    logger.info("Wrote %d predictions to %s (%d API failures)", len(cases), output, failed)
    return EXIT_FAILURE if failed else EXIT_SUCCESS


def main() -> int:
    """Run prediction collection."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = create_parser().parse_args()
    try:
        return asyncio.run(
            run(args.dataset, args.output, args.api_url, args.timeout)
        )
    except (OSError, ValueError, httpx.HTTPError) as exc:
        logger.error("Prediction collection failed: %s", exc)
        return EXIT_FAILURE


if __name__ == "__main__":
    sys.exit(main())
