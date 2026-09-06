#!/usr/bin/env python3
"""`Number of (n+1) X W 0..m arrays with every 2 X 2 subblock diagonal maximum minus
antidiagonal minimum unequal to its neighbors horizontally, vertically, diagonally and
antidiagonally.'

A subblock of size K is reduced to one number by a statistic read off its two diagonals: writing
d for the main diagonal top-left to bottom-right and t for the antidiagonal, the entries use

    the northeast entry minus the southwest entry           t[0] - t[K-1]
    the northwest entry plus the southeast entry            d[0] + d[K-1]
    max(d) - min(t),  max(d) - max(t),  max(d) + min(t),  sum(d) - sum(t).

The condition is that this number differs from the same number computed at a NEIGHBOURING
subblock, in the directions the entry names --- a neighbour being the subblock one step over,
not a disjoint one. Some entries state two such clauses at once, one statistic against the
horizontal neighbours and another against the vertical, and some impose the same statistic on
2 X 2 and on 3 X 3 subblocks together.

A subblock of size K occupies K consecutive rows and its vertical neighbour occupies the K rows
one lower, so the comparison is settled inside K+1 consecutive rows and nothing wider. The state
is the last K rows; a step tests the topmost subblock of the window it completes; and the
subblocks whose lower neighbour never arrives are exactly the ones that need no test, so the end
vector is all ones.

Transposing the array exchanges the horizontal and vertical directions, fixes the two diagonal
directions, and either fixes each statistic or negates it --- the northeast and southwest
entries swap. Negating both sides of an inequality changes nothing, so a transposed entry is the
same problem with the two directions exchanged.
"""
import re
from itertools import product

import namecanon
import transfer19

FRAC = re.compile(r'^\s*(?:(Half)|One quarter|1/(\d+))\s+the number of\s+', re.I)
HEAD = re.compile(r'^\s*Number of\s+', re.I)
SH = r'(?:\((?P<ra>n|\d+)\s*\+\s*(?P<rb>\d+)\)|(?P<rc>n|\d+))\s*X\s*' \
     r'(?:\((?P<ca>n|\d+)\s*\+\s*(?P<cb>\d+)\)|(?P<cc>n|\d+))'
SHAPE = re.compile(r'^' + SH + r'\s+(?:0\.\.(?P<m>\d+)|(?P<bin>binary))\s+arrays?\s+with\s+',
                   re.I)

STAT = [(r'ne-sw antidiagonal difference', 'nesw'),
        (r'nw\+se diagonal sum', 'nwse'),
        (r'diagonal maximum minus antidiagonal minimum', 'dmax-amin'),
        (r'diagonal maximum minus antidiagonal maximum', 'dmax-amax'),
        (r'diagonal maximum plus antidiagonal minimum', 'dmax+amin'),
        (r'diagonal sum minus antidiagonal sum', 'dsum-asum')]
DIRW = re.compile(r'\b(?:ne\+sw )?(antidiagonal|diagonal|horizontal|vertical)(?:ly)?\b', re.I)
DVEC = {'horizontal': (0, 1), 'vertical': (1, 0), 'diagonal': (1, 1), 'antidiagonal': (1, -1)}
SIZES = re.compile(r'every ((?:\d+ X \d+)(?: and \d+ X \d+)*) subblock ', re.I)


def _stat(kind, d, t):
    if kind == 'nesw':
        return t[0] - t[-1]
    if kind == 'nwse':
        return d[0] + d[-1]
    if kind == 'dmax-amin':
        return max(d) - min(t)
    if kind == 'dmax-amax':
        return max(d) - max(t)
    if kind == 'dmax+amin':
        return max(d) + min(t)
    return sum(d) - sum(t)


