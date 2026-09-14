#!/usr/bin/env python3
"""The k for which the k-th triangular number plus a constant is a perfect square.

    Indices k such that 6 plus the k-th triangular number is a perfect square.

k(k+1)/2 + c = m^2 is a Pell equation in disguise. Multiply by 8 and complete the square:

    (2k+1)^2 - 2(2m)^2 = 1 - 8c ,

so with X = 2k+1 and Y = 2m the admissible k are exactly the solutions of X^2 - 2Y^2 = N,
N = 1 - 8c, with X odd and positive and Y even and nonnegative.

The automorph of the form x^2 - 2y^2 coming from the unit 3 + 2*sqrt(2) is

    T(X, Y) = (3X + 4Y, 2X + 3Y),

which maps solutions to solutions, and every solution is T^j of a FUNDAMENTAL one -- a solution
whose T-preimage (3X - 4Y, -2X + 3Y) leaves the region. There are finitely many of those; call
their number r. T is strictly increasing on the region, because Y = sqrt((X^2 - N)/2) increases
with X there, so T preserves the ORDER of solutions. Hence once the sorted list of solutions has
its (n+r)-th entry equal to T of its n-th, it does so for every later n, and the whole sequence
is r interleaved orbits.

Within one orbit X_{j+2} = 6X_{j+1} - X_j, so in terms of k = (X-1)/2

    k_{j+2} = 6 k_{j+1} - k_j + 2 ,

and therefore a(n + 2r) = 6 a(n + r) - a(n) + 2 past the index where the interleaving settles.
The annihilator is (z - 1)(z^{2r} - 6 z^r + 1), of degree 2r + 1 -- which for r = 2 is exactly
the order-5 recurrence these entries conjecture, and for r = 4 the order-9 one.
"""
import math
import re

NAME = re.compile(
    r'(?i)^(?:Indices|Numbers) (k|n) such that (\d+) plus the \1-th triangular number is a '
    r'perfect square\s*\.?\s*$')


def parse_name(nm):
    nm = ' '.join(nm.split())
    m = NAME.match(nm)
    if not m:
        return None
    c = int(m.group(2))
    if c < 0 or c > 10 ** 6:
        return None
    return {'engine': 'triangsq', 'c': c, 'frac': 1}


def _T(X, Y):
    return 3 * X + 4 * Y, 2 * X + 3 * Y


def _Tinv(X, Y):
    return 3 * X - 4 * Y, -2 * X + 3 * Y


def _ok(X, Y, N):
    return X >= 1 and Y >= 0 and X % 2 == 1 and Y % 2 == 0 and X * X - 2 * Y * Y == N


def _fundamentals(c, search):
    """every solution whose T-preimage leaves the region, found by direct search on k"""
    N = 1 - 8 * c
    out = []
    for k in range(0, search):
        v = k * (k + 1) // 2 + c
        m = math.isqrt(v)
        if m * m != v:
            continue
        X, Y = 2 * k + 1, 2 * m
        if not _ok(*_Tinv(X, Y), N):
            out.append((X, Y))
    return N, out


def build(p, cap=400000):
    c = p['c']
    # The fundamental solutions are small -- T multiplies X by about 5.83, so a solution far
    # above sqrt(|N|) has a preimage in the region -- but rather than quote a bound, the search
    # is run to `lim` and then CHECKED: if any solution between lim and 4*lim is fundamental,
    # the search was too short and the engine refuses instead of returning a partial orbit set.
    lim = min(cap, max(2000, 40 * (1 + 8 * c)))
    N, fund = _fundamentals(c, lim)
    if not fund:
        return None
    _N2, late = _fundamentals(c, 4 * lim)
    if len(late) != len(fund):
        return None
    r = len(fund)
    # generate a long sorted prefix of the solution set
    sols = []
    for f in fund:
        X, Y = f
        for _ in range(80):
            sols.append((X, Y))
            X, Y = _T(X, Y)
    sols.sort()
    ks = [(X - 1) // 2 for X, _Y in sols]
    # the index from which the (n+r)-th solution is T of the n-th; T is order preserving, so
    # once that holds for r consecutive n it holds for ever
    idx = {s: i for i, s in enumerate(sols)}
    n0 = None
    run = 0
    for i in range(len(sols) - r):
        if idx.get(_T(*sols[i])) == i + r:
            run += 1
            if run >= r and n0 is None:
                n0 = i - r + 1
        else:
            run = 0
            n0 = None
    if n0 is None:
        return None
    return {'ks': ks, 'r': r, 'n0': n0, 'S': n0 + 2 * r + 2, 'fund': len(fund)}


def terms(b, N):
    """out[j] is the (j+1)-st admissible k, the entry's offset being 1."""
    ks = b['ks']
    if N + 2 > len(ks):
        return ks
    return ks[:N + 2]


def threshold(b, coeffs, order):
    S = b['S']
    t = terms(b, 2 * S + order + 30)
    if len(t) < 2 * S + order + 20:
        return None
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
