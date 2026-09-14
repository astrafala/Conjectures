#!/usr/bin/env python3
"""The affine pieces of a tiling's distance function, exactly.

d written in lattice coordinates is a polyhedral norm:

    d(m, n) = max_i ( A_i*m + B_i*n + C_i )

A scan over gradients finds the cones that occupy enough lattice points to be noticed and
misses the thin ones. Every miss showed the same way -- the fitted max came out 1 too small,
never too large -- which says the cones found are genuine and some are absent, so the fix is to
ADD the missing supports rather than to re-fit.

Enumerating supports through every triple of points is cubic and hopeless at a few hundred
points per class. But the scan misses very few points (28 of 5,839 on Gal.4.31), so the cubic
search is only ever run through those: for a point the current max underestimates, look for a
supporting plane through it and two others. That pays the high cost exactly where it is owed.

Everything is integer or Fraction arithmetic. A support plane wrong by one would put the whole
certificate on sand, so there is no tolerance anywhere in this file.
"""
import collections
from fractions import Fraction


def scan(pts, minc=2):
    """the cones a gradient scan can see: [(A, B, C)] with integer A, B"""
    D = {(m, n): d for m, n, d in pts}
    g = collections.Counter()
    for (m, n), d in D.items():
        if (m + 1, n) in D and (m, n + 1) in D:
            g[(D[(m + 1, n)] - d, D[(m, n + 1)] - d)] += 1
    out = []
    for (A, B), c in g.items():
        if c < minc:
            continue
        C = min(d - A * m - B * n for (m, n), d in D.items())
        out.append((Fraction(A), Fraction(B), Fraction(C)))
    return out


def _plane(p, q, r):
    (m1, n1, d1), (m2, n2, d2), (m3, n3, d3) = p, q, r
    det = (m2 - m1) * (n3 - n1) - (m3 - m1) * (n2 - n1)
    if det == 0:
        return None
    A = Fraction((d2 - d1) * (n3 - n1) - (d3 - d1) * (n2 - n1), det)
    B = Fraction((m2 - m1) * (d3 - d1) - (m3 - m1) * (d2 - d1), det)
    return (A, B, Fraction(d1) - A * m1 - B * n1)


def pieces(pts, tries=400):
    """(planes, leftovers): the max-of-affine description, and the points it cannot reach.

    An empty leftover list means d IS the max over `planes` at every point given -- an exact,
    checkable closed form. A non-empty one is not a failure to hide: those points are where the
    function is not convex, and the certificate has to carry them as an exceptional set the way
    `kdcert` carries the board heights below H0.
    """
    P = list(pts)
    planes = scan(P)

    def val(m, n):
        return max((A * m + B * n + C for A, B, C in planes), default=Fraction(-10 ** 9))

    short = [(m, n, d) for (m, n, d) in P if val(m, n) < d]
    for (m, n, d) in short:
        if val(m, n) == d:
            continue
        near = sorted(P, key=lambda t: (t[0] - m) ** 2 + (t[1] - n) ** 2)[:tries]
        best = None
        for i in range(len(near)):
            for j in range(i + 1, len(near)):
                pl = _plane((m, n, d), near[i], near[j])
                if pl is None:
                    continue
                A, B, C = pl
                if all(A * mm + B * nn + C <= dd for (mm, nn, dd) in P):
                    best = pl
                    break
            if best:
                break
        if best:
            planes.append(best)
    left = [(m, n, d) for (m, n, d) in P if val(m, n) != d]
    return planes, left
