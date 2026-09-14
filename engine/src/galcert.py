#!/usr/bin/env python3
"""Does a fitted distance function actually hold on the WHOLE lattice?

`galhull` fits d = max_i(A*m + B*n + C) on a patch and checks it on that patch, which is
circular: a cone whose region lies outside the patch cannot appear as a leftover, so the fit
certifies itself. On A310102 the fitted form agreed with breadth-first search for 29 terms and
diverged at the 30th, one step past the fitting radius.

The honest check is the pair of Bellman conditions, which do not care where D came from. Write
the tiling's edges as (class c, class c', lattice offset (dm, dn)). With D(origin) = 0:

    (b)  D_{c'}(m + dm, n + dn) <= D_c(m, n) + 1     for every edge and every (m, n)
    (c)  every (m, n) other than the origin has an edge attaining D_c = D_{c'} + 1

Together these force D = d, by the same two inductions `kdcert` uses.

Both are decided here WITHOUT a general LP, using the one thing that makes this tractable: D is
piecewise affine, so past the last breakpoint of the arrangement every condition is affine on a
cone, and an affine statement that holds at three affinely independent points of a cone holds
on all of it. So the check is: exhaustively inside the breakpoint radius, and three points per
cone outside it. The breakpoint radius is computed from the planes, not guessed.
"""
from fractions import Fraction

import gallat


def edges(types, a, b, reps, cls_of):
    """the tiling's edges as (class index, class index, (dm, dn)), one entry per directed edge"""
    import galtile
    out = []
    for ci, (pos, letter, rot, refl) in enumerate(reps):
        ns = galtile.neighbours(pos, letter, rot, refl, types)
        if ns is None:
            return None
        for (q, nl, nr, nf) in ns:
            cj = cls_of(q, nl, nr, nf)
            if cj is None:
                return None
            j, rep = cj
            off = gallat.coords(gallat._sub(q, rep), a, b)
            if off is None:
                return None
            out.append((ci, j, off))
    return out


def breakpoint_radius(planes):
    """past this, every cone is a genuine cone and the max-plane assignment never changes again"""
    r = 1
    for P in planes:
        for i in range(len(P)):
            for j in range(i + 1, len(P)):
                A1, B1, C1 = P[i]
                A2, B2, C2 = P[j]
                dA, dB, dC = A1 - A2, B1 - B2, C1 - C2
                if dA == 0 and dB == 0:
                    continue
                # the line g_i = g_j passes within |dC| / |(dA, dB)| of the origin
                den = max(abs(dA), abs(dB))
                if den:
                    r = max(r, abs(dC) // den + 2)
    return r


def _D(P, m, n):
    return max(A * m + B * n + C for (A, B, C) in P)


def check(planes, edge_list, R=None, margin=6):
    """(ok, reason). ok is True only when both conditions are established everywhere."""
    if R is None:
        R = breakpoint_radius(planes) + margin
    # (1) exhaustively on the lattice points inside the breakpoint radius
    for ci, P in enumerate(planes):
        for m in range(-R, R + 1):
            for n in range(-R, R + 1):
                v = _D(P, m, n)
                witness = False
                for (a_, b_, (dm, dn)) in edge_list:
                    if a_ != ci:
                        continue
                    w = _D(planes[b_], m + dm, n + dn)
                    if w > v + 1:
                        return False, 'edge raises D by more than 1 at (%d,%d)' % (m, n)
                    if w == v - 1:
                        witness = True
                if (m, n) != (0, 0) or ci != 0:
                    if not witness:
                        return False, 'no predecessor at class %d (%d,%d)' % (ci, m, n)
    # (2) three affinely independent points per cone, outside the breakpoint radius
    for ci, P in enumerate(planes):
        for i, (A, B, C) in enumerate(P):
            pts = _cone_points(P, i, R)
            if pts is None:
                continue                  # this plane is never the strict max: it is redundant
            for (m, n) in pts:
                v = _D(P, m, n)
                witness = False
                for (a_, b_, (dm, dn)) in edge_list:
                    if a_ != ci:
                        continue
                    w = _D(planes[b_], m + dm, n + dn)
                    if w > v + 1:
                        return False, 'edge raises D by more than 1 far out at (%d,%d)' % (m, n)
                    if w == v - 1:
                        witness = True
                if not witness:
                    return False, 'no predecessor far out at class %d (%d,%d)' % (ci, m, n)
    return True, 'ok'


def _cone_points(P, i, R):
    """three affinely independent lattice points well inside the cone where plane i is the max"""
    A, B, C = P[i]
    found = []
    for scale in (2, 3, 5):
        for (dx, dy) in ((1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, -1), (1, -1), (-1, 1)):
            m, n = A * scale * R + dx * R, B * scale * R + dy * R
            if _D(P, m, n) == A * m + B * n + C:
                if all((m - p[0]) * (n - q[1]) - (n - p[1]) * (m - q[0]) != 0
                       for p in found for q in found if p != q) or len(found) < 2:
                    found.append((m, n))
            if len(found) >= 3:
                return found
    return found or None
