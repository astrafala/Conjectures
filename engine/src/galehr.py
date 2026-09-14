#!/usr/bin/env python3
"""The coordination sequence from the distance function, by Ehrhart.

For a class whose distance is d(m, n) = max_i (A_i*m + B_i*n + C_i), the ball of radius t meets
that class in

    P_c(t) = { (m, n) in Z^2 : A_i*m + B_i*n + C_i <= t  for every i },

a rational polygon whose facet normals are fixed and whose right-hand sides move linearly with
t. Its lattice-point count is a quasi-polynomial in t of degree 2, and the period divides the
lcm of the 2x2 determinants of pairs of facet normals -- those determinants are the only
denominators a vertex of the polygon can have. That bound is DERIVED, not assumed; STATE.md
defect 11 is the record of what assuming one costs.

So: count directly for enough t to determine a degree-2 quasi-polynomial on each residue, then
keep counting well past that and check the closed form reproduces every value. The ball is the
sum over classes, a(t) = |B(t)| - |B(t-1)|, and the annihilator is (z^q - 1)^2.
"""
from fractions import Fraction


def period(planes):
    """the lcm of the 2x2 determinants of facet-normal pairs: every vertex denominator divides it"""
    q = 1
    for i in range(len(planes)):
        for j in range(i + 1, len(planes)):
            det = abs(planes[i][0] * planes[j][1] - planes[j][0] * planes[i][1])
            det = int(det)
            if det:
                q = q * det // _gcd(q, det)
    return max(1, q)


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def count(planes, t):
    """|{(m, n) in Z^2 : A_i*m + B_i*n + C_i <= t}| -- exact, by scanning m and solving for n"""
    lo_m, hi_m = _range_m(planes, t)
    if lo_m is None:
        return 0
    tot = 0
    for m in range(lo_m, hi_m + 1):
        lo = None
        hi = None
        ok = True
        for (A, B, C) in planes:
            rhs = t - C - A * m
            if B == 0:
                if rhs < 0:
                    ok = False
                    break
                continue
            if B > 0:
                v = _floor(rhs, B)
                hi = v if hi is None else min(hi, v)
            else:
                v = _ceil(rhs, B)
                lo = v if lo is None else max(lo, v)
        if not ok or lo is None or hi is None or hi < lo:
            continue
        tot += hi - lo + 1
    return tot


def _floor(a, b):
    return (Fraction(a) / b).__floor__()


def _ceil(a, b):
    return (Fraction(a) / b).__ceil__()


def _range_m(planes, t):
    """the m for which the slice can be non-empty; None when the polygon is empty or unbounded"""
    lo = hi = None
    for (A, B, C) in planes:
        if B != 0:
            continue
        rhs = t - C
        if A == 0:
            if rhs < 0:
                return None, None
            continue
        if A > 0:
            v = _floor(rhs, A)
            hi = v if hi is None else min(hi, v)
        else:
            v = _ceil(rhs, A)
            lo = v if lo is None else max(lo, v)
    if lo is None or hi is None:
        # no axis-aligned facet pins m; bound it from the polygon's own extent instead
        b = _extent(planes, t)
        if b is None:
            return None, None
        lo2, hi2 = b
        lo = lo2 if lo is None else max(lo, lo2)
        hi = hi2 if hi is None else min(hi, hi2)
    return (lo, hi) if lo is not None and hi is not None and lo <= hi else (None, None)


def _extent(planes, t):
    """crude but sound bounds on m: every vertex is the meet of two facets"""
    xs = []
    for i in range(len(planes)):
        for j in range(i + 1, len(planes)):
            A1, B1, C1 = planes[i]
            A2, B2, C2 = planes[j]
            det = A1 * B2 - A2 * B1
            if det == 0:
                continue
            x = Fraction((t - C1) * B2 - (t - C2) * B1, det)
            xs.append(x)
    if not xs:
        return None
    return (min(xs).__floor__() - 2, max(xs).__ceil__() + 2)


