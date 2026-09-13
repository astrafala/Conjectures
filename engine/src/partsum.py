#!/usr/bin/env python3
"""Arrays whose every leading partial sum is divisible by one of a fixed set of numbers.

    Number of length n 1..(4+1) arrays with every leading partial sum divisible by 2, 3 or 5.

The partial sums are unbounded and the condition is not: divisibility by any of d_1,...,d_r is
decided by the sum modulo M = lcm(d_1,...,d_r). So the state is that residue, the digraph has
exactly M vertices, and an array is a walk from residue 0 -- the empty prefix -- through
residues that are each divisible by at least one of the d_i. Nothing about the values matters
beyond their residues, so the alphabet 1..K contributes K edges out of every vertex, of which
only the admissible ones survive.

The bound is M, read off the divisors and not estimated.
"""
import re
from math import gcd

NAME = re.compile(
    r'(?i)^Number of length n 1\.\.\((\d+)\+1\) arrays with every leading partial sum '
    r'divisible by ([\d, ]+?(?:\s+or\s+\d+)?)\s*\.?\s*$')


def _divs(t):
    out = []
    for piece in re.split(r',|\bor\b', t):
        piece = piece.strip()
        if piece:
            if not piece.isdigit():
                return None
            out.append(int(piece))
    return sorted(set(out)) or None


def parse_name(nm):
    nm = ' '.join(nm.split())
    m = NAME.match(nm)
    if not m:
        return None
    K = int(m.group(1)) + 1
    ds = _divs(m.group(2))
    if ds is None or K < 1 or K > 40 or any(d < 2 or d > 60 for d in ds):
        return None
    M = 1
    for d in ds:
        M = M * d // gcd(M, d)
    if M > 5000:
        return None
    return {'engine': 'partsum', 'K': K, 'divs': tuple(ds), 'M': M, 'frac': 1}


def build(p, cap=20000):
    M, K, ds = p['M'], p['K'], p['divs']
    if M > cap:
        return None
    good = [r for r in range(M) if any(r % d == 0 for d in ds)]
    adj = {r: [] for r in range(M)}
    for r in range(M):
        for v in range(1, K + 1):
            s = (r + v) % M
            if any(s % d == 0 for d in ds):
                adj[r].append(s)
    import lumpauto
    st = [0] * M
    st[0] = 1
    wadj, wstart, wend, S = lumpauto.lump(adj, st, [1] * M)
    return {'adj': {i: r for i, r in enumerate(wadj)}, 'startv': wstart, 'endv': wend,
            'S': S, 'raw': M, 'good': len(good)}


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
