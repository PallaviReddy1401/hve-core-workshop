# Challenge 2: Business Requirements Document to Product Requirements Document (PRD)

| | |
|---|---|
| **Duration** | 30 minutes |
| **Objective** | Transform the BRD into a technical PRD using HVE-Core's product definition agents |
| **HVE-Core Stage** | Stage 3: Product Definition |
| **Agent** | `PRD Builder` |

## Context

In the HVE-Core lifecycle, **Stage 3: Product Definition** transforms business requirements into a technical product specification. The PRD bridges the gap between *what the business wants* and *what engineers will build*.

A PRD differs from a BRD in critical ways:

| Aspect | BRD | PRD |
|--------|-----|-----|
| Audience | Business stakeholders | Engineering team |
| Language | Business outcomes | Technical capabilities |
| Granularity | High-level objectives | Feature-level specifications |
| Format | Narrative + metrics | User stories + acceptance criteria |

The `prd-builder` agent (or Task Planner in product definition mode) reads your BRD and produces user stories with acceptance criteria, technical architecture decisions, and a feature breakdown suitable for backlog creation.

## Instructions

### Step 1: Clear Context and Start Fresh

**Critical:** Start a new chat session. Every new task agent requires clear context between phases.

Open GitHub Copilot Chat → New Chat (`Ctrl+Alt+I`).

### Step 2: Attach Your BRD

Attach your `docs/brds/brdname.md` file to the chat context.

### Step 3: Invoke the PRD Builder

Select the `PRD builder` agent in Copilot Chat, then use this prompt:

```
Transform this BRD into a Product Requirements Document for SmartAssist.
```

### Step 4: Save the PRD

Save the final PRD as `docs/prds/prdname.md`:

```
docs/
├── brds/
│   └── brdname.md
└── prds/
	└── prdname.md
```

## Success Criteria

Your PRD must contain:

- [ ] **Product Overview** — One-paragraph description of what SmartAssist is
- [ ] **Architecture Decision** — Microsoft Agent Framework chosen with rationale
- [ ] **Priority** — Each story tagged P0/P1/P2
- [ ] **Technical Constraints** — Python, Azure, Foundry, SOC2/GDPR noted
- [ ] **MVP Boundary** — Clear P0 feature set that forms the MVP
- [ ] **Non-Functional Requirements** — Performance, security, scalability specs

## Hints

<details>
<summary>Hint 1: Getting the right architecture framing</summary>

Help the agent understand the target architecture:

```
The system uses Microsoft Agent Framework (Python). Architecture:
- A Router Agent receives all incoming messages
- Specialized sub-agents handle domains (billing, technical, general)
- Handoff workflow for escalation to human agents
- FoundryChatClient connects to Azure OpenAI
- OpenTelemetry for observability
```

</details>

<details>
<summary>Hint 2: MVP scoping</summary>

If the agent produces too many features, constrain it:

```
MVP (P0) scope is limited to:
- Single router agent with 3 specialist agents
- Text-only chat interface (no email/async yet)
- Basic conversation memory (session-level, not persistent)
- Simple escalation (transfer context, no AI-suggested responses)
- Basic telemetry (request count, latency, error rate)
```

</details>

## Bonus

- Create a C4 architecture diagram description (context + container level)
- Define the agent communication protocol (message format between router and specialists)
- Add a phased rollout plan (MVP → V1.1 → V2.0) with feature mapping
