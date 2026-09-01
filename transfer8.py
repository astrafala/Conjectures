#!/usr/bin/env python3
"""Cell-neighbourhood conditions needing a TWO-LINE window, counted up to relabelling.

"each element equal to exactly two horizontal and vertical neighbors", "no element equal to
fewer vertical neighbors than horizontal neighbors" and their relatives look at the line
above AND the line below, so a single line is not enough state: the vertices are ordered
pairs of consecutive lines, (p,c) -> (c,x) is an edge when every cell of the middle line c
passes with p above and x below, a walk of length L-2 is an array of L lines, and the first
and last lines are tested with one neighbour line missing.

The relabelling machinery of transfer7 carries over unchanged: the conditions are stated in
equalities, so K! a(n) = sum_i C(K,i) D_(K-i) L_i(n) and each chain lumps over the equality
pattern of the PAIR.
"""
import re
import namecanon
from itertools import product
from math import comb
import transfer6 as T6
from transfer7 import rgs, derange, falling, npatterns, ROWMAJOR

DIMTOK = r'\(?\s*(\d*\s*n\s*(?:\+\s*\d+)?|\d+\s*\+\s*\d+|\d+)\s*\)?'
# the connector is not always ``with'': the graph-colouring names say ``arrays where'', and
# several say ``arrays x(i,j) with''
SHAPE2 = re.compile(DIMTOK + r'\s*X\s*' + DIMTOK +
                    r'\s+(?:(0)\.\.(\d+)|(binary))\s+(?:colorings?|arrays?)'
                    r'(?:\s+x\(i,j\))?(?:\s+(?:with|where|in which))?\s+', re.I)


def _dim(s):
    """-> ('n', constant, multiplier) or ('c', value, 1); the n dimension may be 2n or 3n."""
    s = s.replace(' ', '')
    if 'n' in s:
        a, _, b = s.partition('n')
        mult = int(a) if a else 1
        cst = int(b[1:]) if b.startswith('+') else 0
        return ('n', cst, mult)
    if '+' in s:
        return ('c', sum(int(x) for x in s.split('+')), 1)
    return ('c', int(s), 1)


HV = [(-1, 0), (1, 0), (0, -1), (0, 1)]
KING = HV + [(-1, -1), (-1, 1), (1, -1), (1, 1)]
NUM = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
       'six': 6, 'seven': 7, 'eight': 8}


def _nums(s):
    out = []
    for t in re.findall(r'[a-z]+|\d+', s.lower()):
        if t in ('or', 'and'):
            continue
        if t in NUM:
            out.append(NUM[t])
        elif t.isdigit():
            out.append(int(t))
        else:
            return None
    return sorted(set(out)) or None


def _countpred(txt):
    """text describing how many neighbours -> (predicate on an int, LaTeX)."""
    txt = txt.strip().lower()
    if txt in ('any', 'no'):
        return (lambda c: c == 0), '=0'
    if txt == 'an odd number of':
        return (lambda c: c % 2 == 1), r'\ \text{is odd}'
    if txt == 'an even number of':
        return (lambda c: c % 2 == 0), r'\ \text{is even}'
    m = re.fullmatch(r'(exactly|at least|at most|no more than|more than|fewer than) (.+)', txt)
    if m:
        rel, rest = m.group(1), m.group(2)
        v = _nums(rest)
        if not v or len(v) != 1:
            return None
        k = v[0]
        f = {'exactly': lambda c: c == k, 'at least': lambda c: c >= k,
             'at most': lambda c: c <= k, 'no more than': lambda c: c <= k,
             'more than': lambda c: c > k, 'fewer than': lambda c: c < k}[rel]
        sy = {'exactly': '=', 'at least': r'\ge', 'at most': r'\le', 'no more than': r'\le',
              'more than': '>', 'fewer than': '<'}[rel]
        return f, rf'{sy}{k}'
    v = _nums(txt)
    if not v:
        return None
    return (lambda c, V=set(v): c in V), r'\in\{' + ','.join(map(str, v)) + r'\}'


