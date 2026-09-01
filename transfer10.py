#!/usr/bin/env python3
"""Explicit-offset conditions reaching two lines back, counted up to relabelling.

    Number of n X 3 0..2 arrays with no element equal to any value at offset
    (-1,-1) (-2,0) or (0,-2) and new values introduced in order 0..2.

The offsets are given outright and all point backwards in reading order, but some reach TWO
lines back, so the state is a pair of consecutive lines: the step (a,b) -> (b,x) tests every
cell of the NEW line x against b (one line up) and a (two lines up), and the first two lines
are tested by the start vector with the missing lines absent.

"new values introduced in order 0..k" is the canonical-form clause, so the relabelling
reduction of transfer7 applies verbatim: K! a(n) = sum_i C(K,i) D_(K-i) L_i(n), and each
chain lumps over the equality pattern of the pair.
"""
import re
from itertools import product
from math import comb, factorial
import transfer6 as T6
from transfer7 import rgs, derange, falling, npatterns
from transfer8 import SHAPE2, _dim, _pairs

NAME = re.compile(r'no element equal to any value at offset '
                  r'((?:\(-?\d+,-?\d+\)[\s,]*(?:or\s*)?)+)'
                  r'and new values introduced in order \d+\.\.(\d+)', re.I)


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
    m = NAME.fullmatch(rest)
    if not m:
        return None
    offs = [(int(x), int(y)) for x, y in re.findall(r'\((-?\d+),(-?\d+)\)', m.group(1))]
    if int(m.group(2)) != alpha:
        return None
    if walk == 'cols':
        offs = [(du, dt) for dt, du in offs]
    if any(dt > 0 for dt, _ in offs):
        offs = [(-dt, du) for dt, du in offs]
        if any(dt > 0 for dt, _ in offs):
            return None
    if any(dt < -2 for dt, _ in offs):
        return None
    if any(dt == 0 and du > 0 for dt, du in offs):
        offs = [(dt, -du) if dt == 0 else (dt, du) for dt, du in offs]
    return {'walk': walk, 'fixed': fixed, 'base': base, 'mult': mult, 'alpha': alpha,
            'K': alpha + 1, 'frac': frac, 'offs': offs,
            'tex': (r'x_{t+d_1,\,u+d_2}\ne x_{t,u}\quad\text{for every }(d_1,d_2)\in'
                    r'\mathcal N\text{ inside the array}'),
            'rest': rest}


def line_ok(two, one, cur, W, offs):
    """cells of `cur` against `one` (one line up) and `two` (two lines up)."""
    for u in range(W):
        v = cur[u]
        for dt, du in offs:
            uu = u + du
            if not (0 <= uu < W):
                continue
            L = cur if dt == 0 else (one if dt == -1 else two)
            if L is None:
                continue
            if L[uu] == v:
                return False
    return True


def build(p, cap=200000):
    W, K, offs = p['fixed'], p['K'], p['offs']
    index, plist = {}, []
    for i in range(1, K + 1):
        if npatterns(2 * W, i) > cap:
            return None
        for P in _pairs(W, i):
            index[(i, P)] = len(plist)
            plist.append((i, P))
            if len(plist) > cap:
                return None
    adj, start = [], []
    for i, P in plist:
        vals = list(range(i))
        a, b = P[:W], P[W:]
        cnt = {}
        for x in product(vals, repeat=W):
            if not line_ok(a, b, x, W, offs):
                continue
            q = rgs(b + x)
            j = index.get((i, q))
            if j is not None:
                cnt[j] = cnt.get(j, 0) + 1
        adj.append(list(cnt.items()))
        ok = line_ok(None, None, a, W, offs) and line_ok(None, a, b, W, offs)
        start.append(comb(K, i) * derange(K - i) * falling(i, max(P) + 1) if ok else 0)
    return adj, start, plist


def wmatvec(adj, v):
    return [sum(c * v[t] for t, c in row) for row in adj]


def singles(p):
    W, K, offs = p['fixed'], p['K'], p['offs']
    tot = 0
    for i in range(1, K + 1):
        for r in _pairs(W, i):
            pass
        for r in product(range(i), repeat=W):
            if rgs(r) != r:
                continue
            if line_ok(None, None, r, W, offs):
                tot += comb(K, i) * derange(K - i) * falling(i, max(r) + 1)
    return tot


def avals(adj, start, p, nmax):
    mult, base, K = p['mult'], p['base'], p['K']
    Lmax = mult * nmax + base
    vals = {0: factorial(K) * p['frac'], 1: singles(p)}
    g = [1] * len(adj)
    L = 2
    while L <= Lmax:
        vals[L] = sum(s * x for s, x in zip(start, g) if s)
        g = wmatvec(adj, g)
        L += 1
    return [vals.get(mult * n + base) if mult * n + base >= 0 else None
            for n in range(nmax + 1)]


def threshold(adj, start, coeffs, order, p):
    import time as _t
    mult, base = p['mult'], p['base']
    S = len(adj)
    n_lo = 0
    while mult * n_lo + base < 2:
        n_lo += 1
    o = mult * n_lo + base - 2
    h = [1] * S
    for _ in range(o):
        h = wmatvec(adj, h)
    powers = [h]
    for _ in range(order):
        for _ in range(mult):
            h = wmatvec(adj, h)
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
            w = wmatvec(adj, w)
        j += 1
    if zeros < S + 1:
        return None
    last = max((i for i, u in enumerate(us) if u != 0), default=-1)
    return n_lo + order + last
