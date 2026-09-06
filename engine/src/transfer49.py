#!/usr/bin/env python3
"""`Number of (n+1) X W 0..m arrays CONTAINING ALL VALUES 0..m with every K X K subblock
having <k> distinct values, and new values 0..m introduced in row major order.'

The subblock condition counts how many DISTINCT values a window holds, so it is untouched by
renaming the alphabet, and the closing clause says the array is the canonical representative of
its equality pattern. What separates this family from its neighbours is the words `containing
all values 0..m': the pattern must use EVERY letter, not at most every letter.

Write `N_j' for the number of admissible patterns on exactly `j' letters and `L_i' for the
number of admissible arrays over an alphabet of `i' letters. An array over `i' letters is a
pattern together with an injection of its letters into the alphabet, so

    L_i = sum_j N_j i(i-1)...(i-j+1),

a triangular system with unit diagonal. The neighbouring families want `N_1 + ... + N_K' and
so use the row vector `1^T F^{-1}'; this one wants `N_K' alone, and so uses the single row
`e_K^T F^{-1}' of the same inverse. Everything else is shared: each `L_i' is a walk count on
the rows of the array, one edge for each admissible window of `K' consecutive rows.
"""
import re
from fractions import Fraction
from itertools import product

import namecanon
import transfer19

NUM = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7,
       'eight': 8, 'nine': 9}

NAME = re.compile(
    r'Number of\s+(?:\(\s*n\s*\+\s*(\d+)\s*\)\s*X\s*(\d+)|(\d+)\s*X\s*\(\s*n\s*\+\s*(\d+)\s*\))'
    r'\s*0\.\.(\d+)\s*arrays containing all values 0\.\.(\d+)\s*with every\s+'
    r'(\d+)\s*X\s*(\d+)\s+subblock having\s+(.*?)\s+distinct values,\s*and new values '
    r'0\.\.(\d+)\s+introduced in row major order\s*\.?\s*$', re.I)


def _counts(txt):
    out = set()
    for w in re.findall(r'\w+', txt.lower()):
        if w in ('or', 'and'):
            continue
        v = int(w) if w.isdigit() else NUM.get(w)
        if v is None:
            return None
        out.add(v)
    return out or None


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = NAME.search(nm)
    if not m:
        return None
    if m.group(1):
        W, trans = int(m.group(2)), False
    else:
        W, trans = int(m.group(3)), True
    alpha = int(m.group(5))
    if int(m.group(6)) != alpha or int(m.group(10)) != alpha:
        return None
    K, K2 = int(m.group(7)), int(m.group(8))
    if K != K2 or K < 2:
        return None
    ok = _counts(m.group(9))
    if ok is None or W < 1:
        return None
    return {'W': W, 'alpha': alpha, 'K': alpha + 1, 'blk': K, 'ok': sorted(ok),
            'trans': trans, 'frac': 1}


def _inv_row(K, r):
    """row r of the inverse of the falling-factorial matrix, 1-based"""
    F = [[Fraction(0)] * (K + 1) for _ in range(K + 1)]
    for i in range(1, K + 1):
        for j in range(1, K + 1):
            v = Fraction(1)
            for t in range(j):
                v *= (i - t)
            F[i][j] = v
    A = [[F[i][j] for i in range(1, K + 1)] + [Fraction(1) if j == r else Fraction(0)]
         for j in range(1, K + 1)]
    n = K
    for col in range(n):
        piv = next(t for t in range(col, n) if A[t][col] != 0)
        A[col], A[piv] = A[piv], A[col]
        dd = A[col][col]
        A[col] = [x / dd for x in A[col]]
        for t in range(n):
            if t != col and A[t][col] != 0:
                f = A[t][col]
                A[t] = [x - f * y for x, y in zip(A[t], A[col])]
    return [A[t][n] for t in range(n)]


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def _one(W, A, blk, ok):
    rows = list(product(range(A), repeat=W))
    idx = {r: i for i, r in enumerate(rows)}

    def fits(win):
        for j in range(W - blk + 1):
            vals = {win[t][j + s] for t in range(blk) for s in range(blk)}
            if len(vals) not in ok:
                return False
        return True

    if blk == 2:
        adj = [[idx[s] for s in rows if fits((r, s))] for r in rows]
        return adj, [1] * len(rows), len(rows)
    states = [w for w in product(rows, repeat=blk - 1)]
    si = {w: i for i, w in enumerate(states)}
    adj = [[si[w[1:] + (s,)] for s in rows if fits(w + (s,))] for w in states]
    return adj, [1] * len(states), len(states)


def build(p, cap=40000):
    W, K, blk, ok = p['W'], p['K'], p['blk'], set(p['ok'])
    if (K ** W) ** max(1, blk - 1) > 40 * cap:
        return None
    c = _inv_row(K, K)
    den = 1
    for x in c:
        den = den * x.denominator // _gcd(den, x.denominator)
    w = [int(x * den) for x in c]
    adj, start, base = [], [], 0
    for A in range(1, K + 1):
        a_i, s_i, S_i = _one(W, A, blk, ok)
        adj.extend([[k + base for k in row] for row in a_i])
        start.extend([w[A - 1] * x for x in s_i])
        base += S_i
        if base > cap:
            return None
    return adj, start, [1] * base, base, den


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
