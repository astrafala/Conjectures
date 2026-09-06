#!/usr/bin/env python3
"""`Number of n X W 0..m arrays with every 0 next to a 1 and every 1 next to a 2
horizontally, diagonally or antidiagonally[, with no adjacent values equal].'

For each of a short list of pairs, every cell carrying the first value of the pair must have at
least one neighbour, in the named directions, carrying the second. Some entries add that no two
neighbouring cells carry equal values.

The neighbours of a cell lie in the row above, its own row and the row below, so a window of
three consecutive rows decides the condition for the middle one. The state is the pair (row
above, current row), a row not yet written carried as a symbol; a step appends a row and settles
the middle row of the window it completes, and the LAST row is settled by the end vector, with
nothing below it. The end vector is therefore not the all-ones vector: a row whose cells find
what they need only because a further row is written below them does not finish an array.
"""
import re
from itertools import product

import namecanon
import transfer19

CLASS = {'horizontally': [(0, -1), (0, 1)], 'vertically': [(-1, 0), (1, 0)],
         'diagonally': [(-1, -1), (1, 1)], 'antidiagonally': [(-1, 1), (1, -1)]}
_W1 = r'(?:horizontally|vertically|diagonally|antidiagonally)'
SHAPE = r'(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))\s*X\s*(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))'

NAME = re.compile(
    r'Number of\s+' + SHAPE + r'\s*0\.\.(\d+)\s*arrays with\s+'
    r'((?:every \d+ next to a \d+(?:,\s*|\s+and\s+)?)+)\s*'
    r'(' + _W1 + r'(?:[, ]+(?:or |and )?' + _W1 + r')*)'
    r'(,?\s*(?:with\s+|and\s+)?no adjacent (?:values|elements) equal)?\s*\.?\s*$', re.I)


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = NAME.search(nm)
    if not m:
        return None
    ra = m.group(1) or m.group(3)
    rb = int(m.group(2) or 0)
    ca = m.group(4) or m.group(6)
    cb = int(m.group(5) or 0)
    if (ra == 'n') == (ca == 'n'):
        return None
    if ra == 'n':
        W, trans = int(ca) + cb, False
    else:
        W, trans = int(ra) + rb, True
    alpha = int(m.group(7))
    pairs = [(int(g.group(1)), int(g.group(2)))
             for g in re.finditer(r'every (\d+) next to a (\d+)', m.group(8), re.I)]
    if not pairs:
        return None
    D = []
    for w in dict.fromkeys(re.findall(_W1, m.group(9).lower())):
        D += CLASS[w]
    if trans:
        D = [(b, a) for a, b in D]
    noeq = bool(m.group(10))
    if not D or W < 1:
        return None
    return {'W': W, 'alpha': alpha, 'pairs': pairs, 'dirs': sorted(set(D)), 'noeq': noeq,
            'trans': trans, 'frac': 1}


def build(p, cap=40000):
    W, A = p['W'], p['alpha'] + 1
    D = [tuple(t) for t in p['dirs']]
    want = {}
    for v, w in p['pairs']:
        want.setdefault(v, set()).add(w)
    noeq = p['noeq']
    if A ** W > 8 * cap:
        return None
    rows = list(product(range(A), repeat=W))

    def okrow(prev, cur, nxt):
        for j in range(W):
            v = cur[j]
            seen = set()
            for di, dj in D:
                b = j + dj
                if not (0 <= b < W):
                    continue
                r = cur if di == 0 else (prev if di < 0 else nxt)
                if r is None:
                    continue
                y = r[b]
                if noeq and y == v:
                    return False
                seen.add(y)
            if v in want and not (want[v] & seen):
                return False
        return True

    idx, order, adj, end = {}, [], [], []

    def push(st):
        if st not in idx:
            idx[st] = len(order)
            order.append(st)
            adj.append(None)
            end.append(0)
        return idx[st]

    push((None, None))
    t = 0
    while t < len(order):
        prev, cur = order[t]
        row = []
        if cur is None:
            for x in rows:
                row.append(push((None, x)))
            end[t] = 1
        else:
            for x in rows:
                if okrow(prev, cur, x):
                    row.append(push((cur, x)))
            end[t] = 1 if okrow(prev, cur, None) else 0
        adj[t] = row
        t += 1
        if len(order) > cap:
            return None
    n = len(order)
    st = [0] * n
    st[0] = 1
    return adj, st, end[:n], n


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
