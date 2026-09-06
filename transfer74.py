#!/usr/bin/env python3
"""`Number of (n+1) X (2+1) 0..2 arrays with the minimum plus the maximum equal to the lower
median plus the upper median in every 2 X 2 subblock.'

For the four values of a `2 x 2' block, sorted as `a <= b <= c <= d', the minimum plus the
maximum is `a + d' and the two medians are `b' and `c', so the entry's condition is
`a + d = b + c' --- or its negation, which half the family states instead.

That is a condition on two consecutive rows and nothing wider, so the state is the last row and
a step appends one. The whole engine is the predicate.
"""
import re
from itertools import product

import namecanon
import transfer19

FRAC = re.compile(r'^\s*(?:(Half)|One\s+quarter|1\s*/\s*(\d+))\s+the number of\s+', re.I)
HEAD = re.compile(r'^\s*Number of\s+', re.I)
SH = r'(?:\((?P<ra>n|\d+)\s*\+\s*(?P<rb>\d+)\)|(?P<rc>n|\d+))\s*X\s*' \
     r'(?:\((?P<ca>n|\d+)\s*\+\s*(?P<cb>\d+)\)|(?P<cc>n|\d+))'
SHAPE = re.compile(r'^' + SH + r'\s+(?:0\.\.(?P<m>\d+)|(?P<bin>binary))\s+arrays?\s+with\s+',
                   re.I)
BODY = re.compile(r'^the minimum plus the maximum\s+(un)?equal to the lower median plus the '
                  r'upper median in every 2\s*X\s*2 subblock$', re.I)


def parse_name(nm):
    nm = namecanon.canon(nm)
    s = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    frac = 1
    m = FRAC.match(s)
    if m:
        frac = 2 if m.group(1) else (4 if m.group(0).lower().startswith('one quarter')
                                     else int(m.group(2)))
        s = s[m.end():]
    else:
        m = HEAD.match(s)
        if not m:
            return None
        s = s[m.end():]
    m = SHAPE.match(s)
    if not m:
        return None
    rows = m.group('ra') or m.group('rc')
    cols = m.group('ca') or m.group('cc')
    if rows is None or cols is None or (rows == 'n') == (cols == 'n'):
        return None
    if rows == 'n':
        W, trans = int(cols) + int(m.group('cb') or 0), False
    else:
        W, trans = int(rows) + int(m.group('rb') or 0), True
    alpha = 1 if m.group('bin') else int(m.group('m'))
    body = s[m.end():].strip().rstrip('.')
    b = BODY.match(body)
    if not b:
        return None
    # the condition is symmetric in the four cells of a block, so transposing the array does
    # not change it and 'trans' only records which side the entry lets grow
    return {'W': W, 'alpha': alpha, 'equal': b.group(1) is None, 'trans': trans, 'frac': frac}


def build(p, cap=200000):
    W, A, want = p['W'], p['alpha'] + 1, p['equal']
    if A ** W > 200000:
        return None
    rows = list(product(range(A), repeat=W))

    def ok(u, v):
        for j in range(W - 1):
            s = sorted((u[j], u[j + 1], v[j], v[j + 1]))
            if ((s[0] + s[3]) == (s[1] + s[2])) != want:
                return False
        return True

    idx = {r: i for i, r in enumerate(rows)}
    adj = [[idx[v] for v in rows if ok(u, v)] for u in rows]
    n = len(rows)
    return adj, [1] * n, [1] * n, n


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
