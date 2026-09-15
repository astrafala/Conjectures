#!/usr/bin/env python3
"""One bounded slice of the known-side sweep."""
import json, sys
sys.path.insert(0, ".")
import runpool
from known_run import attack


def report(it, res):
    st, val = res
    if st != "ok" or not val:
        return
    for status, cl, rec in val:
        if status == "PROVED" and not rec.get("integer_bad"):
            print(f"  PROVED    {it['anum']}  [{rec['route']}]  {cl[:55]}", flush=True)
        elif status == "DISPROVED":
            print(f"  DISPROVED {it['anum']}  fails at n={rec.get('fails_at')}", flush=True)


if __name__ == "__main__":
    items = json.load(open("known_todo.json"))
    runpool.run(attack, items, lambda it: it["anum"], "known_progress.json",
                per_item=120, budget=int(sys.argv[1]) if len(sys.argv) > 1 else 520,
                workers=4, report=report)
