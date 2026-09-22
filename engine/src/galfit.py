#!/usr/bin/env python3
"""One place that turns (tiling, vertex) into the data a certificate needs.

`galcoord` had this inline and `galcert`'s tests had their own copy, which is how the two
disagreed about which class is the origin. It returns

    {'planes': [[(A, B, C), ...] per class], 'edges': [(c, c', (dm, dn))], ...}

or None with a reason, and it makes one check `galhull` does not: the fit is made on the INNER
patch (distance <= R - margin) and then validated on the WHOLE patch, rim included.

That matters. `galhull.pieces` reports "no leftovers" when its max reaches every point it was
GIVEN, and its supports were only ever validated against those same points. On Gal.8.x at
radius 110 the fit had no leftovers and still exceeded the true distance by one at 35 rim
points -- the distance is not convex there, so no max of affine pieces equals it, and the fit
was a fit of something else. Validating on the rim says so in a second, instead of leaving it
for the whole-lattice certificate to discover expensively or, worse, not at all.
"""
import gallat
import galhull
import galtile


def data(u, t, v, radius=70, margin=6, minpts=40, refine=(1, 1), exc=False):
    """(data, None) or (None, reason)

    `refine` passes to a SUBLATTICE (k1*a, k2*b) of the translation lattice, which splits each
    vertex class into k1*k2 subclasses. The distance of a periodic graph is a polyhedral norm
    plus a correction that is periodic, not convex -- measured over the 379 coordination
    sequences, the fit made on an inner patch EXCEEDS the true distance further out, by up to
    5, on most tilings, and no patch radius fixes that because the excess is not an artifact of
    the radius. Refining the lattice absorbs a correction whose period divides the refinement:
    on each subclass the remaining function can be convex even when it is not on the class.
    """
    T = galtile.tilings()
    types = T.get((u, t))
    if not types:
        return None, 'tiling missing'
    letters = sorted(types)
    if not 1 <= v <= len(letters):
        return None, 'vertex index out of range'
    start = letters[v - 1]
    L = gallat.lattice(types, start=start)
    if L is None:
        return None, 'no translation lattice'
    a, b = L
    k1, k2 = refine
    a = tuple(k1 * x for x in a)
    b = tuple(k2 * x for x in b)
    seen = gallat.patch(types, radius, start=start)
    if not seen:
        return None, 'no patch'

    reps, cells = [], []

    def find(pos, l, r, f):
        s = gallat.sig(types, l, r, f)
        for ci, (rp, rl, rr, rf) in enumerate(reps):
            if gallat.sig(types, rl, rr, rf) != s:
                continue
            c = gallat.coords(gallat._sub(pos, rp), a, b)
            if c is not None:
                return ci, c, rp
        return None

    for pos, (l, r, f, d) in seen.items():
        hit = find(pos, l, r, f)
        if hit is None:
            reps.append((pos, l, r, f))
            cells.append([(0, 0, d)])
        else:
            cells[hit[0]].append((hit[1][0], hit[1][1], d))
    # the start vertex must be class 0 at the origin: the certificate's one exception is there
    if not cells or (0, 0, 0) not in cells[0]:
        return None, 'the start vertex is not class 0 at the origin'

    planes = []
    excpts = []
    for lst in cells:
        if len(lst) < minpts:
            return None, 'a class has too few patch points'
        # Fitted on the WHOLE patch, not on the inside of it. `galhull.scan` takes
        # C = min(d - A*m - B*n) over the points it is GIVEN, so every plane it returns is a
        # support at those points and only those; fitting on d <= R - margin and then looking
        # at the rim found the fit exceeding the true distance on 72 of 98 entries. That was a
        # statement about which points the fit had been shown, not about the tiling: given the
        # whole patch the same two tilings fit with no leftovers at all. Whether the planes are
        # right OUTSIDE the patch is not decided here and must not be -- `galcert2` decides it.
        pl, left = galhull.pieces(lst)
        if left and exc:
            # EXCEPTIONAL SET. The distance on this class is not a max of affine pieces, and
            # measured on 22 September the uncovered points are usually a pair of opposite RAYS
            # through the origin with d affine along the ray (IDEAS A11). Carried out rather
            # than refused, so the ball count can subtract them:
            #     |B(t)| = #{max_i l_i <= t} - #{exceptional m : max_i l_i(m) <= t < d(m)}
            # On a ray both bounds are affine in the ray parameter, so that correction is
            # quasi-linear in t and leaves a(n) quasi-linear -- the shape galehr already fits.
            # Nothing here certifies it; `exc` is opt-in and the caller must say what it does
            # with the points.
            P = [(int(A), int(B), int(C)) for A, B, C in pl]
            # the exceptional set is every patch point the planes do not reach, not just the
            # ones `galhull.pieces' returns: it reports only those with d <= max(d) - margin,
            # deliberately leaving the rim band out, and a point in that band is still a point
            # the max of planes does not equal.
            bad = [(int(m), int(n), int(dd)) for (m, n, dd) in lst
                   if max(A * m + B * n + C for A, B, C in P) != dd]
            over = [x for x in bad
                    if max(A * x[0] + B * x[1] + C for A, B, C in P) > x[2]]
            if over:
                # a plane ABOVE the true distance is not an exceptional point, it is a wrong
                # fit, and must still refuse
                return None, 'a fitted plane exceeds the distance at %d patch points' % len(over)
            excpts.append(bad)
            planes.append(P)
            continue
        if left:
            # the COUNT, not just the fact. Whether a class leaves 3 points uncovered out of
            # 400 or 120 out of 400 is the difference between a patch that is too small and a
            # distance function that genuinely is not a max of affine pieces, and it decides
            # whether RADIUS is the lever. It was computed on every one of these refusals and
            # thrown away, which is why 355 declines looked like one problem.
            return None, ('distance is not a max of affine pieces '
                          '(%d of %d points uncovered by %d pieces)'
                          % (len(left) if hasattr(left, '__len__') else left,
                             len(lst), len(pl)))
        P = [(int(A), int(B), int(C)) for A, B, C in pl]
        for (m, n, d) in lst:
            if max(A * m + B * n + C for A, B, C in P) != d:
                return None, 'the fit fails on the patch'
        planes.append(P)
        excpts.append([])

    def cls_of(q, nl, nr, nf):
        h = find(q, nl, nr, nf)
        return None if h is None else (h[0], h[2])

    out = []
    for ci, (pos, letter, rot, refl) in enumerate(reps):
        ns = galtile.neighbours(pos, letter, rot, refl, types)
        if ns is None:
            return None, 'neighbours not available'
        for (q, nl, nr, nf) in ns:
            cj = cls_of(q, nl, nr, nf)
            if cj is None:
                return None, 'a neighbour is outside the patch'
            j, rep = cj
            off = gallat.coords(gallat._sub(q, rep), a, b)
            if off is None:
                return None, 'an edge is not expressible in lattice coordinates'
            out.append((ci, j, off))
    return {'planes': planes, 'exc': excpts, 'edges': out, 'classes': len(planes),
            'start': start, 'u': u, 't': t, 'v': v, 'radius': radius,
            'refine': (k1, k2)}, None
