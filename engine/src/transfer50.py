#!/usr/bin/env python3
"""`Number of n X W integer arrays with each element equal to the number of <directions>
neighbors <predicate>.'

Every entry of the array is required to COUNT its own neighbours of a stated kind: the
neighbours in the named directions that are zero, or equal to a fixed value, or smaller than
the entry, or exactly one smaller, and so on. The array is therefore self-referential, but only
locally: the neighbours of a cell lie in the row above, its own row and the row below, so a
window of three consecutive rows decides the condition for the middle one.

The alphabet is bounded even when the entry says `integer arrays': an entry is a count of
neighbours in the named directions, of which there are two per direction, so every entry lies
in `0..2d' with `d' the number of directions named.

The state is the pair (row above, current row), the row above allowed to be absent, and a step
appends a row and settles the condition for the middle row of the window it completes. The
condition for the LAST row is settled by the end vector, with nothing below it --- so the end
vector is not the all-ones vector, and a row that only satisfies its condition when something
is written below it does not finish an array.
"""
import re

import namecanon
import transfer19

CLASS = {'horizontal': [(0, -1), (0, 1)], 'vertical': [(-1, 0), (1, 0)],
         'diagonal': [(-1, -1), (1, 1)], 'antidiagonal': [(-1, 1), (1, -1)]}
_W1 = r'(?:horizontal|vertical|antidiagonal|diagonal)'

NAME = re.compile(
    r'Number of\s+(?:n\s*X\s*(\d+)|(\d+)\s*X\s*n)\s+(?:0\.\.(\d+)|integer)\s*arrays with each '
    r'element equal to the number\s+(?:of\s+|its\s+)?(' + _W1 +
    r'(?:[, ]+(?:or |and )?' + _W1 + r')*)\s+(zero\s+)?neighbors\s*(.*?)\s*\.?\s*$', re.I)


def _pred(zero, tail):
    tail = re.sub(r'\s+', ' ', tail).strip().lower()
    if zero:
        return ('zero', 0) if not tail else None
    m = re.fullmatch(r'equal to (\d+)', tail)
    if m:
        return ('eqk', int(m.group(1)))
    for pat, key in ((r'less than or equal to itself', 'le'),
                     (r'less than itself', 'lt'),
                     (r'greater than or equal to itself', 'ge'),
                     (r'greater than itself', 'gt'),
                     (r'not equal to itself', 'ne'),
                     (r'equal to itself', 'eq'),
                     (r'exactly one smaller than itself', 'sm1'),
                     (r'exactly one larger than itself', 'lg1'),
                     (r'differing from itself by exactly one', 'd1')):
        if re.fullmatch(pat, tail):
            return (key, 0)
    return None


TEST = {
    'zero': lambda nb, v, k: nb == 0,
    'eqk': lambda nb, v, k: nb == k,
    'lt': lambda nb, v, k: nb < v,
    'le': lambda nb, v, k: nb <= v,
    'gt': lambda nb, v, k: nb > v,
    'ge': lambda nb, v, k: nb >= v,
    'ne': lambda nb, v, k: nb != v,
    'eq': lambda nb, v, k: nb == v,
    'sm1': lambda nb, v, k: nb == v - 1,
    'lg1': lambda nb, v, k: nb == v + 1,
    'd1': lambda nb, v, k: nb == v - 1 or nb == v + 1,
}


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn])\s*[xX]\s*(?=[\dn])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = NAME.search(nm)
    if not m:
        return None
    W = int(m.group(1) or m.group(2))
    trans = m.group(1) is None
    words = re.findall(r'antidiagonal|diagonal|horizontal|vertical', m.group(4).lower())
    if not words:
        return None
    D = []
    for w in dict.fromkeys(words):
        D += CLASS[w]
    if trans:
        D = [(b, a) for a, b in D]
    pr = _pred(bool(m.group(5)), m.group(6) or '')
    if pr is None or W < 1:
        return None
    alpha = int(m.group(3)) if m.group(3) else len(D)
    return {'W': W, 'alpha': alpha, 'dirs': sorted(set(D)), 'pred': pr[0], 'k': pr[1],
            'trans': trans, 'frac': 1}


def build(p, cap=40000):
    W, A = p['W'], p['alpha'] + 1
    D = [tuple(t) for t in p['dirs']]
    f = TEST[p['pred']]
    k = p['k']
    if A ** W > 8 * cap:
        return None

    def okrow(prev, cur, nxt):
        """the condition for every cell of `cur' in the window (prev, cur, nxt)"""
        for j in range(W):
            v = cur[j]
            c = 0
            for di, dj in D:
                b = j + dj
                if not (0 <= b < W):
                    continue
                r = cur if di == 0 else (prev if di < 0 else nxt)
                if r is None:
                    continue
                if f(r[b], v, k):
                    c += 1
            if c != v:
                return False
        return True

    rows = []
    stack = [()]
    while stack:                                    # every word of length W over the alphabet
        t = stack.pop()
        if len(t) == W:
            rows.append(t)
            continue
        for v in range(A):
            stack.append(t + (v,))
    idx, order, adj, start, end = {}, [], [], [], []

    def push(st):
        if st not in idx:
            idx[st] = len(order)
            order.append(st)
            adj.append(None)
            start.append(0)
            end.append(0)
        return idx[st]

    # the empty window is a state of its own, so that a walk of no steps is the EMPTY array
    # and the entries whose offset is 0 are reachable
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
    start[0] = 1
    n = len(order)
    return adj, start[:n], end[:n], n


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
