#!/usr/bin/env python3
"""Knight-distance labellings of a strip. NOT IN SERVICE --- see the caveat below.

    Number of (n+2) X (1+2) nonnegative integer arrays with all values the knight distance
    from the upper left minus as much as 2, with successive minimum path knight move
    differences either 0 or +1, and any unreachable value zero.

Let d(c) be the knight distance from the top left corner and v(c) the entry's value. The
entry asks for d(c) - s <= v(c) <= d(c) and, along every minimum knight path, for successive
values to differ by 0 or +1. Put w = d - v. Then w takes values in {0,...,s}, and for a
minimum-path edge a -> b (so d(b) = d(a)+1) the condition v(b)-v(a) in {0,1} becomes
w(b)-w(a) in {0,1}: w rises along every such edge, by at most one. Unreachable cells are
fixed at zero and contribute nothing.

That reading is PINNED: a direct enumeration of those labellings reproduces A253112's
published 53, 272, 1342 exactly, and a row-by-row count using each board's own distances
reproduces every published term of all fifteen reachable entries.

WHY THIS IS NOT IN SERVICE. Turning the row-by-row count into a fixed transfer matrix needs
the local structure of the board --- which pairs within two rows are minimum-path edges, and
how far each label is capped --- to repeat down the strip. It does repeat, with period 4, but
the row from which it repeats is not what a first measurement suggested, and the engine built
on that measurement produced a model that matched the first six published terms of A253112
and then undercounted every one after them. The measurement compared the wrong signature: it
checked the edges within rows i-1, i, i+1 but the transfer also needs the edges between rows
i-2 and i, and those settle one row later.

Repairing the offset is easy. What is not settled is the underlying claim, which is that
d(i+4, j) = d(i, j) + 2 for every column once i is large enough. The inequality <= is
immediate --- two knight moves, (2,1) then (2,-1), drop four rows and return to the same
column --- but >= is not proved here, and a finite check of it over a few hundred rows is
evidence, not a proof. Until that is proved, any recurrence this engine certified would rest
on it, so the engine is kept, unregistered, with its reading pinned and its obstruction
written down rather than shipped.
"""
import re
from itertools import product

import lumpauto
import namecanon
import transfer19

KN = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]
PERIOD = 4
SETTLED = {3: 5, 4: 5, 5: 7, 6: 9, 7: 11}      # first row from which the edge sets
                                               # AND the caps repeat, per width; the
                                               # earlier table was one row short because
                                               # it did not check the (i-2, i) edges
EXCEPTIONAL = (2, 3, 4)                        # heights whose distances differ

DIM = r'(?:\((\d+)\+(\d+)\)|(\d+))'
HEAD = re.compile(
    r'^Number of \(n\+(\d+)\) X ' + DIM + r' nonnegative integer arrays with all values the '
    r'knight distance from the upper left minus as much as (\d+), with successive minimum '
    r'path knight move differences either 0 or \+1, and any unreachable value zero\.?$',
    re.I)


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'\s+', ' ', nm).strip()
    nm = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', nm)
    m = HEAD.match(nm)
    if not m:
        return None
    a = int(m.group(1))
    C = int(m.group(4)) if m.group(4) else int(m.group(2)) + int(m.group(3))
    s = int(m.group(5))
    if C not in SETTLED or not 1 <= s <= 3:
        return None
    return {'C': C, 'a': a, 'slack': s, 'frac': 1}


def dists(R, C):
    """knight distance from the top left, on a board of exactly R rows and C columns"""
    d = {(0, 0): 0}
    q = [(0, 0)]
    while q:
        nq = []
        for (i, j) in q:
            for di, dj in KN:
                x, y = i + di, j + dj
                if 0 <= x < R and 0 <= y < C and (x, y) not in d:
                    d[(x, y)] = d[(i, j)] + 1
                    nq.append((x, y))
        q = nq
    return d


def _rowstates(d, C, s, i):
    """the possible labellings of row i, as tuples with None where the cell is unreachable"""
    doms = [(None,) if (i, j) not in d else tuple(range(min(s, d[(i, j)]) + 1))
            for j in range(C)]
    return list(product(*doms))


