#!/usr/bin/env python3
"""Permutations of a grid with a bounded index change.

    Number of (n+1) X (3+1) arrays of permutations of 0..n*4+3 with each element having
    index change (+-,+-) 0,0 1,1 or 1,2.

The array holds each of 0..LW-1 once. The value v has a HOME cell, its position in the plain
row-major filling: row v//W, column v%W. Placing v at cell (i,j) changes its index by
(i - v//W, j - v%W), and the entry lists which (|di|, |dj|) pairs are allowed. So the object
counted is a perfect matching between cells and values, with cell (i,j) joined to the value
whose home is (hi,hj) exactly when (|i-hi|, |j-hj|) is on the list.

That is a walk. Let R be the largest allowed |di|. A value with home row h can only be placed
in rows h-R..h+R, so after the positions of rows 0..i have been filled every home row up to
i-R is used up, and the only home rows that can be partly used are i-R+1,...,i+R. The state is
therefore the tuple of "which values are already taken" bitmasks for those 2R home rows, one
step fills one row of positions, and the row that closes must come out full. Nonexistent home
rows (before the first, after the last) are carried as FULL, which is why the walk starts and
ends at the same state.

Verified against the entries by brute force before anything else was built: for the 2 X 3 case
of A263960 the enumeration over all 720 permutations gives 20, the entry's first term, and the
3 X 2 case gives 9, the first term of its transposed companion A263966.
"""
import re
from itertools import product

import namecanon

NAME = re.compile(
    r'Number of\s+\(?\s*(n\s*\+\s*\d+|n|\d+\s*\+\s*\d+|\d+)\s*\)?\s*X\s*'
    r'\(?\s*(n\s*\+\s*\d+|n|\d+\s*\+\s*\d+|\d+)\s*\)?\s+arrays of permutations of\s+'
    r'0\.\.[^ ]+\s+with each element having (directed )?index change\s*'
    r'(\(\+-,\+-\)|\+-\(\.,\.\))?\s*([-\d,\s]+(?:or\s*[-\d,\s]+)?)', re.I)


def _dv(s):
    s = s.replace(' ', '')
    if 'n' in s:
        return ('n', int(s.split('+')[1]) if '+' in s else 0)
    if '+' in s:
        return ('c', sum(int(x) for x in s.split('+')))
    return ('c', int(s))


def parse_name(nm):
    nm = namecanon.canon(nm)
    norm = re.sub(r'(\bn|\d|\))\s*[xX]\s*(?=[\d(n])', r'\1 X ', nm)
    norm = re.sub(r'\s+', ' ', norm).strip()
    m = NAME.search(norm)
    if not m:
        return None
    d1, d2 = _dv(m.group(1)), _dv(m.group(2))
    # TWO conventions, and they are not the same set. "(+-,+-) a,b" signs each component
    # independently, so it means (+-a, +-b). "+-(.,.) a,b" signs the PAIR, so it means only
    # (a,b) and (-a,-b) -- and there the second component may be written negative, as in
    # "2,-2". Reading the second form as the first drops the sign, which is what the DATA
    # check caught: thirteen of twenty-three entries in the first sample disagreed.
    # THREE conventions, and they give three different sets:
    #   "(+-,+-) a,b"   each coordinate signed independently -> (+-a, +-b)
    #   "+-(.,.) a,b"   the PAIR signed                      -> (a,b) and (-a,-b)
    #   "directed a,b"  taken literally                      -> (a,b) only
    # Each was checked by brute force on its own smallest case before use, because a check
    # on one example only settles the convention that example happens to use.
    directed = bool(m.group(3))
    mark = m.group(4) or ''
    if directed and mark:
        return None
    kind = 'directed' if directed else ('indep' if mark.startswith('(') else 'pair')
    if not directed and not mark:
        return None
    prs = re.findall(r'(-?\d+)\s*,\s*(-?\d+)', m.group(5))
    if not prs:
        return None
    A = set()
    for x, y in prs:
        x, y = int(x), int(y)
        if kind == 'indep':
            for sx in ({x} if x == 0 else {x, -x}):
                for sy in ({y} if y == 0 else {y, -y}):
                    A.add((sx, sy))
        elif kind == 'pair':
            A.add((x, y)); A.add((-x, -y))
        else:
            A.add((x, y))
    if d1[0] == 'n' and d2[0] == 'c':
        walk, W = 'rows', d2[1]
    elif d2[0] == 'n' and d1[0] == 'c':
        walk, W = 'cols', d1[1]
        A = {(y, x) for x, y in A}          # the walk runs along columns: transpose
    else:
        return None
    if W < 1:
        return None
    return {'walk': walk, 'fixed': W, 'base': (d1[1] if walk == 'rows' else d2[1]),
            'allowed': sorted(A), 'R': max(abs(x) for x, _ in A), 'kind': kind}


def build(p, cap=40000):
    W, A, R = p['fixed'], set(map(tuple, p['allowed'])), p['R']
    if R == 0:
        # no value leaves its home row: every row is an independent permutation of itself
        cols = [[hj for hj in range(W) if (0, j - hj) in A] for j in range(W)]
        rows = []
        for pick in product(*cols):
            if len(set(pick)) == W:
                rows.append(pick)
        k = len(rows)
        # a(L) = k^L: one state with k parallel self-loops
        return [[0] * k], [1], [1], 1, 1
    nm = 2 * R
    FULL = (1 << W) - 1
    if (1 << (W * nm)) > cap:
        return None
    states = list(product(range(1 << W), repeat=nm))
    idx = {s: i for i, s in enumerate(states)}
    S = len(states)
    adj = [[] for _ in range(S)]
    # groups g = 0..2R index the home rows i-R+1 .. i+R+1 available to position row i+1;
    # its own row is g = R-1+1 = R, so |di| = |R - g|
    for st in states:
        masks = list(st) + [0]
        out = []

        def rec(j, ms):
            if j == W:
                if ms[0] != FULL:
                    return
                out.append(idx[tuple(ms[1:])])
                return
            for g in range(nm + 1):
                di = R - g
                for hj in range(W):
                    if (di, j - hj) not in A:
                        continue
                    if ms[g] >> hj & 1:
                        continue
                    ms2 = list(ms)
                    ms2[g] |= 1 << hj
                    rec(j + 1, ms2)
        rec(0, masks)
        adj[idx[st]] = sorted(out)
    start = [0] * S
    end = [0] * S
    # after position rows 0..i the state lists home rows i-R+1..i+R. Before any row (i=-1)
    # that is home rows -R..R-1: the negative ones do not exist and are carried FULL, the
    # rest are untouched. After the last row (i=L-1) it is home rows L-R..L+R-1: the first R
    # must have been used up and the ones past the end must never have been drawn from. The
    # two conditions coincide, so the walk starts and ends at the same state.
    init = tuple([FULL] * R + [0] * R)
    start[idx[init]] = 1
    end[idx[init]] = 1
    return adj, start, end, S, 1


def matvec(adj, v):
    return [sum(v[k] for k in row) for row in adj]


def terms(adj, start, end, N):
    """terms[j] = number of admissible arrays with j lines."""
    v = end[:]
    out = []
    for _ in range(N + 1):
        out.append(sum(start[i] * v[i] for i in range(len(v))))
        v = matvec(adj, v)
    return out                        # out[L] = the count for L lines
