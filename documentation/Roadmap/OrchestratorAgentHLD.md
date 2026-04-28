# Orchestrator Agent HLD

## Purpose
The product is a web agent harness for churn modeling. The user should not move through a fixed form before seeing action. The user should be able to start with data, documents, or a short message.

The orchestrator sits above the agents. It decides which agent should run, whether an agent can exit for now, and whether new evidence should reopen an earlier agent.

The core promise is: understand the user's business through the data and documents they already have. Ask questions only when the answer changes what the system should do next.

## Market Boundary
The harness must work across the companies and verticals in `documentation/TargetMarket/CompanyList.md` and the data types in `documentation/TargetMarket/DataPoints.md`.

Supported company pattern:
- physical product company
- dealer, distributor, retailer, stockist, franchisee, outlet, fleet, workshop, or influencer network
- sales head or distribution head has exports but cannot rebuild the source systems
- output must become an action file for sales teams

Supported data families:
- Type 1: transaction-only
- Type 2: transaction plus service or warranty
- Type 3: transaction plus loyalty or membership
- Type 4: transaction plus delivery, returns, or fulfillment
- Type 5: transaction plus field interaction

The system should not have company-specific logic. It should use vertical and data-family blueprints to reason about companies such as FMCG, dairy, paints, adhesives, cement, wires, tiles, steel, durables, tyres, batteries, lubricants, auto OEM, auto aftermarket, pharma, agri, textiles, footwear, and telecom.

## Core Idea
Code owns the rails. Models own the conversation inside the rails.

Code defines:
- agent contracts
- state schema
- artifact schema
- allowed transitions
- validation checks
- grounding checks
- blocked states

Models generate:
- next question
- answer options
- answer validation
- working hypothesis
- artifact draft
- reason for handoff or rollback

## UX Promise
The first screen should not be a questionnaire.

The first screen should say:

```text
Start with whatever you have.

Upload sales data, MIS files, review decks, dealer lists, target sheets, watchlists, or notes. If you prefer, just tell me your company and role.
```

The user can start with:
- CSV or spreadsheet data
- sales review decks
- org charts
- dealer or distributor policies
- scheme circulars
- territory lists
- beat plans
- target files
- monthly MIS files
- CRM exports
- sales notes
- prior watchlists
- a short text description

Documents are first-class context. They are not secondary attachments after the real upload.

## Intake Model
PersonaAgent, CompanyContextAgent, and DataInventoryAgent are intake agents. They do not gate upload.

They can run:
- before upload
- during upload
- after upload
- after a contradiction
- after the user changes the target
- after a later agent requests missing context

Their output can be provisional.

```text
confirmed: grounded in user answer or document/data evidence
inferred: model inference with evidence
unknown_non_blocking: not known, but progress can continue
unknown_blocking: not known, and progress should pause
```

Only `unknown_blocking` stops progress.

## Orchestrator Role
The orchestrator is not one of the loop agents. It is the session controller.

It owns:
- session stage
- artifact graph
- active agent
- uploaded data and document inventory
- transition decisions
- rollback decisions
- contradiction handling
- user-visible progress
- stop conditions

It must be able to say:
- continue with current agent
- accept upload now
- extract context from files and documents
- exit current agent for now
- enter next agent
- go back to a prior agent because new evidence changed the premise
- ask the user one blocking question
- ask the user for a route decision when routing is ambiguous
- block the run because the needed artifact cannot be produced

## State Graph
The flow is a graph, not a line.

```text
SessionStart
  -> IntakeOrchestrator
       -> PersonaAgent
       -> CompanyContextAgent
       -> DataInventoryAgent
       -> UploadAgent
       -> DocumentUnderstandingAgent
       -> DataUnderstandingAgent
       -> DataReadinessAgent
       -> RiskDefinitionAgent
       -> SignalDesignAgent
       -> ModelValidationAgent
       -> ActionOutputAgent
       -> Delivery
```

Upload can happen at any point after `SessionStart`.

The first three agents do not have to finish before upload. They build and revise provisional artifacts as evidence arrives.