DIAG = [(-1, -1), (1, 1)]
ANTI = [(-1, 1), (1, -1)]
NBSET = {'horizontal or vertical': HV, 'horizontal and vertical': HV,
         'vertical or horizontal': HV, 'vertical and horizontal': HV,
         'horizontal, vertical or diagonal': HV + DIAG,
         'horizontal, vertical or antidiagonal': HV + ANTI,
         'horizontal, vertical, diagonal or antidiagonal': KING,
         'horizontal, diagonal or antidiagonal': [(0, -1), (0, 1)] + DIAG + ANTI,
         'king-move': KING}

# the neighbour-set phrase is spelled out rather than matched by a character class: with a
# lazy (.+?) in front, ``at least one horizontal or vertical'' split as ``at'' + ``least one
# horizontal or vertical'' and every name in the family was refused.
NBALT = '|'.join(re.escape(k) for k in sorted(NBSET, key=len, reverse=True))
CELL = re.compile(r'(?:each|every) element (equal|unequal) to (.+) '
                  r'(' + NBALT + r') neighbou?rs?', re.I)
NOEL = re.compile(r'no element equal to (.+) '
                  r'(' + NBALT + r') neighbou?rs?', re.I)
CMP = re.compile(r'no element equal to (fewer|more|the same number of) '
                 r'(vertical|horizontal) neighbou?rs (?:than|as) (vertical|horizontal) '
                 r'neighbou?rs', re.I)


def _cond(rest):
    """-> (kind, data, latex) for the cell condition, or None."""
    low = rest.strip().rstrip('.').lower()
    m = CMP.fullmatch(low)
    if m:
        rel, s1, s2 = m.groups()
        if s1 == s2:
            return None
        f = {'fewer': lambda a, b: a >= b,          # "no element equal to FEWER v than h"
             'more': lambda a, b: a <= b,
             'the same number of': lambda a, b: a != b}[rel]
        sy = {'fewer': r'\ge', 'more': r'\le', 'the same number of': r'\ne'}[rel]
        first = s1                                   # the count named first
        return ('cmp', (f, first),
                rf'c_{{\mathrm{{{s1[0]}}}}}\;{sy}\;c_{{\mathrm{{{s2[0]}}}}}', '', False)
    m = CELL.fullmatch(low)
    if m:
        sense, num, nbs = m.groups()
        nb = NBSET.get(nbs.strip())
        got = _countpred(num)
        if nb is None or not got:
            return None
        f, tex = got
        return ('cell', (f, nb, sense == 'unequal', True),
                (r'\#\{\text{neighbours with an equal value}\}' if sense == 'equal'
                 else r'\#\{\text{neighbours with a different value}\}') + tex, tex, False)
    m = NOEL.fullmatch(low)
    if m:
        num, nbs = m.groups()
        nb = NBSET.get(nbs.strip())
        got = _countpred(num)
        if nb is None or not got:
            return None
        f, tex = got
        return ('cell', (f, nb, False, False),
                r'\#\{\text{neighbours with an equal value}\}\;\text{is not }' + tex,
                tex, True)
    return None


