#!/usr/bin/env python3
"""Nondecreasing arrangements of n numbers from -A..A with sum zero.

    Number of nondecreasing arrangements of n numbers in -5..5 with sum zero.
    Number of nondecreasing arrangements of n numbers in -2..2 with sum zero and sum of squares
      not greater than n*6/3.

12 entries, none read: the LENGTH grows and the alphabet is fixed, so no walk on a window
counts them, and `latpoly' reads the mirror shape where the length is fixed.

A nondecreasing arrangement is a multiset, so it is its counts c_v for v in -A..A, and every
condition the entry names is linear in those and in n:

    sum_v c_v = n,   sum_v v c_v = 0,   sum_v v^2 c_v <= alpha n,   c_v >= 0.

Every one is homogeneous in (c, n) jointly, so the admissible c at height n are the lattice
points of a finite union of relatively open rational cones in R^(2A+2) and a(n) is their Ehrhart
quasi-polynomial. Its period is read off the arrangement exactly as in `latpoly': every ray of
every cell is cut out by as many independent hyperplanes as there are variables, so by Cramer
its primitive generator has its n-coordinate dividing the determinant of their c-parts, and a
ray leaving the region bounds no cell and is dropped. The degree is at most the dimension of
the cone, which the two equalities drop to 2A.

The count itself is a DP over v carrying the two running sums, which is exact and costs
O(A n^2) a term.
"""
import re

NAME = re.compile(
    r'^\s*Number of nondecreasing arrangements of n numbers in (-?\d+)\.\.(-?\d+) '
    r'with sum zero\s*(.*?)\s*\.?\s*$', re.I)
SQ = re.compile(r'and sum of squares (not greater than|less than|greater than|not less than) '
                r'(?:n\*(\d+)/(\d+)|(\d+)n|n\*(\d+)|(\d+)\*n)')


