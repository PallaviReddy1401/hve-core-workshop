---
title: SmartAssist Product Requirements Document
description: Product behavior, functional requirements, release criteria, and measurement plan for the SmartAssist customer support platform
author: Contoso Ltd.
ms.date: 2026-09-20
ms.topic: concept
keywords:
  - SmartAssist
  - customer support
  - product requirements
  - Azure AI
estimated_reading_time: 18
---

## Document control

| Field                 | Value                                                                                      |
| --------------------- | ------------------------------------------------------------------------------------------ |
| Document status       | Draft for product, engineering, security, and UX review                                    |
| Version               | 0.1                                                                                        |
| Product owner         | Product Manager                                                                            |
| Business owner        | VP of Customer Success                                                                     |
| Technical owner       | Head of Engineering                                                                        |
| Security approver     | CISO                                                                                       |
| Source document       | [SmartAssist Business Requirements Document](../brds/smartassist-business-requirements.md) |
| Delivery milestones   | MVP at 8 weeks; target production launch at 16 weeks                                       |

## Product summary

SmartAssist is an Azure-hosted customer support service that understands an
incoming request, routes it to the appropriate specialist, maintains context
across a conversation, and either provides a grounded response or identifies
that human support is required.

The minimum viable product (MVP) is a controlled, non-production API validation.
It supports billing policy, technical support, and general inquiries using
synthetic or de-identified data. It does not connect to production customer
systems or serve production customer traffic.

The production launch extends the same conversation service with approved
customer channels, billing and knowledge integrations, human handoff,
agent-assist, privacy controls, audit trails, and business analytics.

> [!IMPORTANT]
> The 70% autonomous resolution objective applies to eligible production
> conversations after stabilization. It is not an MVP acceptance criterion.
> Safety, factual accuracy, and required escalation take precedence over
> automation rate.

## Product vision

Customers receive accurate, concise help without repeating themselves.
Support agents receive the context needed to continue unresolved conversations.
Product and operations teams can measure outcomes and identify failures.
Specialist capabilities can grow without redesigning the conversation platform.

## Product goals

| ID       | Goal                                                                      | Product outcome                                                                    |
| -------- | ------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| PG-01    | Resolve common support inquiries safely                                   | Eligible requests receive grounded answers without human handling.                 |
| PG-02    | Protect customer trust                                                    | The product does not leak context or fabricate billing information.                |
| PG-03    | Reduce customer effort                                                    | Context persists across turns and approved handoffs.                               |
| PG-04    | Route work to the correct expertise                                       | Billing, technical support, and general requests reach the appropriate specialist. |
| PG-05    | Make uncertainty visible                                                  | Clarification, escalation, and failure are explicit product outcomes.              |
| PG-06    | Improve support operations                                                | Operators and product owners can measure service health and support outcomes.      |
| PG-07    | Enable controlled expansion                                               | New specialists and channels use stable, versioned contracts.                      |

## Non-goals

The initial product will not:

* Replace ticketing, billing, payment, account, or knowledge systems of record
* Make autonomous financial adjustments, refunds, credits, or commitments
* Guarantee an answer when approved evidence is unavailable
* Use AI providers outside Contoso's approved Azure tenant
* Train third-party models with Contoso customer content
* Expose the MVP to production customers
* Store unredacted personally identifiable information (PII) in logs or telemetry
* Include returns, refunds, proactive outreach, or unapproved channels at launch

## Users and personas

### Customer

The customer wants a correct answer with minimal effort. The customer expects the
assistant to remember relevant context, ask focused questions, state when it
cannot help, and transfer available context when human support is required.

### Support agent

The support agent receives unresolved conversations. The agent needs a concise,
redacted summary, the escalation reason, relevant diagnostic context, and
optional grounded response suggestions. The agent remains responsible for any
message sent from the agent-assist experience.

### Support operations lead

The support operations lead monitors workload, escalations, topic trends,
handling time, and resolution outcomes. The lead needs consistent metric
definitions and enough detail to identify product or process regressions.

### Product manager

The product manager owns supported scenarios, eligible-conversation rules,
specialist behavior, evaluation datasets, and release acceptance.

### Service operator

The service operator monitors health, latency, capacity, dependencies, and
failures. The operator needs correlation identifiers and actionable alerts
without routine access to customer conversation content.

### Security and compliance reviewer

The reviewer validates data boundaries, access controls, redaction, retention,
auditability, and launch evidence.

## Product principles

1. Escalate rather than invent.
2. Request only the information needed for the current task.
3. Keep every conversation isolated.
4. Separate conversational tone from factual authority.
5. Use one channel-neutral conversation model.
6. Record measurable outcomes without exposing prohibited content.
7. Make failure states explicit to clients and operators.
8. Require human approval for agent-assist suggestions.

## Release scope

### MVP release

The eight-week MVP includes:

