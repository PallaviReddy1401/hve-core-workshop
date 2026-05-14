# Challenge 4: PRD to GitHub Backlog

| <br />             | <br />                                                                                                                                   |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **Duration**       | 50 minutes                                                                                                                               |
| **Objective**      | Use research and ADR outputs to decompose the PRD into epics and user stories, then push them to GitHub using the GitHub Backlog Manager |
| **HVE-Core Stage** | Stage 4: Decomposition                                                                                                                   |
| **Agent**          | `GitHub Backlog Manager`                                                                                                                 |

## Prerequisites

You need the **GitHub MCP Server** configured and running in VS Code. If you haven't set this up yet, refer to [Challenge 0, Step 5](challenge-0.md#step-5-enable-github-mcp-server) for instructions.

### Enable Issues on Your Repository

1. Go to `https://github.com/<your-github-username>/gcid-workshop/settings`
2. Under **Features**, check **Issues** → **Save**

## Context

**Stage 4: Decomposition** breaks the PRD into implementable work items. Using your PRD and ADRs from Challenge 3, the `GitHub Backlog Manager` agent creates epics, user stories, labels, acceptance criteria, and dependency relationships as GitHub issues.

## Instructions

### Step 1: Start a Fresh Chat Session

Clear context between phases — open a new chat session.

### Step 2: Attach Your Artifacts

Add these files to the chat context:

- `docs/prd.md` — your PRD
- `docs/decisions/` — your ADRs from Challenge 3

### Step 3: Invoke the GitHub Backlog Manager

Select the **GitHub Backlog Manager** agent, then use this prompt:

```
Discover issues from this PRD and the attached ADRs. Create a GitHub backlog for the SmartAssist project.

Repository: <your-github-username>/smartassist-agent

Use the research findings and architecture decisions to inform issue structure. Create epics as parent issues and user stories as sub-issues.

Use "Epic" label for epics and "User Story" label for user stories. Create these labels if they do not already exist. Also apply priority labels (P0-must-have, P1-should-have, P2-future) and domain labels (billing-agent, technical-agent, general-agent, infrastructure, observability) — create any missing labels automatically.

Each issue must include acceptance criteria in Given/When/Then format.

Focus on P0 items first — these form our MVP sprint.

Use GitHub MCP tools to create the issues directly in the repository.

Important: Label all the MVP stories with "P0" so that these can be implemented for the initial MVP.
```

### Step 4: Review the Discovery Plan

The agent produces `issue-analysis.md` in `.copilot-tracking/github-issues/discovery/`. Before approving, check:

- Issues are sized for 1-2 RPI cycles
- Dependencies are identified
- Acceptance criteria match the PRD
- Issues reflect your ADR decisions

Approve to proceed with issue creation.

### Step 5: Verify the Backlog

```bash
gh issue list --state open --limit 30
```

### Step 6: Create MVP Milestone (Manual)

> [!NOTE]
> The Backlog Manager agent cannot create milestones. Create this manually.

**GitHub UI:**
Go to `https://github.com/<your-github-username>/gcid-workshop/milestones/new` → title **MVP - Sprint 1** → due date **2 weeks from today** → **Create milestone** → then assign all `P0-must-have` issues to it.

**GitHub CLI:**

```bash
gh api repos/<your-github-username>/gcid-workshop/milestones --method POST \
  -f title="MVP - Sprint 1" \
  -f due_on="$(date -v+14d -u +%Y-%m-%dT%H:%M:%SZ)" \
  -f description="Initial MVP sprint — all P0 must-have items"

gh issue list --label "P0-must-have" --json number --jq '.[].number' | \
  xargs -I {} gh issue edit {} --milestone "MVP - Sprint 1"
```

## Success Criteria

Your GitHub backlog must contain:

- **Epics Created** — At least 4 epic issues (infrastructure, billing, technical, general)
- **User Stories** — At least 10 issues linked as sub-issues to epics
- **Labels Applied** — Priority labels (P0/P1/P2) on all issues
- **Domain Labels** — Agent-type labels on relevant issues
- **Acceptance Criteria** — Each issue body contains Given/When/Then criteria
- **ADR Alignment** — Issues reflect architecture decisions from Challenge 3
- **Milestone** — MVP milestone created with P0 issues assigned
- **Dependencies** — Issues note their dependencies in the body
- **Sizing** — Issues are small enough for 1-2 RPI implementation cycles

## Example Issue Structure

```markdown
## Epic: Core Agent Infrastructure

### Issue: Set up Microsoft Agent Framework project structure
Labels: infrastructure, P0-must-have
Milestone: MVP - Sprint 1

**Description:**
Initialize the Python project with Microsoft Agent Framework,
configure the development environment, and establish the base
agent architecture.

**Acceptance Criteria:**
- Given: A developer clones the repository
- When: They run `pip install -e .` and `python -m smartassist`
- Then: The application starts without errors and responds to a health check

- Given: The project structure exists
- When: A new specialist agent needs to be added
- Then: There is a clear pattern to follow (base class, registration, routing)

**Dependencies:** None (this is the foundation)
**Complexity:** Medium
```

## Hints

<details>
<summary>Hint 1: Right-sizing issues for RPI</summary>

Each issue should be completable in a single RPI cycle (Research → Plan → Implement → Review). If an issue would take multiple days, break it down further:

```
Break down any issue estimated as XL into 2-3 smaller issues.
Each issue should be implementable in a single RPI cycle (typically 30-60 minutes of agent-assisted work).
```

</details>

<details>
<summary>Hint 2: Ordering for implementation</summary>

Ask the agent to suggest an implementation order:

```
Suggest an implementation order for the P0 issues based on dependencies.
Which issues must be completed first to unblock others?
```

A typical order:

1. Project setup + base agent class
2. Router agent
3. First specialist agent (billing — highest volume)
4. Escalation workflow
5. Observability basics

</details>

<details>
<summary>Hint 3: If issue creation fails</summary>

If the GitHub Backlog Manager cannot create issues:

1. Verify the GitHub MCP server is running — check the MCP status in Copilot Chat
2. Ensure you're in Agent mode (toggle in the Copilot Chat input area)
3. Try a simpler request first: "Create a single test issue titled 'Test' in my repo"
4. If the MCP server won't start, revisit [Challenge 0, Step 5](challenge-0.md#step-5-enable-github-mcp-server)

</details>

## Bonus

- Add story points or t-shirt sizing to each issue
- Create a project board view with columns: Backlog → In Progress → Review → Done
- Generate a sprint burndown estimate based on team velocity assumptions

