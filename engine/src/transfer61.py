#!/usr/bin/env python3
"""`Number of (n+1) X W 0..m arrays with column and row pair sums b(i,j)=a(i,j)+a(i,j-1) and
c(i,j)=a(i,j)+a(i-1,j) <condition>.'

Two derived arrays are formed from the array `a': `b' adds each cell to its LEFT neighbour and
`c' adds each cell to the one ABOVE it. The entries then ask one of three things of them:

    nondecreasing in column and row directions, respectively
        b(i,j) <= b(i+1,j) and c(i,j) <= c(i,j+1);

    rows of b and columns of c lexicographically nondecreasing
        row i of b is at most row i+1 of b, and column j of c is at most column j+1 of c,
        each in lexicographic order;

    b(i,j)*b(i-1,j) - c(i,j)*c(i,j-1) nonzero.

The first and third are conditions on two consecutive rows of `a' and nothing more --- for the
third, every one of the four terms is built from rows `i-1' and `i' --- so a single row is a
state. The row comparison of the second is likewise a condition on two consecutive rows, since
a row of `b' is built from one row of `a'. The COLUMN comparison of the second is not local:
which of two columns of `c' is smaller is settled by the first row in which they differ, so the
state carries one bit for each adjacent pair of columns saying whether that pair has been equal
in every row so far.
"""
import re
from itertools import product

import namecanon
import transfer19

SHAPE = r'(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))\s*X\s*(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))'
NAME = re.compile(
    r'Number of\s+' + SHAPE + r'\s*0\.\.(\d+)\s*arrays with column and row pair sums\s+'
    r'b\(i,j\)\s*=\s*a\(i,j\)\+a\(i,j-1\)\s*and\s*c\(i,j\)\s*=\s*a\(i,j\)\+a\(i-1,j\)\s+'
    r'(.*?)\s*\.?\s*$', re.I)

MONO = re.compile(r'^nondecreasing in column and row directions, respectively$', re.I)
LEX = re.compile(r'^such that rows of b\(i,j\) and columns of c\(i,j\) are lexicographically '
                 r'(nondecreasing|nonincreasing)$', re.I)
DET = re.compile(r'^such that b\(i,j\)\*b\(i-1,j\)\s*-\s*c\(i,j\)\*c\(i,j-1\) is nonzero$',
                 re.I)


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = NAME.search(nm)
    if not m:
        return None
    ra = m.group(1) or m.group(3)
    rb = int(m.group(2) or 0)
    ca = m.group(4) or m.group(6)
    cb = int(m.group(5) or 0)
    if (ra == 'n') == (ca == 'n'):
        return None
    if ra == 'n':
        W, trans = int(ca) + cb, False
    else:
        W, trans = int(ra) + rb, True
    if trans:
        return None        # b and c name the array's own axes, which transposing exchanges
    alpha = int(m.group(7))
    body = m.group(8)
    if MONO.match(body):
        kind, up = 'mono', True
    elif LEX.match(body):
        kind, up = 'lex', LEX.match(body).group(1).lower() == 'nondecreasing'
    elif DET.match(body):
        kind, up = 'det', True
    else:
        return None
    if W < 1:
        return None
    return {'W': W, 'alpha': alpha, 'kind': kind, 'up': up, 'frac': 1}


def build(p, cap=40000):
    W, A, kind = p['W'], p['alpha'] + 1, p['kind']
    if A ** W > 40 * cap:
        return None
    rows = list(product(range(A), repeat=W))

    def brow(r):
        return [r[j] + r[j - 1] for j in range(1, W)]

    idx, order, adj = {}, [], []

    def push(st):
        if st not in idx:
            idx[st] = len(order)
            order.append(st)
            adj.append(None)
        return idx[st]

    if kind in ('mono', 'det'):
        push(None)
        t = 0
        while t < len(order):
            r = order[t]
            row = []
            for s in rows:
                if r is not None:
                    if kind == 'mono':
                        if any(x > y for x, y in zip(brow(r), brow(s))):
                            continue
                        c = [s[j] + r[j] for j in range(W)]
                        if any(c[j] > c[j + 1] for j in range(W - 1)):
                            continue
                    else:
                        bs, br = brow(s), brow(r)
                        c = [s[j] + r[j] for j in range(W)]
                        if any(bs[j - 1] * br[j - 1] - c[j] * c[j - 1] == 0
                               for j in range(1, W)):
                            continue
                row.append(push(s))
            adj[t] = row
            t += 1
            if len(order) > cap:
                return None
        n = len(order)
        st = [0] * n
        st[0] = 1
        return adj, st, [1] * n, n

    up = p['up']
    push((None, (True,) * (W - 1)))
    t = 0
    while t < len(order):
        r, eq = order[t]
        row = []
        for s in rows:
            if r is not None:
                bs, br = brow(s), brow(r)
                if (br > bs) if up else (br < bs):
                    continue
                c = [s[j] + r[j] for j in range(W)]
                neq, ok = [], True
                for j in range(W - 1):
                    if not eq[j]:
                        neq.append(False)
                        continue
                    if c[j] == c[j + 1]:
                        neq.append(True)
                    elif (c[j] < c[j + 1]) == up:
                        neq.append(False)
                    else:
                        ok = False
                        break
                if not ok:
                    continue
                row.append(push((s, tuple(neq))))
            else:
                row.append(push((s, eq)))
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
