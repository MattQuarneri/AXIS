# Worked example: a user profile editor (browser)

> Assembled by `build.py` from AXIS-Code.md. To change it, edit the source document and rebuild.

One feature traced through twelve of the fourteen parts in vanilla JavaScript, one file per part. It is a full-profile example, shown for clarity; it is not the required layout for every codebase.

## The Example

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
