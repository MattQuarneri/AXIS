# Worked example: an extensible web server (Node)

> Assembled by `build.py` from AXIS-Specification.md. To change it, edit the source document and rebuild.

A server where routes and services are registered at runtime. The point to notice: dynamic extension is an ordinary state change, handled by the same dispatch, Action, delta and commit as a request.

## The Example

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
