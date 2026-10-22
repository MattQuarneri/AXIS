#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# AXIS, formulated by Matthew Quarneri — MENTIC Cognitive Systems. © 2026 MENTIC LLC. https://mentic.com/AXIS
"""axis.py: tools for reading a repository in AXIS terms. Python 3.8+, standard library only.

  scan [root]             per-file signals (IO, DOM, clock, entry points, schemas, ...) and first guesses at roles
  lint <path[:sym,sym]>   flag IO, async, clock and randomness in code that is claimed to be pure
  lint --map              the same, for every role the map records as a pure Action
  validate                check codemaps/axis-map.json
  render                  write codemaps/AXIS-MAP.md from codemaps/axis-map.json
  where <path>            which roles, boundary and findings cover a path
  stale                   mapped files that changed since the map was written, and source files it does not cover

Everything here reads text. It finds the obvious and proves nothing about what it cannot see:
a function that calls a helper that calls fetch() passes the lint. Treat output as leads to confirm.
"""
import argparse
import bisect
import datetime
import json
import os
import re
import subprocess
import sys

ROLES = ['Form', 'Instance', 'Identity', 'Token', 'Facet', 'Intent', 'Bond', 'Link',
         'Action', 'Manager', 'Effect', 'Impact', 'Wrapper', 'Adapter']
AXES = [('Being', 'Form', 'Instance'), ('Identity', 'Identity', 'Token'), ('Meaning', 'Facet', 'Intent'),
        ('Relating', 'Bond', 'Link'), ('Doing', 'Action', 'Manager'), ('Changing', 'Effect', 'Impact'),
        ('Bridging', 'Wrapper', 'Adapter')]
PURITY = ['pure', 'reads-state', 'io', 'mixed']
BEHAVIOUR = ['Action', 'Manager', 'Impact', 'Wrapper', 'Adapter', 'Link']   # roles that run, and so must state their purity
CONFIDENCE = ['high', 'medium', 'low']
DEPTHS = ['scoped', 'standard', 'deep']
RISKS = ['low', 'medium', 'high']
FINDING_KINDS = ['io-in-logic', 'adapter-decides', 'manager-too-broad', 'hidden-state', 'traversal-in-logic',
                 'self-executing-effect', 'policy-in-logic', 'framework-coupling', 'other']
DEFAULT_MAP = os.path.join('codemaps', 'axis-map.json')

