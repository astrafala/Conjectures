#!/usr/bin/env python3
"""Independent brute force for the lumped graph-colouring family.

Same as bf66 -- the graphs rebuilt by a different route, the arrays written out cell by cell --
but the counting here applies the entry's start condition DIRECTLY, so it also checks the claim
that fixing the top-left cell divides the unrestricted count by the number of vertices: the
model's terms carry that division, this brute force does not.
"""
import json, sys
import localentry as LE, transfer67, bf66


def check(anum, steps=3):
    e = LE.get(anum)
    p = transfer67.parse_name(e['name'])
    if not p:
        return anum, 'PARSE-FAIL', None
    N, E = bf66.graph_of(p)
    if N != p['N']:
        return anum, 'GRAPH SIZE', (N, p['N'])
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    W, dirs = p['W'], p['dirs']
    if p['trans']:
        dirs = ['vertical' if w == 'horizontal' else
                'horizontal' if w == 'vertical' else w for w in dirs]
    out = []
    for k in range(1, steps + 1):
        R, C = (W, k) if p['trans'] else (k, W)
        out.append(bf66.count(R, C, N, E, dirs, p['start0']))
    for s in range(len(d) - len(out) + 1):
        if d[s:s + len(out)] == out:
            return anum, 'OK', (len(out), s)
    return anum, 'MISMATCH', (out, d[:6])


if __name__ == '__main__':
    import collections
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer67' and not h.get('FAILS')]
    todo = sys.argv[1:] or [h['anum'] for h in hits]
    c = collections.Counter()
    for a in todo:
        r = check(a)
        c[r[1]] += 1
        if r[1] != 'OK':
            print(*r)
    print(c)
