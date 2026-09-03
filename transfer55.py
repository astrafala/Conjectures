#!/usr/bin/env python3
"""`Number of n X W 0..m arrays with every repeated value in every row and column <relation>
the previous repeated value[, and new values introduced in row-major sequential order]
[, and upper left element zero].'

Read a row from left to right. A REPEATED VALUE is an entry equal to the entry just before it;
the row therefore produces a sequence of repeated values, one for each place where two equal
entries stand side by side, and the entry asks that consecutive members of that sequence stand
in a stated relation --- unequal, equal, greater, greater or equal, one larger modulo `k', not
one larger. The first repeated value of a row has no predecessor and is unconstrained. The same
is asked of every column, read downwards, with its own relation.

Taking the array a slice at a time along the side that grows, one of the two scans runs INSIDE
a slice and is settled as the slice is filled; the other runs ACROSS slices and needs, for each
position, the previous slice's entry (to see whether a repeat happens) and the last repeated
value so far in that scan. So the state is the pair (previous slice, vector of last repeated
values), the second component taking `m+2' values per position with a symbol for `none yet'.

When the entry closes with `new values introduced in row-major sequential order' the count is
of arrays up to renaming. That clause is only compatible with relations built from equality;
those entries are handled by the usual falling-factorial inversion over alphabets of each size,
and an entry whose relation compares letters by size or does arithmetic on them is counted over
its own alphabet instead, exactly as written.
"""
import re
from fractions import Fraction
from itertools import product

import namecanon
import transfer19

SHAPE = r'(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))\s*X\s*(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))'

NAME = re.compile(
    # greedy: the phrase `the previous repeated value' can occur once per clause, and the
    # body runs up to its LAST occurrence
    r'Number of\s+' + SHAPE + r'\s*0\.\.(\d+)\s*arrays with every repeated value in\s+(.*)\s+'
    r'the previous repeated value'
    r'(,\s*and new values introduced in row-major sequential order)?'
    r'(,\s*and upper left element zero)?\s*\.?\s*$', re.I)

INVARIANT = ('eq', 'ne')


def _rel(txt, mod):
    t = re.sub(r'\s+', ' ', txt.strip().lower()).strip(' ,')
    t = re.sub(r'\b(?:to|than)\b\s*$', '', t).strip(' ,')
    m = re.fullmatch(r'(not )?one (larger|smaller)(?: mod (\d+))?', t)
    if m:
        k = int(m.group(3)) if m.group(3) else mod
        if k is None:
            return None, None
        return ('n' if m.group(1) else '') + ('cyc+' if m.group(2) == 'larger' else 'cyc-'), k
    for pat, key in ((r'unequal', 'ne'), (r'equal', 'eq'),
                     (r'greater or equal|greater than or equal', 'ge'),
                     (r'less or equal|less than or equal', 'le'),
                     (r'greater', 'gt'), (r'less', 'lt')):
        if re.fullmatch(pat, t):
            return key, mod
    return None, None


TEST = {
    'eq': lambda a, b, k: a == b,
    'ne': lambda a, b, k: a != b,
    'gt': lambda a, b, k: a > b,
    'ge': lambda a, b, k: a >= b,
    'lt': lambda a, b, k: a < b,
    'le': lambda a, b, k: a <= b,
    'cyc+': lambda a, b, k: a == (b + 1) % k,
    'ncyc+': lambda a, b, k: a != (b + 1) % k,
    'cyc-': lambda a, b, k: a == (b - 1) % k,
    'ncyc-': lambda a, b, k: a != (b - 1) % k,
}


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = NAME.search(nm)
    if not m:
        return None
    ra = m.group(1) or m.group(3)
    rb = int(m.group(2) or 0)
    ca = m.group(4) or m.group(6)
    cb = int(m.group(5) or 0)
    if (ra == 'n') == (ca == 'n'):
        return None
    if ra == 'n':
        W, trans = int(ca) + cb, False
    else:
        W, trans = int(ra) + rb, True
    alpha = int(m.group(7))
    body = m.group(8)
    rel = m.group(9)
    tl0 = bool(m.group(10))
    mod = None
    g = re.search(r'mod (\d+)', body)
    if g:
        mod = int(g.group(1))
    rules = {}
    for chunk in re.split(r',?\s*and in every\s+', body):
        c = re.sub(r'^every\s+', '', chunk.strip())
        c = re.sub(r'\s*the previous repeated value\s*', ' ', c).strip()
        h = re.match(r'(row and column|column and row|row|column)\b\s*(.*)$', c, re.I)
        if not h:
            return None
        k, kk = _rel(h.group(2), mod)
        if k is None:
            return None
        who = h.group(1).lower()
        for w in (('row', 'column') if 'and' in who else (who,)):
            if w in rules:
                return None
            rules[w] = (k, kk)
    if set(rules) != {'row', 'column'} or W < 1:
        return None
    if rel and any(v[0] not in INVARIANT for v in rules.values()):
        return None
    inr, acr = ('row', 'column') if not trans else ('column', 'row')
    return {'W': W, 'alpha': alpha, 'K': alpha + 1, 'inrun': rules[inr], 'across': rules[acr],
            'rel': bool(rel), 'tl0': tl0, 'trans': trans, 'frac': 1}


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


def _one(W, A, p, cap):
    ik, imod = p['inrun']
    ak, amod = p['across']
    fi, fa = TEST[ik], TEST[ak]
    slices = []
    for r in product(range(A), repeat=W):
        last = None
        ok = True
        for q in range(1, W):
            if r[q] == r[q - 1]:
                if last is not None and not fi(r[q], last, imod):
                    ok = False
                    break
                last = r[q]
        if ok:
            slices.append(r)
    if not slices:
        return [], [], 0
    NONE = A                                   # the symbol for `no repeated value yet'
    idx, order, adj, start = {}, [], [], []

    def push(st):
        if st not in idx:
            idx[st] = len(order)
            order.append(st)
            adj.append(None)
            start.append(0)
        return idx[st]

    push((None, (NONE,) * W))
    t = 0
    while t < len(order):
        prev, LR = order[t]
        row = []
        for x in slices:
            if prev is None and p['tl0'] and x[0] != 0:
                continue
            ok = True
            nLR = list(LR)
            if prev is not None:
                for q in range(W):
                    if x[q] == prev[q]:
                        if LR[q] != NONE and not fa(x[q], LR[q], amod):
                            ok = False
                            break
                        nLR[q] = x[q]
            if ok:
                row.append(push((x, tuple(nLR))))
        adj[t] = row
        t += 1
        if len(order) > cap:
            return None, None, None
    n = len(order)
    start[0] = 1
    return adj, start[:n], n


def build(p, cap=40000):
    W, K = p['W'], p['K']
    if K ** W > 40 * cap:
        return None
    if not p['rel']:
        a_i, s_i, S = _one(W, K, p, cap)
        if a_i is None:
            return None
        return a_i, s_i, [1] * S, S, 1
    c = _weights(K)
    den = 1
    for x in c:
        den = den * x.denominator // _gcd(den, x.denominator)
    w = [int(x * den) for x in c]
    adj, start, base = [], [], 0
    for A in range(1, K + 1):
        a_i, s_i, S_i = _one(W, A, p, cap)
        if a_i is None:
            return None
        adj.extend([[k + base for k in row] for row in a_i])
        start.extend([w[A - 1] * v for v in s_i])
        base += S_i
        if base > cap:
            return None
    return adj, start, [1] * base, base, den


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
