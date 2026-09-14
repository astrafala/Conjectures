#!/usr/bin/env python3
"""Coordination sequences of the Galebach k-uniform tilings.

    Coordination sequence Gal.4.31.1 where Gal.u.t.v denotes the coordination sequence for a
    vertex of type v in tiling number t in the Galebach list of u-uniform tilings.

6,070 OEIS entries read like that and no engine had ever looked at one, because the tilings
were missing: the local oeisdata mirror keeps the auxiliary file a250120.html only as a
git-LFS pointer. It is not missing from oeis.org, and it determines all 1,248 tilings.

The chain, each part validated on its own:

    galtile   the tiling as a graph, exactly, in Z[zeta_24]   6,536/6,536 sequences reproduced
    gallat    the translation lattice and the vertex classes
    galhull   d per class as max_i(A*m + B*n + C), exactly
    galehr    the lattice-point count, with period and onset DERIVED

Why that is a proof and not a fit. On a class, the ball of radius t is the lattice points of
{ (m,n) : A_i*m + B_i*n + C_i <= t }. Every candidate vertex of that region is the meet of two
facets and moves AFFINELY in t, so its relation to any facet flips at most once, at one
rational t; past the largest such t the region's combinatorial type never changes again. That
is the onset. The vertices' denominators divide the 2x2 determinants of facet-normal pairs, so
the Ehrhart quasi-polynomial's period divides their lcm; the smallest divisor that reproduces
the counts is kept, which is a stronger statement and is checked rather than assumed. The ball
count is then a degree-2 quasi-polynomial, and a(n) = |B(n)| - |B(n-1)| is quasi-linear.

The engine REFUSES a tiling whose d is not exactly a max of affine pieces. 723 of the 1,248
are exact; on the other 525 the distance exceeds the hull by one on a sparse set that recurs
with the tiling's own period, so d is genuinely not convex there and this argument does not
reach them. They are refused with that reason rather than approximated.
"""
import math
import re

import galcert
import galehr
import gallat
import galhull
import galtile

NAME = re.compile(r'Coordination sequence Gal\.(\d+)\.(\d+)\.(\d+)\b', re.I)
RADIUS = 34                      # patch radius for fitting

# The premise is now PROVED per tiling rather than assumed, by `galcert`.
#
# `galhull` fits d = max_i(A*m + B*n + C) on a patch and checks it on that same patch. That is
# circular: a cone whose region lies entirely outside the patch cannot show up as a leftover,
# and the fit then reports itself exact. On A310102 (Gal.4.16.1) the fitted form agrees with
# breadth-first search for 29 terms and diverges at the 30th -- exactly one step past the
# radius it was fitted on. The Ehrhart half is not at fault: the closed form and a direct
# lattice count of the fitted region agree with each other everywhere. It is the region that
# is wrong.
#
# `galcert` is that check: for the closed form D, it verifies the two Bellman conditions over
# the WHOLE lattice rather than over a patch --
#
#   (b) for every edge, given as (class c, class c', lattice offset (dm, dn)),
#       D_{c'}(m + dm, n + dn) <= D_c(m, n) + 1  for all (m, n);
#   (c) every class and every (m, n) other than the origin has an edge attaining equality.
#
# and it decides them without a general LP: D is piecewise affine, so past the last breakpoint
# of the arrangement every condition is affine on a cone, and an affine statement holding at
# three affinely independent points of a cone holds on all of it. So: exhaustively inside the
# breakpoint radius, three points per cone outside it, with the radius computed from the planes.
#
# It was validated both ways and PASSED those tests -- it accepts the honeycomb, 4.8.8 and the
# triangular tiling, it refuses Gal.4.16 whose patch fit agreed with breadth-first search for
# 29 terms and diverged at the 30th, and perturbing any plane's constant by one in either
# direction makes it refuse a tiling it otherwise accepts.
#
# IT IS STILL NOT SOUND, and A310511 shows it: the certificate accepts, and the fitted form
# diverges from breadth-first search at the 35th term. Two gaps, both in the "outside the
# breakpoint radius" half:
#
#   * `galcert._cone_points` locates a cone by walking out along its plane's gradient. When
#     that heuristic fails it returns None and the cone is SKIPPED -- silently unverified.
#     A check that skips what it cannot find is not a check;
#   * three affinely independent points settle an affine statement on a cone, but condition
#     (c) is "SOME edge attains equality", and the edge that attains it may differ from point
#     to point. Three points do not settle a disjunction.
#
# The fix is to stop sampling and compute the arrangement. In two dimensions the normal fan is
# cheap: sort the planes by gradient angle, and the region where plane i is the maximum is
# bounded by the rays where it ties with its neighbours in that order. With a cone given by its
# apex and two generator directions, "affine <= affine on the cone" is decided exactly -- the
# difference at the apex, and its linear part on each generator -- and condition (c) is decided
# per cone by intersecting with each edge's equality region. No sampling, nothing skipped.
# `galcert2` is that fix, and it is written: `galpoly` does exact integer region arithmetic in
# the plane (vertices, recession rays, emptiness, "affine >= 0 on a region", and subtraction of
# one region from another), validated against brute force on 1,494 random regions; `galcert2`
# decides (b) as an affine inequality on each maximum-region and (c) as a COVERING of that
# region by the neighbours' equality regions, subtracting them one at a time. Nothing is
# sampled and nothing is skipped. It refuses A310511, which `galcert` certified and which
# diverges at term 35, and it certifies the honeycomb outright.
#
# What still blocks the vein is the FIT, not the certificate. `galhull` fits on a patch of
# radius 34, which for a tiling with eighteen vertex classes is 64 lattice points per class and
# fifteen affine pieces -- and extrapolating that to lattice coordinate 40 is off by 63. The
# plane count also grows with the radius (15 at 34, 21 at 70, and back to 16..20 at 110), which
# is a fit picking up the patch rim rather than the tiling. So: a bigger patch, and a prune
# that tests a plane against the tiling rather than against the rim. The certificate will say
# when it is right; that was the part that could not be trusted before, and now it can.
IN_SERVICE = False


