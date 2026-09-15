#!/usr/bin/env python3
"""Brute force straight from the definition for the consecutive-triple family.

Cells are filled in row-major order and a triple is tested the moment its last cell is
placed; the `new values 0 upwards' clause is imposed the same way, by allowing a cell to
introduce only the next unused value. No transfer matrix and no relabelling inversion is
involved -- this is the definition, with dead branches cut.
"""
import json, sys
import transfer45, localentry as LE

N = json.load(open('/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))
STEPS = (('row', (0, 1)), ('column', (1, 0)), ('diagonal', (1, 1)), ('antidiagonal', (1, -1)))


def count(nm, R, C):
    p = transfer45.parse_name(nm)
    cond = p['cond']
    if p['trans']:
        cond = {('column' if k == 'row' else 'row' if k == 'column' else k): v
                for k, v in cond.items()}
    mm = p['alpha']
    g = [[-1] * C for _ in range(R)]
    tot = 0

    def full(i, j):
        """triples ending at (i,j), all of whose cells are already placed"""
        for key, (di, dj) in STEPS:
            if key not in cond:
                continue
            q = [(i - t * di, j - t * dj) for t in range(3)]
            if not all(0 <= x < R and 0 <= y < C for x, y in q):
                continue
            if len({g[x][y] for x, y in q}) not in cond[key]:
                return False
        return True

    def go(k, used):
        nonlocal tot
        if k == R * C:
            tot += 1
            return
        i, j = divmod(k, C)
        for v in range(min(used + 1, mm + 1)):
            g[i][j] = v
            if full(i, j):
                go(k + 1, used + (1 if v == used else 0))
            g[i][j] = -1
    go(0, 0)
    return tot


for a in sys.argv[1:]:
    nm = N[a]
    p = transfer45.parse_name(nm)
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    got = []
    for k in range(5):
        nn = off + k
        R = nn + 2 if not p['trans'] else p['W']
        C = p['W'] if not p['trans'] else nn + 2
        if R * C > 30:
            break
        got.append(count(nm, R, C))
    print(a, 'brute', got, 'data', d[:len(got)], 'MATCH' if got == d[:len(got)] else 'DIFFER')
