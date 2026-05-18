# Challenge 8: Brownfield — Refactor to Microsoft Agent Framework for Foundry Deployment

| <br />             | <br />                                                                                                                                        |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **Duration**       | 60 minutes                                                                                                                                    |
| **Objective**      | Refactor your existing SmartAssist agents to use Microsoft Agent Framework with `FoundryChatClient`, enabling deployment to Microsoft Foundry |
| **HVE-Core Stage** | Stage 6: Implementation (brownfield)                                                                                                          |
| **Agents**         | `GitHub Backlog Manager` → `Task Researcher` → `Task Planner` → `Task Implementor` → `Task Reviewer`                                          |

## Introduction

Up to this point you have built a working agent system. Now you face a common real-world scenario: **brownfield refactoring** — migrating existing, functioning code to a new framework while preserving all behavior. You will refactor SmartAssist to use Microsoft Agent Framework with `FoundryChatClient`. The R→P→I→R workflow applies equally well to refactoring tasks as it does to greenfield work.

## Learning Objectives

By the end of this challenge, you will be able to:

- Apply the R→P→I→R workflow to a brownfield refactoring scenario
- Map existing agent abstractions to Microsoft Agent Framework equivalents (`Agent`, `FoundryChatClient`)
- Create a phased migration strategy that maintains backward compatibility
- Use `DefaultAzureCredential` for secret-free authentication
- Verify post-migration behavior matches the original implementation
- Prepare an application for cloud deployment to Microsoft Foundry

## Context

### Where You Are (End of Day 2)

By the end of Day 2, you have a **running implementation** of:

- ✅ **API Router Agent** — Routes customer queries to the appropriate specialist
- ✅ **3 Specialized Agents** — Billing, Technical Support, and Account Management (or similar)
- ✅ **Local Memory** — Session-scoped conversation memory
- ✅ **Observability** — (depends on your implementation progress)

Your current code may be using **OpenAI client directly**, **Semantic Kernel**, or **another framework** to power these agents.

### What Changes Now (Brownfield Refactor)

This is a **brownfield refactoring** scenario. You are **not** building new features — you are migrating your existing, working agent system to a new framework while preserving all functionality.

**Why Microsoft Agent Framework?**

- Enables deployment to **Microsoft Foundry** (cloud-hosted agent infrastructure)
- Provides a standardized agent abstraction with `FoundryChatClient`
- Built-in support for streaming, conversation history, and tooling
- Production-grade observability and scaling out of the box

**The refactoring challenge:**

1. **Research** discovers how your current agents work and how MAF maps to them
2. **Planning** creates a migration strategy that maintains backward compatibility
3. **Implementation** refactors agent code to use `FoundryChatClient` and `Agent` classes
4. **Review** verifies all existing functionality still works post-migration

## Instructions

### Step 1: Add Issue to GitHub Backlog

Use the **GitHub Backlog Manager** agent (or agent mode) to create a new issue for this refactoring work:

```text
Create a new issue for refactoring our SmartAssist agent system to Microsoft Agent Framework.

Title: "refactor: Migrate agents to Microsoft Agent Framework (FoundryChatClient)"

Body:
As a developer, I want to refactor the existing SmartAssist agents to use Microsoft Agent Framework
so that we can deploy them to Microsoft Foundry.

Current State:
- Router agent, 3 specialist agents, and local memory are working

Target State:
- All agents use `agent_framework.Agent` with `FoundryChatClient`
- Routing logic preserved (router dispatches to specialists)
- Application remains backward-compatible (same API surface)
- Ready for Foundry deployment

Acceptance Criteria:
- Given: The existing SmartAssist system with router + 3 specialists
- When: Agents are refactored to use FoundryChatClient
- Then: All existing routing, memory, and agent behaviors still work
- And: Each agent is created using `Agent(client=FoundryChatClient(...), ...)`
- And: The system can be deployed to Microsoft Foundry

Technical Notes:
- Reference: https://github.com/microsoft/agent-framework/blob/main/python/samples/01-get-started/01_hello_agent.py
- Key imports: `from agent_framework import Agent` and `from agent_framework.foundry import FoundryChatClient`
- Auth: `from azure.identity import AzureCliCredential`

Labels: P0-must-have, refactoring, day-3
```

Note the issue number: `#___`

### Step 2: Research Phase (Task Researcher)

> Refer to [Challenge 5 (Day 2)](../day-2/challenge-5.md) for detailed R→P→I→R workflow instructions.

Start a **new chat session** and select the **Task Researcher** agent. Point it at your new issue:

```text
Research GitHub issue #<issue-number> for implementation. This is a brownfield refactoring task.
```

Wait for the research document in `.copilot-tracking/research/`.

**Review the research:** Does it clearly map your current agent code to the MAF equivalents? Does it identify all files that need changes?

### Step 3: Plan Phase (Task Planner)

Clear context (`/clear` or new chat). Select the **Task Planner** agent. Add the research document to chat context:

```text
Plan the implementation for the attached research document. 

```

Review the plan in `.copilot-tracking/plans/`. Verify the migration order makes sense (typically: shared client setup → router agent → specialist agents → memory integration).

### Step 4: Implement Phase (Task Implementor)

Clear context. Select the **Task Implementor** agent. Add the plan to chat context:

```text
Implement the plan for attached implementation plan

```

**Let it work autonomously.** Only intervene if it asks for clarification.

### Step 5: Review Phase (Task Reviewer)

Clear context. Select the **Task Reviewer** agent:

```text
Review the implementation for GitHub issue #<issue-number> against the plan in .copilot-tracking/plans/.


```

### Step 6: Verify the Refactoring

