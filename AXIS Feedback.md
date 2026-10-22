# AXIS Feedback

## Executive Judgment

AXIS is useful, but not equally useful in every framing.

The strongest version of the work is not "a new software architecture." That framing makes it compete with MVC, Clean Architecture, DDD, CQRS, Event Sourcing, Redux, Hexagonal Architecture, and functional-core / imperative-shell patterns. A skeptical senior engineer will immediately recognize many of the shapes and may dismiss AXIS as a renamed taxonomy.

The stronger framing is:

> AXIS is a metadata architecture for helping human and AI agents understand, generate, recompose, and safely reuse code.

That is a better claim because it fits the actual novelty in the material. AXIS is not strongest as a replacement for existing engineering patterns. It is strongest as a shared map that makes architectural boundaries explicit enough for agents to navigate.

If I were evaluating this for AI Solutions Architect roles at OpenAI, Anthropic, or Google, I would see real signal here. The work shows systems thinking, agent-awareness, abstraction ability, and a practical understanding of codebase comprehension. But I would also expect a hiring manager or principal engineer to push hard on over-abstraction, evidence, and usability.

The work can be compelling if presented as a disciplined method for agentic code comprehension and recomposition. It will be weaker if presented as a grand theory that claims to derive all software architecture from first principles.

## What Is Actually Strong

### 1. The CodeMaps + Recomposer pipeline is the most market-relevant piece

The CodeMaps prompts are excellent because they address an immediate problem AI coding teams care about:

- agents lose context,
- codebases are too large to read exhaustively,
- repo structure is often implicit,
- reusable subsystem boundaries are hard to identify,
- cross-repo code reuse is usually file-oriented instead of capability-oriented.

The CodeMaps, Metaprogrammer, Recomposer, and Composer prompts form a coherent pipeline:

```txt
Repo -> structural digest -> navigation maps -> component model -> harvestable organs -> graft plan
```

This is useful. It is concrete. It maps directly to agentic engineering workflows.

The language around "functional closure," "harvest posture," "dependency seams," and "rewrite pressure" is particularly strong. That vocabulary is more differentiated than the AXIS component grid itself. It describes what an AI coding agent actually needs to know before attempting reuse:

- What does this subsystem do?
- What must come with it?
- What can be replaced?
- Where does host infrastructure attach?
- What will probably break if we transplant it?

That is valuable and worth leading with.

### 2. AXIS Lite is credible engineering discipline

The Lite profile is the most defensible engineering artifact in the AXIS set. Its hard rules are practical:

- Actions stay pure.
- Effects are data.
- Only Impact performs IO.
- Adapters normalize edge input.
- Mutable state has an explicit owner.
- Invariants are validated at commit time.
- Cross-boundary interaction is explicit.

These are not merely philosophical. They reduce real failure modes:

- business rules hidden in controllers,
- IO mixed into domain logic,
- auth decisions scattered across adapters,
- state mutation with no owner,
- code that agents can patch locally while damaging architecture globally.

For agentic development, these rules are especially valuable. Agents need explicit placement constraints. "Put the business rule in the Action and declare IO as an Effect" is a much better instruction than "keep the code clean."

### 3. The Wantware/AXIS/CodeMaps stack has a coherent story

The broader stack has a promising shape:

```txt
Wantware preserves the Want, establishes the gap, and carries delivery obligations through execution and verification.
AXIS decides where it belongs.
CodeMaps shows how the existing code tree is shaped.
Recomposer identifies reusable capability organs.
Composer decides how to graft those organs into another tree.
```

That is a strong idea. It connects user intent, architecture, repo comprehension, code generation, and reuse.

