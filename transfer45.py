#!/usr/bin/env python3
"""`... arrays with every consecutive three elements in every <direction> having <k> distinct
values ..., and new values 0 upwards introduced in row major order.'

Four families of triples run through the array --- along a row, down a column, and along the
two diagonals --- and each direction carries its own condition on how many DISTINCT values its
triples may hold. Nothing compares letters or does arithmetic on them, so the whole condition
is invariant under permuting the alphabet, and the relabelling clause can be handled the usual
way: count over an alphabet of each size and invert the falling-factorial triangle.

Every triple lies inside three consecutive rows, so a pair of consecutive rows is a state and
the walk is over the pairs. That state space is `A^(2W)' before pruning, which is out of reach
past the narrowest arrays, and the symmetry is used a second time to cut it: the transfer
matrix commutes with the action of the symmetric group on the alphabet, so the walk may be run
on ORBITS of pairs --- that is, on the PATTERNS of the pair, its partition into equal-letter
positions --- with the start vector weighted by the orbit size. That is a factor of up to
`A!' and it is what makes the wider arrays reachable.
"""
import re
from fractions import Fraction

import namecanon
import transfer19

DIRS = ('row', 'column', 'diagonal', 'antidiagonal')
NUM = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'zero': 0}
ALL = frozenset((1, 2, 3))

CLAUSE = re.compile(
    r'every\s+((?:row|column|antidiagonal|nw-se diagonal|diagonal)'
    r'(?:\s*,\s*|\s+and\s+|\s+)*(?:(?:row|column|antidiagonal|nw-se diagonal|diagonal)'
    r'(?:\s*,\s*|\s+and\s+|\s+)*)*)'
    r'(not\s+)?(?:having\s+)?(?:exactly\s+)?'
    r'(\w+)(?:\s+or\s+(\w+))?\s+distinct\s+values', re.I)

HEAD = re.compile(
    r'Number of\s+\((\w+)\+(\d+)\)\s*X\s*\((\w+)\+(\d+)\)\s*0\.\.(\d+)\s*arrays with\s+'
    r'every consecutive three elements in\s+(.*?),?\s*and new values 0 upwards introduced in '
    r'row major order\s*\.?\s*$', re.I)


def _val(w):
    w = w.lower()
    return int(w) if w.isdigit() else NUM.get(w)


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = HEAD.search(nm)
    if not m:
        return None
    ra, rb, ca, cb, mm = m.group(1), int(m.group(2)), m.group(3), int(m.group(4)), int(m.group(5))
    if (ra == 'n') == (ca == 'n'):
        return None
    if ra == 'n':
        along, fixed = 'rows', cb + (0 if ca == 'n' else int(ca))
    else:
        along, fixed = 'cols', rb + (0 if ra == 'n' else int(ra))
    body = m.group(6)
    cond = {}
    seen = 0
    for g in CLAUSE.finditer(body):
        words = re.findall(r'antidiagonal|nw-se diagonal|diagonal|column|row', g.group(1).lower())
        a, b = _val(g.group(3)), (_val(g.group(4)) if g.group(4) else None)
        if a is None or (g.group(4) and b is None):
            return None
        s = frozenset((a,) if b is None else (a, b))
        if g.group(2):
            s = ALL - s
        for w in words:
            d = 'diagonal' if w == 'nw-se diagonal' else w
            if d in cond and cond[d] != s:
                return None
            cond[d] = s
            seen += 1
    if seen == 0 or len(body.split()) > 4 * seen + 24:
        return None
    if along == 'cols':
        cond = {('column' if k == 'row' else 'row' if k == 'column' else k): v
                for k, v in cond.items()}
    if fixed < 1:
        return None
    return {'W': fixed, 'cond': {k: sorted(v) for k, v in cond.items()},
            'alpha': mm, 'K': mm + 1, 'trans': along == 'cols'}


