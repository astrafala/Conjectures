#!/usr/bin/env python3
"""Exact power-series arithmetic over Q (Fractions) with composition and iteration."""
from fractions import Fraction as Fr


def trim(a, K):
    a = list(a[:K + 1])
    return a + [Fr(0)] * (K + 1 - len(a))


def mul(a, b, K):
    r = [Fr(0)] * (K + 1)
    for i in range(K + 1):
        if a[i]:
            ai = a[i]
            for j in range(K + 1 - i):
                if b[j]:
                    r[i + j] += ai * b[j]
    return r


def comp(f, g, K):
    """f(g(x)); requires g[0] == 0."""
    assert g[0] == 0
    r = [Fr(0)] * (K + 1)
    p = [Fr(0)] * (K + 1); p[0] = Fr(1)
    for j in range(K + 1):
        if f[j]:
            for i in range(K + 1):
                r[i] += f[j] * p[i]
        p = mul(p, g, K)
        if not any(p):
            break
    return r


def iterate(f, k, K):
    """k-th compositional iterate of f (f^1 = f)."""
    r = f
    for _ in range(k - 1):
        r = comp(f, r, K)
    return r
