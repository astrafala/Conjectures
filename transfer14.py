#!/usr/bin/env python3
"""Order conditions along rows, columns, diagonals and antidiagonals.

    Number of n X 3 0..2 arrays with rows nondecreasing and antidiagonals unimodal.

A "nondecreasing" condition along a direction is local: it compares two cells a step apart.
"Unimodal" is not -- a sequence is unimodal exactly when it never rises again after it has
fallen, so the state must remember, for each sequence still running, whether it has already
fallen. Those flags travel with their sequences: the flag of the antidiagonal through
(t,u) becomes the flag at (t+1,u-1), and a fresh antidiagonal starts at the far end of each
new line.

Directions are given in the array's own (row, column) frame. Walking columns instead of rows
swaps the two components, and an antidiagonal is then traversed BACKWARDS, which turns
"nondecreasing" into "nonincreasing"; unimodality is unchanged by reversal.
"""
import re
from itertools import product
import transfer6 as T6
from transfer8 import SHAPE2, _dim

DIRV = {'row': (0, 1), 'rows': (0, 1), 'column': (1, 0), 'columns': (1, 0),
        'diagonal': (1, 1), 'diagonals': (1, 1),
        'antidiagonal': (1, -1), 'antidiagonals': (1, -1)}
CONDW = re.compile(r'\b(nondecreasing|nonincreasing|unimodal)\b', re.I)


def parse_name(nm):
    norm = re.sub(r'(\bn|\d|\))\s*[xX]\s*(?=[\d(n])', r'\1 X ', nm)
    norm = re.sub(r'\s+', ' ', norm).strip().rstrip('.')
    norm = re.sub(r'^[^:]{1,90}:\s*', '', norm)
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
    rest = norm[m.end():].strip().rstrip('.').lower()
    if d1[0] == 'n' and d2[0] == 'c':
        walk, fixed, base, mult = 'rows', d2[1], d1[1], d1[2]
    elif d2[0] == 'n' and d1[0] == 'c':
        walk, fixed, base, mult = 'cols', d1[1], d2[1], d2[2]
    else:
        return None
    clauses, pos = [], 0
    for mm in CONDW.finditer(rest):
        head = rest[pos:mm.start()]
        pos = mm.end()
        words = [w for w in re.split(r'[,\s]+', head) if w]
        lex = 'lexicographically' in words
        dirs = [DIRV[w] for w in words if w in DIRV]
        if not dirs or any(w not in DIRV and
                           w not in ('and', 'or', 'in', 'with', 'the', 'lexicographically')
                           for w in words):
            return None
        clauses.append((dirs, mm.group(1), lex))
    tail = rest[pos:].strip()
    if not clauses or tail not in ('', 'order', 'in order'):
        return None
    # ``rows and columns in nondecreasing order'' means the rows are sorted as VECTORS, not
    # that each row is nondecreasing along itself: the two readings differ from n = 2 on
    # (86 against 50 for 2 X 2 arrays over 0..3), and the DATA settles it.
    if tail in ('order', 'in order'):
        clauses = [(d, c, True) for d, c, _ in clauses]
    specs, lexspecs = [], []
    for dirs, cond, lex in clauses:
        if lex:
            if cond != 'nondecreasing':
                return None
            for dr, dc in dirs:
                if (dr, dc) == (0, 1):
                    lexspecs.append('line' if walk == 'rows' else 'pos')
                elif (dr, dc) == (1, 0):
                    lexspecs.append('pos' if walk == 'rows' else 'line')
                else:
                    return None
            continue
        for dr, dc in dirs:
            dl, dp = (dr, dc) if walk == 'rows' else (dc, dr)
            c = cond
            if dl < 0:
                dl, dp = -dl, -dp
                c = {'nondecreasing': 'nonincreasing',
                     'nonincreasing': 'nondecreasing', 'unimodal': 'unimodal'}[c]
            if dl not in (0, 1):
                return None
            specs.append((dl, dp, c))
    if not specs and not lexspecs:
        return None
    return {'walk': walk, 'fixed': fixed, 'base': base, 'mult': mult, 'alpha': alpha,
            'frac': frac, 'specs': specs, 'lex': lexspecs, 'rest': rest,
            'tex': (',\\ '.join(rf'({dl},{dp})\text{{: {c}}}' for dl, dp, c in specs)
                    + (r'\text{; lexicographic: }' + ','.join(lexspecs) if lexspecs else ''))}


