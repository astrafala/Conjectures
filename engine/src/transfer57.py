#!/usr/bin/env python3
"""`... arrays with every 3 X 3 subblock row and column sum 3 or 6 and every diagonal and
antidiagonal sum not 3 or 6' and its relatives.

Each `K x K' window of the array carries eight lines --- its `K' rows, its `K' columns, its
main diagonal and its antidiagonal --- and the entry constrains the SUM along each of them:
some entries forbid a list of values, some require the sum to lie in a list, some ask for a
prime, and some constrain the sum of the whole window instead of its lines. Row and column
lines usually carry one rule and the two diagonals another.

A `K x K' window lies in `K' consecutive array rows, so the window of the last `K-1' rows is a
state and one step appends a row, settling every window it completes. That is the whole
construction; the work is in reading the four ways the entries write their constraint.
"""
import re
from itertools import product

import namecanon
import transfer19

SHAPE = r'(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))\s*X\s*(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))'
HEAD = re.compile(r'Number of\s+' + SHAPE + r'\s*0\.\.(\d+)\s*arrays with\s+(.*?)\s*\.?\s*$',
                  re.I)

# the entries write these lists three ways -- "3 6", "3, 6" and "1, 2, 3, 4, 5, 6, or 7" --
# and the class here allowed only the first. The "or" is stripped before matching; the commas
# were not, so every comma-separated entry silently failed to parse.
NUMS = r'[\d\s,]*\d'
# the body has "or" stripped before matching, which also removes the one inside
# "diagonal or antidiagonal" -- so the literal has to tolerate its absence, or every entry of
# this shape refuses. That is what kept 28 of them out.
P1 = re.compile(r'^no row, column, diagonal (?:or )?antidiagonal in any (\d+)\s*X\s*(\d+) subblock '
                r'summing to (' + NUMS + r')$', re.I)
P2 = re.compile(r'^every row, column, diagonal (?:or )?antidiagonal in each (\d+)\s*X\s*(\d+) '
                r'subblock summing to a prime$', re.I)
P3 = re.compile(r'^every (\d+)\s*X\s*(\d+) subblock row and column sum '
                r'(not |unequal to |equal to )?(' + NUMS + r') and every diagonal and '
                r'antidiagonal sum (not |unequal to |equal to )?(' + NUMS + r')$', re.I)
P4 = re.compile(r'^every (\d+)\s*X\s*(\d+) subblock summing to (' + NUMS + r')$', re.I)
# the two comparison forms: one line of a subblock measured against another
P5 = re.compile(r'^no (\d+)\s*X\s*(\d+) subblock diagonal sum (less than|greater than|equal to)'
                r' the antidiagonal sum'
                r'(?: central row sum (less than|greater than|equal to) the central column '
                r'sum)?$', re.I)
P6 = re.compile(r'^no (\d+)\s*X\s*(\d+) subblock '
                r'((?:(?:diagonal|antidiagonal|row|column) sum \w+(?: and no )?)+)$', re.I)
WORDNUM = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6,
           'seven': 7, 'eight': 8, 'nine': 9}
CMP = {'less than': lambda a, b: a < b, 'greater than': lambda a, b: a > b,
       'equal to': lambda a, b: a == b}


def _set(txt):
    v = [int(x) for x in re.findall(r'\d+', txt)]
    return frozenset(v) if v else None


