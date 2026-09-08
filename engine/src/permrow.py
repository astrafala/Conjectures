#!/usr/bin/env python3
"""Arrays whose rows are permutations, ordered by a condition on consecutive rows.

    Number of n X 4 arrays with each row a permutation of 1..4 having at least as many
    downsteps as the preceding row, with rows in lexicographically nonincreasing order.

No engine read one: every array engine expects a name giving a value range like "0..3", and
these give a permutation of 1..W instead. The object is as easy as anything in the project --
the rows are the W! permutations, the condition compares a row with the one before it, so the
count is a walk count on W! vertices. For W = 4 that is 24 states.

The reading was pinned by direct enumeration before the engine was written: for A222002 the
model gives 24, 157, 704, 2470, 7328, 19228 and the entry publishes exactly those.
"""
import re
from itertools import permutations

HEAD = re.compile(
    r'^\s*Number of\s+(?:n\s*X\s*(\d+)|(\d+)\s*X\s*n)\s+arrays with each row a permutation of '
    r'(\d+)\.\.(\d+)\s+(.+?)\s*\.?\s*$', re.I)
COND = {
    'at least as many downsteps as the preceding row': ('ds', '>='),
    'at least as many descents as the preceding row': ('ds', '>='),
    'no more downsteps than the preceding row': ('ds', '<='),
    'at least as many upsteps as the preceding row': ('us', '>='),
}
ORDER = {
    'lexicographically nonincreasing order': 'noninc',
    'lexicographically nondecreasing order': 'nondec',
}


def parse_name(nm):
    m = HEAD.match(re.sub(r'\s+', ' ', nm).strip())
    if not m:
        return None
    W = int(m.group(1) or m.group(2))
    lo, hi = int(m.group(3)), int(m.group(4))
    if hi - lo + 1 != W or W < 2 or W > 6:  # 7! is 5040 states, too dense to build
        return None
    body = m.group(5).lower().rstrip('.')
    stat = order = None
    for k, v in COND.items():
        if k in body:
            stat = v
            break
    for k, v in ORDER.items():
        if k in body:
            order = v
            break
    if stat is None:
        return None
    # every clause must be accounted for, or the name says more than the model does
    left = body
    for k in list(COND) + list(ORDER):
        left = left.replace(k, '')
    # the leftover check rejected the word 'having', so every name in the family
    # failed a test meant only to catch clauses the model does not implement
    left = re.sub(r'[,\s]|with|rows|in|and|having|the|preceding|row', '', left)
    if left:
        return None
    return {'W': W, 'lo': lo, 'stat': stat, 'order': order, 'frac': 1}


def _steps(p, kind):
    if kind == 'ds':
        return sum(1 for i in range(len(p) - 1) if p[i] > p[i + 1])
    return sum(1 for i in range(len(p) - 1) if p[i] < p[i + 1])


def build(p, cap=200000):
    W = p['W']
    rows = list(permutations(range(p['lo'], p['lo'] + W)))
    if len(rows) > cap:
        return None
    kind, rel = p['stat']
    st = [_steps(r, kind) for r in rows]
    n = len(rows)
    adj = [[0] * n for _ in range(n)]
    for i, a in enumerate(rows):
        for j, b in enumerate(rows):
            ok = (st[j] >= st[i]) if rel == '>=' else (st[j] <= st[i])
            if not ok:
                continue
            if p['order'] == 'noninc' and not (b <= a):
                continue
            if p['order'] == 'nondec' and not (b >= a):
                continue
            adj[i][j] = 1
    return {'adj': adj, 'S': n}


def terms(b, N):
    n = b['S']
    v = [1] * n
    out = [0]
    for _ in range(N + 1):
        out.append(sum(v))
        nv = [0] * n
        for i, row in enumerate(b['adj']):
            if v[i]:
                for j in range(n):
                    if row[j]:
                        nv[j] += v[i]
        v = nv
    return out


def threshold(b, coeffs, order):
    S = b['S']
    t = terms(b, 2 * S + order + 8)
    last, run = None, 0
    for j in range(order, len(t)):
        u = t[j] - sum(c * t[j - i] for i, c in coeffs.items())
        if u:
            last, run = j, 0
        else:
            run += 1
    if run < S:
        return None
    return last if last is not None else 0
