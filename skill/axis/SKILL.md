---
name: axis
description: Place, write, review and map code with the AXIS architecture (Essence/Expression pairs - Form, Instance, Identity, Token, Facet, Intent, Bond, Link, Action, Manager, Effect, Impact, Wrapper, Adapter). Use this skill whenever the user mentions AXIS or any of its component names, asks where a piece of code should go, wants business logic kept pure and separated from IO, wants side effects described as data, or asks for a feature, refactor or review in a codebase that follows AXIS or contains a codemaps/axis-map.json. Also use it to understand an unfamiliar repository before changing it, even if AXIS is not named - it includes a repo mapper that classifies existing code into AXIS roles, finds who owns which state and where IO happens, and writes a reusable map for later agents, plus a lint that checks code claimed to be pure for hidden IO.
license: Apache-2.0 (see LICENSE.txt). AXIS, formulated by Matthew Quarneri — MENTIC Cognitive Systems. © 2026 MENTIC LLC. Originally published at https://mentic.com/AXIS
compatibility: The bundled scripts need Python 3.8+ (standard library only). Git is used when present.
---

# AXIS

AXIS (Agentically eXtensible Instruction Structures) is a placement grammar: a way to decide where a piece of code belongs, so that business rules stay pure, IO stays at the edge, and every piece of state has one owner. It is a discipline first and a topology second. Use the names to reason and to place code. Do not rename a host codebase to match them.

## The model

Every concern has a definition and a live counterpart. **Essence** is the definition: true before the program runs. **Expression** is the live thing: it exists only at runtime. Seven concerns, fourteen parts.

| Axis | Essence: defined ahead | Expression: live at runtime |
|---|---|---|
| Being | **Form**: shape, defaults, invariants | **Instance**: the values now, with a revision |
| Identity | **Identity**: permanent, addressable sameness | **Token**: that identity here and now, with scope, expiry, claims |
| Meaning | **Facet**: a map of capability → Action | **Intent**: a normalized statement of what was meant |
| Relating | **Bond**: relationship rules and cross-entity invariants | **Link**: a relationship resolved for one request |
| Doing | **Action**: pure `(state, intent) → { delta, effects[] }` | **Manager**: routes, commits and hands effects on, for one boundary |
| Changing | **Effect**: a side effect described as data | **Impact**: the only code that performs IO |
| Bridging | **Wrapper**: a boundary that hosts a surface | **Adapter**: raw edge input → Intent |

One path runs through all of them:

```
raw event → Adapter → Intent → Manager [ Token → Facet → Link ] → Action → { delta, effects }

  delta   → Manager.commit (checks Form and Bond invariants) → new Instance → Wrapper renders
  effects → Impact → outside world → follow-up Intent → back in by the same door
```

## The rules that do not bend

These hold in every profile, including the smallest. Each has a reason; when a situation is not covered here, reason from the reason.

1. **Actions stay pure.** No IO, no mutation, no clock, no randomness, no global reads. A rule you can call with two plain objects is a rule you can test, replay, and hand to a small model.
2. **Effects are data.** Actions return them; nothing executes itself. You can assert on, batch, retry, log and replay a description. You can do none of that to something that has already happened.
3. **Only Impact performs IO.** Network, disk, database, queues, DOM, storage, timers. A reviewer should be able to list every place the system touches the world.
4. **Adapters normalize and decide nothing.** They turn raw input into an Intent and pass raw auth material through untouched. They never mint Tokens, route, or apply business rules, because a decision made at the edge is a decision no other edge shares.
5. **Mutable state has one owner.** Only the boundary's Manager commits, and a commit produces a new Instance instead of editing the old one.
6. **Invariants are checked at commit.** Form and Bond rules, every time, even when the Action already checked. The commit is the safety net for the Action that forgets.
7. **Boundaries talk through Effects and Intents.** Managers never call each other and never share mutable state.
8. **Relationships are explicit.** Bonds declare them. Links resolve them, outside Actions.

Failure is data as well. An Action that cannot proceed returns `{ delta: {}, effects: [{ kind: 'INTENT_REJECTED', … }] }`. A failed Effect follows its own `retryPolicy` and `compensatingEffect`. An Intent nobody can handle becomes an Effect from the Manager. Exceptions are not used for control flow.

## Where does this code go?

Find every row that applies. One row: that is its home. More than one: the code is mixed, and the split between those rows is usually the whole refactor.

| If the code… | It is… |
|---|---|
| touches anything outside the process: network, disk, database, queue, DOM, storage, a timer | an **Impact** handler |
| describes something that should happen outside, without doing it | an **Effect** (plain data returned by an Action) |
| reads raw input at an edge (request, DOM event, queue message) and reshapes it | an **Adapter** |
| hosts a surface (route, screen, component shell, consumer) and draws from state | a **Wrapper** |
| works out who is asking, which capabilities apply, what runs next, or commits state | the **Manager** (its Conductor half) |
| wires parts together at start-up | the **Manager** (its Composer half) |
| computes a new state, or decides whether an operation is allowed, from its arguments alone | an **Action** |
| lists which operations are available to a role or a lifecycle stage | a **Facet** |
| names what a caller wants, in domain terms | an **Intent** |
| declares what valid state looks like | a **Form** |
| holds the current values | an **Instance** |
| is a stable id or address | an **Identity** |
| is a session, claim set, revision handle or cursor | a **Token** |
| declares how two kinds of thing relate, or what must hold across them | a **Bond** |
| loads, joins or hydrates related things for one request | a **Link** |