# ── signals ──────────────────────────────────────────────────────────────────────────────────
# HARD: any of these inside an Action breaks the purity rule. SOFT: worth a look. HINT: where to look for a role.
SIGNALS = {
    'network': (r"\bfetch\s*\(|\baxios\b|XMLHttpRequest|\brequests\.(get|post|put|patch|delete|request)\b|\bhttpx\.|\burllib\b"
                r"|\bhttp\.(Get|Post|NewRequest|request|get)\b|reqwest::|\bHttpClient\b|\bWebSocket\b|\bnet\.Dial|\bgrpc\b|\bsocket\.(socket|connect)", 0),
    'filesystem': (r"\bfs\.(promises\.)?(read|write|append|unlink|mkdir|rm|rename|stat|exists|create|open)\w*"
                   r"|require\(\s*['\"](node:)?fs['\"]|from\s+['\"](node:)?fs(/promises)?['\"]"
                   r"|\bos\.(remove|rename|mkdir|makedirs|listdir|walk)\b|\bshutil\.|\bioutil\.|\bos\.(Open|Create|ReadFile|WriteFile)\b"
                   r"|std::fs|\bFile\.(read|write|open|new)\b|\bFiles\.(read|write)|(?<![\w.])open\s*\(", 0),
    'database': (r"\b(SELECT\s.+\sFROM|INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM)\b|\.(query|execute|executemany)\s*\("
                 r"|\bprisma\.|\bknex\b|\bsequelize\b|\bmongoose\b|\bsqlite3?\b|\bpsycopg\d?\b|\bsqlalchemy\b"
                 r"|\.(findOne|findMany|findById|findAll|insertOne|updateOne|deleteOne|save|commit|rollback)\s*\("
                 r"|\bsql\.Open\b|\bgorm\.|diesel::|\bEntityManager\b|\bDbContext\b|\bindexedDB\b|\bredis\b", 0),
    'response': (r"\bres(ponse)?\.(status|json|send|end|write|writeHead|redirect|render|setHeader)\s*\(", 0),
    'storage': (r"\blocalStorage\b|\bsessionStorage\b|document\.cookie", 0),
    'dom': (r"\bdocument\.(querySelector|querySelectorAll|getElementById|createElement|body|head|addEventListener)\b|\.innerHTML\b"
            r"|\.appendChild\s*\(|\bwindow\.(location|history|open|alert)\b|\bcustomElements\.define|\bReactDOM\b|(?<![\w.])alert\s*\(", 0),
    'process': (r"\bprocess\.(env|exit|argv|stdout|stdin)\b|\bos\.environ\b|\bos\.Getenv\b|std::env|\bchild_process\b|\bsubprocess\."
                r"|\bexec\.Command\b|\bSystem\.(getenv|exit)\b|\bsys\.(argv|exit|stdin|stdout)\b", 0),
    'messaging': (r"\.(publish|sendMessage|enqueue)\s*\(|\bkafka\b|\bamqp\b|\bsqs\b|\bpubsub\b|\bpostMessage\s*\(|\bnats\b", re.I),
    'email': (r"\bsendMail\b|\bsmtp\w*\b|\bnodemailer\b|\bsendgrid\b|\bmailer\.\w+\s*\(", re.I),
    'clock': (r"\bDate\.now\s*\(|\bnew\s+Date\s*\(\s*\)|\btime\.time\s*\(|\bdatetime\.(now|utcnow|today)\b|\btime\.Now\s*\(|Instant::now"
              r"|SystemTime::now|\bperformance\.now\b|\bsetTimeout\s*\(|\bsetInterval\s*\(|\btime\.sleep\b", 0),
    'random': (r"\bMath\.random\s*\(|\brandom\.(random|randint|choice|shuffle|uniform)\b|\bcrypto\.(randomUUID|getRandomValues|randomBytes)\b"
               r"|\buuid\.uuid[14]\b|\buuidv?4\s*\(|\brand\.(Intn|Int|Float)|rand::", 0),
    'async': (r"\basync\b|\bawait\b|\.then\s*\(|\bnew\s+Promise\b|\bgo\s+func\b|\btokio::|\basyncio\b", 0),
    'logging': (r"\bconsole\.(log|warn|error|info|debug)\b|\blogging\.\w+\s*\(|\blogger\.\w+\s*\(|\blog\.(Print|Fatal|Panic)\w*\b"
                r"|\bprintln!\s*\(|(?<![\w.])print\s*\(", 0),
    'mutation': (r"\bthis\.\w+(\[[^\]]*\])?\s*(=(?!=)|\+=|-=|\+\+|--)|\bself\.\w+\s*(=(?!=)|\+=|-=)|^\s*global\s+\w+|\bwindow\.\w+\s*=(?!=)", re.M),
    'throws': (r"\bthrow\s+(new\s+)?\w+|\braise\s+\w+|\bpanic!?\s*\(", 0),
    'entry': (r"\b(app|router|server|api)\.(get|post|put|patch|delete|use|route|all)\s*\("
              r"|@(Get|Post|Put|Patch|Delete|Controller|RestController|RequestMapping|GetMapping|PostMapping)\b"
              r"|@(app|router|bp)\.(route|get|post|put|delete)\b|\bcreateServer\s*\(|\.listen\s*\(|__name__\s*==\s*['\"]__main__['\"]"
              r"|\bfunc\s+main\s*\(|\bfn\s+main\s*\(|\bargparse\b|\bclick\.(command|group)\b|\bcommander\b|\byargs\b|clap::"
              r"|\baddEventListener\s*\(|\bcustomElements\.define|\bhandler\s*\(\s*(req|event|ctx)\b|\bexport\s+default\s+(async\s+)?function\b"
              r"|\(\s*(req|request)\s*,\s*(res|response)\b", 0),
    'schema': (r"^\s*(export\s+)?(interface|type|enum)\s+\w+|\bz\.object\s*\(|\bJoi\.object\b|\byup\.object\b|@dataclass\b|\(BaseModel\)"
               r"|^\s*(pub\s+)?struct\s+\w+|\bTypedDict\b|\bnew\s+Schema\s*\(|@Entity\b|\bpydantic\b|\bCREATE\s+TABLE\b", re.M),
    'policy': (r"\b(roles?|permissions?|claims?|isAdmin|is_admin|authorize\w*|acl|polic(y|ies)|feature[_-]?flags?|can[A-Z]\w+)\b", 0),
    'auth': (r"\b(jwt|session|bearer|oauth|authorization|api[_-]?key|csrf|cookies?)\b", re.I),
    'relation': (r"\bFOREIGN\s+KEY\b|\bREFERENCES\b|\b(belongs_to|has_many|has_one|hasMany|belongsTo|hasOne)\b"
                 r"|@(ManyToOne|OneToMany|ManyToMany|OneToOne)\b|\brelationship\s*\(|\bJOIN\b|\.populate\s*\(|\binclude\s*:|\b(prefetch|select)_related\b", 0),
    'orchestration': (r"\b(dispatch\w*|orchestrat\w*|coordinator|workflow|saga|transaction|handle(Command|Event|Intent)|useReducer|createStore|EventEmitter)\b", re.I),
    'effect-data': (r"\b(kind|type)\s*:\s*['\"][A-Z][A-Z0-9_]{2,}['\"]|\beffects?\s*:\s*\[", 0),
}
RX = {name: re.compile(pattern, flags) for name, (pattern, flags) in SIGNALS.items()}
IO = ['network', 'response', 'filesystem', 'database', 'storage', 'process', 'messaging', 'email']
HARD = IO + ['dom', 'clock', 'random', 'async']
SOFT = ['logging', 'mutation', 'throws']
RX_FUNCTION = re.compile(r"\bfunction\b|=>|^\s*(async\s+)?def\s+\w+|\bfunc\s+[\w(]|\bfn\s+\w+", re.M)
RX_BRANCH = re.compile(r"\b(if|elif|switch|case|for|while|match|catch|except)\b")
RX_TEST = re.compile(r"(^|/)(tests?|__tests__|specs?|e2e|fixtures?)(/|$)|\.(test|spec)\.\w+$|_test\.\w+$|(^|/)test_\w+\.py$")

