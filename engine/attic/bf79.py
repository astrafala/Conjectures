#!/usr/bin/env python3
"""Brute force for the plane-partition-in-a-box family: enumerate the matrices themselves.

No product formula and no plane partitions -- every P X Q matrix over 0..n is written out row
by row and its rows and columns tested for being nondecreasing."""
import json, sys
from itertools import combinations_with_replacement

import transfer79, localentry as LE


def count(P, Q, n):
    """count the matrices by listing the admissible rows and counting the chains of P of them
    that increase componentwise -- the definition itself, with no formula anywhere"""
    rows = list(combinations_with_replacement(range(n + 1), Q))   # nondecreasing rows
    cur = [1] * len(rows)
    for _ in range(P - 1):
        nxt = []
        for r in rows:
            nxt.append(sum(c for s, c in zip(rows, cur)
                           if all(s[j] <= r[j] for j in range(Q))))
        cur = nxt
    return sum(cur)


if __name__ == '__main__':
    LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 40000
    names = json.load(open('/tmp/claude-0/-home-user-Conjectures/'
                           'a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))
    for a in sorted(names):
        p = transfer79.parse_name(names[a])
        if not p:
            continue
        P, Q = p['P'], p['Q']
        e = LE.get(a)
        d = [int(x) for x in e['data'].split(',') if x.strip()]
        off = int(e['offset'].split(',')[0])
        got, want = [], []
        for k in range(4):
            n = off + k
            from math import comb
            if comb(n + Q, Q) ** 2 * P > LIMIT or k >= len(d):
                break
            got.append(count(P, Q, n))
            want.append(d[k])
        print(a, f'{P}x{Q}', 'brute', got, 'entry', want,
              'OK' if got and got == want else ('MISMATCH' if got else 'too big'), flush=True)
