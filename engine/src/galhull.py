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


def prune(planes, pts, margin):
    """drop supports that are only ever tight near the edge of the patch.

    The patch is a BALL in graph distance, so its rim is not a feature of the tiling: class
    points there make a plane look tight when it is an artifact of where the computation
    stopped. On Gal.1.2 exactly one such plane appeared, with gradient (3, 3), and its constant
    marched with the patch radius -- -11, -21, -31 at radii 30, 50, 70 -- which is how it was
    caught. A plane that is a real facet is tight somewhere well inside.
    """
    if not pts:
        return planes
    lim = max(d for (_m, _n, d) in pts) - margin
    inner = [(m, n, d) for (m, n, d) in pts if d <= lim]
    if not inner:
        return planes
    keep = [pl for pl in planes
            if any(pl[0] * m + pl[1] * n + pl[2] == d for (m, n, d) in inner)]
    return keep or planes


def pieces(pts, tries=None, margin=6):
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
        # `support` DECIDES this: either it returns a supporting plane or there provably is
        # none, at about 9 ms a point. What stood here tried every pair among the 400 nearest
        # points -- 80,000 candidates, each validated against the whole class -- took seconds
        # per short point, and when it came back empty that was a search failing rather than a
        # proof. On one class of Gal.4.31.1 it left 10 of 12 short points unsupported.
        best = support(P, (m, n, d))
        if best:
            planes.append(best)
    planes = prune(planes, P, margin)

    def val2(m, n):
        return max((A * m + B * n + C for A, B, C in planes), default=Fraction(-10 ** 9))

    lim = max(d for (_m, _n, d) in P) - margin
    left = [(m, n, d) for (m, n, d) in P if d <= lim and val2(m, n) != d]
    return planes, left


def support(pts, p):
    """a supporting plane of d at p, or None if there provably is none.

    `pieces` looked for one by trying every pair among the 400 nearest points and checking the
    plane through the three against all the data -- 80,000 candidates each validated against
    hundreds of points, seconds per short point, and when it found nothing that was a SEARCH
    failing, not a proof that no support exists. The question is a two-variable feasibility
    problem and is decided outright:

        a supporting plane at p is (A, B) with
            A*(q1-p1) + B*(q2-p2) <= d(q) - d(p)     for every q,

    an intersection of half-planes in the (A, B) plane. `galpoly` decides emptiness exactly and
    returns the vertices, so either there is no support -- a genuine non-convexity of d, which
    is a fact about the tiling -- or one is produced.

    The vertices are rational. A plane with a fractional gradient is refused rather than
    rounded: `int()` on a Fraction truncates, and a plane wrong by any amount puts the whole
    certificate on sand.
    """
    import galpoly
    (p1, p2, dp) = p
    seen = {}
    for (q1, q2, dq) in pts:
        u, v, c = q1 - p1, q2 - p2, dq - dp
        if (u, v) == (0, 0):
            continue
        g = abs(_gcd(u, v))
        if g > 1 and c % g == 0:
            u, v, c = u // g, v // g, c // g
        # only the TIGHTEST constraint in each direction binds; keeping the first one seen
        # left the rest in and made the clip below do a hundred times the work it needed
        if (u, v) not in seen or c < seen[(u, v)]:
            seen[(u, v)] = c
    cons = [(-u, -v, c) for (u, v), c in seen.items()]
    M = max(abs(dq - dp) for (_q1, _q2, dq) in pts) + 1
    poly = galpoly.polygon(cons, M)
    if not poly:
        return None
    for (A, B) in poly:
        if A.denominator != 1 or B.denominator != 1:
            continue
        A, B = int(A), int(B)
        C = dp - A * p1 - B * p2
        if all(A * q1 + B * q2 + C <= dq for (q1, q2, dq) in pts):
            return (Fraction(A), Fraction(B), Fraction(C))
    return None


def _gcd(a, b):
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a
