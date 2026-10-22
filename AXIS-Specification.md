# AXIS: Agentically eXtensible Instruction Structures - Architectural Specification
(aka The Essence–Expression Model for Software Architecture)
**Author:** Matthew Quarneri (matt@mentic.com)
**Organization:** MENTIC Cognitive Systems  
**Version:** 2026.05.22  
**Copyright:** © 2026 MENTIC LLC  
**License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — see [LICENSE.md](LICENSE.md)

> This Specification is the complete AXIS reference and the ideal full-profile shape.
> For most application work, start with `AXIS-Lite.md` and escalate into this document when workflow, identity, policy, or cross-boundary complexity requires it.
> `AXIS-Design.md` reconciles the full and lite profiles; `AXIS-Code.md` turns both into implementation guidance.

This document defines **AXIS** as a *meta-architectural model* for structuring codified software systems into coherent compositional components that are easy to understand, maintain, and evolve. The ideal is to enable both human and machine agents to reason about, generate, and orchestrate software architectures with clarity and precision.

AXIS structures codifications — structured statements that derive and drive state — along two orthogonal dimensions: **Immutable Essence** and **Projected Expression**; static and dynamic; being and doing; form and function.

This decomposition clearly separates the *core identity and structure* of a system (Essence) from its *runtime behavior and interactions* (Expression), while maintaining explicit mappings between them.

---

## 0. The Grid

| Axis | Immutable Essence | Projected Expression |
|------|-------------------|----------------------|
| **Being** | FORM — static generative structure | INSTANCE — dynamic generated state |
| **Identity** | IDENTITY — immutable sameness | TOKEN — temporal identity projections |
| **Meaning** | FACET — defined capability views | INTENT — active interpretations |
| **Relating (Having)** | BOND — static composition and relationship rules | LINK — dynamic traversal and reference resolution |
| **Doing** | ACTION — pure control logic | MANAGER — contextual orchestration |
| **Changing** | EFFECT — declared causal descriptions | IMPACT — runtime causal execution |
| **Bridging** | WRAPPER — structural boundaries | ADAPTER — dynamic transformations |

**Reading the grid:**
- **Columns**: Essence defines *what something is*. Expression defines *how it manifests at runtime*.
- **Rows**: Each axis names a fundamental concern. Every axis has exactly one Essence component and one Expression component.
- **The diagonal**: a thing *exists* (Being), *is itself* (Identity), *is perceived* (Meaning), *has relationships* (Relating), *acts* (Doing), *causes change* (Changing), and *connects* (Bridging).

**In prose:**

Forms define generative structure, realized as Instances of state.
Identity provides immutable sameness, expressed through Tokens across time.
Facets define how something may be seen, while Intents determine how it is interpreted.
Bonds define static relationship and composition rules, realized as Links of traversal.
Actions define pure control logic, contextualized and executed by Managers.
Effects declare what should happen; Impacts are what actually does.
Wrappers establish structural boundaries, while Adapters enable dynamic transformation between them.

### How to use this document

- Treat this Specification as the ideal, complete vocabulary, contracts, and topology for full AXIS systems.
- Treat `AXIS-Lite.md` as the pragmatic default for ordinary application work.
- Treat `AXIS-Design.md` as the bridge between the ideal model and pragmatic decomposition decisions.
- Treat `AXIS-Code.md` as the implementation guide that preserves the same rules while allowing lighter shapes when the problem does not need full ceremony.

### AXIS in conventional engineering terms

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

---

## 1. Canonical Meanings

### FORM — Immutable Essence of Being
Forms say: "This is the shape of state, and the rules that govern it."

Forms are the **generative definitions** that determine what state *can* be: schemas, types, templates, structural contracts.

A Form defines:
- `shape` — the structure of valid state (fields, types, constraints)
- `defaults` — initial values and factory patterns
- `invariants` — conditions that must always hold

**Forms generate; they do not hold.**

A Form is to an Instance as a class is to an object, a schema is to a record, a template is to a document. But unlike a class, a Form carries no behavior — only structure.

---

### INSTANCE — Projected Expression of Being
Instances say: "This is the state as it exists now, with its own history and version."

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

---

### IDENTITY — Immutable Essence of Identity
Identity says: "This is the same thing across time and contexts, and this is how to address it."

Identity is the **stable reference** that names and addresses state. It is the principle of *sameness across time*.

An Identity is:
- `entityId` — a stable, immutable key (string, URI, composite key)
- `formRef` — which Form governs this entity's shape
- `versioning policy` — how revisions are tracked (hash, counter, timestamp)

**Identity defines *what* something is and how to find it. It does not hold live values.**

Identity enables:
- stable addressing across contexts
- lookup and resolution
- equality testing ("is this the same entity?")

---

### TOKEN — Projected Expression of Identity
Tokens say: "This Identity is present here and now, with this scope, authority, and lifetime."

A Token is the **temporal projection** of an Identity into a specific runtime context. It is how an Identity appears as it moves through time, sessions, and scopes.

A Token carries:
- `identityRef` — the Identity it represents
- `scope` — where this token is valid (session, request, transaction)
- `expiry` — when it ceases to be authoritative
- `claims` — contextual attributes (permissions, roles, capabilities)

**Tokens are issued, scoped, and revocable. Identities are none of these.**

**Who mints Tokens?** The Manager (or a dedicated sub-component it delegates to). Adapters extract raw auth material and pass it through in the Intent; the Manager resolves that material into a Token with appropriate claims based on system state. This centralizes identity resolution and claim assignment in one place.

`Token` is a family name, not a claim that every projection must share one concrete implementation. In practice, the family commonly includes:
- **Session Tokens** — auth/session projections with claims and expiry
- **Revision Tokens** — projections pointing at a specific Instance revision
- **Workflow Tokens** — handles for optimistic branches, transactions, or saga scopes
- **Scope Tokens** — wrapper-, cache-, or view-scoped projections

Most systems need only one or two of these. AXIS groups them because they all answer the same design question: how does this Identity appear here, now, with what scope or authority?

Examples:
- A session token issued for a user Identity
- A revision token pointing to a specific Instance version
- A workflow token for an optimistic branch or long-running process
- A scope token scoping an Instance to a particular Wrapper or cache

---

### FACET — Immutable Essence of Meaning
Facets say: "Given this context, these are the ways this may be viewed or acted upon."

Facets define **capability surfaces** — the ways something may be viewed or interacted with.

A Facet is:
- `capability` → `Action` delegate (or pipeline)

Facets are:
- static definitions
- data structures (maps of function references)
- dynamically selected by the Manager based on context

**Facets define policy affordances, not UI widgets.** They answer: "given this context, what can be done?"

---

### INTENT — Projected Expression of Meaning
Intents say: "This is what someone meant to do."

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

---

### BOND — Immutable Essence of Relating (Having)
Bonds say: “Here is what it means to relate, and the invariants that govern it.”

Bonds define **static relationship and composition rules** between different Forms or Identities.
Instead of burying relationship rules inside unstructured Form attributes or procedural code, a Bond explicitly declares:
- Cardinality & Ownership: Does User own Project (cascade delete, single consistency boundary), or is it a loose association?
- Aggregate Boundaries: Which identities must be committed together to satisfy multi-entity invariants?
- Access Propagation: If I have access to a Parent, do I automatically inherit access to the Child?

A Bond defines:
- `ownerRef` — which Form or Identity owns the relationship
- `targetRef` — which Form or Identity is targeted by the relationship
- `cardinality` — the nature of the association (`one-to-one` | `one-to-many` | `many-to-many`)
- `invariants[]` — relational constraints that must hold true between related states

**Bonds structure topology; they do not hold references or resolve graphs.**

With a Bond, the Committer understands the aggregate boundary natively. It knows that a transaction on Project must evaluate the invariants of both Project and User forms before executing the commit.

---

### LINK — Projected Expression of Relating (Having)
Links say: "This is the resolved relationship traversal for this specific source, in this specific context."

A Link is the **materialized traversal** of a Bond within a runtime context. It manages:
- Graph Hydration: How references are materialized.
- Traversal Paths: Going from userInstance to projectInstances without manual SQL or API calls in your Actions.
- Referential Integrity: Ensuring a commit doesn't create orphaned references.
- Connect

A Link holds:
- `bondRef` — back-reference to the Bond it was generated from
- `sourceRef` — the source Identity being traversed from
- `resolvedRefs` — the resolved target Identities or pre-hydrated target Instances
- `scope` — where this link is valid (transaction, request, cache boundary)

