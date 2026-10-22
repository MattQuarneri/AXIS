# AXIS: Agentically eXtensible Instruction Structures - Design Reference
**Author:** Matthew Quarneri (matt@mentic.com)
**Organization:** MENTIC Cognitive Systems  
**Version:** 2026.05.22   
**Copyright:** © 2026 MENTIC LLC  
**License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — see [LICENSE.md](LICENSE.md)

> Use this document when reasoning about **system architecture, component decomposition, and design decisions** under the AXIS model.
> Design bridges the full Specification and AXIS Lite: it uses the full vocabulary, but it treats Lite as the default operating profile for ordinary application work.
> For code generation, folder layout, and implementation rules, see **AXIS-Code.md**; for the complete ideal reference, see **AXIS-Specification.md**.

---

## The Grid (Quick Reference)

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

### How to read Design in the AXIS set

- Treat `AXIS-Specification.md` as the complete ideal and the full-profile contract.
- Treat `AXIS-Lite.md` as the pragmatic default profile for ordinary services and refactors.
- Use this document to decide when the ideal shape is worth the extra structure and when the lighter shape preserves the same guarantees.

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

---

## Canonical Flow

### Composition Time (Binding)

```
Wrapper.eventSlot  →  Adapter
Intent             →  Facet       (via Manager routing)
Facet              →  Action      (delegate resolution)
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
Facet.delegate (resolves to Action)
  ↓
Action(instance.state, intent) → { delta, effects[] }
  ↓                                    ↓
Manager.commit(delta)              Impact.execute(effects[])
  ↓                                    ↓
Instance(identity) updated         Side effects occur
  ↓                                    ↓
Token refreshed (if needed)        Follow-up Intents emitted
  ↓
Wrapper.render(instance)
```

---

## Composition Patterns

### Relational Composition (Bonds & Links)
* **Aggregate Invariant Enforcement**: The Committer uses registered **Bonds** to walk the tree of related entity Instances on each transaction commit. If a related entity's invariants are broken by the delta (e.g., parent total doesn't match sum of child items), the commit is rejected.
* **Declarative Graph Hydration**: The Manager uses **Links** to hydrate relationships prior to Action execution. Instead of making the Action perform asynchronous two-pass loading, the Manager pre-hydrates the aggregate tree using dynamic Links and hands the pre-hydrated state aggregate directly to the Action.
* **Bonds as DDD Aggregate Boundaries**: In Domain-Driven Design (DDD), an Aggregate Root ensures consistency of changes within its boundary. Bonds formally specify these relationships and invariants externally, keeping individual Forms clean and focused on local schema structure.

### Capability Overlays
Facets compose via layers:
- Base capabilities
- Role-based capabilities (driven by Token claims)
- Feature-flag capabilities
- Experiment / A/B capabilities

### Facet Decomposition

A Facet exists because a specific kind of viewer needs a specific capability surface of an Identity's Form. Use this decision tree:

1. **Do different viewers (roles, scopes, contexts) need different capabilities for this entity?** → Different Facets, selected by Token claims.
2. **Does the same viewer need different capabilities at different lifecycle stages?** → Different Facets, selected by Instance state or workflow phase (e.g., `draftFacet` vs. `publishedFacet`).
3. **Does the same viewer with the same role just need more operations on the same surface?** → Same Facet, add new delegate entries.
4. **Is the Manager's routing growing branchy to select the right Facet?** → You may have too few Facets. Split by the natural boundary (the Token claim or state value that drives the branch).

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

Three failure points in the canonical flow:

#### 1. Action-level failure (validation, business rule violation)

The Action is pure — it returns a delta and effects that *describe* the failure:

```
function transferFunds(state, intent) {
  if (state.balance < intent.payload.amount) {
    return {
      delta: {},
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
```

Impact retries per policy, then executes `compensatingEffect` on exhaustion, then emits a follow-up Intent describing the outcome. The follow-up re-enters the system through the Manager.

#### 3. Manager-level failure (unroutable Intent, missing Facet, expired Token)

The Manager produces Effects directly:

```
if (!facet) {
  await runImpact([{
    kind: "INTENT_UNROUTABLE",
    target: "caller",
    payload: { intent, reason: "no_matching_facet" },
  }], ctx);
  return;
}
```

**At every failure point, the system produces *data* (Effects, follow-up Intents) rather than throwing exceptions.** This makes failures loggable, replayable, testable, and composable.

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

A Manager in one context produces an Effect (e.g., `{ kind: "EMIT_EVENT", target: "order-service" }`). Impact executes it. The receiving context's Adapter normalizes it into a local Intent, and that context's Manager routes it through its own Facets and Actions.

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

In practical terms, a believable Manager boundary makes five things explicit: owned state, accepted intents, emitted effects or events, returned outcomes, and policy scope.

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

### Read Path: Graph Hydration via Links

While the two-pass pattern is ideal for executing async queries that depend on action results, many read paths simply require traversing existing relationships (e.g., fetching a Flow and its Tasks).

Using **Links** streamlines this:
1. The client requests a parent Instance (e.g., Flow).
2. The Manager checks registered **Bonds** to find associated entities.
3. The Manager resolves the **Link** (either eagerly or on demand) to populate the related child Instances.
4. The unified, pre-hydrated graph is returned or passed directly to the Action.

This eliminates the need for async two-pass flows on standard reads, keeping Actions focused entirely on state transformations without bloating them with graph traversal logic.

---

## Diagrams

### Binding (Composition Time)
```
WRAPPER → ADAPTER → MANAGER → FACET → ACTION → EFFECT → IMPACT
```

### Runtime Flow
```
Event → Adapter → Intent → Manager → Action → { Δ, Effects }
                    ↑          |          ↓            ↓
                 Token      Facet    Instance     Impact
                 (scope)   (route)  (commit Δ)   (execute)
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

---

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

### Roles, Responsibilities, and Capabilities

These three concepts are already fully expressed across the existing grid:

| Concept | AXIS component | How |
|---------|----------------|-----|
| **Role** (who) | TOKEN claims | A role is a claim carried by a Token |
| **Capability** (what) | FACET delegate keys | A capability is an entry in a Facet |
| **Responsibility** (how) | ACTION | A responsibility is a pure function |
| **Authorization** (when/where) | MANAGER routing | The Manager selects a Facet based on Token claims |

A role is not its own architectural component — it's a *value* in a Token that drives Facet selection. Adding a ROLE axis would pull apart what the Token→Facet→Action chain already expresses cleanly.

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