#!/usr/bin/env python3
"""Triangular arrays whose ALPHABET grows: a quasi-polynomial, not a walk count.

    Number of K X K X K triangular 0..n arrays with some element plus some adjacent element
    totalling t exactly once,           t = n or n+1

Every other array family in this roster fixes the alphabet and lets the shape grow, so the
count is a walk count in a finite digraph.  Here the SHAPE is fixed --- the triangle has
T = K(K+1)/2 cells and 3*C(K,2) adjacent pairs --- and the alphabet 0..n is what grows.  There
is no digraph to walk, and the sequence is C-finite for a different reason.

Write E for the adjacent pairs.  By inclusion--exclusion on which pairs are satisfied,

    a(n) = sum over nonempty S of E of  (-1)^(|S|-1) |S| N(S),

with N(S) the number of arrays satisfying every pair in S.  N(S) has a closed form.  A pair
(u,v) in S forces x_v = t - x_u, so on each connected component of the graph (V,S) the value of
one cell determines all the others, alternating; a component containing an ODD cycle forces
2x = t and so admits only x = t/2, and only when t is even.  Hence, writing v(S) for the
touched cells, cb and co for the bipartite and the odd components,

    N(S) = (n+1)^(T-v(S)) * B^cb * F^co,
    B = #{c : 0 <= c <= n, 0 <= t-c <= n},        F = [t even and 0 <= t/2 <= n].

B is a polynomial in n and F is a function of n mod 2, so a(n) is a quasi-polynomial of period
2 --- exactly, for every n >= 0, with no threshold.  Writing a(n) = A(n) + (-1)^n C(n), it is
annihilated by (E-1)^(deg A + 1) (E+1)^(deg C + 1), and that is its minimal annihilator, so
every recurrence it satisfies is a multiple of that one and the question is decidable by
polynomial division.

The statistics (|S|, T-v, cb, co) do not depend on n, so the sum over subsets is taken ONCE and
every value of a(n) is then free.  That is what makes the fit and its verification cheap.
"""
import re
from itertools import combinations
from fractions import Fraction

import namecanon

NAME = re.compile(r'^Number of\s+(\d+)\s*X\s*(\d+)\s*X\s*(\d+)\s+triangular\s+0\.\.n\s+arrays'
                  r'\s+with some element plus some adjacent element totalling\s+'
                  r'n(?:\s*([+-])\s*(\d+))?\s+exactly once\s*\.?\s*$', re.I)
# forming the subset statistics costs 2^|E|, and |E| = 3*C(K,2); at K=5 that is 2^30, which is
# not a cap the caller may raise -- it is a property of the entry
MAXEDGES = 20


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn])\s*[xX]\s*(?=[\dn])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = NAME.match(nm)
    if not m:
        return None
    K = int(m.group(1))
    if int(m.group(2)) != K or int(m.group(3)) != K or K < 2:
        return None
    shift = 0
    if m.group(4):
        shift = int(m.group(5)) * (1 if m.group(4) == '+' else -1)
    return {'K': K, 'shift': shift, 'frac': 1}


def cells(K):
    return [(i, j) for i in range(K) for j in range(i + 1)]


def edges(K):
    E = []
    for i in range(K):
        for j in range(i + 1):
            if j + 1 <= i:
                E.append(((i, j), (i, j + 1)))
            if i + 1 < K:
                E.append(((i, j), (i + 1, j)))
                E.append(((i, j), (i + 1, j + 1)))
    return E


