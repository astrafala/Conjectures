#!/usr/bin/env python3
"""`Number of (n+1) X (K+1) 0..m arrays with <a statistic> of every 2 X 2 subblock DIFFERING
from its horizontal and vertical neighbors BY EXACTLY d.'

The same subblock grid as the `colored with' family, and the same statistic vocabulary --- the
order statistics of the four entries and signed sums of them --- but a sharper relation: the
values of neighbouring subblocks must differ by exactly $d$, not merely differ. A subblock's
value needs two consecutive array rows and the vertical relation compares two consecutive
subblock rows, so the state is the pair of consecutive rows, one step appends a row, and an
$(n+1)$-row array is a walk of $n-1$ steps.
"""
import re
from itertools import product

import namecanon
import transfer17
from transfer30 import _colour

NAME = re.compile(
    r'Number of \(\s*n\s*\+\s*(\d+)\s*\)\s*X\s*\(?\s*(\d+)(?:\s*\+\s*(\d+))?\s*\)?\s*'
    r'0\.\.(\d+)\s+arrays\s+with\s+(.*?)\s+of every 2\s*X\s*2 subblock\s+differing from its\s+'
    r'horizontal and vertical neighbors\s+by exactly\s+(one|two|three|\d+)\s*\.?\s*$', re.I)

NUM = {'one': 1, 'two': 2, 'three': 3}


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn)])\s*[xX]\s*(?=[\dn(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = NAME.search(nm)
    if not m:
        return None
    d = int(m.group(1))
    W = int(m.group(2)) + (int(m.group(3)) if m.group(3) else 0)
    alpha = int(m.group(4))
    col = _colour(m.group(5))
    if col is None or col[0] != 'lin' or d != 1 or W < 2 or alpha < 1:
        return None
    g = m.group(6).lower()
    delta = NUM.get(g, None) if not g.isdigit() else int(g)
    if delta is None:
        return None
    return {'K': W - 1, 'alpha': alpha, 'coef': col[1], 'delta': delta, 'frac': 1}


def build(p, cap=40000):
    K, A, coef, delta = p['K'], p['alpha'] + 1, p['coef'], p['delta']
    W = K + 1
    if A ** (2 * W) > 10 * cap:
        return None
    key = ('minimum', 'lower median', 'upper median', 'maximum')
    cf = [coef.get(k, 0) for k in key]
    rows = list(product(range(A), repeat=W))

    def value(q):
        s = sorted(q)
        return cf[0] * s[0] + cf[1] * s[1] + cf[2] * s[2] + cf[3] * s[3]

    def crow(r, s):
        return tuple(value((r[j], r[j + 1], s[j], s[j + 1])) for j in range(K))

    pair, ok = {}, []
    for i, r in enumerate(rows):
        for j, s in enumerate(rows):
            c = crow(r, s)
            if any(abs(c[t] - c[t + 1]) != delta for t in range(K - 1)):
                continue
            pair[(i, j)] = c
            ok.append((i, j))
            if len(ok) > cap:
                return None
    if not ok:
        return None
    index = {k: n for n, k in enumerate(ok)}
    nxt = {}
    for (i, j) in ok:
        nxt.setdefault(i, []).append(j)
    adj = []
    for (i, j) in ok:
        c = pair[(i, j)]
        row = []
        for t in nxt.get(j, ()):
            c2 = pair[(j, t)]
            if all(abs(x - y) == delta for x, y in zip(c, c2)):
                row.append(index[(j, t)])
        adj.append(row)
    return ok, adj


terms = transfer17.terms
threshold = transfer17.threshold
