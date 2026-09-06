#!/usr/bin/env python3
"""`... arrays with each 3 X 3 subblock <property of the block>'.

Five properties, all of them functions of the nine entries of one `3 x 3' window and nothing
else:

    the sum of the nine entries lies in a named set;
    the multiset of value multiplicities is a named partition ("three of each value",
        "two of one value, two of another, and five of the last");
    the determinant is positive;
    the sum of the absolute differences over the 36 unordered pairs equals a named number;
    every subblock has the same population.

A `3 x 3' window lies in three consecutive rows, so the state is the last two rows and one step
appends a row, settling every window it completes. The last property is the exception: it ties
blocks to each other rather than constraining each alone, and the tie is carried as one extra
number in the state --- the common population --- which the first block fixes and every later
one must match.

Three readings are pinned against published terms rather than assumed. "The same population"
is the count of EACH value, not the sum and not the number of nonzeros: over `0..2' the sum
reading gives 102789 where A224654 publishes 67797, and the count-vector reading gives 67797.
On a binary matrix the two coincide, which is why the wrong reading survived the binary
entries and was caught only by the ternary ones. "two of one value, three
of another, and four of the last" names the SORTED multiplicities `(2,3,4)' with no assignment
of values to roles. And "the sum of its 72 absolute element differences equal to 34" compares
against the sum over the 36 UNORDERED pairs: 34 is not an achievable ordered-pair sum at all,
while the unordered reading gives A234834's published 4032 exactly.
"""
import re
from itertools import product
from collections import Counter

import namecanon
import transfer19

FRAC = re.compile(r'^\s*(?:(Half)|(One\s+quarter)|(\d+)\s*/\s*(\d+))\s+the number of\s+', re.I)
HEAD = re.compile(r'^\s*Number of\s+', re.I)
SH = r'(?:\((?P<ra>n|\d+)\s*\+\s*(?P<rb>\d+)\)|(?P<rc>n|\d+))\s*X\s*' \
     r'(?:\((?P<ca>n|\d+)\s*\+\s*(?P<cb>\d+)\)|(?P<cc>n|\d+))'
SHAPE = re.compile(r'^' + SH + r'\s+(?:0\.\.(?P<m>\d+)|(?P<bin>binary))\s+'
                   r'(?:arrays?|matrices)\s+with\s+', re.I)
WORD = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9}

B_SUMSET = re.compile(r'^each 3 X 3 subblock having (?:a )?sum(?: of)? ([\d,\s]*\d(?:\s*or\s*\d+)?)$', re.I)
B_SUMRNG = re.compile(r'^each 3 X 3 subblock having a sum in (\d+)\.\.(\d+)$', re.I)
B_EACH = re.compile(r'^each 3 X 3 subblock containing (\w+) of each value$', re.I)
B_PART = re.compile(r'^each 3 X 3 subblock containing (\w+) of one value, (\w+) of another, '
                    r'and (\w+) of the last$', re.I)
B_DET = re.compile(r'^each 3 X 3 subblock having a positive determinant$', re.I)
B_POP = re.compile(r'^each 3 X 3 subblock having the same population$', re.I)
B_ABS = re.compile(r'^each 3 X 3 subblock having the sum of its \d+ absolute element '
                   r'differences equal to (\d+)(,? and no adjacent elements equal)?$', re.I)


