# HVE-Core Workshop: From Requirements to Production AI Agents

> **This is a reference repository.** Do not work directly in this repo. Each participant must fork this repository into their own GitHub account and use the fork to carry out workshop tasks. This repo serves as the source for challenge instructions, templates, and reference materials only.

A hands-on, challenge-based workshop (3 days × 3 hours) that teaches the full Hypervelocity Engineering (HVE-Core) lifecycle: transforming raw stakeholder requirements into a production-ready AI agent deployed on Azure.

## Workshop Overview

Participants build **SmartAssist**, a multi-agent customer support platform for Contoso Ltd., while mastering HVE-Core's AI-assisted development workflows.

| Day | Theme                    | Duration | Focus                                                    |
|-----|--------------------------|----------|----------------------------------------------------------|
| 1   | Requirements to Backlog  | 3 hours  | BRD → PRD → Architecture → GitHub Backlog                |
| 2   | Implementation with RPI  | 3 hours  | Manual R→P→I→R → Autonomous RPI → Evaluation             |
| 3   | Evolve & Deploy          | 3 hours  | Brownfield refactor → Azure Deployment                   |

## The Problem Statement

The workshop uses a realistic product scenario drawn from [raw-requirements.md](workshop/assets/raw-requirements.md): Contoso Ltd. handles 2,000+ support tickets daily with declining customer satisfaction (CSAT 3.2/5). Stakeholders across engineering, product, security, and UX have contributed unstructured, sometimes contradictory requirements for an AI-powered support system.

The MVP scope defines a focused deliverable:

- A REST API exposing multi-turn chat conversations powered by Azure OpenAI
- Query classification and routing to three specialized agents (billing, tech-support, general)
- Graceful escalation signaling when the AI cannot resolve a query
- In-memory conversation history (no external database)

Participants use HVE-Core agents to progressively refine these raw notes into structured requirements, architecture, code, evaluations, and a deployed service.

## End-to-End Flow

The workshop follows a continuous pipeline from discovery through deployment. Each stage builds on the previous output. Day 1 focuses on understanding and structuring the problem. Day 2 shifts to building and validating working software. Day 3 evolves the codebase to a production-grade framework and deploys it to Azure.

```text
┌──────────────┐    ┌─────┐    ┌─────┐    ┌─────────┐    ┌───────────┐    ┌──────────┐    ┌───────────┐    ┌──────────┐    ┌──────────┐
│    Raw       │    │     │    │     │    │         │    │           │    │          │    │           │    │          │    │          │
│ Requirements ├───►│ BRD ├───►│ PRD ├───►│ Backlog ├───►│ Research  ├───►│   Plan   ├───►│ Implement ├───►│  Review  ├───►│  Deploy  │
│              │    │     │    │     │    │         │    │           │    │          │    │           │    │          │    │          │
└──────────────┘    └─────┘    └─────┘    └─────────┘    └───────────┘    └──────────┘    └───────────┘    └──────────┘    └──────────┘
```

## What You Will Build

A multi-agent customer support system (SmartAssist) that:

- Routes customer queries to specialized sub-agents (billing, technical, general)
- Maintains conversation context across multi-turn interactions
- Classifies intent and delegates to the appropriate domain agent
- Signals escalation when queries exceed agent capability
- Deploys as a hosted agent on Azure via Microsoft Foundry

## Challenge Details

### Day 1: Requirements to Backlog

| Challenge | Title | Description |
|-----------|-------|-------------|
| [Challenge 0](workshop/day-1/challenge-0.md) | Environment Setup & Verification | Install and verify all tools, extensions, and accounts needed for the workshop |
| [Challenge 1](workshop/day-1/challenge-1.md) | Raw Requirements → BRD | Use the BRD Builder agent to transform unstructured stakeholder notes into a structured Business Requirements Document |
| [Challenge 2](workshop/day-1/challenge-2.md) | BRD → PRD | Use the PRD Builder agent to convert the BRD into a detailed Product Requirements Document with user stories and acceptance criteria |
| [Challenge 3](workshop/day-1/challenge-3.md) | Technical Research & Architecture Decisions | Use the Task Researcher and ADR Creation agents to explore technical options and document architecture decisions |
| [Challenge 4](workshop/day-1/challenge-4.md) | PRD → GitHub Backlog | Use the GitHub Backlog Manager agent to decompose the PRD into epics, user stories, and tasks as GitHub issues |

