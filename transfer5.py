#!/usr/bin/env python3
"""Transfer matrix for the Hardin neighbour-count families.

    Number of n X K 0..m arrays with every element equal|unequal to <set> <neighbourhood>
    adjacent elements [, with upper left element zero].

For each cell the condition counts how many of its neighbours carry the same value (or a
different value) and asks that the count lie in a stated set. A neighbourhood reaching one
row up and one row down makes the condition span THREE consecutive rows, so the state is a
window of two rows. Unlike the earlier families the boundary rows matter: the first row has
no row above it and the last none below, so the walk needs genuine start and end vectors
rather than all-ones.

    a(n) = start^T P^(n-2) end   for n >= 2,

where start(r,s) says row r satisfies the condition with nothing above it, the edge
(r,s) -> (s,t) says row s satisfies it with r above and t below, and end(r,s) says row s
satisfies it with nothing below.
"""
import re
from itertools import product

KING = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
HDA = [(0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]          # horiz, diag, antidiag
HV = [(0, -1), (0, 1), (-1, 0), (1, 0)]                              # horiz, vert

NAME = re.compile(
    r'Number of\s+n\s*X\s*(\d+)\s*(?:0\.\.(\d+)|binary)\s*arrays?\s*with every element\s+'
    r'(equal|unequal)\s+to\s+([0-9,\s]+?(?:\s*or\s*\d+)?)\s+'
    r'(king-move|horizontally, diagonally or antidiagonally|horizontally or vertically)'
    r'\s+adjacent elements?(,\s*with upper left element zero)?\s*\.?\s*$', re.I)


def parse_name(nm):
    norm = re.sub(r'(?<=[\dn)])\s*[xX]\s*(?=[\dn(])', ' X ', nm)
    norm = re.sub(r'\s+', ' ', norm).strip()
    m = NAME.search(norm)
    if not m:
        return None
    K = int(m.group(1))
    alpha = 1 if m.group(2) is None else int(m.group(2))
    same = m.group(3).lower() == 'equal'
    counts = frozenset(int(v) for v in re.findall(r'\d+', m.group(4)))
    nb = {'king-move': KING,
          'horizontally, diagonally or antidiagonally': HDA,
          'horizontally or vertically': HV}[m.group(5).lower()]
    ul0 = bool(m.group(6))
    return K, alpha, same, counts, nb, ul0


def _ok_row(win, mid, K, same, counts, nb):
    """Does every cell of row `mid` of the window satisfy the count condition?

    `win` is a list of rows; rows outside it simply contribute no neighbours, which is
    exactly what the boundary of the array does.
    """
    for j in range(K):
        v = win[mid][j]
        c = 0
        for di, dj in nb:
            i2, j2 = mid + di, j + dj
            if 0 <= i2 < len(win) and 0 <= j2 < K:
                w = win[i2][j2]
                if (w == v) if same else (w != v):
                    c += 1
        if c not in counts:
            return False
    return True


def build(K, alpha, same, counts, nb, ul0):
    rows = list(product(range(alpha + 1), repeat=K))
    st = [(r, s) for r in rows for s in rows]
    idx = {p: i for i, p in enumerate(st)}
    S = len(st)
    start = [0] * S
    end = [0] * S
    adj = [[] for _ in range(S)]
    for i, (r, s) in enumerate(st):
        if (not ul0 or r[0] == 0) and _ok_row([r, s], 0, K, same, counts, nb):
            start[i] = 1
        if _ok_row([r, s], 1, K, same, counts, nb):
            end[i] = 1
        for t in rows:
            if _ok_row([r, s, t], 1, K, same, counts, nb):
                adj[i].append(idx[(s, t)])
    return st, adj, start, end


def one_row(K, alpha, same, counts, nb, ul0):
    n = 0
    for r in product(range(alpha + 1), repeat=K):
        if ul0 and r[0] != 0:
            continue
        if _ok_row([r], 0, K, same, counts, nb):
            n += 1
    return n


def matvec(adj, v):
    return [sum(v[s] for s in row) for row in adj]


def terms(adj, start, end, N):
    """[a(2), a(3), ...] = start^T P^j end for j = 0..N."""
    v = end[:]
    out = []
    for _ in range(N + 1):
        out.append(sum(start[i] * v[i] for i in range(len(v))))
        v = matvec(adj, v)
    return out


def threshold(adj, start, end, coeffs, order, S):
    """Smallest t with the recurrence holding for every n > t, or None."""
    v = end[:]
    powers = [v]
    for _ in range(order):
        v = matvec(adj, v)
        powers.append(v)
    w = powers[order][:]
    for i, c in coeffs.items():
        p = powers[order - i]
        for j in range(len(w)):
            w[j] -= c * p[j]
    us = []
    zeros = 0
    j = 0
    while zeros < S + 1 and j <= 3 * S + order + 8:
        u = sum(start[i] * w[i] for i in range(len(w)))
        us.append(u)
        zeros = zeros + 1 if u == 0 else 0
        if not any(w):
            zeros = S + 1
            break
        w = matvec(adj, w)
        j += 1
    if zeros < S + 1:
        return None
    last = max((i for i, u in enumerate(us) if u != 0), default=-1)
    return order + 1 + last          # a(n) index: the j-th value is n = j + 2 + order
