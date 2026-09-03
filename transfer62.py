#!/usr/bin/env python3
"""`Number of n X W 0..m arrays with no element equal to another within two positions in the
same row or column, and new values 0..m introduced in row major order' and its relatives.

Two cells are FORBIDDEN TO AGREE when they stand in a stated positional relation. The relation
is given in one of three ways:

    `within k positions in the same row or column'   |di|+|dj| > 0, and either di=0 with
                                                     |dj|<=k, or dj=0 with |di|<=k;
    `within a city block distance of k'              0 < |di|+|dj| <= k;
    `at a city block distance of exactly k'          |di|+|dj| = k.

Each is a finite set of offsets, so the condition is the same shape as the offset family: no
cell may equal the cell at any offset of the set. The array is then counted up to renaming, the
closing clause naming the canonical representative of each equality class.

The reduction and the walk are the offset engine's, and this module only reads the three
distance phrasings into the offset set they name. Equality is symmetric, so an offset and its
negative forbid the same pairs, and the offset engine normalises them to point backwards along
the growing side before building.
"""
import re

import namecanon
import transfer54

SHAPE = r'(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))\s*X\s*(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))'
NAME = re.compile(
    r'Number of\s+' + SHAPE + r'\s*0\.\.(?P<al>\d+)\s*arrays with no element equal to another\s+'
    r'(?:within (?P<lin>\w+) positions in the same row or column'
    r'|within a city block distance of (?P<cb>\w+)'
    r'|at a city block distance of exactly (?P<ex>\w+))'
    r',\s*and new values 0\.\.(?P<al2>\d+) introduced in row major order\s*\.?\s*$', re.I)
NUM = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5}


def _n(w):
    if w is None:
        return None
    w = w.lower()
    return int(w) if w.isdigit() else NUM.get(w)


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
    alpha = int(m.group('al'))
    if int(m.group('al2')) != alpha:
        return None
    offs = []
    if m.group('lin') is not None:
        k = _n(m.group('lin'))
        if k is None:
            return None
        for t in range(1, k + 1):
            offs += [(0, t), (0, -t), (t, 0), (-t, 0)]
    else:
        exact = m.group('ex') is not None
        k = _n(m.group('ex') if exact else m.group('cb'))
        if k is None:
            return None
        for di in range(-k, k + 1):
            for dj in range(-k, k + 1):
                if (di, dj) == (0, 0):
                    continue
                s = abs(di) + abs(dj)
                if (s == k) if exact else (s <= k):
                    offs.append((di, dj))
    if not offs or W < 1:
        return None
    # hand the offsets to the shared machinery in the frame it wants them
    norm = []
    for di, dj in offs:
        s, q = (dj, di) if trans else (di, dj)
        if s > 0 or (s == 0 and q > 0):
            s, q = -s, -q
        norm.append((s, q))
    return {'W': W, 'alpha': alpha, 'K': alpha + 1, 'offs': sorted(set(norm)),
            'trans': trans, 'frac': 1}


build = transfer54.build
matvec = transfer54.matvec
terms = transfer54.terms
threshold = transfer54.threshold