### Day 2: Implementation with RPI

| Challenge | Title | Description |
|-----------|-------|-------------|
| [Challenge 5](workshop/day-2/challenge-5.md) | Greenfield: Manual R→P→I→R Cycle | Walk through the full Research → Plan → Implement → Review cycle manually using individual agents |
| [Challenge 6](workshop/day-2/challenge-6.md) | RPI Autonomous Agent — Remaining Epics | Use the RPI Agent to autonomously complete remaining backlog items end-to-end |
| [Challenge 7](workshop/day-2/challenge-7.md) | First Evaluation Run | Create evaluation datasets and run the first quality assessment of the built agents |

### Day 3: Evolve & Deploy

| Challenge | Title | Description |
|-----------|-------|-------------|
| [Challenge 8](workshop/day-3/challenge-8.md) | Brownfield: Refactor to Microsoft Agent Framework | Refactor the existing implementation to the Microsoft Agent Framework for Foundry compatibility |
| [Challenge 9](workshop/day-3/challenge-9.md) | Deploy to Azure | Deploy the refactored agent to Azure using Microsoft Foundry |


## Workshop Structure

```text
workshop/
├── day-1/                    # Requirements to Backlog
│   ├── challenge-0.md        # Environment Setup & Verification
│   ├── challenge-1.md        # Raw Requirements → BRD
│   ├── challenge-2.md        # BRD → PRD
│   ├── challenge-3.md        # Technical Research & Architecture Decisions
│   └── challenge-4.md        # PRD → GitHub Backlog
├── day-2/                    # Implementation with RPI
│   ├── challenge-5.md        # Greenfield: Manual R→P→I→R Cycle
│   ├── challenge-6.md        # RPI Autonomous Agent — Remaining Epics
│   └── challenge-7.md        # First Evaluation Run
├── day-3/                    # Evolve & Deploy
│   ├── challenge-8.md        # Brownfield: Refactor to Microsoft Agent Framework
│   └── challenge-9.md        # Deploy to Azure
└── assets/                   # Starter files and reference materials
    ├── raw-requirements.md   # Stakeholder requirements (workshop input)
    ├── quick-reference.md    # Quick reference guide
    ├── meeting_transcripts/  # Stakeholder meeting transcripts
    └── reference_images/     # Setup reference screenshots
```

## HVE-Core Agents Used

| Agent                      | Stage              | Purpose                                                          |
|----------------------------|--------------------|------------------------------------------------------------------|
| `BRD Builder`              | Discovery          | Transform raw requirements into a Business Requirements Document |
| `PRD Builder`              | Product Definition | Transform BRD into a Product Requirements Document               |
| `Task Researcher`          | Research           | Research codebase, patterns, and architecture                    |
| `Task Planner`             | Planning           | Create implementation plans                                      |
| `ADR Creation`             | Architecture       | Document architectural decisions                                 |
| `GitHub Backlog Manager`   | Decomposition      | Convert PRD into actionable GitHub issues                        |
| `Task Implementor`         | Implementation     | Execute plans with precision                                     |
| `Task Reviewer`            | Review             | Validate implementations against acceptance criteria             |
| `RPI Agent`                | Orchestration      | Autonomous end-to-end Research → Plan → Implement → Review       |
| `Evaluation Dataset Creator` | Evaluation       | Generate evaluation datasets for agent testing                   |

## Challenge Format

Each challenge follows a consistent structure:

1. **Objective** — What you will accomplish
2. **Context** — Background and HVE-Core concepts
3. **Instructions** — Step-by-step guidance
4. **Success Criteria** — How to verify completion
5. **Hints** — Progressive hints (try without them first)
6. **Bonus** — Stretch goals for fast movers

## License

MIT
