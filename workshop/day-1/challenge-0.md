# Challenge 0: Environment Setup and Verification

| | |
|---|---|
| **Duration** | 20 minutes |
| **Objective** | Verify all tools are installed and configured for the workshop |

## Context

Before diving into HVE-Core workflows, you need a properly configured development environment. This challenge ensures everyone starts from the same baseline.

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

### Step 4: Verify GitHub CLI

Install if needed: <https://cli.github.com/>

```bash
gh auth status          # Should show authenticated
```

### Step 5: Enable GitHub MCP Server

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

### Step 6: Fork the Workshop Repository

Fork the workshop repository to your own GitHub account:

```bash
gh repo fork https://github.com/sapsing_microsoft/gcid-workshop --clone
cd gcid-workshop
```

Verify the fork:

```bash
git remote -v   # Should show your fork as 'origin'
```

### Step 7: Verify HVE-Core Agents

Open GitHub Copilot Chat (`Ctrl+Alt+I`) and verify you can see these agents in the agent picker:

- BRD Builder
- PRD Builder
- Task Researcher
- Task Planner
- ADR Creation
- GitHub Backlog Manager
- Task Implementor
- Task Reviewer
- RPI Agent
- Evaluation Dataset Creator

## Success Criteria

- [ ] HVE Core - All extension active in VS Code
- [ ] Python 3.11+ available
- [ ] Azure CLI authenticated with active subscription
- [ ] GitHub CLI authenticated
- [ ] GitHub MCP server configured in VS Code
- [ ] Workshop repository forked and cloned
- [ ] All HVE Core agents visible in Copilot Chat

## Troubleshooting

| Issue | Solution |
|-------|----------|
| HVE-Core agents not appearing | Reload VS Code window (`Ctrl+Shift+P` → "Reload Window") |
| Azure CLI not authenticated | Run `az login` and select your subscription |
| GitHub CLI auth failed | Run `gh auth login` and follow the browser flow |
| Python version too old | Install Python 3.11+ from python.org |
