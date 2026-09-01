#!/usr/bin/env python3
"""Arrays in which all 2 X 2 subblock sums are EQUAL, the common value not being named.

    1/4 the number of (n+1) X 3 binary arrays with all 2 X 2 subblock sums the same.

The common sum is not a free parameter of the array: an array with at least one 2 X 2
subblock determines it. So the count splits as a sum over the possible values,
a(n) = sum_s (number of arrays all of whose subblocks sum to s), with no array counted
twice, and each summand is the ordinary transfer count of transfer6. The whole thing is a
walk count on the block-diagonal matrix over s.
"""
import re
import namecanon
from itertools import product
import transfer6 as T6
from transfer8 import SHAPE2, _dim

NAME = re.compile(r'all 2 X 2 subblock sums the same', re.I)


def parse_name(nm):
    nm = namecanon.canon(nm)   # 'a(n) is the number of ...' and friends
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
    if not NAME.fullmatch(rest):
        return None
    if d1[0] == 'n' and d2[0] == 'c':
        walk, fixed, base, mult = 'rows', d2[1], d1[1], d1[2]
    elif d2[0] == 'n' and d1[0] == 'c':
        walk, fixed, base, mult = 'cols', d1[1], d2[1], d2[2]
    else:
        return None
    if fixed < 2 or base < 1:
        return None                       # with one line or one cross there is no subblock
    return {'walk': walk, 'fixed': fixed, 'base': base, 'mult': mult, 'alpha': alpha,
            'frac': frac, 'rest': rest,
            'tex': r'r_j+r_{j+1}+s_j+s_{j+1}=c\ \text{ for a single }c'}


def build(p, cap=200000):
    W, al = p['fixed'], p['alpha']
    tot = (4 * al + 1) * (al + 1) ** W
    if tot > cap:
        return None
    adj, start, off = [], [], 0
    for s in range(0, 4 * al + 1):
        q = {'walk': p['walk'], 'fixed': W, 'alpha': al, 'noadj': False,
             'pred': (lambda a, b, c, d, s=s: a + b + c + d == s)}
        st, a2 = T6.build(q)
        for row in a2:
            adj.append([off + t for t in row])
        start += [1] * len(st)
        off += len(st)
    return adj, start, None, st


def matvec(adj, v):
    return [sum(v[t] for t in row) for row in adj]


def avals(adj, start, end, p, nmax):
    mult, base = p['mult'], p['base']
    Lmax = mult * nmax + base
    vals = {}
    g = [1] * len(adj)
    L = 1
    while L <= Lmax:
        vals[L] = sum(x for s, x in zip(start, g) if s)
        g = matvec(adj, g)
        L += 1
    return [vals.get(mult * n + base) if mult * n + base >= 1 else None
            for n in range(nmax + 1)]


def threshold(adj, start, end, coeffs, order, p):
    import time as _t
    mult, base = p['mult'], p['base']
    S = len(adj)
    n_lo = 0
    while mult * n_lo + base < 1:
        n_lo += 1
    o = mult * n_lo + base - 1
    h = [1] * S
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
        u = sum(x for s, x in zip(start, w) if s)
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
