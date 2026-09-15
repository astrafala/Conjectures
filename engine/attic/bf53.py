#!/usr/bin/env python3
"""Brute force from the definition for the modular-neighbour family."""
import json, re, sys
from itertools import product
import localentry as LE, transfer53

N = json.load(open('/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))


def raw(nm):
    s = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ',
               re.sub(r'\s+', ' ', transfer53.namecanon.canon(nm))).strip()
    m = transfer53.NAME.search(s)
    ra = m.group(1) or m.group(3)
    rb = int(m.group(2) or 0)
    ca = m.group(4) or m.group(6)
    cb = int(m.group(5) or 0)
    D = []
    for w in dict.fromkeys(re.findall(transfer53._W1, m.group(8).lower())):
        D += transfer53.CLASS[w]
    return (ra, rb, ca, cb), sorted(set(D))


def count(R, C, A, M, D, up, dn, noeq):
    tot = 0
    for flat in product(range(A), repeat=R * C):
        if flat[0] != 0:
            continue
        g = [flat[i * C:(i + 1) * C] for i in range(R)]
        ok = True
        for i in range(R):
            for j in range(C):
                v = g[i][j]
                cu = cd = 0
                for di, dj in D:
                    a, b = i + di, j + dj
                    if not (0 <= a < R and 0 <= b < C):
                        continue
                    y = g[a][b]
                    if noeq and y == v:
                        ok = False
                        break
                    if (y - v) % M == 1:
                        cu += 1
                    if (v - y) % M == 1:
                        cd += 1
                if not ok or cu < up or (dn is not None and cd < dn):
                    ok = False
                    break
            if not ok:
                break
        tot += ok
    return tot


for a in sys.argv[1:]:
    p = transfer53.parse_name(N[a])
    (ra, rb, ca, cb), D = raw(N[a])
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    got = []
    for t in range(4):
        nn = off + t
        R = nn + rb if ra == 'n' else int(ra) + rb
        C = nn + cb if ca == 'n' else int(ca) + cb
        if (p['alpha'] + 1) ** (R * C) > 3 * 10 ** 7:
            break
        got.append(count(R, C, p['alpha'] + 1, p['mod'], D, p['up'], p['dn'], p['noeq']))
    print(a, 'brute', got, 'data', d[:len(got)], 'MATCH' if got == d[:len(got)] else 'DIFFER')
