# Challenge 9: Deploy to Azure

| <br />             | <br />                                                                                 |
| ------------------ | -------------------------------------------------------------------------------------- |
| **Duration**       | 50 minutes                                                                             |
| **Objective**      | Deploy SmartAssist to Azure Container Apps with Managed Identity using Bicep and `azd` |
| **HVE-Core Stage** | Stage 8: Delivery                                                                      |
| **Agent**          | Task Implementer agent                                                                 |

## Context

SmartAssist is a FastAPI application built with the Microsoft Agent Framework. It uses `FoundryChatClient` with `DefaultAzureCredential` to call OpenAI models hosted in an **existing** Azure AI Foundry project. The deployment target is **Azure Container Apps** — a serverless container platform that handles scaling, networking, and TLS termination.

### Prerequisites — Existing Resources

You already have these resources provisioned in Azure:

| Resource | Purpose |
|----------|---------|
| **Azure AI Foundry project** | Hosts the OpenAI model deployment |
| **Chat model deployment** (e.g., `gpt-4o`) | LLM inference for agent responses |

Collect these values before you begin:

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `<your-rg>` | Resource group for SmartAssist infra | `smartassist-rg` |
| `<location>` | Azure region | `eastus2` |
| `<foundry-project-endpoint>` | Full endpoint URL of your AI Foundry project | `https://<account>.services.ai.azure.com/api/projects/<project>` |
| `<model-deployment-name>` | Name of the deployed chat model | `gpt-4o` |

### Architecture

```
┌─────────────┐     HTTPS      ┌──────────────────────┐    DefaultAzureCredential    ┌─────────────────────┐
│   Client     │ ──────────────▶│  Azure Container App  │ ─────────────────────────────▶│  Azure AI Foundry    │
│  (browser /  │                │  (SmartAssist API)    │     (Managed Identity)       │  (GPT-4o)           │
│   curl)      │                │                      │                              │                     │
└─────────────┘                └──────┬───────────────┘                              └─────────────────────┘
                                      │
                                      │ telemetry
                                      ▼
                               ┌──────────────────┐
                               │ Application       │
                               │ Insights          │
                               └──────────────────┘
```

### What Gets Provisioned (New Resources)

| Service | Purpose |
|---------|---------|
| **Azure Container Registry** | Stores the SmartAssist container image |
| **User-Assigned Managed Identity** | Authenticates to AI Foundry without secrets |
| **Container Apps Environment** | Hosting environment with Log Analytics integration |
| **Container App** | Runs the SmartAssist FastAPI container |
| **Log Analytics Workspace** | Collects container and application logs |
| **Application Insights** | Distributed tracing and monitoring |

> The AI Foundry project and model deployment are **not** provisioned by this challenge — they already exist.

## Instructions

### Step 1: Verify Azure Prerequisites

Confirm your Azure subscription and existing AI Foundry resources.

```bash
# Verify your active subscription
az account show --query "{name:name, id:id}" -o table

# List AI Services in your resource group
az cognitiveservices account list \
  --resource-group <your-rg> \
  --query "[].{name:name, endpoint:properties.endpoint}" -o table
```

If you need a new resource group for the SmartAssist deployment:

```bash
az group create --name <your-rg> --location <location>
```

### Step 2: Create the Dockerfile

In the **Task Implementer agent**, prompt:

```text
Create a Dockerfile at the project root for our SmartAssist FastAPI application.

Requirements:
- Use python:3.12-slim as the base image
- Install system dependencies (gcc) needed by Python packages
- Copy pyproject.toml/requirements.txt and src/ into the image
- Install the project with pip install --no-cache-dir .
- Create a non-root user and switch to it
- Expose port 8000
- Start with: uvicorn <Fast API App> --host 0.0.0.0 --port 8000
```

### Step 3: Test the Dockerfile Locally (Optional)

Build and run the container locally to verify the image works before deploying to Azure. Skip this step if Docker is not installed on your machine.

```bash
# Build the image
docker build -t smartassist .

# Run the container using your local .env file
docker run -d --name smartassist-test -p 8000:8000 --env-file .env smartassist

# Verify the liveness endpoint
curl http://localhost:8000/health

# Clean up
docker stop smartassist-test && docker rm smartassist-test
```

The `--env-file .env` flag loads all environment variables from your local `.env` file into the container. You should see a `200 OK` from `/health`. The `/chat` endpoint may still fail without Azure credentials forwarded into the container, which is expected at this stage.

