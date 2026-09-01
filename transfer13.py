#!/usr/bin/env python3
"""Neighbour conditions with a symmetry-breaking clause on the ORDER of first occurrences.

    Number of 2 X n 0..3 arrays with no element x(i,j) adjacent to value 3-x(i,j)
    horizontally or antidiagonally, top left element zero, and 1 appearing before 2 in row
    major order.

Two clauses beyond the neighbour condition. "top left element zero" restricts which lines may
begin a walk. "1 appearing before 2 in row major order" is a statement about first
occurrences over the WHOLE array, and for a K X n name the walk runs along columns while row
major order runs along rows, so the two orders disagree: the state carries, for each ROW, a
flag saying which of the two values was seen first in that row, and the array is accepted
when the first row that saw either saw 1.

The neighbour condition is symmetric in the two cells of a pair, so each unordered adjacency
is tested once, from the earlier cell; every offset then points forward and one line of state
suffices.
"""
import re
import namecanon
from itertools import product
import transfer6 as T6
from transfer8 import SHAPE2, _dim
from transfer9 import _nbset, DIRWORDS

COND = re.compile(r'no element x\(i,j\) adjacent to (itself or )?value (\d+)-x\(i,j\) ('
                  + DIRWORDS + r'), top left element zero, and (\d+) appearing before (\d+) '
                  r'in row major order', re.I)


def parse_name(nm):
    nm = namecanon.canon(nm)   # 'a(n) is the number of ...' and friends
    norm = re.sub(r'(\bn|\d|\))\s*[xX]\s*(?=[\d(n])', r'\1 X ', nm)
    norm = re.sub(r'\s+', ' ', norm).strip().rstrip('.')
    norm = re.sub(r'^[^:]{1,90}:\s*', '', norm)
    frac = 1
    m = T6.FRAC.match(norm)
    if m:
        frac = 2 if m.group(1) else (4 if m.group(0).lower().startswith('one quarter')
                                     else int(m.group(2)))
        norm = norm[m.end():]
    else:
        m = T6.HEAD.match(norm)
        if not m:
            return None
        norm = norm[m.end():]
    m = SHAPE2.match(norm)
    if not m:
        return None
    d1, d2 = _dim(m.group(1)), _dim(m.group(2))
    alpha = 1 if m.group(5) else int(m.group(4))
    rest = norm[m.end():].strip().rstrip('.')
    if d1[0] == 'n' and d2[0] == 'c':
        walk, fixed, base, mult = 'rows', d2[1], d1[1], d1[2]
    elif d2[0] == 'n' and d1[0] == 'c':
        walk, fixed, base, mult = 'cols', d1[1], d2[1], d2[2]
    else:
        return None
    m = COND.fullmatch(rest.lower())
    if not m:
        return None
    self_too, c, dirs, pv, qv = m.groups()
    offs = _nbset(dirs)
    if offs is None:
        return None
    if walk == 'cols':
        offs = [(du, dt) for dt, du in offs]
    # the condition is symmetric in the two cells, so one representative per unordered
    # adjacency is enough -- and choosing the forward one makes every offset point ahead
    offs = [(dt, du) for dt, du in offs if dt > 0 or (dt == 0 and du > 0)]
    if not offs:
        return None
    return {'walk': walk, 'fixed': fixed, 'base': base, 'mult': mult, 'alpha': alpha,
            'frac': frac, 'offs': offs, 'c': int(c), 'self': bool(self_too),
            'p': int(pv), 'q': int(qv), 'rest': rest,
            'nbtex': ',\\ '.join(f'({x},{y})' for x, y in offs),
            'tex': (r'x_{t+d_1,\,u+d_2}\ne ' + c + r'-x_{t,u}'
                    + (r'\ \text{ and }\ x_{t+d_1,\,u+d_2}\ne x_{t,u}' if self_too else ''))}


