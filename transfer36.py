#!/usr/bin/env python3
"""Edge counts on the 2 X 2 subblocks: clockwise increases, and its relatives.

The four cells of a subblock $\\begin{pmatrix}p&q\\\\r&s\\end{pmatrix}$ carry four perimeter
edges. Going CLOCKWISE they are $p\\to q\\to s\\to r\\to p$, and the ``number of clockwise edge
increases'' is how many of those four steps go up in value; counterclockwise is the same cycle
the other way, $p\\to r\\to s\\to q\\to p$. ``Rightwards and downwards edge increases'' counts
instead the four directed edges $p\\to q$, $r\\to s$, $p\\to r$, $q\\to s$, and ``equal edges''
counts the perimeter edges whose two cells agree.

Those readings are not guesses. Over $0..1$ the $2\\times3$ arrays whose two subblocks have
equal clockwise counts number $40$, over $0..2$ the $2\\times2$ arrays with clockwise count $2$
number $30$, and the $3\\times2$ binary arrays whose two subblocks have unequal
rightwards-and-downwards counts number $40$ --- the three numbers the corresponding entries
publish.

Name shapes covered, for an $(n+1)\\times W$ array over $\\{0,\\dots,m\\}$:

    the number of <edge count> in every 2 X 2 subblock equal to <k>
        [, and every 2 X 2 determinant nonzero]
    the number of <edge count> in every 2 X 2 subblock the same
    the number of <edge count> in every 2 X 2 subblock unequal to the number of <edge count>
    the number of <edge count> in each 2 X 2 subblock equal to the number in all its
        horizontal and vertical neighbors
    the number of <edge count> in every/each 2 X 2 subblock differing from
        (each horizontal or vertical neighbor | the number in all its horizontal and vertical
        neighbors)

A condition on one subblock at a time makes a single array row a state; a condition relating
NEIGHBOURING subblocks makes it the pair of consecutive rows, since a subblock needs two rows
and the vertical comparison needs the two subblock rows that three rows produce.
"""
import re
from itertools import product

import namecanon
import transfer17

EDGE = r'(clockwise edge increases|counterclockwise edge increases|' \
       r'rightwards and downwards edge increases|equal edges)'
NUM = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4}


def _cw(b):
    p, q, r, s = b
    seq = (p, q, s, r, p)
    return sum(1 for i in range(4) if seq[i] < seq[i + 1])


def _ccw(b):
    p, q, r, s = b
    seq = (p, r, s, q, p)
    return sum(1 for i in range(4) if seq[i] < seq[i + 1])


def _rd(b):
    p, q, r, s = b
    return sum(1 for x, y in ((p, q), (r, s), (p, r), (q, s)) if x < y)


def _eq(b):
    p, q, r, s = b
    return sum(1 for x, y in ((p, q), (q, s), (s, r), (r, p)) if x == y)


STAT = {'clockwise edge increases': _cw, 'counterclockwise edge increases': _ccw,
        'rightwards and downwards edge increases': _rd, 'equal edges': _eq}

HEAD = re.compile(r'Number of \(\s*n\s*\+\s*1\s*\)\s*X\s*(\d+)\s*'
                  r'(?:0\.\.(\d+)|(binary))\s+arrays\s+with\s+(.*?)\s*\.?\s*$', re.I)

B = r'2\s*X\s*2 subblock'
P1 = re.compile(r'the number of ' + EDGE + r' in every ' + B + r' equal to (\w+)'
                r'(, and every 2\s*X\s*2 determinant nonzero)?$', re.I)
P2 = re.compile(r'the number of ' + EDGE + r' in every ' + B + r' the same$', re.I)
P3 = re.compile(r'the number of ' + EDGE + r' in every ' + B + r' unequal to the number of '
                + EDGE + r'$', re.I)
P4 = re.compile(r'the number of ' + EDGE + r' in each ' + B + r' equal to the number in '
                r'all its horizontal and vertical neighbors$', re.I)
P5 = re.compile(r'the number of ' + EDGE + r' in (?:each|every) ' + B + r' differing from '
                r'(?:each horizontal or vertical neighbor|the number in (?:all|each of) its '
                r'horizontal and vertical neighbors)$', re.I)


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
    base = {'W': W, 'alpha': alpha, 'frac': 1, 'det': False}
    c = P1.match(body)
    if c:
        g = c.group(2).lower()
        k = NUM.get(g) if not g.isdigit() else int(g)
        if k is None:
            return None
        base.update(kind='fixed', stat=c.group(1).lower(), value=k, det=bool(c.group(3)))
        return base
    c = P2.match(body)
    if c:
        base.update(kind='same', stat=c.group(1).lower())
        return base
    c = P3.match(body)
    if c:
        if c.group(1).lower() == c.group(2).lower():
            return None
        base.update(kind='twostat', stat=c.group(1).lower(), stat2=c.group(2).lower())
        return base
    c = P4.match(body)
    if c:
        base.update(kind='nbequal', stat=c.group(1).lower())
        return base
    c = P5.match(body)
    if c:
        base.update(kind='nbdiffer', stat=c.group(1).lower())
        return base
    return None


def build(p, cap=40000):
    W, A, kind = p['W'], p['alpha'] + 1, p['kind']
    f = STAT[p['stat']]
    K = W - 1
    if A ** W > 4 * cap:
        return None
    rows = list(product(range(A), repeat=W))

    def blocks(r, s):
        return [(r[j], r[j + 1], s[j], s[j + 1]) for j in range(K)]

    if kind in ('fixed', 'twostat'):
        if kind == 'twostat':
            g = STAT[p['stat2']]
            ok = lambda b: f(b) != g(b)
        else:
            v, det = p['value'], p['det']
            def ok(b):
                if f(b) != v:
                    return False
                return not det or (b[0] * b[3] - b[1] * b[2]) != 0
        adj = []
        for r in rows:
            adj.append([j for j, s in enumerate(rows) if all(ok(b) for b in blocks(r, s))])
        return list(rows), adj

    if kind == 'same':
        groups = {}
        for i, r in enumerate(rows):
            for j, s in enumerate(rows):
                v = {f(b) for b in blocks(r, s)}
                if len(v) == 1:
                    groups.setdefault(v.pop(), []).append((i, j))
        states, index, adj = [], {}, []

        def sid(k):
            t = index.get(k)
            if t is None:
                t = index[k] = len(states)
                states.append(k); adj.append([])
            return t
        for x, pairs in sorted(groups.items()):
            touched = {i for i, _ in pairs} | {j for _, j in pairs}
            if len(states) + len(touched) > cap:
                return None
            for i in touched:
                sid((x, i))
            for i, j in pairs:
                adj[index[(x, i)]].append(index[(x, j)])
        return (states, adj) if states else None

    want = (kind == 'nbequal')
    vals, ok = {}, []
    for i, r in enumerate(rows):
        for j, s in enumerate(rows):
            v = tuple(f(b) for b in blocks(r, s))
            if any((v[t] == v[t + 1]) != want for t in range(K - 1)):
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
        adj.append([index[(j, t)] for t in nxt.get(j, ())
                    if all((x == y) == want for x, y in zip(u, vals[(j, t)]))])
    return ok, adj


terms = transfer17.terms
threshold = transfer17.threshold
