#!/usr/bin/env python3
"""Brute force from the definition for the running-sum family.

The array is filled cell by cell in row major order in the orientation the NAME writes, and
each cell is tested against the four rays by summing the cells along them directly. No residue
state and no slice-wise recurrence.
"""
import json, re, sys
import localentry as LE, transfer52

N = json.load(open('/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))
STEP = {'west': (0, -1), 'north': (-1, 0), 'nw': (-1, -1), 'ne': (-1, 1)}


def raw(nm):
    s = re.sub(r'(?<=[\dn])\s*[xX]\s*(?=[\dn])', ' X ',
               re.sub(r'\s+', ' ', transfer52.namecanon.canon(nm))).strip()
    m = transfer52.NAME.search(s)
    W = int(m.group(1) or m.group(2))
    trans = m.group(1) is None
    alpha, mod = int(m.group(3)), int(m.group(5))
    con = {}
    for g in transfer52.CLAUSE.finditer(m.group(4)):
        w = g.group(1).lower()
        con[transfer52.KEY[g.group(2).lower()]] = (int(w) if w.isdigit()
                                                   else transfer52.NUM[w]) % mod
    return W, trans, alpha, mod, con


def count(R, C, A, M, con):
    g = [[0] * C for _ in range(R)]
    tot = 0

    def ok(i, j, v):
        for k, c in con.items():
            di, dj = STEP[k]
            s, a, b = 0, i + di, j + dj
            while 0 <= a < R and 0 <= b < C:
                s += g[a][b]
                a += di
                b += dj
            if v % M == (c + s) % M:
                return False
        return True

    def go(t):
        nonlocal tot
        if t == R * C:
            tot += 1
            return
        i, j = divmod(t, C)
        for v in range(A):
            if ok(i, j, v):
                g[i][j] = v
                go(t + 1)
                g[i][j] = 0
    go(0)
    return tot


for a in sys.argv[1:]:
    W, trans, alpha, M, con = raw(N[a])
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    got = []
    for t in range(4):
        nn = off + t
        R, C = (nn, W) if not trans else (W, nn)
        if (alpha + 1) ** (R * C) > 3 * 10 ** 7:
            break
        got.append(count(R, C, alpha + 1, M, con))
    print(a, 'brute', got, 'data', d[:len(got)], 'MATCH' if got == d[:len(got)] else 'DIFFER')