* Python 3.11 REST APIs for starting and continuing conversations
* Server-managed multi-turn context addressed by an explicit session identifier
* Billing, technical support, and general classification
* A dedicated specialist for each supported category
* Clarification, response, escalation-required, and failure dispositions
* Concurrent session processing with context-isolation safeguards
* Approved test content for general billing policies and technical support
* In-memory or file-based session storage for controlled validation
* Existing Azure OpenAI deployments accessed through Microsoft Foundry
* Operational telemetry and evaluation outputs
* A versioned specialist contract and extensibility demonstration
* Synthetic or de-identified test data only

### Production launch release

The target 16-week production release adds:

* Web chat and asynchronous messaging adapters
* Approved customer identity and authorization
* Ticketing-system integration and live handoff
* Authorized billing account-data integration
* Production knowledge-base integration
* Redacted conversation persistence in an approved Azure data store
* PII detection and redaction
* Role-based access and audit trails
* Agent-assist response suggestions
* Business and product analytics
* Production availability, capacity, recovery, alerting, and support controls

### Future releases

Future releases may add:

* Returns and refunds specialist
* Proactive outreach specialist
* Additional approved languages
* Additional customer and support channels

## Primary product journeys

### Resolve a supported inquiry

1. A client starts a conversation.
2. SmartAssist returns a unique conversation identifier.
3. The customer submits a message.
4. SmartAssist classifies the message and selects a specialist.
5. The specialist retrieves approved context when available.
6. The specialist returns a grounded, concise answer.
7. SmartAssist records the disposition and relevant non-sensitive telemetry.
8. The conversation remains active until resolved, expired, or escalated.

### Clarify an ambiguous request

1. SmartAssist determines that required information is missing or the
   classification is not reliable enough.
2. SmartAssist asks one or more focused questions without requesting unnecessary
   sensitive information.
3. The customer replies in the same conversation.
4. SmartAssist uses the new and prior context to classify or answer.
5. If uncertainty remains beyond configured policy limits, SmartAssist marks the
   conversation as requiring escalation.

### Escalate an unsupported request in the MVP

1. SmartAssist identifies an account-specific billing request, unsupported
   action, missing approved evidence, or another mandatory escalation condition.
2. SmartAssist tells the customer that human assistance is required.
3. The API returns a machine-readable `escalation_required` disposition and
   reason code.
4. The calling test client determines how to display or record the outcome.
5. No live ticket or handoff occurs in the MVP.

### Hand off a conversation at production launch

1. SmartAssist identifies a mandatory escalation condition.
2. SmartAssist explains that the request will be transferred.
3. SmartAssist creates or updates a ticket through the approved integration.
4. SmartAssist sends the minimum authorized redacted summary, escalation reason,
   and relevant diagnostic context.
5. The support agent receives the ticket and continues the conversation without
   asking the customer to repeat available context.
6. Handoff creation, access, and outcome are auditable.

### Recover from a dependency failure

1. A model, storage, billing, knowledge, or ticketing dependency times out or
   returns an error.
2. SmartAssist does not present a successful-looking answer.
3. SmartAssist returns an explicit retryable failure, non-retryable failure, or
   escalation outcome according to policy.
4. The request remains traceable through its correlation identifier.
5. The product emits the required operational signal.

## Conversation model

### Conversation states

| State                     | Meaning                                                               |
| ------------------------- | --------------------------------------------------------------------- |
| `active`                  | The conversation can accept another customer message.                 |
| `awaiting_clarification`  | SmartAssist has asked for information required to continue.           |
| `escalation_required`     | SmartAssist cannot continue safely without human support.             |
| `handoff_pending`         | A production handoff has been requested but not confirmed.            |
| `handed_off`              | The ticketing system confirmed transfer to human support.             |
| `resolved`                | The customer need was completed without a pending action.             |
| `failed`                  | A non-recoverable product or dependency failure prevented processing. |
| `expired`                 | The configured inactivity period elapsed.                             |

MVP implementations use `active`, `awaiting_clarification`,
`escalation_required`, `resolved`, `failed`, and `expired`. Handoff states become
available only with the production ticketing integration.

### Message dispositions

Every processed customer message must produce exactly one disposition:

| Disposition                | Client behavior                                                     |
| -------------------------- | ------------------------------------------------------------------- |
| `answered`                 | Display the grounded response and allow another turn.               |
| `clarification_required`   | Display the clarification question and await a reply.               |
| `escalation_required`      | Display the escalation message and prevent autonomous resolution.   |
| `handoff_started`          | Display transfer status and await ticket confirmation.              |
| `resolved`                 | Display the final response and mark the conversation complete.      |
| `retryable_error`          | Tell the client that processing is temporarily unavailable.         |
| `failed`                   | Display an approved failure message and stop autonomous processing. |

The API must not encode failures as an `answered` or `resolved` disposition.

### Identifiers and timestamps

