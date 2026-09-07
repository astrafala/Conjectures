#!/usr/bin/env python3
"""Conditions on the multiset of every subblock.

    Number of (n+1) X (2+1) 0..3 arrays with the upper median equal to the lower median in
        every 2 X 2 subblock.
    1/120 the number of (n+1) X 5 0..4 arrays with every 2 X 2 subblock containing four
        distinct values.
    1/6 the number of (n+1) X 3 0..2 arrays with every 2 X 2 subblock containing all three
        values.
    Half the number of (n+1) X 4 binary arrays with no 2 X 2 subblock containing exactly
        one 1.
    Number of (n+1) X 3 binary arrays with no 2 X 2 subblock containing fewer than two 1s.
    1/36 the number of (n+2) X 6 0..2 arrays with each 3 X 3 subblock containing two of one
        value, two of another, and five of the last.

What these share is that the condition on a subblock depends only on which values it holds
and how many times --- not on where in the block they sit. How many distinct values, how many
ones, whether the two middle order statistics agree, what the multiset of multiplicities is:
each is a function of the multiset alone. That is why one predicate table serves all of them.

The medians are the order statistics of the block read as a multiset: for a 2 X 2 block with
entries sorted $v_0\\le v_1\\le v_2\\le v_3$, the lower median is $v_1$ and the upper median
is $v_2$, and they are equal exactly when the two middle values agree.

A block spanning h lines is decided by h consecutive lines, so the state is the h-1 lines
before the current one and the arrays are the walks of a finite digraph.

The leading fraction is carried as a denominator rather than ignored, because the entry's own
terms are the scaled ones: 1/120 of the 0..4 arrays, half of the binary ones, and so on.
"""
import re
from itertools import product

import lumpauto
import namecanon
import transfer19

NUM = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7,
       'eight': 8, 'nine': 9, 'ten': 10}
FRAC = {'half': 2, 'one third': 3, 'one quarter': 4, 'one sixth': 6}

HEAD = re.compile(
    r'^(?:(1/(\d+)|Half|One third|One quarter|One sixth) the number of|Number of|number of)'
    r'\s+(.+?)\s+(binary|(\d+)\.\.(\d+))\s+(?:arrays|matrices)\s+with\s+(.+?)\s*\.?\s*$',
    re.I)
DIM = r'(?:\((\d+)\+(\d+)\)|\(?(\d+)\)?)'
SHAPE = [
    (re.compile(r'^\(n\+(\d+)\) X ' + DIM + r'$', re.I), 'rows'),
    (re.compile(r'^n X ' + DIM + r'$', re.I), 'rows0'),
    (re.compile(r'^' + DIM + r' X \(n\+(\d+)\)$', re.I), 'cols'),
    (re.compile(r'^' + DIM + r' X n$', re.I), 'cols0'),
]
BLK = r'(\d+) X (\d+) (?:sub)?block'
CLAUSE = [
    ('median', re.compile(r'^the upper median (equal|unequal) to the lower median in every '
                          + BLK + r'$', re.I)),
    ('distinct', re.compile(r'^every ' + BLK + r' containing (?:exactly )?([a-z]+|\d+) '
                            r'distinct values$', re.I)),
    ('allvals', re.compile(r'^every ' + BLK + r' containing all ([a-z]+|\d+) values$', re.I)),
    ('ones_ne', re.compile(r"^no " + BLK + r" containing exactly ([a-z]+|\d+) 1'?s?$", re.I)),
    ('ones_ge', re.compile(r"^no " + BLK + r" containing fewer than ([a-z]+|\d+) 1'?s?$",
                           re.I)),
    ('multi', re.compile(r'^each ' + BLK + r' containing ([a-z]+|\d+) of one value, '
                         r'([a-z]+|\d+) of another,? and ([a-z]+|\d+) of the last$', re.I)),
]


def _num(t):
    t = t.strip().lower()
    return int(t) if t.isdigit() else NUM.get(t)


def _dim(a, b, c):
    return int(c) if c else int(a) + int(b)


