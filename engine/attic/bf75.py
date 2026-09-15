#!/usr/bin/env python3
"""Brute force for the 3 X 3 subblock-property family, from the words of the name.

Every array is written out cell by cell and each 3 x 3 subblock is tested directly: its sum,
its multiset of value multiplicities, its determinant, its 36 pairwise absolute differences, or
its vector of value counts. No rows, no window, no state, no transfer matrix -- and in
particular nothing shared with either of the two engines that produce these counts.
"""
import json, os, re, sys, time
from itertools import product
from collections import Counter
import localentry as LE, transfer75, transfer23, uniform

N = json.load(open('/tmp/claude-0/-home-user-Conjectures/'
                   'a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))
OUT = 'bf75_done.json'
SH = re.compile(r'(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))\s*X\s*'
                r'(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))\s*0\.\.(\d+)')
WORD = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9}


def predicate(nm, A):
    """(per-block test, or None) and (per-block key for a 'same across blocks' condition)."""
    s = re.sub(r'\s+', ' ', nm)
    m = re.search(r'each 3 ?X ?3 subblock (.*?)\.?$', s, re.I)
    if not m:
        return None, None, False
    b = m.group(1)
    noadj = bool(re.search(r'no adjacent elements equal', b, re.I))
    if re.search(r'the same population', b, re.I):
        return None, (lambda c: tuple(c.count(v) for v in range(A))), noadj
    g = re.search(r'having a sum in (\d+)\.\.(\d+)', b, re.I)
    if g:
        lo, hi = int(g.group(1)), int(g.group(2))
        return (lambda c: lo <= sum(c) <= hi), None, noadj
    g = re.search(r'having (?:a )?sum(?: of)? ([\d,\s]*\d(?:\s*or\s*\d+)?)', b, re.I)
    if g:
        S = {int(x) for x in re.findall(r'\d+', g.group(1))}
        return (lambda c: sum(c) in S), None, noadj
    g = re.search(r'containing (\w+) of each value', b, re.I)
    if g:
        k = WORD[g.group(1).lower()]
        return (lambda c: sorted(Counter(c).values()) == [k] * A), None, noadj
    g = re.search(r'containing (\w+) of one value, (\w+) of another, and (\w+) of the last', b, re.I)
    if g:
        want = sorted(WORD[x.lower()] for x in g.groups())
        def f(c, want=want):
            v = sorted(Counter(c).values())
            v = [0] * (len(want) - len(v)) + v
            return v == want
        return f, None, noadj
    if re.search(r'a positive determinant', b, re.I):
        def det(c):
            return (c[0] * (c[4] * c[8] - c[5] * c[7])
                    - c[1] * (c[3] * c[8] - c[5] * c[6])
                    + c[2] * (c[3] * c[7] - c[4] * c[6])) > 0
        return det, None, noadj
    g = re.search(r'absolute element differences equal to (\d+)', b, re.I)
    if g:
        tgt = int(g.group(1))
        return (lambda c: sum(abs(c[i] - c[j]) for i in range(9) for j in range(i + 1, 9))
                == tgt), None, noadj
    return None, None, noadj


def count(R, C, A, test, key, noadj, frac):
    tot = 0
    for flat in product(range(A), repeat=R * C):
        g = [flat[i * C:(i + 1) * C] for i in range(R)]
        if noadj and any((j + 1 < C and g[i][j] == g[i][j + 1])
                         or (i + 1 < R and g[i][j] == g[i + 1][j])
                         for i in range(R) for j in range(C)):
            continue
        ok, keys = True, set()
        for i in range(R - 2):
            for j in range(C - 2):
                c = [g[i + r][j + q] for r in range(3) for q in range(3)]
                if test is not None and not test(c):
                    ok = False
                    break
                if key is not None:
                    keys.add(key(c))
                    if len(keys) > 1:
                        ok = False
                        break
            if not ok:
                break
        if ok:
            tot += 1
    return tot // frac if tot % frac == 0 else None


if __name__ == '__main__':
    done = json.load(open(OUT)) if os.path.exists(OUT) else {}
    rm = {r['anum'] for r in json.load(open('rank-map.json'))}
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') in ('transfer23', 'transfer75') and not h.get('FAILS')
            and h['anum'] not in rm]
    seen = set()
    t0 = time.time()
    for h in hits:
        a = h['anum']
        if a in done or a in seen or time.time() - t0 > float(sys.argv[1] if len(sys.argv) > 1 else 470):
            continue
        seen.add(a)
        nm = re.sub(r'\s+', ' ', N[a])
        m = SH.search(nm)
        if m is None:                      # a "binary matrices" name has no 0..m
            m = re.search(r'(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))\s*X\s*'
                          r'(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))\s+binary', nm)
            if m is None:
                done[a] = {'v': 'SHAPE NOT READ'}; continue
            A = 2
        else:
            A = int(m.group(7)) + 1
        ra = m.group(1) or m.group(3); rb = int(m.group(2) or 0)
        ca = m.group(4) or m.group(6); cb = int(m.group(5) or 0)
        p = transfer75.parse_name(nm) or transfer23.parse_name(nm)
        frac = (p or {}).get('frac', 1)
        test, key, noadj = predicate(nm, A)
        if test is None and key is None:
            done[a] = {'v': 'CONDITION NOT READ'}; continue
        e = LE.get(a)
        d = [int(v) for v in e['data'].split(',') if v.strip()]
        off = int(e['offset'].split(',')[0])
        got = []
        for t in range(3):
            nn = off + t
            R = nn + rb if ra == 'n' else int(ra) + rb
            C = nn + cb if ca == 'n' else int(ca) + cb
            if A ** (R * C) > 2_500_000:
                break
            got.append(count(R, C, A, test, key, noadj, frac))
        done[a] = {'brute': got, 'data': d[:len(got)],
                   'v': 'OK' if got and got == d[:len(got)] else
                        ('NO TERMS SMALL ENOUGH' if not got else 'MISMATCH')}
        json.dump(done, open(OUT, 'w'))
        print(a, done[a]['v'], got, d[:len(got)], flush=True)
    import collections
    print(len(done), 'of', len({h['anum'] for h in hits}),
          dict(collections.Counter(v['v'] for v in done.values())))
