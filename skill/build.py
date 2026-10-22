#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# AXIS, formulated by Matthew Quarneri — MENTIC Cognitive Systems. © 2026 MENTIC LLC. https://mentic.com/AXIS
"""Build the AXIS skill from the canonical AXIS documents.

    python build.py            regenerate the assembled references, the agent pages and axis.skill
    python build.py --check    change nothing; exit 1 if anything is out of date

What is written by hand and what is generated:

  axis/SKILL.md                         by hand: the core an agent reads when the skill triggers
  axis/references/mapping.md            by hand: the AXIS repo mapper
  axis/references/generation-units.md   by hand
  axis/scripts/axis.py                  by hand
  axis/assets/axis-map.example.json     by hand
  axis/LICENSE.txt, axis/NOTICE.txt     by hand: Apache 2.0 and the attribution notice
  axis/references/<the rest>            GENERATED here, section by section, from ../AXIS-*.md
  axis/references/codemaps.prompt.md    GENERATED: a byte-for-byte mirror of ../../CodeMaps/codemaps.prompt.md
  llms.txt, llms-full.txt               GENERATED: the same content as plain pages for agents without the skill
  axis.skill                            GENERATED: the installable package (a zip of axis/)

So: to change a definition, a rule or an example, edit the AXIS document it comes from and run this again.
Every section is located by its heading; if a heading is renamed, the build fails and says which.
"""
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.dirname(HERE)                                   # architectures/AXIS
CODEMAPS = os.path.join(os.path.dirname(DOCS), 'CodeMaps')     # architectures/CodeMaps
SKILL = os.path.join(HERE, 'axis')
CHECK = '--check' in sys.argv
changed = []


def read(path):
    with open(path, encoding='utf-8') as handle:
        return handle.read()


def write(path, text, binary=False):
    old = None
    if os.path.exists(path):
        with open(path, 'rb') as handle:
            old = handle.read()
    new = text if binary else text.encode('utf-8')
    if old == new:
        return
    changed.append(os.path.relpath(path, HERE))
    if not CHECK:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as handle:
            handle.write(new)


def headings(lines):
    """(index, level, title) for every markdown heading that is not inside a code fence."""
    found, fenced = [], False
    for i, line in enumerate(lines):
        if line.lstrip().startswith('```'):
            fenced = not fenced
        match = None if fenced else re.match(r'^(#{1,6})\s+(.*\S)\s*$', line)
        if match:
            found.append((i, len(match.group(1)), match.group(2)))
    return found


def section(doc, heading, level=2, rename=None, drop=()):
    """One section of a canonical document, re-levelled so that its own heading is at `level`."""
    lines = read(os.path.join(DOCS, doc)).split('\n')
    marks = headings(lines)
    start = next((m for m in marks if '#' * m[1] + ' ' + m[2] == heading), None)
    if not start:
        sys.exit('build.py: heading not found in %s: %r. Was it renamed?' % (doc, heading))
    end = next((m[0] for m in marks if m[0] > start[0] and m[1] <= start[1]), len(lines))
    body = lines[start[0]:end]
    for unwanted in drop:
        inner = headings(body)
        hit = next((m for m in inner if '#' * m[1] + ' ' + m[2] == unwanted), None)
        if not hit:
            sys.exit('build.py: sub-heading not found in %s: %r' % (doc, unwanted))
        stop = next((m[0] for m in inner if m[0] > hit[0] and m[1] <= hit[1]), len(body))
        body = body[:hit[0]] + body[stop:]
    if '> **Attribution and License**' in body:                 # the document's own footer; the skill carries its own licence
        body = body[:body.index('> **Attribution and License**')]
    shift = level - start[1]
    for i, depth, title in headings(body):
        body[i] = '#' * max(1, min(6, depth + shift)) + ' ' + (rename if rename and i == 0 else title)
    while body and body[-1].strip() in ('', '>', '---', '------------------------------------------------------------------------'):
        body.pop()
    return '\n'.join(body)