* All generated conversation, message, correlation, and handoff identifiers must
  use UUID version 4.
* All API timestamps must be ISO 8601 strings in Coordinated Universal Time.
* Clients must provide the conversation identifier on every turn after creation.
* A missing, invalid, expired, or inaccessible conversation identifier must
  return an explicit error and must not create an implicit replacement session.

## Functional requirements

### Conversation API

| ID        | Release   | Priority   | Requirement                                                                                                                                                                                    |
| --------- | --------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| FR-001    | MVP       | Must       | The API must provide an operation to create a conversation and return its identifier, state, creation timestamp, and correlation identifier.                                                   |
| FR-002    | MVP       | Must       | The API must provide an operation to submit a customer message to an existing conversation.                                                                                                    |
| FR-003    | MVP       | Must       | Request bodies must be validated against versioned schemas before processing.                                                                                                                  |
| FR-004    | MVP       | Must       | A successful message response must include the assistant message, conversation state, disposition, category, specialist identifier, message identifier, timestamp, and correlation identifier. |
| FR-005    | MVP       | Must       | An escalation response must include an approved customer-facing message and a machine-readable reason code.                                                                                    |
| FR-006    | MVP       | Must       | Invalid input, missing sessions, expired sessions, conflicts, rate limits, and service failures must use distinct documented HTTP status codes and error codes.                                |
| FR-007    | MVP       | Must       | Repeated processing caused by a client retry must not duplicate a logical message or mix session context when the client supplies the supported idempotency value.                             |
| FR-008    | MVP       | Must       | The API must reject a message for a conversation that is resolved, failed, expired, or awaiting completed human handoff unless product policy explicitly permits reopening.                    |
| FR-009    | Launch    | Must       | Channel adapters must use the same conversation operations and dispositions as direct API clients.                                                                                             |

### Session and context management

| ID        | Release   | Priority   | Requirement                                                                                                                    |
| --------- | --------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------ |
| FR-010    | MVP       | Must       | SmartAssist must retrieve context only for the supplied conversation identifier.                                               |
| FR-011    | MVP       | Must       | SmartAssist must preserve relevant prior turns within the configured session lifetime.                                         |
| FR-012    | MVP       | Must       | Concurrent requests for different conversations must not share customer messages, summaries, model state, or specialist state. |
| FR-013    | MVP       | Must       | Concurrent updates to the same conversation must be serialized or rejected with an explicit conflict outcome.                  |
| FR-014    | MVP       | Must       | Session expiration must be configurable and observable.                                                                        |
| FR-015    | MVP       | Must       | The MVP must store only synthetic or de-identified conversation content.                                                       |
| FR-016    | Launch    | Must       | Production conversation storage must apply approved redaction, access, retention, deletion, and encryption controls.           |

### Classification and routing

| ID        | Release   | Priority   | Requirement                                                                                                                                          |
| --------- | --------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| FR-017    | MVP       | Must       | SmartAssist must classify each processable customer message as `billing`, `tech_support`, or `general`.                                              |
| FR-018    | MVP       | Must       | SmartAssist must route the classified request to the registered specialist for that category.                                                        |
| FR-019    | MVP       | Must       | Classification output must include a category and sufficient evaluation metadata to measure routing quality without exposing hidden model reasoning. |
| FR-020    | MVP       | Must       | Low-confidence or materially ambiguous classification must produce clarification or escalation according to configured policy.                       |
| FR-021    | MVP       | Must       | SmartAssist must not silently route low-confidence requests to the general specialist.                                                               |
| FR-022    | MVP       | Must       | Requests that span multiple categories must be clarified, handled through an approved orchestration policy, or escalated.                            |
| FR-023    | MVP       | Must       | Routing outcomes must be traceable by release, category, specialist version, and disposition.                                                        |

### Specialist behavior

| ID        | Release   | Priority   | Requirement                                                                                                                      |
| --------- | --------- | ---------- | -------------------------------------------------------------------------------------------------------------------------------- |
| FR-024    | MVP       | Must       | Billing, technical support, and general specialists must implement one versioned specialist contract.                            |
| FR-025    | MVP       | Must       | The specialist contract must accept conversation context, the current message, approved evidence, and request metadata.          |
| FR-026    | MVP       | Must       | The specialist contract must return response content, disposition, evidence references when applicable, and escalation metadata. |
| FR-027    | MVP       | Must       | A specialist must ask for clarification when required facts are missing and can be safely requested.                             |
| FR-028    | MVP       | Must       | A specialist must return escalation-required when an applicable business rule prohibits an autonomous answer.                    |
| FR-029    | MVP       | Must       | A new test specialist must be registerable without modifying existing specialist business logic.                                 |
| FR-030    | MVP       | Should     | Prompts, policies, and source-content versions should be identifiable in evaluation records.                                     |

### Billing behavior