**Links resolve, hydrate, and traverse relationships at runtime.**

With a Link, the Manager can pre-hydrate an aggregate tree before dispatching to an Action, eliminating the need for Actions to perform async two-pass loading of related entities.

---

### ACTION — Immutable Essence of Doing
Actions say: "This is the pure state transformation and the Effects it declares."

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

---

### MANAGER — Projected Expression of Doing
Managers say: "This is how to orchestrate doing things in context."

The Manager is the **runtime orchestrator**. It is the only component that wires other components together and drives execution.

It has four internal responsibilities:

#### Binder
- Wrapper events → Adapters
- Adapters → Manager dispatch

#### Router
- Intent → Facet → Action delegate
- Policy- and context-driven (Facet selection)

#### Workflow
- Multi-step async orchestration
- Sagas / process managers
- Token lifecycle management

#### Committer
- Applies deltas to produce new Instances
- Validates Form invariants after applying deltas; rejects commits that violate invariants
- Issues and revokes Tokens

**Within a given boundary, the Manager is the only place where state transitions and orchestration are coordinated.**

**Boundary discipline:** A Manager is a boundary-scoped coordinator, not a catch-all service class. It owns one consistency boundary, one commit path, and one policy surface. Pure business calculations belong in Actions; transport formatting belongs in Wrappers or Adapters; IO belongs in Impact. If a Manager accumulates unrelated domain logic, split the boundary rather than letting `Manager` become a bucket.

**Commit validation:** The Manager's commit path should validate Form invariants after applying a delta. If invariants fail, the commit is rejected and the Manager emits a structured failure Effect (e.g., `{ kind: "COMMIT_REJECTED", payload: { violations, delta } }`). This requires no changes to how Actions produce deltas — it's a safety net that ensures deltas never leave state in an invariant-violating condition.

Note: The Manager does *not* execute effects. That belongs to Impact.

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

---

### EFFECT — Immutable Essence of Change
Effects say: "This is what should happen in the world as a result of this action."

An Effect is a **declared description of a side effect** — a pure value that describes what *should* happen in the world, without doing it.

An Effect carries:
- `kind` — the type of effect (IO, emit, notify, persist, schedule)
- `target` — what system/resource is affected
- `payload` — the data to carry
- `retryPolicy` — how failures should be handled
- `compensatingEffect` — what to do on rollback

**Effects are data, not execution.** They are produced by Actions, collected by the Manager, and handed to Impact for execution.

This separation is the core of testability: you can assert that an Action declared the correct Effects without ever performing IO.

---

### IMPACT — Projected Expression of Change
Impact says: "This is what actually happens in the world when we execute these Effects."

Impact is the **runtime execution of declared Effects** — the point where the system actually touches the outside world.

Impact responsibilities:
- Execute Effects against real targets (network, disk, external APIs)
- Handle retries, timeouts, and failure recovery
- Execute compensating Effects on rollback
- Emit follow-up Intents when an Effect's result requires further processing
- Report outcomes back to the Manager

**Impact is the only place where side effects actually occur.**

Impact is to Effect as Instance is to Form: the runtime realization of a static declaration.

---

### WRAPPER — Immutable Essence of Bridging
Wrappers say: "This is the boundary where an outside surface hosts interaction."

Wrappers are **structural boundaries** that host interaction surfaces.

Examples:
- Screens, panels, routes
- API endpoint definitions
- DOM roots, canvas contexts
- Message queue consumers

**Wrappers host interaction surfaces but do not contain business logic.**

They render from Instances and expose event slots that Adapters bind to.

---

### ADAPTER — Projected Expression of Bridging
Adapters say: "This is how we convert edge input into internal structure."

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

---

## 2. Non-Negotiable Contracts

These contracts must hold everywhere:

1. **Adapters always produce Intents** — never raw mutations or direct Action calls
2. **Adapters never mint Tokens** — they extract raw auth material and include it in the Intent; the Manager resolves identity
3. **Actions always return `{ delta, effects[] }`** — never perform IO or mutate state
4. **Effects are data** — declared by Actions, never self-executing
5. **Only Impact executes Effects** — the sole site of side effects
6. **Only the Manager commits state** — producing new Instances and issuing Tokens
7. **Manager validates invariants on commit** — rejecting deltas that would violate Form and Bond invariants
8. **Facets are capability maps** — not type annotations or UI components
9. **Forms are generative** — they define shape, not hold values
10. **Identity is immutable** — only Tokens project identity into temporal contexts
11. **Bonds define composition boundaries** — Actions declare link mutations as deltas, leaving structural validation and cascades to the Committer
12. **Only Links traverse relations** — Graph hydration and reference resolution happen outside pure Actions (e.g., pre-hydrated by the Manager)

---

## 3. Canonical Flow

### Composition Time (Binding)

```
Wrapper.eventSlot  →  Adapter
Intent             →  Facet       (via Manager routing)
Facet              →  Action      (delegate resolution)
Bond               →  Manager     (relationship registration)
Effect             →  Impact      (handler registration)
```

### Runtime (Execution)

```
Event (from outside world)
  ↓
Adapter (normalizes to Intent)
  ↓
Intent (semantic description of meaning)
  ↓
Manager.route() (selects Facet by context + Token)
  ↓
Manager.hydrate() (uses Link to pre-hydrate related entities if required)
  ↓
Facet.delegate (resolves to Action)
  ↓
Action(hydratedInstance, intent) → { delta, effects[] }
  ↓                                    ↓
Manager.commit(delta)              Impact.execute(effects[])
(validates Form & Bond invariants)     ↓
  ↓                                Side effects occur
Instance(identity) updated             ↓
  ↓                                Follow-up Intents emitted
Token refreshed (if needed)
  ↓
Wrapper.render(instance)
```

---

## 4. Folder Structure

A default full-profile layout for humans and agents. In lite or smaller services, folders may be collapsed as long as the same state ownership, IO boundaries, and policy seams remain obvious:

```
/forms          # Generative structure (schemas, types, templates)
/instances      # Live state + versioning
/identity       # Stable references + addressing
/tokens         # Temporal identity projections
/bonds          # Static relationship definitions
/links          # Dynamic reference traversers
/facets         # Capability maps
/intents        # Intent schemas
/actions        # Pure logic
/manager        # Binding / routing / workflow
/effects        # Effect declarations + schemas
/impacts        # Effect executors + handlers
/wrappers       # Structural boundaries
/adapters       # Event → Intent transformers
/tests          # Unit + integration tests
```

---

## 5. Type Contracts (Language-Agnostic)

### Form
```
{
    shape,
    defaults,
    invariants[],
    transitions?      // optional: valid delta shapes for this Form
}
```

### Instance
```
{
    formRef,
    identityRef,
    revisionId,
    state
}
```

### Identity
```
{
    entityId,
    formRef,
    versioningPolicy
}
```

### Token
```
{
    identityRef,
    scope,
    expiry,
    claims
}
```

### Facet
```
{
    delegates: {
        capability: Action | ActionPipeline
    }
}
```

### Intent
```
{
    kind,
    capability,
    identityRef?,
    payload,
    rawAuth?,         // raw auth material extracted by Adapter (header, cookie, key)
    wrapperCtx,
    meta
}
```

### Action
```
(state, intent) → {
    delta,
    effects[]
}
```

### Effect
```
{
    kind,
    target,
    payload,
    retryPolicy?,
    compensatingEffect?
}
```

### Bond
```
{
    ownerRef,         // Form or Identity of the owner
    targetRef,        // Form or Identity of the target
    cardinality,      // 'one-to-one' | 'one-to-many' | 'many-to-many'
    invariants[]      // relational constraint validation functions
}
```

### Link
```
{
    bondRef,          // stable reference to the Bond definition
    sourceRef,        // Identity being traversed from
    resolvedRefs,     // resolved target Identities or pre-hydrated target Instances
    scope             // query boundary metadata
}
```

### Manager
```
dispatch(intent)
bind(wrapper)
commit(delta) → Instance   // validates Form and Bond invariants; rejects on violation
issueToken(identity, scope, rawAuth) → Token
revokeToken(token)
registerBond(bond)
resolveLink(link) → Link   // traverses relationship at runtime
```

### Impact
```
execute(effects[]) → outcomes[]
compensate(effects[])
```

---

