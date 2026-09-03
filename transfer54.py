#!/usr/bin/env python3
"""`Number of W X n 0..m arrays with no element equal to any value at offset (-2,-2) (-1,0) or
(-1,1) and new values introduced in order 0..m.'

A cell is forbidden to equal the cells sitting at a short list of fixed offsets from it, and
the array is then counted up to renaming: the closing clause says that, reading the array, a
letter may appear for the first time only when every smaller letter already has.

Two things make this easy once they are noticed.

First, the count does not depend on the ORDER in which the array is read. The condition tests
only whether two cells are equal, so it is invariant under permuting the alphabet, and each
class of arrays under renaming contains exactly one array whose first appearances run
`0,1,2,...' in any fixed reading order. So the entry counts CLASSES, whatever order is meant,
and the usual falling-factorial inversion applies: with `N_j' the classes on exactly `j'
letters and `L_i' the admissible arrays over an alphabet of `i' letters,

    L_i = sum_j N_j i(i-1)...(i-j+1),   a = N_1 + ... + N_K = (1^T F^{-1}) L .

Second, equality is symmetric, so an offset and its negative forbid the same pairs. Normalising
every offset to point BACKWARDS along the direction the array grows makes each pair tested
exactly once, from the later of its two cells, and the state is then the window of the last few
slices --- rows for an `n X W' entry, columns for a `W X n' one.
"""
import re
from fractions import Fraction
from itertools import product

import namecanon
import transfer19

SHAPE = r'(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))\s*X\s*(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))'

NAME = re.compile(
    r'Number of\s+' + SHAPE + r'\s*0\.\.(\d+)\s*arrays with no element equal to any value at '
    r'offsets?\s+((?:\(\s*-?\d+\s*,\s*-?\d+\s*\)[\s,]*(?:or\s*)?)+)'
    r'\s*and new values introduced in order 0\.\.(\d+)\s*\.?\s*$', re.I)


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
    if int(m.group(9)) != alpha:
        return None
    offs = []
    for g in re.finditer(r'\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)', m.group(8)):
        di, dj = int(g.group(1)), int(g.group(2))
        s, q = (dj, di) if trans else (di, dj)      # (slice shift, position shift)
        if s > 0 or (s == 0 and q > 0):
            s, q = -s, -q                           # equality is symmetric
        if s == 0 and q == 0:
            return None
        offs.append((s, q))
    offs = sorted(set(offs))
    if not offs or W < 1:
        return None
    return {'W': W, 'alpha': alpha, 'K': alpha + 1, 'offs': offs, 'trans': trans, 'frac': 1}


def _weights(K):
    F = [[Fraction(0)] * (K + 1) for _ in range(K + 1)]
    for i in range(1, K + 1):
        for j in range(1, K + 1):
            v = Fraction(1)
            for t in range(j):
                v *= (i - t)
            F[i][j] = v
    A = [[F[i][j] for i in range(1, K + 1)] + [Fraction(1)] for j in range(1, K + 1)]
    n = K
    for col in range(n):
        piv = next(t for t in range(col, n) if A[t][col] != 0)
        A[col], A[piv] = A[piv], A[col]
        d = A[col][col]
        A[col] = [x / d for x in A[col]]
        for t in range(n):
            if t != col and A[t][col] != 0:
                f = A[t][col]
                A[t] = [x - f * y for x, y in zip(A[t], A[col])]
    return [A[t][n] for t in range(n)]


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def _one(W, A, offs, cap):
    L = max(-s for s, _ in offs) or 1
    same = [q for s, q in offs if s == 0]
    back = [(s, q) for s, q in offs if s < 0]
    slices = []
    for r in product(range(A), repeat=W):
        if all(not (0 <= p + q < W) or r[p] != r[p + q] for p in range(W) for q in same):
            slices.append(r)
    idx, order, adj = {}, [], []

    def push(st):
        if st not in idx:
            idx[st] = len(order)
            order.append(st)
            adj.append(None)
        return idx[st]

    push((None,) * L)
    t = 0
    while t < len(order):
        win = order[t]
        row = []
        for x in slices:
            ok = True
            for s, q in back:
                r = win[L + s]                    # s is negative: L-1 is the last slice
                if r is None:
                    continue
                for p in range(W):
                    b = p + q
                    if 0 <= b < W and x[p] == r[b]:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                row.append(push(win[1:] + (x,)))
        adj[t] = row
        t += 1
        if len(order) > cap:
            return None, None
    return adj, len(order)


def build(p, cap=40000):
    W, K, offs = p['W'], p['K'], [tuple(t) for t in p['offs']]
    c = _weights(K)
    den = 1
    for x in c:
        den = den * x.denominator // _gcd(den, x.denominator)
    w = [int(x * den) for x in c]
    adj, start, base = [], [], 0
    for A in range(1, K + 1):
        if A ** W > 40 * cap:
            return None
        a_i, S_i = _one(W, A, offs, cap)
        if a_i is None:
            return None
        adj.extend([[k + base for k in row] for row in a_i])
        s_i = [0] * S_i
        s_i[0] = w[A - 1]
        start.extend(s_i)
        base += S_i
        if base > cap:
            return None
    return adj, start, [1] * base, base, den


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