EXT = {'.js': 'javascript', '.mjs': 'javascript', '.cjs': 'javascript', '.jsx': 'javascript', '.ts': 'typescript', '.tsx': 'typescript',
       '.py': 'python', '.go': 'go', '.rs': 'rust', '.java': 'java', '.kt': 'kotlin', '.cs': 'csharp', '.rb': 'ruby', '.php': 'php',
       '.swift': 'swift', '.c': 'c', '.h': 'c', '.cpp': 'cpp', '.hpp': 'cpp', '.vue': 'vue', '.svelte': 'svelte'}
HASH_COMMENTS = {'python', 'ruby'}
SKIP_DIRS = {'.git', 'node_modules', 'dist', 'build', 'out', 'vendor', 'target', '__pycache__', '.venv', 'venv', 'coverage',
             '.next', '.nuxt', 'codemaps', '.idea', '.vscode'}


# ── reading source ───────────────────────────────────────────────────────────────────────────
def git(root, *args):
    try:
        done = subprocess.run(['git', '-C', root] + list(args), capture_output=True, text=True, timeout=30)
        return done.stdout if done.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def source_files(root):
    """Source files under root, relative paths. Uses git when it can, so .gitignore is respected."""
    listed = git(root, 'ls-files', '-co', '--exclude-standard')
    if listed is not None:
        paths = [p for p in listed.splitlines() if p]
    else:
        paths = []
        for base, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            paths += [os.path.relpath(os.path.join(base, f), root) for f in files]
    keep = []
    for p in sorted(set(paths)):
        p = p.replace(os.sep, '/')
        if os.path.splitext(p)[1].lower() not in EXT or '.min.' in p or SKIP_DIRS.intersection(p.split('/')[:-1]):
            continue
        full = os.path.join(root, p)
        if os.path.isfile(full) and os.path.getsize(full) < 300_000:
            keep.append(p)
    return keep


def blank(match):
    return re.sub(r"[^\n]", ' ', match.group(0))


def strip_comments(text, language):
    """Blank out comments, keeping line numbers. Approximate: it does not parse string literals."""
    if language in HASH_COMMENTS:
        text = re.sub(r'("""|\'\'\')[\s\S]*?\1', blank, text)
        return re.sub(r"#[^\n]*", blank, text)
    text = re.sub(r"/\*[\s\S]*?\*/", blank, text)
    return re.sub(r"(?<![:\\])//[^\n]*", blank, text)


def read(root, path):
    with open(os.path.join(root, path), encoding='utf-8', errors='replace') as handle:
        return handle.read()


def find_signals(code):
    """{category: [(line, text)]} for every signal found in comment-stripped code."""
    starts = [0] + [m.end() for m in re.finditer(r"\n", code)]
    lines = code.split('\n')
    found = {}
    for name, rx in RX.items():
        for match in rx.finditer(code):
            line = bisect.bisect_right(starts, match.start())
            found.setdefault(name, []).append((line, lines[line - 1].strip()[:110]))
    return found


def extract_symbol(code, name, language):
    """(first line number, body text) of a named function, or None. Brace matching or indentation; heuristic."""
    n = re.escape(name)
    patterns = [r"(?:async\s+)?function\s*\*?\s*%s\s*\(" % n, r"\b(?:const|let|var)\s+%s\s*=" % n, r"^\s*(?:async\s+)?def\s+%s\s*\(" % n,
                r"\bfunc\s+(?:\([^)]*\)\s*)?%s\s*\(" % n, r"\bfn\s+%s\s*[<(]" % n, r"^\s*(?:[\w<>\[\],]+\s+)+%s\s*\([^;]*$" % n,
                r"^\s*(?:async\s+)?%s\s*\([^)]*\)\s*\{" % n, r"\b%s\s*:\s*(?:async\s*)?(?:function\b|\()" % n]
    match = next((m for m in (re.search(p, code, re.M) for p in patterns) if m), None)
    if not match:
        return None
    first = code.count('\n', 0, match.start()) + 1
    if language in HASH_COMMENTS:
        lines = code.split('\n')
        indent = len(lines[first - 1]) - len(lines[first - 1].lstrip())
        end = first
        while end < len(lines) and (not lines[end].strip() or len(lines[end]) - len(lines[end].lstrip()) > indent):
            end += 1
        return first, '\n'.join(lines[first - 1:end])
    brace = code.find('{', match.end() - 1)
    semi = code.find(';', match.end())
    if brace == -1 or (semi != -1 and semi < brace and '=>' in code[match.end():semi]):
        stop = semi if semi != -1 else code.find('\n', match.end())
        return first, code[match.start():stop if stop != -1 else len(code)]
    depth, i = 0, brace
    while i < len(code):
        depth += code[i] == '{'
        depth -= code[i] == '}'
        if depth == 0:
            break
        i += 1
    return first, code[match.start():i + 1]


# ── scan ─────────────────────────────────────────────────────────────────────────────────────
def guess_roles(counts, functions, branching):
    io = sum(counts.get(c, 0) for c in IO)
    impure = io + counts.get('dom', 0) + counts.get('clock', 0) + counts.get('random', 0)
    quiet = impure == 0 and not counts.get('async') and not counts.get('mutation')
    roles = []
    if counts.get('entry'):
        roles += ['Wrapper', 'Adapter']
    if counts.get('schema') and quiet and functions <= counts['schema']:
        roles.append('Form')
    if quiet and functions and 'Form' not in roles:
        roles.append('Action')
    if io:
        roles += ['Impact'] if branching <= 2 * io + 3 else ['Action', 'Impact']
    if counts.get('dom') and 'Wrapper' not in roles:
        roles.append('Wrapper')
    if counts.get('orchestration') and not quiet:
        roles.append('Manager')
    if counts.get('effect-data') and quiet:
        roles.append('Effect')
    purity = 'pure' if quiet else 'mixed' if (impure and branching > 2 * impure + 3) else 'io' if impure else 'reads-state'
    return list(dict.fromkeys(roles)), purity


