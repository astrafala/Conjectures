#!/usr/bin/env python3
"""Conjectures that are POLYNOMIAL identities in the shifts of one sequence.

Every engine written so far is linear: it asks whether sum_i p_i(n) a(n-i) vanishes. A
different and untouched shape appears throughout the corpus,

    a(n)*a(n+3) - a(n+1)*a(n+2) + (-1)^n = 0,

nonlinear in a. These are decidable, and by an argument that needs nothing about the
particular sequence. If a satisfies a recurrence of order r, then a(n+r) is a Q(n)-linear
combination of a(n),...,a(n+r-1), so every monomial of degree <= d in the shifts of a
reduces to a Q(n)-combination of the C(r+d,d) monomials in a(n),...,a(n+r-1). Those span a
module M of finite dimension D, and the shift operator maps M to itself. The expression E
of the conjecture lies in M, so E, sigma E, ..., sigma^D E are D+1 vectors in a
D-dimensional space and admit a linear dependence over Q(n): an annihilator L of E of
order m <= D. If E vanishes at m consecutive indices from n0 on and the leading
coefficient of L has no integer root >= n0, then E vanishes identically.

This file only measures how many such conjectures exist. The engine is separate.
"""
import os, re
from collections import Counter

ROOT = "/home/user/oeis/oeisdata/seq"
MARK = re.compile(r"^\s*(Conjectur\w*|Empirical)\s*\d*\s*[:,]?\s*", re.I)
ATTRIB = re.compile(r"-\s*_[^_]+_,?\s*[A-Z][a-z]{2}\s+\d")
# a product of two or more a(...) factors: what makes it nonlinear
NONLIN = re.compile(r"a\([^()]*\)\s*\*\s*a\(")
# and it must be an equation in a alone, with no other sequence and no prose
CLEAN = re.compile(r"^[-+*/^() \t0-9a-z,.=<>]*$")
BAD = re.compile(r"\b(Sum|Product|sqrt|log|exp|floor|ceiling|mod|prime|A\d{6})\b", re.I)

cnt, hits = Counter(), []
for d in sorted(os.listdir(ROOT)):
    dd = os.path.join(ROOT, d)
    if not os.path.isdir(dd):
        continue
    for fn in sorted(os.listdir(dd)):
        if not fn.endswith(".seq"):
            continue
        a = "A" + fn[1:7]
        for line in open(os.path.join(dd, fn), errors="ignore"):
            line = line.rstrip("\n")
            if len(line) < 4 or line[0] != "%" or line[1] not in "FC":
                continue
            body = re.sub(r"^%.\s+A\d{6}\s*", "", line)
            if not MARK.match(body):
                continue
            s = ATTRIB.split(MARK.sub("", body))[0].strip().rstrip(".")
            s = re.sub(r"\(Start\)|\(End\)", "", s).strip()
            if "=" not in s or not NONLIN.search(s):
                continue
            cnt["nonlinear in a"] += 1
            if BAD.search(s):
                cnt["  ...but names another function or entry"] += 1
                continue
            if not CLEAN.match(s.replace("n", "n")):
                cnt["  ...but carries prose"] += 1
                continue
            cnt["POLYNOMIAL IDENTITY"] += 1
            hits.append((a, s))

for k, v in cnt.most_common():
    print(f"{v:6d}  {k}")
print()
for a, s in hits[:60]:
    print(f"  {a}  {s[:120]}")
print(f"\n{len(hits)} candidates")
