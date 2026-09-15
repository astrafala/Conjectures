#!/usr/bin/env python3
"""Brute force for the array-permutation family, straight from the definition.

Every cell is matched to its image one cell at a time, over the whole grid, with no window, no
mask over a sliding frame and no transfer matrix -- the thing the engine builds is exactly what
this avoids. Only the smallest arrays are counted, which is all a check of the reading needs.
"""
import json, sys
import localentry as LE, transfer73

N = json.load(open('/tmp/claude-0/-home-user-Conjectures/'
                   'a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))
OUT = 'bf73_done.json'


def count(R, C, offs):
    cells = [(i, j) for i in range(R) for j in range(C)]
    idx = {c: k for k, c in enumerate(cells)}
    adj = [[idx[(i + d1, j + d2)] for d1, d2 in offs
            if 0 <= i + d1 < R and 0 <= j + d2 < C] for (i, j) in cells]
    n = len(cells)
    memo = {}

    def go(k, used):
        if k == n:
            return 1
        key = (k, used)
        if key in memo:
            return memo[key]
        s = 0
        for t in adj[k]:
            if not used >> t & 1:
                s += go(k + 1, used | 1 << t)
        memo[key] = s
        return s
    return go(0, 0)


if __name__ == '__main__':
    import os
    done = json.load(open(OUT)) if os.path.exists(OUT) else {}
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer73' and not h.get('FAILS')]
    import time
    t0 = time.time()
    for h in hits:
        a = h['anum']
        if a in done or time.time() - t0 > float(sys.argv[1] if len(sys.argv) > 1 else 480):
            continue
        nm = N[a]
        p = transfer73.parse_name(nm)
        # the parser transposes a "W X n" name; the brute force works in the name's own frame
        offs = [(d2, d1) for d1, d2 in p['offs']] if p['trans'] else [tuple(o) for o in p['offs']]
        W = p['W']
        e = LE.get(a)
        d = [int(v) for v in e['data'].split(',') if v.strip()]
        off = int(e['offset'].split(',')[0])
        got = []
        for t in range(4):
            nn = off + t
            R, C = (nn, W) if not p['trans'] else (W, nn)
            if R * C > 22:
                break
            got.append(count(R, C, offs))
        done[a] = {'brute': got, 'data': d[:len(got)],
                   'v': 'OK' if got == d[:len(got)] else 'MISMATCH'}
        json.dump(done, open(OUT, 'w'))
        print(a, done[a]['v'], got, d[:len(got)], flush=True)
    import collections
    print(len(done), 'of', len(hits), dict(collections.Counter(v['v'] for v in done.values())))
