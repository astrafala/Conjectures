#!/usr/bin/env python3
"""Transfer matrix for the Hardin RECIPROCAL LINK families.

Name shape:
    Number of ways to reciprocally link elements of an n X W array either to themselves or
    to exactly <one|two> <neighbour words> neighbors[, without <3-loops|consecutive
    collinear links>]

and the same with the array written W X n.

Because a link is reciprocal it is an undirected edge, and "linked to itself" is the same as
"in no edge at all". So what is counted is the spanning subgraphs of the grid graph on the
stated neighbour set in which every vertex has degree $0$ or $d$, with $d=1$ (a matching) or
$d=2$ (a disjoint union of cycles). Two entries fix the reading of the two ambiguous cases:
the $1\\times2$ and $2\\times2$ king-move counts $1$ and $8$ are the degree-$0$-or-$2$
subgraphs of $K_2$ and $K_4$ with SIMPLE edges, so a vertex's two links go to two DIFFERENT
neighbours and a doubled edge is not a configuration.

The state is the set of edges crossing the boundary between two consecutive rows. Every
neighbour set here lies within one row of the boundary, so a step consumes the incoming
crossing edges, chooses the horizontal edges of the new row and the edges it sends downward,
and settles the degree of every one of its cells at once. `without consecutive collinear
links' forbids a vertex whose two links are opposite, which is decided at the same moment.
`without 3-loops' forbids a triangle; a triangle in any of these neighbour sets has all its
vertices in two consecutive rows, so it is enough to carry the previous row's horizontal
edges alongside the crossing edges.
"""
import re
from itertools import product

import namecanon

CLASS = {'horizontal': [(0, -1), (0, 1)],
         'vertical': [(-1, 0), (1, 0)],
         'diagonal': [(-1, -1), (1, 1)],
         'antidiagonal': [(-1, 1), (1, -1)],
         'king-move': [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if (a, b) != (0, 0)]}

NAME = re.compile(
    r'Number of ways to reciprocally link elements of an?\s+'
    r'(?:n\s*X\s*(\d+)|(\d+)\s*X\s*n)\s+array\s+either to themselves or to exactly\s+'
    r'(one|two)\s+(.*?)\s+neighbors?'
    r'(?:,\s*without\s+(3-loops|consecutive collinear links))?\s*\.?\s*$', re.I)


def parse_name(nm):
    nm = namecanon.canon(nm)
    norm = re.sub(r'(?<=[\dn)])\s*[xX]\s*(?=[\dn(])', ' X ', nm)
    norm = re.sub(r'\s+', ' ', norm).strip()
    m = NAME.search(norm)
    if not m:
        return None
    W = int(m.group(1) or m.group(2))
    walk = 'rows' if m.group(1) else 'cols'
    deg = 1 if m.group(3).lower() == 'one' else 2
    body = m.group(4).lower()
    # 'antidiagonal' contains 'diagonal', so the longer word must come first
    words = re.findall(r'antidiagonal|king-move|horizontal|vertical|diagonal', body)
    left = re.sub(r'antidiagonal|king-move|horizontal|vertical|diagonal', ' ', body)
    left = re.sub(r'\b(and|or)\b|,|\s+', '', left)
    if not words or left:
        return None
    D = set()
    for w in words:
        D.update(CLASS[w])
    if walk == 'cols':
        D = {(b, a) for a, b in D}
    flag = (m.group(5) or '').lower()
    if W < 2:
        return None
    return {'W': W, 'dirs': sorted(D), 'deg': deg,
            'noloop3': flag == '3-loops', 'nocoll': flag.startswith('consecutive'),
            'frac': 1}


def build(p, cap=40000):
    W, deg = p['W'], p['deg']
    D = set(map(tuple, p['dirs']))
    noloop3, nocoll = p['noloop3'], p['nocoll']
    down = [t for t in (-1, 0, 1) if (1, t) in D]
    horiz = (0, 1) in D
    E = [(j, t) for j in range(W) for t in down if 0 <= j + t < W]
    EI = {e: i for i, e in enumerate(E)}
    NH = W - 1 if horiz else 0
    zeroE = (0,) * len(E)
    zeroH = (0,) * NH
    states, index, adj = [], {}, []

    def sid(s):
        i = index.get(s)
        if i is None:
            i = index[s] = len(states)
            states.append(s)
            adj.append([])
        return i

    def triangle(P, Hprev, Hcur):
        """a triangle whose vertices lie in the two rows the crossing set P joins"""
        for j in range(NH):
            if Hprev[j]:                       # (i-1,j)-(i-1,j+1) present
                for k in range(W):
                    if (1, k - j) in D and (1, k - j - 1) in D:
                        if P[EI[(j, k - j)]] and P[EI[(j + 1, k - j - 1)]]:
                            return True
            if Hcur[j]:                        # (i,j)-(i,j+1) present
                for l in range(W):
                    if (1, j - l) in D and (1, j + 1 - l) in D:
                        if P[EI[(l, j - l)]] and P[EI[(l, j + 1 - l)]]:
                            return True
        return False

    sid((zeroE, zeroH) if noloop3 else zeroE)
    qi = 0
    while qi < len(states):
        cur = states[qi]
        P, Hprev = cur if noloop3 else (cur, zeroH)
        qi += 1
        up = [[] for _ in range(W)]
        for (j, t), mult in zip(E, P):
            if mult:
                up[j + t].append((-1, -t))
        outs = [[t for t in down if 0 <= j + t < W] for j in range(W)]
        found = []

        def rec(j, hprev, Q, H, tdeg):
            if j == W:
                found.append((tuple(Q), tuple(H)))
                return
            for hs in ((0, 1) if (horiz and j < W - 1) else (0,)):
                for qs in product((0, 1), repeat=len(outs[j])):
                    if hprev + hs + sum(qs) + len(up[j]) not in (0, deg):
                        continue
                    td = list(tdeg)
                    ok = True
                    for t, mult in zip(outs[j], qs):
                        if mult:
                            td[j + t] += 1
                            if td[j + t] > deg:
                                ok = False
                    if not ok:
                        continue
                    if nocoll:
                        links = list(up[j])
                        if hprev:
                            links.append((0, -1))
                        if hs:
                            links.append((0, 1))
                        links += [(1, t) for t, mult in zip(outs[j], qs) if mult]
                        if any((-a, -b) in links for a, b in links):
                            continue
                    Q2 = list(Q)
                    for t, mult in zip(outs[j], qs):
                        Q2[EI[(j, t)]] = mult
                    H2 = list(H)
                    if j < NH:
                        H2[j] = hs
                    rec(j + 1, hs, Q2, H2, td)

        rec(0, 0, [0] * len(E), [0] * NH, [0] * W)
        for Q, H in found:
            if noloop3 and triangle(P, Hprev, H):
                continue
            adj[index[cur]].append(sid((Q, H) if noloop3 else Q))
            if len(states) > cap:
                return None
    S = len(states)
    start = [0] * S
    start[0] = 1
    end = [1 if (s[0] if noloop3 else s) == zeroE else 0 for s in states]
    return adj, start, end, S


def terms(adj, start, end, N):
    v = end[:]
    out = []
    for _ in range(N + 1):
        out.append(sum(start[i] * v[i] for i in range(len(v))))
        v = [sum(v[k] for k in row) for row in adj]
    return out