def assemble(name, title, intro, parts):
    sources = sorted({p[0] for p in parts})
    body = [section(*p[:2], **(p[2] if len(p) > 2 else {})) for p in parts]
    tops = [m[2] for chunk in body for m in headings(chunk.split('\n')) if m[1] == 2]
    out = ['# ' + title, '',
           '> Assembled by `build.py` from %s. To change it, edit the source document and rebuild.' % ', '.join(sources), '', intro, '']
    if len(tops) >= 4:
        out += ['## Contents', ''] + ['- ' + t for t in tops] + ['']
    write(os.path.join(SKILL, 'references', name), '\n'.join(out) + '\n' + '\n\n'.join(body) + '\n')


# ── the assembled references ─────────────────────────────────────────────────────────────────
D, L, C, S, F = 'AXIS-Design.md', 'AXIS-Lite.md', 'AXIS-Code.md', 'AXIS-Specification.md', 'AXIS-FrontEnd-Web.md'

assemble('components.md', 'The fourteen components',
         'Precise definitions of each part, the familiar term each one corresponds to, and how AXIS relates to patterns you may already use. '
         'Read the entry you need; you rarely need the whole file.', [
             (D, '### AXIS in conventional engineering terms'),
             (D, '## Canonical Meanings'),
             (D, '## Core Mental Shifts'),
             (D, '## Relationship to Existing Patterns', {'drop': ['### Roles, Responsibilities, and Capabilities']}),
             (S, '## 12. Non-Goals', {'rename': 'Non-Goals'}),
         ])

assemble('boundaries.md', 'Boundaries: Managers, Facets, failure and reads',
         'Design decisions that the core rules do not settle on their own: how wide a Manager should be, when to split a Facet, '
         'how failure travels, and how reads work when Actions cannot fetch.', [
             (L, '## Manager, Narrowed'),
             (L, '## When To Create A New Manager'),
             (L, '## Manager Split Heuristics'),
             (L, '## Interfaces Between Managers'),
             (D, '### Manager Boundaries', {'rename': 'Managers Never Call Each Other'}),
             (L, '## Recommended Code Shape'),
             (D, '### Facet Decomposition'),
             (D, '### Capability Overlays'),
             (D, '### Token-Scoped Views'),
             (S, '### Roles, Responsibilities, and Capabilities'),
             (S, '### Failure Patterns'),
             (D, '### Read Path: The Two-Pass Pattern'),
             (D, '### Read Path: Graph Hydration via Links'),
             (D, '### Relational Composition (Bonds & Links)'),
             (L, '### Bonds & Links in AXIS Lite'),
             (D, '### Action Pipelines'),
             (D, '### Effect Batching'),
             (D, '### Event Sourcing'),
         ])

assemble('recipe.md', 'Adding a capability',
         'The order to build in, the shape of each part, and what to test at each layer. Skip the steps the feature does not need: '
         'see "Use the smallest shape" in SKILL.md. The worked test files the recipe mentions are in `tests.md`.', [
             (C, '## Feature Recipe: Adding a New Capability'),
             (C, '## Type Contracts (Language-Agnostic)'),
             (C, '### Test Generation', {'rename': 'What To Test At Each Layer'}),
             (C, '## Folder Structure'),
             (L, '## Credibility Tests'),
         ])

assemble('tests.md', 'Worked test files',
         'One test file per layer, for the user profile editor in `example-spa.md`. Note what the Action tests do not need: no mocks, no DOM, no network.', [
             (C, '## Test File Examples'),
         ])

assemble('mistakes.md', 'Common mistakes and review checklist',
         'Ten wrong-and-right pairs, then a checklist. When reviewing, name the mixture you found and the smallest change that restores the rule. '
         'After reading, run `python scripts/axis.py lint <paths>` on anything claimed to be pure.', [
             (C, '## Common Mistakes Checklist'),
             (S, '### Code Review Checklist'),
             (C, '### Constraints', {'rename': 'Constraints For Agents'}),
         ])

