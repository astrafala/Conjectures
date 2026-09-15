#!/usr/bin/env python3
"""Check cached b-files, in parallel, with a per-entry timeout.

Fetching and checking have opposite needs. Fetching must be sequential and slow, because
oeis.org blocked this address once already. Checking is pure local computation and should
be parallel -- and it needs a real per-entry timeout, since one pathological series
expansion otherwise consumes an entire slice while the budget, which is only tested between
entries, never gets a chance to fire.

So the two phases are separate: bsweep.py fetches, this checks whatever is cached.
"""
import json, os, re, sys
sys.path.insert(0, ".")
import runpool
import bsweep
import bfile
from regf import entry

OUT = "bsweep_results.json"


def one(anum):
    off, vals = bfile.contiguous(anum)
    if len(vals) < 12:
        return {"status": "b-file too short"}
    try:
        F, data, doff, nm = entry(anum)
    except Exception:
        return {"status": "no entry"}
    m = min(len(data), len(vals))
    if off != doff or any(vals[i] != data[i] for i in range(min(m, 20))):
        return {"status": "b-file disagrees with DATA"}
    import conjlines
    conjs = [l for l in F if conjlines.is_recurrence(l)]
    bad = bsweep.check(anum, conjs, vals, off)
    bad += bsweep.check_closed(F, vals, off) + bsweep.check_gf(F, vals, off)
    return {"status": "DISPROVED" if bad else "holds on all b-file terms",
            "nterms": len(vals), "ndata": len(data), "bad": bad}


def report(anum, res):
    st, val = res
    if st != "ok" or not isinstance(val, dict):
        return
    if val.get("status") == "DISPROVED":
        b = val["bad"][0]
        print(f"  DISPROVED {anum}  fails n={b[1]}..{b[2]} ({b[3]} times, tested to n={b[4]})",
              flush=True)


if __name__ == "__main__":
    q = json.load(open("bsweep_queue.json"))
    cached = [a for a in q
              if os.path.exists(os.path.join(bfile.CACHE, "b" + a[1:] + ".txt"))]
    done = runpool.run(one, cached, lambda a: a, OUT, per_item=45,
                       budget=int(sys.argv[1]) if len(sys.argv) > 1 else 500,
                       workers=4, report=report)
    from collections import Counter
    c = Counter(v[1].get("status") if isinstance(v[1], dict) else str(v[0])
                for v in done.values())
    for k, v in c.most_common():
        print(f"  {v:6d}  {k}")
