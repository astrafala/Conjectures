#!/usr/bin/env python3
"""`... arrays with nondecreasing <f>(x(i,j),x(i,j-1)) in the i direction and nondecreasing
<g>(x(i,j),x(i-1,j)) in the j direction' and `... with nondecreasing <statistic> of every
<k> consecutive values in every row and column'.

Both shapes take a statistic of a short run of cells, form the array of its values, and ask
that array to be monotone in a named direction.

In the first shape the horizontal statistic `f' is read across a pair of neighbouring cells of
one row and the resulting array must not decrease DOWN a column, while the vertical statistic
`g' is read down a pair of neighbouring cells of one column and its array must not decrease
ALONG a row. Each of those comparisons involves two consecutive array rows and nothing else,
so a single row is a state and one step of the walk appends a row.

In the second shape one statistic is read along every run of `k' consecutive cells, in the rows
and in the columns alike, and both arrays must not decrease in their own direction. The row
comparisons live inside one row; a column comparison relates the runs starting at rows `i' and
`i+1', so it spans `k+1' rows and the state is the window of the last `k' rows.

Nothing here is invariant under renaming the alphabet --- every statistic does arithmetic on
the letters or compares them by size --- so no pattern reduction is available or attempted;
the walk runs over the alphabet the entry names.
"""
import re
from itertools import product

import namecanon
import transfer19

SHAPE = re.compile(r'\((n|\d+)\s*\+\s*(\d+)\)\s*X\s*\((n|\d+)\s*\+\s*(\d+)\)')

PAIRSTAT = {
    'sum': lambda a, b: a + b,
    'difference': lambda a, b: a - b,
    'absolute difference': lambda a, b: abs(a - b),
    'min': min,
    'max': max,
}

RUNSTAT = {
    'sum': sum,
    'maximum': max,
    'minimum': min,
    'median': lambda v: sorted(v)[len(v) // 2],
    'range': lambda v: max(v) - min(v),
}

COUNT = {'two': 2, 'three': 3, 'four': 4}

NAME_A = re.compile(
    r'Number of\s+(.*?)\s*0\.\.(\d+)\s*arrays with nondecreasing\s+(.*?)\s+in the i direction '
    r'and nondecreasing\s+(.*?)\s+in the j direction\s*\.?\s*$', re.I)
NAME_B = re.compile(
    r'Number of\s+(.*?)\s*0\.\.(\d+)\s*arrays with nondecreasing\s+(.*?)\s+of every\s+'
    r'(\w+)\s+consecutive values in every row and column\s*\.?\s*$', re.I)


def _pair(expr, later, earlier):
    """name the two-cell statistic, checking it is read in the direction the shape needs"""
    e = re.sub(r'\s+', '', expr.lower())
    a, b = 'x(%s)' % later, 'x(%s)' % earlier
    if e == a + '+' + b:
        return 'sum'
    if e == a + '-' + b:
        return 'difference'
    if e == 'absolutevalueof' + a + '-' + b:
        return 'absolute difference'
    for k in ('min', 'max'):
        if e == k + '(' + a + ',' + b + ')':
            return k
    return None


def _shape(txt):
    m = SHAPE.search(txt.replace(' ', ''))
    if not m:
        return None
    ra, rb, ca, cb = m.group(1), int(m.group(2)), m.group(3), int(m.group(4))
    if (ra == 'n') == (ca == 'n'):
        return None
    if ra == 'n':
        return int(ca) + cb, False
    return int(ra) + rb, True


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = NAME_A.search(nm)
    if m:
        sh = _shape(m.group(1))
        if not sh:
            return None
        W, trans = sh
        h = _pair(m.group(3), 'i,j', 'i,j-1')
        v = _pair(m.group(4), 'i,j', 'i-1,j')
        if h is None or v is None:
            return None
        if trans:
            h, v = v, h
        return {'kind': 'A', 'W': W, 'alpha': int(m.group(2)), 'h': h, 'v': v, 'k': 1,
                'trans': trans, 'frac': 1}
    m = NAME_B.search(nm)
    if m:
        sh = _shape(m.group(1))
        if not sh:
            return None
        W, trans = sh                  # the condition is the same along rows and columns
        s = m.group(3).strip().lower()
        s = {'maximum minus minimum': 'range', 'medians': 'median'}.get(s, s)
        if s not in RUNSTAT:
            return None
        w = m.group(4).lower()
        k = int(w) if w.isdigit() else COUNT.get(w)
        if k is None or k < 2:
            return None
        return {'kind': 'B', 'W': W, 'alpha': int(m.group(2)), 'stat': s, 'k': k,
                'trans': trans, 'frac': 1}
    return None


def _rows_B(W, A, f, k):
    """rows whose own runs do not decrease along the row"""
    out = []
    for r in product(range(A), repeat=W):
        if all(f(r[j:j + k]) <= f(r[j + 1:j + 1 + k]) for j in range(W - k)):
            out.append(r)
    return out


def build(p, cap=40000):
    W, A = p['W'], p['alpha'] + 1
    if A ** W > 40 * cap:
        return None
    if p['kind'] == 'A':
        h, v = PAIRSTAT[p['h']], PAIRSTAT[p['v']]
        rows = list(product(range(A), repeat=W))
        if len(rows) > cap:
            return None
        idx = {r: i for i, r in enumerate(rows)}

        def edge(r, s):
            for j in range(1, W):
                if h(r[j], r[j - 1]) > h(s[j], s[j - 1]):
                    return False
            for j in range(W - 1):
                if v(s[j], r[j]) > v(s[j + 1], r[j + 1]):
                    return False
            return True

        adj = [[idx[s] for s in rows if edge(r, s)] for r in rows]
        return adj, [1] * len(rows), [1] * len(rows), len(rows)
    f, k = RUNSTAT[p['stat']], p['k']
    rows = _rows_B(W, A, f, k)
    if not rows:
        return [], [], [], 0
    if len(rows) ** k > 40 * cap:
        return None
    states = list(product(rows, repeat=k))
    if len(states) > cap:
        return None
    idx = {s: i for i, s in enumerate(states)}

    def ok(win):
        """the column runs of the k+1 rows `win' do not decrease"""
        for j in range(W):
            if f([win[t][j] for t in range(k)]) > f([win[t + 1][j] for t in range(k)]):
                return False
        return True

    adj = []
    for st in states:
        row = []
        for nxt in rows:
            if ok(st + (nxt,)):
                row.append(idx[st[1:] + (nxt,)])
        adj.append(row)
    return adj, [1] * len(states), [1] * len(states), len(states)


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
