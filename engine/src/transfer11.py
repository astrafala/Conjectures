#!/usr/bin/env python3
"""Array conditions that count something GLOBALLY, not cell by cell.

    Number of n X 2 0..2 arrays with some element plus some horizontally or vertically
    adjacent neighbor totalling two exactly once.
    Number of n X 3 binary arrays with some 1 horizontally or vertically adjacent to some
    other 1 exactly once.

The condition is on the whole array: the number of adjacent PAIRS with a stated property is
exactly one (or at most one). A transfer matrix still applies once the running count is put
into the state, capped at two -- "two or more" is absorbing and can never come back.

Each unordered adjacency is represented by one offset with a nonnegative line shift, so every
pair is counted exactly once: the pairs inside a line are counted when that line is laid
down, and the pairs between two lines when the second of them is.
"""
import re
import namecanon
from itertools import product
import transfer6 as T6
from transfer8 import SHAPE2, _dim

DIR1 = {'horizontal': (0, 1), 'vertical': (1, 0), 'diagonal': (1, 1),
        'antidiagonal': (1, -1)}
NUM = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6,
       'seven': 7, 'eight': 8}
DIRW = r'(?:(?:horizontal|vertical|diagonal|antidiagonal)(?:ly)?' \
       r'(?:[,\s]+(?:or\s+|and\s+)?(?:horizontal|vertical|diagonal|antidiagonal)(?:ly)?)*)'

TOTAL = re.compile(r'some element plus some (' + DIRW + r') adjacent neighbou?r totalling '
                   r'(\w+) (exactly once|not more than once|at most once)', re.I)
SAME = re.compile(r'some (\d+) (' + DIRW + r') adjacent to some other (\d+) '
                  r'(exactly once|not more than once|at most once)', re.I)


def _nbset(txt):
    offs = []
    for w in re.split(r'[,\s]+|\bor\b|\band\b', txt.strip().lower()):
        if not w:
            continue
        w = w[:-2] if w.endswith('ly') else w
        if w not in DIR1:
            return None
        if DIR1[w] not in offs:
            offs.append(DIR1[w])
    return offs or None


def _num(s):
    s = s.strip().lower()
    return NUM.get(s, int(s) if s.isdigit() else None)


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
    if d1[0] == 'n' and d2[0] == 'c':
        walk, fixed, base, mult = 'rows', d2[1], d1[1], d1[2]
    elif d2[0] == 'n' and d1[0] == 'c':
        walk, fixed, base, mult = 'cols', d1[1], d2[1], d2[2]
    else:
        return None
    low = rest.lower()
    m = TOTAL.fullmatch(low)
    if m:
        offs = _nbset(m.group(1))
        tot = _num(m.group(2))
        if offs is None or tot is None:
            return None
        kind, dat = 'sum', tot
        tex = rf'x_{{p}}+x_{{q}}={tot}'
    else:
        m = SAME.fullmatch(low)
        if not m or m.group(1) != m.group(3):
            return None
        offs = _nbset(m.group(2))
        if offs is None:
            return None
        kind, dat = 'both', int(m.group(1))
        tex = rf'x_{{p}}=x_{{q}}={dat}'
    once = m.group(4) if kind == 'both' else m.group(3)
    exact = once.startswith('exactly')
    if walk == 'cols':
        offs = [(du, dt) for dt, du in offs]
        offs = [(-dt, -du) if dt < 0 else (dt, du) for dt, du in offs]
    return {'walk': walk, 'fixed': fixed, 'base': base, 'mult': mult, 'alpha': alpha,
            'frac': frac, 'offs': offs, 'kind': kind, 'dat': dat, 'exact': exact,
            'tex': tex, 'nbtex': ',\\ '.join(f'({x},{y})' for x, y in offs), 'rest': rest}


def _pair_ok(v, w, p):
    return (v + w == p['dat']) if p['kind'] == 'sum' else (v == p['dat'] and w == p['dat'])


def _within(r, W, p):
    n = 0
    for dt, du in p['offs']:
        if dt != 0:
            continue
        for u in range(W):
            uu = u + du
            if 0 <= uu < W and _pair_ok(r[u], r[uu], p):
                n += 1
    return n


def _between(r, s, W, p):
    n = 0
    for dt, du in p['offs']:
        if dt != 1:
            continue
        for u in range(W):
            uu = u + du
            if 0 <= uu < W and _pair_ok(r[u], s[uu], p):
                n += 1
    return n


def build(p, cap=200000):
    """States are (line, running count), the count capped at 1.

    Counts of two or more can never come back, so those states are simply absent and the
    edges leading to them are never created. That is what keeps the graph SPARSE: the dense
    version, with a third absorbing state and an edge for every pair of lines, has
    (alpha+1)^(2W) edges and is unusable past a few hundred lines.
    """
    W, al = p['fixed'], p['alpha']
    lines = list(product(range(al + 1), repeat=W))
    if len(lines) * 2 > cap:
        return None
    win = {r: _within(r, W, p) for r in lines}
    idx, st = {}, []
    for r in lines:
        for c in range(2):
            idx[(r, c)] = len(st)
            st.append((r, c))
    adj, end = [], []
    for (r, c) in st:
        row = []
        for s in lines:
            b = win[s]
            if c + b > 1:
                continue
            b += _between(r, s, W, p)
            if c + b <= 1:
                row.append(idx[(s, c + b)])
        adj.append(row)
        end.append(1 if (c == 1 if p['exact'] else True) else 0)
    start = [1 if c == win[r] else 0 for (r, c) in st]
    return adj, start, end, st


def matvec(adj, v):
    return [sum(v[t] for t in row) for row in adj]


def singles(p):
    W, al = p['fixed'], p['alpha']
    n = 0
    for r in product(range(al + 1), repeat=W):
        c = min(2, _within(r, W, p))
        if (c == 1 if p['exact'] else c <= 1):
            n += 1
    return n


def avals(adj, start, end, p, nmax):
    mult, base = p['mult'], p['base']
    Lmax = mult * nmax + base
    # the state already carries one line, so start^T M^(L-1) end counts arrays of L lines:
    # an earlier version used M^(L-2) and returned every value one index late
    vals = {0: p['frac'] if not p['exact'] else 0}
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
