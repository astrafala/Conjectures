#!/usr/bin/env python3
"""Arrays with x(i) confined to i..i+k and no value used too often.

    Number of length n arrays x(i), i=1..n with x(i) in i..i+3 and no value appearing more
      than 2 times.

Eight entries, none read. The value x(i) = i + d with d in 0..k, so the value v can be taken
only by the indices v-k..v: at any moment just k+1 values are in play, and how often each has
been used so far is all the condition asks. The state is those k+1 counters, each capped at the
allowed multiplicity, and the walk slides one value out and one in at each step -- a value that
leaves has had its final count, and no count is ever required, only bounded.
"""
import re
from itertools import product

NAME = re.compile(
    r'^\s*Number of length n arrays x\(i\), i=1\.\.n with x\(i\) in i\.\.i\+(\d+) and no value '
    r'appearing more than (\d+) times\s*\.?\s*$', re.I)


def parse_name(nm):
    m = NAME.match(' '.join(nm.split()))
    if not m:
        return None
    k, mult = int(m.group(1)), int(m.group(2))
    if not 1 <= k <= 9 or not 1 <= mult <= 4 or (mult + 1) ** (k + 1) > 400000:
        return None
    return {'engine': 'shiftmult', 'k': k, 'mult': mult, 'frac': 1}


def build(p, cap=200000):
    k, mult = p['k'], p['mult']
    W = k + 1
    states, index = [], {}

    def sid(s):
        if s not in index:
            index[s] = len(states)
            states.append(s)
        return index[s]

    s0 = sid((0,) * W)
    adj = {}
    i = 0
    while i < len(states):
        cnt = states[i]
        out = []
        for d in range(W):
            if cnt[d] + 1 > mult:
                continue
            c = list(cnt)
            c[d] += 1
            out.append(sid(tuple(c[1:]) + (0,)))
            if len(states) > cap:
                return None
        adj[i] = out
        i += 1
    return {'adj': adj, 'start': [s0], 'end': list(range(len(states))), 'S': len(states)}


def terms(b, N):
    adj, S = b['adj'], b['S']
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
        out.append(sum(vec))
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
