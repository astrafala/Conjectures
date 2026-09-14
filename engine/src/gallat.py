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


def lattice(types, R=22, inner=12):
    """two shortest independent translations, or None"""
    seen = patch(types, R)
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
        if ok and checked > 25:
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
