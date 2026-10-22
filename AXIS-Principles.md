# AXIS: Agentically eXtensible Instruction Structures - Principles

*(The Essence--Expression Model for Software Architecture)*

## Purpose

AXIS is a meta-architecture for structuring codified logic.

Rather than prescribing a framework, programming language, or
implementation pattern, AXIS provides a cognitive model for organizing
software according to the way intent becomes behavior and behavior
produces change.

Most successful architectural styles have independently discovered
useful patterns---separation of concerns, composition, dependency
inversion, event-driven workflows, immutable state, explicit boundaries,
and pure business logic. AXIS attempts to explain why these patterns
work by revealing the deeper structural principles they share.

It is therefore not an alternative to Clean Architecture, Domain-Driven
Design, CQRS, Event Sourcing, MVC, React, or similar approaches.
Instead, AXIS provides a vocabulary that describes the common cognitive
structure from which these patterns emerge.

------------------------------------------------------------------------

## Foundational Premise

Software exists to produce change.

Change is not produced directly.

It is produced through behavior.

Behavior emerges from the execution of codified instructions.

Those instructions originate from progressively higher levels of intent.

Architecture therefore should not be organized primarily around
technologies, frameworks, or deployment boundaries.

It should be organized around the progression by which meaning becomes
behavior and behavior becomes change.

AXIS calls this progression the **Cognitive Flow of Change**.

``` text
Values
    ↓
Goals
    ↓
Plans
    ↓
Declaratives
    ↓
Imperatives
    ↓
Instructions
    ↓
Actions
    ↓
Behaviors
    ↓
Change
```

Each layer constrains and gives meaning to the layers beneath it.

The closer a component is to Values, the more it expresses purpose.

The closer it is to Change, the more it expresses execution.

------------------------------------------------------------------------

## The Essence--Expression Principle

Every software system contains two fundamentally different kinds of
structure.

**Essence** defines what something *is*.

It consists of stable definitions, identities, capabilities,
relationships, and rules.

**Expression** defines how those structures manifest at runtime.

It consists of state, execution, interpretation, orchestration, and
interaction.

One of AXIS's central principles is that these concerns should remain
explicitly separated.

Static structures produce dynamic behavior.

Dynamic behavior produces change.

Change becomes new declarative state.

Maintaining these boundaries makes software easier to reason about,
test, compose, observe, and evolve.

------------------------------------------------------------------------

## The AXIS Principles

1.  **Organize around behavior, not technology.**
    -   Structure software according to responsibilities and behavior
        rather than frameworks, transport protocols, persistence
        mechanisms, or implementation details.
2.  **Follow the Cognitive Flow of Change.**
    -   Higher levels of intent progressively refine into executable
        behavior.
3.  **Separate Essence from Expression.**
    -   Separate definitions from execution, identity from state, and
        declarations from realization.
4.  **Treat behavior as the engine of change.**
    -   Behavior is the mechanism by which systems transform state.
5.  **Treat side effects as data until execution.**
    -   Describe change before performing it.
6.  **Treat responsibility as a routing problem.**
    -   Every behavior should have an explicit owner and execution path.
7.  **Prefer composition over inheritance.**
    -   Assemble systems from composable capabilities with explicit
        responsibilities.
8.  **Design explicit boundaries.**
    -   Components should own one responsibility with well-defined
        interfaces.
9.  **Dependencies are supplied, not discovered.**
    -   Components receive collaborators rather than locating them.
10. **Form follows responsibility.**
    -   Architecture should reveal what the system does, not merely how
        it is implemented.

------------------------------------------------------------------------

## The AXIS Model

The complete AXIS specification expresses these principles through
fourteen complementary architectural components.

Those components are not the starting point---they are the natural
decomposition that follows from the principles above.

The documentation is organized into four complementary guides:

-   **AXIS-Specification.md** --- the complete conceptual model.
-   **AXIS-Design.md** --- pragmatic architectural guidance.
-   **AXIS-Code.md** --- implementation patterns and conventions.
-   **AXIS-Lite.md** --- the minimum subset of principles for
    lightweight adoption.
    **AXIS-FrontEnd-Web.md** --- front-end web application patterns.

------------------------------------------------------------------------

## Closing Thought

AXIS does not begin with software components.

It begins with cognition.

It asks how meaning becomes action, then derives software structure from
that progression.

The architectural components are consequences of that model---not the
model itself.


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