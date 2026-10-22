# The AXIS skill

AXIS for agents, in three forms built from one source:

| File | What it is | Who uses it |
|---|---|---|
| `axis/` | An Agent Skill: a short core (`SKILL.md`), references read on demand, and a zero-dependency tool | Agents with skills (Claude Code, Claude apps, the Agent SDK) |
| `axis.skill` | The same folder, packaged for upload or sharing | Anyone installing the skill |
| `llms.txt`, `llms-full.txt` | The same content as plain pages: an index with links, and everything in one file | Any agent that can fetch a URL |

## What is in the skill

```
axis/
  SKILL.md                        the core: the model, eight rules, where code goes, working in an existing repo
  references/
    recipe.md  tests.md           adding a capability; worked test files
    mistakes.md                   ten wrong-and-right pairs; review checklist
    boundaries.md                 Managers, Facets, failure, reads
    components.md                 precise definitions; AXIS beside MVC, Redux, CQRS, event sourcing
    frontend.md                   the browser mapping
    example-spa.md  example-server.md
    mapping.md                    the AXIS repo mapper
    generation-units.md           breaking a change into small contracts
    codemaps.prompt.md            the CodeMaps navigation prompt (verbatim mirror)
  scripts/axis.py                 scan · lint · validate · render · where · stale
  assets/axis-map.example.json    a complete, validated map of a small service
  evals/                          test prompts and fixtures (not packaged)
  LICENSE.txt  NOTICE.txt         Apache 2.0 and the attribution notice, packaged with the skill
```

An agent pays for the name and description always, the core (about 2,600 tokens) when the skill triggers, and a reference only when it opens one. `python build.py` prints the current sizes.

## Install

- **Claude Code, for yourself:** copy the `axis` folder to `~/.claude/skills/axis`.
- **Claude Code, for a project:** copy it to `.claude/skills/axis` in the repository and commit it.
- **Claude apps:** upload `axis.skill` where custom skills are managed.
- **Anything else:** point the agent at `llms.txt`.

## The repo mapper

`references/mapping.md` describes how an agent maps any repository in AXIS terms. It writes `codemaps/axis-map.json` and renders `codemaps/AXIS-MAP.md` from it: where each role lives in that repo, who owns which state, where IO happens, the top flows, the mixed spots, and house rules for changing it. Try the tool on the fixture:

```bash
python axis/scripts/axis.py scan axis/evals/files/orders-service
```

```bash
python axis/scripts/axis.py render --map-file axis/assets/axis-map.example.json --root axis/evals/files/orders-service --out /tmp/AXIS-MAP.md
```

It sits beside the CodeMaps prompt and does not replace it: CodeMaps reads a repo as a tree, the AXIS map reads it by role, and `mapping.md` says how one feeds the other. `../../CodeMaps/ReadMe.md` describes the two stages end to end.

The Stage 2 prompts in `../../CodeMaps/` and its driver, `codemaps.sh`, do not repeat this skill's procedures. They attach `references/mapping.md`, `references/generation-units.md` and `assets/axis-map.example.json`, and they run `scripts/axis.py`. If you rename or move any of those four, update `codemaps.sh`.

## Rebuilding

Most references are assembled, section by section, from the AXIS documents in the parent folder, and `codemaps.prompt.md` is copied byte for byte from `../../CodeMaps/`. After editing any of those:

```bash
python build.py
```

```bash
python build.py --check
```

The second form changes nothing and exits non-zero if the skill is out of date, which makes it usable as a pre-commit or CI check. The files written by hand are `axis/SKILL.md`, `axis/references/mapping.md`, `axis/references/generation-units.md`, `axis/scripts/axis.py` and `axis/assets/axis-map.example.json`.

## Not yet done

- **Evaluation.** `axis/evals/evals.json` holds four test prompts with expected results. They have not been run, so there is no measurement yet of how much the skill changes an agent's output.

## License

AXIS, formulated by Matthew Quarneri — MENTIC Cognitive Systems. © 2026 MENTIC LLC. Originally published at [mentic.com/AXIS](https://mentic.com/AXIS).

If you found these ideas useful you could [Buy Me a Coffee](https://buymeacoffee.com/mattq4) to show your support.

Everything in `skill/` is licensed under the [Apache License 2.0](axis/LICENSE.txt). Redistributions and derivative works must keep [`axis/NOTICE.txt`](axis/NOTICE.txt). The AXIS documents these references are built from are under CC BY 4.0. See [../LICENSE.md](../LICENSE.md).
