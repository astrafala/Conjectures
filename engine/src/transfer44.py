#!/usr/bin/env python3
"""Occupancy arrays under a constraint on the turn a token makes on arrival.

Same family as the plain occupancy engine: every cell of the grid holds one token, each
token moves to a cell of the neighbour set (or stays put, when the entry allows it), and the
array recorded is the OCCUPANCY, how many tokens land on each cell. The entry counts how
many different occupancy arrays arise, an IMAGE, so the count is produced by the subset
construction in `imagedet' rather than by weighting walks.

What is new here is the condition. It relates the move INTO a cell to the move OUT of it: if
the token at A moves to B with direction d, and the token at B moves with direction d', the
pair (d, d') is forbidden when

    d' = d           `straight through' -- also written `consecutive moves in the
                     same direction'
    d' = -d          a `2-loop': the two tokens exchange places
    d' left of d     a `left turn', meaning the cross product of d with d' is positive

A token that stays put neither arrives nor leaves, so a zero direction on either side of the
pair carries no condition.

Each ordered pair is tested once, from the moving token's own row: the target lies in that
row or in one of its two neighbours, so a window of three consecutive move-rows decides both
the occupancy row and every condition whose source is the middle row. That is the same window
the occupancy already needs, so the state is unchanged --- a pair of consecutive move-rows,
with an absent row carried as a symbol so that the machine knows when a move would leave the
array.

For a `W X n' entry the walk runs down the transpose of the array the name describes.
Transposition is a reflection, so it reverses the sense of a turn, and the left-turn test is
negated in that case rather than being applied in the wrong frame.
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
_W1 = r'(?:horizontal|vertical|diagonal|antidiagonal|king-move)'
NBSET = r'(' + _W1 + r'(?:[, ]+(?:or |and )?' + _W1 + r')*)'

NAME = re.compile(
    r'Number of\s+(?:n\s*X\s*(\d+)|(\d+)\s*X\s*n)\s+arrays of occupancy after each element\s+'
    r'(stays put or )?moves to some\s+' + NBSET + r'\s+neighbor'
    r'(?:,?\s+(.*?))?\s*\.?\s*$', re.I)

NUM = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4}

TAILS = [
    (re.compile(r'without move-in move-out straight through or left turns?', re.I),
     ('straight', 'left')),
    (re.compile(r'without move-in move-out left turns?', re.I), ('left',)),
    (re.compile(r'without consecutive moves in the same direction', re.I), ('straight',)),
    (re.compile(r'without 2-loops? or left turns?', re.I), ('loop', 'left')),
    (re.compile(r'with no 2-loops? and with no occupancy greater than (\w+)', re.I),
     ('loop',)),
]


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn])\s*[xX]\s*(?=[\dn])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = NAME.search(nm)
    if not m:
        return None
    tail = (m.group(5) or '').strip().rstrip('.')
    if not tail:
        return None
    bad, cap_occ = None, None
    for rx, kinds in TAILS:
        g = rx.fullmatch(tail)
        if g:
            bad = kinds
            if g.groups():
                v = g.group(1).lower()
                cap_occ = int(v) if v.isdigit() else NUM.get(v)
                if cap_occ is None:
                    return None
            break
    if bad is None:
        return None
    W = int(m.group(1) or m.group(2))
    trans = m.group(1) is None
    stay = bool(m.group(3))
    D = []
    for w in re.findall(r'antidiagonal|king-move|horizontal|vertical|diagonal',
                        m.group(4).lower()):
        D += CLASS[w]
    D = sorted(set(D))
    if trans:
        D = sorted({(b, a) for a, b in D})
    if stay:
        D = sorted(set(D) | {(0, 0)})
    if W < 1 or not D:
        return None
    return {'W': W, 'dirs': D, 'stay': stay, 'cap': cap_occ, 'bad': sorted(bad),
            'trans': trans, 'frac': 1}


def forbidden(bad, trans):
    """the set of ordered direction pairs (into a cell, out of it) the entry rules out"""
    sgn = -1 if trans else 1

    def f(d, e):
        if d == (0, 0) or e == (0, 0):
            return False
        if 'straight' in bad and e == d:
            return True
        if 'loop' in bad and e == (-d[0], -d[1]):
            return True
        if 'left' in bad:
            # rows run downward, so the plane vector of (di,dj) is (dj,-di) and a positive
            # cross product is a turn to the left
            if sgn * (d[1] * (-e[0]) - (-d[0]) * e[1]) > 0:
                return True
        return False
    return f


def build(p, cap=20000):
    W = p['W']
    D = [tuple(t) for t in p['dirs']]
    bad = forbidden(p['bad'], p['trans'])
    choices = [[d for d in D if 0 <= j + d[1] < W] for j in range(W)]
    tot = 1
    for c in choices:
        tot *= len(c)
        if tot > 40 * cap:
            return None
    rows = list(product(*choices))

    def emit(prev, cur, nxt):
        """the occupancy row of `cur', or None if this configuration is impossible"""
        for j, (di, dj) in enumerate(cur):
            if di < 0 and prev is None:
                return None
            if di > 0 and nxt is None:
                return None
        for j, d in enumerate(cur):
            di, dj = d
            tgt = cur if di == 0 else (prev if di < 0 else nxt)
            if bad(d, tgt[j + dj]):
                return None
        occ = [0] * W
        for j, (di, dj) in enumerate(cur):
            if di == 0:
                occ[j + dj] += 1
        if prev is not None:
            for j, (di, dj) in enumerate(prev):
                if di == 1:
                    occ[j + dj] += 1
        if nxt is not None:
            for j, (di, dj) in enumerate(nxt):
                if di == -1:
                    occ[j + dj] += 1
        if p['cap'] is not None and any(v > p['cap'] for v in occ):
            return None
        return tuple(occ)

    def step(el, x):
        b = emit(el[0], el[1], x)
        return None if b is None else (b, (el[1], x))

    return imagedet.build([(None, r) for r in rows], rows, step,
                          lambda el: emit(el[0], el[1], None), cap)


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
