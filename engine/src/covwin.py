#!/usr/bin/env python3
"""Arrays in which every window of a fixed width holds every value, and new values come in order.

    Number of length n+3+1 0..3 arrays with every value 0..3 appearing at least once in every
      consecutive 3+2 elements, and new values 0..3 introduced in order.

Two conditions and neither is a plain window test. The coverage condition IS local -- a window
of w consecutive elements must contain all of 0..k -- so the last w-1 values decide whether a
new one may be added. The introduction order is not local at all: a value may be used only if
every smaller value has appeared somewhere earlier, and "somewhere earlier" is unbounded. One
counter carries it: how many of 0..k have been introduced so far, since they arrive in order.

So the state is (the last w-1 values, the number of values introduced), and a window closing is
what the edge relation tests. The alphabet has k+1 values and the window w is k+2 or k+3, so a
closing window holds every value with one or two to spare, which is restrictive enough that the
reachable state count stays small.

The entry's length is n + k + 1 or n + k + 2, which is exactly the length at which the first
window closes: below that the coverage condition is vacuous.
"""
import re
from itertools import product

NAME = re.compile(
    r'(?i)^Number of length n\+(\d+)\+(\d+) 0\.\.(\d+) arrays with every value 0\.\.(\d+) '
    r'appearing at least once in every consecutive (\d+)\+(\d+) elements, and new values '
    r'0\.\.(\d+) introduced in order\s*\.?\s*$')


def parse_name(nm):
    nm = ' '.join(nm.split())
    m = NAME.match(nm)
    if not m:
        return None
    k1, c1, a1, a2, k2, c2, a3 = (int(m.group(i)) for i in range(1, 8))
    if not (k1 == k2 and a1 == a2 == a3 == k1 and c1 == c2 - 1):
        return None
    k, w = k1, k2 + c2
    if k < 1 or k > 8 or w < k + 2 or w > k + 4:
        return None
    return {'engine': 'covwin', 'k': k, 'w': w, 'off': k + c1, 'frac': 1}


def build(p, cap=2000000):
    k, w = p['k'], p['w']
    m = k + 1                                   # the alphabet 0..k
    states, index = [], {}

    def sid(s):
        if s not in index:
            index[s] = len(states)
            states.append(s)
        return index[s]

    s0 = sid(((), 0))
    adj = {}
    i = 0
    while i < len(states):
        tail, used = states[i]
        out = []
        for v in range(min(used + 1, m)):       # new values only in order
            nt = (tail + (v,))[-(w - 1):]
            nu = max(used, v + 1)
            # a window closes on every step once w values have been read: the window is the
            # w-1 kept values together with the one just read
            if len(tail) == w - 1:
                win = tail + (v,)
                if len(set(win)) != m:
                    continue
            out.append(sid((nt, nu)))
        adj[i] = out
        i += 1
        if len(states) > cap:
            return None
    # only arrays that have introduced every value are counted? No: the coverage condition
    # forces it as soon as one window closes, and the entry's length always closes one.
    import lumpauto
    st = [0] * len(states)
    st[s0] = 1
    wend = [1 if used == m else 0 for (_t, used) in states]
    wadj, wstart, wendv, S = lumpauto.lump(adj, st, wend)
    return {'adj': {i: r for i, r in enumerate(wadj)}, 'startv': wstart, 'endv': wendv,
            'S': S, 'raw': len(states), 'off': p['off']}


def terms(b, N):
    """out[n] counts the arrays of length n; the entry's a(1) is at length off+1."""
    adj, S = b['adj'], b['S']
    vec = list(b['startv'])
    ev = b['endv']
    out = [sum(v * e for v, e in zip(vec, ev))]
    for _ in range(N + b['off'] + 2):
        nxt = [0] * S
        for i, v in enumerate(vec):
            if not v:
                continue
            for j in adj[i]:
                nxt[j] += v
        vec = nxt
        out.append(sum(v * e for v, e in zip(vec, ev)))
    return out[b['off']:]


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
