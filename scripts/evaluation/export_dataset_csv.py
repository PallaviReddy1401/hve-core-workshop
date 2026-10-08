#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# SPDX-License-Identifier: MIT
"""Export the SmartAssist JSON evaluation dataset to CSV.

Usage:
    python -m scripts.evaluation.export_dataset_csv
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from scripts.evaluation.models import load_cases, write_dataset_csv

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
DEFAULT_DATASET = Path("data/evaluation/datasets/smartassist-eval-dataset.json")
DEFAULT_OUTPUT = Path("data/evaluation/datasets/smartassist-eval-dataset.csv")

logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def run(dataset: Path, output: Path) -> int:
    """Validate the JSON dataset and export it to CSV."""
    cases = load_cases(dataset)
    write_dataset_csv(output, cases)
    logger.info("Exported %d cases to %s", len(cases), output)
    return EXIT_SUCCESS


def main() -> int:
    """Run the dataset export command."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = create_parser().parse_args()
    try:
        return run(args.dataset, args.output)
    except (OSError, ValueError) as exc:
        logger.error("Dataset export failed: %s", exc)
        return EXIT_FAILURE


if __name__ == "__main__":
    sys.exit(main())
