# Worked test files

> Assembled by `build.py` from AXIS-Code.md. To change it, edit the source document and rebuild.

One test file per layer, for the user profile editor in `example-spa.md`. Note what the Action tests do not need: no mocks, no DOM, no network.

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
