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

import galehr
import gallat
import galhull
import galtile

NAME = re.compile(r'Coordination sequence Gal\.(\d+)\.(\d+)\.(\d+)\b', re.I)
RADIUS = 34                      # patch radius for fitting

# NOT IN SERVICE. The pipeline below is correct arithmetic on an UNPROVED premise, and the
# premise is false often enough to matter.
#
# `galhull` fits d = max_i(A*m + B*n + C) on a patch and checks it on that same patch. That is
# circular: a cone whose region lies entirely outside the patch cannot show up as a leftover,
# and the fit then reports itself exact. On A310102 (Gal.4.16.1) the fitted form agrees with
# breadth-first search for 29 terms and diverges at the 30th -- exactly one step past the
# radius it was fitted on. The Ehrhart half is not at fault: the closed form and a direct
# lattice count of the fitted region agree with each other everywhere. It is the region that
# is wrong.
#
# What would make it a proof is the check that was deferred: for the closed form D, verify the
# two Bellman conditions over the WHOLE lattice rather than over a patch --
#
#   (b) for every edge, given as (class c, class c', lattice offset (dm, dn)),
#       D_{c'}(m + dm, n + dn) <= D_c(m, n) + 1  for all (m, n);
#   (c) every class and every (m, n) other than the origin has an edge attaining equality.
#
# Both sides are convex piecewise-linear, so each condition splits into finitely many
# "affine <= affine on a polyhedral cone" tests, each an exact rational LP. Finite, and it is
# the whole content of the proof. Until it is written this engine refuses everything, because
# a pipeline that is right on 29 terms and wrong on the 30th is exactly the kind of thing this
# project exists not to ship.
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
    cl = _classes(types, a, b, start)
    if cl is None:
        return None
    planes, fits = [], []
    for lst in cl:
        pts = [(m, n, d) for m, n, d in lst if d <= RADIUS - 6]
        if len(pts) < 12:
            return None
        pl, left = galhull.pieces(pts)
        if left:
            return None                      # d is not a max of affine pieces here
        ip = [(int(A), int(B), int(C)) for A, B, C in pl]
        f = galehr.fit(ip)
        if f is None:
            return None
        planes.append(ip)
        fits.append(f)
    q = 1
    for (qq, _T, _c) in fits:
        q = q * qq // math.gcd(q, qq)
    return {'planes': planes, 'fits': fits, 'q': q,
            'T': max(f[1] for f in fits), 'S': q, 'start': start,
            'u': p['u'], 't': p['t'], 'v': p['v']}


def _classes(types, a, b, start):
    """the translation classes, with distances measured from the entry's own vertex"""
    seen = gallat.patch(types, RADIUS, start=start)
    if not seen:
        return None
    reps, out = {}, {}
    for v, (l, r, f, d) in seen.items():
        s = gallat.sig(types, l, r, f)
        placed = False
        for key in reps:
            if key[0] != s:
                continue
            c = gallat.coords(gallat._sub(v, reps[key]), a, b)
            if c is not None:
                out[key].append((c[0], c[1], d))
                placed = True
                break
        if not placed:
            key = (s, v)
            reps[key] = v
            out[key] = [(0, 0, d)]
    return list(out.values())


def ball(b, t):
    """|{v : d(v) <= t}| -- from the closed form where it applies, by direct count below it"""
    s = 0
    for pl, (qq, TT, c) in zip(b['planes'], b['fits']):
        if t >= TT:
            a0, a1, a2 = c[(t - TT) % qq]
            s += a0 * t * t + a1 * t + a2
        else:
            s += galehr.count(pl, t)
    return s


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
