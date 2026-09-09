#!/usr/bin/env python3
"""Permutations of 0..n-1 in which no element moves far, under a condition on nearby values.

    Number of length n arrays of permutations of 0..n-1 with each element moved by -3 to 3
      places and every three consecutive elements having its maximum within 5 of its minimum.

35 entries of this shape carry a conjectured recurrence and nothing read any of them.

Build the permutation left to right. At position i the value placed must lie in [i-d, i+d], so
only the 2d+1 values in that window are ever in play, and the value i-d can never be reached
again once position i is passed -- so it must already be used. Carry a bitmask of which of the
window's values are taken and slide the window one place at each step, and that is the whole
model: a walk on masks.

The boundaries fall out of the same picture. Before position 0 the window is [-d, d] and its
negative half does not exist, so those bits start set; after n positions the window is
[n-d, n+d], every value below n is used and every value at or above n does not exist, so the
accepting mask is the one the walk started from. A permutation of 0..n-1 is therefore exactly a
closed walk of length n, and the count is det(I - xM)-rational with S the number of states.

The extra condition compares consecutive VALUES, and the value at position i is i - d + j for
the chosen bit j, so a difference of consecutive values is 1 + j' - j: the condition is decided
by the last few chosen bits, which the state carries.
"""
import re

NAME = re.compile(
    r'^\s*Number of length n arrays of permutations of 0\.\.n-1 with each element moved by '
    r'-(\d+) to (\d+) places and (.*?)\s*\.?\s*$', re.I)
WORD = {'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7}


def _cond(body):
    """(how many consecutive values it looks at, predicate on that many values)."""
    b = ' '.join(body.lower().split())
    m = re.match(r'every (\w+) consecutive elements having its maximum within (\d+) of its '
                 r'minimum$', b)
    if m:
        k, lim = WORD.get(m.group(1)), int(m.group(2))
        if not k:
            return None
        return k, (lambda v: max(v) - min(v) <= lim)
    if b == 'with no two consecutive increases':
        return 3, (lambda v: not (v[0] < v[1] < v[2]))
    if b == 'with no two consecutive decreases':
        return 3, (lambda v: not (v[0] > v[1] > v[2]))
    if b == 'with no two consecutive increases or two consecutive decreases':
        return 3, (lambda v: not (v[0] < v[1] < v[2]) and not (v[0] > v[1] > v[2]))
    if b == 'the median of every three consecutive elements nondecreasing':
        return 4, (lambda v: sorted(v[0:3])[1] <= sorted(v[1:4])[1])
    return None


def parse_name(nm):
    m = NAME.match(' '.join(nm.split()))
    if not m:
        return None
    d1, d2 = int(m.group(1)), int(m.group(2))
    if d1 != d2 or not 1 <= d1 <= 8:
        return None
    got = _cond(m.group(3))
    if not got:
        return None
    k, pred = got
    return {'engine': 'permdisp', 'd': d1, 'k': k, 'pred': pred}


def build(p, cap=200000):
    d, k, pred = p['d'], p['k'], p['pred']
    W = 2 * d + 1
    startmask = (1 << d) - 1
    start = (startmask, ())
    states, index, adj = [], {}, []

    def sid(s):
        i = index.get(s)
        if i is None:
            i = index[s] = len(states)
            states.append(s)
            adj.append(None)
        return i

    sid(start)
    i = 0
    while i < len(states):
        mask, hist = states[i]
        row = []
        for j in range(W):
            if mask >> j & 1:
                continue
            nh = hist + (j,)
            if len(nh) >= k:
                nh = nh[-k:]
                # consecutive values from consecutive chosen bits: v(t+1) - v(t) = 1 + j' - j
                vals = [0]
                for a, b in zip(nh, nh[1:]):
                    vals.append(vals[-1] + 1 + b - a)
                if not pred(tuple(vals)):
                    continue
                nh = nh[1:]
            m2 = mask | (1 << j)
            if not m2 & 1:
                continue                      # the value leaving the window was never used
            row.append(sid((m2 >> 1, nh)))
        adj[i] = row
        i += 1
        if len(states) > cap:
            return None
    # acceptance is a property of the MASK, not of the whole state: after n placements the
    # history component is whatever the last few choices were, and every state carrying the
    # starting mask is a completed permutation of 0..n-1
    acc = [i for i, (m, _) in enumerate(states) if m == startmask]
    # States with the same future contribute identically to the count, so merging them
    # changes nothing. It matters here: the residual scan runs 2S steps and S reaches 31,000
    # on the widest of these, which is hopeless on the unmerged walk and immediate on the
    # merged one. The bound S stays the unmerged count, which is the Cayley-Hamilton figure
    # a paper is entitled to quote.
    import lumpauto
    st = [1 if i == index[start] else 0 for i in range(len(states))]
    en = [1 if i in set(acc) else 0 for i in range(len(states))]
    try:
        adj2, st2, en2, n2 = lumpauto.lump(adj, st, en)
    except Exception:
        adj2, st2, en2, n2 = adj, st, en, len(states)
    return {'adj': adj2, 'startv': st2, 'endv': en2, 'S': len(states), 'Slump': n2}


def terms(b, N):
    """the number of such permutations of 0..n-1, for n = 0, 1, 2, ..."""
    n = b['Slump']
    v = list(b['startv'])
    en = b['endv']
    out = [sum(c * en[i] for i, c in enumerate(v))]
    for _ in range(N + 2):
        w = [0] * n
        for i, c in enumerate(v):
            if c:
                for j in b['adj'][i]:
                    w[j] += c
        v = w
        out.append(sum(c * en[i] for i, c in enumerate(v)))
    return out


def threshold(b, coeffs, order):
    S = b['S']
    t = terms(b, 2 * S + order + 20)
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
