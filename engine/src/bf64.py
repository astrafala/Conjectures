#!/usr/bin/env python3
"""Independent brute force for the 2 X 2 perimeter family.

Every array of the stated width with a few rows is written out cell by cell; each of its
2 X 2 subblocks is read round its perimeter and the condition applied straight from the
entry's own words. Nothing here touches transfer64: no window, no state, no recurrence.
"""
import json, sys
from itertools import product
import localentry as LE, transfer64


def ok(g, R, C, p):
    k, m = p['kind'], p['mode']
    if p['noadjeq']:
        for i in range(R):
            for j in range(C):
                if j + 1 < C and g[i][j] == g[i][j + 1]:
                    return False
                if i + 1 < R and g[i][j] == g[i + 1][j]:
                    return False
    cw = {}
    cc = {}
    for i in range(R - 1):
        for j in range(C - 1):
            a, b, c, d = g[i][j], g[i][j + 1], g[i + 1][j], g[i + 1][j + 1]
            u = (a < b) + (b < d) + (d < c) + (c < a)
            v = (a < c) + (c < d) + (d < b) + (b < a)
            cw[(i, j)], cc[(i, j)] = u, v
            if k == 'pattern':
                if '%d%d%d%d' % (a, b, d, c) not in p['pats']:
                    return False
            elif k == 'cmp':
                if not (u == v if m == 'eq' else u <= v):
                    return False
            elif k == 'jump':
                x = max(b - a, d - b, c - d, a - c) <= 1
                y = max(c - a, d - c, b - d, a - b) <= 1
                if not ((x or y) if m == 'or' else (x != y)):
                    return False
            elif k == 'strict':
                if a == b or b == d or d == c or c == a or u not in (1, 3):
                    return False
            elif k == 'diffs':
                if len({b - a, d - b, c - d, a - c}) not in (1, 4):
                    return False
    if k == 'samecw':
        return len(set(cw.values())) <= 1
    for (i, j), u in cw.items():
        v = cc[(i, j)]
        R1, D1 = cw.get((i, j + 1)), cw.get((i + 1, j))
        R2, D2 = cc.get((i, j + 1)), cc.get((i + 1, j))
        if k == 'mono':
            if R1 is not None and not u <= R1:
                return False
            if D1 is not None and not u <= D1:
                return False
            if p['ccw']:
                if R2 is not None and not v >= R2:
                    return False
                if D2 is not None and not v >= D2:
                    return False
        elif k == 'nbr':
            L, U = cc.get((i, j - 1)), cc.get((i - 1, j))
            for w in (L, U):
                if w is None:
                    continue
                if (u == w) if m == 'ne' else (u != w):
                    return False
        elif k == 'hv':
            if R1 is not None and ((u == R1) if m == 'ne' else (u != R1)):
                return False
            if D2 is not None and ((v == D2) if m == 'ne' else (v != D2)):
                return False
    if k == 'strict' and m == 'adj':
        for (i, j), u in cw.items():
            if cw.get((i, j + 1)) == u or cw.get((i + 1, j)) == u:
                break
        else:
            return False
    return True


def _local(a, b, c, d, p):
    """The part of the condition that one completed subblock decides on its own."""
    k, m = p['kind'], p['mode']
    u = (a < b) + (b < d) + (d < c) + (c < a)
    v = (a < c) + (c < d) + (d < b) + (b < a)
    if k == 'pattern':
        return '%d%d%d%d' % (a, b, d, c) in p['pats']
    if k == 'cmp':
        return u == v if m == 'eq' else u <= v
    if k == 'jump':
        x = max(b - a, d - b, c - d, a - c) <= 1
        y = max(c - a, d - c, b - d, a - b) <= 1
        return (x or y) if m == 'or' else (x != y)
    if k == 'strict':
        return not (a == b or b == d or d == c or c == a) and u in (1, 3)
    if k == 'diffs':
        return len({b - a, d - b, c - d, a - c}) in (1, 4)
    return True


def count(R, C, A, p):
    """Backtracking over the cells in reading order. A partial fill is abandoned only when a
    subblock it has just completed already fails on its own; every array that survives to the
    last cell is then tested in full by ok(), so the acceptance test is the entry's own words
    applied to a finished array."""
    g = [[0] * C for _ in range(R)]
    n = 0
    total = R * C

    def rec(t):
        nonlocal n
        if t == total:
            n += ok(g, R, C, p)
            return
        i, j = divmod(t, C)
        for x in range(A):
            if p['noadjeq'] and ((j and g[i][j - 1] == x) or (i and g[i - 1][j] == x)):
                continue
            g[i][j] = x
            if i and j and not _local(g[i - 1][j - 1], g[i - 1][j], g[i][j - 1], x, p):
                continue
            rec(t + 1)

    rec(0)
    return n


def check(anum, rows=2, budget=3000000000):
    e = LE.get(anum)
    p = transfer64.parse_name(e['name'])
    W, A = p['W'], p['alpha'] + 1
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    out = []
    for R in range(2, rows + 1):        # a single row has no subblock and says nothing
        out.append(count(R, W, A, p) // p['frac'])
    if not out:
        return anum, 'too big', None
    # arrays of R rows are a(R-1+off_shift); locate by matching
    for s in range(len(d) - len(out) + 1):
        if d[s:s + len(out)] == out:
            return anum, 'OK', (len(out), s)
    return anum, 'MISMATCH', (out, d[:6])


if __name__ == '__main__':
    import collections
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer64' and not h.get('FAILS')]
    todo = sys.argv[1:] or [h['anum'] for h in hits]
    c = collections.Counter()
    for a in todo:
        r = check(a, rows=3)
        c[r[1]] += 1
        if r[1] != 'OK':
            print(*r)
    print(c)
