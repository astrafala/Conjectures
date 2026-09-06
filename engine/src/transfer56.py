#!/usr/bin/env python3
"""`... arrays with no increasing sequence of length 3 horizontally or antidiagonally
downwards' and `... arrays with no occurrence of three equal elements in a row horizontally,
vertically or nw-to-se diagonally, and new values 0..m introduced in row major order.'

Two conditions of the same shape: a RUN of `L' consecutive cells taken along one of the four
directions of the grid is forbidden when its entries are strictly increasing, in the first
family, or all equal, in the second. Each direction moves the row index by at most one and
`L' is three, so every run lies inside three consecutive array rows and the state is the
window of the last two, a row not yet written carried as a symbol.

The second family closes with `new values introduced in row major order', so it counts arrays
up to renaming. That is legitimate here and only here: `all equal' is a statement about
equality and survives any permutation of the alphabet, while `strictly increasing' compares
letters by size and does not. An entry naming an increasing run together with a renaming
clause would be refused; none occurs.
"""
import re
from fractions import Fraction
from itertools import product

import namecanon
import transfer19

DIRW = [(r'nw-to-se diagonally|diagonally downwards|diagonally', (1, 1)),
        (r'ne-to-sw antidiagonally|antidiagonally downwards|antidiagonally', (1, -1)),
        (r'horizontally', (0, 1)),
        (r'vertically', (1, 0))]
DIRRX = re.compile('|'.join('(?:%s)' % w for w, _ in DIRW), re.I)
NUM = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6}

SHAPE = r'(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))\s*X\s*(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))'

INC = re.compile(
    r'Number of\s+' + SHAPE + r'\s*0\.\.(\d+)\s*arrays with no increasing sequence of length\s+'
    r'(\w+)\s+(.*?)\s*\.?\s*$', re.I)
EQ = re.compile(
    r'Number of\s+' + SHAPE + r'\s*0\.\.(\d+)\s*arrays with no occurrence of\s+(\w+)\s+equal '
    r'elements in a row\s+(.*?)'
    r'(?:,\s*and new values 0\.\.(\d+) introduced in row major order)?\s*\.?\s*$', re.I)


def _dirs(txt, trans):
    out = []
    for h in DIRRX.finditer(txt):
        w = h.group(0).lower()
        for pat, off in DIRW:
            if re.fullmatch(r'(?:%s)' % pat, w, re.I):
                out.append(off)
                break
    if not out:
        return None
    if trans:
        out = [(b, a) for a, b in out]
    # normalise every direction to point DOWNWARDS, remembering when that reverses it: an
    # increasing run read one way is a decreasing run read the other, so the flag matters
    fixed = set()
    for a, b in out:
        if a < 0 or (a == 0 and b < 0):
            fixed.add((-a, -b, True))
        else:
            fixed.add((a, b, False))
    return sorted(fixed)


def _shape(m):
    ra = m.group(1) or m.group(3)
    rb = int(m.group(2) or 0)
    ca = m.group(4) or m.group(6)
    cb = int(m.group(5) or 0)
    if (ra == 'n') == (ca == 'n'):
        return None
    if ra == 'n':
        return int(ca) + cb, False
    return int(ra) + rb, True


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    for kind, rx in (('inc', INC), ('eq', EQ)):
        m = rx.search(nm)
        if not m:
            continue
        sh = _shape(m)
        if not sh:
            return None
        W, trans = sh
        alpha = int(m.group(7))
        w = m.group(8).lower()
        L = int(w) if w.isdigit() else NUM.get(w)
        D = _dirs(m.group(9), trans)
        rel = kind == 'eq' and m.group(10) is not None
        if rel and int(m.group(10)) != alpha:
            return None
        left = DIRRX.sub('', m.group(9))
        left = re.sub(r'\bor\b|\band\b|,|\s+', '', left, flags=re.I)
        if left or L is None or L < 2 or D is None or W < 1:
            return None
        if kind == 'inc' and rel:
            return None
        return {'W': W, 'alpha': alpha, 'K': alpha + 1, 'kind': kind, 'L': L, 'dirs': D,
                'rel': rel, 'trans': trans, 'frac': 1}
    return None


def _weights(K):
    F = [[Fraction(0)] * (K + 1) for _ in range(K + 1)]
    for i in range(1, K + 1):
        for j in range(1, K + 1):
            v = Fraction(1)
            for t in range(j):
                v *= (i - t)
            F[i][j] = v
    A = [[F[i][j] for i in range(1, K + 1)] + [Fraction(1)] for j in range(1, K + 1)]
    n = K
    for col in range(n):
        piv = next(t for t in range(col, n) if A[t][col] != 0)
        A[col], A[piv] = A[piv], A[col]
        d = A[col][col]
        A[col] = [x / d for x in A[col]]
        for t in range(n):
            if t != col and A[t][col] != 0:
                f = A[t][col]
                A[t] = [x - f * y for x, y in zip(A[t], A[col])]
    return [A[t][n] for t in range(n)]


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def _bad(kind, vals, rev):
    if kind == 'eq':
        return all(v == vals[0] for v in vals)
    if rev:
        vals = vals[::-1]
    return all(vals[t] < vals[t + 1] for t in range(len(vals) - 1))


def _one(W, A, p, cap):
    L, D, kind = p['L'], [tuple(t) for t in p['dirs']], p['kind']
    rows = []
    for r in product(range(A), repeat=W):
        ok = True
        for di, dj, rev in D:
            if di:
                continue
            for j in range(W):
                cols = [j + dj * t for t in range(L)]
                if any(c < 0 or c >= W for c in cols):
                    continue
                if _bad(kind, [r[c] for c in cols], rev):
                    ok = False
                    break
            if not ok:
                break
        if ok:
            rows.append(r)
    if not rows:
        return [], 0
    idx, order, adj = {}, [], []

    def push(st):
        if st not in idx:
            idx[st] = len(order)
            order.append(st)
            adj.append(None)
        return idx[st]

    push((None,) * (L - 1))
    t = 0
    while t < len(order):
        win = order[t] + (None,)
        row = []
        for x in rows:
            w = order[t] + (x,)
            ok = True
            for di, dj, rev in D:
                if di == 0:
                    continue
                if any(s is None for s in w):
                    continue
                for j in range(W):
                    cols = [j - dj * (L - 1 - s) for s in range(L)]
                    if any(c < 0 or c >= W for c in cols):
                        continue
                    if _bad(kind, [w[s][cols[s]] for s in range(L)], rev):
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                row.append(push(w[1:]))
        adj[t] = row
        t += 1
        if len(order) > cap:
            return None, None
    return adj, len(order)


def build(p, cap=40000):
    W, K = p['W'], p['K']
    if K ** W > 40 * cap:
        return None
    if not p['rel']:
        a_i, S = _one(W, K, p, cap)
        if a_i is None:
            return None
        st = [0] * S
        if S:
            st[0] = 1
        return a_i, st, [1] * S, S, 1
    c = _weights(K)
    den = 1
    for x in c:
        den = den * x.denominator // _gcd(den, x.denominator)
    w = [int(x * den) for x in c]
    adj, start, base = [], [], 0
    for A in range(1, K + 1):
        a_i, S_i = _one(W, A, p, cap)
        if a_i is None:
            return None
        adj.extend([[k + base for k in row] for row in a_i])
        s_i = [0] * S_i
        if S_i:
            s_i[0] = w[A - 1]
        start.extend(s_i)
        base += S_i
        if base > cap:
            return None
    return adj, start, [1] * base, base, den


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
