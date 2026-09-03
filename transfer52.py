#!/usr/bin/env python3
"""`Number of n X W 0..m-1 arrays with no element equal to c1 plus the sum of elements to its
left or c2 plus the sum of elements above it [or c3 plus the sum of the elements diagonally to
its northwest] [or c4 plus the sum of the elements antidiagonally to its northeast], modulo m.'

Each cell is forbidden to equal, modulo `m', a constant plus the sum of the cells lying before
it along one of up to four rays: west, north, northwest and northeast. None of those sums is
bounded, but every one of them is built by adding one term at a time, so its RESIDUE is carried
in the state.

Take the array a slice at a time along whichever side varies with `n' --- a row for an
`n X W' entry, a column for a `W X n' one. Writing `x' for the slice just written and
indexing positions of a slice by `p':

    the sum along one ray lies INSIDE the current slice   (running total as the slice is filled)
    the sum along the opposite ray is per position        U'[p]  = U[p] + x[p]
    the northwest sum is per diagonal, shifted one right  NW'[p] = NW[p-1] + x[p-1]
    the northeast sum is per antidiagonal, shifted left   NE'[p] = NE[p+1] + x[p+1]

with `NW'[0]' and `NE'[W-1]' zero, those rays being empty at the border. Reduced modulo `m'
this is a bounded state and the walk is over it.

The northeast ray is the one asymmetry. For an `n X W' entry it points into slices already
written; for a `W X n' entry it points into slices still to come, and no bounded state built
this way can hold it. Those entries are REFUSED here rather than modelled with the ray read
in the wrong direction.
"""
import re

import namecanon
import transfer19

NUM = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6,
       'seven': 7, 'eight': 8, 'nine': 9}

RAY = [('west', r'to its left'),
       ('north', r'above it'),
       ('nw', r'diagonally to its northwest'),
       ('ne', r'antidiagonally to its northeast')]

CLAUSE = re.compile(
    r'(\w+)\s+plus the sum of\s+(?:the\s+)?(?:sum of\s+)?(?:the\s+)?elements\s+'
    r'(to its left|above it|diagonally to its northwest|antidiagonally to its northeast)',
    re.I)

NAME = re.compile(
    r'Number of\s+(?:n\s*X\s*(\d+)|(\d+)\s*X\s*n)\s+0\.\.(\d+)\s*arrays with no element equal '
    r'to\s+(.*?),\s*modulo\s+(\d+)\s*\.?\s*$', re.I)

KEY = {'to its left': 'west', 'above it': 'north',
       'diagonally to its northwest': 'nw', 'antidiagonally to its northeast': 'ne'}


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn])\s*[xX]\s*(?=[\dn])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = NAME.search(nm)
    if not m:
        return None
    W = int(m.group(1) or m.group(2))
    trans = m.group(1) is None
    alpha = int(m.group(3))
    mod = int(m.group(5))
    body = m.group(4)
    con = {}
    used = 0
    for g in CLAUSE.finditer(body):
        w = g.group(1).lower()
        v = int(w) if w.isdigit() else NUM.get(w)
        if v is None:
            return None
        k = KEY[g.group(2).lower()]
        if k in con:
            return None
        con[k] = v % mod
        used += g.end() - g.start()
    if not con or W < 1 or mod < 1:
        return None
    # nothing but the clauses and the words joining them may be left in the body
    rest = CLAUSE.sub('', body)
    rest = re.sub(r'\bor\b|\band\b|,|\s+', '', rest, flags=re.I)
    if rest:
        return None
    if trans and 'ne' in con:
        return None                     # the northeast ray would point into unwritten slices
    if trans:
        con = {('north' if k == 'west' else 'west' if k == 'north' else k): v
               for k, v in con.items()}
    return {'W': W, 'alpha': alpha, 'mod': mod, 'con': con, 'trans': trans, 'frac': 1}


def build(p, cap=40000):
    W, A, M = p['W'], p['alpha'] + 1, p['mod']
    con = p['con']
    hasU, hasNW, hasNE = 'north' in con, 'nw' in con, 'ne' in con
    inrun = con.get('west')
    if A ** W > 40 * cap:
        return None
    z = (0,) * W
    idx, order, adj = {}, [], []

    def push(st):
        if st not in idx:
            idx[st] = len(order)
            order.append(st)
            adj.append(None)
        return idx[st]

    def fill(U, NW, NE):
        """every slice legal against the given ray residues, as a list of tuples"""
        out, cur = [], []

        def go(pp, run):
            if pp == W:
                out.append(tuple(cur))
                return
            for v in range(A):
                if inrun is not None and v % M == (inrun + run) % M:
                    continue
                if hasU and v % M == (con['north'] + U[pp]) % M:
                    continue
                if hasNW and v % M == (con['nw'] + NW[pp]) % M:
                    continue
                if hasNE and v % M == (con['ne'] + NE[pp]) % M:
                    continue
                cur.append(v)
                go(pp + 1, (run + v) % M)
                cur.pop()
        go(0, 0)
        return out

    push((z, z, z))
    t = 0
    while t < len(order):
        U, NW, NE = order[t]
        row = []
        for x in fill(U, NW, NE):
            nU = tuple((U[q] + x[q]) % M for q in range(W)) if hasU else z
            nNW = tuple(0 if q == 0 else (NW[q - 1] + x[q - 1]) % M
                        for q in range(W)) if hasNW else z
            nNE = tuple(0 if q == W - 1 else (NE[q + 1] + x[q + 1]) % M
                        for q in range(W)) if hasNE else z
            row.append(push((nU, nNW, nNE)))
        adj[t] = row
        t += 1
        if len(order) > cap:
            return None
    n = len(order)
    st = [0] * n
    st[0] = 1
    return adj, st, [1] * n, n


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