def line_ok(cur, nxt, W, p):
    for u in range(W):
        v = cur[u]
        for dt, du in p['offs']:
            uu = u + du
            if not (0 <= uu < W):
                continue
            L = cur if dt == 0 else nxt
            if L is None:
                continue
            y = L[uu]
            if y == p['c'] - v:
                return False
            if p['self'] and y == v:
                return False
    return True


def _flags(line, fl, p):
    pv, qv = p['p'], p['q']
    if p['walk'] == 'rows':
        if fl[0]:
            return fl
        for x in line:
            if x == pv:
                return (1,)
            if x == qv:
                return (2,)
        return fl
    out = list(fl)
    for r, x in enumerate(line):
        if out[r] == 0:
            if x == pv:
                out[r] = 1
            elif x == qv:
                out[r] = 2
    return tuple(out)


def _accept(fl):
    for f in fl:
        if f:
            return f == 1
    return True                     # neither value occurs: nothing is out of order


def build(p, cap=200000):
    W, al = p['fixed'], p['alpha']
    lines = list(product(range(al + 1), repeat=W))
    nf = W if p['walk'] == 'cols' else 1
    if len(lines) * 3 ** nf > cap:
        return None
    idx, st = {}, []
    for r in lines:
        for fl in product(range(3), repeat=nf):
            idx[(r, fl)] = len(st)
            st.append((r, fl))
    adj, start, end = [], [], []
    for (r, fl) in st:
        row = []
        for s in lines:
            if line_ok(r, s, W, p):
                row.append(idx[(s, _flags(s, fl, p))])
        adj.append(row)
        start.append(1 if (r[0] == 0 and fl == _flags(r, (0,) * nf, p)) else 0)
        end.append(1 if (line_ok(r, None, W, p) and _accept(fl)) else 0)
    return adj, start, end, st


def matvec(adj, v):
    return [sum(v[t] for t in row) for row in adj]


def singles(p):
    W, al = p['fixed'], p['alpha']
    nf = W if p['walk'] == 'cols' else 1
    n = 0
    for r in product(range(al + 1), repeat=W):
        if r[0] != 0 or not line_ok(r, None, W, p):
            continue
        if _accept(_flags(r, (0,) * nf, p)):
            n += 1
    return n


def avals(adj, start, end, p, nmax):
    mult, base = p['mult'], p['base']
    Lmax = mult * nmax + base
    vals = {0: p['frac']}
    g = end[:]
    L = 1
    while L <= Lmax:
        vals[L] = sum(s * x for s, x in zip(start, g) if s)
        g = matvec(adj, g)
        L += 1
    return [vals.get(mult * n + base) if mult * n + base >= 0 else None
            for n in range(nmax + 1)]


def threshold(adj, start, end, coeffs, order, p):
    import time as _t
    mult, base = p['mult'], p['base']
    S = len(adj)
    n_lo = 0
    while mult * n_lo + base < 1:
        n_lo += 1
    o = mult * n_lo + base - 1
    h = end[:]
    for _ in range(o):
        h = matvec(adj, h)
    powers = [h]
    for _ in range(order):
        for _ in range(mult):
            h = matvec(adj, h)
        powers.append(h)
    w = powers[order][:]
    for i, c in coeffs.items():
        pw = powers[order - i]
        for j in range(S):
            w[j] -= c * pw[j]
    t0 = _t.time()
    us, zeros, j = [], 0, 0
    while zeros < S + 1 and j <= 2 * S + order + 8:
        if _t.time() - t0 > 420:
            return None
        u = sum(s * x for s, x in zip(start, w) if s)
        us.append(u)
        zeros = zeros + 1 if u == 0 else 0
        if not any(w):
            zeros = S + 1
            break
        for _ in range(mult):
            w = matvec(adj, w)
        j += 1
    if zeros < S + 1:
        return None
    last = max((i for i, u in enumerate(us) if u != 0), default=-1)
    return n_lo + order + last
