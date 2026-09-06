#!/usr/bin/env python3
"""Bala's periodicity conjecture: a(n) mod m eventually periodic, period | phi(m).

ALG 1: generate a(n) from the e.g.f. G(exp(x)-1) by power-series arithmetic
       over the rationals, then reduce mod m.
ALG 2: generate a(n) mod m from the Stirling form a(n) = Sum_k c_k k! S(n,k),
       using an integer recurrence for S(n,k) -- no series, no rationals.
Then measure the actual eventual period and compare with phi(m).
"""
from fractions import Fraction
from sympy import totient, divisors


def egf_coeffs(c, N):
    """a(n) for n<=N from e.g.f. G(e^x-1), G(y)=sum c[k] y^k, exact rationals."""
    # (e^x - 1)^k as a series in x, coefficient list of x^n
    N1 = N + 1
    # E[n] = coefficient of x^n in (e^x - 1)
    E = [Fraction(0)] + [Fraction(1, fact(n)) for n in range(1, N1)]
    total = [Fraction(0)] * N1
    power = [Fraction(0)] * N1
    power[0] = Fraction(1)                      # (e^x-1)^0 = 1
    for k in range(len(c)):
        if c[k]:
            for n in range(N1):
                total[n] += c[k] * power[n]
        # power *= (e^x - 1)
        new = [Fraction(0)] * N1
        for i in range(N1):
            if power[i]:
                for j in range(1, N1 - i):
                    new[i + j] += power[i] * E[j]
        power = new
    return [total[n] * fact(n) for n in range(N1)]


_f = [1]
def fact(n):
    while len(_f) <= n:
        _f.append(_f[-1] * len(_f))
    return _f[n]


def stirling_mod(c, N, m):
    """a(n) mod m via a(n) = Sum_k c_k k! S(n,k), integer arithmetic only."""
    K = len(c)
    # S[k] as a rolling row: S(n,k)
    S = [[0] * (K + 1) for _ in range(N + 1)]
    S[0][0] = 1
    for n in range(1, N + 1):
        for k in range(0, K + 1):
            up = S[n - 1][k - 1] if k >= 1 else 0
            S[n][k] = (up + k * S[n - 1][k]) % m
    out = []
    for n in range(N + 1):
        v = 0
        for k in range(K):
            if c[k]:
                v = (v + c[k] * fact(k) * S[n][k]) % m
        out.append(v % m)
    return out


def eventual_period(seq, tail):
    """Smallest p such that seq[i]==seq[i+p] for all i >= len(seq)-tail-p."""
    n = len(seq)
    start = n - tail
    for p in range(1, tail // 2 + 1):
        if all(seq[i] == seq[i + p] for i in range(start, n - p)):
            return p
    return None


CASES = {
    "A000670 (Fubini, G=1/(1-y))":      [1] * 40,
    "A004123 (G=1/(1-2y))":             [2 ** k for k in range(40)],
    "G=1/(1-3y)":                       [3 ** k for k in range(40)],
    "G=(1+y)^3 (polynomial)":           [1, 3, 3, 1] + [0] * 36,
    "G=exp-like c_k=k":                 list(range(40)),
    "G=1/(1-y-y^2) (Fibonacci c_k)":    None,
}
fib = [1, 1]
while len(fib) < 40:
    fib.append(fib[-1] + fib[-2])
CASES["G=1/(1-y-y^2) (Fibonacci c_k)"] = fib

N = 260
print(f"{'case':34s} {'m':>4s} {'phi(m)':>6s} {'period':>7s}  {'divides?':>8s}  algs")
for label, c in CASES.items():
    exact = egf_coeffs(c, 40)
    for m in (5, 7, 8, 9, 12, 16, 25, 27, 30, 11, 13, 32, 36):
        seq = stirling_mod(c, N, m)
        # cross-check ALG1 vs ALG2 on the range where exact values were formed
        agree = all(int(exact[n]) % m == seq[n] for n in range(41))
        p = eventual_period(seq, tail=120)
        ph = int(totient(m))
        ok = (p is not None and ph % p == 0)
        print(f"{label:34s} {m:4d} {ph:6d} {str(p):>7s}  {str(ok):>8s}  "
              f"{'ALG1==ALG2' if agree else 'ALG MISMATCH'}")
