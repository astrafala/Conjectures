#!/usr/bin/env python3
"""Turn the harvest into per-engine build specs, with live entry data attached.

Numbers assigned here are temporary: rank.py renumbers the whole roster afterwards.
"""
import json, os, sys, time
from verify_open import fetch

eng = {int(k): v for k, v in json.load(open("paper-engines.json")).items()}
nxt = max(eng) + 1
rows = json.load(open("harvest.json"))
specs = {"hyper": [], "parity": [], "regf": [], "zeilb": [], "zeil": []}
cache = {}
for v in sorted(rows, key=lambda r: (r["group"], r["anum"], r["conj"])):
    a = v["anum"]
    if a not in cache:
        e = None
        for i in range(5):
            try:
                e = fetch(a); break
            except Exception:
                time.sleep(3 * (i + 1))
        if e is None:
            print(f"could not fetch {a}, skipped"); continue
        cache[a] = e
        time.sleep(0.35)
    e = cache[a]
    s = dict(v)
    s["num"] = nxt
    s["data"] = [int(t) for t in e["data"].split(",")]
    s["offset"] = int(e["offset"].split(",")[0])
    s["name"] = e["name"]
    s["time"] = e["time"][:10]
    s["revision"] = e["revision"]
    if v["group"] == "regf":
        s["gfs"] = [v["gf_src"]]
        s["mode"] = v.get("mode", "ogf")
    specs[v["group"]].append(s)
    nxt += 1
for g, rows_ in specs.items():
    if rows_:
        json.dump(rows_, open(f"spec-{g}.json", "w"), indent=1)
        print(f"spec-{g}.json  {len(rows_)} papers, numbers "
              f"{rows_[0]['num']}..{rows_[-1]['num']}")
