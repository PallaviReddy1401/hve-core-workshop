# Challenge 0 — Option A: Dev Container Setup

[← Back to Challenge 0](../challenge-0.md)

The `.devcontainer/` folder in this repository includes a fully configured development container with all prerequisites pre-installed (Python 3.11, Azure CLI, azd, GitHub CLI, Docker, and all required VS Code extensions).

You can run the dev container **locally** or on **GitHub Codespaces**.

## A1: Open the Dev Container

**Locally (Docker Desktop required):**

1. Install [Docker Desktop](https://docs.docker.com/get-started/get-docker/) and ensure it is running
2. Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) in VS Code
3. Open this repository in VS Code
4. Press `Ctrl+Shift+P` → **Dev Containers: Reopen in Container**
5. Wait for the container to build and the post-create script to finish

**GitHub Codespaces:**

1. Go to your forked repository on GitHub
2. Click **Code** → **Codespaces** → **Create codespace on main**
3. Wait for the environment to be ready

> **Codespaces Gotcha:** Azure login (`az login`) with non-production (corp) subscriptions does not work in Codespaces due to network restrictions. Use one of these alternatives:
>
> - A **personal Azure subscription**
> - As a Microsoft FTE, the **$150 monthly Azure Credit subscription** available at <https://my.visualstudio.com/Benefits>
>
> Additionally, the GitHub MCP server **extension** is not supported on Codespaces. The repo includes `.vscode/mcp.json` as a fallback — see [MCP setup for Codespaces](../challenge-0.md#if-running-on-github-codespaces) for details.

## A2: Authenticate

Once inside the dev container, authenticate with Azure and GitHub:

```bash
az login
azd auth login
gh auth login
```

## A3: Provision Azure Resources

If you do not already have an Azure AI Foundry resource, run the interactive setup script:

```bash
bash .devcontainer/azure-setup.sh
```

This script prompts for your preferred region, resource group name, and AI account name, then creates the resource group, AI Services account, Foundry project, and a `gpt-4o` model deployment.

> **Note:** Save the endpoint printed at the end — you will need it in Challenge 7.

## Next Steps

Return to [Challenge 0](../challenge-0.md#step-3-enable-github-mcp-server) to complete the remaining common steps (GitHub MCP Server and HVE-Core agent verification).

Once done, check off the [Success Criteria](../challenge-0.md#success-criteria).
