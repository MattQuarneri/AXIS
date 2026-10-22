# The fourteen components

> Assembled by `build.py` from AXIS-Design.md, AXIS-Specification.md. To change it, edit the source document and rebuild.

Precise definitions of each part, the familiar term each one corresponds to, and how AXIS relates to patterns you may already use. Read the entry you need; you rarely need the whole file.

## Contents

- AXIS in conventional engineering terms
- Canonical Meanings
- Core Mental Shifts
- Relationship to Existing Patterns
- Non-Goals

## AXIS in conventional engineering terms

| AXIS term | Closest familiar term | What AXIS adds |
|-----------|-----------------------|----------------|
| **Form** | schema, type, model shape | separates structural definition from live mutable state |
| **Instance** | entity record, aggregate state, document | makes mutable state explicit and versionable |
| **Identity** | id, key, stable reference | separates enduring sameness from runtime-scoped projections |
| **Token** | session, revision handle, workflow handle, scoped reference | treats runtime-scoped identity projection as a first-class design concern |
| **Facet** | capability map, policy surface, role overlay | makes available operations explicit without burying them in conditionals |
| **Intent** | command, request DTO, semantic event | captures normalized meaning instead of raw transport data |
| **Bond** | schema relationship, foreign key rule, aggregate boundary | defines ownership and composition rules between Forms |
| **Link** | hydrated reference, join, graph query result | traverses and resolves relationships dynamically |
| **Action** | pure domain function, reducer, use-case step | must stay deterministic and side-effect free |
| **Manager** | coordinator, application service, orchestrator | owns routing, workflow, and commit for one boundary |
| **Effect** | side-effect descriptor, infrastructure command | keeps IO as data until execution time |
| **Impact** | effect handler, infrastructure executor | is the only place where IO actually occurs |
| **Wrapper** | endpoint, screen, route, consumer host | names the structural boundary separately from business capability |
| **Adapter** | controller, input mapper, request normalizer | converts raw edge input into stable internal meaning |

## Canonical Meanings

### FORM — Immutable Essence of Being

Forms are the **generative definitions** that determine what state *can* be: schemas, types, templates, structural contracts.

A Form defines:
- `shape` — the structure of valid state (fields, types, constraints)
- `defaults` — initial values and factory patterns
- `invariants` — conditions that must always hold

**Forms generate; they do not hold.**

A Form is to an Instance as a class is to an object, a schema is to a record, a template is to a document. But unlike a class, a Form carries no behavior — only structure.

### INSTANCE — Projected Expression of Being

An Instance is the **materialized state** generated from a Form within a runtime context.

An Instance holds:
- `formRef` — back-reference to the Form it was generated from
- `identityRef` — the Identity this Instance belongs to
- `revisionId` — current version/hash
- `state` — the live value snapshot

**All mutable state lives here.**

Multiple Instances of the same Identity may coexist:
- the committed head
- an optimistic branch (during async workflows)
- a stale cache (in another Wrapper)
- an undo stack entry

### IDENTITY — Immutable Essence of Identity

Identity is the **stable reference** that names and addresses state. It is the principle of *sameness across time*.

An Identity is:
- `entityId` — a stable, immutable key (string, URI, composite key)
- `formRef` — which Form governs this entity's shape
- `versioning policy` — how revisions are tracked (hash, counter, timestamp)

**Identity defines *what* something is and how to find it. It does not hold live values.**

### TOKEN — Projected Expression of Identity

A Token is the **temporal projection** of an Identity into a specific runtime context. It is how an Identity appears as it moves through time, sessions, and scopes.

A Token carries:
- `identityRef` — the Identity it represents
- `scope` — where this token is valid (session, request, transaction)
- `expiry` — when it ceases to be authoritative
- `claims` — contextual attributes (permissions, roles, capabilities)

**Tokens are issued, scoped, and revocable. Identities are none of these.**

**Who mints Tokens?** The Manager (or a dedicated sub-component it delegates to). Adapters extract raw auth material and pass it through in the Intent; the Manager resolves that material into a Token with appropriate claims based on system state. This centralizes identity resolution and claim assignment in one place.

`Token` is a family name, not a requirement that every projection share one concrete implementation. In practice, the family commonly shows up as session tokens, revision cursors, workflow handles, and wrapper- or cache-scoped references. Most systems need only one or two of these. AXIS groups them because they all answer the same design question: how does this Identity appear here, now, with what scope or authority?

### FACET — Immutable Essence of Meaning

Facets define **capability surfaces** — the ways something may be viewed or interacted with.

A Facet is:
- `capability` → `Action` delegate (or pipeline)

Facets are:
- static definitions
- data structures (maps of function references)
- dynamically selected by the Manager based on context

**Facets define policy affordances, not UI widgets.** They answer: "given this context, what can be done?"

### INTENT — Projected Expression of Meaning

Intent is a normalized description of *meaning*:
> "What someone meant to do."

An Intent carries:
- `kind` — the type of intent
- `capability` — which Facet capability this targets
- `identityRef` — the entity being acted upon
- `payload` — the data of the intent
- `wrapperCtx` — which Wrapper context originated this
- `meta` — timestamps, correlation IDs, provenance

