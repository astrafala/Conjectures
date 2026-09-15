#!/usr/bin/env python3
"""One bounded slice of the universal sweep."""
import json, sys
sys.path.insert(0, ".")
import runpool
from universal import decide_all


def report(it, res):
    st, val = res
    if st != "ok" or not val or val[0] != "ok":
        return
    for status, cl, r in val[1]:
        if status in ("PROVED", "DISPROVED"):
            print(f"  {status:9s} {it['anum']}  [{r.get('route','')}]  {cl[:46]}", flush=True)


if __name__ == "__main__":
    items = json.load(open("uni_todo.json"))
    runpool.run(decide_all, items, lambda it: it["anum"], "uni_progress.json",
                per_item=150, budget=int(sys.argv[1]) if len(sys.argv) > 1 else 520,
                workers=4, report=report)
