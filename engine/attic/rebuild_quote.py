#!/usr/bin/env python3
"""Rewrite every installed paper whose section 1 does not quote the conjecture it proves.

Two defects, both in `conjquote`'s docstring: a word test for "conjecture" ON the line, which a
`Conjectures from X: (Start) ... (End)' block does not carry, so 542 papers printed a
parenthetical placeholder; and the first line with an `a(n) =' on it taken from such a block,
which on 41 papers was a closed form where the theorem below stated the recurrence. Every
builder now delegates to `conjquote`, and this rewrites the papers built before it did.

Only the papers whose quoted line actually CHANGES are rebuilt: asking the question is cheap
and compiling is not.
"""
import importlib
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import conjquote
import localentry as LE

ONLY = set(sys.argv[1:])
ORIG = json.load(open('deep-check/orig-paper-dates.json')) if os.path.exists(
    'deep-check/orig-paper-dates.json') else {}
ENG = {int(k): v for k, v in json.load(open('paper-engines.json')).items()}
BUILDNO = {}
for _n, _v in ENG.items():
    BUILDNO.setdefault(_v['anum'], []).append(_n)
rank = {r['anum']: r for r in json.load(open('rank-map.json'))}
WORD = re.compile(r'onjectur|Empirical', re.I)


def old_line(anum):
    """what the word test on the line would have found -- what the paper printed."""
    e = LE.get(anum)
    for L in e['comment'] + e['formula']:
        if WORD.search(L) and re.search(r'a\(n\)\s*=', L):
            return L
    return None


# `build_new' is a script, not a library: importing it RUNS the builder. Its engine-to-builder
# map is read out of the source instead.
_src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_new.py')).read()
SPECIAL = eval(_src[_src.index('SPECIAL = {') + len('SPECIAL = '):
                    _src.index('}', _src.index('SPECIAL = {')) + 1])


def main():
    hits = [h for h in json.load(open('uniall_hits.json'))
            if not h.get('FAILS') and h.get('coeffs') and h['anum'] in rank]
    if ONLY:
        hits = [h for h in hits if h['engine'] in ONLY]
    todo = []
    for h in hits:
        a = h['anum']
        new = conjquote.line(a, h['coeffs'])
        old = old_line(a)
        if new and (old is None or ' '.join(old.split()) != ' '.join(new.split())):
            todo.append(h)
    print('installed papers whose quoted conjecture changes:', len(todo))
    done, failed = 0, []
    for h in sorted(todo, key=lambda x: x['anum']):
        a, en = h['anum'], h['engine']
        mod = importlib.import_module(SPECIAL.get(en, 'unibuild'))
        mod.DATE = ORIG.get(a, getattr(mod, 'DATE', ''))
        dd = 'build/q%s' % a
        os.makedirs(dd, exist_ok=True)
        try:
            open(dd + '/p.tex', 'w').write(mod.build(h))
        except Exception as exc:
            failed.append('%s(%s)' % (a, type(exc).__name__))
            continue
        for _ in range(2):
            subprocess.run(['pdflatex', '-interaction=nonstopmode', 'p.tex'], cwd=dd,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pdf = dd + '/p.pdf'
        if not (os.path.exists(pdf) and os.path.getsize(pdf) > 50000):
            failed.append(a)
            continue
        for n in BUILDNO.get(a, ()):
            shutil.copyfile(pdf, 'papers-old-numbering/%d-%s.pdf'
                            % (n, 'DISPROOF' if ENG[n].get('disproof') else 'PROOF'))
        shutil.copyfile(pdf, rank[a]['path'])
        done += 1
        if done % 50 == 0:
            print('  rebuilt', done, flush=True)
    print('rebuilt', done, 'failed', len(failed))
    if failed:
        print('  failed:', ' '.join(failed[:20]))


main()