| ID        | Release   | Priority   | Requirement                                                                                                                        |
| --------- | --------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| FR-031    | MVP       | Must       | The billing specialist may answer only general policy questions supported by approved test content.                                |
| FR-032    | MVP       | Must       | Account-specific balances, charges, payment states, entitlements, disputes, and financial actions must return escalation-required. |
| FR-033    | Launch    | Must       | Account-specific answers must require successful customer authorization and retrieval from the approved billing source.            |
| FR-034    | Launch    | Must       | SmartAssist must not infer missing account values or present model-generated values as account facts.                              |
| FR-035    | Launch    | Must       | Disputed charges, refunds, credits, adjustments, commitments, and unsupported financial actions must be handed to a human.         |
| FR-036    | Launch    | Must       | Billing dependency failures must produce escalation or explicit unavailability, not a cached or invented account answer.           |

### Technical support behavior

| ID        | Release   | Priority   | Requirement                                                                                                 |
| --------- | --------- | ---------- | ----------------------------------------------------------------------------------------------------------- |
| FR-037    | MVP       | Must       | The technical support specialist must answer from approved packaged test content.                           |
| FR-038    | MVP       | Must       | The specialist must request missing diagnostic details before selecting steps that depend on those details. |
| FR-039    | MVP       | Must       | Unsupported issues or issues without sufficient approved evidence must return escalation-required.          |
| FR-040    | Launch    | Must       | Production technical guidance must reference content retrieved from the approved knowledge base.            |
| FR-041    | Launch    | Must       | Knowledge retrieval failures must return escalation or explicit unavailability.                             |

### General support behavior

| ID        | Release   | Priority   | Requirement                                                                                                          |
| --------- | --------- | ---------- | -------------------------------------------------------------------------------------------------------------------- |
| FR-042    | MVP       | Must       | The general specialist must answer supported informational inquiries from approved content.                          |
| FR-043    | MVP       | Must       | The general specialist must not act as a fallback for uncertain billing or technical requests.                       |
| FR-044    | MVP       | Must       | Requests for unsupported actions, sensitive decisions, or unavailable facts must return clarification or escalation. |

### Response experience

| ID        | Release   | Priority   | Requirement                                                                                                           |
| --------- | --------- | ---------- | --------------------------------------------------------------------------------------------------------------------- |
| FR-045    | MVP       | Must       | Customer-facing language must be concise, complete, respectful, and free of internal implementation terminology.      |
| FR-046    | MVP       | Must       | SmartAssist must distinguish confirmed facts, requested clarification, and inability to answer.                       |
| FR-047    | MVP       | Must       | Clarification prompts must request only information necessary to continue.                                            |
| FR-048    | MVP       | Must       | Escalation messages must state that human assistance is required without claiming that a handoff occurred in the MVP. |
| FR-049    | Launch    | Must       | Handoff messages must communicate whether transfer is pending, confirmed, or unavailable.                             |
| FR-050    | Launch    | Should     | Channel presentation may vary, but meaning, safety behavior, and state transitions must remain consistent.            |

### Human handoff and agent-assist

| ID        | Release   | Priority   | Requirement                                                                                                                                |
| --------- | --------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| FR-051    | Launch    | Must       | SmartAssist must create or update a ticket when a live handoff begins.                                                                     |
| FR-052    | Launch    | Must       | The handoff package must include a redacted summary, escalation reason, relevant approved diagnostic context, and conversation identifier. |
| FR-053    | Launch    | Must       | A failed ticket creation must result in an explicit handoff failure state and an approved customer message.                                |
| FR-054    | Launch    | Must       | Handoff status must be traceable from request through ticket-system confirmation.                                                          |
| FR-055    | Launch    | Should     | Authorized agents should receive grounded draft responses for eligible escalated conversations.                                            |
| FR-056    | Launch    | Must       | Suggested responses must identify their supporting evidence and remain unsent until an agent approves them.                                |
| FR-057    | Launch    | Must       | Access to handoff context and agent-assist output must be role-controlled and audited.                                                     |

### Channels

| ID        | Release   | Priority   | Requirement                                                                                                                 |
| --------- | --------- | ---------- | --------------------------------------------------------------------------------------------------------------------------- |
| FR-058    | Launch    | Must       | The web chat adapter must create, continue, and display conversation states through the channel-neutral API.                |
| FR-059    | Launch    | Must       | The asynchronous adapter must correlate replies to the correct conversation without relying on mutable process-local state. |
| FR-060    | Launch    | Must       | Both channels must present clarification, escalation, handoff, and failure states.                                          |
| FR-061    | Launch    | Must       | Channel retries must follow the API idempotency contract.                                                                   |
| FR-062    | Launch    | Should     | Channel-specific copy and interaction details should meet approved UX and accessibility standards.                          |

### Analytics and administration

