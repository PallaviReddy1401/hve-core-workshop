# Challenge 3: Technical Research and Architecture Decisions

| | |
|---|---|
| **Duration** | 40 minutes |
| **Objective** | Research technical approaches from the PRD and formalize architecture decisions as ADRs |
| **HVE-Core Stage** | Stage 4: Research |
| **Agents** | `Task Researcher` |

## Introduction

Before jumping into implementation, strong engineering teams invest in **technical research** to explore the problem space, surface risks, and compare alternative approaches. In this challenge, you will use the `Task Researcher` agent to investigate technical patterns informed by your PRD — covering agent handoff strategies, memory architectures, deployment options, and observability patterns. The research output provides the evidence base for informed architecture decisions.

## Learning Objectives

By the end of this challenge, you will be able to:

- Use the `Task Researcher` agent to explore technical approaches from a PRD
- Compare multiple implementation options with documented trade-offs
- Identify technical risks and unknowns before committing to an approach
- Understand the role of Architecture Decision Records (ADRs) in capturing the *why* behind choices
- Produce a research document that informs downstream planning and implementation

## Context

| Activity | Input | Output | Agent |
|----------|-------|--------|-------|
| Technical Research | PRD | Research document with tech recommendations | Task Researcher |

## Instructions

### Technical Research

#### Step 1: Clear Context and Start Fresh

**Critical:** Start a new chat session. Clear context between phases.

Open GitHub Copilot Chat → New Chat (`Ctrl+Alt+I`).

#### Step 2: Attach Your PRD

Attach your `docs/prds/prdname.md` file to the chat context.

#### Step 3: Run Task Researcher on the PRD

Select the **Task Researcher** agent in Copilot Chat, then use this prompt to explore the problem space:

```
Research the technical approaches for implementing SmartAssist based on this PRD.

Focus on:
- How to implement handoff between router and specialist agents
- Conversation memory strategies (session-level vs persistent)
- Azure AI Foundry deployment options
- Observability patterns with OpenTelemetry for agent systems

Produce a research document summarizing findings, recommended approaches, trade-offs, and risks.


```

#### Step 4: Review the Research Output

The researcher produces a document in `.copilot-tracking/`. Review it for:

- Are multiple approaches compared for key decisions?
- Are trade-offs clearly articulated?
- Are risks and unknowns surfaced?

Save or note the research output path for the next part.

> [!NOTE]
> **Architecture Decision Records (ADRs)**
>
> ADRs are lightweight documents that capture the *why* behind key technical choices. They help current and future team members understand the reasoning, constraints, and trade-offs that informed a decision — preventing repeated debates and preserving institutional knowledge.
>
> A typical ADR includes the decision context, options considered, the chosen approach, and its consequences.
>
> HVE-Core includes an **ADR Creation** agent that can guide teams through authoring ADRs using a Socratic coaching approach. If your team wants to formalize decisions, try it after this challenge with your research output + PRD as input.

## Success Criteria

- [ ] **Research Document** — Task Researcher produced a document exploring technical approaches
- [ ] **Multiple Options** — At least 2 approaches compared for key architectural decisions
- [ ] **Trade-offs Documented** — Pros, cons, and risks identified for each approach

## Hints

<details>
<summary>Hint 1: Guiding the Task Researcher</summary>

If the researcher output is too generic, provide more specific research questions:

```
Specifically research:
- What are the common patterns for multi-turn routing in multi-agent systems?
- What are the patterns for agent handoff vs agent delegation?
- How does FoundryChatClient manage token limits across conversation turns?
```

</details>

<details>
<summary>Hint 2: Structuring the research output</summary>

If the research output is unstructured, ask for a comparison table:

```text
For each architectural decision (handoff strategy, memory architecture, observability), present a comparison table with columns: Option, Pros, Cons, Risks, Recommendation.
```

## Bonus

- Use the **ADR Creation** agent to formalize one or more architecture decisions from your research
- Research additional areas: observability strategy, testing approach, or CI/CD pipeline design
- Document a phased rollout plan (MVP → V1.1 → V2.0) in your research output