def cmd_scan(args):
    root = os.path.abspath(args.root)
    files, tests = [], 0
    for path in source_files(root):
        if RX_TEST.search(path) and not args.include_tests:
            tests += 1
            continue
        language = EXT[os.path.splitext(path)[1].lower()]
        code = strip_comments(read(root, path), language)
        found = find_signals(code)
        counts = {name: len(hits) for name, hits in found.items()}
        functions, branching = len(RX_FUNCTION.findall(code)), len(RX_BRANCH.findall(code))
        roles, purity = guess_roles(counts, functions, branching)
        files.append({'path': path, 'language': language, 'lines': code.count('\n') + 1, 'functions': functions, 'branching': branching,
                      'signals': counts, 'guess': roles, 'purityGuess': purity,
                      'hits': {name: [{'line': l, 'text': t} for l, t in hits[:4]] for name, hits in found.items() if name in HARD + SOFT}})
    report = {'meta': {'tool': 'axis.py scan', 'root': root, 'generatedAt': datetime.date.today().isoformat(),
                       'files': len(files), 'testsSkipped': tests, 'note': 'Signals are leads, not verdicts. Confirm in source.'},
              'files': files}
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, 'w') as handle:
            json.dump(report, handle, indent=1)
    if args.json:
        print(json.dumps(report, indent=1))
        return 0

    def io_of(f):
        return sum(f['signals'].get(c, 0) for c in IO)

    def show(title, rows, describe, limit=args.top):
        rows = list(rows)
        if not rows:
            return
        print('\n' + title)
        for f in rows[:limit]:
            print('  %-52s %s' % (f['path'][-52:], describe(f)))
        if len(rows) > limit:
            print('  … and %d more (use --top N or --out FILE for all)' % (len(rows) - limit))

    def cats(f, names):
        return '  '.join('%s×%d' % (c, f['signals'][c]) for c in names if f['signals'].get(c))

    print('AXIS scan · %s · %d source files, %d lines%s' % (root, len(files), sum(f['lines'] for f in files),
                                                            ' · %d test files skipped' % tests if tests else ''))
    print('Signals are leads, not verdicts. Confirm in source before recording a role.')
    by = lambda key: lambda f: -key(f)
    show('Edges · entry points (look for Wrapper, Adapter)', sorted((f for f in files if f['signals'].get('entry')), key=by(lambda f: f['signals']['entry'])),
         lambda f: cats(f, ['entry'] + IO))
    show('IO sites (look for Impact)', sorted((f for f in files if io_of(f) and f['purityGuess'] != 'mixed'), key=by(io_of)), lambda f: cats(f, IO))
    show('Logic and IO together (likely mixed: Action + Impact, a finding)', sorted((f for f in files if f['purityGuess'] == 'mixed'),
         key=lambda f: (-min(1, io_of(f)), -f['branching'] * max(1, io_of(f)))), lambda f: 'branches×%d  %s' % (f['branching'], cats(f, HARD)))
    show('Pure candidates (look for Action)', sorted((f for f in files if 'Action' in f['guess'] and f['purityGuess'] == 'pure'), key=by(lambda f: f['branching'])),
         lambda f: 'functions×%d  branches×%d' % (f['functions'], f['branching']))
    show('Declarations (look for Form)', sorted((f for f in files if f['signals'].get('schema')), key=by(lambda f: f['signals']['schema'])), lambda f: cats(f, ['schema']), 10)
    show('Policy and auth mentions (look for Facet, Token)', sorted((f for f in files if f['signals'].get('policy', 0) + f['signals'].get('auth', 0) >= 3),
         key=by(lambda f: f['signals'].get('policy', 0) + f['signals'].get('auth', 0))), lambda f: cats(f, ['policy', 'auth']), 8)
    show('Relationships (look for Bond, Link)', sorted((f for f in files if f['signals'].get('relation')), key=by(lambda f: f['signals']['relation'])), lambda f: cats(f, ['relation']), 8)
    show('Orchestration (look for Manager: each state-owning one is a boundary)', sorted((f for f in files if f['signals'].get('orchestration')),
         key=by(lambda f: f['signals']['orchestration'])), lambda f: cats(f, ['orchestration', 'mutation', 'async']), 8)
    folders = {}
    for f in files:
        d = folders.setdefault(os.path.dirname(f['path']) or '.', {'files': 0, 'pure': 0, 'io': 0, 'mixed': 0, 'edge': 0})
        d['files'] += 1
        d['pure'] += f['purityGuess'] == 'pure'
        d['io'] += f['purityGuess'] == 'io'
        d['mixed'] += f['purityGuess'] == 'mixed'
        d['edge'] += bool(f['signals'].get('entry'))
    print('\nBy directory (a first sketch of the placement table)')
    for name, d in sorted(folders.items(), key=lambda kv: -kv[1]['files'])[:args.top + 5]:
        print('  %-44s %3d files · pure %d · io %d · mixed %d · edge %d' % (name[-44:], d['files'], d['pure'], d['io'], d['mixed'], d['edge']))
    if args.out:
        print('\nFull detail written to ' + args.out)
    return 0


