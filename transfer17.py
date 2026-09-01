#!/usr/bin/env python3
"""Generic transfer matrix for Hardin arrays whose condition is local to each 3 X 3 block.

    Number of (n+2) X (K+2) 0..m arrays with every 3 X 3 subblock <P>

A 3 X 3 block spans three consecutive lines, so the state is a PAIR of consecutive lines and
the step (r,s) -> (s,t) tests <P> on every window of three consecutive columns of the three
lines r, s, t. An array with L lines is then a walk of length L-2 on the pair state, so with
V the set of lines and M the adjacency matrix,

    a(L) = 1^T M^(L-2) 1     for L >= 2.

Line entries of a block are written g[i][j] with i the line index within the block and j the
column index, so g[0] is the top line of the block.
"""
import re
from itertools import product

DIM = r'\(?\s*(n\s*\+\s*\d+|n|\d+\s*\+\s*\d+|\d+)\s*\)?'
FRAC = re.compile(r'^\s*(?:(Half)|One quarter|1/(\d+))\s+the number of\s+', re.I)
HEAD = re.compile(r'^\s*Number of\s+', re.I)
SHAPE = re.compile(rf'{DIM}\s*X\s*{DIM}\s+(?:(0)\.\.(\d+)|(binary))\s+arrays?\s+with\s+', re.I)
QUANT = re.compile(r'^(every|each|no|all)\s+3\s*X\s*3\s+subblock\s+', re.I)
SPLIT = re.compile(r'\s+and\s+(?:every|each|no|all)\s+3\s*X\s*3\s+', re.I)


def _numlist(s):
    out = [int(t) for t in re.findall(r'\d+', s)]
    return sorted(set(out)) if out else None


def rows_of(g):
    return [g[0], g[1], g[2]]


def cols_of(g):
    return [(g[0][j], g[1][j], g[2][j]) for j in range(3)]


def diag_of(g):
    return (g[0][0], g[1][1], g[2][2])


def anti_of(g):
    return (g[0][2], g[1][1], g[2][0])


LINES = {'row': rows_of, 'column': cols_of,
         'diagonal': lambda g: [diag_of(g)], 'antidiagonal': lambda g: [anti_of(g)]}
PERIM = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0), (1, 0)]


def _clause(t):
    """one clause of the condition: (fn(g)->bool, latex) or None."""
    t = t.strip().rstrip('.').strip()
    low = re.sub(r'\s+', ' ', t.lower())

    m = re.fullmatch(r'(?:having )?clockwise perimeter pattern ((?:[01]{8}[ ,]*|or )+)', low)
    if m:
        pats = re.findall(r'[01]{8}', m.group(1))
        if not pats:
            return None
        # the perimeter is a CYCLE: the entry names one representative and the pattern is
        # matched wherever the clockwise reading starts, so every rotation counts. Reading
        # the representative literally gives a count far below the entry's own first term
        # (6 against 48 on A259994), which is how this was caught.
        S = set()
        for p in pats:
            w = tuple(int(ch) for ch in p)
            for r in range(8):
                S.add(w[r:] + w[:r])

        def fn(g, S=S):
            return tuple(g[i][j] for i, j in PERIM) in S
        tex = (r'\text{the clockwise perimeter word of }g\text{ is a rotation of one of }\{' +
               ',\\ '.join(p for p in pats) + r'\}')
        return fn, tex

    if low in ('singular', 'nonsingular'):
        want = (low == 'singular')

        def fn(g, want=want):
            det = (g[0][0]*(g[1][1]*g[2][2]-g[1][2]*g[2][1])
                   - g[0][1]*(g[1][0]*g[2][2]-g[1][2]*g[2][0])
                   + g[0][2]*(g[1][0]*g[2][1]-g[1][1]*g[2][0]))
            return (det == 0) == want
        return fn, (r'\det g = 0' if want else r'\det g \ne 0')

    # "<lines> sum [not] equal to <list>", the lines being any of row/column/diagonal/
    # antidiagonal joined by commas and "and"
    m = re.fullmatch(r'((?:row|column|diagonal|antidiagonal)(?:[, ]+(?:and )?'
                     r'(?:row|column|diagonal|antidiagonal))*) sum (not )?equal to ([\d ,or]+)',
                     low)
    if m:
        kinds = re.findall(r'row|column|diagonal|antidiagonal', m.group(1))
        neg = bool(m.group(2))
        vals = _numlist(m.group(3))
        if not vals or not kinds:
            return None
        S = set(vals)

        def fn(g, kinds=tuple(kinds), S=S, neg=neg):
            for k in kinds:
                for ln in LINES[k](g):
                    if (sum(ln) in S) == neg:
                        return False
            return True
        rel = r'\notin' if neg else r'\in'
        tex = (r'\text{every %s sum} %s \{%s\}' %
               (', '.join(kinds), rel, ','.join(str(v) for v in vals)))
        return fn, tex

    # "<kind> sum <v>" / "no <kind> sum <v>" -- a bare equality or disequality
    m = re.fullmatch(r'(no )?(row|column|diagonal|antidiagonal) sum ([\d ,or]+)', low)
    if m:
        neg = bool(m.group(1))
        kind = m.group(2)
        vals = _numlist(m.group(3))
        if not vals:
            return None
        S = set(vals)

        def fn(g, kind=kind, S=S, neg=neg):
            for ln in LINES[kind](g):
                if (sum(ln) in S) == neg:
                    return False
            return True
        rel = r'\notin' if neg else r'\in'
        tex = r'\text{every %s sum} %s \{%s\}' % (kind, rel, ','.join(str(v) for v in vals))
        return fn, tex
    return None


