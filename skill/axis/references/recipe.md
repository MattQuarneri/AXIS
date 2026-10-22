# Adding a capability

> Assembled by `build.py` from AXIS-Code.md, AXIS-Lite.md. To change it, edit the source document and rebuild.

The order to build in, the shape of each part, and what to test at each layer. Skip the steps the feature does not need: see "Use the smallest shape" in SKILL.md. The worked test files the recipe mentions are in `tests.md`.

## Contents

- Feature Recipe: Adding a New Capability
- Type Contracts (Language-Agnostic)
- What To Test At Each Layer
- Folder Structure
- Credibility Tests

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

## What To Test At Each Layer
- **Actions**: unit test with snapshot state + intent → assert delta + effects
- **Adapters**: raw event → assert correct Intent produced (including rawAuth extraction)
- **Manager commit**: delta + Form invariants → assert commit accepted or rejected
- **Manager routing**: intent + token → assert correct Facet selected
- **Effects**: assert Action declares expected Effect data
- **Impact**: integration test with mocked targets → assert side effects executed
- **Tokens**: assert scoping, expiry, and claim propagation

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

## Credibility Tests

AXIS Lite is helping only if it makes the codebase easier to change.

Use these checks:

1. Can a business rule be unit tested without network or database mocks?
2. Can reviewers quickly tell where IO happens and where it does not?
3. Can a new feature be added without touching unrelated workflows?
4. Can one bounded context change without silently corrupting another?
5. Did adopting AXIS reduce ambiguity more than it increased ceremony?

If the answer to `5` is no, simplify the shape.
