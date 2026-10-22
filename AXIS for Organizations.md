# AXIS for Organizations

*An organizational interpretation of Agentically eXtensible Instruction Structures for process and workflow engineering.*

**Status:** Draft organizational design guide  
**Date:** 2026-10-08

## 1. Purpose and basis

AXIS can be applied to an organization by treating its operating model as the structure through which intent becomes coordinated behavior and produces change. Values constrain goals; goals guide projects and processes; responsibilities determine who may decide and act; execution produces evidence that changes the organization's understanding of its state.

This guide develops that interpretation from [AXIS-Principles.md](AXIS-Principles.md), using the fourteen-component model in [AXIS-Specification.md](AXIS-Specification.md), the boundary and composition guidance in [AXIS-Design.md](AXIS-Design.md), the contracts in [AXIS-Code.md](AXIS-Code.md), and the pragmatic adoption approach in [AXIS-Lite.md](AXIS-Lite.md). The [June 2026 conversation summary](AXIS-Conversation-Summary-2026-06-29.md) also motivates this extension by describing AXIS as a model of codified knowledge becoming behavior.

The mappings below are proposed organizational applications, not claims that the existing software specification already defines an organizational standard. They provide a vocabulary and design method for human, AI, and mixed workforces. They can be expressed in charters, operating procedures, task records, decision tables, workflow systems, or agent instructions.

The central design question is:

> For an intended change, what responsibility owns it, what capability can produce it, which agent is qualified and authorized to exercise that capability, and what evidence establishes the result?

## 2. From organizational intent to change

The Cognitive Flow of Change maps naturally to organizational design:

| AXIS level | Organizational expression | Design artifact or question |
|---|---|---|
| Values | Principles and constraints on acceptable conduct | What must remain true even when pursuing a goal? |
| Goals | Desired outcomes and measures | What change matters, for whom, by when? |
| Plans | Project plans and process strategies | Which capabilities and dependencies will achieve the goal? |
| Declaratives | Definitions, policies, constraints, and recorded facts | What is required, permitted, and currently known? |
| Imperatives | Directives and obligations to perform work | What must be done, and who owns the obligation? |
| Instructions | Procedures, task briefs, and execution guidance | What inputs, methods, limits, and acceptance criteria apply? |
| Actions | Defined decision and transformation logic | How do supplied facts lead to a proposed decision or change? |
| Behaviors | Actual coordinated execution over time | How are decisions and work carried out in context? |
| Change | Delivered outcomes and their consequences | What actually changed, and what evidence supports that claim? |

For example: a value of customer trust constrains a goal of faster onboarding; a plan composes Sales, Finance, and Operations capabilities; policies define readiness; tasks request checks and provisioning; execution produces an active customer account and measured onboarding results.

Keep traceability in both directions. A task should identify the goal or process obligation it serves. A goal should identify the work, constraints, and evidence through which it will be achieved. If an instruction contradicts a higher-level constraint, surface the conflict to the designated decision owner.

The flow also needs feedback. Execution evidence updates recorded state; measured outcomes may justify changes to plans, procedures, or policies. Changes to values or goals require their own governance rather than being silently inferred from local execution.

## 3. Essence and Expression in an organization

**Essence** is the defined operating model: department mandates, role definitions, capability contracts, process definitions, relationship rules, and policy versions.

**Expression** is the organization operating in context: staffed teams, current assignments, active projects, running process cases, individual requests, decisions, and execution outcomes.

Examples:

- A role definition describes responsibility; an appointment assigns a particular agent to that role for a scope and period.
- A process definition describes valid work; a process case records one occurrence of that work.
- A department charter describes its mandate; its current staffing, workload, and performance are live state.
- A task template defines required inputs and completion evidence; a task instance holds the actual assignee, status, and outputs.

Organizational Essence is **stable and versioned**, not permanently unchangeable. Preserve each approved definition version and make its replacement explicit. A running case should identify the versions it uses. Moving it to a new definition requires a migration decision when the change affects responsibilities, authority, or acceptance criteria.

One person or system may serve several architectural functions. The separation concerns responsibilities and records; it does not require fourteen departments, job titles, or applications.

## 4. The fourteen-component organizational mapping

