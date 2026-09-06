#!/usr/bin/env python3
"""`Number of n X W 0..m arrays with every element both >= and <= some horizontal or
antidiagonal neighbor', and the rest of the family in which a cell demands that SOME neighbour
of it look a certain way.

The offsets are the usual ones, both ways round:

    horizontal (0,-1),(0,1)     vertical (-1,0),(1,0)     diagonal (-1,-1),(1,1)
    antidiagonal (-1,1),(1,-1)  king-move all eight

and one wording names three single directions outright, `NW, E or S' --- the offsets
(-1,-1), (0,1), (1,0), a set carried to itself by transposing the array.

Seven statements are read:

    every nonzero cell has a neighbour at least as large as itself;
    every cell has a neighbour at least as large AND one at most as large;
    every cell has neighbours equal to both of two named values;
    every cell of one named value has a neighbour of another named value;
    every cell of one named value has an allowed NUMBER of neighbours of another;
    every cell is equal to at least one of its neighbours;
    every cell has among its neighbours each of its own value plus and minus one that is still
        in range, sometimes with no neighbour equal to it.

Each is a statement about one cell and the cells at a fixed set of offsets, so it reaches U rows
up and D rows down and is settled by a window of U+D+1 consecutive rows. The state is the last
U+D of them; a step settles the row that the new row completes; and the last D rows of a
finished array are still untested when the walk stops, so the end vector is the indicator of the
states whose remaining rows pass with nothing below them.

Two entries add that one value is introduced before another in reading order. That is one more
symbol in the state --- which of the two has been seen first, or neither yet --- and it never
goes back.
"""
import re
from itertools import product

import namecanon
import transfer19

ROWMAX = 300000

FRAC = re.compile(r'^\s*(?:(Half)|One quarter|1/(\d+))\s+the number of\s+', re.I)
HEAD = re.compile(r'^\s*Number of\s+', re.I)
DIM = r'(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))'
SHAPE = re.compile(r'^' + DIM + r'\s*X\s*' + DIM +
                   r'\s+(?:(0)\.\.(\d+)|(binary))\s+arrays?\s+with\s+', re.I)

BOTH = {'horizontal': [(0, -1), (0, 1)], 'vertical': [(-1, 0), (1, 0)],
        'diagonal': [(-1, -1), (1, 1)], 'antidiagonal': [(-1, 1), (1, -1)],
        'king-move': [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if (a, b) != (0, 0)]}
DIRW = re.compile(r'\b(antidiagonal|diagonal|horizontal|vertical|king-move)(?:ly)?\b',
                  re.I)
NWES = [(-1, -1), (0, 1), (1, 0)]

LESOME = re.compile(r'^every nonzero element less than or equal to some NW, E or S '
                    r'neighbou?r\s*\.?$', re.I)
GELE = re.compile(r'^every element both >= and <= some (.+?) neighbou?r\s*\.?$', re.I)
BOTH01 = re.compile(r'^every element neighbou?ring (.+?) both a (\d+) and a (\d+)'
                    r'(?:, and (\d+) introduced before (\d+) in row major order)?\s*\.?$', re.I)
NBRSOME = re.compile(r'^every (\d+) an? (.+?) neighbou?r to some (\d+)\s*\.?$', re.I)
ADJCNT = re.compile(r"^every (\d+) (.+?) adjacent to (\d+) or (\d+) neighbou?ring (\d+)'s\s*\.?$",
                    re.I)
EQONE = re.compile(r'^each element equal to at least one neighbou?r\s*\.?$', re.I)
# "every one adjacent to another one horizontally or vertically" says the same thing as
# "every 1 a horizontal or vertical neighbor to some 1", which NBRSOME already reads -- only
# the wording differs, and thirteen binary entries sat outside every engine because of it.
ONEADJ = re.compile(r'^every one adjacent to another one (.+?)\s*\.?$', re.I)
PLUSMINUS = re.compile(r'^every element next to itself plus and minus one within the range '
                       r'0\.\.(\d+) (.+?)\s*\.?$', re.I)
NOEQ = ', with no adjacent elements equal'


def _dirs(txt):
    ws = [w.lower() for w in dict.fromkeys(DIRW.findall(txt))]   # `-ly' forms too
    if not ws:
        return None
    out = []
    for w in ws:
        out += BOTH[w]
    return out


