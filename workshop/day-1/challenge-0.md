# Challenge 0: Environment Setup and Verification

| | |
|---|---|
| **Duration** | 20 minutes |
| **Objective** | Verify all tools are installed and configured for the workshop |

## Introduction

Before diving into HVE-Core workflows, you need a properly configured development environment. This challenge ensures everyone starts from the same baseline with all required tools installed, authenticated, and ready to use. You will verify your IDE setup, CLI tools, cloud services, and MCP integrations that power the entire workshop.

## Learning Objectives

By the end of this challenge, you will be able to:

- Confirm that VS Code extensions (HVE-Core, GitHub Copilot) are installed and active
- Verify Python, Azure CLI, Azure Developer CLI, GitHub CLI, and Docker are properly configured
- Authenticate against Azure and GitHub services
- Provision an Azure resource group and AI Foundry resource for use in later challenges
- Enable the GitHub MCP server for direct GitHub integration from Copilot Chat
- Access all HVE-Core agents from the Copilot Chat agent picker

## Instructions

### Step 1: Verify VS Code Extensions

Open VS Code and confirm these extensions are installed:

- **HVE Core - All** (`ise-hve-essentials.hve-core-all`) — The core HVE extension
- **GitHub Copilot** — AI pair programming
- **GitHub Copilot Chat** — Chat interface for Copilot
- **Python** — Python language support

```bash
code --list-extensions | Select-String "hve-core|copilot|python"
```
For MacOS -
```bash
code --list-extensions | grep -iE "hve-core|copilot|python"
```

### Step 2: Verify Python Environment

Install Python 3.11+ if needed: <https://www.python.org/downloads/>

```bash
python --version        # Should be 3.11+
pip --version           # Should be available
```

### Step 3: Verify Azure CLI

Install if needed: <https://learn.microsoft.com/cli/azure/install-azure-cli>

```bash
az account show         # Should display your subscription
az login                # If not authenticated
```

### Step 4: Verify Azure Developer CLI (azd)

Install if needed: <https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd>

```bash
azd version             # Should display the installed version
azd auth login          # If not authenticated
```

### Step 5: Verify GitHub CLI

Install if needed: <https://cli.github.com/>

```bash
gh auth status          # Should show authenticated
```

### Step 6: Verify Docker

Docker is used in Challenge 9 to build and test the container locally before deploying to Azure.

Install if needed: <https://docs.docker.com/get-started/get-docker/>

```bash
docker --version        # Should display the installed version
docker info             # Should show Docker daemon is running
```

### Step 7: Provision Azure Resources (Resource Group + AI Foundry)

You will create a dedicated resource group plus an Azure AI Foundry (formerly Azure OpenAI) account, a Foundry project, and a `gpt-4o` model deployment. The model deployment is required for the evaluation challenge (Challenge 7), so set everything up now.

To keep names consistent across commands, define shell variables once and reference them in every command. Pick the tab matching your shell — the commands are identical apart from variable syntax and line-continuation characters.

**Define your variables** (edit `LOCATION` to your preferred Azure region, e.g. `eastus2`, `westus3`, `swedencentral`; and set the name for your azure resources):

<details>
<summary><strong>Windows (PowerShell)</strong></summary>

```powershell
$LOCATION       = "<YOUR LOCATION>"
$RG_NAME        = "<YOUR RESOURCE GROUP NAME>"
$AI_ACCOUNT     = "<YOUR FOUNDRY RESOURCE NAME>"        # also used as the custom subdomain (must be globally unique)
$PROJECT_NAME   = "<YOUR PROJECT NAME>"
$MODEL_NAME     = "gpt-4o"   # change this if you want to use a different model
$MODEL_VERSION  = "2024-11-20"  # set the version based on your model selection 
$DEPLOYMENT     = "gpt-4o" # set your deployment name
```

**1. Create the resource group:**

```powershell
az group create --name $RG_NAME --location $LOCATION
az group show --name $RG_NAME --query "{name:name, location:location, state:properties.provisioningState}" -o table
```

**2. Create the Azure AI Services (Foundry) account:**

```powershell
az cognitiveservices account create `
  --name $AI_ACCOUNT `
  --resource-group $RG_NAME `
  --kind AIServices `
  --sku S0 `
  --location $LOCATION `
  --custom-domain $AI_ACCOUNT `
  --yes
```

> **Note:** `--custom-domain` is required so the account can host a Foundry project and use Entra ID auth. The value must be globally unique across Cognitive Services and **cannot be changed after it is set**.

**3. Create a Foundry project inside the account:**

```powershell
az cognitiveservices account project create `
  --resource-group $RG_NAME `
  --name $AI_ACCOUNT `
  --project-name $PROJECT_NAME `
  --location $LOCATION
```

**4. Deploy a `gpt-4o` model:**

```powershell
az cognitiveservices account deployment create `
  --name $AI_ACCOUNT `
  --resource-group $RG_NAME `
  --deployment-name $DEPLOYMENT `
  --model-name $MODEL_NAME `
  --model-version $MODEL_VERSION `
  --model-format OpenAI `
  --sku-name Standard `
  --sku-capacity 10
```

**5. Retrieve the endpoint for later use:**

```powershell
az cognitiveservices account show `
  --name $AI_ACCOUNT `
  --resource-group $RG_NAME `
  --query "{endpoint:properties.endpoint}" -o table
```

</details>

<details>
<summary><strong>macOS / Linux (bash / zsh)</strong></summary>

