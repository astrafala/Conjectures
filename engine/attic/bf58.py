#!/usr/bin/env python3
"""Brute force from the definition for the adjacency/precedence family."""
import json, re, sys
from itertools import product
import localentry as LE, transfer58

N = json.load(open('/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))


def shape(nm):
    s = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ',
               re.sub(r'\s+', ' ', transfer58.namecanon.canon(nm))).strip()
    m = transfer58.HEAD.search(s)
    return (m.group(1) or m.group(3), int(m.group(2) or 0),
            m.group(4) or m.group(6), int(m.group(5) or 0))


def count(p, R, C):
    A = p['alpha'] + 1
    adj = [tuple(r) for r in p['adj']]
    pre = [tuple(r) for r in p['pre']]
    tot = 0
    for flat in product(range(A), repeat=R * C):
        g = [flat[i * C:(i + 1) * C] for i in range(R)]
        ok = True
        for i in range(R):
            for j in range(C):
                v = g[i][j]
                for r in adj:
                    if v != r[1]:
                        continue
                    if r[0] == 'all':
                        c = sum(1 for di, dj in ((0, -1), (0, 1), (-1, 0), (1, 0))
                                if 0 <= i + di < R and 0 <= j + dj < C
                                and g[i + di][j + dj] == r[3])
                        if c != r[2]:
                            ok = False
                    else:
                        cv = sum(1 for di in (-1, 1)
                                 if 0 <= i + di < R and g[i + di][j] == r[3])
                        ch = sum(1 for dj in (-1, 1)
                                 if 0 <= j + dj < C and g[i][j + dj] == r[5])
                        if cv != r[2] or ch != r[4]:
                            ok = False
                for kind, val, arg in pre:
                    if v != val:
                        continue
                    left = g[i][j - 1] if j > 0 else None
                    up = g[i - 1][j] if i > 0 else None
                    if kind == 'none':
                        if left == arg[0] or up == arg[0]:
                            ok = False
                    elif kind == 'both':
                        have = [t for t in (left, up) if t is not None]
                        if not all(any(t == x for t in have) for x in arg):
                            ok = False
                    elif len(arg) == 1:
                        if not any(t == arg[0] for t in (left, up) if t is not None):
                            ok = False
                    else:
                        a, b = arg
                        okl = j >= 2 and g[i][j - 2] == a and g[i][j - 1] == b
                        oku = i >= 2 and g[i - 2][j] == a and g[i - 1][j] == b
                        if not (okl or oku):
                            ok = False
                if not ok:
                    break
            if not ok:
                break
        tot += ok
    return tot


for a in sys.argv[1:]:
    p = transfer58.parse_name(N[a])
    ra, rb, ca, cb = shape(N[a])
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    got = []
    for t in range(4):
        nn = off + t
        R = nn + rb if ra == 'n' else int(ra) + rb
        C = nn + cb if ca == 'n' else int(ca) + cb
        if (p['alpha'] + 1) ** (R * C) > 3 * 10 ** 7:
            break
        got.append(count(p, R, C))
    print(a, 'brute', got, 'data', d[:len(got)], 'MATCH' if got == d[:len(got)] else 'DIFFER')
