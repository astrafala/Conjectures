#!/usr/bin/env python3
"""Generic transfer matrix for Hardin arrays whose condition is local to each 2 X 2 block.

Every name of the form

    Number of (n+1) X (K+1) 0..m arrays with every 2 X 2 subblock <P>

where <P> is a predicate depending only on the four entries of the block, describes a set
of arrays whose rows (or columns, for the transposed names) are the vertices of a finite
digraph: r -> s is an edge when placing s under r satisfies <P> in every column pair. An
array with L lines is then a walk of length L-1, so the count is 1^T M^(L-1) 1 and is
C-finite. The only per-entry work is compiling <P>; the rest of the engine is fixed.

Block entries are written (a, b, c, d) = (top-left, top-right, bottom-left, bottom-right).
"""
import re
from itertools import product

NUM = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6}
TEXNUM = {v: k for k, v in NUM.items()}


def _numlist(s):
    """'one, two or three' or '1 3 or 5' -> sorted list of ints, else None."""
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


def _isprime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


# --------------------------------------------------------------------------- predicates
# each handler: text -> (fn(a,b,c,d), latex condition on alpha,beta,gamma,delta) or None

A, B, C, D = r'\alpha', r'\beta', r'\gamma', r'\delta'
SUM4 = rf'{A}+{B}+{C}+{D}'
CWD = rf'\{{{B}-{A},\ {D}-{B},\ {C}-{D},\ {A}-{C}\}}'
SIX = rf'\{{{B}-{A},\ {D}-{B},\ {C}-{D},\ {A}-{C},\ {D}-{A},\ {C}-{B}\}}'
EDGES = rf'\{{{B}-{A},\ {D}-{B},\ {C}-{D},\ {A}-{C}\}}'
VALS = rf'\{{{A},{B},{C},{D}\}}'


def _setex(vals):
    return r'\{' + ','.join(str(v) for v in vals) + r'\}'


