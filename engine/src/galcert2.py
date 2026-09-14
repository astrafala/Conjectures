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


def check(planes, edge_list, R=6):
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

    def D(c, m):
        return max(A * m[0] + B * m[1] + C for (A, B, C) in Pl[c])

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

    # (b) everywhere, as an affine inequality on each region
    for c, P in enumerate(Pl):
        for i, reg in enumerate(cells(P)):
            Ai, Bi, Ci = P[i]
            for (c2, d) in nbr.get(c, ()):
                for co in Pl[c2]:
                    A2, B2, C2 = _shift(co, d, den)
                    f = (Ai - A2, Bi - B2, Ci + den - C2)
                    if not galpoly.nonneg(f, reg):
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
