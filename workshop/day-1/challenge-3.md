# Challenge 3: Technical Research and Architecture Decisions

| | |
|---|---|
| **Duration** | 40 minutes |
| **Objective** | Research technical approaches from the PRD and formalize architecture decisions as ADRs |
| **HVE-Core Stage** | Stage 4: Research |
| **Agents** | `Task Researcher` |

## Context

Before jumping into implementation, strong engineering teams invest in **technical research** and **architecture decisions**. This challenge covers a critical activity:

- **Task Research** — Explore the problem space from the PRD, surface technical risks, and recommend approaches


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

IMPORTANT: Use only the attached file as context for this research. Do not use workspace files, prior conversation history, or 
any other external context.

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
- How does AgentGroupChat in Microsoft Agent Framework handle multi-turn routing?
- What are the patterns for agent handoff vs agent delegation?
- How does FoundryChatClient manage token limits across conversation turns?
```

</details>

</details>

## Bonus

- Use the **ADR Creation** agent to formalize one or more architecture decisions from your research
- Research additional areas: observability strategy, testing approach, or CI/CD pipeline design
- Document a phased rollout plan (MVP → V1.1 → V2.0) in your research output

