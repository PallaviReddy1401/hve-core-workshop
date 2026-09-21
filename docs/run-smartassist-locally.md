---
title: Run SmartAssist Locally
description: Environment variables, credentials, and commands for running the SmartAssist MVP API
author: Copilot
ms.date: 2026-09-21
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
* Azure OpenAI credentials only when using the Azure provider

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

## Run with Azure OpenAI

Set these variables:

```powershell
$env:SMARTASSIST_MODEL_PROVIDER = "azure"
$env:SMARTASSIST_AZURE_OPENAI_ENDPOINT = "https://<resource>.openai.azure.com"
$env:SMARTASSIST_AZURE_OPENAI_DEPLOYMENT = "<deployment-name>"
$env:SMARTASSIST_AZURE_OPENAI_API_VERSION = "2024-10-21"
```

For local API-key authentication:

```powershell
$env:SMARTASSIST_AZURE_OPENAI_API_KEY = "<secret>"
```

For Microsoft Entra authentication, omit the API-key variable and authenticate
with a supported `DefaultAzureCredential` source. Set the tenant when required:

```powershell
$env:AZURE_TENANT_ID = "<tenant-id>"
az login
```

Never commit values from these variables. The checked-in `.env.example`
contains names and safe defaults only.

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

## Validate

```powershell
python -m ruff check .
python -m pytest
```

The MVP accepts only `synthetic` and `deidentified` conversation
classifications. Production content is rejected.