def parse_name(nm):
    nm = namecanon.canon(nm)   # 'a(n) is the number of ...' and friends
    norm = re.sub(r'(\bn|\d|\))\s*[xX]\s*(?=[\d(n])', r'\1 X ', nm)
    norm = re.sub(r'\s+', ' ', norm).strip().rstrip('.')
    m = ROWMAJOR.search(norm)
    if m:
        head = norm[:m.start()].rstrip(', ')
    else:
        m2 = re.search(r'(?:new )?values \d+\.\.\d+ introduced in row major order\s*'
                       r'(?:(?:and|with)\s+)?', norm, re.I)
        if not m2:
            return None
        head = norm[:m2.start()].rstrip(', ') + ' ' + norm[m2.end():]
        head = re.sub(r'\s+', ' ', head).strip().rstrip('.')
    frac = 1
    m = T6.FRAC.match(head)
    if m:
        frac = 2 if m.group(1) else (4 if m.group(0).lower().startswith('one quarter')
                                     else int(m.group(2)))
        head = head[m.end():]
    else:
        m = T6.HEAD.match(head)
        if not m:
            return None
        head = head[m.end():]
    head = re.sub(r'\s*\(colorings ignoring permutations of colors\)\s*', ' ', head,
                  flags=re.I).strip().rstrip('.')
    m = SHAPE2.match(head)
    if not m:
        return None
    d1, d2 = _dim(m.group(1)), _dim(m.group(2))
    if d1 is None or d2 is None:
        return None
    alpha = 1 if m.group(5) else int(m.group(4))
    rest = head[m.end():].strip().rstrip('.').rstrip(',')
    if d1[0] == 'n' and d2[0] == 'c':
        walk, fixed, base, mult = 'rows', d2[1], d1[1], d1[2]
    elif d2[0] == 'n' and d1[0] == 'c':
        walk, fixed, base, mult = 'cols', d1[1], d2[1], d2[2]
    else:
        return None
    got = _cond(rest)
    if not got:
        return None
    kind, data, tex, reltex, negated = got
    if walk == 'cols':
        if kind == 'cell':
            f, nb, unequal, isall = data
            data = (f, [(du, dt) for dt, du in nb], unequal, isall)
        else:
            f, first = data
            data = (f, {'vertical': 'horizontal', 'horizontal': 'vertical'}[first])
    if kind == 'cell' and any(abs(dt) > 1 for dt, _ in data[1]):
        return None                       # a knight move reaches two lines away
    return {'walk': walk, 'fixed': fixed, 'base': base, 'mult': mult, 'alpha': alpha,
            'K': alpha + 1, 'frac': frac, 'kind': kind, 'data': data, 'tex': tex,
            'reltex': reltex, 'negated': negated, 'rest': rest}


def cell_ok(above, cur, below, u, W, p):
    v = cur[u]
    if p['kind'] == 'cmp':
        f, first = p['data']
        cv = ch = 0
        for dt in (-1, 1):
            L = above if dt == -1 else below
            if L is not None and L[u] == v:
                cv += 1
        for du in (-1, 1):
            if 0 <= u + du < W and cur[u + du] == v:
                ch += 1
        a, b = (cv, ch) if first == 'vertical' else (ch, cv)
        return f(a, b)
    f, nb, unequal, _ = p['data']
    eq = tot = 0
    for dt, du in nb:
        uu = u + du
        if not (0 <= uu < W):
            continue
        L = cur if dt == 0 else (above if dt < 0 else below)
        if L is None:
            continue
        tot += 1
        if L[uu] == v:
            eq += 1
    return f(tot - eq) if unequal else f(eq)


def line_ok(above, cur, below, W, p):
    return all(cell_ok(above, cur, below, u, W, p) for u in range(W))


def build(p, cap=200000):
    """lumped two-line-window chain: states are equality patterns of a pair of lines."""
    W, K = p['fixed'], p['K']
    index, plist = {}, []
    for i in range(1, K + 1):
        for P in _pairs(W, i):
            index[(i, P)] = len(plist)
            plist.append((i, P))
            if len(plist) > cap:
                return None
    adj, start, end, one = [], [], [], []
    for i, P in plist:
        vals = list(range(i))
        pr, cu = P[:W], P[W:]
        row = {}
        for x in product(vals, repeat=W):
            if not line_ok(pr, cu, x, W, p):
                continue
            q = rgs(cu + x)
            if (i, q) not in index:
                continue
            row[index[(i, q)]] = row.get(index[(i, q)], 0) + 1
        adj.append(list(row.items()))
        e = comb(K, i) * derange(K - i) * falling(i, max(P) + 1)
        start.append(e if line_ok(None, pr, cu, W, p) else 0)
        end.append(1 if line_ok(pr, cu, None, W, p) else 0)
    for i in range(1, K + 1):
        for P in _pairs(W, i):
            pass
    return adj, start, end, plist


