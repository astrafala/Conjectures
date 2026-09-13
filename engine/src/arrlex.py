#!/usr/bin/env python3
"""n X k arrays over a fixed alphabet with lexicographic order on rows and columns.

    Number of n X 4 0..1 arrays with rows and columns lexicographically nondecreasing.
    Number of n X 3 0..1 arrays with rows and columns lexicographically nondecreasing and
      every element equal to at least one horizontal or vertical neighbor.

The height grows and the width and alphabet are fixed, so a row transfer counts these -- but
neither condition is local to a pair of rows on its own, which is why no engine read them.

* **Rows lexicographically nondecreasing** IS local: row_i <= row_{i+1}, a condition on the
  pair, so the previous row is part of the state anyway.
* **Columns lexicographically nondecreasing** is not: column j and column j+1 are compared over
  the whole height. One bit per adjacent pair carries it -- `still equal' or `already strictly
  less' -- and a pair that would go strictly greater kills the walk. k-1 bits.
* **Every element equal to at least one horizontal or vertical neighbour** is not either: an
  element's obligation can be met by the row BELOW, which has not been chosen yet. One bit per
  position of the previous row carries that, and the walk may only end with none outstanding.

So the state is (previous row, the k-1 column flags, the k pending bits) and the count is a
walk count in a finite digraph, which is what every transfer-matrix paper here already settles:
det(I - xM) has degree at most the number of states, so the residual test proves a conjectured
recurrence rather than checking it.
"""
import re
from itertools import product

NAME = re.compile(
    r'^\s*Number of n ?X ?(\d+) 0\.\.(\d+) arrays with rows and columns lexicographically '
    r'nondecreasing\s*(.*?)\s*\.?\s*$', re.I)

TAILS = {
    '': (),
    'and every element equal to at least one horizontal or vertical neighbor': ('nbr',),
    'read forwards and nonincreasing read backwards': ('back',),
    'read forwards, and nonincreasing read backwards': ('back',),
}


def parse_name(nm):
    m = NAME.match(' '.join(nm.split()))
    if not m:
        return None
    k, A = int(m.group(1)), int(m.group(2))
    tail = ' '.join(m.group(3).lower().split())
    if tail not in TAILS:
        return None
    if not 1 <= k <= 7 or not 1 <= A <= 4 or (A + 1) ** k > 20000:
        return None
    return {'engine': 'arrlex', 'k': k, 'A': A, 'flags': TAILS[tail], 'frac': 1}


def _rows(k, A):
    return list(product(range(A + 1), repeat=k))


def build(p, cap=200000):
    k, A, fl = p['k'], p['A'], p['flags']
    rows = _rows(k, A)
    R = len(rows)
    back = 'back' in fl
    nbr = 'nbr' in fl
    # Each adjacent column pair carries a flag. Read FORWARDS (top to bottom) the pair must be
    # lexicographically nondecreasing, which is decided by its FIRST difference; read BACKWARDS
    # (bottom to top) it must be nonincreasing, which is decided by its LAST difference. So the
    # flag is 0 while the two columns agree, 1 once they have differed with the latest
    # difference `less', and 2 once they have differed with the latest difference `greater' --
    # and a pair whose FIRST difference is `greater' is dead either way. Without the backward
    # condition only 0 and 1 occur and both are accepted at the end; with it, 1 is not.
    def colstep(flags, cur):
        out = 0
        for j in range(k - 1):
            b = flags // (3 ** j) % 3
            if cur[j] == cur[j + 1]:
                nb = b
            elif cur[j] < cur[j + 1]:
                nb = 1
            else:
                if b == 0:
                    return None                       # the first difference goes the wrong way
                nb = 2
            out += nb * (3 ** j)
        return out

    def okrow(prev, cur):
        if prev is None:
            return True
        if list(cur) < list(prev):
            return False
        if back and list(cur[::-1]) > list(prev[::-1]):
            return False
        return True

    def horiz(cur):
        """positions already matched by a horizontal neighbour."""
        s = 0
        for j in range(k):
            if (j and cur[j] == cur[j - 1]) or (j + 1 < k and cur[j] == cur[j + 1]):
                s |= 1 << j
        return s

    states, index = [], {}

    def sid(s):
        if s not in index:
            index[s] = len(states)
            states.append(s)
        return index[s]

    start = []
    for ri, cur in enumerate(rows):
        f = colstep(0, cur)
        if f is None:
            continue
        pend = 0
        if nbr:
            pend = ((1 << k) - 1) & ~horiz(cur)
        start.append(sid((ri, f, pend)))
    adj = {}
    i = 0
    while i < len(states):
        ri, f, pend = states[i]
        prev = rows[ri]
        out = []
        for rj, cur in enumerate(rows):
            if not okrow(prev, cur):
                continue
            nf = colstep(f, cur)
            if nf is None:
                continue
            npend = 0
            if nbr:
                if any(pend >> j & 1 and cur[j] != prev[j] for j in range(k)):
                    continue
                npend = ((1 << k) - 1) & ~horiz(cur)
                npend &= ~sum(1 << j for j in range(k) if cur[j] == prev[j])
            out.append(sid((rj, nf, npend)))
            if len(states) > cap:
                return None
        adj[i] = out
        i += 1
    def colend(f):
        if not back:
            return True
        return all(f // (3 ** j) % 3 != 1 for j in range(k - 1))
    end = [i for i, s in enumerate(states) if s[2] == 0 and colend(s[1])]
    return {'adj': adj, 'start': start, 'end': end, 'S': len(states), 'k': k, 'A': A}


def terms(b, N):
    """a(n) for n = 1, 2, ... rows -- index 0 is the empty array and is not listed."""
    adj, S = b['adj'], b['S']
    endset = set(b['end'])
    vec = [0] * S
    for s in b['start']:
        vec[s] += 1
    out = [0]
    for _ in range(N):
        out.append(sum(v for i, v in enumerate(vec) if v and i in endset))
        nxt = [0] * S
        for i, v in enumerate(vec):
            if not v:
                continue
            for j in adj[i]:
                nxt[j] += v
        vec = nxt
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
