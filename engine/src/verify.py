#!/usr/bin/env python3
"""Independent verification, two genuinely different algorithms per claim.

  ALG 1: brute force the conjectured gcd-sum directly, k = 1..n.
  ALG 2: build the sequence from its multiplicative definition a(p^e), via
         factorisation only -- never touches a gcd.

Both are compared against the DATA published on the entry.
"""
import json, subprocess
from math import gcd
from sympy import factorint, primefactors, totient, mobius


def published(anum):
    out = subprocess.run(
        ["curl", "-sS", "-A", "Mozilla/5.0",
         f"https://oeis.org/search?q=id:{anum}&fmt=json"],
        capture_output=True, text=True, timeout=60).stdout
    d = json.loads(out)
    r = d[0] if isinstance(d, list) else d["results"][0]
    return [int(x) for x in r["data"].split(",")], int(r["offset"].split(",")[0])


def lam(n):                       # Liouville lambda, A008836
    return (-1) ** sum(factorint(n).values())


def a076479(n):                   # mu(rad(n))
    return mobius(1) if n == 1 else (-1) ** len(primefactors(n))


# ---------------- ALG 1: direct gcd-sums (the conjectured right-hand sides) --
def gcdsum_358272(n):
    return sum(gcd(k, n) * lam(gcd(k, n)) for k in range(1, n + 1))


def gcdsum_358319(n):
    return sum(gcd(k, n) * a076479(gcd(k, n)) for k in range(1, n + 1))


def gcdsum_384531(n):
    return sum(gcd(i, n) * gcd(i + 1, n) for i in range(1, n + 1))


# ---------------- ALG 2: multiplicative definitions (the left-hand sides) ----
def mult(local):
    def f(n):
        v = 1
        for p, e in factorint(n).items():
            v *= local(p, e)
        return v
    return f


a358272 = mult(lambda p, e: (-1) ** e * p ** (2 * (e // 2)))
a358319 = mult(lambda p, e: ((p - 2) - (p - 1) * e) * p ** (e - 1))
a384531 = mult(lambda p, e: ((2 * e + 1) * p - 2 * e) * p ** (e - 1))

CASES = [("A358272", a358272, gcdsum_358272),
         ("A358319", a358319, gcdsum_358319),
         ("A384531", a384531, gcdsum_384531)]

N = 400
for anum, mult_side, gcd_side in CASES:
    data, off = published(anum)
    print(f"=== {anum}  (offset {off}, {len(data)} published terms)")

    bad = [n for n in range(off, off + len(data)) if mult_side(n) != data[n - off]]
    print(f"  ALG 2 vs published DATA, n = {off}..{off+len(data)-1}: "
          f"{'MISMATCH ' + str(bad[:5]) if bad else 'all agree'}")

    bad = [n for n in range(off, off + len(data)) if gcd_side(n) != data[n - off]]
    print(f"  ALG 1 vs published DATA, n = {off}..{off+len(data)-1}: "
          f"{'MISMATCH ' + str(bad[:5]) if bad else 'all agree'}")

    bad = [n for n in range(1, N + 1) if mult_side(n) != gcd_side(n)]
    print(f"  ALG 1 vs ALG 2, n = 1..{N}: "
          f"{'MISMATCH ' + str(bad[:5]) if bad else 'all agree'}")
