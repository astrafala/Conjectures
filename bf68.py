#!/usr/bin/env python3
"""Independent brute force for the neighbourhood-condition family.

Every array of the entry's own width with a few rows is written out cell by cell and each cell
tested against its neighbours directly. No window, no state, no end vector, no recurrence.
"""
import json, sys
from fractions import Fraction
from itertools import product
import localentry as LE, transfer68


def ok(g, R, C, p):
    kind = p['kind']
    for i in range(R):
        for j in range(C):
            x = g[i][j]
            v = [g[i + a][j + b] for a, b in p['offs']
                 if 0 <= i + a < R and 0 <= j + b < C]
            if kind == 'avg':
                if v and Fraction(sum(v), len(v)) == x:
                    return False
            elif kind == 'avgself':
                if Fraction(sum(v) + x, len(v) + 1) == p['val']:
                    return False
            elif kind == 'maj':
                if 2 * sum(1 for y in v if y == x) > len(v):
                    return False
            elif kind == 'majplus':
                t = (x + 1) % p['mod']
                if 2 * sum(1 for y in v if y == t) > len(v):
                    return False
            elif kind == 'both':
                if i and j and x == g[i - 1][j] and x == g[i][j - 1]:
                    return False
            else:
                v2 = [g[i + a][j + b] for a, b in p['offs2']
                      if 0 <= i + a < R and 0 <= j + b < C]
                if x != sum(v) % p['mod'] and x != sum(v2) % p['mod']:
                    return False
    if p['ul0'] and g[0][0] != 0:
        return False
    return True


def _settled(R, C, p, i, j):
    """Whether cell (i,j)'s own condition can already be decided in reading order."""
    offs = list(p['offs']) + list(p['offs2'] or [])
    for a, b in offs:
        y, x = i + a, j + b
        if 0 <= y < R and 0 <= x < C and y * C + x > i * C + j:
            return False
    return True


def count(R, C, A, p):
    """Backtracking in reading order. A partial fill is abandoned when a cell whose whole
    neighbourhood is already written fails its own condition; anything reaching the last cell
    is then tested in full by ok(), so the acceptance test is the entry's own words."""
    g = [[0] * C for _ in range(R)]
    tot, n = R * C, 0
    early = [[_settled(R, C, p, i, j) for j in range(C)] for i in range(R)]

    def one(i, j):
        x = g[i][j]
        v = [g[i + a][j + b] for a, b in p['offs'] if 0 <= i + a < R and 0 <= j + b < C]
        k = p['kind']
        if k == 'avg':
            return not v or Fraction(sum(v), len(v)) != x
        if k == 'avgself':
            return Fraction(sum(v) + x, len(v) + 1) != p['val']
        if k == 'maj':
            return 2 * sum(1 for y in v if y == x) <= len(v)
        if k == 'majplus':
            t = (x + 1) % p['mod']
            return 2 * sum(1 for y in v if y == t) <= len(v)
        if k == 'both':
            return not (i and j and x == g[i - 1][j] and x == g[i][j - 1])
        v2 = [g[i + a][j + b] for a, b in p['offs2'] if 0 <= i + a < R and 0 <= j + b < C]
        return x == sum(v) % p['mod'] or x == sum(v2) % p['mod']

    def rec(t):
        nonlocal n
        if t == tot:
            n += ok(g, R, C, p)
            return
        i, j = divmod(t, C)
        for x in range(A):
            if p['ul0'] and t == 0 and x != 0:
                continue
            g[i][j] = x
            if early[i][j] and not one(i, j):
                continue
            rec(t + 1)

    rec(0)
    return n


def check(anum, steps=3):
    e = LE.get(anum)
    p = transfer68.parse_name(e['name'])
    if not p:
        return anum, 'PARSE-FAIL', None
    W, A = p['W'], p['alpha'] + 1
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    q = dict(p)
    if p['trans']:            # count in the entry's own orientation
        q['offs'] = [(b, a) for a, b in p['offs']]
        if p['offs2']:
            q['offs2'] = [(b, a) for a, b in p['offs2']]
    out = []
    for k in range(1, steps + 1):
        R, C = (W, k) if p['trans'] else (k, W)
        out.append(count(R, C, A, q) // p['frac'])
    # the model's own first index need not be the entry's: match any suffix of the recount
    # (of length at least two) against a window of the published data
    for k in range(len(out) - 1):
        tail = out[k:]
        for s in range(len(d) - len(tail) + 1):
            if d[s:s + len(tail)] == tail:
                return anum, 'OK', (len(tail), s)
    return anum, 'MISMATCH', (out, d[:6])


if __name__ == '__main__':
    import collections
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer68' and not h.get('FAILS')]
    todo = sys.argv[1:] or [h['anum'] for h in hits]
    c = collections.Counter()
    for a in todo:
        r = check(a)
        c[r[1]] += 1
        if r[1] != 'OK':
            print(*r)
    print(c)
