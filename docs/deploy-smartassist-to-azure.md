---
title: Deploy SmartAssist to Azure
description: Prepare, validate, deploy, and verify SmartAssist on Azure Container Apps
author: Copilot
ms.date: 2026-10-05
ms.topic: how-to
keywords:
  - SmartAssist
  - Azure Container Apps
  - Microsoft Foundry
  - Azure Developer CLI
estimated_reading_time: 8
---

## Prerequisites

Install and authenticate these tools:

* Azure CLI
* Azure Developer CLI
* Docker
* Bicep CLI through Azure CLI

Use the confirmed subscription and tenant:

```powershell
az login --tenant 7c8049d6-6290-429b-8e79-97aacf409e3c --use-device-code
az account set --subscription 334eb417-4d1e-4ee1-a5d9-9fbba8bda10d
azd auth login
```

Do not deploy until the
[deployment plan](../.azure/deployment-plan.md) has a `Validated` status.

## Deployment architecture

The AZD and Bicep configuration creates:

* One Azure Container Apps API with external HTTPS ingress
* One Basic Azure Container Registry
* One user-assigned managed identity
* One Microsoft Foundry account and project
* One `gpt-4.1-mini` Global Standard deployment at 10K TPM
* One Log Analytics workspace
* One workspace-based Application Insights resource

SmartAssist authenticates to Foundry with managed identity. No model API key is
stored in the application or deployment parameters.

## Local container verification

Build the image:

```powershell
docker build --tag smartassist:challenge-9 .
```

Run the stub provider for a local health check:

```powershell
docker run --rm --publish 8000:8000 `
  --env SMARTASSIST_MODEL_PROVIDER=stub `
  smartassist:challenge-9
```

Verify health from another terminal:

```powershell
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:8000/health/ready
```

## Azure preparation and validation

The preparation workflow validates the files before deployment:

```powershell
az bicep build --file infra\main.bicep
azd config list
```

The Azure validation workflow must then verify Bicep, AZD, provider
registrations, policies, permissions, and container behavior. It records proof
in the deployment plan and changes the status to `Validated`.

## Deployment

Run deployment only through the Azure deployment workflow after validation and
explicit approval. Foundry-specific AZD commands must set the user agent for
the current process:

```powershell
$env:AZURE_DEV_USER_AGENT = "microsoft_foundry_skill"
azd env new smartassist-dev
azd env set AZURE_LOCATION northcentralus
azd up
```

The deployment workflow handles failures, verifies outputs, and removes the
temporary process-scoped environment variable when complete.

## Endpoint verification

Read deployment outputs:

```powershell
azd env get-values
```

Verify liveness and readiness:

```powershell
$apiUrl = azd env get-value API_URL
Invoke-RestMethod "$apiUrl/health"
Invoke-RestMethod "$apiUrl/health/ready"
```

Create a conversation:

```powershell
$conversation = Invoke-RestMethod `
  -Method Post `
  -Uri "$apiUrl/api/v1/conversations" `
  -ContentType "application/json" `
  -Body '{"data_classification":"synthetic"}'
```

Send a message:

```powershell
$headers = @{
  "Idempotency-Key" = [guid]::NewGuid().ToString()
}
$body = @{
  content = "I need help understanding a charge on my bill."
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri "$apiUrl/api/v1/conversations/$($conversation.conversation_id)/messages" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $body
```

## Telemetry verification

Application Insights receives automatic FastAPI request telemetry, dependency
spans, exceptions, and logs through Azure Monitor OpenTelemetry.

Use this query to verify requests:

```kusto
requests
| where cloud_RoleName == "smartassist-api"
| order by timestamp desc
| take 20
```

Use this query to verify Foundry calls:

```kusto
dependencies
| where cloud_RoleName == "smartassist-api"
| order by timestamp desc
| take 20
```

## Cleanup

Cleanup deletes the resource group, monitoring history, registry images,
Foundry project, model deployment, and application. Run it only after explicit
destructive-action approval:

```powershell
azd down
```