“Direct” means the distinction can be implemented as an organizational contract or record. “Adapted” means the design principle transfers, but software properties such as determinism require qualification.

| Axis | Essence: organizational definition | Expression: organizational realization | Mapping |
|---|---|---|---|
| Being | **FORM:** Shape and invariants of a department, role, project, process case, task, or deliverable record | **INSTANCE:** Actual department state, project, process case, task, or deliverable at a recorded revision | Direct |
| Identity | **IDENTITY:** Stable reference for an organizational entity or agent | **TOKEN:** Scoped appointment, delegation, assignment authority, or reference to a particular revision | Direct; a delegation need not be a digital credential |
| Meaning | **FACET:** Capability surface available for a role and context, mapping operations to defined decision logic | **INTENT:** A normalized request to exercise a capability on a particular case or entity | Direct |
| Relating | **BOND:** Rules for ownership, reporting, participation, dependencies, and handoffs | **LINK:** Resolved participants, dependencies, and related records for a particular case | Direct |
| Doing | **ACTION:** Defined evaluation or decision logic that proposes state changes and declares needed execution | **MANAGER:** Boundary-scoped coordination of routing, workflow, and accepted state transitions | Adapted; human judgment is not inherently a pure function |
| Changing | **EFFECT:** Description of work to perform, including its target, limits, and required evidence | **IMPACT:** Actual execution and reported result of that work | Direct for declared versus performed work; actual outcomes require observation |
| Bridging | **WRAPPER:** Defined intake or interaction surface, such as a service desk, form, meeting channel, or partner portal | **ADAPTER:** Translation of incoming material into a locally meaningful request | Direct; translation must not silently confer authority |

### Definitions that should not be collapsed

- **Form versus Instance:** A process definition is not a running case. A required deliverable is not an existing deliverable.
- **Identity versus Token:** Being the same employee or AI agent does not imply retaining the same delegated authority.
- **Facet versus Intent:** Permission to evaluate an application is not a request to evaluate this application.
- **Bond versus Link:** “Every case has one accountable owner” is a rule; “Operations owns case C-42” is a resolved relationship.
- **Action versus Impact:** Evaluating whether provisioning is permissible is separate from actually provisioning an account.
- **Effect versus outcome:** A work order describes intended execution; it does not prove completion or business success.
- **Manager versus supervisor:** AXIS Manager names a coordination function. It may be implemented by a person, a workflow service, or both, and need not match a line-management position.

## 5. Departments, processes, projects, and tasks

These describe different parts of the operating model:

| Organizational concept | Principal responsibility | AXIS interpretation |
|---|---|---|
| Department | Steward a domain of expertise, capability quality, resources, and policy | Charter and record Forms; owned state boundaries; Facets; agent relationships through Bonds and Links |
| Process | Define repeatable work that transforms inputs into accepted outcomes | Versioned definition composing Actions, Effects, relationships, and coordination rules |
| Process case | Carry out one occurrence of a process | Instances with identity, current state, task Links, evidence, and scoped coordination |
| Project | Achieve a bounded goal through a temporary composition of capabilities | Project Form and Instance; work decomposition; project-scoped coordination and delegations |
| Task | Define an assignable obligation with explicit completion criteria | Task Form and Instance referencing an Intent, capability, executor, and declared work |
| Agent | Supply human or machine capacity to perform defined responsibilities | Agent Identity and profile Instance; qualifications; role appointments; scoped Tokens |

A department may steward a process without performing every step. A project may invoke several departmental processes. A task can belong to a project, a recurring process case, or both through explicit relationships.

A task is usually larger than an AXIS Action. It may contain intake, evaluation, authorization, execution, and verification. Map those responsibilities inside the task rather than calling every real-world activity a pure Action.

Design ownership around capabilities and state, then connect those boundaries to departments. One department may contain several boundaries. One shared service may support several departments. An organizational chart alone does not define the workflow architecture.

### Distributed ownership with end-to-end accountability

A customer-onboarding coordinator may own the case's overall progress. Finance owns the financial-clearance decision; Operations owns provisioning status; Sales owns the commercial handoff. The coordinator consumes their acknowledged outcomes and maintains the case record. It does not overwrite their authoritative records.

Each boundary should publish the five contracts recommended by AXIS Lite:

