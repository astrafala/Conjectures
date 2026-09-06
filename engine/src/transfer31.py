#!/usr/bin/env python3
"""`Number of (n+1) X (K+1) 0..m arrays with every 2 X 2 subblock <statistic> NONDECREASING
horizontally, vertically and ne-to-sw antidiagonally' and its relatives.

The $2\\times2$ subblocks of an array form a grid, each carries the value of a statistic of
its four entries, and the entry asks that this value not decrease along the named directions
of that grid. Some entries name two statistics, one for the horizontal direction and one for
the vertical.

Every direction moves the subblock row by at most one, so the state is the PAIR of consecutive
array rows --- that pair fixes a whole subblock row --- and one step appends an array row,
which fixes the next subblock row and settles every comparison between the two. An
$(n+1)$-row array is a walk of $n-1$ steps.

The readings were pinned against the entries' own terms before anything was built: `ne-to-sw
antidiagonally' is the offset $(+1,-1)$ on the subblock grid (the offset $(+1,+1)$ gives 164
where the entry publishes 126), `diagonal minus antidiagonal sum' is $(p+s)-(q+r)$ for the
subblock $\\begin{pmatrix}p&q\\\\r&s\\end{pmatrix}$, `ne-sw antidiagonal difference' is $q-r$,
and `nw+se diagonal sum' is $p+s$.
"""
import re
from itertools import product

import namecanon
import transfer17

DIRS = {'horizontally': (0, 1), 'vertically': (1, 0),
        'ne-to-sw antidiagonally': (1, -1), 'antidiagonally ne-to-sw': (1, -1),
        'ne to sw antidiagonally': (1, -1)}

NAME = re.compile(
    r'Number of\s+(?:\(\s*n\s*\+\s*1\s*\)\s*X\s*\(?\s*(\d+)(?:\s*\+\s*(\d+))?\s*\)?|'
    r'\(?\s*(\d+)(?:\s*\+\s*(\d+))?\s*\)?\s*X\s*\(\s*n\s*\+\s*1\s*\))\s*'
    r'0\.\.(\d+)\s+arrays with every 2\s*X\s*2 subblock\s+(.*?)\s*\.?\s*$', re.I)

AGG = r'(diagonal|antidiagonal)\s+(maximum|minimum|sum)'


def _stat(s):
    """a function of (p, q, r, s) = (nw, ne, sw, se), or None"""
    s = re.sub(r'\s+', ' ', s.strip().lower())
    if s == 'sum':
        return lambda b: b[0] + b[1] + b[2] + b[3]
    if s == 'diagonal minus antidiagonal sum':
        return lambda b: (b[0] + b[3]) - (b[1] + b[2])
    if s == 'nw+se diagonal sum':
        return lambda b: b[0] + b[3]
    if s == 'ne-sw antidiagonal difference':
        return lambda b: b[1] - b[2]
    m = re.fullmatch(AGG + r' (plus|minus) ' + AGG, s)
    if not m:
        return None
    sign = 1 if m.group(3) == 'plus' else -1

    def one(which, how):
        pair = (lambda b: (b[0], b[3])) if which == 'diagonal' else (lambda b: (b[1], b[2]))
        if how == 'maximum':
            return lambda b: max(pair(b))
        if how == 'minimum':
            return lambda b: min(pair(b))
        return lambda b: sum(pair(b))
    f1 = one(m.group(1), m.group(2))
    f2 = one(m.group(4), m.group(5))
    return lambda b: f1(b) + sign * f2(b)


def _dirs(s):
    s = re.sub(r'\s+', ' ', s.strip().lower())
    parts = [p.strip() for p in re.split(r',| and ', s) if p.strip()]
    out = []
    for p in parts:
        if p not in DIRS:
            return None
        out.append(DIRS[p])
    return out or None