## 6. Composition Patterns

### Relational Composition (Bonds & Links)
* **Aggregate Invariant Enforcement**: The Committer uses registered **Bonds** to walk the tree of related entity Instances on each transaction commit. If a related entity's invariants are broken by the delta (e.g., parent total doesn't match sum of child items), the commit is rejected.
* **Declarative Graph Hydration**: The Manager uses **Links** to hydrate relationships prior to Action execution. Instead of making the Action perform asynchronous two-pass loading, the Manager pre-hydrates the aggregate tree using dynamic Links and hands the pre-hydrated state aggregate directly to the Action.

### Capability Overlays
Facets compose via layers:
- Base capabilities
- Role-based capabilities (driven by Token claims)
- Feature-flag capabilities
- Experiment / A/B capabilities

### Action Pipelines
Pure action chains:
```
validate → compute → transform → declare effects
```

### Effect Batching
Effects declared by multiple Actions within a single workflow can be:
- batched for efficiency
- ordered by dependency
- rolled back atomically via compensating Effects

### Event Sourcing
Store Intents or committed deltas to enable:
- replay
- audit
- undo/redo
- temporal queries

### Token-Scoped Views
Different Tokens for the same Identity can yield different Facets:
- Admin Token → full capability Facet
- Read-only Token → restricted Facet
- Expired Token → re-authentication Intent

### Failure Patterns

Every Intent expresses a desired outcome. When the outcome diverges from the desire, the divergence itself is expressible in AXIS — not as an exception, but as a structured flow through the same components.

**Principle: failures are alternate Effects, not exceptions.**

There are three failure points in the canonical flow, and each has a distinct AXIS treatment:

#### 1. Action-level failure (validation, business rule violation)

The Action is pure — it doesn't "fail" in the runtime sense. It returns a delta and effects that *describe* the failure:

```
function transferFunds(state, intent) {
  if (state.balance < intent.payload.amount) {
    return {
      delta: {},  // no state change
      effects: [{
        kind: "INTENT_REJECTED",
        target: "caller",
        payload: {
          originalIntent: intent,
          reason: "insufficient_funds",
          details: { available: state.balance, requested: intent.payload.amount },
        },
      }],
    };
  }
  // ... happy path
}
```

The rejection is an Effect. Impact delivers it. The caller receives a structured rejection, not a thrown error.

#### 2. Impact-level failure (IO error, timeout, external system down)

When Impact cannot execute an Effect, it follows the Effect's declared recovery strategy:

```
// The Effect declares its own failure plan:
{
  kind: "HTTP_POST",
  target: "/api/payments",
  payload: { ... },
  retryPolicy: { maxRetries: 3, backoff: "exponential" },
  compensatingEffect: {
    kind: "ROLLBACK_TRANSFER",
    target: "ledger",
    payload: { reverseOf: originalDelta },
  },
}

// Impact's responsibility:
// 1. Attempt execution
// 2. Retry per retryPolicy
// 3. On exhaustion, execute compensatingEffect
// 4. Emit a follow-up Intent describing the outcome:
//    { kind: "impact.failed", payload: { effect, error, compensated: true } }
```

The follow-up Intent re-enters the system through the Manager, which can route it to an error-handling Facet — logging, user notification, dead-letter queuing, or escalation.

#### 3. Manager-level failure (unroutable Intent, missing Facet, expired Token)

The Manager is the only component that can detect structural failures — an Intent that doesn't match any route, a Token that has expired, a Facet that was unregistered. These are handled by producing Effects directly:

```
// In the Manager's dispatch:
if (!facet) {
  await runImpact([{
    kind: "INTENT_UNROUTABLE",
    target: "caller",
    payload: { intent, reason: "no_matching_facet" },
  }], ctx);
  return;
}
```

**The key insight: at every failure point, the system produces *data* (Effects, follow-up Intents) rather than throwing exceptions.** This makes failures:
- **Loggable** — the same Intent stream captures successes and failures
- **Replayable** — retry a failed Intent against fixed state
- **Testable** — assert that an Action returns the correct rejection Effect without performing IO
- **Composable** — error-handling Facets can be layered just like capability Facets

#### Designing for failure in AXIS

| Concern | Where it lives |
|---------|----------------|
| "Can this operation succeed?" | **Action** — validates and returns a rejection Effect if not |
| "What if IO fails?" | **Effect** — declares retryPolicy + compensatingEffect |
| "What if IO fails after retries?" | **Impact** — executes compensation, emits follow-up Intent |
| "What do we tell the user/caller?" | **Facet** — an error-handling Facet maps failure Intents to notification Actions |
| "What if the Intent can't be routed?" | **Manager** — produces an INTENT_UNROUTABLE Effect |
| "What's the permanent record?" | **Intent stream** — all Intents (successful and failed) are logged |

### Manager Boundaries

Both worked examples use a single Manager. Real systems have multiple bounded contexts, each with its own Manager. The rule:

**Managers never call each other directly. They communicate through Effects and Intents.**

A Manager in one context produces an Effect (e.g., `{ kind: "EMIT_EVENT", target: "order-service" }`). Impact executes it — placing a message on a queue, calling an API, writing to a shared store. The receiving context's Adapter normalizes it into a local Intent, and that context's Manager routes it through its own Facets and Actions.

This means:
- Each Manager owns its own Instances — no shared mutable state
- Each Manager has its own Facet registry — capabilities are local
- Cross-context communication is always asynchronous and explicit
- Failure at the boundary is handled by Effect retry/compensation, not distributed transactions

**One Manager per bounded context. One Instance store per Manager. Effects are the only bridges.**

```
[ Context A ]                    [ Context B ]
Manager A                        Manager B
  ↓                                ↑
Action → Effect                  Adapter → Intent
  ↓                                ↑
Impact ──── (queue/API/store) ────→ Wrapper
```

**Boundary contract:** A complete AXIS Manager should make five things explicit:
- `owned state` — which Forms, Instances, and Identities it is allowed to commit
- `accepted intents` — the commands or intent kinds it accepts
- `emitted effects/events` — the only outward requests it can make of other boundaries
- `returned outcomes` — acknowledgements, failures, and follow-up intents/events
- `policy scope` — which claims, roles, or token scopes it is allowed to interpret

How to decide Manager boundaries:
- Different domain language? Different Manager.
- Different deployment unit? Different Manager.
- Different team? Almost certainly different Manager.
- Same entity viewed differently? Same Manager, different Facets.

### Read Path: The Two-Pass Pattern

Actions are pure — they can't fetch data. So how do reads work?

**The two-pass pattern: "ask to know, tell to show."**

1. **Pass 1 — Request the read:** An Event (e.g., "show profile X") becomes an Intent. The Manager routes it to an Action. The Action can't fetch, so it returns `{ delta: {}, effects: [{ kind: "FETCH_PROFILE", target: "/api/users/123" }] }`.

2. **Impact executes the fetch:** Impact performs the IO and emits a *follow-up Intent* carrying the fetched data.

3. **Pass 2 — Apply the result:** The follow-up Intent re-enters the Manager, routes to an Action that applies the data as a delta, the Instance is updated, and the Wrapper renders.

```
Pass 1:  Event → Adapter → Intent → Action → { delta: {}, effects: [FETCH] }
                                                              ↓
                                                          Impact (fetch)
                                                              ↓
Pass 2:  Follow-up Intent → Action → { delta: fetchedData, effects: [] }
                                              ↓
                                        Instance updated
                                              ↓
                                        Wrapper renders
```

**Why two passes?** This might seem surprising, but allowing reads to be async two-phase flows rather than synchronous pipelines enables:
- **Retry** — failed fetches can be retried per Effect policy
- **Bundling** — multiple fetch Effects can be batched for efficiency
- **Auditing** — both the request and the result are logged as Intents

**Composition-time hydration:** For initial data loading, a pragmatic shortcut is available: the Manager can hydrate the Instance directly during its `bind()` phase — before the pipeline is live. This is not a violation of AXIS; it's composition-time setup, not a runtime flow. Document both patterns:
- **Runtime fetch:** Two-pass via Effect → Impact → follow-up Intent
- **Composition-time hydration:** Manager loads initial data during bind, before events flow

---

## 7. Rules for Humans

