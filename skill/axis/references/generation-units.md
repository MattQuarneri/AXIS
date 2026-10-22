# Generation units: breaking a change into small contracts

Use this when a change is larger than one function, or when parts of it will be handed to other agents or smaller models. The aim is a set of narrow implementation contracts, each of which can be written and checked without redesigning the system. Planning the units is a separate step from implementing them.

Work from the repository's map when there is one (`codemaps/axis-map.json`; see `mapping.md`). Without a map, do a scoped mapping pass over the area you will touch first.

## Decomposition order

Work from the inside out. Starting at the UI or the Manager produces units that have to be redone once the state and rules are settled.

1. Restate the request in one or two sentences, unchanged in meaning.
2. Identify the native components it touches and the AXIS role each plays (`axis.py where <path>`).
3. New or changed Intents: commands, events, requests.
4. Form changes: schema, state shape, invariants.
5. Pure Actions, including logic that can be extracted from mixed code.
6. Effects to declare.
7. Impact handlers or infrastructure adapters.
8. Facet or capability registration, and any Manager routing change.
9. Wrapper and Adapter changes at the edge.
10. Tests and scenario traces.
11. Migration and compatibility checks.

Depart from this order only when the task is purely presentation or purely orchestration.

## The unit contract

| Field | Meaning |
|---|---|
| `id` | Stable, readable: `gen-action-declare-goal` |
| `kind` | `axis.form`, `axis.intent`, `axis.action`, `axis.effect`, `axis.impact`, `axis.adapter`, `axis.wrapper`, `axis.manager`, `axis.facet`, `axis.test`, or `native.other` |
| `targetFiles`, `symbols` | Where it goes, using the repo's `placement` |
| `purpose` | One sentence |
| `inputs`, `outputContract` | What it receives and what it must return |
| `constraints` | The rules that apply to this unit |
| `allowedDependencies`, `forbiddenDependencies` | What it may and may not import or call |
| `sideEffectPolicy` | `pure`, `declares-effects`, or `performs-io` |
| `acceptanceChecks` | Observable behaviours that prove it is done |
| `risk` | `low`, `medium`, `high` |
| `dependsOn` | Unit ids that must land first |
| `recommendedModel` | `small-local`, `strong-agent`, or `human-review` |

Choose `recommendedModel` by what can go wrong:

- `small-local`: tightly bounded pure logic, object literals, Adapters with explicit fields, tests written from examples.
- `strong-agent`: Manager routing, cross-file refactors, Effect and Impact integration, framework lifecycle work.
- `human-review`: security-sensitive policy, auth and claims, migrations, irreversible data changes, unclear invariants.

## Example unit

```json
{
  "id": "gen-action-declare-goal",
  "kind": "axis.action",
  "targetFiles": ["src/app/actions/goal.actions.js"],
  "symbols": ["declareGoal"],
  "purpose": "Add a new goal to workspace state and declare persistence.",
  "inputs": { "state": "Workspace state snapshot", "intent": "goal.declare intent" },
  "outputContract": { "delta": "new state delta with appended goal", "effects": ["PERSIST_WORKSPACE"] },
  "constraints": [
    "Do not mutate input state",
    "Do not perform IO",
    "Return effects as data only",
    "Reject empty goal text with an INTENT_REJECTED effect"
  ],
  "allowedDependencies": ["createGoalId", "normalizeGoalText"],
  "forbiddenDependencies": ["fetch", "localStorage", "fs", "Date.now", "Math.random"],
  "sideEffectPolicy": "pure",
  "acceptanceChecks": [
    "appends valid goal",
    "does not mutate original state",
    "declares persistence effect",
    "rejects empty goal"
  ],
  "risk": "low",
  "dependsOn": ["gen-intent-goal-declare"],
  "recommendedModel": "small-local"
}
```

## What to hand back

Unless asked for files, present the plan in your reply: the request as you understood it, the affected roles, the units in dependency order (id, kind, target, one-line purpose, recommended model), the risk areas that need a person, and how the whole change will be verified. When files are wanted, write `codemaps/axis-generation-units.json` (an array of units) and a short `codemaps/axis-generation-plan.md`.

After implementing a unit marked `pure`, run `axis.py lint <file>:<symbol>` on it.

## Rules

- Preserve the repo's native conventions where they are clear. AXIS roles guide placement; they are not a reason to rename files.
- Keep units small. A unit that needs the word "and" in its purpose is probably two.
- Mark ambiguous units for a strong agent or a person instead of guessing.
- Never hide IO inside a unit marked `pure`.
- Adapters do not make business decisions.
- Managers do not absorb logic that could be tested as an Action.