def _pred(p):
    p = p.strip().rstrip('.').strip()
    low = p.lower()

    m = re.fullmatch(r'summing to ([\d,\s]*\d(?:\s+or\s+\d+)?[\d,\s]*)', low)
    if m:
        vals = _numlist(m.group(1))
        if vals:
            return (lambda a, b, c, d, V=set(vals): a + b + c + d in V,
                    rf'{SUM4}\in{_setex(vals)}')

    if low == 'summing to a prime':
        return (lambda a, b, c, d: _isprime(a + b + c + d),
                rf'{SUM4}\ \text{{is prime}}')

    m = re.fullmatch(r'summing to a nonzero multiple of (\d+)', low)
    if m:
        k = int(m.group(1))
        return (lambda a, b, c, d, k=k: (a + b + c + d) % k == 0 and a + b + c + d != 0,
                rf'{SUM4}\ \text{{is a nonzero multiple of }}{k}')

    m = re.fullmatch(r'summing to a multiple of (\d+)', low)
    if m:
        k = int(m.group(1))
        return (lambda a, b, c, d, k=k: (a + b + c + d) % k == 0,
                rf'{k}\mid {SUM4}')

    m = re.fullmatch(r'having (?:exactly )?([a-z, ]+?) distinct values', low)
    if m:
        vals = _numlist(m.group(1))
        if vals and all(1 <= v <= 4 for v in vals):
            return (lambda a, b, c, d, V=set(vals): len({a, b, c, d}) in V,
                    rf'\#{VALS}\in{_setex(vals)}')

    m = re.fullmatch(r'(?:sum(?:ming)?(?: to| equal to)?|having (?:a )?sum(?: of)?)\s+'
                     r'(?:(less|greater|more) than )?(\d+)', low)
    if m:
        rel, k = m.group(1), int(m.group(2))
        if rel is None:
            return (lambda a, b, c, d, k=k: a + b + c + d == k, rf'{SUM4}={k}')
        if rel == 'less':
            return (lambda a, b, c, d, k=k: a + b + c + d < k, rf'{SUM4}<{k}')
        return (lambda a, b, c, d, k=k: a + b + c + d > k, rf'{SUM4}>{k}')

    m = re.fullmatch(r'having exactly (\w+) (?:ones|1s)', low)
    if m:
        v = _numlist(m.group(1))
        if v and len(v) == 1:
            k = v[0]
            return (lambda a, b, c, d, k=k: (a, b, c, d).count(1) == k,
                    rf'\#\{{x\in({A},{B},{C},{D}):x=1\}}={k}')

    m = re.fullmatch(r'having ([a-z, ]+?) (?:ones|1s)', low)
    if m:
        v = _numlist(m.group(1))
        if v and all(0 <= x <= 4 for x in v):
            return (lambda a, b, c, d, V=set(v): (a, b, c, d).count(1) in V,
                    rf'\#\{{x\in({A},{B},{C},{D}):x=1\}}\in{_setex(v)}')

    m = re.fullmatch(r'having a single 1 or two 1s on the same edge( or main diagonally)?', low)
    if m:
        diag = bool(m.group(1))

        def f(a, b, c, d, diag=diag):
            t = (a, b, c, d)
            n1 = t.count(1)
            if n1 == 1:
                return True
            if n1 != 2:
                return False
            pairs = [(0, 1), (2, 3), (0, 2), (1, 3)] + ([(0, 3)] if diag else [])
            return any(t[i] == 1 and t[j] == 1 for i, j in pairs)
        extra = rf'\ \text{{ or }}\ ({A},{D})=(1,1)' if diag else ''
        return (f, rf'\#\{{x:x=1\}}=1\ \text{{ or the two }}1\text{{s are adjacent}}{extra}')

    m = re.fullmatch(r'having a diagonal absolute difference (less|greater) than its '
                     r'antidiagonal absolute difference', low)
    if m:
        lt = m.group(1) == 'less'
        return ((lambda a, b, c, d: abs(a - d) < abs(b - c)) if lt else
                (lambda a, b, c, d: abs(a - d) > abs(b - c)),
                rf'|{A}-{D}|{"<" if lt else ">"}|{B}-{C}|')

    m = re.fullmatch(r'having x(\d)(\d)\s*-\s*x(\d)(\d) (less|greater) than '
                     r'x(\d)(\d)\s*-\s*x(\d)(\d)', low)
    if m:
        g = [int(x) if x.isdigit() else x for x in m.groups()]
        pos = {(0, 0): 0, (0, 1): 1, (1, 0): 2, (1, 1): 3}
        try:
            i1, i2, i3, i4 = (pos[(g[0], g[1])], pos[(g[2], g[3])],
                              pos[(g[5], g[6])], pos[(g[7], g[8])])
        except KeyError:
            return None
        lt = g[4] == 'less'
        sym = [A, B, C, D]

        def f(a, b, c, d, i1=i1, i2=i2, i3=i3, i4=i4, lt=lt):
            t = (a, b, c, d)
            return (t[i1] - t[i2] < t[i3] - t[i4]) if lt else (t[i1] - t[i2] > t[i3] - t[i4])
        return (f, rf'{sym[i1]}-{sym[i2]}{"<" if lt else ">"}{sym[i3]}-{sym[i4]}')

    m = re.fullmatch(r'having its (maximum|minimum) (anti)?diagonal element (greater|less) '
                     r'than the (sum|maximum|minimum|absolute difference) of its '
                     r'(anti)?diagonal elements', low)
    if m:
        g1, s1, rel, g2, s2 = m.groups()
        return _cmp(g1, s1, rel, g2, s2)

    m = re.fullmatch(r'having (?:exactly )?([a-z, ]+?) distinct clockwise edge differences', low)
    if m:
        vals = _numlist(m.group(1))
        if vals and all(1 <= v <= 4 for v in vals):
            return (lambda a, b, c, d, V=set(vals): len({b - a, d - b, c - d, a - c}) in V,
                    rf'\#{CWD}\in{_setex(vals)}')

    if low == 'having distinct clockwise edge differences':
        return (lambda a, b, c, d: len({b - a, d - b, c - d, a - c}) == 4,
                rf'\#{CWD}=4')

    if low == 'having distinct edge sums':
        return (lambda a, b, c, d: len({a + b, b + d, d + c, c + a}) == 4,
                rf'\#\{{{A}+{B},\ {B}+{D},\ {D}+{C},\ {C}+{A}\}}=4')

    m = re.fullmatch(r'having the sum of the absolute values of all six edge and diagonal '
                     r'differences (equal to|no larger than|less than|greater than) (\d+)', low)
    if m:
        rel, k = m.group(1), int(m.group(2))
        f = {'equal to': lambda x, k: x == k, 'no larger than': lambda x, k: x <= k,
             'less than': lambda x, k: x < k, 'greater than': lambda x, k: x > k}[rel]
        sy = {'equal to': '=', 'no larger than': r'\le', 'less than': '<', 'greater than': '>'}[rel]
        return (lambda a, b, c, d, f=f, k=k: f(abs(b - a) + abs(d - b) + abs(c - d) + abs(a - c)
                                               + abs(d - a) + abs(c - b), k),
                rf'|{B}-{A}|+|{D}-{B}|+|{C}-{D}|+|{A}-{C}|+|{D}-{A}|+|{C}-{B}|\;{sy}\;{k}')

    m = re.fullmatch(r'having the absolute values of all six edge and diagonal differences '
                     r'(no larger than|less than) (\d+)', low)
    if m:
        rel, k = m.group(1), int(m.group(2))
        f = (lambda x, k: x <= k) if rel == 'no larger than' else (lambda x, k: x < k)
        sy = r'\le' if rel == 'no larger than' else '<'
        return (lambda a, b, c, d, f=f, k=k: all(f(abs(x), k) for x in
                                                 (b - a, d - b, c - d, a - c, d - a, c - b)),
                rf'\max\bigl(|{B}-{A}|,|{D}-{B}|,|{C}-{D}|,|{A}-{C}|,|{D}-{A}|,|{C}-{B}|\bigr)'
                rf'\;{sy}\;{k}')

    m = re.fullmatch(r'having the sum of the squares of all six edge and diagonal '
                     r'differences equal to (\d+)', low)
    if m:
        k = int(m.group(1))
        return (lambda a, b, c, d, k=k: (b - a) ** 2 + (d - b) ** 2 + (c - d) ** 2 +
                (a - c) ** 2 + (d - a) ** 2 + (c - b) ** 2 == k,
                rf'({B}-{A})^2+({D}-{B})^2+({C}-{D})^2+({A}-{C})^2+({D}-{A})^2+({C}-{B})^2={k}')

    m = re.fullmatch(r'having the sum of the squares of the edge differences equal to (\d+)', low)
    if m:
        k = int(m.group(1))
        return (lambda a, b, c, d, k=k: (b - a) ** 2 + (d - b) ** 2 + (c - d) ** 2 +
                (a - c) ** 2 == k,
                rf'({B}-{A})^2+({D}-{B})^2+({C}-{D})^2+({A}-{C})^2={k}')

    m = re.fullmatch(r'having the sum of the absolute values of the edge differences '
                     r'equal to (\d+)', low)
    if m:
        k = int(m.group(1))
        return (lambda a, b, c, d, k=k: abs(b - a) + abs(d - b) + abs(c - d) + abs(a - c) == k,
                rf'|{B}-{A}|+|{D}-{B}|+|{C}-{D}|+|{A}-{C}|={k}')

    m = re.fullmatch(r'having (equal|unequal) diagonal elements or (equal|unequal) '
                     r'antidiagonal elements', low)
    if m:
        e1, e2 = m.group(1) == 'equal', m.group(2) == 'equal'
        s1 = '=' if e1 else r'\ne'
        s2 = '=' if e2 else r'\ne'
        return (lambda a, b, c, d, e1=e1, e2=e2: ((a == d) if e1 else (a != d)) or
                ((b == c) if e2 else (b != c)),
                rf'{A}{s1}{D}\ \text{{ or }}\ {B}{s2}{C}')

    m = re.fullmatch(r'having (zero|nonzero) (determinant|permanent)', low)
    if m:
        z, kind = m.group(1) == 'zero', m.group(2)
        sy = '=' if z else r'\ne'
        if kind == 'determinant':
            return (lambda a, b, c, d, z=z: (a * d - b * c == 0) if z else (a * d - b * c != 0),
                    rf'{A}{D}-{B}{C}{sy}0')
        return (lambda a, b, c, d, z=z: (a * d + b * c == 0) if z else (a * d + b * c != 0),
                rf'{A}{D}+{B}{C}{sy}0')

    if low == 'containing exactly one value repeat':
        return (lambda a, b, c, d: len({a, b, c, d}) == 3, rf'\#{VALS}=3')

    if low == 'having at least two equal elements connected horizontally or vertically':
        return (lambda a, b, c, d: a == b or c == d or a == c or b == d,
                rf'{A}={B}\ \text{{ or }}\ {C}={D}\ \text{{ or }}\ {A}={C}\ \text{{ or }}\ {B}={D}')

    m = re.fullmatch(r'having (at most|exactly|at least) one duplicate clockwise edge '
                     r'difference', low)
    if m:
        rel = m.group(1)
        f = {'at most': lambda x: x <= 1, 'exactly': lambda x: x == 1,
             'at least': lambda x: x >= 1}[rel]
        sy = {'at most': r'\le', 'exactly': '=', 'at least': r'\ge'}[rel]
        return (lambda a, b, c, d, f=f: f(4 - len({b - a, d - b, c - d, a - c})),
                rf'4-\#{CWD}\;{sy}\;1')

    m = re.fullmatch(r'having exactly ([a-z]+|\d+) nonzero entries', low)
    if m:
        v = _numlist(m.group(1))
        if v and len(v) == 1:
            k = v[0]
            return (lambda a, b, c, d, k=k: sum(1 for x in (a, b, c, d) if x) == k,
                    rf'\#\{{x\in({A},{B},{C},{D}):x\ne0\}}={k}')

    m = re.fullmatch(r'having its diagonal sum differing from its antidiagonal sum by (\d+)', low)
    if m:
        k = int(m.group(1))
        return (lambda a, b, c, d, k=k: abs(a + d - b - c) == k,
                rf'|{A}+{D}-{B}-{C}|={k}')

    # comparisons between aggregates of the diagonal and of the antidiagonal
    AGG = r'(sum|maximum|minimum|absolute difference)'
    m = re.fullmatch(rf'having the {AGG} of its (anti)?diagonal elements '
                     r'(greater|less) than (?:the )?' + AGG + r' of its (anti)?diagonal elements',
                     low)
    if m:
        g1, s1, rel, g2, s2 = m.groups()
        return _cmp(g1, s1, rel, g2, s2)

    m = re.fullmatch(r'having its (maximum|minimum) (anti)?diagonal element '
                     r'(greater|less) than its (maximum|minimum) (anti)?diagonal element', low)
    if m:
        g1, s1, rel, g2, s2 = m.groups()
        return _cmp(g1, s1, rel, g2, s2)

    return None


