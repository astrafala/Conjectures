#!/usr/bin/env python3
"""`every 2 X 3 or 3 X 2 subblock having exactly two clockwise edge increases' and relatives.

Both window shapes have all six of their cells on the perimeter, so each carries a $6$-cycle:
for $\\begin{pmatrix}p&q\\\\r&s\\\\t&u\\end{pmatrix}$ the clockwise cycle is
$p\\to q\\to s\\to u\\to t\\to r\\to p$, and for $\\begin{pmatrix}p&q&t\\\\r&s&u\\end{pmatrix}$ it
is $p\\to q\\to t\\to u\\to s\\to r\\to p$; counterclockwise is each cycle reversed. The readings
were pinned by direct enumeration first: over $0..2$ the $3\\times2$ arrays with clockwise
count $2$ number $423$ and those with count $3$ number $150$; over $0..3$ the $3\\times2$
arrays with count $1$ number $480$; and the $2\\times3$ arrays over $0..2$ with clockwise count
$2$ also number $423$. Those are the first terms of the corresponding entries.

A $3\\times2$ window spans three array rows and a $2\\times3$ window two, so the state is the
pair of consecutive rows: the $2\\times3$ windows decide which pairs are admissible, and the
$3\\times2$ windows decide which pair may follow which.
"""
import re
from itertools import product

import namecanon
import transfer17

NUM = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6}
EDGE = r'(clockwise|counterclockwise) edge increases'

HEAD = re.compile(r'Number of \(\s*n\s*\+\s*1\s*\)\s*X\s*(\d+)\s*'
                  r'(?:0\.\.(\d+)|(binary))\s+arrays\s+with\s+every\s+2\s*X\s*3\s+or\s+'
                  r'3\s*X\s*2\s+subblock\s+having\s+(.*?)\s*\.?\s*$', re.I)

Q1 = re.compile(r'exactly (\w+) ' + EDGE + r'$', re.I)
Q2 = re.compile(r'exactly (\w+) counterclockwise and (\w+) clockwise edge increases$', re.I)
Q3 = re.compile(r'an (equal|unequal) number of clockwise and counterclockwise edge '
                r'increases$', re.I)
Q4 = re.compile(r'exactly (\w+) equal edges$', re.I)
Q5 = re.compile(r'no more than (\w+) equal edges$', re.I)


def _n(w):
    w = w.lower()
    return int(w) if w.isdigit() else NUM.get(w)


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn)])\s*[xX]\s*(?=[\dn(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = HEAD.search(nm)
    if not m:
        return None
    W = int(m.group(1))
    alpha = 1 if m.group(3) else int(m.group(2))
    body = m.group(4)
    if W < 2 or alpha < 1:
        return None
    base = {'W': W, 'alpha': alpha, 'frac': 1}
    c = Q2.match(body)
    if c:
        a1, a2 = _n(c.group(1)), _n(c.group(2))
        if a1 is None or a2 is None:
            return None
        base.update(kind='both', ccw=a1, cw=a2)
        return base
    c = Q1.match(body)
    if c:
        k = _n(c.group(1))
        if k is None:
            return None
        base.update(kind='one', which=c.group(2).lower(), value=k)
        return base
    c = Q3.match(body)
    if c:
        base.update(kind='cmp', equal=(c.group(1).lower() == 'equal'))
        return base
    c = Q4.match(body)
    if c:
        k = _n(c.group(1))
        if k is None:
            return None
        base.update(kind='eq', value=k, atmost=False)
        return base
    c = Q5.match(body)
    if c:
        k = _n(c.group(1))
        if k is None:
            return None
        base.update(kind='eq', value=k, atmost=True)
        return base
    return None


def _ring(h, w):
    """the cells of an h x w window in clockwise perimeter order, as (row, col)"""
    top = [(0, j) for j in range(w)]
    right = [(i, w - 1) for i in range(1, h)]
    bot = [(h - 1, j) for j in range(w - 2, -1, -1)]
    left = [(i, 0) for i in range(h - 2, 0, -1)]
    return top + right + bot + left


R32 = _ring(3, 2)
R23 = _ring(2, 3)


def _counts(vals):
    n = len(vals)
    cw = sum(1 for i in range(n) if vals[i] < vals[(i + 1) % n])
    ccw = sum(1 for i in range(n) if vals[i] > vals[(i + 1) % n])
    eq = sum(1 for i in range(n) if vals[i] == vals[(i + 1) % n])
    return cw, ccw, eq


def _ok(p, vals):
    cw, ccw, eq = _counts(vals)
    k = p['kind']
    if k == 'one':
        return (cw if p['which'] == 'clockwise' else ccw) == p['value']
    if k == 'both':
        return cw == p['cw'] and ccw == p['ccw']
    if k == 'cmp':
        return (cw == ccw) == p['equal']
    return (eq <= p['value']) if p['atmost'] else (eq == p['value'])


def build(p, cap=40000):
    W, A = p['W'], p['alpha'] + 1
    if A ** (2 * W) > 10 * cap:
        return None
    rows = list(product(range(A), repeat=W))

    def pair_ok(r, s):
        for j in range(W - 2):
            g = ((r[j], r[j + 1], r[j + 2]), (s[j], s[j + 1], s[j + 2]))
            if not _ok(p, [g[i][c] for i, c in R23]):
                return False
        return True

    def step_ok(r, s, t):
        for j in range(W - 1):
            g = ((r[j], r[j + 1]), (s[j], s[j + 1]), (t[j], t[j + 1]))
            if not _ok(p, [g[i][c] for i, c in R32]):
                return False
        return True

    ok = [(i, j) for i in range(len(rows)) for j in range(len(rows))
          if pair_ok(rows[i], rows[j])]
    if not ok or len(ok) > cap:
        return None
    index = {k: n for n, k in enumerate(ok)}
    nxt = {}
    for (i, j) in ok:
        nxt.setdefault(i, []).append(j)
    adj = []
    for (i, j) in ok:
        adj.append([index[(j, t)] for t in nxt.get(j, ())
                    if step_ok(rows[i], rows[j], rows[t])])
    return ok, adj


terms = transfer17.terms
threshold = transfer17.threshold