1. **Owned state:** Records and decisions it may change.
2. **Accepted Intents:** Requests it can receive and their required inputs.
3. **Emitted Effects:** Work or requests it may send outward.
4. **Returned outcomes:** Acknowledgements, decisions, evidence, and failure results.
5. **Policy scope:** Delegations, constraints, and capability-selection rules it enforces.

An end-to-end owner is accountable for integration and resolution. That does not automatically grant authority over every participating department's decisions.

## 6. Roles, agents, skills, and knowledge

Keep four questions distinct:

| Question | Organizational design element |
|---|---|
| Who is this? | Agent Identity and current profile |
| What responsibility are they serving here? | Role definition and scoped appointment |
| What work can they perform competently? | Skills, qualification evidence, and available knowledge |
| What may they do in this case? | Valid delegation, selected Facet, and contextual constraints |

The software specification already places role claims in Tokens, capabilities in Facets, responsibility logic in Actions, and authorization in Manager routing. The organizational extension adds explicit qualification and knowledge requirements to those contracts without introducing another AXIS axis.

### Role definition

Define each role with its purpose, accountable outputs, capability surface, required skills, required knowledge, decision limits, review obligations, and escalation route. A role definition describes a possible assignment; it does not appoint anyone.

### Agent profile and appointment

Record the agent's identity, agent type, steward, evidenced skills, current availability, relevant tool access, and qualification status. Represent project membership, departmental affiliation, and role appointments through explicit relationships. An appointment or delegation identifies its issuer, agent, role, scope, validity period, limits, and revocation conditions.

An AI agent's profile should identify the model/tool configuration relevant to qualification. A configuration change may require requalification for affected capabilities. A human's job title or an AI agent's self-description is insufficient evidence of competence or authority.

### Skills and knowledge

**Skills** describe the ability to perform work. **Knowledge** supplies the facts, policies, methods, and domain context needed for that work. Possessing one does not establish the other.

For each capability, define:

- Required skills and acceptable evidence of proficiency.
- Required knowledge sources, owners, versions, freshness expectations, and access restrictions.
- Required tools, input records, and output artifacts.
- Conditions requiring peer review, specialist support, or escalation.

Supply a task-specific context package: request, state snapshot, resolved dependencies, policy versions, relevant knowledge, tool permissions, and acceptance criteria. Agents may use an approved discovery capability when needed, but they should record the sources and assumptions it adds. This applies AXIS's “dependencies are supplied, not discovered” principle to work without pretending that exploratory work has no unknowns.

### Assignment and routing

Use an explicit eligibility rule:

```text
Eligible = valid appointment and authority
           + required skills with acceptable evidence
           + required knowledge and tool access
           + compatible capacity and timing
           + required independence from conflicting roles
```

The `+` signs mean all conditions must be satisfied, not a numerical score. Select among eligible agents using declared priority, availability, continuity, or workload rules. Record the selection and acknowledgement. Recheck authority and critical preconditions before execution, especially after a long wait.

When no suitable agent is available, hold or escalate the task with a reason. Explicit alternatives include training, supplying missing context, narrowing the assignment, obtaining specialist assistance, or revising the schedule. Do not silently grant authority or lower qualifications to make routing succeed.

## 7. Decision, coordination, and execution

AXIS's separation of Actions, Managers, Effects, and Impact is particularly useful for process engineering.

### Action: decide from supplied information

An Action evaluates a supplied state snapshot and Intent, returning a proposed state delta and declared Effects. Examples include checking completeness, calculating eligibility, applying an approval threshold, or proposing a routing decision.

For deterministic rules, retain the software contract directly:

```text
(state snapshot, normalized request, supplied policy context)
    → proposed state change + declared execution requests
```

Human and generative-AI judgment cannot simply be declared pure or deterministic. Apply the separation as a discipline: record inputs, policy versions, reasoning, uncertainty, and proposed results before consequential execution. Research, interviews, measurements, and tool calls are execution steps that gather evidence; their results become inputs to subsequent evaluation. In software implementing this model, Actions still obey AXIS's strict purity rules.

### Manager: coordinate within an owned boundary

Map the four AXIS Manager responsibilities as follows:

