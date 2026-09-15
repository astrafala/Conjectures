#!/usr/bin/env python3
"""Brute force from the definition for the pair-sums family."""
import json, re, sys
from itertools import product
import localentry as LE, transfer61

N = json.load(open('/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))


def count(p, R, C):
    A = p['alpha'] + 1
    kind, up = p['kind'], p['up']
    tot = 0
    for flat in product(range(A), repeat=R * C):
        g = [flat[i * C:(i + 1) * C] for i in range(R)]
        b = {(i, j): g[i][j] + g[i][j - 1] for i in range(R) for j in range(1, C)}
        c = {(i, j): g[i][j] + g[i - 1][j] for i in range(1, R) for j in range(C)}
        ok = True
        if kind == 'mono':
            for (i, j) in b:
                if (i + 1, j) in b and b[(i, j)] > b[(i + 1, j)]:
                    ok = False
            for (i, j) in c:
                if (i, j + 1) in c and c[(i, j)] > c[(i, j + 1)]:
                    ok = False
        elif kind == 'det':
            for i in range(1, R):
                for j in range(1, C):
                    if b[(i, j)] * b[(i - 1, j)] - c[(i, j)] * c[(i, j - 1)] == 0:
                        ok = False
        else:
            brows = [[b[(i, j)] for j in range(1, C)] for i in range(R)]
            ccols = [[c[(i, j)] for i in range(1, R)] for j in range(C)]
            for t in range(R - 1):
                if (brows[t] > brows[t + 1]) if up else (brows[t] < brows[t + 1]):
                    ok = False
            for t in range(C - 1):
                if (ccols[t] > ccols[t + 1]) if up else (ccols[t] < ccols[t + 1]):
                    ok = False
        tot += ok
    return tot


for a in sys.argv[1:]:
    p = transfer61.parse_name(N[a])
    s = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ',
               re.sub(r'\s+', ' ', transfer61.namecanon.canon(N[a]))).strip()
    m = transfer61.NAME.search(s)
    rb = int(m.group(2) or 0)
    ca = m.group(4) or m.group(6)
    cb = int(m.group(5) or 0)
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    got = []
    for t in range(4):
        nn = off + t
        R = nn + rb
        C = int(ca) + cb
        if (p['alpha'] + 1) ** (R * C) > 3 * 10 ** 7:
            break
        got.append(count(p, R, C))
    print(a, 'brute', got, 'data', d[:len(got)], 'MATCH' if got == d[:len(got)] else 'DIFFER')
