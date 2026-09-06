#!/usr/bin/env python3
"""`Number of n X W arrays of the MINIMUM value of corresponding elements and their
<neighbours> in a random 0..m n X W array' -- another image count.

Each cell of the derived array carries the least of its own value and those of its
neighbours, and the entry counts how many different derived arrays occur. As in the `maps'
families this is the size of an image, so it is not a walk count on the underlying arrays; the
determinisation of `imagedet` supplies one. The derived row is fixed by the three rows above,
at and below it, so the state of the machine is the pair of the last two rows read, and the
last derived row is emitted with nothing below it and so is counted at the state the walk
stops in rather than being a step of it.
"""
import re
from itertools import product

import namecanon
import imagedet
import transfer19

CLASS = {'horizontal': [(0, -1), (0, 1)],
         'vertical': [(-1, 0), (1, 0)],
         'diagonal': [(-1, -1), (1, 1)],
         'antidiagonal': [(-1, 1), (1, -1)],
         'king-move': [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if (a, b) != (0, 0)]}

NAME = re.compile(
    r'Number of\s+(?:n\s*X\s*(\d+)|(\d+)\s*X\s*n)\s+arrays of the (minimum|maximum) value of '
    r'corresponding elements and their\s+(.*?)\s+neighbors?\s+in a random\s+0\.\.(\d+)\s+'
    r'.*$', re.I)


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn])\s*[xX]\s*(?=[\dn])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = NAME.search(nm)
    if not m:
        return None
    W = int(m.group(1) or m.group(2))
    walk = 'rows' if m.group(1) else 'cols'
    which = m.group(3).lower()
    body = m.group(4).lower()
    alpha = int(m.group(5))
    words = re.findall(r'antidiagonal|king-move|horizontal|vertical|diagonal', body)
    left = re.sub(r'antidiagonal|king-move|horizontal|vertical|diagonal', ' ', body)
    left = re.sub(r'\b(and|or|their)\b|,|\s+', '', left)
    if not words or left:
        return None
    D = set()
    for w in words:
        D.update(CLASS[w])
    if walk == 'cols':
        D = {(b, a) for a, b in D}
    if W < 1 or alpha < 1:
        return None
    return {'W': W, 'dirs': sorted(D), 'alpha': alpha, 'which': which, 'frac': 1}


def build(p, cap=20000):
    W, A = p['W'], p['alpha'] + 1
    D = set(map(tuple, p['dirs']))
    pick = min if p['which'] == 'minimum' else max
    if A ** W > 40 * cap:
        return None
    rows = list(product(range(A), repeat=W))

    def brow(prev, cur, nxt):
        out = []
        for j in range(W):
            vals = [cur[j]]
            for (di, dj) in D:
                jj = j + dj
                if not 0 <= jj < W:
                    continue
                line = prev if di < 0 else (cur if di == 0 else nxt)
                if line is None:
                    continue
                vals.append(line[jj])
            out.append(pick(vals))
        return tuple(out)

    return imagedet.build([(None, r) for r in rows], rows,
                          lambda el, x: (brow(el[0], el[1], x), (el[1], x)),
                          lambda el: brow(el[0], el[1], None), cap)


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
