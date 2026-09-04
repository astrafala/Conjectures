#!/usr/bin/env python3
"""`Number of n X W 0..m arrays with no element equal to the average of its horizontal and
vertical neighbors', and the rest of the family of conditions each cell states about the cells
around it.

Every condition here is read at one cell at a time, out of a fixed set of offsets:

    horizontal      (0,-1) and (0,1)          vertical        (-1,0) and (1,0)
    diagonal        (-1,-1) and (1,1)         antidiagonal    (-1,1) and (1,-1)
    knight-move     the eight knight offsets

and some entries instead name a single direction each --- `vertically above' is (-1,0) alone,
`horizontally left' is (0,-1), `diagonally above and left' is (-1,-1). Only the offsets that
land inside the array count, so a cell on the border simply has fewer neighbours; a cell with
no neighbour at all satisfies an `is not equal to the average of' condition vacuously, and that
is what the published first terms say.

Seven statements are read:

    x is not the average of its neighbours;
    the average of x together with its neighbours is not a given value;
    x is not equal to a strict majority of its neighbours;
    no strict majority of the neighbours equals x+1 mod m  (the `rock, paper and scissors' ones);
    x is not equal both to the cell above and to the cell to its left;
    x is the sum mod m of one named group of neighbours, or of another;

some with the extra clause that the top-left cell is 0.

A cell's condition reaches U rows up and D rows down, so it is settled by a window of U+D+1
consecutive rows; the state is the last U+D of them, and the row a step tests is the one the new
row completes. The last D rows are still untested when the array stops, so the end vector is not
all ones: a state is accepted exactly when those rows pass with nothing below them.
"""
import re
from fractions import Fraction
from itertools import product

import namecanon
import transfer19

FRAC = re.compile(r'^\s*(?:(Half)|One quarter|1/(\d+))\s+the number of\s+', re.I)
HEAD = re.compile(r'^\s*Number of\s+', re.I)
DIM = r'(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))'
SHAPE = re.compile(r'^' + DIM + r'\s*X\s*' + DIM +
                   r'\s+(?:(0)\.\.(\d+)|(binary))\s+arrays?(?:\s+x\(i,j\))?\s+with\s+', re.I)

BOTH = {'horizontal': [(0, -1), (0, 1)], 'vertical': [(-1, 0), (1, 0)],
        'diagonal': [(-1, -1), (1, 1)], 'antidiagonal': [(-1, 1), (1, -1)],
        'knight-move': [(1, 2), (2, 1), (-1, 2), (-2, 1),
                        (1, -2), (2, -1), (-1, -2), (-2, -1)]}
ONE = {'vertically above': (-1, 0), 'horizontally left': (0, -1),
       'diagonally above and left': (-1, -1),
       'antidiagonally above and right': (-1, 1)}
DIRW = re.compile(r'\b(antidiagonal|diagonal|horizontal|vertical|knight-move)\b', re.I)
NUM = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6}
UL0 = r'(?:,\s*with upper left element zero(?:\s*\(rock paper and scissors[^)]*\))?)?'

AVGDIR = re.compile(r'^no element equal the average of immediate neighbors (.+?) of it\s*\.?$',
                    re.I)
AVGNBR = re.compile(r'^no element equal to the average of its (.+?) neighbors\s*\.?$', re.I)
AVGSELF = re.compile(r'^no average of any element and its (.+?) neighbors equal to (\w+)\s*\.?$',
                     re.I)
MAJSELF = re.compile(r'^no element equal to a strict majority of its (.+?) neighbors' + UL0 +
                     r'\s*\.?$', re.I)
MAJPLUS = re.compile(r'^no element having a strict majority of its (.+?) neighbors equal to '
                     r'itself plus one mod (\d+)' + UL0 + r'\s*\.?$', re.I)
BOTHAL = re.compile(r'^no element equal both to the element above and to the element to its '
                    r'left\s*\.?$', re.I)
SUMMOD = re.compile(r'^(?:every|each) element equal to either the sum mod (\d+) of its (.+?) '
                    r'neighbors or the sum mod (\d+) of its (.+?) neighbors\s*\.?$', re.I)


def _both(txt):
    ws = [w.lower() for w in dict.fromkeys(DIRW.findall(txt))]
    if not ws:
        return None
    out = []
    for w in ws:
        out += BOTH[w]
    return out