| Responsibility | Organizational application |
|---|---|
| Binder / Composer | Establish intake routes, capability registries, role relationships, and executor contracts |
| Router | Interpret authority and context; select the capability and eligible agent |
| Workflow / Conductor | Track dependencies, capacity acknowledgements, timing, parallel work, retries, and escalation |
| Committer | Accept valid state transitions against current state, record decisions and evidence, and issue or revoke delegations within its authority |

Process designers compose the operating model; coordinators conduct particular cases. These functions may share personnel but should have distinct responsibilities. Changing a running case is not permission to rewrite its process definition.

### Effect: describe work before performing it

An execution request should identify what is to happen, the target, authorized scope, executor capability, dependencies, completion evidence, deadline, and failure treatment. Add approval requirements only where the operating policy requires them. Existing delegation can authorize routine work without a separate approval step each time.

### Impact: execute and return evidence

Executors perform the declared work and report the actual outcome, artifacts, timings, deviations, and failures. A person may both coordinate and execute, but the records should still distinguish the authorization, execution attempt, and result.

Committing “authorized” or “scheduled” state does not establish that work occurred. Completion requires the relevant evidence and acceptance check. Likewise, completion of a task does not establish that the higher-level goal was achieved; outcome measures must assess that separately.

## 8. Workflow state, handoffs, and failure

A useful starting lifecycle for a task is:

```text
Requested → Accepted → Ready → Assigned → In progress
          → Evidence submitted → Verified → Closed
```

Define allowed transitions, their owners, and their conditions. Add named states such as Awaiting approval, Blocked, Rejected, Failed, Cancelled, or Rework where they have distinct operational meaning. Tailor the lifecycle to the process rather than requiring every label.

Examples of invariants:

- Every accepted case has exactly one accountable coordinator.
- An assigned task has a qualified assignee and valid scope of authority.
- A downstream step starts only after its required inputs are accepted.
- A required independent reviewer is not the producer of the reviewed work.
- A closed case contains the required outcome evidence or an authorized exception disposition.

Validate these at state acceptance, using current records and the applicable definitions. When facts change, preserve that observation even if it reveals a violation. For example, an expired delegation during execution should produce an exception or blocked state, not suppress the fact that execution occurred.

### Handoff contract

For each departmental handoff, define the sender, receiving capability, required inputs, acknowledgement deadline, rejection reasons, completion deadline, returned evidence, escalation owner, and correlation reference.

Sending a request does not mean the receiving department accepted the obligation. Distinguish receipt, acceptance, completion, and verification. The receiving boundary validates and commits its own state; the sender updates its dependency state from acknowledged outcomes.

This is the organizational equivalent of Effects crossing a boundary and being normalized into receiving Intents. It may occur through a meeting or phone call as well as a workflow tool. The important contract is explicit meaning, authority, and acknowledgement, rather than a particular transport.

### Failure and recovery

| Situation | Designed response |
|---|---|
| Incomplete or ambiguous request | Return a structured clarification request; retain provenance |
| No eligible agent or insufficient capacity | Queue, renegotiate timing, or escalate to the resource owner |
| Missing or outdated knowledge | Obtain authoritative context before the affected decision |
| Rejected handoff | Record the reason and route correction to its owner |
| Deadline exceeded | Identify the blocked dependency and escalate through a named route |
| Execution failed | Record attempt and actual result; retry only under the declared policy |
| Partial or uncertain execution | Reconcile the target's actual state before repeating work |
| Acceptance evidence fails | Open rework or an exception; preserve the submitted evidence |
| Irreversible consequence | Apply a defined remedy or escalation and record residual consequences |

Avoid duplicate execution by giving consequential work a stable execution reference and checking prior attempts. A timed-out request may already have succeeded. Compensation is further work; it does not erase a sent message, undo elapsed labor, or guarantee reversal of every consequence.

Independent departmental commitments are not automatically atomic. If a cross-boundary invariant requires all-or-nothing behavior, design explicit reservations and acknowledgements, define a shared authoritative boundary, or define how partial commitment is detected and reconciled.

## 9. Worked example: customer onboarding

This illustrative process shows how departments steward capabilities while a case coordinator composes their work. Its business policies are examples, not prescribed requirements.

