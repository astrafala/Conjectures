#!/usr/bin/env python3
"""Defective colourings: proper except for a fixed number of monochromatic adjacent pairs.

    Number of defective 3-colorings of an n X 3 0..2 array connected horizontally and
    vertically with exactly one mistake and colors introduced in row-major 0..2 order.

Two things at once, and both have already been solved separately. The number of "mistakes" --
adjacent pairs carrying equal colours -- is a property of the whole array, so it goes into
the state as a running count capped at the budget, with the states past the budget simply
absent. And "colors introduced in row-major order" is the canonical-form clause, removed by
counting equality patterns: K! a(n) = sum_i C(K,i) D_(K-i) L_i(n), each L_i being the count
over an i-letter alphabet.

Each unordered adjacency is represented by one offset with a nonnegative line shift, so every
pair is counted exactly once.
"""
import re
import namecanon
from itertools import product
from math import comb, factorial
from transfer7 import derange
from transfer9 import _nbset, DIRWORDS

NUM = {'one': 1, 'two': 2, 'three': 3, 'four': 4}
NAME = re.compile(r'number of defective (\d+)-colorings of an? '
                  r'(\d*\s*n\s*(?:\+\s*\d+)?|\d+) X (\d*\s*n\s*(?:\+\s*\d+)?|\d+) '
                  r'0\.\.(\d+) array connected (' + DIRWORDS + r') with exactly (\w+) '
                  r'mistakes?,? and colors introduced in row-major 0\.\.(\d+) order', re.I)


def _dim(s):
    s = s.replace(' ', '')
    if 'n' in s:
        a, _, b = s.partition('n')
        return ('n', int(b[1:]) if b.startswith('+') else 0, int(a) if a else 1)
    return ('c', int(s), 1)


def parse_name(nm):
    nm = namecanon.canon(nm)   # 'a(n) is the number of ...' and friends
    norm = re.sub(r'(\bn|\d|\))\s*[xX]\s*(?=[\d(n])', r'\1 X ', nm)
    norm = re.sub(r'\s+', ' ', norm).strip().rstrip('.')
    m = NAME.fullmatch(norm)
    if not m:
        return None
    kcol, dd1, dd2, alpha, dirs, exc, top = m.groups()
    alpha, top = int(alpha), int(top)
    if int(kcol) != alpha + 1 or top != alpha:
        return None
    d1, d2 = _dim(dd1), _dim(dd2)
    if d1[0] == 'n' and d2[0] == 'c':
        walk, fixed, base, mult = 'rows', d2[1], d1[1], d1[2]
    elif d2[0] == 'n' and d1[0] == 'c':
        walk, fixed, base, mult = 'cols', d1[1], d2[1], d2[2]
    else:
        return None
    offs = _nbset(dirs)
    if offs is None:
        return None
    if walk == 'cols':
        offs = [(du, dt) for dt, du in offs]
    offs = [(dt, du) for dt, du in offs if dt > 0 or (dt == 0 and du > 0)]
    E = NUM.get(exc, int(exc) if exc.isdigit() else None)
    if E is None or not offs:
        return None
    return {'walk': walk, 'fixed': fixed, 'base': base, 'mult': mult, 'alpha': alpha,
            'K': alpha + 1, 'frac': 1, 'offs': offs, 'E': E,
            'nbtex': ',\\ '.join(f'({x},{y})' for x, y in offs),
            'tex': r'x_{t,u}=x_{t+d_1,\,u+d_2}', 'rest': norm}


def _within(r, W, p):
    n = 0
    for dt, du in p['offs']:
        if dt:
            continue
        for u in range(W):
            uu = u + du
            if 0 <= uu < W and r[u] == r[uu]:
                n += 1
    return n


def _between(r, s, W, p):
    n = 0
    for dt, du in p['offs']:
        if dt != 1:
            continue
        for u in range(W):
            uu = u + du
            if 0 <= uu < W and r[u] == s[uu]:
                n += 1
    return n


def build(p, cap=200000):
    W, K, E = p['fixed'], p['K'], p['E']
    tot = sum(i ** W for i in range(1, K + 1)) * (E + 1)
    if tot > cap:
        return None
    idx, st = {}, []
    for i in range(1, K + 1):
        for r in product(range(i), repeat=W):
            for c in range(E + 1):
                idx[(i, r, c)] = len(st)
                st.append((i, r, c))
    adj, start, end = [], [], []
    for (i, r, c) in st:
        row = []
        for s in product(range(i), repeat=W):
            b = _within(s, W, p)
            if c + b > E:
                continue
            b += _between(r, s, W, p)
            if c + b <= E:
                row.append(idx[(i, s, c + b)])
        adj.append(row)
        w = comb(K, i) * derange(K - i)
        start.append(w if c == _within(r, W, p) else 0)
        end.append(1 if c == E else 0)
    return adj, start, end, st


def matvec(adj, v):
    return [sum(v[t] for t in row) for row in adj]


def singles(p):
    W, K, E = p['fixed'], p['K'], p['E']
    tot = 0
    for i in range(1, K + 1):
        for r in product(range(i), repeat=W):
            if _within(r, W, p) == E:
                tot += comb(K, i) * derange(K - i)
    return tot


def avals(adj, start, end, p, nmax):
    mult, base, K, E = p['mult'], p['base'], p['K'], p['E']
    Lmax = mult * nmax + base
    vals = {0: factorial(K) if E == 0 else 0}
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
