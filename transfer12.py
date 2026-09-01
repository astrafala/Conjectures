#!/usr/bin/env python3
"""Cell conditions allowed to fail at exactly E cells, counted up to relabelling.

    Number of n X 3 0..1 arrays with no element equal to more than one of its horizontal and
    antidiagonal neighbors, with the exception of exactly two elements, and with new values
    introduced in order 0 sequentially upwards.

Three things at once: a cell condition reaching one line up and one line down, a GLOBAL
budget of exactly E cells that may break it, and the canonical-form clause. The state is a
pair of consecutive lines together with the number of offending cells so far, capped at E
(a count past E can never come back, so those states are simply absent); the canonical-form
clause is handled by the falling-factorial inversion, the alphabets here being small enough
that the pattern lumping is not needed.
"""
import re
from itertools import product
from math import comb, factorial
import transfer6 as T6
from transfer7 import derange
from transfer8 import SHAPE2, _dim
from transfer9 import _nbset, DIRWORDS, _nbvals

NUM = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'zero': 0}
COND = re.compile(r'no element (equal|unequal) to (?:(more than|at least|exactly) (\w+) of '
                  r'its|(a strict majority) of its) (' + DIRWORDS + r') neighbou?rs, with '
                  r'the exception of exactly (\w+) elements?, and with new values introduced '
                  r'in order 0 sequentially upwards', re.I)


def parse_name(nm):
    norm = re.sub(r'(\bn|\d|\))\s*[xX]\s*(?=[\d(n])', r'\1 X ', nm)
    norm = re.sub(r'\s+', ' ', norm).strip().rstrip('.')
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
    sense, rel, num, maj, dirs, exc = m.groups()
    offs = _nbset(dirs)
    if offs is None or any(abs(dt) > 1 for dt, _ in offs):
        return None
    E = NUM.get(exc, int(exc) if exc.isdigit() else None)
    if E is None:
        return None
    if maj:
        kind, lim = 'major', None
        tex = (r'2\,\#\{\text{neighbours ' + ('equal to' if sense == 'equal' else
                                             'different from') +
               r' }x_{t,u}\}>\#\{\text{neighbours}\}')
    else:
        k = NUM.get(num, int(num) if num.isdigit() else None)
        if k is None or rel != 'more than':
            return None
        kind, lim = 'count', k
        tex = (r'\#\{\text{neighbours ' + ('equal to' if sense == 'equal' else
                                          'different from') + r' }x_{t,u}\}>' + str(k))
    if walk == 'cols':
        offs = [(du, dt) for dt, du in offs]
    return {'walk': walk, 'fixed': fixed, 'base': base, 'mult': mult, 'alpha': alpha,
            'K': alpha + 1, 'frac': frac, 'offs': offs, 'kind': kind, 'lim': lim,
            'uneq': sense == 'unequal', 'E': E, 'tex': tex,
            'nbtex': ',\\ '.join(f'({x},{y})' for x, y in offs), 'rest': rest}


def _viol_cell(above, cur, below, u, W, p):
    v = cur[u]
    vals = _nbvals(above, cur, below, u, W, p['offs'])
    c = sum(1 for y in vals if ((y != v) if p['uneq'] else (y == v)))
    if p['kind'] == 'major':
        return 2 * c > len(vals)
    return c > p['lim']


def viol(above, cur, below, W, p):
    return sum(1 for u in range(W) if _viol_cell(above, cur, below, u, W, p))


def build(p, cap=200000):
    W, K, E = p['fixed'], p['K'], p['E']
    tot = sum(i ** (2 * W) * (E + 1) for i in range(1, K + 1))
    if tot > cap:
        return None
    idx, st = {}, []
    for i in range(1, K + 1):
        for a in product(range(i), repeat=W):
            for b in product(range(i), repeat=W):
                for v in range(E + 1):
                    idx[(i, a, b, v)] = len(st)
                    st.append((i, a, b, v))
    adj, start, end = [], [], []
    for (i, a, b, v) in st:
        row = []
        for x in product(range(i), repeat=W):
            nv = v + viol(a, b, x, W, p)
            if nv <= E:
                row.append(idx[(i, b, x, nv)])
        adj.append(row)
        w = comb(K, i) * derange(K - i)
        start.append(w if v == viol(None, a, b, W, p) else 0)
        end.append(1 if v + viol(a, b, None, W, p) == E else 0)
    return adj, start, end, st


def matvec(adj, v):
    return [sum(v[t] for t in row) for row in adj]


def singles(p):
    W, K, E = p['fixed'], p['K'], p['E']
    tot = 0
    for i in range(1, K + 1):
        for r in product(range(i), repeat=W):
            if viol(None, r, None, W, p) == E:
                tot += comb(K, i) * derange(K - i)
    return tot


def avals(adj, start, end, p, nmax):
    mult, base, K, E = p['mult'], p['base'], p['K'], p['E']
    Lmax = mult * nmax + base
    vals = {0: factorial(K) * p['frac'] if E == 0 else 0, 1: singles(p)}
    g = end[:]
    L = 2
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
    while mult * n_lo + base < 2:
        n_lo += 1
    o = mult * n_lo + base - 2
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
