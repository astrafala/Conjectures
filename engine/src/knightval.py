#!/usr/bin/env python3
"""Arrays whose values sit just below the knight distance from the corner.

    Number of (n+2)X(1+2) nonnegative integer arrays with all values the knight distance from
      the upper left minus as much as 2, with successive minimum path knight move differences
      either 0 or +1, and any unreachable value zero.

The reading, settled against the entries' own first terms rather than assumed. Write kd(x) for
the knight distance from the upper-left corner on the board. A cell's value is kd(x) - t(x) with
t(x) in 0..D-1, D being one more than the "as much as" number, and the value must stay
NONNEGATIVE. A "successive minimum path knight move" is a pair (p, x) with p a knight neighbour
of x and kd(p) = kd(x) - 1, and the condition is value(x) - value(p) in {0, 1}. Unreachable
cells are 0 and lie on no minimum path. Read with two options instead of three, or without the
nonnegativity, a 3 X 3 board gives 17, 18 or 71 where A253112 gives 53.

Because kd(x) = kd(p) + 1 the distances cancel and the condition is local in t alone:

    t(x) - t(p) in {0, 1}.

So t rises by at most one along any minimum path and never falls, which is what keeps the model
small: the predecessors of a cell must have t-values within one of each other, and the reachable
set of (row, row) pairs collapses from D^(2C) to a few hundred.

A minimum-path edge spans at most two rows, so the vertex is the pair of t-rows (r-1, r) and an
edge is checked when its LOWER row arrives; carrying the phase r mod 4 alongside turns the
periodic transition into a single digraph, and the count is a walk in it.

WHAT MAKES THE TRANSFER MATRIX LEGITIMATE. Two facts about the distance field, and neither is
assumed here: that the field does not depend on the height of the board once the board is tall
enough, and that its rows repeat with period 4, the distance rising by 2 per period. An earlier
engine for this same family, `transfer88`, was written and then deliberately left OUT OF
SERVICE because both had only been MEASURED over a few hundred rows, and a finite check of an
infinite claim is evidence rather than proof. `kdcert` proves them: a guessed field that
satisfies the two Bellman conditions IS the distance whatever its provenance, the conditions at
a row involve only the two rows on either side, and so finitely many rows settle every row.
This engine reads its field from that certificate and refuses any width the certificate does
not cover. The heights below the certificate's H0 -- where the short board's own field really
is different, the centre of a 3 X 3 board being unreachable while on a tall board it is at
distance 4 -- are counted on their own boards, which needs no theorem at all.
"""
import re
from collections import defaultdict

import kdcert

MV = kdcert.KN

NAME = re.compile(
    r'(?i)^Number of \(n\+2\)\s*X\s*\((\d+)\+2\) nonnegative integer arrays with all values '
    r'the knight distance from the upper left minus as much as (\d+), with successive minimum '
    r'path knight move differences either 0 or \+1, and any unreachable value zero\s*\.?\s*$')


def parse_name(nm):
    nm = ' '.join(nm.split())
    nm = re.sub(r'(?<=[\dn)])\s*[xX]\s*(?=[\d(])', ' X ', nm)
    nm = ' '.join(nm.split())
    m = NAME.match(nm)
    if not m:
        return None
    C, D = int(m.group(1)) + 2, int(m.group(2)) + 1
    if C < 3 or C > 12 or D < 2 or D > 6:
        return None
    return {'engine': 'knightval', 'C': C, 'D': D, 'frac': 1}


def _field(R, C):
    """the distance field of the board of exactly R rows, as a table with -1 for unreachable.

    Below the certificate's H0 this is the short board's own field, which differs from the
    tall one and is computed on the board itself; from H0 on it is the certified field."""
    f = kdcert.field(C, R)
    if f is None:
        return None
    return [[-1 if v == kdcert.INF else int(v) for v in row] for row in f]


def _edges(M, R, C):
    """edges (p -> x), p a knight neighbour of x with kd(p) = kd(x) - 1, keyed by the LOWER
    of the two rows they touch, so an edge is checked when its lower row arrives."""
    edges = defaultdict(list)
    for r in range(R):
        for c in range(C):
            if M[r][c] < 0:
                continue
            for dr, dc in MV:
                pr, pc = r - dr, c - dc
                if 0 <= pr < R and 0 <= pc < C and M[pr][pc] == M[r][c] - 1:
                    edges[max(pr, r)].append((pr, pc, r, c))
    return edges


def _rowsof(M, C, D, r):
    acc = [()]
    for c in range(C):
        o = [t for t in range(D) if t <= M[r][c]] if M[r][c] >= 0 else [0]
        acc = [a + (t,) for a in acc for t in o]
    return acc


def _ok(edges, rows, r):
    """every edge whose lower row is r, given the t-rows in `rows`"""
    for (pr, pc, xr, xc) in edges[r]:
        if pr not in rows or xr not in rows:
            return False
        if rows[xr][xc] - rows[pr][pc] not in (0, 1):
            return False
    return True