| ID        | Release   | Priority   | Requirement                                                                                                                     |
| --------- | --------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------- |
| FR-063    | MVP       | Must       | SmartAssist must record request count, latency, error, category, specialist, and disposition telemetry.                         |
| FR-064    | MVP       | Must       | Every processed request must be traceable through a correlation identifier.                                                     |
| FR-065    | MVP       | Must       | Telemetry must identify product, policy, specialist, and model configuration versions needed for release comparison.            |
| FR-066    | MVP       | Must       | Routine operational telemetry must not contain unredacted customer message content or PII.                                      |
| FR-067    | Launch    | Must       | Authorized users must be able to view autonomous resolution, escalation, handling time, satisfaction, and topic-trend measures. |
| FR-068    | Launch    | Must       | Product measures must be filterable by approved time period, channel, category, specialist, and release.                        |
| FR-069    | Launch    | Must       | Analytics must apply approved definitions, exclusions, and measurement windows.                                                 |
| FR-070    | Launch    | Should     | The product should enable authorized users to identify statistically material quality regressions by specialist and release.    |

## Product rules

### Mandatory escalation conditions

SmartAssist must require human support when:

* The customer disputes a charge.
* The customer requests a refund, credit, adjustment, exception, or commitment.
* Required authorization fails or is unavailable.
* Approved evidence does not support a factual answer.
* A required downstream system is unavailable and no safe answer remains.
* The request falls outside approved specialist scope.
* Product policy identifies a safety, privacy, security, or compliance condition.
* Clarification limits are reached without enough information to continue.

Product and Security must maintain the complete versioned escalation policy.

### Autonomous resolution rules

A conversation may be marked `resolved` without human handling only when:

* The scenario is included in the approved eligible-conversation definition.
* The applicable specialist completed the customer's stated need.
* Required evidence and authorization were available.
* No mandatory escalation condition occurred.
* No handoff or agent intervention occurred.

Reporting must remove the conversation from autonomous resolution if it is
reopened within the approved measurement window.

## Data requirements

### Core product records

| Record           | Minimum product data                                                                                                            |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Conversation     | Conversation ID, state, channel, created time, updated time, expiration time, and authorized customer reference when applicable |
| Message          | Message ID, conversation ID, sender type, timestamp, content reference or approved content, and processing status               |
| Routing result   | Message ID, category, specialist version, policy version, disposition, and evaluation metadata                                  |
| Evidence         | Source type, source reference, retrieval time, and content or version reference permitted by policy                             |
| Escalation       | Conversation ID, reason code, status, timestamps, and ticket reference when available                                           |
| Audit event      | Actor or service identity, action, resource reference, timestamp, outcome, and correlation identifier                           |

### Data-handling rules

* MVP records may contain only synthetic or de-identified content.
* Production content persistence must occur only after redaction and policy checks.
* Operational metrics should use non-content metadata whenever possible.
* Production access must follow least privilege and be auditable.
* Retention, deletion, and data-subject handling must follow approved policies.
* Data must remain within approved Contoso Azure services and tenant boundaries.

## Non-functional product requirements

### Security and privacy

| ID         | Release   | Requirement                                                                                                         |
| ---------- | --------- | ------------------------------------------------------------------------------------------------------------------- |
| PR-NF-01   | MVP       | All service and model processing must use Contoso-approved Azure services and tenants.                              |
| PR-NF-02   | MVP       | Data in transit must use organization-approved encryption.                                                          |
| PR-NF-03   | MVP       | Secrets must not appear in source code, prompts, conversation content, or telemetry.                                |
| PR-NF-04   | MVP       | Concurrency and retry tests must demonstrate zero cross-session content leakage.                                    |
| PR-NF-05   | Launch    | Production data must use approved encryption, identity, authorization, retention, deletion, and redaction controls. |
| PR-NF-06   | Launch    | Sensitive context access and production actions must generate audit events.                                         |
| PR-NF-07   | Launch    | Production data handling must pass security, privacy, SOC 2 control-alignment, and GDPR-readiness review.           |

### Reliability and performance

| ID         | Release   | Requirement                                                                                                          |
| ---------- | --------- | -------------------------------------------------------------------------------------------------------------------- |
| PR-NF-08   | MVP       | The controlled load test must achieve at least 99% successful responses, excluding injected dependency failures.     |
| PR-NF-09   | MVP       | At least 99% of requests must have complete correlation and outcome telemetry. The acceptance target is 100%.        |
| PR-NF-10   | MVP       | Timeouts and dependency failures must produce bounded, explicit outcomes.                                            |
| PR-NF-11   | MVP       | Health endpoints and telemetry must expose service, model, storage, and routing health.                              |
| PR-NF-12   | Launch    | Availability, latency, capacity, and recovery objectives must be approved from MVP and pilot evidence.               |
| PR-NF-13   | Launch    | Alerts must identify sustained customer-impacting failures before the agreed service objective is breached.          |
| PR-NF-14   | Launch    | The service must support peak concurrency derived from validated arrival patterns for more than 2,000 daily tickets. |

