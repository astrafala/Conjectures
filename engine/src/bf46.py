#!/usr/bin/env python3
"""Brute force straight from the definition for the monotone-statistic family.

The array is built cell by cell in row major order and every comparison is made the moment
both of its runs are complete, in the orientation the NAME writes -- no transposing, no
transfer matrix. The statistics are written out here rather than imported.
"""
import json, re, sys
import localentry as LE, transfer46

N = json.load(open('/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))
PAIR = {'sum': lambda a, b: a + b, 'difference': lambda a, b: a - b,
        'absolute difference': lambda a, b: a - b if a >= b else b - a,
        'min': lambda a, b: a if a < b else b, 'max': lambda a, b: a if a > b else b}
RUN = {'sum': lambda v: sum(v), 'maximum': lambda v: max(v), 'minimum': lambda v: min(v),
       'median': lambda v: sorted(v)[len(v) // 2], 'range': lambda v: max(v) - min(v)}


def shape(nm, k):
    """rows and columns as the name writes them, for the entry's n = 1, 2, ..."""
    m = transfer46.SHAPE.search(nm.replace(' ', ''))
    ra, rb, ca, cb = m.group(1), int(m.group(2)), m.group(3), int(m.group(4))
    return (ra, rb, ca, cb)


def count(nm, p, R, C, trans):
    A = p['alpha'] + 1
    g = [[0] * C for _ in range(R)]
    tot = 0
    if p['kind'] == 'A':
        h, v = p['h'], p['v']
        # the two directions carry their own sense, and this check hardcoded both as
        # nondecreasing -- the same blindness the parser had, so for a name that is
        # NONINCREASING in one direction it was testing a different problem and disagreeing
        # with the model for that reason alone
        hs, vs = p.get('hsense', 1), p.get('vsense', 1)
        if trans:                      # undo the swap the parser made, senses included
            h, v = v, h
            hs, vs = vs, hs
        H, V = PAIR[h], PAIR[v]

        def okcell(i, j):
            if i and j and hs * H(g[i - 1][j], g[i - 1][j - 1]) > hs * H(g[i][j], g[i][j - 1]):
                return False
            if i and j and vs * V(g[i][j - 1], g[i - 1][j - 1]) > vs * V(g[i][j], g[i - 1][j]):
                return False
            return True
    else:
        f, k = RUN[p['stat']], p['k']

        def okcell(i, j):
            if j >= k and f([g[i][j - k + t] for t in range(k)]) > \
                          f([g[i][j - k + 1 + t] for t in range(k)]):
                return False
            if i >= k and f([g[i - k + t][j] for t in range(k)]) > \
                          f([g[i - k + 1 + t][j] for t in range(k)]):
                return False
            return True

    def go(t):
        nonlocal tot
        if t == R * C:
            tot += 1
            return
        i, j = divmod(t, C)
        for x in range(A):
            g[i][j] = x
            if okcell(i, j):
                go(t + 1)
    go(0)
    return tot


for a in sys.argv[1:]:
    nm = N[a]
    p = transfer46.parse_name(nm)
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    ra, rb, ca, cb = shape(nm, p['k'])
    trans = (ra != 'n')
    got = []
    for t in range(4):
        nn = off + t
        R = nn + rb if ra == 'n' else int(ra) + rb
        C = nn + cb if ca == 'n' else int(ca) + cb
        if R * C > 16:
            break
        got.append(count(nm, p, R, C, trans))
    print(a, 'brute', got, 'data', d[:len(got)], 'MATCH' if got == d[:len(got)] else 'DIFFER')