**Intents are loggable, replayable, testable artifacts.** They are the system's semantic event stream.

### BOND — Immutable Essence of Relating (Having)

Bonds define **static relationship and composition rules** between different Forms or Identities.

A Bond defines:
- `ownerRef` — which Form or Identity owns the relationship
- `targetRef` — which Form or Identity is targeted by the relationship
- `cardinality` — the nature of the association (`one-to-one` | `one-to-many` | `many-to-many`)
- `invariants[]` — relational constraints that must hold true between related states

**Bonds structure topology; they do not hold references or resolve graphs.**

### LINK — Projected Expression of Relating (Having)

A Link is the **materialized traversal** of a Bond within a runtime context.

A Link holds:
- `bondRef` — back-reference to the Bond it was generated from
- `sourceRef` — the source Identity being traversed from
- `resolvedRefs` — the resolved target Identities or pre-hydrated target Instances
- `scope` — where this link is valid (transaction, request, cache boundary)

**Links resolve, hydrate, and traverse relationships at runtime.**

### ACTION — Immutable Essence of Doing

Actions are **pure functions**. They transform state and declare effects without performing either.

Signature:
```
(stateSnapshot, intent) → { delta, effects[] }
```

**Rules:**
- No IO
- No mutation
- No global reads
- Deterministic

Actions may be composed into pipelines: validate → compute → transform → declare effects.

### MANAGER — Projected Expression of Doing

The Manager is the **runtime orchestrator**. It is the only component that wires other components together and drives execution.

It has four internal responsibilities:

- **Binder**: Wrapper events → Adapters → Manager dispatch
- **Router**: Intent → Facet → Action delegate (policy- and context-driven)
- **Workflow**: Multi-step async orchestration, sagas, token lifecycle
- **Committer**: Applies deltas to produce new Instances, issues and revokes Tokens

**Within a given boundary, the Manager is the place where state transitions and orchestration are coordinated.**

**Boundary discipline:** In practice, a Manager must stay boundary-scoped. If it becomes a vague bucket for policy, domain calculations, transport formatting, and integration details, it has stopped being a Manager and started being an unowned application blob. Move pure logic into Actions, transport logic into Wrappers or Adapters, and IO into Impact.

Note: The Manager does *not* execute effects. That belongs to Impact.
Also; if your Manager's dispatch function has more than 3–4 branching paths, you may need multiple Facets rather than more Manager logic.

**Commit validation:** The Manager's commit path should validate Form invariants after applying a delta. If invariants fail, the commit is rejected and the Manager emits a structured failure Effect (e.g., `{ kind: "COMMIT_REJECTED", payload: { violations, delta } }`). This requires no changes to how Actions produce deltas — it's a safety net that ensures deltas never leave state in an invariant-violating condition.

#### The Composer–Conductor Decomposition

A Manager has two distinct roles: composing the system's structure and conducting its runtime performance.

**The Composer** (Binder) is concerned with *structure*: what instruments (components) exist, what the score (bindings) looks like, what sections play together. The Composer wires Adapters to Wrappers, registers Facets, and establishes the composition. It runs at setup time and when the system's structure changes (a new service registers, a feature flag flips). The Composer decides *what's possible*.

**The Conductor** (Router + Workflow + Committer) is concerned with *performance*: when a particular Intent arrives, which section picks it up, at what tempo (sync vs. async), with what dynamics (retry policy, timeout). The Conductor decides *what happens now*.

In an orchestra, the conductor doesn't tell each violinist which notes to play — the section handles that. Similarly, the Manager shouldn't contain routing logic for every capability inline. Instead, each "section" is a Facet (or a cluster of related Facets), and the Manager's routing is just: "this Intent goes to this section." The section (Facet → Action chain) handles the details.

**When to decompose:**

- **The Composer grows complex?** You need more Facets, not more wiring logic.
- **The Conductor grows complex?** You likely need a Workflow sub-component (saga/process manager), not more conditional branches.
- **The Conductor coordinates across fundamentally different domains?** You need separate Managers communicating through Effects.

The metric for splitting: if two concerns in the Manager don't share state transitions or workflow coordination, they belong in different sections. If dispatch has a branch for "user management" and a branch for "billing," and those branches never interact within a single dispatch cycle, they should be separate Facets (sections) — or potentially separate Managers (bounded contexts) if they also have different Instance stores.

### EFFECT — Immutable Essence of Changing

An Effect is a **declared description of a side effect** — a pure value that describes what *should* happen in the world, without doing it.

An Effect carries:
- `kind` — the type of effect (IO, emit, notify, persist, schedule)
- `target` — what system/resource is affected
- `payload` — the data to carry
- `retryPolicy` — how failures should be handled
- `compensatingEffect` — what to do on rollback

**Effects are data, not execution.** They are produced by Actions, collected by the Manager, and handed to Impact for execution.

### IMPACT — Projected Expression of Changing

Impact is the **runtime execution of declared Effects** — the point where the system actually touches the outside world.

