#!/usr/bin/env python3
"""Settle a conjectural recurrence whose KNOWN side is a coefficient extraction.

diagonal.py was written for entries whose DEFINITION is a(n) = [x^n] f g^n. But the same
form also turns up as an ordinary formula line -- stated as fact -- on entries whose
recurrence is only conjectured, and no sweep ever routed those lines to it: the known-side
detector tried cfparse, cfparse cannot read a coefficient extraction, and the line was
recorded as "no usable known side".

Here the extraction gives the generating function A(t) = f(x(t))/(1 - t g'(x(t))) by
Lagrange inversion, its minimal polynomial follows by a resultant, and the conjecture is
decided in that algebraic field by the residual-polynomial criterion: the residual is a
polynomial exactly when the recurrence holds for all large n.
"""
import json, re, sys
sys.path.insert(0, ".")
import sympy as sp
import diagonal as dg, algfield as af, blocks, conjlines
from diagonal import t, y
from prove_rec import parse_conj
from regf import entry
import timeoutrun

X, n = sp.symbols('x n')
MARK = re.compile(r"^\s*(Conjectur\w*|Empirical)\s*\d*\s*[:.,]?\s*(D-finite with recurrence\s*)?", re.I)
# this sweep originally had no settlement filter at all, and reported A114121 as a new
# result when the entry itself says "Conjecture verified ... - Robert Israel, Jul 27 2020".
SETTLED = re.compile(r"\bproof\b|prove[sndg]?\b|is true|confirm\w*|verif\w*|"
                     r"follows from|establish\w*|is correct", re.I)


def attack(item):
    a, defn = item
    F, data, off, name = entry(a)
    fg = dg.parse_extraction(defn)
    if fg is None:
        return ("no", "definition did not reparse")
    f, g = fg
    N = min(len(data) - 1, 10)
    ser = dg.series(f, g, off + N + 3)
    if ser is None:
        return ("no", "no series")
    if not all(sp.simplify(ser[off + i] - data[i]) == 0 for i in range(N + 1)):
        return ("no", "the extraction does not reproduce the entry's terms")
    P = dg.minimal_polynomial(f, g)
    if P is None:
        return ("no", "no minimal polynomial")
    fac = dg.pick_factor(P, ser, off + N + 3)
    if fac is None:
        return ("no", "no branch")
    minp = sp.expand(fac.subs(t, X))
    fld = af.Field(minp)
    if any(SETTLED.search(l) for l in F):
        return ("no", "the entry itself says the conjecture is settled")
    out = []
    for cl in [l for l in F if conjlines.is_recurrence(l)]:
        ps = parse_conj(MARK.sub("", cl))
        if ps is None:
            continue
        ok, B = fld.is_polynomial(fld.residual(sp.Poly(y, y), ps, n))
        if not ok:
            out.append(("fails", cl, None))
            continue
        deg = int(sp.Poly(B, X).total_degree()) if B != 0 else -1
        order = len(ps) - 1
        lo = max(order, deg + 1)
        bad = [i + off for i in range(lo, len(data))
               if sum(int(sp.Poly(p, n).eval(i + off)) * data[i - j]
                      for j, p in enumerate(ps) if p != 0) != 0]
        if bad or len(data) - lo < 3:
            out.append(("integer re-check failed", cl, bad[:3]))
            continue
        out.append(("PROVED", cl, {"minpoly": sp.srepr(minp), "B": sp.srepr(B),
                                   "deg": deg, "order": order, "defn": defn}))
    return ("ok", out)


if __name__ == "__main__":
    cands = json.load(open("extr_cands.json"))
    hits = []
    for a, defn in cands:
        st, r = timeoutrun.call(attack, ((a, defn),), timeout=300)
        if st != "ok":
            print(f"{a}  {st}: {r}", flush=True); continue
        tag, val = r
        if tag != "ok":
            print(f"{a}  SKIP {val}", flush=True); continue
        for verdict, cl, extra in val:
            print(f"{a}  {verdict}  {cl[:70]}", flush=True)
            if verdict == "PROVED":
                hits.append({"anum": a, "conj": cl, **extra})
    json.dump(hits, open("extr_hits.json", "w"), indent=1)
    print(f"\n{len(hits)} proved")