### Code Review Checklist
- Is code in the correct component?
- Are Actions pure (no IO, no mutation)?
- Are Effects declared as data, not executed inline?
- Is mutable state only in Instances?
- Is Identity immutable (no live values)?
- Are Tokens scoped and expirable?
- Are Tokens minted only by the Manager (not Adapters)?
- Does the Manager validate Form invariants on commit?
- Is side-effect execution only in Impact?
- Is orchestration centralized in the Manager?
- Are Facets capability maps (not type annotations)?
- Are Forms purely structural (no behavior)?
- Do Adapters only extract raw auth (no identity resolution)?

### "Where does this code go?"

| If it... | It belongs in... |
|----------|------------------|
| Defines valid state shape | **Form** |
| Holds live mutable state | **Instance** |
| Names/addresses an entity | **Identity** |
| Projects identity into a session/scope | **Token** |
| Defines static relationship/ownership boundaries | **Bond** |
| Resolves and traverses references dynamically | **Link** |
| Mints tokens from raw auth material | **Manager** (or delegate) |
| Maps capabilities to actions | **Facet** |
| Describes what someone meant to do | **Intent** |
| Transforms state (pure logic) | **Action** |
| Orchestrates routing and workflow | **Manager** |
| Validates invariants on commit | **Manager** |
| Declares a side effect | **Effect** |
| Executes a side effect | **Impact** |
| Hosts a UI surface or endpoint | **Wrapper** |
| Converts raw events to Intents | **Adapter** |
| Extracts raw auth material | **Adapter** (passes through in Intent) |

---

## 8. Rules for Machine Agents

### Constraints
1. Never mutate state outside Instance
2. Never perform IO outside Impact
3. Identity is immutable — only Tokens project it into runtime contexts
4. Effects are data — never self-executing
5. In the full AXIS profile, introduce the explicit chain:
   - Adapter → Intent → Manager → Facet → Action → Effect → Impact
  Collapse pieces only in lighter profiles where doing so does not hide IO, ownership, or policy boundaries.
6. Prefer **new capabilities** (new Facet entries) over conditionals
7. Forms define shape — never embed behavior in a Form
8. Adapters never mint Tokens — they extract raw auth and include it in the Intent
9. Manager validates Form and Bond invariants on commit — rejecting invalid deltas
10. Actions express relationship changes purely as data deltas, leaving DB and hydration concerns to the Link layer

### Test Generation
- **Actions**: unit test with snapshot state + intent → assert delta + effects
- **Adapters**: raw event → assert correct Intent produced
- **Manager routing**: intent + token → assert correct Facet selected
- **Manager commit**: delta + invariants (Form & Bond) → assert accepted or rejected
- **Bonds & Links**: assert relational traversal resolves to correct Instances; assert constraints block violations
- **Effects**: assert Action declares expected Effect data
- **Impact**: integration test with mocked targets → assert side effects executed
- **Tokens**: assert scoping, expiry, and claim propagation

---

## 9. Diagrams

### Binding (Composition Time)
```
BOND → MANAGER
WRAPPER → ADAPTER → MANAGER → FACET → ACTION → EFFECT → IMPACT
```

### Runtime Flow
```
Event → Adapter → Intent → Manager ──(Link)──→ Action → { Δ, Effects }
                    ↑          |                 ↓            ↓
                 Token      Facet           Instance     Impact
                 (scope)   (route)         (commit Δ)   (execute)
                                                 ↓
                                              (Bond)
```

### The Essence–Expression Split
```
    Essence (static)         Expression (dynamic)
    ─────────────────        ─────────────────────
    FORM          ←────→     INSTANCE
    IDENTITY      ←────→     TOKEN
    FACET         ←────→     INTENT
    BOND          ←────→     LINK
    ACTION        ←────→     MANAGER
    EFFECT        ←────→     IMPACT
    WRAPPER       ←────→     ADAPTER
```

---

## 10. Core Mental Shifts