def stats(K):
    """{(free, cb, co): signed multiplicity}, summed over every nonempty subset of edges."""
    V = cells(K)
    E = edges(K)
    T = len(V)
    out = {}
    for k in range(1, len(E) + 1):
        sgn = (-1) ** (k - 1) * k
        for S in combinations(E, k):
            par, rel = {}, {}

            def find(x):
                r, p = x, 0
                while par[r] != r:
                    p ^= rel[r]
                    r = par[r]
                return r, p

            touched = sorted({v for e in S for v in e})
            for v in touched:
                par[v], rel[v] = v, 0
            odd = set()
            for u, v in S:
                ru, pu = find(u)
                rv, pv = find(v)
                if ru == rv:
                    if pu == pv:
                        odd.add(ru)
                else:
                    par[ru], rel[ru] = rv, pu ^ pv ^ 1
                    if ru in odd:
                        odd.discard(ru)
                        odd.add(rv)
            roots = {find(v)[0] for v in touched}
            co = len(roots & odd)
            cb = len(roots) - co
            key = (T - len(touched), cb, co)
            out[key] = out.get(key, 0) + sgn
    return out


def build(p, cap=None):
    K = p['K']
    if len(edges(K)) > MAXEDGES:
        return None
    return {'K': K, 'T': len(cells(K)), 'shift': p['shift'], 'stats': stats(K)}


def value(b, n):
    t = n + b['shift']
    B = min(n, t) - max(0, t - n) + 1
    if B < 0:
        B = 0
    F = 1 if (t % 2 == 0 and 0 <= t // 2 <= n) else 0
    tot = 0
    for (free, cb, co), mult in b['stats'].items():
        if co and not F:
            continue
        tot += mult * (n + 1) ** free * B ** cb * F ** co
    return tot


def terms(b, N, off=1):
    return [value(b, off + k) for k in range(N + 1)]


def _interp(xs, ys):
    """Lagrange interpolation, returning exact coefficients low degree first."""
    d = len(xs)
    coef = [Fraction(0)] * d
    for i in range(d):
        num = [Fraction(1)]
        den = Fraction(1)
        for j in range(d):
            if i == j:
                continue
            num = [Fraction(0)] + num
            for k in range(len(num) - 1):
                num[k] -= xs[j] * num[k + 1]
            den *= xs[i] - xs[j]
        for k in range(len(num)):
            coef[k] += Fraction(ys[i]) * num[k] / den
    while coef and coef[-1] == 0:
        coef.pop()
    return coef


def fit(b, off=1):
    """a(n) split as A(n) + (-1)^n C(n), returned as exact coefficient lists."""
    T = b['T']
    d = T + 2
    ev = [n for n in range(off, off + 4 * d) if n % 2 == 0][:d]
    od = [n for n in range(off, off + 4 * d) if n % 2 == 1][:d]
    Pe = _interp([Fraction(n) for n in ev], [value(b, n) for n in ev])
    Po = _interp([Fraction(n) for n in od], [value(b, n) for n in od])
    A = [(x + y) / 2 for x, y in zip(Pe + [Fraction(0)] * len(Po),
                                     Po + [Fraction(0)] * len(Pe))]
    C = [(x - y) / 2 for x, y in zip(Pe + [Fraction(0)] * len(Po),
                                     Po + [Fraction(0)] * len(Pe))]
    A = A[:max(len(Pe), len(Po))]
    C = C[:max(len(Pe), len(Po))]
    while A and A[-1] == 0:
        A.pop()
    while C and C[-1] == 0:
        C.pop()
    return A, C


def _polymul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def minimal_annihilator(b, off=1):
    """(t-1)^(deg A+1) (t+1)^(deg C+1), coefficients low degree first."""
    A, C = fit(b, off)
    q = [1]
    for _ in range(len(A)):
        q = _polymul(q, [-1, 1])
    for _ in range(len(C)):
        q = _polymul(q, [1, 1])
    return q, A, C


def divides(q, r):
    """does polynomial q divide r? both low degree first, integer coefficients."""
    q = list(q)
    r = list(r)
    while r and r[-1] == 0:
        r.pop()
    while len(r) >= len(q) and r:
        if r[-1] % q[-1]:
            return False
        f = r[-1] // q[-1]
        sh = len(r) - len(q)
        for i in range(len(q)):
            r[sh + i] -= f * q[i]
        while r and r[-1] == 0:
            r.pop()
    return not r
