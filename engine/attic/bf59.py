#!/usr/bin/env python3
"""Brute force from the definition for the `every V next to a W' family."""
import json, re, sys
from itertools import product
import localentry as LE, transfer59

N = json.load(open('/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))


def raw(nm):
    s = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ',
               re.sub(r'\s+', ' ', transfer59.namecanon.canon(nm))).strip()
    m = transfer59.NAME.search(s)
    D = []
    for w in dict.fromkeys(re.findall(transfer59._W1, m.group(9).lower())):
        D += transfer59.CLASS[w]
    return ((m.group(1) or m.group(3), int(m.group(2) or 0),
             m.group(4) or m.group(6), int(m.group(5) or 0)), sorted(set(D)))


def count(p, D, R, C):
    A = p['alpha'] + 1
    want = {}
    for v, w in p['pairs']:
        want.setdefault(v, set()).add(w)
    tot = 0
    for flat in product(range(A), repeat=R * C):
        g = [flat[i * C:(i + 1) * C] for i in range(R)]
        ok = True
        for i in range(R):
            for j in range(C):
                v = g[i][j]
                seen = set()
                for di, dj in D:
                    a, b = i + di, j + dj
                    if not (0 <= a < R and 0 <= b < C):
                        continue
                    if p['noeq'] and g[a][b] == v:
                        ok = False
                        break
                    seen.add(g[a][b])
                if not ok or (v in want and not (want[v] & seen)):
                    ok = False
                    break
            if not ok:
                break
        tot += ok
    return tot


for a in sys.argv[1:]:
    p = transfer59.parse_name(N[a])
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
        got.append(count(p, D, R, C))
    print(a, 'brute', got, 'data', d[:len(got)], 'MATCH' if got == d[:len(got)] else 'DIFFER')
