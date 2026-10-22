# AXIS: Agentically eXtensible Instruction Structures - Code Reference
**Author:** Matthew Quarneri (matt@mentic.com)
**Organization:** MENTIC Cognitive Systems  
**Version:** 2026.05.22 
**Copyright:** © 2026 MENTIC LLC  
**License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — see [LICENSE.md](LICENSE.md)

> Use this document when **generating, reviewing, or refactoring code** under the AXIS model.
> This is the implementation guide: pragmatic by default, but still governed by the full AXIS rules.
> Start with **AXIS-Lite.md** for most application work, use **AXIS-Design.md** to decide when more structure is justified, and use the **AXIS-Specification.md** when the feature truly needs the full topology.

This guide uses the full AXIS names as canonical labels, but it leans practical: add only the components the problem actually needs, and collapse files or modules only when the hard rules stay visible in code.

---

## The Grid (Quick Reference)

| Axis | Essence | Expression |
|------|---------|------------|
| Being | FORM | INSTANCE |
| Identity | IDENTITY | TOKEN |
| Meaning | FACET | INTENT |
| Relating (Having) | BOND | LINK |
| Doing | ACTION | MANAGER |
| Changing | EFFECT | IMPACT |
| Bridging | WRAPPER | ADAPTER |

---

## Non-Negotiable Contracts

1. **Adapters always produce normalized Intents or equivalent command objects** — never raw mutations or direct Action calls
2. **Adapters normalize only** — they extract raw auth material and include it in the Intent or equivalent command object; they never mint Tokens, resolve identity, or make business decisions
3. **Actions always return `{ delta, effects[] }`** — never perform IO or mutate state
4. **Effects are data** — declared by Actions, never self-executing
5. **Only Impact executes Effects** — the sole site of IO side effects
6. **Only the state-owning coordination boundary commits state** — in full AXIS this is the Manager, producing new Instances and issuing Tokens when those concepts exist
7. **That boundary validates invariants on commit** — rejecting deltas that would violate Form and Bond invariants
8. **Facets are capability maps** — not type annotations or UI components
9. **Forms are generative** — they define shape, not hold values
10. **Identity is immutable** — only Tokens project identity into temporal contexts
11. **Bonds structure relationship topology** — they do not hold references or resolve graphs
12. **Links traverse and hydrate relationships at runtime** — they are resolved by the Manager or link-services, never within pure Actions

---

## Folder Structure

Reference layout for the fuller AXIS profile. In smaller services or lite implementations, collapse directories when the same state ownership, IO boundaries, and policy seams remain clear.

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

## Type Contracts (Language-Agnostic)

