# AI Coding Agents Need Maps, Not Just Prompts

AI coding tools have clearly gotten better at writing code. Generating the text that compiles and works is no longer the hard part.

The harder problem is structural. Determining the shape of the codebase: what components exist and what they're responsible for, where logic and state belong, what it should depend on, what it is allowed to change, and how useful pieces of logic should be designed to facilitate reuse and recomposition without dragging half a codebase with it.

Most software teams already know this problem in human terms. Classically a senior engineer would join a project and spend days if not weeks building a mental map of the system. They would ask questions like:

- Where does execution start?
- Which modules own state?
- Which services touch the database?
- Which functions are pure business logic?
- Which files are framework glue?
- Which parts are reusable and which are deeply tied to the current app?

AI agents have the same problem, but worse. If it's not documented they do not inherit the team's tacit memory. They reconstruct context from whatever files, prompts, comments, tests, and tool outputs they can see in the moment. And that structure is often incomplete, inconsistent, and ambiguous. They can generate code that compiles, but they cannot reliably generate code that fits the architecture. To avoid this, a coding agent needs more than instructions, it needs maps.

## The Missing Layer: Architectural Metadata

Most codebases contain a lot of implicit knowledge:

- the entry points,
- the runtime loop,
- the major components,
- the public APIs,
- the data boundaries,
- the side-effect boundaries,
- the reusable subsystems,
- the parts that are safe to move,
- the parts that should never be copied without their surrounding context.

Humans learn this gradually through reading, debugging, code review, and tribal knowledge. Agents need that same structure represented explicitly.

That is the motivation behind a project I have been calling AXIS, supported by a set of CodeMaps and recomposition prompts.

The goal is not to invent another framework. The goal is to create a metadata architecture that helps human and AI agents understand, modify, generate, and reuse code with less ambiguity.

## CodeMaps: Reading a Codebase as a Tree

The first idea is simple: map the codebase before asking an agent to change it.

A useful map should not be an exhaustive class listing. Exhaustive documentation is often too much noise. A good map should help an agent quickly answer:

- What is this system?
- How does it run?
- Where does execution begin?
- What are the major branches of behavior?
- Where does state live?
- Where does IO happen?
- What public surfaces does the system expose?
- Which components are central enough that changing them is risky?

I think of this as reading the repository like a logical tree:

```txt
roots           -> entry points
trunk           -> runtime loop and lifecycle
branches        -> major components
leaves          -> public interfaces and extension points
functionality   -> signatures, functions, methods, contracts
ground          -> persistence, config, state, external systems
```

This gives agents and humans a shared navigation layer. Instead of telling an agent "go inspect the repo," we can ask it to build or consult a structured map:

- architecture overview,
- entry-point map,
- runtime topology,
- component map,
- state and persistence map,
- public surface map,
- signature index,
- recomposer anchors.

The important shift is that paths, signatures, imports, exports, side-effect hints, and ownership boundaries become first-class navigation material.

## Recomposition: Reusing Organs, Not Files

The second idea is that code reuse should not start with files. It should start with functional closures around objects and components.

When people say "can we reuse this code?", they often mean "can we copy this file?" That is usually the wrong question.

The better questions are:

- What useful capability lives here?
- What is the smallest set of components needed for that capability to work?
- What contracts, state, config, and side-effect boundaries must come with it?
- Which dependencies are intrinsic to the capability?
- Which dependencies are replaceable host infrastructure?
- Where would an adapter need to sit in a different codebase?
- How much rewrite pressure should we expect?

I call these reusable capability clusters "harvest targets." They are closer to organs than files. A validation pipeline, event batching loop, workflow coordinator, document parser, rules engine, or synchronization process may span many files. To functionally support reuse, understanding the capability's functional closure is essential.

That is what the Recomposer prompt is designed to surface:

```txt
capability nucleus
functional closure
inbound edges
outbound edges
dependency seams
owned state
side effects
rewrite pressure
recommended integration strategy
```

This matters because AI-assisted reuse can easily become fast copy-paste at scale; which is dangerous. If an agent imports logic without understanding host assumptions, state ownership, lifecycle hooks, or IO patterns, it may create subtle damage that compiles cleanly.

Recomposition is the discipline of asking what must survive the transplant.

## AXIS: A Placement Grammar For Generated Code

The third idea is AXIS itself: a vocabulary for deciding where code belongs.

At the practical level, AXIS starts with a few rules:

- Normalize raw input at the edge.
- Keep business logic pure when possible.
- Treat side effects as data until execution.
- Let one boundary own mutable state.
- Validate invariants at commit time.
- Make cross-boundary interaction explicit.

