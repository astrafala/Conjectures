#!/usr/bin/env python3
"""Brute force for the entries transfer41 reads in the TRANSPOSED orientation.

The engine transposes the array and swaps the words `horizontal' and `vertical'. This does not:
it writes out arrays with the shape and the words exactly as the NAME gives them, and tests
every cell against the neighbours the name lists. If the transposition were wrong, the counts
would differ.
"""
import json, os, re, sys, time
from itertools import product
import localentry as LE, transfer41

N = json.load(open('/tmp/claude-0/-home-user-Conjectures/'
                   'a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))
OUT = 'bf41t_done.json'
CLASS = {'horizontal': [(0, -1), (0, 1)], 'vertical': [(-1, 0), (1, 0)],
         'diagonal': [(-1, -1), (1, 1)], 'antidiagonal': [(-1, 1), (1, -1)]}
SH = re.compile(r'\(?\s*(\d+)(?:\s*\+\s*(\d+))?\s*\)?\s*X\s*(?:\(\s*n\s*\+\s*1\s*\)|n)\s+'
                r'(?:0\.\.(\d+)|(binary))\s+arrays\s+with\s+', re.I)


def count(R, C, A, offs, topleft):
    tot = 0
    for flat in product(range(A), repeat=R * C):
        g = [flat[i * C:(i + 1) * C] for i in range(R)]
        if topleft and g[0][0] != 0:
            continue
        ok = True
        for i in range(R):
            for j in range(C):
                seen = False
                for di, dj in offs:
                    ii, jj = i + di, j + dj
                    if 0 <= ii < R and 0 <= jj < C and g[ii][jj] == g[i][j]:
                        seen = True
                        break
                if not seen:
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
            if h.get('engine') == 'transfer41' and not h.get('FAILS')
            and (transfer41.parse_name(N[h['anum']]) or {}).get('trans')]
    t0 = time.time()
    for h in hits:
        a = h['anum']
        if a in done or time.time() - t0 > float(sys.argv[1] if len(sys.argv) > 1 else 460):
            continue
        nm = re.sub(r'\s+', ' ', N[a])
        p = transfer41.parse_name(nm)
        if p['kind'] != 'somematch':
            done[a] = {'v': 'NOT THIS BRUTE FORCE', 'kind': p['kind']}
            continue
        m = SH.search(nm)
        R = int(m.group(1)) + (int(m.group(2)) if m.group(2) else 0)
        A = 2 if m.group(4) else int(m.group(3)) + 1
        body = nm[m.end():]
        offs = []
        for w in re.findall(r'antidiagonal|horizontal|vertical|diagonal', body.lower()):
            offs += CLASS[w]
        offs = sorted(set(offs))
        topleft = bool(re.search(r'top left element zero', body, re.I))
        e = LE.get(a)
        d = [int(v) for v in e['data'].split(',') if v.strip()]
        off = int(e['offset'].split(',')[0])
        got = []
        for t in range(4):
            C = off + t + 1                       # the name's "(n+1)" columns
            if A ** (R * C) > 3_000_000:
                break
            got.append(count(R, C, A, offs, topleft) // p['frac'])
        done[a] = {'brute': got, 'data': d[:len(got)], 'R': R, 'offs': offs,
                   'v': 'OK' if got and got == d[:len(got)] else
                        ('NO TERMS SMALL ENOUGH' if not got else 'MISMATCH')}
        json.dump(done, open(OUT, 'w'))
        print(a, done[a]['v'], got, d[:len(got)], flush=True)
    import collections
    print(len(done), 'of', len(hits), dict(collections.Counter(v['v'] for v in done.values())))