def _flagdirs(p):
    return [i for i, (dl, dp, c) in enumerate(p['specs']) if dl == 1 and c == 'unimodal']


def line_ok(r, W, p):
    """the within-line clauses (dl = 0)."""
    for dl, dp, c in p['specs']:
        if dl != 0:
            continue
        seq = [r[u] for u in range(0, W)] if dp > 0 else [r[u] for u in range(W - 1, -1, -1)]
        step = abs(dp)
        for s0 in range(step):
            sub = seq[s0::step]
            fell = False
            for i in range(1, len(sub)):
                if c == 'nondecreasing' and sub[i] < sub[i - 1]:
                    return False
                if c == 'nonincreasing' and sub[i] > sub[i - 1]:
                    return False
                if c == 'unimodal':
                    if sub[i] < sub[i - 1]:
                        fell = True
                    elif sub[i] > sub[i - 1] and fell:
                        return False
    return True


def step(r, s, fl, W, p):
    """-> new flag tuple, or None when the step is impossible."""
    fd = _flagdirs(p)
    out = []
    k = 0
    for i, (dl, dp, c) in enumerate(p['specs']):
        if dl != 1:
            continue
        if c == 'unimodal':
            cur = fl[k]
            new = [0] * W
            for u in range(W):
                uu = u + dp
                if not (0 <= uu < W):
                    continue
                if s[uu] < r[u]:
                    new[uu] = 1
                elif s[uu] > r[u] and cur[u]:
                    return None
                else:
                    new[uu] = cur[u]
            out.append(tuple(new))
            k += 1
        else:
            for u in range(W):
                uu = u + dp
                if not (0 <= uu < W):
                    continue
                if c == 'nondecreasing' and s[uu] < r[u]:
                    return None
                if c == 'nonincreasing' and s[uu] > r[u]:
                    return None
    return tuple(out)


def _lexpos_update(fl, s, W):
    """lexicographic comparison of adjacent POSITION sequences, decided column by column."""
    out = list(fl)
    for j in range(W - 1):
        if out[j] == 0:
            if s[j] < s[j + 1]:
                out[j] = 1
            elif s[j] > s[j + 1]:
                return None
    return tuple(out)


def build(p, cap=200000):
    W, al = p['fixed'], p['alpha']
    lines = [r for r in product(range(al + 1), repeat=W) if line_ok(r, W, p)]
    nf = len(_flagdirs(p))
    npos = p['lex'].count('pos')
    tot = len(lines) * (2 ** W) ** nf * (2 ** (W - 1)) ** min(npos, 1)
    if tot > cap or not lines:
        return None
    flagsets = list(product(*[list(product((0, 1), repeat=W)) for _ in range(nf)]))
    lexsets = list(product((0, 1), repeat=W - 1)) if npos else [()]
    idx, st = {}, []
    for r in lines:
        for fl in flagsets:
            for lx in lexsets:
                idx[(r, fl, lx)] = len(st)
                st.append((r, fl, lx))
    zero = tuple((0,) * W for _ in range(nf))
    lexline = 'line' in p['lex']
    adj, start, end = [], [], []
    for (r, fl, lx) in st:
        row = []
        for s in lines:
            if lexline and not (r <= s):
                continue
            nfl = step(r, s, fl, W, p)
            if nfl is None:
                continue
            nlx = _lexpos_update(lx, s, W) if npos else ()
            if nlx is None:
                continue
            row.append(idx[(s, nfl, nlx)])
        adj.append(row)
        init = _lexpos_update((0,) * (W - 1), r, W) if npos else ()
        start.append(1 if (fl == zero and init is not None and lx == init) else 0)
        end.append(1)
    return adj, start, end, st


def matvec(adj, v):
    return [sum(v[t] for t in row) for row in adj]


def singles(p):
    W, al = p['fixed'], p['alpha']
    npos = p['lex'].count('pos')
    n = 0
    for r in product(range(al + 1), repeat=W):
        if not line_ok(r, W, p):
            continue
        if npos and _lexpos_update((0,) * (W - 1), r, W) is None:
            continue
        n += 1
    return n


def avals(adj, start, end, p, nmax):
    mult, base = p['mult'], p['base']
    Lmax = mult * nmax + base
    vals = {0: p['frac']}
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
