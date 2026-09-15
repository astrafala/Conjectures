#!/usr/bin/env python3
"""Brute force straight from the definition for the pattern-avoidance family.

The array is enumerated cell by cell in the orientation the NAME writes, and after every cell
each rule is tested on the occurrences that end there. The rules are re-read from the name
here, not taken from the engine's transposed form, and the pattern matching is written out
again rather than imported.
"""
import json, re, sys
import localentry as LE, transfer48

N = json.load(open('/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))


def rules_raw(nm):
    """(rules, W, transposed) with the offsets as the name states them"""
    s = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ',
               re.sub(r'\s+', ' ', transfer48.namecanon.canon(nm))).strip()
    m = transfer48.HEAD.search(s)
    sh = transfer48.SHAPE.search(m.group(1).replace(' ', ''))
    ra = sh.group(1) or sh.group(3)
    rb = int(sh.group(2) or 0)
    ca = sh.group(4) or sh.group(6)
    cb = int(sh.group(5) or 0)
    trans = ra != 'n'
    out = []
    for pats, offs in transfer48._clauses(m.group(4)):
        for o in offs:
            for k, t in pats:
                out.append((k, t, o))
    return out, (ra, rb, ca, cb), trans


def hit(kind, pat, vals):
    if kind == 'abs':
        return tuple(vals) == tuple(pat)
    d = [v - o for v, o in zip(vals, pat)]
    return all(x == d[0] for x in d)


def count(rules, R, C, A):
    g = [[-1] * C for _ in range(R)]
    tot = 0

    def ok(i, j):
        for k, t, (di, dj) in rules:
            n = len(t)
            cells = [(i - di * (n - 1 - s), j - dj * (n - 1 - s)) for s in range(n)]
            if any(not (0 <= a < R and 0 <= b < C) for a, b in cells):
                continue
            if any(g[a][b] < 0 for a, b in cells):
                continue
            if hit(k, t, [g[a][b] for a, b in cells]):
                return False
        return True

    def go(p):
        nonlocal tot
        if p == R * C:
            tot += 1
            return
        i, j = divmod(p, C)
        for v in range(A):
            g[i][j] = v
            if ok(i, j):
                go(p + 1)
            g[i][j] = -1
    go(0)
    return tot


for a in sys.argv[1:]:
    nm = N[a]
    rules, (ra, rb, ca, cb), trans = rules_raw(nm)
    p = transfer48.parse_name(nm)
    A = p['alpha'] + 1
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    got = []
    for t in range(4):
        nn = off + t
        R = nn + rb if ra == 'n' else int(ra) + rb
        C = nn + cb if ca == 'n' else int(ca) + cb
        if R * C > 14 or A ** (R * C) > 3 * 10 ** 7:
            break
        got.append(count(rules, R, C, A))
    print(a, 'brute', got, 'data', d[:len(got)], 'MATCH' if got == d[:len(got)] else 'DIFFER')
