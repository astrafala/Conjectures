#!/usr/bin/env python3
"""Brute force from the definition for the self-counting neighbour family."""
import json, re, sys
from itertools import product
import localentry as LE, transfer50

N = json.load(open('/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))
CLASS = transfer50.CLASS


def raw(nm):
    s = re.sub(r'(?<=[\dn])\s*[xX]\s*(?=[\dn])', ' X ',
               re.sub(r'\s+', ' ', transfer50.namecanon.canon(nm))).strip()
    m = transfer50.NAME.search(s)
    W = int(m.group(1) or m.group(2))
    trans = m.group(1) is None
    D = []
    for w in dict.fromkeys(re.findall(r'antidiagonal|diagonal|horizontal|vertical',
                                      m.group(4).lower())):
        D += CLASS[w]
    return W, trans, sorted(set(D))


def count(p, D, R, C):
    A = p['alpha'] + 1
    f = transfer50.TEST[p['pred']]
    k = p['k']
    tot = 0
    for flat in product(range(A), repeat=R * C):
        g = [flat[i * C:(i + 1) * C] for i in range(R)]
        ok = True
        for i in range(R):
            for j in range(C):
                v = g[i][j]
                c = 0
                for di, dj in D:
                    a, b = i + di, j + dj
                    if 0 <= a < R and 0 <= b < C and f(g[a][b], v, k):
                        c += 1
                if c != v:
                    ok = False
                    break
            if not ok:
                break
        tot += ok
    return tot


for a in sys.argv[1:]:
    p = transfer50.parse_name(N[a])
    W, trans, D = raw(N[a])
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    got = []
    for t in range(4):
        nn = off + t
        R, C = (nn, W) if not trans else (W, nn)
        if R * C == 0:
            got.append(1)
            continue
        if (p['alpha'] + 1) ** (R * C) > 2 * 10 ** 7:
            break
        got.append(count(p, D, R, C))
    print(a, 'brute', got, 'data', d[:len(got)], 'MATCH' if got == d[:len(got)] else 'DIFFER')
