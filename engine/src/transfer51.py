#!/usr/bin/env python3
"""`Number of (n+k) X (W+k) 0..m arrays with each row and column divisible by d, read as a
base-b number with top and left being the most significant digits.'

Each ROW of the array, read left to right with the left digit most significant, is a base-`b'
number of `W' digits, and each COLUMN, read top to bottom with the top digit most significant,
is a base-`b' number of as many digits as the array has rows. The entry asks that these be
divisible --- or not divisible --- by given moduli.

The row condition is a condition on one row and is imposed as the rows are chosen. The column
condition is not local at all: a column's value depends on every row of the array. But its
RESIDUE is built by Horner's rule, one row at a time,

    v_j  <-  b*v_j + x(i,j)   (mod e),

so the vector of column residues is a state of bounded size and the column condition is read
off it at the end. That is the whole construction: the walk is over `e^W' residue vectors, one
step per array row, and the end vector picks out the residue vectors the entry accepts.

Some entries add `rows and columns lexicographically nondecreasing'. Comparing two rows needs
the previous row in the state; comparing two COLUMNS is decided by the first array row where
they differ, so the state also carries which adjacent column pairs are still equal --- one bit
each, and once a pair is decided it never has to be looked at again.
"""
import re
from itertools import product

import namecanon
import transfer19

NAME = re.compile(
    r'Number of\s+(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))\s*X\s*'
    r'(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))\s*0\.\.(\d+)\s*arrays with\s+'
    r'each row (and (?:each )?column )?(not )?divisible by (\d+)'
    r'(?:\s+and\s+(?:each\s+)?column\s+(not )?divisible by (\d+))?'
    r',\s*read as a (?:(binary)|base-(\d+)) number with top and left being the most '
    r'significant (?:bits|digits)'
    r'(?:,?\s*and rows and columns lexicographically (nondecreasing|nonincreasing))?'
    r'\s*\.?\s*$', re.I)


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = NAME.search(nm)
    if not m:
        return None
    ra = m.group(1) or m.group(3)
    rb = int(m.group(2) or 0)
    ca = m.group(4) or m.group(6)
    cb = int(m.group(5) or 0)
    if (ra == 'n') == (ca == 'n'):
        return None
    if ra == 'n':
        W, trans = int(ca) + cb, False
    else:
        W, trans = int(ra) + rb, True
    alpha = int(m.group(7))
    shared = bool(m.group(8))
    rowneg, rowmod = bool(m.group(9)), int(m.group(10))
    if m.group(12):
        colneg, colmod = bool(m.group(11)), int(m.group(12))
    elif shared:
        colneg, colmod = rowneg, rowmod
    else:
        return None
    base = 2 if m.group(13) else int(m.group(14))
    lex = (m.group(15) or '').lower()
    if base != alpha + 1 or W < 1 or rowmod < 1 or colmod < 1:
        return None
    if trans:
        rowneg, rowmod, colneg, colmod = colneg, colmod, rowneg, rowmod
    return {'W': W, 'alpha': alpha, 'base': base, 'rowmod': rowmod, 'rowneg': rowneg,
            'colmod': colmod, 'colneg': colneg, 'lex': lex, 'trans': trans, 'frac': 1}


def build(p, cap=40000):
    W, b, E = p['W'], p['base'], p['colmod']
    # the only up-front enumeration is over the b^W possible rows; the residue space is
    # reached lazily and bounded by `cap' below, so guarding on e^W here would refuse a
    # model whose reachable part is small
    if b ** W > 40 * cap:
        return None
    rows = []
    for r in product(range(b), repeat=W):
        v = 0
        for x in r:
            v = v * b + x
        if (v % p['rowmod'] == 0) != p['rowneg']:
            rows.append(r)
    if not rows:
        return [], [], [], 0
    lex = p['lex']
    idx, order, adj, end = {}, [], [], []

    def push(st):
        if st not in idx:
            idx[st] = len(order)
            order.append(st)
            adj.append(None)
            end.append(0)
        return idx[st]

    def okend(res):
        return all((v % E == 0) != p['colneg'] for v in res)

    if not lex:
        push((0,) * W)
        t = 0
        while t < len(order):
            res = order[t]
            row = []
            for r in rows:
                row.append(push(tuple((res[j] * b + r[j]) % E for j in range(W))))
            adj[t] = row
            end[t] = 1 if okend(res) else 0
            t += 1
            if len(order) > cap:
                return None
        n = len(order)
        st = [0] * n
        st[0] = 1
        return adj, st, end[:n], n

    up = lex == 'nondecreasing'
    push(((0,) * W, None, (True,) * (W - 1)))
    t = 0
    while t < len(order):
        res, last, eq = order[t]
        row = []
        for r in rows:
            if last is not None and ((r < last) if up else (r > last)):
                continue
            neq, ok = [], True
            for j in range(W - 1):
                if not eq[j]:
                    neq.append(False)
                    continue
                if r[j] == r[j + 1]:
                    neq.append(True)
                elif (r[j] < r[j + 1]) == up:
                    neq.append(False)
                else:
                    ok = False
                    break
            if not ok:
                continue
            row.append(push((tuple((res[j] * b + r[j]) % E for j in range(W)), r,
                             tuple(neq))))
            if len(order) > cap:
                return None
        adj[t] = row
        end[t] = 1 if okend(res) else 0
        t += 1
        if len(order) > cap:
            return None
    n = len(order)
    st = [0] * n
    st[0] = 1
    return adj, st, end[:n], n


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