### Step 4: Create the `azure.yaml` Project File

In the **Task Implementer agent**, prompt:

```text
Create an azure.yaml file at the project root for Azure Developer CLI (azd).

Requirements:
- Project name: smartassist
- Single service named "api" using containerapp host and python language
- Point docker.path to the Dockerfile we just created
- Set infra provider to bicep with path infra/
```

### Step 5: Create Bicep Infrastructure

In the **Task Implementer agent**, prompt:

```text
Create infra/main.bicep for deploying SmartAssist to Azure Container Apps.

Scope: resourceGroup

Parameters (all values that vary between environments):
- baseName (string) — prefix for all resource names
- location (string, default resourceGroup().location) — Azure region
- foundryProjectEndpoint (string) — existing AI Foundry project endpoint URL
- foundryModel (string, default 'gpt-4o') — model deployment name
- containerImage (string) — container image reference (use a placeholder default for initial provisioning)
- minReplicas (int, default 1) / maxReplicas (int, default 10) — scaling bounds
- tags (object) — resource tags

Derived values:
- Extract the AI Services account name from foundryProjectEndpoint (the subdomain before .services.ai.azure.com) using Bicep string functions — do NOT ask for it as a separate parameter.

Resources to create:
1. Log Analytics Workspace — PerGB2018 SKU, 30 day retention
2. Application Insights — web type, connected to the Log Analytics workspace
3. User-Assigned Managed Identity — the Container App authenticates to AI Foundry with this
4. Container Apps Environment — log destination set to log-analytics
5. Container App with:
   - User-assigned managed identity attached
   - External ingress on port 8000
   - Environment variables: FOUNDRY_PROJECT_ENDPOINT, FOUNDRY_MODEL, AZURE_CLIENT_ID (from the identity's clientId), APPLICATIONINSIGHTS_CONNECTION_STRING, LOG_LEVEL (INFO), CORS_ORIGINS (["*"])
   - Liveness probe on /health, readiness probe on /health/ready, startup probe on /health
   - HTTP-based autoscaling rule (concurrentRequests: 50)
   - 0.5 CPU, 1Gi memory
6. Role Assignment — derive the AI Services account name from foundryProjectEndpoint (extract subdomain), reference it with the 'existing' keyword, assign "Cognitive Services OpenAI User" (role definition ID 5e0bd9bd-7b93-4f28-af87-19fc36ad61bd) to the managed identity's principalId. Use guid(aiServices.id, identity.id, roleDefinitionId) for the assignment name.

Outputs:
- containerAppFqdn and containerAppUrl
- appInsightsConnectionString
- identityClientId and identityPrincipalId

Do NOT provision AI Foundry or model deployments — those already exist. The AI Services account is in the same resource group — derive its name from foundryProjectEndpoint and reference it with the 'existing' keyword.
```

### Step 6: Create Bicep Parameters

In the **Task Implementer agent**, prompt:

```text
Create infra/main.bicepparam using the 'using' syntax referencing ./main.bicep.

Set these values:
- baseName = 'smartassist'
- location = '<location>'
- foundryProjectEndpoint = '<foundry-project-endpoint>'
- foundryModel = '<model-deployment-name>'
- minReplicas = 1
- maxReplicas = 10
- tags with project = 'smartassist' and environment = 'development'

Leave the placeholder values as-is — participants will replace them with their own.
```

### Step 7: Deploy with `azd`

```bash
# Authenticate azd
azd auth login

# Create an azd environment and set the resource group
azd env new smartassist-dev
azd env set AZURE_RESOURCE_GROUP <your-rg>

# Provision infrastructure and deploy the container
azd up
```

`azd up` prompts for subscription and location, then runs `azd provision` (creates Azure resources from Bicep) followed by `azd deploy` (builds and pushes the container image, then updates the Container App). Setting `AZURE_RESOURCE_GROUP` tells `azd` to use your existing resource group instead of creating a new one.

### Step 8: Verify the Deployment

```bash
# Get the deployed URL
APP_URL=$(az containerapp show \
  --name <baseName>-app \
  --resource-group <your-rg> \
  --query "properties.configuration.ingress.fqdn" -o tsv)

# Liveness check
curl "https://$APP_URL/health"

# Readiness check
curl "https://$APP_URL/health/ready"

# Send a test message
curl -X POST "https://$APP_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "I have a billing question about my last invoice", "session_id": "test-001"}'
```

### Step 9: Verify Observability

Open the Azure portal and navigate to your Application Insights resource:

