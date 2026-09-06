#!/usr/bin/env python3
"""`Number of n X W 0..m arrays with no element x(i,j) adjacent to [itself or] value m-x(i,j)
<directions>[, top left element zero][, and v appearing before w ... in row major order]'.

The condition proper is local: a cell and a neighbour in one of the named directions may not
carry values summing to `m' (and, when the entry says `itself or', may not carry equal values
either). Every named direction moves the row index by at most one, so a single array row is
enough state for the condition.

Two extra clauses appear in most of the family and are not decoration --- they are what makes
the entry count UNLABELLED colourings rather than coloured arrays:

  `top left element zero'   fixes one cell, so it restricts which rows may BEGIN the array;

  `1 appearing before 2 3 and 4, and 2 appearing before 3 in row major order'
                            asks that, reading the cells in row major order, the first
                            appearance of one value precede the first appearance of another.

For an `n X W' entry the walk runs down the rows and visits the cells in exactly row major
order, so the second clause is carried by one extra piece of state: the SET of the mentioned
values seen so far. A value may be written for the first time only when every value required
to precede it is already in that set. Nothing more is needed, because a precedence is decided
the moment the later value first appears.

For a `W X n' entry the walk runs across the columns and does NOT visit the cells in row major
order, so the precedence clause cannot be carried this way; those entries are refused here.
Entries of that shape without the clause are accepted, the array being transposed once.
"""
import re
from itertools import product

import namecanon
import transfer19
import lumpauto

CLASS = {'horizontally': [(0, 1)], 'vertically': [(1, 0)],
         'diagonally': [(1, 1)], 'antidiagonally': [(1, -1)]}
_W1 = r'(?:horizontally|vertically|diagonally|antidiagonally)'
NBSET = r'(' + _W1 + r'(?:[, ]+(?:or |and )?' + _W1 + r')*)'

NAME = re.compile(
    r'Number of\s+(?:n\s*X\s*(\d+)|(\d+)\s*X\s*n)\s+0\.\.(\d+)\s+arrays with no element '
    r'x\(i,j\) adjacent to\s+(itself or\s+)?value\s+(\d+)\s*-\s*x\(i,j\)\s+' + NBSET +
    r'(?:\s*,\s*(.*?))?\s*\.?\s*$', re.I)

