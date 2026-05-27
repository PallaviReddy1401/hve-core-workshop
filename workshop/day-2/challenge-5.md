# Challenge 5: Greenfield Implementation — Manual R→P→I→R Cycle

| | |
|---|---|
| **Duration** | 45 minutes |
| **Objective** | Use the manual R→P→I→R workflow to prioritize your backlog and implement the first core epic |
| **HVE-Core Stage** | Stage 6: Implementation |
| **Agents** | `GitHub Backlog Manager` → `Task Researcher` → `Task Planner` → `Task Implementor` → `Task Reviewer` |

## Introduction

This is where HVE-Core's RPI workflow shines. Instead of asking Copilot to "build me an agent" (which produces hallucinated, untested code), you will use the structured **Research → Plan → Implement → Review** cycle to build verified, working code. Each phase has a dedicated agent, and you drive the workflow manually — inspecting and validating outputs at every step. This gives you fine-grained control over architectural decisions and ensures research-backed implementation.

## Learning Objectives

By the end of this challenge, you will be able to:

- Use the `GitHub Backlog Manager` agent to prioritize and sequence epics for implementation
- Execute the full manual R→P→I→R cycle: Research, Plan, Implement, Review
- Use the `Task Researcher` agent to investigate implementation patterns before writing code
- Use the `Task Planner` agent to create actionable implementation plans from research
- Use the `Task Implementor` agent to build code that follows a verified plan
- Use the `Task Reviewer` agent to validate implementation against the plan
- Understand when manual R→P→I→R is preferred over autonomous execution

## Context

You will start by using the **GitHub Backlog Manager** agent to get a prioritized, ordered list of P0 epics. Then you'll implement the first epic using the **manual R→P→I→R cycle**, giving you fine-grained control over every phase. The RPI workflow ensures:

- Research verifies basic API scaffolding patterns before writing code
- Planning creates an actionable implementation checklist
- Implementation follows the plan with precision
- Review validates everything works

> [!IMPORTANT]
> In this workshop we run the RPI cycle on **epics** because the MVP scope is small and time is limited. In a real-world project, developers would run R→P→I→R on individual **user stories** — epics are too large for a single cycle and should be broken down first.

## Instructions

### Step 1: Get Your Ordered Epic List (GitHub Backlog Manager Agent)

Before diving into implementation, use the **GitHub Backlog Manager** agent to get a prioritized, ordered list of epics from your backlog. Start a **new chat session** and run:

```text
List down all the P0 epics that I can implement in order
```

The agent will analyze your backlog and return a sequenced list of epics based on priority and dependencies. **Save this list** — you will use it across this challenge and the next.

> [!IMPORTANT]
> The rough implementation order you want is:
>
> 1. Scaffolding / API creation
> 2. Router agent setup
> 3. Individual agents (Billing, General, Technical, etc.)
> 4. Telemetry
> 5. Security
>
> Epics 1–3 are required to get a basic working app. Telemetry, security, and other epics can be implemented later as needed. If the backlog manager's ordered list does not reflect this sequence on a high level, manually choose the order based on the list above.

Pick the **first epic** from the ordered list to begin implementation.

Note the issue number: `#___`

> [!NOTE]
> Before starting the implementation cycle below, review the `.github/copilot-instructions.md` file at the root of this repository. It defines project structure rules (no code files in the root), read-only folder boundaries, and coding conventions (async route handlers, RESTful design, Pydantic validation, UUID v4 identifiers, ISO 8601 dates, PEP 8 naming) that the implementation phase must follow.

### Step 2: Manual R→P→I→R Cycle — First Epic

> **Pick the first epic** from your ordered list. You will implement it using the manual R→P→I→R cycle, running each phase individually.

This approach gives you **fine-grained control over every step**. You drive each phase — Research, Plan, Implement, Review — one at a time, inspecting and validating outputs before moving on. This is essential when:

- The epic involves architectural decisions or design trade-offs
- You want to review and refine the research or plan before implementation begins
- The task is complex and benefits from human judgment between phases

#### 2a. Research Phase (Task Researcher)

Start a **new chat session** and select the **Task Researcher** agent. Point it directly at the GitHub issue so it pulls in all the context — acceptance criteria, labels, and linked epics — automatically:

```text
Research GitHub issue #<issue-number> for implementation. Include architecture patterns, required libraries, risks, and open questions.
```

Wait for the research document to be created in `.copilot-tracking/research/`.

**Review the research:** Open the generated file. Does it address the issue's acceptance criteria? Are the recommended patterns backed by real library APIs and documentation?

#### 2b. Plan Phase (Task Planner)

Clear context (`/clear` or new chat). Select the **Task Planner** agent. Add the research document from `.copilot-tracking/research/` to the chat context, then run:

```text
Plan the implementation for the attached research document
```

Review the plan in `.copilot-tracking/plans/`. Verify it references real APIs from the research.

#### 2c. Implement Phase (Task Implementor)

Clear context. Select the **Task Implementor** agent. Add the plan from `.copilot-tracking/plans/` to the chat context, then run:

```text
Implement the attached plan, follow each phase in order and verify before proceeding.
```

The implementor will:

1. Read the plan from `.copilot-tracking/plans/`
2. Create files according to the plan
3. Track changes in a changes log
4. Verify each step before proceeding

**Let it work autonomously.** Only intervene if it asks for clarification.

#### 2d. Review Phase (Task Reviewer)

Clear context. Select the **Task Reviewer** agent:

```text
Review the implementation for GitHub issue #<issue-number> against the plan in .copilot-tracking/plans/. Check for correctness, missing items, and code quality.
```

The reviewer will:

1. Check implementation against the plan
2. Verify code conventions
3. Run any validation commands
4. Identify issues or missing items

#### 2e. Verify and Commit

After the review, ask the same agent what credentials or environment variables are needed and how to run the application:

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

## Success Criteria

- [ ] **Ordered Backlog** — Prioritized epic list from GitHub Backlog Manager
- [ ] **Manual R→P→I→R Complete** — First epic implemented through the full manual cycle with research, plan, implementation, and review artifacts
- [ ] **Application Runs** — `python -m smartassist` starts without errors
- [ ] **Agent Responds** — Sending a test message produces a response
- [ ] **Issue Closed** — GitHub issue closed via commit

## Hints

<details>
<summary>Hint 1: When to use manual R→P→I→R</summary>

**Use manual R→P→I→R when:**

- You're building foundational infrastructure (first epic is always a good candidate)
- The epic has ambiguous acceptance criteria that need interpretation
- **Rule of Thumb:** If you need to understand something before implementing, use RPI.


| Use RPI When...                | Use Quick Edits When... |
|--------------------------------|-------------------------|
| Changes span multiple files    | Fixing a typo           |
| Learning new patterns/APIs     | Adding a log statement  |
| External dependencies involved | Refactoring < 50 lines  |
| Requirements are unclear       | Change is obvious       |



</details>

<details>
<summary>Hint 2: Environment configuration</summary>

Check if a `.env.example` file was created during implementation. If it exists, copy it to `.env` and fill in your actual values:

```bash
cp .env.example .env
```

Then update the values in .env with your Azure OpenAI resource details:
```env
AZURE_OPENAI_ENDPOINT=https://<your-project>.services.ai.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
```
Ensure your application loads these variables at startup (e.g., via python-dotenv or your framework's config module). An example below:

```python
import os
from dotenv import load_dotenv
load_dotenv()
```

</details>
