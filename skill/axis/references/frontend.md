# AXIS in the browser

> Assembled by `build.py` from AXIS-FrontEnd-Web.md. To change it, edit the source document and rebuild.

How the fourteen parts map onto front-end code, without forcing a one-to-one mapping onto every DOM node. For most browser work, keep to the Lite discipline.

## Contents

- What AXIS Helps With In The Browser
- Recommended Front-End Mapping
- Browser-Specific Guidance
- Event Flow In A Small SPA
- About The Static/Dynamic Pairings
- Recommended Front-End Rules

## What AXIS Helps With In The Browser

AXIS is useful for frontend code when the application has:

- non-trivial local state
- multiple interaction modes
- async work
- styling variants
- a need for clearer seams between DOM, state, and effects

The strongest frontend benefits are:

- event normalization through Adapters
- pure state transitions through Actions
- one explicit state owner through a Manager
- effect isolation for DOM, storage, and network work
- explicit visual facet composition instead of giant CSS bundles

It is less useful when a page is mostly static or only needs a handful of direct DOM listeners.

## Recommended Front-End Mapping

This mapping is the most useful practical translation of AXIS into browser code:

| AXIS term | Front-end meaning |
|-----------|-------------------|
| `Form` | component state shape, props contract, invariants |
| `Instance` | live in-memory state snapshot |
| `Identity` | stable id for an entity, component, or session |
| `Token` | scoped runtime handle such as route, view, selection, or render token |
| `Wrapper` | custom element boundary, route shell, panel host, or other UI boundary |
| `Adapter` | raw DOM event, URL change, or storage input normalized into an `Intent` |
| `Facet` | capability or presentation surface, including layout and visual variants |
| `Intent` | stable description of what the user or system meant to do |
| `Action` | pure state transition logic that returns `{ delta, effects[] }` |
| `Manager` | orchestrator that routes intents, commits state, and dispatches effects |
| `Effect` | declarative description of DOM, storage, or network work |
| `Impact` | concrete execution of those effects |

## Browser-Specific Guidance

### 1. Wrappers Are UI Boundaries

In frontend code, a `Wrapper` is usually a custom element or route-level host. It owns:

- a stable DOM boundary
- event attachment points
- rendering slots
- component-local structure

It should not own business rules.

### 2. Adapters Normalize Browser Noise

Raw DOM events are noisy and inconsistent. Adapters convert them into stable intent objects such as:

- `todo.add`
- `todo.toggle`
- `route.change`
- `theme.set`

This makes UI flows replayable and testable.

### 3. Actions Stay Pure

Actions should not:

- touch the DOM
- call `fetch`
- read from `localStorage`
- mutate shared state directly

They should only compute:

```js
{ delta, effects }
```

### 4. Impact Is Where Browser IO Happens

In browser code, `Impact` typically handles:

- DOM rendering
- stylesheet swaps
- `localStorage` or IndexedDB persistence
- network requests
- timers

### 5. Use Facets For Visual Composition

The browser gives a very concrete meaning to `Facet`: visible variants.

For CSS, split layout and look into separate facet families.

Recommended naming:

- `{component}.{layoutKind}.layout.css`
- `{component}.{lookName}.look.css`

Examples:

- `app.columnar.layout.css`
- `app.mobile.layout.css`
- `todo-list.rowified.layout.css`
- `app.dark.look.css`
- `app.cyberpunk.look.css`
- `todo-form.dark.look.css`

This lets one layout facet mix with a different look facet without collapsing everything into one stylesheet.

### 6. Treat Divs As Projection, Not The Domain Object

A raw `div` is usually not the `Instance` itself.

It is more useful to think of the DOM as a rendered projection of the current `Instance` inside a `Wrapper`.

That distinction matters:

- `Instance` is the authoritative state snapshot
- DOM is a visible projection of that state
- Adapters translate DOM interaction back into `Intent`

### 7. Tokens In The Browser

A useful browser token family might look like:

- `sessionToken`
- `routeToken`
- `viewToken`
- `selectionToken`

A concrete format like `GUID.name.value` is reasonable when it helps make scope and meaning explicit.

Examples:

- `5d9f...route.inbox`
- `a12c...look.cyberpunk`
- `ff31...selection.todo-17`

These are not always required, but they are useful when runtime scope matters.

## Event Flow In A Small SPA

Typical AXIS browser flow:

1. `Wrapper` hosts the UI boundary.
2. `Adapter` converts a raw event into an `Intent`.
3. `Manager` routes the `Intent`.
4. `Action` returns `{ delta, effects[] }`.
5. `Manager` commits the new `Instance`.
6. `Impact` executes the `Effect`s.
7. DOM, styles, storage, or network state changes become visible.

This creates a browser architecture that is composable without being framework-heavy.

## About The Static/Dynamic Pairings

The pairings below are interesting as an exploratory lens:

- static model / dynamic model
- static controller / dynamic controller
- static identity / dynamic identity

But they should not become the main frontend teaching model. Some of the pairings can become forced if applied too literally.

For practical browser work, the most reliable distinctions are:

- structure vs runtime
- state vs projection
- pure logic vs effectful execution
- layout facet vs look facet

That framing is easier for agents to apply consistently.

## Recommended Front-End Rules

Use these rules by default:

1. Normalize browser input at the edge.
2. Keep view-state transitions pure.
3. Let one boundary own mutable state.
4. Make DOM and storage work explicit through effects.
5. Separate layout facets from look facets.
6. Start with AXIS Lite discipline and escalate only when the app truly needs more structure.
