#!/usr/bin/env python3
"""One bounded slice of the f(z) sweep."""
import json, sys
sys.path.insert(0, ".")
import runpool
from fz_run import attack


def report(it, res):
    st, val = res
    if st != "ok" or not val or val[0] != "ok":
        return
    for status, cl, r in val[1]:
        if status in ("PROVED", "DISPROVED"):
            print(f"  {status:9s} {it['anum']}  {cl[:56]}", flush=True)


if __name__ == "__main__":
    items = json.load(open("fz_cands.json"))
    runpool.run(attack, items, lambda it: it["anum"], "fz_progress.json",
                per_item=150, budget=int(sys.argv[1]) if len(sys.argv) > 1 else 520,
                workers=4, report=report)