def _aggfn(kind, anti):
    if anti:
        pick = lambda a, b, c, d: (b, c)
        tx = (B, C)
    else:
        pick = lambda a, b, c, d: (a, d)
        tx = (A, D)
    if kind == 'sum':
        return (lambda a, b, c, d: sum(pick(a, b, c, d))), rf'({tx[0]}+{tx[1]})'
    if kind == 'maximum':
        return (lambda a, b, c, d: max(pick(a, b, c, d))), rf'\max({tx[0]},{tx[1]})'
    if kind == 'minimum':
        return (lambda a, b, c, d: min(pick(a, b, c, d))), rf'\min({tx[0]},{tx[1]})'
    if kind == 'absolute difference':
        return (lambda a, b, c, d: abs(pick(a, b, c, d)[0] - pick(a, b, c, d)[1])), \
               rf'|{tx[0]}-{tx[1]}|'
    return None, None


def _cmp(g1, s1, rel, g2, s2):
    f1, t1 = _aggfn(g1, bool(s1))
    f2, t2 = _aggfn(g2, bool(s2))
    if f1 is None or f2 is None:
        return None
    if rel == 'greater':
        return (lambda a, b, c, d: f1(a, b, c, d) > f2(a, b, c, d)), rf'{t1}>{t2}'
    return (lambda a, b, c, d: f1(a, b, c, d) < f2(a, b, c, d)), rf'{t1}<{t2}'


