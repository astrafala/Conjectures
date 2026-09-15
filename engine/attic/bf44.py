#!/usr/bin/env python3
"""Brute force straight from the definition, for the turn-constrained occupancy family."""
import json, re, sys
from itertools import product
import transfer44, localentry as LE

N = json.load(open('/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))
CLASS = transfer44.CLASS


def raw(nm):
    """the array shape and the moves as the NAME states them, with no transposing"""
    nm = re.sub(r'(?<=[\dn])\s*[xX]\s*(?=[\dn])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = transfer44.NAME.search(nm)
    W = int(m.group(1) or m.group(2))
    trans = m.group(1) is None
    D = []
    for w in re.findall(r'antidiagonal|king-move|horizontal|vertical|diagonal',
                        m.group(4).lower()):
        D += CLASS[w]
    if m.group(3):
        D.append((0, 0))
    return W, trans, sorted(set(D))


def count(nm, n):
    W, trans, D = raw(nm)
    p = transfer44.parse_name(nm)
    R, C = (n, W) if not trans else (W, n)
    kinds = p['bad']

    def bad(d, e):
        # written out here rather than imported, so that the check does not share the
        # engine's own reading of the condition
        if d == (0, 0) or e == (0, 0):
            return False
        if 'straight' in kinds and e == d:
            return True
        if 'loop' in kinds and (e[0] + d[0], e[1] + d[1]) == (0, 0):
            return True
        if 'left' in kinds:
            (ax, ay), (bx, by) = (d[1], -d[0]), (e[1], -e[0])
            if ax * by - ay * bx > 0:
                return True
        return False

    cells = [(i, j) for i in range(R) for j in range(C)]
    opts = [[d for d in D if 0 <= i + d[0] < R and 0 <= j + d[1] < C] for i, j in cells]
    seen = set()
    for mv in product(*opts):
        m = dict(zip(cells, mv))
        ok = True
        for (i, j), d in m.items():
            t = (i + d[0], j + d[1])
            if bad(d, m[t]):
                ok = False
                break
        if not ok:
            continue
        occ = [[0] * C for _ in range(R)]
        for (i, j), d in m.items():
            occ[i + d[0]][j + d[1]] += 1
        if p['cap'] is not None and any(v > p['cap'] for row in occ for v in row):
            continue
        seen.add(tuple(tuple(r) for r in occ))
    return len(seen)


for a in sys.argv[1:]:
    nm = N[a]
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    got = []
    for k in range(4):
        n = off + k
        W, trans, D = raw(nm)
        if (n * W if not trans else n * W) > 12:
            break
        got.append(count(nm, n))
    print(a, 'brute', got, 'data', d[:len(got)], 'MATCH' if got == d[:len(got)] else 'DIFFER')
