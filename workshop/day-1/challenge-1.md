# Challenge 1: Raw Requirements to Business Requirements Document (BRD)

| | |
|---|---|
| **Duration** | 30 minutes |
| **Objective** | Use HVE-Core's discovery agents to transform raw stakeholder notes into a structured BRD |
| **HVE-Core Stage** | Stage 2: Discovery |
| **Agent** | `brd-builder` |

## Introduction

In the HVE-Core lifecycle, **Stage 2: Discovery** is where unstructured information becomes structured knowledge. Real-world projects begin with scattered inputs — meeting notes, emails, stakeholder conversations — that must be distilled into a coherent understanding of what the business needs. In this challenge, you will use the `brd-builder` agent to analyze raw stakeholder notes and produce a Business Requirements Document (BRD) that captures business objectives, stakeholder needs, constraints, and scope boundaries. The BRD is a **business-facing** document: it describes *what* the business needs, not *how* to build it technically.

## Learning Objectives

By the end of this challenge, you will be able to:

- Use the `BRD Builder` agent to transform unstructured stakeholder inputs into a structured document
- Identify and reconcile contradictions between competing stakeholder priorities
- Define clear scope boundaries (in-scope, out-of-scope, future-scope)
- Produce measurable business objectives with quantifiable success criteria
- Iterate on agent output to refine and improve document quality

## Your Raw Requirements

Open the file `workshop/assets/raw-requirements.md` in your editor. These are the raw stakeholder notes from Contoso Ltd's SmartAssist project.

Use `workshop/assets/raw-requirements.md` as the primary context for the BRD builder. This file is already a cleaned, processed, and summarized version of the stakeholder inputs.

> **Note:** You can alternatively use the meeting transcripts in `workshop/assets/meeting_transcripts/` as the primary context if you want the BRD builder to work from the original source conversations.

## Instructions

### Step 1: Start a New Copilot Chat Session

Open GitHub Copilot Chat (`Ctrl+Alt+I`).

### Step 2: Choose and Attach Context

Attach `workshop/assets/raw-requirements.md` to your chat.

> **Note:** If you prefer to derive the BRD from the original meeting transcripts, attach files from `workshop/assets/meeting_transcripts/` instead (or in addition to the raw requirements as supporting evidence). A Statement of Work (SOW) document can also be used as a source for generating your BRD.

### Step 3: Invoke the BRD Builder

Select the `BRD Builder` agent in Copilot Chat, then use this prompt:

```
Create a Business Requirements Document from the attached SmartAssist stakeholder context. Identify business objectives, reconcile contradictions between stakeholders, define scope boundaries, and produce a structured BRD.
```

### Step 4: Review the BRD Output

The agent will create a BRD document in `docs/brds/<brd_name.md>`. Review it for:

- Did it identify all 7 stakeholders?
- Did it reconcile the contradictions noted in the raw requirements?
- Are business objectives quantified (e.g., "70% automated resolution")?
- Are scope boundaries clear?

### Step 5: Refine the BRD

If the initial output misses key elements, iterate:

```
Continue researching. Ensure the BRD covers:
1. Explicit success metrics with measurable targets
2. Resolution of the security vs. UX tension (James vs. Sarah)
3. Clear MVP scope vs. future scope boundary
4. Compliance requirements mapped to specific capabilities
```

### Step 6: Save the BRD

Ensure your final BRD is saved as `docs/brds/brdname.md` in your project repository. The document should follow this structure:

```
docs/
└── brds/
	└── brdname.md
```

## Success Criteria

Your BRD must contain:

- [ ] **Business Objectives** — At least 3 measurable objectives with KPIs
- [ ] **Stakeholder Registry** — All stakeholders listed with their primary concerns
- [ ] **Requirements** — Functional requirements categorized by domain (billing, technical, general)
- [ ] **Constraints** — Technical, compliance, and timeline constraints documented
- [ ] **Scope** — Clear in-scope / out-of-scope / future-scope boundaries
- [ ] **Contradictions Resolved** — Documented decisions on conflicting requirements
- [ ] **Assumptions** — Explicit assumptions that could invalidate requirements if wrong
- [ ] **Success Metrics** — Quantifiable criteria for project success

## Hints

<details>
<summary>Hint 1: Getting better results from the agent</summary>

Provide explicit structure in your prompt. The agent works best when you tell it what sections you expect:

```
Research and produce a BRD with these sections:
- Executive Summary
- Business Objectives & KPIs
- Stakeholder Analysis
- Functional Requirements (grouped by domain)
- Non-Functional Requirements
- Constraints & Assumptions
- Scope Definition (In/Out/Future)
- Risk Register
```

</details>

<details>
<summary>Hint 2: Resolving contradictions</summary>

Ask the agent to apply a priority framework:

```
Resolve contradictions using this priority: Security/Compliance > Business Value > User Experience > Technical Preference. Document the trade-off decision for each conflict.
```

</details>

<details>
<summary>Hint 3: Checking completeness</summary>

After generating the BRD, ask:

```
Review this BRD against ISO/IEC 29148 requirements documentation standards. What sections are missing or incomplete?
```

</details>

## Bonus

- Add a RACI matrix showing which stakeholder owns/approves each requirement area
- Create a requirements traceability seed (requirement ID → stakeholder → priority)
- Identify 3 questions you would ask stakeholders to fill remaining gaps
