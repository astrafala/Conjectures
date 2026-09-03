#!/usr/bin/env python3
"""`Number of (n+1) X W 0..m arrays with each 2 X 2 subblock having clockwise pattern ...',
and the whole family of conditions the encyclopedia states on the four corners of a 2 X 2
subblock read round its perimeter.

Write a subblock as

        p q
        r s

The clockwise cycle is p -> q -> s -> r -> p and the counterclockwise cycle is
p -> r -> s -> q -> p.  `Clockwise edge increases' counts the steps of the first cycle at
which the value goes up, `counterclockwise edge increases' the steps of the second.  Every
undirected edge of the square is walked once by each cycle, in opposite directions, so an
edge contributes to exactly one of the two counts unless its ends are equal:

        cw + ccw = 4 - (number of equal edges).

`Clockwise pattern P' means the four corners read clockwise spell P up to rotation --- the
starting corner is not fixed.  That is forced by the data: with patterns 0000, 0011, 0101
allowed there are 7 two-by-two binary arrays, and 7 is what A259215 publishes, while a fixed
starting corner would give 3.

All of these conditions live inside two consecutive rows, except the ones that compare a
subblock with the subblock above it, which live inside three.  So the walk steps a row at a
time and the state carries the last row together with whatever the vertical comparison needs
to know about the row pair just closed --- the clockwise counts, the counterclockwise counts,
or the increasing direction, one small number per column.  Two conditions are not local at
all: `every subblock has the same number of clockwise edge increases' fixes one value for the
whole array, carried in the state and pinned by the first subblock seen, and `at least two
adjacent blocks having the same increasing direction' is an existential, carried as a single
bit that is set the first time it is witnessed and never cleared.

Rows are extended column by column with pruning rather than tried whole, because the strict
conditions accept so few of them that enumerating all m^W candidates per state would be the
whole cost of the build.
"""
import re
from itertools import product

import namecanon
import transfer19

FRAC = re.compile(r'^\s*(?:(Half)|One quarter|1/(\d+))\s+the number of\s+', re.I)
HEAD = re.compile(r'^\s*Number of\s+', re.I)
DIM = r'(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))'
SHAPE = re.compile(r'^' + DIM + r'\s*X\s*' + DIM +
                   r'\s+(?:(0)\.\.(\d+)|(binary))\s+arrays?\s+(?:with|where)\s+', re.I)

ROWMAX = 200000            # rows enumerated per build, an absolute bound
EMAX = 8000000             # edges built, an absolute bound

_PAT = re.compile(r'^(?:each|every) 2 X 2 subblock having clockwise pattern '
                  r'((?:[01]{4}[ ,]*(?:or )?)+)\.?$', re.I)
_EQ = re.compile(r'^the number of clockwise edge increases in every 2 X 2 subblock equal to '
                 r'the number of counterclockwise edge increases\.?$', re.I)
_LE = re.compile(r'^(?:each|every) 2 X 2 subblock having the number of clockwise edge increases '
                 r'less than or equal to the number of counterclockwise edge increases\.?$', re.I)
_NAE = re.compile(r'^no adjacent elements equal and with (?:each|every) 2 X 2 subblock having '
                  r'the number of clockwise edge increases equal to the number of '
                  r'counterclockwise edge increases\.?$', re.I)
_JMP = re.compile(r'^2 X 2 edge jumps all no more than \+1 in one of the clockwise or '
                  r'counterclockwise directions (or both|but not both)\.?$', re.I)
_STR = re.compile(r'^every 2 X 2 subblock strictly increasing clockwise or counterclockwise '
                  r'with one decrease(, and at least two adjacent blocks having the same '
                  r'increasing direction)?\.?$', re.I)
_DIF = re.compile(r'^every 2 X 2 subblock having one or four distinct clockwise edge '
                  r'differences\.?$', re.I)
_SAME = re.compile(r'^every 2 X 2 subblock has the same number of clockwise edge increases\.?$',
                   re.I)
_MONO2 = re.compile(r'^the number of clockwise edge increases in 2 X 2 subblocks nondecreasing, '
                    r'and counterclockwise edge increases nonincreasing, rightwards and '
                    r'downwards\.?$', re.I)
