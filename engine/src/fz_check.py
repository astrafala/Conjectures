#!/usr/bin/env python3
"""Live openness check on the f(z) results, run BEFORE any paper is built."""
import json, os, re, sys, time
sys.path.insert(0, ".")
from verify_open import fetch
from openness import SETTLED, FINITE

OUT = "fz_open.json"
done = json.load(open(OUT)) if os.path.exists(OUT) else {}
todo = sorted({h["anum"] for h in json.load(open("fz_new.json"))})
t0 = time.time()
for a in todo:
    if a in done or time.time() - t0 > 480:
        continue
    e = None
    for i in range(4):
        try:
            e = fetch(a); break
        except Exception:
            time.sleep(2 * (i + 1))
    if e is None:
        continue
    fields = (e.get("formula", []) + e.get("comment", []) + e.get("link", [])
              + e.get("reference", []) + e.get("example", []))
    hits = [f for f in fields if SETTLED.search(f) and not FINITE.search(f)]
    done[a] = {"time": e["time"][:10], "rev": e["revision"], "name": e["name"],
               "flag": hits[:3]}
    json.dump(done, open(OUT, "w"), indent=1)
    time.sleep(0.35)
flagged = {a: v for a, v in done.items() if v["flag"]}
print(f"{len(done)}/{len(todo)} checked; {len(flagged)} flagged")
for a, v in flagged.items():
    print(f"  {a}  {v['flag'][0][:150]}")
