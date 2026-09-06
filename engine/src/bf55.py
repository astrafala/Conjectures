#!/usr/bin/env python3
"""Brute force from the definition for the repeated-value family."""
import json, re, sys
from itertools import product
import localentry as LE, transfer55

N = json.load(open('/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))


def shape(nm):
    s = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ',
               re.sub(r'\s+', ' ', transfer55.namecanon.canon(nm))).strip()
    m = transfer55.NAME.search(s)
    return (m.group(1) or m.group(3), int(m.group(2) or 0),
            m.group(4) or m.group(6), int(m.group(5) or 0))


def chain(seq, key, mod):
    """the repeated values of one scan stand in the stated relation"""
    f = transfer55.TEST[key]
    last = None
    for t in range(1, len(seq)):
        if seq[t] == seq[t - 1]:
            if last is not None and not f(seq[t], last, mod):
                return False
            last = seq[t]
    return True


def count(p, R, C):
    A = p['alpha'] + 1
    rk, rmod = (p['inrun'] if not p['trans'] else p['across'])      # the ROW relation
    ck, cmod = (p['across'] if not p['trans'] else p['inrun'])      # the COLUMN relation
    tot = 0
    for flat in product(range(A), repeat=R * C):
        if p['tl0'] and flat and flat[0] != 0:
            continue
        if p['rel']:
            seen = []
            bad = False
            for v in flat:
                if v not in seen:
                    if v != len(seen):
                        bad = True
                        break
                    seen.append(v)
            if bad:
                continue
        g = [flat[i * C:(i + 1) * C] for i in range(R)]
        if not all(chain(list(r), rk, rmod) for r in g):
            continue
        if not all(chain([g[i][j] for i in range(R)], ck, cmod) for j in range(C)):
            continue
        tot += 1
    return tot


for a in sys.argv[1:]:
    p = transfer55.parse_name(N[a])
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