PREC = re.compile(r'(\d+)\s+appearing before\s+((?:\d+|and|\s)+?)\s*(?:,|in row major order)',
                  re.I)


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'\([^()]*\)\s*\.?\s*$', '', nm).strip()      # the parenthetical gloss
    nm = re.sub(r'(?<=[\dn])\s*[xX]\s*(?=[\dn])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = NAME.search(nm)
    if not m:
        return None
    W = int(m.group(1) or m.group(2))
    trans = m.group(1) is None
    alpha = int(m.group(3))
    self_too = bool(m.group(4))
    if int(m.group(5)) != alpha:
        return None
    D = []
    for w in re.findall(_W1, m.group(6).lower()):
        D += CLASS[w]
    D = sorted(set(D))
    if trans:
        D = sorted({(b, a) for a, b in D})
    # the clash relation is symmetric, so an offset and its negative name the same pairs;
    # transposing can turn (1,-1) into (-1,1), and without this the two would be read as
    # different directions and one of them lost
    D = sorted({(-a, -b) if (a < 0 or (a == 0 and b < 0)) else (a, b) for a, b in D})
    tail = (m.group(7) or '').strip().rstrip('.')
    tl0 = bool(re.search(r'top left element zero', tail, re.I))
    prec = {}
    for g in PREC.finditer(tail):
        v = int(g.group(1))
        ws = [int(x) for x in g.group(2).replace('and', ' ').split()]
        for w in ws:
            prec.setdefault(w, set()).add(v)
    rest = re.sub(r'top left element zero', '', tail, flags=re.I)
    rest = PREC.sub('', rest)
    rest = re.sub(r'in row major order|\band\b|,|\s+', '', rest, flags=re.I)
    if rest:
        return None
    if prec and trans:
        return None            # row major order is not the order this walk visits cells
    if W < 1 or not D:
        return None
    return {'W': W, 'alpha': alpha, 'dirs': D, 'self': self_too, 'tl0': tl0,
            'prec': {k: sorted(v) for k, v in prec.items()}, 'trans': trans, 'frac': 1}


def build(p, cap=40000):
    W, A = p['W'], p['alpha'] + 1
    if A ** W > 40 * cap:
        return None
    D = [tuple(t) for t in p['dirs']]
    s = p['alpha']
    self_too = p['self']
    prec = {int(k): set(v) for k, v in p['prec'].items()}
    named = sorted(set(prec) | {v for vs in prec.values() for v in vs})
    bit = {v: 1 << i for i, v in enumerate(named)}
    FULL = (1 << len(named)) - 1

    def clash(a, b):
        return a + b == s or (self_too and a == b)

    def rowok(r):
        for di, dj in D:
            if di == 0:
                for j in range(W):
                    k = j + dj
                    if 0 <= k < W and clash(r[j], r[k]):
                        return False
        return True

    def pairok(r, t):
        for di, dj in D:
            if di == 0:
                continue
            for j in range(W):
                k = j + dj
                if 0 <= k < W and clash(r[j], t[k]):
                    return False
        return True

    def scan(row, seen):
        """the seen-set after writing `row', or None if a precedence is broken"""
        for v in row:
            b = bit.get(v)
            if b is None or seen & b:
                continue
            for u in prec.get(v, ()):
                if not seen & bit[u]:
                    return None
            seen |= b
        return seen

    rows = [r for r in product(range(A), repeat=W) if rowok(r)]
    if not rows:
        return [], [], [], 0
    # Which rows may FOLLOW a given one is a per-position condition, so it is decided by bit
    # operations rather than by scanning every pair: at[k][v] is the set of rows carrying v at
    # position k, held as one integer, and the rows barred by r are the union of the at[k][v]
    # over the (k, v) its own entries clash with. The pairwise scan is quadratic in the row
    # count and is what kept the wider entries of this family out of reach.
    R = len(rows)
    at = [[0] * A for _ in range(W)]
    for i, r in enumerate(rows):
        for k in range(W):
            at[k][r[k]] |= 1 << i
    ALL = (1 << R) - 1
    succ = []
    for r in rows:
        barred = 0
        for di, dj in D:
            if di == 0:
                continue
            for j in range(W):
                k = j + dj
                if not 0 <= k < W:
                    continue
                for x in range(A):
                    if clash(r[j], x):
                        barred |= at[k][x]
        good = ALL & ~barred
        out = []
        while good:
            low = good & -good
            out.append(low.bit_length() - 1)
            good ^= low
        succ.append(out)
    scantab = [[scan(u, sn) for sn in range(FULL + 1)] for u in rows]
    idx, order, adj, start = {}, [], [], []

    def push(st):
        if st not in idx:
            idx[st] = len(order)
            order.append(st)
            adj.append(None)
            start.append(0)
        return idx[st]

    for r in rows:
        if p['tl0'] and r[0] != 0:
            continue
        sn = scan(r, 0)
        if sn is None:
            continue
        start[push((r, sn))] = 1
        if len(order) > cap:
            return None
    rowidx = {r: i for i, r in enumerate(rows)}
    t = 0
    while t < len(order):
        r, sn = order[t]
        row = []
        for ui in succ[rowidx[r]]:
            v = scantab[ui][sn]
            if v is None:
                continue
            row.append(push((rows[ui], v)))
        adj[t] = row
        t += 1
        if len(order) > cap:
            return None
    n = len(order)
    # states with the same future are merged; the count iota^T M^n tau is unchanged and the
    # annihilation test, whose length is governed by the state count, gets much shorter
    return lumpauto.lump(adj, start[:n], [1] * n)


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
