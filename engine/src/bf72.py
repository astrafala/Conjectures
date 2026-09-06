#!/usr/bin/env python3
"""Independent brute force for the subblock-statistic-unequal-to-neighbour family.

Arrays are written out cell by cell, every subblock's statistic is computed from its own two
diagonals, and every named comparison is made directly. No window, no state, no recurrence.
"""
import json, sys
from itertools import product
import localentry as LE, transfer72

DVEC = transfer72.DVEC


def ok(g, R, C, p):
    for k in p['ks']:
        B = [(i, j) for i in range(R - k + 1) for j in range(C - k + 1)]
        bs = set(B)
        for kind, ws in p['clauses']:
            val = {}
            for (i, j) in B:
                d = [g[i + t][j + t] for t in range(k)]
                a = [g[i + t][j + k - 1 - t] for t in range(k)]
                val[(i, j)] = transfer72._stat(kind, d, a)
            for (i, j) in B:
                for w in ws:
                    di, dj = DVEC[w]
                    for sg in (1, -1):
                        q = (i + sg * di, j + sg * dj)
                        if q in bs and val[q] == val[(i, j)]:
                            return False
    return True


def count(R, C, A, p):
    """Backtracking in reading order: a partial fill is abandoned as soon as a comparison whose
    two subblocks are both completely written already fails. Whatever reaches the last cell is
    tested in full by ok(), so the acceptance test is the entry's own words."""
    g = [[0] * C for _ in range(R)]
    tot, n = R * C, 0

    def done(i, j, k, t):
        return (i + k - 1) * C + (j + k - 1) <= t and i >= 0 and j >= 0 \
            and i + k <= R and j + k <= C

    def val(i, j, k, kind):
        d = [g[i + u][j + u] for u in range(k)]
        a = [g[i + u][j + k - 1 - u] for u in range(k)]
        return transfer72._stat(kind, d, a)

    def rec(t):
        nonlocal n
        if t == tot:
            n += ok(g, R, C, p)
            return
        i, j = divmod(t, C)
        for x in range(A):
            g[i][j] = x
            bad = False
            for k in p['ks']:
                for kind, ws in p['clauses']:
                    for bi in range(max(0, i - k + 1), i + 1):
                        for bj in range(max(0, j - k + 1), j + 1):
                            if not done(bi, bj, k, t):
                                continue
                            s = val(bi, bj, k, kind)
                            for w in ws:
                                di, dj = DVEC[w]
                                for sg in (1, -1):
                                    ci, cj = bi + sg * di, bj + sg * dj
                                    if done(ci, cj, k, t) and val(ci, cj, k, kind) == s:
                                        bad = True
                                        break
                                if bad:
                                    break
                            if bad:
                                break
                        if bad:
                            break
                    if bad:
                        break
                if bad:
                    break
            if not bad:
                rec(t + 1)
    rec(0)
    return n


def check(anum, steps=3):
    e = LE.get(anum)
    p = transfer72.parse_name(e['name'])
    if not p:
        return anum, 'PARSE-FAIL', None
    W, A = p['W'], p['alpha'] + 1
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    q = dict(p)
    if p['trans']:                 # count in the entry's own orientation
        q['clauses'] = [(k, ['vertical' if w == 'horizontal' else
                             'horizontal' if w == 'vertical' else w for w in ws])
                        for k, ws in p['clauses']]
    lo = max(p['ks'])
    out = []
    for k in range(lo, lo + steps):
        R, C = (W, k) if p['trans'] else (k, W)
        out.append(count(R, C, A, q) // p['frac'])
    for k in range(len(out) - 1):
        tail = out[k:]
        for s in range(len(d) - len(tail) + 1):
            if d[s:s + len(tail)] == tail:
                return anum, 'OK', (len(tail), s)
    return anum, 'MISMATCH', (out, d[:6])


if __name__ == '__main__':
    import collections
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer72' and not h.get('FAILS')]
    todo = sys.argv[1:] or [h['anum'] for h in hits]
    c = collections.Counter()
    for a in todo:
        r = check(a)
        c[r[1]] += 1
        if r[1] != 'OK':
            print(*r)
    print(c)