# ------------------------------------------------------------------------------- parsing
FRAC = re.compile(r'^\s*(?:(Half)|One quarter|1/(\d+))\s+the number of\s+', re.I)
HEAD = re.compile(r'^\s*Number of\s+', re.I)
DIM = r'\(?\s*(n\s*\+\s*\d+|n|\d+\s*\+\s*\d+|\d+)\s*\)?'
SHAPE = re.compile(rf'{DIM}\s*X\s*{DIM}\s+(?:(0)\.\.(\d+)|(binary))\s+arrays?\s+with\s+', re.I)
QUANT = re.compile(r'^(every|no|all)\s+2\s*X\s*2\s+subblock\s+', re.I)
ADJ = re.compile(r'(?:,?\s+(?:and|with)\s+no\s+(?:two\s+)?adjacent\s+(?:elements|values)\s+equal)\s*$',
                 re.I)
PAREN = re.compile(r'\s*\([^()]*\)\s*$')


def _dimval(s):
    s = s.replace(' ', '')
    if 'n' in s:
        return ('n', int(s.split('+')[1]) if '+' in s else 0)
    if '+' in s:
        return ('c', sum(int(x) for x in s.split('+')))
    return ('c', int(s))


def parse_name(nm):
    # the product sign sits between two dimension tokens; requiring the left token to be a
    # digit, a closing bracket or a STANDALONE n keeps the rule off ordinary words -- an
    # earlier version turned ``than x10'' into ``than X 10'' because ``than'' ends in n
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
    d1, d2 = _dimval(m.group(1)), _dimval(m.group(2))
    alpha = 1 if m.group(5) else int(m.group(4))
    rest = norm[m.end():].strip()
    if d1[0] == 'n' and d2[0] == 'c':
        walk, fixed, base = 'rows', d2[1], d1[1]
    elif d2[0] == 'n' and d1[0] == 'c':
        walk, fixed, base = 'cols', d1[1], d2[1]
    else:
        return None                          # both or neither dimension carries n
    m = QUANT.match(rest)
    if not m:
        return None
    quant = m.group(1).lower()
    body = rest[m.end():].strip().rstrip('.').strip()
    body = PAREN.sub('', body)               # a trailing parenthetical gloss
    noadj = False
    m = ADJ.search(body)
    if m:
        noadj = True
        body = body[:m.start()].strip().rstrip(',')
    got = _pred(body)
    if not got:
        return None
    fn, tex = got
    if quant == 'no':
        base_fn = fn
        fn = lambda a, b, c, d, f=base_fn: not f(a, b, c, d)
        tex = r'\text{not }\bigl(' + tex + r'\bigr)'
    return {'walk': walk, 'fixed': fixed, 'base': base, 'alpha': alpha, 'frac': frac,
            'quant': quant, 'pred': fn, 'tex': tex, 'noadj': noadj, 'body': body}


