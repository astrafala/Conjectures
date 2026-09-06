#!/usr/bin/env python3
"""Matrix statistics of the 2 X 2 subblocks: determinant, permanent, trace and sum.

Name shapes covered, for an $(n+1)\\times W$ array over $\\{0,\\dots,m\\}$:

    every 2 X 2 subblock singular / nonsingular
    the <statistic>s of 2 X 2 subblocks nondecreasing rightwards and downwards
    the <statistic>s of all 2 X 2 subblocks equal [and nonzero]
    no 2 X 2 subblock <statistic> equal to any horizontal or vertical neighbor 2 X 2 subblock
        <statistic>
    <statistic>s of 2 X 2 subblocks differing from [horizontal and vertical] neighbor(ing)
        <statistic>s

Two state shapes are needed and the parser records which. When the condition looks at ONE
subblock at a time --- singular, nonsingular, all equal to a common value --- a single array
row is a state. When it compares NEIGHBOURING subblocks the state is a pair of consecutive
rows, because a subblock's value needs two rows and the vertical comparison needs the two
subblock rows the three rows produce.

`all ... equal' does not name the common value, so the count splits by it: the arrays whose
subblocks all give $v$ are counted separately for each $v$ and the sets are disjoint.
"""
import re
from itertools import product

import namecanon
import transfer17

STAT = {'determinant': lambda p, q, r, s: p * s - q * r,
        'permanent': lambda p, q, r, s: p * s + q * r,
        'trace': lambda p, q, r, s: p + s,
        'sum': lambda p, q, r, s: p + q + r + s}
SING = r'(determinant|permanent|trace|sum)'
PLUR = r'(determinants|permanents|traces|sums)'

HEAD = re.compile(r'Number of \(\s*n\s*\+\s*1\s*\)\s*X\s*(\d+)\s*'
                  r'(?:0\.\.(\d+)|(binary))\s+arrays\s+with\s+(.*?)\s*\.?\s*$', re.I)

C1 = re.compile(r'every 2\s*X\s*2 subblock (singular|nonsingular)$', re.I)
C2 = re.compile(r'the ' + PLUR + r' of 2\s*X\s*2 subblocks nondecreasing rightwards and '
                r'downwards$', re.I)
C3 = re.compile(r'the ' + PLUR + r' of all 2\s*X\s*2 subblocks equal( and nonzero)?$', re.I)
C4 = re.compile(r'no 2\s*X\s*2 subblock ' + SING + r' equal to any horizontal or vertical '
                r'neighbor 2\s*X\s*2 subblock ' + SING + r'$', re.I)
C5 = re.compile(PLUR + r' of 2\s*X\s*2 subblocks differing from '
                r'(?:horizontal and vertical neighbor|neighboring) ' + PLUR + r'$', re.I)


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn)])\s*[xX]\s*(?=[\dn(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = HEAD.search(nm)
    if not m:
        return None
    W = int(m.group(1))
    alpha = 1 if m.group(3) else int(m.group(2))
    body = m.group(4)
    if W < 2 or alpha < 1:
        return None
    out = {'W': W, 'alpha': alpha, 'frac': 1, 'nonzero': False}
    c = C1.match(body)
    if c:
        out.update(kind='single', stat='determinant',
                   want=('zero' if c.group(1).lower() == 'singular' else 'nonzero'))
        return out
    c = C2.match(body)
    if c:
        out.update(kind='mono', stat=c.group(1).lower().rstrip('s'))
        return out
    c = C3.match(body)
    if c:
        out.update(kind='same', stat=c.group(1).lower().rstrip('s'),
                   nonzero=bool(c.group(2)))
        return out
    c = C4.match(body)
    if c and c.group(1).lower() == c.group(2).lower():
        out.update(kind='differ', stat=c.group(1).lower())
        return out
    c = C5.match(body)
    if c and c.group(1).lower() == c.group(2).lower():
        out.update(kind='differ', stat=c.group(1).lower().rstrip('s'))
        return out
    return None


def _rowvals(f, r, s, K):
    return tuple(f(r[j], r[j + 1], s[j], s[j + 1]) for j in range(K))


def build(p, cap=40000):
    W, A, kind = p['W'], p['alpha'] + 1, p['kind']
    f = STAT[p['stat']]
    K = W - 1
    if A ** W > 4 * cap:
        return None
    rows = list(product(range(A), repeat=W))

    if kind == 'single':                      # one subblock at a time: a row is a state
        want = p['want']
        adj = []
        for r in rows:
            row = []
            for j, s in enumerate(rows):
                v = _rowvals(f, r, s, K)
                if all((x == 0) if want == 'zero' else (x != 0) for x in v):
                    row.append(j)
            adj.append(row)
        return list(rows), adj

    if kind == 'same':                        # split by the unnamed common value
        groups = {}
        for i, r in enumerate(rows):
            for j, s in enumerate(rows):
                v = set(_rowvals(f, r, s, K))
                if len(v) != 1:
                    continue
                x = v.pop()
                if p['nonzero'] and x == 0:
                    continue
                groups.setdefault(x, []).append((i, j))
        states, index, adj = [], {}, []

        def sid(k):
            i = index.get(k)
            if i is None:
                i = index[k] = len(states)
                states.append(k); adj.append([])
            return i
        for x, pairs in sorted(groups.items()):
            touched = {i for i, _ in pairs} | {j for _, j in pairs}
            if len(states) + len(touched) > cap:
                return None
            for i in touched:
                sid((x, i))
            for i, j in pairs:
                adj[index[(x, i)]].append(index[(x, j)])
        return (states, adj) if states else None

    # the neighbour conditions: a pair of consecutive rows is a state
    vals = {}
    ok = []
    for i, r in enumerate(rows):
        for j, s in enumerate(rows):
            v = _rowvals(f, r, s, K)
            if kind == 'differ' and any(v[t] == v[t + 1] for t in range(K - 1)):
                continue
            if kind == 'mono' and any(v[t] > v[t + 1] for t in range(K - 1)):
                continue
            vals[(i, j)] = v
            ok.append((i, j))
            if len(ok) > cap:
                return None
    if not ok:
        return None
    index = {k: n for n, k in enumerate(ok)}
    nxt = {}
    for (i, j) in ok:
        nxt.setdefault(i, []).append(j)
    adj = []
    for (i, j) in ok:
        u = vals[(i, j)]
        row = []
        for t in nxt.get(j, ()):
            w = vals[(j, t)]
            if kind == 'differ':
                good = all(x != y for x, y in zip(u, w))
            else:
                good = all(x <= y for x, y in zip(u, w))
            if good:
                row.append(index[(j, t)])
        adj.append(row)
    return ok, adj


terms = transfer17.terms
threshold = transfer17.threshold