Every node can return to an earlier node when its artifact depends on context that changed.

Examples:
- UploadAgent sees doctor prescription data after the user described dealer churn. Orchestrator returns to PersonaAgent or DataInventoryAgent to clarify whether the target is doctors, stockists, or retailers.
- DataUnderstandingAgent sees only loyalty data and no transactions. Orchestrator returns to DataInventoryAgent to ask if transaction data exists or if the scope must change.
- RiskDefinitionAgent cannot define churn for agri month-on-month because the vertical is seasonal. Orchestrator returns to CompanyContextAgent to confirm crop season and comparison window.
- ActionOutputAgent needs owner fields but uploaded data has no territory or sales owner. Orchestrator returns to DataInventoryAgent to ask for master data or accept a scope warning.

## Individual Agents
Each agent owns one artifact and one set of exit criteria.

| Agent | Runs | Artifact | Purpose |
| --- | --- | --- | --- |
| PersonaAgent | intake, evidence extraction, rollback | Persona Brief | Understand role, decision rights, action owner, region, cadence, and output use |
| CompanyContextAgent | intake, evidence extraction, rollback | Company Context Brief | Identify company, vertical, channel, customer entities, seasonality, and influence structure |
| DataInventoryAgent | intake, upload guidance, rollback | Data Inventory Brief | Learn what files the user has, expected systems, expected grain, and gaps |
| UploadAgent | whenever user provides files | Upload Manifest | Collect files, file descriptions, and initial profiles |
| DocumentUnderstandingAgent | whenever user provides documents | Document Context Brief | Extract org, cadence, territory, schemes, metrics, watchlists, and business rules from documents |
| DataUnderstandingAgent | after any data upload | Data Understanding Brief | Map files to business meaning, grain, keys, dates, entities, and joins |
| DataReadinessAgent | after understanding | Data Readiness Report | Decide whether the files support the stated action and what scope is safe |
| RiskDefinitionAgent | before labels | Risk Contract | Define churn, decline, dormancy, observation window, prediction window, and exclusions |
| SignalDesignAgent | before modeling | Signal Ledger | Propose behavior signals grounded in uploaded data and vertical logic |
| ModelValidationAgent | after modeling | Trust Report | Verify model output against history, rules, misses, and user-recognized cases |
| ActionOutputAgent | final step | Field Action File Spec | Shape the output for sales action, ownership, capacity, and caveats |

## Intake Agents
### PersonaAgent
PersonaAgent should infer from login context, user text, documents, and uploaded data.

It should use the sales-leader default: the output becomes a ranked account list for field follow-up through the territory sales chain.

It should ask only when evidence points to a different workflow or when the output route changes the artifact.

Examples of blocking questions:
- This looks like a credit-collections workflow, not field sales recovery. Should I optimize the output for collections or sales follow-up?
- The uploaded deck shows distributor-owned reps, not company field agents. Should the action file be grouped by distributor or company territory?
- The watchlist is for key accounts, while the sales file covers the full network. Should the first run cover key accounts only or all active accounts?

PersonaAgent should not ask for data columns or ask questions whose answer is implied by the target user.

### CompanyContextAgent
CompanyContextAgent should infer from company name, vertical blueprint, documents, user text, and uploaded data.

It should ask only when two business interpretations lead to different modeling choices.

Examples of blocking questions:
- Is the target dealer, retailer, stockist, fleet, workshop, doctor, farmer, or influencer?
- Should seasonality be compared month-on-month or same-season last year?
- Does this business depend on an influencer network such as painters, masons, electricians, mechanics, doctors, or farmers?

CompanyContextAgent should not force a company profile interview.

### DataInventoryAgent
DataInventoryAgent should infer from uploaded files, file names, file descriptions, documents, and user text.

It should suggest missing files without blocking when the current data can still produce a useful first read.

Examples of non-blocking guidance:

```text
I can start with this invoice file. If you also have dealer master or territory owner mapping, upload it later and I will revise the output.
```

