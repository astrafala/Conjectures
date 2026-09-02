#!/usr/bin/env python3
"""Proper colourings of a grid that is CIRCULAR in one direction, up to relabelling.

Name shapes:
    Number of 0..m colorings of an n X W array circular in the W direction
        with new values 0..m introduced in row major order
    Number of 0..m colorings of a R X (n+c) array circular in the n+c direction
        with new values 0..m introduced in row major order

A ``colouring'' here is proper: horizontally and vertically adjacent cells differ. The check
is the entry's own first term -- one row of $W$ cells joined into a cycle has
$(i-1)^W+(-1)^W(i-1)$ proper colourings over $i$ colours, which at $W=6$, $i=3$ is $66$, and
$66/3!=11$ is what the corresponding entry publishes.

The relabelling clause is handled as in `transfer20`: what is counted is equality patterns,
`L_i = sum_j N_j i(i-1)...(i-j+1)` is triangular with unit diagonal, and the entry's count is
the fixed rational combination `a = (1^T F^{-1}) L` of the colouring counts `L_i` over
alphabets of size `i = 1..K`. Proper colouring is stated through equality alone, so the
condition is invariant under permuting the colours and the reduction is legitimate.

The two directions of circularity are genuinely different.

  * Circular ACROSS the walk (`n X W`, wrapped in the $W$ direction): a row is a proper
    colouring of the cycle $C_W$, two consecutive rows differ in every position, and
    `L_i(n)` is an ordinary walk count.

  * Circular ALONG the walk (`R X (n+c)`, wrapped in the growing direction): a column is a
    proper colouring of the path $P_R$, and `L_i(m) = tr(T^m)` for $m=n+c$ columns. A trace
    is not `iota^T M^m tau` for fixed vectors, and running one walk per starting state is
    too expensive. It is not needed: $T$ commutes with the simultaneous permutation of the
    colours, so the diagonal entry `(T^m)_{ss}` depends only on the equality pattern of $s$,
    and
        `tr(T^m) = sum_pattern  i(i-1)...(i-j+1) * (T^m)_{s s}`
    over one representative $s$ per pattern, $j$ being the number of colours the pattern
    uses. That is a few walks, not $S$ of them, and each is a walk with a fixed start and a
    fixed end, so the ordinary machinery applies to the disjoint union.
"""
import re
from fractions import Fraction

import namecanon
import transfer19 as T19
from transfer20 import falling_weights, strip_relabel

NAME_A = re.compile(
    r'Number of 0\.\.(\d+)\s+colorings?\s+(?:on|of|in)\s+an?\s+'
    r'n\s*X\s*(\d+)\s+array\s+circular in the\s+(\d+)\s+direction\s*\.?\s*$', re.I)
NAME_B = re.compile(
    r'Number of 0\.\.(\d+)\s+colorings?\s+(?:on|of|in)\s+an?\s+'
    r'(\d+)\s*X\s*\(\s*n\s*\+\s*(\d+)\s*\)\s+array\s+circular in the\s+n\s*\+\s*(\d+)\s+'
    r'direction\s*\.?\s*$', re.I)


def parse_name(nm):
    nm = namecanon.canon(nm)
    plain, hit = strip_relabel(nm)
    if not hit:
        return None
    norm = re.sub(r'(?<=[\dn)])\s*[xX]\s*(?=[\dn(])', ' X ', plain)
    norm = re.sub(r'\s+', ' ', norm).strip()
    m = NAME_A.search(norm)
    if m:
        alpha, W, wd = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if W != wd or W < 2:
            return None
        return {'mode': 'A', 'W': W, 'K': alpha + 1, 'frac': 1}
    m = NAME_B.search(norm)
    if m:
        alpha, R, c, cd = (int(m.group(i)) for i in (1, 2, 3, 4))
        if c != cd or R < 1:
            return None
        return {'mode': 'B', 'R': R, 'c': c, 'K': alpha + 1, 'frac': 1}
    return None


def _cycle_states(W, i):
    out = []

    def rec(t):
        if len(t) == W:
            if W > 1 and t[0] != t[-1]:
                out.append(tuple(t))
            return
        for v in range(i):
            if t and v == t[-1]:
                continue
            t.append(v); rec(t); t.pop()
    rec([])
    return out


def _path_states(R, i):
    out = []

    def rec(t):
        if len(t) == R:
            out.append(tuple(t)); return
        for v in range(i):
            if t and v == t[-1]:
                continue
            t.append(v); rec(t); t.pop()
    rec([])
    return out