**Goal:** Activate an eligible customer within the agreed lead time, with an accepted commercial package and complete handoff evidence.

| Boundary | Owned state and responsibility | Capabilities and agents |
|---|---|---|
| Sales | Commercial package and customer requirements | Sales agent prepares package; Sales reviewer accepts completeness |
| Finance | Financial assessment and clearance | Qualified Finance agent evaluates terms under delegated limits |
| Operations | Provisioning work and activation evidence | Operations executor provisions; designated verifier checks results |
| Onboarding coordination | Case identity, dependencies, milestones, and overall disposition | Case coordinator routes requests and accepts case transitions |

**Definition layer:** The onboarding-case Form specifies required records, statuses, and closure evidence. Bonds require one case coordinator, one current Finance disposition, and related Operations tasks. Facets expose `submit-package`, `assess-terms`, `authorize-provisioning`, and `verify-activation` to appropriate roles and lifecycle contexts.

**Running case:** Case `ONB-042` has a stable Identity and current Instance. Its Links resolve the customer, accepted commercial-package revision, appointed agents, Finance decision, and Operations task. Role appointments supply authority for this case; they do not confer authority over every customer.

1. Sales submits a package through the defined intake surface (**Wrapper**). Intake translation (**Adapter**) creates an Intent to start onboarding and preserves the originating evidence.
2. The case **Manager** validates the request, creates the case, and routes the completeness **Action**. Missing inputs produce a correction request rather than provisioning work.
3. With a complete package, the Action declares an **Effect** requesting Finance assessment. Delivery of that request is **Impact**. Finance acknowledges acceptance in its own boundary and assigns a qualified agent with current policy knowledge.
4. Finance gathers any required evidence through execution steps, evaluates the supplied record, and accepts its decision under its own rules. Its returned outcome includes the disposition, scope, policy version, evidence, and expiry or recheck conditions.
5. The case coordinator accepts that outcome. If clearance permits provisioning, an Action proposes `Ready for provisioning` and declares the provisioning Effect. The coordinator checks the current preconditions before accepting that transition and dispatching the work.
6. Operations acknowledges the request. Its authorized executor performs provisioning (**Impact**) and returns the account reference and execution evidence. A failed or uncertain attempt remains visible and follows the recovery policy.
7. Verification establishes that the provisioned service matches the accepted requirements. The coordinator closes the case only when the required departmental outcomes and evidence are present.
8. Lead time, rework, and activation quality feed process review. Any approved improvement creates a new process-definition version; active cases are migrated explicitly when necessary.

A project to onboard an initial customer cohort can reference many instances of this recurring process. The project owns cohort-level milestones and outcomes; each case retains its own identity, evidence, authority, and departmental decisions.

## 10. Process and workflow engineering method

Use the smallest set of artifacts that makes the following decisions inspectable:

1. **State the intended change.** Define beneficiaries, outcome measures, constraints, and the goal owner. Separate deliverables from the business outcomes they are expected to cause.
2. **Map the current behavior.** Follow an actual case through intake, decisions, work, waiting, handoffs, and closure. Identify hidden approvals, unofficial records, and exception paths.
3. **Define capability and state ownership.** Name the responsibilities and authoritative records. Connect them to departments without assuming every department is one boundary.
4. **Separate definitions from occurrences.** Define Forms for the relevant project, process case, task, and deliverable records. Identify their Instances and revision rules.
5. **Define relationships.** Use Bonds for ownership and dependency rules. Specify the Links that each running case must resolve.
6. **Define roles and authority.** Specify Facets, appointment scopes, decision limits, and who can grant or revoke them.
7. **Define qualification and context.** Specify skills, qualification evidence, knowledge dependencies, tool access, capacity requirements, and review conditions.
8. **Normalize intake.** Define accepted Intents and the Adapter rules for each interaction surface. Retain provenance and a clarification route.
9. **Separate evaluation from execution.** Identify Actions, declared Effects, executors, and required evidence. State which steps require approval and which are covered by existing delegation.
10. **Design coordination.** Define lifecycle transitions, dependency sequencing, parallel work, state acceptance, and escalation ownership. Set handoff and capacity commitments explicitly.
11. **Design failure paths.** Cover rejection, absence, stale inputs, timeout, partial execution, rework, cancellation, and any feasible compensation.
12. **Walk through and pilot.** Run normal and exception cases using realistic inputs. Check that agents can find their context, authority, responsibilities, and completion criteria. Revise the design using measured results.

