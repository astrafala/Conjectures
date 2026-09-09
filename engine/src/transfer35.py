#!/usr/bin/env python3
"""`Number of (n+K-1) X W 0..m arrays with every K X K subblock COMMUTING with each horizontal
and vertical neighbor K X K subblock.'

Adjacent $K\\times K$ subblocks overlap --- horizontally in $K\\times(K-1)$ entries, vertically
in $(K-1)\\times K$ --- and the condition is that the two matrices commute, $AB=BA$ over the
integers. A subblock row is fixed by $K$ consecutive array rows, and the vertical condition
compares two consecutive subblock rows, so $K$ consecutive rows are a state and one step
appends a row. An array of $n+K-1$ rows is a walk of $n-1$ steps.

There is no compressing this state: what the next step needs is the previous subblock row, and
for $W\\ge K$ that row determines the $K$ array rows it came from. So the reach is set by
$(m+1)^{KW}$, and the wider or larger-alphabet members of the family are out of range here
rather than settled.
"""
import re
from itertools import product

import namecanon
import transfer17

NAME = re.compile(
    r'Number of \(\s*n\s*\+\s*(\d+)\s*\)\s*X\s*(\d+)\s*'
    r'(?:0\.\.(\d+)|(binary))\s+arrays\s+with\s+(every|no)\s+(\d+)\s*X\s*\6\s+subblock\s+'
    r'(having nonzero determinant and )?commuting with\s+'
    r'(?:each|any|every)(?:\s+of\s+its)?\s+horizontal\s+(?:and|or)\s+vertical\s+'
    r'(?:neighbor\s+)?(?:\d+\s*X\s*\d+\s+)?(?:subblock\s+)?(?:neighbors?|subblocks?)?\s*\.?\s*$',
    re.I)


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn)])\s*[xX]\s*(?=[\dn(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = NAME.search(nm)
    if not m:
        return None
    d = int(m.group(1))
    W = int(m.group(2))
    alpha = 1 if m.group(4) else int(m.group(3))
    every = m.group(5).lower() == 'every'
    K = int(m.group(6))
    det = bool(m.group(7))
    if d != K - 1 or W < K or K < 2 or alpha < 1:
        return None
    if det and K != 2:
        return None
    return {'K': K, 'W': W, 'alpha': alpha, 'every': every, 'det': det, 'frac': 1}


def _mul(A, B, K):
    return tuple(tuple(sum(A[i][t] * B[t][j] for t in range(K)) for j in range(K))
                 for i in range(K))


def _comm(A, B, K):
    return _mul(A, B, K) == _mul(B, A, K)


def build(p, cap=40000):
    K, W, A, every, det = p['K'], p['W'], p['alpha'] + 1, p['every'], p['det']
    # A ** (K * W) is exactly right and I briefly replaced it with something worse. The
    # states are K-tuples of rows -- `product(rows, repeat=K)' below -- so there are
    # (A^W)^K = A^(K*W) of them, not A^W. Reading the refusal as though the rows were the
    # states turned a fast refusal into a slow one: the loop still walks the whole product
    # and only gives up once `len(states) > cap' fires, after minutes rather than instantly.
    if A ** (K * W) > 2_000_000:
        return None
    rows = list(product(range(A), repeat=W))
    nb = W - K + 1                                  # subblocks across

    def blocks(t):
        return [tuple(tuple(t[i][j + c] for c in range(K)) for i in range(K))
                for j in range(nb)]

    def okself(t):
        B = blocks(t)
        if det:
            for M in B:
                if M[0][0] * M[1][1] - M[0][1] * M[1][0] == 0:
                    return None
        for j in range(nb - 1):
            if _comm(B[j], B[j + 1], K) != every:
                return None
        return B

    states, index, adj, blk = [], {}, [], []

    def sid(t):
        i = index.get(t)
        if i is None:
            i = index[t] = len(states)
            states.append(t); adj.append(None); blk.append(None)
        return i

    for t in product(rows, repeat=K):
        B = okself(t)
        if B is None:
            continue
        i = sid(t)
        blk[i] = B
        if len(states) > cap:
            return None
    if not states:
        return None
    bysuffix = {}
    for i, t in enumerate(states):
        bysuffix.setdefault(t[:K - 1], []).append(i)
    for i, t in enumerate(states):
        row = []
        for j in bysuffix.get(t[1:], ()):
            if all(_comm(blk[i][c], blk[j][c], K) == every for c in range(nb)):
                row.append(j)
        adj[i] = row
    return states, adj


terms = transfer17.terms
threshold = transfer17.threshold