### Maintainability

| ID         | Release   | Requirement                                                                             |
| ---------- | --------- | --------------------------------------------------------------------------------------- |
| PR-NF-15   | MVP       | The core service must use Python 3.11.                                                  |
| PR-NF-16   | MVP       | API, event, and specialist contracts must be versioned and documented.                  |
| PR-NF-17   | MVP       | Routing, specialists, storage, and integration adapters must be independently testable. |
| PR-NF-18   | MVP       | Configuration must not require duplicated specialist source code.                       |
| PR-NF-19   | Launch    | Releases must support controlled rollback and release-level metric comparison.          |

## Measurement plan

### Product metrics

| Metric                           | Definition                                                                                                                                |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Autonomous resolution rate       | Eligible conversations resolved without human handling and not reopened during the approved window, divided by all eligible conversations |
| Escalation rate                  | Conversations that reach `escalation_required` or a handoff state, divided by processable conversations                                   |
| Routing accuracy                 | Correct category predictions divided by evaluated messages in the approved labeled set                                                    |
| Context retention pass rate      | Passed multi-turn context scenarios divided by executed context scenarios                                                                 |
| Unsupported billing claim rate   | Responses containing an account-specific claim without authorized evidence, divided by evaluated billing responses                        |
| Average handling time            | Approved elapsed or active-work duration from conversation start to terminal outcome                                                      |
| Customer satisfaction            | Average score collected through the approved post-interaction survey                                                                      |
| Handoff completeness             | Confirmed handoffs containing every required context field, divided by confirmed handoffs                                                 |
| Reopen rate                      | Resolved conversations reopened within the approved measurement window, divided by resolved conversations                                 |

### MVP quality thresholds

| Measure                      | Acceptance threshold                                                                |
| ---------------------------- | ----------------------------------------------------------------------------------- |
| Routing accuracy             | At least 90% on the approved representative labeled evaluation set                  |
| Cross-session leakage        | Zero occurrences in concurrency and retry testing                                   |
| Unsupported billing claims   | Zero occurrences in the approved safety evaluation set                              |
| Mandatory escalation         | 100% of defined mandatory-escalation cases return `escalation_required`             |
| Multi-turn context           | At least 95% of approved scenarios pass                                             |
| Controlled API reliability   | At least 99%, excluding injected dependency failures                                |
| Request traceability         | 100% of evaluated requests have a correlation identifier and outcome                |
| Extensibility                | A test specialist is registered without changing existing specialist business logic |
| Production data use          | Zero production PII used or retained                                                |

### Production targets

| Measure                        | Target                                               |
| ------------------------------ | ---------------------------------------------------- |
| Autonomous resolution          | 70% of eligible conversations after stabilization    |
| Customer satisfaction          | At least 4.0 out of 5 within 90 days                 |
| Confirmed context leakage      | Zero incidents                                       |
| Fabricated billing facts       | Zero incidents                                       |
| Complete successful handoffs   | At least 99%                                         |
| Metric availability            | At least 99% for approved reporting intervals        |
| Average handling time          | Target approved after MVP baseline and before launch |

## Analytics events

| Event                             | Trigger                                             | Required non-content properties                                  |
| --------------------------------- | --------------------------------------------------- | ---------------------------------------------------------------- |
| `conversation_created`            | A conversation is accepted                          | Conversation ID, channel, timestamp, release                     |
| `message_received`                | A validated customer message is accepted            | Conversation ID, message ID, timestamp, correlation ID           |
| `message_classified`              | Classification completes                            | Category, policy version, outcome, latency                       |
| `specialist_completed`            | A specialist returns                                | Specialist, version, disposition, latency, evidence-present flag |
| `clarification_requested`         | The product asks for more information               | Reason code, category, clarification count                       |
| `escalation_required`             | Product policy requires human support               | Reason code, category, specialist                                |
| `handoff_started`                 | Production ticket creation begins                   | Reason code, channel, integration                                |
| `handoff_completed`               | Ticketing confirms the handoff                      | Ticket reference, duration, completeness result                  |
| `conversation_resolved`           | The conversation enters `resolved`                  | Category, specialist, turn count, elapsed duration               |
| `conversation_failed`             | The conversation enters `failed`                    | Failure code, dependency, retryable flag                         |
| `dependency_call_completed`       | A model or integration call completes               | Dependency, outcome, latency, retry count                        |

Event properties must follow the approved telemetry schema and must not include
unredacted customer content or PII.

## MVP acceptance scenarios