def _shape(s):
    for rx, kind in SHAPE:
        m = rx.match(s)
        if not m:
            continue
        g = m.groups()
        if kind == 'rows':
            return _dim(g[1], g[2], g[3]), int(g[0]), False
        if kind == 'rows0':
            return _dim(g[0], g[1], g[2]), 0, False
        if kind == 'cols':
            return _dim(g[0], g[1], g[2]), int(g[3]), True
        return _dim(g[0], g[1], g[2]), 0, True
    return None


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'^T\(n,\s*k\)\s*=\s*', '', re.sub(r'\s+', ' ', nm)).strip()
    nm = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', nm)
    m = HEAD.match(nm)
    if not m:
        return None
    frac = 1
    if m.group(1):
        frac = int(m.group(2)) if m.group(2) else FRAC[m.group(1).lower()]
    sh = _shape(m.group(3).strip())
    if sh is None:
        return None
    L, a, tr = sh
    k = 2 if m.group(4).lower() == 'binary' else int(m.group(6)) + 1
    cond = m.group(7).strip()
    for kind, rx in CLAUSE:
        g = rx.match(cond)
        if not g:
            continue
        if kind == 'median':
            rel, h, w = g.group(1).lower(), int(g.group(2)), int(g.group(3))
            val = None
        else:
            rel = None
            h, w = int(g.group(1)), int(g.group(2))
            if kind == 'multi':
                val = sorted(_num(g.group(i)) for i in (3, 4, 5))
                if None in val:
                    return None
            else:
                val = _num(g.group(3))
                if val is None:
                    return None
        if not 2 <= h <= 3 or not 2 <= w <= 3:
            return None
        if kind == 'median' and (h * w) % 2:
            return None            # an odd block has one median, not two
        if kind == 'multi' and sum(val) != h * w:
            return None
        if not 1 <= L <= 12 or not 2 <= k <= 6:
            return None
        return {'L': L, 'a': a, 'k': k, 'h': h, 'w': w, 'kind': kind, 'val': val,
                'rel': rel, 'transposed': tr, 'frac': frac}
    return None


def _ok_block(flat, p):
    kind, val = p['kind'], p['val']
    if kind == 'median':
        s = sorted(flat)
        mid = len(s) // 2
        return (s[mid - 1] == s[mid]) if p['rel'] == 'equal' else (s[mid - 1] != s[mid])
    if kind in ('distinct', 'allvals'):
        return len(set(flat)) == val
    if kind == 'ones_ne':
        return flat.count(1) != val
    if kind == 'ones_ge':
        return flat.count(1) >= val
    counts = sorted(flat.count(v) for v in set(flat))
    return counts == val                      # 'multi'


def build(p, cap=200000):
    L, k, h, w = p['L'], p['k'], p['h'], p['w']
    tr = p.get('transposed', False)
    dep, spn = (w, h) if tr else (h, w)       # lines the block needs, cells across it
    if spn > L or k ** L > 4 * cap:
        return None
    lines = list(product(range(k), repeat=L))
    nb = L - spn + 1

    def flat(win, j):
        if tr:
            return [win[c][j + r] for r in range(h) for c in range(w)]
        return [win[r][j + c] for r in range(h) for c in range(w)]

    def ok(win):
        if len(win) < dep:
            return True
        return all(_ok_block(flat(win[-dep:], j), p) for j in range(nb))

    index, states, adj = {}, [], []

    def sid(key):
        i = index.get(key)
        if i is None:
            i = index[key] = len(states)
            states.append(key)
            adj.append([])
        return i

    frontier = [sid((r,)) for r in lines]
    seen = set(frontier)
    starts = list(seen)
    while frontier:
        u = frontier.pop()
        last = states[u]
        for r in lines:
            win = last + (r,)
            if not ok(win):
                continue
            v = sid(win[-(dep - 1):] if dep > 1 else ())
            if len(states) > cap:
                return None
            adj[u].append(v)
            if v not in seen:
                seen.add(v)
                frontier.append(v)
    S = len(states)
    start = [0] * S
    for i in starts:
        start[i] = 1
    end = [1] * S           # every block is judged when its last line arrives
    return lumpauto.lump(adj, start, end)


terms = transfer19.terms