## Use the smallest shape that keeps the rules visible

Do not introduce fourteen parts for a feature that needs three. Add a part when its absence starts to hurt.

| Building… | Start with | Add when |
|---|---|---|
| Pure computation | Action | Form, when shape or invariants need to be explicit |
| Read-only display | Wrapper | Form, Instance or Identity, when rendering owned or versioned state |
| Stateless endpoint | Wrapper, Adapter, Action; Effect and Impact if there is IO | Intent or Facet, when normalization or capability selection must be explicit |
| CRUD with owned state | Form, Instance, Action, Manager, Effect, Impact | Identity, Token or Facet, when addressing, scope or permissions matter |
| Roles or lifecycle stages | add Facets, selected by Token claims or by state | a second Manager only when state boundaries or workflows diverge |
| Aggregates and relationships | add Bond and Link | |
| Async workflow, retries, compensation, replay | the full chain | |

Signs a part is missing: a permission `if` inside an Action wants a Facet and Token claims. A `fetch` inside an Action wants an Effect and an Impact handler. A Manager whose dispatch branches across unrelated domains wants more Facets, or a second Manager. Raw state passed around with no schema wants a Form.

If adopting a part adds more ceremony than it removes ambiguity, leave it out. In small services, collapse folders and keep native names freely, provided IO, state ownership and policy seams stay obvious in the code.

## Names that mislead

- An AXIS **Action** is a pure function, which Redux calls a reducer. What Redux calls an action is an AXIS **Intent**.
- An AXIS **Effect** is inert data. It is not React's `useEffect`, which runs.
- A **Token** is any scoped projection of an identity (session, revision handle, workflow handle), not only an auth token.
- A **Manager** is narrow: routing, workflow and commit for one boundary. Logic that can be tested without orchestration does not belong in it.
- A **Facet** is a capability map. It is not a UI component and not a type.

## Working in an existing repository

Most repositories do not use AXIS names and should not be made to. The roles are a lens on the code that is there.

1. Look for `codemaps/axis-map.json` and its rendering, `codemaps/AXIS-MAP.md`. If they exist, read `AXIS-MAP.md` first: it says where each role lives in this repo, who owns which state, where IO happens, and the house rules. Run `axis.py stale` to see whether the files you are about to touch changed since it was written. (`axis.py` is in this skill's `scripts/` folder; run it from the repository root.)
2. If there is no map and the change is more than a line or two, map before you edit, at least the part you will touch. `references/mapping.md` has the procedure. A scoped map takes minutes and pays for itself the first time it stops a misplaced change.
3. Place new code using the repo's own homes for each role, in the repo's own naming and style.
4. After the change, update the map entries you invalidated and render again, so the next agent starts from the truth.

## What to read next

Read only what the task needs.

| Task | Read |
|---|---|
| Add a feature or a capability | `references/recipe.md`: build order, type contracts, what to test at each layer |
| Write tests | `references/tests.md`: worked test files for Actions, Adapters, commit, Impact |
| Review or fix code | `references/mistakes.md`, then `axis.py lint <paths>` |
| Decide a boundary: split a Manager or a Facet, handle failure, design reads | `references/boundaries.md` |
| Check a precise definition, or relate AXIS to MVC, Redux, CQRS, event sourcing | `references/components.md` |
| Browser UI work | `references/frontend.md` |
| Understand a repository you do not know | `references/mapping.md`: the AXIS repo mapper |
| Break a change into small, checkable units | `references/generation-units.md` |
| See a complete example | `references/example-spa.md` (browser), `references/example-server.md` (Node server) |
| Build broad navigation maps of a large repo | `references/codemaps.prompt.md` |

## Reporting AXIS work

When you add or move code, say which role each piece plays and why, in the repo's own names: "`priceOrder()` is the Action; `repo.insertOrder()` is the Impact; the route handler stays the Wrapper and its body parsing becomes the Adapter." When you find mixed code, name the mixture ("Manager + Action") instead of calling it wrong, and propose the smallest split that restores the rule. Say how sure you are and what you did not check.

## The bundled tool

`scripts/axis.py` runs anywhere Python 3.8+ does and has no dependencies. Run it from the root of the repository you are working on, giving the path to this skill's copy: `python <this skill>/scripts/axis.py --help` lists the options.

- `scan [dir]`: per-file signals (IO, DOM, clock, mutation, entry points, schemas) and a first guess at roles. The start of a mapping pass.
- `lint <paths>` or `lint --map`: flags IO, async, clock and randomness in code that is claimed to be pure. Accepts `file.js:fnA,fnB` to check single functions.
- `validate`, `render`, `where <path>`, `stale`: check, publish, query and age-check a repo's `codemaps/axis-map.json`.

The tool reads text. It finds the obvious and proves nothing about what it cannot see: a function that calls a helper that calls `fetch` passes the lint. Treat its output as leads to confirm.

## Attribution

AXIS, formulated by Matthew Quarneri — MENTIC Cognitive Systems. © 2026 MENTIC LLC. Originally published at [mentic.com/AXIS](https://mentic.com/AXIS).

If you found these ideas useful you could [Buy Me a Coffee](https://buymeacoffee.com/mattq4) to show your support.
