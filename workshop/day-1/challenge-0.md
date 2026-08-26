# Challenge 0: Environment Setup and Verification

| | |
|---|---|
| **Duration** | 20 minutes |
| **Objective** | Verify all tools are installed and configured for the workshop |

## Introduction

Before diving into HVE-Core workflows, you need a properly configured development environment. This challenge ensures everyone starts from the same baseline with all required tools installed, authenticated, and ready to use.

## Learning Objectives

By the end of this challenge, you will be able to:

- Confirm that VS Code extensions (HVE-Core, GitHub Copilot) are installed and active
- Verify Python, Azure CLI, Azure Developer CLI, GitHub CLI, and Docker are properly configured
- Authenticate against Azure and GitHub services
- Provision an Azure resource group and AI Foundry resource for use in later challenges
- Enable the GitHub MCP server for direct GitHub integration from Copilot Chat
- Access all HVE-Core agents from the Copilot Chat agent picker

## Instructions

### Step 1: Fork the Workshop Repository

Fork the workshop repository to your own GitHub account. This gives you your own copy that you can open locally or in a Codespace.

Install the GitHub CLI if needed: <https://cli.github.com/>

```bash
gh auth login               # If not already authenticated
gh repo fork https://github.com/mcaps-microsoft/hve-core-workshop --clone
cd hve-core-workshop
```

**Or using git directly:**

1. Fork the repository via the GitHub UI (click **Fork** on the repo page)
2. Clone your fork:

```bash
git clone https://github.com/<YOUR-GITHUB-USERNAME>/hve-core-workshop.git
cd hve-core-workshop
```

Verify the fork:

```bash
git remote -v   # Should show your fork as 'origin'
```

### Step 2: Choose Your Setup Path

> [!NOTE]
> If Python, Azure CLI, Azure Developer CLI are installed locally and your Foundry resource is already provisioned, choose **Option B**. If you do not have the required tooling installed, **Option A** is the preferred path.

| Path | Best for | What you get |
|------|----------|--------------|
| **[Option A — Dev Container](setup/devcontainer-setup.md)** | Fastest start, consistent environment | All tools pre-installed; just authenticate and provision Azure resources |
| **[Option B — Local Machine](setup/local-setup.md)** | Full control, no container overhead | Manual installation of each prerequisite |

Follow the instructions in your chosen path, then return here for the remaining common steps.

---

### Step 3: Enable GitHub MCP Server

The GitHub MCP server lets Copilot interact with GitHub issues, PRs, and repositories directly.

**If running locally or in a local dev container:**

The GitHub MCP server extension should already be installed (the dev container installs it automatically). If running on a local machine without the dev container, install it manually:

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

#### If running on GitHub Codespaces

The GitHub MCP server **extension** is not yet supported on Codespaces. Instead, this repository includes a `.vscode/mcp.json` file that configures the MCP server via the CLI (`npx @modelcontextprotocol/server-github`). The `GITHUB_TOKEN` is automatically supplied by the Codespaces environment — no changes to the file are required.

To activate it:

1. Open the Copilot Chat panel and switch to **Agent mode**
2. Click the **MCP tools** icon (or open the Command Palette → **MCP: List Servers**)
3. Start the `github` server if it is not already running

Verify the server shows a green/running status before proceeding.

### Step 4: Verify HVE-Core Agents

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

- [ ] Workshop repository forked and cloned
- [ ] HVE Core - All extension active in VS Code
- [ ] Python 3.11+ available
- [ ] Azure CLI authenticated with active subscription
- [ ] Azure Developer CLI (`azd`) installed and authenticated
- [ ] Resource group created in Azure
- [ ] Azure AI Foundry resource created with a `gpt-4o` deployment
- [ ] GitHub CLI authenticated
- [ ] Docker installed and daemon running
- [ ] GitHub MCP server configured in VS Code
- [ ] All HVE Core agents visible in Copilot Chat

> **Tip:** If you used the dev container path (Option A), all tool installation criteria are satisfied automatically — just verify authentication and Azure resource provisioning.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| HVE-Core agents not appearing | Reload VS Code window (`Ctrl+Shift+P` → "Reload Window") |
| Azure CLI not authenticated | Run `az login` and select your subscription |
| `az login` fails in Codespaces | Corp/non-prod subscriptions are blocked. Use a personal subscription or the [$150 Azure Credit](https://my.visualstudio.com/Benefits) (Microsoft FTEs) |
| Azure Developer CLI not found | Install from <https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd> |
| Resource group creation failed | Ensure your subscription is active: `az account show` |
| AI Foundry deployment failed | Check region availability and quota: `az cognitiveservices account list-skus --kind OpenAI --location <region>` |
| GitHub CLI auth failed | Run `gh auth login` and follow the browser flow |
| Docker daemon not running | Start Docker Desktop or run `sudo systemctl start docker` (Linux) |
| Python version too old | Install Python 3.11+ from python.org |
