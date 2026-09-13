#!/usr/bin/env python3
"""Arrays in which each element is no smaller than a sum of earlier ones, taken modulo M.

    Number of 0..5 arrays x(0..n-1) of n elements with each no smaller than the sum of its two
      previous neighbors modulo 6.
    Number of 0..5 arrays x(0..n-1) of n elements with each no smaller than the sum of its
      previous elements modulo 6.

The comparison is against a sum, and sums are unbounded; the modulo is what makes the state
finite. For the "k previous neighbors" form the sum runs over a window, so the state is the last
k values -- their sum modulo M is what the condition reads, but the window has to be carried in
full because the oldest value leaves it. For the "previous elements" form the sum runs over
everything read so far, and then the running total modulo M IS the state, one vertex per
residue.

At the start there are fewer previous elements than the window asks for, and the entry's own
terms say which convention it uses: the sum is over those that exist, so x(0) is unconstrained
and a(1) is the whole alphabet. Both forms reproduce every published term under that reading.
"""
import re
from itertools import product

WORD = {'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6}

WIN = re.compile(
    r'(?i)^Number of (-?\d+)\.\.(-?\d+) arrays x\(0\.\.n-1\) of n elements with each no '
    r'smaller than the sum of its (two|three|four|five|six) previous neighbors modulo '
    r'(\d+)\s*\.?\s*$')
ALL = re.compile(
    r'(?i)^Number of (-?\d+)\.\.(-?\d+) arrays x\(0\.\.n-1\) of n elements with each no '
    r'smaller than the sum of its previous elements modulo (\d+)\s*\.?\s*$')


def parse_name(nm):
    nm = ' '.join(nm.split())
    m = WIN.match(nm)
    if m:
        lo, hi, k, M = int(m.group(1)), int(m.group(2)), WORD[m.group(3).lower()], int(m.group(4))
        if lo != 0 or hi < 1 or M < 2 or (hi + 1) ** k > 400000:
            return None
        return {'engine': 'modprev', 'A': hi, 'k': k, 'M': M, 'kind': 'window', 'frac': 1}
    m = ALL.match(nm)
    if m:
        lo, hi, M = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if lo != 0 or hi < 1 or M < 2 or M > 20000:
            return None
        return {'engine': 'modprev', 'A': hi, 'k': None, 'M': M, 'kind': 'all', 'frac': 1}
    return None


def build(p, cap=400000):
    A, M, kind = p['A'], p['M'], p['kind']
    V = range(A + 1)
    if kind == 'all':
        # state: the running total modulo M; the empty prefix sums to 0
        if M > cap:
            return None
        adj = {r: [] for r in range(M)}
        for r in range(M):
            for v in V:
                if v >= r:
                    adj[r].append((r + v) % M)
        start, states = 0, M
    else:
        k = p['k']
        # state: the last min(k, read so far) values, shorter while the array is starting
        wins = []
        index = {}

        def sid(w):
            if w not in index:
                index[w] = len(wins)
                wins.append(w)
            return index[w]

        start = sid(())
        adj = {}
        i = 0
        while i < len(wins):
            w = wins[i]
            out = []
            s = sum(w) % M
            for v in V:
                if v >= s:
                    nw = (w + (v,))[-k:]
                    out.append(sid(nw))
            adj[i] = out
            i += 1
            if len(wins) > cap:
                return None
        states = len(wins)
    import lumpauto
    st = [0] * states
    st[start] = 1
    wadj, wstart, wend, S = lumpauto.lump(adj, st, [1] * states)
    return {'adj': {i: r for i, r in enumerate(wadj)}, 'startv': wstart, 'endv': wend,
            'S': S, 'raw': states}


def terms(b, N):
    """out[n] counts the length-n arrays; out[0] = 1 is the empty array."""
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
