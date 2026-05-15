# Challenge 6: RPI Autonomous Agent — Remaining Epics

| | |
|---|---|
| **Duration** | 45 minutes |
| **Objective** | Use the RPI Autonomous Agent to implement remaining epics end-to-end without manual intervention |
| **HVE-Core Stage** | Stage 6: Implementation |
| **Agents** | `RPI Agent` |

## Context

In the previous challenge you learned the manual R→P→I→R cycle by driving each phase individually. Now you will use the **RPI Autonomous Agent**, which runs the same Research → Plan → Implement → Review workflow but does it autonomously, with no user input required between phases.

This approach is ideal for:

- Smaller, well-defined tasks where the scope is clear
- Epics with no major design decisions that need human judgment
- Tasks where the acceptance criteria are unambiguous and don't require trade-off discussions

> [!IMPORTANT]
> In this workshop we run the RPI cycle on **epics** because the MVP scope is small and time is limited. In a real-world project, developers would run R→P→I→R on individual **user stories** — epics are too large for a single cycle and should be broken down first.

## Instructions

### Step 1: RPI Autonomous Agent — Next Epic(s)

> **Pick the next epic** from your ordered list (generated in Challenge 5), or pick a collection of related epics that can be implemented together. Given workshop time constraints, batching multiple epics into a single RPI run can fast-track development significantly.

Start a **new chat session** and select the **RPI Agent**:

```text
Implement GitHub issue #<issue-number>. Read the issue description for full acceptance criteria. Research the required patterns, plan the implementation, build it, and review the result.
```

The RPI Agent will automatically:

1. **Research** — Investigate patterns, libraries, and constraints
2. **Plan** — Create a phased implementation plan
3. **Implement** — Build the code following the plan
4. **Review** — Validate the implementation against the plan

**Let it run to completion.** Once finished, ask the agent what credentials or environment variables are needed and how to run the application:

```text
What credentials and environment setup do I need, and how do I run this locally?
```

Follow the agent's instructions to verify the application starts and responds correctly.

Then commit and close the issue. You can either use git directly or ask Copilot to do it:

```bash
git add .
git commit -m "feat: <description of what was implemented>

Closes #<issue-number>"

git push
```

Or simply ask Copilot:

```text
Commit all changes and close GitHub issue #<issue-number>
```

Copilot will use the GitHub MCP tools or CLI to commit, push, and close the issue for you.

### Step 2: Implement Remaining Epics

For each remaining epic in your ordered list, **choose the approach that fits the task**:

| Approach | When to Use |
|---|---|
| **Manual R→P→I→R** (Challenge 5, Step 2) | Complex epics, architectural decisions, tasks requiring human judgment at each phase |
| **RPI Autonomous Agent** (Step 1 above) | Smaller epics, well-defined tasks, no major decision-making needed |

Work through the remaining epics in order, committing and closing each issue as you go.

## Expected Project Structure

After completing Challenges 5 and 6, your project should look something like:

```text
smartassist-agent/
├── pyproject.toml
├── README.md
├── .env.example
├── src/
│   └── smartassist/
│       ├── __init__.py
│       ├── __main__.py
│       ├── config.py
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── router.py
│       │   └── billing.py
│       └── tools/
│           └── __init__.py
└── tests/
    └── __init__.py
```

## Success Criteria

- [ ] **RPI Autonomous Complete** — At least one epic implemented end-to-end by the RPI Agent
- [ ] **Application Runs** — `python -m smartassist` starts without errors
- [ ] **Agent Responds** — Sending a test message produces a response
- [ ] **Issues Closed** — GitHub issues closed via commits
- [ ] **Remaining Epics Addressed** — Additional epics implemented using whichever approach fits

## Hints

<details>
<summary>Hint 1: Agents using hardcoded keyword classification instead of Azure OpenAI</summary>

If the RPI Agent implements your router or classification logic using a hardcoded list of keywords (e.g., `if "billing" in message`) instead of making LLM calls via Azure OpenAI, guide it to use actual chat completions.

Run a revised prompt for the RPI Agent:

```text
Implement GitHub issue #<issue-number>. The agent classification and routing MUST use Azure OpenAI chat completion endpoints — do NOT use hardcoded keyword matching or rule-based classification. Use the Azure OpenAI SDK to call the chat endpoint for intent classification and agent responses.
```

This ensures the agents call Azure OpenAI for classification rather than relying on static keyword lists.

</details>

<details>
<summary>Hint 2: Choosing between manual R→P→I→R and RPI Agent</summary>

**Use manual R→P→I→R when:**

- The epic has ambiguous acceptance criteria that need interpretation
- You need to make architectural decisions that require your judgment
- The task touches foundational patterns that other epics depend on

**Use RPI Agent when:**

- The epic is a clear feature addition with well-defined scope
- There are no design decisions that require your judgment
- You've already established patterns in earlier epics that this one can follow

</details>

<details>
<summary>Hint 3: Environment configuration</summary>

Create a `.env.example` with required variables:

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

</details>

## Bonus

- Add unit tests for the router's classification logic
- Implement a simple CLI interface for testing conversations
- Add type hints throughout the codebase
