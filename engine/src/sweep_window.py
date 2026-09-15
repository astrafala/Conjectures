#!/usr/bin/env python3
"""The sweep for image counts of a sliding-window MAXIMUM over a growing alphabet.

    python3 src/sweep_window.py

See `window` for the argument. Only max and min windows are swept: the median is NOT order-type
invariant (a witness can need a value strictly between two entries of b, and whether an integer
sits there is a fact about the gaps, not about the order type), and those entries are left
refused rather than settled by a formula that does not apply to them.
"""
import collections
import json
import os
import re

import sympy as sp

import closedform as CF
import conjlines
import localentry as LE
import openness
import window

NAME = re.compile(
    r'Number of arrays of (?:the )?(maxima|minima) of '
    r'(two|three|four|five|six) adjacent elements of some length[- ](\d+) 0\.\.n array\.?\s*$',
    re.I)
WORD = {'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6}
STAT = {'maxima': 'max', 'minima': 'min'}

pool = [a for a in open(os.environ.get('ANUMS_FILE', 'deep-check/window.txt')).read().split()
        if a.startswith('A')]
roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
roster |= {r['anum'] for r in json.load(open('rank-map.json'))}
hits, res = [], collections.Counter()
n = window.n
cache = {}

for a in sorted(pool):
    if a in roster:
        res['already on the roster'] += 1; continue
    e = LE.get(a)
    if not e:
        res['name unknown'] += 1; continue
    m = NAME.search(' '.join(e['name'].split()))
    if not m:
        res['name is not a plain windowed max or min'] += 1; continue
    if not openness.status(a)[0]:
        res['not open'] += 1; continue
    cl = [L for L in conjlines.claims(e) if CF.parse_line(L)]
    if not cl:
        res['no readable closed form'] += 1; continue
    stat, w, k = STAT[m.group(1).lower()], WORD[m.group(2).lower()], int(m.group(3))
    if k - w + 1 > 8:
        res['image length over 8: the order-type census is too large'] += 1; continue
    key = (k, w, stat)
    if key not in cache:
        cache[key] = window.census(k, w, stat)
    A = cache[key]
    P = window.polynomial(A)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    bad = [i + off for i, v in enumerate(d) if P.subs(n, i + off) != v]
    if bad:
        # the derived count is exact, so a disagreement is a fact about the entry -- recorded,
        # never installed, and read by hand before it is called anything
        res['derived count disagrees with the published DATA'] += 1
        hits.append({'anum': a, 'FAILS': True, 'k': k, 'w': w, 'stat': stat,
                     'A': A, 'poly': str(P), 'bad': bad[:6], 'line': cl[0]})
        continue
    got = CF.parse_line(cl[0])
    try:
        same = sp.simplify(P - sp.sympify(str(got[0] if isinstance(got, tuple) else got),
                                          locals={'n': n})) == 0
    except Exception:
        same = None
    res['PROVED' if same else 'proved, but the entry states a different polynomial'] += 1
    hits.append({'anum': a, 'k': k, 'w': w, 'stat': stat, 'A': A, 'poly': str(P),
                 'nterms': len(d), 'offset': off, 'agrees': bool(same),
                 'line': ' '.join(cl[0].split())})

json.dump(hits, open(os.environ.get('HITS', 'window_hits.json'), 'w'), indent=1)
json.dump(dict(res), open('window_why.json', 'w'), indent=1, sort_keys=True)
for k_, v in res.most_common():
    print(f'{v:5}  {k_}')