These ideas are familiar because good architectures keep rediscovering them. You can see relatives in functional-core / imperative-shell, Redux, CQRS, Event Sourcing, Hexagonal Architecture, Clean Architecture, and Domain-Driven Design.

AXIS is not valuable because no one has ever separated pure logic from IO before. AXIS is valuable because agents need explicit placement rules.

For example:

```txt
Raw browser event or HTTP request -> Adapter
Normalized meaning -> Intent
Pure state transition -> Action
Declared side effect -> Effect
Actual network, disk, DOM, or queue work -> Impact
State ownership and orchestration -> Manager
```

That gives an agent a decision procedure. If the code performs IO, it does not belong in a pure Action. If it translates an HTTP request or DOM event, it belongs at the Adapter boundary. If it describes an external operation, it can be an Effect. If it executes that operation, it is Impact.

That may sound like ordinary discipline, but ordinary discipline is exactly what breaks under pressure. It is also exactly what agents need written down.

## Why This Matters For Business

AI adoption in software teams is not only a productivity question. It is a reliability question.

If agents can generate code faster than teams can review architectural consequences, the bottleneck moves from typing to trust. Businesses will need ways to answer:

- Did the agent put the change in the right place?
- Did it accidentally mix business logic with infrastructure?
- Did it touch a state boundary it does not own?
- Did it copy reusable logic without its required closure?
- Did it make a local fix that damages long-term maintainability?

Better prompts help, but prompts alone are not enough. Teams need a structured representation of the system the agent is operating in.

That is what this architecture is trying to provide:

```txt
Want -> architecture placement -> code map -> generation unit -> validation -> recomposition
```

The business value is straightforward:

- faster onboarding for humans and agents,
- safer AI-assisted refactoring,
- more reliable modernization of legacy systems,
- better identification of reusable subsystems,
- cleaner separation between core logic and infrastructure,
- improved testability because pure logic is easier to validate,
- less context loss across long-running agent workflows.

## What I Would Not Claim

I would not claim AXIS is a replacement for all existing architectures.

I would not use the full vocabulary for every small feature.

I would not force a team to create a dozen files for a simple CRUD endpoint.

The practical version is AXIS Lite: preserve the discipline, not the ceremony. Start with the smallest shape that keeps the important boundaries visible. Add the richer vocabulary only when complexity justifies it.

That caveat matters. An architecture that helps agents must constrain them, but it must not turn every change into ritual.

## The Deeper Thesis

My working thesis is this:

> AI coding agents will need architectural metadata the way compilers need type information.

Types do not write the program for us. They constrain interpretation. They catch certain classes of errors early. They make contracts explicit.

Architectural metadata can do something similar for agents:

- map the repo,
- identify ownership boundaries,
- distinguish pure logic from side effects,
- expose reusable capability closures,
- guide generation tasks,
- support safer recomposition.

The more capable coding agents become, the more important this layer becomes. The cost of ambiguity rises when the actor making changes can modify hundreds of files quickly.

## What Is In The Repo

I am preparing the AXIS and CodeMaps materials as a public repo for people who want the full details.

The core pieces are:

- AXIS Lite: the practical rules for pure logic, effects, IO boundaries, state ownership, and commit validation.
- AXIS Principles: the conceptual framing.
- AXIS Specification: the full reference model.
- CodeMaps prompts: repo navigation maps for agents.
- Metaprogrammer prompts: component-level shape extraction.
- Recomposer prompts: identifying harvestable functionality and functional closure.
- Composer prompts: planning cross-repo integration.
- Example code: a small frontend implementation using wrappers, adapters, intents, actions, effects, and impacts.

The article version is intentionally lighter than the repo. The repo is where the terminology, examples, and implementation details belong.

## Closing Thought

AI coding agents do not just need better generation. They need better orientation.

A human engineer with context can often infer where code belongs. An agent benefits when that context is externalized as maps, contracts, boundaries, and generation units.

That is the heart of AXIS and CodeMaps:

```txt
Make the architecture legible enough that humans and agents can work on it together.
```

The future of AI-assisted software development is not be only about writing more code. It's about making codebases understandable, navigable, recomposable, and able to handle change at agent speed safely.

---

*AXIS, formulated by Matthew Quarneri — MENTIC Cognitive Systems. © 2026 MENTIC LLC. Originally published at [mentic.com/AXIS](https://mentic.com/AXIS). Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).*

If you found these ideas useful you could [Buy Me a Coffee](https://buymeacoffee.com/mattq4) to show your support.