def parse_name(nm):
    nm = namecanon.canon(nm)
    s = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    frac = 1
    m = FRAC.match(s)
    if m:
        frac = 2 if m.group(1) else (4 if m.group(2) else int(m.group(4)))
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
    body = re.sub(r'\s*3\s*X\s*3\s*', ' 3 X 3 ', s[m.end():].strip().rstrip('.')).strip()
    body = re.sub(r'\s+', ' ', body)
    p = {'W': W, 'alpha': alpha, 'trans': trans, 'frac': frac, 'noadj': False}
    g = B_SUMSET.match(body)
    if g:
        p['kind'], p['arg'] = 'sum', sorted({int(x) for x in re.findall(r'\d+', g.group(1))})
        return p
    g = B_SUMRNG.match(body)
    if g:
        p['kind'] = 'sum'
        p['arg'] = list(range(int(g.group(1)), int(g.group(2)) + 1))
        return p
    g = B_EACH.match(body)
    if g:
        k = WORD.get(g.group(1).lower())
        if k is None or k * (alpha + 1) != 9:
            return None
        p['kind'], p['arg'] = 'part', [k] * (alpha + 1)
        return p
    g = B_PART.match(body)
    if g:
        vs = [WORD.get(x.lower()) for x in g.groups()]
        if any(v is None for v in vs) or sum(vs) != 9 or alpha + 1 != 3:
            return None
        p['kind'], p['arg'] = 'part', sorted(vs)
        return p
    if B_DET.match(body):
        p['kind'], p['arg'] = 'det', None
        return p
    if B_POP.match(body):
        p['kind'], p['arg'] = 'pop', None
        return p
    g = B_ABS.match(body)
    if g:
        p['kind'], p['arg'] = 'absdiff', int(g.group(1))
        p['noadj'] = g.group(2) is not None
        return p
    return None


def _blockok(p, b):
    """b is the nine entries of a 3 x 3 window, row by row."""
    k = p['kind']
    if k == 'sum':
        return sum(b) in p['arg']
    if k == 'part':
        c = sorted(Counter(b).values())
        want = list(p['arg'])
        c = [0] * (len(want) - len(c)) + c
        return c == want
    if k == 'det':
        return (b[0] * (b[4] * b[8] - b[5] * b[7])
                - b[1] * (b[3] * b[8] - b[5] * b[6])
                + b[2] * (b[3] * b[7] - b[4] * b[6])) > 0
    # the 36 UNORDERED pairs, pinned against the data; see the module docstring
    return sum(abs(b[i] - b[j]) for i in range(9) for j in range(i + 1, 9)) == p['arg']


def build(p, cap=200000):
    W, A = p['W'], p['alpha'] + 1
    if W < 3 or A ** W > 60000:
        return None
    rows = list(product(range(A), repeat=W))
    if p['noadj']:
        rows = [r for r in rows if all(r[j] != r[j + 1] for j in range(W - 1))]
    ri = {r: i for i, r in enumerate(rows)}
    pop = p['kind'] == 'pop'

    def wins(u, v, w):
        for j in range(W - 2):
            yield [u[j], u[j + 1], u[j + 2], v[j], v[j + 1], v[j + 2],
                   w[j], w[j + 1], w[j + 2]]

    def step_ok(u, v, w):
        if p['noadj'] and (any(u[j] == v[j] for j in range(W))
                           or any(v[j] == w[j] for j in range(W))):
            return None
        out = []
        for b in wins(u, v, w):
            if pop:
                out.append(tuple(b.count(x) for x in range(A)))
            elif not _blockok(p, b):
                return None
        if pop:
            if len(set(out)) > 1:
                return None
            return out[0]
        return -1                       # a sentinel: no population to carry

    idx, order, adj, endv = {}, [], [], []

    def push(st):
        if st not in idx:
            idx[st] = len(order)
            order.append(st)
            adj.append(None)
            endv.append(1)
        return idx[st]

    push((None, None, None))            # before any row
    t = 0
    while t < len(order):
        u, v, carried = order[t]
        out = []
        for w in rows:
            if u is None or v is None:
                # still filling the first two rows: no window is complete yet
                if p['noadj'] and v is not None and any(v[j] == w[j] for j in range(W)):
                    continue
                out.append(push((v, w, carried)))
                continue
            r = step_ok(u, v, w)
            if r is None:
                continue
            if pop:
                if carried is not None and carried != r:
                    continue
                out.append(push((v, w, r)))
            else:
                out.append(push((v, w, None)))
        adj[t] = sorted(out)
        t += 1
        if len(order) > cap:
            return None
    n = len(order)
    sv = [0] * n
    sv[0] = 1
    return adj, sv, endv[:n], n


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
