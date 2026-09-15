#!/usr/bin/env python3
"""Brute force from the definition for the capped-pair-count family."""
import json, re, sys
from itertools import product
import localentry as LE, transfer60

N = json.load(open('/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))
CLASS = {'horizontally': (0, 1), 'vertically': (1, 0), 'diagonally': (1, 1),
         'antidiagonally': (1, -1)}


def raw(nm):
    s = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ',
               re.sub(r'\s+', ' ', transfer60.namecanon.canon(nm))).strip()
    m = transfer60.NAME.search(s)
    words = [w.lower() for w in dict.fromkeys(re.findall(transfer60._W1, m.group(9).lower()))]
    return ((m.group(1) or m.group(3), int(m.group(2) or 0),
             m.group(4) or m.group(6), int(m.group(5) or 0)), [CLASS[w] for w in words])


def count(p, steps, R, C):
    A = p['alpha'] + 1
    T = p['total']
    tot = 0
    for flat in product(range(A), repeat=R * C):
        g = [flat[i * C:(i + 1) * C] for i in range(R)]
        c = 0
        for di, dj in steps:                 # each unordered pair once, taken in one sense
            for i in range(R):
                for j in range(C):
                    a, b = i + di, j + dj
                    if 0 <= a < R and 0 <= b < C and g[i][j] + g[a][b] == T:
                        c += 1
        if (c == 1) if p['exact'] else (c <= 1):
            tot += 1
    return tot


for a in sys.argv[1:]:
    p = transfer60.parse_name(N[a])
    (ra, rb, ca, cb), steps = raw(N[a])
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    got = []
    for t in range(3):
        nn = off + t
        R = nn + rb if ra == 'n' else int(ra) + rb
        C = nn + cb if ca == 'n' else int(ca) + cb
        if (p['alpha'] + 1) ** (R * C) > 2 * 10 ** 7:
            break
        got.append(count(p, steps, R, C))
    print(a, 'brute', got, 'data', d[:len(got)], 'MATCH' if got == d[:len(got)] else 'DIFFER')
