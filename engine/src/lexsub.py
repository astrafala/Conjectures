#!/usr/bin/env python3
"""Distinct images of a 2 X 2 subblock statistic over a lex-ordered binary source.

    Number of n X 2 (-1,0,1) arrays of determinants of 2 X 2 subblocks of some (n+1) X 3
      binary array with rows and columns of the latter in lexicographically nondecreasing order.
    Number of n X 3 0,1 arrays indicating 2 X 2 subblocks of some larger (n+1) X 4 binary
      array having a sum of zero, with rows and columns of the latter in lexicographically
      nondecreasing order.

Two things are happening at once and each is already a solved shape elsewhere in this engine
set.  The SOURCE is an (n+1) X (k+1) binary array whose rows are lexicographically nondecreasing
downwards and whose columns are lexicographically nondecreasing rightwards -- `arrlex`'s walk:
the row order is a condition on two consecutive rows, and the column order needs one bit per
adjacent column pair saying whether that pair is still equal or has already gone strictly less.
The OUTPUT is the DISTINCT images of a map whose value on output row i is a function of source
rows i and i+1 -- `winimage`'s subset construction: a state is the set of (source row, column
flags) pairs consistent with the output emitted so far.

So the NFA has 2^(k+1) * 2^k states, the output alphabet is the set of possible output rows, and
the entry's a(n) is the number of distinct output words of length n, i.e. the number of length-n
paths in the subset automaton.  Lumping by identical future behaviour is what keeps that
automaton small enough to read a degree bound off.

Nothing about the statistic matters beyond its being a function of the four cells, so
determinants, permanents, sums, diagonal-minus-antidiagonal, the lex-order indicators and the
various sum indicators are one engine.
"""
import re
from itertools import product

# ---------------------------------------------------------------- the statistic on one block
# x00 = A[i][j], x01 = A[i][j+1], x10 = A[i+1][j], x11 = A[i+1][j+1].
# DIAGONAL is x00, x11; ANTIDIAGONAL is x01, x10; ADJACENT inside the block means joined by an
# edge -- (x00,x01), (x10,x11), (x00,x10), (x01,x11) -- never by a diagonal.  Same readings as
# src/indep2x2.py, which shares no code with this file.


def _stat(kind, a, b, c, d):
    if kind == 'det':
        return a * d - b * c
    if kind == 'perm':
        return a * d + b * c
    if kind == 'sum':
        return a + b + c + d
    if kind == 'diagminusanti':
        return (a + d) - (b + c)
    if kind == 'lexinc':
        return 1 if ((a, b) < (c, d) and (a, c) < (b, d)) else 0
    if kind == 'lexnondec':
        return 1 if ((a, b) <= (c, d) and (a, c) <= (b, d)) else 0
    if kind == 'nzdet':
        return 1 if a * d - b * c else 0
    if kind == 'oddsum':
        return (a + b + c + d) & 1
    if kind == 'adj10':
        pairs = ((a, b), (c, d), (a, c), (b, d))
        return 1 if ((1, 1) in pairs and (0, 0) in pairs) else 0
    if kind[0] == 'e':                      # sum equal to t
        return 1 if a + b + c + d == int(kind[1:]) else 0
    if kind[0] == 'l':                      # sum at most t
        return 1 if a + b + c + d <= int(kind[1:]) else 0
    raise ValueError(kind)


# ---------------------------------------------------------------- reading the name
_NUM = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4}
_TAIL = (r'with rows and columns of the latter in lexicographically nondecreasing order\s*\.?\s*$')

# "Number of n X 2 (-1,0,1) arrays of determinants of 2 X 2 subblocks of some (n+1) X 3 binary
#  array with rows and ..."
_FORM1 = re.compile(
    r'(?i)^Number of n X (\d+) \S+ arrays of (determinants|sums|permanents) of 2 X 2 subblocks '
    r'of some \(n\+1\) X (\d+) binary array ' + _TAIL)
# "... arrays of 2 X 2 subblock diagonal sums minus antidiagonal sums for some (n+1) X 3 ..."
_FORM1B = re.compile(
    r'(?i)^Number of n X (\d+) \S+ arrays of 2 X 2 subblock diagonal sums minus antidiagonal '
    r'sums for some \(n\+1\) X (\d+) binary array ' + _TAIL)
# "... binary arrays indicating whether each 2 X 2 subblock of a larger binary array has
#  lexicographically increasing rows and columns, for some larger (n+1) X 3 binary array ..."
_FORM2 = re.compile(
    r'(?i)^Number of n X (\d+) binary arrays indicating whether each 2 X 2 subblock of a larger '
    r'binary array has lexicographically (increasing|nondecreasing) rows and columns, for some '
    r'larger \(n\+1\) X (\d+) binary array ' + _TAIL)
