# Mapping a repository in AXIS terms

The AXIS repo mapper produces a small, durable map that tells any agent, including you next session, where each AXIS role lives in one particular codebase, who owns which state, where IO happens, and what the house rules are.

This is a mapping pass, not a rewrite pass. Most repositories do not use AXIS names and should not be forced to. You are identifying the roles the native architecture already plays, by evidence, and naming honestly where one piece of code plays several.

## Contents

- What you produce
- Choose a depth
- Procedure (eight steps)
- Classifying conservatively
- The map format
- Using and maintaining a map
- How this relates to CodeMaps

## What you produce

Two files, in the repository's `codemaps/` folder:

- `codemaps/axis-map.json`: the map. You write this.
- `codemaps/AXIS-MAP.md`: rendered from the JSON by `axis.py render`. Never edit it by hand.

The JSON can be validated and queried. The markdown is what an agent reads at the start of a task, about two thousand tokens for a mid-sized repo. Rendering one from the other means they cannot disagree.

Run `axis.py` from the repository root, giving the path to this skill's `scripts/axis.py`.

## Choose a depth

| Depth | When | Reading budget | Covers |
|---|---|---|---|
| `scoped` | You have a specific change to make | The scan summary and at most about ten files | The boundary you will touch, its edges and its IO |
| `standard` | Onboarding onto a repo | The scan summary, entry points, and the central file of each boundary | Every boundary, three to ten flows, the audit, placement and rules |
| `deep` | Preparing reuse or a larger refactor | As standard, plus the files behind each finding | Adds `recompositionNotes` on every role. Pair with the CodeMaps navigation maps |

Record the depth and the scope in `meta`. A scoped map is a legitimate result; list what it leaves out in `unmapped`. Stop expanding when new files stop changing the picture.

## Procedure

**1. Scan.**

```bash
python <skill>/scripts/axis.py scan . --out codemaps/axis-scan.json
```

Read the printed summary first, not the JSON. It lists entry points, IO sites, files where logic and IO sit together, pure candidates, declarations, policy and auth mentions, relationships, orchestration, and a per-directory tally. The scan is a lead generator: names and signals suggest, source confirms. If `codemaps/` already holds navigation maps (`01-architecture.md` and so on) or a repo digest, read those before opening source. If it holds output from the earlier CodeMaps AXIS pipeline (`axis-role-map.json`, `axis-shape.md`, `axis-boundary-audit.md`), start from that: its role descriptors carry over field for field, and its audit becomes `findings`.

**2. Walk the seven axes, from the outside in.** For each axis, answer its question for this repo, confirm the central items in source, and record role entries. Following a request inward is the cheapest way to find everything.

| Axis | The question for this repo | Look for |
|---|---|---|
| Bridging | Where does the outside come in? | **Wrapper**: routes, CLI commands, UI shells, message consumers, schedulers, worker hosts. **Adapter**: request mappers, DOM event normalizers, payload parsers, DTO converters |
| Meaning | What can be asked of it, and who may ask what? | **Intent**: command objects, semantic events, normalized requests. **Facet**: role or capability maps, policy tables, feature gates, plugin registries |
| Identity | What are the stable things, and who is asking? | **Identity**: ids, keys, URIs, record locators. **Token**: sessions, claim sets, revision handles, cursors, transaction or workflow handles |
| Doing | Where are the rules, and who coordinates? | **Action**: pure reducers, validators, pricing rules, parser cores, state transitions. **Manager**: coordinators, application services, dispatchers, process managers, commit points |
| Changing | What does it do to the world, and where? | **Effect**: side-effect descriptors, job envelopes, outbound commands. **Impact**: repositories, HTTP clients, file writers, queue producers, mailers, renderers |
| Being | What state exists, and what shape must it have? | **Form**: schemas, types, validation contracts, config shapes. **Instance**: records, aggregate state, store values, caches, documents |
| Relating | What belongs to what? | **Bond**: foreign-key rules, aggregate boundaries, ownership relations. **Link**: joins, hydrated graphs, lazy loads, resolved references |

Each Manager-equivalent that owns state is a **boundary**. Record it in `boundaries` with what it owns, what it accepts, and what it emits. For every piece of state, be able to say which boundary writes it. State with two writers, or none you can name, is a finding.