| ID       | Scenario                                 | Expected result                                                                                                 |
| -------- | ---------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| AC-01    | Start a conversation                     | A UUID v4 conversation identifier, active state, timestamp, and correlation identifier are returned.            |
| AC-02    | Ask a supported billing policy question  | The request is classified as billing and answered from approved test content.                                   |
| AC-03    | Ask for an account balance               | The billing specialist returns `escalation_required` because the MVP has no account integration.                |
| AC-04    | Submit an underspecified technical issue | The technical specialist asks for the missing diagnostic information.                                           |
| AC-05    | Ask an unsupported technical question    | The technical specialist returns `escalation_required` rather than invented steps.                              |
| AC-06    | Ask a supported general question         | The general specialist returns a concise answer from approved content.                                          |
| AC-07    | Continue a prior conversation            | The response uses relevant earlier context from the same session.                                               |
| AC-08    | Run concurrent conversations             | Each response uses only its own conversation context.                                                           |
| AC-09    | Submit an invalid session ID             | The API returns a documented client error without creating a session or exposing context.                       |
| AC-10    | Submit concurrent turns to one session   | One update succeeds and the other is serialized or receives a documented conflict response.                     |
| AC-11    | Retry a message idempotently             | The product does not create a duplicate logical message or response.                                            |
| AC-12    | Trigger a model timeout                  | The API returns a traceable retryable error or escalation outcome, not an answer.                               |
| AC-13    | Trigger a storage failure                | The API returns an explicit failure and emits the required operational signal.                                  |
| AC-14    | Inspect telemetry                        | An authorized operator can correlate request, route, specialist, latency, and disposition without customer PII. |
| AC-15    | Register a test specialist               | The specialist is available through the contract without changes to existing specialist business logic.         |

## Launch acceptance themes

Production launch validation must include:

* End-to-end customer authorization and account-data retrieval
* Grounding and failure handling for billing and knowledge sources
* Web chat and asynchronous conversation continuity
* Ticket creation, handoff-state handling, and context completeness
* Agent-assist evidence, authorization, review, and audit behavior
* PII detection, redaction, retention, deletion, and access controls
* Data-subject and audit procedures
* Capacity, resilience, recovery, and alerting
* Analytics accuracy and exclusion rules
* Customer usability, accessibility, and satisfaction

## Delivery plan

### MVP sequence

| Phase                 | Intended outcome                                                                                              |
| --------------------- | ------------------------------------------------------------------------------------------------------------- |
| Foundation            | Versioned API contracts, conversation states, storage abstraction, telemetry conventions, and evaluation plan |
| Core conversation     | Session creation, validated messages, context retrieval, concurrency behavior, and explicit errors            |
| Routing               | Three-category classification, clarification policy, specialist registry, and routing telemetry               |
| Specialists           | Billing, technical support, and general behavior using approved test content                                  |
| Safety and quality    | Mandatory escalation, billing safeguards, isolation tests, evaluation suite, and failure handling             |
| MVP readiness         | Controlled load test, extensibility demonstration, evidence review, and stakeholder acceptance                |

### Launch sequence

| Phase                      | Intended outcome                                                                       |
| -------------------------- | -------------------------------------------------------------------------------------- |
| Production data controls   | Approved persistence, redaction, retention, identity, access, and audit                |
| Grounding integrations     | Authorized billing and knowledge retrieval with failure policies                       |
| Support integration        | Ticketing, handoff states, redacted summaries, and agent-assist                        |
| Customer channels          | Web chat and asynchronous adapters using common contracts                              |
| Operations and analytics   | Service objectives, dashboards, alerts, business metrics, and runbooks                 |
| Pilot and launch           | Representative pilot, remediation, compliance evidence, training, and go-live decision |

## Dependencies

### MVP dependencies

* Existing Azure OpenAI deployments and approved Microsoft Foundry access
* Approved model and service configuration
* Labeled, representative, de-identified evaluation data
* Approved billing-policy and technical-support test content
* Versioned escalation and eligible-scenario definitions
* Deployment, telemetry, and environment support

### Production dependencies

* Approved customer identity and authorization capability
* Ticketing, billing, and knowledge API contracts, sandboxes, credentials, and
  owning teams
* Approved Azure persistence and retention design
* Web chat and asynchronous channel owners
* Security threat assessment and privacy impact assessment
* SOC 2 control mapping and GDPR readiness review
* Support staffing, training, operating procedures, and escalation service levels
* Production-representative pilot cohort and evaluation plan

## Risks and mitigations

| Risk                                         | Product mitigation                                                                            |
| -------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Automation pressure weakens safety           | Pair resolution targets with zero-fabrication, leakage, reopening, and satisfaction measures. |
| Required integrations miss the launch window | Keep launch conditional on readiness evidence and preserve explicit escalation paths.         |
| Context leaks under concurrency or retries   | Require explicit identifiers, concurrency control, idempotency, and isolation testing.        |
| The model invents billing or technical facts | Permit facts only from approved evidence and escalate when evidence is absent.                |
| Telemetry exposes customer information       | Use non-content metadata by default and enforce approved redaction before persistence.        |
| Customers reject the interaction style       | Conduct scenario-based usability testing and monitor satisfaction by category and channel.    |
| Metrics overstate autonomous success         | Define eligibility, exclusions, reopen windows, and calculation ownership before reporting.   |
| Sixteen-week scope exceeds team capacity     | Sequence launch gates, assign external-system owners, and reforecast after dependency review. |

