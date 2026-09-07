#!/usr/bin/env python3
"""Deep check, Phase 6: the checks, themselves audited.

The standing pattern on this project is that when the engine and the independent check
disagreed, the CHECK was wrong. So the checks get checked. Two of these are mechanical and
both have caught real losses before:

  1. **Swallowed exceptions.** An `except` that records nothing turns a bug into a silent
     refusal. That has cost this project results five separate times --- `transfer7` refused
     for a TypeError in the caller, a table sweep reporting "model does not match" for an
     AttributeError in 62 of 71 engines. Every `except` in every engine and sweep is listed
     with whether anything is recorded before control moves on.

  2. **Regexes over entry text outside the parser.** Building a candidate list with a regex
     written fresh at a call site, rather than with the parser that decides the candidate,
     has narrowed a pool at least twice --- most sharply when a fixed g.f. parser was paired
     with a hand-written pool regex and the pool came out at 49 instead of 130. Every module
     that matches against entry text without going through the canonical parser is listed.

Neither list is a defect list by itself. A bare `except Exception: continue` around a
best-effort probe is fine; the same line where a result should have been recorded is not.
The point is that they are visible.
"""
import os
import re
import sys

SRC = os.path.dirname(os.path.abspath(__file__))
RECORDS = re.compile(r"res\[|note\(|print\(|append\(|defect|raise|log|return None|"
                     r"skip\(|state\[")
ENTRYTEXT = re.compile(r"e\['comment'\]|e\['formula'\]|\['data'\]|LE\.get\(")
PARSERS = {'ratrec.py', 'openness.py', 'localentry.py', 'namecanon.py', 'uniform.py',
           'chunks.py', 'dc_phase3.py', 'dc_phase7.py', 'freshcheck.py', 'dc_phase6.py'}


def live_path():
    """the modules a sweep actually loads, found by following the imports

    Reporting every silent `except` in seven hundred one-off scripts buries the handful that
    can still cost a result today. Only the modules on the path a sweep takes can turn a bug
    into a silent refusal now; the rest are history.
    """
    seen, stack = set(), ['sweep_shard', 'uniform', 'sweep_ordwhole', 'build_new']
    while stack:
        m = stack.pop()
        if m in seen:
            continue
        f = os.path.join(SRC, m + '.py')
        if not os.path.exists(f):
            continue
        seen.add(m)
        txt = open(f, errors='ignore').read()
        for name in re.findall(r'^\s*import\s+([a-zA-Z_][\w]*)', txt, re.M):
            stack.append(name)
        for name in re.findall(r"importlib\.import_module\(['\"]([\w]+)", txt):
            stack.append(name)
        for name in re.findall(r"^ENG = \[([^\]]*)\]", txt, re.M):
            stack += re.findall(r"'([\w]+)'", name)
    return seen


def main():
    live = live_path()
    silent, loud, files = [], 0, 0
    for fn in sorted(os.listdir(SRC)):
        if not fn.endswith('.py'):
            continue
        files += 1
        lines = open(os.path.join(SRC, fn), errors='ignore').read().split('\n')
        for i, L in enumerate(lines):
            if not re.match(r'\s*except\b', L):
                continue
            body = '\n'.join(lines[i + 1:i + 4])
            if RECORDS.search(body):
                loud += 1
            else:
                silent.append((fn, i + 1, ' '.join(L.split()),
                               ' '.join(lines[i + 1].split())[:60] if i + 1 < len(lines) else ''))
    print(f'Phase 6: {files} modules')
    print(f'  {loud} exception handlers record something before continuing')
    print(f'  {len(silent)} record nothing -- each is a place a bug becomes a silent refusal')
    onpath = [x for x in silent if x[0][:-3] in live]
    print(f'  {len(live)} modules are on the path a sweep actually takes; '
          f'{len(onpath)} of the silent handlers are among them, and only those can cost a '
          f'result today:')
    for fn, ln, exc, nxt in onpath:
        print(f'    {fn}:{ln}  {exc}  ->  {nxt}')

    stray = []
    for fn in sorted(os.listdir(SRC)):
        if not fn.endswith('.py') or fn in PARSERS:
            continue
        txt = open(os.path.join(SRC, fn), errors='ignore').read()
        if not ENTRYTEXT.search(txt):
            continue
        pats = re.findall(r"re\.(?:compile|search|match|findall|fullmatch)\(\s*r?['\"]([^'\"]{6,})",
                          txt)
        if pats:
            stray.append((fn, len(pats), pats[0][:52]))
    print(f'\n  {len(stray)} modules match their own patterns against entry text rather than '
          f'going through the canonical parser:')
    for fn, n, p in sorted(stray, key=lambda x: -x[1])[:15]:
        print(f'    {n:3d} patterns  {fn:28s} e.g. {p}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
