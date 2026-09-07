#!/usr/bin/env python3
"""Connected runs of equal values that must be straight.

    Number of n X 2 0..3 arrays with all horizontally or vertically connected equal values
        in a straight line, and new values 0..3 introduced in row major order.

The condition reads as a condition on connected components, which is a global thing: whether
a component is straight depends on the whole array, not on any bounded window. It is not,
though. A component fails to be straight exactly when it contains a turn, and a turn is a
single cell with an equal neighbour to its side and an equal neighbour above or below it.

    A component is a connected set of equal cells. If every edge of it is horizontal it lies
    in one row and is a horizontal segment; if every edge is vertical it lies in one column.
    Otherwise it has an edge of each kind, and since it is connected there is a path of edges
    from one to the other, along which two consecutive edges differ in kind; those two share
    a cell, and that cell has both a horizontal and a vertical equal neighbour. Conversely a
    cell with both is a turn and its component is neither a row segment nor a column segment.

So: no cell may have a horizontal equal neighbour and a vertical equal neighbour at once.
That is local, and it is more local than it looks. Whether a cell has a horizontal equal
neighbour is decided by its own row alone. Write B(r) for the set of positions in row r that
do. Then the condition on the whole array is exactly

    for every pair of consecutive rows r, s and every j in B(r) union B(s):  r[j] != s[j],

because a cell of B(r) must differ from the cell above it and from the cell below it, and a
cell not in B(r) is unconstrained vertically. Every constraint mentions two consecutive rows
and nothing else, so the state is one row: no window, no deferred judgement, and the last row
needs no special treatment. A single-row array has no vertical neighbours and is always
admissible, which is why these sequences start where they do.
"""
import re
from itertools import product

import lumpauto
import namecanon
import transfer19

DIM = r'(?:\((\d+)\+(\d+)\)|(\d+))'
HEAD = re.compile(
    r'^(?:(Half|One quarter|1/(\d+)) the number of|Number of|number of)\s+(.+?)\s+'
    r'(binary|(\d+)\.\.(\d+))\s+arrays\s+with\s+(.+?)\s*\.?\s*$', re.I)
CANON = re.compile(r'^(.*?),?\s*(?:and\s+|with\s+)?new values (?:\d+\.\.(\d+) )?introduced in '
                   r'(?:row major order|order 0\.\.(\d+))'
                   r'(?:\s*\(colorings ignoring permutations of colors\))?$', re.I)
CANON2 = re.compile(r'^new values \d+\.\.(\d+) introduced in row major order and (.+?)'
                    r'(?:\s*\(colorings ignoring permutations of colors\))?$', re.I)
SHAPE = [
    (re.compile(r'^\(n\+(\d+)\) X ' + DIM + r'$', re.I), 'rows'),
    (re.compile(r'^n X ' + DIM + r'$', re.I), 'rows0'),
]
COND = re.compile(r'^all horizontally or vertically connected equal values in a '
                  r'straight line$', re.I)


def _dim(a, b, c):
    return int(c) if c else int(a) + int(b)


def _shape(s):
    for rx, kind in SHAPE:
        m = rx.match(s)
        if not m:
            continue
        g = m.groups()
        if kind == 'rows':
            return _dim(g[1], g[2], g[3]), int(g[0])
        return _dim(g[0], g[1], g[2]), 0
    return None


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'\s+', ' ', nm).strip()
    nm = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', nm)
    m = HEAD.match(nm)
    if not m:
        return None
    frac = 1
    if m.group(1):
        frac = {'half': 2, 'one quarter': 4}.get(m.group(1).lower()) or int(m.group(2))
    sh = _shape(m.group(3).strip())
    if sh is None:
        return None
    L, a = sh
    k = 2 if m.group(4).lower() == 'binary' else int(m.group(6)) + 1
    cond = m.group(7).strip()
    canon = False
    g = CANON.match(cond)
    if g:
        hi = g.group(2) or g.group(3)
        if hi is not None and int(hi) + 1 != k:
            return None
        canon, cond = True, g.group(1).strip().rstrip(',')
    else:
        g = CANON2.match(cond)
        if g:
            if int(g.group(1)) + 1 != k:
                return None
            canon, cond = True, g.group(2).strip().rstrip(',')
    if not COND.match(cond):
        return None
    if not 1 <= L <= 8 or not 2 <= k <= 5:
        return None
    return {'L': L, 'a': a, 'k': k, 'canon': canon, 'frac': frac, 'transposed': False}


def _advance(m, line, k):
    """m values introduced so far; the row major canonical rule allows a cell to be any
    value already introduced, or the next unused one, and nothing else."""
    for v in line:
        if v > m:
            return None
        if v == m:
            m += 1
    return m if m <= k else None


def hmask(r):
    """positions of the row holding a value equal to the one beside them"""
    L = len(r)
    s = 0
    for j in range(L):
        if (j and r[j - 1] == r[j]) or (j + 1 < L and r[j + 1] == r[j]):
            s |= 1 << j
    return s


def build(p, cap=200000):
    L, k = p['L'], p['k']
    lines = list(product(range(k), repeat=L))
    B = {r: hmask(r) for r in lines}
    if len(lines) * (k + 1) > cap:
        return None

    def ok(r, s):
        m = B[r] | B[s]
        return all(not ((m >> j) & 1 and r[j] == s[j]) for j in range(L))

    index, states, adj = {}, [], []

    def sid(key):
        i = index.get(key)
        if i is None:
            i = index[key] = len(states)
            states.append(key)
            adj.append([])
        return i

    starts = []
    for r in lines:
        m = _advance(0, r, k) if p['canon'] else 0
        if m is None:
            continue
        starts.append(sid((r, m)))
    if not states:
        return None
    frontier, seen = list(starts), set(starts)
    while frontier:
        u = frontier.pop()
        r, m = states[u]
        for s in lines:
            m2 = _advance(m, s, k) if p['canon'] else 0
            if m2 is None or not ok(r, s):
                continue
            v = sid((s, m2))
            if len(states) > cap:
                return None
            adj[u].append(v)
            if v not in seen:
                seen.add(v)
                frontier.append(v)
    S = len(states)
    start = [0] * S
    for i in set(starts):
        start[i] = 1
    end = [1] * S              # every cell is judged by the pair it belongs to
    return lumpauto.lump(adj, start, end)


terms = transfer19.terms
