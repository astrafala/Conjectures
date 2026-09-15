#!/usr/bin/env python3
"""What KINDS of conjecture does the OEIS actually contain?

Everything here so far has attacked one shape: a linear recurrence with polynomial
coefficients. That was where the tooling started, not a judgement that it is where the
opportunities are. This classifies every line beginning "Conjecture" across the whole
encyclopedia, so the next engine can be aimed at a shape rather than at another corner of
the same one.
"""
import os, re
from collections import Counter

ROOT = "/home/user/oeis/oeisdata/seq"
CONJ = re.compile(r"^\s*Conjectur", re.I)
SETTLED = re.compile(
    r"\bproof\b|prove[sndg]?\b|\bproven\b|is true|has been shown|\bshown\b|\bshows\b|"
    r"follows from|confirm\w*|verif\w*|establish\w*|settled|is correct|are correct|"
    r"follows easily|sumrecursion|Zeilberger|can be obtained", re.I)


def shape(l):
    b = re.sub(r"^\s*Conjectur\w*\s*\d*\s*[:.]?\s*", "", l, flags=re.I)
    b = re.sub(r"^(D-finite with recurrence|to be D-finite with recurrence)[:.]?\s*", "",
               b, flags=re.I)
    nb = b.replace(" ", "")
    if "a(n-" in nb and "=0" in nb:
        return "linear recurrence, = 0"
    if re.match(r"a\(n\)=", nb) and "a(n-" in nb:
        return "linear recurrence, a(n) = ..."
    if re.search(r"\bmod\b|\(mod|congruen", b, re.I):
        return "congruence"
    if re.search(r"^a\(n\)\s*=\s*A\d{6}", b) or re.search(r"=\s*A\d{6}\(", b):
        return "identity with another sequence"
    if re.match(r"a\(n\)\s*=\s*Sum_", b, re.I):
        return "closed form: a sum"
    if re.match(r"a\(n\)\s*=", b):
        return "closed form for a(n)"
    if re.search(r"G\.f\.|generating function", b, re.I):
        return "a generating function"
    if re.search(r"\bprime\b|\bprimes\b", b, re.I):
        return "about primes"
    if re.search(r"\bdivisib|divides|\bgcd\b|\bdivisor", b, re.I):
        return "divisibility"
    if re.search(r"\bperiod|eventually", b, re.I):
        return "periodicity / eventual behaviour"
    if re.search(r"~|asymptot|\blim\b|Limit", b, re.I):
        return "asymptotics or a limit"
    if re.search(r"\bonly\b|\bno\b .*\bexist|finitely many|infinitely many", b, re.I):
        return "existence / finiteness"
    if re.search(r"\bincreasing\b|\bmonotone\b|\bpositive\b|\bnonneg", b, re.I):
        return "monotonicity / sign"
    if re.search(r"\bequals\b|\bis\b .*\bequal", b, re.I):
        return "an equality, in words"
    return "other"


def main():
    cnt, opencnt, ex = Counter(), Counter(), {}
    entries = 0
    for d in sorted(os.listdir(ROOT)):
        dd = os.path.join(ROOT, d)
        if not os.path.isdir(dd):
            continue
        for fn in sorted(os.listdir(dd)):
            if not fn.endswith(".seq"):
                continue
            txt = open(os.path.join(dd, fn), errors="ignore").read()
            if "Conjectur" not in txt:
                continue
            entries += 1
            a = "A" + fn[1:7]
            for line in txt.split("\n"):
                if line[:2] not in ("%C", "%F", "%e"):
                    continue
                l = re.sub(r"^A\d{6}\s*", "", line[3:].strip())
                if not CONJ.match(l):
                    continue
                s = shape(l)
                cnt[s] += 1
                if not SETTLED.search(l):
                    opencnt[s] += 1
                    ex.setdefault(s, (a, l[:150]))
    print(f"{entries} entries mention a conjecture; "
          f"{sum(cnt.values())} conjecture lines\n")
    print(f"{'count':>7} {'open':>7}  shape")
    for s, c in cnt.most_common():
        print(f"{c:7d} {opencnt[s]:7d}  {s}")
        if s in ex:
            print(f"                  e.g. {ex[s][0]}  {ex[s][1]}")


if __name__ == "__main__":
    main()
