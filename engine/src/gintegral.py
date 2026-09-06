#!/usr/bin/env python3
"""Recover G from an entry's published terms and decide whether G has integer coefficients.

If a(n) = n![x^n] G(exp(x)-1) then a(n) = Sum_j c_j j! S(n,j). Since S(n,n)=1 and the
Stirling matrix is unit lower triangular, the c_j are determined one at a time by the
published terms:  c_n n! = a(n) - Sum_{j<n} c_j j! S(n,j).  This needs no parsing of the
entry's e.g.f. -- it reads the coefficients straight off the data -- and the answer is
exact rational arithmetic, so "integer" means integer.
"""
from fractions import Fraction
import entry


def stirling_rows(N):
    rows = [[1]]
    for n in range(1, N):
        prev = rows[-1] + [0]
        rows.append([(j * prev[j] + (prev[j - 1] if j else 0)) for j in range(n + 1)])
    return rows


def coeffs(anum, nmax=22):
    e = entry.get(anum)
    d = [int(x) for x in e['data'].split(',')]
    off = int(e['offset'].split(',')[0])
    N = min(nmax, len(d))
    S = stirling_rows(N)
    fact = [1] * (N + 1)
    for j in range(1, N + 1):
        fact[j] = fact[j - 1] * j
    best = None
    for shift in (0, 1, 2, 3):           # the entry may not start at n=0
        a = d[:N]
        c = []
        ok = True
        for n in range(N - shift):
            m = n + shift
            if m >= len(S):
                break
            tot = Fraction(a[n]) - sum(c[j] * fact[j] * S[m][j] for j in range(min(len(c), m + 1)))
            c.append(tot / fact[m])
        if len(c) < 8:
            continue
        integral = all(x.denominator == 1 for x in c)
        cand = (shift, integral, [str(x) for x in c[:10]], len(c))
        if best is None or (integral and not best[1]):
            best = cand
        if integral:
            break
    return best


CANDIDATES = ["A000670", "A002050", "A004123", "A006531", "A052895", "A064618",
              "A080253", "A162314", "A167137", "A179929", "A259533", "A301921",
              "A305550", "A306082", "A316142", "A316143", "A316144", "A320352",
              "A354242", "A354253", "A355409", "A370092"]

if __name__ == "__main__":
    for a in CANDIDATES:
        try:
            r = coeffs(a)
        except Exception as ex:
            print(f"{a}  ERROR {ex}")
            continue
        if r is None:
            print(f"{a}  too few terms")
            continue
        shift, integral, first, n = r
        print(f"{a}  shift={shift}  G INTEGER: {integral}  ({n} coeffs)  c = {first}")