The resulting operating model should let a new participant answer: what work exists, why it matters, who owns it, what I may do, what I need, who receives my output, and how completion is established.

## 11. Reusable design templates

These are organizational record templates, not additions to the canonical AXIS software type contracts. Merge them into existing tools where possible and reference authoritative records rather than copying their contents.

### Boundary or department capability contract

```text
Name / identity:
Mandate and goals served:
Definition version and steward:
Owned state and authoritative records:
Accepted request kinds and required inputs:
Capability → decision/procedure mapping:
Roles, skills, and knowledge requirements:
Delegation issuer, scope, limits, and revocation:
Outgoing work requests and receiving boundaries:
Returned outcomes and evidence:
Coordination and state-acceptance owner:
Service commitments and escalation route:
```

### Process definition

```text
Process identity / version / definition owner:
Purpose and outcome measures:
Trigger, entry conditions, and accepted Intent:
Case Form, lifecycle, and invariants:
Participating boundaries and relationship rules:
Capabilities, Actions, and decision criteria:
Task definitions and dependency structure:
Required role appointments, skills, and knowledge:
Effects, executors, and required acknowledgements:
Approval and verification rules:
Timing, capacity, retry, and escalation policies:
Failure, cancellation, rework, and remedy paths:
Closure criteria and evidence:
Change control and active-case migration policy:
```

### Project charter

```text
Project identity / sponsor / accountable coordinator:
Goal, beneficiaries, and outcome measures:
Scope, constraints, milestones, and budget:
Deliverables and acceptance owners:
Processes and capabilities to compose:
Participating departments and resource commitments:
Work decomposition and dependency Links:
Project-scoped authority and decision limits:
Risks, exceptions, and escalation route:
Handover, closure, and outcome-review criteria:
```

### Task definition and running task

```text
Definition:
  Task kind / version / purpose:
  Required capability and decision/procedure reference:
  Inputs, preconditions, and dependency rules:
  Required skills, knowledge, tools, and authority:
  Declared work and execution limits:
  Output, acceptance criteria, and evidence:
  Review, timing, failure, and escalation rules:

Occurrence:
  Task identity / current revision / definition version:
  Project or process-case reference / originating Intent:
  Accountable owner / executor / verifier if required:
  Appointment or delegation reference:
  Resolved inputs, knowledge versions, and dependencies:
  Status / acknowledgements / timestamps:
  Decision record / execution references and attempts:
  Outputs, evidence, deviations, and acceptance result:
```

### Execution request and outcome

```text
Effect:
  Stable execution reference / originating case and decision:
  Work kind / target / payload:
  Executor capability / authority / limits:
  Dependencies / deadline / retry policy:
  Required evidence / failure or compensation plan:

Impact outcome:
  Execution reference / executor identity / attempt:
  Actual result and observed target state:
  Artifacts, evidence, and timestamps:
  Deviations, uncertainty, failures, and residual consequences:
  Receiving state owner / verification disposition:
```

## 12. The ten AXIS principles as organizational design rules

| AXIS principle | Organizational application |
|---|---|
| Organize around behavior, not technology | Design around outcomes and responsibilities; select tools to support them |
| Follow the Cognitive Flow of Change | Trace work to goals and constraints, and outcomes back to evidence |
| Separate Essence from Expression | Separate charters, definitions, and policies from live assignments and cases |
| Treat behavior as the engine of change | Assess actual execution and resulting outcomes, as well as documented plans |
| Treat side effects as data until execution | Describe consequential work, its limits, and its completion evidence before performing it |
| Treat responsibility as a routing problem | Give requests explicit owners, eligible executors, and escalation paths |
| Prefer composition over inheritance | Compose projects and processes from capabilities; do not infer authority solely from hierarchy |
| Design explicit boundaries | Specify owned decisions, authoritative records, and handoff contracts |
| Dependencies are supplied, not discovered | Supply task context and collaborators; make additional discovery explicit |
| Form follows responsibility | Let process artifacts reveal what the organization is responsible for doing |

