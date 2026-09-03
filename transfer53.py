#!/usr/bin/env python3
"""`Number of n X W 0..m arrays x(i,j) with each element <directions> next to at least one
element with value (x(i,j)+1) mod M and at least one element with value (x(i,j)-1) mod M,
[no adjacent elements equal,] and upper left element zero.'

Every cell must SEE, among its neighbours in the named directions, at least a stated number of
cells carrying the value one more than its own modulo `M', and --- when the entry asks for it
--- at least a stated number carrying the value one less. Some entries add that no two
neighbouring cells are equal, and all of them fix the top left cell at zero.

The neighbours of a cell lie in the row above, its own row and the row below, so a window of
three consecutive rows decides the condition for the middle one. The state is the pair (row
above, current row), the row above allowed to be absent; a step appends a row and settles the
middle row of the window it completes, and the LAST row is settled by the end vector, with
nothing below it. The end vector is therefore not the all-ones vector: a row that sees enough
neighbours only when another row is written below it does not finish an array.
"""
import re
from itertools import product

import namecanon
import transfer19

CLASS = {'horizontally': [(0, -1), (0, 1)], 'vertically': [(-1, 0), (1, 0)],
         'diagonally': [(-1, -1), (1, 1)], 'antidiagonally': [(-1, 1), (1, -1)]}
_W1 = r'(?:horizontally|vertically|diagonally|antidiagonally)'
NUM = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4}

SHAPE = r'(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))\s*X\s*(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))'

NAME = re.compile(
    r'Number of\s+' + SHAPE + r'\s*0\.\.(\d+)\s*arrays x\(i,j\) with each element\s+'
    r'(' + _W1 + r'(?:[, ]+(?:or |and )?' + _W1 + r')*)\s+next to at least\s+(\w+)\s+'
    r'elements?\s+with value \(x\(i,j\)\+1\) mod (\d+)'
    r'(?:\s+and at least\s+(\w+)\s+elements?\s+with value \(x\(i,j\)-1\) mod (\d+))?'
    r'(,\s*no adjacent elements equal)?'
    r',\s*and upper left element zero\s*\.?\s*$', re.I)


def _n(w):
    w = w.lower()
    return int(w) if w.isdigit() else NUM.get(w)


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
    D = []
    for w in dict.fromkeys(re.findall(_W1, m.group(8).lower())):
        D += CLASS[w]
    if trans:
        D = [(b, a) for a, b in D]
    up = _n(m.group(9))
    M = int(m.group(10))
    dn = _n(m.group(11)) if m.group(11) else None
    if m.group(12) and int(m.group(12)) != M:
        return None
    noeq = bool(m.group(13))
    if up is None or (m.group(11) and dn is None) or W < 1 or M < 2:
        return None
    return {'W': W, 'alpha': alpha, 'dirs': sorted(set(D)), 'up': up, 'dn': dn, 'mod': M,
            'noeq': noeq, 'trans': trans, 'frac': 1}


def build(p, cap=40000):
    W, A, M = p['W'], p['alpha'] + 1, p['mod']
    D = [tuple(t) for t in p['dirs']]
    up, dn, noeq = p['up'], p['dn'], p['noeq']
    if A ** W > 8 * cap:
        return None
    rows = list(product(range(A), repeat=W))

    def okrow(prev, cur, nxt):
        for j in range(W):
            v = cur[j]
            cu = cd = 0
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
                if (y - v) % M == 1:
                    cu += 1
                if (v - y) % M == 1:
                    cd += 1
            if cu < up:
                return False
            if dn is not None and cd < dn:
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
                if x[0] == 0:                      # upper left element zero
                    row.append(push((None, x)))
            end[t] = 0                             # the empty array is not counted
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
