#!/usr/bin/env python3
"""`Rolling cube footprints: number of n X W 0..5 arrays starting with 0 where 0..5 label faces
of a cube and every array movement to a horizontal or vertical neighbor moves across a
corresponding cube edge.'

Fix a finite graph $G$ on the label set. The array is a map from its cells to the vertices of
$G$, and the condition is that any two cells adjacent in one of the named array directions ---
horizontal, vertical, diagonal, antidiagonal --- carry vertices joined by an edge of $G$. Some
entries add that the top-left cell carries the vertex $0$.

Four graphs are named outright and two are given by an edge list:

    faces of a cube            two faces are adjacent unless opposite: the octahedron graph
    vertices of a cube         the 3-cube $Q_3$
    faces of an icosahedron    two faces are adjacent when they share an edge: the
                               dodecahedron graph
    vertices of an icosahedron the icosahedron graph
    the fully triangulated graph   a triangle of side $k$ in the triangular lattice
    nodes of a graph with edges ... the edges as listed

The labelling is never in doubt, and does not need to be. The condition speaks only of the edge
relation, so relabelling the vertices carries the arrays of one labelling bijectively onto those
of another; and the four named graphs are vertex-transitive, so even the entries that fix the
top-left cell at $0$ are counted the same whichever vertex is called $0$.

The state is one row (one slice in the direction the array grows) and nothing more: every
condition joins cells in the same slice or in two consecutive ones. Rows are extended one cell
at a time with pruning, because for the sparser graphs almost no full row is legal.
"""
import re
from itertools import combinations

import namecanon
import transfer19

FRAC = re.compile(r'^\s*(?:(Half)|One quarter|1/(\d+))\s+the number of\s+', re.I)
def _dim(t):
    return (r'(?:\((?P<%sa>n|\d+)\s*\+\s*(?P<%sb>\d+)\)|(?P<%sc>n|\d+))' % (t, t, t))
NAME = re.compile(
    r'^(?P<pre>.*?)\bnumber of\s+' + _dim('r') + r'\s*X\s*' + _dim('c') +
    r'\s+0\.\.(?P<m>\d+)\s+arrays(?P<st1>\s+starting with 0)?\s+where\s+0\.\.(?P<m2>\d+)\s+'
    r'label\s+(?P<gspec>.*?)\s+and every array movement to an?\s+(?P<dirs>[a-z, ]+?)\s+'
    r'neighbou?rs?\s+moves\s+(?:across|along)\s+(?P<tail>.*?)\s*$', re.I)
TAIL = re.compile(r'^(?:a corresponding cube edge|an icosahedral edge|an edge of this graph)'
                  r'(?P<st2>,\s*with the array starting at 0)?\s*\.?$', re.I)
DIRW = re.compile(r'\b(antidiagonal|diagonal|horizontal|vertical)\b', re.I)
TRI = re.compile(r'(\d+)\s*X\s*(\d+)\s*X\s*(\d+)\s+triangular graph', re.I)

ROWMAX = 400000
EMAX = 16000000
# The plain construction is used only when its size is known in advance to be manageable.
# Both bounds are computed exactly, by a dynamic programme over the columns, so the decision
# is a function of the entry alone -- not of whatever cap a caller happens to pass -- and a
# rebuild always takes the same path as the run that produced it.
PLAIN_ROWS = 300000
PLAIN_EDGES = 12000000


def plain_bounds(p):
    """(number of legal slices, number of edges) of the unlumped digraph, counted not built."""
    N, W, ds = p['N'], p['W'], set(p['dirs'])
    A = [[False] * N for _ in range(N)]
    for a, b in p['edges']:
        A[a][b] = A[b][a] = True
    horiz = 'horizontal' in ds
    if horiz:
        r = [1] * N
        for _ in range(W - 1):
            r = [sum(r[a] for a in range(N) if A[a][b]) for b in range(N)]
        rows = sum(r)
    else:
        rows = N ** W
    f = {}
    for a in range(N):
        for b in range(N):
            if 'vertical' in ds and not A[a][b]:
                continue
            f[(a, b)] = 1
    for _ in range(W - 1):
        g = {}
        for (a, b), c in f.items():
            for a2 in range(N):
                if horiz and not A[a][a2]:
                    continue
                if 'antidiagonal' in ds and not A[a2][b]:
                    continue
                for b2 in range(N):
                    if horiz and not A[b][b2]:
                        continue
                    if 'vertical' in ds and not A[a2][b2]:
                        continue
                    if 'diagonal' in ds and not A[a][b2]:
                        continue
                    g[(a2, b2)] = g.get((a2, b2), 0) + c
        f = g
    return rows, rows + sum(f.values())