## 13. Limits of the mapping

The organizational use of AXIS is strongest where responsibilities, records, authority, and handoffs can be made explicit. Some software guarantees do not transfer literally:

- **People are not deterministic functions.** Judgment, negotiation, learning, and creativity need room for interpretation. Record uncertainty and review conditions rather than claiming repeatability.
- **A model of state is not the world itself.** Evidence can be incomplete, late, or disputed. Track provenance and uncertainty, and distinguish a recorded decision from an observed fact.
- **Organizational authority is not just a software token.** A digital claim represents a delegation; its legitimacy comes from the organization's actual governance. Skills and tool access also do not create authority.
- **An Intent is not proof of an event.** Audit and reconstruction need decisions, state revisions, definition versions, and execution evidence. Replaying requests alone cannot recreate human judgment or external outcomes.
- **Real-world execution is not generally reversible.** Design remedies and reconciliation where exact rollback is impossible. Simulations and historical replay must not automatically repeat consequential work.
- **Explicit contracts do not replace relationships.** Collaboration can remain conversational and adaptive. Capture decisions and obligations where they affect ownership, authority, or outcomes.

Exploratory work fits through time-bounded assignments with defined questions, permissible methods, resource limits, and learning outputs. Its goal may be to reduce uncertainty rather than deliver a predetermined answer.

## 14. Lightweight adoption and design review

Start with one process and six essentials:

1. A clear outcome and accountable owner.
2. A versioned process definition and distinct case record.
3. Qualified agents with explicit scope of authority.
4. Defined inputs, dependencies, and departmental handoffs.
5. Declared work separated from execution evidence.
6. Completion criteria and exception routes.

Introduce more detailed Facets, Tokens, Bonds, and coordination structures when complexity otherwise hides responsibility or authority. Existing forms, procedures, service catalogs, responsibility matrices, and task boards can carry AXIS distinctions without being renamed.

Review a proposed design against concrete cases:

- Can every consequential decision and state transition be traced to its owner and authority?
- Can an agent obtain the required skills support, knowledge, and inputs without guessing?
- Can a department change its internal method while honoring its external contract?
- Can the coordinator distinguish waiting, rejection, failure, and uncertain completion?
- Can another participant verify completion from evidence rather than a status label?
- Can a definition change be distinguished from a change to a running case?
- Does the design reduce ambiguity enough to justify its maintenance cost?

Evaluate a pilot using lead time, waiting time by boundary, handoff rejection, rework, unresolved exceptions, evidence completeness, and the goal's outcome measures. Include the effort spent maintaining the model. Simplify artifacts that add effort without clarifying decisions, dependencies, or accountability.

>
> **Attribution and License**
>
> AXIS, formulated by Matthew Quarneri — MENTIC Cognitive Systems. © 2026 MENTIC LLC. Originally published at [mentic.com/AXIS](https://mentic.com/AXIS).
>
> If you found these ideas useful you could [Buy Me a Coffee](https://buymeacoffee.com/mattq4) to show your support.
> 
> Except where otherwise noted, this document is licensed under the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). Code examples in it may also be used under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0). See [LICENSE.md](LICENSE.md).
>
> You may share and adapt this material, including for commercial purposes, under the license terms. When sharing the material or adaptations, give appropriate credit to Matthew Quarneri and MENTIC Cognitive Systems, link to the original at [mentic.com/AXIS](https://mentic.com/AXIS), provide a link to the license, and indicate any changes. Attribution must not imply endorsement.
>
> **Support and Advisory Services**
>
> If AXIS contributes substantial commercial value to your organization, please consider supporting its continued development through sponsorship or a paid advisory engagement. Financial support is voluntary and is not a condition of the license. Or just buy us a coffee [here](https://www.buymeacoffee.com/mentic).
>
> For sponsorship, workshops, process design, or agent orchestration consulting, contact [consulting@mentic.com](mailto:consulting@mentic.com).
>
> ---
>
> This permits commercial reuse **without mandatory payment**, while requiring attribution under the license. [Official license summary](https://creativecommons.org/licenses/by/4.0/)
>
> For more interesting ideas visit [MENTIC Cognitive Systems](https://www.mentic.com)