The Wantware layer needs the stepwise process described in [The WantWare Development Process](../The%20WantWare%20Development%20Process.md#31-the-speech-act-flow): preserve the expressed Want; establish current and wanted states from evidence while recording assumptions and uncertainty; specify the truths required to close the gap; obtain an accountable actor's delivery commitment; have that committer write the Directives; refine those instructions into executable steps; and check the resulting evidence against the required truths and the original Want.

AXIS supplies placement and component discipline for that work. CodeMaps, Recomposer, and Composer support comprehension and implementation within the committer's Directives; they do not replace the commitment or author it merely by producing a graft plan. A generated component, a successful test of one operation, or a Manager's valid state commit can provide evidence, but none alone establishes delivery fulfillment. The process needs deterministic contracts around probabilistic analysis and generation: explicit inputs, acceptance checks, and defined revision, retry, or escalation branches. Failed checks leave the obligation unmet and route work back to the affected step; they do not redefine the Want to fit the generated result.

This is the part most likely to interest AI platform teams: not "here is my architecture," but "here is a repeatable way to turn wants and existing codebases into structured, inspectable, reusable generation units."

### 4. The example implementation helps

The AXIS web todo example matters because it shows that the model can become code:

- wrappers for UI boundaries,
- adapters for raw DOM events,
- intents as normalized meaning,
- actions as pure state transitions,
- effects as declarations,
- impacts as DOM/storage execution,
- CSS facets for layout/look composition.

The example is small, but it proves the vocabulary is not only prose. For a public repo, keep this example and add at least one more scenario showing CodeMaps/Recomposer output on a real codebase.

## What Will Get Challenged

### 1. The ontology can sound over-claimed

The full AXIS grid is elegant:

```txt
Form / Instance
Identity / Token
Facet / Intent
Bond / Link
Action / Manager
Effect / Impact
Wrapper / Adapter
```

But a senior reviewer will see familiar concepts:

- Form = schema/type/model shape
- Instance = entity state/document
- Intent = command/event/request DTO
- Action = pure reducer/use-case function
- Effect = side-effect descriptor
- Impact = effect handler/driver
- Wrapper/Adapter = ports-and-adapters edge structure
- Manager = coordinator/application service/process manager
- Bond/Link = relationship definition and traversal

That does not invalidate AXIS. But it means the public claim must be precise.

Do not imply that AXIS invents these categories. Say that AXIS normalizes them into a shared agent-readable vocabulary.

### 2. The full profile risks ceremony

The full 14-component topology is too heavy as a default. If a reviewer thinks every feature requires every AXIS component, they will file the work under "architecture astronautics."

Your own Lite document solves this. Make it central.

The public line should be:

> AXIS is a discipline first and a topology second. Start Lite. Add vocabulary only when complexity creates ambiguity.

That one sentence prevents a lot of objections.

### 3. "Manager" remains dangerous

The docs correctly warn that Manager can become a god object. But the concept still attracts risk because it owns routing, workflow, commit, token lifecycle, and sometimes composition.

For credibility, emphasize boundary-scoped coordination and the Composer/Conductor split. Better yet, in examples, show Managers that are small. A public reader should see that AXIS prevents god objects rather than renaming them.

### 4. The philosophical language should not lead the business article

"Essence," "Expression," "Being," "Meaning," and "Cognitive Flow of Change" are interesting, but they are not the first hook for LinkedIn.

For a business-oriented audience, lead with the operational problem:

- AI agents can write code but struggle to understand large codebases.
- Reuse fails because code is copied by file, not by functional closure.
- Teams need repo maps, component contracts, and side-effect boundaries.
- AXIS/CodeMaps provides a structure for that.

Only after that should you introduce Essence/Expression as the organizing lens.

### 5. Hiring teams will want evidence

For AI Solutions Architect roles, the idea is not enough. You need proof artifacts:

- before/after refactor using AXIS Lite,
- CodeMaps generated for a non-trivial repo,
- Recomposer candidates extracted from that repo,
- one attempted transplant or recomposition,
- tests showing pure Actions are easier to validate,
- a simple diagram of the pipeline.

The current docs show strong conceptual design. The next credibility leap is demonstrable execution.

## How I Would Position This For OpenAI, Anthropic, and Google

### Lead with agentic systems, not private terminology

Hiring managers at these companies are likely to care about:

- making AI agents more reliable in codebases,
- reducing context loss,
- structuring tool and code interactions,
- making generated code auditable,
- helping enterprises adopt AI safely,
- mapping messy software systems into machine-readable forms.

So the positioning should be:

> I designed a metadata architecture for agentic software development: a way to map codebases, identify reusable capability closures, and constrain code generation so AI agents can modify and recompose systems safely.

That lands better than:

> I invented a new architecture called AXIS based on Essence and Expression.

### Use AXIS as the underlying model

In interviews, AXIS should be the mechanism, not the headline.

Good interview framing:

1. "The problem is that agents do not have the tacit architectural memory humans have."
2. "I built prompts and documents that externalize that memory as maps, signatures, closures, and side-effect boundaries."
3. "AXIS provides the placement grammar: edge normalization, pure transformations, declared effects, isolated IO, explicit state ownership."
4. "CodeMaps and Recomposer turn existing repos into navigation and reuse substrates."
5. "This lets agents operate at the subsystem level instead of blindly editing files."

That is a strong solutions-architect story.

## What The LinkedIn Article Should Do

The article should not try to teach the whole AXIS ontology. It should make one useful argument:

> AI coding agents need maps, not just prompts.

Then introduce AXIS and CodeMaps as a practical answer.

Recommended article structure:

1. The problem: agents can code, but codebases are not self-explanatory.
2. The missing layer: architectural metadata.
3. CodeMaps: read the codebase as a tree.
4. Recomposer: identify reusable "organs," not reusable files.
5. AXIS: constrain where generated code belongs.
6. Why this matters for businesses: safer modernization, better reuse, less context loss.
7. What is in the public repo.

Avoid going too deep into Form/Instance/Facet/Bond unless you use them as examples, not as the center.

## What The Public Repo Should Include

Minimum credible public repo:

- `README.md` with the problem statement and pipeline diagram.
- `AXIS-Lite.md` as the default profile.
- `AXIS-Principles.md` as the conceptual overview.
- `AXIS-Specification.md` as the full reference, clearly marked advanced.
- `CodeMaps/` prompts.
- `examples/axis-web-todo/`.
- One `examples/codemaps-output/` folder from a real or toy repo.
- One `examples/recomposer-output/` showing harvest candidates.
- A short `docs/when-not-to-use-axis.md`.

The "when not to use it" doc will increase credibility because it shows judgment.

## Brutally Honest Hiring Signal Assessment

### Positive signals

- You are thinking at the right abstraction level for agentic software work.
- You understand that AI coding needs structure, not just better prompts.
- You have connected architecture, codebase mapping, reuse, and generation.
- You are aware of over-engineering risk and have AXIS Lite as a mitigation.
- The CodeMaps/Recomposer language is practical and differentiated.

### Negative signals if not handled carefully

- The philosophical framing can sound grandiose.
- The full ontology can look like renaming known patterns.
- The docs are long and may feel like a private universe.
- There is not yet enough empirical proof in the materials.
- Business readers may bounce if the first screen is the grid.

### Net

This is worth presenting, but the public artifact should be edited ruthlessly.

For a hiring manager, the useful claim is:

> I can design agent-readable architectures that let AI systems understand, modify, and reuse software more safely.

That is strong.

The weaker claim is:

> I have a universal theory of software architecture.

That invites skepticism before the work gets a fair read.

## Recommended Next Step

Publish the LinkedIn article as a practical field note, not a manifesto.

Article Title:
- "Guiding AI Agents Through Codebases with CodeMaps and an AXIS of Navigation"

Then put the repo online as the deep reference. The article should create curiosity. The repo should prove rigor.


## Attribution

AXIS, formulated by Matthew Quarneri — MENTIC Cognitive Systems. © 2026 MENTIC LLC. Originally published at [mentic.com/AXIS](https://mentic.com/AXIS).

If you found these ideas useful you could [Buy Me a Coffee](https://buymeacoffee.com/mattq4) to show your support.