def _ok(cond, key, a, b, c):
    s = cond.get(key)
    return s is None or len({a, b, c}) in s


def _rows(W, A, cond):
    """every row of width W over A letters whose own triples pass"""
    out, cur = [], []

    def go(j):
        if j == W:
            out.append(tuple(cur))
            return
        for v in range(A):
            if j >= 2 and not _ok(cond, 'row', cur[j - 2], cur[j - 1], v):
                continue
            cur.append(v)
            go(j + 1)
            cur.pop()
    go(0)
    return out


def _pattern(t):
    """the orbit of a tuple under relabelling: first occurrences renumbered 0,1,2,..."""
    seen, out = {}, []
    for v in t:
        if v not in seen:
            seen[v] = len(seen)
        out.append(seen[v])
    return tuple(out), len(seen)


def _succ(r0, r1, W, A, cond):
    """every row r2 completing the window, generated column by column with pruning"""
    out, cur = [], []

    def go(j):
        if j == W:
            out.append(tuple(cur))
            return
        for v in range(A):
            if not _ok(cond, 'column', r0[j], r1[j], v):
                continue
            if j >= 2 and not _ok(cond, 'row', cur[j - 2], cur[j - 1], v):
                continue
            if j >= 2 and not _ok(cond, 'diagonal', r0[j - 2], r1[j - 1], v):
                continue
            if j + 2 < W and not _ok(cond, 'antidiagonal', r0[j + 2], r1[j + 1], v):
                continue
            cur.append(v)
            go(j + 1)
            cur.pop()
    go(0)
    return out


def _falling(A, p):
    v = 1
    for t in range(p):
        v *= A - t
    return v


def _one(W, A, cond, cap):
    """the lumped digraph for one alphabet size: (adj, start, S) with an all-ones end"""
    rows = _rows(W, A, cond)
    if not rows:
        return [], [], 0
    idx, adj, start, order = {}, [], [], []

    def push(pat, p):
        if pat not in idx:
            idx[pat] = len(order)
            order.append((pat, p))
            adj.append(None)
            start.append(0)
        return idx[pat]

    for r0 in rows:
        for r1 in rows:
            pat, p = _pattern(r0 + r1)
            if p > A:
                continue
            i = push(pat, p)
            if start[i] == 0:
                start[i] = _falling(A, p)
        if len(order) > cap:
            return None, None, None
    t = 0
    while t < len(order):
        pat, p = order[t]
        r0, r1 = pat[:W], pat[W:]
        row = []
        for r2 in _succ(r0, r1, W, A, cond):
            q, pq = _pattern(r1 + r2)
            if pq > A:
                continue
            row.append(push(q, pq))
        adj[t] = row
        t += 1
        if len(order) > cap:
            return None, None, None
    return adj, start, len(order)


def _weights(K):
    """the rational c with a = sum_i c_i L_i for patterns of at most K letters"""
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
        piv = next(r for r in range(col, n) if A[r][col] != 0)
        A[col], A[piv] = A[piv], A[col]
        d = A[col][col]
        A[col] = [x / d for x in A[col]]
        for r in range(n):
            if r != col and A[r][col] != 0:
                f = A[r][col]
                A[r] = [x - f * y for x, y in zip(A[r], A[col])]
    return [A[r][n] for r in range(n)]


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def build(p, cap=40000):
    W, K, cond = p['W'], p['K'], p['cond']
    c = _weights(K)
    den = 1
    for x in c:
        den = den * x.denominator // _gcd(den, x.denominator)
    w = [int(x * den) for x in c]
    adj, start, base = [], [], 0
    for A in range(1, K + 1):
        a_i, s_i, S_i = _one(W, A, cond, cap)
        if a_i is None:
            return None
        adj.extend([[k + base for k in row] for row in a_i])
        start.extend([w[A - 1] * x for x in s_i])
        base += S_i
        if base > cap:
            return None
    return adj, start, [1] * base, base, den


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