**3. Classify conservatively.** See the next section.

**4. Trace the top flows.** Pick three to ten that an agent is likely to extend. For each: the trigger, then the steps in order, each with its AXIS role, where it happens, and what it does. Say plainly where a role is skipped ("there is no explicit Intent object").

**5. Audit the boundaries.** Record each problem as a finding, with paths, evidence, a risk, and the smallest separation that would restore the rule.

| Kind | What you saw |
|---|---|
| `io-in-logic` | Business rules and IO in the same function |
| `policy-in-logic` | Role or permission checks written inline in rules or handlers |
| `adapter-decides` | An edge handler routing, applying rules, or reaching past the coordinator |
| `manager-too-broad` | One coordinator spanning unrelated domains or stores |
| `hidden-state` | Shared mutable state with no clear owner |
| `traversal-in-logic` | Lazy loads, joins or fetches of related entities inside business logic |
| `self-executing-effect` | A "description" of work that performs the work |
| `framework-coupling` | Framework types threaded through logic, blocking test or reuse |
| `other` | Anything else an agent changing this code should know |

Do not recommend a large rewrite unless a boundary problem directly damages testability, reuse, or the safety of an agent working there.

**6. Write `placement` and `rules`.** These are what an agent uses most.

- `placement` answers "where does new code of this role go, in this repo?" For each of the fourteen roles give the native files or folders, or `null` when the repo has no home for that role.
- `rules` are five to twelve imperative sentences for anyone changing this repo: boundaries not to cross, the single place each kind of IO lives, what to do instead of repeating a known mixture, which tests to run. Write them in the repo's own names.

**7. Validate, lint, render.**

```bash
python <skill>/scripts/axis.py validate
python <skill>/scripts/axis.py lint --map
python <skill>/scripts/axis.py render
```

Fix what `validate` reports. `lint --map` checks every role you recorded as a pure Action; a failure means the entry is misclassified or you have found a real problem, and either way the map should say so.

**8. Leave a pointer.** So that later agents find the map, add a short note to the repo's `AGENTS.md`, `CLAUDE.md` or README. Ask before editing a file that is not yours to change.

```markdown
## Architecture map
`codemaps/AXIS-MAP.md` describes where each kind of code lives here, who owns which state, and where IO happens.
Read it before changing code. It is rendered from `codemaps/axis-map.json`; update the JSON, then re-render.
```

## Classifying conservatively

- **Evidence over names.** A file called `actions.ts` that calls `fetch` is not an Action. Record what the code does.
- **Name mixtures.** Give the role the code mostly plays as `primaryAxisRole`, the others as `secondaryAxisRoles`, and set `purity` to `mixed` when logic and IO share a function.
  - Business logic that also performs IO: `Action` + `Impact`, never a pure Action.
  - A controller that parses input and runs the workflow: `Wrapper` + `Adapter` + `Manager`.
  - A repository that validates rules and writes: `Impact` + `Action`.
  - A service that sequences calls and contains the rules: `Manager` + `Action`.
  - Framework lifecycle glue: `Wrapper` or `Manager`, with a note about the coupling.
- **Absent is an answer.** If the repo has no declared Effects, say so (`"Effect": null` in `placement`) and say what plays that part. Do not invent roles for symmetry.
- **Mark your confidence.** `high` when you read the source, `medium` when signatures and call paths agree, `low` when you are going by signals alone. Set `evidenceBasis` to `source-confirmed` or `scan`.
- **Every role needs evidence.** At least one concrete observation: an import, a signature, a call, a write.
- **Do not claim compliance.** Say "already AXIS-shaped" only where the evidence is strong.

## The map format

A complete, validated example for a small service is in `assets/axis-map.example.json`. Read it before writing your first map. The skeleton:

```json
{
  "meta": {
    "axisMapVersion": 1,
    "repo": "name",
    "generatedAt": "YYYY-MM-DD",
    "commit": "the HEAD commit when mapped, so staleness can be computed",
    "depth": "scoped | standard | deep",
    "scope": ["src"],
    "languages": ["typescript"]
  },
  "summary": "Two to four sentences: what the system is, how it is organised natively, where it is clean and where it is mixed.",
  "boundaries": [
    { "id": "orders", "name": "Orders", "nativeName": "OrderService", "paths": ["src/orders"],
      "ownedState": ["orders table"], "acceptedIntents": ["create order"], "emittedEffects": ["confirmation email"],
      "policyScope": "which roles or claims it interprets" }
  ],
  "roles": [
    { "id": "unique-id",
      "nativeName": "what this repo calls it",
      "nativeKind": "route-handler | service | repository | schema | …",
      "paths": ["src/orders/controller.ts"],
      "symbols": ["create"],
      "boundary": "orders",
      "primaryAxisRole": "Wrapper",
      "secondaryAxisRoles": ["Adapter", "Manager"],
      "purity": "pure | reads-state | io | mixed",
      "stateOwnership": "none | reads | owns",
      "sideEffects": ["writes HTTP responses"],
      "confidence": "high | medium | low",
      "evidenceBasis": "source-confirmed | scan",
      "evidence": ["(req, res) handlers", "calls OrderService.create"],
      "inboundEdges": ["POST /orders"],
      "outboundEdges": ["OrderService.create"],
      "boundaryNotes": ["what is clean, what is mixed"],
      "recompositionNotes": ["what to preserve, extract or leave in place"] }
  ],
  "flows": [
    { "name": "Create an order", "trigger": "POST /orders",
      "steps": [ { "role": "Adapter", "ref": "a role id", "does": "what happens at this step" } ] }
  ],
  "findings": [
    { "kind": "io-in-logic", "risk": "low | medium | high", "paths": ["src/orders/service.ts"],
      "evidence": "what you saw", "separation": "the smallest change that restores the rule" }
  ],
  "placement": { "Form": ["src/schemas"], "Action": ["src/domain"], "Impact": ["src/infra"], "Effect": null },
  "rules": ["Imperative sentences for anyone changing this repo."],
  "unmapped": ["path — why it was left out"]
}
```

Required: `meta`, and `roles` with `id`, `nativeName`, `paths`, `primaryAxisRole`, `confidence` and `evidence`. `purity` is required for the roles that run (Action, Manager, Impact, Wrapper, Adapter, Link). A flow step may use `where` (a path) instead of `ref` when it has no role entry. Paths are relative to the repository root and must exist. The role descriptors keep the field names of the earlier `axis-role-map.json`, so prompts written for that file can read `roles` directly.

## Using and maintaining a map

At the start of a task:

```bash
python <skill>/scripts/axis.py stale                 # what changed since the map was written
python <skill>/scripts/axis.py where src/orders/service.ts
```

Read `codemaps/AXIS-MAP.md`, then ask `where` about each file you expect to touch. It prints the roles, the boundary, the notes, and any findings that cover it.

After a change, update the entries you invalidated: roles whose behaviour moved, findings you fixed or introduced, `placement` if a role gained a home, and `meta.commit` and `meta.generatedAt`. Then validate and render. A map that is known to be stale in three places is still worth more than no map, provided `stale` can tell the next reader which three.

## How this relates to CodeMaps

`references/codemaps.prompt.md` builds navigation maps: it reads a repo as a tree (entry points, runtime, components, state, public surface) and marks which subsystems could be harvested for reuse. The AXIS map reads the same repo by role. They answer different questions and compose well. CodeMaps calls the pair Stage 1 (map and understand) and Stage 2 (clarify and refactor); this procedure is the first step of Stage 2.

| CodeMaps file | Feeds this axis |
|---|---|
| `02-entry-points.md`, `08-public-surface.md` | Bridging: Wrappers and Adapters |
| `03-runtime-topology.md`, `04-components.md` | Doing: Managers and boundaries |
| `05-state-and-persistence.md` | Being and Changing: Instances, who owns them, Impacts |
| `06-domain-model.md` | Being, Relating, Meaning: Forms, Bonds, Intents |
| `10-guardrails-and-workflows.md` | `rules` |
| `11-recomposer-anchors.md` | `recompositionNotes` at `deep` depth |

On a large or unfamiliar repo, run CodeMaps first and build the AXIS map from its output. On a small repo, or for a scoped map, the scan is enough.