def _dirs(txt):
    """`vertically above, diagonally above and left, and horizontally left'."""
    t = ' ' + re.sub(r'\s+', ' ', txt.lower()).replace(',', ' ') + ' '
    out, seen = [], []
    for k, v in ONE.items():
        if ' ' + k + ' ' in t:
            out.append(v)
            seen.append(k)
    if not out:
        return None
    left = t
    for k in seen:
        left = left.replace(' ' + k + ' ', ' ')
    if re.search(r'[a-z]', left.replace(' and ', ' ')):
        return None                      # an unread direction word is still in the phrase
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

    kind = offs = offs2 = None
    mod = val = None
    ul0 = False
    mm = AVGDIR.match(body)
    if mm:
        kind, offs = 'avg', _dirs(mm.group(1))
    if kind is None:
        mm = AVGNBR.match(body)
        if mm:
            kind, offs = 'avg', _both(mm.group(1))
    if kind is None:
        mm = AVGSELF.match(body)
        if mm:
            kind, offs = 'avgself', _both(mm.group(1))
            w = mm.group(2).lower()
            val = int(w) if w.isdigit() else NUM.get(w)
            if val is None:
                return None
    if kind is None:
        mm = MAJPLUS.match(body)
        if mm:
            kind, offs, mod = 'majplus', _both(mm.group(1)), int(mm.group(2))
            ul0 = 'upper left element zero' in body.lower()
    if kind is None:
        mm = MAJSELF.match(body)
        if mm:
            kind, offs = 'maj', _both(mm.group(1))
            ul0 = 'upper left element zero' in body.lower()
    if kind is None and BOTHAL.match(body):
        kind, offs = 'both', [(-1, 0), (0, -1)]
    if kind is None:
        mm = SUMMOD.match(body)
        if mm:
            if mm.group(1) != mm.group(3):
                return None
            kind, mod = 'summod', int(mm.group(1))
            offs, offs2 = _both(mm.group(2)), _both(mm.group(4))
    if kind is None or offs is None or (kind == 'summod' and offs2 is None):
        return None
    if trans:
        offs = [(b, a) for a, b in offs]
        if offs2:
            offs2 = [(b, a) for a, b in offs2]
    if W < 1:
        return None
    return {'W': W, 'alpha': alpha, 'kind': kind, 'offs': sorted(offs),
            'offs2': sorted(offs2) if offs2 else None, 'mod': mod, 'val': val,
            'ul0': ul0, 'trans': trans, 'frac': frac}


def _reach(p):
    o = list(p['offs']) + list(p['offs2'] or [])
    return max(0, max(-d for d, _ in o)), max(0, max(d for d, _ in o))


def build(p, cap=400000):
    W, A, kind = p['W'], p['alpha'] + 1, p['kind']
    U, D = _reach(p)
    K = U + D
    if A ** (W * max(K, 1)) > 8 * cap:
        return None
    rows = list(product(range(A), repeat=W))

    def get(win, i, j):
        """The cell (i,j) of a window of K+1 rows, or None when it is off the array."""
        if i < 0 or i >= len(win) or j < 0 or j >= W:
            return None
        r = win[i]
        return None if r is None else r[j]

    def cell_ok(win, j):
        x = get(win, U, j)
        if x is None:
            return True
        v = [y for y in (get(win, U + di, j + dj) for di, dj in p['offs']) if y is not None]
        if kind == 'avg':
            return not v or Fraction(sum(v), len(v)) != x
        if kind == 'avgself':
            return Fraction(sum(v) + x, len(v) + 1) != p['val']
        if kind == 'maj':
            return 2 * sum(1 for y in v if y == x) <= len(v)
        if kind == 'majplus':
            t = (x + 1) % p['mod']
            return 2 * sum(1 for y in v if y == t) <= len(v)
        if kind == 'both':
            a = get(win, U - 1, j)
            b = get(win, U, j - 1)
            return not (a is not None and b is not None and x == a and x == b)
        s1 = sum(v) % p['mod']
        v2 = [y for y in (get(win, U + di, j + dj) for di, dj in p['offs2']) if y is not None]
        return x == s1 or x == sum(v2) % p['mod']

    def row_ok(win):
        return all(cell_ok(win, j) for j in range(W))

    idx, order, adj, endv = {}, [], [], []

    def push(st):
        if st not in idx:
            idx[st] = len(order)
            order.append(st)
            adj.append(None)
            endv.append(None)
        return idx[st]

    start = (None,) * K
    push(start)
    t = 0
    while t < len(order):
        st = order[t]
        out = []
        first = all(r is None for r in st)
        for v in rows:
            if p['ul0'] and first and v[0] != 0:
                continue
            win = st + (v,)
            if row_ok(win):
                out.append(push(win[1:] if K else ()))
        adj[t] = out
        # what is still untested when the array stops here: the last D rows, with nothing below
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