def _small(H, C, D):
    """the height-H count computed on the height-H board's OWN distance field.

    The field is not height-free all the way down: on a 3 X 3 board the centre is unreachable
    while on a tall board it is at distance 4, and the first three or four heights each have a
    field of their own. Those heights are counted directly."""
    M = _field(H, C)
    E = _edges(M, H, C)
    cur = defaultdict(int)
    for a in _rowsof(M, C, D, 0):
        for b in _rowsof(M, C, D, 1):
            if _ok(E, {0: a, 1: b}, 1):
                cur[(a, b)] += 1
    for r in range(2, H):
        nxt = defaultdict(int)
        for (a, b), w in cur.items():
            for c2 in _rowsof(M, C, D, r):
                if _ok(E, {r - 2: a, r - 1: b, r: c2}, r):
                    nxt[(b, c2)] += w
        cur = nxt
        if not cur:
            return 0
    return sum(cur.values())


def build(p, cap=400000):
    C, D = p['C'], p['D']
    cert = kdcert.get(C)
    if cert is None:
        return None                        # no proof of the period, so no model
    R = cert['i0'] + 6 * kdcert.PERIOD + 8
    M = _field(R, C)
    edges = _edges(M, R, C)
    h0 = cert['H0']                        # below this a board's own field is its own

    def rows_of(r):
        return _rowsof(M, C, D, r)

    def ok(a, b, c2, r):
        return _ok(edges, {r - 2: a, r - 1: b, r: c2}, r)

    # The first row whose state may be carried by the fixed matrix. Its transition reads rows
    # r-1 .. r+3, all of which must lie in the certified periodic region -- that region starts
    # at the certificate's i0 -- and the option list at a cell must already be the full
    # 0..D-1, which it is once every reachable distance in the region is at least D-1.
    r0 = None
    for r in range(max(cert['i0'] + 2, h0 - 1), R - 8):
        if all(M[t][c] < 0 or M[t][c] >= D - 1
               for t in range(r - 1, r - 1 + kdcert.PERIOD) for c in range(C)):
            r0 = r
            break
    if r0 is None:
        return None

    pre = {h: _small(h, C, D) for h in range(2, h0)}

    # forward DP on the tall field; after row r the state is the pair (row r-1, row r) and the
    # running total is the height-(r+1) count
    cur = defaultdict(int)
    for a in rows_of(0):
        for b in rows_of(1):
            if ok((), a, b, 1):
                cur[(a, b)] += 1
    if h0 <= 2:
        pre[2] = sum(cur.values())
    for r in range(2, r0 + 1):
        nxt = defaultdict(int)
        for (a, b), w in cur.items():
            for c2 in rows_of(r):
                if ok(a, b, c2, r):
                    nxt[(b, c2)] += w
        cur = nxt
        if r + 1 >= h0:
            pre[r + 1] = sum(cur.values())
        if len(cur) > cap:
            return None

    # the periodic digraph on (pair, phase), phase = row index mod 4
    states, index = [], {}

    def sid(s):
        if s not in index:
            index[s] = len(states)
            states.append(s)
        return index[s]

    start = defaultdict(int)
    for k, w in cur.items():
        start[sid((k, r0 % kdcert.PERIOD))] += w
    adj = {}
    i = 0
    while i < len(states):
        (a, b), ph = states[i]
        r = r0 + ((ph - r0) % kdcert.PERIOD)   # a row of that phase, in the certified region
        out = []
        for c2 in rows_of(r + 1):
            if ok(a, b, c2, r + 1):
                out.append(sid(((b, c2), (ph + 1) % kdcert.PERIOD)))
        adj[i] = out
        i += 1
        if len(states) > cap:
            return None
    import lumpauto
    stv = [0] * len(states)
    for j, w in start.items():
        stv[j] = w
    wadj, wstart, wend, S = lumpauto.lump(adj, stv, [1] * len(states))
    return {'adj': wadj, 'startv': wstart, 'endv': wend,
            'S': S, 'raw': len(states), 'r0': r0, 'pre': pre}


def terms(b, N):
    """a(n) counts the (n+2) X C arrays, so a(n) is the height-(n+2) count; offset 1."""
    pre, r0 = dict(b['pre']), b['r0']
    adj, S = b['adj'], b['S']
    vec = list(b['startv'])
    ev = b['endv']
    h = r0 + 1                                 # the height `pre` already reaches
    while h < N + 2:
        nxt = [0] * S
        for i, v in enumerate(vec):
            if not v:
                continue
            for j in adj[i]:
                nxt[j] += v
        vec = nxt
        h += 1
        pre[h] = sum(v * e for v, e in zip(vec, ev))
    return [pre[n + 2] for n in range(1, N + 1)]


def threshold(b, coeffs, order):
    """The walk certifies a(n) only from height r0+1 on, so the residual is tested in two
    pieces: the annihilation test on the transfer matrix settles every large n at once, and
    the heights below r0+1 -- each counted on its own board, because the distance field is not
    height-free down there -- are checked term by term. The bound returned is the later of the
    two, so nothing is certified on a term the matrix never produced."""
    import transfer19 as T19
    adj, S, r0 = b['adj'], b['S'], b['r0']
    tw = T19.threshold(adj, b['startv'], b['endv'], coeffs, order, S)
    if tw is None:
        return None
    # u_j of the walk test is the residual at a-index j + order + r0 - 1
    N = max(tw + r0 - 1, r0 + order + 5) + 3
    t = terms(b, N)
    last = 0
    for n in range(order + 1, N + 1):
        if t[n - 1] - sum(c * t[n - 1 - i] for i, c in coeffs.items()):
            last = n
    return last
