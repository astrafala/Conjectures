#!/usr/bin/env python3
"""The translation lattice of a Galebach tiling, and vertices in lattice coordinates.

A translation is a symmetry when it carries every vertex to a vertex with the same type AND
the same set of edge directions. Comparing the raw frame instead finds NOTHING: the frame this
code carries is finer than the tiling's own symmetry, because a vertex figure with a rotational
symmetry (6^3 is symmetric under 120 degrees) has several frames describing the same vertex.
That cost a false start, so the signature below is the edge-direction set.
"""
import galtile

DEG = galtile.DEG
ORIGIN = tuple([0] * DEG)


def _add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def _sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def patch(types, R, start=None):
    """every vertex within R steps: {position: (letter, rot, refl, distance)}"""
    if start is None:
        start = sorted(types)[0]
    seen = {ORIGIN: (start, 0, False, 0)}
    frontier = [(ORIGIN, start, 0, False)]
    for n in range(1, R + 1):
        nxt = []
        for (p, l, r, f) in frontier:
            ns = galtile.neighbours(p, l, r, f, types)
            if ns is None:
                return None
            for (q, nl, nr, nf) in ns:
                if q not in seen:
                    seen[q] = (nl, nr, nf, n)
                    nxt.append((q, nl, nr, nf))
        frontier = nxt
        if not nxt:
            break
    return seen


def sig(types, l, r, f):
    """what identifies a vertex up to translation: its type and its edge directions"""
    conf, _ = types[l]
    d = galtile._dirs(galtile._conf(conf))
    return (l, tuple(sorted(((-x if f else x) + r) % 24 for x in d)))


def _indep(a, b):
    for i in range(DEG):
        for j in range(i + 1, DEG):
            if a[i] * b[j] - a[j] * b[i] != 0:
                return True
    return False


def _automorphism(types, seen, v, inner):
    """does translating by v carry the tiling's EDGES to its edges, not just its signatures?

    The signature is the vertex type and its set of edge directions, and that is NOT enough. A
    vertex figure with a symmetry (6^3 under 120 degrees) has several frames describing the
    same direction set, and the polygons sitting between the edges can then differ. On
    Gal.4.142 the shortest signature-preserving vector fails to be a symmetry at 140 of 700
    inner vertices, and every class, every edge offset and every distance built on it is wrong.
    Nothing downstream could see that: `galcert2` caught it as "no predecessor at (-1, 0)",
    which is a true statement about a function that was never the distance.

    The honest test is the one the word "symmetry" means: w + v is a vertex of the same type
    for every inner w, and the neighbours of w + v are exactly the neighbours of w translated.
    """
    for w, (l, r, f, d) in seen.items():
        if d > inner:
            continue
        u = _add(w, v)
        if u not in seen:
            continue
        if seen[u][0] != l:
            return False
        nw = galtile.neighbours(w, l, r, f, types)
        nu = galtile.neighbours(u, seen[u][0], seen[u][1], seen[u][2], types)
        if nw is None or nu is None:
            continue
        if {_add(q, v) for (q, _a, _b, _c) in nw} != {q for (q, _a, _b, _c) in nu}:
            return False
    return True


def lattice(types, R=22, inner=12, start=None):
    """two shortest independent translations, or None.

    `start` MUST be the vertex the caller's own patch was laid out from. The positions this
    module works in are absolute in Z[zeta_24] and a patch laid out from a different vertex is
    a different embedding -- rotated, reflected, or both -- so a translation that is a symmetry
    of one is not a symmetry of the other. `galcoord` built its patch from the entry's own
    vertex letter and took the lattice from the default one, and on Gal.4.142 the resulting
    vector was not a symmetry at 140 of 700 inner vertices. Everything downstream -- classes,
    edge offsets, distances -- was then a function of something that was not the tiling.
    """
    seen = patch(types, R, start=start)
    if not seen:
        return None
    S = {v: sig(types, l, r, f) for v, (l, r, f, _d) in seen.items()}
    D = {v: d for v, (_l, _r, _f, d) in seen.items()}
    o = S[ORIGIN]
    good = []
    for v, s in S.items():
        if s != o or v == ORIGIN:
            continue
        ok, checked = True, 0
        for w, sw in S.items():
            if D[w] > inner:
                continue
            u = S.get(_add(w, v))
            if u is None:
                continue
            checked += 1
            if u != sw:
                ok = False
                break
        if ok and checked > 25 and _automorphism(types, seen, v, inner):
            good.append((D[v], v))
    good.sort()
    if not good:
        return None
    a = good[0][1]
    for _d, b in good:
        if _indep(a, b):
            return a, b
    return None


def coords(v, a, b):
    """(m, n) with v = m*a + n*b, or None when v is not in the lattice"""
    for i in range(DEG):
        for j in range(i + 1, DEG):
            det = a[i] * b[j] - a[j] * b[i]
            if det == 0:
                continue
            mnum = v[i] * b[j] - v[j] * b[i]
            nnum = a[i] * v[j] - a[j] * v[i]
            if mnum % det or nnum % det:
                return None
            m, n = mnum // det, nnum // det
            for k in range(DEG):            # verified in EVERY coordinate, so a chance
                if m * a[k] + n * b[k] != v[k]:   # agreement in one minor cannot pass
                    return None
            return (m, n)
    return None


def classes(types, a, b, R=22):
    """{(signature, representative): [(m, n, distance), ...]} -- the translation classes"""
    seen = patch(types, R)
    reps, out = {}, {}
    for v, (l, r, f, d) in seen.items():
        s = sig(types, l, r, f)
        placed = False
        for key in reps:
            if key[0] != s:
                continue
            c = coords(_sub(v, reps[key]), a, b)
            if c is not None:
                out[key].append((c[0], c[1], d))
                placed = True
                break
        if not placed:
            key = (s, v)
            reps[key] = v
            out[key] = [(0, 0, d)]
    return out
