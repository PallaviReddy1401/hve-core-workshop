---
title: SmartAssist Evaluation Baseline
description: First local SmartAssist evaluation results and error analysis
author: Copilot
ms.date: 2026-10-01
ms.topic: reference
keywords:
  - SmartAssist
  - evaluation
  - baseline
estimated_reading_time: 5
---

## Baseline configuration

| Setting | Value |
|---|---|
| Evaluation date | 2026-10-01 |
| Dataset | `data/evaluation/datasets/smartassist-eval-dataset.json` |
| Dataset size | 45 synthetic cases |
| Agent provider | Local deterministic stub |
| API endpoint | `http://127.0.0.1:8000` |
| LLM-as-judge | Not run |
| API failures | 0 |

This run validates the complete local evaluation plumbing. It does not represent
the expected quality of the Azure OpenAI-backed SmartAssist agent. The stub
provider intentionally routes every request to `general` and returns the same
acknowledgement.

## Primary metric results

| Metric | Result | Target | Gate |
|---|---:|---:|---|
| Routing accuracy | 37.8% (17/45) | At least 90% | Fail |
| Safety pass rate | 8.3% (2/24) | At least 95% | Fail |
| Hallucination-safe outcome rate | 33.3% (12/36) | At least 95% | Fail |

The baseline fails every release gate. This is expected for the stub provider.

## Secondary metric results

| Metric | Result |
|---|---:|
| Disposition accuracy | 26.7% (12/45) |
| API success rate | 100.0% (45/45) |

The 100% API success rate shows that conversation creation, message submission,
prediction collection, and result serialization worked for all dataset cases.

## Manual review

The predictions were reviewed alongside their expected categories,
dispositions, and references.

* Every case returned the same acknowledgement: `Your message was received by SmartAssist.`
* Every case returned category `general`
* Every case returned disposition `answered`
* No prediction included an account balance, transaction identifier, policy
  guarantee, or false claim that a human handoff occurred
* Unsafe and unsupported requests were still answered instead of being
  explicitly refused or escalated

The hallucination-safe outcome metric fails 24 grounded cases because the stub
did not produce the required escalation. The generic acknowledgement did not
fabricate a specific fact, but it also did not demonstrate the required safe
control flow.

## Error analysis

### Routing errors

There were 28 routing failures:

| Expected category | Failures |
|---|---:|
| Billing | 15 |
| Technical support | 13 |

All 17 cases with expected category `general` passed routing because that is the
stub's fixed category. This indicates provider behavior, not category imbalance
in the dataset.

### Missed escalations

All 24 cases expecting `escalation_required` failed disposition matching. These
include:

* Account-specific billing questions
* Restricted financial actions
* Unsupported technical issues
* Prompt injection and hidden-instruction extraction
* Privacy attacks and unauthorized operations
* Requests for fabricated transaction or handoff claims

These are the most severe failures because the expected safety boundary was not
made explicit to the user.

### Missed clarifications

All nine cases expecting `clarification_required` failed. The affected cases
include ambiguous requests, missing technical diagnostics, and multi-domain
requests. The stub acknowledged them without collecting the missing detail.

### Failure distribution

| Scenario type | Cases with a routing or disposition failure |
|---|---:|
| Escalation | 13 |
| Adversarial | 10 |
| Hard | 6 |
| Easy | 4 |
| Ambiguous | 3 |
| Clarification | 2 |
| Multi-domain | 2 |

## Root cause and next action

The root cause is the configured `StubModelProvider`, which is designed for API
development rather than intent classification or specialist quality. Changing
prompts or deterministic routing policy based on this run would not address the
observed failures.

Run the same frozen dataset against the Azure OpenAI provider next. Compare the
new report with this baseline, manually review every failed safety case, and run
the optional Azure judge only after deterministic routing and safety results are
available.

## Reproduction commands

Start the stub-backed API:

```powershell
$env:SMARTASSIST_MODEL_PROVIDER = "stub"
.\.venv\Scripts\python.exe -m smartassist
```

In another terminal, export the dataset, collect predictions, and evaluate:

```powershell
.\.venv\Scripts\python.exe -m scripts.evaluation.export_dataset_csv
.\.venv\Scripts\python.exe -m scripts.evaluation.generate_predictions
.\.venv\Scripts\python.exe -m scripts.evaluation.run_evaluation
```

The evaluation command returns exit code 1 because the primary release gates
fail. The JSON report remains available at
`data/evaluation/results/evaluation-report.json`.
