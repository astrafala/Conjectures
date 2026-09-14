#!/usr/bin/env python3
"""The k for which a quadratic in k is a perfect square: a Pell equation, listed in order.

    Numbers k such that 8*k^2 + 1 is a square.
    Numbers n such that 3*n^2 + 2*n + 1 is a square.

A k^2 + B k + C = m^2 with A >= 1 becomes, on multiplying by 4A and completing the square,

    (2Ak + B)^2 - 4A m^2 = B^2 - 4AC ,

so with X = 2Ak + B, Y = m, D = 4A and N = B^2 - 4AC the admissible k are exactly the solutions
of X^2 - D Y^2 = N with X in the right residue class mod 2A and of the right sign.

When D is a perfect square the form factors and there are only finitely many solutions; that is
refused. Otherwise let (u, v) be the fundamental solution of u^2 - D v^2 = 1, from the continued
fraction of sqrt(D). Then

    T(X, Y) = (uX + DvY, vX + uY)

carries solutions to solutions, every solution is T^j of a FUNDAMENTAL one -- whose preimage
(uX - DvY, -vX + uY) leaves the region -- and there are finitely many of those, r say. On the
region X >= 1, Y >= 0 one has Y = sqrt((X^2 - N)/D), increasing in X, so T is strictly increasing
and PRESERVES THE ORDER of solutions: once the sorted list has its (n+r)-th entry equal to T of
its n-th for r consecutive n, it does so for ever.

Within one orbit X_{j+2} = 2u X_{j+1} - X_j, since u +- v*sqrt(D) are the roots of t^2 - 2ut + 1;
in terms of k = (X - B)/(2A) that reads k_{j+2} = 2u k_{j+1} - k_j + B(u-1)/A. So

    a(n + 2r) = 2u a(n + r) - a(n) + B(u-1)/A

past the index where the interleaving settles, and the annihilator is
(z - 1)(z^{2r} - 2u z^r + 1), of degree 2r + 1.
"""
import math
import re

HEAD = re.compile(
    r'(?i)^(?:Numbers|Indices|Positive integers)\s+([A-Za-z])\s+such that\s+(.+?)\s+is a '
    r'(?:perfect )?square\s*\.?\s*$')


def _poly(expr, var):
    """integer coefficients (A, B, C) of a degree<=2 polynomial in `var`, or None"""
    s = expr.replace(' ', '')
    if not re.fullmatch(r'[-+*^0-9' + var + r']+', s):
        return None
    A = B = C = 0
    for tm in re.finditer(r'([+-]?)(\d*)\*?(' + var + r'(?:\^(\d+))?)?', s):
        sign, num, vpart, pw = tm.group(1), tm.group(2), tm.group(3), tm.group(4)
        if not tm.group(0):
            continue
        co = int(num) if num else 1
        if sign == '-':
            co = -co
        if vpart is None:
            C += co
        else:
            d = int(pw) if pw else 1
            if d == 1:
                B += co
            elif d == 2:
                A += co
            else:
                return None
    return A, B, C


def parse_name(nm):
    nm = ' '.join(nm.split())
    m = HEAD.match(nm)
    if not m:
        return None
    var, expr = m.group(1), m.group(2)
    p = _poly(expr, var)
    if p is None:
        return None
    A, B, C = p
    if A < 1 or A > 10 ** 4 or abs(B) > 10 ** 6 or abs(C) > 10 ** 6:
        return None
    D = 4 * A
    if math.isqrt(D) ** 2 == D:
        return None                       # the form factors: finitely many solutions
    return {'engine': 'pellsq', 'A': A, 'B': B, 'C': C, 'D': D,
            'N': B * B - 4 * A * C, 'frac': 1}


def _unit(D):
    """fundamental solution of u^2 - D v^2 = 1, by the continued fraction of sqrt(D)"""
    a0 = math.isqrt(D)
    m, d, a = 0, 1, a0
    num1, num = 1, a0
    den1, den = 0, 1
    while num * num - D * den * den != 1:
        m = d * a - m
        d = (D - m * m) // d
        a = (a0 + m) // d
        num1, num = num, a * num + num1
        den1, den = den, a * den + den1
        if num > 10 ** 40:
            return None
    return num, den


def _ok(X, Y, p):
    A, B, D, N = p['A'], p['B'], p['D'], p['N']
    return (X >= 0 and Y >= 0 and X * X - D * Y * Y == N
            and (X - B) % (2 * A) == 0 and (X - B) // (2 * A) >= 0)


def build(p, cap=400000):
    A, B, C, D, N = p['A'], p['B'], p['C'], p['D'], p['N']
    uv = _unit(D)
    if uv is None:
        return None
    u, v = uv

    def T(X, Y):
        return u * X + D * v * Y, v * X + u * Y

    # Seeds: every solution with |Y| below Nagell's bound, BOTH SIGNS of Y. The conjugate
    # (X, -Y) is a solution too and its T-images re-enter the region as a DIFFERENT orbit --
    # taking only Y >= 0 seeds lost half the orbits and produced sorted lists with holes in
    # them, which is what the entries' own terms showed at twenty-four names at once.
    ymax = math.isqrt(abs(N) * (u + 1) // (2 * D)) + 2
    if ymax > 4 * 10 ** 6:
        return None
    seeds = []
    for Y in range(0, ymax + 1):
        X2 = N + D * Y * Y
        if X2 < 0:
            continue
        X = math.isqrt(X2)
        if X * X != X2:
            continue
        seeds.append((X, Y))
        if Y:
            seeds.append((X, -Y))
    if not seeds:
        return None
    got = set()
    for (X, Y) in seeds:
        for _ in range(90):
            if _ok(X, Y, p):
                got.add((X, Y))
            X, Y = T(X, Y)
            if X > 10 ** 400:
                break
    if not got:
        return None
    sols = sorted(got)
    # Guard: the generated k below a direct-search limit must be exactly the k a direct search
    # finds. A missed orbit shows up here as a missing term, not as a wrong recurrence.
    lim = min(cap, 200000)
    direct = []
    for k in range(0, lim):
        val = A * k * k + B * k + C
        if val < 0:
            continue
        m = math.isqrt(val)
        if m * m == val:
            direct.append(k)
    ks = [(X - B) // (2 * A) for X, _Y in sols]
    if [k for k in ks if k < lim] != direct:
        return None
    idx = {s: i for i, s in enumerate(sols)}
    best = None
    for r in range(1, 13):
        n0, run = None, 0
        for i in range(len(sols) - r):
            if idx.get(T(*sols[i])) == i + r:
                run += 1
                if run >= r and n0 is None:
                    n0 = i - r + 1
            else:
                run, n0 = 0, None
        if n0 is not None and len(sols) - n0 > 4 * r + 6:
            best = (r, n0)
            break
    if best is None:
        return None
    r, n0 = best
    return {'ks': ks, 'r': r, 'n0': n0, 'u': u, 'S': n0 + 2 * r + 2}


def terms(b, N):
    ks = b['ks']
    return ks[:N + 2] if N + 2 <= len(ks) else ks


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