```bash
LOCATION       = "<YOUR LOCATION>"
RG_NAME        = "<YOUR RESOURCE GROUP NAME>"
AI_ACCOUNT     = "<YOUR FOUNDRY RESOURCE NAME>"        # also used as the custom subdomain (must be globally unique)
PROJECT_NAME   = "<YOUR PROJECT NAME>"
MODEL_NAME     = "gpt-4o"   # change this if you want to use a different model
MODEL_VERSION  = "2024-11-20"  # set the version based on your model selection 
DEPLOYMENT     = "gpt-4o" # set your deployment name
```

**1. Create the resource group:**

```bash
az group create --name "$RG_NAME" --location "$LOCATION"
az group show --name "$RG_NAME" --query "{name:name, location:location, state:properties.provisioningState}" -o table
```

**2. Create the Azure AI Services (Foundry) account:**

```bash
az cognitiveservices account create \
  --name "$AI_ACCOUNT" \
  --resource-group "$RG_NAME" \
  --kind AIServices \
  --sku S0 \
  --location "$LOCATION" \
  --custom-domain "$AI_ACCOUNT" \
  --yes
```

> **Note:** `--custom-domain` is required so the account can host a Foundry project and use Entra ID auth. The value must be globally unique across Cognitive Services and **cannot be changed after it is set**.

**3. Create a Foundry project inside the account:**

```bash
az cognitiveservices account project create \
  --resource-group "$RG_NAME" \
  --name "$AI_ACCOUNT" \
  --project-name "$PROJECT_NAME" \
  --location "$LOCATION"
```

**4. Deploy a `gpt-4o` model:**

```bash
az cognitiveservices account deployment create \
  --name "$AI_ACCOUNT" \
  --resource-group "$RG_NAME" \
  --deployment-name "$DEPLOYMENT" \
  --model-name "$MODEL_NAME" \
  --model-version "$MODEL_VERSION" \
  --model-format OpenAI \
  --sku-name Standard \
  --sku-capacity 10
```

**5. Retrieve the endpoint for later use:**

```bash
az cognitiveservices account show \
  --name "$AI_ACCOUNT" \
  --resource-group "$RG_NAME" \
  --query "{endpoint:properties.endpoint}" -o table
```

</details>

> **Note:** Save the endpoint — you will need it in Challenge 7 for LLM-as-judge evaluation calls. Authentication uses Azure AD (`az login`) — key-based auth is not supported. The resource group is used throughout the workshop; do not delete it until all challenges are complete.

### Step 8: Enable GitHub MCP Server

The GitHub MCP server lets Copilot interact with GitHub issues, PRs, and repositories directly. Enable it in VS Code:

1. Open the **Extensions** view (`Cmd+Shift+X` / `Ctrl+Shift+X`)
2. In the search bar, type `@mcp github`

   ![Search for GitHub MCP](../assets/reference_images/mcp-extension-search.png)

3. Click **Install** on the GitHub MCP server entry
4. Follow the authentication workflow that appears — sign in with your GitHub account when prompted

   ![MCP authentication flow](../assets/reference_images/mcp-auth-flow.png)

5. Once installed, switch to **Agent mode** in the Copilot Chat input area
6. Verify the server is running by checking the MCP tool icon in the Copilot Chat panel

   ![MCP server running status](../assets/reference_images/mcp-server-status.png)

> **Note:** Requires VS Code 1.101 or later for remote MCP and OAuth support.

### Step 9: Fork the Workshop Repository

Fork the workshop repository to your own GitHub account:

```bash
gh repo fork https://github.com/mcaps-microsoft/hve-core-workshop --clone
cd hve-core-workshop
```

Verify the fork:

```bash
git remote -v   # Should show your fork as 'origin'
```

### Step 10: Verify HVE-Core Agents

Open GitHub Copilot Chat (`Ctrl+Alt+I`) and verify you can see these agents in the agent picker:

- BRD Builder
- PRD Builder
- Task Researcher
- ADR Creation
- GitHub Backlog Manager
- Task Planner
- Task Implementor
- Task Reviewer
- RPI Agent
- Evaluation Dataset Creator

## Success Criteria

- [ ] HVE Core - All extension active in VS Code
- [ ] Python 3.11+ available
- [ ] Azure CLI authenticated with active subscription
- [ ] Azure Developer CLI (`azd`) installed and authenticated
- [ ] Resource group `hve-workshop-rg` created
- [ ] Azure AI Foundry resource created with a `gpt-4o` deployment
- [ ] GitHub CLI authenticated
- [ ] Docker installed and daemon running
- [ ] GitHub MCP server configured in VS Code
- [ ] Workshop repository forked and cloned
- [ ] All HVE Core agents visible in Copilot Chat

## Troubleshooting

| Issue | Solution |
|-------|----------|
| HVE-Core agents not appearing | Reload VS Code window (`Ctrl+Shift+P` → "Reload Window") |
| Azure CLI not authenticated | Run `az login` and select your subscription |
| Azure Developer CLI not found | Install from <https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd> |
| Resource group creation failed | Ensure your subscription is active: `az account show` |
| AI Foundry deployment failed | Check region availability and quota: `az cognitiveservices account list-skus --kind OpenAI --location <region>` |
| GitHub CLI auth failed | Run `gh auth login` and follow the browser flow |
| Docker daemon not running | Start Docker Desktop or run `sudo systemctl start docker` (Linux) |
| Python version too old | Install Python 3.11+ from python.org |
