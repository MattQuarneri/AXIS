# Boundaries: Managers, Facets, failure and reads

> Assembled by `build.py` from AXIS-Design.md, AXIS-Lite.md, AXIS-Specification.md. To change it, edit the source document and rebuild.

Design decisions that the core rules do not settle on their own: how wide a Manager should be, when to split a Facet, how failure travels, and how reads work when Actions cannot fetch.

## Contents

- Manager, Narrowed
- When To Create A New Manager
- Manager Split Heuristics
- Interfaces Between Managers
- Managers Never Call Each Other
- Recommended Code Shape
- Facet Decomposition
- Capability Overlays
- Token-Scoped Views
- Roles, Responsibilities, and Capabilities
- Failure Patterns
- Read Path: The Two-Pass Pattern
- Read Path: Graph Hydration via Links
- Relational Composition (Bonds & Links)
- Bonds & Links in AXIS Lite
- Action Pipelines
- Effect Batching
- Event Sourcing

## Manager, Narrowed

The full AXIS documents are right that orchestration needs a home. The risk is that **Manager** becomes a renamed god object.

In AXIS Lite, a Manager is a **boundary-scoped coordinator**, not a general-purpose service class.

The term **Manager** can still work, but only if the code makes the role narrow and inspectable. If "Manager" becomes a vague bucket for orchestration, policy, domain logic, and integration details, rename or split it. In many codebases, `Coordinator`, `Workflow`, or `Runtime` is clearer for the runtime half.

### A Manager may do these things

- receive normalized Intents or commands
- select the right Action or Facet delegate
- coordinate workflow steps
- commit deltas to owned state
- enforce commit-time invariants
- issue or revoke Tokens if that boundary owns auth/session projection
- hand declared Effects to Impact

### A Manager must not do these things

- contain core business calculations that belong in Actions
- perform IO directly
- own unrelated domains in one class or module
- format transport-specific data for Wrappers
- reach into another Manager's state store
- encode permissions inline when a Facet or policy map would do

### Composer and Conductor

The Composer/Conductor distinction is useful, but by itself it is not enough.

It becomes credible only when it is enforced in code structure:

- **Composer** should be setup-only: binding wrappers, registering adapters, wiring facet registries, installing handlers.
- **Conductor** should be runtime-only: dispatch, routing, workflow progression, commit.
- If both roles grow large, split them into separate modules even if they are still presented as one conceptual Manager.

**Practical rule:** do not let "Manager" be the place where leftover logic goes. If logic can be tested without orchestration, it does not belong in the Manager.

## When To Create A New Manager

Create a new Manager when one or more of these become true:

1. The code is coordinating a different domain language or business capability.
2. The code owns a different consistency boundary or state store.
3. The workflow can evolve independently of the current one.
4. The deployment boundary or team ownership is different.
5. The existing Manager would need to directly know about another domain's invariants.
6. The dispatch path is branching across unrelated domains rather than related capabilities.

Do **not** create a new Manager just because:

1. the same entity has different roles or permissions; use Facets first.
2. the same workflow gained another step; add or split Workflow logic first.
3. the same state boundary gained more commands; add Actions first.

## Manager Split Heuristics

If a Manager shows these symptoms, split it:

- it owns more than one unrelated state store
- it imports Actions from unrelated domains
- it contains routing branches for unrelated business areas
- it needs different release cadence than part of its own logic
- it is accumulating workflow state machines that do not share commit rules
- changes to one capability routinely risk regressions in another unrelated capability

If a Manager shows these symptoms, keep it whole:

- all Actions operate on the same state boundary
- all workflows share the same invariants and commit rules
- capabilities differ mainly by role or lifecycle state
- the "split" would only replace function calls with noisy cross-boundary messages

## Interfaces Between Managers

The current AXIS guidance that Managers should not call each other directly is directionally right. The missing piece is a more concrete interface contract.

For AXIS Lite, each Manager boundary should define:

- **owned state**: which Forms, Instances, and Identities it is allowed to commit
- **accepted intents**: the commands or intent kinds it accepts
- **emitted effects/events**: the only outward requests it can make of other boundaries
- **returned outcomes**: acknowledgements, failures, and follow-up intents/events
- **policy scope**: which claims, roles, or token scopes it is allowed to interpret

If those five things are not clear, the boundary is not clear.

## Managers Never Call Each Other

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

## Recommended Code Shape

For services that need a Manager, prefer this internal split even if you keep the AXIS name:

- `manager/composer.*` for setup and registrations
- `manager/conductor.*` for dispatch and workflow progression
- `manager/commit.*` for delta application and invariant validation
- `manager/policy.*` for facet or permission selection

