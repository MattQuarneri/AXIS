# AXIS: Agentically eXtensible Instruction Structures
### *The Essence–Expression Meta-Architectural Model for Software, Systems, and Agents*

**Author:** Matthew Quarneri ([matt@mentic.com](mailto:matt@mentic.com))  
**Organization:** MENTIC Cognitive Systems  
**Status:** Core Architectural Framework  

---

## Executive Summary: What is AXIS?

**AXIS** (*Agentically eXtensible Instruction Structures*) is a meta-architectural framework and cognitive model for structuring codified logic. Rather than prescribing a rigid language or runtime framework, AXIS organizes software according to the fundamental way **intent becomes behavior and behavior produces change**.

Modern software engineering—particularly in the era of generative AI coding agents—suffers from implicit architecture. AI agents and developers can easily generate syntactically correct code, but struggle to maintain architectural coherence, clear boundaries, and safe state ownership across large codebases. 

AXIS addresses this by organizing all software structures along two orthogonal dimensions:
1. **Immutable Essence** (*Static / Generative / Structure / What something is*)
2. **Projected Expression** (*Dynamic / Runtime / Performance / How it manifests in action*)

By making these boundaries explicit, AXIS provides a shared architectural map that enables humans, AI coding agents, and multi-agent systems to design, generate, navigate, refactor, and safely recompose complex systems without architectural drift.

---

## Core Concepts at a Glance

### 1. The 7-Axis Architectural Grid

AXIS decomposes systems across seven fundamental dimensions of concern. Each dimension is paired into its immutable definition (**Essence**) and its runtime manifestation (**Expression**):

| Axis | Immutable Essence (Structure / Definition) | Projected Expression (Runtime / Performance) | Engineering Role |
| :--- | :--- | :--- | :--- |
| **Being** | **FORM** | **INSTANCE** | State schema, types, defaults, and invariant rules vs. actual runtime state values. |
| **Identity** | **IDENTITY** | **TOKEN** | Permanent semantic identity vs. temporary, scoped credentials and context claims. |
| **Meaning** | **FACET** | **INTENT** | Defined capability surfaces and role perspectives vs. active, parameterized command requests. |
| **Relating** | **BOND** | **LINK** | Static relationship rules and composition contracts vs. dynamic graph traversals and references. |
| **Doing** | **ACTION** | **MANAGER** | Pure, deterministic business logic functions vs. contextual coordinators that route and sequence. |
| **Changing** | **EFFECT** | **IMPACT** | Pure, declared data descriptions of side effects vs. the actual execution of IO (network, disk, queues). |
| **Bridging** | **WRAPPER** | **ADAPTER** | Structural integration boundaries vs. translation layers normalizing external edge noise into clean Intents. |

---

### 2. The Cognitive Flow of Change

All state transitions in an AXIS-governed system follow a deterministic lifecycle:

```
[Raw Event / IO]
       │
       ▼
1. ADAPTER ──────────► Normalizes edge input into a typed INTENT
       │
       ▼
2. TOKEN & FACET ────► Authenticates caller and selects the authorized capability surface
       │
       ▼
3. MANAGER ──────────► Coordinates workflow, binds state, routes to appropriate Action
       │
       ▼
4. ACTION ───────────► Pure calculation: computes next state + declares pure EFFECT data (NO IO)
       │
       ▼
5. COMMIT CHECK ─────► Validates that the new state satisfies FORM and BOND invariants
       │
       ▼
6. IMPACT ───────────► Executes declared EFFECTS against the outside world (database, network, UI)
```

---

### 3. AXIS Lite: The Pragmatic Core

You do not need to implement all 14 components for every feature. AXIS embraces **"Preserve the discipline, not the ceremony."** 

AXIS Lite isolates the 8 non-negotiable rules that deliver the majority of the architecture's benefits:

1. **Actions stay pure:** Transform state and return effect descriptions. No IO.
2. **Effects are data:** Pure data structures describing intent to interact with the world.
3. **Only Impact performs IO:** Disk, network, database, and system calls live strictly in Impact drivers.
4. **Adapters normalize edge inputs:** External protocols, UI events, and raw payloads are normalized into stable Intents.
5. **Mutable state has an explicit owner:** Boundaries and lifecycles of state are strictly declared.
6. **Invariants check at commit:** Invalid transitions are rejected at boundary thresholds.
7. **Cross-boundary interaction is explicit:** No hidden global state or shared memory across boundaries.
8. **Relationships are explicit:** Static rules live in Bonds; dynamic queries live in Links.

---

## Directory Documents: Descriptions & Reading Guide

This directory contains the complete theoretical, architectural, implementation, and domain documentation for AXIS. Below is a guide to each document, its contents, and when you should read it.

### Core Architectural Specifications

| Document | Overview | When to Read |
| :--- | :--- | :--- |
| [**AXIS-Lite.md**](AXIS-Lite.md) | **The Pragmatic Default Profile.** Distills AXIS down to its essential 8 hard rules. Explains Manager decomposition (Composer vs. Conductor), heuristics for splitting services, and minimal folder layouts. | **Read this first!** Use as the daily reference for ordinary application development, microservices, and practical refactoring. |
| [**AXIS-Code.md**](AXIS-Code.md) | **Developer & Agent Implementation Guide.** Provides concrete type contracts (TypeScript/language-agnostic), directory conventions, test patterns (unit, integration, invariant), and step-by-step feature recipes. | Read when writing, testing, or reviewing code. Essential for AI coding agents tasked with generating AXIS-compliant systems. |
| [**AXIS-Design.md**](AXIS-Design.md) | **System Architecture & Component Decomposition.** Bridges the full theoretical specification and the pragmatic Lite profile. Explains boundary placement, Manager sections, and capability modeling. | Read when making system design decisions, modeling new domains, or deciding whether additional structure beyond AXIS Lite is justified. |
| [**AXIS-Specification.md**](AXIS-Specification.md) | **The Canonical Full Specification.** The complete, uncompromised reference manual defining all 7 axes, 14 canonical components, formal architectural invariants, and the full ontology. | Read when you need formal precision, or when designing complex enterprise systems with intricate multi-tenant identities, multi-step sagas, or formal contracts. |
| [**AXIS-Principles.md**](AXIS-Principles.md) | **Foundational Philosophy & Cognitive Model.** Explains the Essence–Expression model and demonstrates why patterns like Clean Architecture, DDD, CQRS, and Hexagonal independently converge on AXIS principles. | Read before deep diving into code to grasp the foundational "why" and mental model behind the architecture. |

---

### Domain-Specific Applications

| Document | Overview | When to Read |
| :--- | :--- | :--- |
| [**AXIS-FrontEnd-Web.md**](AXIS-FrontEnd-Web.md) | **Front-End & Browser Application Guide.** Maps AXIS to browser environments without fighting DOM ergonomics. Covers UI wrappers, event-normalizing adapters, pure UI actions, and view composition via Facets. | Read when building web frontends, SPAs (React, Vue, Web Components), or UI design systems under AXIS discipline. |
| [**AXIS for Orchestrations.md**](AXIS%20for%20Orchestrations.md) | **Multi-Agent Orchestration & Workflow Guide.** Applies the "Composer vs. Conductor" symphony metaphor to human, AI, and mixed-agent systems. Details how intent becomes coordinated work, capability assignment, and verified outcomes. | Read when building agentic workflows, LLM orchestration layers, autonomous agent swarms, or distributed workflow engines. |
| [**AXIS for Organizations.md**](AXIS%20for%20Organizations.md) | **Organizational Architecture & Operating Model.** Maps the 14-component model to human organizations, business processes, roles, decision rights, and governance for mixed human-AI workforces. | Read when designing organizational operating models, department interfaces, delegation structures, or enterprise workflow governance. |

---

### Thought Leadership, Strategy & Context

