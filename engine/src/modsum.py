#!/usr/bin/env python3
"""2 X n arrays over 0..A in which no element equals a shifted running sum, modulo M.

    Number of 2Xn 0..3 arrays with no element equal to zero plus the sum of elements to its
      left or one plus the sum of the elements above it or one plus the sum of the elements
      diagonally to its northwest or one plus the sum of the elements antidiagonally to its
      northeast, modulo 4.

14 entries, none read. The four sums look unbounded, but every comparison is taken MODULO M, so
only the residues matter and the state is finite. Reading the array column by column, the sum to
the left of a cell is its row's running sum; the sum above it is the cell over it in the same
column; the sum diagonally to the north-west is the cell above and one column back. The sum
ANTIDIAGONALLY to the north-east is the cell above and one column FORWARD, which has not been
read yet, so that comparison is deferred by one column -- and at the last column it is the empty
sum, which is what the walk accepts on.
"""
import re

WORD = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5}
NAME = re.compile(
    r'^\s*Number of 2 ?X ?n 0\.\.(\d+) arrays with no element equal to '
    r'(.*?) the sum of elements to its left or '
    r'(.*?) the sum of the elements above it or '
    r'(.*?) the sum of the elements diagonally to its northwest or '
    r'(.*?) the sum of the elements antidiagonally to its northeast, modulo (\d+)\s*\.?\s*$',
    re.I)


def _c(t):
    t = t.strip().lower()
    if t == '':
        return 0
    m = re.fullmatch(r'(\w+) plus', t)
    if not m:
        return None
    w = m.group(1)
    return WORD.get(w, int(w) if w.isdigit() else None)


def parse_name(nm):
    m = NAME.match(' '.join(nm.split()))
    if not m:
        return None
    A, M = int(m.group(1)), int(m.group(6))
    cs = [_c(m.group(i)) for i in (2, 3, 4, 5)]
    if any(c is None for c in cs) or not 1 <= A <= 8 or not 2 <= M <= 12:
        return None
    return {'engine': 'modsum', 'A': A, 'M': M, 'c': tuple(cs), 'frac': 1}


def build(p, cap=200000):
    A, M, c = p['A'], p['M'], p['c']
    c1, c2, c3, c4 = c
    V = range(A + 1)
    states, index = [], {}

    def sid(s):
        if s not in index:
            index[s] = len(states)
            states.append(s)
        return index[s]

    # (row sums so far, the previous column, or None before the first)
    s0 = sid((0, 0, None))
    adj = {}
    i = 0
    while i < len(states):
        s1, s2, prev = states[i]
        out = []
        for v1 in V:
            if v1 % M in ((c1 + s1) % M, c2 % M, c3 % M, c4 % M):
                continue
            if prev is not None and prev[1] % M == (c4 + v1) % M:
                continue                       # the deferred north-east comparison
            nw = 0 if prev is None else prev[0]
            for v2 in V:
                if v2 % M in ((c1 + s2) % M, (c2 + v1) % M, (c3 + nw) % M):
                    continue
                out.append(sid(((s1 + v1) % M, (s2 + v2) % M, (v1, v2))))
                if len(states) > cap:
                    return None
        adj[i] = out
        i += 1
    # a walk ends on a column whose row-2 cell survives the empty north-east sum
    end = [i for i, (s1, s2, prev) in enumerate(states)
           if prev is not None and prev[1] % M != c4 % M]
    return {'adj': adj, 'start': [s0], 'end': end, 'S': len(states)}


def terms(b, N):
    adj, S = b['adj'], b['S']
    es = set(b['end'])
    vec = [0] * S
    for s in b['start']:
        vec[s] += 1
    out = [1]
    for _ in range(N):
        nxt = [0] * S
        for i, v in enumerate(vec):
            if not v:
                continue
            for j in adj[i]:
                nxt[j] += v
        vec = nxt
        out.append(sum(v for i, v in enumerate(vec) if i in es))
    return out


def threshold(b, coeffs, order):
    S = b['S']
    t = terms(b, 2 * S + order + 30)
    last, run = None, 0
    for j in range(order, len(t)):
        u = t[j] - sum(c * t[j - i] for i, c in coeffs.items())
        if u:
            last, run = j, 0
        else:
            run += 1
    if run < S + order:
        return None
    return last if last is not None else 0
