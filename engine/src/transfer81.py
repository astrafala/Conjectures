#!/usr/bin/env python3
"""Arrays counted up to renaming, under a condition on every subblock.

    Number of (n+1) X W 0..k arrays with every 2 X 2 subblock having the same number of equal
    diagonal or antidiagonal elements, and new values 0..k introduced in row major order.
    ... with the number of equal 2 X 2 subblock diagonal pairs and equal antidiagonal pairs
    differing from each horizontal or vertical neighbor, and new values ...
    ... with every 2 X 2 subblock in a row having an equal number of equal diagonal or equal
    antidiagonal elements, adjacent rows differing in this number, and new values ...
    ... with every 3 X 3 subblock having three equal elements in a row horizontally,
    vertically, diagonally or antidiagonally exactly two different ways, and new values ...

Two things are happening at once and both go into the state.

The subblock condition is local: a subblock spans h consecutive rows, so carrying the last
h - 1 rows is enough to test every subblock as the row that closes it arrives. Three of the
four conditions also compare a subblock with subblocks BESIDE or ABOVE it, so the state also
carries what the last completed band of subblocks scored -- a tuple for the neighbour
condition, one number for the two conditions that force a band to be constant.

"New values introduced in row major order" is the canonical-form condition: reading the
array in row major order, a value may appear for the first time only when every smaller
value already has. It counts each array once per renaming class rather than once, and it is
NOT a local condition -- but it is a counter condition: all that matters is how many values
have been introduced so far, so one extra component m, bounded by the alphabet, carries it
exactly. A row is admissible from m precisely when each of its entries is at most the
running m, and each entry equal to m raises m by one.

So the state is (the last h - 1 rows, m, what the last band scored) and the walk adds one
row at a time. Nothing about the count is approximated: the digraph is the exact one whose
walks are the arrays being counted.
"""
import re
from itertools import product

import lumpauto
import namecanon
import transfer19

NUM = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6,
       'seven': 7, 'eight': 8, 'nine': 9}

# the four subblock conditions, each with the subblock shape it is stated for
NEIGHBOUR = re.compile(
    r'^the number of equal (\d+) X (\d+) subblock diagonal pairs and equal antidiagonal '
    r'pairs differing from each horizontal or vertical neighbor$', re.I)
BAND = re.compile(
    r'^every (\d+) X (\d+) subblock in a row having an equal number of equal diagonal or '
    r'equal antidiagonal elements, adjacent rows differing in this number$', re.I)
SAME = re.compile(
    r'^every (\d+) X (\d+) subblock having the same number of equal diagonal or '
    r'antidiagonal elements$', re.I)
LINES = re.compile(
    r'^every (\d+) X (\d+) subblock having three equal elements in a row horizontally, '
    r'vertically, diagonally or antidiagonally (exactly|at least) ([a-z]+|\d+) '
    r'different ways$', re.I)

HEAD = re.compile(
    r'^Number of (.+?) 0\.\.(\d+) arrays with (.+?), and new values 0\.\.(\d+) '
    r'introduced in row major order\.?$', re.I)
# (n+a) X W, n X W, W X (n+a), W X n -- the growing side is the one carrying n
SHAPE = [
    (re.compile(r'^\(n\+(\d+)\) X (\d+)$', re.I), 'rows'),
    (re.compile(r'^n X (\d+)$', re.I), 'rows0'),
    (re.compile(r'^(\d+) X \(n\+(\d+)\)$', re.I), 'cols'),
    (re.compile(r'^(\d+) X n$', re.I), 'cols0'),
]


def _num(t):
    t = t.strip().lower()
    return int(t) if t.isdigit() else NUM.get(t)


