#!/usr/bin/env python3
"""`Number of n X W binary arrays with each 1 adjacent to exactly two other 1s' and
`Number of n X W 0..m arrays with every 1 immediately preceded by 0 to the left or above,
and every 2 immediately preceded by 0 1 to the left or above.'

Two kinds of local clause, both settled inside three consecutive array rows.

An ADJACENCY clause counts, for every cell carrying a stated value, how many of its four
neighbours --- left, right, above, below --- carry another stated value, and requires that
count to be exactly what the entry says. Some entries split the count, asking for so many
vertically and so many horizontally.

A PRECEDENCE clause looks the other way. The PREDECESSORS of a cell are the cell to its left
and the cell above it, those that exist. `Every 1 immediately preceded by 0 to the left or
above' asks that at least one predecessor of each `1' carry a `0' --- so a `1' in the top left
corner, which has no predecessor at all, is forbidden; `no 0 immediately preceded by a 0' asks
that none carry it; `every 2 immediately preceded by 0 1' asks that the two cells to the left,
or the two above, read `0' then `1' in that order; and `preceded by both a 1 and a 0' asks that
the two predecessors show one of each.

The state is the pair (row above, current row). An adjacency clause for a row is settled when
the row BELOW it is written, so the last row of an array is settled by the end vector, with
nothing below it. A precedence clause reaches two rows back and two columns left, all of them
already written, so it is settled as its own row is appended.
"""
import re
from itertools import product

import namecanon
import transfer19

NUM = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6}
SHAPE = r'(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))\s*X\s*(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))'
HEAD = re.compile(r'Number of\s+' + SHAPE + r'\s*(binary|0\.\.(\d+))\s*arrays with\s+'
                  r'(.*?)\s*\.?\s*$', re.I)

ADJ_VH = re.compile(r'^each (\d+) adjacent to exactly (\w+) (\d+) vertically and (\w+) (\d+) '
                    r'horizontally$', re.I)
ADJ = re.compile(r"^each (\d+) adjacent to exactly (\w+) (?:other )?(\d+)'?s?$", re.I)
PRE_SEQ = re.compile(r'^every (\d+) immediately preceded by ((?:\d+ )*\d+) to the left or '
                     r'above$', re.I)
PRE_BOTH = re.compile(r'^every (\d+) immediately preceded by both an? (\d+) and an? (\d+)$',
                      re.I)
NOPRE = re.compile(r'^no (\d+) immediately preceded by an? (\d+)$', re.I)


def _n(w):
    w = w.lower()
    return int(w) if w.isdigit() else NUM.get(w)


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = HEAD.search(nm)
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
    alpha = 1 if m.group(7).lower() == 'binary' else int(m.group(8))
    adj, pre = [], []
    for chunk in re.split(r',\s*and\s+|,\s*|\s+and\s+(?=(?:every|no|each)\b)', m.group(9)):
        c = chunk.strip()
        if not c:
            continue
        g = ADJ_VH.match(c)
        if g:
            v, nv, wv, nh, wh = (int(g.group(1)), _n(g.group(2)), int(g.group(3)),
                                 _n(g.group(4)), int(g.group(5)))
            if nv is None or nh is None:
                return None
            adj.append(('vh', v, nv, wv, nh, wh))
            continue
        g = ADJ.match(c)
        if g:
            v, k, w = int(g.group(1)), _n(g.group(2)), int(g.group(3))
            if k is None:
                return None
            adj.append(('all', v, k, w))
            continue
        g = PRE_SEQ.match(c)
        if g:
            pre.append(('seq', int(g.group(1)), [int(x) for x in g.group(2).split()]))
            continue
        g = PRE_BOTH.match(c)
        if g:
            pre.append(('both', int(g.group(1)), [int(g.group(2)), int(g.group(3))]))
            continue
        g = NOPRE.match(c)
        if g:
            pre.append(('none', int(g.group(1)), [int(g.group(2))]))
            continue
        return None
    if not adj and not pre:
        return None
    if trans and (pre or any(r[0] == 'vh' for r in adj)):
        return None       # `to the left or above' and `vertically' name the array's own axes
    return {'W': W, 'alpha': alpha, 'adj': adj, 'pre': pre, 'trans': trans, 'frac': 1}


def build(p, cap=40000):
    W, A = p['W'], p['alpha'] + 1
    adj, pre = [tuple(r) for r in p['adj']], [tuple(r) for r in p['pre']]
    if A ** W > 8 * cap:
        return None
    rows = list(product(range(A), repeat=W))

    def adjok(prev, cur, nxt):
        for r in adj:
            for j in range(W):
                if cur[j] != r[1]:
                    continue
                if r[0] == 'all':
                    _, v, k, w = r
                    c = 0
                    for q in (j - 1, j + 1):
                        if 0 <= q < W and cur[q] == w:
                            c += 1
                    for row in (prev, nxt):
                        if row is not None and row[j] == w:
                            c += 1
                    if c != k:
                        return False
                else:
                    _, v, nv, wv, nh, wh = r
                    cv = sum(1 for row in (prev, nxt) if row is not None and row[j] == wv)
                    ch = sum(1 for q in (j - 1, j + 1) if 0 <= q < W and cur[q] == wh)
                    if cv != nv or ch != nh:
                        return False
        return True

    def preok(w2, w1, x):
        """the precedence clauses for the row `x', whose two rows above are w1 then x"""
        for kind, v, arg in pre:
            for j in range(W):
                if x[j] != v:
                    continue
                left = x[j - 1] if j > 0 else None
                up = w1[j] if w1 is not None else None
                if kind == 'none':
                    if left == arg[0] or up == arg[0]:
                        return False
                elif kind == 'both':
                    have = [t for t in (left, up) if t is not None]
                    if not all(any(t == a for t in have) for a in arg):
                        return False
                elif len(arg) == 1:
                    if not any(t == arg[0] for t in (left, up) if t is not None):
                        return False
                else:
                    a, b = arg
                    okl = j >= 2 and x[j - 2] == a and x[j - 1] == b
                    oku = (w2 is not None and w1 is not None
                           and w2[j] == a and w1[j] == b)
                    if not (okl or oku):
                        return False
        return True

    idx, order, adjl, end = {}, [], [], []

    def push(st):
        if st not in idx:
            idx[st] = len(order)
            order.append(st)
            adjl.append(None)
            end.append(0)
        return idx[st]

    push((None, None))
    t = 0
    while t < len(order):
        w2, w1 = order[t]
        row = []
        for x in rows:
            if not preok(w2, w1, x):
                continue
            if w1 is not None and not adjok(w2, w1, x):
                continue
            row.append(push((w1, x)))
        adjl[t] = row
        end[t] = 1 if (w1 is None or adjok(w2, w1, None)) else 0
        t += 1
        if len(order) > cap:
            return None
    n = len(order)
    st = [0] * n
    st[0] = 1
    return adjl, st, end[:n], n


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