# ── lint ─────────────────────────────────────────────────────────────────────────────────────
def lint_file(root, path, symbols, strict):
    language = EXT.get(os.path.splitext(path)[1].lower(), 'javascript')
    code = strip_comments(read(root, path), language)
    regions, notes = [], []
    for name in symbols or []:
        got = extract_symbol(code, name, language)
        if got:
            regions.append((name, got[0], got[1]))
        else:
            notes.append('%s: could not find "%s"; checked the whole file instead' % (path, name))
    if not regions:
        regions = [(None, 1, code)]
    problems = []
    for name, first, body in regions:
        for category, hits in find_signals(body).items():
            if category in HARD or (strict and category in SOFT):
                problems += [(path, first + line - 1, category, name, text) for line, text in hits]
            elif category in SOFT:
                notes += ['%s:%d  (%s) %s' % (path, first + line - 1, category, text) for line, text in hits[:2]]
    return problems, notes


def cmd_lint(args):
    root = os.path.abspath(args.root)
    targets = []
    if args.map:
        data = load_map(args.map_file)
        for role in data.get('roles', []):
            if role.get('primaryAxisRole') == 'Action' and role.get('purity') == 'pure':
                targets += [(p, role.get('symbols') or []) for p in role.get('paths', [])]
        if not targets:
            print('The map records no role as a pure Action; nothing to check.')
            return 0
    for spec in args.paths:
        path, _, names = spec.partition(':')
        targets.append((path, [n for n in names.split(',') if n]))
    if not targets:
        print('Nothing to lint. Give paths (file, dir, or file:symbol,symbol) or use --map.')
        return 2
    files = []
    for path, names in targets:
        full = os.path.join(root, path)
        if os.path.isdir(full):
            files += [(os.path.join(path, p).replace(os.sep, '/'), names) for p in source_files(full)]
        elif os.path.isfile(full):
            files.append((path, names))
        else:
            print('skipped (not found): ' + path)
    problems, notes = [], []
    for path, names in files:
        found, extra = lint_file(root, path, names, args.strict)
        problems += found
        notes += extra
    for path, line, category, name, text in sorted(problems):
        print('%s:%d  [%s]%s  %s' % (path, line, category, ' in ' + name if name else '', text))
    if notes and not args.quiet:
        print('\nWorth a look (not counted; use --strict to count them):')
        for note in notes[:20]:
            print('  ' + note)
    print('\n%d file%s checked · %d purity problem%s.' % (len(files), '' if len(files) == 1 else 's', len(problems), '' if len(problems) == 1 else 's'))
    print('This reads text. It cannot see IO hidden behind a helper call, so a clean result is a good sign and not a proof.')
    return 1 if problems else 0


# ── the map ──────────────────────────────────────────────────────────────────────────────────
def load_map(path):
    try:
        with open(path) as handle:
            return json.load(handle)
    except FileNotFoundError:
        sys.exit('No map at %s. See references/mapping.md to make one.' % path)
    except json.JSONDecodeError as err:
        sys.exit('%s is not valid JSON: %s' % (path, err))


def repo_root(map_file):
    """The repository a map describes: the parent of its codemaps/ folder."""
    return os.path.dirname(os.path.dirname(os.path.abspath(map_file))) or '.'


