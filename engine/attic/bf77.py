#!/usr/bin/env python3
"""Brute force for transfer77: count in the ORIGINAL frame, listing the cells in TRUE row
major order and testing each precedence on that list.

Nothing here transposes anything and nothing walks. Reading the clause in the walk's own order
instead --- which is what the array's own transpose would give --- returns different numbers
for the entries of this family whose neighbour set includes the diagonal, so this is the check
that separates the two readings."""
import json, re
from itertools import product
import localentry as LE

CLASS = {'horizontally': [(0, 1)], 'vertically': [(1, 0)],
         'diagonally': [(1, 1)], 'antidiagonally': [(1, -1)]}


def spec(a):
    nm = LE.get(a)['name']
    nm = re.sub(r'(?<=[\dn])\s*[xX]\s*(?=[\dn])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = re.search(r'Number of (\d+) X n 0\.\.(\d+) arrays with no element x\(i,j\) adjacent to '
                  r'value (\d+)-x\(i,j\) ([a-z, ]+?), top left element zero, and (.*?) in row '
                  r'major order', nm, re.I)
    R, al = int(m.group(1)), int(m.group(2))
    D = []
    for w in re.findall(r'horizontally|vertically|diagonally|antidiagonally', m.group(4)):
        D += CLASS[w]
    prec = []
    for g in re.finditer(r'(\d+) appearing before ((?:\d+[\s,]*(?:and\s+)?)+?)\s*(?=,|$)', m.group(5)):
        for hi in re.findall(r'\d+', g.group(2)):
            prec.append((int(g.group(1)), int(hi)))
    return R, al, sorted(set(D)), prec


def count(R, al, D, prec, n):
    """R rows, n columns, cells read in ROW MAJOR order of this original frame."""
    m, A = al, al + 1
    tracked = sorted({v for p in prec for v in p})
    tot = 0
    for cells in product(range(A), repeat=R * n):
        g = [cells[i * n:(i + 1) * n] for i in range(R)]
        if g[0][0] != 0:
            continue
        ok = True
        for i in range(R):
            for j in range(n):
                for (di, dj) in D:
                    x, y = i + di, j + dj
                    if 0 <= x < R and 0 <= y < n and g[i][j] + g[x][y] == m:
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                break
        if not ok:
            continue
        seen = set()
        for v in cells:                      # cells is already row major in this frame
            if v in tracked and v not in seen:
                if any(hi == v and lo not in seen for lo, hi in prec):
                    ok = False
                    break
                seen.add(v)
        if ok:
            tot += 1
    return tot


IDS = sorted({h['anum'] for h in json.load(open('transfer77_hits.json'))
              if not h.get('FAILS')})
for a in IDS:
    R, al, D, prec = spec(a)
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    got, want = [], []
    for n in (1, 2, 3):
        if (al + 1) ** (R * n) > 8 * 10 ** 6:
            break
        k = n - off
        if not 0 <= k < len(d):
            break
        got.append(count(R, al, D, prec, n))
        want.append(d[k])
    print(a, 'R=%d al=%d prec=%s' % (R, al, prec), 'rowmajor', got, 'entry', want,
          'OK' if got and got == want else 'MISMATCH', flush=True)
