#!/usr/bin/env python3
"""Walks of a FIXED number of steps on a board whose SIDE grows.

    Number of 7-step self-avoiding walks on an n X n square summed over all starting positions.
    Number of 3-step one space at a time bishop's tours on an n X n board summed over all
      starting positions.
    Number of 9-step self-avoiding walks on an n X n X n cube summed over all starting
      positions.

The number of steps is fixed and the board grows, so the set of walk SHAPES is finite and does
not depend on n at all.  Fix the move set M of the piece and enumerate every self-avoiding walk
of the stated length in M up to translation.  A shape whose bounding box has sides
(w_1,...,w_d) fits into an n x ... x n board in exactly prod_i max(0, n - w_i) positions -- one
choice of where to put the box in each coordinate -- and distinct (start, walk) pairs are
exactly distinct (shape, placement) pairs.  Hence

    a(n) = sum over shapes of prod_i max(0, n - w_i),

which is exact for every n >= 0 and, once n is at least the largest bounding-box side over all
shapes, is a polynomial of degree d in n.  So (z-1)^(d+1) annihilates the sequence from that
index on; the bound is read off the shapes, not assumed.

A "k-step" walk visits k CELLS, hence makes k-1 moves.  That is not a guess: with k moves the
3-step bishop of A187156 gives 8 where the entry gives 20, and with k-1 moves it gives the
entry's every published term, as does the 7-step self-avoiding walk of A188152.
"""
import re
from functools import lru_cache

# ------------------------------------------------------------------ the pieces
_KING = [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if (a, b) != (0, 0)]
_KNIGHT = [(a, b) for a in (-2, -1, 1, 2) for b in (-2, -1, 1, 2) if abs(a) != abs(b)]
_BISHOP1 = [(a, b) for a in (-1, 1) for b in (-1, 1)]
_BISHOP12 = _BISHOP1 + [(2 * a, 2 * b) for a, b in _BISHOP1]
_ROOK1 = [(1, 0), (-1, 0), (0, 1), (0, -1)]
_ROOK12 = _ROOK1 + [(2, 0), (-2, 0), (0, 2), (0, -2)]
# "one space for components leftwards or up, two space for components rightwards or down":
# the x component is -1 going left and +2 going right, the y component +1 going up and -2 going
# down. The name's own aside -- that the antidiagonal moves become knight moves -- is the check:
# (2,1) and (-1,-2) are knight moves and the other two are not.
_QBISHOP = [(2, 1), (-1, 1), (2, -2), (-1, -2)]
_QROOK = [(-1, 0), (2, 0), (0, 1), (0, -2)]

_PIECE = {
    "one space at a time bishop's tours": _BISHOP1,
    "one or two space at a time bishop's tours": _BISHOP12,
    "one or two space at a time rook's tours": _ROOK12,
    "one or two collinear space at a time queen's tours": _ROOK12 + _BISHOP12,
    "king's tours": _KING,
    # A366829 says "self-avoiding king's tours"; every tour here is self-avoiding, and the
    # entry's own terms agree with the plain king's, so the words are the same condition.
    "self-avoiding king's tours": _KING,
    "king-knight's tours (piece capable of both kinds of moves)": _KING + _KNIGHT,
    "knight's tours": _KNIGHT,
    # "moves only out two, left one": out two in one of the four directions and then one step
    # to the LEFT of that direction -- the chiral half of the knight, four moves not eight.
    "left-handed knight's tours (moves only out two, left one)":
        [(2, 1), (-1, 2), (-2, -1), (1, -2)],
    "S, NW and NE-moving king's tours": [(0, -1), (-1, 1), (1, 1)],
    "E, S, NW and NE-moving king's tours": [(1, 0), (0, -1), (-1, 1), (1, 1)],
    "S, E, and NW-moving king's tours": [(0, -1), (1, 0), (-1, 1)],
    "one space leftwards or up, two space rightwards or down asymmetric rook's tours":
        [(-1, 0), (0, 1), (2, 0), (0, -2)],
    "one space for components leftwards or up, two space for components rightwards or down "
    "asymmetric quasi-bishop's tours (antidiagonal moves become knight moves)": _QBISHOP,
    "one space for components leftwards or up, two space for components rightwards or down "
    "asymmetric quasi-queen's tours (antidiagonal moves become knight moves)":
        _QROOK + _QBISHOP,
}