This keeps the architecture legible without forcing every concern into a single file.

## Facet Decomposition

A Facet exists because a specific kind of viewer needs a specific capability surface of an Identity's Form. Use this decision tree:

1. **Do different viewers (roles, scopes, contexts) need different capabilities for this entity?** → Different Facets, selected by Token claims.
2. **Does the same viewer need different capabilities at different lifecycle stages?** → Different Facets, selected by Instance state or workflow phase (e.g., `draftFacet` vs. `publishedFacet`).
3. **Does the same viewer with the same role just need more operations on the same surface?** → Same Facet, add new delegate entries.
4. **Is the Manager's routing growing branchy to select the right Facet?** → You may have too few Facets. Split by the natural boundary (the Token claim or state value that drives the branch).

## Capability Overlays
Facets compose via layers:
- Base capabilities
- Role-based capabilities (driven by Token claims)
- Feature-flag capabilities
- Experiment / A/B capabilities

## Token-Scoped Views
Different Tokens for the same Identity can yield different Facets:
- Admin Token → full capability Facet
- Read-only Token → restricted Facet
- Expired Token → re-authentication Intent

## Roles, Responsibilities, and Capabilities

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

## Failure Patterns

Every Intent expresses a desired outcome. When the outcome diverges from the desire, the divergence itself is expressible in AXIS — not as an exception, but as a structured flow through the same components.

**Principle: failures are alternate Effects, not exceptions.**

There are three failure points in the canonical flow, and each has a distinct AXIS treatment:

### 1. Action-level failure (validation, business rule violation)

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

### 2. Impact-level failure (IO error, timeout, external system down)

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

### 3. Manager-level failure (unroutable Intent, missing Facet, expired Token)

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

### Designing for failure in AXIS

| Concern | Where it lives |
|---------|----------------|
| "Can this operation succeed?" | **Action** — validates and returns a rejection Effect if not |
| "What if IO fails?" | **Effect** — declares retryPolicy + compensatingEffect |
| "What if IO fails after retries?" | **Impact** — executes compensation, emits follow-up Intent |
| "What do we tell the user/caller?" | **Facet** — an error-handling Facet maps failure Intents to notification Actions |
| "What if the Intent can't be routed?" | **Manager** — produces an INTENT_UNROUTABLE Effect |
| "What's the permanent record?" | **Intent stream** — all Intents (successful and failed) are logged |

## Read Path: The Two-Pass Pattern

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

## Read Path: Graph Hydration via Links

While the two-pass pattern is ideal for executing async queries that depend on action results, many read paths simply require traversing existing relationships (e.g., fetching a Flow and its Tasks).

Using **Links** streamlines this:
1. The client requests a parent Instance (e.g., Flow).
2. The Manager checks registered **Bonds** to find associated entities.
3. The Manager resolves the **Link** (either eagerly or on demand) to populate the related child Instances.
4. The unified, pre-hydrated graph is returned or passed directly to the Action.

This eliminates the need for async two-pass flows on standard reads, keeping Actions focused entirely on state transformations without bloating them with graph traversal logic.

## Relational Composition (Bonds & Links)
* **Aggregate Invariant Enforcement**: The Committer uses registered **Bonds** to walk the tree of related entity Instances on each transaction commit. If a related entity's invariants are broken by the delta (e.g., parent total doesn't match sum of child items), the commit is rejected.
* **Declarative Graph Hydration**: The Manager uses **Links** to hydrate relationships prior to Action execution. Instead of making the Action perform asynchronous two-pass loading, the Manager pre-hydrates the aggregate tree using dynamic Links and hands the pre-hydrated state aggregate directly to the Action.
* **Bonds as DDD Aggregate Boundaries**: In Domain-Driven Design (DDD), an Aggregate Root ensures consistency of changes within its boundary. Bonds formally specify these relationships and invariants externally, keeping individual Forms clean and focused on local schema structure.

## Bonds & Links in AXIS Lite

Bonds and Links prevent relationship logic from bloating Forms (schemas) and Actions (logic).
- **Use a Bond** when one entity owns another (multiplicity/cardinality) or when you must enforce consistency invariants across multiple entities during a commit.
- **Use a Link** to pre-hydrate entity references prior to dispatching to an Action. Instead of making an Action perform an async two-pass read to load related state, let the Manager resolve a Link at composition/request boundaries.

## Action Pipelines
Pure action chains:
```
validate → compute → transform → declare effects
```

## Effect Batching
Effects declared by multiple Actions within a single workflow can be:
- batched for efficiency
- ordered by dependency
- rolled back atomically via compensating Effects

## Event Sourcing
Store Intents or committed deltas to enable:
- replay
- audit
- undo/redo
- temporal queries
