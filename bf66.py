#!/usr/bin/env python3
"""Independent brute force for the graph-colouring family.

The graphs are rebuilt here by a different route from the one transfer66 uses -- the cube from
its eight corner points and six face normals in space, the icosahedron as a pentagonal
antiprism capped at both poles -- and the arrays are then written out cell by cell, each cell
tested against the already-placed cells it must be joined to. No row state, no walk, no
recurrence.
"""
import json, sys
import localentry as LE, transfer66

DIRV = {'horizontal': (0, 1), 'vertical': (1, 0), 'diagonal': (1, 1),
        'antidiagonal': (1, -1)}


def cube_faces():
    """The six face normals of a cube; two faces meet unless their normals are opposite."""
    N = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    E = {(i, j) for i in range(6) for j in range(6)
         if i < j and sum(a * b for a, b in zip(N[i], N[j])) != -1}
    return 6, E


def cube_vertices():
    """The eight corners of the cube in space; an edge is a pair at the shortest distance."""
    P = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    E = {(i, j) for i in range(8) for j in range(8)
         if i < j and sum((a - b) ** 2 for a, b in zip(P[i], P[j])) == 4}
    return 8, E


def icosa_vertices():
    """A pentagonal antiprism with a pole glued to each end."""
    up = [1 + i for i in range(5)]
    lo = [6 + i for i in range(5)]
    E = set()

    def add(a, b):
        E.add((min(a, b), max(a, b)))
    for i in range(5):
        add(0, up[i])
        add(11, lo[i])
        add(up[i], up[(i + 1) % 5])
        add(lo[i], lo[(i + 1) % 5])
        add(up[i], lo[i])
        add(up[i], lo[(i - 1) % 5])
    return 12, E


def icosa_faces():
    n, E = icosa_vertices()
    adj = {i: set() for i in range(n)}
    for a, b in E:
        adj[a].add(b)
        adj[b].add(a)
    F = sorted({tuple(sorted((a, b, c))) for a, b in E for c in adj[a] & adj[b]})
    G = {(i, j) for i in range(len(F)) for j in range(len(F))
         if i < j and len(set(F[i]) & set(F[j])) == 2}
    return len(F), G


def triangle(side):
    idx, k = {}, 0
    for i in range(side):
        for j in range(i + 1):
            idx[(i, j)] = k
            k += 1
    E = set()
    for (i, j), u in idx.items():
        for q in ((i, j + 1), (i + 1, j), (i + 1, j + 1)):
            if q in idx:
                v = idx[q]
                E.add((min(u, v), max(u, v)))
    return k, E


BUILDERS = {'faces of a cube': cube_faces, 'vertices of a cube': cube_vertices,
            'vertices of an icosahedron': icosa_vertices,
            'faces of an icosahedron': icosa_faces}


def graph_of(p):
    g = p['graph']
    if g in BUILDERS:
        return BUILDERS[g]()
    if g.startswith('triangular'):
        return triangle(int(g.split()[1]))
    N = p['N']
    return N, set(p['edges'])


def count(R, C, N, E, dirs, start0):
    A = [[False] * N for _ in range(N)]
    for a, b in E:
        A[a][b] = A[b][a] = True
    back = []
    for w in dirs:
        di, dj = DIRV[w]
        back += [(di, dj), (-di, -dj)]
    g = [[0] * C for _ in range(R)]
    tot, res = R * C, 0

    def rec(t):
        nonlocal res
        if t == tot:
            res += 1
            return
        i, j = divmod(t, C)
        for x in (range(1) if (t == 0 and start0) else range(N)):
            ok = True
            for di, dj in back:
                i2, j2 = i + di, j + dj
                if 0 <= i2 < R and 0 <= j2 < C and i2 * C + j2 < t and not A[x][g[i2][j2]]:
                    ok = False
                    break
            if ok:
                g[i][j] = x
                rec(t + 1)
    rec(0)
    return res


def check(anum, steps=3):
    e = LE.get(anum)
    p = transfer66.parse_name(e['name'])
    N, E = graph_of(p)
    if N != p['N']:
        return anum, 'GRAPH SIZE', (N, p['N'])
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    W = p['W']
    dirs = p['dirs']
    if p['trans']:      # count in the entry's own orientation, undoing the parser's transpose
        dirs = ['vertical' if w == 'horizontal' else
                'horizontal' if w == 'vertical' else w for w in dirs]
    out = []
    for k in range(1, steps + 1):
        R, C = (W, k) if p['trans'] else (k, W)
        out.append(count(R, C, N, E, dirs, p['start0']) // p['frac'])
    for s in range(len(d) - len(out) + 1):
        if d[s:s + len(out)] == out:
            return anum, 'OK', (len(out), s)
    return anum, 'MISMATCH', (out, d[:6])


if __name__ == '__main__':
    import collections
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer66' and not h.get('FAILS')]
    todo = sys.argv[1:] or [h['anum'] for h in hits]
    c = collections.Counter()
    for a in todo:
        r = check(a)
        c[r[1]] += 1
        if r[1] != 'OK':
            print(*r)
    print(c)