Examples of blocking questions:
- Do you have any customer identifier in another file?
- Is this file a transaction export or a monthly summary?
- Can you continue without owner mapping, or should we wait for dealer master?

## Agent Structure
Every agent should use the same internal structure.

```yaml
agent_id: string
mission: string
entry_conditions:
  - condition
input_artifacts:
  - artifact_key
available_evidence:
  - user_messages
  - uploaded_data_profiles
  - uploaded_document_extracts
  - prior_artifacts
  - vertical_blueprints
available_tools:
  - model
  - profile_reader
  - document_extractor
  - artifact_store
question_policy:
  max_questions_per_turn: 1
  options_allowed: true
  free_text_allowed: true
  must_explain_why_question_matters: true
  ask_only_if_blocking_or_high_impact: true
exit_schema: pydantic_model_name
exit_criteria:
  - criterion
validation_rules:
  - rule
rollback_triggers:
  - trigger
handoff_targets:
  - agent_id
```

Each agent turn returns this structure.

```json
{
  "agent_id": "data_understanding",
  "status": "collecting | done_for_now | needs_user_answer | needs_file | blocked | rollback_request",
  "confidence": 0.0,
  "working_hypothesis": "string",
  "missing_context": ["string"],
  "blocking_unknowns": ["string"],
  "non_blocking_unknowns": ["string"],
  "next_question": {
    "question": "string",
    "why_this_matters": "string",
    "options": [
      {"label": "string", "value": "string"}
    ],
    "free_text_enabled": true,
    "skip_allowed": true
  },
  "answer_validation": {
    "accepted": true,
    "reason": "string"
  },
  "artifact_delta": {},
  "exit_artifact": null,
  "rollback_request": null
}
```

The model can propose `done_for_now`, but the orchestrator verifies the schema, grounding, and transition.

## Orchestrator Structure
The orchestrator has its own contract.

```yaml
orchestrator_id: churn_harness_orchestrator
inputs:
  - active_agent_result
  - session_state
  - artifact_graph
  - uploaded_file_profiles
  - uploaded_document_extracts
  - user_message
outputs:
  - route_decision
  - active_agent
  - user_visible_message
  - state_update
route_decisions:
  - continue_current_agent
  - accept_upload
  - extract_context
  - enter_next_agent
  - reopen_agent
  - ask_user_one_question
  - ask_user_to_choose_route
  - block_session
```

Orchestrator turn output:

```json
{
  "route_decision": "continue_current_agent | accept_upload | extract_context | enter_next_agent | reopen_agent | ask_user_one_question | ask_user_to_choose_route | block_session",
  "target_agent_id": "string",
  "reason": "string",
  "state_updates": {},
  "user_message": "string",
  "requires_user_input": true
}
```

## Artifact Graph
Artifacts are the memory of the run.

```text
Persona Brief
Company Context Brief
Data Inventory Brief
Upload Manifest
Document Context Brief
Data Understanding Brief
Data Readiness Report
Risk Contract
Signal Ledger
Trust Report
Field Action File Spec
```

Every artifact stores:
- fields
- confidence
- grounding references
- open risks
- status: provisional, done_for_now, confirmed, superseded
- source agent
- time created
- supersedes artifact id when revised

Grounding references can point to:
- user answer
- uploaded data profile
- uploaded document extract
- column sample
- prior artifact
- model inference marked as inference

## Rollback And Re-Entry
Rollback is a product requirement, not an error.

The orchestrator should reopen an agent when:
- uploaded data contradicts the stated persona or action
- uploaded document contradicts the stated channel or customer entity
- uploaded grain cannot support the current risk contract
- required action fields are missing
- vertical logic changes the churn definition
- the user changes the target entity
- a later agent marks an upstream artifact as unsafe

Rollback does not delete prior context. It creates a new artifact version and marks the old one superseded.

Example rollback:

```text
User context: I want dealer churn.
Upload evidence: file contains painter loyalty points but no dealer purchases.
Orchestrator decision: reopen DataInventoryAgent.
Question: This file describes painter engagement, not dealer purchases. Do you want the first model to focus on painter disengagement, or can you upload dealer transaction data?
```