assemble('frontend.md', 'AXIS in the browser',
         'How the fourteen parts map onto front-end code, without forcing a one-to-one mapping onto every DOM node. '
         'For most browser work, keep to the Lite discipline.', [
             (F, '## What AXIS Helps With In The Browser'),
             (F, '## Recommended Front-End Mapping'),
             (F, '## Browser-Specific Guidance'),
             (F, '## Event Flow In A Small SPA'),
             (F, '## About The Static/Dynamic Pairings'),
             (F, '## Recommended Front-End Rules'),
         ])

assemble('example-spa.md', 'Worked example: a user profile editor (browser)',
         'One feature traced through twelve of the fourteen parts in vanilla JavaScript, one file per part. '
         'It is a full-profile example, shown for clarity; it is not the required layout for every codebase.', [
             (C, '## Worked Example: User Profile Editor (Vanilla JS SPA)', {'rename': 'The Example'}),
         ])

assemble('example-server.md', 'Worked example: an extensible web server (Node)',
         'A server where routes and services are registered at runtime. The point to notice: dynamic extension is an ordinary state change, '
         'handled by the same dispatch, Action, delta and commit as a request.', [
             (S, '## 14. Worked Example: Extensible Web Server (Vanilla Node.js)', {'rename': 'The Example'}),
         ])

# ── the CodeMaps prompt, mirrored byte for byte ──────────────────────────────────────────────
with open(os.path.join(CODEMAPS, 'codemaps.prompt.md'), 'rb') as handle:
    write(os.path.join(SKILL, 'references', 'codemaps.prompt.md'), handle.read(), binary=True)

# ── pages for agents that do not have the skill installed ────────────────────────────────────
ABOUT = {
    'recipe.md': 'adding a feature: build order, type contracts, what to test at each layer',
    'tests.md': 'worked test files for Actions, Adapters, commit validation and Impact',
    'mistakes.md': 'ten wrong-and-right pairs and a review checklist',
    'boundaries.md': 'when to split a Manager or a Facet; failure as data; the two-pass read',
    'components.md': 'precise definitions of the fourteen parts; AXIS beside MVC, Redux, CQRS, event sourcing',
    'frontend.md': 'the mapping for browser code',
    'mapping.md': 'the AXIS repo mapper: describe any existing repository in AXIS terms',
    'generation-units.md': 'break a change into small, checkable contracts',
    'example-spa.md': 'a complete browser example, one file per part',
    'example-server.md': 'a complete Node server example with runtime extension',
    'codemaps.prompt.md': 'the CodeMaps navigation prompt, for broad maps of a large repository',
}
core = read(os.path.join(SKILL, 'SKILL.md'))
front, core_body = re.match(r'^---\n(.*?)\n---\n(.*)$', core, re.S).groups()
references = sorted(os.listdir(os.path.join(SKILL, 'references')), key=lambda n: list(ABOUT).index(n) if n in ABOUT else 99)
missing = [n for n in references if n not in ABOUT]
if missing:
    sys.exit('build.py: add a one-line description to ABOUT for: ' + ', '.join(missing))
tokens = lambda text: len(text) // 4
ATTRIBUTION = ('AXIS, formulated by Matthew Quarneri — MENTIC Cognitive Systems. © 2026 MENTIC LLC. Originally published at https://mentic.com/AXIS. '
               'This skill is licensed under Apache 2.0 (axis/LICENSE.txt); the AXIS documents under CC BY 4.0 (../LICENSE.md).\n\n'
               'If you found these ideas useful you could [Buy Me a Coffee](https://buymeacoffee.com/mattq4) to show your support.')

full = ['# AXIS: everything in one file', '',
        '> The AXIS skill as a single page: the core document, then every reference. Prefer llms.txt and fetch only what a task needs.', '',
        ATTRIBUTION, '',
        core_body.strip(), '']
for name in references:
    full += ['', '=' * 100, 'FILE: axis/references/' + name, '=' * 100, '', read(os.path.join(SKILL, 'references', name)).strip(), '']
