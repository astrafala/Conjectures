#!/usr/bin/env python3
"""The 3 X 3 half of the monotone-subblock family.

`Number of (n+2) X W 0..m arrays with every 3 X 3 subblock <statistic> nondecreasing
horizontally, vertically and ne-to-sw antidiagonally.'

A $3\\times3$ subblock has four distinguished lines --- its diagonal, its antidiagonal, its
central row and its central column, three cells each --- and the statistics of this family are
signed sums of aggregates (sum, maximum, minimum, median) taken over those lines: `sum of the
medians of the diagonal and antidiagonal minus the two sums of the central row and column',
and so on.

A subblock spans three array rows and the vertical comparison spans four, so the naive state is
three consecutive rows, which is out of reach past a narrow array. It is not needed: what the
next step actually consults is the last TWO rows (to build the new subblock row) and the
PREVIOUS SUBBLOCK ROW (to compare against). Carrying the subblock row itself instead of the
third array row collapses all the third rows that produce the same statistics into one state.
The starting vector is then weighted, one unit for each array row that produced the state.
"""
import re
from itertools import product

import namecanon
import transfer19

LINE = r'(?:the\s+)?(?:central\s+row|central\s+column|diagonal|antidiagonal|row|column)'
LINELIST = LINE + r'(?:\s*,\s*' + LINE + r')*(?:\s+and\s+' + LINE + r')?'
AGG = r'(sums|maximums|minimums|medians|sum|maximum|minimum|median)'
T0 = re.compile(r'(?:the\s+)?sum\s+of\s+the\s+' + AGG + r'\s+of\s+(?:the\s+)?(' + LINELIST + r')')
T1 = re.compile(r'(?:the\s+)?(?:two|three|four)?\s*' + AGG + r'\s+of\s+(?:the\s+)?(' + LINELIST + r')')
T2 = re.compile(r'(diagonal|antidiagonal|central\s+row|central\s+column)\s+' + AGG)
OP = re.compile(r'\s+(plus|minus|and)\s+')

DIRS = {'horizontally': (0, 1), 'vertically': (1, 0),
        'ne-to-sw antidiagonally': (1, -1), 'antidiagonally ne-to-sw': (1, -1)}

NAME = re.compile(
    r'Number of\s+(?:\(\s*n\s*\+\s*2\s*\)\s*X\s*\(?\s*(\d+)(?:\s*\+\s*(\d+))?\s*\)?|'
    r'\(?\s*(\d+)(?:\s*\+\s*(\d+))?\s*\)?\s*X\s*\(\s*n\s*\+\s*2\s*\))\s*'
    r'0\.\.(\d+)\s+arrays with every 3\s*X\s*3 subblock\s+(.*?)\s*\.?\s*$', re.I)


def _lines(s):
    out = []
    for p in re.split(r'\s*,\s*|\s+and\s+', s.strip()):
        p = re.sub(r'^the\s+', '', p.strip())
        if p == 'diagonal':
            out.append('diag')
        elif p == 'antidiagonal':
            out.append('anti')
        elif p in ('central row', 'row'):
            out.append('crow')
        elif p in ('central column', 'column'):
            out.append('ccol')
        else:
            return None
    return out or None


def _term(s):
    for rx, gi in ((T0, 2), (T1, 2)):
        m = rx.match(s)
        if m:
            L = _lines(m.group(gi))
            if L:
                return (m.group(1).rstrip('s'), L), s[m.end():]
    m = T2.match(s)
    if m:
        w = re.sub(r'\s+', ' ', m.group(1))
        nm = {'diagonal': 'diag', 'antidiagonal': 'anti',
              'central row': 'crow', 'central column': 'ccol'}[w]
        return (m.group(2).rstrip('s'), [nm]), s[m.end():]
    return None


def _expr(s):
    s = re.sub(r'\s+', ' ', s.strip().lower())
    s = re.sub(r'^sum of ', '', s)
    out, sign = [], 1
    while True:
        r = _term(s)
        if not r:
            return None
        (agg, L), s = r
        out.append((sign, agg, L))
        if not s.strip():
            return out
        m = OP.match(s)
        if not m:
            return None
        sign = -1 if m.group(1) == 'minus' else 1
        s = s[m.end():]


