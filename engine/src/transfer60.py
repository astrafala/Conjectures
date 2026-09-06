#!/usr/bin/env python3
"""`Number of n X W 0..m arrays with some element plus some horizontally or vertically
adjacent neighbor totalling two no more than once.'

This is a GLOBAL condition, not a local one: over the whole array, the number of PAIRS of
adjacent cells whose two entries add up to a stated total must be at most one, or exactly one.
Nothing about a bounded window decides it.

What is bounded is the count itself, once it is capped. Carry in the state the number of such
pairs seen so far, stopped at two --- `0', `1' and `two or more' are all the distinctions the
condition can make --- together with the previous array row, which is what the next row needs
to see in order to count the pairs that straddle them. Appending a row adds the pairs lying
inside it and the pairs joining it to the row above, and the end vector accepts the states whose
count is what the entry asks for.

The pairs are unordered: the pair of cells is counted once, not once from each end.
"""
import re
from itertools import product

import namecanon
import transfer19

_W1 = r'(?:horizontally|vertically|diagonally|antidiagonally)'
NUM = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6,
       'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10}
SHAPE = r'(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))\s*X\s*(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))'

NAME = re.compile(
    r'Number of\s+' + SHAPE + r'\s*(binary|0\.\.(\d+))\s*arrays with some element plus some\s+'
    r'(' + _W1 + r'(?:[, ]+(?:or |and )?' + _W1 + r')*)\s+adjacent neighbor total+ing\s+'
    r'(\w+)\s+(no more than once|exactly once)\s*\.?\s*$', re.I)


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
    alpha = 1 if m.group(7).lower() == 'binary' else int(m.group(8))
    words = [w.lower() for w in dict.fromkeys(re.findall(_W1, m.group(9).lower()))]
    if trans:                       # transposing exchanges the two straight directions and
        words = ['vertically' if w == 'horizontally' else                # fixes the diagonals
                 'horizontally' if w == 'vertically' else w for w in words]
    tw = m.group(10).lower()
    T = int(tw) if tw.isdigit() else NUM.get(tw)
    if T is None or W < 1 or not words:
        return None
    return {'W': W, 'alpha': alpha, 'dirs': sorted(words), 'total': T,
            'exact': m.group(11).lower() == 'exactly once', 'trans': trans, 'frac': 1}


def build(p, cap=40000):
    W, A, T = p['W'], p['alpha'] + 1, p['total']
    ds = set(p['dirs'])
    if A ** W * 3 > 8 * cap:
        return None
    rows = list(product(range(A), repeat=W))

    def inside(x):
        c = 0
        if 'horizontally' in ds:
            for j in range(W - 1):
                if x[j] + x[j + 1] == T:
                    c += 1
        return c

    def across(prev, x):
        c = 0
        if 'vertically' in ds:
            for j in range(W):
                if prev[j] + x[j] == T:
                    c += 1
        if 'diagonally' in ds:
            for j in range(W - 1):
                if prev[j] + x[j + 1] == T:
                    c += 1
        if 'antidiagonally' in ds:
            for j in range(W - 1):
                if prev[j + 1] + x[j] == T:
                    c += 1
        return c

    idx, order, adj, end = {}, [], [], []

    def push(st):
        if st not in idx:
            idx[st] = len(order)
            order.append(st)
            adj.append(None)
            end.append(0)
        return idx[st]

    push((None, 0))
    t = 0
    while t < len(order):
        prev, k = order[t]
        row = []
        for x in rows:
            c = inside(x) + (0 if prev is None else across(prev, x))
            row.append(push((x, min(2, k + c))))
        adj[t] = row
        end[t] = 1 if (k == 1 if p['exact'] else k <= 1) else 0
        t += 1
        if len(order) > cap:
            return None
    n = len(order)
    st = [0] * n
    st[0] = 1
    return adj, st, end[:n], n


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