| Document | Overview | When to Read |
| :--- | :--- | :--- |
| [**AXIS Article.md**](AXIS%20Article.md) | **"AI Coding Agents Need Maps, Not Just Prompts."** Thought-leadership essay explaining the structural crisis in generative coding: why LLMs generate compiling syntax that breaks systems, and how CodeMaps + AXIS provide the missing architectural metadata. | Read to understand the commercial and operational motivation for AXIS, or when communicating the value of AXIS to leadership and engineering teams. |
| [**AXIS feed.md**](AXIS%20feed.md) | **Architectural Critique & Positioning Analysis.** Candid feedback on AXIS's strengths (CodeMaps, Recomposition, AXIS Lite) and risks (over-abstraction, ceremony). Includes guidance on positioning AXIS to frontier AI labs (OpenAI, Anthropic, Google). | Read when pitching AXIS, evaluating architectural trade-offs, or preparing for high-level technical reviews. |
| [**AXIS thoughts.md**](AXIS%20thoughts.md) | **Raw Architectural Insights & Heuristics.** Concentrated working notes detailing the Manager Composer/Conductor split, the orchestra "sections" decomposition heuristic, and Facet decision trees based on Token claims. | Read when facing nuanced questions about when to split a Manager or how to avoid Facet proliferation. |
| [**AXIS-Conversation-Summary-2026-06-29.md**](AXIS-Conversation-Summary-2026-06-29.md) | **Foundations & Evolution Summary.** Notes capturing the milestone conversation where AXIS shifted from an architectural pattern to a universal cognitive model of codified knowledge and software. | Read for historical context and deeper insight into the philosophical genesis of the framework. |

---

### Interactive Presentations & Agent Tooling

| Directory / File | Overview | When to Use |
| :--- | :--- | :--- |
| [**`presentations/`**](presentations/) | **Interactive Visuals & Cheatsheets:**<br>• [`AXIS_quicksheet_bySol.html`](presentations/AXIS_quicksheet_bySol.html) — Printable 1-page quick sheet & reference card.<br>• [`Presenting_AXIS_bySol.html`](presentations/Presenting_AXIS_bySol.html) — Interactive visual walkthrough and guide.<br>• [`Presenting_AXIS_byGemini.html`](presentations/Presenting_AXIS_byGemini.html) & [`Presenting_AXIS_byOpus.html`](presentations/Presenting_AXIS_byOpus.html) — Deep-dive multi-perspective analyses.<br>• [`the_AXIS_arch.html`](presentations/the_AXIS_arch.html) — Architectural diagram and visual breakdown. | Open in any browser for visual onboarding, quick reference, team presentations, or printing physical cheat sheets. |
| [**`skill/`**](skill/) | **Agent Skill & LLM Integration Package:**<br>• [`skill/README.md`](skill/README.md) & [`skill/axis/SKILL.md`](skill/axis/SKILL.md) — Pre-packaged agent skill for Claude Code, Antigravity, and OpenAI agents.<br>• `skill/axis.skill` — Distributable packaged agent skill.<br>• `llms.txt` / `llms-full.txt` — Standardized context files for LLM prompt ingestion.<br>• `build.py` — Generator script for skill packages. | Use when equipping autonomous AI coding assistants with native AXIS execution knowledge and coding guardrails. |

---

## Recommended Reading Paths

Depending on your immediate role and objective, follow one of these curated pathways:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        HOW SHOULD YOU START?                           │
└────────────────────────────────────────────────────────────────────────┘

 [ Pragmatic Developer / AI Coding Agent ]
   1. Read AXIS-Lite.md               (Understand the 8 non-negotiables)
   2. Read AXIS-Code.md               (Folder structure, type contracts, recipes)
   3. Check AXIS_quicksheet_bySol.html (Keep as a quick reference)
   4. (If Browser/UI): Read AXIS-FrontEnd-Web.md

 [ Software Architect / Systems Designer ]
   1. Read AXIS-Principles.md         (The cognitive model & Essence–Expression)
   2. Read AXIS-Design.md             (Boundary decomposition & placement)
   3. Read AXIS-Specification.md      (The complete 14-component grid)
   4. Read AXIS-Code.md               (Implementation verification)

 [ AI Systems & Agent Orchestration Engineer ]
   1. Read AXIS Article.md            (Why agents need architectural maps)
   2. Read AXIS for Orchestrations.md (Composer vs. Conductor for agent swarms)
   3. Read skill/README.md            (Deploying AXIS skills into agent tooling)

 [ Executive, Strategist, or Engineering Leader ]
   1. Read AXIS Article.md            (The business problem & agentic leverage)
   2. Open Presenting_AXIS_bySol.html (Interactive executive overview)
   3. Read AXIS feed.md               (Objective positioning & critique)
   4. Read AXIS for Organizations.md  (Scaling human-AI operating models)