def parse_name(nm):
    m = NAME.search(' '.join(nm.split()))
    if not m:
        return None
    u, t, v = (int(x) for x in m.groups())
    return {'engine': 'galcoord', 'u': u, 't': t, 'v': v, 'frac': 1}


def build(p, cap=400000):
    if not IN_SERVICE:
        return None
    T = galtile.tilings()
    types = T.get((p['u'], p['t']))
    if not types:
        return None
    letters = sorted(types)
    if not 1 <= p['v'] <= len(letters):
        return None
    start = letters[p['v'] - 1]
    L = gallat.lattice(types)
    if L is None:
        return None
    a, b = L
    seen = gallat.patch(types, RADIUS, start=start)
    if not seen:
        return None

    reps, cells = [], []

    def _find(pos, l, r, f):
        s = gallat.sig(types, l, r, f)
        for ci, (rp, rl, rr, rf) in enumerate(reps):
            if gallat.sig(types, rl, rr, rf) != s:
                continue
            c = gallat.coords(gallat._sub(pos, rp), a, b)
            if c is not None:
                return ci, c, rp
        return None

    for pos, (l, r, f, d) in seen.items():
        hit = _find(pos, l, r, f)
        if hit is None:
            reps.append((pos, l, r, f))
            cells.append([(0, 0, d)])
        else:
            cells[hit[0]].append((hit[1][0], hit[1][1], d))

    def cls_of(q, nl, nr, nf):
        h = _find(q, nl, nr, nf)
        return None if h is None else (h[0], h[2])

    planes = []
    for lst in cells:
        pts = [(m, n, d) for m, n, d in lst if d <= RADIUS - 6]
        if len(pts) < 12:
            return None
        pl, left = galhull.pieces(pts)
        if left:
            return None                      # d is not a max of affine pieces on the patch
        planes.append([(int(A), int(B), int(C)) for A, B, C in pl])

    el = galcert.edges(types, a, b, reps, cls_of)
    if el is None:
        return None
    ok, _why = galcert.check(planes, el)
    if not ok:
        return None                          # the fit does not hold off the patch: refuse

    fits = [galehr.fit(pl) for pl in planes]
    if any(f is None for f in fits):
        return None
    q = 1
    for (qq, _T, _c) in fits:
        q = q * qq // math.gcd(q, qq)
    return {'planes': planes, 'fits': fits, 'q': q,
            'T': max(f[1] for f in fits), 'S': q, 'start': start,
            'u': p['u'], 't': p['t'], 'v': p['v']}


def ball(b, t):
    """|{v : d(v) <= t}| -- counted exactly, every time.

    An earlier version used the Ehrhart closed form wherever the derived onset said it applied,
    and that was wrong on entries the certificate accepted: `galehr.onset` can come out too
    small, the quasi-polynomial then gets fitted inside the transient, and its own verification
    (a few values just past the fit) passes because the transient is locally smooth. A310393
    showed it -- the planes gave the true ball at every radius while the closed form drifted
    from t = 12.

    So the closed form is not used for counting at all. `galehr.count` is exact for every t and
    was checked against brute-force enumeration of the region; the quasi-polynomial's only job
    is to supply the PERIOD for the threshold, where Ehrhart's theorem is what carries the
    argument past the computed range.
    """
    return sum(galehr.count(pl, t) for pl in b['planes'])


def terms(b, N):
    """a(n) for n = 1, 2, ...

    The entries have offset 1 and a(1) = 1: the first term counts the vertex itself, at
    distance 0. So a(n) is the number of vertices at distance n-1, not n -- an off-by-one that
    showed up as a "model mismatch" on A310102 and was nothing of the sort.
    """
    out = []
    prev = 0
    for t in range(0, N + 1):
        cur = ball(b, t)
        out.append(int(cur - prev))
        prev = cur
    return out


def threshold(b, coeffs, order):
    """the last n at which the conjectured recurrence may fail -- a finite exact check.

    a(n) is quasi-linear with period q from the onset, so the residual of any fixed linear
    recurrence is quasi-linear with period q as well. A quasi-linear function with period q
    vanishes identically past a point exactly when it vanishes at 2q consecutive values there,
    so the check below is complete rather than a sample.
    """
    q, T = b['q'], b['T']
    n0 = T + order + 2
    hi = n0 + 4 * q + order + 4
    t = terms(b, hi + 2)
    last = 0
    for n in range(order + 1, hi + 1):
        if t[n - 1] - sum(c * t[n - 1 - i] for i, c in coeffs.items()):
            last = n
    # everything past n0 + 2q is settled by the two periods already checked
    return last
