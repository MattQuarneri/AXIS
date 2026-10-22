# AXIS: Agentically eXtensible Instruction Structures - For Front-End Web
**Author:** Matthew Quarneri (matt@mentic.com)
**Organization:** MENTIC Cognitive Systems  
**Version:** 2026.05.22   
**Copyright:** © 2026 MENTIC LLC  
**License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — see [LICENSE.md](LICENSE.md)

This document shows how to apply AXIS to front-end web development without forcing a brittle one-to-one metaphysical mapping onto every DOM node.

The goal is practical:

- make UI state ownership explicit
- normalize browser events into stable intent objects
- keep pure UI logic separate from DOM and network effects
- make layout and visual styling composable
- produce code that is easier for human and synthetic agents to navigate and evolve

For most browser work, use AXIS in the spirit of `AXIS-Lite.md`: preserve the discipline, not the ceremony.

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

## Example Template

See:

- [AXIS Web Todo Example](/Users/mattq/Projects/MENTIC/Core/architectures/examples/axis-web-todo/index.html)

This example demonstrates:

- custom-element wrappers
- DOM-event adapters
- pure todo actions
- a small manager/store loop
- declarative effects and concrete impacts
- composable CSS facets for layout and look

## Recommended Front-End Rules

Use these rules by default:

1. Normalize browser input at the edge.
2. Keep view-state transitions pure.
3. Let one boundary own mutable state.
4. Make DOM and storage work explicit through effects.
5. Separate layout facets from look facets.
6. Start with AXIS Lite discipline and escalate only when the app truly needs more structure.


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