_MONO1 = re.compile(r'^the number of clockwise edge increases in 2 X 2 subblocks nondecreasing '
                    r'rightwards and downwards\.?$', re.I)
_NBRN = re.compile(r'^no 2 X 2 subblock having the number of clockwise edge increases equal to '
                   r'the number of counterclockwise edge increases in its adjacent leftward or '
                   r'upward neighbors\.?$', re.I)
_NBRE = re.compile(r'^every 2 X 2 subblock having the number of clockwise edge increases equal '
                   r'to the number of counterclockwise edge increases in its adjacent leftward '
                   r'and upward neighbors\.?$', re.I)
_HVE = re.compile(r'^every 2 X 2 subblock having the same number of clockwise edge increases as '
                  r'its horizontal neighbors and the same number of counterclockwise edge '
                  r'increases as its vertical neighbors\.?$', re.I)
_HVN = re.compile(r'^no 2 X 2 subblock having the same number of clockwise edge increases as '
                  r'its horizontal neighbors or the same number of counterclockwise edge '
                  r'increases as its vertical neighbors\.?$', re.I)


def _rots(w):
    return {w[i:] + w[:i] for i in range(4)}


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
    ra, rb, rc, ca, cb, cc = (m.group(1), m.group(2), m.group(3),
                              m.group(4), m.group(5), m.group(6))
    rows = ra or rc
    cols = ca or cc
    # the row count must be the one that grows; the width must be a fixed number
    if rows != 'n' or cols == 'n' or cols is None:
        return None
    W = int(cols) + int(cb or 0)
    alpha = 1 if m.group(9) else int(m.group(8))
    body = s[m.end():].strip()

    p = {'W': W, 'alpha': alpha, 'frac': frac, 'ccw': False, 'noadjeq': False,
         'pats': None, 'mode': None}
    m = _PAT.match(body)
    if m:
        if alpha != 1:
            return None
        words = re.findall(r'[01]{4}', m.group(1))
        pats = set()
        for w in words:
            pats |= _rots(w)
        p['kind'], p['pats'], p['words'] = 'pattern', frozenset(pats), words
        return p
    if _EQ.match(body):
        p['kind'], p['mode'] = 'cmp', 'eq'
        return p
    if _LE.match(body):
        p['kind'], p['mode'] = 'cmp', 'le'
        return p
    if _NAE.match(body):
        p['kind'], p['mode'], p['noadjeq'] = 'cmp', 'eq', True
        return p
    m = _JMP.match(body)
    if m:
        p['kind'] = 'jump'
        p['mode'] = 'xor' if m.group(1).lower().startswith('but') else 'or'
        return p
    m = _STR.match(body)
    if m:
        p['kind'] = 'strict'
        p['mode'] = 'adj' if m.group(1) else 'plain'
        return p
    if _DIF.match(body):
        p['kind'] = 'diffs'
        return p
    if _SAME.match(body):
        p['kind'] = 'samecw'
        return p
    if _MONO2.match(body):
        p['kind'], p['ccw'] = 'mono', True
        return p
    if _MONO1.match(body):
        p['kind'] = 'mono'
        return p
    if _NBRN.match(body):
        p['kind'], p['mode'] = 'nbr', 'ne'
        return p
    if _NBRE.match(body):
        p['kind'], p['mode'] = 'nbr', 'eq'
        return p
    if _HVE.match(body):
        p['kind'], p['mode'] = 'hv', 'eq'
        return p
    if _HVN.match(body):
        p['kind'], p['mode'] = 'hv', 'ne'
        return p
    return None


