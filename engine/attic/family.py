#!/usr/bin/env python3
"""Classify the entries carrying the phi(k) periodicity conjecture.

If A(x) = G(e^x - 1) with G(y) = sum_k c_k y^k then, substituting x = log(1+y),

    c_k = (1/k!) * sum_n s(k,n) a(n),      s = signed Stirling numbers, 1st kind.

So G is integral exactly when k! divides sum_n s(k,n) a(n) for every k. That is an
exact test on the published DATA.

For entries that pass, we then extend the sequence mod m ourselves using
a(n) = sum_k c_k k! S(n,k) (integer arithmetic) and measure the eventual period.
"""
import json, subprocess
from math import factorial
from sympy import totient
from sympy.functions.combinatorial.numbers import stirling

ENTRIES = """A000670 A002050 A004123 A080253 A064618 A167137 A301921 A305550
A306082 A316142 A316143 A316144 A320352 A354242 A354253 A355409 A259533 A006531
A162314 A052895 A258899 A258903 A276371 A365777 A365782 A365794 A370092
A000436 A000657 A002105 A012780 A126156 A143138 A143139""".split()

_s1 = {}
def s1(k, n):
    if (k, n) not in _s1:
        _s1[(k, n)] = (-1) ** (k - n) * int(stirling(k, n, kind=1, signed=False))
    return _s1[(k, n)]


def entry(anum):
    out = subprocess.run(
        ["curl", "-sS", "-A", "Mozilla/5.0",
         f"https://oeis.org/search?q=id:{anum}&fmt=json"],
        capture_output=True, text=True, timeout=90).stdout
    r = json.loads(out)[0]
    return ([int(x) for x in r["data"].split(",")],
            int(r["offset"].split(",")[0]), r["name"])


def coeffs(a):
    """Recover c_k; return (list_or_None, first_failing_k)."""
    c = []
    for k in range(len(a)):
        t = sum(s1(k, n) * a[n] for n in range(k + 1))
        if t % factorial(k):
            return None, k
        c.append(t // factorial(k))
    return c, None


def stirling_mod(c, N, m):
    K = len(c)
    prev = [0] * (K + 1); prev[0] = 1
    out = []
    for n in range(N + 1):
        if n:
            cur = [0] * (K + 1)
            for k in range(K + 1):
                cur[k] = ((prev[k - 1] if k else 0) + k * prev[k]) % m
            prev = cur
        out.append(sum(c[k] * factorial(k) * prev[k] for k in range(K)) % m)
    return out


def period(seq, m, tail):
    s = [x % m for x in seq]; n = len(s); start = n - tail
    for p in range(1, tail // 2 + 1):
        if all(s[i] == s[i + p] for i in range(start, n - p)):
            return p
    return None


ok_list, bad_list = [], []
for anum in ENTRIES:
    try:
        a, off, name = entry(anum)
    except Exception as e:
        print(f"{anum}  FETCH FAILED"); continue
    if off != 0:
        a = a[:]                      # offset only shifts indexing; note it
    c, badk = coeffs(a)
    if c is None:
        bad_list.append(anum)
        print(f"{anum}  NOT integral G (first failure k={badk:2d})   {name[:46]}")
        continue
    res = []
    for m in (5, 7, 8, 9, 11, 12, 13, 16, 25, 27):
        seq = stirling_mod(c, 400, m)
        p = period(seq, m, tail=160)
        res.append(p is not None and int(totient(m)) % p == 0)
    verdict = "conjecture HOLDS" if all(res) else "CONJECTURE FAILS"
    ok_list.append(anum)
    print(f"{anum}  integral G, offset {off}, c_0..c_5={c[:6]}  {verdict}   {name[:40]}")

print(f"\nintegral-G entries: {len(ok_list)}")
print(" ".join(ok_list))
print(f"not in the family: {len(bad_list)}")
print(" ".join(bad_list))
