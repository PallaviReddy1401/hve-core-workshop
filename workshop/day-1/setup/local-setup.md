# Challenge 0 — Option B: Local Machine Setup

[← Back to Challenge 0](../challenge-0.md)

Install all prerequisites manually on your local machine.

## Step 1: Verify VS Code Extensions

Open VS Code and confirm these extensions are installed:

- **HVE Core - All** (`ise-hve-essentials.hve-core-all`) — The core HVE extension
- **GitHub Copilot** — AI pair programming
- **GitHub Copilot Chat** — Chat interface for Copilot
- **Python** — Python language support

```bash
code --list-extensions | Select-String "hve-core|copilot|python"
```

For macOS / Linux:

```bash
code --list-extensions | grep -iE "hve-core|copilot|python"
```

## Step 2: Verify Python Environment

Install Python 3.11+ if needed: <https://www.python.org/downloads/>

```bash
python --version        # Should be 3.11+
pip --version           # Should be available
```

## Step 3: Verify Azure CLI

Install if needed: <https://learn.microsoft.com/cli/azure/install-azure-cli>

```bash
az account show         # Should display your subscription
az login                # If not authenticated
```

## Step 4: Verify Azure Developer CLI (azd)

Install if needed: <https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd>

```bash
azd version             # Should display the installed version
azd auth login          # If not authenticated
```

## Step 5: Verify GitHub CLI

Install if needed: <https://cli.github.com/>

```bash
gh auth status          # Should show authenticated
```

## Step 6: Verify Docker

Docker is used in Challenge 9 to build and test the container locally before deploying to Azure.

Install if needed: <https://docs.docker.com/get-started/get-docker/>

```bash
docker --version        # Should display the installed version
docker info             # Should show Docker daemon is running
```

## Step 7: Provision Azure Resources (Resource Group + AI Foundry)

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
LOCATION="<YOUR LOCATION>"
RG_NAME="<YOUR RESOURCE GROUP NAME>"
AI_ACCOUNT="<YOUR FOUNDRY RESOURCE NAME>"        # also used as the custom subdomain (must be globally unique)
PROJECT_NAME="<YOUR PROJECT NAME>"
MODEL_NAME="gpt-4o"   # change this if you want to use a different model
MODEL_VERSION="2024-11-20"  # set the version based on your model selection 
DEPLOYMENT="gpt-4o" # set your deployment name
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

## Next Steps

Return to [Challenge 0](../challenge-0.md#step-3-enable-github-mcp-server) to complete the remaining common steps (GitHub MCP Server and HVE-Core agent verification).

Once done, check off the [Success Criteria](../challenge-0.md#success-criteria).
