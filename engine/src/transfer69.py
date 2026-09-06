#!/usr/bin/env python3
"""`Number of white square subarrays of (n+1) X (k+1) binary arrays with no element equal to a
strict majority of its diagonal and antidiagonal neighbors, with upper left element zero.'

Colour the cells of the array like a chessboard: $(i,j)$ is white when $i+j$ is even and black
when it is odd. Every one of these entries states its condition purely in terms of DIAGONAL and
ANTIDIAGONAL neighbours, and a diagonal step changes $i$ and $j$ each by one, so it never
changes the colour of a cell. The white cells and the black cells therefore satisfy their
conditions independently of one another: a valid array is exactly a valid white half together
with a valid black half, chosen freely. Counting the white subarrays that occur is then simply
counting the valid white halves, and the entry's ``upper left element zero'' fixes the first
cell of that half in reading order --- for a black subarray that is the cell $(0,1)$, not
$(0,0)$.

So this is a walk after all, on the sublattice of one colour. Taking the array a row at a time,
the cells of one colour in a row are the ones at every other column, and their diagonal and
antidiagonal neighbours are exactly the cells of the same colour in the rows immediately above
and below. The state is two consecutive rows; each step settles the row in the middle of the
three it completes; and because a cell looks one row DOWN as well as up, the last row of a
finished array is still untested when the walk stops, so the end vector is the indicator of the
states whose last row passes with nothing below it.

Two conditions occur. One forbids a cell to equal a strict majority of its neighbours. The other
asks every cell to have a neighbour one greater than it modulo $m$, with no two neighbours
equal. Two extra clauses occur: the first cell of the subarray is $0$, or the values
$0..m$ are introduced in reading order --- the latter carried as one more number in the state,
how many distinct values have been introduced so far, since a cell may then take any value
already used or the next one up.
"""
import re
from itertools import product

import namecanon
import transfer19

DIM = r'(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))'
SH = r'(?:\((?P<ra>n|\d+)\s*\+\s*(?P<rb>\d+)\)|(?P<rc>n|\d+))\s*X\s*' \
     r'(?:\((?P<ca>n|\d+)\s*\+\s*(?P<cb>\d+)\)|(?P<cc>n|\d+))'
RANGE = r'(?:0\.\.(?P<m>\d+)|(?P<bin>binary))'
FORM1 = re.compile(r'^Number of (?P<col>white|black)[ -]square subarrays of ' + SH +
                   r'\s+' + RANGE + r'\s+arrays?(?:\s+x\(i,j\))?\s+with\s+(?P<body>.*)$', re.I)
FORM2 = re.compile(r'^Number of ' + SH + r'\s+(?P<col>white|black)-square subarrays of\s+' +
                   RANGE + r'\s+arrays?(?:\s+x\(i,j\))?\s+with\s+(?P<body>.*)$', re.I)
MAJ = re.compile(r'^no element equal to a strict majority of its diagonal and antidiagonal '
                 r'neighbors, with (?:(upper left element zero)|values 0\.\.(\d+) introduced '
                 r'in row major order)\s*\.?$', re.I)
PLUS = re.compile(r'^each element diagonally or antidiagonally next to at least one element '
                  r'with value \(x\(i,j\)\+1\) mod (\d+), no adjacent elements equal, and '
                  r'upper left element zero\s*\.?$', re.I)
DA = ((-1, -1), (1, 1), (-1, 1), (1, -1))


def parse_name(nm):
    nm = namecanon.canon(nm)
    s = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = FORM1.match(s) or FORM2.match(s)
    if not m:
        return None
    rows = m.group('ra') or m.group('rc')
    cols = m.group('ca') or m.group('cc')
    if rows != 'n' or cols is None or cols == 'n':
        return None
    C = int(cols) + int(m.group('cb') or 0)
    alpha = 1 if m.group('bin') else int(m.group('m'))
    par = 0 if m.group('col').lower() == 'white' else 1
    body = m.group('body').strip()
    mm = MAJ.match(body)
    if mm:
        if mm.group(2) is not None and int(mm.group(2)) != alpha:
            return None
        return {'C': C, 'alpha': alpha, 'par': par, 'kind': 'maj', 'mod': None,
                'ul0': bool(mm.group(1)), 'rowmajor': mm.group(2) is not None, 'frac': 1}
    mm = PLUS.match(body)
    if mm:
        if int(mm.group(1)) != alpha + 1:
            return None
        return {'C': C, 'alpha': alpha, 'par': par, 'kind': 'plus', 'mod': int(mm.group(1)),
                'ul0': True, 'rowmajor': False, 'frac': 1}
    return None


def build(p, cap=400000):
    C, A, par, kind = p['C'], p['alpha'] + 1, p['par'], p['kind']
    cols = [[j for j in range(C) if (i + j) % 2 == par] for i in (0, 1)]
    if not cols[0] and not cols[1]:
        return None
    if A ** max(len(cols[0]), len(cols[1])) > 4 * cap:
        return None

    def rowsof(parity):
        """The class cells of a row of the given parity, as a full-width tuple with None
        elsewhere. The reading-order clause is applied afterwards, cell by cell along the row,
        because a value first used early in a row makes a larger value legal later in it."""
        out = []
        cs = cols[parity]
        for v in product(range(A), repeat=len(cs)):
            r = [None] * C
            for k, j in enumerate(cs):
                r[j] = v[k]
            out.append(tuple(r))
        return out

    def get(win, i, j):
        if i < 0 or i >= len(win) or j < 0 or j >= C:
            return None
        r = win[i]
        return None if r is None else r[j]

    def row_ok(win):
        """Test the middle row of a three-row window; win[1] may be None (before the array)."""
        if win[1] is None:
            return True
        for j in range(C):
            x = get(win, 1, j)
            if x is None:
                continue
            nb = [y for y in (get(win, 1 + a, j + b) for a, b in DA) if y is not None]
            if kind == 'maj':
                if 2 * sum(1 for y in nb if y == x) > len(nb):
                    return False
            else:
                if not any(y == (x + 1) % p['mod'] for y in nb):
                    return False
                if any(y == x for y in nb):
                    return False
        return True

    def intro(m, r):
        """Values introduced so far after writing row r in reading order, or None if r breaks
        the order."""
        for j in range(C):
            x = r[j]
            if x is None:
                continue
            if x > m:
                return None
            if x == m:
                m += 1
        return m

    idx, order, adj, endv = {}, [], [], []

    def push(st):
        if st not in idx:
            idx[st] = len(order)
            order.append(st)
            adj.append(None)
            endv.append(None)
        return idx[st]

    push((None, None, 0, 0))          # (row above, row just written, next row's parity, m)
    t = 0
    while t < len(order):
        u, v, parity, m = order[t]
        first = u is None and v is None
        out = []
        for w in rowsof(parity):
            if p['ul0'] and first:
                k = next((j for j in range(C) if w[j] is not None), None)
                if k is not None and w[k] != 0:
                    continue
            if not row_ok((u, v, w)):
                continue
            m2 = intro(m, w) if p['rowmajor'] else 0
            if m2 is None:
                continue
            out.append(push((v, w, 1 - parity, m2)))
        adj[t] = out
        endv[t] = 1 if row_ok((u, v, None)) else 0
        t += 1
        if len(order) > cap:
            return None
    n = len(order)
    st = [0] * n
    st[0] = 1
    return adj, st, endv[:n], n


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
