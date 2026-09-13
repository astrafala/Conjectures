#!/usr/bin/env python3
"""Arrays whose second differences never vanish.

    Half the number of 0..2 arrays of length n+2 with second differences nonzero.

The second difference at i is x_i - 2x_{i+1} + x_{i+2}, a window of three, so the condition is
the edge relation on the pairs (x_i, x_{i+1}) and the digraph has (k+1)^2 vertices.

The name's divisor is 2, and it is the reflection x -> k - x. That map sends every second
difference to its negative, so it preserves the counted set; it is an involution; and it has no
fixed point there, since a fixed array would need x_i = k - x_i at every place, hence be
constant, hence have second difference zero. So the count is even and half of it is the number
of reflection ORBITS, which is the entry's sequence.
"""
import re
from itertools import product

NAME = re.compile(
    r'(?i)^Half the number of 0\.\.(\d+) arrays of length n\+2 with second differences '
    r'nonzero\s*\.?\s*$')


def parse_name(nm):
    nm = ' '.join(nm.split())
    m = NAME.match(nm)
    if not m:
        return None
    k = int(m.group(1))
    if k < 1 or k > 12:
        return None
    return {'engine': 'seconddiff', 'k': k, 'div': 2, 'frac': 1}


def build(p, cap=400000):
    k = p['k']
    V = range(k + 1)
    pairs = [(a, b) for a in V for b in V]
    if len(pairs) > cap:
        return None
    idx = {q: i for i, q in enumerate(pairs)}
    adj = {}
    for i, (a, b) in enumerate(pairs):
        adj[i] = [idx[(b, c)] for c in V if a - 2 * b + c != 0]
    import lumpauto
    st = [1] * len(pairs)
    wadj, wstart, wend, S = lumpauto.lump(adj, st, [1] * len(pairs))
    return {'adj': {i: r for i, r in enumerate(wadj)}, 'startv': wstart, 'endv': wend,
            'S': S, 'raw': len(pairs), 'div': 2}


def terms(b, N):
    """out[n] is half the number of arrays of length n+2, for n >= 1.

    The walk starts at length 2, where there is no second difference at all and every array
    qualifies -- and where the reflection DOES have a fixed point when k is even, the constant
    array k/2, so the count is odd and no half of it exists. That index is not the entry's:
    its a(1) is the length-3 count. So the walk is stepped once before anything is emitted.
    """
    adj, S, div = b['adj'], b['S'], b['div']
    vec = list(b['startv'])
    ev = b['endv']
    out = []
    for _ in range(N + 2):
        nxt = [0] * S
        for i, v in enumerate(vec):
            if not v:
                continue
            for j in adj[i]:
                nxt[j] += v
        vec = nxt
        t = sum(v * e for v, e in zip(vec, ev))
        out.append(t // div if t % div == 0 else None)
    return out


def threshold(b, coeffs, order):
    S = b['S']
    t = terms(b, 2 * S + order + 30)
    if any(x is None for x in t):
        return None
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