def check_map(data, root, check_paths=True):
    errors, warnings = [], []
    err, warn = errors.append, warnings.append
    if not isinstance(data, dict):
        return ['the map must be a JSON object with "meta" and "roles"'], []
    meta = data.get('meta') or {}
    if meta.get('axisMapVersion') != 1:
        err('meta.axisMapVersion must be 1')
    if meta.get('depth') not in DEPTHS:
        err('meta.depth must be one of ' + ', '.join(DEPTHS))
    for field in ('repo', 'generatedAt'):
        if not meta.get(field):
            err('meta.%s is required' % field)
    if not meta.get('commit'):
        warn('meta.commit is empty, so "stale" cannot use git to tell what changed')
    if not data.get('summary'):
        warn('summary is empty: say in two to four sentences what the system is and how it is organised natively')

    def exists(path):
        return not check_paths or os.path.exists(os.path.join(root, path))

    boundaries = set()
    for i, b in enumerate(data.get('boundaries') or []):
        where = 'boundaries[%d]%s' % (i, ' (%s)' % b.get('id') if b.get('id') else '')
        if not b.get('id') or not b.get('name'):
            err(where + ': id and name are required')
        if b.get('id') in boundaries:
            err(where + ': duplicate id')
        boundaries.add(b.get('id'))
        if not isinstance(b.get('ownedState'), list):
            err(where + ': ownedState must be a list (use [] if it owns none, and ask whether it is then a boundary)')
        for p in b.get('paths') or []:
            if not exists(p):
                err('%s: path does not exist: %s' % (where, p))

    roles = data.get('roles')
    if not isinstance(roles, list) or not roles:
        err('roles must be a non-empty list')
        roles = []
    ids = set()
    for i, r in enumerate(roles):
        where = 'roles[%d]%s' % (i, ' (%s)' % r.get('id') if r.get('id') else '')
        if not r.get('id') or r.get('id') in ids:
            err(where + ': id is required and must be unique')
        ids.add(r.get('id'))
        if not r.get('nativeName'):
            err(where + ': nativeName is required (what this repo calls it)')
        primary, secondary = r.get('primaryAxisRole'), r.get('secondaryAxisRoles') or []
        if primary not in ROLES:
            err('%s: primaryAxisRole must be one of the fourteen, got %r' % (where, primary))
        for s in secondary:
            if s not in ROLES or s == primary:
                err('%s: secondaryAxisRoles has an invalid or repeated role: %r' % (where, s))
        if r.get('purity') not in PURITY and (primary in BEHAVIOUR or r.get('purity') is not None):
            err('%s: purity must be one of %s (required for %s)' % (where, ', '.join(PURITY), ', '.join(BEHAVIOUR)))
        if r.get('confidence') not in CONFIDENCE:
            err('%s: confidence must be one of %s' % (where, ', '.join(CONFIDENCE)))
        if not r.get('evidence'):
            err(where + ': evidence is required. A role with no evidence is a guess from the name')
        if not r.get('paths'):
            err(where + ': paths is required')
        for p in r.get('paths') or []:
            if not exists(p):
                err('%s: path does not exist: %s' % (where, p))
        if r.get('boundary') and r['boundary'] not in boundaries:
            err('%s: boundary %r is not in boundaries[]' % (where, r['boundary']))
        if primary == 'Action' and r.get('purity') in ('io', 'mixed') and 'Impact' not in secondary:
            warn(where + ': an Action that does IO is mixed. Add "Impact" to secondaryAxisRoles and record a finding')
        if primary in ('Impact', 'Wrapper') and r.get('purity') == 'pure':
            warn('%s: a pure %s is unusual. Check the role' % (where, primary))
        if primary == 'Manager' and not r.get('boundary'):
            warn(where + ': a Manager should name the boundary it coordinates')

    for i, flow in enumerate(data.get('flows') or []):
        where = 'flows[%d]%s' % (i, ' (%s)' % flow.get('name') if flow.get('name') else '')
        if not flow.get('name') or not flow.get('trigger') or not flow.get('steps'):
            err(where + ': name, trigger and steps are required')
        for step in flow.get('steps') or []:
            if step.get('role') not in ROLES:
                err('%s: step role must be one of the fourteen, got %r' % (where, step.get('role')))
            if step.get('ref') and step['ref'] not in ids:
                err('%s: step ref %r is not a role id' % (where, step['ref']))
            if not step.get('does'):
                err(where + ': every step needs "does"')

    for i, finding in enumerate(data.get('findings') or []):
        where = 'findings[%d]' % i
        if finding.get('kind') not in FINDING_KINDS:
            err('%s: kind must be one of %s' % (where, ', '.join(FINDING_KINDS)))
        if finding.get('risk') not in RISKS:
            err('%s: risk must be low, medium or high' % where)
        for field in ('paths', 'evidence', 'separation'):
            if not finding.get(field):
                err('%s: %s is required' % (where, field))
        for p in finding.get('paths') or []:
            if not exists(p):
                err('%s: path does not exist: %s' % (where, p))

    placement = data.get('placement') or {}
    for role, homes in placement.items():
        if role not in ROLES:
            err('placement: %r is not one of the fourteen roles' % role)
        for p in homes or []:
            if not exists(p):
                err('placement.%s: path does not exist: %s' % (role, p))
    missing = [r for r in ROLES if r not in placement]
    if missing:
        warn('placement says nothing about: %s. Use null for a role this repo does not have' % ', '.join(missing))
    if not data.get('rules'):
        warn('rules is empty: an agent changing this repo gets no house rules')
    if roles and not data.get('flows'):
        warn('flows is empty: trace at least the flow an agent is most likely to extend')
    return errors, warnings


def cmd_validate(args):
    data = load_map(args.map_file)
    errors, warnings = check_map(data, args.root or repo_root(args.map_file), not args.no_paths)
    for message in errors:
        print('error    ' + message)
    for message in warnings:
        print('warning  ' + message)
    roles = data.get('roles') or [] if isinstance(data, dict) else []
    print('%s: %d roles · %d errors · %d warnings' % (args.map_file, len(roles), len(errors), len(warnings)))
    return 1 if errors else 0


def cell(text):
    return str(text).replace('|', '\\|').replace('\n', ' ')