def _edges(d, r1, r2, C):
    """minimum-path edges between row r1 and row r2, as (column in r1, column in r2, up)"""
    out = []
    for j1 in range(C):
        for j2 in range(C):
            if (r2 - r1, j2 - j1) not in KN:
                continue
            a, b = (r1, j1), (r2, j2)
            if a in d and b in d:
                if d[b] == d[a] + 1:
                    out.append((j1, j2, False))
                elif d[a] == d[b] + 1:
                    out.append((j1, j2, True))
    return out


def _ok(row_a, row_b, edges):
    """every edge between two rows: w rises by 0 or 1 from the lower d to the higher"""
    for j1, j2, up in edges:
        x, y = row_a[j1], row_b[j2]
        if x is None or y is None:
            continue
        lo, hi = (y, x) if up else (x, y)
        if not 0 <= hi - lo <= 1:
            return False
    return True


def count_board(R, C, s):
    """the exact count on a board of exactly R rows, using that board's own distances"""
    d = dists(R, C)
    layer = {(): 1}
    for i in range(R):
        e1 = _edges(d, i - 1, i, C) if i >= 1 else []
        e2 = _edges(d, i - 2, i, C) if i >= 2 else []
        nxt = {}
        for r in _rowstates(d, C, s, i):
            for st, w in layer.items():
                if e1 and not _ok(st[-1], r, e1):
                    continue
                if e2 and not _ok(st[-2], r, e2):
                    continue
                k = (st + (r,))[-2:]
                nxt[k] = nxt.get(k, 0) + w
        layer = nxt
        if not layer:
            return 0
    return sum(layer.values())


def build(p, cap=200000):
    C, s = p['C'], p['slack']
    i0 = SETTLED[C]
    tall = dists(400, C)

    def phase(i):
        return i if i < i0 else i0 + (i - i0) % PERIOD

    # the phase is a faithful stand-in for the row index: the edge sets and the caps at row i
    # depend on i only through phase(i), which is what the period measurement establishes
    rows = {}

    def rowstates(ph):
        if ph not in rows:
            rows[ph] = _rowstates(tall, C, s, ph)
        return rows[ph]

    E1 = {}
    E2 = {}

    def e1(ph):
        if ph not in E1:
            E1[ph] = _edges(tall, ph - 1, ph, C)
        return E1[ph]

    def e2(ph):
        if ph not in E2:
            E2[ph] = _edges(tall, ph - 2, ph, C)
        return E2[ph]

    index, states, adj = {}, [], []

    def sid(key):
        i = index.get(key)
        if i is None:
            i = index[key] = len(states)
            states.append(key)
            adj.append([])
        return i

    starts = [sid((0, None, r)) for r in rowstates(0)]
    if not states:
        return None
    frontier, seen = list(starts), set(starts)
    while frontier:
        u = frontier.pop()
        i, prev, cur = states[u]
        nxt_i = i + 1
        ph = phase(nxt_i)
        for r in rowstates(ph):
            if not _ok(cur, r, e1(ph)):
                continue
            if prev is not None and not _ok(prev, r, e2(ph)):
                continue
            v = sid((ph, cur, r))
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
    end = [1] * S
    return lumpauto.lump(adj, start, end)


def terms_p(p, b, N):
    """model counts by walk step: step j is a board of j + 1 rows

    The matrix is built from distances that are correct for every height except 2, 3 and 4,
    so those three are recounted here on their own boards. Without that the model would
    disagree with the entry's first terms, which is how the discrepancy was noticed.
    """
    adj, start, end, S = b
    out = transfer19.terms(adj, start, end, N)
    for R in EXCEPTIONAL:
        j = R - 1
        if 0 <= j <= N:
            out[j] = count_board(R, p['C'], p['slack'])
    return out


def threshold_p(p, b, coeffs, order):
    """the last walk index at which the conjectured recurrence may fail

    The matrix certifies the recurrence for its own sequence, which is the true one only from
    a board of five rows on. A residual at index j reads terms j-order..j, so no residual
    below index (4 - 1) + order is certified by the matrix, and the bound is raised to cover
    them. Being conservative here can only shrink the range claimed.
    """
    adj, start, end, S = b
    adj, start, end, S = lumpauto.lump(adj, start, end)
    t = transfer19.threshold(adj, start, end, coeffs, order, S)
    return None if t is None else max(t, max(EXCEPTIONAL) - 1 + order)


terms = transfer19.terms