def _clauses(body):
    """[(statistic, [(di, dj, '<=' or '>='), ...]), ...] or None"""
    body = re.sub(r'\s+', ' ', body.strip().lower())
    chunks = re.split(r'\s+(nondecreasing|nonincreasing)\s+', body)
    if len(chunks) < 3 or len(chunks) % 2 == 0:
        return None
    out = []
    for i in range(0, len(chunks) - 1, 2):
        name = chunks[i]
        rel = chunks[i + 1]
        rest = chunks[i + 2]
        if i + 3 < len(chunks):
            # the tail carries the next clause's statistic after a joining "and"
            m = re.match(r'(.*?)\s+and\s*([^,]*)$', rest)
            if not m:
                return None
            rest, chunks[i + 2] = m.group(1), m.group(2)
            chunks[i + 2] = m.group(2)
        name = re.sub(r'^and ', '', name).strip()
        # ``... nonincreasing horizontally and nondecreasing vertically'' names the statistic
        # once and changes only the relation; an empty name means the previous one again
        f = out[-1][0] if (not name and out) else _stat(name)
        d = _dirs(rest)
        if f is None or d is None:
            return None
        out.append((f, [(a, b, '<=' if rel == 'nondecreasing' else '>=') for a, b in d]))
    return out


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn)])\s*[xX]\s*(?=[\dn(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = NAME.search(nm)
    if not m:
        return None
    if m.group(1) is not None:
        W = int(m.group(1)) + (int(m.group(2)) if m.group(2) else 0)
        trans = False
    else:
        W = int(m.group(3)) + (int(m.group(4)) if m.group(4) else 0)
        trans = True
    alpha = int(m.group(5))
    cl = _clauses(m.group(6))
    if cl is None or W < 2 or alpha < 1:
        return None
    out = []
    for f, cons in cl:
        norm = []
        for di, dj, rel in cons:
            if trans:
                di, dj = dj, di
            if di < 0 or (di == 0 and dj < 0):
                di, dj = -di, -dj
                rel = '<=' if rel == '>=' else '>='
            if di > 1:
                return None
            norm.append((di, dj, rel))
        out.append((f, norm))
    return {'W': W, 'alpha': alpha, 'clauses': out, 'frac': 1}


def build(p, cap=40000):
    W, A, clauses = p['W'], p['alpha'] + 1, p['clauses']
    if A ** (2 * W) > 10 * cap:
        return None
    rows = list(product(range(A), repeat=W))
    K = W - 1                                   # subblocks across

    def srow(f, r, s):
        return tuple(f((r[j], r[j + 1], s[j], s[j + 1])) for j in range(K))

    def okself(rr):
        for f, cons in clauses:
            v = srow(f, *rr)
            for di, dj, rel in cons:
                if di:
                    continue
                for j in range(K):
                    k = j + dj
                    if 0 <= k < K:
                        if (v[j] > v[k]) if rel == '<=' else (v[j] < v[k]):
                            return False
        return True

    ok = [(i, j) for i in range(len(rows)) for j in range(len(rows))
          if okself((rows[i], rows[j]))]
    if not ok or len(ok) > cap:
        return None
    index = {k: n for n, k in enumerate(ok)}
    cache = {}
    for (i, j) in ok:
        cache[(i, j)] = [srow(f, rows[i], rows[j]) for f, _ in clauses]
    nxt = {}
    for (i, j) in ok:
        nxt.setdefault(i, []).append(j)
    adj = []
    for (i, j) in ok:
        u = cache[(i, j)]
        row = []
        for t in nxt.get(j, ()):
            v = cache[(j, t)]
            good = True
            for c, (f, cons) in enumerate(clauses):
                for di, dj, rel in cons:
                    if not di:
                        continue
                    for x in range(K):
                        y = x + dj
                        if 0 <= y < K:
                            if (u[c][x] > v[c][y]) if rel == '<=' else (u[c][x] < v[c][y]):
                                good = False
                                break
                    if not good:
                        break
                if not good:
                    break
            if good:
                row.append(index[(j, t)])
        adj.append(row)
    return ok, adj


terms = transfer17.terms
threshold = transfer17.threshold
