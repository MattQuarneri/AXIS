# AXIS: Agentically eXtensible Instruction Structures - Lite Spec
(aka The Essence–Expression Model for Software Architecture, Pragmatic Profile)
**Author:** Matthew Quarneri (matt@mentic.com)
**Organization:** MENTIC Cognitive Systems  
**Version:** 2026.05.22  
**Copyright:** © 2026 MENTIC LLC  
**License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — see [LICENSE.md](LICENSE.md)

> Use this document as the pragmatic default profile when applying AXIS to ordinary IT services, internal systems, and application refactors.
> The Specification is the full ideal, Design bridges the ideal and the pragmatic profile, and Code turns both into implementation guidance.
> For the full ontology and worked examples, see `AXIS-Design.md`, `AXIS-Code.md`, and `AXIS-Specification.md`.

---

## Purpose

AXIS Lite keeps the parts of AXIS that reliably improve software quality:

- pure business logic
- explicit side-effect boundaries
- normalized inputs at system edges
- explicit ownership of mutable state
- bounded orchestration

AXIS Lite does **not** require all 14 components for every feature.

**Rule of thumb:** preserve the discipline, not the ceremony.

---

## Hard Rules

These rules are mandatory even in the lite profile:

1. **Actions stay pure.** They transform state and declare effects. They do not perform IO.
2. **Effects are data.** They describe side effects; they do not execute themselves.
3. **Only Impact performs IO.** Network, disk, queues, and external APIs stay out of Actions.
4. **Adapters normalize edge input.** They convert raw events, requests, or UI signals into stable Intents or equivalent command objects.
5. **Mutable state has an owner.** If state is shared, the owning boundary must be explicit.
6. **Invariant checks happen at commit time.** If a boundary accepts state transitions, it must reject invalid ones (validating both Form and Bond invariants).
7. **Cross-boundary interaction is explicit.** No hidden shared mutable state between bounded contexts.
8. **Relationships are explicit.** Static relationship configurations are defined as Bonds, while runtime graph traversals are resolved as Links by the Manager or a link-service, never inside pure Actions.

---

## Optional Pieces

These AXIS components are introduced only when the problem actually needs them:

| Component | Introduce it when... |
|-----------|----------------------|
| **Form** | state shape, defaults, or invariants need to be explicit |
| **Identity** | the same entity must be addressed across requests, stores, or workflows |
| **Token** | claims, scope, expiry, or temporal identity really matter |
| **Facet** | one entity has multiple capability surfaces by role, lifecycle, or context |
| **Bond** | relationship rules, parent-child multiplicities, or cross-entity invariants must be validated on commit |
| **Link** | entities must traverse relationships dynamically or pre-hydrate state graphs for Actions |
| **Manager** | more than one Action must be coordinated across state transitions or workflows |
| **Two-pass reads** | reads must be replayable, audited, retried, or fed through the same effect pipeline |

**Not required by default:**

- the full Adapter -> Intent -> Manager -> Facet -> Action -> Effect -> Impact chain
- one file per AXIS component
- a dedicated folder for every axis in small services

If the lighter shape is clear and does not violate the hard rules, keep it.

### Bonds & Links in AXIS Lite

Bonds and Links prevent relationship logic from bloating Forms (schemas) and Actions (logic).
- **Use a Bond** when one entity owns another (multiplicity/cardinality) or when you must enforce consistency invariants across multiple entities during a commit.
- **Use a Link** to pre-hydrate entity references prior to dispatching to an Action. Instead of making an Action perform an async two-pass read to load related state, let the Manager resolve a Link at composition/request boundaries.

---

## Adoption Profiles

Use the smallest profile that preserves the rules.

| Scenario | Start with |
|----------|------------|
| Pure computation | Action |
| Simple stateless endpoint | Wrapper, Adapter, Action, Effect/Impact if IO is needed |
| CRUD service with owned state | Form, Instance, Action, Manager, Effect/Impact |
| Role-aware or lifecycle-aware domain | Add Facets |
| Complex relational or aggregate domain | Form, Instance, Action, Bond, Link, Manager, Effect/Impact |
| Multi-step async workflow, retries, compensation, replay | Full AXIS or close to it |

**Escalation rule:** add the next AXIS component only when the current shape would otherwise hide IO, blur ownership, or mix unrelated responsibilities.

---

## Manager, Narrowed

The full AXIS documents are right that orchestration needs a home. The risk is that **Manager** becomes a renamed god object.

