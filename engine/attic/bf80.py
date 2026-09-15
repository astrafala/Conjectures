#!/usr/bin/env python3
"""Brute force for the bounded-difference lower triangles: enumerate the arrays themselves.

Every assignment of 0..n to the cells is written out and every neighbour pair tested in turn.
No frontier walk, no patterns, no spreads -- so a wrong cell set, a wrong direction word or a
wrong comparison shows here and nowhere else."""
import json, sys
from itertools import product

import transfer80, localentry as LE


def count(p, n):
    K, d, kind = p['K'], p['d'], p['kind']
    C = transfer80.cells(K)
    idx = {c: i for i, c in enumerate(C)}
    E = transfer80.edges(K, [tuple(t) for t in p['dirs']])
    tot = 0
    for x in product(range(n + 1), repeat=len(C)):
        ok = True
        for u, v in E:
            t = abs(x[idx[u]] - x[idx[v]])
            if (t > d) if kind == 'atmost' else (t != d):
                ok = False
                break
        if ok:
            tot += 1
    return tot


def small_alphabet(p):
    """The first term, argued rather than enumerated, for the shapes too big to walk through.

    At n = 1 every entry is 0 or 1, so every difference is 0 or 1. For an "at most d" condition
    with d >= 1 that is no condition at all and the count is 2^T. For "differing by exactly 1"
    it says adjacent cells differ, i.e. the array is a proper 2-colouring of the neighbour
    graph, of which there are 2^(components) when the graph is bipartite and none otherwise.
    Both test the cell set and the neighbour graph, which is what the brute force is for."""
    import collections
    C = transfer80.cells(p['K'])
    E = transfer80.edges(p['K'], [tuple(t) for t in p['dirs']])
    T = len(C)
    if p['kind'] == 'atmost':
        return 2 ** T if p['d'] >= 1 else None
    if p['d'] != 1:
        return None
    adj = collections.defaultdict(list)
    for u, v in E:
        adj[u].append(v)
        adj[v].append(u)
    colour, comps = {}, 0
    for s in C:
        if s in colour:
            continue
        comps += 1
        colour[s] = 0
        q = [s]
        while q:
            u = q.pop()
            for v in adj[u]:
                if v not in colour:
                    colour[v] = 1 - colour[u]
                    q.append(v)
                elif colour[v] == colour[u]:
                    return 0
    return 2 ** comps


if __name__ == '__main__':
    BUDGET = int(sys.argv[1]) if len(sys.argv) > 1 else 3 * 10 ** 6
    for h in json.load(open('transfer80_hits.json')):
        if h.get('FAILS'):
            continue
        a = h['anum']
        p = transfer80.parse_name(h['name'])
        T = len(transfer80.cells(p['K']))
        e = LE.get(a)
        d = [int(x) for x in e['data'].split(',') if x.strip()]
        off = h['offset']
        got, want = [], []
        for k in range(4):
            n = off + k
            if (n + 1) ** T > BUDGET or k >= len(d):
                break
            got.append(count(p, n))
            want.append(d[k])
        if got:
            print(a, f"K={p['K']} d={p['d']} {p['kind']}", 'brute', got, 'entry', want,
                  'OK' if got == want else 'MISMATCH', flush=True)
        else:
            v = small_alphabet(p)
            print(a, f"K={p['K']} d={p['d']} {p['kind']}", 'argued a(1) =', v,
                  'entry', d[0],
                  'OK' if v == d[0] else 'MISMATCH', flush=True)