1. Check **Live Metrics** for real-time request telemetry
2. Open **Transaction search** to find the chat request trace
3. Verify the end-to-end trace shows the call from Container App → AI Foundry

### Step 10: Commit

```bash
git add Dockerfile azure.yaml infra/
git commit -m "feat: add Azure Container Apps deployment with Bicep and azd

- Add Dockerfile for containerized deployment
- Add azure.yaml for azd project configuration
- Add Bicep templates for Container Apps, Managed Identity, and monitoring
- Configure DefaultAzureCredential via user-assigned managed identity
- Add health probes (liveness, readiness, startup)
- Wire Application Insights telemetry via environment variable"

git push
```

## Success Criteria

- **Dockerfile** — builds a working container image with a non-root user
- **azure.yaml** — valid `azd` project file pointing to the Dockerfile and Bicep
- **Bicep template** — provisions Container Apps Environment, Container App, Managed Identity, Log Analytics, and Application Insights
- **Managed Identity** — user-assigned identity with `Cognitive Services OpenAI User` role on the AI Foundry resource
- **No secrets in code** — authentication uses `DefaultAzureCredential` exclusively; no API keys in environment variables or source
- **Health probes** — `/health` (liveness) and `/health/ready` (readiness) return 200 OK
- **Deployed and responding** — `azd up` succeeds and the Container App answers chat requests
- **Observability** — request traces visible in Application Insights

## Hints

<details>
<summary>Hint 1: Dockerfile</summary>

```dockerfile
FROM python:3.12-slim AS base

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY src/ ./src/

RUN pip install --no-cache-dir .

RUN adduser --disabled-password --gecos "" appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "smartassist.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

</details>

<details>
<summary>Hint 2: azure.yaml</summary>

```yaml
name: smartassist
metadata:
  template: smartassist-customer-support

services:
  api:
    project: .
    host: containerapp
    language: python
    docker:
      path: Dockerfile

infra:
  provider: bicep
  path: infra
```

</details>

<details>
<summary>Hint 3: Bicep parameter file</summary>

```bicep
using './main.bicep'

param baseName = 'smartassist'
param location = 'eastus2'
param foundryProjectEndpoint = '<foundry-project-endpoint>'
param foundryModel = '<model-deployment-name>'
param aiServicesAccountName = '<ai-services-account-name>'
param minReplicas = 1
param maxReplicas = 10
param tags = {
  project: 'smartassist'
  environment: 'production'
}
```

</details>

<details>
<summary>Hint 4: Managed Identity and role assignment in Bicep</summary>

`DefaultAzureCredential` inside the container picks up the user-assigned managed identity when `AZURE_CLIENT_ID` is set as an environment variable:

```bicep
env: [
  { name: 'AZURE_CLIENT_ID', value: identity.properties.clientId }
]
```

Since the AI Services account is in the same resource group, reference it with `existing` and assign the role directly in Bicep:

```bicep
@description('Name of the existing AI Services account in this resource group.')
param aiServicesAccountName string

resource aiServices 'Microsoft.CognitiveServices/accounts@2024-10-01' existing = {
  name: aiServicesAccountName
}

var cognitiveServicesOpenAIUserRole = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
)

resource roleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aiServices.id, identity.id, cognitiveServicesOpenAIUserRole)
  scope: aiServices
  properties: {
    principalId: identity.properties.principalId
    roleDefinitionId: cognitiveServicesOpenAIUserRole
    principalType: 'ServicePrincipal'
  }
}
```

This assigns the role during `azd up` — no manual CLI step needed.

</details>

<details>
<summary>Hint 5: If Azure resources are limited</summary>

If you don't have full Azure access during the workshop:

1. Create the Dockerfile, `azure.yaml`, and Bicep files as artifacts
2. Build and test the container locally: `docker build -t smartassist . && docker run -p 8000:8000 --env-file .env smartassist`
3. Verify health checks work: `curl http://localhost:8000/health`
4. Run `azd provision --preview` to validate the Bicep template without deploying

The learning value is in understanding the Container Apps + Managed Identity pattern, even without a live deployment.

</details>

## Bonus

- Add an HTTP scaling rule that scales to zero when idle (`minReplicas = 0`)
- Set up CI/CD with GitHub Actions using `azd` (`azd pipeline config`)
- Add a staging environment with a separate `azd` environment (`azd env new staging`)
- Configure custom domain and TLS certificate on the Container App
- Add a revision-based blue/green deployment strategy

