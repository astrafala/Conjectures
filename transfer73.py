#!/usr/bin/env python3
"""`Number of n X W array permutations with each element moving zero or one space
diagonally, horizontally or vertically.'

The cells of an `n x W' array are permuted, and every cell's image must differ from it by one
of the offsets the name lists. That count is the PERMANENT of the 0/1 matrix of the offset
graph, and for a fixed width it is a walk count: read the cells in row-major order, let each
one choose its image, and carry as the state which images in a bounded window have already
been taken.

The window is bounded because an offset moves a cell by at most `hi' and at least `lo'
positions in the linear order, so an image more than `hi - lo' positions behind the cell being
processed can never be chosen again. Requiring it to be taken before it leaves the window is
what makes the walk count the permanent rather than a partial matching count.

Two boundaries, and they turn out to be the same condition. Images above the first row do not
exist, so the walk starts with those window positions marked taken; images below the last row
do not exist either, so the walk must END with exactly those positions marked and nothing
beyond. In the window's own coordinates both are the same mask, so the start state is also the
only accepting one.

The direction words each name an AXIS, two opposite offsets: `horizontally' is
`(0,1),(0,-1)', `diagonally' is `(1,1),(-1,-1)', `antidiagonally' is `(1,-1),(-1,1)'. That is
what the entries mean and it is pinned against their published terms, not assumed: reading
`diagonally, horizontally or vertically' as all eight king moves gives 24 where A189305
publishes 14.
"""
import re
from itertools import product

import namecanon
import transfer19

AXIS = {'horizontal': [(0, 1), (0, -1)], 'vertical': [(1, 0), (-1, 0)],
        'diagonal': [(1, 1), (-1, -1)], 'antidiagonal': [(1, -1), (-1, 1)]}
COMPASS = {'N': (-1, 0), 'S': (1, 0), 'E': (0, 1), 'W': (0, -1),
           'NE': (-1, 1), 'NW': (-1, -1), 'SE': (1, 1), 'SW': (1, -1)}
KNIGHT = [(a, b) for a in (-2, -1, 1, 2) for b in (-2, -1, 1, 2) if abs(a) + abs(b) == 3]
KING = [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if (a, b) != (0, 0)]
# "right-handed knight moves (out 2, right 1)": two out and one to the right, in each of the
# four headings. Pinned against A209538, where the full knight set gives 4 and the entry has 2.
RIGHT_KNIGHT = [(-2, -1), (-1, 2), (1, -2), (2, 1)]
LEFT_KNIGHT = [(-2, 1), (-1, -2), (1, 2), (2, -1)]

HEAD = re.compile(r'^\s*Number of\s+(n|\d+)\s*X\s*(n|\d+)\s+array permutations\s+with\s+(.*?)\s*\.?\s*$',
                  re.I)


def _offsets(body):
    stay = bool(re.search(r'\bzero or\b|\bnot mov(?:ed|ing)\b', body, re.I))
    offs = set()
    if re.search(r'knight move', body, re.I):
        if re.search(r'right-handed', body, re.I):
            offs |= set(RIGHT_KNIGHT)
        elif re.search(r'left-handed', body, re.I):
            offs |= set(LEFT_KNIGHT)
        else:
            offs |= set(KNIGHT)
    elif re.search(r'king move', body, re.I):
        offs |= set(KING)
    else:
        for w, v in AXIS.items():
            if re.search(r'\b' + w + r'(?:ly)?\b', body, re.I):
                offs |= set(v)
        for w, v in COMPASS.items():
            if re.search(r'(?<![A-Za-z])' + w + r'(?![A-Za-z])', body):
                offs.add(v)
    if not offs:
        return None
    if stay:
        offs.add((0, 0))
    return sorted(offs)


def parse_name(nm):
    nm = namecanon.canon(nm)
    s = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = HEAD.match(s)
    if not m:
        return None
    ra, ca, body = m.group(1), m.group(2), m.group(3)
    if (ra == 'n') == (ca == 'n'):
        return None
    # anything beyond the plain offset list is a different problem
    if re.search(r'loop|city block|hexagon|no more than|and no |, and |without', body, re.I):
        return None
    offs = _offsets(body)
    if offs is None:
        return None
    if ra == 'n':
        W, trans = int(ca), False
    else:
        W, trans = int(ra), True
        offs = [(b, a) for a, b in offs]        # transposing exchanges the coordinates
    if W < 1 or W > 8:
        return None
    return {'W': W, 'offs': sorted(offs), 'trans': trans, 'frac': 1}


def build(p, cap=200000):
    W = p['W']
    offs = [tuple(o) for o in p['offs']]
    lin = [d1 * W + d2 for d1, d2 in offs]
    lo, hi = min(lin + [0]), max(lin + [0])
    WIN = hi - lo + 1
    if WIN > 26:
        return None
    base = sum(1 << b for b in range(WIN) if lo + b < 0)   # positions above the first row

    def cellstep(mask, j):
        """one cell chooses its image, then the window slides by one position"""
        out = []
        for d1, d2 in offs:
            jj = j + d2
            if not 0 <= jj < W:
                continue
            b = (d1 * W + d2) - lo
            if mask >> b & 1:
                continue
            m2 = mask | (1 << b)
            if not m2 & 1:               # the position leaving the window was never taken
                continue
            out.append(m2 >> 1)
        return out

    idx = {base: 0}
    order = [base]
    adj = [None]
    t = 0
    while t < len(order):
        cur = [order[t]]
        for j in range(W):               # a row is W cell steps
            nxt = []
            for m in cur:
                nxt.extend(cellstep(m, j))
            cur = nxt
            if len(cur) > 40 * cap:
                return None
        row = []
        for m in cur:
            i = idx.get(m)
            if i is None:
                i = idx[m] = len(order)
                order.append(m)
                adj.append(None)
            row.append(i)
        adj[t] = sorted(row)
        t += 1
        if len(order) > cap:
            return None
    n = len(order)
    start = [0] * n
    start[0] = 1
    end = [1 if order[i] == base else 0 for i in range(n)]
    return adj, start, end, n


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
