#!/usr/bin/env python3
"""Permutations of 1..n whose displacements lie in a prescribed SET.

    Number of permutations of 1..n with displacements restricted to {-5,-4,-2,0,1,3}.

23 entries, none read: `permdisp' counts permutations whose displacement lies in an INTERVAL
-d..d, and reads a different name; here the allowed set has holes in it, which the same walk
handles without changing anything but which values a step may choose.

Build the permutation left to right. At position i the value placed is i + delta for some delta
in D, so only the values in the window [i - L, i + R] are ever in play, with L = -min D and
R = max D. Carry a bitmask of which of those W = L + R + 1 values are already used and slide the
window one place at each step. The value i - L can never be reached again once position i is
passed, so it must be used by then -- that is the whole constraint on the slide.

The boundaries fall out of the same picture. Before position 1 the window's values below 1 do
not exist, so their bits start set; after n positions the window is [n+1-L, n+1+R], every value
at most n is used and every value above n does not exist, so the accepting mask is the one the
walk started from. A permutation is therefore exactly a closed walk of length n, and the count
is det(I - xM)-rational with S the number of states.
"""
import re

NAME = re.compile(
    r'^\s*Number of permutations of 1\.\.n with displacements restricted to '
    r'\{([-\d, ]+)\}\s*\.?\s*$', re.I)


def parse_name(nm):
    m = NAME.match(' '.join(nm.split()))
    if not m:
        return None
    try:
        D = sorted({int(v) for v in m.group(1).split(',') if v.strip()})
    except ValueError:
        return None
    if not D or max(D) - min(D) > 16:
        return None
    return {'engine': 'permset', 'D': tuple(D), 'frac': 1}


def build(p, cap=200000):
    D = p['D']
    L, R = -min(D), max(D)
    W = L + R + 1
    if L < 0 or W > 18 or (1 << W) > 8 * cap:
        return None
    startmask = (1 << L) - 1 if L > 0 else 0
    full = (1 << W) - 1
    states, index = [], {}

    def sid(s):
        if s not in index:
            index[s] = len(states)
            states.append(s)
        return index[s]

    s0 = sid(startmask)
    adj = {}
    i = 0
    while i < len(states):
        mask = states[i]
        out = []
        for delta in D:
            j = delta + L
            if mask >> j & 1:
                continue
            nm_ = mask | (1 << j)
            if not nm_ & 1:
                continue                       # the value leaving the window is still unused
            out.append(sid((nm_ >> 1) & full))
            if len(states) > cap:
                return None
        adj[i] = out
        i += 1
    return {'adj': adj, 'start': s0, 'end': s0, 'S': len(states), 'D': D}


def terms(b, N):
    """a(n) = permutations of 1..n, for n = 0, 1, 2, ... -- closed walks of length n."""
    adj, S = b['adj'], b['S']
    vec = [0] * S
    vec[b['start']] = 1
    out = [vec[b['end']]]
    for _ in range(N):
        nxt = [0] * S
        for i, v in enumerate(vec):
            if not v:
                continue
            for j in adj[i]:
                nxt[j] += v
        vec = nxt
        out.append(vec[b['end']])
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
