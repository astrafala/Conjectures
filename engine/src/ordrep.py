#!/usr/bin/env python3
"""Arrays of FIXED length over 0..n constrained through their REPEATED VALUES.

    Number of length-5 0..n arrays with no repeated value differing from the previous repeated
      value by one or less.
    Number of length-7 0..n arrays with no repeated value differing from the previous repeated
      value by other than plus two or minus 1.

A *repeated value* is a term equal to the one before it, and its value is that term. `repval`
reads the MIRROR family -- `length-n 0..K arrays', growing length over a fixed alphabet, where
the count is a walk on at most (K+1)(K+2) states. Here the length is fixed and the ALPHABET
grows, so no walk counts it, and 43 entries of this shape carry a conjectured recurrence that
nothing had ever read. `ordpoly' reads the shape but only the conditions decided by ORDER
alone, and these are not: they name an actual difference.

**Counting.** The state after a prefix is the last term and the previous repeated value, and
the step is uniform in a way that costs O(n^2) rather than O(n^3): writing A[p][v] for the
number of prefixes ending in v whose previous repeated value is p, appending t gives
A'[p][t] += (sum_v A[p][v]) - A[p][t] when t differs from the last term, and
A'[t][t] += A[p][t] when it equals it and the condition allows.

**Why it is a polynomial, and from where.** Let k be the point past which the predicate stops
caring: f(v, r) depends on v - r only through its sign and its magnitude up to k, and is
constant for v - r > k and for v - r < -k. That k is read off the predicate, not assumed.
An array is determined by its weak ordering -- the ordered set partition of the L positions
into m blocks of equal value, listed in increasing value -- together with the base value
g_0 >= 0 and the gaps g_1, ..., g_{m-1} >= 1 between consecutive distinct values, subject to
g_0 + sum g_i <= n. Every constraint the condition imposes is on a difference of two values,
which is a signed sum of consecutive gaps; since f is constant past k, each constraint splits
into finitely many cases, each of which fixes that gap-sum to one of at most 2k+1 values or
pushes it beyond k. Within a case the count is the number of integer points of a system of the
form (fixed amounts) + (free gaps) <= n, a polynomial in n of degree at most L, valid as soon
as n exceeds the total forced amount. That total is at most (m-1) + (number of constrained
pairs)(k+1) <= L + L(k+1), so

    a(n) is a polynomial in n of degree at most L for every n >= n_0 = L + L(k+1),

the annihilator is (z-1)^(L+1) shifted by z^(n_0+1), and S = n_0 + L + 2.

Conditions taken modulo n+1 are refused: the modulus then moves with the parameter, the
differences are no longer bounded, and the argument above does not reach them.
"""
import re

import repval

NAME = re.compile(
    r'^\s*Number of length[- ]\(?(\d+(?:\s*\+\s*\d+)?)\)?\s+0\.\.n\s+arrays?\s+with\s+'
    r'(.*?)\s*\.?\s*$', re.I)
PROBE = 14


def _threshold(f):
    """the k past which the predicate stops caring, or None if it never does."""
    g = [f(PROBE + d, PROBE) for d in range(-PROBE, PROBE + 1)]
    hi, lo = g[-1], g[0]
    k = 0
    for i, d in enumerate(range(-PROBE, PROBE + 1)):
        if g[i] != (hi if d > 0 else lo if d < 0 else g[i]):
            k = max(k, abs(d))
    for d in range(k + 1, PROBE + 1):
        if f(PROBE + d, PROBE) != hi or f(PROBE - d, PROBE) != lo:
            return None
    return k


def parse_name(nm):
    m = NAME.match(' '.join(nm.split()))
    if not m:
        return None
    L = sum(int(x) for x in m.group(1).split('+'))
    if not 2 <= L <= 12:
        return None
    body = ' '.join(m.group(2).lower().split())
    if 'mod' in body:
        return None                     # the modulus moves with n; the bound does not reach it
    f = repval._cond(body, 0) or repval._diffcond(body, 0)
    if f is None:
        return None
    try:
        k = _threshold(f)
    except Exception:
        return None
    if k is None or k > 6:
        return None
    return {'engine': 'ordrep', 'L': L, 'f': f, 'k': k, 'frac': 1}


def count(L, f, n):
    """arrays of length L over 0..n whose repeated values satisfy f against the previous."""
    V = n + 1
    A = [[0] * V for _ in range(V + 1)]        # A[0] is `no previous repeated value yet'
    for v in range(V):
        A[0][v] = 1
    for _ in range(L - 1):
        B = [[0] * V for _ in range(V + 1)]
        for p in range(V + 1):
            row = A[p]
            s = sum(row)
            if not s:
                continue
            Bp = B[p]
            for t in range(V):
                c = row[t]
                if s != c:
                    Bp[t] += s - c
                if c and (p == 0 or f(t, p - 1)):
                    B[t + 1][t] += c
        A = B
    return sum(sum(r) for r in A)


def build(p, cap=200000):
    L, f, k = p['L'], p['f'], p['k']
    n0 = L + L * (k + 1)
    S = n0 + L + 2
    if S > 200:
        return None
    vals = [count(L, f, n) for n in range(S + 8)]
    # the derived bound, tested on terms it did not supply: (z-1)^(L+1) after the transient
    A = [1]
    for _ in range(L + 1):
        A = [a - b for a, b in zip(A + [0], [0] + A)]
    d = len(A) - 1
    for m in range(n0 + d, len(vals)):
        if sum(A[j] * vals[m - d + j] for j in range(d + 1)) != 0:
            return None
    return {'L': L, 'k': k, 'n0': n0, 'S': S, 'vals': vals, 'f': f}


def terms(b, N):
    v = list(b['vals'])
    while len(v) <= N:
        v.append(count(b['L'], b['f'], len(v)))
    return v[:N + 1]


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