# -------------------------------------------------------------------------------- engine
def build(p):
    """Adjacency lists of the row-to-row (or column-to-column) digraph.

    The edge condition is a conjunction of local constraints, one per adjacent column pair,
    so the successors of a row are enumerated by a depth-first scan across the columns
    rather than by testing all S^2 pairs.
    """
    W, alpha, fn, noadj = p['fixed'], p['alpha'], p['pred'], p['noadj']
    vals = list(range(alpha + 1))
    rowwalk = p['walk'] == 'rows'
    st = list(product(vals, repeat=W))
    idx = {s: i for i, s in enumerate(st)}
    tab = {}
    for rj in vals:
        for rj1 in vals:
            for sj in vals:
                L = []
                for sj1 in vals:
                    a, b, c, d = (rj, rj1, sj, sj1) if rowwalk else (rj, sj, rj1, sj1)
                    if not fn(a, b, c, d):
                        continue
                    if noadj and (a == b or c == d or a == c or b == d):
                        continue
                    L.append(sj1)
                tab[(rj, rj1, sj)] = L
    adj = []
    for r in st:
        if W == 1:
            adj.append([idx[(v,)] for v in vals if not (noadj and v == r[0])])
            continue
        out = []
        stack = [(0, (v,)) for v in reversed(vals)]
        while stack:
            j, pref = stack.pop()
            if j == W - 1:
                out.append(idx[pref])
                continue
            for nxt in reversed(tab[(r[j], r[j + 1], pref[j])]):
                stack.append((j + 1, pref + (nxt,)))
        out.sort()
        adj.append(out)
    return st, adj


def matvec(adj, v):
    return [sum(v[s] for s in row) for row in adj]


def terms(adj, S, N):
    """terms[j] = number of admissible configurations with j+1 lines."""
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