def build(p, cap=400000):
    W, A = p['W'], p['alpha'] + 1
    kind, mode = p['kind'], p['mode']
    if W < 1 or A < 2 or A ** W > ROWMAX:
        return None
    pats = p['pats']
    noadjeq = p['noadjeq']
    useccw = p['ccw']
    strictadj = kind == 'strict' and mode == 'adj'
    samecw = kind == 'samecw'
    # which per-column number the row pair hands down to the pair below it
    if kind == 'mono':
        VK = 2 if useccw else 1
    elif kind in ('nbr', 'hv'):
        VK = 3                      # counterclockwise count
    elif strictadj:
        VK = 4                      # increasing direction
    else:
        VK = 0

    def loc(a, b, c, d, cw, cc):
        if kind == 'pattern':
            return '%d%d%d%d' % (a, b, d, c) in pats
        if kind == 'cmp':
            return cw == cc if mode == 'eq' else cw <= cc
        if kind == 'jump':
            u = max(b - a, d - b, c - d, a - c) <= 1
            v = max(c - a, d - c, b - d, a - b) <= 1
            return (u or v) if mode == 'or' else (u != v)
        if kind == 'strict':
            if a == b or b == d or d == c or c == a:
                return False
            return cw in (1, 3)
        if kind == 'diffs':
            return len({b - a, d - b, c - d, a - c}) in (1, 4)
        return True

    def hrel(pr, cw, cc):
        if kind == 'mono':
            return pr[0] <= cw and (not useccw or pr[1] >= cc)
        if kind == 'nbr':
            return cw != pr[1] if mode == 'ne' else cw == pr[1]
        if kind == 'hv':
            return pr[0] != cw if mode == 'ne' else pr[0] == cw
        return True

    def vrel(up, cw, cc):
        if kind == 'mono':
            return (up[0] if useccw else up) <= cw and (not useccw or up[1] >= cc)
        if kind == 'nbr':
            return cw != up if mode == 'ne' else cw == up
        if kind == 'hv':
            return cc != up if mode == 'ne' else cc == up
        return True

    def vkey(cw, cc):
        if VK == 1:
            return cw
        if VK == 2:
            return (cw, cc)
        if VK == 3:
            return cc
        return cw                                    # VK == 4: 1 or 3

    idx, order, adj, endv = {}, [], [], []

    def push(st):
        if st not in idx:
            idx[st] = len(order)
            order.append(st)
            adj.append(None)
        return idx[st]

    ex0 = -1 if samecw else 0
    push((None, None, ex0))
    edges = 0
    t = 0
    while t < len(order):
        u, up, ex = order[t]
        out = []
        if u is None:
            for v in product(range(A), repeat=W):
                if noadjeq and any(v[j] == v[j + 1] for j in range(W - 1)):
                    continue
                out.append(push((v, None, ex)))
        else:
            v = [0] * W
            keys = [0] * max(W - 1, 1)

            def rec(j, pr, e):
                if j == W:
                    out.append(push((tuple(v), tuple(keys[:W - 1]) if VK else None, e)))
                    return
                for x in range(A):
                    if noadjeq and (x == u[j] or (j and x == v[j - 1])):
                        continue
                    if j == 0:
                        v[0] = x
                        rec(1, None, e)
                        continue
                    a, b, c, d = u[j - 1], u[j], v[j - 1], x
                    cw = (a < b) + (b < d) + (d < c) + (c < a)
                    cc = (a < c) + (c < d) + (d < b) + (b < a)
                    if not loc(a, b, c, d, cw, cc):
                        continue
                    if pr is not None and not hrel(pr, cw, cc):
                        continue
                    if VK and up is not None and not vrel(up[j - 1], cw, cc):
                        continue
                    e2 = e
                    if samecw:
                        if e == -1:
                            e2 = cw
                        elif e != cw:
                            continue
                    if strictadj and e2 == 0:
                        if (pr is not None and pr[0] == cw) or \
                           (up is not None and up[j - 1] == cw):
                            e2 = 1
                    if VK:
                        keys[j - 1] = vkey(cw, cc)
                    v[j] = x
                    rec(j + 1, (cw, cc), e2)

            rec(0, None, ex)
        adj[t] = out
        edges += len(out)
        t += 1
        if len(order) > cap or edges > EMAX:
            return None
    n = len(order)
    st = [0] * n
    st[0] = 1
    for i in range(n):
        endv.append(1 if not strictadj else (1 if order[i][2] else 0))
    return adj, st, endv, n


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
