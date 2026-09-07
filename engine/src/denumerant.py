#!/usr/bin/env python3
"""Thruster arrays: a lattice count, not a walk count.

    Number of 4 X n -1,1 arrays such that the sum over i=1..4, j=1..n of i*x(i,j) is zero and
    rows are nondecreasing.

A row of -1s and 1s that is nondecreasing is a block of -1s followed by a block of 1s, so it
is determined by one number: how many -1s it has. Writing k_i in [0,n] for that number in row
i, the row sums to (n - k_i) - k_i = n - 2k_i, and the entry's condition becomes

    Sum_i i*(n - 2 k_i) = 0,   that is   Sum_i i*k_i = n*H*(H+1)/4,

with H the number of rows. So the entry counts the lattice points of a box under one linear
condition, and the array itself has disappeared. A brute force over the arrays and this count
agree, and both agree with the published terms.

Two consequences. The count is the number of lattice points in the n-th dilate of a fixed
rational polytope, hence a quasi-polynomial in n --- which is what makes the conjectured
linear recurrence provable at all, since a quasi-polynomial of degree d and period P
satisfies the recurrence with characteristic polynomial (x^P - 1)^(d+1). And it is computable
without enumerating anything: by inclusion-exclusion over which k_i exceed n,

    a(n) = Sum over S of (-1)^|S| D(T(n) - (n+1)*sigma(S)),

where D(m) counts the solutions of Sum_i i*k_i = m in non-negative integers with no upper
bound --- the classical denumerant for parts 1..H --- and sigma(S) is the sum of S. D is a
single one-dimensional table, so thousands of exact terms cost almost nothing, which is what
the certificate below needs.

THE ORDER BOUND. D is a quasi-polynomial in m of degree H-1 with period dividing
lcm(1,...,H); substituting the integer-linear arguments above keeps the degree and the period
divides it still, and the parity case --- H*(H+1)/4 a half-integer, so the count vanishes at
odd n --- at worst doubles the period. So a(n) is a quasi-polynomial of degree at most H-1
and period dividing 2*lcm(1,...,H), and therefore satisfies a linear recurrence of order at
most 2*H*lcm(1,...,H). That number is the certificate: once that many consecutive residuals
of the conjectured recurrence vanish, every later one does.

Only the entries with the single condition are handled here. The ones that also ask for the
sum of x(i,j) to be zero have two conditions and need a two-dimensional denumerant, whose
period bound at H = 12 is in the tens of thousands; those are left, with the reason recorded.
"""
import re
from math import lcm

import namecanon

HEAD = re.compile(
    r'^Number of (\d+)\s*X\s*n -1,1 arrays such that the sum over i=1\.\.\1,\s*j=1\.\.n of '
    r'i\*x\(i,j\) is zero and rows are nondecreasing.*$', re.I)


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'\s+', ' ', nm).strip()
    m = HEAD.match(nm)
    if not m:
        return None
    H = int(m.group(1))
    if not 2 <= H <= 8:
        return None
    return {'H': H, 'frac': 1}


def _denumerant(H, M):
    """D[m] = number of (k_1..k_H) >= 0 with sum i*k_i = m, for m = 0..M"""
    D = [0] * (M + 1)
    D[0] = 1
    for i in range(1, H + 1):
        for m in range(i, M + 1):
            D[m] += D[m - i]
    return D


def _target(H, n):
    """n*H*(H+1)/4, or None when that is not an integer and the count is zero"""
    t, r = divmod(n * H * (H + 1), 4)
    return None if r else t


def counts(H, N):
    """a(n) for n = 0..N, exactly"""
    big = _target(H, N) or (N * H * (H + 1)) // 4
    D = _denumerant(H, max(big, 1))
    subsets = []
    for mask in range(1 << H):
        s = sum(i + 1 for i in range(H) if (mask >> i) & 1)
        subsets.append((s, -1 if bin(mask).count('1') % 2 else 1))
    out = []
    for n in range(N + 1):
        T = _target(H, n)
        if T is None:
            out.append(0)
            continue
        tot = 0
        for s, sign in subsets:
            m = T - (n + 1) * s
            if 0 <= m < len(D):
                tot += sign * D[m]
        out.append(tot)
    return out


def order_bound(H):
    """a valid order for a linear recurrence satisfied by a(n) --- see the module docstring"""
    return 2 * H * lcm(*range(1, H + 1))


def build(p, cap=200000):
    S = order_bound(p['H'])
    if S > cap:
        return None
    return (None, None, None, S)


def terms_p(p, b, N):
    return counts(p['H'], N)


def threshold_p(p, b, coeffs, order):
    """the last index at which the conjectured recurrence fails, or None if it does not settle

    The residual of a sequence satisfying a linear recurrence of order S again satisfies it,
    so S consecutive vanishing residuals force every later one. S here is the certified bound
    from the quasi-polynomial degree and period, not a guess.
    """
    S = b[3]
    need = S + order + 8
    a = counts(p['H'], need + S + order + 8)
    us = []
    for j in range(order, len(a)):
        us.append(a[j] - sum(int(c) * a[j - i] for i, c in coeffs.items()))
    last = max((i for i, u in enumerate(us) if u != 0), default=-1)
    if len(us) - 1 - last < S:
        return None
    return order + last


terms = None
