#!/usr/bin/env python3
"""Brute force from the definition for the containing-all-values subblock family."""
import json, sys
from itertools import product
import localentry as LE, transfer49

N = json.load(open('/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))


def count(p, R, C):
    A = p['alpha'] + 1
    blk, ok = p['blk'], set(p['ok'])
    tot = 0
    for flat in product(range(A), repeat=R * C):
        seen = []
        good = True
        for v in flat:                       # new values introduced in row major order
            if v not in seen:
                if v != len(seen):
                    good = False
                    break
                seen.append(v)
        if not good or len(seen) != A:       # containing all values 0..m
            continue
        g = [flat[i * C:(i + 1) * C] for i in range(R)]
        for i in range(R - blk + 1):
            for j in range(C - blk + 1):
                if len({g[i + s][j + t] for s in range(blk) for t in range(blk)}) not in ok:
                    good = False
                    break
            if not good:
                break
        tot += good
    return tot


for a in sys.argv[1:]:
    p = transfer49.parse_name(N[a])
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    got = []
    for t in range(4):
        nn = off + t
        R, C = (nn + 1, p['W']) if not p['trans'] else (p['W'], nn + 1)
        if (p['alpha'] + 1) ** (R * C) > 2 * 10 ** 7:
            break
        got.append(count(p, R, C))
    print(a, 'brute', got, 'data', d[:len(got)], 'MATCH' if got == d[:len(got)] else 'DIFFER')