full_text = '\n'.join(full) + '\n'
write(os.path.join(HERE, 'llms-full.txt'), full_text)

index = ['# AXIS', '',
         '> AXIS (Agentically eXtensible Instruction Structures) is a placement grammar for code: seven concerns, each split into a definition '
         '(Essence) and a live counterpart (Expression), with rules that keep business logic pure, IO at the edge, and state under one owner. '
         'These pages are written for agents. Read the core first; fetch a reference only when the task needs it.', '',
         '## Core', '',
         '- [AXIS core](axis/SKILL.md): the model, the eight rules, where code goes, how to work in an existing repository (about %d tokens)' % tokens(core_body), '',
         '## References', '']
index += ['- [%s](axis/references/%s): %s (about %d tokens)' % (name, name, ABOUT[name], tokens(read(os.path.join(SKILL, 'references', name)))) for name in references]
index += ['', '## Tools', '',
          '- [axis.py](axis/scripts/axis.py): scan a repo for signals, lint claimed-pure code, and validate, render, query and age-check a repo map. Python 3.8+, no dependencies',
          '- [axis-map.example.json](axis/assets/axis-map.example.json): a complete map of a small service, to copy the shape from', '',
          '## Install', '',
          '- [axis.skill](axis.skill): all of the above as an installable Agent Skill',
          '- [llms-full.txt](llms-full.txt): all of the above as one file (about %d tokens)' % tokens(full_text), '',
          '## Optional', '',
          '- [Presenting AXIS](../presentations/Presenting_AXIS_byOpus.html): an interactive introduction for people',
          '- [AXIS-Lite.md](../AXIS-Lite.md), [AXIS-Design.md](../AXIS-Design.md), [AXIS-Code.md](../AXIS-Code.md), '
          '[AXIS-Specification.md](../AXIS-Specification.md), [AXIS-FrontEnd-Web.md](../AXIS-FrontEnd-Web.md), [AXIS-Principles.md](../AXIS-Principles.md): the source documents', '',
          '## License', '', ATTRIBUTION, '']
write(os.path.join(HERE, 'llms.txt'), '\n'.join(index))

# ── the installable package ──────────────────────────────────────────────────────────────────
def packaged(rel):
    parts = rel.split(os.sep)
    return not (parts[0] == 'evals' or '__pycache__' in parts or parts[-1] == '.DS_Store' or rel.endswith('.pyc'))


members = sorted(os.path.relpath(os.path.join(base, f), SKILL) for base, _, files in os.walk(SKILL) for f in files)
members = [m for m in members if packaged(m)]
package = os.path.join(HERE, 'axis.skill')
stamp = lambda: sorted((m, read_bytes(os.path.join(SKILL, m))) for m in members)


def read_bytes(path):
    with open(path, 'rb') as handle:
        return handle.read()


current = None
if os.path.exists(package):
    with zipfile.ZipFile(package) as old:
        current = sorted((n[len('axis/'):].replace('/', os.sep), old.read(n)) for n in old.namelist())
if current != stamp():
    changed.append('axis.skill')
    if not CHECK:
        with zipfile.ZipFile(package, 'w', zipfile.ZIP_DEFLATED) as out:
            for member in members:
                out.write(os.path.join(SKILL, member), 'axis/' + member.replace(os.sep, '/'))

# ── report ───────────────────────────────────────────────────────────────────────────────────
print('%-44s %8s' % ('file', '~tokens'))
print('%-44s %8d   loaded when the skill triggers' % ('axis/SKILL.md', tokens(core_body)))
for name in references:
    print('%-44s %8d' % ('axis/references/' + name, tokens(read(os.path.join(SKILL, 'references', name)))))
print('%-44s %8d   only if fetched whole' % ('llms-full.txt', tokens(full_text)))
print('\n%d files in axis.skill.' % len(members))
if changed:
    print(('Out of date: ' if CHECK else 'Updated: ') + ', '.join(changed))
else:
    print('Everything is up to date.')
sys.exit(1 if CHECK and changed else 0)
