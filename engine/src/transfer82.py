#!/usr/bin/env python3
"""Arrays under a condition on every subblock, or on every pair of neighbouring subblocks.

    Number of n X 3 binary matrices with no 2 X 2 block having four 1's.
    Number of (n+2) X 4 binary matrices with every 3 X 3 block having exactly four 1's.
    T(n,k) = number of (n+1) X (k+1) 0..2 arrays with every 2 X 2 subblock summing to 4.
    Number of (n+1) X 4 0..2 arrays with each element of every 2 X 2 subblock being the sum
        mod 3 of two others.
    1/16 the number of (n+1) X 3 binary arrays with no 2 X 2 subblock being a reflection
        across the shared element pair of any horizontal or vertical neighbour.

Every condition here is decided by a bounded window of consecutive lines: a subblock spanning
h lines needs h of them, and a condition relating a subblock to the one below it needs h + 1.
So the admissible windows are the vertices of a finite digraph, the arrays are its walks, and
the count is C-finite.

Two things are deliberately not assumed. The array is never transposed: "L X (n+a)" grows
along its columns and "(n+a) X L" along its rows, and the conditions stay where the entry puts
them. And the leading "1/16 the number of" is carried as a denominator rather than ignored,
because the entry's own terms are the scaled ones.
"""
import re
from itertools import product

import lumpauto
import namecanon
import transfer19

NUM = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6,
       'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10}

HEAD = re.compile(
    r'^(?:1/(\d+) the number of|Number of|number of)\s+(.+?)\s+'
    r'(binary|0\.\.(\d+))\s+(?:arrays|matrices)\s+with\s+(.+?)\s*\.?\s*$', re.I)
# the fixed dimension may arrive parenthesised: specialising a table's "(n+1) X (k+1)" to
# k = 2 leaves "(n+1) X (3)", and requiring a bare digit there hid the whole table family
SHAPE = [
    (re.compile(r'^\(n\+(\d+)\) X \(?(\d+)\)?$', re.I), 'rows'),
    (re.compile(r'^n X \(?(\d+)\)?$', re.I), 'rows0'),
    (re.compile(r'^\(?(\d+)\)? X \(n\+(\d+)\)$', re.I), 'cols'),
    (re.compile(r'^\(?(\d+)\)? X n$', re.I), 'cols0'),
]
CLAUSE = [
    ('sum', re.compile(r'^every (\d+) X (\d+) (?:sub)?block summing to (\d+)$', re.I)),
    ('ones_eq', re.compile(r"^every (\d+) X (\d+) (?:sub)?block having exactly "
                           r"([a-z]+|\d+) 1'?s$", re.I)),
    ('ones_ne', re.compile(r"^no (\d+) X (\d+) (?:sub)?block having ([a-z]+|\d+) 1'?s$",
                           re.I)),
    ('summod', re.compile(r'^each element of every (\d+) X (\d+) (?:sub)?block being the '
                          r'sum mod (\d+) of two others$', re.I)),
    ('reflect', re.compile(r'^no (\d+) X (\d+) (?:sub)?block being a reflection across the '
                           r'shared element pair of any horizontal or vertical neighbou?r$',
                           re.I)),
]


def _num(t):
    t = t.strip().lower()
    return int(t) if t.isdigit() else NUM.get(t)