Impact responsibilities:
- Execute Effects against real targets (network, disk, external APIs)
- Handle retries, timeouts, and failure recovery
- Execute compensating Effects on rollback
- Emit follow-up Intents when an Effect's result requires further processing
- Report outcomes back to the Manager

**Impact is the only place where side effects actually occur.**

### WRAPPER — Immutable Essence of Bridging

Wrappers are **structural boundaries** that host interaction surfaces.

Examples:
- Screens, panels, routes
- API endpoint definitions
- DOM roots, canvas contexts
- Message queue consumers

**Wrappers host interaction surfaces but do not contain business logic.**

### ADAPTER — Projected Expression of Bridging

Adapters convert **raw events + runtime context** into Intents.

**Responsibilities:**
- Read Wrapper-local inputs (forms, selections, request bodies)
- Extract raw authentication material (headers, cookies, API keys) and pass it through in the Intent
- Normalize raw events into stable Intents

**Rules:**
- No IO
- No state mutation
- No identity resolution (extracting raw auth material is not resolving identity — minting a Token is)
- No business decisions

Adapters are the *only* path from the outside world into the system's Intent stream.

**On Tokens:** Adapters should never issue Tokens. A Token is a scoped, temporal projection of Identity with claims (permissions, roles, expiry) — that's a security decision. The Adapter's job is normalization: extract the raw auth material (the header value, the cookie, the API key string) and include it in the Intent via a `rawAuth` field or in the payload. The Manager (or a dedicated sub-component it delegates to) mints the Token, because only the Manager understands what claims to grant given the current system state. This also centralizes Token validation in one place rather than scattering it across Adapters for different Wrappers.

## Core Mental Shifts

1. Events don't do work — **they express intent**
2. Effects are data — **Impact is execution**
3. State changes are values — **not mutations**
4. Identity is permanent — **Tokens are temporary**
5. Forms generate — **Instances hold**
6. Facets are data — **not type annotations**
7. Composition is **runtime responsibility** (the Manager's job)
8. Side effects have **two phases**: declaration (Effect) and execution (Impact)
9. Relationships are declared — **Bonds structure, Links traverse**

## Relationship to Existing Patterns

### MVC → AXIS

| MVC | AXIS Essence | AXIS Expression | What changed |
|-----|--------------|-----------------|--------------|
| Model | FORM (shape) | INSTANCE (state) | Model split into definition vs. live values |
| View | FACET (capabilities) | INTENT (meaning) | View split into "what can be seen" vs. "what was meant" |
| Controller | ACTION (logic) | MANAGER (orchestration) | Controller split into pure logic vs. runtime wiring |
| *(none)* | IDENTITY | TOKEN | Identity axis is new — MVC doesn't address it |
| *(none)* | BOND | LINK | Relating (Having) axis is new — MVC leaves relationships implicit |
| *(none)* | EFFECT | IMPACT | Changing axis is new — MVC conflates effects into Controller |
| *(none)* | WRAPPER | ADAPTER | Bridging axis is new — MVC assumes a single context |

### Flux / Redux → AXIS

Flux introduced the unidirectional data flow: Action → Dispatcher → Store → View. AXIS preserves this flow but decomposes it further:

- **Flux Action** ≈ AXIS Intent (a description of what happened)
- **Flux Dispatcher** ≈ AXIS Manager (routes intents to logic)
- **Flux Store** ≈ AXIS Instance (holds state)
- **Flux Reducer** ≈ AXIS Action (pure state transformation)

The key difference: Redux thunks and middleware conflate effect declaration with effect execution. AXIS separates them into EFFECT (data) and IMPACT (execution), making side effects testable without mocking middleware.

### CQRS → AXIS

CQRS separates commands (writes) from queries (reads). In AXIS, this separation emerges naturally from the Facet system:

- A **command** is an Intent whose capability maps to a state-mutating Action in a write Facet
- A **query** is an Intent whose capability maps to a read-only Action in a read Facet
- Different Tokens can grant access to different Facets — command access vs. query access

CQRS is not a separate pattern to adopt; it's a Facet configuration.

### Event Sourcing → AXIS

AXIS's Intent stream *is* an event source. Store Intents (or committed deltas) and you get replay, audit, and temporal queries for free. The difference: AXIS names all the other components around the event stream (Forms validate, Actions transform, Effects declare consequences), while Event Sourcing as typically described leaves those as implementation details.

### Events and Handlers

The generic "event → handler" pattern is the most common abstraction in software. AXIS decomposes it into *specific, testable seams*:

```
Generic:     Event  →  Handler
AXIS:        Event  →  Adapter  →  Intent  →  Manager  →  Facet  →  Action
             (raw)     (normalize)  (meaning)   (route)    (select)   (execute)
```

Each step is independently testable. The generic pattern gives you one seam; AXIS gives you five.

## Non-Goals

AXIS does not prescribe:
- A specific programming language or framework
- UI component structure or rendering strategy
- A particular database or persistence technology
- Deployment topology or infrastructure patterns

AXIS is a **thinking tool** — a structural vocabulary that turns architecture into enforceable, composable, testable layers for both humans and machine agents.