def _shape(s):
    """(W, a) with the array having n + a rows of W columns, after transposing if needed"""
    for rx, kind in SHAPE:
        m = rx.match(s)
        if not m:
            continue
        if kind == 'rows':
            return int(m.group(2)), int(m.group(1))
        if kind == 'rows0':
            return int(m.group(1)), 0
        if kind == 'cols':
            return int(m.group(1)), int(m.group(2))
        return int(m.group(1)), 0
    return None


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = HEAD.match(nm)
    if not m:
        return None
    if m.group(2) != m.group(4):               # the two alphabets must be the same alphabet
        return None
    sh = _shape(m.group(1).strip())
    if sh is None:
        return None
    W, a = sh
    k = int(m.group(2)) + 1
    if not 2 <= W <= 5 or not 2 <= k <= 5:
        return None
    cond, want, kind = m.group(3).strip(), None, None
    for rx, tag in ((NEIGHBOUR, 'neighbour'), (BAND, 'band'), (SAME, 'same'), (LINES, 'lines')):
        g = rx.match(cond)
        if not g:
            continue
        h, w = int(g.group(1)), int(g.group(2))
        if tag == 'lines':
            if (h, w) != (3, 3):
                return None
            want = _num(g.group(4))
            if want is None:
                return None
            kind = ('lines_exact' if g.group(3).lower() == 'exactly' else 'lines_atleast')
        else:
            if (h, w) != (2, 2):
                return None
            kind = tag
        return {'W': W, 'a': a, 'k': k, 'h': h, 'w': w, 'kind': kind, 'want': want,
                'frac': 1}
    return None


def _rows(W, k):
    return list(product(range(k), repeat=W))


def _advance(m, row, k):
    """the running count of introduced values after this row, or None if the row is not
    admissible: a value may appear only once every smaller value has"""
    for v in row:
        if v > m:
            return None
        if v == m:
            m += 1
    return m if m <= k else None


def _stat2(block, j):
    """a 2 X 2 subblock at column j: equal diagonal pairs plus equal antidiagonal pairs"""
    top, bot = block
    return (top[j] == bot[j + 1]) + (top[j + 1] == bot[j])


THREE = [[(0, 0), (0, 1), (0, 2)], [(1, 0), (1, 1), (1, 2)], [(2, 0), (2, 1), (2, 2)],
         [(0, 0), (1, 0), (2, 0)], [(0, 1), (1, 1), (2, 1)], [(0, 2), (1, 2), (2, 2)],
         [(0, 0), (1, 1), (2, 2)], [(0, 2), (1, 1), (2, 0)]]


def _lines(block, j):
    """how many of the eight lines of a 3 X 3 subblock at column j are constant"""
    return sum(1 for L in THREE
               if len({block[r][j + c] for r, c in L}) == 1)


def build(p, cap=200000):
    W, k, h, w, kind = p['W'], p['k'], p['h'], p['w'], p['kind']
    if w > W:
        return None
    rows = _rows(W, k)
    nb = W - w + 1                              # subblocks across one band

    def band(block):
        """the scores of one band of subblocks, or None if the band is already illegal"""
        if kind.startswith('lines'):
            s = [_lines(block, j) for j in range(nb)]
            good = (all(v == p['want'] for v in s) if kind == 'lines_exact'
                    else all(v >= p['want'] for v in s))
            return () if good else None
        s = [_stat2(block, j) for j in range(nb)]
        if kind == 'neighbour':
            for j in range(nb - 1):
                if s[j] == s[j + 1]:            # a subblock beside it with the same score
                    return None
            return tuple(s)
        if len(set(s)) != 1:                    # band and same both force a constant band
            return None
        return (s[0],)

    index, states, adj = {}, [], []

    def sid(key):
        i = index.get(key)
        if i is None:
            i = index[key] = len(states)
            states.append(key)
            adj.append([])
        return i

    # a state is (the last h - 1 rows, m, the last band's score); the score is () until a
    # band has been completed, and for `same' it is the score every band must have
    frontier, seen = [], set()
    for r in rows:
        m = _advance(0, r, k)
        if m is None:
            continue
        i = sid(((r,), m, ()))
        frontier.append(i)
        seen.add(i)
    if not states:
        return None
    start_states = list(seen)
    while frontier:
        u = frontier.pop()
        last, m, prev = states[u]
        for r in rows:
            m2 = _advance(m, r, k)
            if m2 is None:
                continue
            keep = (last + (r,))[-(h - 1):]
            if len(last) < h - 1:               # not enough rows yet to close a subblock
                cur = prev
            else:
                cur = band(last + (r,))
                if cur is None:
                    continue
                if kind == 'band' and prev and cur[0] == prev[0]:
                    continue                    # adjacent bands must differ in the number
                if kind == 'neighbour' and prev:
                    if any(cur[j] == prev[j] for j in range(nb)):
                        continue                # a subblock above it with the same score
                if kind == 'same' and prev and cur != prev:
                    continue
                if kind.startswith('lines'):
                    cur = ()
            v = sid((keep, m2, cur))
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
