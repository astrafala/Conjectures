#!/usr/bin/env python3
"""Transfer matrix for the Hardin pattern-avoidance array families.

    Number of n X K 0..m arrays avoiding <h> [and <h2>] horizontally
                                 and <v> [and <v2>] vertically.

The horizontal patterns constrain consecutive entries WITHIN a row, so they select which
rows are admissible at all. The vertical patterns constrain consecutive entries within a
column, so with patterns of length L they involve L consecutive rows: the transfer state is
therefore a window of L-1 rows, and a step appends one more.

With V the admissible rows and L = 3 (the common case) the state is a pair (r,s) of
admissible rows, the step (r,s) -> (s,t) is allowed when no column j has
(r_j, s_j, t_j) equal to a forbidden vertical pattern, and

    a(n) = 1^T P^(n-2) 1     for n >= 2,      a(1) = |V|.

For the transposed names ("Number of K X n ... arrays") the array has K rows and n columns,
so the roles of the two directions swap and the same code applies to columns.
"""
import re
from itertools import product

NAME = re.compile(
    r'Number of\s+(?:(n)\s*X\s*(\d+)|(\d+)\s*X\s*(n))\s*0\.\.(\d+)\s*arrays?\s+avoiding\s+'
    r'(.+?)\s+horizontally\s+and\s+(.+?)\s+vertically\s*\.?\s*$', re.I)


def _pats(s):
    """'0 0 1 and 1 1 0' -> [(0,0,1),(1,1,0)]"""
    out = []
    for part in re.split(r'\s+and\s+', s.strip()):
        digs = re.findall(r'\d', part)
        if not digs:
            return None
        out.append(tuple(int(d) for d in digs))
    return out


REFUSE = re.compile(r'\bthe pattern\b|[a-yA-Y]\s*[+-]\s*\d|\bz\b', re.I)


def parse_name(nm):
    if REFUSE.search(nm):
        return None                      # a parametrised pattern such as "z+1 z+1 z"
    norm = re.sub(r'(?<=[\dn)])\s*[xX]\s*(?=[\dn(])', ' X ', nm)
    norm = re.sub(r'\s+', ' ', norm).strip()
    m = NAME.search(norm)
    if not m:
        return None
    if m.group(1):                       # n X K : n counts rows, K columns
        K = int(m.group(2)); transposed = False
    else:                                # K X n : K rows, n columns -> transpose
        K = int(m.group(3)); transposed = True
    alpha = int(m.group(5))
    H = _pats(m.group(6)); V = _pats(m.group(7))
    if H is None or V is None:
        return None
    if transposed:
        H, V = V, H                      # after transposing, the two directions swap
    lens = {len(p) for p in H} | {len(p) for p in V}
    if len(lens) != 1:
        return None                      # mixed pattern lengths: refuse
    L = lens.pop()
    if L < 2:
        return None
    return K, alpha, H, V, L


def rows_ok(K, alpha, H, L):
    """Rows of length K with no forbidden horizontal pattern."""
    out = []
    for r in product(range(alpha + 1), repeat=K):
        if all(tuple(r[j:j + L]) not in H for j in range(K - L + 1)):
            out.append(r)
    return out


def build(K, alpha, H, V, L):
    """State = window of L-1 admissible rows; step appends one row."""
    rows = rows_ok(K, alpha, H, L)
    if not rows:
        return [], []
    st = list(product(rows, repeat=L - 1))
    idx = {s: i for i, s in enumerate(st)}
    Vset = set(V)
    adj = []
    for w in st:
        row = []
        for t in rows:
            col = w + (t,)
            if all(tuple(col[i][j] for i in range(L)) not in Vset for j in range(K)):
                row.append(idx[w[1:] + (t,)])
        adj.append(row)
    return st, adj
