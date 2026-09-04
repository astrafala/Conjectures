#!/usr/bin/env python3
"""Independent brute force for the chessboard-colour subarray family.

The cells of one colour are enumerated directly -- every assignment of values to them, with no
walk, no rows and no state -- and each is tested by the entry's own words. The colour classes
are worked out here from i+j, not taken from transfer69.
"""
import json, sys
from itertools import product
import localentry as LE, transfer69

DA = ((-1, -1), (1, 1), (-1, 1), (1, -1))


def _ok(g, cs, p):
    """The entry's own words, applied to a finished assignment."""
    if p['ul0'] and g[cs[0]] != 0:
        return False
    if p['rowmajor']:
        m = 0
        for c in cs:                       # cs is already in reading order
            if g[c] > m:
                return False
            if g[c] == m:
                m += 1
    for (i, j) in cs:
        x = g[(i, j)]
        nb = [g[(i + a, j + b)] for a, b in DA if (i + a, j + b) in g]
        if p['kind'] == 'maj':
            if 2 * sum(1 for y in nb if y == x) > len(nb):
                return False
        else:
            if not any(y == (x + 1) % p['mod'] for y in nb) or any(y == x for y in nb):
                return False
    return True


def count(R, C, A, p):
    """Backtracking over the cells of the colour class in reading order. A partial assignment
    is abandoned when two neighbours are already equal (for the second condition) or when a cell
    whose whole neighbourhood is written already fails; whatever reaches the last cell is then
    tested in full by _ok()."""
    cs = [(i, j) for i in range(R) for j in range(C) if (i + j) % 2 == p['par']]
    if not cs:
        return 0
    pos = {c: k for k, c in enumerate(cs)}
    g = {}
    n = 0

    def rec(t):
        nonlocal n
        if t == len(cs):
            n += _ok(g, cs, p)
            return
        i, j = cs[t]
        for x in range(A):
            g[(i, j)] = x
            nb = [(i + a, j + b) for a, b in DA if (i + a, j + b) in pos]
            done = [g[c] for c in nb if pos[c] < t]
            if p['kind'] == 'plus' and x in done:
                continue
            if len(done) == len(nb):                 # this cell is settled
                if p['kind'] == 'maj':
                    if 2 * sum(1 for y in done if y == x) > len(nb):
                        continue
                elif not any(y == (x + 1) % p['mod'] for y in done):
                    continue
            rec(t + 1)
        g.pop((i, j), None)

    rec(0)
    return n


def check(anum, steps=3):
    e = LE.get(anum)
    p = transfer69.parse_name(e['name'])
    if not p:
        return anum, 'PARSE-FAIL', None
    C, A = p['C'], p['alpha'] + 1
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    out = [count(R, C, A, p) for R in range(2, 2 + steps)]
    while len(out) > 1 and out[0] == 0:      # a shape too small to hold any valid assignment
        out = out[1:]                        # cannot appear in the published data
    for k in range(len(out)):
        tail = out[k:]
        for s in range(len(d) - len(tail) + 1):
            if d[s:s + len(tail)] == tail:
                return anum, 'OK', (len(tail), s)
    return anum, 'MISMATCH', (out, d[:6])


if __name__ == '__main__':
    import collections
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer69' and not h.get('FAILS')]
    todo = sys.argv[1:] or [h['anum'] for h in hits]
    c = collections.Counter()
    for a in todo:
        r = check(a)
        c[r[1]] += 1
        if r[1] != 'OK':
            print(*r)
    print(c)
