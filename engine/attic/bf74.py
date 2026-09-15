#!/usr/bin/env python3
"""Brute force for the min-plus-max family, straight from the words of the name.

Every array is written out cell by cell and each 2 x 2 subblock is tested by taking its four
values, sorting them, and comparing the smallest plus the largest with the two in the middle.
No rows, no state, no transfer matrix.
"""
import json, os, re, sys, time
from itertools import product
import localentry as LE, transfer74

N = json.load(open('/tmp/claude-0/-home-user-Conjectures/'
                   'a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))
OUT = 'bf74_done.json'
SH = re.compile(r'(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))\s*X\s*'
                r'(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))')


def count(R, C, A, want):
    tot = 0
    for flat in product(range(A), repeat=R * C):
        g = [flat[i * C:(i + 1) * C] for i in range(R)]
        ok = True
        for i in range(R - 1):
            for j in range(C - 1):
                s = sorted((g[i][j], g[i][j + 1], g[i + 1][j], g[i + 1][j + 1]))
                if ((s[0] + s[3]) == (s[1] + s[2])) != want:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            tot += 1
    return tot


if __name__ == '__main__':
    done = json.load(open(OUT)) if os.path.exists(OUT) else {}
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer74' and not h.get('FAILS')]
    t0 = time.time()
    for h in hits:
        a = h['anum']
        if a in done or time.time() - t0 > float(sys.argv[1] if len(sys.argv) > 1 else 480):
            continue
        nm = re.sub(r'\s+', ' ', N[a])
        p = transfer74.parse_name(nm)
        m = SH.search(nm)
        ra = m.group(1) or m.group(3); rb = int(m.group(2) or 0)
        ca = m.group(4) or m.group(6); cb = int(m.group(5) or 0)
        e = LE.get(a)
        d = [int(v) for v in e['data'].split(',') if v.strip()]
        off = int(e['offset'].split(',')[0])
        got = []
        for t in range(4):
            nn = off + t
            R = nn + rb if ra == 'n' else int(ra) + rb
            C = nn + cb if ca == 'n' else int(ca) + cb
            if (p['alpha'] + 1) ** (R * C) > 3_000_000:
                break
            got.append(count(R, C, p['alpha'] + 1, p['equal']) // p['frac'])
        done[a] = {'brute': got, 'data': d[:len(got)],
                   'v': 'OK' if got and got == d[:len(got)] else
                        ('NO TERMS SMALL ENOUGH' if not got else 'MISMATCH')}
        json.dump(done, open(OUT, 'w'))
        print(a, done[a]['v'], got, d[:len(got)], flush=True)
    import collections
    print(len(done), 'of', len(hits), dict(collections.Counter(v['v'] for v in done.values())))
