#!/usr/bin/env python3
"""Does a fitted distance function hold on the WHOLE lattice? -- decided, not sampled.

The certificate is the one `kdcert` uses, one dimension up. Write the tiling's edges as
(class c, class c', lattice offset d). For D with D(origin) = 0:

    (b)  D_{c'}(m + d) <= D_c(m) + 1        for every edge and every m
    (c)  every m other than the origin has an edge attaining D_c(m) = D_{c'}(m + d) + 1

Either half is one induction and neither cares where D came from, so a fit made on a patch is
certified by them without circularity.

`galcert` decided both by sampling three points per cone. That is wrong twice: it could not
tell whether its three points lay in the cone (it returned None and skipped it in silence), and
(c) is a DISJUNCTION, so three points may each have a different predecessor while no single one
serves the whole cone. It accepted A310511, whose sequence diverges at term 35.

Here D = max_i l_i is piecewise affine, and the region where piece i is the maximum is the
honest polyhedron

    P_i = { m : l_i(m) - l_j(m) >= 0 for every j } ,

so (b) is an affine inequality on a polyhedron -- exact, by `galpoly.nonneg`. And (c) says
P_i is COVERED by the regions

    S_k = { m : l_i(m) - 1 - l''_{k,j}(m + d_k) >= 0 for every j }

one per neighbour k, which is decided by subtracting them from P_i one at a time and asking
whether anything is left. Covering is the part sampling cannot see, and it is the part that
was wrong.
"""
from fractions import Fraction

import galpoly

CAP = 4000          # pieces of leftover region; past this the answer is a refusal, not a claim


def _int_planes(planes):
    """(A, B, C) as integers, scaled by the common denominator -- comparisons are unchanged
    only if every plane of the class is scaled by the SAME factor, which is what happens here"""
    den = 1
    for P in planes:
        for co in P:
            for x in co:
                den = den * Fraction(x).denominator // _gcd(den, Fraction(x).denominator)
    return [[tuple(int(Fraction(x) * den) for x in co) for co in P] for P in planes], den


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def cells(P):
    """for each plane of one class, the constraints cutting out the region where it is the max"""
    out = []
    for i, (A, B, C) in enumerate(P):
        out.append([(A - A2, B - B2, C - C2) for j, (A2, B2, C2) in enumerate(P) if j != i])
    return out


def _shift(co, d, den):
    """l(m + d) as an affine function of m, with the class-wide scaling already applied"""
    A, B, C = co
    return (A, B, C + A * d[0] + B * d[1])