def parse_name(nm):
    m = NAME.match(' '.join(nm.split()))
    if not m:
        return None
    lo, hi = int(m.group(1)), int(m.group(2))
    if lo != -hi or not 1 <= hi <= 6:
        return None
    tail = ' '.join(m.group(3).lower().split())
    sq = None
    if tail:
        s = SQ.match(tail)
        if not s or s.end() != len(tail):
            return None
        rel = s.group(1)
        if s.group(2):
            num, den = int(s.group(2)), int(s.group(3))
        else:
            num, den = int(s.group(4) or s.group(5) or s.group(6)), 1
        if num % den:
            return None
        sq = (rel, num // den)
    return {'engine': 'multizero', 'A': hi, 'sq': sq, 'frac': 1}


def _ok(rel, s, bound):
    if rel == 'not greater than':
        return s <= bound
    if rel == 'less than':
        return s < bound
    if rel == 'greater than':
        return s > bound
    return s >= bound


def count(A, sq, n):
    """multisets of n values in -A..A with sum zero and the square condition.

    Two axes when there is no square clause, three when there is: carrying the third through a
    dictionary made the A = 5 case cost minutes a term, where the sum axis alone is a few
    milliseconds.
    """
    V = range(-A, A + 1)
    if sq is None:
        W = A * n
        cur = [[0] * (2 * W + 1) for _ in range(n + 1)]
        cur[0][W] = 1
        for v in V:
            nxt = [[0] * (2 * W + 1) for _ in range(n + 1)]
            for u in range(n + 1):
                row = cur[u]
                for sidx, c in enumerate(row):
                    if not c:
                        continue
                    s0 = sidx - W
                    for t in range(0, n - u + 1):
                        q = s0 + v * t
                        if abs(q) > W:
                            continue
                        nxt[u + t][q + W] += c
            cur = nxt
        return cur[n][W]
    lim = A * A * n
    W = A * n
    cur = {(0, 0, 0): 1}
    for v in V:
        nxt = {}
        for (u, s0, q0), c in cur.items():
            for t in range(0, n - u + 1):
                s1 = s0 + v * t
                q1 = q0 + v * v * t
                if abs(s1) > W or q1 > lim:
                    continue
                key = (u + t, s1, q1)
                nxt[key] = nxt.get(key, 0) + c
        cur = nxt
    tot = 0
    for (u, s0, q0), c in cur.items():
        if u == n and s0 == 0 and _ok(sq[0], q0, sq[1] * n):
            tot += c
    return tot


def _rays(A, sq):
    """the primitive rays of the arrangement, by their height n = sum c_v.

    The constraint sum_v c_v = n is used to ELIMINATE n rather than to carry it: every other
    condition becomes homogeneous in c alone -- sum v c_v = 0 and sum (v^2 - alpha) c_v <> 0 --
    and the height of a ray is the value of sum c_v on it. Passing the equality to `latpoly`'s
    ray finder instead, which reads its forms in the x variables only, asked for sum c = 0 and
    found two rays where the arrangement has many: the derived annihilator then failed at every
    index, which is what the extrapolation guard is for.
    """
    from fractions import Fraction
    from itertools import combinations
    import latpoly
    V = list(range(-A, A + 1))
    m = len(V)
    H = []
    for i in range(m):
        f = [0] * m
        f[i] = 1
        H.append(tuple(f))
    H.append(tuple(V))
    if sq is not None:
        H.append(tuple(v * v - sq[1] for v in V))
    H = sorted(set(H))
    eq = tuple(V)
    T = {}
    for S in combinations(H, m - 1):
        M = [list(f) for f in S]
        # the kernel of an (m-1) x m integer matrix: one direction, by cofactors
        g = []
        for col in range(m):
            sub = [[row[c] for c in range(m) if c != col] for row in M]
            g.append(((-1) ** col) * latpoly._det(sub))
        if not any(g):
            continue
        from math import gcd
        q = 0
        for x in g:
            q = gcd(q, abs(x))
        g = [x // q for x in g]
        for sign in (1, -1):
            r = [sign * x for x in g]
            if any(x < 0 for x in r):
                continue
            if sum(a * b for a, b in zip(eq, r)) != 0:
                continue
            if sq is not None:
                val = sum((v * v - sq[1]) * x for v, x in zip(V, r))
                if sq[0] in ('not greater than', 'less than') and val > 0:
                    continue
                if sq[0] in ('greater than', 'not less than') and val < 0:
                    continue
            t = sum(r)
            if t > 0:
                T.setdefault(t, set()).add(tuple(r))
    return T


def build(p, cap=200000):
    import latpoly
    A, sq = p['A'], p['sq']
    m = 2 * A + 1
    T = _rays(A, sq)
    if not T:
        return None
    dim = m - 1
    Apoly = latpoly._annihilator(T, 1, m, dim=dim)
    Apoly = [0] + Apoly
    S = len(Apoly) - 1
    # the square clause costs a third axis in the count, so a long annihilator there is
    # a model that cannot be evaluated: refused with the reason rather than left to run
    if S > (40 if sq is not None else 140):
        return None
    vals = [count(A, sq, n) for n in range(S + 6)]
    for j in range(S, len(vals)):
        if vals[j] != -sum(Apoly[q] * vals[j - S + q] for q in range(S)):
            return None
    return {'A': A, 'sq': sq, 'S': S, 'vals': vals}


def terms(b, N):
    v = list(b['vals'])
    while len(v) <= N:
        v.append(count(b['A'], b['sq'], len(v)))
    return v[:N + 1]


def threshold(b, coeffs, order):
    S = b['S']
    t = terms(b, 2 * S + order + 30)
    last, run = None, 0
    for j in range(order, len(t)):
        u = t[j] - sum(c * t[j - i] for i, c in coeffs.items())
        if u:
            last, run = j, 0
        else:
            run += 1
    if run < S + order:
        return None
    return last if last is not None else 0
