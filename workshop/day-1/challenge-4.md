# Challenge 4: PRD to GitHub Backlog

| <br />             | <br />                                                                                                                                   |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **Duration**       | 50 minutes                                                                                                                               |
| **Objective**      | Use research and ADR outputs to decompose the PRD into epics and user stories, then push them to GitHub using the GitHub Backlog Manager |
| **HVE-Core Stage** | Stage 4: Decomposition                                                                                                                   |
| **Agent**          | `GitHub Backlog Manager`                                                                                                                 |

## Introduction

A PRD describes what to build, but engineers need a prioritized, decomposed backlog of implementable work items. In the HVE-Core lifecycle, **Stage 4: Decomposition** breaks the PRD into epics, user stories, labels, and dependency relationships — creating a structured backlog ready for sprint planning. You will use the `GitHub Backlog Manager` agent to generate GitHub issues directly from your PRD, complete with acceptance criteria, priority labels, and parent-child relationships.

## Learning Objectives

By the end of this challenge, you will be able to:

- Use the `GitHub Backlog Manager` agent to decompose a PRD into GitHub issues
- Create epics as parent issues and user stories as sub-issues with proper hierarchy
- Apply structured labeling conventions (priority, domain, type) to issues
- Write acceptance criteria in Given/When/Then format
- Create milestones and assign prioritized work items for sprint planning
- Use the GitHub MCP server to interact with GitHub directly from Copilot Chat

## Prerequisites

You need the **GitHub MCP Server** configured and running in VS Code. If you haven't set this up yet, refer to [Challenge 0, Step 5](challenge-0.md#step-5-enable-github-mcp-server) for instructions.

### Enable Issues on Your Repository

1. Go to `https://github.com/<your-github-username>/hve-core-workshop/settings`
2. Under **Features**, check **Issues** → **Save**

## Instructions

### Step 1: Start a Fresh Chat Session

Clear context between phases — open a new chat session.

### Step 2: Attach Your Artifacts

Add the context documents to the chat context:

- `docs/prds/<your-prd>.md` — your PRD
- `.copilot-tracking/research/<date>/<research_file_name>.md` — your research doc from previous step

### Step 3: Invoke the GitHub Backlog Manager

Select the **GitHub Backlog Manager** agent, then use this prompt:

```
Discover issues from the attached PRD. Plan a GitHub backlog for the SmartAssist project.

Use the research findings and architecture decisions to inform issue structure. Plan epics as parent issues and user stories as sub-issues.

Use "Epic" label for epics and "User Story" label for user stories. Also plan priority labels (P0-must-have, P1-should-have, P2-future) and domain labels (billing-agent, technical-agent, general-agent, infrastructure, observability).

Each issue must include acceptance criteria in Given/When/Then format.

Focus on P0 items first — these form our MVP sprint.

Important: Do NOT create issues in GitHub yet. Only produce the discovery plan so I can review it first. Label all the MVP stories with "P0" so that these can be implemented for the initial MVP.
```

### Step 4: Review the Discovery Plan

The agent produces `issue-analysis.md` in `.copilot-tracking/github-issues/discovery/`. Before approving, check:

- Issues are sized for 1-2 RPI cycles
- Dependencies are identified
- Acceptance criteria match the PRD
- Issues reflect your ADR decisions

If anything needs adjustment, ask the agent to revise the plan before proceeding.

### Step 5: Create Issues in GitHub

Once you are satisfied with the discovery plan, tell the agent to push the issues:

```
The discovery plan looks good. Now create all the planned issues in GitHub.

Prefer the GitHub MCP server tools to create the labels, epics, and user stories. If the GitHub MCP server is not available or any MCP tool call fails, fall back to the `gh` CLI to create labels and issues instead.

Create the labels if they do not already exist. Create epics first, then create user stories as sub-issues linked to their parent epics.
```

### Step 6: Verify the Backlog

```bash
gh issue list --state open --limit 30
```

### Step 7: Create MVP Milestone and Assign P0 Issues

> [!NOTE]
> The Backlog Manager agent cannot create milestones. Create the milestone manually first, then use **either** the GitHub Backlog Manager agent **or** GitHub CLI to assign your P0 issues to it.

**Create the milestone (GitHub UI):**

Go to `https://github.com/<your-github-username>/hve-core-workshop/milestones/new` → title **MVP - Sprint 1** → due date **2 weeks from today** → **Create milestone**.

**Create the milestone (GitHub CLI):**

```bash
gh api repos/<your-github-username>/gcid-workshop/milestones --method POST \
  -f title="MVP - Sprint 1" \
  -f due_on="$(date -v+14d -u +%Y-%m-%dT%H:%M:%SZ)" \
  -f description="Initial MVP sprint — all P0 must-have items"
```

**Assign P0 issues to the milestone — pick whichever approach you prefer:**

**Option A: Using GitHub Backlog Manager agent**


Ask the agent to move your P0 issues into the milestone:

```text
Assign all issues labeled "P0-must-have" to the "MVP - Sprint 1" milestone.
```

**Option B: UsingGitHub CLI**

```bash
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
<summary>Hint 1: Right-sizing issues forimplementation</summary>

Each issue should be small enough to implement in a single focused session (typically 30–60 minutes of agent-assisted work). If an issue would take multiple days, break it down further:

```text
Break down any issue estimated as XL into 2-3 smaller issues.
Each issue should be implementable in a single focused session with clear start and end points.
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

