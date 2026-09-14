#!/usr/bin/env python3
"""Exact integer polyhedra in the plane, for the Galebach distance certificate.

`galcert` decided its conditions by sampling three points per cone, on the argument that an
affine statement true at three affinely independent points of a cone is true on all of it.
That argument is wrong twice over: the sampler could not tell whether its three points were in
the cone at all (it returned None and the cone was silently skipped), and condition (c) is not
an affine statement but a DISJUNCTION -- each sampled point may have a different predecessor
while no single one serves the whole cone. It accepted A310511, whose coordination sequence
diverges from the fitted model at term 35.

What is needed instead is the real region arithmetic, and in the plane that is small:

    a constraint is (a, b, c) meaning  a*m + b*n + c >= 0, with a, b, c INTEGERS,
    a region is a list of constraints.

Everything here is integer or Fraction; there is no tolerance anywhere. Only LATTICE points
matter, so a region is called empty when it holds no integer point -- and since proving that
exactly is not needed, `empty` proves the stronger real emptiness and otherwise reports
"maybe". A "maybe" can only ever cost a refusal, never a false certificate.
"""
from fractions import Fraction

BIG = 10 ** 9


def _vertex(p, q):
    """the intersection of two constraint lines as exact rationals, or None if parallel"""
    a1, b1, c1 = p
    a2, b2, c2 = q
    det = a1 * b2 - a2 * b1
    if det == 0:
        return None
    return (Fraction(-c1 * b2 + c2 * b1, det), Fraction(-a1 * c2 + a2 * c1, det))


def _sat(con, pt):
    a, b, c = con
    return a * pt[0] + b * pt[1] + c >= 0


def vertices(cons):
    """the vertices of the region: pairwise line intersections that satisfy every constraint"""
    out = []
    for i in range(len(cons)):
        for j in range(i + 1, len(cons)):
            v = _vertex(cons[i], cons[j])
            if v is None:
                continue
            if all(_sat(c, v) for c in cons):
                if v not in out:
                    out.append(v)
    return out


def rays(cons):
    """generators of the recession cone {d : a*d1 + b*d2 >= 0 for every constraint}.

    In the plane the extreme rays of such a cone are among the two normals' rotations, so the
    candidates are (-b, a) and (b, -a) for each constraint, plus the axes when there are no
    constraints at all. A candidate is a ray of the cone when it satisfies every constraint's
    homogeneous part.
    """
    cand = []
    for a, b, _c in cons:
        for d in ((-b, a), (b, -a)):
            if d != (0, 0) and d not in cand:
                cand.append(d)
    if not cand:
        cand = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    return [d for d in cand if all(a * d[0] + b * d[1] >= 0 for a, b, _c in cons)]


def _full_rank(cons):
    """True when the constraints' normals span the plane (so the region is pointed or empty)"""
    for i in range(len(cons)):
        for j in range(i + 1, len(cons)):
            a1, b1, _ = cons[i]
            a2, b2, _ = cons[j]
            if a1 * b2 - a2 * b1 != 0:
                return True
    return False


def empty(cons):
    """True only when the region provably holds no real point.

    A region in the plane is non-empty exactly when it has a vertex, or its recession cone has
    a ray from some feasible point. Rather than a general LP, the two cases are separated: if
    the normals span the plane the region is pointed, so it is non-empty iff it has a vertex;
    otherwise every constraint is a half-plane with one of two opposite normals (or the region
    is a slab or all of the plane), and feasibility is a one-dimensional interval test.
    """
    if not cons:
        return False
    if _full_rank(cons):
        return not vertices(cons)
    # all normals parallel: reduce to t = a*m + b*n on the common direction
    a0, b0 = next(((a, b) for a, b, _ in cons if (a, b) != (0, 0)), (0, 0))
    lo, hi = None, None
    for a, b, c in cons:
        if (a, b) == (0, 0):
            if c < 0:
                return True
            continue
        # (a, b) = s * (a0, b0) for some rational s
        s = Fraction(a, a0) if a0 else Fraction(b, b0)
        # s*t + c >= 0
        if s > 0:
            v = Fraction(-c, s)
            lo = v if lo is None else max(lo, v)
        else:
            v = Fraction(-c, s)
            hi = v if hi is None else min(hi, v)
    return lo is not None and hi is not None and lo > hi


def nonneg(f, cons):
    """is the affine f = (a, b, c) non-negative at every point of the region?

    For a non-empty region, an affine function attains its infimum at a vertex or decreases
    along a ray, so the test is: f >= 0 at every vertex, and the gradient pairs non-negatively
    with every ray. An empty region satisfies it vacuously. When the region is not pointed the
    vertices do not describe it, and the answer is only reported when the gradient settles it
    on its own.
    """
    if empty(cons):
        return True
    a, b, c = f
    rs = rays(cons)
    if any(a * d[0] + b * d[1] < 0 for d in rs):
        return False
    if not _full_rank(cons):
        # unpointed: f is bounded below on it only if the gradient is orthogonal to the
        # common direction; then f is constant along it and one feasible point decides.
        pt = _any_point(cons)
        return pt is not None and a * pt[0] + b * pt[1] + c >= 0
    vs = vertices(cons)
    if not vs:
        return True
    return all(a * v[0] + b * v[1] + c >= 0 for v in vs)


def _any_point(cons):
    """some feasible point of an unpointed region, or None"""
    for a, b, c in cons:
        if (a, b) != (0, 0):
            # walk out along the normal from the origin until every constraint holds
            for k in range(0, 4 * BIG, max(1, abs(c) + 1)):
                p = (Fraction(a * k, a * a + b * b), Fraction(b * k, a * a + b * b))
                if all(_sat(q, p) for q in cons):
                    return p
                p = (-p[0], -p[1])
                if all(_sat(q, p) for q in cons):
                    return p
                if k > 4 * (abs(c) + 1) * (len(cons) + 2):
                    break
    return (Fraction(0), Fraction(0)) if all(c >= 0 for _a, _b, c in cons) else None


def subtract(cons, other):
    """the pieces of `cons` outside `other`, as a list of regions.

    A point fails `other` when it violates one of its constraints, so the complement splits
    into one piece per constraint of `other`: violate that one and satisfy the ones before it.
    Only LATTICE points matter, so violating a*m + b*n + c >= 0 is a*m + b*n + c <= -1, which
    keeps every coefficient integral -- there is no strict inequality anywhere in this file.
    """
    out = []
    for t, (a, b, c) in enumerate(other):
        piece = list(cons) + [(-a, -b, -c - 1)] + list(other[:t])
        if not empty(piece):
            out.append(piece)
    return out