### Form
```
{
    shape,
    defaults,
    invariants[],
    transitions?      // optional: named delta shapes for strict state machines
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

Canonical full-profile token shape. Practical implementations often narrow this into session tokens, revision references, workflow handles, or other scoped identity projections. Use only the subtypes your boundary actually needs.

### Bond
```js
{
    ownerRef,         // Form or Identity of the owner
    targetRef,        // Form or Identity of the target
    cardinality,      // 'one-to-one' | 'one-to-many' | 'many-to-many'
    invariants[]      // relational constraint validation functions
}
```

### Link
```js
{
    bondRef,          // stable reference to the Bond definition
    sourceRef,        // Identity being traversed from
    resolvedRefs,     // resolved target Identities or pre-hydrated target Instances
    scope             // query boundary metadata
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
    rawAuth?,         // raw auth material extracted by Adapter
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

### Manager

The Manager is a boundary-scoped coordinator, not a catch-all service class. In full AXIS it owns one consistency boundary and decomposes into two conceptual roles:

- **Composer** (Binder): Wires structure at setup time — Adapters to Wrappers, Facets to capabilities. Runs when composition changes.
- **Conductor** (Router + Workflow + Committer): Drives execution at runtime — routes Intents, coordinates workflows, commits deltas with invariant validation.

```
// Composer (structure)
bind(wrapper)
registerFacet(facet)
registerBond(bond)

// Conductor (performance)
dispatch(intent)
commit(delta) → Instance   // validates Form and Bond invariants; rejects on violation
issueToken(identity, scope, rawAuth) → Token
revokeToken(token)
resolveLink(link) → Link   // traverses relationship at runtime
```

### Impact
```
execute(effects[]) → outcomes[]
compensate(effects[])
```

---

## "Where Does This Code Go?"

| If it... | It belongs in... |
|----------|------------------|
| Defines valid state shape | **Form** |
| Holds live mutable state | **Instance** |
| Names/addresses an entity | **Identity** |
| Projects identity into a session/scope | **Token** |
| Mints tokens from raw auth material | **Manager** (or delegate) |
| Maps capabilities to actions | **Facet** |
| Describes what someone meant to do | **Intent** |
| Transforms state (pure logic) | **Action** |
| Orchestrates routing and workflow | **Manager** (Conductor) |
| Validates aggregate invariants on commit | **Manager** (Conductor using Bonds) |
| Defines static relationship/ownership boundaries | **Bond** |
| Resolves runtime relationship/reference queries | **Link** |
| Wires Adapters to Wrappers | **Manager** (Composer) |
| Registers Facets at setup | **Manager** (Composer) |
| Declares a side effect | **Effect** |
| Executes a side effect | **Impact** |
| Hosts a UI surface or endpoint | **Wrapper** |
| Converts raw events to Intents | **Adapter** |
| Extracts raw auth material | **Adapter** (passes through in Intent) |

---

## Feature Recipe: Adding a New Capability

When a feature truly benefits from the fuller AXIS chain, create files in this order. Skip the pieces that AXIS Lite or Partial AXIS do not require. Each step produces one testable artifact.

### Step 1 — Form (if new entity or new shape)

Define the shape, defaults, and invariants. Skip if the feature operates on an existing Form.

### Step 1b — Bond (if new relationship)

Define ownership, target, cardinality, and relational invariants.

```js
// bonds/invoiceCustomer.js
export const InvoiceCustomerBond = {
  ownerRef: "InvoiceForm",
  targetRef: "CustomerForm",
  cardinality: "one-to-one",
  invariants: [
    (invoice, customer) => !invoice.isTaxable || customer.taxId || "Taxable invoice requires customer tax ID",
  ],
};
```

```js
// forms/invoice.js
export const InvoiceForm = {
  shape: {
    lineItems: { type: "array", required: true },
    total:     { type: "number", required: true },
    status:    { type: "string", enum: ["draft", "sent", "paid"], required: true },
  },
  defaults: { lineItems: [], total: 0, status: "draft" },
  invariants: [
    (s) => s.total >= 0 || "total must not be negative",
    (s) => s.lineItems.length > 0 || "invoice must have at least one line item",
  ],
};
```

### Step 2 — Identity (if new entity)

Define stable addressing. Skip if the feature operates on an existing Identity.

```js
// identity/invoiceIdentity.js
export function createInvoiceIdentity(invoiceId) {
  return Object.freeze({
    entityId: `invoice:${invoiceId}`,
    formRef: "InvoiceForm",
    versioningPolicy: "counter",
  });
}
```

### Step 3 — Intent

Define the semantic description of the new capability.

```js
// intents/invoiceIntents.js
export function sendInvoiceIntent(identityRef, payload, wrapperCtx) {
  return Object.freeze({
    kind: "invoice.send",
    capability: "send",
    identityRef,
    payload,
    wrapperCtx,
    meta: { timestamp: Date.now() },
  });
}
```

### Step 4 — Action

Write the pure function. This is where you spend most of your design effort.

```js
// actions/invoiceActions.js
export function sendInvoice(state, intent) {
  if (state.status !== "draft") {
    return {
      delta: {},
      effects: [{
        kind: "INTENT_REJECTED",
        target: "caller",
        payload: { reason: "invoice_already_sent" },
      }],
    };
  }

  return {
    delta: { status: "sent" },
    effects: [{
      kind: "EMAIL_SEND",
      target: intent.payload.recipientEmail,
      payload: { invoiceId: intent.identityRef, total: state.total },
      retryPolicy: { maxRetries: 3, backoff: "exponential" },
    }],
  };
}
```

### Step 5 — Effect (declared by the Action above)

No separate file needed — Effects are the data values returned by Actions. Document the new Effect kind if it requires a new Impact handler.

### Step 6 — Impact handler (if new Effect kind)

Register a handler for the new Effect kind.

```js
// impacts/emailImpact.js
export const emailHandlers = {
  EMAIL_SEND: async (effect) => {
    const res = await fetch("/api/email", {
      method: "POST",
      body: JSON.stringify({ to: effect.target, ...effect.payload }),
    });
    if (!res.ok) throw new Error(`Email failed: ${res.status}`);
    return { ok: true };
  },
};
```

### Step 7 — Facet (add delegate)

Register the new capability in the appropriate Facet.

```js
// facets/invoiceFacets.js
import { sendInvoice } from "../actions/invoiceActions.js";

export const draftFacet = {
  delegates: {
    send: sendInvoice,
    // ... other draft-stage capabilities
  },
};
```

### Step 8 — Adapter (if new event source)

Wire the new Intent to a Wrapper event. Skip if reusing an existing Adapter.

### Step 8b — Link (if traversing relationships runtime)

Implement dynamic traversal and graph hydration.

```js
// links/invoiceCustomerLink.js
import { InvoiceCustomerBond } from "../bonds/invoiceCustomer.js";

export function createInvoiceCustomerLink(invoiceIdentity, customerIdentity = null) {
  return {
    bondRef: "InvoiceCustomerBond",
    sourceRef: invoiceIdentity.entityId,
    resolvedRefs: customerIdentity ? [customerIdentity.entityId] : [],
    scope: "request",
  };
}

export async function resolveInvoiceCustomerLink(link, loadInstanceFn) {
  // Runtime resolver fetches related aggregate entity
  const customerInstance = await loadInstanceFn(link.sourceRef);
  return {
    ...link,
    resolvedRefs: [customerInstance],
  };
}
```

### Step 9 — Manager (register the new Facet + Impact handler)

Wire the new capability into the Manager's Composer (bind-time) and ensure the Conductor can route to it.

### Step 10 — Tests

Write one test per layer. See the **Test File Examples** section below.

---

## Partial AXIS: When You Don't Need All 14

Not every feature requires every component. Use the smallest shape that preserves the rules:

| Scenario | Start with | Add when needed |
|----------|------------|-----------------|
| **Pure computation** | Action | Add Form when shape, defaults, or invariants need to be explicit |
| **Read-only display** | Wrapper | Add Form, Instance, or Identity when rendering from owned or versioned state |
| **Simple stateless endpoint** | Wrapper, Adapter, Action, Effect/Impact if IO is needed | Add Intent or Facet when semantic normalization or capability selection needs to be explicit |
| **CRUD service with owned state** | Form, Instance, Action, Manager, Effect/Impact | Add Identity, Token, or Facet when stable addressing, scope, or permissions matter |
| **Role-aware or lifecycle-aware domain** | Add Facets | Split Managers only when state boundaries or workflows diverge |
| **New event source** (e.g., WebSocket alongside HTTP) | Wrapper, Adapter | Reuse existing Actions, Effects, Facets, and Managers where possible |
| **Multi-step async workflow, retries, compensation, replay** | Full AXIS or close to it | Keep the full chain visible |

**The rule:** start with the minimum set. Add components when you feel the absence — not before.

**When you feel the absence:**
- Getting `undefined` when you try to address something? You need an **Identity**.
- Passing raw state around with no schema? You need a **Form**.
- Checking permissions inline in an Action? You need a **Facet** split and **Token** claims.
- Doing `fetch()` inside an Action? You need to declare an **Effect** and handle it in **Impact**.
- Hardcoding initial data? You may need the **two-pass read path** (see below).

---

## Facet Decomposition: When to Split

A Facet exists because a specific kind of viewer needs a specific capability surface of an Identity's Form. Use this decision tree:

1. **Do different viewers (roles, scopes, contexts) need different capabilities for this entity?** → Different Facets, selected by Token claims.
2. **Does the same viewer need different capabilities at different lifecycle stages?** → Different Facets, selected by Instance state or workflow phase (e.g., `draftFacet` vs. `publishedFacet`).
3. **Does the same viewer with the same role just need more operations on the same surface?** → Same Facet, add new delegate entries.
4. **Is the Manager's routing growing branchy to select the right Facet?** → You may have too few Facets. Split by the natural boundary (the Token claim or state value that drives the branch).

---

## The Read Path: Two-Pass Pattern

Actions are pure — they can't fetch data. Reads use two passes through the pipeline: **"ask to know, tell to show."**

```
Pass 1:  Event → Adapter → Intent → Action → { delta: {}, effects: [FETCH] }
                                                              ↓
                                                          Impact (IO)
                                                              ↓
Pass 2:  Follow-up Intent → Action → { delta: fetchedData, effects: [] }
                                              ↓
                                        Instance updated → Wrapper renders
```

**Composition-time hydration:** For initial data loading, the Manager can hydrate the Instance directly during `bind()` — before the event pipeline is live. This is composition-time setup, not a runtime violation.

---

## Rules for Machine Agents

### Constraints
1. Never mutate state outside Instance
2. Never perform IO outside Impact
3. Identity is immutable — only Tokens project it into runtime contexts
4. Effects are data — never self-executing
5. Prefer the explicit chain when the feature crosses normalization, policy, owned state, or IO boundaries: Adapter → Intent → Manager → Facet → Action → Effect → Impact. Collapse pieces only when the same guarantees remain obvious in code.
6. Prefer **new capabilities** (new Facet entries) over conditionals
7. Forms define shape — never embed behavior in a Form
8. Adapters normalize only — they extract raw auth and include it in the Intent or equivalent command object; they never mint Tokens or resolve identity
9. Manager validates Form invariants on commit — rejecting invalid deltas
10. Manager Composer grows complex? → add Facets, not wiring logic
11. Manager Conductor grows complex? → add Workflow sub-component, not branches
12. Conductor coordinates multiple domains? → separate Managers via Effects
13. Actions signal workflow operations (cancel, restore) through Effects — never through magic delta keys

### Test Generation
- **Actions**: unit test with snapshot state + intent → assert delta + effects
- **Adapters**: raw event → assert correct Intent produced (including rawAuth extraction)
- **Manager commit**: delta + Form invariants → assert commit accepted or rejected
- **Manager routing**: intent + token → assert correct Facet selected
- **Effects**: assert Action declares expected Effect data
- **Impact**: integration test with mocked targets → assert side effects executed
- **Tokens**: assert scoping, expiry, and claim propagation

---

## AXIS Shape Analysis For Existing Repos

AXIS can also be used as a metadata lens for existing codebases that were not written with AXIS names.

The goal of an AXIS shape pass is not to rewrite the repo. The goal is to map native structures into AXIS roles so agents can understand where state, intent, pure logic, side effects, IO, boundaries, and reusable capability closures already live.

Run this after a CodeMaps digest and navigation pass whenever the task involves repo understanding, refactoring, code generation, reuse, or cross-repo recomposition.

Recommended pipeline, in two stages:

```txt
Stage 1, map and understand (the repo in its own terms):
  repo digest -> CodeMaps navigation maps
              -> component metadata, recomposer candidates    (optional)

Stage 2, clarify and refactor (the same repo, read by role):
  AXIS role map -> generation units for one change -> carry it out, update the map
                -> AXIS functional forms, for reuse            (optional)
```

### AXIS role map

An AXIS role map records the closest AXIS role for native code components:

```json
{
  "nativeName": "OrderController.create",
  "paths": ["src/orders/controller.ts"],
  "primaryAxisRole": "Adapter",
  "secondaryAxisRoles": ["Wrapper", "Manager"],
  "confidence": "medium",
  "evidence": [
    "reads HTTP request body",
    "calls OrderService.create",
    "returns framework response"
  ],
  "boundaryNotes": [
    "normalizes input and starts workflow in the same function"
  ],
  "recompositionNotes": [
    "extract request-to-intent normalization",
    "keep route binding as Wrapper"
  ]
}
```

This is intentionally descriptive. A mixed component should be marked as mixed rather than forced into one clean AXIS category.

Role descriptors are stored as the `roles` array of `codemaps/axis-map.json`, together with the repo's boundaries, its main flows, the boundary findings, a placement table and house rules. `codemaps/AXIS-MAP.md` is rendered from that file.

### AXIS functional forms

An AXIS functional form describes a reusable capability by functional closure rather than by file adjacency.

For each harvest target, record:

- useful capability nucleus
- required Forms, Intents, Actions, Effects, Impacts, and state boundaries
- host assumptions
- dependency seams
- what is portable as-is
- what should be adapted
- what should be recomposited
- tests or golden behaviors to carry

This is the bridge between code understanding and remix/reuse. It lets an agent ask, "What must survive the transplant?" before copying or regenerating code.

### Generation units

For a concrete change, turn the AXIS role map into small generation contracts:

```txt
axis.intent   -> define normalized command/event shape
axis.form     -> update state shape or invariant
axis.action   -> implement pure state transition
axis.effect   -> declare side-effect data
axis.impact   -> execute IO behind the existing host boundary
axis.adapter  -> normalize raw edge input
axis.test     -> prove the behavior and boundary rules
```

Small local models can often handle pure Actions, object literals, simple Adapters, and tests. Stronger agents or human review should handle Managers, security-sensitive policy, migrations, cross-boundary workflow, and infrastructure integration.

The prompts and the driver for this workflow live under `CodeMaps/`, and `CodeMaps/ReadMe.md` describes the two stages end to end:

- `axis-shape.prompt.md`: build the role map
- `axis-generation-units.prompt.md`: plan one change
- `axis-refactor.prompt.md`: carry it out
- `axis-recomposer.prompt.md`: functional forms, for reuse
- `codemaps.sh`: runs the stages

The mapping procedure, the map format and the `axis.py` tool are part of the AXIS skill (`skill/axis/`).

---

## Worked Example: User Profile Editor (Vanilla JS SPA)

This traces editing a user profile through 12 of the 14 AXIS components. The feature has no relationships between entities, so it needs no Bond or Link. Every file maps to exactly one component. For a server-side AXIS example (extensible web server with dynamic service registration), see the AXIS specification document.

> **Shadow DOM is a Wrapper** (structural encapsulation), not a Facet (business capability surface).

### FORM — `forms/userProfile.js`

```js
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

### IDENTITY — `identity/userIdentity.js`

```js
export function createUserIdentity(userId) {
  return Object.freeze({
    entityId: userId,
    formRef: "UserProfileForm",
    versioningPolicy: "hash",
  });
}
```

### INSTANCE — `instances/profileInstance.js`

```js
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

### TOKEN — `tokens/sessionToken.js`

```js
export function issueSessionToken(identity, claims = {}) {
  return {
    identityRef: identity.entityId,
    scope: "session",
    expiry: Date.now() + 30 * 60 * 1000,
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

### FACET — `facets/profileFacets.js`

```js
import { validateAndSave, cancelEdit, loadProfile, applyFetchedProfile }
  from "../actions/profileActions.js";

export const editableFacet = {
  delegates: {
    save:       validateAndSave,
    cancel:     cancelEdit,
    load:       loadProfile,
    applyFetch: applyFetchedProfile,
  },
};

export const readOnlyFacet = {
  delegates: {
    load:       loadProfile,
    applyFetch: applyFetchedProfile,
  },
};
```

### INTENT — `intents/profileIntents.js`

```js
export function saveProfileIntent(identityRef, payload, wrapperCtx) {
  return Object.freeze({
    kind: "profile.save",
    capability: "save",
    identityRef,
    payload,
    wrapperCtx,
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

export function loadProfileIntent(identityRef, wrapperCtx) {
  return Object.freeze({
    kind: "profile.load",
    capability: "load",
    identityRef,
    payload: null,
    wrapperCtx,
    meta: { timestamp: Date.now() },
  });
}
```

### ACTION — `actions/profileActions.js`

```js
import { UserProfileForm } from "../forms/userProfile.js";

export function validateAndSave(state, intent) {
  const next = { ...state, ...intent.payload };
  const violations = UserProfileForm.invariants
    .map((inv) => inv(next))
    .filter((r) => r !== true);

  if (violations.length > 0) {
    // Action-level validation: return specific errors for the UI
    return {
      delta: { _validationErrors: violations },
      effects: [],
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

export function loadProfile(state, intent) {
  // Pass 1 of two-pass read: declare the fetch, can't execute it
  return {
    delta: { _loading: true },
    effects: [{
      kind: "FETCH_PROFILE",
      target: `/api/users/${intent.identityRef}/profile`,
      payload: null,
    }],
  };
}

export function applyFetchedProfile(state, intent) {
  // Pass 2 of two-pass read: apply fetched data as delta
  return {
    delta: { ...intent.payload.data, _loading: false },
    effects: [],
  };
}
```

### EFFECT — (declared inline by Actions)

```js
// Effects are pure data returned by Actions. Two categories:

// IO Effects — executed by Impact
{ kind: "HTTP_PUT", target: "/api/users/u-1234/profile", payload: { ... }, retryPolicy: { ... } }
{ kind: "FETCH_PROFILE", target: "/api/users/u-1234/profile", payload: null }

// Workflow Effects — handled by Manager's Conductor before reaching Impact
{ kind: "RESTORE_COMMITTED", target: "u-1234" }
```

### IMPACT — `impacts/httpImpact.js`

```js
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

  FETCH_PROFILE: async (effect) => {
    const res = await fetch(effect.target);
    if (!res.ok) throw new Error(`Fetch failed: ${res.status}`);
    const data = await res.json();
    return {
      ok: true,
      followUpIntent: {
        kind: "profile.fetched",
        capability: "applyFetch",
        identityRef: effect.target.split("/")[3],
        payload: { data },
      },
    };
  },

  ROLLBACK_INSTANCE: async (effect) => {
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
      if (effect.compensatingEffect) {
        await execute([effect.compensatingEffect]);
      }
      outcomes.push({ ok: false, error: err.message });
    }
  }
  return outcomes;
}
```

### WRAPPER — `wrappers/profileEditor.js`

```js
class ProfileEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
  }

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

  get eventSlots() {
    return {
      submit: () => this.shadowRoot.querySelector("#profile-form"),
      cancel: () => this.shadowRoot.querySelector("#cancel"),
    };
  }

  readInputs() {
    const form = this.shadowRoot.querySelector("#profile-form");
    return Object.fromEntries(new FormData(form));
  }
}

customElements.define("profile-editor", ProfileEditor);
export { ProfileEditor };
```

### ADAPTER — `adapters/profileAdapter.js`

```js
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

### MANAGER — `manager/profileManager.js`

This Manager demonstrates all four responsibilities: Binder, Router, Workflow (committed state tracking), and Committer (invariant validation).

```js
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
        // Safety net: reject delta that violates invariants
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

### Entry Point — `app.js`

```js
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
```

**Key observations:**
- In this worked example, every file maps to exactly one AXIS component. That layout makes the architecture explicit, but it is a full-profile example rather than a mandatory topology for every codebase.
- **Composition-time bootstrapping:** The entry point creates the Token and Instance directly. At runtime, Tokens are minted by the Manager and data is loaded via the two-pass read path. Both are documented AXIS patterns.
- **Invariant validation at commit:** The Manager's `commit()` validates Form invariants as a safety net — even though `validateAndSave` already validates. The safety net catches bugs in Actions that forget.
- **Cancel without magic deltas:** `cancelEdit` returns `{ delta: {}, effects: [RESTORE_COMMITTED] }`. The Manager's Workflow handles restoration. No magic keys corrupt Instance state.
- **Committed state tracking:** The Manager maintains `committedInstance` vs. `currentInstance`. On successful save IO, committed promotes. On cancel, working restores to committed.
- Testing is trivial per layer: call `validateAndSave()` with test data → assert delta and effects. No mocking fetch, no rendering DOM.

---

## Test File Examples

### Testing an Action

```js
// tests/actions/profileActions.test.js
import { validateAndSave, cancelEdit } from "../../actions/profileActions.js";

describe("validateAndSave", () => {
  const validState = {
    displayName: "Alice",
    email: "alice@example.com",
    bio: "",
    avatarUrl: null,
  };

  test("returns delta and HTTP_PUT effect for valid input", () => {
    const intent = {
      identityRef: "u-1234",
      payload: { displayName: "Bob", email: "bob@example.com" },
    };

    const { delta, effects } = validateAndSave(validState, intent);

    expect(delta.displayName).toBe("Bob");
    expect(delta.email).toBe("bob@example.com");
    expect(delta._validationErrors).toEqual([]);
    expect(effects).toHaveLength(1);
    expect(effects[0].kind).toBe("HTTP_PUT");
    expect(effects[0].target).toBe("/api/users/u-1234/profile");
    expect(effects[0].retryPolicy).toBeDefined();
    expect(effects[0].compensatingEffect).toBeDefined();
  });

  test("returns validation errors for empty displayName", () => {
    const intent = {
      identityRef: "u-1234",
      payload: { displayName: "", email: "bob@example.com" },
    };

    const { delta, effects } = validateAndSave(validState, intent);

    expect(delta._validationErrors).toContain("displayName must not be empty");
    expect(effects).toHaveLength(0);
  });

  test("is pure — does not modify input state", () => {
    const state = { ...validState };
    const frozen = JSON.stringify(state);
    const intent = { identityRef: "u-1234", payload: { displayName: "Bob" } };

    validateAndSave(state, intent);

    expect(JSON.stringify(state)).toBe(frozen);
  });
});

describe("cancelEdit", () => {
  test("returns empty delta and RESTORE_COMMITTED effect", () => {
    const intent = { identityRef: "u-1234" };
    const { delta, effects } = cancelEdit({}, intent);

    expect(Object.keys(delta)).toHaveLength(0);
    expect(effects).toHaveLength(1);
    expect(effects[0].kind).toBe("RESTORE_COMMITTED");
    expect(effects[0].target).toBe("u-1234");
  });
});
```

### Testing an Adapter

```js
// tests/adapters/profileAdapter.test.js
import { bindProfileAdapter } from "../../adapters/profileAdapter.js";

describe("profileAdapter", () => {
  test("dispatches saveProfileIntent on form submit", () => {
    const dispatched = [];
    const mockWrapper = {
      eventSlots: {
        submit: () => {
          const el = document.createElement("form");
          el.innerHTML = `<input name="displayName" value="Alice">`;
          return el;
        },
        cancel: () => document.createElement("button"),
      },
      readInputs: () => ({ displayName: "Alice" }),
    };

    bindProfileAdapter(mockWrapper, "u-1234", (intent) => dispatched.push(intent));

    const form = mockWrapper.eventSlots.submit();
    form.dispatchEvent(new Event("submit"));

    expect(dispatched).toHaveLength(1);
    expect(dispatched[0].kind).toBe("profile.save");
    expect(dispatched[0].capability).toBe("save");
    expect(dispatched[0].identityRef).toBe("u-1234");
    expect(dispatched[0].payload.displayName).toBe("Alice");
  });
});
```

### Testing Manager Commit Validation

```js
// tests/manager/commitValidation.test.js
import { UserProfileForm } from "../../forms/userProfile.js";
import { applyDelta, createProfileInstance } from "../../instances/profileInstance.js";
import { createUserIdentity } from "../../identity/userIdentity.js";

// Extract the commit logic for unit testing
function commit(instance, delta, form) {
  const proposed = { ...instance.state, ...delta };
  const violations = form.invariants
    .map((inv) => inv(proposed))
    .filter((r) => r !== true);
  if (violations.length > 0) return { ok: false, violations };
  return { ok: true, instance: applyDelta(instance, delta) };
}

describe("Manager commit validation", () => {
  const identity = createUserIdentity("u-1234");
  const instance = createProfileInstance(identity, {
    displayName: "Alice",
    email: "alice@example.com",
    bio: "",
    avatarUrl: null,
  });

  test("accepts valid delta", () => {
    const result = commit(instance, { bio: "Engineer" }, UserProfileForm);
    expect(result.ok).toBe(true);
    expect(result.instance.state.bio).toBe("Engineer");
  });

  test("rejects delta that violates invariants", () => {
    const result = commit(instance, { displayName: "" }, UserProfileForm);
    expect(result.ok).toBe(false);
    expect(result.violations).toContain("displayName must not be empty");
  });

  test("rejects delta with invalid email", () => {
    const result = commit(instance, { email: "not-an-email" }, UserProfileForm);
    expect(result.ok).toBe(false);
    expect(result.violations).toContain("invalid email");
  });
});
```

### Testing Impact with Mocked Targets

```js
// tests/impacts/httpImpact.test.js
import { execute } from "../../impacts/httpImpact.js";

describe("Impact execution", () => {
  const originalFetch = globalThis.fetch;

  afterEach(() => {
    globalThis.fetch = originalFetch;
  });

  test("HTTP_PUT calls fetch and returns ok on success", async () => {
    globalThis.fetch = async () => ({ ok: true, status: 200 });

    const outcomes = await execute([{
      kind: "HTTP_PUT",
      target: "/api/users/u-1234/profile",
      payload: { displayName: "Bob" },
    }]);

    expect(outcomes[0].ok).toBe(true);
  });

  test("FETCH_PROFILE returns follow-up intent with data", async () => {
    const mockData = { displayName: "Alice", email: "alice@example.com" };
    globalThis.fetch = async () => ({
      ok: true,
      json: async () => mockData,
    });

    const outcomes = await execute([{
      kind: "FETCH_PROFILE",
      target: "/api/users/u-1234/profile",
      payload: null,
    }]);

    expect(outcomes[0].ok).toBe(true);
    expect(outcomes[0].followUpIntent.kind).toBe("profile.fetched");
    expect(outcomes[0].followUpIntent.payload.data).toEqual(mockData);
  });
});
```

---

## Common Mistakes Checklist

Use this to detect and reject anti-patterns during code review or generation.

### 1. IO in an Action
```js
// WRONG — Action performs IO
export function loadUser(state, intent) {
  const data = await fetch(`/api/users/${intent.identityRef}`);  // ← IO!
  return { delta: data, effects: [] };
}

// RIGHT — Action declares an Effect; Impact does the IO
export function loadUser(state, intent) {
  return {
    delta: {},
    effects: [{ kind: "FETCH_USER", target: `/api/users/${intent.identityRef}` }],
  };
}
```

### 2. Token Minting in an Adapter
```js
// WRONG — Adapter resolves identity
export function bindHttpAdapter(wrapper, dispatch) {
  wrapper.onRequest(async (req, res) => {
    const token = issueRequestToken(req);  // ← identity resolution!
    dispatch(intent, { res, token });
  });
}

// RIGHT — Adapter extracts raw auth; Manager mints Token
export function bindHttpAdapter(wrapper, dispatch) {
  wrapper.onRequest(async (req, res) => {
    const rawAuth = { authHeader: req.headers["authorization"] || "" };
    const intent = requestIntent(req.method, req.url, body, rawAuth, "http");
    dispatch(intent, { res });
  });
}
```

### 3. Magic Delta Keys (Control Flow Through State)
```js
// WRONG — smuggles a control instruction through the delta channel
export function cancelEdit(state, intent) {
  return { delta: { _resetToCommitted: true }, effects: [] };
  // ↑ applyDelta spread-merges this into Instance state, corrupting it
}

// RIGHT — declares a workflow Effect; Manager handles restoration
export function cancelEdit(state, intent) {
  return {
    delta: {},
    effects: [{ kind: "RESTORE_COMMITTED", target: intent.identityRef }],
  };
}
```

### 4. Skipping Invariant Validation at Commit
```js
// WRONG — commits delta without checking invariants
const { delta, effects } = action(currentInstance.state, intent);
currentInstance = applyDelta(currentInstance, delta);  // ← no validation!

// RIGHT — validate Form invariants before committing
const proposed = { ...currentInstance.state, ...delta };
const violations = Form.invariants.map(inv => inv(proposed)).filter(r => r !== true);
if (violations.length > 0) {
  // Reject commit, emit structured failure Effect
  return;
}
currentInstance = applyDelta(currentInstance, delta);
```

### 5. Business Logic in the Wrapper
```js
// WRONG — Wrapper makes business decisions
render(instance) {
  const canSave = instance.state.role === "admin";  // ← business logic!
  this.shadowRoot.innerHTML = `${canSave ? '<button>Save</button>' : ''}`;
}

// RIGHT — Wrapper renders state; Facet controls capabilities
// The Manager selects readOnlyFacet when Token lacks save permission.
// The Wrapper always renders the save button. If the user clicks it,
// dispatch finds no "save" capability in readOnlyFacet and warns.
```

### 6. Routing Logic in the Adapter
```js
// WRONG — Adapter decides what to do with the event
export function bindAdapter(wrapper, dispatch) {
  wrapper.onClick(async (e) => {
    if (e.target.id === "save") dispatch(saveIntent(...));
    else if (e.target.id === "delete") dispatch(deleteIntent(...));  // ← routing!
  });
}

// RIGHT — Adapter binds specific events to specific Intents
export function bindAdapter(wrapper, dispatch) {
  wrapper.eventSlots.save().addEventListener("click", () => dispatch(saveIntent(...)));
  wrapper.eventSlots.delete().addEventListener("click", () => dispatch(deleteIntent(...)));
}
```

### 7. Effects That Execute Themselves
```js
// WRONG — Effect is a function, not data
const effect = {
  kind: "SEND_EMAIL",
  execute: async () => await sendEmail(to, body),  // ← self-executing!
};

// RIGHT — Effect is pure data; Impact has the handler
const effect = { kind: "SEND_EMAIL", target: to, payload: { body } };
// Impact: handlers["SEND_EMAIL"] = async (effect) => sendEmail(...)
```

### 8. Identity Carrying Live State
```js
// WRONG — Identity holds mutable values
const identity = {
  entityId: "u-1234",
  formRef: "UserForm",
  currentEmail: "alice@example.com",  // ← live state in Identity!
};

// RIGHT — Identity is immutable addressing; Instance holds live values
const identity = Object.freeze({
  entityId: "u-1234",
  formRef: "UserForm",
  versioningPolicy: "hash",
});
```

### 9. Facets Used as Type Guards
```js
// WRONG — Facet used for type checking
const userFacet = { type: "User", fields: ["name", "email"] };  // ← Form's job

// RIGHT — Facet maps capabilities to Actions
const userFacet = {
  delegates: {
    "user.save":   saveUser,
    "user.delete": deleteUser,
  },
};
```

### 10. Manager Growing Without Bounds
```js
// SMELL — Manager dispatch has many domain-specific branches
async function dispatch(intent) {
  if (intent.kind === "user.save") { ... }
  else if (intent.kind === "billing.charge") { ... }    // different domain
  else if (intent.kind === "inventory.check") { ... }   // different domain
}

// RIGHT — separate Managers per bounded context, communicating through Effects
// User Manager, Billing Manager, Inventory Manager each with their own
// Instances, Facets, and Actions. Cross-context communication via Effects.
```

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