#!/usr/bin/env python3
"""Brute force from the definition for the forbidden-run family."""
import json, re, sys
from itertools import product
import localentry as LE, transfer56

N = json.load(open('/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))
WORD = {'nw-to-se diagonally': (1, 1), 'diagonally downwards': (1, 1), 'diagonally': (1, 1),
        'ne-to-sw antidiagonally': (1, -1), 'antidiagonally downwards': (1, -1),
        'antidiagonally': (1, -1), 'horizontally': (0, 1), 'vertically': (1, 0)}


def raw(nm):
    s = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ',
               re.sub(r'\s+', ' ', transfer56.namecanon.canon(nm))).strip()
    for kind, rx in (('inc', transfer56.INC), ('eq', transfer56.EQ)):
        m = rx.search(s)
        if not m:
            continue
        ra = m.group(1) or m.group(3)
        rb = int(m.group(2) or 0)
        ca = m.group(4) or m.group(6)
        cb = int(m.group(5) or 0)
        D = []
        for h in transfer56.DIRRX.finditer(m.group(9)):
            D.append(WORD[h.group(0).lower()])
        rel = kind == 'eq' and m.group(10) is not None
        return kind, (ra, rb, ca, cb), int(m.group(7)), sorted(set(D)), rel
    return None


def count(kind, R, C, A, L, D, rel):
    """cells filled in row major order, a run tested as soon as its last cell is placed"""
    g = [[-1] * C for _ in range(R)]
    tot = 0

    def ends(i, j):
        for di, dj in D:
            cells = [(i - di * t, j - dj * t) for t in range(L)][::-1]
            if any(not (0 <= a < R and 0 <= b < C) for a, b in cells):
                continue
            if any(g[a][b] < 0 for a, b in cells):
                continue
            v = [g[a][b] for a, b in cells]
            if (all(x == v[0] for x in v) if kind == 'eq'
                    else all(v[t] < v[t + 1] for t in range(L - 1))):
                return False
        return True

    def go(t, used):
        nonlocal tot
        if t == R * C:
            tot += 1
            return
        i, j = divmod(t, C)
        top = min(used + 1, A) if rel else A
        for v in range(top):
            g[i][j] = v
            if ends(i, j):
                go(t + 1, used + (1 if rel and v == used else 0))
            g[i][j] = -1
    go(0, 0)
    return tot


for a in sys.argv[1:]:
    kind, (ra, rb, ca, cb), alpha, D, rel = raw(N[a])
    p = transfer56.parse_name(N[a])
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    got = []
    for t in range(4):
        nn = off + t
        R = nn + rb if ra == 'n' else int(ra) + rb
        C = nn + cb if ca == 'n' else int(ca) + cb
        if R * C > 15:
            break
        got.append(count(kind, R, C, alpha + 1, p['L'], D, rel))
    print(a, 'brute', got, 'data', d[:len(got)], 'MATCH' if got == d[:len(got)] else 'DIFFER')
