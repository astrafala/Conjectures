#!/usr/bin/env python3
"""Eventual periodicity mod k, for a sequence with a constant-coefficient recurrence.

Eighty open entries conjecture that a(n) mod k is eventually periodic for every k, and
forty-two of them are Peter Bala's. Where the entry states a recurrence

    a(n) = c_1 a(n-1) + ... + c_r a(n-r)      (c_i integers)

the conjecture is a theorem with a two-line proof, and one that gives explicit bounds.

Fix k. The state vector v(n) = (a(n), a(n-1), ..., a(n-r+1)) mod k satisfies v(n+1) = M
v(n) for the companion matrix M of the recurrence, over the finite ring Z/k. There are at
most k^r states, so among v(0), ..., v(k^r) two coincide, say v(s) = v(t) with s < t; from
then on v is periodic with period dividing t - s, and the pre-period is at most s. So a(n)
mod k is eventually periodic, with pre-period and period bounded by k^r.

When det(M) = (-1)^(r-1) c_r is invertible mod k the map is a bijection of the state space,
so the orbit is PURELY periodic -- there is no pre-period at all. That is the stronger form
several of these entries actually conjecture.

Both the true pre-period and the true minimal period are computed here by running the
orbit, so the paper states the exact values rather than the bound.
"""
import sympy as sp


def orbit(coeffs, init, k):
    """(pre-period, period) of a(n) mod k, exactly, by running the state map."""
    r = len(coeffs)
    st = tuple(int(v) % k for v in init[:r])
    seen = {st: 0}
    n = 0
    while True:
        nxt = tuple([sum(coeffs[i] * st[i] for i in range(r)) % k] + list(st[:r - 1]))
        n += 1
        if nxt in seen:
            return seen[nxt], n - seen[nxt]
        seen[nxt] = n
        st = nxt


def purely_periodic(coeffs, k):
    """True when the state map is invertible mod k, so there is no pre-period."""
    return sp.gcd(int(coeffs[-1]), k) == 1


def table(coeffs, init, ks):
    return {k: orbit(coeffs, init, k) for k in ks}
