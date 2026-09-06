#!/usr/bin/env python3
"""`Number of n X W arrays of OCCUPANCY after each element moves to some <neighbour>.'

Every cell of the grid holds one token. Each token moves to one of the cells named by the
neighbour set --- or stays put, when the entry allows it --- and the OCCUPANCY array records
how many tokens land on each cell. What the entry counts is how many different occupancy
arrays arise, which is the size of an IMAGE: two different assignments of moves that produce
the same occupancy count once.

So this is the subset construction again. The occupancy of row $i$ is decided by the moves
chosen in rows $i-1,i,i+1$, so the pair of consecutive move-rows is the state of a
nondeterministic machine whose output is the occupancy array, and `imagedet' determinises it.
A move that would leave the array is not available, which for the first and last rows depends
on the context; the absent row is carried as a symbol, exactly as in the cell-condition engine,
so the machine knows when `up' or `down' is not a legal move.

Optional clauses handled: `stays put or', `with no occupancy greater than k', `with every
occupancy equal to zero or two', and `without 2-loops' (no two tokens exchanging places).
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
    r'(?:,?\s+(?:but\s+)?with(?:out)?\s+(.*?))?\s*\.?\s*$', re.I)

NUM = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4}


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn])\s*[xX]\s*(?=[\dn])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = NAME.search(nm)
    if not m:
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
    tail = (m.group(5) or '').strip().rstrip('.')
    cap_occ, exact, noloop = None, None, False
    if tail:
        c = re.fullmatch(r'no occupancy greater than (\w+)', tail, re.I)
        if c:
            v = c.group(1).lower()
            cap_occ = int(v) if v.isdigit() else NUM.get(v)
            if cap_occ is None:
                return None
        else:
            c = re.fullmatch(r'every occupancy equal to (\w+) or (\w+)', tail, re.I)
            if c:
                a1 = c.group(1).lower(); a2 = c.group(2).lower()
                a1 = int(a1) if a1.isdigit() else NUM.get(a1)
                a2 = int(a2) if a2.isdigit() else NUM.get(a2)
                if a1 is None or a2 is None:
                    return None
                exact = {a1, a2}
            elif re.fullmatch(r'2-loops', tail, re.I):
                noloop = True
            else:
                return None
    if W < 1 or not D:
        return None
    return {'W': W, 'dirs': D, 'stay': stay, 'cap': cap_occ, 'exact': exact,
            'noloop': noloop, 'frac': 1}


def build(p, cap=20000):
    W = p['W']
    D = [tuple(t) for t in p['dirs']]
    # per column, the moves whose column offset stays inside the array
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
        if p['exact'] is not None and any(v not in p['exact'] for v in occ):
            return None
        if p['noloop']:
            for j, (di, dj) in enumerate(cur):
                k = j + dj
                if di == 0 and cur[k] == (0, -dj):
                    return None
                if di == 1 and nxt is not None and nxt[k] == (-1, -dj):
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