_BOARD = {'square': 2, 'board': 2, 'cube': 3, '4-cube': 4}

# the side is n, or n+c: "(n+2) X (n+2) board" is the same family with the board two larger
_SIDE = re.compile(r'^\(?n(?:\s*\+\s*(\d+))?\)?$')
NAME = re.compile(
    r"(?i)^Number of (\d+)-step (.+?) on an? (.+?) (square|board|cube|4-cube)"
    r" summed over all starting positions\s*\.?\s*$")


def parse_name(nm):
    nm = ' '.join(nm.split())
    m = NAME.match(nm)
    if not m:
        return None
    cells, piece = int(m.group(1)), m.group(2)
    sides = [t.strip() for t in m.group(3).split(' X ')]
    d = _BOARD.get(m.group(4).lower())
    base = None
    for t in sides:
        mm = _SIDE.match(t)
        if not mm:
            return None
        c = int(mm.group(1) or 0)
        if base is not None and c != base:
            return None                       # a board that is not square in n is not this shape
        base = c
    if d is None or len(sides) != d or cells < 1 or cells > 12:
        return None
    if piece.lower() == 'self-avoiding walks':
        M = [tuple(1 if j == i else 0 for j in range(d)) for i in range(d)]
        M += [tuple(-c for c in v) for v in M]
    else:
        M = _PIECE.get(piece)
        # every named piece here is planar; a three-dimensional bishop is not defined by any of
        # these names and guessing one would be inventing the entry's condition
        if M is None or d != 2:
            return None
    return {'engine': 'boardwalk', 'd': d, 'cells': cells, 'moves': tuple(sorted(M)),
            'base': base, 'frac': 1}


# ------------------------------------------------------------------ the shapes
def _boxes(M, steps, d, cap):
    """bounding boxes of every self-avoiding walk of `steps` moves from the origin, counted."""
    from collections import Counter
    out = Counter()
    zero = (0,) * d
    lo = [0] * d
    hi = [0] * d
    seen = {zero}
    path = [zero]
    n = [0]

    def rec(k):
        if k == steps:
            out[tuple(hi[i] - lo[i] for i in range(d))] += 1
            n[0] += 1
            return n[0] <= cap
        cur = path[-1]
        for mv in M:
            q = tuple(cur[i] + mv[i] for i in range(d))
            if q in seen:
                continue
            old = [(lo[i], hi[i]) for i in range(d)]
            for i in range(d):
                if q[i] < lo[i]:
                    lo[i] = q[i]
                elif q[i] > hi[i]:
                    hi[i] = q[i]
            seen.add(q)
            path.append(q)
            ok = rec(k + 1)
            path.pop()
            seen.discard(q)
            for i in range(d):
                lo[i], hi[i] = old[i]
            if not ok:
                return False
        return True

    if not rec(0):
        return None
    return out


def build(p, cap=4000000):
    b = _boxes(list(p['moves']), p['cells'] - 1, p['d'], cap)
    if b is None:
        return None
    base = p.get('base', 0)
    # the side of the board is n + base, so the count is the polynomial once n + base reaches
    # the largest bounding-box side; the annihilator in force is z^(n0+1) * (z-1)^(d+1), and
    # its degree is the bound the annihilation test needs.
    n0 = max(0, max((max(k) for k in b), default=0) - base)
    return {'boxes': sorted(b.items()), 'd': p['d'], 'n0': n0, 'base': base,
            'S': n0 + p['d'] + 2, 'shapes': sum(b.values())}


def terms(b, N):
    """out[n] is the count on a board of side n + base; the entry's offset is 1."""
    base = b.get('base', 0)
    out = []
    for n in range(N + 2):
        t = 0
        for box, c in b['boxes']:
            f = c
            for w in box:
                f *= max(0, n + base - w)
                if not f:
                    break
            t += f
        out.append(t)
    return out


def threshold(b, coeffs, order):
    S = b['S']
    t = terms(b, 2 * S + order + 30)
    last, run = None, 0
    for j in range(order, len(t)):
        u = t[j] - sum(c * t[j - i] for i, c in coeffs.items())
        if u:
            last, run = j, 0
        else:
            run += 1
    if run < S + order:
        return None
    return last if last is not None else 0
