# Challenge 2: Business Requirements Document to Product Requirements Document (PRD)

| <br />             | <br />                                                                            |
| ------------------ | --------------------------------------------------------------------------------- |
| **Duration**       | 30 minutes                                                                        |
| **Objective**      | Transform the BRD into a technical PRD using HVE-Core's product definition agents |
| **HVE-Core Stage** | Stage 3: Product Definition                                                       |
| **Agent**          | `PRD Builder`                                                                     |

## Introduction

With business requirements captured in a BRD, the next step is translating them into a technical product specification that engineering teams can act on. In the HVE-Core lifecycle, **Stage 3: Product Definition** bridges the gap between *what the business wants* and *what engineers will build*. You will use the `PRD Builder` agent to produce a Product Requirements Document containing user stories, acceptance criteria, architecture decisions, and a feature breakdown suitable for backlog creation.

## Learning Objectives

By the end of this challenge, you will be able to:

- Use the `PRD Builder` agent to transform a BRD into a technical product specification
- Distinguish between BRD-level (business outcomes) and PRD-level (technical capabilities) writing
- Define user stories with clear acceptance criteria
- Establish MVP scope boundaries using priority tagging (P0/P1/P2)
- Document non-functional requirements including performance, security, and scalability

## Context

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
- [ ] **Architecture Decision** —  Technology stack chosen with rationale
- [ ] **Priority** — Each story tagged P0/P1/P2
- [ ] **Technical Constraints** — Python, Azure, Foundry, SOC2/GDPR noted
- [ ] **MVP Boundary** — Clear P0 feature set that forms the MVP
- [ ] **Non-Functional Requirements** — Performance, security, scalability specs

## Hints

<details>
<summary>Hint 1: Ensuring PRD-level writing vs BRD-level</summary>

If the PRD Builder output reads like a summary of the BRD rather than a technical product spec, redirect it:

```
This reads like business requirements. Rewrite as a PRD targeting the engineering team:
- Replace business outcomes with technical capabilities and feature specifications
- Add a product overview paragraph describing what SmartAssist is technically
- List technical constraints explicitly (Python, Azure Foundry, SOC2, GDPR)
- Tag every feature with a priority level (P0, P1, or P2)
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

<details>
<summary>Hint 3: Defining a clear MVP boundary</summary>

If the PRD lacks a clear MVP scope or everything seems equally prioritized, ask the agent to draw the line:

```text
Define the MVP boundary explicitly. Mark which features are P0 (must-have for launch), P1 (fast-follow), and P2 (future). The MVP should be the smallest set of P0 features that delivers core value to users. Include a summary table showing the MVP feature set vs deferred items.
```

</details>

## Bonus

- Ask the PRD Builder to generate a feature dependency map showing which capabilities must be built before others
- Add a stakeholder communication matrix to the PRD (who needs to know what, and when)
- Include a risk register section identifying top technical and product risks with mitigation strategies

