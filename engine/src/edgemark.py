#!/usr/bin/env python3
"""How many binary arrays can mark the trailing edge maxima of a convolved random array.

    Number of binary arrays indicating the locations of trailing edge maxima of a random
      length-n 0..2 array extended with zeros and convolved with 1,4,6,4,1.

The reading, stated so it can be argued with.  The length-n array x over 0..k is embedded in
the bi-infinite all-zero sequence and convolved with the kernel K, giving

    c(i) = sum_j K[j] * x(i-j),

which is zero outside a window of length n + |K| - 1.  Position i is a TRAILING EDGE MAXIMUM
of c when c(i) > c(i+1) and the nearest earlier position with a different value is lower --
that is, i is the right-hand end of a plateau which is a strict local maximum.  A plateau of
one cell is the ordinary local maximum; the point of the word "trailing" is which end of a
longer plateau gets the mark.  The entry counts the DISTINCT indicator arrays, not the inputs.

A radius-one test on (c(i-1), c(i), c(i+1)) is NOT this condition and no such test reproduces
these entries: a plateau of c can be arbitrarily long (with K = 1,1 the plateau condition is
x(i-1) = x(i+1), so x = a,b,a,b,... is one plateau throughout), and whether its left end rose
or fell is not visible from one neighbour.  An exhaustive search over all 512 radius-one sign
predicates fails on A222021 and A222329 at every window.  What carries the unbounded lookback
is one bit of state: whether the nearest earlier DIFFERENT value was lower or higher.

So the model is an automaton whose state is the last |K| input values -- which give c at the
current position and at the one before it -- together with that bit, emitting one mark per
step with a delay of one; and, the entry counting images rather than inputs, the count is a
walk in its subset construction, the end vector recording how many distinct ways the forced
all-zero tail can finish from each state.
"""
import re
from itertools import product

NAME = re.compile(
    r'(?i)^Number of binary arrays indicating the locations of trailing edge maxima of a '
    r'random length-n (-?\d+)\.\.(-?\d+) array extended with zeros and convolved with '
    r'([-\d,\s]+?)\s*\.?\s*$')


def parse_name(nm):
    nm = ' '.join(nm.split())
    m = NAME.match(nm)
    if not m:
        return None
    lo, hi = int(m.group(1)), int(m.group(2))
    ker = tuple(int(t) for t in m.group(3).split(',') if t.strip())
    if lo != 0 or hi < 1 or hi > 9 or not 2 <= len(ker) <= 6:
        return None
    return {'engine': 'edgemark', 'k': hi, 'ker': ker, 'frac': 1}


def _conv(K, win):
    """c at the position whose window of the last len(K) inputs is `win` (oldest first)."""
    L = len(K)
    return sum(K[j] * win[L - 1 - j] for j in range(L))


def build(p, cap=300000):
    K, k = p['ker'], p['k']
    L = len(K)
    V = list(range(k + 1))

    # ---- the input automaton, tabulated once: a state is (window of the last L values, bit).
    # `bit` is True when the nearest earlier position with a value different from the current
    # one was LOWER (the all-zero left tail counts as lower, since nothing different precedes).
    # Recomputing the step and the tail inside the subset loop, once per member per subset, was
    # the whole cost of this engine: 0..4 with a width-5 kernel took a minute for a model of
    # 1,216 states.
    wins = list(product(V, repeat=L))
    widx = {w: i for i, w in enumerate(wins)}
    cval = [_conv(K, w) for w in wins]
    NS = len(wins) * 2                                  # state id = 2 * window index + bit
    trans = [[0] * len(V) for _ in range(NS)]
    emit = [[0] * len(V) for _ in range(NS)]
    for wi, w in enumerate(wins):
        cur = cval[wi]
        for v in V:
            ni = widx[w[1:] + (v,)]
            nxt = cval[ni]
            for bit in (0, 1):
                trans[2 * wi + bit][v] = 2 * ni + (bit if nxt == cur else int(nxt > cur))
                emit[2 * wi + bit][v] = 1 if (cur > nxt and bit) else 0
    start = 2 * widx[(0,) * L] + 1

    # ---- the forced tail: L+1 zeros flush every position that can still carry a mark
    TAIL = L + 1
    tailword = [0] * NS
    for q in range(NS):
        w, word = q, 0
        for _ in range(TAIL):
            word = (word << 1) | emit[w][0]
            w = trans[w][0]
        tailword[q] = word

    # ---- subset construction on the emitted marks
    states, index = [], {}

    def sid(S):
        if S not in index:
            index[S] = len(states)
            states.append(S)
        return index[S]

    s0 = sid(frozenset([start]))
    adj, end = {}, {}
    i = 0
    while i < len(states):
        S = states[i]
        b0, b1 = set(), set()
        for st in S:
            tr, em = trans[st], emit[st]
            for v in V:
                (b1 if em[v] else b0).add(tr[v])
        adj[i] = [sid(frozenset(T)) for T in (b0, b1) if T]
        end[i] = len({tailword[st] for st in S})
        i += 1
        if len(states) > cap:
            return None

    import lumpauto
    stv = [0] * len(states)
    stv[s0] = 1
    ev = [end[j] for j in range(len(states))]
    wadj, wstart, wend, S = lumpauto.lump(adj, stv, ev)
    return {'adj': {j: r for j, r in enumerate(wadj)}, 'startv': wstart, 'endv': wend,
            'S': S, 'raw': len(states)}


def terms(b, N):
    """out[n] = the number of distinct indicator arrays for a length-n input; offset 1."""
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