def parse_name(nm):
    norm = re.sub(r'(\bn|\d|\))\s*[xX]\s*(?=[\d(n])', r'\1 X ', nm)
    norm = re.sub(r'\s+', ' ', norm).strip()
    frac = 1
    m = FRAC.match(norm)
    if m:
        frac = 2 if m.group(1) else (4 if m.group(0).lower().startswith('one quarter')
                                     else int(m.group(2)))
        norm = norm[m.end():]
    else:
        m = HEAD.match(norm)
        if not m:
            return None
        norm = norm[m.end():]
    m = SHAPE.match(norm)
    if not m:
        return None

    def dv(s):
        s = s.replace(' ', '')
        if 'n' in s:
            return ('n', int(s.split('+')[1]) if '+' in s else 0)
        if '+' in s:
            return ('c', sum(int(x) for x in s.split('+')))
        return ('c', int(s))
    d1, d2 = dv(m.group(1)), dv(m.group(2))
    alpha = 1 if m.group(5) else int(m.group(4))
    rest = norm[m.end():].strip()
    if d1[0] == 'n' and d2[0] == 'c':
        walk, fixed, base = 'rows', d2[1], d1[1]
    elif d2[0] == 'n' and d1[0] == 'c':
        walk, fixed, base = 'cols', d1[1], d2[1]
    else:
        return None
    m = QUANT.match(rest)
    if not m:
        return None
    quant = m.group(1).lower()
    body = rest[m.end():].strip().rstrip('.').strip()
    # ``no 3X3 subblock diagonal sum 1 and no antidiagonal sum 1 and no row sum 0'' is a
    # conjunction of separate prohibitions, not the negation of a conjunction: each ``no''
    # binds its own clause. Negating the whole thing would count arrays in which SOME block
    # violates one of the four, which is a different and much larger set.
    percl = quant == 'no' and re.search(r'\s+and\s+no\s+', body, re.I)
    if percl:
        parts = ['no ' + q.strip() for q in re.split(r'\s+and\s+no\s+', body, flags=re.I)]
    else:
        parts = SPLIT.split(body)
    cls = []
    for i, part in enumerate(parts):
        part = re.sub(r'^subblock\s+', '', part.strip(), flags=re.I)
        got = _clause(part)
        if not got:
            return None
        cls.append(got)
    fns = [c[0] for c in cls]

    def pred(g, fns=tuple(fns)):
        return all(f(g) for f in fns)
    if quant == 'no' and not percl:
        inner = pred

        def pred(g, inner=inner):
            return not inner(g)
    tex = r'\ \text{ and }\ '.join(c[1] for c in cls)
    if quant == 'no' and not percl:
        tex = r'\text{not }\bigl(' + tex + r'\bigr)'
    return {'walk': walk, 'fixed': fixed, 'base': base, 'alpha': alpha, 'frac': frac,
            'quant': quant, 'pred': pred, 'tex': tex, 'body': body}


def build(p, cap=40000):
    """Pair-of-lines digraph. Vertices are ordered pairs (r, s) of admissible lines."""
    W, alpha, fn = p['fixed'], p['alpha'], p['pred']
    rowwalk = p['walk'] == 'rows'
    vals = list(range(alpha + 1))
    if (alpha + 1) ** (2 * W) > cap:
        return None
    lines = list(product(vals, repeat=W))
    st = [(r, s) for r in lines for s in lines]
    idx = {v: i for i, v in enumerate(st)}

    def ok(r, s, t):
        for j in range(W - 2):
            if rowwalk:
                g = ((r[j], r[j + 1], r[j + 2]),
                     (s[j], s[j + 1], s[j + 2]),
                     (t[j], t[j + 1], t[j + 2]))
            else:                       # the walk runs along columns: transpose the block
                g = ((r[j], s[j], t[j]),
                     (r[j + 1], s[j + 1], t[j + 1]),
                     (r[j + 2], s[j + 2], t[j + 2]))
            if not fn(g):
                return False
        return True
    adj = []
    for (r, s) in st:
        out = [idx[(s, t)] for t in lines if ok(r, s, t)]
        adj.append(out)
    return st, adj


def matvec(adj, v):
    return [sum(v[k] for k in row) for row in adj]


def terms(adj, S, N):
    """terms[j] = number of admissible arrays with j+2 lines."""
    v = [1] * S
    out = []
    for _ in range(N + 1):
        out.append(sum(v))
        v = matvec(adj, v)
    return out


def threshold(adj, S, coeffs, order):
    v = [1] * S
    powers = [v]
    for _ in range(order):
        v = matvec(adj, v)
        powers.append(v)
    w = powers[order][:]
    for i, c in coeffs.items():
        pw = powers[order - i]
        for j in range(S):
            w[j] -= c * pw[j]
    us, zeros, j = [], 0, 0
    while zeros < S + 1 and j <= 3 * S + order + 8:
        u = sum(w)
        us.append(u)
        zeros = zeros + 1 if u == 0 else 0
        if not any(w):
            zeros = S + 1
            break
        w = matvec(adj, w)
        j += 1
    if zeros < S + 1:
        return None
    last = max((i for i, u in enumerate(us) if u != 0), default=-1)
    return order + last
