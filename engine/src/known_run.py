#!/usr/bin/env python3
"""Sweep every open conjectural recurrence that still has a usable known side and no paper.

Re-measured after the conjlines fix, the whole corpus holds 11,897 open conjectural
recurrences. 10,418 of them state nothing as fact at all, which is the honest ceiling on
this approach. Of the rest, 230 have a closed form, generating function or sum that a
parser here accepts, and no paper -- many because the selector that chooses candidates
refused every "Empirical" line until today, so they were never offered to an engine.

Each is decided by whichever route its known side supports: decide.decide_one for a
generating function, hyperterm for a closed form, zeilb for a sum.
"""
import json, re, sys
sys.path.insert(0, ".")
import sympy as sp
import cfparse, gfclean, sumparse, fsplit, decide, hyperterm, conjlines
# coeffs_of, not parse_conj: parse_conj insists on the "... = 0" spelling and raised
# ValueError on 41 of the 230, every one of which writes the recurrence as
# "a(n) = <combination of earlier terms>".
from makeslots import coeffs_of
from regf import entry

n = sp.Symbol('n')
# the marker can be written "Conjecture:", "Conjecture D-finite with recurrence" or
# "Conjecture: D-finite with recurrence:" -- a single optional colon left a stray one
# behind on the third, and sympify then choked on a leading ":".
MARK = re.compile(r"^\s*(Conjectur\w*|Empirical)\s*\d*\s*[:.,]?\s*"
                  r"(?:(?:to be\s+)?D-finite\s+with\s+recurrence\s*[:.,]?\s*)?", re.I)
GF = re.compile(r"^\s*(o\.)?g\.f\.\s*[:=]", re.I)
EGFL = re.compile(r"^\s*e\.g\.f\.\s*[:=]", re.I)


def attack(item):
    a = item["anum"]
    F, data, off, nm = entry(a)
    parts = [p for l in item["known"] for p in [l] + fsplit.split(l)]
    gfc = [c for p in parts if GF.match(p) for c in gfclean.candidates(p)]
    egfc = [c for p in parts if EGFL.match(p) for c in gfclean.candidates(p)]
    cfs = [e for p in parts for e in [cfparse.parse(p)] if e is not None]
    out = []
    for cl in item["conj"]:
        conj = MARK.sub("", cl)
        ps = coeffs_of(cl)
        if ps is None:
            continue
        got = None
        for cands, egf in ((gfc, False), (egfc, True)):
            if not cands:
                continue
            r = decide.decide_one(conj, data, off, egf, cands)
            if r.get("status") in ("PROVED", "DISPROVED"):
                got = dict(r, route="egf" if egf else "gf")
                break
        if got is None:
            for e in cfs:
                al, sh = cfparse.align(e, data, off)
                if al is None:
                    continue
                ok, ev = hyperterm.is_zero_sum(
                    sp.expand(sum(p * al.subs(n, n - j) for j, p in enumerate(ps) if p != 0)), n)
                if ok:
                    got = {"status": "PROVED", "route": "closedform",
                           "formula": sp.srepr(al), "order": len(ps) - 1}
                    break
        if got is None:
            continue
        # start the check where the criterion actually guarantees the recurrence: for an
        # o.g.f. that is n > deg, for an e.g.f. n > deg + order (the exponential residual
        # is re-indexed forward). Starting at `order` rejected three true results whose
        # only failures sit below their own threshold.
        order = len(ps) - 1
        deg = got.get("degree", -1)
        lo = max(order, deg + 1 + (order if got.get("route") == "egf" else 0))
        bad = [i + off for i in range(lo, len(data))
               if sum(int(sp.Poly(p, n).eval(i + off)) * data[i - j]
                      for j, p in enumerate(ps) if p != 0) != 0]
        got["integer_bad"] = bad[:3]
        got["nver"] = len(data) - lo
        got["firstn"] = lo + off
        out.append((got["status"], cl, got))
    return out
