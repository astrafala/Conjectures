#!/usr/bin/env python3
"""Test conjectured CLOSED FORMS and GENERATING FUNCTIONS against the entry's own terms.

The b-file work exposed something simpler that needs no downloads. Every disproof check in
this project has looked at conjectured RECURRENCES. A conjectured closed form or generating
function was only ever used as an input to be proved, never tested for being wrong -- and
the DATA field alone is enough to refuse one, since a closed form that misses a published
term is false on the spot.

The same two guards as the b-file sweep apply, and both were learned there: a conjecture
qualified "for n > k" is not tested below k, and the failure must persist into the upper
half of the tested range rather than sit at the boundary.
"""
import json, os, re, sys
sys.path.insert(0, ".")
import sympy as sp
import bsweep, openness
from regf import entry

OUT = "datacheck_results.json"


def one(anum):
    try:
        F, data, off, nm = entry(anum)
    except Exception:
        return {"status": "no entry"}
    if len(data) < 12:
        return {"status": "too few terms"}
    bad = bsweep.check_closed(F, data, off) + bsweep.check_gf(F, data, off)
    return {"status": "DISPROVED" if bad else "holds on the published terms",
            "ndata": len(data), "bad": bad}


def report(anum, res):
    st, val = res
    if st != "ok" or not isinstance(val, dict):
        return
    if val.get("status") == "DISPROVED":
        b = val["bad"][0]
        print(f"  DISPROVED {anum}  n={b[1]}..{b[2]} ({b[3]} failures of {b[4]} terms)",
              flush=True)
        print(f"      {b[0][:100]}", flush=True)


if __name__ == "__main__":
    import runpool
    items = json.load(open("datacheck_queue.json"))
    done = runpool.run(one, items, lambda a: a, OUT, per_item=60,
                       budget=int(sys.argv[1]) if len(sys.argv) > 1 else 480,
                       workers=4, report=report)
    from collections import Counter
    c = Counter(v[1].get("status") if isinstance(v[1], dict) else str(v[0])
                for v in done.values())
    for k, v in c.most_common():
        print(f"  {v:6d}  {k}")
