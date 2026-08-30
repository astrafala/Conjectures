#!/usr/bin/env python3
"""Settle the conjectured recurrences of the "G.f. f: f(z) = ..." family.

The generating function is quadratic over Q(x), so the residual-polynomial criterion
applies in the field the engine here was built for first: with theta = x d/dx, the
conjecture holds for all n past deg B exactly when B(x) = sum_i x^i (p_i(theta+i)A)(x) is a
polynomial. decide.decide_one runs that, and checks first that the g.f. reproduces every
published term.
"""
import json, re, sys
sys.path.insert(0, ".")
import sympy as sp
import fzparse, decide
from makeslots import coeffs_of
from regf import entry

MARK = re.compile(r"^\s*(Conjectur\w*|Empirical)\s*\d*\s*[:.,]?\s*"
                  r"(?:(?:to be\s+)?D-finite\s+with\s+recurrence\s*[:.,]?\s*)?", re.I)
n = sp.Symbol('n')


def attack(item):
    a = item["anum"]
    F, data, off, nm = entry(a)
    A = fzparse.parse(item["gf"], data, off)
    if A is None:
        return ("no", "the g.f. line did not parse")
    out = []
    for cl in item["conj"]:
        r = decide.decide_one(MARK.sub("", cl), data, off, False, [sp.sstr(A)])
        st = r.get("status")
        if st == "PROVED":
            try:
                ps = coeffs_of(cl)
            except Exception:
                ps = None
            if ps:
                deg = r.get("degree", -1)
                lo = max(len(ps) - 1, deg + 1)
                bad = [i + off for i in range(lo, len(data))
                       if sum(int(sp.Poly(p, n).eval(i + off)) * data[i - j]
                              for j, p in enumerate(ps) if p != 0) != 0]
                if bad:
                    out.append(("integer re-check failed", cl, bad[:3])); continue
                r["nver"] = len(data) - lo
                r["firstn"] = lo + off
        out.append((st, cl, r))
    return ("ok", out)
