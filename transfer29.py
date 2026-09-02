#!/usr/bin/env python3
"""`Number of (n+1) X (K+1) 0..m arrays with <a signed sum of the order statistics> of every
2 X 2 subblock equal.'

The four entries of a $2\\times2$ subblock, sorted as $a\\le b\\le c\\le d$, are its minimum,
lower median, upper median and maximum; the entries of this family ask that a fixed signed sum
of those four be the SAME for every subblock of the array. The common value is not named, so
the count splits by it: fix $v$, count the arrays all of whose subblocks give $v$, and the
sets belonging to different $v$ are disjoint because the value is determined by the array.

For a fixed $v$ the condition couples two consecutive rows only, so a row is a state, an
$(n+1)$-row array is a walk of $n$ steps, and $a(n)=\\iota^\\top M^n\\tau$ with both vectors
all-ones on the disjoint union of the graphs for the possible $v$. Rows carrying no edge at
all are dropped: they can only be the whole of a one-row array, which is not what is counted.
"""
import re
from itertools import product

import namecanon
import transfer17

STAT = r'(?:the\s+)?(maximum|minimum|upper median|lower median)'
NAME = re.compile(
    r'Number of \(\s*n\s*\+\s*(\d+)\s*\)\s*X\s*\(?\s*(\d+)(?:\s*\+\s*(\d+))?\s*\)?\s*'
    r'0\.\.(\d+)\s+arrays\s+with\s+(.*?)\s+of every 2\s*X\s*2 subblock equal\s*\.?\s*$',
    re.I)


def _expr(s):
    """the signed sum, as a dict stat -> coefficient, or None"""
    s = s.strip().lower()
    if s == 'the sum of all four elements':
        return {'minimum': 1, 'lower median': 1, 'upper median': 1, 'maximum': 1}
    parts = re.split(r'\s+(plus|minus)\s+', s)
    if len(parts) % 2 == 0:
        return None
    out, sign = {}, 1
    for i, tok in enumerate(parts):
        if i % 2:
            sign = 1 if tok == 'plus' else -1
            continue
        m = re.fullmatch(STAT, tok.strip())
        if not m:
            return None
        k = m.group(1)
        if k in out:
            return None
        out[k] = sign
    return out or None


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn)])\s*[xX]\s*(?=[\dn(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = NAME.search(nm)
    if not m:
        return None
    d = int(m.group(1))
    W = int(m.group(2)) + (int(m.group(3)) if m.group(3) else 0)
    alpha = int(m.group(4))
    if d != 1 or W < 2 or alpha < 1:
        return None
    e = _expr(m.group(5))
    if e is None:
        return None
    return {'W': W, 'alpha': alpha, 'coef': e, 'frac': 1}


def build(p, cap=40000):
    W, A, coef = p['W'], p['alpha'] + 1, p['coef']
    if A ** W > 4 * cap:
        return None
    rows = list(product(range(A), repeat=W))
    key = ('minimum', 'lower median', 'upper median', 'maximum')
    cf = [coef.get(k, 0) for k in key]

    def stat(q):
        s = sorted(q)
        return cf[0] * s[0] + cf[1] * s[1] + cf[2] * s[2] + cf[3] * s[3]

    # the statistic of the pair of rows at each column, as a tuple; all must agree with v
    vals = {}
    for i, r in enumerate(rows):
        for j, s in enumerate(rows):
            t = {stat((r[k], r[k + 1], s[k], s[k + 1])) for k in range(W - 1)}
            if len(t) == 1:
                vals.setdefault(t.pop(), []).append((i, j))
    states, index, adj = [], {}, []

    def sid(k):
        i = index.get(k)
        if i is None:
            i = index[k] = len(states)
            states.append(k); adj.append([])
        return i

    for v, pairs in sorted(vals.items()):
        touched = set()
        for i, j in pairs:
            touched.add(i); touched.add(j)
        if len(states) + len(touched) > cap:
            return None
        for i, j in pairs:
            adj[sid((v, i))].append(sid((v, j)))
        for i in touched:
            sid((v, i))
    if not states:
        return None
    return states, adj


terms = transfer17.terms
threshold = transfer17.threshold
