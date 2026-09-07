#!/usr/bin/env python3
"""The white squares of a board, each needing a neighbour of a matching value.

    Number of n X 3 0..2 white square subarrays x(i,j) with each element diagonally or
    antidiagonally next to at least one element with value 2-x(i,j).
    Number of (n+3) X (1+3) 0..2 white square subarrays x(i,j) with each element diagonally
    or antidiagonally next to at least one element with value (x(i,j)+1) mod 3, and upper
    left element zero.

Only the cells with i + j even carry a value. Their diagonal and antidiagonal neighbours are
again such cells, so the white squares form a board of their own, and the entry's condition
is that every one of them has at least one neighbour holding a prescribed function of its
value --- the successor modulo the alphabet, or the complement.

That condition looks one row up and one row down, so three consecutive rows settle it for the
middle one: carry two rows, judge a row when the row after it arrives, and judge the last row
by the end vector. A cell on the edge of the board simply has fewer neighbours, and having
none of the right value is then a failure rather than a special case --- which is why the
first term of A230647 is zero and not one.

The white cells of a row occupy alternate columns, and which alternate columns depends on the
parity of the row, so the two row shapes alternate down the board. The state carries that
parity implicitly, in the shape of the row it holds.
"""
import re
from itertools import product

import lumpauto
import namecanon
import transfer19

DIAG = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
DIM = r'(?:\((\d+)\+(\d+)\)|(\d+))'
HEAD = re.compile(
    r'^Number of (.+?) (\d+)\.\.(\d+) white square subarrays x\(i,j\) with each element '
    r'diagonally or antidiagonally next to at least one element with value (.+?)'
    r'(, and upper left element (\w+))?\s*\.?$', re.I)
SHAPE = [
    (re.compile(r'^\(n\+(\d+)\) X ' + DIM + r'$', re.I), 'rows'),
    (re.compile(r'^n X ' + DIM + r'$', re.I), 'rows0'),
    (re.compile(r'^' + DIM + r' X \(n\+(\d+)\)$', re.I), 'cols'),
    (re.compile(r'^' + DIM + r' X n$', re.I), 'cols0'),
]
SUCC = re.compile(r'^\(x\(i,j\)\+(\d+)\) mod (\d+)$', re.I)
COMP = re.compile(r'^(\d+)-x\(i,j\)$', re.I)
WORD = {'zero': 0, 'one': 1, 'two': 2, 'three': 3}


def _dim(a, b, c):
    return int(c) if c else int(a) + int(b)


def _shape(s):
    for rx, kind in SHAPE:
        m = rx.match(s)
        if not m:
            continue
        g = m.groups()
        if kind == 'rows':
            return _dim(g[1], g[2], g[3]), int(g[0]), False
        if kind == 'rows0':
            return _dim(g[0], g[1], g[2]), 0, False
        if kind == 'cols':
            return _dim(g[0], g[1], g[2]), int(g[3]), True
        return _dim(g[0], g[1], g[2]), 0, True
    return None


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'\s+', ' ', nm).strip()
    nm = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', nm)
    m = HEAD.match(nm)
    if not m:
        return None
    sh = _shape(m.group(1).strip())
    if sh is None:
        return None
    L, a, tr = sh
    lo, hi = int(m.group(2)), int(m.group(3))
    if lo != 0 or not 1 <= hi <= 4 or not 2 <= L <= 8:
        return None
    k = hi + 1
    tgt = m.group(4).strip()
    g = SUCC.match(tgt)
    if g:
        if int(g.group(2)) != k:
            return None
        rule = ('succ', int(g.group(1)))
    else:
        g = COMP.match(tgt)
        if not g or int(g.group(1)) != hi:
            return None
        rule = ('comp', hi)
    corner = None
    if m.group(6) is not None:
        c = m.group(6).lower()
        corner = int(c) if c.isdigit() else WORD.get(c)
        if corner is None:
            return None
    return {'L': L, 'a': a, 'k': k, 'rule': rule, 'corner': corner,
            'transposed': tr, 'frac': 1}


def build(p, cap=200000):
    L, k = p['L'], p['k']
    tr = p.get('transposed', False)
    kind, val = p['rule']

    def target(x):
        return (x + val) % k if kind == 'succ' else val - x

    # the white cells of a line, by the parity of that line's index
    cols = {q: [j for j in range(L) if (j % 2) == q] for q in (0, 1)}
    lines = {q: list(product(range(k), repeat=len(cols[q]))) for q in (0, 1)}

    def sat(mid, q, t, above, below):
        """is every white cell of the middle line matched by a neighbour above or below?

        A neighbour of a white cell in column j sits at column j-1 or j+1 of the adjacent
        line, which is white there because the parities alternate.
        """
        other = cols[1 - q]
        pos = {j: i for i, j in enumerate(other)}
        for i, j in enumerate(cols[q]):
            want = target(mid[i])
            found = False
            for row in (above, below):
                if row is None:
                    continue
                for jj in (j - 1, j + 1):
                    x = pos.get(jj)
                    if x is not None and row[x] == want:
                        found = True
                        break
                if found:
                    break
            if not found:
                return False
        return True

    index, states, adj = {}, [], []

    def sid(key):
        i = index.get(key)
        if i is None:
            i = index[key] = len(states)
            states.append(key)
            adj.append([])
        return i

    starts = []
    for r in lines[0]:
        if p['corner'] is not None and (not cols[0] or cols[0][0] != 0 or r[0] != p['corner']):
            continue
        starts.append(sid((0, None, r)))
    if not states:
        return None
    frontier, seen = list(starts), set(starts)
    while frontier:
        u = frontier.pop()
        q, above, mid = states[u]
        nq = 1 - q
        for r in lines[nq]:
            if not sat(mid, q, None, above, r):
                continue
            v = sid((nq, mid, r))
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
    end = [1 if sat(mid, q, None, above, None) else 0 for q, above, mid in states]
    return lumpauto.lump(adj, start, end)


terms = transfer19.terms