def parse_name(nm):
    nm = namecanon.canon(nm)
    s = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    frac = 1
    m = FRAC.match(s)
    if m:
        frac = 2 if m.group(1) else (4 if m.group(0).lower().startswith('one quarter')
                                     else int(m.group(2)))
        s = s[m.end():]
    else:
        m = HEAD.match(s)
        if not m:
            return None
        s = s[m.end():]
    m = SHAPE.match(s)
    if not m:
        return None
    rows = m.group(1) or m.group(3)
    cols = m.group(4) or m.group(6)
    if rows is None or cols is None or (rows == 'n') == (cols == 'n'):
        return None
    if rows == 'n':
        W, trans = int(cols) + int(m.group(5) or 0), False
    else:
        W, trans = int(rows) + int(m.group(2) or 0), True
    alpha = 1 if m.group(9) else int(m.group(8))
    body = s[m.end():].strip()

    p = {'W': W, 'alpha': alpha, 'trans': trans, 'frac': frac, 'noeq': False,
         'v': None, 'w': None, 'counts': None, 'before': None}
    mm = LESOME.match(body)
    if mm:
        p['kind'], p['offs'] = 'lesome', list(NWES)
        return _fin(p)
    mm = GELE.match(body)
    if mm:
        p['kind'], p['offs'] = 'gele', _dirs(mm.group(1))
        return _fin(p)
    mm = BOTH01.match(body)
    if mm:
        p['kind'], p['offs'] = 'both2', _dirs(mm.group(1))
        p['v'], p['w'] = int(mm.group(2)), int(mm.group(3))
        if mm.group(4) is not None:
            p['before'] = (int(mm.group(4)), int(mm.group(5)))
        return _fin(p)
    mm = NBRSOME.match(body)
    if mm:
        p['kind'], p['offs'] = 'some', _dirs(mm.group(2))
        p['v'], p['w'] = int(mm.group(1)), int(mm.group(3))
        return _fin(p)
    mm = ONEADJ.match(body)
    if mm:
        p['kind'], p['offs'] = 'some', _dirs(mm.group(1))
        p['v'], p['w'] = 1, 1
        return _fin(p)
    mm = ADJCNT.match(body)
    if mm:
        p['kind'], p['offs'] = 'count', _dirs(mm.group(2))
        p['v'], p['w'] = int(mm.group(1)), int(mm.group(5))
        p['counts'] = frozenset((int(mm.group(3)), int(mm.group(4))))
        return _fin(p)
    if EQONE.match(body):
        p['kind'], p['offs'] = 'eqone', BOTH['horizontal'] + BOTH['vertical']
        return _fin(p)
    b2, noeq = body, False
    if b2.rstrip('.').lower().endswith(NOEQ):
        b2, noeq = b2.rstrip('.')[:-len(NOEQ)] + '.', True
    mm = PLUSMINUS.match(b2)
    if mm:
        if int(mm.group(1)) != alpha:
            return None
        p['kind'], p['offs'] = 'plusminus', _dirs(mm.group(2))
        p['noeq'] = noeq
        return _fin(p)
    return None


def _fin(p):
    if p['offs'] is None or p['W'] < 1:
        return None
    for k in ('v', 'w'):
        if p[k] is not None and not 0 <= p[k] <= p['alpha']:
            return None
    if p['before'] and not all(0 <= t <= p['alpha'] for t in p['before']):
        return None
    if p['trans']:
        p['offs'] = [(b, a) for a, b in p['offs']]
    p['offs'] = sorted(p['offs'])
    return p


def _reach(p):
    return max(0, max(-d for d, _ in p['offs'])), max(0, max(d for d, _ in p['offs']))


def build(p, cap=400000):
    W, A, kind = p['W'], p['alpha'] + 1, p['kind']
    U, D = _reach(p)
    K = U + D
    # The guard is on the number of ROWS enumerated, which is what the build actually walks
    # through, and it is an absolute bound rather than a function of the caller's cap: a rebuild
    # at a smaller cap must take the same path as the run that produced the model. The state
    # count is held down by the `len(order) > cap' test below.
    if A ** W > ROWMAX:
        return None
    rows = list(product(range(A), repeat=W))

    def get(win, i, j):
        if i < 0 or i >= len(win) or j < 0 or j >= W:
            return None
        r = win[i]
        return None if r is None else r[j]

    def cell_ok(win, j):
        x = get(win, U, j)
        if x is None:
            return True
        v = [y for y in (get(win, U + a, j + b) for a, b in p['offs']) if y is not None]
        if kind == 'lesome':
            return x == 0 or any(y >= x for y in v)
        if kind == 'gele':
            return any(y >= x for y in v) and any(y <= x for y in v)
        if kind == 'both2':
            return p['v'] in v and p['w'] in v
        if kind == 'some':
            return x != p['v'] or p['w'] in v
        if kind == 'count':
            return x != p['v'] or sum(1 for y in v if y == p['w']) in p['counts']
        if kind == 'eqone':
            return x in v
        for t in (x - 1, x + 1):
            if 0 <= t < A and t not in v:
                return False
        if p['noeq'] and any(y == x for y in v):
            return False
        return True

    def row_ok(win):
        return all(cell_ok(win, j) for j in range(W))

    def seen(f, r):
        """How the `introduced before' clause stands after writing row r: 0 neither value seen,
        1 the earlier value seen first (settled), 2 broken."""
        if f != 0:
            return f
        a, b = p['before']
        for x in r:
            if x == b:
                return 2
            if x == a:
                return 1
        return 0

    idx, order, adj, endv = {}, [], [], []

    def push(st):
        if st not in idx:
            idx[st] = len(order)
            order.append(st)
            adj.append(None)
            endv.append(None)
        return idx[st]

    push(((None,) * K, 0))
    t = 0
    while t < len(order):
        st, f = order[t]
        out = []
        for v in rows:
            win = st + (v,)
            if not row_ok(win):
                continue
            f2 = seen(f, v) if p['before'] else 0
            if f2 == 2:
                continue
            out.append(push((win[1:] if K else (), f2)))
        adj[t] = out
        w = st
        ok = True
        for _ in range(D):
            win = w + (None,)
            if not row_ok(win):
                ok = False
                break
            w = win[1:] if K else ()
        endv[t] = 1 if ok else 0
        t += 1
        if len(order) > cap:
            return None
    n = len(order)
    sv = [0] * n
    sv[0] = 1
    return adj, sv, endv[:n], n


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