def cmd_render(args):
    data = load_map(args.map_file)
    errors, _ = check_map(data, args.root or repo_root(args.map_file), not args.no_paths)
    if errors:
        print('The map has %d error%s. Run "validate", fix them, then render.' % (len(errors), '' if len(errors) == 1 else 's'))
        return 1
    meta, roles = data['meta'], data['roles']
    by_role = {name: [r for r in roles if r['primaryAxisRole'] == name] for name in ROLES}
    also = {name: [r for r in roles if name in (r.get('secondaryAxisRoles') or [])] for name in ROLES}
    placement = data.get('placement') or {}
    code = lambda items: ', '.join('`%s`' % i for i in items)
    out = ['# AXIS map: %s' % meta['repo'], '',
           '> Rendered from `axis-map.json` by `axis.py render`. Do not edit this file; change the JSON and render again.',
           '> Depth: %s%s · written %s%s.' % (meta['depth'], ' · scope: ' + ', '.join(meta['scope']) if meta.get('scope') else '',
                                              meta['generatedAt'], ' at commit `%s`' % str(meta['commit'])[:10] if meta.get('commit') else ''),
           '> This repository is described in AXIS terms as a reading aid. It is not required to use AXIS names.', '']
    if data.get('summary'):
        out += [data['summary'], '']

    out += ['## Where things go in this repo', '',
            'Put new code where its role already lives. A role marked *absent* has no home here; check the rules below before creating one.', '',
            '| Axis | Role | New code goes in | Present as |', '|---|---|---|---|']
    for axis, essence, expression in AXES:
        for name in (essence, expression):
            homes = placement.get(name)
            mine, mixed_in = by_role[name], also[name]
            present = ', '.join(cell(r['nativeName']) for r in mine[:4]) + (' +%d more' % (len(mine) - 4) if len(mine) > 4 else '')
            if mixed_in:
                present += ('; ' if present else '') + 'mixed into ' + ', '.join(cell(r['nativeName']) for r in mixed_in[:3])
            out.append('| %s | **%s** | %s | %s |' % (axis, name, code(homes) if homes else '*absent*' if not mine and not mixed_in else '*no single home*', present or '*absent*'))
    out.append('')

    if data.get('boundaries'):
        out += ['## Boundaries: who owns which state', '', 'Only a boundary\'s own coordinator commits its state. Cross a boundary through its accepted requests, never by reaching into its store.', '',
                '| Boundary | Native name | Lives in | Owns | Accepts | Emits |', '|---|---|---|---|---|---|']
        for b in data['boundaries']:
            out.append('| **%s** | %s | %s | %s | %s | %s |' % (cell(b['name']), cell(b.get('nativeName', '')), code(b.get('paths') or []),
                       cell('; '.join(b.get('ownedState') or []) or 'nothing'), cell('; '.join(b.get('acceptedIntents') or [])), cell('; '.join(b.get('emittedEffects') or []))))
        out.append('')

    touches = [r for r in roles if r.get('purity') in ('io', 'mixed')]
    if touches:
        out += ['## Where IO happens', '', 'Every place the map found that touches the outside world. New IO belongs beside these, not inside logic.', '']
        for r in touches:
            label = r['primaryAxisRole'] + (' + ' + ' + '.join(r['secondaryAxisRoles']) if r.get('secondaryAxisRoles') else '')
            out.append('- %s%s (%s): %s' % ('**mixed** · ' if r['purity'] == 'mixed' else '', code(r['paths']), label, cell('; '.join(r.get('sideEffects') or []) or r['nativeName'])))
        out.append('')

    pure = [r for r in roles if r.get('purity') == 'pure' and r['primaryAxisRole'] == 'Action']
    if pure:
        out += ['## Pure core', '', 'Logic that takes inputs and returns results. Keep it that way: no IO, no clock, no shared state.', '']
        out += ['- %s: %s%s' % (code(r['paths']), cell(r['nativeName']), ' (%s)' % ', '.join(r['symbols']) if r.get('symbols') else '') for r in pure]
        out.append('')

    if data.get('flows'):
        index = {r['id']: r for r in roles}
        out += ['## Flows', '']
        for flow in data['flows']:
            out += ['### %s' % flow['name'], '', 'Trigger: %s' % flow['trigger'], '']
            for n, step in enumerate(flow['steps'], 1):
                ref = index.get(step.get('ref'))
                where = code(ref['paths'][:1]) if ref else code([step['where']]) if step.get('where') else ''
                out.append('%d. **%s**%s: %s' % (n, step['role'], ' · ' + where if where else '', step['does']))
            out.append('')

    if data.get('findings'):
        order = {'high': 0, 'medium': 1, 'low': 2}
        out += ['## Mixed and risky spots', '', 'Named mixtures, with the smallest separation that would restore the rule. Do not widen a change to fix these unless asked.', '',
                '| Risk | Kind | Where | Evidence | Smallest separation |', '|---|---|---|---|---|']
        for f in sorted(data['findings'], key=lambda f: order.get(f['risk'], 3)):
            out.append('| %s | %s | %s | %s | %s |' % (f['risk'], f['kind'], code(f['paths']), cell(f['evidence']), cell(f['separation'])))
        out.append('')

    if data.get('rules'):
        out += ['## House rules for changing this repo', ''] + ['%d. %s' % (n, rule) for n, rule in enumerate(data['rules'], 1)] + ['']
    if data.get('unmapped'):
        out += ['## Not mapped', ''] + ['- %s' % cell(item) for item in data['unmapped']] + ['']
    out += ['## Query and upkeep', '',
            '- `axis.py where <path>`: the roles, boundary and findings that cover a file.',
            '- `axis.py stale`: mapped files changed since this was written, and source files it does not cover.',
            '- After changing code, update the affected entries in `axis-map.json`, then `axis.py validate` and `axis.py render`.', '']
    target = args.out or os.path.join(os.path.dirname(os.path.abspath(args.map_file)), 'AXIS-MAP.md')
    with open(target, 'w') as handle:
        handle.write('\n'.join(out))
    print('wrote %s (%d lines)' % (target, len(out)))
    return 0


def covers(mapped, path):
    mapped, path = mapped.rstrip('/'), path.rstrip('/')
    return path == mapped or path.startswith(mapped + '/') or mapped.startswith(path + '/')


