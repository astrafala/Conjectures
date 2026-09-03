#!/usr/bin/env python3
"""Brute force straight from the definition for the clashing-pair family.

The array is built cell by cell in row major order, in the orientation the NAME writes, and
each clause is tested the moment it can be: a clash as soon as both cells of a pair are
placed, the top-left clause on the very first cell, and a precedence the first time the later
value is written. No transfer matrix and no transposition.
"""
import json, re, sys
import localentry as LE, transfer47

N = json.load(open('/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))
WORD = {'horizontally': (0, 1), 'vertically': (1, 0),
        'diagonally': (1, 1), 'antidiagonally': (1, -1)}


def raw(nm):
    """the shape and the offsets as the name states them, with no transposing"""
    s = re.sub(r'\([^()]*\)\s*\.?\s*$', '', transfer47.namecanon.canon(nm)).strip()
    s = re.sub(r'(?<=[\dn])\s*[xX]\s*(?=[\dn])', ' X ', re.sub(r'\s+', ' ', s)).strip()
    m = transfer47.NAME.search(s)
    W = int(m.group(1) or m.group(2))
    trans = m.group(1) is None
    D = sorted({WORD[w] for w in re.findall(
        r'horizontally|vertically|diagonally|antidiagonally', m.group(6).lower())})
    return W, trans, D


def count(nm, p, R, C, D):
    A = p['alpha'] + 1
    s = p['alpha']
    prec = {int(k): set(v) for k, v in p['prec'].items()}
    g = [[-1] * C for _ in range(R)]
    tot = 0

    def bad(a, b):
        return a + b == s or (p['self'] and a == b)

    def go(t, seen):
        nonlocal tot
        if t == R * C:
            tot += 1
            return
        i, j = divmod(t, C)
        for x in range(A):
            if p['tl0'] and t == 0 and x != 0:
                continue
            ok = True
            for di, dj in D:                     # the partner already placed, either way
                for (a, b) in ((i - di, j - dj), (i + di, j + dj)):
                    if 0 <= a < R and 0 <= b < C and (a, b) < (i, j) and bad(g[a][b], x):
                        ok = False
            if not ok:
                continue
            if x in prec and x not in seen and not prec[x] <= seen:
                continue
            g[i][j] = x
            go(t + 1, seen | {x})
            g[i][j] = -1
    go(0, set())
    return tot


for a in sys.argv[1:]:
    nm = N[a]
    p = transfer47.parse_name(nm)
    W, trans, D = raw(nm)
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    got = []
    for k in range(4):
        nn = off + k
        R, C = (nn, W) if not trans else (W, nn)
        if R * C > 13:
            break
        got.append(count(nm, p, R, C, D))
    print(a, 'brute', got, 'data', d[:len(got)], 'MATCH' if got == d[:len(got)] else 'DIFFER')
