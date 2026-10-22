# Common mistakes and review checklist

> Assembled by `build.py` from AXIS-Code.md, AXIS-Specification.md. To change it, edit the source document and rebuild.

Ten wrong-and-right pairs, then a checklist. When reviewing, name the mixture you found and the smallest change that restores the rule. After reading, run `python scripts/axis.py lint <paths>` on anything claimed to be pure.

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

## Code Review Checklist
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

## Constraints For Agents
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
