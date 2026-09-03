#!/usr/bin/env python3
"""Brute force from the definition for the distance-inequality family."""
import json, re, sys
from itertools import product
import localentry as LE, transfer62

N = json.load(open('/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))


def raw(nm):
    """the shape and the offsets as the name states them, with no transposing"""
    s = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ',
               re.sub(r'\s+', ' ', transfer62.namecanon.canon(nm))).strip()
    m = transfer62.NAME.search(s)
    offs = []
    if m.group('lin') is not None:
        k = transfer62._n(m.group('lin'))
        for t in range(1, k + 1):
            offs += [(0, t), (0, -t), (t, 0), (-t, 0)]
    else:
        exact = m.group('ex') is not None
        k = transfer62._n(m.group('ex') if exact else m.group('cb'))
        for di in range(-k, k + 1):
            for dj in range(-k, k + 1):
                if (di, dj) == (0, 0):
                    continue
                t = abs(di) + abs(dj)
                if (t == k) if exact else (t <= k):
                    offs.append((di, dj))
    return ((m.group(1) or m.group(3), int(m.group(2) or 0),
             m.group(4) or m.group(6), int(m.group(5) or 0)), offs, int(m.group('al')))


def count(R, C, A, offs):
    tot = 0
    for flat in product(range(A), repeat=R * C):
        seen = []
        ok = True
        for v in flat:
            if v not in seen:
                if v != len(seen):
                    ok = False
                    break
                seen.append(v)
        if not ok:
            continue
        g = [flat[i * C:(i + 1) * C] for i in range(R)]
        for i in range(R):
            for j in range(C):
                for di, dj in offs:
                    a, b = i + di, j + dj
                    if 0 <= a < R and 0 <= b < C and g[a][b] == g[i][j]:
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                break
        tot += ok
    return tot


for a in sys.argv[1:]:
    (ra, rb, ca, cb), offs, alpha = raw(N[a])
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    got = []
    for t in range(4):
        nn = off + t
        R = nn + rb if ra == 'n' else int(ra) + rb
        C = nn + cb if ca == 'n' else int(ca) + cb
        if (alpha + 1) ** (R * C) > 3 * 10 ** 7:
            break
        got.append(count(R, C, alpha + 1, offs))
    print(a, 'brute', got, 'data', d[:len(got)], 'MATCH' if got == d[:len(got)] else 'DIFFER')