def raymap(exc):
    """the exceptional set of one class as rays: {primitive direction: (d1, step)}, or None.

    An exceptional point is one where the true distance EXCEEDS the max of the fitted planes,
    so D is not `max_i l_i' there and the certificate below must be told. Measured on
    22 September (IDEAS A11), those points are usually a pair of opposite rays k*v through the
    origin with d affine in k -- A310039 at +/-(1,-2) with d = 13, 25, 37, and so on. Returns
    None when they are not, which is a class this cannot certify and must refuse.
    """
    import math
    dirs = {}
    for m, n, d in exc:
        g = math.gcd(abs(m), abs(n)) or 1
        dirs.setdefault((m // g, n // g), []).append((g, int(d)))
    out = {}
    for v, ks in dirs.items():
        ks.sort()
        if len(ks) < 2 or ks[0][0] != 1:
            return None
        if {ks[i + 1][0] - ks[i][0] for i in range(len(ks) - 1)} != {1}:
            return None
        steps = {ks[i + 1][1] - ks[i][1] for i in range(len(ks) - 1)}
        if len(steps) != 1:
            return None
        out[v] = (ks[0][1], steps.pop())
    return out


def check(planes, edge_list, exc=None, R=6):
    """(ok, reason).

    `planes[c]` is the max-of-affines description of class c and `edge_list` the directed
    edges (c, c', (dm, dn)). R bounds the box checked exhaustively; outside it the four
    half-planes m1 >= R+1, m1 <= -R-1, m2 >= R+1, m2 <= -R-1 cover the rest, and (c) is
    decided on each of those by region arithmetic.
    """
    Pl, den = _int_planes(planes)
    if den != 1:
        # a shift by an integer lattice vector must stay integral for _shift to be exact
        pass
    if max(co[2] for co in Pl[0]) != 0:
        return False, 'D is not 0 at the origin'
    nbr = {}
    for (c, c2, d) in edge_list:
        nbr.setdefault(c, []).append((c2, d))

    # the exceptional set, per class, as rays. `exc' is opt-in: with none of it the function
    # below is exactly `max_i l_i' and every caller behaves as before.
    rays = []
    if exc:
        import math
        for E in exc:
            if not E:
                rays.append({})
                continue
            r = raymap(E)
            if r is None:
                return False, 'the exceptional set of a class is not a union of rays'
            rays.append({v: (d1 * den, st * den) for v, (d1, st) in r.items()})
    else:
        rays = [{} for _ in Pl]

    def D(c, m):
        base = max(A * m[0] + B * m[1] + C for (A, B, C) in Pl[c])
        if rays[c] and (m[0] or m[1]):
            import math as _m
            g = _m.gcd(abs(m[0]), abs(m[1])) or 1
            hit = rays[c].get((m[0] // g, m[1] // g))
            if hit is not None:
                # d(k) = d1 + (k-1)*step along the ray, which is the true distance there and
                # exceeds the max of planes by construction
                return hit[0] + (g - 1) * hit[1]
        return base

    # (a) and the exceptional box, exhaustively
    for c, P in enumerate(Pl):
        for m1 in range(-R, R + 1):
            for m2 in range(-R, R + 1):
                v = D(c, (m1, m2))
                wit = False
                for (c2, d) in nbr.get(c, ()):
                    w = D(c2, (m1 + d[0], m2 + d[1]))
                    if w > v + den:
                        return False, f'edge raises D by more than 1 at class {c} {(m1, m2)}'
                    if w == v - den:
                        wit = True
                if (c, m1, m2) != (0, 0, 0) and not wit:
                    return False, f'no predecessor at class {c} {(m1, m2)}'

    # --- the exceptional set as regions -------------------------------------------------
    # A ray k*v (k >= 1) lies on the line h.m = 0 with h = (-v[1], v[0]), and on it the true
    # distance is d1 + (k-1)*step, which is AFFINE in m: on the line m = k*v, so k = m[0]/v[0]
    # (or m[1]/v[1]), and r(m) = (step/v[0])*m[0] + (d1 - step). Everything below is therefore
    # still an affine function on a polyhedron, which is all `galpoly.nonneg' needs. Nothing
    # here is new machinery; what is new is that the region a condition is checked on now
    # knows where D is not the max of planes.
    def ray_line(v):
        return (-v[1], v[0], 0)

    def ray_pos(v):
        """the half of the line with k >= 1, as one constraint"""
        if v[0]:
            return (1, 0, -1) if v[0] > 0 else (-1, 0, -1)
        return (0, 1, -1) if v[1] > 0 else (0, -1, -1)

    def ray_aff(v, d1, step):
        """r(m) on the line, as an affine form with Fraction coefficients"""
        if v[0]:
            return (Fraction(step, v[0]), Fraction(0), Fraction(d1 - step))
        return (Fraction(0), Fraction(step, v[1]), Fraction(d1 - step))

    def off_ray_pieces(c, reg):
        """`reg` split into polyhedra on which D_c IS the max of planes"""
        hs = [ray_line(v) for v in rays[c]]
        seen = set()
        lines = []
        for h in hs:
            k = h if h[0] > 0 or (h[0] == 0 and h[1] > 0) else (-h[0], -h[1], 0)
            if k not in seen:
                seen.add(k)
                lines.append(k)
        out = [list(reg)]
        for h in lines:
            nxt = []
            for piece in out:
                nxt.append(piece + [(h[0], h[1], -1)])          # h.m >= 1
                nxt.append(piece + [(-h[0], -h[1], -1)])        # h.m <= -1
            out = nxt
        return out

    def on_ray_piece(c, reg, v):
        """`reg` intersected with the ray k*v, k >= 1"""
        h = ray_line(v)
        return list(reg) + [(h[0], h[1], 0), (-h[0], -h[1], 0), ray_pos(v)]

    # (b) everywhere, as an affine inequality on each region
    for c, P in enumerate(Pl):
        for i, reg in enumerate(cells(P)):
            Ai, Bi, Ci = P[i]
            src_here = [((Fraction(Ai), Fraction(Bi), Fraction(Ci)), pc)
                        for pc in off_ray_pieces(c, reg)]
            # and where m IS on a ray of class c, D_c is the ray's own affine form and the
            # inequality is WEAKER there, not stronger -- checking the plane on the ray is what
            # made (b) fail on A310039's class 0 region 0
            for v, (d1, st) in rays[c].items():
                src_here.append((ray_aff(v, d1, st), on_ray_piece(c, reg, v)))
            for (c2, d) in nbr.get(c, ()):
                for (fsrc, piece) in src_here:
                    if galpoly.empty(piece):
                        continue
                    # the TARGET splits the same way: off every c2-ray it is a plane, and on
                    # one it is that ray's affine form, evaluated at m + d
                    tgt = [((Fraction(A2), Fraction(B2), Fraction(C2)), pp)
                           for (A2, B2, C2) in (_shift(co, d, den) for co in Pl[c2])
                           for pp in [piece]]
                    for v2, (d12, st2) in rays[c2].items():
                        h2 = ray_line(v2)
                        # m + d on the ray k*v2 is a line in m, and the ray's affine form in
                        # m + d is affine in m
                        a2, b2, c2f = ray_aff(v2, d12, st2)
                        shifted = (a2, b2, c2f + a2 * d[0] + b2 * d[1])
                        pos = ray_pos(v2)
                        pp = piece + [(h2[0], h2[1], h2[0] * d[0] + h2[1] * d[1]),
                                      (-h2[0], -h2[1], -(h2[0] * d[0] + h2[1] * d[1])),
                                      (pos[0], pos[1], pos[2] + pos[0] * d[0] + pos[1] * d[1])]
                        tgt.append((shifted, pp))
                    for (ftgt, pp) in tgt:
                        if galpoly.empty(pp):
                            continue
                        f = (fsrc[0] - ftgt[0], fsrc[1] - ftgt[1],
                             fsrc[2] + den - ftgt[2])
                        if not galpoly.nonneg(f, pp):
                            return False, f'(b) fails on class {c} region {i}'

    # (c) outside the box: P_i must be covered by the neighbours' regions
    HALF = [(1, 0, -(R + 1)), (-1, 0, -(R + 1)), (0, 1, -(R + 1)), (0, -1, -(R + 1))]
    for c, P in enumerate(Pl):
        for i, reg in enumerate(cells(P)):
            Ai, Bi, Ci = P[i]
            for H in HALF:
                left = [list(reg) + [H]]
                if galpoly.empty(left[0]):
                    continue
                for (c2, d) in nbr.get(c, ()):
                    S = []
                    for co in Pl[c2]:
                        A2, B2, C2 = _shift(co, d, den)
                        S.append((Ai - A2, Bi - B2, Ci - den - C2))
                    nxt = []
                    for piece in left:
                        nxt.extend(galpoly.subtract(piece, S))
                        if len(nxt) > CAP:
                            return None, 'region arithmetic exceeded the cap'
                    left = nxt
                    if not left:
                        break
                if left:
                    return False, f'(c) not covered on class {c} region {i}'
    return True, 'ok'