def _pattern(s):
    m, out = {}, []
    for v in s:
        if v not in m:
            m[v] = len(m)
        out.append(m[v])
    return tuple(out)


def _falling(i, j):
    v = 1
    for t in range(j):
        v *= (i - t)
    return v


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def _canon(t, fixed):
    """canonical form of a colouring under the permutations fixing `fixed` pointwise"""
    m, out = {}, []
    for v in t:
        if v in fixed:
            out.append(('f', v))
        else:
            if v not in m:
                m[v] = len(m)
            out.append(('n', m[v]))
    return tuple(out)


def _lump(states, fixed, i, adjacent):
    """orbits of `states` under the permutations fixing `fixed`, and the lumped adjacency.

    The transfer matrix commutes with any permutation of the colours, so a vector constant
    on orbits stays constant on orbits: the walk may be run on the orbits instead of on the
    colourings, which is what makes the wider alphabets affordable at all.
    """
    rep = {}
    for t in states:
        rep.setdefault(_canon(t, fixed), t)
    keys = list(rep)
    idx = {k: n for n, k in enumerate(keys)}
    size = {k: 0 for k in keys}
    for t in states:
        size[_canon(t, fixed)] += 1
    adj = []
    for k in keys:
        t = rep[k]
        cnt = {}
        for u in states:
            if adjacent(t, u):
                o = idx[_canon(u, fixed)]
                cnt[o] = cnt.get(o, 0) + 1
        adj.append(sorted(cnt.items()))
    return keys, idx, size, adj, rep


def build(p, cap=40000):
    K = p['K']
    c = falling_weights(K)
    den = 1
    for x in c:
        den = den * x.denominator // _gcd(den, x.denominator)
    w = [int(x * den) for x in c]
    adj, start, end = [], [], []
    base = 0

    def differ(a, b):
        return all(x != y for x, y in zip(a, b))

    for i in range(1, K + 1):
        if p['mode'] == 'A':
            st = _cycle_states(p['W'], i)
            if not st:
                continue
            keys, idx, size, row, _ = _lump(st, frozenset(), i, differ)
            if base + len(keys) > cap:
                return None
            adj.extend([[(k + base, m) for k, m in r] for r in row])
            start.extend([w[i - 1] * size[k] for k in keys])
            end.extend([1] * len(keys))
            base += len(keys)
        else:
            st = _path_states(p['R'], i)
            if not st:
                continue
            anchors = {}
            for s in st:
                anchors.setdefault(_pattern(s), s)
            for pat, s in anchors.items():
                j = len(set(pat))
                fixed = frozenset(s)
                keys, idx, size, row, _ = _lump(st, fixed, i, differ)
                if base + len(keys) > cap:
                    return None
                adj.extend([[(k + base, m) for k, m in r] for r in row])
                here = idx[_canon(s, fixed)]
                sv = [0] * len(keys)
                sv[here] = w[i - 1] * _falling(i, j)
                start.extend(sv)
                ev = [0] * len(keys)
                ev[here] = 1
                end.extend(ev)
                base += len(keys)
    if base == 0:
        return None
    return adj, start, end, base, den


def matvec(adj, v):
    return [sum(m * v[k] for k, m in row) for row in adj]


def terms(adj, start, end, N):
    v = end[:]
    out = []
    for _ in range(N + 1):
        out.append(sum(start[i] * v[i] for i in range(len(v))))
        v = matvec(adj, v)
    return out


def threshold(adj, start, end, coeffs, order, S):
    """last index at which the conjectured recurrence fails, or None if it never settles"""
    v = end[:]
    powers = [v]
    for _ in range(order):
        v = matvec(adj, v)
        powers.append(v)
    w = powers[order][:]
    for i, c in coeffs.items():
        pw = powers[order - i]
        for j in range(len(w)):
            w[j] -= c * pw[j]
    us, zeros, j = [], 0, 0
    while zeros < S + 1 and j <= 3 * S + order + 8:
        u = sum(start[t] * w[t] for t in range(len(w)))
        us.append(u)
        zeros = zeros + 1 if u == 0 else 0
        if not any(w):
            zeros = S + 1
            break
        w = matvec(adj, w)
        j += 1
    if zeros < S + 1:
        return None
    last = max((i for i, u in enumerate(us) if u != 0), default=-1)
    return order + last