def cmd_where(args):
    data = load_map(args.map_file)
    root = args.root or repo_root(args.map_file)
    path = os.path.relpath(os.path.abspath(args.path), os.path.abspath(root)).replace(os.sep, '/') if os.path.exists(args.path) else args.path
    hits = [r for r in data.get('roles', []) if any(covers(p, path) for p in r.get('paths', []))]
    print(path)
    if not hits:
        print('  not covered by any role entry')
    for r in hits:
        label = r['primaryAxisRole'] + (' + ' + ' + '.join(r['secondaryAxisRoles']) if r.get('secondaryAxisRoles') else '')
        print('  %-28s %s · %s · confidence %s%s' % (label, r['nativeName'], r.get('purity'), r.get('confidence'), ' · boundary ' + r['boundary'] if r.get('boundary') else ''))
        for note in (r.get('boundaryNotes') or [])[:3]:
            print('      note: ' + note)
    homes = [role for role, places in (data.get('placement') or {}).items() if places and any(covers(p, path) for p in places)]
    if homes:
        print('  this location is the home for new: ' + ', '.join(homes))
    for b in data.get('boundaries') or []:
        if any(covers(p, path) for p in b.get('paths') or []):
            print('  inside boundary "%s", which owns: %s' % (b['name'], '; '.join(b.get('ownedState') or []) or 'nothing'))
    for f in data.get('findings') or []:
        if any(covers(p, path) for p in f.get('paths', [])):
            print('  finding (%s, %s): %s' % (f['kind'], f['risk'], f['evidence']))
    return 0


def cmd_stale(args):
    data = load_map(args.map_file)
    root = os.path.abspath(args.root or repo_root(args.map_file))
    meta = data.get('meta') or {}
    mapped = [p for r in data.get('roles', []) for p in r.get('paths', [])]
    changed, how = None, ''
    if meta.get('commit'):
        diff = git(root, 'diff', '--name-only', str(meta['commit']), 'HEAD')
        dirty = git(root, 'status', '--porcelain')
        if diff is not None:
            changed = set(diff.splitlines()) | {line[3:].split(' -> ')[-1] for line in (dirty or '').splitlines() if line.strip()}
            how = 'git, since commit %s' % str(meta['commit'])[:10]
    if changed is None:
        stamp = os.path.getmtime(args.map_file)
        changed = {p for p in source_files(root) if os.path.getmtime(os.path.join(root, p)) > stamp}
        how = 'file times, since the map file was last written'
    touched = sorted(p for p in changed if any(covers(m, p) for m in mapped))
    known = mapped + [p for places in (data.get('placement') or {}).values() for p in places or []] + [str(u).split(' ')[0] for u in data.get('unmapped') or []]
    scope = meta.get('scope') or ['']
    uncovered = sorted(p for p in source_files(root) if any(p.startswith(s.rstrip('/') + '/') or not s for s in scope)
                       and not RX_TEST.search(p) and not any(covers(k, p) for k in known))
    print('Compared using %s.' % how)
    print('\nMapped files that changed (%d): re-check their entries' % len(touched))
    for p in touched[:40]:
        print('  ' + p)
    print('\nSource files the map does not cover (%d)' % len(uncovered))
    for p in uncovered[:40]:
        print('  ' + p)
    if not touched and not uncovered:
        print('\nThe map is current.')
    return 0


def main():
    parser = argparse.ArgumentParser(prog='axis.py', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command')

    p = sub.add_parser('scan', help='signals per source file and first guesses at roles')
    p.add_argument('root', nargs='?', default='.')
    p.add_argument('--out', help='also write the full result as JSON to this file')
    p.add_argument('--json', action='store_true', help='print JSON instead of the summary')
    p.add_argument('--top', type=int, default=12, help='rows per section in the summary (default 12)')
    p.add_argument('--include-tests', action='store_true')
    p.set_defaults(run=cmd_scan)

    p = sub.add_parser('lint', help='flag IO, async, clock and randomness in code claimed to be pure')
    p.add_argument('paths', nargs='*', help='file, directory, or file:symbol,symbol')
    p.add_argument('--map', action='store_true', help='check every role the map records as a pure Action')
    p.add_argument('--strict', action='store_true', help='also count logging, mutation of this/self and thrown exceptions')
    p.add_argument('--quiet', action='store_true')
    p.add_argument('--root', default='.')
    p.set_defaults(run=cmd_lint)

    for name, run, text in (('validate', cmd_validate, 'check the map'), ('render', cmd_render, 'write AXIS-MAP.md from the map'),
                            ('where', cmd_where, 'what covers a path'), ('stale', cmd_stale, 'what changed since the map was written')):
        p = sub.add_parser(name, help=text)
        if name == 'where':
            p.add_argument('path')
        if name == 'render':
            p.add_argument('--out', help='where to write the markdown (default: beside the map, as AXIS-MAP.md)')
        if name in ('validate', 'render'):
            p.add_argument('--no-paths', action='store_true', help='do not check that paths exist')
        p.add_argument('--root', help='repository root (default: the parent of the map\'s folder)')
        p.set_defaults(run=run)
    for p in sub.choices.values():
        p.add_argument('--map-file', default=DEFAULT_MAP, help='default: ' + DEFAULT_MAP)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 2
    return args.run(args)


if __name__ == '__main__':
    sys.exit(main())
