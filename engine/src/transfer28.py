#!/usr/bin/env python3
"""`Number of n X W 0..k arrays of the MEDIAN (or SUM) of the corresponding element, the
element to the east and the element to the south in a larger (n+1) X (W+1) 0..m array' --
again an image count, and again settled by determinising.

Here the derived cell (i,j) reads A(i,j), A(i,j+1) and A(i+1,j) of the larger array, so it
depends on two consecutive rows only: the state of the machine is the last row read, and one
step emits a whole derived row. An array of n+1 rows gives n derived rows, so there is no
final emission and the walk simply has n steps. The optional clause `without adjacent equal
elements in the latter' restricts the larger array, which removes transitions and start
states but changes nothing else.
"""
import re
from itertools import product

import namecanon
import imagedet
import transfer19

NAME = re.compile(
    r'Number of\s+n\s*X\s*(\d+)\s+0\.\.(\d+)\s+arrays of the (median|sum) of the '
    r'corresponding element, the element to the east and the element to the south in a '
    r'larger\s+\(\s*n\s*\+\s*1\s*\)\s*X\s*(\d+)\s+0\.\.(\d+)\s+array'
    r'(\s+without adjacent equal elements in the latter)?\s*\.?\s*$', re.I)


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn)])\s*[xX]\s*(?=[\dn(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = NAME.search(nm)
    if not m:
        return None
    W, outa, f, WW, alpha = (int(m.group(1)), int(m.group(2)), m.group(3).lower(),
                             int(m.group(4)), int(m.group(5)))
    if WW != W + 1 or W < 1 or alpha < 1:
        return None
    want = (3 * alpha if f == 'sum' else alpha)
    if outa != want:                 # the stated output alphabet must match the operation
        return None
    return {'W': W, 'alpha': alpha, 'op': f, 'noadj': bool(m.group(6)), 'frac': 1}


def build(p, cap=20000):
    W, A, op, noadj = p['W'], p['alpha'] + 1, p['op'], p['noadj']
    if A ** (W + 1) > 40 * cap:
        return None
    rows = [r for r in product(range(A), repeat=W + 1)
            if not (noadj and any(r[j] == r[j + 1] for j in range(W)))]
    if not rows:
        return None

    def val(a, b, c):
        return (a + b + c) if op == 'sum' else sorted((a, b, c))[1]

    def step(r, x):
        if noadj and any(u == v for u, v in zip(r, x)):
            return None
        return tuple(val(r[j], r[j + 1], x[j]) for j in range(W)), x

    return imagedet.build(rows, rows, step, None, cap)


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
