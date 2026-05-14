# Challenge 9: Deploy to Azure

| | |
|---|---|
| **Duration** | 50 minutes |
| **Objective** | Deploy SmartAssist to Azure using Microsoft Foundry hosted agents |
| **HVE-Core Stage** | Stage 8: Delivery |
| **Agent** | `RPI Agent` |

## Context

Microsoft Agent Framework supports **Foundry Hosted Agents** — deploy your agents to Azure with minimal configuration changes. The deployment path:

```
Local Development → Azure Foundry → Production
```

Key Azure services involved:

| Service | Purpose |
|---------|---------|
| **Azure AI Foundry** | Host and manage your agents |
| **Azure OpenAI** | LLM inference (GPT-4o) |
| **Azure Monitor** | Observability (Application Insights) |
| **Azure Container Apps** (optional) | Custom hosting if needed |

## Instructions

### Step 1: Verify Azure Resources

Ensure you have the required Azure resources:

```bash
# Check your subscription
az account show

# Verify you have an AI Foundry project
az ml workspace list --resource-group <your-rg>

# Or check for AI Services
az cognitiveservices account list --resource-group <your-rg>
```

If you need to create resources:

```bash
# Create a resource group
az group create --name smartassist-rg --location eastus2

# Create an AI Foundry project (if using Foundry)
# Follow: https://learn.microsoft.com/azure/ai-studio/how-to/create-projects
```

### Step 2: Research Deployment Pattern (RPI)

```
/rpi task="Research how to deploy a Microsoft Agent Framework Python application to Azure. Investigate: 1) Foundry Hosted Agents deployment pattern (preferred), 2) Required Azure resources and configuration, 3) How to transition from local FoundryChatClient to hosted deployment, 4) Environment variable configuration for production, 5) Health check and monitoring setup. Reference the MAF python/samples/04-hosting directory for patterns."
```

### Step 3: Prepare for Deployment

Based on research, prepare your application:

```
/rpi task="Prepare SmartAssist for Azure deployment. Tasks: 1) Create a Dockerfile for containerized deployment, 2) Add production configuration (separate from dev), 3) Add health check endpoint, 4) Configure OTLP export to Application Insights, 5) Add proper secret management (Key Vault references or environment variables), 6) Create deployment configuration files (azd, Bicep, or Docker Compose as appropriate). Do not include any secrets in code."
```

### Step 4: Create Infrastructure as Code

```
/rpi task="Create Azure infrastructure for SmartAssist deployment. Create Bicep or azd templates that provision: 1) Azure AI Foundry project (or reference existing), 2) Azure OpenAI deployment (gpt-4o), 3) Application Insights for monitoring, 4) Container App or Foundry hosting configuration, 5) Key Vault for secrets. Place templates in infra/ directory. Follow Azure best practices for naming and tagging."
```

### Step 5: Deploy

Using Azure Developer CLI (if azd templates created):

```bash
azd init
azd up
```

Or using direct deployment:

```bash
# Build container
docker build -t smartassist:latest .

# Push to Azure Container Registry
az acr build --registry <your-acr> --image smartassist:latest .

# Deploy to Container Apps (or Foundry)
az containerapp up --name smartassist \
  --resource-group smartassist-rg \
  --image <your-acr>.azurecr.io/smartassist:latest \
  --env-vars FOUNDRY_PROJECT_ENDPOINT=<endpoint> \
             FOUNDRY_MODEL_DEPLOYMENT_NAME=gpt-4o
```

For Foundry Hosted Agents (preferred):

```python
# The transition to hosted is minimal in MAF:
from agent_framework.foundry import FoundryHostedAgent

# Instead of running locally, register with Foundry
hosted = FoundryHostedAgent(
    agent=your_agent,
    project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
)
await hosted.start()
```

### Step 6: Verify Deployment

```bash
# Test the deployed endpoint
curl -X POST https://<your-endpoint>/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I have a billing question about my last invoice"}'

# Check health
curl https://<your-endpoint>/health
```

### Step 7: Run Evaluations Against Production

Run your evaluation suite against the deployed endpoint:

```bash
# Set the endpoint to production
export SMARTASSIST_ENDPOINT=https://<your-deployed-url>

# Run integration tests against prod
pytest tests/eval/ -v -m "integration" --endpoint=$SMARTASSIST_ENDPOINT
```

### Step 8: Commit Deployment Configuration

```bash
git add .
git commit -m "feat: add Azure deployment configuration

- Add Dockerfile for containerized deployment
- Add infrastructure as code (Bicep/azd)
- Configure Application Insights integration
- Add production environment configuration
- Add health check endpoint

Closes #<issue-number>"

git push
```

## Success Criteria

- [ ] **Deployment Files** — Dockerfile and/or azd configuration created
- [ ] **Infrastructure Code** — Bicep/ARM templates for Azure resources
- [ ] **Health Check** — `/health` endpoint responds with 200 OK
- [ ] **Deployed** — Application running on Azure (Foundry or Container Apps)
- [ ] **Responds to Queries** — Deployed agent answers customer support questions
- [ ] **Observability** — Traces visible in Application Insights
- [ ] **No Secrets in Code** — All credentials via environment variables or Key Vault
- [ ] **Evaluations Pass** — Remote evaluation confirms quality matches local

## Hints

<details>
<summary>Hint 1: Minimal Dockerfile</summary>

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["python", "-m", "smartassist", "--host", "0.0.0.0", "--port", "8000"]
```

</details>

<details>
<summary>Hint 2: azd template structure</summary>

```
infra/
├── main.bicep           # Main orchestration
├── main.parameters.json # Parameter values
├── modules/
│   ├── ai-foundry.bicep
│   ├── container-app.bicep
│   ├── monitoring.bicep
│   └── keyvault.bicep
azure.yaml               # azd project configuration
```

`azure.yaml`:
```yaml
name: smartassist
services:
  api:
    host: containerapp
    language: python
    project: .
```

</details>

<details>
<summary>Hint 3: If Azure resources are limited</summary>

If you don't have full Azure access during the workshop:

1. Create the deployment files (Dockerfile, Bicep) as artifacts
2. Test the Docker container locally: `docker build -t smartassist . && docker run -p 8000:8000 smartassist`
3. Verify the health check works locally
4. Document what Azure resources would be needed in a `docs/deployment-guide.md`

The learning value is in understanding the deployment pattern, even if you can't deploy live.

</details>

## Bonus

- Set up CI/CD with GitHub Actions (build → test → deploy on merge to main)
- Configure autoscaling based on request volume
- Add a staging environment with separate Azure resources
- Implement blue/green deployment for zero-downtime updates