def _dirs(s):
    parts = [p.strip() for p in re.split(r',| and ', re.sub(r'\s+', ' ', s.strip().lower()))
             if p.strip()]
    out = []
    for p in parts:
        if p not in DIRS:
            return None
        out.append(DIRS[p])
    return out or None


def _clauses(body):
    body = re.sub(r'\s+', ' ', body.strip().lower())
    chunks = re.split(r'\s+(nondecreasing|nonincreasing)\s+', body)
    if len(chunks) < 3 or len(chunks) % 2 == 0:
        return None
    out = []
    for i in range(0, len(chunks) - 1, 2):
        name, rel, rest = chunks[i], chunks[i + 1], chunks[i + 2]
        if i + 3 < len(chunks):
            m = re.match(r'(.*?)\s+and\s*([^,]*)$', rest)
            if not m:
                return None
            rest = m.group(1)
            chunks[i + 2] = m.group(2)
        name = re.sub(r'^and ', '', name).strip()
        e = out[-1][0] if (not name and out) else _expr(name)
        d = _dirs(rest)
        if e is None or d is None:
            return None
        out.append((e, [(a, b, '<=' if rel == 'nondecreasing' else '>=') for a, b in d]))
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
    if cl is None or W < 3 or alpha < 1:
        return None
    out = []
    for e, cons in cl:
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
        out.append((e, norm))
    return {'W': W, 'alpha': alpha, 'clauses': out, 'frac': 1}


def _agg(kind, vals):
    if kind == 'sum':
        return sum(vals)
    if kind == 'maximum':
        return max(vals)
    if kind == 'minimum':
        return min(vals)
    return sorted(vals)[len(vals) // 2]


def _value(expr, c):
    """c is the 3 x 3 block as a tuple of three triples"""
    L = {'diag': (c[0][0], c[1][1], c[2][2]), 'anti': (c[0][2], c[1][1], c[2][0]),
         'crow': (c[1][0], c[1][1], c[1][2]), 'ccol': (c[0][1], c[1][1], c[2][1])}
    tot = 0
    for sign, kind, names in expr:
        tot += sign * sum(_agg(kind, L[n]) for n in names)
    return tot


def build(p, cap=40000):
    W, A, clauses = p['W'], p['alpha'] + 1, p['clauses']
    if A ** W > 4096:
        return None
    rows = list(product(range(A), repeat=W))
    K = W - 2

    def srows(r1, r2, r3):
        out = []
        for e, _ in clauses:
            out.append(tuple(_value(e, ((r1[j], r1[j + 1], r1[j + 2]),
                                        (r2[j], r2[j + 1], r2[j + 2]),
                                        (r3[j], r3[j + 1], r3[j + 2]))) for j in range(K)))
        return tuple(out)

    def okself(v):
        for c, (_, cons) in enumerate(clauses):
            for di, dj, rel in cons:
                if di:
                    continue
                for j in range(K):
                    k = j + dj
                    if 0 <= k < K:
                        if (v[c][j] > v[c][k]) if rel == '<=' else (v[c][j] < v[c][k]):
                            return False
        return True

    def okstep(u, v):
        for c, (_, cons) in enumerate(clauses):
            for di, dj, rel in cons:
                if not di:
                    continue
                for j in range(K):
                    k = j + dj
                    if 0 <= k < K:
                        if (u[c][j] > v[c][k]) if rel == '<=' else (u[c][j] < v[c][k]):
                            return False
        return True

    states, index, adj = [], {}, []

    def sid(s):
        i = index.get(s)
        if i is None:
            i = index[s] = len(states)
            states.append(s); adj.append(None)
        return i

    startw = {}
    for r1 in rows:
        for r2 in rows:
            for r3 in rows:
                v = srows(r1, r2, r3)
                if okself(v):
                    k = (r2, r3, v)
                    startw[k] = startw.get(k, 0) + 1
                    if len(startw) > cap:
                        return None
    for k in startw:
        sid(k)
    qi = 0
    while qi < len(states):
        r2, r3, v = states[qi]
        row = []
        for r4 in rows:
            w = srows(r2, r3, r4)
            if okself(w) and okstep(v, w):
                row.append(sid((r3, r4, w)))
                if len(states) > cap:
                    return None
        adj[qi] = row
        qi += 1
    S = len(states)
    start = [startw.get(s, 0) for s in states]
    end = [1] * S
    return adj, start, end, S


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
