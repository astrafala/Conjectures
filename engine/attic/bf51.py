#!/usr/bin/env python3
"""Brute force from the definition for the row/column divisibility family.

Every array of the size the NAME states is enumerated, each row and each column is turned into
a base-b number with the first digit most significant, and the divisibility (and, where the
name asks for it, the lexicographic order) is tested directly. No residue state, no Horner
step and no transposing.
"""
import json, re, sys
from itertools import product
import localentry as LE, transfer51

N = json.load(open('/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))


def raw(nm):
    s = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ',
               re.sub(r'\s+', ' ', transfer51.namecanon.canon(nm))).strip()
    m = transfer51.NAME.search(s)
    ra = m.group(1) or m.group(3)
    rb = int(m.group(2) or 0)
    ca = m.group(4) or m.group(6)
    cb = int(m.group(5) or 0)
    shared = bool(m.group(8))
    rowneg, rowmod = bool(m.group(9)), int(m.group(10))
    if m.group(12):
        colneg, colmod = bool(m.group(11)), int(m.group(12))
    else:
        colneg, colmod = rowneg, rowmod
    base = 2 if m.group(13) else int(m.group(14))
    lex = (m.group(15) or '').lower()
    return (ra, rb, ca, cb), base, (rowneg, rowmod), (colneg, colmod), lex


def val(digits, b):
    v = 0
    for x in digits:
        v = v * b + x
    return v


def count(R, C, b, rowc, colc, lex):
    rneg, rmod = rowc
    cneg, cmod = colc
    tot = 0
    for flat in product(range(b), repeat=R * C):
        g = [flat[i * C:(i + 1) * C] for i in range(R)]
        if any((val(r, b) % rmod == 0) == rneg for r in g):
            continue
        cols = [tuple(g[i][j] for i in range(R)) for j in range(C)]
        if any((val(c, b) % cmod == 0) == cneg for c in cols):
            continue
        if lex:
            up = lex == 'nondecreasing'
            if up and (any(g[i] > g[i + 1] for i in range(R - 1)) or
                       any(cols[j] > cols[j + 1] for j in range(C - 1))):
                continue
            if not up and (any(g[i] < g[i + 1] for i in range(R - 1)) or
                           any(cols[j] < cols[j + 1] for j in range(C - 1))):
                continue
        tot += 1
    return tot


for a in sys.argv[1:]:
    (ra, rb, ca, cb), b, rowc, colc, lex = raw(N[a])
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    got = []
    for t in range(4):
        nn = off + t
        R = nn + rb if ra == 'n' else int(ra) + rb
        C = nn + cb if ca == 'n' else int(ca) + cb
        if b ** (R * C) > 3 * 10 ** 7:
            break
        got.append(count(R, C, b, rowc, colc, lex))
    print(a, 'brute', got, 'data', d[:len(got)], 'MATCH' if got == d[:len(got)] else 'DIFFER')