def _shape(s):
    for rx, kind in SHAPE:
        m = rx.match(s)
        if not m:
            continue
        if kind == 'rows':
            return int(m.group(2)), int(m.group(1)), False
        if kind == 'rows0':
            return int(m.group(1)), 0, False
        if kind == 'cols':
            return int(m.group(1)), int(m.group(2)), True
        return int(m.group(1)), 0, True
    return None


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'^T\(n,\s*k\)\s*=\s*', '', re.sub(r'\s+', ' ', nm)).strip()
    nm = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', nm)
    m = HEAD.match(nm)
    if not m:
        return None
    frac = int(m.group(1)) if m.group(1) else 1
    sh = _shape(m.group(2).strip())
    if sh is None:
        return None
    L, a, tr = sh
    k = 2 if m.group(3).lower() == 'binary' else int(m.group(4)) + 1
    # A fixed bound on the width and the alphabet is a wall, and the standing rule is that
    # a cap is a setting. The real limit is the state space, which `build` measures against
    # the cap it is given; refusing "n X 7 binary matrices" here left three whole families
    # unasked while their models fit in sixteen thousand states.
    if not 1 <= L <= 14 or not 2 <= k <= 8:
        return None
    cond = m.group(5).strip()
    for kind, rx in CLAUSE:
        g = rx.match(cond)
        if not g:
            continue
        h, w = int(g.group(1)), int(g.group(2))
        if not 2 <= h <= 3 or not 2 <= w <= 3:
            return None
        val = _num(g.group(3)) if g.lastindex >= 3 else None
        if kind in ('sum', 'ones_eq', 'ones_ne', 'summod') and val is None:
            return None
        if kind == 'reflect' and (h, w) != (2, 2):
            return None                     # the shared pair is one line only for 2 X 2
        return {'L': L, 'a': a, 'k': k, 'h': h, 'w': w, 'kind': kind, 'val': val,
                'transposed': tr, 'frac': frac}
    return None


def _ok_block(b, kind, val, k):
    flat = [x for row in b for x in row]
    if kind == 'sum':
        return sum(flat) == val
    if kind == 'ones_eq':
        return flat.count(1) == val
    if kind == 'ones_ne':
        return flat.count(1) != val
    if kind == 'summod':
        for t in range(len(flat)):
            rest = flat[:t] + flat[t + 1:]
            if not any((rest[p] + rest[q]) % val == flat[t]
                       for p in range(len(rest)) for q in range(p + 1, len(rest))):
                return False
        return True
    return True


def build(p, cap=200000):
    L, k, h, w, kind = p['L'], p['k'], p['h'], p['w'], p['kind']
    tr = p.get('transposed', False)
    dep, spn = (w, h) if tr else (h, w)
    # a condition relating a block to the block below it needs one more line than the block
    pair = kind == 'reflect'
    dep = dep + 1 if pair else dep
    if spn > L:
        return None
    if k ** L > 4 * cap:
        return None
    lines = list(product(range(k), repeat=L))
    nb = L - spn + 1

    def blk(win, t, j):
        """the subblock starting at window line t and fixed offset j, as rows"""
        if tr:
            return [[win[t + c][j + r] for c in range(w)] for r in range(h)]
        return [[win[t + r][j + c] for c in range(w)] for r in range(h)]

    def mirror_across(A, B):
        """B sits one step along the FIXED axis from A, sharing a line with it"""
        return (B[1] == A[0]) if tr else (B[0][1] == A[0][0] and B[1][1] == A[1][0])

    def mirror_along(A, B):
        """B sits one step along the WALK direction from A, sharing a line with it"""
        return (B[0][1] == A[0][0] and B[1][1] == A[1][0]) if tr else (B[1] == A[0])

    base = dep - 1 if pair else dep          # lines a single block needs

    def ok(win):
        """every constraint the last line of this window completes

        The across-axis constraints are decided as soon as one band exists, so they must be
        tested on a window of `base` lines. Testing them only once a second band had arrived
        left every two-row array unconstrained, and the model then counted every array.
        """
        if len(win) < base:
            return True
        if not pair:
            return all(_ok_block(blk(win, len(win) - base, j), kind, p['val'], k)
                       for j in range(nb))
        t = len(win) - base
        for j in range(nb - 1):
            if mirror_across(blk(win, t, j), blk(win, t, j + 1)):
                return False
        if len(win) >= base + 1:
            for j in range(nb):
                if mirror_along(blk(win, t - 1, j), blk(win, t, j)):
                    return False
        return True

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
    start_states = list(seen)
    while frontier:
        u = frontier.pop()
        last = states[u]
        for r in lines:
            win = last + (r,)
            if not ok(win[-dep:]):
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
    for i in start_states:
        start[i] = 1
    end = [1] * S
    return lumpauto.lump(adj, start, end)


terms = transfer19.terms
