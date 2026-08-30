#!/usr/bin/env python3
"""Which of the uncovered periodicity conjectures fall under the theorem already proved?"""
import json, re
import sympy as sp
import balacheck, gfclean, timeoutrun
from balacheck import x, t
from regf import entry, EGFL
from prove_rec import parse_gf

COVERED = {'A000670', 'A002050', 'A004123', 'A006531', 'A052895', 'A064618', 'A080253',
           'A162314', 'A167137', 'A259533', 'A301921', 'A305550', 'A306082', 'A316142',
           'A316143', 'A316144', 'A320352', 'A354242', 'A354253', 'A355409'}


def check(a):
    F, data, off, name = entry(a)
    egfs = [l for l in F if EGFL.match(l)]
    if not egfs:
        return {"status": "no e.g.f. posted"}
    for l in egfs:
        for c in gfclean.candidates(l):
            try:
                E = parse_gf(c, 'x', raw=c)
            except Exception:
                continue
            got = balacheck.to_G(E)
            if got is None:
                continue
            G, cs = got
            ok, why = balacheck.integral_forever(G)
            frac = [str(v) for v in cs[:8] if not sp.nsimplify(v, rational=True).is_Integer]
            if ok:
                vals = balacheck.stirling_values(cs, min(len(data), 9))
                match = all(sp.simplify(vals[i] - data[i]) == 0
                            for i in range(min(len(vals), len(data), 9)))
                return {"status": "FITS THE THEOREM" if match else
                                  "G is integral but does not reproduce the terms",
                        "G": sp.sstr(G), "why": why, "egf": c}
            return {"status": "does not fit", "why": why, "G": sp.sstr(G),
                    "non_integer": frac[:4], "egf": c}
    return {"status": "no e.g.f. could be read"}


if __name__ == "__main__":
    w = json.load(open("periodic-phi.json"))
    todo = [u["anum"] for u in w if u["anum"] not in COVERED]
    out = {}
    for a in todo:
        st, val = timeoutrun.call(check, (a,), timeout=90)
        out[a] = val if st == "ok" else {"status": st}
        print(f"{a}: {out[a]['status']}"
              + (f"  ({out[a].get('why','')[:70]})" if out[a]['status'] == "does not fit"
                 else ""), flush=True)
    json.dump(out, open("bala-check.json", "w"), indent=1)
    fits = [a for a, v in out.items() if v["status"] == "FITS THE THEOREM"]
    print(f"\n{len(fits)} of {len(todo)} fall under the theorem: {fits}")
