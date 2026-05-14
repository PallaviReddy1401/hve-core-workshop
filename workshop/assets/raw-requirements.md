# Raw Requirements: SmartAssist Customer Support Platform

The following is a raw brain-dump from the stakeholder meeting with Contoso Ltd. These are unstructured, sometimes contradictory notes from multiple stakeholders.

---

## Stakeholder Notes (Unedited)

**From VP of Customer Success (Sarah):**

> We need an AI-powered support system that can handle 70% of tickets without human intervention. Our support team is drowning - we get 2000+ tickets daily and our CSAT dropped to 3.2/5 last quarter. The AI should feel natural, not robotic. Customers hate chatbots. This needs to be different.

**From Head of Engineering (Marcus):**

> Whatever we build needs to integrate with our existing ticketing system via REST APIs. We're a Python shop. I don't want another JavaScript framework. It should be observable - we need to know when things go wrong before customers tell us. Also, it must handle multiple conversations simultaneously without mixing up context.

**From Product Manager (Priya):**

> Key scenarios: billing inquiries (40% of volume), technical troubleshooting (35%), general questions (20%), escalation to human (5%). Each needs different expertise. Billing questions need access to account data. Technical issues need our knowledge base. The system should know when it's out of its depth and hand off gracefully.

**From CISO (James):**

> No customer PII stored in conversation logs. All data in transit must be encrypted. The AI must never make up information about billing - if it doesn't know, it asks. We need audit trails. Must comply with SOC2 and GDPR. Azure-hosted only - no third-party AI providers outside our Azure tenant.

**From CTO (Lin):**

> I want this on Azure. We already have Foundry set up. Use our existing Azure OpenAI deployments. The architecture should allow us to add new specialized agents easily - next quarter we want to add a returns/refund agent and a proactive outreach agent. Think modular.

**From Support Team Lead (Diego):**

> When the AI escalates to us, we need full conversation history. The handoff should be seamless - customers shouldn't have to repeat themselves. Also, can the AI suggest responses to our agents for the tricky cases? That would be a huge productivity boost. Oh, and we need analytics - which topics are trending, what's the AI's resolution rate, average handling time.

**From UX Designer (Aisha):**

> The interaction should support both chat (web widget) and async messaging (email-style). Responses should be concise but complete. The AI should ask clarifying questions rather than guessing. It needs to maintain conversation context over multiple exchanges - not just one-shot Q\&A.

---

## MVP Scope

### Core API

- Expose a REST API for chat conversations using Azure Open AI (stateless request/response per turn). 
- Accept a user message and return an AI-generated response
- Maintain multi-turn conversation context within a session

### Query Classification & Routing

- Classify each incoming user query into one of three categories: **billing**, **tech-support**, or **general**
- Route the classified query to a dedicated agent:
  - **Billing Agent** — handles account and payment inquiries
  - **Tech-Support Agent** — handles product and technical troubleshooting
  - **General Agent** — handles all other informational queries
- When the AI cannot resolve a query, return a clear indication that human escalation is needed (no live handoff in MVP)

### Storage

- Use file-based or in-memory local storage for conversation history (no external database in MVP)

### Out of MVP Scope

The following are deferred to post-MVP phases:

- Web chat widget and email/async channel support
- Live human-agent handoff and agent-assist (suggested responses)
- Integration with external systems (Zendesk, Stripe, Confluence)
- PII redaction, SOC2/GDPR compliance, and audit trails
- Analytics dashboards (resolution rate, trending topics, handling time)
- Proactive outreach and returns/refund agent

## Additional Context

- Current stack: Python 3.11, Azure
- Timeline: MVP in 8 weeks, full launch in 16 weeks
- Team: 4 backend engineers, 1 ML engineer, 1 DevOps
- Budget: Azure consumption-based, no hard cap for MVP

---

## Contradictions and Ambiguities Noted

- Sarah wants "not robotic" but James wants strict guardrails on billing info
- Priya says 5% escalation but Diego wants AI-suggested responses (implies higher human involvement)
- Aisha wants email-style async but Marcus wants real-time multi-conversation handling
- Lin says "modular" but no specific interface contracts mentioned
- Timeline pressure vs. SOC2/GDPR compliance requirements