# "... 0,1 arrays indicating 2 X 2 subblocks of some larger (n+1) X 3 binary array having
#  a sum of two, with rows and ..."
_FORM3 = re.compile(
    r'(?i)^Number of n X (\d+) 0,1 arrays indicating 2 X 2 subblocks of some larger '
    r'\(n\+1\) X (\d+) binary array having (.+?), ' + _TAIL)

_COND3 = {
    'nonzero determinant': 'nzdet',
    'an odd sum': 'oddsum',
    "two adjacent 1's and two adjacent 0's": 'adj10',
}


def _cond3(t):
    t = ' '.join(t.lower().split())
    if t in _COND3:
        return _COND3[t]
    m = re.match(r'^a sum of (\w+)(?: or less)?$', t)
    if m and m.group(1) in _NUM:
        return ('l' if t.endswith('or less') else 'e') + str(_NUM[m.group(1)])
    return None


def parse_name(nm):
    nm = ' '.join(nm.split())
    m = _FORM1.match(nm)
    if m:
        kind = {'determinants': 'det', 'sums': 'sum', 'permanents': 'perm'}[m.group(2).lower()]
        k, w = int(m.group(1)), int(m.group(3))
    else:
        m = _FORM1B.match(nm)
        if m:
            kind, k, w = 'diagminusanti', int(m.group(1)), int(m.group(2))
        else:
            m = _FORM2.match(nm)
            if m:
                kind = 'lexinc' if m.group(2).lower() == 'increasing' else 'lexnondec'
                k, w = int(m.group(1)), int(m.group(3))
            else:
                m = _FORM3.match(nm)
                if not m:
                    return None
                kind = _cond3(m.group(3))
                if kind is None:
                    return None
                k, w = int(m.group(1)), int(m.group(2))
    if w != k + 1:
        # the source is one column wider than the output, because a 2 X 2 window over w columns
        # leaves w-1 of them.  A name that says otherwise is not this shape; refuse it rather
        # than silently counting something else.
        return None
    if k > 5:
        return None
    return {'engine': 'lexsub', 'k': k, 'kind': kind, 'frac': 1}


# ---------------------------------------------------------------- the automaton
def _colflags(f, r, k):
    """update the per-adjacent-column-pair status on reading source row r; None if col j > col j+1."""
    g = 0
    for j in range(k):
        if f >> j & 1:                       # already strictly less: nothing further to check
            g |= 1 << j
        elif r[j] < r[j + 1]:
            g |= 1 << j
        elif r[j] > r[j + 1]:
            return None
    return g


def build(p, cap=400000):
    k, kind = p['k'], p['kind']
    W = k + 1
    rows = list(product((0, 1), repeat=W))

    nfa = []                                 # (row, colflags)
    nid = {}

    def nsid(s):
        if s not in nid:
            nid[s] = len(nfa)
            nfa.append(s)
        return nid[s]

    start = []
    for r in rows:
        f = _colflags(0, r, k)
        if f is not None:
            start.append(nsid((r, f)))

    # NFA transitions, built lazily: from (r,f), any row s with r <= s lexicographically and a
    # legal column update, emitting the output row it forces.
    trans = {}

    def out_of(i):
        if i in trans:
            return trans[i]
        r, f = nfa[i]
        by = {}
        for s in rows:
            if s < r:
                continue
            g = _colflags(f, s, k)
            if g is None:
                continue
            o = tuple(_stat(kind, r[j], r[j + 1], s[j], s[j + 1]) for j in range(k))
            by.setdefault(o, set()).add(nsid((s, g)))
        trans[i] = by
        return by

    states, index = [], {}

    def sid(S):
        if S not in index:
            index[S] = len(states)
            states.append(S)
        return index[S]

    s0 = sid(frozenset(start))
    adj = {}
    i = 0
    while i < len(states):
        S = states[i]
        by = {}
        for q in S:
            for o, T in out_of(q).items():
                by.setdefault(o, set()).update(T)
        adj[i] = [sid(frozenset(T)) for T in by.values()]
        i += 1
        if len(states) > cap:
            return None

    import lumpauto
    st = [0] * len(states)
    st[s0] = 1
    wadj, wstart, wend, K = lumpauto.lump(adj, st, [1] * len(states))
    return {'adj': {i: r for i, r in enumerate(wadj)}, 'startv': wstart, 'endv': wend,
            'S': K, 'raw': len(states), 'nfa': len(nfa)}


def terms(b, N):
    """out[n] = number of distinct n X k output arrays; the entry's offset is 1."""
    adj, S = b['adj'], b['S']
    vec = list(b['startv'])
    ev = b['endv']
    out = [sum(v * e for v, e in zip(vec, ev))]
    for _ in range(N + 1):
        nxt = [0] * S
        for i, v in enumerate(vec):
            if not v:
                continue
            for j in adj[i]:
                nxt[j] += v
        vec = nxt
        out.append(sum(v * e for v, e in zip(vec, ev)))
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
