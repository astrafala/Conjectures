#!/usr/bin/env python3
r"""`Number of (n+1) X (n+1) -m..m symmetric matrices with every 2 X 2 subblock having sum zero
and two or three distinct values.'

Both sides of these matrices grow with $n$, so there is no slice of bounded width to walk along
and no transfer matrix in the usual sense. There does not have to be. The sum-zero condition is
linear and solves completely:

    put y(i,j) = (-1)^(i+j) x(i,j); then the four terms of a 2 X 2 subblock of x alternate in
    sign, so their sum is the mixed second difference of y, and it vanishes for every subblock
    exactly when y(i,j) = f(i) + g(j).

Symmetry forces f - g to be constant, and absorbing half of it into each,

    x(i,j) = (-1)^(i+j) * (u_i + u_j) / 2 ,

where u is a sequence of integers all of one parity. Setting j = i shows u_i = x(i,i): the
sequence IS the diagonal of the matrix, so the correspondence is a bijection, and the entry's
range condition -m..m on every entry is just |u_i| <= m.

What is left is one-dimensional but not local. The four entries of the subblock at (i,j) are
built from the consecutive pair (u_i, u_{i+1}) and the consecutive pair (u_j, u_{j+1}), for ALL
i and j -- so the number of distinct values must be right for every ORDERED PAIR of consecutive
pairs of the sequence, not just for neighbouring ones. The consecutive pairs used must form a
clique in a fixed finite graph.

Carrying the set of pairs used is hopeless -- it is exponential. Carrying what that set FORBIDS
is not: the pairs still available are the intersection of the neighbourhoods of the pairs
already used, and those intersections are few. The state is the last value of the sequence
together with that intersection.
"""
import re
from fractions import Fraction

import namecanon
import transfer19

NUM = {'one': 1, 'two': 2, 'three': 3, 'four': 4}
NAME = re.compile(
    r'^Number of\s+\((n)\s*\+\s*(\d+)\)\s*X\s*\((n)\s*\+\s*(\d+)\)\s+'
    r'-(\d+)\.\.(\d+)\s+symmetric matrices with every\s+2\s*X\s*2\s+subblock having sum zero '
    r'and\s+((?:one|two|three|four)(?:[, ]+(?:or\s+)?(?:one|two|three|four))*)\s+'
    r'distinct values\s*\.?$', re.I)


def parse_name(nm):
    nm = namecanon.canon(nm)
    s = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = NAME.match(s)
    if not m:
        return None
    if m.group(2) != m.group(4):
        return None
    lo, hi = int(m.group(5)), int(m.group(6))
    if lo != hi or lo < 1:
        return None
    D = frozenset(NUM[w.lower()] for w in re.findall(r'one|two|three|four', m.group(7), re.I))
    if not D:
        return None
    return {'m': lo, 'D': D, 'off': int(m.group(2)), 'frac': 1}


def _count(p, q):
    """How many distinct entries the 2 X 2 subblock built from the two consecutive pairs has."""
    a, b = p
    c, d = q
    return len({Fraction(a + c, 2), Fraction(-(a + d), 2),
                Fraction(-(b + c), 2), Fraction(b + d, 2)})


def build(p, cap=400000):
    m, D = p['m'], p['D']
    vals = {par: [v for v in range(-m, m + 1) if (v - par) % 2 == 0] for par in (0, 1)}
    if not vals[0] and not vals[1]:
        return None
    if (2 * m + 2) ** 2 > 40 * cap:
        return None
    P = {par: [(a, b) for a in vals[par] for b in vals[par]] for par in (0, 1)}
    R = {par: {q: frozenset(r for r in P[par] if _count(q, r) in D) for q in P[par]}
         for par in (0, 1)}
    A0 = {par: frozenset(q for q in P[par] if q in R[par][q]) for par in (0, 1)}

    idx, order, adj = {}, [], []

    def push(st):
        if st not in idx:
            idx[st] = len(order)
            order.append(st)
            adj.append(None)
        return idx[st]

    push(None)
    t = 0
    while t < len(order):
        st = order[t]
        out = []
        if st is None:
            for par in (0, 1):
                for v in vals[par]:
                    out.append(push((par, v, A0[par])))
        else:
            par, v, A = st
            for w in vals[par]:
                q = (v, w)
                if q not in A:
                    continue
                out.append(push((par, w, A & R[par][q])))
        adj[t] = out
        t += 1
        if len(order) > cap:
            return None
    n = len(order)
    sv = [0] * n
    sv[0] = 1
    return adj, sv, [1] * n, n


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
