#!/usr/bin/env python3
"""Settle a conjectured recurrence against another recurrence the entry states as FACT.

The strongest known side an entry can offer is not a formula but another recurrence. If
the entry asserts L(a) = 0 and conjectures C(a) = 0, the question is whether C annihilates
every solution of L that the sequence could be -- and that is decided in the Ore algebra
Q(n)[N], not guessed.

The naive test, "is C a left multiple of L", is sufficient but NOT necessary: C(a) = 0
only requires C to lie in the left ideal of the sequence's MINIMAL annihilator, and the
stated L need not be minimal. oremod.py handles this properly: divide C = QL + R, so
C(a) = R(a); R(a) lies in the r-dimensional module spanned by a(n),...,a(n+r-1), so its
shifts are linearly dependent and yield an operator T with T(R(a)) = 0; if R(a) vanishes
at enough consecutive indices and T's leading coefficient has no integer root beyond them,
then R(a) is identically zero and the conjecture holds.
"""
import json, re, sys
sys.path.insert(0, ".")
import sympy as sp
import ore, oremod
from makeslots import coeffs_of
from regf import entry
import timeoutrun

n = sp.Symbol('n')


def attack(item):
    a = item["anum"]
    F, data, off, nm = entry(a)
    out = []
    for stated, vec in item["stated"]:
        try:
            ls = coeffs_of(stated)
        except Exception:
            continue
        if not ls or len(ls) < 2:
            continue
        L = ore.to_operator(ls)
        for cl in item["conj"]:
            try:
                cs = coeffs_of(cl)
            except Exception:
                continue
            if not cs or len(cs) < 2:
                continue
            C = ore.to_operator(cs)
            Q, R = ore.right_divide(C, L)
            if ore.is_zero(R):
                verdict, how = "PROVED", "the conjecture is a left multiple of the stated recurrence"
            else:
                ok = oremod.vanishes(R, L, data, off, len(ls) - 1)
                verdict, how = ("PROVED", "the residual operator annihilates the sequence") \
                    if ok else ("not settled", "residual does not vanish")
            if verdict != "PROVED":
                out.append((verdict, cl, stated, how)); continue
            order = len(cs) - 1
            bad = [i + off for i in range(order, len(data))
                   if sum(int(sp.Poly(p, n).eval(i + off)) * data[i - j]
                          for j, p in enumerate(cs) if p != 0) != 0]
            if bad:
                out.append(("integer re-check failed", cl, stated, bad[:3])); continue
            out.append(("PROVED", cl, stated, how))
    return out


if __name__ == "__main__":
    hits = []
    for it in json.load(open("stated_rec.json")):
        st, r = timeoutrun.call(attack, (it,), timeout=240)
        if st != "ok":
            print(f"{it['anum']}  {st}: {r}", flush=True); continue
        for verdict, cl, stated, how in r or []:
            print(f"{it['anum']}  {verdict:24s} {cl[:52]}", flush=True)
            if verdict == "PROVED":
                hits.append({"anum": it["anum"], "conj": cl, "stated": stated, "how": how})
    json.dump(hits, open("stated_hits.json", "w"), indent=1)
    print(f"\n{len(hits)} proved")
