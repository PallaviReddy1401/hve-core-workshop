---
title: Run SmartAssist Locally
description: Environment variables, credentials, and commands for running the SmartAssist MVP API
author: Copilot
ms.date: 2026-10-01
ms.topic: how-to
keywords:
  - SmartAssist
  - FastAPI
  - Microsoft Foundry
estimated_reading_time: 4
---

## Prerequisites

* Python 3.11 or later
* A virtual environment
* Access to a Microsoft Foundry project only when using the Foundry provider

## Install dependencies

The project uses a standard `pyproject.toml`. If `uv` is installed:

```powershell
uv sync --extra dev
```

Without `uv`, use pip:

```powershell
python -m pip install -e ".[dev]"
```

## Run with the local provider

The local provider requires no cloud credentials and does not send content to an
external service.

```powershell
$env:SMARTASSIST_MODEL_PROVIDER = "stub"
python -m smartassist
```

Open `http://127.0.0.1:8000/docs` for the generated API documentation.

## Run with Microsoft Foundry

Set these variables:

```powershell
$env:SMARTASSIST_MODEL_PROVIDER = "foundry"
$env:SMARTASSIST_FOUNDRY_PROJECT_ENDPOINT = "https://<resource>.services.ai.azure.com/api/projects/<project>"
$env:SMARTASSIST_FOUNDRY_MODEL_DEPLOYMENT_NAME = "<deployment-name>"
```

SmartAssist uses `DefaultAzureCredential`. For local development, authenticate
Azure CLI with the tenant that owns the Foundry project:

```powershell
az login --tenant <tenant-id> --use-device-code
az account set --subscription "<enabled-subscription>"
```

Run the application:

```powershell
python -m smartassist
```

The same credential chain can use managed identity after deployment. Never
commit endpoint values, deployment names, tokens, or keys. The checked-in
`.env.example` contains variable names and safe defaults only.

## Debug with Foundry Toolkit

Install the development dependencies, open **Run and Debug**, and select
`Debug SmartAssist Agent API`. The configuration:

* Starts the actual SmartAssist FastAPI entry point from `.venv`
* Enables `debugpy` on port 5679
* Starts the API on port 8000
* Opens Foundry Toolkit Agent Inspector

The Inspector can connect to the local API process for development. A
Foundry-hosted agent protocol endpoint is deferred to the deployment challenge.

## Exercise the API

Create a conversation:

```powershell
$conversation = Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/v1/conversations `
  -ContentType application/json `
  -Body '{"data_classification":"synthetic"}'
```

Submit a message:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/api/v1/conversations/$($conversation.conversation_id)/messages" `
  -Headers @{"Idempotency-Key" = "local-request-1"} `
  -ContentType application/json `
  -Body '{"content":"Hello SmartAssist"}'
```

Verify liveness and readiness:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/health/ready
```

## Validate

```powershell
python -m ruff check .
python -m pytest
```

The MVP accepts only `synthetic` and `deidentified` conversation
classifications. Production content is rejected.