def _prime(x):
    if x < 2:
        return False
    d = 2
    while d * d <= x:
        if x % d == 0:
            return False
        d += 1
    return True


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = HEAD.search(nm)
    if not m:
        return None
    ra = m.group(1) or m.group(3)
    rb = int(m.group(2) or 0)
    ca = m.group(4) or m.group(6)
    cb = int(m.group(5) or 0)
    if (ra == 'n') == (ca == 'n'):
        return None                        # a square array grows both ways: not one walk
    if ra == 'n':
        W, trans = int(ca) + cb, False
    else:
        W, trans = int(ra) + rb, True
    alpha = int(m.group(7))
    body = re.sub(r'\s*or\s*', ' ', m.group(8).strip(), flags=re.I)
    rules = {}
    total = None
    K = None
    g = P1.match(body)
    if g:
        K = int(g.group(1))
        s = _set(g.group(3))
        for t in ('row', 'column', 'diagonal', 'antidiagonal'):
            rules[t] = ('forbid', s)
    if K is None:
        g = P2.match(body)
        if g:
            K = int(g.group(1))
            for t in ('row', 'column', 'diagonal', 'antidiagonal'):
                rules[t] = ('prime', None)
    if K is None:
        g = P3.match(body)
        if g:
            K = int(g.group(1))
            for grp, kinds in ((3, ('row', 'column')), (5, ('diagonal', 'antidiagonal'))):
                neg = (g.group(grp) or '').strip().lower() in ('not', 'unequal to')
                s = _set(g.group(grp + 1))
                for t in kinds:
                    rules[t] = ('forbid' if neg else 'require', s)
    if K is None:
        g = P4.match(body)
        if g:
            K = int(g.group(1))
            total = _set(g.group(3))       # a SET: "summing to 2, 4, or 6" is three values
    cmps = []
    if K is None:
        g = P5.match(body)
        if g:
            K = int(g.group(1))
            cmps.append(('diagonal', 'antidiagonal', g.group(3).lower()))
            if g.group(4):
                cmps.append(('crow', 'ccol', g.group(4).lower()))
    if K is None:
        g = P6.match(body)
        if g:
            K = int(g.group(1))
            for h in re.finditer(r'(diagonal|antidiagonal|row|column) sum (\w+)', g.group(3),
                                 re.I):
                t = h.group(1).lower()
                w = h.group(2).lower()
                v = int(w) if w.isdigit() else WORDNUM.get(w)
                if v is None:
                    return None
                mode, s0 = rules.get(t, ('forbid', frozenset()))
                if mode != 'forbid':
                    return None
                rules[t] = ('forbid', s0 | {v})
    if K is None or (not rules and total is None and not cmps):
        return None
    if int(g.group(2)) != K or K < 2 or W < 1:
        return None
    if any(v[1] is None for v in rules.values() if v[0] != 'prime'):
        return None
    SW = {'row': 'column', 'column': 'row', 'crow': 'ccol', 'ccol': 'crow'}
    if trans:                              # transposing exchanges rows with columns
        rules = {SW.get(t, t): v for t, v in rules.items()}
        cmps = [(SW.get(x, x), SW.get(y, y), c) for x, y, c in cmps]
    return {'W': W, 'alpha': alpha, 'K': K,
            'total': sorted(total) if total is not None else None, 'cmps': cmps,
            'rules': {t: (mode, sorted(s) if s is not None else None)
                      for t, (mode, s) in rules.items()},
            'trans': trans, 'frac': 1}


def build(p, cap=40000):
    W, A, K = p['W'], p['alpha'] + 1, p['K']
    # a window wider than the array admits no subblock at all, and the condition is then
    # vacuous rather than unsatisfiable: `fits' loops over an empty range and says so
    rules = {t: (mode, frozenset(s) if s is not None else None)
             for t, (mode, s) in p['rules'].items()}
    total = frozenset(p['total']) if p['total'] is not None else None
    cmps = [tuple(c) for c in p.get('cmps', [])]
    if A ** W > 40 * cap:
        return None

    def okline(t, v):
        mode, s = rules[t]
        if mode == 'forbid':
            return v not in s
        if mode == 'require':
            return v in s
        return _prime(v)

    def fits(win):
        """every K x K window sitting in the K rows `win'"""
        for j in range(W - K + 1):
            blk = [[win[r][j + c] for c in range(K)] for r in range(K)]
            if total is not None:
                if sum(sum(r) for r in blk) not in total:
                    return False
                continue
            val = {'diagonal': sum(blk[r][r] for r in range(K)),
                   'antidiagonal': sum(blk[r][K - 1 - r] for r in range(K)),
                   'crow': sum(blk[K // 2]),
                   'ccol': sum(blk[r][K // 2] for r in range(K))}
            for x, y, c in cmps:
                if CMP[c](val[x], val[y]):
                    return False
            if 'row' in rules:
                for r in range(K):
                    if not okline('row', sum(blk[r])):
                        return False
            if 'column' in rules:
                for c in range(K):
                    if not okline('column', sum(blk[r][c] for r in range(K))):
                        return False
            for t in ('diagonal', 'antidiagonal'):
                if t in rules and not okline(t, val[t]):
                    return False
        return True

    rows = list(product(range(A), repeat=W))
    idx, order, adj = {}, [], []

    def push(st):
        if st not in idx:
            idx[st] = len(order)
            order.append(st)
            adj.append(None)
        return idx[st]

    push((None,) * (K - 1))
    t = 0
    while t < len(order):
        win = order[t]
        row = []
        for x in rows:
            w = win + (x,)
            if any(s is None for s in w) or fits(w):
                row.append(push(w[1:]))
        adj[t] = row
        t += 1
        if len(order) > cap:
            return None
    n = len(order)
    st = [0] * n
    st[0] = 1
    return adj, st, [1] * n, n


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