def parse_name(nm):
    nm = namecanon.canon(nm)
    s = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    frac = 1
    m = FRAC.match(s)
    if m:
        frac = 2 if m.group(1) else (4 if m.group(0).lower().startswith('one quarter')
                                     else int(m.group(2)))
        s = s[m.end():]
    else:
        m = HEAD.match(s)
        if not m:
            return None
        s = s[m.end():]
    m = SHAPE.match(s)
    if not m:
        return None
    rows = m.group('ra') or m.group('rc')
    cols = m.group('ca') or m.group('cc')
    if rows is None or cols is None or (rows == 'n') == (cols == 'n'):
        return None
    if rows == 'n':
        W, trans = int(cols) + int(m.group('cb') or 0), False
    else:
        W, trans = int(rows) + int(m.group('rb') or 0), True
    alpha = 1 if m.group('bin') else int(m.group('m'))
    body = s[m.end():].strip().rstrip('.')

    mm = SIZES.match(body)
    if not mm:
        return None
    ks = [int(x) for x in re.findall(r'(\d+) X \d+', mm.group(1))]
    if not ks or any(k < 2 for k in ks):
        return None
    for a, b in zip(re.findall(r'(\d+) X (\d+)', mm.group(1)), ks):
        if int(a[0]) != int(a[1]):
            return None                        # only square subblocks are read here
    rest = body[mm.end():]
    clauses = []
    for piece in re.split(r'\s+and\s+(?=(?:ne-sw|nw\+se|diagonal)\b)', rest):
        piece = piece.strip()
        for rx, kind in STAT:
            m2 = re.match(rx + r'\s+unequal to its neighbou?rs\s+(.*)$', piece, re.I)
            if m2:
                ws = [w.lower() for w in dict.fromkeys(DIRW.findall(m2.group(1)))]
                if not ws:
                    return None
                clauses.append((kind, ws))
                break
        else:
            return None
    if not clauses:
        return None
    if trans:
        clauses = [(k, ['vertical' if w == 'horizontal' else
                        'horizontal' if w == 'vertical' else w for w in ws])
                   for k, ws in clauses]
    return {'W': W, 'alpha': alpha, 'ks': sorted(set(ks)),
            'clauses': [(k, sorted(ws)) for k, ws in clauses],
            'trans': trans, 'frac': frac}


def build(p, cap=400000):
    W, A = p['W'], p['alpha'] + 1
    K = max(p['ks'])
    if A ** W > 200000:
        return None
    rows = list(product(range(A), repeat=W))

    def blockstat(win, top, j, k, kind):
        """The statistic of the k X k subblock whose top-left cell is win[top][j], or None when
        the subblock does not fit inside the window or the array."""
        if top < 0 or top + k > len(win) or j < 0 or j + k > W:
            return None
        for t in range(k):
            if win[top + t] is None:
                return None
        d = [win[top + t][j + t] for t in range(k)]
        a = [win[top + t][j + k - 1 - t] for t in range(k)]
        return _stat(kind, d, a)

    def win_ok(win):
        """Test every comparison whose two subblocks both lie inside this window. Comparisons
        get tested more than once as the window slides, which costs nothing and guarantees that
        every comparison in the array is tested: each one lies inside K+1 consecutive rows, and
        every K+1 consecutive rows are a window at some step."""
        for k in p['ks']:
            for kind, ws in p['clauses']:
                for top in range(len(win) - k + 1):
                    for j in range(W - k + 1):
                        s = blockstat(win, top, j, k, kind)
                        if s is None:
                            continue
                        for w in ws:
                            di, dj = DVEC[w]
                            s2 = blockstat(win, top + di, j + dj, k, kind)
                            if s2 is not None and s2 == s:
                                return False
        return True

    idx, order, adj, endv = {}, [], [], []

    def push(st):
        if st not in idx:
            idx[st] = len(order)
            order.append(st)
            adj.append(None)
            endv.append(None)
        return idx[st]

    push((None,) * K)
    t = 0
    while t < len(order):
        st = order[t]
        out = []
        for v in rows:
            win = st + (v,)
            if win_ok(win):
                out.append(push(win[1:]))
        adj[t] = out
        # an array of exactly K rows forms no window of K+1, so its own comparisons are tested
        # here instead; for a longer array this repeats a test already passed
        endv[t] = 1 if win_ok(st) else 0
        t += 1
        if len(order) > cap:
            return None
    n = len(order)
    sv = [0] * n
    sv[0] = 1
    return adj, sv, endv[:n], n


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
