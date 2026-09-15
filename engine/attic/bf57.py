#!/usr/bin/env python3
"""Brute force from the definition for the subblock line-sum family."""
import json, re, sys
import localentry as LE, transfer57

N = json.load(open('/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))


def shape(nm):
    s = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ',
               re.sub(r'\s+', ' ', transfer57.namecanon.canon(nm))).strip()
    m = transfer57.HEAD.search(s)
    return (m.group(1) or m.group(3), int(m.group(2) or 0),
            m.group(4) or m.group(6), int(m.group(5) or 0))


def count(p, R, C):
    """cells in row major order, a subblock tested as soon as its last cell is placed"""
    A = p['alpha'] + 1
    K = p['K']
    rules = {t: (mode, set(s) if s is not None else None) for t, (mode, s) in p['rules'].items()}
    cmps = [tuple(c) for c in p['cmps']]
    total = p['total']
    # undo the parser's transpose: the brute force works in the frame the NAME writes
    if p['trans']:
        SW = {'row': 'column', 'column': 'row', 'crow': 'ccol', 'ccol': 'crow'}
        rules = {SW.get(t, t): v for t, v in rules.items()}
        cmps = [(SW.get(x, x), SW.get(y, y), c) for x, y, c in cmps]
    g = [[0] * C for _ in range(R)]
    tot = 0

    def okline(t, v):
        mode, s = rules[t]
        if mode == 'forbid':
            return v not in s
        if mode == 'require':
            return v in s
        return transfer57._prime(v)

    def blockok(i, j):
        blk = [[g[i + r][j + c] for c in range(K)] for r in range(K)]
        if total is not None:
            # the name may allow a SET of window sums -- "summing to 2, 4, or 6" -- so this
            # is membership, not equality
            return sum(sum(r) for r in blk) in set(total)
        val = {'diagonal': sum(blk[r][r] for r in range(K)),
               'antidiagonal': sum(blk[r][K - 1 - r] for r in range(K)),
               'crow': sum(blk[K // 2]),
               'ccol': sum(blk[r][K // 2] for r in range(K))}
        for x, y, c in cmps:
            if transfer57.CMP[c](val[x], val[y]):
                return False
        if 'row' in rules and any(not okline('row', sum(blk[r])) for r in range(K)):
            return False
        if 'column' in rules and any(not okline('column', sum(blk[r][c] for r in range(K)))
                                     for c in range(K)):
            return False
        for t in ('diagonal', 'antidiagonal'):
            if t in rules and not okline(t, val[t]):
                return False
        return True

    def go(t):
        nonlocal tot
        if t == R * C:
            tot += 1
            return
        i, j = divmod(t, C)
        for v in range(A):
            g[i][j] = v
            if i >= K - 1 and j >= K - 1 and not blockok(i - K + 1, j - K + 1):
                continue
            go(t + 1)
        g[i][j] = 0
    go(0)
    return tot


for a in sys.argv[1:]:
    p = transfer57.parse_name(N[a])
    ra, rb, ca, cb = shape(N[a])
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    got = []
    for t in range(4):
        nn = off + t
        R = nn + rb if ra == 'n' else int(ra) + rb
        C = nn + cb if ca == 'n' else int(ca) + cb
        if R * C > 24:
            break
        got.append(count(p, R, C))
    print(a, 'brute', got, 'data', d[:len(got)], 'MATCH' if got == d[:len(got)] else 'DIFFER')
