# HVE-Core Quick Reference Card

## HVE-Core Lifecycle Stages

```
Setup → Discovery → Product Definition → Decomposition → Sprint Planning → Implementation → Review → Delivery → Operations
```

## Key Prompts

| Prompt | Purpose | Agent |
|--------|---------|-------|
| `/task-research topic="..."` | Start research phase | Task Researcher |
| `/task-plan` | Create implementation plan | Task Planner |
| `/task-implement` | Execute the plan | Task Implementor |
| `/task-review` | Validate implementation | Task Reviewer |
| `/rpi task="..."` | Autonomous full cycle | RPI Agent |
| `/rpi continue=1` | Continue with suggestion #1 | RPI Agent |
| `/rpi continue=all` | Process all suggestions | RPI Agent |
| `/rpi suggest` | Discover next work items | RPI Agent |

## Critical Rule

> Always clear context between RPI phases: `/clear` or start a new chat.

Research findings persist in files, not in chat context.

## Agent Picker

Switch agents via the dropdown in Copilot Chat:

- **Task Researcher** — Research only, produces `.copilot-tracking/research/` docs
- **Task Planner** — Plans only, produces `.copilot-tracking/plans/` docs
- **Task Implementor** — Implements from plans, tracks in changes log
- **Task Reviewer** — Validates against plan and research
- **RPI Agent** — Does all phases autonomously
- **GitHub Backlog Manager** — Creates/manages GitHub issues from documents

## Tracking Files

All HVE-Core state lives in `.copilot-tracking/`:

```
.copilot-tracking/
├── research/          # Research documents
│   └── YYYY-MM-DD/
├── plans/             # Implementation plans
│   └── logs/          # Planning logs
├── details/           # Implementation details
├── github-issues/     # Backlog management state
│   ├── discovery/
│   ├── triage/
│   └── execution/
└── doc-ops/           # Documentation operations
```

## RPI Agent Handoff Buttons

| Button | Action |
|--------|--------|
| Compact | Summarize session for context limit |
| 1️⃣ 2️⃣ 3️⃣ | Continue with specific suggestion |
| ▶️ All | Process all suggestions |
| 🔄 Suggest | Discover next work items |
| 💾 Save | Checkpoint session to memory |

## Useful Commands

```bash
# GitHub CLI
gh issue list                    # List issues
gh issue create --title "..."    # Create issue
gh issue close <number>          # Close issue

# Azure CLI
az login                         # Authenticate
az account show                  # Current subscription
az group create --name <n> --location eastus2

# Python
pip install -e .                 # Install in dev mode
pytest tests/ -v                 # Run tests
pytest tests/ -m "not integration"  # Skip integration tests
```
