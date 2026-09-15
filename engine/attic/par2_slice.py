#!/usr/bin/env python3
"""One bounded slice of the parity-split sweep."""
import json, sys
sys.path.insert(0, ".")
import runpool
from par2_run import attack


def report(it, res):
    st, val = res
    if st != "ok" or not val or val[0] != "ok":
        return
    for verdict, cl, extra in val[1]:
        if verdict == "PROVED":
            print(f"  PROVED  {it['anum']}  {cl[:58]}", flush=True)


if __name__ == "__main__":
    items = json.load(open("parity_cands2.json")) + json.load(open("half_cands.json"))
    runpool.run(attack, items, lambda it: it["anum"], "par2_progress.json",
                per_item=120, budget=int(sys.argv[1]) if len(sys.argv) > 1 else 520,
                workers=4, report=report)
