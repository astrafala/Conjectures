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
    """(L, a, transposed): L lines fixed, n + a lines added, and which way round it is

    "W X (n+a)" is NOT the transpose of "(n+a) X W" for these entries and must not be turned
    into one. The conditions are stated about ROWS --- "every subblock in a row", "adjacent
    rows differing", "row major order" --- so transposing the array rewrites the condition
    into a different one. Transposing gave exactly the counts of the other orientation, and
    the six entries where the two orientations disagree failed against the published DATA,
    which is the only reason it was caught.
    """
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
    nm = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = HEAD.match(nm)
    if not m:
        return None
    if m.group(2) != m.group(4):               # the two alphabets must be the same alphabet
        return None
    sh = _shape(m.group(1).strip())
    if sh is None:
        return None
    W, a, tr = sh
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
                'transposed': tr, 'frac': 1}
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
    """The digraph whose walks are the arrays.

    One walk step adds one line: a row when the entry writes "(n+a) X L", a column when it
    writes "L X (n+a)". A subblock spans `dep` added lines and `spn` fixed positions, which
    are (h, w) one way round and (w, h) the other, so one step closes `nb = L - spn + 1`
    subblocks.

    Where the two orientations really differ is what a step closes. Adding a row closes one
    whole band of subblocks; adding a column closes one subblock from each of nb different
    bands. The conditions that speak of bands ("every subblock in a row scores the same,
    adjacent rows differ") therefore need the established score of every band carried at
    once in the column orientation, and only the last band's score in the row orientation.

    The canonical condition is read along the walk: first occurrences in the order the walk
    visits the cells. In the row orientation that is the entry's own row major order. In the
    column orientation it is column major order, which selects a DIFFERENT representative of
    each renaming class but exactly one of them, just as row major order does --- and every
    condition here is a statement about which entries are equal, so it is invariant under
    renaming. The two rules therefore count the same classes, and the count is the same.
    """
    L, k, h, w, kind = p['W'], p['k'], p['h'], p['w'], p['kind']
    tr = p.get('transposed', False)
    dep, spn = (w, h) if tr else (h, w)
    if spn > L:
        return None
    lines = _rows(L, k)
    nb = L - spn + 1

    def scores(win):
        """the score of each subblock closed by this window, in band order"""
        if kind.startswith('lines'):
            blk = [[win[c][r + i] for i in range(3)] for c in range(3)] if tr else win
            out = []
            for j in range(nb):
                b = ([[win[c][j + i] for i in range(3)] for c in range(3)] if tr
                     else [win[c] for c in range(3)])
                out.append(_lines(b, 0) if tr else _lines(win, j))
            return out
        if tr:
            # a 2 X 2 subblock at row j, spanning the two columns in the window
            c0, c1 = win
            return [(c0[j] == c1[j + 1]) + (c0[j + 1] == c1[j]) for j in range(nb)]
        return [_stat2(win, j) for j in range(nb)]

    def check(s, est):
        """(admissible, the new established value) for one window's scores"""
        if kind.startswith('lines'):
            good = (all(v == p['want'] for v in s) if kind == 'lines_exact'
                    else all(v >= p['want'] for v in s))
            return good, ()
        if kind == 'neighbour':
            # a subblock may not score what the subblock beside it scores, which within one
            # step is the neighbour along the fixed axis, nor what the subblock before it
            # scores, which is the same position at the previous step
            for j in range(nb - 1):
                if s[j] == s[j + 1]:
                    return False, None
            if est and any(s[j] == est[j] for j in range(nb)):
                return False, None
            return True, tuple(s)
        if kind == 'same':
            if len(set(s)) != 1:
                return False, None
            if est and est[0] != s[0]:
                return False, None
            return True, (s[0],)
        # kind == 'band'
        if not tr:
            if len(set(s)) != 1:
                return False, None
            if est and est[0] == s[0]:
                return False, None
            return True, (s[0],)
        # one subblock from each band: fix each band's score, then adjacent bands must differ
        cur = list(est) if est else [None] * nb
        for j in range(nb):
            if cur[j] is None:
                cur[j] = s[j]
            elif cur[j] != s[j]:
                return False, None
        for j in range(nb - 1):
            if cur[j] is not None and cur[j + 1] is not None and cur[j] == cur[j + 1]:
                return False, None
        return True, tuple(cur)

    index, states, adj = {}, [], []

    def sid(key):
        i = index.get(key)
        if i is None:
            i = index[key] = len(states)
            states.append(key)
            adj.append([])
        return i

    frontier, seen = [], set()
    for r in lines:
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
        last, m, est = states[u]
        for r in lines:
            m2 = _advance(m, r, k)
            if m2 is None:
                continue
            keep = (last + (r,))[-(dep - 1):] if dep > 1 else ()
            if len(last) < dep - 1:
                cur = est
            else:
                good, cur = check(scores(last + (r,)), est)
                if not good:
                    continue
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
