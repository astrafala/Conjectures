#!/usr/bin/env python3
"""Independent brute force for the lexicographic 2 X 2 statistic family.

Every array of the entry's own width with a few rows is written out cell by cell, the derived
array is formed by applying the named statistic to each 2 X 2 subblock, and its rows and
columns are compared as whole words. Nothing here uses transfer65's state: no equality bits,
no walk, no recurrence.
"""
import json, sys
from itertools import product
import localentry as LE, transfer65


def _f(name):
    return transfer65._stat(name)


def ok(g, R, C, p):
    f = _f(p['stat'])
    D = [[f(g[i][j], g[i][j + 1], g[i + 1][j], g[i + 1][j + 1]) for j in range(C - 1)]
         for i in range(R - 1)]
    if not D or not D[0]:
        return True
    if p['nonzero'] and any(v == 0 for row in D for v in row):
        return False
    for a, b in zip(D, D[1:]):
        if (a > b) if p['rowdir'] else (a < b):
            return False
    cols = [list(c) for c in zip(*D)]
    for a, b in zip(cols, cols[1:]):
        if (a > b) if p['coldir'] else (a < b):
            return False
    return True


def count(R, C, A, p):
    n = 0
    for a in product(range(A), repeat=R * C):
        g = [list(a[i * C:(i + 1) * C]) for i in range(R)]
        n += ok(g, R, C, p)
    return n


def check(anum, rows=3):
    e = LE.get(anum)
    p = transfer65.parse_name(e['name'])
    W, A = p['W'], p['alpha'] + 1
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    out = []
    for R in range(2, rows + 1):
        out.append(count(R, W, A, p) // p['frac'])
    for s in range(len(d) - len(out) + 1):
        if d[s:s + len(out)] == out:
            return anum, 'OK', (len(out), s)
    return anum, 'MISMATCH', (out, d[:6])


if __name__ == '__main__':
    import collections
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer65' and not h.get('FAILS')]
    todo = sys.argv[1:] or [h['anum'] for h in hits]
    c = collections.Counter()
    for a in todo:
        r = check(a)
        c[r[1]] += 1
        if r[1] != 'OK':
            print(*r)
    print(c)
