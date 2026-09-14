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


def data(u, t, v, radius=70, margin=6, minpts=40):
    """(data, None) or (None, reason)"""
    T = galtile.tilings()
    types = T.get((u, t))
    if not types:
        return None, 'tiling missing'
    letters = sorted(types)
    if not 1 <= v <= len(letters):
        return None, 'vertex index out of range'
    start = letters[v - 1]
    L = gallat.lattice(types)
    if L is None:
        return None, 'no translation lattice'
    a, b = L
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
    for lst in cells:
        inner = [(m, n, d) for m, n, d in lst if d <= radius - margin]
        if len(inner) < minpts:
            return None, 'a class has too few patch points'
        pl, left = galhull.pieces(inner)
        if left:
            return None, 'distance is not a max of affine pieces'
        P = [(int(A), int(B), int(C)) for A, B, C in pl]
        # validated on the WHOLE patch, rim included -- see the module docstring
        for (m, n, d) in lst:
            if max(A * m + B * n + C for A, B, C in P) != d:
                return None, 'the fit fails on the patch rim'
        planes.append(P)

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
    return {'planes': planes, 'edges': out, 'classes': len(planes),
            'start': start, 'u': u, 't': t, 'v': v, 'radius': radius}, None
