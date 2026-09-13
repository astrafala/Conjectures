#!/usr/bin/env python3
"""Arrays in which every position lies in a short zero-sum block, and arrays whose values are
introduced in order.

    Number of arrays of -3..3 integers x(1..n) with every x(i) in a subsequence of length 1, 2
      or 3 with sum zero.
    Number of arrays of n 0..14 integers with new values introduced in order 0..14 but
      otherwise unconstrained.

Both are walks, and neither is local on its own.

*Every x(i) in a zero-sum block of length at most W.* An obligation on position i can be met by
a block that has not been read yet, so the state carries the last W-1 values together with which
of those positions are still uncovered; a position may only leave the window once covered. With
W = 3 over -3..3 that is 49 windows and four flags.

*New values introduced in order.* The array is determined by which of the values already used
each term repeats, or that it is the next unused one, so the state is just HOW MANY distinct
values have been used: a walk on at most the alphabet's size, with m + 1 edges out of state m --
m repeats and one new value. The count is the sum of Stirling numbers of the second kind up to
that many blocks, and its generating function is rational of that degree.
"""
import re
from itertools import product

NAME = re.compile(
    r'^\s*Number of arrays of (-?\d+)\.\.(-?\d+) integers x\(1\.\.n\) with every x\(i\) in a '
    r'subsequence of length ([\d, or]+) with sum zero\s*\.?\s*$', re.I)
ORDER = re.compile(
    r'^\s*Number of arrays of n (-?\d+)\.\.(-?\d+) integers with new values introduced in '
    r'order (-?\d+)\.\.(-?\d+) but otherwise unconstrained\s*\.?\s*$', re.I)


def parse_name(nm):
    nm = ' '.join(nm.split())
    m = ORDER.match(nm)
    if m:
        lo, hi = int(m.group(1)), int(m.group(2))
        if (int(m.group(3)), int(m.group(4))) != (lo, hi) or hi - lo > 60:
            return None
        return {'engine': 'coverzero', 'kind': 'order', 'm': hi - lo + 1, 'frac': 1}
    m = NAME.match(nm)
    if not m:
        return None
    lo, hi = int(m.group(1)), int(m.group(2))
    if lo != -hi or not 1 <= hi <= 5:
        return None
    L = sorted({int(v) for v in re.findall(r'\d+', m.group(3))})
    if not L or max(L) > 5 or min(L) < 1:
        return None
    return {'engine': 'coverzero', 'kind': 'cover', 'A': hi, 'L': tuple(L), 'frac': 1}


def build(p, cap=200000):
    if p['kind'] == 'order':
        m = p['m']
        adj = {i: [i] * i + [i + 1] if i < m else [i] * i for i in range(m + 1)}
        return {'adj': adj, 'start': [0], 'end': list(range(m + 1)), 'S': m + 1,
                'kind': 'order'}
    A, L = p['A'], p['L']
    W = max(L)
    V = list(range(-A, A + 1))
    states, index = [], {}

    def sid(s):
        if s not in index:
            index[s] = len(states)
            states.append(s)
        return index[s]

    def cover(win, flags):
        """mark every position a zero-sum block ending at the newest position covers."""
        f = list(flags)
        n = len(win)
        for ell in L:
            if ell > n:
                continue
            if sum(win[n - ell:]) == 0:
                for q in range(n - ell, n):
                    f[q] = 1
        return tuple(f)

    # the state is the last W-1 values and their coverage flags; the first W-1 positions are
    # built up one at a time, so the walk starts from a short prefix
    start = []
    for pref in product(V, repeat=W - 1):
        f = (0,) * (W - 1)
        for t in range(1, W):
            f = cover(pref[:t], f[:t]) + f[t:]
        start.append(sid((pref, f)))
    adj = {}
    i = 0
    while i < len(states):
        pref, f = states[i]
        out = []
        for v in V:
            win = pref + (v,)
            nf = cover(win, f + (0,))
            if not nf[0]:
                continue                      # the position leaving the window is uncovered
            out.append(sid((win[1:], nf[1:])))
            if len(states) > cap:
                return None
        adj[i] = out
        i += 1
    end = [i for i, (pref, f) in enumerate(states) if all(f)]
    return {'adj': adj, 'start': start, 'end': end, 'S': len(states), 'kind': 'cover',
            'W': W, 'A': A, 'L': L}


def _small(b, n):
    """arrays shorter than the window, counted directly."""
    from itertools import product
    A, L = b['A'], b['L']
    V = range(-A, A + 1)
    tot = 0
    for x in product(V, repeat=n):
        if all(any(j <= i < j + ell and sum(x[j:j + ell]) == 0
                   for ell in L for j in range(max(0, i - ell + 1), min(i + 1, n - ell + 1)))
               for i in range(n)):
            tot += 1
    return tot


def terms(b, N):
    adj, S = b['adj'], b['S']
    es = set(b['end'])
    vec = [0] * S
    for s in b['start']:
        vec[s] += 1
    if b['kind'] == 'order':
        out = [0]
        for _ in range(N):
            nxt = [0] * S
            for i, v in enumerate(vec):
                if not v:
                    continue
                for j in adj[i]:
                    nxt[j] += v
            vec = nxt
            out.append(sum(vec))
        return out
    W = b['W']
    # the walk starts once the window is full, so the first W-1 terms are counted directly --
    # taking them as zero made a(1) come out 0 where the entry says 1
    out = [1] + [_small(b, n) for n in range(1, W - 1)]
    out.append(sum(v for i, v in enumerate(vec) if i in es))
    for _ in range(N):
        nxt = [0] * S
        for i, v in enumerate(vec):
            if not v:
                continue
            for j in adj[i]:
                nxt[j] += v
        vec = nxt
        out.append(sum(v for i, v in enumerate(vec) if i in es))
    return out[:N + 1]


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