def _pairs(W, maxb):
    out = []

    def go(pref, mx):
        if len(pref) == 2 * W:
            out.append(tuple(pref))
            return
        for v in range(min(mx + 1, maxb - 1) + 1):
            go(pref + [v], max(mx, v))
    go([], -1)
    return out


def singles(p):
    """K! * (number of canonical one-line arrays)."""
    W, K = p['fixed'], p['K']
    tot = 0
    for i in range(1, K + 1):
        for P in _pairs(W, i)[:0]:
            pass
    for i in range(1, K + 1):
        for r in _lines(W, i):
            if line_ok(None, r, None, W, p):
                tot += comb(K, i) * derange(K - i) * falling(i, max(r) + 1)
    return tot


def _lines(W, maxb):
    out = []

    def go(pref, mx):
        if len(pref) == W:
            out.append(tuple(pref))
            return
        for v in range(min(mx + 1, maxb - 1) + 1):
            go(pref + [v], max(mx, v))
    go([], -1)
    return out


def wmatvec(adj, v):
    return [sum(c * v[t] for t, c in row) for row in adj]


def avals(adj, start, end, p, nmax):
    """[K!*frac*a(n) for n = 0..nmax]; a(n) counts arrays with mult*n + base lines."""
    mult, base = p['mult'], p['base']
    Lmax = mult * nmax + base
    from math import factorial as _f
    vals = {0: _f(p['K']) * p['frac'], 1: singles(p)}
    g = end[:]
    L = 2
    while L <= Lmax:
        vals[L] = sum(sv * x for sv, x in zip(start, g) if sv)
        g = wmatvec(adj, g)
        L += 1
    out = []
    for n in range(nmax + 1):
        L = mult * n + base
        out.append(vals.get(L) if L >= 0 else None)
    return out


def threshold(adj, start, end, coeffs, order, p):
    """smallest n with the recurrence holding for every larger n, or None."""
    mult, base = p['mult'], p['base']
    S = S0 = len(adj)
    n_lo = 0
    while mult * n_lo + base < 2:
        n_lo += 1
    o = mult * n_lo + base - 2
    h = end[:]
    for _ in range(o):
        h = wmatvec(adj, h)
    powers = [h]
    for _ in range(order):
        for _ in range(mult):
            h = wmatvec(adj, h)
        powers.append(h)
    w = powers[order][:]
    for i, c in coeffs.items():
        pw = powers[order - i]
        for j in range(S):
            w[j] -= c * pw[j]
    # the Cayley-Hamilton bound is S, but a true recurrence drives w to the zero vector in
    # a few steps and each step here costs a matrix-vector product on a lumped chain with
    # thousands of states. The run is therefore given a budget; exceeding it is reported as
    # UNRESOLVED, never as a proof and never as a failure.
    budget = 2 * S + order + 8
    import time as _t
    t0 = _t.time()
    us, zeros, j = [], 0, 0
    while zeros < S + 1 and j <= budget:
        if _t.time() - t0 > 420:
            return None                     # UNRESOLVED, never a proof and never a failure
        u = sum(sv * x for sv, x in zip(start, w) if sv)
        us.append(u)
        zeros = zeros + 1 if u == 0 else 0
        if not any(w):
            zeros = S + 1
            break
        for _ in range(mult):
            w = wmatvec(adj, w)
        j += 1
    if zeros < S + 1:
        return None
    last = max((i for i, u in enumerate(us) if u != 0), default=-1)
    return n_lo + order + last
