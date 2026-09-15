#!/usr/bin/env python3
"""Exact power series for the secant/tangent family, and the modulo-k periodicity test.

Everything is exact rational arithmetic in Q[[x]] -- no floating point, no truncation
that could hide a term. Each sequence is checked against the entry's published DATA
before any conclusion is drawn from it.
"""
from fractions import Fraction as Fr

N = 220


def zero(): return [Fr(0)] * N
def one():
    c = zero(); c[0] = Fr(1); return c


def add(a, b): return [a[i] + b[i] for i in range(N)]
def sub(a, b): return [a[i] - b[i] for i in range(N)]
def smul(s, a): return [Fr(s) * a[i] for i in range(N)]


def mul(a, b):
    r = zero()
    for i in range(N):
        if a[i]:
            ai = a[i]
            for j in range(N - i):
                if b[j]:
                    r[i + j] += ai * b[j]
    return r


def inv(a):
    assert a[0] != 0
    r = zero(); r[0] = 1 / a[0]
    for n in range(1, N):
        r[n] = -sum(a[k] * r[n - k] for k in range(1, n + 1)) / a[0]
    return r


def cos_(c=1):
    """cos(c*x)"""
    r = zero(); term = Fr(1)
    for m in range(0, N, 2):
        r[m] = term
        term = term * Fr(-1) * Fr(c) ** 2 / ((m + 1) * (m + 2))
    return r


def sin_(c=1):
    r = zero(); term = Fr(c)
    for m in range(1, N, 2):
        r[m] = term
        term = term * Fr(-1) * Fr(c) ** 2 / ((m + 1) * (m + 2))
    return r


def integrate(a):
    r = zero()
    for n in range(N - 1):
        r[n + 1] = a[n] / (n + 1)
    return r


def deriv(a):
    r = zero()
    for n in range(1, N):
        r[n - 1] = a[n] * n
    return r


def log1p(a):
    """log(a) for a with a[0] == 1"""
    assert a[0] == 1
    return integrate(mul(deriv(a), inv(a)))


def sqrt_(a):
    assert a[0] == 1
    r = zero(); r[0] = Fr(1)
    for n in range(1, N):
        s = sum(r[k] * r[n - k] for k in range(1, n))
        r[n] = (a[n] - s) / 2
    return r


def compose(f, g):
    assert g[0] == 0
    r = zero(); p = one()
    for j in range(N):
        if f[j]:
            r = add(r, smul(f[j], p))
        p = mul(p, g)
        if all(x == 0 for x in p):
            break
    return r


def arcsin_():
    """arcsin(x) as a series in x"""
    # d/dx arcsin = (1-x^2)^(-1/2)
    q = zero(); q[0] = Fr(1); q[2] = Fr(-1)
    return integrate(inv(sqrt_(q)))


def terms(series, parity, offset_pow):
    """a(n) = (offset_pow + parity*n)! * [x^(offset_pow + parity*n)] series"""
    out = []
    f = [Fr(1)]
    for i in range(1, N + 1):
        f.append(f[-1] * i)
    n = 0
    while offset_pow + parity * n < N:
        p = offset_pow + parity * n
        v = series[p] * f[p]
        out.append(v)
        n += 1
    return out
