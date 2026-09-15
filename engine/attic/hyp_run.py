#!/usr/bin/env python3
"""Settle a conjectural recurrence whose known side is a hypergeometric VALUE.

Fifty-nine entries state their fact side as a(n) = pFq([...],[...],z). Every parser here
refused those lines: "hypergeom" is not a function cfparse knows, and the line is not a
Sum_ that sumparse can read, so they were recorded as "no usable known side".

But pFq IS a sum, hypconv.py writes it out as one, and its summand is a proper
hypergeometric term in (n,k) whenever the parameters are linear in n. That is exactly the
input creative telescoping wants, so the class becomes reachable by machinery already
built and already validated -- Zeilberger's algorithm with the boundary correction of
zeilb.py, then right division of the conjecture by the derived operator.
"""
import json, sys
sys.path.insert(0, ".")
import sympy as sp
import zeil, zeilb, ore, hypconv, conjlines
from zeil import n, k
from prove_rec import parse_conj
from zeil_run import numeric_ok
from regf import entry
import timeoutrun
import re

MARK = re.compile(r"^\s*(Conjectur\w*|Empirical)\s*\d*\s*[:.,]?\s*(D-finite with recurrence\s*)?", re.I)
SETTLED = re.compile(r"\bproof\b|prove[sndg]?\b|is true|confirm\w*|verif\w*|"
                     r"follows from|establish\w*|is correct", re.I)


def attack(item):
    a, line = item
    F_, data, off, nm = entry(a)
    if any(SETTLED.search(l) for l in F_):
        return ("no", "the entry says the conjecture is settled")
    p = hypconv.parse(line)
    if p is None:
        return ("no", "the hypergeometric value did not parse")
    F, lo, hi, pre = p
    # the summand must reproduce the entry's own terms before anything is derived from it
    for i in range(min(6, len(data))):
        v = sp.simplify(sp.Sum(F, (k, lo, hi)).subs(n, off + i).doit())
        if sp.simplify(v - data[i]) != 0:
            return ("no", f"the sum does not reproduce a({off+i})")
    tel = None
    for r in range(1, 4):
        tel = zeil.telescoper(F, r)
        if tel is not None:
            break
    if tel is None:
        return ("no", "no telescoper up to order 3")
    sig, R = tel
    h = zeilb.inhomogeneity(F, sig, R, lo, hi)
    if h is None:
        return ("no", "boundary correction not computable")
    if zeilb.check_numeric(F, lo, hi, sig, h, data, off) is not True:
        return ("no", "the inhomogeneous recurrence fails on the published terms")
    L, how = zeilb.annihilator(sig, h)
    if L is None:
        return ("no", how)
    out = []
    for cl in [l for l in F_ if conjlines.is_recurrence(l)]:
        pc = parse_conj(MARK.sub("", cl))
        if pc is None:
            continue
        Q, Rem = ore.right_divide(ore.to_operator(pc), L)
        if not ore.is_zero(Rem):
            out.append(("not a left multiple", cl, None))
            continue
        bad, checked, firstn = numeric_ok(pc, data, off)
        if bad or checked < 3:
            out.append(("fails on published terms", cl, bad[:3]))
            continue
        out.append(("PROVED", cl, {"formula": line, "how": how,
                                   "summand": sp.sstr(F), "hi": sp.sstr(hi),
                                   "order_conj": len(pc) - 1, "order_derived": len(L) - 1,
                                   "terms_verified": checked, "first_n": firstn}))
    return ("ok", out)


if __name__ == "__main__":
    cands = json.load(open("hyp_good.json"))
    print(f"{len(cands)} hypergeometric fact lines with a rational shift quotient", flush=True)
    hits = []
    for it in cands:
        st, r = timeoutrun.call(attack, (tuple(it),), timeout=600)
        if st != "ok":
            print(f"{it[0]}  {st}: {r}", flush=True); continue
        if r[0] != "ok":
            print(f"{it[0]}  skip: {r[1]}", flush=True); continue
        for verdict, cl, extra in r[1]:
            print(f"{it[0]}  {verdict}  {cl[:60]}", flush=True)
            if verdict == "PROVED":
                hits.append({"anum": it[0], "conj": cl, **extra})
    json.dump(hits, open("hyp_hits.json", "w"), indent=1)
    print(f"\n{len(hits)} proved")