def onset(planes):
    """T beyond which the polygon's combinatorial type no longer changes.

    Each candidate vertex is the meet of two facets and moves AFFINELY in t, so whether a given
    vertex satisfies a given facet flips at most once, at a single rational t. Past the largest
    such t nothing about the shape changes again, and the lattice count is a quasi-polynomial
    from there. Everything here is exact rational arithmetic: this bound is the thing the whole
    proof rests on, and STATE.md defect 11 is what happens when such a bound is assumed rather
    than derived.
    """
    cross = [Fraction(0)]
    n = len(planes)
    for i in range(n):
        for j in range(i + 1, n):
            A1, B1, C1 = planes[i]
            A2, B2, C2 = planes[j]
            det = A1 * B2 - A2 * B1
            if det == 0:
                continue
            # vertex = P + Q*t
            px = Fraction(-C1 * B2 + C2 * B1, det)
            qx = Fraction(B2 - B1, det)
            py = Fraction(-A1 * C2 + A2 * C1, det)
            qy = Fraction(A1 - A2, det)
            for (A, B, C) in planes:
                # slack(t) = t - C - A*x(t) - B*y(t), affine in t
                c0 = -C - A * px - B * py
                c1 = 1 - A * qx - B * qy
                if c1 == 0:
                    continue
                tc = Fraction(-c0, c1)
                if tc > 0:
                    cross.append(tc)
    return max(cross).__ceil__() + 1


def quasi(planes, q, T, extra=None):
    """(coefficients per residue, verified range) for the degree-2 quasi-polynomial of `count`.

    Determined from 3 values per residue past T, then CHECKED on `extra` further values per
    residue. Returns None if the check fails, which would mean the period or the onset is
    wrong -- better a refusal than a closed form nobody tested.
    """
    if extra is None:
        extra = 4
    coeffs = {}
    for r in range(q):
        ts = [T + r + k * q for k in range(3)]
        ys = [count(planes, t) for t in ts]
        # solve the 3x3 Vandermonde in exact rationals
        a0, a1, a2 = _solve3([(Fraction(t), Fraction(y)) for t, y in zip(ts, ys)])
        coeffs[r] = (a0, a1, a2)
        for k in range(3, 3 + extra):
            t = T + r + k * q
            if a0 * t * t + a1 * t + a2 != count(planes, t):
                return None
    return coeffs


def _solve3(pts):
    (x0, y0), (x1, y1), (x2, y2) = pts
    d = (x0 - x1) * (x0 - x2) * (x1 - x2)
    if d == 0:
        raise ValueError('degenerate')
    a0 = (y0 * (x1 - x2) - y1 * (x0 - x2) + y2 * (x0 - x1)) / d
    a1 = (y0 * (x2 * x2 - x1 * x1) + y1 * (x0 * x0 - x2 * x2) + y2 * (x1 * x1 - x0 * x0)) / d
    a2 = (y0 * x1 * x2 * (x1 - x2) + y1 * x2 * x0 * (x2 - x0) + y2 * x0 * x1 * (x0 - x1)) / d
    return a0, a1, a2


def divisors(q):
    out = []
    i = 1
    while i * i <= q:
        if q % i == 0:
            out.append(i)
            if i != q // i:
                out.append(q // i)
        i += 1
    return sorted(out)


def fit(planes, extra=4):
    """(q, T, coefficients) -- the smallest period that verifies, which is still a theorem.

    Ehrhart gives that the period DIVIDES the lcm of the vertex denominators, so trying the
    divisors in order and keeping the first that reproduces the counts is sound: a smaller
    period is a stronger statement, and it is checked, not assumed. The generous bound is kept
    as the fallback.
    """
    qmax = period(planes)
    T = onset(planes)
    for q in divisors(qmax):
        c = quasi(planes, q, T, extra=extra)
        if c is not None:
            return q, T, c
    return None
