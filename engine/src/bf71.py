#!/usr/bin/env python3
"""Independent brute force for the existential-neighbour family.

Arrays are written out cell by cell over the entry's own range and every cell is tested against
the neighbours it has, straight from the entry's words. No window, no state, no end vector.
"""
import json, sys
from itertools import product
import localentry as LE, transfer71


def ok(g, R, C, p):
    A = p['alpha'] + 1
    kind = p['kind']
    for i in range(R):
        for j in range(C):
            x = g[i][j]
            v = [g[i + a][j + b] for a, b in p['offs']
                 if 0 <= i + a < R and 0 <= j + b < C]
            if kind == 'lesome':
                if x != 0 and not any(y >= x for y in v):
                    return False
            elif kind == 'gele':
                if not (any(y >= x for y in v) and any(y <= x for y in v)):
                    return False
            elif kind == 'both2':
                if p['v'] not in v or p['w'] not in v:
                    return False
            elif kind == 'some':
                if x == p['v'] and p['w'] not in v:
                    return False
            elif kind == 'count':
                if x == p['v'] and sum(1 for y in v if y == p['w']) not in p['counts']:
                    return False
            elif kind == 'eqone':
                if x not in v:
                    return False
            else:
                for t in (x - 1, x + 1):
                    if 0 <= t < A and t not in v:
                        return False
                if p['noeq'] and any(y == x for y in v):
                    return False
    if p['before']:
        a, b = p['before']
        for i in range(R):
            for j in range(C):
                if g[i][j] == b:
                    return False
                if g[i][j] == a:
                    return True
    return True


def count(R, C, A, p):
    n = 0
    for a in product(range(A), repeat=R * C):
        g = [a[i * C:(i + 1) * C] for i in range(R)]
        n += ok(g, R, C, p)
    return n


def check(anum, steps=3):
    e = LE.get(anum)
    p = transfer71.parse_name(e['name'])
    if not p:
        return anum, 'PARSE-FAIL', None
    W, A = p['W'], p['alpha'] + 1
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    q = dict(p)
    if p['trans']:
        q['offs'] = [(b, a) for a, b in p['offs']]
    out = []
    for k in range(1, steps + 1):
        R, C = (W, k) if p['trans'] else (k, W)
        out.append(count(R, C, A, q) // p['frac'])
    while len(out) > 1 and out[0] == 0 and out[0] not in d[:1]:
        out = out[1:]
    for k in range(len(out)):
        tail = out[k:]
        for s in range(len(d) - len(tail) + 1):
            if d[s:s + len(tail)] == tail:
                return anum, 'OK', (len(tail), s)
    return anum, 'MISMATCH', (out, d[:6])


if __name__ == '__main__':
    import collections
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer71' and not h.get('FAILS')]
    todo = sys.argv[1:] or [h['anum'] for h in hits]
    c = collections.Counter()
    for a in todo:
        r = check(a)
        c[r[1]] += 1
        if r[1] != 'OK':
            print(*r)
    print(c)