def too_big(p):
    r, e = plain_bounds(p)
    return r > PLAIN_ROWS or e > PLAIN_EDGES


def _octahedron():
    """Face adjacency of the cube: six faces, adjacent unless opposite."""
    return 6, {(a, b) for a in range(6) for b in range(6) if a < b and a // 2 != b // 2}


def _q3():
    return 8, {(a, b) for a in range(8) for b in range(8)
               if a < b and bin(a ^ b).count('1') == 1}


def _icosa_pts():
    phi = (1 + 5 ** 0.5) / 2
    P = []
    for s1 in (1, -1):
        for s2 in (1, -1):
            P += [(0, s1, s2 * phi), (s1, s2 * phi, 0), (s1 * phi, 0, s2)]
    return P


def _icosahedron():
    P = _icosa_pts()
    n = len(P)

    def d2(a, b):
        return sum((x - y) ** 2 for x, y in zip(a, b))
    m = min(d2(P[i], P[j]) for i in range(n) for j in range(n) if i != j)
    return n, {(i, j) for i in range(n) for j in range(n)
               if i < j and abs(d2(P[i], P[j]) - m) < 1e-6}


def _icosa_faces():
    """Face adjacency of the icosahedron: its twenty triangles, adjacent when they share an
    edge. This is the dodecahedron graph."""
    n, E = _icosahedron()
    adj = {i: set() for i in range(n)}
    for a, b in E:
        adj[a].add(b)
        adj[b].add(a)
    F = [t for t in combinations(range(n), 3)
         if t[1] in adj[t[0]] and t[2] in adj[t[0]] and t[2] in adj[t[1]]]
    return len(F), {(i, j) for i in range(len(F)) for j in range(len(F))
                    if i < j and len(set(F[i]) & set(F[j])) == 2}


def _triangular(side):
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


GRAPHS = {
    'faces of a cube': (_octahedron, 'the faces of a cube, two of them adjacent unless they '
                                     'are opposite: the octahedron graph, $4$-regular on $6$ '
                                     'vertices'),
    'vertices of a cube': (_q3, 'the vertices of a cube: the graph $Q_3$, $3$-regular on $8$ '
                                'vertices'),
    'faces of an icosahedron': (_icosa_faces, 'the faces of an icosahedron, two of them '
                                              'adjacent when they share an edge: the '
                                              'dodecahedron graph, $3$-regular on $20$ '
                                              'vertices'),
    'vertices of an icosahedron': (_icosahedron, 'the vertices of an icosahedron: the '
                                                 'icosahedron graph, $5$-regular on $12$ '
                                                 'vertices'),
}


def parse_name(nm):
    nm = namecanon.canon(nm)
    s = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    frac = 1
    m = FRAC.match(s)
    if m:
        frac = 2 if m.group(1) else (4 if m.group(0).lower().startswith('one quarter')
                                     else int(m.group(2)))
        s = s[m.end():]
    m = NAME.match(s)
    if not m:
        return None
    t = TAIL.match(m.group('tail'))
    if not t:
        return None
    rows = m.group('ra') or m.group('rc')
    cols = m.group('ca') or m.group('cc')
    if rows is None or cols is None or (rows == 'n') == (cols == 'n'):
        return None
    if rows == 'n':
        W, trans = int(cols) + int(m.group('cb') or 0), False
    else:
        W, trans = int(rows) + int(m.group('rb') or 0), True
    alpha = int(m.group('m'))
    if int(m.group('m2')) != alpha:
        return None
    g = m.group('gspec').strip().lower()
    g = re.sub(r'^nodes of ', '', g) if g.startswith('nodes of ') else g
    if g in GRAPHS:
        N, E = GRAPHS[g][0]()
        gname = g
    elif g.startswith('a graph with edges'):
        pairs = re.findall(r'(\d+)\s*,\s*(\d+)', g)
        if not pairs:
            return None
        E = {(min(int(a), int(b)), max(int(a), int(b))) for a, b in pairs}
        N = max(max(e) for e in E) + 1
        gname = 'listed'
    elif g == 'the fully triangulated graph':
        mt = TRI.search(m.group('pre'))
        if not mt or len({mt.group(1), mt.group(2), mt.group(3)}) != 1:
            return None
        side = int(mt.group(1))
        N, E = _triangular(side)
        gname = 'triangular %d' % side
    else:
        return None
    if N != alpha + 1:
        return None
    words = [w.lower() for w in dict.fromkeys(DIRW.findall(m.group('dirs')))]
    if not words:
        return None
    orig = sorted(words)
    if trans:                    # transposing exchanges horizontal with vertical and fixes
        words = ['vertical' if w == 'horizontal' else                   # both diagonals
                 'horizontal' if w == 'vertical' else w for w in words]
    start0 = bool(m.group('st1') or t.group('st2'))
    if W < 1:
        return None
    p = {'W': W, 'alpha': alpha, 'N': N, 'edges': sorted(E), 'dirs': sorted(words),
         'orig': orig, 'start0': start0, 'graph': gname, 'trans': trans, 'frac': 1}
    return None if too_big(p) else p


def parse_any(nm):
    """The same reading with the size test left off, for the lumped engine to use."""
    global PLAIN_ROWS, PLAIN_EDGES
    a, b = PLAIN_ROWS, PLAIN_EDGES
    PLAIN_ROWS = PLAIN_EDGES = float('inf')
    try:
        return parse_name(nm)
    finally:
        PLAIN_ROWS, PLAIN_EDGES = a, b


def build(p, cap=400000):
    W, N = p['W'], p['N']
    ds = set(p['dirs'])
    A = [[False] * N for _ in range(N)]
    for a, b in p['edges']:
        A[a][b] = A[b][a] = True
    nbr = [[b for b in range(N) if A[a][b]] for a in range(N)]
    horiz = 'horizontal' in ds
    if not horiz and N ** W > ROWMAX:
        return None

    def rows(first):
        """All legal rows, built one cell at a time; `first` fixes the leading cell at 0."""
        out = []
        cur = [0] * W

        def rec(j):
            if j == W:
                out.append(tuple(cur))
                return
            cand = [0] if (j == 0 and first) else range(N)
            for x in cand:
                if horiz and j and not A[cur[j - 1]][x]:
                    continue
                cur[j] = x
                rec(j + 1)
        rec(0)
        return out

    idx, order, adj = {}, [], []

    def push(st):
        if st not in idx:
            idx[st] = len(order)
            order.append(st)
            adj.append(None)
        return idx[st]

    push(None)
    edges = 0
    t = 0
    while t < len(order):
        u = order[t]
        if u is None:
            out = [push(v) for v in rows(p['start0'])]
        else:
            out = []
            cur = [0] * W

            def rec(j):
                if j == W:
                    out.append(push(tuple(cur)))
                    return
                if 'vertical' in ds:
                    cand = nbr[u[j]]
                elif 'diagonal' in ds and j:
                    cand = nbr[u[j - 1]]
                elif 'antidiagonal' in ds and j + 1 < W:
                    cand = nbr[u[j + 1]]
                else:
                    cand = range(N)
                for x in cand:
                    if horiz and j and not A[cur[j - 1]][x]:
                        continue
                    if 'vertical' in ds and not A[u[j]][x]:
                        continue
                    if 'diagonal' in ds and j and not A[u[j - 1]][x]:
                        continue
                    if 'antidiagonal' in ds and j + 1 < W and not A[u[j + 1]][x]:
                        continue
                    cur[j] = x
                    rec(j + 1)
            rec(0)
        adj[t] = out
        edges += len(out)
        t += 1
        if len(order) > cap or edges > EMAX:
            return None
    n = len(order)
    st = [0] * n
    st[0] = 1
    return adj, st, [1] * n, n


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