## Open product decisions

| ID        | Decision                                                                              | Owner candidates                       | Needed by            |
| --------- | ------------------------------------------------------------------------------------- | -------------------------------------- | -------------------- |
| PD-01     | Approve API resource names, schema versions, and supported idempotency mechanism      | Product and Engineering                | End of week 2        |
| PD-02     | Define category labels, multi-domain behavior, and representative evaluation set      | Product, Support, and ML Engineering   | End of week 2        |
| PD-03     | Approve classification and specialist escalation policies                             | Product, Security, and ML Engineering  | End of week 3        |
| PD-04     | Set session lifetime, turn limit, message-size limit, and clarification limit         | Product, UX, Security, and Engineering | End of week 3        |
| PD-05     | Define eligible conversations, exclusion rules, and reopen window                     | Product and Customer Success           | End of week 4        |
| PD-06     | Confirm production data store, retention periods, and deletion behavior               | Engineering, Security, and Privacy     | End of week 6        |
| PD-07     | Confirm ticketing, billing, and knowledge API readiness                               | Engineering and system owners          | End of week 6        |
| PD-08     | Approve handoff summary fields and agent-assist experience                            | Support, UX, Product, and Security     | Before pilot         |
| PD-09     | Set production availability, latency, recovery, and capacity objectives               | Engineering and Customer Success       | Before pilot         |
| PD-10     | Approve supported languages, accessibility criteria, and channel service expectations | Product and UX                         | Before pilot         |
| PD-11     | Define customer satisfaction collection and reporting method                          | Customer Success, Product, and UX      | Before pilot         |
| PD-12     | Set the target date for reaching 70% autonomous resolution                            | Customer Success and Product           | After pilot baseline |

## Traceability to business requirements

| Product area                      | Product requirements       | BRD source                                 |
| --------------------------------- | -------------------------- | ------------------------------------------ |
| Conversation and context          | FR-001 through FR-016      | BR-01 through BR-07; NFR-09                |
| Classification and routing        | FR-017 through FR-023      | BR-08 through BR-13                        |
| Specialist contract               | FR-024 through FR-030      | BR-10 through BR-13; NFR-16 through NFR-18 |
| Billing grounding                 | FR-031 through FR-036      | BR-14, BR-15, BR-17, BR-21                 |
| Technical and general support     | FR-037 through FR-044      | BR-16 through BR-18, BR-22                 |
| Response experience               | FR-045 through FR-050      | BR-03 through BR-07, BR-23                 |
| Handoff and agent-assist          | FR-051 through FR-057      | BR-25 through BR-29                        |
| Channels                          | FR-058 through FR-062      | BR-07, BR-19, BR-23                        |
| Analytics and operations          | FR-063 through FR-070      | BR-30 through BR-34; NFR-10 through NFR-14 |
| Security and privacy              | PR-NF-01 through PR-NF-07  | NFR-01 through NFR-08                      |
| Reliability and maintainability   | PR-NF-08 through PR-NF-19  | NFR-09 through NFR-19                      |

## Release approval

### MVP exit criteria

The MVP may be accepted when:

* All MVP Must requirements are implemented and demonstrated.
* Every MVP quality threshold is met.
* No production customer traffic or unredacted production PII was used.
* Known limitations and failed evaluation cases are documented.
* Product, Engineering, Security, Support, and UX representatives approve the
  controlled validation result.

### Production launch criteria

Production launch requires:

* All launch Must requirements are implemented and tested.
* Billing, knowledge, ticketing, and channel integrations pass functional,
  authorization, concurrency, and failure-mode tests.
* Security, privacy, legal, SOC 2 control-alignment, and GDPR-readiness evidence
  is approved.
* Capacity, recovery, monitoring, alerting, and support procedures are approved.
* A representative pilot demonstrates acceptable accuracy, safety, usability,
  satisfaction, and operational performance.
* The Business Owner, Product Manager, Head of Engineering, and CISO approve
  go-live.

## Sign-off

| Role                     | Name     | Decision   | Date   |
| ------------------------ | -------- | ---------- | ------ |
| VP of Customer Success   | Sarah    | Pending    |        |
| Head of Engineering      | Marcus   | Pending    |        |
| Product Manager          | Priya    | Pending    |        |
| CISO                     | James    | Pending    |        |
| CTO                      | Lin      | Pending    |        |
| Support Team Lead        | Diego    | Pending    |        |
| UX Designer              | Aisha    | Pending    |        |
