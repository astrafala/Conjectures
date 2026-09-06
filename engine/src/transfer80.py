#!/usr/bin/env python3
"""Lower triangles over 0..n under a BOUNDED DIFFERENCE condition: eventually linear.

    Number of lower triangles of a K X K 0..n array with each element differing from all of
    its <directions> neighbors by <d>[ or less].
    Number of lower triangles of a K X K 0..n array with no element differing from any of its
    <directions> neighbors by more than <d>.

The shape is fixed and the alphabet 0..n is what grows, so there is no digraph to walk. What
makes these tractable is that the condition constrains DIFFERENCES only. Write x = m + y with
m the least entry, so y >= 0 with least entry 0; then y satisfies exactly the same condition,
and x lies in {0..n} precisely when 0 <= m <= n - spread(y). So

    a(n) = sum over difference patterns y of max(0, n + 1 - spread(y)),

a sum of finitely many terms, and for n at least the largest spread every term is positive and

    a(n) = N*(n+1) - sum of spreads = N*n + C,

LINEAR, which is the shape every conjecture in this family has.

The largest spread is bounded without being computed: any two cells are joined by a path of at
most D edges, D the diameter of the neighbour graph, and each edge moves the value by at most
d, so spread <= d*D. Evaluating a(n) at n = d*D and n = d*D + 1 therefore pins N and C exactly,
and the identity holds for every n >= d*D. Nothing is fitted and nothing is extrapolated.

a(n) itself is counted by a frontier walk over the cells in row major order: a cell's value has
to be remembered only until the last of its neighbours is placed, which for this shape is at
most K+1 cells later.
"""
import re
import collections

import namecanon

CLASS = {'horizontal': (0, 1), 'vertical': (1, 0),
         'diagonal': (1, 1), 'antidiagonal': (1, -1)}
NUM = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5}
_W1 = r'(?:horizontal|vertical|diagonal|antidiagonal)'
NBSET = r'((?:' + _W1 + r')(?:[, ]+(?:or |and )?(?:' + _W1 + r'))*)'

EXACT = re.compile(r'^Number of lower triangles of a (\d+)\s*X\s*(\d+) 0\.\.n array with each '
                   r'element differing from all of its ' + NBSET +
                   r' neighbors by ([a-z]+|\d+)(\s+or less)?\s*\.?\s*$', re.I)
NOMORE = re.compile(r'^Number of lower triangles of a (\d+)\s*X\s*(\d+) 0\.\.n array with no '
                    r'element differing from any of its ' + NBSET +
                    r' neighbors by more than ([a-z]+|\d+)\s*\.?\s*$', re.I)


def _num(t):
    t = t.strip().lower()
    return int(t) if t.isdigit() else NUM.get(t)


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn])\s*[xX]\s*(?=[\dn])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = EXACT.match(nm)
    if m:
        # group 3 is the direction list, 4 the number, 5 the optional " or less"
        kind = 'atmost' if m.group(5) else 'exact'
    else:
        m = NOMORE.match(nm)
        if not m:
            return None
        kind = 'atmost'
    K = int(m.group(1))
    if int(m.group(2)) != K or K < 2:
        return None
    d = _num(m.group(4))
    if d is None or d < 1:
        return None
    dirs = sorted({CLASS[w] for w in re.findall(_W1, m.group(3).lower())})
    if not dirs:
        return None
    return {'K': K, 'd': d, 'kind': kind, 'dirs': [list(t) for t in dirs], 'frac': 1}


def cells(K):
    return [(i, j) for i in range(K) for j in range(i + 1)]


def edges(K, dirs):
    C = set(cells(K))
    E = []
    for (i, j) in cells(K):
        for (di, dj) in dirs:
            t = (i + di, j + dj)
            if t in C:
                E.append(((i, j), t))
    return E


def diameter(K, dirs):
    C = cells(K)
    adj = collections.defaultdict(list)
    for u, v in edges(K, dirs):
        adj[u].append(v)
        adj[v].append(u)
    best = 0
    for s in C:
        seen = {s: 0}
        q = [s]
        while q:
            nq = []
            for u in q:
                for v in adj[u]:
                    if v not in seen:
                        seen[v] = seen[u] + 1
                        nq.append(v)
            q = nq
        if len(seen) < len(C):
            return None                      # disconnected: the bound below does not apply
        best = max(best, max(seen.values()))
    return best


def count(p, n):
    """a(n), by a frontier walk over the cells in row major order."""
    K, d, kind = p['K'], p['d'], p['kind']
    dirs = [tuple(t) for t in p['dirs']]
    C = cells(K)
    pos = {c: i for i, c in enumerate(C)}
    nb = collections.defaultdict(list)
    for u, v in edges(K, dirs):
        nb[v].append(u)                      # v is placed after u in row major order
    # how far back a value must be remembered
    W = max((pos[c] - min(pos[u] for u in nb[c]) for c in C if nb[c]), default=0) + 1

    def ok(a, b):
        t = abs(a - b)
        return t <= d if kind == 'atmost' else t == d

    state = {(): 1}
    for c in C:
        nxt = collections.defaultdict(int)
        back = [pos[c] - pos[u] for u in nb[c]]
        for st, w in state.items():
            for v in range(n + 1):
                good = True
                for b in back:
                    if not ok(st[len(st) - b], v):
                        good = False
                        break
                if good:
                    nxt[(st + (v,))[-W:]] += w
        state = nxt
        if not state:
            return 0
    return sum(state.values())


def build(p, cap=None):
    D = diameter(p['K'], [tuple(t) for t in p['dirs']])
    if D is None:
        return None
    return {'p': p, 'D': D, 'bound': p['d'] * D}


def line(b):
    """(N, C) with a(n) = N*n + C for every n >= bound, computed and not fitted."""
    t = b['bound']
    a1 = count(b['p'], t)
    a2 = count(b['p'], t + 1)
    N = a2 - a1
    return N, a1 - N * t


def terms(b, N, off=1):
    return [count(b['p'], off + k) for k in range(N + 1)]