Run your existing tests and verify the application still works. Ensure:

- All existing tests pass
- The application starts without errors
- Routing still works (queries go to the correct specialist agent)
- Conversation memory is functional

### Step 7: Commit and Close

```bash
git add .
git commit -m "refactor: migrate agents to Microsoft Agent Framework (FoundryChatClient)

- Replace existing agent implementation with agent_framework.Agent
- Use FoundryChatClient with AzureCliCredential for all agents
- Preserve routing logic and conversation memory
- All existing tests pass (backward compatible)
- Ready for Microsoft Foundry deployment

Closes #<issue-number>"

git push
```

Or ask Copilot:

```text
Commit all changes and close GitHub issue #<issue-number>
```

> [!IMPORTANT]
> **Prepare for deployment.** The next challenge deploys SmartAssist to Azure Container Apps, which requires **liveness** (`GET /health`) and **readiness** (`GET /health/ready`) probes. Make sure your API exposes both endpoints and that each returns `200 OK`. If either is missing, add them now before moving on.
>
> ```bash
> curl http://localhost:8000/health
> curl http://localhost:8000/health/ready
> ```

## Success Criteria

- **Issue Created** — Refactoring issue exists in GitHub backlog with clear acceptance criteria
- **Research Complete** — Research document maps existing code to MAF equivalents
- **Plan Created** — Migration plan with phased approach and rollback strategy
- **Agents Migrated** — All agents use `Agent` + `FoundryChatClient` pattern
- **Routing Preserved** — Router still dispatches to correct specialist agents
- **Memory Works** — Conversation history still functions post-migration
- **No Regressions** — Existing tests pass, application starts without errors
- **Health Endpoints** — `/health` (liveness) and `/health/ready` (readiness) return `200 OK`
- **Foundry Ready** — Code structure supports deployment to Microsoft Foundry

## Hints

<details>
<summary>Hint 1: Microsoft Agent Framework Hello Agent reference</summary>

The simplest MAF agent using `FoundryChatClient` ([source](https://github.com/microsoft/agent-framework/blob/main/python/samples/01-get-started/01_hello_agent.py)):

```python
import asyncio

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential


async def main() -> None:
    client = FoundryChatClient(
        project_endpoint="https://your-project.services.ai.azure.com",
        model="gpt-4o",
        credential=AzureCliCredential(),
    )

    agent = Agent(
        client=client,
        name="HelloAgent",
        instructions="You are a friendly assistant. Keep your answers brief.",
    )

    # Non-streaming
    result = await agent.run("What is the capital of France?")
    print(f"Agent: {result}")

    # Streaming
    print("Agent (streaming): ", end="", flush=True)
    async for chunk in agent.run("Tell me a one-sentence fun fact.", stream=True):
        if chunk.text:
            print(chunk.text, end="", flush=True)
    print()


if __name__ == "__main__":
    asyncio.run(main())
```

</details>

<details>
<summary>Hint 2: Mapping existing agents to MAF</summary>

Each of your existing agents maps directly to an MAF `Agent` instance:

```python
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential

# Shared client (all agents can share the same FoundryChatClient)
client = FoundryChatClient(
    project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    model=os.environ.get("FOUNDRY_MODEL_DEPLOYMENT_NAME", "gpt-4o"),
    credential=AzureCliCredential(),
)

# Router Agent
router = Agent(
    client=client,
    name="SmartAssist Router",
    instructions="You route customer queries to the appropriate specialist...",
)

# Specialist Agents
billing_agent = Agent(
    client=client,
    name="Billing Specialist",
    instructions="You handle billing inquiries...",
)

technical_agent = Agent(
    client=client,
    name="Technical Support",
    instructions="You handle technical support issues...",
)
```

</details>

<details>
<summary>Hint 3: Brownfield RPI research focus</summary>

In brownfield mode, the Task Researcher should focus on your **existing code first**:

```
When researching, prioritize understanding:
1. Current file structure and module boundaries
2. How agents are currently instantiated (what framework/client)
3. How routing decisions are made
4. Where conversation memory is stored/passed
5. What the public API surface looks like (endpoints, contracts)
```

Then map each finding to the MAF equivalent. The goal is **migration**, not redesign.

If the agent tries to redesign everything, redirect: "Don't redesign the existing architecture. Map the current implementation to MAF equivalents with minimal structural change."

</details>

<details>
<summary>Hint 4: Environment configuration for Foundry</summary>

Create or update your `.env.example` with Foundry-specific variables:

```env
FOUNDRY_PROJECT_ENDPOINT=https://<your-project>.services.ai.azure.com
FOUNDRY_MODEL_DEPLOYMENT_NAME=gpt-4o
```

Load in your config:

```python
import os
from dotenv import load_dotenv
load_dotenv()
```

Authentication uses `AzureCliCredential` — ensure you're logged in:

```bash
az login
```

</details>

<details>
<summary>Hint 5: Preserving routing with MAF</summary>

If your router currently uses function calling or structured output to decide routing, the same pattern works with MAF:

```python
# Router decides which specialist to invoke
result = await router.run(user_message)

# Parse routing decision from result
if "billing" in result.lower():
    response = await billing_agent.run(user_message)
elif "technical" in result.lower():
    response = await technical_agent.run(user_message)
```

The key insight: MAF's `Agent.run()` replaces whatever LLM call you were previously making. The orchestration logic around it stays the same.

</details>

## Bonus

- Deploy the refactored agents to Microsoft Foundry
- Add streaming support using `agent.run(message, stream=True)` for real-time responses
- Implement agent-to-agent communication using MAF's native patterns
- Add structured tool definitions to specialist agents using MAF's tool API