## Vertical Blueprint Layer
The orchestrator uses vertical blueprints derived from `CompanyList.md` and `DataPoints.md`.

Blueprint fields:
- vertical
- example companies
- likely customer entities
- likely influencer entities
- common file types
- common grains
- seasonality rules
- common churn definitions
- common action owners
- known data gaps

Example blueprint types:

| Data family | Likely files | Common entity | Common rollback risk |
| --- | --- | --- | --- |
| Transaction-only | orders, invoices, sales, credit | retailer, dealer, distributor | no date, no customer key, no value measure |
| Service or warranty | service calls, warranty claims, install records | dealer, end customer, asset | service file cannot join to transaction file |
| Loyalty or membership | points, tiers, rewards, training | influencer, mechanic, mason, painter | influencer data uploaded but customer target is dealer |
| Returns or fulfillment | returns, expiry, delivery, route | dealer, retailer, stockist | returns are at invoice level but sales are monthly summaries |
| Field interaction | visits, calls, beat plans, demos | outlet, doctor, farmer, dealer | field notes have names but no stable IDs |

Blueprints guide questions. They do not hard-code answers.

## Question Generation Rules
Agents ask one question per turn.

A question must:
- reduce a blocking or high-impact uncertainty
- map to the agent artifact
- include options when options reduce user effort
- allow free text
- allow skip when progress can continue
- use the user's company, vertical, and role only when known
- explain why the answer changes the next step
- proceed with target-market defaults when the question would only confirm the obvious

A question must not:
- ask from a fixed survey list
- assume one company pattern for all companies
- ask for model metrics before trust criteria
- ask the user to know schema terms when business terms work
- block upload unless the file cannot be accepted
- delay first useful analysis for context that can be inferred later
- ask sales leaders to confirm field-execution defaults unless evidence contradicts them

## Done Definition
An agent can be `done_for_now` or `confirmed`.

`done_for_now` means:
- artifact schema validates
- blocking unknowns are empty
- non-blocking unknowns are named
- next agent can start using assumptions and open risks

`confirmed` means:
- artifact schema validates
- exit criteria pass
- required fields have grounding
- open risks are either resolved or accepted by the user
- next agent can start without inventing missing context

The orchestrator is allowed to reject `done_for_now` or `confirmed` if grounding or handoff safety fails.

## Blocked Definition
A session is blocked when no agent can proceed without user action or another file.

Blocked examples:
- user wants customer churn but has no customer identifier
- user wants dealer output but has no dealer names or codes
- user wants field action by owner but no owner or territory exists and the user rejects continuing without it
- user wants validation against known lost customers but no history window exists

A blocked state must show the user the smallest unblock action.

## Implementation Sequence
Build the orchestrator before expanding agents.

1. Define artifact models and artifact store.
2. Define agent result schema with `done_for_now`, `confirmed`, `blocked`, and `rollback_request` states.
3. Define orchestrator route schema with upload-anytime and reopen decisions.
4. Implement UploadAgent and document/data intake before strict context completion.
5. Implement PersonaAgent, CompanyContextAgent, and DataInventoryAgent as intake agents with provisional artifacts.
6. Implement DocumentUnderstandingAgent for decks, PDFs, sheets, notes, and watchlists.
7. Implement DataUnderstandingAgent using uploaded profiles and existing context artifacts.
8. Add DataReadinessAgent and RiskDefinitionAgent.
9. Add SignalDesignAgent, ModelValidationAgent, and ActionOutputAgent.

## UI Shape
The UI should show one active question at a time, but upload should always remain available.

Visible elements:
- upload area for data and documents
- current agent name when an agent is asking
- why the agent is asking
- one question
- options plus free text
- skip or continue-with-assumption when safe
- assumptions the system is using
- artifact summary when an agent exits for now
- reopen message when context changes
- smallest unblock action when blocked

The user should feel like the system is trying to understand their business from evidence before asking them to type explanations.