1. Events don't do work — **they express intent**
2. Effects are data — **Impact is execution**
3. State changes are values — **not mutations**
4. Identity is permanent — **Tokens are temporary**
5. Forms generate — **Instances hold**
6. Facets are data — **not type annotations**
7. Relationships are declared — **Bonds structure, Links traverse**
8. Composition is **runtime responsibility** (the Manager's job)
9. Side effects have **two phases**: declaration (Effect) and execution (Impact)

---

## 11. Relationship to Existing Patterns

AXIS doesn't emerge from nothing — it decomposes and restructures ideas present in MVC, Flux, CQRS, Event Sourcing, and the broader event-driven / handler pattern. Here's specifically what's different.

### MVC → AXIS

MVC has three roles. AXIS observes that each role has a static definition and a dynamic manifestation, then splits accordingly:

| MVC | AXIS Essence | AXIS Expression | What changed |
|-----|--------------|-----------------|--------------|
| Model | FORM (shape) | INSTANCE (state) | Model split into definition vs. live values |
| View | FACET (capabilities) | INTENT (meaning) | View split into "what can be seen" vs. "what was meant" |
| Controller | ACTION (logic) | MANAGER (orchestration) | Controller split into pure logic vs. runtime wiring |
| *(none)* | IDENTITY | TOKEN | Identity axis is new — MVC doesn't address it |
| *(none)* | BOND | LINK | Relating (Having) axis is new — MVC leaves relationships implicit |
| *(none)* | EFFECT | IMPACT | Change axis is new — MVC conflates effects into Controller |
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

The generic "event → handler" pattern is the most common abstraction in software. AXIS decomposes it into *specific, testable seams* rather than treating it as atomic:

```
Generic:     Event  →  Handler
AXIS:        Event  →  Adapter  →  Intent  →  Manager  →  Facet  →  Action
             (raw)     (normalize)  (meaning)   (route)    (select)   (execute)
```

Each step is independently testable. The generic pattern gives you one seam; AXIS gives you five.

### Roles, Responsibilities, and Capabilities

These three concepts are already fully expressed across the existing grid:

| Concept | AXIS component | How |
|---------|----------------|-----|
| **Role** (who) | TOKEN claims | A role is a claim carried by a Token |
| **Capability** (what) | FACET delegate keys | A capability is an entry in a Facet |
| **Responsibility** (how) | ACTION | A responsibility is a pure function |
| **Authorization** (when/where) | MANAGER routing | The Manager selects a Facet based on Token claims |

A role is not its own architectural component — it's a *value* in a Token that drives Facet selection. Adding a ROLE axis would pull apart what the Token→Facet→Action chain already expresses cleanly.

Example: "Admin can delete users" means:
- Token carries `claims: { role: "admin" }` (Identity axis)
- Manager selects `adminFacet` when it sees that claim (Doing axis)
- `adminFacet.delegates["user.delete"]` points to the `deleteUser` Action (Meaning axis)
- The Action is pure logic (Doing axis)

No new axis needed. The existing grid composes roles, capabilities, and responsibilities from its fundamental parts.

---

## 12. Non-Goals

AXIS does not prescribe:
- A specific programming language or framework
- UI component structure or rendering strategy
- A particular database or persistence technology
- Deployment topology or infrastructure patterns

AXIS is a **thinking tool** — a structural vocabulary that turns architecture into enforceable, composable, testable layers for both humans and machine agents.

---

## 13. Worked Example: User Profile Editor (Vanilla JS SPA)

This example traces a single feature — editing a user profile — through 12 of the 14 AXIS components. The feature has no relationships between entities, so it needs no Bond or Link. Vanilla JS is used deliberately: AXIS is the only architecture, with no framework concepts to confuse the picture.

> **Note on Shadow DOM**: Each Wrapper below uses Shadow DOM for structural encapsulation. The Shadow DOM is a natural Wrapper — it establishes a boundary, hides internals, and exposes a public surface (attributes, events, slots). The *business* capability surface is the Facet, not the DOM surface.

---

### FORM — `forms/userProfile.js`

The generative definition of valid profile state.

```js
// forms/userProfile.js
export const UserProfileForm = {
  shape: {
    displayName: { type: "string", maxLength: 100, required: true },
    email:       { type: "string", pattern: /^[^@]+@[^@]+$/, required: true },
    bio:         { type: "string", maxLength: 500, required: false },
    avatarUrl:   { type: "string", required: false },
  },
  defaults: {
    displayName: "",
    email: "",
    bio: "",
    avatarUrl: null,
  },
  invariants: [
    (state) => state.displayName.length > 0 || "displayName must not be empty",
    (state) => !state.email || /^[^@]+@[^@]+$/.test(state.email) || "invalid email",
  ],
};
```

---

### IDENTITY — `identity/userIdentity.js`

Stable reference. A user identity is just an ID and a pointer to the Form.

```js
// identity/userIdentity.js
export function createUserIdentity(userId) {
  return Object.freeze({
    entityId: userId,            // stable, immutable
    formRef: "UserProfileForm",
    versioningPolicy: "hash",    // revisions tracked by content hash
  });
}
```

---

### INSTANCE — `instances/profileInstance.js`

Live mutable state. Created from a Form, owned by an Identity.

```js
// instances/profileInstance.js
import { UserProfileForm } from "../forms/userProfile.js";

export function createProfileInstance(identity, state = null) {
  const liveState = state ?? { ...UserProfileForm.defaults };
  return {
    formRef: identity.formRef,
    identityRef: identity.entityId,
    revisionId: hash(liveState),
    state: liveState,
  };
}

export function applyDelta(instance, delta) {
  const next = { ...instance.state, ...delta };
  return {
    ...instance,
    state: next,
    revisionId: hash(next),
  };
}
```

---

### TOKEN — `tokens/sessionToken.js`

Temporal projection of identity into a session scope.

```js
// tokens/sessionToken.js
export function issueSessionToken(identity, claims = {}) {
  return {
    identityRef: identity.entityId,
    scope: "session",
    expiry: Date.now() + 30 * 60 * 1000,  // 30 minutes
    claims: {
      canEdit: true,
      role: "owner",
      ...claims,
    },
  };
}

export function isExpired(token) {
  return Date.now() > token.expiry;
}
```

---

### FACET — `facets/profileFacets.js`

Capability maps selected by the Manager based on Token claims.

```js
// facets/profileFacets.js
import { validateAndSave, cancelEdit } from "../actions/profileActions.js";

// Full edit capabilities — selected when token.claims.canEdit === true
export const editableFacet = {
  delegates: {
    save:   validateAndSave,
    cancel: cancelEdit,
  },
};

// Read-only — selected when token is absent or canEdit === false
export const readOnlyFacet = {
  delegates: {
    // no save, no cancel — only viewing is possible
  },
};
```

---

### INTENT — `intents/profileIntents.js`

Semantic descriptions of what the user meant to do.

```js
// intents/profileIntents.js
export function saveProfileIntent(identityRef, payload, wrapperCtx) {
  return Object.freeze({
    kind: "profile.save",
    capability: "save",
    identityRef,
    payload,         // { displayName, email, bio }
    wrapperCtx,      // which Wrapper originated this
    meta: { timestamp: Date.now() },
  });
}

export function cancelEditIntent(identityRef, wrapperCtx) {
  return Object.freeze({
    kind: "profile.cancel",
    capability: "cancel",
    identityRef,
    payload: null,
    wrapperCtx,
    meta: { timestamp: Date.now() },
  });
}
```

---

### ACTION — `actions/profileActions.js`

Pure functions. Transform state, declare effects. No IO.

```js
// actions/profileActions.js
import { UserProfileForm } from "../forms/userProfile.js";

export function validateAndSave(state, intent) {
  const next = { ...state, ...intent.payload };

  // Check Form invariants
  const violations = UserProfileForm.invariants
    .map((inv) => inv(next))
    .filter((r) => r !== true);

  if (violations.length > 0) {
    return {
      delta: { _validationErrors: violations },
      effects: [],  // no side effects on validation failure
    };
  }

  return {
    delta: { ...intent.payload, _validationErrors: [] },
    effects: [
      {
        kind: "HTTP_PUT",
        target: `/api/users/${intent.identityRef}/profile`,
        payload: intent.payload,
        retryPolicy: { maxRetries: 2, backoff: "exponential" },
        compensatingEffect: {
          kind: "ROLLBACK_INSTANCE",
          target: intent.identityRef,
          payload: { restoreTo: state },
        },
      },
    ],
  };
}

export function cancelEdit(state, intent) {
  // Cancel declares a workflow effect — the Manager restores committed state.
  // No magic delta keys. The Effect is data describing what should happen.
  return {
    delta: {},
    effects: [{ kind: "RESTORE_COMMITTED", target: intent.identityRef }],
  };
}
```

---

### EFFECT — (declared inline by Actions above)

Effects are data, not a runtime concern. The `effects[]` array returned by `validateAndSave` is the Effect. Restated for clarity:

```js
// What an Effect looks like as a standalone value:
const saveEffect = {
  kind: "HTTP_PUT",
  target: "/api/users/u-1234/profile",
  payload: { displayName: "Alice", email: "alice@example.com" },
  retryPolicy: { maxRetries: 2, backoff: "exponential" },
  compensatingEffect: {
    kind: "ROLLBACK_INSTANCE",
    target: "u-1234",
    payload: { restoreTo: previousState },
  },
};
// This is pure data. Nothing has happened yet.
```

---

### IMPACT — `impacts/httpImpact.js`

The sole site of side effects. Executes declared Effects.

```js
// impacts/httpImpact.js
const handlers = {
  HTTP_PUT: async (effect) => {
    const res = await fetch(effect.target, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(effect.payload),
    });
    if (!res.ok) throw new Error(`PUT failed: ${res.status}`);
    return { ok: true, status: res.status };
  },

  ROLLBACK_INSTANCE: async (effect) => {
    // Manager handles this — emit a follow-up Intent
    return {
      ok: true,
      followUpIntent: {
        kind: "instance.restore",
        identityRef: effect.target,
        payload: effect.payload,
      },
    };
  },
};

export async function execute(effects) {
  const outcomes = [];
  for (const effect of effects) {
    const handler = handlers[effect.kind];
    if (!handler) throw new Error(`No impact handler for: ${effect.kind}`);
    try {
      outcomes.push(await handler(effect));
    } catch (err) {
      // If there's a compensating effect, execute it
      if (effect.compensatingEffect) {
        await execute([effect.compensatingEffect]);
      }
      outcomes.push({ ok: false, error: err.message });
    }
  }
  return outcomes;
}
```

---

### WRAPPER — `wrappers/profileEditor.js`

Structural boundary using Shadow DOM. Hosts the UI, exposes event slots.

```js
// wrappers/profileEditor.js
class ProfileEditor extends HTMLElement {
  constructor() {
    super();
    // Shadow DOM = structural encapsulation boundary (Wrapper)
    this.attachShadow({ mode: "open" });
  }

  // Render from an Instance snapshot — Wrapper never reads state directly
  render(instance) {
    const s = instance.state;
    const errors = s._validationErrors || [];

    this.shadowRoot.innerHTML = `
      <form id="profile-form">
        <label>Name
          <input name="displayName" value="${s.displayName}" />
        </label>
        <label>Email
          <input name="email" type="email" value="${s.email}" />
        </label>
        <label>Bio
          <textarea name="bio">${s.bio}</textarea>
        </label>
        ${errors.length ? `<div class="errors">${errors.join(", ")}</div>` : ""}
        <button type="submit">Save</button>
        <button type="button" id="cancel">Cancel</button>
      </form>
    `;
  }

  // Event slots — the Adapter will bind to these
  get eventSlots() {
    return {
      submit: () => this.shadowRoot.querySelector("#profile-form"),
      cancel: () => this.shadowRoot.querySelector("#cancel"),
    };
  }

  // Read form values — Adapter calls this, Wrapper just provides the surface
  readInputs() {
    const form = this.shadowRoot.querySelector("#profile-form");
    return Object.fromEntries(new FormData(form));
  }
}

customElements.define("profile-editor", ProfileEditor);
export { ProfileEditor };
```

---

### ADAPTER — `adapters/profileAdapter.js`

Converts raw DOM events into Intents and adapts/normalizes data for the wrapper.

```js
// adapters/profileAdapter.js
import { saveProfileIntent, cancelEditIntent } from "../intents/profileIntents.js";

export function bindProfileAdapter(wrapper, identityRef, dispatch) {
  const slots = wrapper.eventSlots;

  slots.submit().addEventListener("submit", (e) => {
    e.preventDefault();
    const payload = wrapper.readInputs();
    dispatch(saveProfileIntent(identityRef, payload, "profile-editor"));
  });

  slots.cancel().addEventListener("click", () => {
    dispatch(cancelEditIntent(identityRef, "profile-editor"));
  });
}
```

---

### MANAGER — `manager/profileManager.js`

The orchestrator. Wires everything. The only place state is committed.

```js
// manager/profileManager.js
import { editableFacet, readOnlyFacet } from "../facets/profileFacets.js";
import { UserProfileForm } from "../forms/userProfile.js";
import { applyDelta } from "../instances/profileInstance.js";
import { isExpired } from "../tokens/sessionToken.js";
import { execute as runImpact } from "../impacts/httpImpact.js";
import { bindProfileAdapter } from "../adapters/profileAdapter.js";

export function createProfileManager(wrapper, identity, token, instance) {
  // Workflow: track committed vs. working state
  let committedInstance = instance;
  let currentInstance = instance;
  let currentToken = token;   // composition-time bootstrap (see entry point)

  // --- Router: select Facet based on Token ---
  function selectFacet() {
    if (!currentToken || isExpired(currentToken) || !currentToken.claims.canEdit) {
      return readOnlyFacet;
    }
    return editableFacet;
  }

  // --- Committer: apply delta with invariant validation ---
  function commit(delta) {
    const proposed = { ...currentInstance.state, ...delta };
    const violations = UserProfileForm.invariants
      .map((inv) => inv(proposed))
      .filter((r) => r !== true);
    if (violations.length > 0) {
      return { ok: false, violations };
    }
    currentInstance = applyDelta(currentInstance, delta);
    return { ok: true };
  }

  // --- Conductor: dispatch loop ---
  async function dispatch(intent) {
    const facet = selectFacet();
    const action = facet.delegates[intent.capability];

    if (!action) {
      console.warn(`No capability "${intent.capability}" in current facet`);
      return;
    }

    // Run pure Action
    const { delta, effects } = action(currentInstance.state, intent);

    // Workflow: separate workflow effects from IO effects
    const ioEffects = [];
    for (const effect of effects) {
      if (effect.kind === "RESTORE_COMMITTED") {
        currentInstance = committedInstance;
      } else {
        ioEffects.push(effect);
      }
    }

    // Committer: validate and apply delta
    if (Object.keys(delta).length > 0) {
      const result = commit(delta);
      if (!result.ok) {
        await runImpact([{
          kind: "COMMIT_REJECTED",
          target: "caller",
          payload: { violations: result.violations, delta },
        }]);
        return;
      }
    }

    // Re-render Wrapper with new Instance
    wrapper.render(currentInstance);

    // Hand IO effects to Impact for execution
    if (ioEffects.length > 0) {
      const outcomes = await runImpact(ioEffects);

      // Workflow: promote to committed on successful IO with state changes
      if (outcomes.every((o) => o.ok) && Object.keys(delta).length > 0) {
        committedInstance = currentInstance;
      }

      // Process follow-up Intents from Impact outcomes
      for (const outcome of outcomes) {
        if (outcome.followUpIntent) {
          await dispatch(outcome.followUpIntent);
        }
      }
    }
  }

  // --- Binder (Composer): wire Wrapper → Adapter → dispatch ---
  function bind() {
    wrapper.render(currentInstance);
    bindProfileAdapter(wrapper, identity.entityId, dispatch);
  }

  return { bind, dispatch };
}
```

---

### Putting It Together — `app.js`

```js
// app.js — the entry point
import { createUserIdentity } from "./identity/userIdentity.js";
import { createProfileInstance } from "./instances/profileInstance.js";
import { issueSessionToken } from "./tokens/sessionToken.js";
import { createProfileManager } from "./manager/profileManager.js";

// 1. Identity — stable reference
const identity = createUserIdentity("u-1234");

// 2. Token — composition-time bootstrap
//    At runtime, Tokens are minted by the Manager from raw auth material.
//    At composition time, the entry point may provide an initial Token directly.
//    This is setup, not a runtime violation — same as Instance hydration below.
const token = issueSessionToken(identity, { canEdit: true, role: "owner" });

// 3. Instance — composition-time hydration (from API, cache, or defaults)
const instance = createProfileInstance(identity, {
  displayName: "Alice",
  email: "alice@example.com",
  bio: "Software engineer",
  avatarUrl: null,
});

// 4. Wrapper — structural boundary (already in DOM)
const wrapper = document.querySelector("profile-editor");

// 5. Manager — wire and go
const manager = createProfileManager(wrapper, identity, token, instance);
manager.bind();

// The runtime flow is now:
//   User clicks Save
//     → Adapter reads form, creates Intent
//     → Manager routes Intent through Token → Facet → Action
//     → Action validates, returns { delta, effects }
//     → Manager commits delta → new Instance → Wrapper re-renders
//     → Impact executes HTTP_PUT effect
//     → On failure, compensating Effect restores previous state
```

---

### What to notice

1. **In this worked example, every file maps to exactly one AXIS component.** That layout makes the architecture explicit, but it is a full-profile example rather than a mandatory topology for every codebase.
2. **The Shadow DOM is a Wrapper**, not a Facet. It provides structural encapsulation. The Facet operates at the business level (what capabilities are available), not the DOM level.
3. **Actions never touched `fetch`**. They declared an Effect. Impact did the fetching.
4. **The Manager validates invariants on commit** as a safety net — even though `validateAndSave` already checks. The safety net catches bugs in Actions that forget.
5. **Cancel uses a workflow Effect, not a magic delta.** `cancelEdit` returns `{ delta: {}, effects: [RESTORE_COMMITTED] }`. The Manager's Workflow handles restoration. No magic keys corrupt Instance state.
6. **The Manager tracks committed vs. working state.** On successful save IO, committed promotes. On cancel, working restores to committed.
7. **Composition-time bootstrapping**: the entry point provides an initial Token and pre-loaded Instance data. At runtime, Tokens are minted by the Manager and data is loaded via the two-pass read path.
8. **Token drives Facet selection.** Change `canEdit: false` in the Token and the save button still renders (Wrapper doesn't know), but `dispatch` finds no `save` capability in `readOnlyFacet`. The architecture enforces access control without conditionals in the Action.
9. **Testing is trivial per layer**: call `validateAndSave()` with test data → assert delta and effects. No mocking fetch. No rendering DOM. No wiring anything.

---

## 14. Worked Example: Extensible Web Server (Vanilla Node.js)

This example traces the design of a web server where **new routes and services can be dynamically added at runtime** — without restarting, without modifying core files. Vanilla Node.js (`http` module) is used to keep AXIS as the sole architecture.

The key insight: dynamic extensibility is not a special mechanism — it's just the Manager binding new Identities, Forms, and Facets into an already-running composition. The same AXIS flow handles the first route and the hundredth.

---

### FORM — `forms/serviceForm.js`

The generative definition of what a valid service plugin looks like, and what a route registration looks like.

```js
// forms/serviceForm.js

// Every service must conform to this shape
export const ServiceForm = {
  shape: {
    name:        { type: "string", required: true },
    version:     { type: "string", pattern: /^\d+\.\d+\.\d+$/, required: true },
    routes:      { type: "array", items: "RouteForm", required: true },
    healthCheck: { type: "function", required: false },
  },
  defaults: {
    routes: [],
    healthCheck: null,
  },
  invariants: [
    (s) => s.name.length > 0 || "service name must not be empty",
    (s) => s.routes.length > 0 || "service must declare at least one route",
    (s) => s.routes.every(r => r.path.startsWith("/")) || "all routes must start with /",
  ],
};

// Each route within a service
export const RouteForm = {
  shape: {
    method:     { type: "string", enum: ["GET", "POST", "PUT", "DELETE", "PATCH"], required: true },
    path:       { type: "string", required: true },
    capability: { type: "string", required: true },  // maps to a Facet delegate key
  },
  defaults: {
    method: "GET",
  },
  invariants: [],
};
```

---

### IDENTITY — `identity/serviceIdentity.js`

Each service gets a stable identity. Routes are addressed through their parent service.

```js
// identity/serviceIdentity.js
export function createServiceIdentity(serviceName) {
  return Object.freeze({
    entityId: `service:${serviceName}`,
    formRef: "ServiceForm",
    versioningPolicy: "semver",
  });
}

// Routes are sub-identities — addressed as service:name/route:path
export function createRouteIdentity(serviceIdentity, method, path) {
  return Object.freeze({
    entityId: `${serviceIdentity.entityId}/route:${method}:${path}`,
    formRef: "RouteForm",
    versioningPolicy: "hash",
  });
}
```

---

### INSTANCE — `instances/serverInstance.js`

The live routing table. This is the dynamic state of the entire server — a map of registered services and their resolved routes.

```js
// instances/serverInstance.js
export function createServerInstance() {
  return {
    formRef: "ServerForm",
    identityRef: "server:main",
    revisionId: 0,
    state: {
      services: {},     // { [serviceId]: serviceConfig }
      routeTable: [],   // [{ method, path, serviceId, capability }]
    },
  };
}

export function applyDelta(instance, delta) {
  const next = { ...instance.state };

  if (delta.registerService) {
    const svc = delta.registerService;
    next.services = { ...next.services, [svc.identity.entityId]: svc };
    next.routeTable = [
      ...next.routeTable,
      ...svc.routes.map((r) => ({
        method: r.method,
        path: r.path,
        serviceId: svc.identity.entityId,
        capability: r.capability,
      })),
    ];
  }

  if (delta.unregisterService) {
    const id = delta.unregisterService;
    const { [id]: _, ...rest } = next.services;
    next.services = rest;
    next.routeTable = next.routeTable.filter((r) => r.serviceId !== id);
  }

  return {
    ...instance,
    state: next,
    revisionId: instance.revisionId + 1,
  };
}
```

---

### TOKEN — `tokens/requestToken.js`

Each incoming HTTP request gets a Token representing the caller's identity and permissions in this request scope.

```js
// tokens/requestToken.js
export function issueRequestToken(rawAuth) {
  return {
    identityRef: extractCallerId(rawAuth.authHeader, rawAuth.apiKey),
    scope: "request",
    expiry: Date.now() + 30_000,   // 30 seconds — request-scoped
    claims: {
      roles: extractRoles(rawAuth.authHeader),
      rateLimit: { remaining: 100, window: 60_000 },
    },
  };
}

function extractCallerId(authHeader, apiKey) {
  // Simplified — real implementation verifies JWT / API key
  if (apiKey) return `apikey:${apiKey.slice(0, 8)}`;
  if (authHeader) return `bearer:${hashToken(authHeader)}`;
  return "anonymous";
}

function extractRoles(authHeader) {
  if (!authHeader) return ["public"];
  // Simplified — real implementation decodes JWT claims
  return ["authenticated"];
}

function hashToken(s) { return s.slice(-8); }
```

---

### FACET — `facets/serviceFacets.js`

Capability maps. Each service registers its own Facet. The management API has a separate Facet for service lifecycle operations.

```js
// facets/serviceFacets.js
import { registerService, unregisterService } from "../actions/managementActions.js";

// Management Facet — for adding/removing services at runtime
export const managementFacet = {
  delegates: {
    "service.register":   registerService,
    "service.unregister": unregisterService,
  },
};

// Service Facets are registered dynamically. This is the registry.
const serviceFacets = {};

export function registerServiceFacet(serviceId, facet) {
  serviceFacets[serviceId] = facet;
}

export function getServiceFacet(serviceId) {
  return serviceFacets[serviceId] || null;
}

// Example: a "greeter" service registers its own Facet
// registerServiceFacet("service:greeter", {
//   delegates: {
//     "greet": greeterAction,
//     "greet.personalized": personalizedGreeterAction,
//   },
// });
```

---

### INTENT — `intents/serverIntents.js`

Normalized descriptions of what a request or management operation means.

```js
// intents/serverIntents.js

// An inbound HTTP request, normalized
export function requestIntent(method, path, body, rawAuth, wrapperCtx) {
  return Object.freeze({
    kind: "http.request",
    capability: null,        // resolved by Manager via route table
    identityRef: null,       // resolved by Manager when minting Token
    payload: { method, path, body },
    rawAuth,                 // raw auth material for Manager to resolve
    wrapperCtx,
    meta: { timestamp: Date.now() },
  });
}

// Register a new service at runtime
export function registerServiceIntent(serviceConfig, token) {
  return Object.freeze({
    kind: "management.register",
    capability: "service.register",
    identityRef: token.identityRef,
    payload: serviceConfig,
    wrapperCtx: "management",
    meta: { timestamp: Date.now() },
  });
}

// Unregister a service
export function unregisterServiceIntent(serviceId, token) {
  return Object.freeze({
    kind: "management.unregister",
    capability: "service.unregister",
    identityRef: token.identityRef,
    payload: { serviceId },
    wrapperCtx: "management",
    meta: { timestamp: Date.now() },
  });
}
```

---

### ACTION — `actions/managementActions.js`

Pure functions for service lifecycle. Also, the pattern for service-specific actions.

```js
// actions/managementActions.js
import { ServiceForm } from "../forms/serviceForm.js";

export function registerService(state, intent) {
  const config = intent.payload;

  // Validate against Form
  const violations = ServiceForm.invariants
    .map((inv) => inv(config))
    .filter((r) => r !== true);

  if (violations.length > 0) {
    return {
      delta: {},
      effects: [{
        kind: "HTTP_RESPONSE",
        target: "caller",
        payload: { status: 400, body: { errors: violations } },
      }],
    };
  }

  // Check for conflicts
  if (state.services[config.identity.entityId]) {
    return {
      delta: {},
      effects: [{
        kind: "HTTP_RESPONSE",
        target: "caller",
        payload: { status: 409, body: { error: "service already registered" } },
      }],
    };
  }

  return {
    delta: { registerService: config },
    effects: [
      {
        kind: "HTTP_RESPONSE",
        target: "caller",
        payload: { status: 201, body: { registered: config.identity.entityId } },
      },
      {
        kind: "LOG",
        target: "audit",
        payload: { event: "service.registered", serviceId: config.identity.entityId },
      },
    ],
  };
}

export function unregisterService(state, intent) {
  const { serviceId } = intent.payload;

  if (!state.services[serviceId]) {
    return {
      delta: {},
      effects: [{
        kind: "HTTP_RESPONSE",
        target: "caller",
        payload: { status: 404, body: { error: "service not found" } },
      }],
    };
  }

  return {
    delta: { unregisterService: serviceId },
    effects: [
      {
        kind: "HTTP_RESPONSE",
        target: "caller",
        payload: { status: 200, body: { unregistered: serviceId } },
      },
      {
        kind: "LOG",
        target: "audit",
        payload: { event: "service.unregistered", serviceId },
      },
    ],
  };
}
```

```js
// actions/greeterActions.js — example service-specific Action
export function greet(state, intent) {
  return {
    delta: {},
    effects: [{
      kind: "HTTP_RESPONSE",
      target: "caller",
      payload: { status: 200, body: { message: "Hello, world!" } },
    }],
  };
}

export function personalizedGreet(state, intent) {
  const name = intent.payload.body?.name || "stranger";
  return {
    delta: {},
    effects: [{
      kind: "HTTP_RESPONSE",
      target: "caller",
      payload: { status: 200, body: { message: `Hello, ${name}!` } },
    }],
  };
}
```

---

### EFFECT — (declared inline by Actions above)

Restated for clarity — the two primary Effect kinds in this server:

```js
// HTTP_RESPONSE — send a response to the caller
{
  kind: "HTTP_RESPONSE",
  target: "caller",
  payload: { status: 200, body: { message: "Hello!" } },
}

// LOG — emit an audit log entry
{
  kind: "LOG",
  target: "audit",
  payload: { event: "service.registered", serviceId: "service:greeter" },
}
```

---

### IMPACT — `impacts/serverImpact.js`

Executes Effects. The HTTP_RESPONSE handler writes to the actual `res` object. This is the *only* place IO occurs.

```js
// impacts/serverImpact.js
const handlers = {
  HTTP_RESPONSE: async (effect, ctx) => {
    const { res } = ctx;
    res.writeHead(effect.payload.status, { "Content-Type": "application/json" });
    res.end(JSON.stringify(effect.payload.body));
    return { ok: true };
  },

  LOG: async (effect) => {
    // In production, this writes to a log service
    console.log(`[AUDIT] ${JSON.stringify(effect.payload)}`);
    return { ok: true };
  },
};

export async function execute(effects, ctx) {
  const outcomes = [];
  for (const effect of effects) {
    const handler = handlers[effect.kind];
    if (!handler) {
      console.error(`No impact handler for: ${effect.kind}`);
      outcomes.push({ ok: false, error: `unknown effect kind: ${effect.kind}` });
      continue;
    }
    outcomes.push(await handler(effect, ctx));
  }
  return outcomes;
}
```

---

### WRAPPER — `wrappers/httpWrapper.js`

The HTTP server itself — a structural boundary that listens for connections and exposes events towards Adapters. It does not parse, route, or respond.

```js
// wrappers/httpWrapper.js
import { createServer } from "node:http";

export function createHttpWrapper(port) {
  const server = createServer();
  let requestHandler = null;

  // Event slot — the Adapter binds here
  function onRequest(handler) {
    requestHandler = handler;
  }

  server.on("request", (req, res) => {
    if (requestHandler) {
      requestHandler(req, res);
    } else {
      res.writeHead(503);
      res.end("Server not ready");
    }
  });

  function start() {
    return new Promise((resolve) => {
      server.listen(port, () => {
        console.log(`Wrapper listening on :${port}`);
        resolve();
      });
    });
  }

  function stop() {
    return new Promise((resolve) => server.close(resolve));
  }

  return { onRequest, start, stop };
}
```

---

### ADAPTER — `adapters/httpAdapter.js`

Converts raw `(req, res)` into Intents. Reads headers, parses body, extracts raw auth material. No routing, no identity resolution, no business logic.

```js
// adapters/httpAdapter.js
import { requestIntent }
  from "../intents/serverIntents.js";

export function bindHttpAdapter(wrapper, dispatch) {
  wrapper.onRequest(async (req, res) => {
    // Parse body for non-GET requests
    const body = await readBody(req);

    // Extract raw auth material — Adapter does NOT mint Tokens
    const rawAuth = {
      authHeader: req.headers["authorization"] || "",
      apiKey: req.headers["x-api-key"] || "",
    };

    // Normalize into Intent — the Adapter doesn't decide what to do with it
    const intent = requestIntent(
      req.method,
      req.url,
      body,
      rawAuth,
      "httpWrapper"
    );

    // Dispatch to Manager, passing res as context for Impact
    await dispatch(intent, { res });
  });
}

function readBody(req) {
  return new Promise((resolve) => {
    if (req.method === "GET" || req.method === "DELETE") return resolve(null);
    const chunks = [];
    req.on("data", (c) => chunks.push(c));
    req.on("end", () => {
      try { resolve(JSON.parse(Buffer.concat(chunks).toString())); }
      catch { resolve(null); }
    });
  });
}
```

---

### MANAGER — `manager/serverManager.js`

Orchestrates routing, dynamic service registration, and the request lifecycle.

```js
// manager/serverManager.js
import { managementFacet, getServiceFacet, registerServiceFacet }
  from "../facets/serviceFacets.js";
import { createServerInstance, applyDelta } from "../instances/serverInstance.js";
import { execute as runImpact } from "../impacts/serverImpact.js";
import { bindHttpAdapter } from "../adapters/httpAdapter.js";
import { issueRequestToken } from "../tokens/requestToken.js";

export function createServerManager(wrapper) {
  let instance = createServerInstance();

  // --- Route resolution ---
  function resolveRoute(method, path) {
    return instance.state.routeTable.find(
      (r) => r.method === method && matchPath(r.path, path)
    );
  }

  function matchPath(pattern, actual) {
    // Simplified — production would handle params like /users/:id
    return pattern === actual;
  }

  // --- Dispatch ---
  async function dispatch(intent, ctx) {
    // Manager mints the Token from raw auth material
    const token = issueRequestToken(intent.rawAuth);
    ctx.token = token;

    let facet, capability;

    if (intent.kind.startsWith("management.")) {
      // Management Intents route to the management Facet
      facet = managementFacet;
      capability = intent.capability;
    } else if (intent.kind === "http.request") {
      // Resolve route from the live routing table
      const route = resolveRoute(intent.payload.method, intent.payload.path);

      if (!route) {
        return await runImpact([{
          kind: "HTTP_RESPONSE",
          target: "caller",
          payload: { status: 404, body: { error: "not found" } },
        }], ctx);
      }

      facet = getServiceFacet(route.serviceId);
      capability = route.capability;

      if (!facet) {
        return await runImpact([{
          kind: "HTTP_RESPONSE",
          target: "caller",
          payload: { status: 502, body: { error: "service facet not loaded" } },
        }], ctx);
      }
    }

    const action = facet.delegates[capability];
    if (!action) {
      return await runImpact([{
        kind: "HTTP_RESPONSE",
        target: "caller",
        payload: { status: 405, body: { error: `no capability: ${capability}` } },
      }], ctx);
    }

    // Run pure Action
    const { delta, effects } = action(instance.state, intent);

    // Commit delta
    if (Object.keys(delta).length > 0) {
      instance = applyDelta(instance, delta);
    }

    // If we just registered a service, also register its Facet
    if (delta.registerService) {
      const svc = delta.registerService;
      registerServiceFacet(svc.identity.entityId, svc.facet);
    }

    // Hand effects to Impact
    await runImpact(effects, ctx);
  }

  // --- Binder ---
  function bind() {
    bindHttpAdapter(wrapper, dispatch);
  }

  // --- Dynamic registration API (for programmatic use) ---
  function registerServiceDirect(serviceConfig, facet) {
    serviceConfig.facet = facet;
    const { delta, effects } = managementFacet.delegates["service.register"](
      instance.state,
      { payload: serviceConfig }
    );
    if (Object.keys(delta).length > 0) {
      instance = applyDelta(instance, delta);
      registerServiceFacet(serviceConfig.identity.entityId, facet);
    }
    return delta;
  }

  return { bind, dispatch, registerServiceDirect };
}
```

---

### Putting It Together — `server.js`

```js
// server.js — the entry point
import { createHttpWrapper } from "./wrappers/httpWrapper.js";
import { createServerManager } from "./manager/serverManager.js";
import { createServiceIdentity } from "./identity/serviceIdentity.js";
import { greet, personalizedGreet } from "./actions/greeterActions.js";

// 1. Wrapper — structural boundary
const wrapper = createHttpWrapper(3000);

// 2. Manager — orchestrator
const manager = createServerManager(wrapper);
manager.bind();

// 3. Register a service dynamically (programmatic)
manager.registerServiceDirect(
  {
    name: "greeter",
    version: "1.0.0",
    identity: createServiceIdentity("greeter"),
    routes: [
      { method: "GET",  path: "/hello",      capability: "greet" },
      { method: "POST", path: "/hello/name",  capability: "greet.personalized" },
    ],
  },
  {
    delegates: {
      "greet":              greet,
      "greet.personalized": personalizedGreet,
    },
  }
);

// 4. Start listening
await wrapper.start();

// Server is live:
//   GET  /hello       → "Hello, world!"
//   POST /hello/name  → "Hello, Alice!"
//
// To add a new service at runtime, POST to a management endpoint
// or call manager.registerServiceDirect() from a plugin loader.
//
// No restart. No recompile. No core file changes.
// The Manager simply binds a new Identity + Facet into the live Instance.
```

---

### What to notice

1. **Dynamic extensibility is just state.** Registering a service = committing a delta to the server Instance. The same `dispatch → Action → delta → commit` flow handles user requests and service registration.
2. **No framework, no magic.** The routing table is a plain array in Instance state. Adding a route appends to it. Removing a service filters it out. Entirely transparent.
3. **The Wrapper never routes.** The `http.createServer` callback just hands `(req, res)` to the Adapter. All routing logic lives in the Manager, informed by the Instance's route table.
4. **Each service is an Identity + Facet pair.** The service's *existence* is its Identity. Its *capabilities* are its Facet. Its *runtime state* (if any) would be its Instance. The service doesn't need to know about the server, HTTP, or other services.
5. **Impact carries the response context.** The `res` object is passed through as `ctx` — never seen by Actions (pure) or Facets (data). Only Impact's `HTTP_RESPONSE` handler touches it.
6. **Testing remains trivial.** Test `registerService()` with mock state → assert delta contains the new service. Test `greet()` → assert it returns an HTTP_RESPONSE effect. No server, no sockets, no HTTP.


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
> If AXIS contributes substantial commercial value to your organization, please consider supporting its continued development through sponsorship or a paid advisory engagement. Financial support is voluntary and is not a condition of the license.
>
> For sponsorship, workshops, process design, or agent orchestration consulting, contact [consulting@mentic.com](mailto:consulting@mentic.com).
>
> ---
>
> This permits commercial reuse **without mandatory payment**, while requiring attribution under the license. [Official license summary](https://creativecommons.org/licenses/by/4.0/)
>
> For more interesting ideas visit [MENTIC Cognitive Systems](https://www.mentic.com)