```

---

## Repository Structure

```
/Users/mattq/Projects/MENTIC/Core/architectures/AXIS/
├── ReadMe.md                             ◄ (You are here) Overview & reading guide
├── AXIS-Lite.md                          ◄ Pragmatic default profile & hard rules
├── AXIS-Code.md                          ◄ Implementation, folder layout, & contracts
├── AXIS-Design.md                        ◄ Architectural design & component decomposition
├── AXIS-Specification.md                 ◄ Complete 14-component architectural spec
├── AXIS-Principles.md                    ◄ Epistemological foundations & principles
├── AXIS-FrontEnd-Web.md                  ◄ Browser & front-end UI adaptation
├── AXIS for Orchestrations.md            ◄ Multi-agent workflow & orchestra conductor guide
├── AXIS for Organizations.md             ◄ Organizational operating model & human-AI workflow
├── AXIS Article.md                       ◄ Thought-leadership essay on agentic architecture
├── AXIS feed.md                          ◄ Critical evaluation & positioning assessment
├── AXIS thoughts.md                      ◄ Manager & Facet decomposition heuristics
├── AXIS-Conversation-Summary-2026-06-29.md◄ Retrospective on framework origin
├── LICENSE.md                            ◄ Which license covers what & how to credit AXIS
├── LICENSE-CC-BY-4.0.txt                 ◄ Full CC BY 4.0 text (documents & presentations)
├── NOTICE                                ◄ Attribution notice to keep with copies
├── CITATION.cff                          ◄ Citation metadata
├── presentations/                        ◄ Interactive HTML presentations & sheets
│   ├── AXIS_quicksheet_bySol.html        ◄ 1-page printable cheatsheet
│   ├── Presenting_AXIS_bySol.html        ◄ Interactive visual walkthrough
│   ├── Presenting_AXIS_byGemini.html     ◄ Gemini's comprehensive presentation
│   ├── Presenting_AXIS_byOpus.html       ◄ Opus's comprehensive presentation
│   └── the_AXIS_arch.html                ◄ Visual architecture breakdown
└── skill/                                ◄ Packaged skills & prompts for AI agents
    ├── README.md                         ◄ Skill documentation & usage
    ├── axis/                             ◄ Agent skill source (SKILL.md + references)
    ├── axis.skill                        ◄ Packaged skill archive
    ├── build.py                          ◄ Skill builder utility
    ├── llms.txt                          ◄ Standard agent index
    └── llms-full.txt                     ◄ Consolidated LLM prompt text
```

---

## License & Attribution

AXIS, formulated by Matthew Quarneri — MENTIC Cognitive Systems. © 2026 MENTIC LLC. Originally published at [mentic.com/AXIS](https://mentic.com/AXIS).

If you found these ideas useful you could [Buy Me a Coffee](https://buymeacoffee.com/mattq4) to show your support.

- **Documents and presentations:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)
- **The skill (`skill/`):** [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)

You may share and adapt AXIS, including commercially, if you credit Matthew Quarneri and MENTIC Cognitive Systems, link to [mentic.com/AXIS](https://mentic.com/AXIS), and say what you changed. See [LICENSE.md](LICENSE.md) for the details, [NOTICE](NOTICE) for the notice to keep with copies, and [CITATION.cff](CITATION.cff) for citation metadata.