In AXIS Lite, a Manager is a **boundary-scoped coordinator**, not a general-purpose service class.

The term **Manager** can still work, but only if the code makes the role narrow and inspectable. If "Manager" becomes a vague bucket for orchestration, policy, domain logic, and integration details, rename or split it. In many codebases, `Coordinator`, `Workflow`, or `Runtime` is clearer for the runtime half.

### A Manager may do these things

- receive normalized Intents or commands
- select the right Action or Facet delegate
- coordinate workflow steps
- commit deltas to owned state
- enforce commit-time invariants
- issue or revoke Tokens if that boundary owns auth/session projection
- hand declared Effects to Impact

### A Manager must not do these things

- contain core business calculations that belong in Actions
- perform IO directly
- own unrelated domains in one class or module
- format transport-specific data for Wrappers
- reach into another Manager's state store
- encode permissions inline when a Facet or policy map would do

### Composer and Conductor

The Composer/Conductor distinction is useful, but by itself it is not enough.

It becomes credible only when it is enforced in code structure:

- **Composer** should be setup-only: binding wrappers, registering adapters, wiring facet registries, installing handlers.
- **Conductor** should be runtime-only: dispatch, routing, workflow progression, commit.
- If both roles grow large, split them into separate modules even if they are still presented as one conceptual Manager.

**Practical rule:** do not let "Manager" be the place where leftover logic goes. If logic can be tested without orchestration, it does not belong in the Manager.

---

## When To Create A New Manager

Create a new Manager when one or more of these become true:

1. The code is coordinating a different domain language or business capability.
2. The code owns a different consistency boundary or state store.
3. The workflow can evolve independently of the current one.
4. The deployment boundary or team ownership is different.
5. The existing Manager would need to directly know about another domain's invariants.
6. The dispatch path is branching across unrelated domains rather than related capabilities.

Do **not** create a new Manager just because:

1. the same entity has different roles or permissions; use Facets first.
2. the same workflow gained another step; add or split Workflow logic first.
3. the same state boundary gained more commands; add Actions first.

---

## Manager Split Heuristics

If a Manager shows these symptoms, split it:

- it owns more than one unrelated state store
- it imports Actions from unrelated domains
- it contains routing branches for unrelated business areas
- it needs different release cadence than part of its own logic
- it is accumulating workflow state machines that do not share commit rules
- changes to one capability routinely risk regressions in another unrelated capability

If a Manager shows these symptoms, keep it whole:

- all Actions operate on the same state boundary
- all workflows share the same invariants and commit rules
- capabilities differ mainly by role or lifecycle state
- the "split" would only replace function calls with noisy cross-boundary messages

---

## Interfaces Between Managers

The current AXIS guidance that Managers should not call each other directly is directionally right. The missing piece is a more concrete interface contract.

For AXIS Lite, each Manager boundary should define:

- **owned state**: which Forms, Instances, and Identities it is allowed to commit
- **accepted intents**: the commands or intent kinds it accepts
- **emitted effects/events**: the only outward requests it can make of other boundaries
- **returned outcomes**: acknowledgements, failures, and follow-up intents/events
- **policy scope**: which claims, roles, or token scopes it is allowed to interpret

If those five things are not clear, the boundary is not clear.

---

## Recommended Code Shape

For services that need a Manager, prefer this internal split even if you keep the AXIS name:

- `manager/composer.*` for setup and registrations
- `manager/conductor.*` for dispatch and workflow progression
- `manager/commit.*` for delta application and invariant validation
- `manager/policy.*` for facet or permission selection

This keeps the architecture legible without forcing every concern into a single file.

---

## Credibility Tests

AXIS Lite is helping only if it makes the codebase easier to change.

Use these checks:

1. Can a business rule be unit tested without network or database mocks?
2. Can reviewers quickly tell where IO happens and where it does not?
3. Can a new feature be added without touching unrelated workflows?
4. Can one bounded context change without silently corrupting another?
5. Did adopting AXIS reduce ambiguity more than it increased ceremony?

If the answer to `5` is no, simplify the shape.

---

## Relationship To Full AXIS

AXIS Lite is not a rejection of full AXIS.

It is the default operating profile for most application work:

- start lite
- escalate intentionally
- keep the hard rules
- add ontology only when the system's complexity justifies it

In practice, most resilient systems need the AXIS disciplines more than they need the full AXIS topology.


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