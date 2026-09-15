#!/usr/bin/env python3
"""Brute force for the triangular family: enumerate the arrays themselves.

No inclusion--exclusion and no closed form -- every assignment of 0..n to the cells of the
triangle is written out and its satisfied adjacent pairs counted, so a wrong reading of the
cell set, of the adjacency, or of the target would show here."""
import json, sys
from itertools import product

import transfer78, localentry as LE


def count(K, n, shift):
    V = transfer78.cells(K)
    E = transfer78.edges(K)
    idx = {c: i for i, c in enumerate(V)}
    t = n + shift
    tot = 0
    for x in product(range(n + 1), repeat=len(V)):
        k = 0
        for u, v in E:
            if x[idx[u]] + x[idx[v]] == t:
                k += 1
                if k > 1:
                    break
        if k == 1:
            tot += 1
    return tot


if __name__ == '__main__':
    BUDGET = int(sys.argv[1]) if len(sys.argv) > 1 else 4 * 10 ** 6
    for h in json.load(open('transfer78_hits.json')):
        if h.get('FAILS'):
            continue
        a, K, shift = h['anum'], h['K'], h['shift']
        e = LE.get(a)
        d = [int(v) for v in e['data'].split(',') if v.strip()]
        off = h['offset']
        got, want = [], []
        for k in range(6):
            n = off + k
            if (n + 1) ** h['T'] > BUDGET or k >= len(d):
                break
            got.append(count(K, n, shift))
            want.append(d[k])
        print(a, 'K', K, 'shift', shift, 'brute', got, 'entry', want,
              'OK' if got and got == want else ('MISMATCH' if got else 'too big'), flush=True)
