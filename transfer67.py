#!/usr/bin/env python3
"""The same graph-colouring arrays as transfer66, for the shapes whose slice alphabet is too
large to carry one state per slice.

The condition names only the edge relation of the graph $G$, so every automorphism $\\sigma$ of
$G$ acts on the arrays: applying $\\sigma$ to every cell carries a valid array to a valid array.
Acting on slices, $\\sigma$ commutes with the transfer matrix $M$, and the all-ones end vector
is fixed by it. That is exactly the hypothesis for LUMPING: the vector $M^{j}\\tau$ is constant
on the orbits of $\\Gamma=\\operatorname{Aut}(G)$, so the walk may be run on the orbits instead
of on the slices, with the orbit sizes as the starting weights. For the cube that divides the
state count by $|\\Gamma|=48$ and for the icosahedron by $120$.

The entries that fix the top-left cell at $0$ are handled by a second consequence of the same
symmetry. All four graphs here are vertex-transitive, so for any two vertices $v,w$ there is a
$\\sigma$ with $\\sigma v=w$, and $x\\mapsto\\sigma\\circ x$ is a bijection from the valid arrays
with $x(0,0)=v$ onto those with $x(0,0)=w$. The fibres of $x\\mapsto x(0,0)$ therefore all have
the same size, and the count the entry wants is the unrestricted count divided by the number of
vertices.

Orbit representatives are generated directly, never by listing the slices and grouping them: a
slice is built one cell at a time carrying the set of automorphisms that have so far written the
same prefix, and it is abandoned the moment one of them writes something lexicographically
smaller. What survives to the end is the lexicographically least member of its orbit, and the
set still tied at that point is its stabiliser --- so the orbit size comes out of the same walk,
by the orbit-stabiliser count.
"""
from collections import deque

import transfer19
import transfer66

STATEMAX = 400000
EMAX = 12000000


def automorphisms(N, E):
    """Every adjacency-preserving bijection of the vertex set, by backtracking in a BFS order."""
    A = [[False] * N for _ in range(N)]
    for a, b in E:
        A[a][b] = A[b][a] = True
    deg = [sum(A[v]) for v in range(N)]
    seen = [False] * N
    order = []
    for s in range(N):
        if seen[s]:
            continue
        seen[s] = True
        q = deque([s])
        while q:
            v = q.popleft()
            order.append(v)
            for w in range(N):
                if A[v][w] and not seen[w]:
                    seen[w] = True
                    q.append(w)
    out = []
    img = [-1] * N
    used = [False] * N

    def rec(k):
        if k == len(order):
            out.append(tuple(img))
            return
        v = order[k]
        for w in range(N):
            if used[w] or deg[w] != deg[v]:
                continue
            ok = True
            for u in order[:k]:
                if A[v][u] != A[w][img[u]]:
                    ok = False
                    break
            if ok:
                img[v] = w
                used[w] = True
                rec(k + 1)
                used[w] = False
                img[v] = -1
    rec(0)
    return out


def transitive(N, G):
    return len({s[0] for s in G}) == N


def parse_name(nm):
    p = transfer66.parse_any(nm)
    if not p:
        return None
    if not transfer66.too_big(p):
        return None                    # transfer66 builds this one slice by slice
    G = automorphisms(p['N'], p['edges'])
    if not G:
        return None
    if p['start0'] and not transitive(p['N'], G):
        return None                    # the fibres of x(0,0) need not then be equal
    p['aut'] = len(G)
    p['frac'] = p['N'] if p['start0'] else 1
    return p


def build(p, cap=400000):
    N, W, ds = p['N'], p['W'], set(p['dirs'])
    A = [[False] * N for _ in range(N)]
    for a, b in p['edges']:
        A[a][b] = A[b][a] = True
    nbr = [[b for b in range(N) if A[a][b]] for a in range(N)]
    horiz = 'horizontal' in ds
    G = automorphisms(N, p['edges'])
    nG = len(G)

    reps, sizes = [], []
    cur = [0] * W

    def gen(k, tied):
        """Slices that are least in their orbit; `tied` is the set of automorphisms that have
        written the same prefix so far, and at the end it is the stabiliser."""
        if k == W:
            reps.append(tuple(cur))
            sizes.append(nG // len(tied))
            return
        for x in range(N):
            if horiz and k and not A[cur[k - 1]][x]:
                continue
            nt = []
            small = False
            for s in tied:
                y = s[x]
                if y < x:
                    small = True
                    break
                if y == x:
                    nt.append(s)
            if small:
                continue
            cur[k] = x
            gen(k + 1, nt)
            if len(reps) > STATEMAX:
                return
    gen(0, G)
    if len(reps) > STATEMAX or len(reps) > cap:
        return None

    idx = {r: i for i, r in enumerate(reps)}
    memo = {}

    def canon(v):
        c = memo.get(v)
        if c is None:
            c = min(tuple(s[t] for t in v) for s in G)
            memo[v] = c
        return c

    adj = []
    edges = 0
    for u in reps:
        out = []
        cur2 = [0] * W

        def rec(j):
            if j == W:
                out.append(idx[canon(tuple(cur2))])
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
                if horiz and j and not A[cur2[j - 1]][x]:
                    continue
                if 'vertical' in ds and not A[u[j]][x]:
                    continue
                if 'diagonal' in ds and j and not A[u[j - 1]][x]:
                    continue
                if 'antidiagonal' in ds and j + 1 < W and not A[u[j + 1]][x]:
                    continue
                cur2[j] = x
                rec(j + 1)
        rec(0)
        adj.append(out)
        edges += len(out)
        if edges > EMAX:
            return None
    S = len(reps)
    return adj, sizes, [1] * S, S


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
